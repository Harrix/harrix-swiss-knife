package dev.harrix.hsk.gallery

import android.net.Uri

data class CameraPhoto(
    val id: Long,
    val uri: Uri,
    val displayName: String?,
    val dateAddedEpochSec: Long,
    /** Capture time in epoch milliseconds; falls back to [dateAddedEpochSec] when unknown. */
    val dateTakenEpochMs: Long,
    val sizeBytes: Long,
)
