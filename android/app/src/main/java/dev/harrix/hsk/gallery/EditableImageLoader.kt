package dev.harrix.hsk.gallery

import android.content.ContentResolver
import android.content.Context
import android.database.Cursor
import android.net.Uri
import android.provider.MediaStore
import android.provider.OpenableColumns

/** Builds a [CameraPhoto] from an arbitrary image [Uri] for the shared editor. */
object EditableImageLoader {
    fun load(
        context: Context,
        uri: Uri,
    ): CameraPhoto? {
        val resolvedUri = MediaStoreImageUri.resolve(context, uri)
        val resolver = context.contentResolver
        val mimeType =
            resolver.getType(resolvedUri)?.takeIf { it.startsWith("image/") }
                ?: resolver.getType(uri)?.takeIf { it.startsWith("image/") }
        if (mimeType == null && !looksLikeImageUri(resolvedUri) && !looksLikeImageUri(uri)) {
            // Still try: some providers omit MIME; decoder will fail later if wrong.
        }
        val displayName =
            queryDisplayName(resolver, resolvedUri) ?: queryDisplayName(resolver, uri)
        val sizeBytes =
            querySizeBytes(resolver, resolvedUri).takeIf { it > 0L }
                ?: querySizeBytes(resolver, uri)
        val mediaId =
            queryMediaStoreId(resolver, resolvedUri) ?: queryMediaStoreId(resolver, uri)
        val dateTakenMs = queryDateTakenMs(resolver, resolvedUri)
        val dateAddedSec = (dateTakenMs / 1000L).coerceAtLeast(0L)
        return CameraPhoto(
            id = mediaId ?: uriToStableId(resolvedUri),
            uri = resolvedUri,
            displayName = displayName,
            dateAddedEpochSec = dateAddedSec,
            dateTakenEpochMs = dateTakenMs,
            sizeBytes = sizeBytes,
            mimeType = mimeType ?: "image/jpeg",
        )
    }

    private fun looksLikeImageUri(uri: Uri): Boolean {
        val path = uri.path?.lowercase().orEmpty()
        return path.endsWith(".jpg") ||
            path.endsWith(".jpeg") ||
            path.endsWith(".png") ||
            path.endsWith(".webp") ||
            path.endsWith(".heic") ||
            path.endsWith(".gif")
    }

    private fun uriToStableId(uri: Uri): Long {
        val hash = uri.toString().hashCode().toLong()
        return if (hash == 0L) 1L else hash
    }

    private fun queryDisplayName(
        resolver: ContentResolver,
        uri: Uri,
    ): String? = queryColumnString(resolver, uri, OpenableColumns.DISPLAY_NAME)
        ?: queryColumnString(resolver, uri, MediaStore.MediaColumns.DISPLAY_NAME)

    private fun querySizeBytes(
        resolver: ContentResolver,
        uri: Uri,
    ): Long {
        val fromColumns =
            queryColumnLong(resolver, uri, OpenableColumns.SIZE)
                ?: queryColumnLong(resolver, uri, MediaStore.MediaColumns.SIZE)
        if (fromColumns != null && fromColumns > 0L) {
            return fromColumns
        }
        return try {
            resolver.openAssetFileDescriptor(uri, "r")?.use { it.length }?.takeIf { it > 0L }
                ?: 0L
        } catch (_: Exception) {
            0L
        }
    }

    private fun queryMediaStoreId(
        resolver: ContentResolver,
        uri: Uri,
    ): Long? {
        if (uri.authority != MediaStore.AUTHORITY) {
            return uri.lastPathSegment?.toLongOrNull()
        }
        return queryColumnLong(resolver, uri, MediaStore.MediaColumns._ID)
            ?: uri.lastPathSegment?.toLongOrNull()
    }

    private fun queryDateTakenMs(
        resolver: ContentResolver,
        uri: Uri,
    ): Long {
        val taken =
            queryColumnLong(resolver, uri, MediaStore.Images.Media.DATE_TAKEN)
                ?.takeIf { it > 0L }
        if (taken != null) {
            return taken
        }
        val addedSec =
            queryColumnLong(resolver, uri, MediaStore.MediaColumns.DATE_ADDED)
                ?.takeIf { it > 0L }
        if (addedSec != null) {
            return addedSec * 1000L
        }
        return System.currentTimeMillis()
    }

    private fun queryColumnString(
        resolver: ContentResolver,
        uri: Uri,
        column: String,
    ): String? = query(resolver, uri, arrayOf(column)) { cursor, index ->
        if (index >= 0 && !cursor.isNull(index)) cursor.getString(index) else null
    }

    private fun queryColumnLong(
        resolver: ContentResolver,
        uri: Uri,
        column: String,
    ): Long? = query(resolver, uri, arrayOf(column)) { cursor, index ->
        if (index >= 0 && !cursor.isNull(index)) cursor.getLong(index) else null
    }

    private fun <T> query(
        resolver: ContentResolver,
        uri: Uri,
        projection: Array<String>,
        read: (Cursor, Int) -> T?,
    ): T? = try {
        resolver.query(uri, projection, null, null, null)?.use { cursor ->
            if (!cursor.moveToFirst()) {
                return@use null
            }
            read(cursor, cursor.getColumnIndex(projection[0]))
        }
    } catch (_: Exception) {
        null
    }
}
