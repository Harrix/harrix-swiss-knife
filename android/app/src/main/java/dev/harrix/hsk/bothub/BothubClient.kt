package dev.harrix.hsk.bothub

import dev.harrix.hsk.ai.AiApiException
import dev.harrix.hsk.ai.AiClient
import okhttp3.OkHttpClient

class BothubApiException(
    message: String,
    cause: Throwable? = null,
) : Exception(message, cause)

/**
 * Backward-compatible BotHub client facade over [AiClient].
 * Mirrors desktop `harrix_swiss_knife.integrations.bothub_client`.
 */
class BothubClient(
    private val httpClient: OkHttpClient = AiClient.defaultHttpClient(),
) {
    private val aiClient = AiClient(httpClient)

    fun chatCompletion(
        model: String,
        text: String,
        audio: Pair<ByteArray, String>? = null,
        images: List<Pair<ByteArray, String>>? = null,
    ): String = try {
        aiClient.chatCompletion(model = model, text = text, audio = audio, images = images)
    } catch (error: AiApiException) {
        throw BothubApiException(error.message ?: "AI request failed", error)
    }

    companion object {
        val MISSING_API_KEY_MESSAGE: String
            get() = AiClient.missingKeyMessage()

        fun defaultHttpClient(): OkHttpClient = AiClient.defaultHttpClient()

        fun stripMarkdownFences(text: String): String = AiClient.stripMarkdownFences(text)
    }
}
