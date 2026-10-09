package dev.harrix.hsk.ai

import android.content.Context

/**
 * Persists the Ask AI chat-model override per BotHub provider
 * (`bothub` / `bothub.ru`), separate from bake-time [AiConfig.model].
 */
class AskAiModelStore(
    context: Context,
) {
    private val prefs =
        context.applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun load(provider: String = AiConfig.provider): String? = prefs.getString(keyFor(provider), null)?.trim()?.ifEmpty { null }

    fun save(
        modelId: String,
        provider: String = AiConfig.provider,
    ) {
        val trimmed = modelId.trim()
        if (trimmed.isEmpty()) {
            return
        }
        prefs.edit().putString(keyFor(provider), trimmed).apply()
    }

    fun resolve(provider: String = AiConfig.provider): String = load(provider) ?: AiConfig.modelFor(provider, forSpeech = false)

    private fun keyFor(provider: String): String = KEY_MODEL_PREFIX + AiConfig.normalizeProvider(provider)

    private companion object {
        const val PREFS_NAME = "ask_ai_model"
        const val KEY_MODEL_PREFIX = "model_"
    }
}
