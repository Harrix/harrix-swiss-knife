package dev.harrix.hsk.gallery

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import android.provider.Settings
import androidx.core.content.ContextCompat

object GalleryPermissions {
    fun requiredPermission(): String = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        Manifest.permission.READ_MEDIA_IMAGES
    } else {
        Manifest.permission.READ_EXTERNAL_STORAGE
    }

    fun requiredVideoPermission(): String = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        Manifest.permission.READ_MEDIA_VIDEO
    } else {
        Manifest.permission.READ_EXTERNAL_STORAGE
    }

    fun hasPhotosPermission(context: Context): Boolean = ContextCompat.checkSelfPermission(
        context,
        requiredPermission(),
    ) == PackageManager.PERMISSION_GRANTED

    fun hasVideosPermission(context: Context): Boolean = ContextCompat.checkSelfPermission(
        context,
        requiredVideoPermission(),
    ) == PackageManager.PERMISSION_GRANTED

    fun canManageMedia(context: Context): Boolean = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && MediaStore.canManageMedia(context)

    fun isManageMediaAvailable(): Boolean = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S

    fun appDetailsSettingsIntent(context: Context): Intent = Intent(
        Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
        Uri.fromParts("package", context.packageName, null),
    )

    fun manageMediaSettingsIntent(context: Context): Intent? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        Intent(Settings.ACTION_REQUEST_MANAGE_MEDIA).apply {
            data = Uri.parse("package:${context.packageName}")
        }
    } else {
        null
    }
}
