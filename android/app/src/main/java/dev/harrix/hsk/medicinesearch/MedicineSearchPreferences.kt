package dev.harrix.hsk.medicinesearch

import android.content.Context
import android.net.Uri

/** Persists the SAF URI of the home medicines Markdown file. */
class MedicineSearchPreferences(
    context: Context,
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun getMedicinesUri(): Uri? {
        val stored = prefs.getString(KEY_MEDICINES_URI, null)?.trim().orEmpty()
        if (stored.isEmpty()) {
            return null
        }
        return runCatching { Uri.parse(stored) }.getOrNull()
    }

    fun setMedicinesUri(uri: Uri?) {
        prefs
            .edit()
            .apply {
                if (uri == null) {
                    remove(KEY_MEDICINES_URI)
                } else {
                    putString(KEY_MEDICINES_URI, uri.toString())
                }
            }.apply()
    }

    fun clearMedicinesUri() {
        setMedicinesUri(null)
    }

    fun resetSettingsToDefaults() {
        clearMedicinesUri()
    }

    companion object {
        private const val PREFS_NAME = "medicine_search"
        private const val KEY_MEDICINES_URI = "medicines_uri"
    }
}
