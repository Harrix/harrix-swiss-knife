package dev.harrix.hsk.gallery

import android.content.ContentUris
import android.content.Context
import android.content.IntentSender
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import androidx.annotation.RequiresApi
import java.util.Locale
import kotlin.math.ln
import kotlin.math.pow

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
                MediaStore.Images.Media.DATE_ADDED,
                MediaStore.Images.Media.DATE_TAKEN,
                MediaStore.Images.Media.SIZE,
            )

        val (selection, selectionArgs) = cameraFolderSelection()
        val sortOrder = "${MediaStore.Images.Media.DATE_ADDED} DESC"

        val photos = mutableListOf<CameraPhoto>()
        context.contentResolver
            .query(collection, projection, selection, selectionArgs, sortOrder)
            ?.use { cursor ->
                val idColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media._ID)
                val nameColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DISPLAY_NAME)
                val dateAddedColumn =
                    cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATE_ADDED)
                val dateTakenColumn =
                    cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATE_TAKEN)
                val sizeColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.SIZE)
                while (cursor.moveToNext()) {
                    val id = cursor.getLong(idColumn)
                    val uri = ContentUris.withAppendedId(collection, id)
                    val dateAddedEpochSec = cursor.getLong(dateAddedColumn)
                    val dateTakenRaw = cursor.getLong(dateTakenColumn)
                    photos +=
                        CameraPhoto(
                            id = id,
                            uri = uri,
                            displayName = cursor.getString(nameColumn),
                            dateAddedEpochSec = dateAddedEpochSec,
                            dateTakenEpochMs =
                                if (dateTakenRaw > 0L) {
                                    dateTakenRaw
                                } else {
                                    dateAddedEpochSec * 1000L
                                },
                            sizeBytes = cursor.getLong(sizeColumn).coerceAtLeast(0L),
                        )
                }
            }
        return photos
    }

    fun loadCameraVideos(): List<CameraVideo> {
        val collection =
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                MediaStore.Video.Media.getContentUri(MediaStore.VOLUME_EXTERNAL)
            } else {
                MediaStore.Video.Media.EXTERNAL_CONTENT_URI
            }

        val projection =
            arrayOf(
                MediaStore.Video.Media._ID,
                MediaStore.Video.Media.DISPLAY_NAME,
                MediaStore.Video.Media.DATE_ADDED,
                MediaStore.Video.Media.SIZE,
            )

        val (selection, selectionArgs) = cameraFolderSelection()
        val sortOrder = "${MediaStore.Video.Media.DATE_ADDED} DESC"

        val videos = mutableListOf<CameraVideo>()
        context.contentResolver
            .query(collection, projection, selection, selectionArgs, sortOrder)
            ?.use { cursor ->
                val idColumn = cursor.getColumnIndexOrThrow(MediaStore.Video.Media._ID)
                val nameColumn = cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DISPLAY_NAME)
                val dateColumn = cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DATE_ADDED)
                val sizeColumn = cursor.getColumnIndexOrThrow(MediaStore.Video.Media.SIZE)
                while (cursor.moveToNext()) {
                    val id = cursor.getLong(idColumn)
                    val uri = ContentUris.withAppendedId(collection, id)
                    videos +=
                        CameraVideo(
                            id = id,
                            uri = uri,
                            displayName = cursor.getString(nameColumn),
                            dateAddedEpochSec = cursor.getLong(dateColumn),
                            sizeBytes = cursor.getLong(sizeColumn).coerceAtLeast(0L),
                        )
                }
            }
        return videos
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
    fun createTrashRequest(uris: Collection<Uri>): IntentSender =
        MediaStore
            .createTrashRequest(context.contentResolver, uris, true)
            .intentSender

    @RequiresApi(Build.VERSION_CODES.R)
    fun createTrashRequest(uri: Uri): IntentSender = createTrashRequest(listOf(uri))

    fun deletePermanently(uris: Collection<Uri>): Int {
        var deleted = 0
        for (uri in uris) {
            if (deletePermanently(uri)) {
                deleted += 1
            }
        }
        return deleted
    }

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
                    "${MediaStore.MediaColumns.RELATIVE_PATH} LIKE ? OR " +
                    "${MediaStore.MediaColumns.RELATIVE_PATH} LIKE ? OR " +
                    "${MediaStore.MediaColumns.BUCKET_DISPLAY_NAME} = ?" +
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
                    "${MediaStore.MediaColumns.DATA} LIKE ? OR " +
                    "${MediaStore.MediaColumns.DATA} LIKE ? OR " +
                    "${MediaStore.MediaColumns.BUCKET_DISPLAY_NAME} = ?" +
                    ")"
            selection to
                arrayOf(
                    "%/DCIM/Camera/%",
                    "%/DCIM/CAMERA/%",
                    "Camera",
                )
        }
    }

    companion object {
        fun formatFileSize(bytes: Long): String {
            if (bytes < 1024) {
                return "$bytes B"
            }
            val units = arrayOf("KB", "MB", "GB", "TB")
            val exp = (ln(bytes.toDouble()) / ln(1024.0)).toInt().coerceIn(1, units.size)
            val value = bytes / 1024.0.pow(exp.toDouble())
            return String.format(Locale.US, "%.1f %s", value, units[exp - 1])
        }
    }
}
