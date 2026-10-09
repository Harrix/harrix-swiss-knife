package dev.harrix.hsk.ai

import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject

/**
 * OpenAI-compatible model entry from `GET /models`.
 * [kind] and [endpoints] are BotHub extensions when present.
 */
data class AiModelInfo(
    val id: String,
    val kind: String? = null,
    val endpoints: List<String> = emptyList(),
) {
    val isChatModel: Boolean
        get() {
            val normalizedKind = kind?.trim()?.lowercase().orEmpty()
            if (normalizedKind.isNotEmpty()) {
                return normalizedKind == "chat"
            }
            if (endpoints.isNotEmpty()) {
                return endpoints.any { endpoint ->
                    endpoint.contains("chat/completions", ignoreCase = true)
                }
            }
            val lowerId = id.lowercase()
            return NON_CHAT_ID_MARKERS.none { marker -> marker in lowerId }
        }

    companion object {
        fun parseOpenAiListResponse(
            raw: String,
            errorMessage: (Any) -> String,
        ): List<AiModelInfo> {
            val data =
                try {
                    JSONObject(raw)
                } catch (e: JSONException) {
                    throw AiApiException("Invalid JSON response: ${raw.take(500)}", e)
                }
            if (data.has("error")) {
                throw AiApiException(errorMessage(data.get("error")))
            }
            val items = data.optJSONArray("data") ?: return emptyList()
            return buildList {
                for (i in 0 until items.length()) {
                    fromJsonObject(items.optJSONObject(i))?.let { add(it) }
                }
            }
        }

        private fun fromJsonObject(item: JSONObject?): AiModelInfo? {
            if (item == null) {
                return null
            }
            val id = item.optString("id").trim()
            if (id.isEmpty()) {
                return null
            }
            return AiModelInfo(
                id = id,
                kind = item.optString("kind").trim().ifEmpty { null },
                endpoints = endpointsFrom(item.optJSONArray("endpoints")),
            )
        }

        private fun endpointsFrom(endpointsJson: JSONArray?): List<String> {
            if (endpointsJson == null) {
                return emptyList()
            }
            return buildList {
                for (j in 0 until endpointsJson.length()) {
                    val endpoint = endpointsJson.optString(j).trim()
                    if (endpoint.isNotEmpty()) {
                        add(endpoint)
                    }
                }
            }
        }

        private val NON_CHAT_ID_MARKERS =
            listOf(
                "image",
                "embed",
                "whisper",
                "tts",
                "video",
                "dall-e",
                "dalle",
                "diffusion",
                "moderation",
                "realtime",
                "audio",
                "transcri",
            )
    }
}
