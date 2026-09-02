package dev.harrix.hsk.ai

import android.content.Context
import dev.harrix.hsk.BuildConfig

/**
 * AI provider settings from [BuildConfig], with a runtime BotHub.chat / BotHub.ru override.
 * Prefer this facade over reading [BuildConfig] from feature code.
 */
object AiConfig {
    @Volatile
    private var overrideProvider: String? = null

    @Volatile
    private var overrideSpeechProvider: String? = null

    @Volatile
    private var store: AiRouterStore? = null

    val provider: String
        get() = normalizeProvider(overrideProvider ?: BuildConfig.AI_PROVIDER)

    val speechProvider: String
        get() {
            val explicit = overrideSpeechProvider ?: BuildConfig.AI_SPEECH_PROVIDER.trim()
            return if (explicit.isEmpty()) {
                provider
            } else {
                normalizeProvider(explicit)
            }
        }

    val apiKey: String
        get() = apiKeyFor(provider)

    val baseUrl: String
        get() = baseUrlFor(provider)

    val model: String
        get() = modelFor(provider, forSpeech = false)

    val speechApiKey: String
        get() = apiKeyFor(speechProvider)

    val speechBaseUrl: String
        get() = baseUrlFor(speechProvider)

    val speechModel: String
        get() = modelFor(speechProvider, forSpeech = true)

    val hasApiKey: Boolean
        get() = hasUsableKey(provider)

    val hasSpeechApiKey: Boolean
        get() = hasUsableKey(speechProvider)

    val supportsSpeech: Boolean
        get() = speechProvider != PROVIDER_ANTHROPIC

    fun attach(context: Context) {
        val next = SharedPrefsAiRouterStore(context.applicationContext)
        store = next
        overrideProvider = next.loadProvider()
        overrideSpeechProvider = next.loadSpeechProvider()
    }

    fun applyRouter(
        providerId: String,
        speechProviderId: String?,
    ) {
        val normalized = normalizeProvider(providerId)
        overrideProvider = normalized
        if (speechProviderId != null) {
            overrideSpeechProvider = normalizeProvider(speechProviderId)
        }
        store?.save(normalized, speechProviderId?.let { normalizeProvider(it) })
    }

    fun apiKeyFor(providerId: String): String {
        val id = normalizeProvider(providerId)
        val embedded = embeddedApiKey(id)
        if (embedded.isNotEmpty()) {
            return embedded
        }
        return if (id == speechProvider && id != provider) {
            BuildConfig.AI_SPEECH_API_KEY.trim()
        } else {
            BuildConfig.AI_API_KEY.trim()
        }
    }

    fun baseUrlFor(providerId: String): String {
        val id = normalizeProvider(providerId)
        val embedded = embeddedBaseUrl(id)
        if (embedded.isNotEmpty()) {
            return embedded
        }
        val baked =
            if (id == speechProvider && id != provider) {
                BuildConfig.AI_SPEECH_BASE_URL.trim()
            } else {
                BuildConfig.AI_BASE_URL.trim()
            }
        return baked.ifEmpty { defaultBaseUrl(id) }
    }

    fun modelFor(
        providerId: String,
        forSpeech: Boolean,
    ): String {
        val id = normalizeProvider(providerId)
        val embedded = if (forSpeech) embeddedSpeechModel(id) else embeddedModel(id)
        if (embedded.isNotEmpty()) {
            return embedded
        }
        val baked =
            if (forSpeech) {
                BuildConfig.AI_SPEECH_MODEL.trim()
            } else {
                BuildConfig.AI_MODEL.trim()
            }
        return baked.ifEmpty {
            if (forSpeech) defaultSpeechModel(id) else defaultModel(id)
        }
    }

    fun isUsableApiKey(value: String): Boolean = value.isNotEmpty() &&
        !value.contains("paste-your", ignoreCase = true) &&
        !value.contains("your-api-key", ignoreCase = true) &&
        !value.contains("REPLACE", ignoreCase = true)

    fun isBothubRouter(providerId: String): Boolean {
        val id = normalizeProvider(providerId)
        return id == PROVIDER_BOTHUB || id == PROVIDER_BOTHUB_RU
    }

    fun otherBothubRouter(providerId: String): String = if (normalizeProvider(providerId) == PROVIDER_BOTHUB) {
        PROVIDER_BOTHUB_RU
    } else {
        PROVIDER_BOTHUB
    }

    fun speechProviderToPersistAfterSwitch(newProvider: String): String? {
        val explicit = overrideSpeechProvider ?: BuildConfig.AI_SPEECH_PROVIDER.trim()
        if (explicit.isEmpty()) {
            return null
        }
        return if (isBothubRouter(explicit)) {
            normalizeProvider(newProvider)
        } else {
            null
        }
    }

