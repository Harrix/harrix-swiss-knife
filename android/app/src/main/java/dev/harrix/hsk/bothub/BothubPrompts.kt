package dev.harrix.hsk.bothub

import android.content.Context
import java.io.IOException

/**
 * BotHub prompt templates. Fix/rewrite markdown is loaded from assets
 * (synced from `config/prompts/` at Gradle preBuild).
 */
object BothubPrompts {
    const val TRANSCRIPTION =
        "Transcribe the speech in this audio accurately and verbatim. " +
            "Return only the transcribed text without comments or formatting."

    private const val TEXT_PLACEHOLDER = "{{TEXT}}"
    private const val ASSET_FIX = "prompts/text-fix-ru.md"
    private const val ASSET_REWRITE = "prompts/text-rewrite-ru.md"

    fun buildTextFixPrompt(
        context: Context,
        text: String,
    ): String = applyTextPlaceholder(loadAsset(context, ASSET_FIX), text)

    fun buildTextRewritePrompt(
        context: Context,
        text: String,
    ): String = applyTextPlaceholder(loadAsset(context, ASSET_REWRITE), text)

    private fun applyTextPlaceholder(
        template: String,
        text: String,
    ): String {
        if (!template.contains(TEXT_PLACEHOLDER)) {
            throw BothubApiException("Prompt template is missing $TEXT_PLACEHOLDER placeholder")
        }
        return template.replace(TEXT_PLACEHOLDER, text)
    }

    private fun loadAsset(
        context: Context,
        assetPath: String,
    ): String {
        try {
            return context.assets
                .open(assetPath)
                .bufferedReader(Charsets.UTF_8)
                .use { it.readText() }
                .trim()
        } catch (e: IOException) {
            throw BothubApiException(
                "Prompt asset missing: $assetPath. Rebuild so Gradle copyBothubPrompts runs.",
                e,
            )
        }
    }
}
