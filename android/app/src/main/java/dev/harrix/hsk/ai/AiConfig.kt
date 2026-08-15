package dev.harrix.hsk.ai

import dev.harrix.hsk.BuildConfig

/**
 * AI provider settings embedded at build time ([BuildConfig]).
 * Prefer this facade over reading [BuildConfig] from feature code.
 */
object AiConfig {
    val provider: String
        get() = BuildConfig.AI_PROVIDER.trim().ifEmpty { PROVIDER_BOTHUB }.lowercase()

    val speechProvider: String
        get() = BuildConfig.AI_SPEECH_PROVIDER.trim().ifEmpty { provider }.lowercase()

    val apiKey: String
        get() = BuildConfig.AI_API_KEY.trim()

    val baseUrl: String
        get() = BuildConfig.AI_BASE_URL.trim().ifEmpty { defaultBaseUrl(provider) }

    val model: String
        get() = BuildConfig.AI_MODEL.trim().ifEmpty { defaultModel(provider) }

    val speechApiKey: String
        get() = BuildConfig.AI_SPEECH_API_KEY.trim().ifEmpty { apiKey }

    val speechBaseUrl: String
        get() = BuildConfig.AI_SPEECH_BASE_URL.trim().ifEmpty { defaultBaseUrl(speechProvider) }

    val speechModel: String
        get() = BuildConfig.AI_SPEECH_MODEL.trim().ifEmpty { defaultSpeechModel(speechProvider) }

    val hasApiKey: Boolean
        get() = isUsableApiKey(apiKey)

    val hasSpeechApiKey: Boolean
        get() = isUsableApiKey(speechApiKey)

    val supportsSpeech: Boolean
        get() = speechProvider != PROVIDER_ANTHROPIC

    fun isUsableApiKey(value: String): Boolean = value.isNotEmpty() &&
        !value.contains("paste-your", ignoreCase = true) &&
        !value.contains("your-api-key", ignoreCase = true) &&
        !value.contains("REPLACE", ignoreCase = true)

    fun defaultBaseUrl(providerId: String): String = when (providerId) {
        PROVIDER_OPENAI -> "https://api.openai.com/v1"
        PROVIDER_ANTHROPIC -> "https://api.anthropic.com"
        PROVIDER_GEMINI -> "https://generativelanguage.googleapis.com/v1beta"
        else -> "https://bothub.chat/api/v2/openai/v1"
    }

    fun defaultModel(providerId: String): String = when (providerId) {
        PROVIDER_OPENAI -> "gpt-4.1"
        PROVIDER_ANTHROPIC -> "claude-sonnet-4-6"
        PROVIDER_GEMINI -> "gemini-2.5-flash"
        else -> "gpt-5.4"
    }

    fun defaultSpeechModel(providerId: String): String = when (providerId) {
        PROVIDER_OPENAI -> "whisper-1"
        PROVIDER_GEMINI -> "gemini-2.5-flash"
        PROVIDER_ANTHROPIC -> ""
        else -> "gemini-3.1-flash-lite-preview"
    }

    const val PROVIDER_BOTHUB = "bothub"
    const val PROVIDER_OPENAI = "openai"
    const val PROVIDER_ANTHROPIC = "anthropic"
    const val PROVIDER_GEMINI = "gemini"
}
