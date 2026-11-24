package dev.harrix.hsk.dropboxsync

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone
import java.util.concurrent.TimeUnit

/** Minimal Dropbox HTTP API v2 client used by SyncEngine. */
class DropboxApiClient(
    private val authManager: DropboxAuthManager,
    private val httpClient: OkHttpClient =
        OkHttpClient
            .Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .writeTimeout(120, TimeUnit.SECONDS)
            .build(),
) {
    fun getCurrentAccount(): DropboxAccount {
        val json = apiRpc("users/get_current_account", JSONObject())
        val name = json.optJSONObject("name")
        return DropboxAccount(
            accountId = json.getString("account_id"),
            displayName = name?.optString("display_name").orEmpty().ifBlank {
                name?.optString("familiar_name").orEmpty()
            },
            email = json.optString("email"),
        )
    }

    fun listFolder(
        path: String,
        recursive: Boolean = true,
    ): List<SyncTreeEntry> {
        val root = normalizeDropboxPath(path)
        val start =
            apiRpc(
                "files/list_folder",
                JSONObject()
                    .put("path", root)
                    .put("recursive", recursive)
                    .put("include_deleted", false)
                    .put("include_mounted_folders", true)
                    .put("limit", 2000),
            )
        val entries = mutableListOf<SyncTreeEntry>()
        collectEntries(start.optJSONArray("entries"), entries, root)
        var hasMore = start.optBoolean("has_more")
        var cursor = start.optString("cursor")
        while (hasMore && cursor.isNotBlank()) {
            val page =
                apiRpc(
                    "files/list_folder/continue",
                    JSONObject().put("cursor", cursor),
                )
            collectEntries(page.optJSONArray("entries"), entries, root)
            hasMore = page.optBoolean("has_more")
            cursor = page.optString("cursor")
        }
        return entries
    }

    fun listFolderChildren(path: String): List<DropboxRemoteItem> {
        val root = normalizeDropboxPath(path)
        val json =
            apiRpc(
                "files/list_folder",
                JSONObject()
                    .put("path", root)
                    .put("recursive", false)
                    .put("include_deleted", false)
                    .put("limit", 2000),
            )
        val items = mutableListOf<DropboxRemoteItem>()
        val array = json.optJSONArray("entries") ?: JSONArray()
        for (i in 0 until array.length()) {
            val entry = array.getJSONObject(i)
            val tag = entry.optString(".tag")
            if (tag != "folder" && tag != "file") {
                continue
            }
            items +=
                DropboxRemoteItem(
                    name = entry.getString("name"),
                    pathDisplay = entry.optString("path_display", entry.getString("name")),
                    pathLower = entry.optString("path_lower", entry.getString("name").lowercase()),
                    isDir = tag == "folder",
                )
        }
        return items.sortedWith(compareByDescending<DropboxRemoteItem> { it.isDir }.thenBy { it.name.lowercase() })
    }

    fun createFolder(path: String) {
        apiRpc(
            "files/create_folder_v2",
            JSONObject()
                .put("path", normalizeDropboxPath(path))
                .put("autorename", false),
        )
    }

    fun delete(path: String) {
        apiRpc(
            "files/delete_v2",
            JSONObject().put("path", normalizeDropboxPath(path)),
        )
    }

    fun download(
        path: String,
        output: OutputStream,
    ): SyncTreeEntry {
        val arg = JSONObject().put("path", normalizeDropboxPath(path))
        val request =
            authorizedRequest("https://content.dropboxapi.com/2/files/download")
                .addHeader("Dropbox-API-Arg", arg.toString())
                .post(emptyBody())
                .build()
        return executeWithRetry(request) { response ->
            val metaHeader = response.header("Dropbox-API-Result").orEmpty()
            val meta = if (metaHeader.isNotBlank()) JSONObject(metaHeader) else JSONObject()
            response.body?.byteStream()?.use { input ->
                val buffer = ByteArray(64 * 1024)
                while (true) {
                    val read = input.read(buffer)
                    if (read < 0) break
                    output.write(buffer, 0, read)
                }
            } ?: throw IOException("Empty download body")
            parseFileMetadata(meta, fallbackPath = path)
        }
    }

    fun upload(
        path: String,
        input: InputStream,
        size: Long,
        mute: Boolean = true,
    ): SyncTreeEntry {
        val remotePath = normalizeDropboxPath(path)
        return if (size <= SIMPLE_UPLOAD_LIMIT) {
            uploadSimple(remotePath, input, size, mute)
        } else {
            uploadSession(remotePath, input, size, mute)
        }
    }

    fun uploadFile(
        path: String,
        file: File,
        mute: Boolean = true,
    ): SyncTreeEntry = file.inputStream().use { upload(path, it, file.length(), mute) }

    private fun uploadSimple(
        path: String,
        input: InputStream,
        size: Long,
        mute: Boolean,
    ): SyncTreeEntry {
        val arg =
            JSONObject()
                .put("path", path)
                .put("mode", "overwrite")
                .put("mute", mute)
                .put("strict_conflict", false)
        val body = input.readBytes(size).toRequestBody("application/octet-stream".toMediaType())
        val request =
            authorizedRequest("https://content.dropboxapi.com/2/files/upload")
                .addHeader("Dropbox-API-Arg", arg.toString())
                .post(body)
                .build()
        return executeWithRetry(request) { response ->
            val payload = response.body?.string().orEmpty()
            parseFileMetadata(JSONObject(payload), fallbackPath = path)
        }
    }

    private fun uploadSession(
        path: String,
        input: InputStream,
        size: Long,
        mute: Boolean,
    ): SyncTreeEntry {
        val buffer = ByteArray(SESSION_CHUNK_SIZE)
        var offset = 0L
        var sessionId: String? = null
        while (offset < size) {
            val toRead = minOf(SESSION_CHUNK_SIZE.toLong(), size - offset).toInt()
            var readTotal = 0
            while (readTotal < toRead) {
                val read = input.read(buffer, readTotal, toRead - readTotal)
                if (read < 0) break
                readTotal += read
            }
            if (readTotal <= 0) break
            val chunk = if (readTotal == buffer.size) buffer else buffer.copyOf(readTotal)
            val close = offset + readTotal >= size
            if (sessionId == null) {
                val startArg = JSONObject().put("close", close && size <= SESSION_CHUNK_SIZE)
                val request =
                    authorizedRequest("https://content.dropboxapi.com/2/files/upload_session/start")
                        .addHeader("Dropbox-API-Arg", startArg.toString())
                        .post(chunk.toRequestBody("application/octet-stream".toMediaType()))
                        .build()
                sessionId =
                    executeWithRetry(request) { response ->
                        JSONObject(response.body?.string().orEmpty()).getString("session_id")
                    }
                if (close) {
                    return finishSession(sessionId, offset + readTotal, path, mute)
                }
            } else if (close) {
                return finishSession(sessionId, offset + readTotal, path, mute, appendChunk = chunk, appendOffset = offset)
            } else {
                val appendArg =
                    JSONObject()
                        .put(
                            "cursor",
                            JSONObject()
                                .put("session_id", sessionId)
                                .put("offset", offset),
                        ).put("close", false)
                val request =
                    authorizedRequest("https://content.dropboxapi.com/2/files/upload_session/append_v2")
                        .addHeader("Dropbox-API-Arg", appendArg.toString())
                        .post(chunk.toRequestBody("application/octet-stream".toMediaType()))
                        .build()
                executeWithRetry(request) { response ->
                    response.body?.close()
                    Unit
                }
            }
            offset += readTotal
        }
        val id = sessionId ?: throw IOException("Upload session was not started")
        return finishSession(id, offset, path, mute)
    }

    private fun finishSession(
        sessionId: String,
        offset: Long,
        path: String,
        mute: Boolean,
        appendChunk: ByteArray? = null,
        appendOffset: Long = 0L,
    ): SyncTreeEntry {
        if (appendChunk != null) {
            val appendArg =
                JSONObject()
                    .put(
                        "cursor",
                        JSONObject()
                            .put("session_id", sessionId)
                            .put("offset", appendOffset),
                    ).put("close", true)
            val appendRequest =
                authorizedRequest("https://content.dropboxapi.com/2/files/upload_session/append_v2")
                    .addHeader("Dropbox-API-Arg", appendArg.toString())
                    .post(appendChunk.toRequestBody("application/octet-stream".toMediaType()))
                    .build()
            executeWithRetry(appendRequest) { response ->
                response.body?.close()
                Unit
            }
        }
        val finishArg =
            JSONObject()
                .put(
                    "cursor",
                    JSONObject()
                        .put("session_id", sessionId)
                        .put("offset", offset),
                ).put(
                    "commit",
                    JSONObject()
                        .put("path", path)
                        .put("mode", "overwrite")
                        .put("mute", mute)
                        .put("strict_conflict", false),
                )
        val request =
            authorizedRequest("https://content.dropboxapi.com/2/files/upload_session/finish")
                .addHeader("Dropbox-API-Arg", finishArg.toString())
                .post(emptyBody())
                .build()
        return executeWithRetry(request) { response ->
            parseFileMetadata(JSONObject(response.body?.string().orEmpty()), fallbackPath = path)
        }
    }

    @Suppress("LoopWithTooManyJumpStatements")
    private fun collectEntries(
        array: JSONArray?,
        out: MutableList<SyncTreeEntry>,
        rootPath: String,
    ) {
        if (array == null) return
        val rootLower = normalizePathLower(rootPath.trimStart('/'))
        for (i in 0 until array.length()) {
            val entry = array.getJSONObject(i)
            val tag = entry.optString(".tag")
            if (tag != "file" && tag != "folder") continue
            val pathDisplay = entry.optString("path_display", entry.optString("name"))
            val pathLower = entry.optString("path_lower", pathDisplay.lowercase())
            val relative =
                relativeFromRoot(
                    pathDisplay = pathDisplay,
                    pathLower = pathLower,
                    rootLower = rootLower,
                ) ?: continue
            if (relative.isEmpty()) continue
            out +=
                if (tag == "folder") {
                    SyncTreeEntry(
                        relativePath = relative,
                        pathLower = normalizePathLower(relative),
                        isDir = true,
                        remoteId = entry.optString("id").ifBlank { null },
                    )
                } else {
                    parseFileMetadata(entry, fallbackPath = relative, asRelative = true)
                }
        }
    }

    private fun parseFileMetadata(
        json: JSONObject,
        fallbackPath: String,
        asRelative: Boolean = true,
    ): SyncTreeEntry {
        val pathDisplay = json.optString("path_display").ifBlank { fallbackPath }
        val relative =
            if (asRelative) {
                normalizeRelativePath(fallbackPath.ifBlank { pathDisplay.substringAfterLast('/') })
            } else {
                normalizeRelativePath(pathDisplay)
            }
        return SyncTreeEntry(
            relativePath = relative,
            pathLower = normalizePathLower(relative),
            isDir = false,
            size = json.optLong("size"),
            mtimeMs = parseDropboxTime(json.optString("client_modified")).takeIf { it > 0 }
                ?: parseDropboxTime(json.optString("server_modified")),
            contentHash = json.optString("content_hash").ifBlank { null },
            remoteId = json.optString("id").ifBlank { null },
            remoteRev = json.optString("rev").ifBlank { null },
            remoteServerModifiedMs = parseDropboxTime(json.optString("server_modified")),
        )
    }

    private fun relativeFromRoot(
        pathDisplay: String,
        pathLower: String,
        rootLower: String,
    ): String? {
        val lower = pathLower.trimStart('/')
        if (rootLower.isEmpty()) {
            return normalizeRelativePath(pathDisplay.trimStart('/'))
        }
        if (lower == rootLower) {
            return ""
        }
        val prefix = "$rootLower/"
        if (!lower.startsWith(prefix)) {
            return null
        }
        val relativeLower = lower.removePrefix(prefix)
        val display = pathDisplay.trimStart('/')
        val idx = display.lowercase().indexOf(relativeLower)
        return if (idx >= 0) {
            normalizeRelativePath(display.substring(idx))
        } else {
            normalizeRelativePath(relativeLower)
        }
    }

    private fun apiRpc(
        method: String,
        body: JSONObject,
    ): JSONObject {
        val request =
            authorizedRequest("https://api.dropboxapi.com/2/$method")
                .post(body.toString().toRequestBody(JSON_MEDIA))
                .build()
        return executeWithRetry(request) { response ->
            val payload = response.body?.string().orEmpty()
            if (payload.isBlank()) JSONObject() else JSONObject(payload)
        }
    }

    private fun authorizedRequest(url: String): Request.Builder {
        val token = authManager.getValidAccessToken()
        return Request
            .Builder()
            .url(url)
            .addHeader("Authorization", "Bearer $token")
    }

    @Suppress("TooGenericExceptionCaught", "ThrowsCount")
    private fun <T> executeWithRetry(
        request: Request,
        attempts: Int = 4,
        block: (okhttp3.Response) -> T,
    ): T {
        var lastError: Exception? = null
        var delayMs = 1000L
        repeat(attempts) { attempt ->
            try {
                httpClient.newCall(request).execute().use { response ->
                    if (response.code == 429 || response.code == 503) {
                        val retryAfter =
                            response.header("Retry-After")?.toLongOrNull()?.times(1000L)
                                ?: delayMs
                        Thread.sleep(retryAfter)
                        delayMs = (delayMs * 2).coerceAtMost(30_000L)
                        return@use
                    }
                    if (!response.isSuccessful) {
                        val payload = response.body?.string().orEmpty()
                        throw IOException("Dropbox API ${response.code}: $payload")
                    }
                    return block(response)
                }
            } catch (error: Exception) {
                lastError = error
                if (attempt == attempts - 1) {
                    throw error
                }
                Thread.sleep(delayMs)
                delayMs = (delayMs * 2).coerceAtMost(30_000L)
            }
        }
        throw lastError ?: IOException("Dropbox request failed")
    }

    private fun emptyBody(): RequestBody = ByteArray(0).toRequestBody(null)

    private fun InputStream.readBytes(size: Long): ByteArray {
        if (size > Int.MAX_VALUE) {
            throw IOException("File too large for simple upload")
        }
        val out = ByteArray(size.toInt())
        var offset = 0
        while (offset < out.size) {
            val read = read(out, offset, out.size - offset)
            if (read < 0) break
            offset += read
        }
        return if (offset == out.size) out else out.copyOf(offset)
    }

    companion object {
        private val JSON_MEDIA = "application/json".toMediaType()
        private const val SIMPLE_UPLOAD_LIMIT = 50L * 1024L * 1024L
        private const val SESSION_CHUNK_SIZE = 8 * 1024 * 1024

        fun normalizeDropboxPath(path: String): String {
            val trimmed = path.trim().replace('\\', '/')
            if (trimmed.isEmpty() || trimmed == "/") {
                return ""
            }
            return if (trimmed.startsWith("/")) trimmed else "/$trimmed"
        }

        private fun parseDropboxTime(value: String?): Long {
            if (value.isNullOrBlank()) return 0L
            return runCatching {
                val parser =
                    SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply {
                        timeZone = TimeZone.getTimeZone("UTC")
                    }
                parser.parse(value)?.time ?: 0L
            }.getOrDefault(0L)
        }
    }
}
