package dev.harrix.hsk.gallery

import android.net.Uri

data class CameraVideo(
    val id: Long,
    val uri: Uri,
    val displayName: String?,
    val dateAddedEpochSec: Long,
    val sizeBytes: Long,
)
