package dev.harrix.hsk.ui.theme

import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat

/**
 * In-app language. [System] follows the device locale;
 * other entries force a BCP-47 language tag via AppCompat.
 */
enum class AppLanguage(
    /** Null means follow the system locale list. */
    val languageTag: String?,
    /** Native language name shown in the picker (not translated). */
    val nativeLabel: String,
) {
    System(null, ""),
    English("en", "English"),
    Russian("ru", "Русский"),
    Spanish("es", "Español"),
    German("de", "Deutsch"),
    French("fr", "Français"),
    Portuguese("pt", "Português"),
    ChineseSimplified("zh-CN", "简体中文"),
    Japanese("ja", "日本語"),
    Italian("it", "Italiano"),
    ;

    fun toLocaleList(): LocaleListCompat = if (languageTag.isNullOrBlank()) {
        LocaleListCompat.getEmptyLocaleList()
    } else {
        LocaleListCompat.forLanguageTags(languageTag)
    }

    fun apply() {
        AppCompatDelegate.setApplicationLocales(toLocaleList())
    }

    companion object {
        val Default: AppLanguage = System

        fun fromStorage(value: String?): AppLanguage = entries.firstOrNull { it.name.equals(value, ignoreCase = true) } ?: Default
    }
}
