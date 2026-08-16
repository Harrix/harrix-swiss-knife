package dev.harrix.hsk.medicinesearch

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import dev.harrix.hsk.R
import dev.harrix.hsk.bothub.BothubApiException
import dev.harrix.hsk.bothub.BothubClient
import dev.harrix.hsk.bothub.BothubConfig
import dev.harrix.hsk.bothub.BothubPrompts
import java.io.IOException

data class MedicinesFileContent(
    val uri: Uri,
    val displayName: String?,
    val markdown: String,
)

/**
 * Loads the medicines Markdown file and asks Bot Hub for advice.
 */
class MedicineSearchRepository(
    private val context: Context,
    private val client: BothubClient = BothubClient(),
) {
    fun requireApiKey() {
        if (!BothubConfig.hasApiKey) {
            throw BothubApiException(BothubClient.MISSING_API_KEY_MESSAGE)
        }
    }

    fun loadMedicinesFile(uri: Uri): MedicinesFileContent {
        val markdown =
            runCatching {
                context.contentResolver.openInputStream(uri)?.use { input ->
                    input.bufferedReader(Charsets.UTF_8).readText()
                }
            }.getOrElse { error ->
                val message =
                    when (error) {
                        is SecurityException -> "No permission to read medicines file"
                        is IOException -> "Failed to read medicines file"
                        else -> "Failed to read medicines file"
                    }
                throw BothubApiException(message, error)
            } ?: throw BothubApiException("Cannot open medicines file")
        return MedicinesFileContent(
            uri = uri,
            displayName = queryDisplayName(uri),
            markdown = markdown,
        )
    }

    fun search(
        medicinesMarkdown: String?,
        query: String,
        photos: List<Uri> = emptyList(),
        history: String? = null,
    ): String {
        requireApiKey()
        val images = loadPhotos(photos)
        val trimmed = resolveQuery(query, images.isNotEmpty())
        val answer =
            client.chatCompletion(
                model = BothubConfig.model,
                text =
                BothubPrompts.buildMedicineSearchPrompt(
                    context = context,
                    medicinesMarkdown = medicinesMarkdown,
                    query = trimmed,
                    history = history,
                ),
                images = images.takeIf { it.isNotEmpty() },
            )
        if (answer.isBlank()) {
            throw BothubApiException("Empty response from BotHub")
        }
        return answer
    }

    private fun loadPhotos(photos: List<Uri>): List<Pair<ByteArray, String>> = photos.map { uri ->
        runCatching { MedicineSearchImages.loadForAi(context, uri) }.getOrElse { error ->
            throw BothubApiException(
                context.getString(R.string.medicine_search_photo_failed),
                error,
            )
        }
    }

    private fun resolveQuery(
        query: String,
        hasPhotos: Boolean,
    ): String {
        val trimmed = query.trim()
        if (trimmed.isNotEmpty()) {
            return trimmed
        }
        if (hasPhotos) {
            return BothubPrompts.PHOTO_ONLY_QUERY
        }
        throw BothubApiException("Query is empty")
    }

    private fun queryDisplayName(uri: Uri): String? {
        val projection = arrayOf(OpenableColumns.DISPLAY_NAME)
        return try {
            context.contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
                if (!cursor.moveToFirst()) {
                    return@use null
                }
                val index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (index < 0) {
                    null
                } else {
                    cursor.getString(index)?.takeIf { it.isNotBlank() }
                }
            }
        } catch (_: Exception) {
            null
        } ?: uri.lastPathSegment?.substringAfterLast('/')
    }
}
