package dev.harrix.hsk.gallery

import android.content.ContentUris
import android.content.Context
import android.content.IntentSender
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import androidx.annotation.RequiresApi

class CameraGalleryRepository(
    private val context: Context,
) {
    fun loadCameraPhotos(): List<CameraPhoto> {
        val collection =
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL)
            } else {
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI
            }

        val projection =
            arrayOf(
                MediaStore.Images.Media._ID,
                MediaStore.Images.Media.DISPLAY_NAME,
            )

        val (selection, selectionArgs) = cameraFolderSelection()
        val sortOrder = "${MediaStore.Images.Media.DATE_ADDED} DESC"

        val photos = mutableListOf<CameraPhoto>()
        context.contentResolver
            .query(collection, projection, selection, selectionArgs, sortOrder)
            ?.use { cursor ->
                val idColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media._ID)
                val nameColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DISPLAY_NAME)
                while (cursor.moveToNext()) {
                    val id = cursor.getLong(idColumn)
                    val uri = ContentUris.withAppendedId(collection, id)
                    photos +=
                        CameraPhoto(
                            id = id,
                            uri = uri,
                            displayName = cursor.getString(nameColumn),
                        )
                }
            }
        return photos
    }

    fun canTrashWithoutPrompt(): Boolean =
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && MediaStore.canManageMedia(context)

    /**
     * Always use [createTrashRequest] on Android 11+.
     *
     * With [MediaStore.canManageMedia] granted, the system skips the confirmation dialog.
     * Direct `IS_TRASHED` updates are only allowed for OEM gallery apps and fail otherwise.
     */
    @RequiresApi(Build.VERSION_CODES.R)
    fun createTrashRequest(uri: Uri): IntentSender =
        MediaStore
            .createTrashRequest(context.contentResolver, listOf(uri), true)
            .intentSender

    fun deletePermanently(uri: Uri): Boolean =
        try {
            context.contentResolver.delete(uri, null, null) > 0
        } catch (_: SecurityException) {
            false
        }

    private fun cameraFolderSelection(): Pair<String, Array<String>> {
        val notTrashed =
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                " AND ${MediaStore.MediaColumns.IS_TRASHED} = 0"
            } else {
                ""
            }

        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val selection =
                "(" +
                    "${MediaStore.Images.Media.RELATIVE_PATH} LIKE ? OR " +
                    "${MediaStore.Images.Media.RELATIVE_PATH} LIKE ? OR " +
                    "${MediaStore.Images.Media.BUCKET_DISPLAY_NAME} = ?" +
                    ")$notTrashed"
            selection to
                arrayOf(
                    "DCIM/Camera/%",
                    "DCIM/CAMERA/%",
                    "Camera",
                )
        } else {
            @Suppress("DEPRECATION")
            val selection =
                "(" +
                    "${MediaStore.Images.Media.DATA} LIKE ? OR " +
                    "${MediaStore.Images.Media.DATA} LIKE ? OR " +
                    "${MediaStore.Images.Media.BUCKET_DISPLAY_NAME} = ?" +
                    ")"
            selection to
                arrayOf(
                    "%/DCIM/Camera/%",
                    "%/DCIM/CAMERA/%",
                    "Camera",
                )
        }
    }
}
