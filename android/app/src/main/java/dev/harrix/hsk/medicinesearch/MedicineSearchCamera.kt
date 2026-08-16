package dev.harrix.hsk.medicinesearch

import android.content.Context
import android.net.Uri
import androidx.core.content.FileProvider
import java.io.File

data class MedicineSearchCapture(
    val file: File,
    val uri: Uri,
)

/**
 * Creates a cache file and FileProvider URI for the system camera.
 */
object MedicineSearchCamera {
    private const val CACHE_DIR = "medicine_search_camera"

    fun createCapture(context: Context): MedicineSearchCapture? {
        val directory = File(context.cacheDir, CACHE_DIR)
        if (!directory.exists() && !directory.mkdirs()) {
            return null
        }
        val file = File(directory, "capture_${System.currentTimeMillis()}.jpg")
        val uri =
            runCatching {
                FileProvider.getUriForFile(
                    context,
                    "${context.packageName}.fileprovider",
                    file,
                )
            }.getOrNull() ?: return null
        return MedicineSearchCapture(file = file, uri = uri)
    }
}
