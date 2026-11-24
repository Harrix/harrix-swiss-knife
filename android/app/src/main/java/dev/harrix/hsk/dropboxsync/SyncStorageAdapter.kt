package dev.harrix.hsk.dropboxsync

import android.content.Context
import android.net.Uri
import android.os.Environment
import android.provider.DocumentsContract
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream

/** Local filesystem abstraction for Direct and SAF roots. */
interface SyncStorageAdapter {
    fun listFiles(
        ignoreMatcher: SyncIgnoreMatcher,
    ): List<SyncTreeEntry>

    fun openInput(relativePath: String): InputStream

    fun writeFile(
        relativePath: String,
        desiredMtimeMs: Long? = null,
        writer: (OutputStream) -> Unit,
    ): SyncTreeEntry

    fun delete(relativePath: String)

    fun mkdir(relativePath: String)

    fun exists(relativePath: String): Boolean

    fun getEntry(relativePath: String): SyncTreeEntry?

    fun contentHash(relativePath: String): String

    fun displayRoot(): String

    companion object {
        fun create(
            context: Context,
            pair: FolderPair,
        ): SyncStorageAdapter = when (pair.storageType) {
            StorageType.Direct -> DirectFileStorageAdapter(File(pair.localPathOrUri))
            StorageType.Saf -> SafStorageAdapter(context, Uri.parse(pair.localPathOrUri))
        }

        fun isLikelyExternalSd(path: String): Boolean {
            val normalized = path.replace('\\', '/')
            if (normalized.contains("/storage/emulated/0")) {
                return false
            }
            return Regex("^/storage/[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}(/|$)").containsMatchIn(normalized)
        }

        fun defaultInternalRoot(): File = Environment.getExternalStorageDirectory()

        /** Internal storage and removable volumes (microSD) when All files access is granted. */
        fun listStorageRoots(context: Context): List<File> {
            val roots = linkedMapOf<String, File>()
            defaultInternalRoot().takeIf { it.exists() }?.let { roots[it.absolutePath] = it }
            context.getExternalFilesDirs(null)?.forEach { filesDir ->
                if (filesDir == null) return@forEach
                val absolute = filesDir.absolutePath.replace('\\', '/')
                val marker = "/Android/data/"
                val idx = absolute.indexOf(marker)
                if (idx <= 0) return@forEach
                val root = File(absolute.substring(0, idx))
                if (root.exists() && root.canRead()) {
                    roots.putIfAbsent(root.absolutePath, root)
                }
            }
            return roots.values.toList()
        }

        fun listChildDirectories(dir: File): List<File> = dir
            .listFiles()
            ?.filter { it.isDirectory && !it.isHidden }
            ?.sortedBy { it.name.lowercase() }
            .orEmpty()
    }
}

class DirectFileStorageAdapter(
    private val root: File,
) : SyncStorageAdapter {
    init {
        if (!root.exists()) {
            root.mkdirs()
        }
    }

    override fun listFiles(ignoreMatcher: SyncIgnoreMatcher): List<SyncTreeEntry> {
        val out = mutableListOf<SyncTreeEntry>()
        walk(root, "", ignoreMatcher, out)
        return out
    }

    private fun walk(
        dir: File,
        relative: String,
        ignoreMatcher: SyncIgnoreMatcher,
        out: MutableList<SyncTreeEntry>,
    ) {
        val children = dir.listFiles() ?: return
        for (child in children) {
            val childRelative =
                if (relative.isEmpty()) {
                    child.name
                } else {
                    "$relative/${child.name}"
                }
            if (ignoreMatcher.ignores(childRelative)) {
                continue
            }
            if (child.isDirectory) {
                out +=
                    SyncTreeEntry(
                        relativePath = childRelative,
                        pathLower = normalizePathLower(childRelative),
                        isDir = true,
                        mtimeMs = child.lastModified(),
                    )
                walk(child, childRelative, ignoreMatcher, out)
            } else if (child.isFile) {
                out +=
                    SyncTreeEntry(
                        relativePath = childRelative,
                        pathLower = normalizePathLower(childRelative),
                        isDir = false,
                        size = child.length(),
                        mtimeMs = child.lastModified(),
                    )
            }
        }
    }

    override fun openInput(relativePath: String): InputStream = resolve(relativePath).inputStream()

    @Suppress("NestedBlockDepth", "TooGenericExceptionCaught")
    override fun writeFile(
        relativePath: String,
        desiredMtimeMs: Long?,
        writer: (OutputStream) -> Unit,
    ): SyncTreeEntry {
        val target = resolve(relativePath)
        target.parentFile?.mkdirs()
        val tmp = File(target.parentFile, ".${target.name}.hsksync.tmp")
        try {
            tmp.outputStream().use(writer)
            if (target.exists() && !target.delete()) {
                throw IOException("Cannot replace $relativePath")
            }
            if (!tmp.renameTo(target)) {
                tmp.inputStream().use { input ->
                    target.outputStream().use { output -> input.copyTo(output) }
                }
                tmp.delete()
            }
            if (desiredMtimeMs != null && desiredMtimeMs > 0L) {
                target.setLastModified(desiredMtimeMs)
            }
        } catch (error: Exception) {
            tmp.delete()
            throw error
        }
        return getEntry(relativePath) ?: throw IOException("Missing file after write: $relativePath")
    }

    override fun delete(relativePath: String) {
        val file = resolve(relativePath)
        if (!file.exists()) return
        if (file.isDirectory) {
            file.deleteRecursively()
        } else {
            file.delete()
        }
    }

    override fun mkdir(relativePath: String) {
        resolve(relativePath).mkdirs()
    }

    override fun exists(relativePath: String): Boolean = resolve(relativePath).exists()

    override fun getEntry(relativePath: String): SyncTreeEntry? {
        val file = resolve(relativePath)
        if (!file.exists()) return null
        return if (file.isDirectory) {
            SyncTreeEntry(
                relativePath = normalizeRelativePath(relativePath),
                pathLower = normalizePathLower(relativePath),
                isDir = true,
                mtimeMs = file.lastModified(),
            )
        } else {
            SyncTreeEntry(
                relativePath = normalizeRelativePath(relativePath),
                pathLower = normalizePathLower(relativePath),
                isDir = false,
                size = file.length(),
                mtimeMs = file.lastModified(),
            )
        }
    }

    override fun contentHash(relativePath: String): String = openInput(relativePath).use { DropboxContentHasher.hash(it) }

    override fun displayRoot(): String = root.absolutePath

    private fun resolve(relativePath: String): File {
        val normalized = normalizeRelativePath(relativePath)
        if (normalized.isEmpty()) return root
        val file = File(root, normalized)
        val rootPath = root.canonicalFile.absolutePath
        val filePath = file.canonicalFile.absolutePath
        if (!filePath.startsWith(rootPath)) {
            throw SecurityException("Path escapes sync root: $relativePath")
        }
        return file
    }
}

