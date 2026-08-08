package dev.harrix.hsk.gallery

import android.content.ContentResolver
import android.content.ContentUris
import android.content.Context
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import java.util.Locale

/**
 * Maps Photo Picker / opaque content URIs to classic MediaStore image rows when possible,
 * so Save can overwrite the original file and copies can target the same folder.
 */
object MediaStoreImageUri {
    fun resolve(
        context: Context,
        uri: Uri,
    ): Uri {
        if (isClassicImagesMediaUri(uri)) {
            return uri
        }
        resolveFromMediaStoreApi(context, uri)?.let { return it }
        resolveFromMediaId(context, uri)?.let { return it }
        return matchByDisplayNameAndSize(context, uri) ?: uri
    }

    fun isClassicImagesMediaUri(uri: Uri): Boolean {
        if (uri.authority != MediaStore.AUTHORITY) {
            return false
        }
        val path = uri.path.orEmpty().lowercase(Locale.US)
        if (path.contains("/picker/") || path.contains("photopicker")) {
            return false
        }
        return path.contains("/images/media/")
    }

    private fun resolveFromMediaStoreApi(
        context: Context,
        uri: Uri,
    ): Uri? {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
            return null
        }
        return try {
            val mediaUri = MediaStore.getMediaUri(context, uri) ?: return null
            if (!isReadableImage(context, mediaUri)) {
                null
            } else {
                preferImagesCollectionUri(context, mediaUri)
            }
        } catch (_: Exception) {
            null
        }
    }

    private fun resolveFromMediaId(
        context: Context,
        uri: Uri,
    ): Uri? {
        val id = extractMediaId(uri) ?: return null
        return candidateUrisForId(id).firstOrNull { isReadableImage(context, it) }
    }

    private fun preferImagesCollectionUri(
        context: Context,
        uri: Uri,
    ): Uri {
        if (isClassicImagesMediaUri(uri)) {
            return uri
        }
        val id = extractMediaId(uri) ?: return uri
        return candidateUrisForId(id).firstOrNull { isReadableImage(context, it) } ?: uri
    }

    private fun extractMediaId(uri: Uri): Long? {
        uri.lastPathSegment?.toLongOrNull()?.let { return it }
        val path = uri.path.orEmpty()
        val match = Regex("""(?:/media/|/images/media/)(\d+)(?:/)?$""").find(path)
        return match?.groupValues?.getOrNull(1)?.toLongOrNull()
    }

    private fun candidateUrisForId(id: Long): List<Uri> {
        val uris = mutableListOf<Uri>()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            uris +=
                ContentUris.withAppendedId(
                    MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL),
                    id,
                )
            uris +=
                ContentUris.withAppendedId(
                    MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY),
                    id,
                )
        }
        uris += ContentUris.withAppendedId(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, id)
        return uris.distinct()
    }

    private fun matchByDisplayNameAndSize(
        context: Context,
        uri: Uri,
    ): Uri? {
        val resolver = context.contentResolver
        val displayName =
            queryString(resolver, uri, MediaStore.MediaColumns.DISPLAY_NAME)
                ?: queryString(resolver, uri, android.provider.OpenableColumns.DISPLAY_NAME)
                ?: return null
        val size =
            queryLong(resolver, uri, MediaStore.MediaColumns.SIZE)
                ?: queryLong(resolver, uri, android.provider.OpenableColumns.SIZE)
                ?: return null
        if (displayName.isBlank() || size <= 0L) {
            return null
        }
        val collection =
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL)
            } else {
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI
            }
        val projection = arrayOf(MediaStore.Images.Media._ID)
        val selection =
            "${MediaStore.Images.Media.DISPLAY_NAME} = ? AND ${MediaStore.Images.Media.SIZE} = ?"
        return try {
            resolver
                .query(
                    collection,
                    projection,
                    selection,
                    arrayOf(displayName, size.toString()),
                    null,
                )?.use { cursor ->
                    if (!cursor.moveToFirst()) {
                        return@use null
                    }
                    // Ambiguous matches are unsafe to overwrite.
                    if (cursor.count != 1) {
                        return@use null
                    }
                    val id =
                        cursor.getLong(cursor.getColumnIndexOrThrow(MediaStore.Images.Media._ID))
                    ContentUris.withAppendedId(collection, id)
                }
        } catch (_: Exception) {
            null
        }
    }

    private fun isReadableImage(
        context: Context,
        uri: Uri,
    ): Boolean {
        if (!isClassicImagesMediaUri(uri) &&
            uri.path
                .orEmpty()
                .lowercase(Locale.US)
                .let { it.contains("/picker/") || it.contains("photopicker") }
        ) {
            return false
        }
        return try {
            context.contentResolver.query(
                uri,
                arrayOf(MediaStore.MediaColumns._ID),
                null,
                null,
                null,
            )?.use { it.moveToFirst() } == true
        } catch (_: Exception) {
            false
        }
    }

    private fun queryString(
        resolver: ContentResolver,
        uri: Uri,
        column: String,
    ): String? = try {
        resolver.query(uri, arrayOf(column), null, null, null)?.use { cursor ->
            if (!cursor.moveToFirst()) {
                return@use null
            }
            val index = cursor.getColumnIndex(column)
            if (index < 0 || cursor.isNull(index)) null else cursor.getString(index)
        }
    } catch (_: Exception) {
        null
    }

    private fun queryLong(
        resolver: ContentResolver,
        uri: Uri,
        column: String,
    ): Long? = try {
        resolver.query(uri, arrayOf(column), null, null, null)?.use { cursor ->
            if (!cursor.moveToFirst()) {
                return@use null
            }
            val index = cursor.getColumnIndex(column)
            if (index < 0 || cursor.isNull(index)) null else cursor.getLong(index)
        }
    } catch (_: Exception) {
        null
    }
}
