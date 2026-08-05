package dev.harrix.hsk.bothub

import android.util.Base64
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class BothubApiException(
    message: String,
    cause: Throwable? = null,
) : Exception(message, cause)

/**
 * OpenAI-compatible BotHub client (`POST …/chat/completions`).
 * Mirrors desktop [harrix_swiss_knife.integrations.bothub_client].
 */
class BothubClient(
    private val apiKey: String = BothubConfig.apiKey,
    private val baseUrl: String = BothubConfig.baseUrl,
    private val httpClient: OkHttpClient = defaultHttpClient(),
) {
    fun chatCompletion(
        model: String,
        text: String,
        audio: Pair<ByteArray, String>? = null,
    ): String {
        if (apiKey.isBlank()) {
            throw BothubApiException(MISSING_API_KEY_MESSAGE)
        }
        return executeChatCompletion(model, text, audio)
    }

    private fun executeChatCompletion(
        model: String,
        text: String,
        audio: Pair<ByteArray, String>?,
    ): String {
        val messageContent = buildMessageContent(text, audio)
        val payload =
            JSONObject()
                .put("model", model)
                .put(
                    "messages",
                    JSONArray().put(
                        JSONObject()
                            .put("role", "user")
                            .put("content", messageContent),
                    ),
                )

        val url = baseUrl.trimEnd('/') + "/chat/completions"
        val body =
            payload
                .toString()
                .toRequestBody(JSON_MEDIA_TYPE)
        val request =
            Request
                .Builder()
                .url(url)
                .header("Authorization", "Bearer ${apiKey.trim()}")
                .header("Accept", "application/json")
                .post(body)
                .build()

        val httpResult =
            runCatching {
                httpClient.newCall(request).execute().use { response ->
                    response.code to response.body?.string().orEmpty()
                }
            }.getOrElse { error ->
                throw BothubApiException(error.message ?: "Network error", error)
            }
        val (code, raw) = httpResult
        if (code !in 200..299) {
            throw BothubApiException("HTTP $code: ${raw.take(500)}")
        }
        return parseAssistantText(raw)
    }

    private fun buildMessageContent(
        text: String,
        audio: Pair<ByteArray, String>?,
    ): Any {
        if (audio == null) {
            return text
        }
        val (bytes, mime) = audio
        val b64 = Base64.encodeToString(bytes, Base64.NO_WRAP)
        return JSONArray()
            .put(
                JSONObject()
                    .put("type", "text")
                    .put("text", text),
            ).put(
                JSONObject()
                    .put("type", "image_url")
                    .put(
                        "image_url",
                        JSONObject()
                            .put("url", "data:$mime;base64,$b64")
                            .put("detail", "auto"),
                    ),
            )
    }

    private fun parseAssistantText(raw: String): String {
        val data = parseJsonObject(raw)
        val failure = assistantFailureMessage(data)
        if (failure != null) {
            throw BothubApiException(failure)
        }
        val assistantText = extractAssistantText(data)
        return stripMarkdownFences(assistantText)
    }

    private fun parseJsonObject(raw: String): JSONObject = try {
        JSONObject(raw)
    } catch (e: JSONException) {
        throw BothubApiException("Invalid JSON response: ${raw.take(500)}", e)
    }

    private fun assistantFailureMessage(data: JSONObject): String? {
        if (data.has("error")) {
            val err = data.get("error")
            return when (err) {
                is JSONObject -> err.optString("message", err.toString())
                else -> err.toString()
            }
        }
        val choices = data.optJSONArray("choices")
        if (choices == null || choices.length() == 0) {
            return "No choices in API response"
        }
        val message = choices.getJSONObject(0).optJSONObject("message")
        val content = message?.opt("content")
        val assistantText = extractMessageContent(content)
        return if (assistantText.isBlank()) {
            "Empty response from model"
        } else {
            null
        }
    }

    private fun extractAssistantText(data: JSONObject): String {
        val choices = data.getJSONArray("choices")
        val message = choices.getJSONObject(0).optJSONObject("message")
        return extractMessageContent(message?.opt("content"))
    }

    private fun extractMessageContent(content: Any?): String = when (content) {
        null -> ""

        is String -> content

        is JSONArray -> {
            buildString {
                for (i in 0 until content.length()) {
                    val part = content.get(i)
                    when (part) {
                        is String -> {
                            if (isNotEmpty()) append('\n')
                            append(part)
                        }

                        is JSONObject -> {
                            if (part.optString("type") == "text") {
                                if (isNotEmpty()) append('\n')
                                append(part.optString("text"))
                            }
                        }
                    }
                }
            }
        }

        else -> content.toString()
    }

    companion object {
        const val MISSING_API_KEY_MESSAGE =
            "BotHub API key is missing. Set BOTHUB_API_KEY or create " +
                "api-keys/bothub-api-key.txt, then rebuild the APK."

        private val JSON_MEDIA_TYPE = "application/json; charset=utf-8".toMediaType()
        private const val TIMEOUT_SEC = 120L

        fun defaultHttpClient(): OkHttpClient = OkHttpClient
            .Builder()
            .connectTimeout(TIMEOUT_SEC, TimeUnit.SECONDS)
            .readTimeout(TIMEOUT_SEC, TimeUnit.SECONDS)
            .writeTimeout(TIMEOUT_SEC, TimeUnit.SECONDS)
            .callTimeout(TIMEOUT_SEC, TimeUnit.SECONDS)
            .build()

        fun stripMarkdownFences(text: String): String {
            val stripped = text.trim()
            val fence =
                Regex(
                    """^```(?:\w+)?\s*\n?(.*?)\n?```\s*$""",
                    setOf(RegexOption.DOT_MATCHES_ALL),
                )
            val match = fence.matchEntire(stripped)
            if (match != null) {
                return match.groupValues[1].trim()
            }
            if (!stripped.startsWith("```")) {
                return stripped
            }
            val lines = stripped.lines().toMutableList()
            if (lines.isNotEmpty() && lines.first().startsWith("```")) {
                lines.removeAt(0)
            }
            if (lines.isNotEmpty() && lines.last().trim() == "```") {
                lines.removeAt(lines.lastIndex)
            }
            return lines.joinToString("\n").trim()
        }
    }
}
