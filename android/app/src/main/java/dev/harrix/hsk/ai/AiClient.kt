package dev.harrix.hsk.ai

import android.util.Base64
import okhttp3.Call
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.TimeUnit
import kotlin.coroutines.cancellation.CancellationException

class AiApiException(
    message: String,
    cause: Throwable? = null,
) : Exception(message, cause)

/**
 * Multi-provider AI client (BotHub / OpenAI / Anthropic / Gemini).
 * Mirrors desktop `harrix_swiss_knife.integrations.ai`.
 */
class AiClient(
    private val httpClient: OkHttpClient = defaultHttpClient(),
) {
    private val activeCalls = ConcurrentHashMap<String, Call>()

    fun chatCompletion(
        model: String,
        text: String,
        audio: Pair<ByteArray, String>? = null,
        images: List<Pair<ByteArray, String>>? = null,
        forSpeech: Boolean = audio != null,
        cancellationKey: String? = null,
    ): String {
        val switched = BothubFailover.prepare(forSpeech)
        val provider = if (forSpeech) AiConfig.speechProvider else AiConfig.provider
        val apiKey = if (forSpeech) AiConfig.speechApiKey else AiConfig.apiKey
        val baseUrl = if (forSpeech) AiConfig.speechBaseUrl else AiConfig.baseUrl
        val resolvedModel =
            if (switched != null) {
                if (forSpeech) AiConfig.speechModel else AiConfig.model
            } else {
                model
            }
        if (!AiConfig.isUsableApiKey(apiKey)) {
            throw AiApiException(missingKeyMessage(provider))
        }
        if (forSpeech && provider == AiConfig.PROVIDER_ANTHROPIC) {
            throw AiApiException(
                "Anthropic does not support speech-to-text. " +
                    "Set ai.speech_provider to openai, gemini, bothub, or bothub.ru, then rebuild the APK.",
            )
        }
        return when (provider) {
            AiConfig.PROVIDER_OPENAI ->
                if (audio != null) {
                    openaiTranscribe(apiKey, baseUrl, resolvedModel, text, audio, cancellationKey)
                } else {
                    openaiChat(
                        apiKey,
                        baseUrl,
                        resolvedModel,
                        text,
                        audio = null,
                        images = images,
                        allowAudioAsImageUrl = false,
                        cancellationKey = cancellationKey,
                    )
                }

            AiConfig.PROVIDER_ANTHROPIC ->
                anthropicMessages(apiKey, baseUrl, resolvedModel, text, images, cancellationKey)

            AiConfig.PROVIDER_GEMINI ->
                geminiGenerate(apiKey, baseUrl, resolvedModel, text, audio, images, cancellationKey)

            else ->
                openaiChat(
                    apiKey,
                    baseUrl,
                    resolvedModel,
                    text,
                    audio,
                    images,
                    allowAudioAsImageUrl = true,
                    cancellationKey = cancellationKey,
                )
        }
    }

    /** Cancel an in-flight request previously started with [cancellationKey]. */
    fun cancel(cancellationKey: String) {
        activeCalls.remove(cancellationKey)?.cancel()
    }

    private fun openaiChat(
        apiKey: String,
        baseUrl: String,
        model: String,
        text: String,
        audio: Pair<ByteArray, String>?,
        images: List<Pair<ByteArray, String>>?,
        allowAudioAsImageUrl: Boolean,
        cancellationKey: String? = null,
    ): String {
        val messageContent =
            buildOpenAiMessageContent(text, audio, images, allowAudioAsImageUrl)
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
        val raw =
            postJson(
                url = url,
                payload = payload,
                headers =
                mapOf(
                    "Authorization" to "Bearer ${apiKey.trim()}",
                    "Accept" to "application/json",
                ),
                cancellationKey = cancellationKey,
            )
        return parseOpenAiChatResponse(raw)
    }

    private fun openaiTranscribe(
        apiKey: String,
        baseUrl: String,
        model: String,
        prompt: String,
        audio: Pair<ByteArray, String>,
        cancellationKey: String? = null,
    ): String {
        val (bytes, mime) = audio
        val filename = filenameForMime(mime)
        val bodyBuilder =
            MultipartBody
                .Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("model", model)
                .addFormDataPart(
                    "file",
                    filename,
                    bytes.toRequestBody((mime.ifBlank { "application/octet-stream" }).toMediaType()),
                )
        if (prompt.isNotBlank()) {
            bodyBuilder.addFormDataPart("prompt", prompt)
        }
        val url = baseUrl.trimEnd('/') + "/audio/transcriptions"
        val request =
            Request
                .Builder()
                .url(url)
                .header("Authorization", "Bearer ${apiKey.trim()}")
                .header("Accept", "application/json")
                .post(bodyBuilder.build())
                .build()
        val raw = execute(request, cancellationKey)
        return parseWhisperResponse(raw)
    }

    private fun anthropicMessages(
        apiKey: String,
        baseUrl: String,
        model: String,
        text: String,
        images: List<Pair<ByteArray, String>>?,
        cancellationKey: String? = null,
    ): String {
        val content = JSONArray()
        images.orEmpty().forEach { (bytes, mime) ->
            val b64 = Base64.encodeToString(bytes, Base64.NO_WRAP)
            content.put(
                JSONObject()
                    .put("type", "image")
                    .put(
                        "source",
                        JSONObject()
                            .put("type", "base64")
                            .put("media_type", mime.substringBefore(';').ifBlank { "image/jpeg" })
                            .put("data", b64),
                    ),
            )
        }
        content.put(JSONObject().put("type", "text").put("text", text))
        val payload =
            JSONObject()
                .put("model", model)
                .put("max_tokens", 8192)
                .put(
                    "messages",
                    JSONArray().put(
                        JSONObject()
                            .put("role", "user")
                            .put("content", content),
                    ),
                )
        val url = baseUrl.trimEnd('/') + "/v1/messages"
        val raw =
            postJson(
                url = url,
                payload = payload,
                headers =
                mapOf(
                    "x-api-key" to apiKey.trim(),
                    "anthropic-version" to "2023-06-01",
                    "Accept" to "application/json",
                ),
                cancellationKey = cancellationKey,
            )
        return parseAnthropicResponse(raw)
    }

    private fun geminiGenerate(
        apiKey: String,
        baseUrl: String,
        model: String,
        text: String,
        audio: Pair<ByteArray, String>?,
        images: List<Pair<ByteArray, String>>?,
        cancellationKey: String? = null,
    ): String {
        val parts = JSONArray().put(JSONObject().put("text", text))
        images.orEmpty().forEach { (bytes, mime) ->
            val b64 = Base64.encodeToString(bytes, Base64.NO_WRAP)
            parts.put(
                JSONObject().put(
                    "inline_data",
                    JSONObject()
                        .put("mime_type", mime.substringBefore(';').ifBlank { "image/jpeg" })
                        .put("data", b64),
                ),
            )
        }
        if (audio != null) {
            val (bytes, mime) = audio
            val b64 = Base64.encodeToString(bytes, Base64.NO_WRAP)
            parts.put(
                JSONObject().put(
                    "inline_data",
                    JSONObject()
                        .put("mime_type", mime.substringBefore(';').ifBlank { "audio/wav" })
                        .put("data", b64),
                ),
            )
        }
        val payload =
            JSONObject().put(
                "contents",
                JSONArray().put(
                    JSONObject()
                        .put("role", "user")
                        .put("parts", parts),
                ),
            )
        val modelId = model.removePrefix("models/")
        val url =
            baseUrl.trimEnd('/') +
                "/models/$modelId:generateContent?key=${apiKey.trim()}"
        val raw =
            postJson(
                url = url,
                payload = payload,
                headers = mapOf("Accept" to "application/json"),
                cancellationKey = cancellationKey,
            )
        return parseGeminiResponse(raw)
    }

    private fun buildOpenAiMessageContent(
        text: String,
        audio: Pair<ByteArray, String>?,
        images: List<Pair<ByteArray, String>>?,
        allowAudioAsImageUrl: Boolean,
    ): Any {
        val parts = JSONArray().put(
            JSONObject()
                .put("type", "text")
                .put("text", text),
        )
        images.orEmpty().forEach { (bytes, mime) ->
            val b64 = Base64.encodeToString(bytes, Base64.NO_WRAP)
            val imageMime = mime.substringBefore(';').ifBlank { "image/jpeg" }
            parts.put(
                JSONObject()
                    .put("type", "image_url")
                    .put(
                        "image_url",
                        JSONObject()
                            .put("url", "data:$imageMime;base64,$b64")
                            .put("detail", "auto"),
                    ),
            )
        }
        if (audio != null && allowAudioAsImageUrl) {
            val (bytes, mime) = audio
            val b64 = Base64.encodeToString(bytes, Base64.NO_WRAP)
            parts.put(
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
        return if (parts.length() == 1) text else parts
    }

    private fun postJson(
        url: String,
        payload: JSONObject,
        headers: Map<String, String>,
        cancellationKey: String? = null,
    ): String {
        val body = payload.toString().toRequestBody(JSON_MEDIA_TYPE)
        val builder =
            Request
                .Builder()
                .url(url)
                .header("Content-Type", "application/json")
                .post(body)
        headers.forEach { (name, value) -> builder.header(name, value) }
        return execute(builder.build(), cancellationKey)
    }

    private fun execute(
        request: Request,
        cancellationKey: String? = null,
    ): String {
        val call = httpClient.newCall(request)
        if (cancellationKey != null) {
            activeCalls[cancellationKey]?.cancel()
            activeCalls[cancellationKey] = call
        }
        return try {
            runCall(call)
        } finally {
            if (cancellationKey != null) {
                activeCalls.remove(cancellationKey, call)
            }
        }
    }

    private fun runCall(call: Call): String {
        val result =
            runCatching {
                call.execute().use { response ->
                    response.code to response.body?.string().orEmpty()
                }
            }
        return result.fold(
            onSuccess = { (code, raw) ->
                ensureNotCanceled(call)
                requireSuccessfulHttp(code, raw)
            },
            onFailure = { error -> mapCallFailure(call, error) },
        )
    }

    private fun ensureNotCanceled(call: Call) {
        if (call.isCanceled()) {
            throw CancellationException("AI request cancelled")
        }
    }

    private fun requireSuccessfulHttp(
        code: Int,
        raw: String,
    ): String {
        if (code !in 200..299) {
            throw AiApiException("HTTP $code: ${raw.take(500)}")
        }
        return raw
    }

    private fun mapCallFailure(
        call: Call,
        error: Throwable,
    ): String {
        if (call.isCanceled() || error is CancellationException) {
            throw CancellationException("AI request cancelled", error)
        }
        throw AiApiException(error.message ?: "Network error", error)
    }

    private fun parseOpenAiChatResponse(raw: String): String {
        val data = parseJsonObject(raw)
        val failure = openAiChatFailure(data)
        if (failure != null) {
            throw AiApiException(failure)
        }
        val choices = data.getJSONArray("choices")
        val message = choices.getJSONObject(0).optJSONObject("message")
        return stripMarkdownFences(extractMessageContent(message?.opt("content")))
    }

    private fun openAiChatFailure(data: JSONObject): String? {
        if (data.has("error")) {
            return errorMessage(data.get("error"))
        }
        val choices = data.optJSONArray("choices")
        if (choices == null || choices.length() == 0) {
            return "No choices in API response"
        }
        val message = choices.getJSONObject(0).optJSONObject("message")
        val assistantText = extractMessageContent(message?.opt("content"))
        return if (assistantText.isBlank()) "Empty response from model" else null
    }

    private fun parseWhisperResponse(raw: String): String {
        val data = parseJsonObject(raw)
        if (data.has("error")) {
            throw AiApiException(errorMessage(data.get("error")))
        }
        val text = data.optString("text").trim()
        if (text.isBlank()) {
            throw AiApiException("Empty transcription from model")
        }
        return text
    }

    private fun parseAnthropicResponse(raw: String): String {
        val data = parseJsonObject(raw)
        val failure = anthropicFailure(data)
        if (failure != null) {
            throw AiApiException(failure)
        }
        val content = data.getJSONArray("content")
        val texts = mutableListOf<String>()
        for (i in 0 until content.length()) {
            val part = content.optJSONObject(i) ?: continue
            if (part.optString("type") == "text") {
                texts.add(part.optString("text"))
            }
        }
        return stripMarkdownFences(texts.joinToString("\n").trim())
    }

    private fun anthropicFailure(data: JSONObject): String? {
        if (data.has("error")) {
            return errorMessage(data.get("error"))
        }
        val content = data.optJSONArray("content")
        if (content == null || content.length() == 0) {
            return "No content in Anthropic response"
        }
        val texts = mutableListOf<String>()
        for (i in 0 until content.length()) {
            val part = content.optJSONObject(i) ?: continue
            if (part.optString("type") == "text") {
                texts.add(part.optString("text"))
            }
        }
        return if (texts.joinToString("\n").trim().isBlank()) {
            "Empty response from model"
        } else {
            null
        }
    }

    private fun parseGeminiResponse(raw: String): String {
        val data = parseJsonObject(raw)
        val failure = geminiFailure(data)
        if (failure != null) {
            throw AiApiException(failure)
        }
        val candidates = data.getJSONArray("candidates")
        val parts = candidates.getJSONObject(0).optJSONObject("content")?.optJSONArray("parts")
        val texts = mutableListOf<String>()
        if (parts != null) {
            for (i in 0 until parts.length()) {
                val part = parts.optJSONObject(i) ?: continue
                if (part.has("text")) {
                    texts.add(part.optString("text"))
                }
            }
        }
        return stripMarkdownFences(texts.joinToString("\n").trim())
    }

    private fun geminiFailure(data: JSONObject): String? {
        if (data.has("error")) {
            return errorMessage(data.get("error"))
        }
        val candidates = data.optJSONArray("candidates")
        if (candidates == null || candidates.length() == 0) {
            return "No candidates in Gemini response"
        }
        val parts = candidates.getJSONObject(0).optJSONObject("content")?.optJSONArray("parts")
        if (parts == null || parts.length() == 0) {
            return "Empty response from model"
        }
        val texts = mutableListOf<String>()
        for (i in 0 until parts.length()) {
            val part = parts.optJSONObject(i) ?: continue
            if (part.has("text")) {
                texts.add(part.optString("text"))
            }
        }
        return if (texts.joinToString("\n").trim().isBlank()) {
            "Empty response from model"
        } else {
            null
        }
    }

    private fun parseJsonObject(raw: String): JSONObject = try {
        JSONObject(raw)
    } catch (e: JSONException) {
        throw AiApiException("Invalid JSON response: ${raw.take(500)}", e)
    }

    private fun errorMessage(err: Any): String = when (err) {
        is JSONObject -> err.optString("message", err.toString())
        else -> err.toString()
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

    private fun filenameForMime(mime: String): String {
        val lower = mime.lowercase()
        val ext =
            when {
                "wav" in lower -> ".wav"
                "mpeg" in lower || "mp3" in lower -> ".mp3"
                "mp4" in lower || "m4a" in lower -> ".m4a"
                "ogg" in lower -> ".ogg"
                "webm" in lower -> ".webm"
                else -> ".bin"
            }
        return "audio$ext"
    }

    companion object {
        fun missingKeyMessage(provider: String = AiConfig.provider): String {
            val file =
                when (provider) {
                    AiConfig.PROVIDER_OPENAI -> "api-keys/openai-api-key.txt"
                    AiConfig.PROVIDER_ANTHROPIC -> "api-keys/anthropic-api-key.txt"
                    AiConfig.PROVIDER_GEMINI -> "api-keys/gemini-api-key.txt"
                    AiConfig.PROVIDER_BOTHUB_RU -> "api-keys/bothub-ru-api-key.txt"
                    else -> "api-keys/bothub-api-key.txt"
                }
            return "AI API key is missing for provider '$provider'. " +
                "Create $file (or set the matching env var), then rebuild the APK."
        }

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
