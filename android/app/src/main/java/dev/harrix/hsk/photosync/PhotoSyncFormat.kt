package dev.harrix.hsk.photosync

import java.util.Locale
import kotlin.math.max

object PhotoSyncFormat {
    private const val KB = 1024.0
    private const val MB = KB * 1024.0
    private const val GB = MB * 1024.0

    fun formatBytes(bytes: Long): String {
        val value = max(0L, bytes).toDouble()
        return when {
            value >= GB -> String.format(Locale.US, "%.2f GB", value / GB)
            value >= MB -> String.format(Locale.US, "%.1f MB", value / MB)
            value >= KB -> String.format(Locale.US, "%.0f KB", value / KB)
            else -> "$bytes B"
        }
    }

    fun formatElapsed(elapsedMs: Long): String {
        val totalSec = max(0L, elapsedMs) / 1000L
        val hours = totalSec / 3600L
        val minutes = (totalSec % 3600L) / 60L
        val seconds = totalSec % 60L
        return if (hours > 0L) {
            String.format(Locale.US, "%d:%02d:%02d", hours, minutes, seconds)
        } else {
            String.format(Locale.US, "%d:%02d", minutes, seconds)
        }
    }
}
