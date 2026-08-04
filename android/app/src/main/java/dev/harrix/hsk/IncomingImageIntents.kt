package dev.harrix.hsk

import android.content.Intent
import android.net.Uri

/** Extracts an image [Uri] from VIEW / EDIT / SEND / SEND_MULTIPLE intents. */
object IncomingImageIntents {
    fun extractImageUri(intent: Intent?): Uri? {
        if (intent == null) {
            return null
        }
        return when (intent.action) {
            Intent.ACTION_VIEW,
            Intent.ACTION_EDIT,
            -> intent.data?.takeIf { looksLikeImage(intent, it) }

            Intent.ACTION_SEND -> {
                val stream =
                    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
                        intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
                    } else {
                        @Suppress("DEPRECATION")
                        intent.getParcelableExtra(Intent.EXTRA_STREAM) as? Uri
                    }
                stream?.takeIf { looksLikeImage(intent, it) }
            }

            Intent.ACTION_SEND_MULTIPLE -> {
                val streams =
                    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
                        intent.getParcelableArrayListExtra(Intent.EXTRA_STREAM, Uri::class.java)
                    } else {
                        @Suppress("DEPRECATION")
                        intent.getParcelableArrayListExtra(Intent.EXTRA_STREAM)
                    }
                streams
                    ?.firstOrNull()
                    ?.takeIf { looksLikeImage(intent, it) }
            }

            else -> null
        }
    }

    private fun looksLikeImage(
        intent: Intent,
        uri: Uri,
    ): Boolean {
        val type = intent.type?.lowercase()
        if (type != null && type.startsWith("image/")) {
            return true
        }
        val path = uri.path?.lowercase().orEmpty()
        return path.endsWith(".jpg") ||
            path.endsWith(".jpeg") ||
            path.endsWith(".png") ||
            path.endsWith(".webp") ||
            path.endsWith(".heic") ||
            path.endsWith(".gif") ||
            // VIEW/EDIT often omit type but still deliver an image content URI.
            intent.action == Intent.ACTION_VIEW ||
            intent.action == Intent.ACTION_EDIT
    }
}
