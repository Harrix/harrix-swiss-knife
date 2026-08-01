package dev.harrix.hsk.gallery

import android.net.Uri
import android.provider.DocumentsContract

/**
 * Helpers for MediaStore [android.provider.MediaStore.MediaColumns.RELATIVE_PATH] folder prefixes.
 */
object MediaFolderPaths {
    /** Default Camera gallery folder shown as the built-in source. */
    const val DEFAULT_CAMERA_RELATIVE_PATH = "DCIM/Camera/"

    const val DEFAULT_CAMERA_LABEL = "DCIM/Camera"

    fun normalizeRelativePath(path: String): String {
        var normalized = path.replace('\\', '/').trim().trimStart('/')
        while (normalized.contains("//")) {
            normalized = normalized.replace("//", "/")
        }
        if (normalized.isNotEmpty() && !normalized.endsWith("/")) {
            normalized += "/"
        }
        return normalized
    }

    fun displayLabel(relativePath: String?): String {
        if (relativePath.isNullOrBlank()) {
            return DEFAULT_CAMERA_LABEL
        }
        return normalizeRelativePath(relativePath).trimEnd('/')
    }

    /**
     * Maps a SAF tree URI (`primary:DCIM/Camera`) to a MediaStore relative path prefix.
     */
    fun fromTreeUri(uri: Uri): String? {
        val documentId =
            try {
                DocumentsContract.getTreeDocumentId(uri)
            } catch (_: Exception) {
                null
            } ?: return null
        val separator = documentId.indexOf(':')
        if (separator < 0 || separator == documentId.lastIndex) {
            return null
        }
        val path = documentId.substring(separator + 1).trim()
        if (path.isEmpty()) {
            return null
        }
        return normalizeRelativePath(path)
    }
}