class SafStorageAdapter(
    context: Context,
    private val treeUri: Uri,
) : SyncStorageAdapter {
    private val resolver = context.contentResolver
    private val treeDocId = DocumentsContract.getTreeDocumentId(treeUri)

    override fun listFiles(ignoreMatcher: SyncIgnoreMatcher): List<SyncTreeEntry> {
        val out = mutableListOf<SyncTreeEntry>()
        walk(treeDocId, "", ignoreMatcher, out)
        return out
    }

    @Suppress("LoopWithTooManyJumpStatements")
    private fun walk(
        parentDocId: String,
        relative: String,
        ignoreMatcher: SyncIgnoreMatcher,
        out: MutableList<SyncTreeEntry>,
    ) {
        val childrenUri = DocumentsContract.buildChildDocumentsUriUsingTree(treeUri, parentDocId)
        resolver
            .query(
                childrenUri,
                arrayOf(
                    DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                    DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                    DocumentsContract.Document.COLUMN_MIME_TYPE,
                    DocumentsContract.Document.COLUMN_SIZE,
                    DocumentsContract.Document.COLUMN_LAST_MODIFIED,
                ),
                null,
                null,
                null,
            )?.use { cursor ->
                val idIdx = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DOCUMENT_ID)
                val nameIdx = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DISPLAY_NAME)
                val mimeIdx = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_MIME_TYPE)
                val sizeIdx = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_SIZE)
                val modifiedIdx =
                    cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_LAST_MODIFIED)
                while (cursor.moveToNext()) {
                    val name = cursor.getString(nameIdx) ?: continue
                    val childRelative =
                        if (relative.isEmpty()) {
                            name
                        } else {
                            "$relative/$name"
                        }
                    if (ignoreMatcher.ignores(childRelative)) {
                        continue
                    }
                    val docId = cursor.getString(idIdx)
                    val mime = cursor.getString(mimeIdx)
                    val isDir = mime == DocumentsContract.Document.MIME_TYPE_DIR
                    if (isDir) {
                        out +=
                            SyncTreeEntry(
                                relativePath = childRelative,
                                pathLower = normalizePathLower(childRelative),
                                isDir = true,
                                mtimeMs = cursor.getLong(modifiedIdx),
                            )
                        walk(docId, childRelative, ignoreMatcher, out)
                    } else {
                        out +=
                            SyncTreeEntry(
                                relativePath = childRelative,
                                pathLower = normalizePathLower(childRelative),
                                isDir = false,
                                size = cursor.getLong(sizeIdx),
                                mtimeMs = cursor.getLong(modifiedIdx),
                            )
                    }
                }
            }
    }

    override fun openInput(relativePath: String): InputStream {
        val docId =
            findDocumentId(relativePath)
                ?: throw IOException("Missing SAF file: $relativePath")
        val uri = DocumentsContract.buildDocumentUriUsingTree(treeUri, docId)
        return resolver.openInputStream(uri) ?: throw IOException("Cannot open $relativePath")
    }

    override fun writeFile(
        relativePath: String,
        desiredMtimeMs: Long?,
        writer: (OutputStream) -> Unit,
    ): SyncTreeEntry {
        val normalized = normalizeRelativePath(relativePath)
        val parentRelative = normalized.substringBeforeLast('/', missingDelimiterValue = "")
        val fileName = normalized.substringAfterLast('/')
        ensureDirectory(parentRelative)
        val parentId =
            if (parentRelative.isEmpty()) {
                treeDocId
            } else {
                findDocumentId(parentRelative)
                    ?: throw IOException("Missing parent folder: $parentRelative")
            }
        val existingId = findDocumentId(normalized)
        if (existingId != null) {
            val existingUri = DocumentsContract.buildDocumentUriUsingTree(treeUri, existingId)
            DocumentsContract.deleteDocument(resolver, existingUri)
        }
        val created =
            DocumentsContract.createDocument(
                resolver,
                DocumentsContract.buildDocumentUriUsingTree(treeUri, parentId),
                "application/octet-stream",
                fileName,
            ) ?: throw IOException("Cannot create $relativePath")
        resolver.openOutputStream(created, "w")?.use(writer)
            ?: throw IOException("Cannot write $relativePath")
        return getEntry(normalized) ?: throw IOException("Missing SAF file after write: $relativePath")
    }

    override fun delete(relativePath: String) {
        val docId = findDocumentId(relativePath) ?: return
        val uri = DocumentsContract.buildDocumentUriUsingTree(treeUri, docId)
        DocumentsContract.deleteDocument(resolver, uri)
    }

    override fun mkdir(relativePath: String) {
        ensureDirectory(normalizeRelativePath(relativePath))
    }

    override fun exists(relativePath: String): Boolean = findDocumentId(relativePath) != null

    override fun getEntry(relativePath: String): SyncTreeEntry? {
        val docId = findDocumentId(relativePath) ?: return null
        val uri = DocumentsContract.buildDocumentUriUsingTree(treeUri, docId)
        resolver
            .query(
                uri,
                arrayOf(
                    DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                    DocumentsContract.Document.COLUMN_MIME_TYPE,
                    DocumentsContract.Document.COLUMN_SIZE,
                    DocumentsContract.Document.COLUMN_LAST_MODIFIED,
                ),
                null,
                null,
                null,
            )?.use { cursor ->
                if (!cursor.moveToFirst()) return null
                val mime =
                    cursor.getString(
                        cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_MIME_TYPE),
                    )
                val isDir = mime == DocumentsContract.Document.MIME_TYPE_DIR
                val normalized = normalizeRelativePath(relativePath)
                return SyncTreeEntry(
                    relativePath = normalized,
                    pathLower = normalizePathLower(normalized),
                    isDir = isDir,
                    size =
                    if (isDir) {
                        0L
                    } else {
                        cursor.getLong(
                            cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_SIZE),
                        )
                    },
                    mtimeMs =
                    cursor.getLong(
                        cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_LAST_MODIFIED),
                    ),
                )
            }
        return null
    }

    override fun contentHash(relativePath: String): String = openInput(relativePath).use { DropboxContentHasher.hash(it) }

    override fun displayRoot(): String = treeUri.toString()

    private fun ensureDirectory(relativePath: String) {
        if (relativePath.isEmpty()) return
        val parts = relativePath.split('/')
        var currentId = treeDocId
        var built = ""
        for (part in parts) {
            built = if (built.isEmpty()) part else "$built/$part"
            val existing = findChildDocumentId(currentId, part)
            currentId =
                if (existing != null) {
                    existing
                } else {
                    val parentUri = DocumentsContract.buildDocumentUriUsingTree(treeUri, currentId)
                    val created =
                        DocumentsContract.createDocument(
                            resolver,
                            parentUri,
                            DocumentsContract.Document.MIME_TYPE_DIR,
                            part,
                        ) ?: throw IOException("Cannot create folder $built")
                    DocumentsContract.getDocumentId(created)
                }
        }
    }

    private fun findDocumentId(relativePath: String): String? {
        val normalized = normalizeRelativePath(relativePath)
        if (normalized.isEmpty()) return treeDocId
        var currentId = treeDocId
        for (part in normalized.split('/')) {
            currentId = findChildDocumentId(currentId, part) ?: return null
        }
        return currentId
    }

    private fun findChildDocumentId(
        parentDocId: String,
        name: String,
    ): String? {
        val childrenUri = DocumentsContract.buildChildDocumentsUriUsingTree(treeUri, parentDocId)
        resolver
            .query(
                childrenUri,
                arrayOf(
                    DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                    DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                ),
                null,
                null,
                null,
            )?.use { cursor ->
                val idIdx = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DOCUMENT_ID)
                val nameIdx =
                    cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DISPLAY_NAME)
                while (cursor.moveToNext()) {
                    if (cursor.getString(nameIdx) == name) {
                        return cursor.getString(idIdx)
                    }
                }
            }
        return null
    }
}
