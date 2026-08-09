package dev.harrix.hsk.photosync

import java.io.IOException
import java.net.ConnectException
import java.net.NoRouteToHostException
import java.net.SocketException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

/** Desktop receiver closed, restarted, or is unreachable on the LAN. */
class PhotoSyncDesktopGoneException(
    message: String = DEFAULT_MESSAGE,
) : IOException(message) {
    companion object {
        const val DEFAULT_MESSAGE =
            "Desktop Photo sync stopped. Open Photo sync on the computer and scan the QR again if needed."
    }
}

object PhotoSyncNetwork {
    private val DESKTOP_GONE_HTTP = Regex("""HTTP (401|403|404|502|503|504)\b""")
    private val DESKTOP_GONE_PHRASES =
        listOf(
            "failed to connect",
            "connection refused",
            "connection reset",
            "connection closed",
            "software caused connection abort",
            "unexpected end of stream",
            "stream was reset",
            "handshake failed",
            "handshake rejected",
            "desktop receiver is not ready",
        )

    fun isDesktopUnavailable(error: Throwable): Boolean {
        var current: Throwable? = error
        while (current != null) {
            if (isUnavailableType(current) || messageLooksUnavailable(current.message)) {
                return true
            }
            current = current.cause
        }
        return false
    }

    private fun isUnavailableType(error: Throwable): Boolean = error is PhotoSyncDesktopGoneException ||
        error is ConnectException ||
        error is UnknownHostException ||
        error is NoRouteToHostException ||
        error is SocketTimeoutException ||
        error is SocketException

    private fun messageLooksUnavailable(message: String?): Boolean {
        if (message.isNullOrBlank()) {
            return false
        }
        val lower = message.lowercase()
        if (DESKTOP_GONE_PHRASES.any { it in lower }) {
            return true
        }
        return DESKTOP_GONE_HTTP.containsMatchIn(message)
    }
}
