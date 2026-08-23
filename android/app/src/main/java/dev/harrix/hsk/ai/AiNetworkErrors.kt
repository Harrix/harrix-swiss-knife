package dev.harrix.hsk.ai

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

    fun remapBothubNetworkError(
        message: String,
        error: Throwable? = null,
        urlOrHost: String? = null,
        provider: String? = null,
    ): String {
        if (!isBothubContext(urlOrHost = urlOrHost, provider = provider)) {
            return message
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
}
