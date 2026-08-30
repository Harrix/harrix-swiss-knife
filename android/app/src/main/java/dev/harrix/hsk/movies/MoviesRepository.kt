package dev.harrix.hsk.movies

import android.content.Context
import android.net.Uri
import android.provider.DocumentsContract
import android.provider.OpenableColumns
import java.io.File
import java.io.IOException

/**
 * Loads the Movies notes folder and groups watches into a searchable catalog.
 */
class MoviesRepository(
    private val context: Context,
    private val folderReader: MoviesFolderReader = MoviesFolderReader(context.contentResolver),
    private val posterStore: MoviesPosterStore =
        MoviesPosterStore(File(context.filesDir, "movies_posters")),
) {
    fun folderLabel(uri: Uri): String {
        queryDisplayName(uri)?.let { return it }
        val documentId =
            try {
                DocumentsContract.getTreeDocumentId(uri)
            } catch (_: Exception) {
                null
            }
        val fromId = documentId?.substringAfterLast('/')?.substringAfterLast(':')
        if (!fromId.isNullOrBlank()) {
            return fromId
        }
        return uri.lastPathSegment?.substringAfterLast('/')?.substringAfterLast(':')
            ?: uri.toString()
    }

    fun loadCatalog(treeUri: Uri): MoviesCatalog {
        val files = folderReader.listMarkdownFiles(treeUri)
        if (files.isEmpty()) {
            throw IOException("No movie Markdown files in folder")
        }
        val watches = mutableListOf<MovieWatch>()
        for (file in files) {
            val markdown =
                runCatching { folderReader.readText(file.uri) }.getOrNull() ?: continue
            watches +=
                MoviesMarkdownParser.parse(
                    markdown = markdown,
                    yearFolder = file.yearFolder,
                    sourceFileName = file.displayName,
                )
        }
        if (watches.isEmpty()) {
            throw IOException("No movie entries in folder")
        }
        return MoviesCatalogBuilder.build(watches)
    }

    fun cachedPoster(movie: MovieTitle): File? = posterStore.cachedFile(movie)

    fun fetchPoster(movie: MovieTitle): File? = posterStore.fetch(movie)

    private fun queryDisplayName(uri: Uri): String? {
        return runCatching {
            context.contentResolver
                .query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)
                ?.use { cursor ->
                    if (!cursor.moveToFirst()) {
                        return@use null
                    }
                    val index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                    if (index < 0) {
                        null
                    } else {
                        cursor.getString(index)?.trim()?.takeIf { it.isNotEmpty() }
                    }
                }
        }.getOrNull()
    }
}