    fun normalizeProvider(value: String): String {
        val name = value.trim().lowercase()
        return when (name) {
            PROVIDER_BOTHUB,
            PROVIDER_OPENAI,
            PROVIDER_OPENROUTER,
            PROVIDER_ANTHROPIC,
            PROVIDER_GEMINI,
            -> name

            "bothub.ru",
            "bothub_ru",
            "bothub-ru",
            -> PROVIDER_BOTHUB_RU

            "open-router",
            "open_router",
            -> PROVIDER_OPENROUTER

            else -> PROVIDER_BOTHUB
        }
    }

    fun defaultBaseUrl(providerId: String): String = when (normalizeProvider(providerId)) {
        PROVIDER_OPENAI -> "https://api.openai.com/v1"
        PROVIDER_OPENROUTER -> "https://openrouter.ai/api/v1"
        PROVIDER_ANTHROPIC -> "https://api.anthropic.com"
        PROVIDER_GEMINI -> "https://generativelanguage.googleapis.com/v1beta"
        PROVIDER_BOTHUB_RU -> "https://openai.bothub.ru/v1"
        else -> "https://bothub.chat/api/v2/openai/v1"
    }

    fun defaultModel(providerId: String): String = when (normalizeProvider(providerId)) {
        PROVIDER_OPENAI -> "gpt-4.1"
        PROVIDER_OPENROUTER -> "openai/gpt-4.1"
        PROVIDER_ANTHROPIC -> "claude-sonnet-4-6"
        PROVIDER_GEMINI -> "gemini-2.5-flash"
        else -> "gpt-5.4"
    }

    fun defaultSpeechModel(providerId: String): String = when (normalizeProvider(providerId)) {
        PROVIDER_OPENAI -> "whisper-1"
        PROVIDER_OPENROUTER -> "openai/whisper-large-v3"
        PROVIDER_GEMINI -> "gemini-2.5-flash"
        PROVIDER_ANTHROPIC -> ""
        else -> "gemini-3.1-flash-lite-preview"
    }

    private fun hasUsableKey(providerId: String): Boolean {
        if (isUsableApiKey(apiKeyFor(providerId))) {
            return true
        }
        return isBothubRouter(providerId) &&
            isUsableApiKey(apiKeyFor(otherBothubRouter(providerId)))
    }

    private fun embeddedApiKey(providerId: String): String = when (providerId) {
        PROVIDER_BOTHUB -> BuildConfig.AI_BOTHUB_API_KEY.trim()
        PROVIDER_BOTHUB_RU -> BuildConfig.AI_BOTHUB_RU_API_KEY.trim()
        else -> ""
    }

    private fun embeddedBaseUrl(providerId: String): String = when (providerId) {
        PROVIDER_BOTHUB -> BuildConfig.AI_BOTHUB_BASE_URL.trim()
        PROVIDER_BOTHUB_RU -> BuildConfig.AI_BOTHUB_RU_BASE_URL.trim()
        else -> ""
    }

    private fun embeddedModel(providerId: String): String = when (providerId) {
        PROVIDER_BOTHUB -> BuildConfig.AI_BOTHUB_MODEL.trim()
        PROVIDER_BOTHUB_RU -> BuildConfig.AI_BOTHUB_RU_MODEL.trim()
        else -> ""
    }

    private fun embeddedSpeechModel(providerId: String): String = when (providerId) {
        PROVIDER_BOTHUB -> BuildConfig.AI_BOTHUB_SPEECH_MODEL.trim()
        PROVIDER_BOTHUB_RU -> BuildConfig.AI_BOTHUB_RU_SPEECH_MODEL.trim()
        else -> ""
    }

    const val PROVIDER_BOTHUB = "bothub"
    const val PROVIDER_BOTHUB_RU = "bothub.ru"
    const val PROVIDER_OPENAI = "openai"
    const val PROVIDER_OPENROUTER = "openrouter"
    const val PROVIDER_ANTHROPIC = "anthropic"
    const val PROVIDER_GEMINI = "gemini"
}

private interface AiRouterStore {
    fun loadProvider(): String?

    fun loadSpeechProvider(): String?

    fun save(
        provider: String,
        speechProvider: String?,
    )
}

private class SharedPrefsAiRouterStore(
    context: Context,
) : AiRouterStore {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    override fun loadProvider(): String? = prefs.getString(KEY_PROVIDER, null)?.trim()?.ifEmpty { null }

    override fun loadSpeechProvider(): String? {
        if (!prefs.contains(KEY_SPEECH_PROVIDER)) {
            return null
        }
        return prefs.getString(KEY_SPEECH_PROVIDER, "")?.trim()
    }

    override fun save(
        provider: String,
        speechProvider: String?,
    ) {
        val editor = prefs.edit().putString(KEY_PROVIDER, provider)
        if (speechProvider != null) {
            editor.putString(KEY_SPEECH_PROVIDER, speechProvider)
        }
        editor.apply()
    }

    private companion object {
        const val PREFS_NAME = "ai_router"
        const val KEY_PROVIDER = "provider"
        const val KEY_SPEECH_PROVIDER = "speech_provider"
    }
}
