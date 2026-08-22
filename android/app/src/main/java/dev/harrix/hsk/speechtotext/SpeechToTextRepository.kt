package dev.harrix.hsk.speechtotext

import android.content.Context
import dev.harrix.hsk.ai.AiClient
import dev.harrix.hsk.ai.AiConfig
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
    fun requireApiKey(forSpeech: Boolean = false) {
        val message =
            when {
                forSpeech && !AiConfig.supportsSpeech ->
                    "Anthropic does not support speech-to-text. " +
                        "Set ai.speech_provider to openai, gemini, bothub, or bothub.ru, then rebuild the APK."

                forSpeech && !AiConfig.hasSpeechApiKey ->
                    AiClient.missingKeyMessage(AiConfig.speechProvider)

                !forSpeech && !BothubConfig.hasApiKey ->
                    BothubClient.MISSING_API_KEY_MESSAGE

                else -> null
            }
        if (message != null) {
            throw BothubApiException(message)
        }
    }

    fun transcribe(
        audioFile: File,
        mimeType: String = AudioRecorder.MIME_WAV,
        cancellationKey: String? = null,
    ): String {
        requireApiKey(forSpeech = true)
        val upload = AudioCompress.prepareForUpload(audioFile, mimeType)
        return try {
            val bytes = upload.file.readBytes()
            if (bytes.size < AudioRecorder.MIN_AUDIO_BYTES) {
                throw BothubApiException("Recording is too short or empty")
            }
            val transcribed =
                client.chatCompletion(
                    model = BothubConfig.speechModel,
                    text = BothubPrompts.TRANSCRIPTION,
                    audio = bytes to upload.mimeType,
                    cancellationKey = cancellationKey,
                )
            if (transcribed.isBlank()) {
                throw BothubApiException("Empty transcription from AI")
            }
            transcribed
        } finally {
            if (upload.temporary && upload.file.absolutePath != audioFile.absolutePath) {
                upload.file.delete()
            }
        }
    }

    fun fixText(
        text: String,
        cancellationKey: String? = null,
    ): String {
        requireApiKey()
        val fixed =
            client.chatCompletion(
                model = BothubConfig.model,
                text = BothubPrompts.buildTextFixPrompt(context, text),
                cancellationKey = cancellationKey,
            )
        if (fixed.isBlank()) {
            throw BothubApiException("Empty response from AI")
        }
        return fixed
    }

    fun rewrite(
        text: String,
        cancellationKey: String? = null,
    ): String {
        requireApiKey()
        val rewritten =
            client.chatCompletion(
                model = BothubConfig.model,
                text = BothubPrompts.buildTextRewritePrompt(context, text),
                cancellationKey = cancellationKey,
            )
        if (rewritten.isBlank()) {
            throw BothubApiException("Empty response from AI")
        }
        return rewritten
    }

    fun cancel(cancellationKey: String) {
        client.cancel(cancellationKey)
    }

    companion object {
        fun isMultiline(text: String): Boolean = text.trim().lines().size > 1

        fun toSingleLine(text: String): String = text
            .lineSequence()
            .map { it.trim() }
            .filter { it.isNotEmpty() }
            .joinToString(" ")
    }
}
