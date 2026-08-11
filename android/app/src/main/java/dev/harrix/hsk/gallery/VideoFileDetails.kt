package dev.harrix.hsk.gallery

import android.content.Context
import android.database.Cursor
import android.media.MediaMetadataRetriever
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import java.util.Locale
import java.util.concurrent.TimeUnit

/** MediaStore / metadata summary for Video Cleaner File details. */
data class VideoFileDetails(
    val displayName: String?,
    val relativePath: String?,
    val sizeBytes: Long,
    val width: Int?,
    val height: Int?,
    val durationMs: Long?,
    val mimeType: String?,
    val dateTakenEpochMs: Long?,
) {
    val resolutionLabel: String?
        get() {
            val w = width ?: return null
            val h = height ?: return null
            if (w <= 0 || h <= 0) {
                return null
            }
            return "${w}x$h"
        }

    val durationLabel: String?
        get() {
            val ms = durationMs ?: return null
            if (ms <= 0L) {
                return null
            }
            return formatDurationMs(ms)
        }

    /** `12.3 MB | 1920x1080 | 1:05 | video/mp4` style summary. */
    fun fileStatsLine(sizeFormatter: (Long) -> String): String? {
        val parts =
            listOfNotNull(
                sizeBytes.takeIf { it > 0L }?.let(sizeFormatter),
                resolutionLabel,
                durationLabel,
                mimeType?.takeIf { it.isNotBlank() },
            )
        return parts.takeIf { it.isNotEmpty() }?.joinToString(" | ")
    }

    companion object {
        fun formatDurationMs(durationMs: Long): String {
            val totalSec = TimeUnit.MILLISECONDS.toSeconds(durationMs.coerceAtLeast(0L))
            val hours = totalSec / 3600L
            val minutes = (totalSec % 3600L) / 60L
            val seconds = totalSec % 60L
            return if (hours > 0L) {
                String.format(Locale.getDefault(), "%d:%02d:%02d", hours, minutes, seconds)
            } else {
                String.format(Locale.getDefault(), "%d:%02d", minutes, seconds)
            }
        }
    }
}

object VideoFileDetailsLoader {
    fun load(
        context: Context,
        video: CameraVideo,
    ): VideoFileDetails {
        val appContext = context.applicationContext
        val media = queryMediaStore(appContext, video.uri)
        val meta = readMetadata(appContext, video.uri)

        val width = media.width ?: meta.width
        val height = media.height ?: meta.height
        val durationMs = media.durationMs ?: meta.durationMs
        val dateTakenEpochMs =
            media.dateTakenEpochMs
                ?: video.dateAddedEpochSec.takeIf { it > 0L }?.times(1000L)

        return VideoFileDetails(
            displayName = media.displayName ?: video.displayName,
            relativePath = media.relativePath,
            sizeBytes = media.sizeBytes.takeIf { it > 0L } ?: video.sizeBytes,
            width = width,
            height = height,
            durationMs = durationMs,
            mimeType = media.mimeType ?: meta.mimeType,
            dateTakenEpochMs = dateTakenEpochMs,
        )
    }

    private data class MediaStoreFields(
        val displayName: String?,
        val relativePath: String?,
        val sizeBytes: Long,
        val width: Int?,
        val height: Int?,
        val durationMs: Long?,
        val mimeType: String?,
        val dateTakenEpochMs: Long?,
    )

    private data class MetadataFields(
        val width: Int?,
        val height: Int?,
        val durationMs: Long?,
        val mimeType: String?,
    )

