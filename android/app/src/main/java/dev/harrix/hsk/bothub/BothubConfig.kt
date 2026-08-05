package dev.harrix.hsk.bothub

import dev.harrix.hsk.BuildConfig

/**
 * BotHub settings embedded at build time ([BuildConfig]).
 * Prefer this facade over reading [BuildConfig] from feature code.
 */
object BothubConfig {
    val apiKey: String
        get() = BuildConfig.BOTHUB_API_KEY.trim()

    val baseUrl: String
        get() = BuildConfig.BOTHUB_BASE_URL.trim().ifEmpty { DEFAULT_BASE_URL }

    val model: String
        get() = BuildConfig.BOTHUB_MODEL.trim().ifEmpty { DEFAULT_MODEL }

    val speechModel: String
        get() = BuildConfig.BOTHUB_SPEECH_MODEL.trim().ifEmpty { DEFAULT_SPEECH_MODEL }

    val hasApiKey: Boolean
        get() = apiKey.isNotEmpty() && !isPlaceholderApiKey(apiKey)

    private fun isPlaceholderApiKey(value: String): Boolean = value.contains("paste-your", ignoreCase = true) ||
        value.contains("your-api-key", ignoreCase = true) ||
        value.contains("REPLACE", ignoreCase = true)

    private const val DEFAULT_BASE_URL = "https://bothub.chat/api/v2/openai/v1"
    private const val DEFAULT_MODEL = "gpt-5.4"
    private const val DEFAULT_SPEECH_MODEL = "gemini-3.1-flash-lite-preview"
}
