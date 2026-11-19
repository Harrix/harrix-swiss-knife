package dev.harrix.hsk.ai

import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException

/**
 * BotHub.chat / BotHub.ru failover: parallel API probes and one API retry.
 * Mirrors desktop `harrix_swiss_knife.integrations.ai.bothub_failover`.
 */
object BothubFailover {
    fun prepare(
        forSpeech: Boolean = false,
        probe: (String) -> Boolean = ::probeBothubSite,
    ): String? {
        val preferred = preferredRouter(forSpeech)
        if (!AiConfig.isBothubRouter(preferred)) {
            return null
        }
        val alternate = AiConfig.otherBothubRouter(preferred)
        val hasAlternate = AiConfig.isUsableApiKey(AiConfig.apiKeyFor(alternate))

        if (isRouterMarkedDown(preferred) && hasAlternate) {
            return commitIfChanged(alternate, forSpeech)
        }

        val preferredUrl = probeUrl(preferred)
        if (!hasAlternate) {
            return if (probe(preferredUrl)) {
                clearRouterDown(preferred)
                commitIfChanged(preferred, forSpeech)
            } else {
                markRouterDown(preferred)
                null
            }
        }

        val (preferredUp, alternateUp) =
            raceProbes(
                preferredUrl = preferredUrl,
                alternateUrl = probeUrl(alternate),
                probe = probe,
            )
        if (preferredUp) {
            clearRouterDown(preferred)
            return commitIfChanged(preferred, forSpeech)
        }
        markRouterDown(preferred)
        if (alternateUp) {
            return commitIfChanged(alternate, forSpeech)
        }
        return null
    }

    /**
     * Switch to the other BotHub site after a failed API call.
     * Does not re-probe (would fail back to preferred). Returns whether to retry.
     */
    fun trySwitchAfterApiFailure(
        forSpeech: Boolean,
        errorMessage: String,
    ): Boolean {
        val current = if (forSpeech) AiConfig.speechProvider else AiConfig.provider
        if (!AiConfig.isBothubRouter(current)) {
            return false
        }
        if (!isApiFailoverError(errorMessage)) {
            return false
        }
        val alternate = AiConfig.otherBothubRouter(current)
        if (!AiConfig.isUsableApiKey(AiConfig.apiKeyFor(alternate))) {
            return false
        }
        markRouterDown(current)
        commitIfChanged(alternate, forSpeech)
        return true
    }

    fun isApiFailoverError(message: String): Boolean {
        val match = HTTP_STATUS_RE.find(message)
        if (match == null) {
            return true
        }
        val code = match.groupValues[1].toIntOrNull() ?: return true
        return code in FAILOVER_HTTP_STATUSES
    }

    fun markRouterDown(providerId: String) {
        if (AiConfig.isBothubRouter(providerId)) {
            routerDownUntil[AiConfig.normalizeProvider(providerId)] =
                System.currentTimeMillis() + NEGATIVE_CACHE_MS
        }
    }

