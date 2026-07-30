package dev.harrix.hsk.notes

import android.content.Context
import android.net.Uri
import android.provider.DocumentsContract
import java.util.Locale

/**
 * Lists Markdown notes and folders under a SAF tree URI using the same rules as
 * `vscode/harrix-notes-explorer-hsk` (collapse `Name/Name.md`, hide `_<Folder>.g.md`,
 * special Diary/Dreams/Cases folders, merged-note detection).
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

    fun listChildren(
        treeUri: Uri,
        dirDocumentId: String,
    ): List<NotesEntry> {
        val entries = queryChildren(treeUri, dirDocumentId)
        val dirName = documentDisplayName(treeUri, dirDocumentId) ?: ""

        val directories = entries.filter { it.isDirectory }
        val files = entries.filter { !it.isDirectory }

        val folders =
            directories.filter { entry ->
                hasMarkdownRecursive(treeUri, entry.documentId) ||
                    isSpecialNotesFolderName(entry.name)
            }

        val mdFiles =
            files.filter { entry ->
                isMd(entry.name) && !isMergedTemplateGmd(entry.name, dirName)
            }

        val items = ArrayList<NotesEntry>(folders.size + mdFiles.size)

        for (folder in folders) {
            val folderChildren = queryChildren(treeUri, folder.documentId)
            val subVisibleMd =
                folderChildren.filter { child ->
                    !child.isDirectory &&
                        isMd(child.name) &&
                        !isMergedTemplateGmd(child.name, folder.name)
                }
            val subFolders =
                folderChildren.filter { child ->
                    child.isDirectory &&
                        (
                            (
                                !SKIP_MARKDOWN_SCAN_DIR_NAMES.contains(child.name.lowercase(Locale.ROOT)) &&
                                    hasMarkdownRecursive(treeUri, child.documentId)
                                ) ||
                                isSpecialNotesFolderName(child.name)
                            )
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

            if (sameNameMd != null && subVisibleMd.size == 1 && subFolders.isEmpty()) {
                items.add(
                    NotesEntry.Note(
                        documentId = sameNameMd.documentId,
                        name = sameNameMd.name,
                        uri = sameNameMd.uri,
                        displayLabel = noteDisplayLabel(sameNameMd.name),
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

        return items.sortedWith(notesLabelComparator)
    }

    fun readText(uri: Uri): String = resolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
        ?: error("Could not open note")

    private fun hasMarkdownRecursive(
        treeUri: Uri,
        dirDocumentId: String,
    ): Boolean {
        val children = queryChildren(treeUri, dirDocumentId)
        for (child in children) {
            if (!child.isDirectory && isMd(child.name)) {
                return true
            }
            if (child.isDirectory) {
                if (SKIP_MARKDOWN_SCAN_DIR_NAMES.contains(child.name.lowercase(Locale.ROOT))) {
                    continue
                }
                if (hasMarkdownRecursive(treeUri, child.documentId)) {
                    return true
                }
            }
        }
        return false
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

    private fun documentDisplayName(
        treeUri: Uri,
        documentId: String,
    ): String? {
        val uri = DocumentsContract.buildDocumentUriUsingTree(treeUri, documentId)
        resolver
            .query(
                uri,
                arrayOf(DocumentsContract.Document.COLUMN_DISPLAY_NAME),
                null,
                null,
                null,
            )?.use { cursor ->
                if (cursor.moveToFirst()) {
                    return cursor.getString(0)
                }
            }
        return null
    }

    private data class RawEntry(
        val documentId: String,
        val name: String,
        val uri: Uri,
        val isDirectory: Boolean,
    )

    companion object {
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
