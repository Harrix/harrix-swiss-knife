package dev.harrix.hsk.photosync

import android.content.Context

/**
 * Caches SHA-256 digests keyed by media id + size so repeat syncs skip re-hashing.
 */
class PhotoSyncHashCache(
    context: Context,
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun get(
        mediaId: Long,
        sizeBytes: Long,
    ): String? {
        val raw = prefs.getString(key(mediaId), null) ?: return null
        val parts = raw.split('|', limit = 2)
        if (parts.size != 2) {
            return null
        }
        val size = parts[0].toLongOrNull() ?: return null
        if (size != sizeBytes) {
            return null
        }
        return parts[1].takeIf { it.length == 64 }
    }

    fun put(
        mediaId: Long,
        sizeBytes: Long,
        hash: String,
    ) {
        prefs.edit().putString(key(mediaId), "$sizeBytes|${hash.lowercase()}").apply()
    }

    private fun key(mediaId: Long): String = "m_$mediaId"

    companion object {
        private const val PREFS_NAME = "photo_sync_hashes"
    }
}
