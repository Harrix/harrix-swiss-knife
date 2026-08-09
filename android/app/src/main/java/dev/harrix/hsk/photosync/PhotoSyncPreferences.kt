package dev.harrix.hsk.photosync

import android.content.Context

class PhotoSyncPreferences(
    context: Context,
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun getHost(): String = prefs.getString(KEY_HOST, "")?.trim().orEmpty()

    fun getPort(): Int = prefs.getInt(KEY_PORT, DEFAULT_PORT)

    fun getToken(): String = prefs.getString(KEY_TOKEN, "")?.trim().orEmpty()

    fun getConfirmCode(): String = prefs.getString(KEY_CONFIRM_CODE, "")?.trim().orEmpty()

    fun getEndpoint(): PhotoSyncEndpoint? {
        val host = getHost()
        val token = getToken()
        val confirmCode = getConfirmCode()
        if (host.isEmpty() || token.isEmpty() || !PhotoSyncPairing.isConfirmCode(confirmCode)) {
            return null
        }
        return PhotoSyncEndpoint(
            host = host,
            port = getPort(),
            token = token,
            confirmCode = confirmCode,
        )
    }

    fun saveConnection(endpoint: PhotoSyncEndpoint) {
        prefs
            .edit()
            .putString(KEY_HOST, endpoint.host.trim())
            .putInt(KEY_PORT, endpoint.port.coerceIn(1, 65535))
            .putString(KEY_TOKEN, endpoint.token.trim())
            .putString(KEY_CONFIRM_CODE, endpoint.confirmCode.trim())
            .apply()
    }

    fun clearConnection() {
        prefs
            .edit()
            .remove(KEY_HOST)
            .remove(KEY_PORT)
            .remove(KEY_TOKEN)
            .remove(KEY_CONFIRM_CODE)
            .apply()
    }

    companion object {
        const val DEFAULT_PORT = 17865
        private const val PREFS_NAME = "photo_sync"
        private const val KEY_HOST = "host"
        private const val KEY_PORT = "port"
        private const val KEY_TOKEN = "token"
        private const val KEY_CONFIRM_CODE = "confirm_code"
    }
}
