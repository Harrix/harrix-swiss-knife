package dev.harrix.hsk.photosync

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import java.util.concurrent.TimeUnit

class PhotoSyncClient(
    private val endpoint: PhotoSyncEndpoint,
    private val deviceId: String,
    private val httpClient: OkHttpClient =
        OkHttpClient
            .Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            // Manifest can wait while the desktop indexes a large Dropbox folder.
            .readTimeout(300, TimeUnit.SECONDS)
            .writeTimeout(300, TimeUnit.SECONDS)
            .callTimeout(360, TimeUnit.SECONDS)
            .build(),
) {
    data class ManifestItem(
        val mediaId: String,
        val contentHash: String,
        val sizeBytes: Long,
        val dateTakenEpochMs: Long,
        val displayName: String?,
        val mimeType: String?,
    )

    private val baseUrl: String
        get() = "http://${endpoint.host}:${endpoint.port}"

    fun checkHealth() {
        val request =
            Request
                .Builder()
                .url("$baseUrl/v1/health")
                .get()
                .build()
        httpClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Health check failed: HTTP ${response.code}")
            }
            val json = JSONObject(response.body?.string().orEmpty())
            if (!json.optBoolean("ok", false)) {
                throw IOException("Desktop receiver is not ready")
            }
        }
    }

    fun handshake() {
        val body =
            JSONObject()
                .put("token", endpoint.token)
                .put("confirmCode", endpoint.confirmCode)
                .put("deviceId", deviceId)
                .toString()
                .toRequestBody(JSON_MEDIA)
        val request =
            Request
                .Builder()
                .url("$baseUrl/v1/handshake")
                .post(body)
                .build()
        httpClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Handshake failed: HTTP ${response.code}")
            }
            val json = JSONObject(response.body?.string().orEmpty())
            if (!json.optBoolean("ok", false)) {
                throw IOException("Handshake rejected")
            }
        }
    }

    fun requestNeeded(items: List<ManifestItem>): List<String> {
        val array = JSONArray()
        for (item in items) {
            array.put(
                JSONObject()
                    .put("mediaId", item.mediaId)
                    .put("contentHash", item.contentHash)
                    .put("sizeBytes", item.sizeBytes)
                    .put("dateTakenEpochMs", item.dateTakenEpochMs)
                    .put("displayName", item.displayName ?: JSONObject.NULL)
                    .put("mimeType", item.mimeType ?: JSONObject.NULL),
            )
        }
        val body =
            JSONObject()
                .put("token", endpoint.token)
                .put("deviceId", deviceId)
                .put("items", array)
                .toString()
                .toRequestBody(JSON_MEDIA)
        val request =
            Request
                .Builder()
                .url("$baseUrl/v1/manifest")
                .post(body)
                .build()
        httpClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("Manifest failed: HTTP ${response.code}")
            }
            val json = JSONObject(response.body?.string().orEmpty())
            val needed = json.optJSONArray("needed") ?: JSONArray()
            return buildList {
                for (i in 0 until needed.length()) {
                    add(needed.getString(i))
                }
            }
        }
    }

    fun upload(
        item: ManifestItem,
        bytes: ByteArray,
    ): String {
        val query =
            buildString {
                append("token=").append(enc(endpoint.token))
                append("&deviceId=").append(enc(deviceId))
                append("&mediaId=").append(enc(item.mediaId))
                append("&contentHash=").append(enc(item.contentHash))
                append("&dateTaken=").append(item.dateTakenEpochMs)
                append("&displayName=").append(enc(item.displayName.orEmpty()))
                append("&mimeType=").append(enc(item.mimeType.orEmpty()))
            }
        val request =
            Request
                .Builder()
                .url("$baseUrl/v1/upload?$query")
                .put(bytes.toRequestBody(OCTET_MEDIA))
                .header("Content-Type", "application/octet-stream")
                .build()
        httpClient.newCall(request).execute().use { response ->
            val bodyText = response.body?.string().orEmpty()
            if (!response.isSuccessful) {
                throw IOException("Upload failed: HTTP ${response.code} $bodyText")
            }
            return JSONObject(bodyText).optString("filename", item.mediaId)
        }
    }

    private fun enc(value: String): String = URLEncoder.encode(value, StandardCharsets.UTF_8.name())

    companion object {
        private val JSON_MEDIA = "application/json; charset=utf-8".toMediaType()
        private val OCTET_MEDIA = "application/octet-stream".toMediaType()
    }
}
