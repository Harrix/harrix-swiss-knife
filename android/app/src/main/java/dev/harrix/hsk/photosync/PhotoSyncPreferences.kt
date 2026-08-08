package dev.harrix.hsk.photosync

import android.content.Context

class PhotoSyncPreferences(
    context: Context,
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun getHost(): String = prefs.getString(KEY_HOST, "")?.trim().orEmpty()

    fun setHost(value: String) {
        prefs.edit().putString(KEY_HOST, value.trim()).apply()
    }

    fun getPort(): Int = prefs.getInt(KEY_PORT, DEFAULT_PORT)

    fun setPort(value: Int) {
        prefs.edit().putInt(KEY_PORT, value.coerceIn(1, 65535)).apply()
    }

    fun getToken(): String = prefs.getString(KEY_TOKEN, "")?.trim().orEmpty()

    fun setToken(value: String) {
        prefs.edit().putString(KEY_TOKEN, value.trim()).apply()
    }

    fun saveConnection(
        host: String,
        port: Int,
        token: String,
    ) {
        prefs
            .edit()
            .putString(KEY_HOST, host.trim())
            .putInt(KEY_PORT, port.coerceIn(1, 65535))
            .putString(KEY_TOKEN, token.trim())
            .apply()
    }

    companion object {
        const val DEFAULT_PORT = 17865
        private const val PREFS_NAME = "photo_sync"
        private const val KEY_HOST = "host"
        private const val KEY_PORT = "port"
        private const val KEY_TOKEN = "token"
    }
}
