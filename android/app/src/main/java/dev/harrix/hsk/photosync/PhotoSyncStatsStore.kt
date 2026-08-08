package dev.harrix.hsk.photosync

import android.content.Context

data class PhotoSyncLifetimeStats(
    val syncCount: Long = 0L,
    val photosUploaded: Long = 0L,
    val bytesUploaded: Long = 0L,
)

class PhotoSyncStatsStore(
    context: Context,
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun load(): PhotoSyncLifetimeStats = PhotoSyncLifetimeStats(
        syncCount = prefs.getLong(KEY_SYNC_COUNT, 0L).coerceAtLeast(0L),
        photosUploaded = prefs.getLong(KEY_PHOTOS, 0L).coerceAtLeast(0L),
        bytesUploaded = prefs.getLong(KEY_BYTES, 0L).coerceAtLeast(0L),
    )

    fun recordSession(
        photosUploaded: Int,
        bytesUploaded: Long,
    ) {
        val current = load()
        prefs
            .edit()
            .putLong(KEY_SYNC_COUNT, current.syncCount + 1L)
            .putLong(KEY_PHOTOS, current.photosUploaded + photosUploaded.coerceAtLeast(0))
            .putLong(KEY_BYTES, current.bytesUploaded + bytesUploaded.coerceAtLeast(0L))
            .apply()
    }

    fun reset() {
        prefs
            .edit()
            .putLong(KEY_SYNC_COUNT, 0L)
            .putLong(KEY_PHOTOS, 0L)
            .putLong(KEY_BYTES, 0L)
            .apply()
    }

    companion object {
        private const val PREFS_NAME = "photo_sync_stats"
        private const val KEY_SYNC_COUNT = "sync_count"
        private const val KEY_PHOTOS = "photos_uploaded"
        private const val KEY_BYTES = "bytes_uploaded"
    }
}
