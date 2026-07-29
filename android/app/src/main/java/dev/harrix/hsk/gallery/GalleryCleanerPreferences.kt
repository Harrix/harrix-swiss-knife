package dev.harrix.hsk.gallery

import android.content.Context

class GalleryCleanerPreferences(
    context: Context,
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun shouldShowIntro(): Boolean = prefs.getBoolean(KEY_SHOW_INTRO, true)

    fun setShowIntro(show: Boolean) {
        prefs.edit().putBoolean(KEY_SHOW_INTRO, show).apply()
    }

    companion object {
        private const val PREFS_NAME = "gallery_cleaner"
        private const val KEY_SHOW_INTRO = "show_intro"
    }
}
