package dev.harrix.hsk

import android.content.Context
import dev.harrix.hsk.ui.theme.AppLanguage
import dev.harrix.hsk.ui.theme.ThemeMode

/** App-wide SharedPreferences (appearance and similar). */
class AppPreferences(
    context: Context,
) {
    private val prefs =
        context.applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun loadThemeMode(): ThemeMode = ThemeMode.fromStorage(prefs.getString(KEY_THEME_MODE, ThemeMode.System.name))

    fun saveThemeMode(mode: ThemeMode) {
        prefs.edit().putString(KEY_THEME_MODE, mode.name).apply()
    }

    fun loadAppLanguage(): AppLanguage = AppLanguage.fromStorage(prefs.getString(KEY_APP_LANGUAGE, null))

    fun saveAppLanguage(language: AppLanguage) {
        prefs.edit().putString(KEY_APP_LANGUAGE, language.name).apply()
    }

    companion object {
        private const val PREFS_NAME = "app_preferences"
        private const val KEY_THEME_MODE = "theme_mode"
        private const val KEY_APP_LANGUAGE = "app_language"
    }
}
