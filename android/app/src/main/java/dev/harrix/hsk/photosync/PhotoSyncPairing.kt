package dev.harrix.hsk.photosync

import android.net.Uri

data class PhotoSyncEndpoint(
    val host: String,
    val port: Int,
    val token: String,
)

object PhotoSyncPairing {
    private val HOST_PORT = Regex("""^([^:\s]+):(\d{1,5})$""")

    fun parse(raw: String): PhotoSyncEndpoint? {
        val text = raw.trim()
        if (text.isEmpty()) {
            return null
        }
        val uri =
            when {
                text.startsWith("hsk-photo-sync://", ignoreCase = true) -> Uri.parse(text)

                text.startsWith("http://", ignoreCase = true) ||
                    text.startsWith("https://", ignoreCase = true) -> Uri.parse(text)

                else -> null
            }
        if (uri != null) {
            val host = uri.host?.trim().orEmpty()
            val port =
                when {
                    uri.port > 0 -> uri.port
                    else -> PhotoSyncPreferences.DEFAULT_PORT
                }
            val token =
                uri.getQueryParameter("token")?.trim().orEmpty()
                    .ifEmpty { uri.getQueryParameter("pin")?.trim().orEmpty() }
            if (host.isNotEmpty() && token.isNotEmpty()) {
                return PhotoSyncEndpoint(host = host, port = port, token = token)
            }
        }
        val match = HOST_PORT.matchEntire(text) ?: return null
        return PhotoSyncEndpoint(
            host = match.groupValues[1],
            port = match.groupValues[2].toIntOrNull() ?: return null,
            token = "",
        )
    }
}