    fun clearDownCache() {
        routerDownUntil.clear()
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

    fun probeUrl(providerId: String): String {
        val base = AiConfig.baseUrlFor(providerId).trimEnd('/')
        return "$base/models"
    }

    fun preferredRouter(forSpeech: Boolean): String {
        if (forSpeech) {
            val speech = BuildConfigSpeechProvider.trim()
            return if (speech.isEmpty()) {
                AiConfig.normalizeProvider(BuildConfigChatProvider)
            } else {
                AiConfig.normalizeProvider(speech)
            }
        }
        return AiConfig.normalizeProvider(BuildConfigChatProvider)
    }

    private fun commitIfChanged(
        providerId: String,
        forSpeech: Boolean,
    ): String? {
        val normalized = AiConfig.normalizeProvider(providerId)
        val current = if (forSpeech) AiConfig.speechProvider else AiConfig.provider
        if (current == normalized) {
            return null
        }
        val speechToWrite = AiConfig.speechProviderToPersistAfterSwitch(normalized)
        AiConfig.applyRouter(normalized, speechToWrite)
        return normalized
    }

    private fun raceProbes(
        preferredUrl: String,
        alternateUrl: String,
        probe: (String) -> Boolean,
    ): Pair<Boolean, Boolean> {
        val executor = Executors.newFixedThreadPool(2)
        try {
            val preferredFuture: Future<Boolean> = executor.submit<Boolean> { probe(preferredUrl) }
            val alternateFuture: Future<Boolean> = executor.submit<Boolean> { probe(alternateUrl) }
            return awaitProbeRace(preferredFuture, alternateFuture)
        } finally {
            executor.shutdownNow()
        }
    }

    private fun awaitProbeRace(
        preferredFuture: Future<Boolean>,
        alternateFuture: Future<Boolean>,
    ): Pair<Boolean, Boolean> {
        val deadlineNs = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(PROBE_WAIT_MS)
        var preferredUp = false
        var alternateUp = false
        var preferredDone = false
        var alternateDone = false

        while ((!preferredDone || !alternateDone) && System.nanoTime() < deadlineNs) {
            val preferredResult = pollPreferred(preferredFuture, preferredDone)
            if (preferredResult != null) {
                preferredDone = true
                preferredUp = preferredResult
                if (preferredUp) {
                    alternateFuture.cancel(true)
                    return true to alternateUp
                }
            }
            val alternateResult = pollAlternate(alternateFuture, alternateDone)
            if (alternateResult != null) {
                alternateDone = true
                alternateUp = alternateResult
            }
            if (preferredDone && !preferredUp && alternateDone) {
                return false to alternateUp
            }
            Thread.sleep(20L)
        }
        if (!preferredDone) {
            preferredFuture.cancel(true)
            preferredUp = false
        }
        if (!alternateDone) {
            alternateUp = resultOrFalse(alternateFuture)
        }
        return preferredUp to alternateUp
    }

    private fun pollPreferred(
        future: Future<Boolean>,
        alreadyDone: Boolean,
    ): Boolean? {
        if (alreadyDone || !future.isDone) {
            return null
        }
        return resultOrFalse(future)
    }

    private fun pollAlternate(
        future: Future<Boolean>,
        alreadyDone: Boolean,
    ): Boolean? {
        if (alreadyDone || !future.isDone) {
            return null
        }
        return resultOrFalse(future)
    }

    private fun resultOrFalse(future: Future<Boolean>): Boolean = try {
        future.get(0, TimeUnit.MILLISECONDS)
    } catch (_: TimeoutException) {
        false
    } catch (_: Exception) {
        false
    }

    private fun isRouterMarkedDown(providerId: String): Boolean {
        val key = AiConfig.normalizeProvider(providerId)
        val until = routerDownUntil[key] ?: return false
        if (System.currentTimeMillis() >= until) {
            routerDownUntil.remove(key)
            return false
        }
        return true
    }

    private fun clearRouterDown(providerId: String) {
        routerDownUntil.remove(AiConfig.normalizeProvider(providerId))
    }

    private val routerDownUntil = ConcurrentHashMap<String, Long>()

    private val probeClient: OkHttpClient by lazy {
        OkHttpClient
            .Builder()
            .connectTimeout(PROBE_TIMEOUT_SEC, TimeUnit.SECONDS)
            .readTimeout(PROBE_TIMEOUT_SEC, TimeUnit.SECONDS)
            .writeTimeout(PROBE_TIMEOUT_SEC, TimeUnit.SECONDS)
            .callTimeout(PROBE_TIMEOUT_SEC, TimeUnit.SECONDS)
            .build()
    }

    private val HTTP_STATUS_RE = Regex("""HTTP\s+(\d{3})\b""", RegexOption.IGNORE_CASE)
    private val FAILOVER_HTTP_STATUSES = setOf(401, 403, 408, 425, 429, 500, 502, 503, 504)

    // Bake-time preferred routers (not the live SharedPreferences override).
    private val BuildConfigChatProvider: String
        get() = dev.harrix.hsk.BuildConfig.AI_PROVIDER
    private val BuildConfigSpeechProvider: String
        get() = dev.harrix.hsk.BuildConfig.AI_SPEECH_PROVIDER

    private const val PROBE_TIMEOUT_SEC = 4L
    private const val PROBE_WAIT_MS = 4500L
    private const val NEGATIVE_CACHE_MS = 60_000L
    private const val PROBE_UA = "Harrix-Swiss-Knife/1.0 (AI router probe)"
}
