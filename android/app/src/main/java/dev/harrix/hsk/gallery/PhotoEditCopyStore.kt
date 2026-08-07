package dev.harrix.hsk.gallery

import android.content.ContentValues
import android.content.Context
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Inserts an edited image copy into MediaStore, preferring the source photo's folder.
 */
class PhotoEditCopyStore(
    private val context: Context,
) {
    data class Result(
        val uri: Uri,
        val sizeBytes: Long,
        val folderLabel: String,
    )

    private data class SourceMediaLocation(
        val relativePath: String?,
        val volumeName: String?,
        val absoluteDir: File?,
    )

    fun writeCopy(
        sourceUri: Uri,
        encoded: ByteArray,
        mimeType: String,
        displayName: String?,
    ): Result? {
        val extension = extensionForMime(mimeType)
        val stem =
            displayName
                ?.substringBeforeLast('.')
                ?.takeIf { it.isNotBlank() }
                ?: "EDIT_${SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())}"
        val fileName = copyFileName(stem, extension)
        val sourceLocation = querySourceMediaLocation(sourceUri)
        val preferredRelative =
            sourceLocation?.relativePath?.takeIf { it.isNotBlank() }
                ?: FALLBACK_COPY_RELATIVE_PATH
        val preferredVolume = sourceLocation?.volumeName
        val preferredAbsoluteDir = sourceLocation?.absoluteDir

        insertCopy(
            encoded = encoded,
            resolvedMime = mimeType,
            fileName = fileName,
            relativePath = preferredRelative,
            volumeName = preferredVolume,
            absoluteDir = preferredAbsoluteDir,
        )?.let { return it }

        val needsFallback =
            preferredRelative != FALLBACK_COPY_RELATIVE_PATH || preferredVolume != null
        if (!needsFallback) {
            return null
        }
        return insertCopy(
            encoded = encoded,
            resolvedMime = mimeType,
            fileName = fileName,
            relativePath = FALLBACK_COPY_RELATIVE_PATH,
            volumeName = null,
            absoluteDir = null,
        )
    }

    private fun copyFileName(
        stem: String,
        extension: String,
    ): String {
        val editStem =
            if (stem.endsWith("_edit", ignoreCase = true)) {
                stem
            } else {
                "${stem}_edit"
            }
        return "$editStem.$extension"
    }

    private fun querySourceMediaLocation(uri: Uri): SourceMediaLocation? {
        val projection = sourceLocationProjection()
        return try {
            context.contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
                if (!cursor.moveToFirst()) {
                    return@use null
                }
                readSourceMediaLocation(cursor)
            }
        } catch (_: Exception) {
            null
        }
    }

    private fun sourceLocationProjection(): Array<String> = buildList {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            add(MediaStore.MediaColumns.RELATIVE_PATH)
            add(MediaStore.MediaColumns.VOLUME_NAME)
        }
        @Suppress("DEPRECATION")
        add(MediaStore.MediaColumns.DATA)
    }.toTypedArray()

    private fun readSourceMediaLocation(cursor: android.database.Cursor): SourceMediaLocation {
        val relative = readRelativePath(cursor)
        val volume = readVolumeName(cursor)
        val absoluteDir = readAbsoluteDir(cursor)
        val relativeFromData = relative ?: absoluteDir?.let(::relativePathFromAbsoluteDir)
        return SourceMediaLocation(
            relativePath = relativeFromData,
            volumeName = volume,
            absoluteDir = absoluteDir,
        )
    }

    private fun readRelativePath(cursor: android.database.Cursor): String? {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
            return null
        }
        val index = cursor.getColumnIndex(MediaStore.MediaColumns.RELATIVE_PATH)
        if (index < 0 || cursor.isNull(index)) {
            return null
        }
        return cursor
            .getString(index)
            ?.let(MediaFolderPaths::normalizeRelativePath)
            ?.trimEnd('/')
            ?.takeIf { it.isNotBlank() }
    }

    private fun readVolumeName(cursor: android.database.Cursor): String? {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
            return null
        }
        val index = cursor.getColumnIndex(MediaStore.MediaColumns.VOLUME_NAME)
        if (index < 0 || cursor.isNull(index)) {
            return null
        }
        return cursor.getString(index)?.takeIf { it.isNotBlank() }
    }

    private fun readAbsoluteDir(cursor: android.database.Cursor): File? {
        @Suppress("DEPRECATION")
        val dataIndex = cursor.getColumnIndex(MediaStore.MediaColumns.DATA)
        if (dataIndex < 0 || cursor.isNull(dataIndex)) {
            return null
        }
        val path = cursor.getString(dataIndex) ?: return null
        return File(path).parentFile?.takeIf { it.isDirectory || it.exists() }
    }

    private fun relativePathFromAbsoluteDir(dir: File): String? {
        val absolute = dir.absolutePath.replace('\\', '/')
        val markerCandidates =
            listOf(
                "/${Environment.DIRECTORY_DCIM}/",
                "/${Environment.DIRECTORY_PICTURES}/",
                "/${Environment.DIRECTORY_DOWNLOADS}/",
            )
        for (marker in markerCandidates) {
            val index = absolute.indexOf(marker, ignoreCase = true)
            if (index >= 0) {
                return absolute.substring(index + 1).trimEnd('/')
            }
        }
        return null
    }

    private fun insertCopy(
        encoded: ByteArray,
        resolvedMime: String,
        fileName: String,
        relativePath: String,
        volumeName: String?,
        absoluteDir: File?,
    ): Result? {
        val folderLabel = MediaFolderPaths.displayLabel(relativePath)
        val values = contentValuesForInsert(fileName, resolvedMime, relativePath, absoluteDir)
        val collection = collectionUri(volumeName)
        val outUri =
            try {
                context.contentResolver.insert(collection, values)
            } catch (_: Exception) {
                null
            } ?: return null
        return finalizeInsertedCopy(outUri, encoded, folderLabel)
    }

    private fun contentValuesForInsert(
        fileName: String,
        resolvedMime: String,
        relativePath: String,
        absoluteDir: File?,
    ): ContentValues = ContentValues().apply {
        put(MediaStore.MediaColumns.DISPLAY_NAME, fileName)
        put(MediaStore.MediaColumns.MIME_TYPE, resolvedMime)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            put(
                MediaStore.MediaColumns.RELATIVE_PATH,
                MediaFolderPaths.normalizeRelativePath(relativePath),
            )
            put(MediaStore.MediaColumns.IS_PENDING, 1)
        } else if (absoluteDir != null) {
            @Suppress("DEPRECATION")
            put(MediaStore.MediaColumns.DATA, File(absoluteDir, fileName).absolutePath)
        }
    }

    private fun collectionUri(volumeName: String?): Uri = when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q && !volumeName.isNullOrBlank() ->
            MediaStore.Images.Media.getContentUri(volumeName)

        Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q ->
            MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)

        else -> MediaStore.Images.Media.EXTERNAL_CONTENT_URI
    }

    private fun finalizeInsertedCopy(
        outUri: Uri,
        encoded: ByteArray,
        folderLabel: String,
    ): Result? {
        return try {
            val written =
                context.contentResolver.openOutputStream(outUri)?.use { output ->
                    output.write(encoded)
                    output.flush()
                    true
                } ?: false
            if (!written) {
                context.contentResolver.delete(outUri, null, null)
                return null
            }
            val values = ContentValues()
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                values.put(MediaStore.MediaColumns.IS_PENDING, 0)
            }
            ExifPreserver.dateTakenMillisFromBytes(encoded)?.let { takenMs ->
                values.put(MediaStore.Images.Media.DATE_TAKEN, takenMs)
            }
            if (values.size() > 0) {
                context.contentResolver.update(outUri, values, null, null)
            }
            Result(
                uri = outUri,
                sizeBytes = encoded.size.toLong(),
                folderLabel = folderLabel,
            )
        } catch (_: Exception) {
            runCatching { context.contentResolver.delete(outUri, null, null) }
            null
        }
    }

    private fun extensionForMime(mimeType: String): String = when (mimeType.lowercase(Locale.US)) {
        "image/png" -> "png"
        "image/webp" -> "webp"
        "image/jpeg", "image/jpg" -> "jpg"
        else -> "jpg"
    }

    companion object {
        private const val FALLBACK_COPY_RELATIVE_PATH = "Pictures/HSK"
    }
}
