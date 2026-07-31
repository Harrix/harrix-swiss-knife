package dev.harrix.hsk.notes

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.DocumentsContract

/** Preferences for the Markdown notes viewer utility. */
class NotesViewerPreferences(
    context: Context,
) {
    private val prefs =
        context.applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun loadNotesTreeUri(): String? = prefs.getString(KEY_NOTES_TREE_URI, null)?.takeIf { it.isNotBlank() }

    fun saveNotesTreeUri(uri: String) {
        prefs.edit().putString(KEY_NOTES_TREE_URI, uri).apply()
    }

    fun clearNotesTreeUri() {
        prefs.edit().remove(KEY_NOTES_TREE_URI).apply()
    }

    fun hasNotesPath(): Boolean = !loadNotesTreeUri().isNullOrBlank()

    fun loadListDensity(): NotesListDensity = NotesListDensity.fromStorageKey(prefs.getString(KEY_LIST_DENSITY, null))

    fun saveListDensity(density: NotesListDensity) {
        prefs.edit().putString(KEY_LIST_DENSITY, density.name).apply()
    }

    companion object {
        private const val PREFS_NAME = "notes_viewer"
        private const val KEY_NOTES_TREE_URI = "notes_tree_uri"
        private const val KEY_LIST_DENSITY = "list_density"
    }
}

/** Persist read/write access to a notes folder chosen via SAF. */
fun takeNotesFolderPermission(
    context: Context,
    treeUri: Uri,
) {
    val flags =
        Intent.FLAG_GRANT_READ_URI_PERMISSION or
            Intent.FLAG_GRANT_WRITE_URI_PERMISSION
    context.contentResolver.takePersistableUriPermission(treeUri, flags)
}

/** Human-readable label for a stored notes tree URI. */
fun notesFolderDisplayName(
    context: Context,
    treeUriString: String,
): String {
    val treeUri = Uri.parse(treeUriString)
    val docId =
        runCatching { DocumentsContract.getTreeDocumentId(treeUri) }.getOrNull()
            ?: return treeUri.lastPathSegment ?: treeUriString
    val name = docId.substringAfterLast(':', missingDelimiterValue = docId)
    return name.ifBlank {
        context.getString(dev.harrix.hsk.R.string.markdown_notes_path_unknown)
    }
}
