package dev.harrix.hsk.dropboxsync

import android.content.Context
import android.net.Uri
import android.util.Base64
import dev.harrix.hsk.BuildConfig
import okhttp3.FormBody
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.security.MessageDigest
import java.security.SecureRandom
import java.util.concurrent.TimeUnit

/** Dropbox OAuth 2.0 Authorization Code + PKCE helper. */
class DropboxAuthManager(
    context: Context,
    private val preferences: DropboxSyncPreferences = DropboxSyncPreferences(context),
    private val httpClient: OkHttpClient =
        OkHttpClient
            .Builder()
            .connectTimeout(20, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build(),
) {
    fun resolveAppKey(): String {
        val override = preferences.getAppKeyOverride()
        if (override.isNotEmpty()) {
            return override
        }
        return BuildConfig.DROPBOX_APP_KEY.trim()
    }

    fun isConfigured(): Boolean = resolveAppKey().isNotEmpty()

    fun isConnected(): Boolean = preferences.isConnected()

    fun accountLabel(): String {
        val name = preferences.getAccountDisplayName().orEmpty()
        val email = preferences.getAccountEmail().orEmpty()
        return when {
            name.isNotEmpty() && email.isNotEmpty() -> "$name ($email)"
            name.isNotEmpty() -> name
            email.isNotEmpty() -> email
            else -> ""
        }
    }

    fun buildAuthorizeUri(): Uri {
        val appKey = resolveAppKey()
        require(appKey.isNotEmpty()) { "Dropbox App Key is not configured" }
        val verifier = createCodeVerifier()
        preferences.setPendingPkceVerifier(verifier)
        val challenge = createCodeChallenge(verifier)
        return Uri
            .parse("https://www.dropbox.com/oauth2/authorize")
            .buildUpon()
            .appendQueryParameter("client_id", appKey)
            .appendQueryParameter("response_type", "code")
            .appendQueryParameter("token_access_type", "offline")
            .appendQueryParameter("redirect_uri", DropboxSyncPreferences.REDIRECT_URI)
            .appendQueryParameter("code_challenge", challenge)
            .appendQueryParameter("code_challenge_method", "S256")
            .build()
    }

    fun handleRedirect(uri: Uri): Result<Unit> {
        if (uri.scheme != "hsk-dropbox" || uri.host != "oauth") {
            return Result.failure(IllegalArgumentException("Unexpected redirect URI"))
        }
        val error = uri.getQueryParameter("error")
        if (!error.isNullOrBlank()) {
            val description = uri.getQueryParameter("error_description").orEmpty()
            return Result.failure(IllegalStateException(description.ifEmpty { error }))
        }
        val code = uri.getQueryParameter("code")
        if (code.isNullOrBlank()) {
            return Result.failure(IllegalStateException("Missing authorization code"))
        }
        return runCatching { exchangeCode(code) }
    }

    fun disconnect() {
        preferences.clearAccount()
        preferences.setPendingPkceVerifier(null)
    }

    @Synchronized
    fun getValidAccessToken(): String {
        val access = preferences.getAccessToken()
        val expiresAt = preferences.getTokenExpiresAtMs()
        val stillValid = !access.isNullOrBlank() && expiresAt > System.currentTimeMillis() + 60_000L
        if (stillValid) {
            return access!!
        }
        val refresh = preferences.getRefreshToken()
        if (refresh.isNullOrBlank()) {
            if (!access.isNullOrBlank()) {
                return access
            }
            error("Dropbox is not connected")
        }
        refreshAccessToken(refresh)
        return preferences.getAccessToken()
            ?: error("Dropbox refresh did not return an access token")
    }

    private fun exchangeCode(code: String) {
        val verifier =
            preferences.getPendingPkceVerifier()
                ?: error("Missing PKCE verifier")
        val appKey = resolveAppKey()
        val body =
            FormBody
                .Builder()
                .add("code", code)
                .add("grant_type", "authorization_code")
                .add("client_id", appKey)
                .add("redirect_uri", DropboxSyncPreferences.REDIRECT_URI)
                .add("code_verifier", verifier)
                .build()
        val request =
            Request
                .Builder()
                .url("https://api.dropboxapi.com/oauth2/token")
                .post(body)
                .build()
        httpClient.newCall(request).execute().use { response ->
            val payload = response.body?.string().orEmpty()
            if (!response.isSuccessful) {
                error("Token exchange failed (${response.code}): $payload")
            }
            storeTokenResponse(JSONObject(payload))
        }
        preferences.setPendingPkceVerifier(null)
    }

    private fun refreshAccessToken(refreshToken: String) {
        val appKey = resolveAppKey()
        val body =
            FormBody
                .Builder()
                .add("grant_type", "refresh_token")
                .add("refresh_token", refreshToken)
                .add("client_id", appKey)
                .build()
        val request =
            Request
                .Builder()
                .url("https://api.dropboxapi.com/oauth2/token")
                .post(body)
                .build()
        httpClient.newCall(request).execute().use { response ->
            val payload = response.body?.string().orEmpty()
            if (!response.isSuccessful) {
                error("Token refresh failed (${response.code}): $payload")
            }
            storeTokenResponse(JSONObject(payload), fallbackRefresh = refreshToken)
        }
    }

    private fun storeTokenResponse(
        json: JSONObject,
        fallbackRefresh: String? = null,
    ) {
        val access = json.getString("access_token")
        val refresh = json.optString("refresh_token").ifBlank { fallbackRefresh }
        val expiresIn = json.optLong("expires_in", 14_400L)
        preferences.saveTokens(
            accessToken = access,
            refreshToken = refresh,
            expiresAtMs = System.currentTimeMillis() + expiresIn * 1000L,
        )
    }

    private fun createCodeVerifier(): String {
        val bytes = ByteArray(32)
        SecureRandom().nextBytes(bytes)
        return Base64.encodeToString(bytes, Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING)
    }

    private fun createCodeChallenge(verifier: String): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(verifier.toByteArray(Charsets.US_ASCII))
        return Base64.encodeToString(digest, Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING)
    }
}