    private fun queryMediaStore(
        context: Context,
        uri: Uri,
    ): MediaStoreFields {
        val projection = mediaStoreProjection()
        return try {
            context.contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
                if (!cursor.moveToFirst()) {
                    return emptyMediaStoreFields()
                }
                readMediaStoreFields(cursor)
            } ?: emptyMediaStoreFields()
        } catch (_: Exception) {
            emptyMediaStoreFields()
        }
    }

    private fun mediaStoreProjection(): Array<String> = buildList {
        add(MediaStore.MediaColumns.DISPLAY_NAME)
        add(MediaStore.MediaColumns.SIZE)
        add(MediaStore.MediaColumns.WIDTH)
        add(MediaStore.MediaColumns.HEIGHT)
        add(MediaStore.MediaColumns.DURATION)
        add(MediaStore.MediaColumns.MIME_TYPE)
        add(MediaStore.MediaColumns.DATE_TAKEN)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            add(MediaStore.MediaColumns.RELATIVE_PATH)
        } else {
            @Suppress("DEPRECATION")
            add(MediaStore.MediaColumns.DATA)
        }
    }.toTypedArray()

    private fun emptyMediaStoreFields(): MediaStoreFields = MediaStoreFields(null, null, 0L, null, null, null, null, null)

    private fun readMediaStoreFields(cursor: Cursor): MediaStoreFields {
        fun col(name: String): Int = cursor.getColumnIndex(name)
        val name =
            col(MediaStore.MediaColumns.DISPLAY_NAME).takeIf { it >= 0 }?.let {
                cursor.getString(it)
            }
        val size =
            col(MediaStore.MediaColumns.SIZE).takeIf { it >= 0 }?.let {
                cursor.getLong(it)
            } ?: 0L
        val width =
            col(MediaStore.MediaColumns.WIDTH).takeIf { it >= 0 }?.let {
                cursor.getInt(it).takeIf { value -> value > 0 }
            }
        val height =
            col(MediaStore.MediaColumns.HEIGHT).takeIf { it >= 0 }?.let {
                cursor.getInt(it).takeIf { value -> value > 0 }
            }
        val durationMs =
            col(MediaStore.MediaColumns.DURATION).takeIf { it >= 0 }?.let {
                cursor.getLong(it).takeIf { value -> value > 0L }
            }
        val mimeType =
            col(MediaStore.MediaColumns.MIME_TYPE).takeIf { it >= 0 }?.let {
                cursor.getString(it)?.takeIf { value -> value.isNotBlank() }
            }
        val dateTaken =
            col(MediaStore.MediaColumns.DATE_TAKEN).takeIf { it >= 0 }?.let {
                cursor.getLong(it).takeIf { value -> value > 0L }
            }
        return MediaStoreFields(
            displayName = name,
            relativePath = readRelativePath(cursor, ::col),
            sizeBytes = size.coerceAtLeast(0L),
            width = width,
            height = height,
            durationMs = durationMs,
            mimeType = mimeType,
            dateTakenEpochMs = dateTaken,
        )
    }

    private fun readRelativePath(
        cursor: Cursor,
        col: (String) -> Int,
    ): String? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        col(MediaStore.MediaColumns.RELATIVE_PATH).takeIf { it >= 0 }?.let {
            cursor.getString(it)?.trimEnd('/')
        }
    } else {
        @Suppress("DEPRECATION")
        col(MediaStore.MediaColumns.DATA).takeIf { it >= 0 }?.let { index ->
            cursor
                .getString(index)
                ?.substringBeforeLast('/', missingDelimiterValue = "")
                ?.takeIf { it.isNotBlank() }
        }
    }

    private fun readMetadata(
        context: Context,
        uri: Uri,
    ): MetadataFields {
        val empty =
            MetadataFields(
                width = null,
                height = null,
                durationMs = null,
                mimeType = null,
            )
        val retriever = MediaMetadataRetriever()
        return try {
            retriever.setDataSource(context, uri)
            val width =
                retriever
                    .extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH)
                    ?.toIntOrNull()
                    ?.takeIf { it > 0 }
            val height =
                retriever
                    .extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT)
                    ?.toIntOrNull()
                    ?.takeIf { it > 0 }
            val durationMs =
                retriever
                    .extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION)
                    ?.toLongOrNull()
                    ?.takeIf { it > 0L }
            val mimeType =
                retriever
                    .extractMetadata(MediaMetadataRetriever.METADATA_KEY_MIMETYPE)
                    ?.takeIf { it.isNotBlank() }
            MetadataFields(
                width = width,
                height = height,
                durationMs = durationMs,
                mimeType = mimeType,
            )
        } catch (_: Exception) {
            empty
        } finally {
            try {
                retriever.release()
            } catch (_: Exception) {
                // Ignore release failures.
            }
        }
    }
}
