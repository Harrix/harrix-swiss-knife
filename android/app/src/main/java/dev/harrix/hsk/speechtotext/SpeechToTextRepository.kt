package dev.harrix.hsk.speechtotext

import android.content.Context
import dev.harrix.hsk.bothub.BothubApiException
import dev.harrix.hsk.bothub.BothubClient
import dev.harrix.hsk.bothub.BothubConfig
import dev.harrix.hsk.bothub.BothubPrompts
import java.io.File

/**
 * Desktop-parity pipeline: transcribe audio → fix text; optional rewrite.
 */
class SpeechToTextRepository(
    private val context: Context,
    private val client: BothubClient = BothubClient(),
) {
    fun requireApiKey() {
        if (!BothubConfig.hasApiKey) {
            throw BothubApiException(BothubClient.MISSING_API_KEY_MESSAGE)
        }
    }

    fun transcribe(audioFile: File): String {
        requireApiKey()
        val bytes = audioFile.readBytes()
        if (bytes.size < AudioRecorder.MIN_AUDIO_BYTES) {
            throw BothubApiException("Recording is too short or empty")
        }
        val transcribed =
            client.chatCompletion(
                model = BothubConfig.speechModel,
                text = BothubPrompts.TRANSCRIPTION,
                audio = bytes to AudioRecorder.MIME_M4A,
            )
        if (transcribed.isBlank()) {
            throw BothubApiException("Empty transcription from BotHub")
        }
        return transcribed
    }

    fun fixText(text: String): String {
        requireApiKey()
        val fixed =
            client.chatCompletion(
                model = BothubConfig.model,
                text = BothubPrompts.buildTextFixPrompt(context, text),
            )
        if (fixed.isBlank()) {
            throw BothubApiException("Empty response from BotHub")
        }
        return fixed
    }

    fun rewrite(text: String): String {
        requireApiKey()
        val rewritten =
            client.chatCompletion(
                model = BothubConfig.model,
                text = BothubPrompts.buildTextRewritePrompt(context, text),
            )
        if (rewritten.isBlank()) {
            throw BothubApiException("Empty response from BotHub")
        }
        return rewritten
    }

    companion object {
        fun toSingleLine(text: String): String = text
            .lineSequence()
            .map { it.trim() }
            .filter { it.isNotEmpty() }
            .joinToString(" ")
    }
}
