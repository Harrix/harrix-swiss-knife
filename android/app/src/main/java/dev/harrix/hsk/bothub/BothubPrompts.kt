package dev.harrix.hsk.bothub

import android.content.Context
import java.io.IOException

/**
 * BotHub prompt templates. Fix/rewrite/medicine markdown is loaded from assets
 * (synced from `config/prompts/` at Gradle preBuild).
 */
object BothubPrompts {
    const val TRANSCRIPTION =
        "Transcribe the speech in this audio accurately and verbatim. " +
            "Return only the transcribed text without comments or formatting."

    const val PHOTO_ONLY_QUERY =
        "Look at the attached photo(s) and advise what I can take from my home medicines."

    private const val TEXT_PLACEHOLDER = "{{TEXT}}"
    private const val MEDICINES_PLACEHOLDER = "{{MEDICINES}}"
    private const val QUERY_PLACEHOLDER = "{{QUERY}}"
    private const val HISTORY_PLACEHOLDER = "{{HISTORY}}"
    private const val ASSET_FIX = "prompts/text-fix-ru.md"
    private const val ASSET_REWRITE = "prompts/text-rewrite-ru.md"
    private const val ASSET_MEDICINE_SEARCH = "prompts/medicine-search.md"
    private const val EMPTY_MEDICINES_MARKER = "(список лекарств не задан)"
    private const val EMPTY_HISTORY_MARKER = "(нет предыдущих сообщений)"

    fun buildTextFixPrompt(
        context: Context,
        text: String,
    ): String = applyTextPlaceholder(loadAsset(context, ASSET_FIX), text)

    fun buildTextRewritePrompt(
        context: Context,
        text: String,
    ): String = applyTextPlaceholder(loadAsset(context, ASSET_REWRITE), text)

    fun buildMedicineSearchPrompt(
        context: Context,
        medicinesMarkdown: String?,
        query: String,
        history: String? = null,
    ): String {
        val template = loadAsset(context, ASSET_MEDICINE_SEARCH)
        if (!template.contains(MEDICINES_PLACEHOLDER) ||
            !template.contains(QUERY_PLACEHOLDER) ||
            !template.contains(HISTORY_PLACEHOLDER)
        ) {
            throw BothubApiException(
                "Prompt template is missing $MEDICINES_PLACEHOLDER, " +
                    "$QUERY_PLACEHOLDER, or $HISTORY_PLACEHOLDER",
            )
        }
        val medicines =
            medicinesMarkdown
                ?.trim()
                ?.takeIf { it.isNotEmpty() }
                ?: EMPTY_MEDICINES_MARKER
        val historyText =
            history
                ?.trim()
                ?.takeIf { it.isNotEmpty() }
                ?: EMPTY_HISTORY_MARKER
        return template
            .replace(MEDICINES_PLACEHOLDER, medicines)
            .replace(HISTORY_PLACEHOLDER, historyText)
            .replace(QUERY_PLACEHOLDER, query.trim())
    }

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
