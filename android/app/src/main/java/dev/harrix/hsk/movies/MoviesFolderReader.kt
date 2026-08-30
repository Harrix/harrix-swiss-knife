package dev.harrix.hsk.movies

import android.content.ContentResolver
import android.net.Uri
import android.provider.DocumentsContract
import java.io.IOException

data class MovieMarkdownFile(
    val uri: Uri,
    val displayName: String,
    val yearFolder: String,
)

/**
 * Walks a SAF document tree and reads movie Markdown notes.
 */
class MoviesFolderReader(
    private val resolver: ContentResolver,
) {
    fun listMarkdownFiles(treeUri: Uri): List<MovieMarkdownFile> {
        val treeId =
            try {
                DocumentsContract.getTreeDocumentId(treeUri)
            } catch (_: Exception) {
                return emptyList()
            }
        val out = mutableListOf<MovieMarkdownFile>()
        walk(treeUri, treeId, parentYear = "", out)
        return out
    }

    fun readText(uri: Uri): String = resolver.openInputStream(uri)?.use { input ->
        input.bufferedReader(Charsets.UTF_8).readText()
    } ?: throw IOException("Cannot open movie note")

    private fun walk(
        treeUri: Uri,
        parentDocId: String,
        parentYear: String,
        out: MutableList<MovieMarkdownFile>,
    ) {
        val childrenUri =
            try {
                DocumentsContract.buildChildDocumentsUriUsingTree(treeUri, parentDocId)
            } catch (_: Exception) {
                return
            }
        val cursor =
            try {
                resolver.query(
                    childrenUri,
                    arrayOf(
                        DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                        DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                        DocumentsContract.Document.COLUMN_MIME_TYPE,
                    ),
                    null,
                    null,
                    null,
                )
            } catch (_: SecurityException) {
                return
            } catch (_: IllegalArgumentException) {
                return
            } ?: return
        cursor.use { rows ->
            val idIndex = rows.getColumnIndex(DocumentsContract.Document.COLUMN_DOCUMENT_ID)
            val nameIndex = rows.getColumnIndex(DocumentsContract.Document.COLUMN_DISPLAY_NAME)
            val mimeIndex = rows.getColumnIndex(DocumentsContract.Document.COLUMN_MIME_TYPE)
            if (idIndex < 0 || nameIndex < 0) {
                return
            }
            while (rows.moveToNext()) {
                addChild(
                    treeUri = treeUri,
                    documentId = rows.getString(idIndex),
                    displayName = rows.getString(nameIndex),
                    mimeType = if (mimeIndex >= 0) rows.getString(mimeIndex) else null,
                    parentYear = parentYear,
                    out = out,
                )
            }
        }
    }

    private fun addChild(
        treeUri: Uri,
        documentId: String?,
        displayName: String?,
        mimeType: String?,
        parentYear: String,
        out: MutableList<MovieMarkdownFile>,
    ) {
        val id = documentId ?: return
        val name = displayName?.trim().orEmpty()
        if (name.isEmpty()) {
            return
        }
        val mime = mimeType.orEmpty()
        if (mime == DocumentsContract.Document.MIME_TYPE_DIR) {
            walk(treeUri, id, parentYear.ifBlank { name }, out)
            return
        }
        if (!MoviesMarkdownParser.shouldReadFile(name)) {
            return
        }
        val uri =
            try {
                DocumentsContract.buildDocumentUriUsingTree(treeUri, id)
            } catch (_: Exception) {
                return
            }
        out +=
            MovieMarkdownFile(
                uri = uri,
                displayName = name,
                yearFolder = parentYear.ifBlank { name.substringBeforeLast('.') },
            )
    }
}
