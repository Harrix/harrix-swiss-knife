package dev.harrix.hsk.speechtotext

import android.content.Context

/**
 * Optional on-device speech fallback when BotHub is unreachable.
 * On by default; cloud AI stays preferred.
 */
class LocalSpeechPrefs(
    context: Context,
) {
    private val prefs =
        context.applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    var enabled: Boolean
        get() = prefs.getBoolean(KEY_ENABLED, true)
        set(value) {
            prefs.edit().putBoolean(KEY_ENABLED, value).apply()
        }

    companion object {
        private const val PREFS_NAME = "speech_local_fallback"
        private const val KEY_ENABLED = "enabled"
    }
}
