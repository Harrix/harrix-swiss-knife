package dev.harrix.hsk.ai

import java.io.InterruptedIOException
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

/**
 * User-facing AI network error messages.
 * Mirrors desktop `harrix_swiss_knife.integrations.ai.network_errors`.
 */
object AiNetworkErrors {
    const val BOTHUB_UNREACHABLE_MSG =
        "Cannot connect to BotHub. This is usually caused by a VPN " +
            "or an unstable internet connection. Please disable the VPN and try again."

    const val AI_NO_RESPONSE_MSG =
        "Reached the AI server, but it did not respond in time. Please try again."

    enum class NetworkFailureKind {
        /** DNS / TCP connect failed — server not reachable. */
        Unreachable,

        /** Connection started, but the response timed out. */
        NoResponse,
    }

    fun isBothubHost(urlOrHost: String): Boolean {
        val raw = urlOrHost.trim()
        if (raw.isEmpty()) {
            return false
        }
        val host =
            raw
                .substringAfter("://", raw)
                .substringBefore('/')
                .substringBefore(':')
                .trim()
                .trimEnd('.')
                .lowercase()
        return host == "bothub.chat" ||
            host.endsWith(".bothub.chat") ||
            host == "bothub.ru" ||
            host.endsWith(".bothub.ru")
    }

    fun isConnectTimeout(error: Throwable): Boolean {
        var current: Throwable? = error
        while (current != null) {
            when (current) {
                is SocketTimeoutException,
                is ConnectException,
                is UnknownHostException,
                -> return true
            }
            if (isConnectTimeoutMessage(current.message.orEmpty())) {
                return true
            }
            current = current.cause
        }
        return false
    }

    fun isConnectTimeoutMessage(text: String): Boolean {
        val lower = text.lowercase()
        return CONNECT_TIMEOUT_MARKERS.any { it in lower }
    }

    /**
     * Classifies a throwable chain as unreachable vs no-response.
     * Returns null for user cancels and non-network failures.
     */
    fun networkFailureKind(error: Throwable): NetworkFailureKind? {
        var current: Throwable? = error
        while (current != null) {
            kindForThrowable(current)?.let { return it }
            current = current.cause
        }
        return null
    }

    private fun kindForThrowable(error: Throwable): NetworkFailureKind? = when (error) {
        is UnknownHostException,
        is ConnectException,
        -> NetworkFailureKind.Unreachable

        is SocketTimeoutException ->
            kindFromMessage(error.message.orEmpty()) ?: NetworkFailureKind.NoResponse

        is InterruptedIOException -> {
            val msg = error.message.orEmpty()
            if (NO_RESPONSE_MARKERS.any { it in msg.lowercase() } || isConnectTimeoutMessage(msg)) {
                kindFromMessage(msg) ?: NetworkFailureKind.NoResponse
            } else {
                null
            }
        }

        else -> kindFromMessage(error.message.orEmpty())
    }

    private fun kindFromMessage(message: String): NetworkFailureKind? {
        val lower = message.lowercase()
        if (lower.isEmpty()) {
            return null
        }
        if (CONNECT_FAILURE_MARKERS.any { it in lower }) {
            return NetworkFailureKind.Unreachable
        }
        if (NO_RESPONSE_MARKERS.any { it in lower }) {
            return NetworkFailureKind.NoResponse
        }
        return null
    }

    fun remapBothubNetworkError(
        message: String,
        error: Throwable? = null,
        urlOrHost: String? = null,
        provider: String? = null,
    ): String {
        val kind = error?.let { networkFailureKind(it) }
        if (kind == NetworkFailureKind.NoResponse) {
            return AI_NO_RESPONSE_MSG
        }
        if (!isBothubContext(urlOrHost = urlOrHost, provider = provider)) {
            return if (kind == NetworkFailureKind.Unreachable && message.isBlank()) {
                BOTHUB_UNREACHABLE_MSG
            } else {
                message
            }
        }
        if (kind == NetworkFailureKind.Unreachable) {
            return BOTHUB_UNREACHABLE_MSG
        }
        if (error != null && isConnectTimeout(error)) {
            return BOTHUB_UNREACHABLE_MSG
        }
        return if (isConnectTimeoutMessage(message)) {
            BOTHUB_UNREACHABLE_MSG
        } else {
            message
        }
    }

    /** True when the AI host could not be reached or did not answer in time. */
    fun isAiUnreachableError(message: String): Boolean {
        val text = message.trim()
        if (text.isEmpty()) {
            return false
        }
        if (BOTHUB_UNREACHABLE_MSG in text || AI_NO_RESPONSE_MSG in text) {
            return true
        }
        if (isConnectTimeoutMessage(text)) {
            return true
        }
        val lower = text.lowercase()
        return UNREACHABLE_MARKERS.any { it in lower }
    }

    private fun isBothubContext(
        urlOrHost: String?,
        provider: String?,
    ): Boolean {
        if (!urlOrHost.isNullOrBlank() && isBothubHost(urlOrHost)) {
            return true
        }
        if (provider.isNullOrBlank()) {
            return false
        }
        return AiConfig.isBothubRouter(provider)
    }

    private val CONNECT_TIMEOUT_MARKERS =
        listOf(
            "10060",
            "did not properly respond after a period of time",
            "connected host has failed to respond",
            "timed out",
            "timeout",
            "etimedout",
            "failed to connect",
            "unable to resolve host",
        )

    private val CONNECT_FAILURE_MARKERS =
        listOf(
            "failed to connect",
            "unable to resolve host",
            "unknown host",
            "connection refused",
            "network is unreachable",
            "no address associated",
            "connect timed out",
            "failed to connect to",
        )

    private val NO_RESPONSE_MARKERS =
        listOf(
            "timed out",
            "timeout",
            "etimedout",
            "did not properly respond after a period of time",
            "connected host has failed to respond",
            "read timed out",
            "call timed out",
        )

    private val UNREACHABLE_MARKERS =
        listOf(
            "cannot connect",
            "network error",
            "unreachable",
            "failed to connect",
            "unable to resolve host",
            "unknown host",
            "did not respond in time",
        )
}
