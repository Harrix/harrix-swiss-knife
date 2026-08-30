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
    }

    companion object {
        private const val PREFS_NAME = "movies"
        private const val KEY_FOLDER_URI = "folder_uri"
    }
}
