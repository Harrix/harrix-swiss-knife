package dev.harrix.hsk.photosync

import android.net.Uri
import kotlin.random.Random

data class PhotoSyncEndpoint(
    val host: String,
    val port: Int,
    val token: String,
    val confirmCode: String,
)

object PhotoSyncPairing {
    private const val CHOICE_COUNT = 4
    private const val CODE_MIN = 10
    private const val CODE_MAX = 99

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
            } ?: return null

        val host = uri.host?.trim().orEmpty()
        val port =
            when {
                uri.port > 0 -> uri.port
                else -> PhotoSyncPreferences.DEFAULT_PORT
            }
        val token =
            uri.getQueryParameter("token")?.trim().orEmpty()
                .ifEmpty { uri.getQueryParameter("pin")?.trim().orEmpty() }
        val confirmCode =
            uri.getQueryParameter("code")?.trim().orEmpty()
                .ifEmpty { uri.getQueryParameter("confirmCode")?.trim().orEmpty() }
        if (host.isEmpty() || token.isEmpty() || !isConfirmCode(confirmCode)) {
            return null
        }
        return PhotoSyncEndpoint(
            host = host,
            port = port,
            token = token,
            confirmCode = confirmCode,
        )
    }

    fun buildConfirmChoices(
        correct: String,
        random: Random = Random.Default,
    ): List<String> {
        val choices = linkedSetOf(correct)
        while (choices.size < CHOICE_COUNT) {
            choices.add(random.nextInt(CODE_MIN, CODE_MAX + 1).toString())
        }
        return choices.shuffled(random)
    }

    fun isConfirmCode(value: String): Boolean {
        val code = value.trim()
        val number = code.toIntOrNull() ?: return false
        return number in CODE_MIN..CODE_MAX && code.length == 2
    }
}
