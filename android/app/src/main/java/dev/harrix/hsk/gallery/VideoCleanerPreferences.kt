package dev.harrix.hsk.gallery

import android.content.Context

/** Persisted Video Cleaner prefs (lifetime delete totals). */
class VideoCleanerPreferences(
    context: Context,
) {
    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun totalDeletedCount(): Int = prefs.getInt(KEY_TOTAL_DELETED_COUNT, 0)

    fun totalFreedBytes(): Long = prefs.getLong(KEY_TOTAL_FREED_BYTES, 0L)

    /** Records successful deletes toward all-time Video Cleaner totals. */
    fun recordDeletedVideos(
        count: Int,
        sizeBytes: Long,
    ) {
        if (count <= 0 && sizeBytes <= 0L) {
            return
        }
        adjustLifetimeDeleteStats(deletedDelta = count, freedBytesDelta = sizeBytes)
    }

    private fun adjustLifetimeDeleteStats(
        deletedDelta: Int,
        freedBytesDelta: Long,
    ) {
        synchronized(this) {
            val deleted = (totalDeletedCount() + deletedDelta).coerceAtLeast(0)
            val freed = (totalFreedBytes() + freedBytesDelta).coerceAtLeast(0L)
            prefs
                .edit()
                .putInt(KEY_TOTAL_DELETED_COUNT, deleted)
                .putLong(KEY_TOTAL_FREED_BYTES, freed)
                .apply()
        }
    }

    companion object {
        private const val PREFS_NAME = "video_cleaner"
        private const val KEY_TOTAL_DELETED_COUNT = "total_deleted_count"
        private const val KEY_TOTAL_FREED_BYTES = "total_freed_bytes"
    }
}
