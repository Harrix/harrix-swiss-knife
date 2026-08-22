package dev.harrix.hsk.ai

import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * One-shot BotHub site failover when bothub.chat or bothub.ru is unreachable.
 * Mirrors desktop `harrix_swiss_knife.integrations.ai.bothub_failover`.
 */
object BothubFailover {
    fun prepare(
        forSpeech: Boolean = false,
        probe: (String) -> Boolean = ::probeBothubSite,
    ): String? {
        val current = if (forSpeech) AiConfig.speechProvider else AiConfig.provider
        if (!AiConfig.isBothubRouter(current)) {
            return null
        }
        val alternate = AiConfig.otherBothubRouter(current)
        if (!AiConfig.isUsableApiKey(AiConfig.apiKeyFor(alternate))) {
            return null
        }
        if (probe(probeUrl(current))) {
            return null
        }
        val speechToWrite = AiConfig.speechProviderToPersistAfterSwitch(alternate)
        AiConfig.applyRouter(alternate, speechToWrite)
        return alternate
    }

    fun probeBothubSite(url: String): Boolean {
        if (!url.startsWith("https://")) {
            return false
        }
        val request =
            Request
                .Builder()
                .url(url)
                .header("User-Agent", PROBE_UA)
                .get()
                .build()
        return try {
            probeClient.newCall(request).execute().use { response ->
                response.body?.source()?.request(64)
                true
            }
        } catch (_: IOException) {
            false
        } catch (_: IllegalArgumentException) {
            false
        }
    }

    private fun probeUrl(providerId: String): String = if (AiConfig.normalizeProvider(providerId) == AiConfig.PROVIDER_BOTHUB_RU) {
        PROBE_BOTHUB_RU
    } else {
        PROBE_BOTHUB
    }

    private val probeClient: OkHttpClient by lazy {
        OkHttpClient
            .Builder()
            .connectTimeout(PROBE_TIMEOUT_SEC, TimeUnit.SECONDS)
            .readTimeout(PROBE_TIMEOUT_SEC, TimeUnit.SECONDS)
            .writeTimeout(PROBE_TIMEOUT_SEC, TimeUnit.SECONDS)
            .callTimeout(PROBE_TIMEOUT_SEC, TimeUnit.SECONDS)
            .build()
    }

    private const val PROBE_BOTHUB = "https://bothub.chat/"
    private const val PROBE_BOTHUB_RU = "https://bothub.ru/"
    private const val PROBE_TIMEOUT_SEC = 5L
    private const val PROBE_UA = "Harrix-Swiss-Knife/1.0 (AI router probe)"
}
