package dev.harrix.hsk.gallery

import android.net.Uri

data class CameraPhoto(
    val id: Long,
    val uri: Uri,
    val displayName: String?,
)
