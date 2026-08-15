package dev.harrix.hsk.bothub

import dev.harrix.hsk.ai.AiConfig

/**
 * Backward-compatible facade over [AiConfig].
 * Prefer [AiConfig] for new code.
 */
object BothubConfig {
    val apiKey: String
        get() = AiConfig.apiKey

    val baseUrl: String
        get() = AiConfig.baseUrl

    val model: String
        get() = AiConfig.model

    val speechModel: String
        get() = AiConfig.speechModel

    val hasApiKey: Boolean
        get() = AiConfig.hasApiKey
}
