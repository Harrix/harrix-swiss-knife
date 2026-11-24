package dev.harrix.hsk.dropboxsync

import android.content.Context

/** Global Dropbox Sync preferences (auth overrides, schedule, ignore list). */
class DropboxSyncPreferences(
    context: Context,
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun getAppKeyOverride(): String = prefs.getString(KEY_APP_KEY, "")?.trim().orEmpty()

    fun setAppKeyOverride(value: String?) {
        prefs
            .edit()
            .apply {
                val trimmed = value?.trim().orEmpty()
                if (trimmed.isEmpty()) {
                    remove(KEY_APP_KEY)
                } else {
                    putString(KEY_APP_KEY, trimmed)
                }
            }.apply()
    }

    fun getAccessToken(): String? = prefs.getString(KEY_ACCESS_TOKEN, null)

    fun getRefreshToken(): String? = prefs.getString(KEY_REFRESH_TOKEN, null)

    fun getTokenExpiresAtMs(): Long = prefs.getLong(KEY_TOKEN_EXPIRES_AT, 0L)

    fun getAccountDisplayName(): String? = prefs.getString(KEY_ACCOUNT_NAME, null)

    fun getAccountEmail(): String? = prefs.getString(KEY_ACCOUNT_EMAIL, null)

    fun saveTokens(
        accessToken: String,
        refreshToken: String?,
        expiresAtMs: Long,
    ) {
        prefs
            .edit()
            .putString(KEY_ACCESS_TOKEN, accessToken)
            .apply {
                if (refreshToken.isNullOrBlank()) {
                    // Keep existing refresh token when Dropbox omits it on refresh.
                } else {
                    putString(KEY_REFRESH_TOKEN, refreshToken)
                }
            }.putLong(KEY_TOKEN_EXPIRES_AT, expiresAtMs)
            .apply()
    }

    fun saveAccount(
        displayName: String,
        email: String,
    ) {
        prefs
            .edit()
            .putString(KEY_ACCOUNT_NAME, displayName)
            .putString(KEY_ACCOUNT_EMAIL, email)
            .apply()
    }

    fun clearAccount() {
        prefs
            .edit()
            .remove(KEY_ACCESS_TOKEN)
            .remove(KEY_REFRESH_TOKEN)
            .remove(KEY_TOKEN_EXPIRES_AT)
            .remove(KEY_ACCOUNT_NAME)
            .remove(KEY_ACCOUNT_EMAIL)
            .apply()
    }

    fun isConnected(): Boolean = !getAccessToken().isNullOrBlank() || !getRefreshToken().isNullOrBlank()

    fun getGlobalIgnores(): String {
        val stored = prefs.getString(KEY_GLOBAL_IGNORES, null)
        return if (stored == null) {
            SyncIgnoreMatcher.DefaultPatterns.joinToString("\n")
        } else {
            stored
        }
    }

    fun setGlobalIgnores(value: String) {
        prefs.edit().putString(KEY_GLOBAL_IGNORES, value).apply()
    }

    fun getScheduleMinutes(): Int = prefs.getInt(KEY_SCHEDULE_MINUTES, 0)

    fun setScheduleMinutes(minutes: Int) {
        prefs.edit().putInt(KEY_SCHEDULE_MINUTES, minutes.coerceAtLeast(0)).apply()
    }

    fun isWifiOnly(): Boolean = prefs.getBoolean(KEY_WIFI_ONLY, true)

    fun setWifiOnly(value: Boolean) {
        prefs.edit().putBoolean(KEY_WIFI_ONLY, value).apply()
    }

    fun isRequireCharging(): Boolean = prefs.getBoolean(KEY_REQUIRE_CHARGING, false)

    fun setRequireCharging(value: Boolean) {
        prefs.edit().putBoolean(KEY_REQUIRE_CHARGING, value).apply()
    }

    fun isIgnoreBatteryLow(): Boolean = prefs.getBoolean(KEY_IGNORE_BATTERY_LOW, true)

    fun setIgnoreBatteryLow(value: Boolean) {
        prefs.edit().putBoolean(KEY_IGNORE_BATTERY_LOW, value).apply()
    }

    fun getPendingPkceVerifier(): String? = prefs.getString(KEY_PKCE_VERIFIER, null)

    fun setPendingPkceVerifier(value: String?) {
        prefs
            .edit()
            .apply {
                if (value.isNullOrBlank()) {
                    remove(KEY_PKCE_VERIFIER)
                } else {
                    putString(KEY_PKCE_VERIFIER, value)
                }
            }.apply()
    }

    fun resetSettingsToDefaults() {
        prefs
            .edit()
            .remove(KEY_APP_KEY)
            .remove(KEY_GLOBAL_IGNORES)
            .putInt(KEY_SCHEDULE_MINUTES, 0)
            .putBoolean(KEY_WIFI_ONLY, true)
            .putBoolean(KEY_REQUIRE_CHARGING, false)
            .putBoolean(KEY_IGNORE_BATTERY_LOW, true)
            .apply()
    }

    companion object {
        private const val PREFS_NAME = "dropbox_sync"
        private const val KEY_APP_KEY = "app_key"
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        private const val KEY_TOKEN_EXPIRES_AT = "token_expires_at"
        private const val KEY_ACCOUNT_NAME = "account_name"
        private const val KEY_ACCOUNT_EMAIL = "account_email"
        private const val KEY_GLOBAL_IGNORES = "global_ignores"
        private const val KEY_SCHEDULE_MINUTES = "schedule_minutes"
        private const val KEY_WIFI_ONLY = "wifi_only"
        private const val KEY_REQUIRE_CHARGING = "require_charging"
        private const val KEY_IGNORE_BATTERY_LOW = "ignore_battery_low"
        private const val KEY_PKCE_VERIFIER = "pkce_verifier"

        const val REDIRECT_URI = "hsk-dropbox://oauth"
    }
}
