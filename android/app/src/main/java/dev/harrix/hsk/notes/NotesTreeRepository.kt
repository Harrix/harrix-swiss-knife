package dev.harrix.hsk.notes

import android.content.Context
import android.net.Uri
import android.provider.DocumentsContract
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.withContext
import java.util.Locale
import java.util.concurrent.ConcurrentHashMap

/**
 * Lists Markdown notes and folders under a SAF tree URI using the same rules as
 * `vscode/harrix-notes-explorer-hsk` (collapse `Name/Name.md`, hide `_<Folder>.g.md`,
 * special Diary/Dreams/Cases folders, merged-note detection).
 *
 * Listing is optimized for SAF: one shallow query per sibling folder (no deep recursive
 * tree walks), an in-memory cache, and optional prefetch of child folders.
 */
class NotesTreeRepository(
    context: Context,
) {
    private val resolver = context.applicationContext.contentResolver

    fun rootSegment(treeUri: Uri): NotesPathSegment {
        val documentId = DocumentsContract.getTreeDocumentId(treeUri)
        val uri = DocumentsContract.buildDocumentUriUsingTree(treeUri, documentId)
        val name = notesFolderDisplayNameFromTree(treeUri)
        return NotesPathSegment(documentId = documentId, name = name, uri = uri)
    }

    fun clearCache() {
        Companion.clearCache()
    }

    /**
     * Drops cached listings when the notes tree URI changes; keeps cache across screen remounts.
     */
    fun prepareForTree(treeUriString: String?) {
        if (treeUriString != cachedTreeUriString) {
            rawChildrenCache.clear()
            listingCache.clear()
            cachedTreeUriString = treeUriString
        }
    }

    fun peekListing(
        treeUri: Uri,
        dirDocumentId: String,
    ): List<NotesEntry>? = listingCache[cacheKey(treeUri, dirDocumentId)]

    /**
     * Instant listing from a single SAF query: filenames only, no per-folder probes.
     * Collapse / empty-folder filtering happen later in [listChildren].
     */
    suspend fun listChildrenShallow(
        treeUri: Uri,
        dirDocumentId: String,
        dirName: String,
    ): List<NotesEntry> = withContext(Dispatchers.IO) {
        val entries = queryChildrenCached(treeUri, dirDocumentId)
        val items = ArrayList<NotesEntry>(entries.size)
        for (entry in entries) {
            if (entry.isDirectory) {
                if (isSkipScanDirName(entry.name)) {
                    continue
                }
                items.add(
                    NotesEntry.Folder(
                        documentId = entry.documentId,
                        name = entry.name,
                        uri = entry.uri,
                        hasMergedNote = false,
                        mergedNoteDocumentId = null,
                        mergedNoteUri = null,
                    ),
                )
            } else if (isMd(entry.name) && !isMergedTemplateGmd(entry.name, dirName)) {
                items.add(
                    NotesEntry.Note(
                        documentId = entry.documentId,
                        name = entry.name,
                        uri = entry.uri,
                        displayLabel = noteDisplayLabel(entry.name),
                    ),
                )
            }
        }
        items.sortedWith(notesLabelComparator)
    }

    /**
     * Warms the cache for [dirDocumentId] so a later [listChildren] can return immediately.
     */
    suspend fun prefetchDirectory(
        treeUri: Uri,
        dirDocumentId: String,
        dirName: String,
    ) {
        if (listingCache.containsKey(cacheKey(treeUri, dirDocumentId))) {
            return
        }
        runCatching { listChildren(treeUri, dirDocumentId, dirName) }
    }

    suspend fun listChildren(
        treeUri: Uri,
        dirDocumentId: String,
        dirName: String,
    ): List<NotesEntry> {
        val key = cacheKey(treeUri, dirDocumentId)
        listingCache[key]?.let { return it }

        val built =
            withContext(Dispatchers.IO) {
                buildListing(treeUri, dirDocumentId, dirName)
            }
        listingCache[key] = built
        return built
    }

    private suspend fun buildListing(
        treeUri: Uri,
        dirDocumentId: String,
        dirName: String,
    ): List<NotesEntry> = coroutineScope {
        val entries = queryChildrenCached(treeUri, dirDocumentId)
        val directories =
            entries.filter { entry ->
                entry.isDirectory && !isSkipScanDirName(entry.name)
            }
        val mdFiles =
            entries.filter { entry ->
                !entry.isDirectory &&
                    isMd(entry.name) &&
                    !isMergedTemplateGmd(entry.name, dirName)
            }

        val folderChildMap =
            directories
                .map { folder ->
                    async {
                        folder.documentId to queryChildrenCached(treeUri, folder.documentId)
                    }
                }.awaitAll()
                .toMap()

        val items = ArrayList<NotesEntry>(directories.size + mdFiles.size)

        for (folder in directories) {
            val folderChildren = folderChildMap[folder.documentId].orEmpty()
            if (!folderLooksListable(folder.name, folderChildren)) {
                continue
            }

            val subVisibleMd =
                folderChildren.filter { child ->
                    !child.isDirectory &&
                        isMd(child.name) &&
                        !isMergedTemplateGmd(child.name, folder.name)
                }
            val childDirectories =
                folderChildren.filter { child ->
                    child.isDirectory && !isSkipScanDirName(child.name)
                }

            val sameNameMd =
                folderChildren.firstOrNull { child ->
                    !child.isDirectory &&
                        child.name.equals("${folder.name}.md", ignoreCase = true)
                }

            val merged =
                folderChildren.firstOrNull { child ->
                    !child.isDirectory && isMergedTemplateGmd(child.name, folder.name)
                }

            val canCollapse = sameNameMd != null && subVisibleMd.size == 1
            val hasVisibleSubfolders =
                if (canCollapse && childDirectories.isNotEmpty()) {
                    // Probe one shallow level only when collapse is otherwise possible.
                    childDirectories
                        .map { childDir ->
                            async {
                                isSpecialNotesFolderName(childDir.name) ||
                                    directoryLooksInterestingShallow(
                                        queryChildrenCached(treeUri, childDir.documentId),
                                    )
                            }
                        }.awaitAll()
                        .any { it }
                } else {
                    childDirectories.isNotEmpty()
                }

            val collapsedNote = sameNameMd.takeIf { canCollapse && !hasVisibleSubfolders }
            if (collapsedNote != null) {
                items.add(
                    NotesEntry.Note(
                        documentId = collapsedNote.documentId,
                        name = collapsedNote.name,
                        uri = collapsedNote.uri,
                        displayLabel = noteDisplayLabel(collapsedNote.name),
                    ),
                )
            } else {
                items.add(
                    NotesEntry.Folder(
                        documentId = folder.documentId,
                        name = folder.name,
                        uri = folder.uri,
                        hasMergedNote = merged != null,
                        mergedNoteDocumentId = merged?.documentId,
                        mergedNoteUri = merged?.uri,
                    ),
                )
            }
        }

        for (file in mdFiles) {
            items.add(
                NotesEntry.Note(
                    documentId = file.documentId,
                    name = file.name,
                    uri = file.uri,
                    displayLabel = noteDisplayLabel(file.name),
                ),
            )
        }

        items.sortedWith(notesLabelComparator)
    }

    private fun folderLooksListable(
        folderName: String,
        children: List<RawEntry>,
    ): Boolean {
        if (isSpecialNotesFolderName(folderName)) {
            return true
        }
        return directoryLooksInterestingShallow(children)
    }

    /**
     * Fast stand-in for a full recursive markdown scan: the folder is interesting if it
     * already has a `.md` file or any non-skipped subdirectory (nested notes open later).
     */
    private fun directoryLooksInterestingShallow(children: List<RawEntry>): Boolean {
        for (child in children) {
            if (!child.isDirectory && isMd(child.name)) {
                return true
            }
            if (child.isDirectory && !isSkipScanDirName(child.name)) {
                return true
            }
        }
        return false
    }

    private fun queryChildrenCached(
        treeUri: Uri,
        dirDocumentId: String,
    ): List<RawEntry> {
        val key = cacheKey(treeUri, dirDocumentId)
        rawChildrenCache[key]?.let { return it }
        val loaded = queryChildren(treeUri, dirDocumentId)
        rawChildrenCache[key] = loaded
        return loaded
    }

    private fun queryChildren(
        treeUri: Uri,
        dirDocumentId: String,
    ): List<RawEntry> {
        val childrenUri = DocumentsContract.buildChildDocumentsUriUsingTree(treeUri, dirDocumentId)
        val result = ArrayList<RawEntry>()
        resolver
            .query(
                childrenUri,
                arrayOf(
                    DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                    DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                    DocumentsContract.Document.COLUMN_MIME_TYPE,
                ),
                null,
                null,
                null,
            )?.use { cursor ->
                val idIndex = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DOCUMENT_ID)
                val nameIndex = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_DISPLAY_NAME)
                val mimeIndex = cursor.getColumnIndexOrThrow(DocumentsContract.Document.COLUMN_MIME_TYPE)
                while (cursor.moveToNext()) {
                    val documentId = cursor.getString(idIndex)
                    val name = cursor.getString(nameIndex)
                    if (documentId != null && name != null) {
                        val mime = cursor.getString(mimeIndex).orEmpty()
                        val uri = DocumentsContract.buildDocumentUriUsingTree(treeUri, documentId)
                        result.add(
                            RawEntry(
                                documentId = documentId,
                                name = name,
                                uri = uri,
                                isDirectory = mime == DocumentsContract.Document.MIME_TYPE_DIR,
                            ),
                        )
                    }
                }
            }
        return result
    }

    fun readText(uri: Uri): String = resolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
        ?: error("Could not open note")

    fun writeText(
        uri: Uri,
        text: String,
    ) {
        resolver.openOutputStream(uri, "wt")?.use { output ->
            output.write(text.toByteArray(Charsets.UTF_8))
            output.flush()
        } ?: error("Could not save note")
    }

    private data class RawEntry(
        val documentId: String,
        val name: String,
        val uri: Uri,
        val isDirectory: Boolean,
    )

    companion object {
        private val rawChildrenCache = ConcurrentHashMap<String, List<RawEntry>>()
        private val listingCache = ConcurrentHashMap<String, List<NotesEntry>>()

        @Volatile
        private var cachedTreeUriString: String? = null

        private val SKIP_MARKDOWN_SCAN_DIR_NAMES =
            setOf(
                ".git",
                ".hg",
                ".svn",
                ".ruff_cache",
                ".venv",
                "venv",
                "node_modules",
                "__pycache__",
            )

        private val notesLabelComparator =
            Comparator<NotesEntry> { a, b ->
                a.sortLabel.compareTo(b.sortLabel, ignoreCase = true)
            }

        fun clearCache() {
            rawChildrenCache.clear()
            listingCache.clear()
            cachedTreeUriString = null
        }

        fun cacheKey(
            treeUri: Uri,
            dirDocumentId: String,
        ): String = "$treeUri::$dirDocumentId"

        fun isSkipScanDirName(name: String): Boolean = SKIP_MARKDOWN_SCAN_DIR_NAMES.contains(name.lowercase(Locale.ROOT))

        fun isMd(fileName: String): Boolean = fileName.lowercase(Locale.ROOT).endsWith(".md")

        fun isGMd(fileName: String): Boolean = fileName.lowercase(Locale.ROOT).endsWith(".g.md")

        fun isMergedTemplateGmd(
            fileName: String,
            parentFolderBasename: String,
        ): Boolean {
            if (!isGMd(fileName)) {
                return false
            }
            val expected = "_$parentFolderBasename.g.md".lowercase(Locale.ROOT)
            return fileName.lowercase(Locale.ROOT) == expected
        }

        fun isSpecialNotesFolderName(name: String): Boolean {
            val lower = name.lowercase(Locale.ROOT)
            return lower == "diary" || lower == "dreams" || lower == "cases"
        }

        fun noteDisplayLabel(fileName: String): String {
            val lower = fileName.lowercase(Locale.ROOT)
            return when {
                lower.endsWith(".g.md") -> fileName.dropLast(5)
                lower.endsWith(".md") -> fileName.dropLast(3)
                else -> fileName
            }
        }
    }
}

private fun notesFolderDisplayNameFromTree(treeUri: Uri): String {
    val docId =
        runCatching { DocumentsContract.getTreeDocumentId(treeUri) }.getOrNull()
            ?: return treeUri.lastPathSegment ?: "Notes"
    val name = docId.substringAfterLast(':', missingDelimiterValue = docId)
    return name.ifBlank { treeUri.lastPathSegment ?: "Notes" }
}
