package dev.harrix.hsk.movies

import android.content.Context
import android.net.Uri

/** Persists the SAF tree URI of the Movies notes folder. */
class MoviesPreferences(
    context: Context,
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun getFolderUri(): Uri? {
        val stored = prefs.getString(KEY_FOLDER_URI, null)?.trim().orEmpty()
        if (stored.isEmpty()) {
            return null
        }
        return runCatching { Uri.parse(stored) }.getOrNull()
    }

    fun setFolderUri(uri: Uri?) {
        prefs
            .edit()
            .apply {
                if (uri == null) {
                    remove(KEY_FOLDER_URI)
                } else {
                    putString(KEY_FOLDER_URI, uri.toString())
                }
            }.apply()
    }

    fun clearFolderUri() {
        setFolderUri(null)
    }

    fun resetSettingsToDefaults() {
        clearFolderUri()
        prefs
            .edit()
            .remove(KEY_SORT_FIELD)
            .remove(KEY_SORT_DESCENDING)
            .apply()
    }

    fun getSortField(): MoviesSortField {
        val stored = prefs.getString(KEY_SORT_FIELD, null)
        return MoviesSortField.entries.firstOrNull { it.name == stored } ?: MoviesSortField.Date
    }

    fun setSortField(field: MoviesSortField) {
        prefs.edit().putString(KEY_SORT_FIELD, field.name).apply()
    }

    fun isSortDescending(): Boolean = prefs.getBoolean(KEY_SORT_DESCENDING, true)

    fun setSortDescending(descending: Boolean) {
        prefs.edit().putBoolean(KEY_SORT_DESCENDING, descending).apply()
    }

    companion object {
        private const val PREFS_NAME = "movies"
        private const val KEY_FOLDER_URI = "folder_uri"
        private const val KEY_SORT_FIELD = "sort_field"
        private const val KEY_SORT_DESCENDING = "sort_descending"
    }
}
