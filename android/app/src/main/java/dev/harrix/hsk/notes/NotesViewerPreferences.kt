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
        val previous = loadNotesTreeUri()
        prefs.edit().putString(KEY_NOTES_TREE_URI, uri).apply()
        if (previous != null && previous != uri) {
            clearOpenTabsSession()
        }
    }

    fun clearNotesTreeUri() {
        prefs.edit().remove(KEY_NOTES_TREE_URI).apply()
        clearOpenTabsSession()
    }

    fun hasNotesPath(): Boolean = !loadNotesTreeUri().isNullOrBlank()

    fun loadListDensity(): NotesListDensity = NotesListDensity.fromStorageKey(prefs.getString(KEY_LIST_DENSITY, null))

    fun saveListDensity(density: NotesListDensity) {
        prefs.edit().putString(KEY_LIST_DENSITY, density.name).apply()
    }

    fun loadBrowseLayout(): NotesBrowseLayout = NotesBrowseLayout.fromStorageKey(prefs.getString(KEY_BROWSE_LAYOUT, null))

    fun saveBrowseLayout(layout: NotesBrowseLayout) {
        prefs.edit().putString(KEY_BROWSE_LAYOUT, layout.name).apply()
    }

    fun loadTitleSource(): NotesTitleSource = NotesTitleSource.fromStorageKey(prefs.getString(KEY_TITLE_SOURCE, null))

    fun saveTitleSource(source: NotesTitleSource) {
        prefs.edit().putString(KEY_TITLE_SOURCE, source.name).apply()
    }

    fun loadMaxOpenTabs(): Int = prefs.getInt(KEY_MAX_OPEN_TABS, DEFAULT_MAX_OPEN_TABS).coerceIn(MIN_OPEN_TABS, MAX_OPEN_TABS)

    fun saveMaxOpenTabs(value: Int) {
        prefs.edit().putInt(KEY_MAX_OPEN_TABS, value.coerceIn(MIN_OPEN_TABS, MAX_OPEN_TABS)).apply()
    }

    fun loadOpenTabsSession(treeUri: String?): NotesOpenTabsSession {
        if (treeUri.isNullOrBlank()) {
            return NotesOpenTabsSession(treeUri = "", selectedDocumentId = null, tabs = emptyList())
        }
        val raw = prefs.getString(KEY_OPEN_TABS_SESSION, null) ?: return emptySession(treeUri)
        val session = NotesOpenTabsSession.fromJson(raw) ?: return emptySession(treeUri)
        if (session.treeUri != treeUri) {
            return emptySession(treeUri)
        }
        return session
    }

    fun saveOpenTabsSession(
        treeUri: String,
        tabs: List<OpenNoteTab>,
        selectedDocumentId: String?,
    ) {
        val session =
            NotesOpenTabsSession(
                treeUri = treeUri,
                selectedDocumentId = selectedDocumentId,
                tabs = tabs,
            )
        prefs.edit().putString(KEY_OPEN_TABS_SESSION, session.toJson()).apply()
    }

    fun clearOpenTabsSession() {
        prefs.edit().remove(KEY_OPEN_TABS_SESSION).apply()
    }

    companion object {
        private const val PREFS_NAME = "notes_viewer"
        private const val KEY_NOTES_TREE_URI = "notes_tree_uri"
        private const val KEY_LIST_DENSITY = "list_density"
        private const val KEY_BROWSE_LAYOUT = "browse_layout"
        private const val KEY_TITLE_SOURCE = "title_source"
        private const val KEY_MAX_OPEN_TABS = "max_open_tabs"
        private const val KEY_OPEN_TABS_SESSION = "open_tabs_session"

        const val DEFAULT_MAX_OPEN_TABS = 10
        const val MIN_OPEN_TABS = 1
        const val MAX_OPEN_TABS = 50

        private fun emptySession(treeUri: String) = NotesOpenTabsSession(
            treeUri = treeUri,
            selectedDocumentId = null,
            tabs = emptyList(),
        )
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
