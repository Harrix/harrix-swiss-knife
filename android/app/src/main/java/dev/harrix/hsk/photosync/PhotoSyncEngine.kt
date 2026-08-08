package dev.harrix.hsk.photosync

import android.content.Context
import android.provider.Settings
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.GalleryCleanerPreferences
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.withContext
import java.security.MessageDigest
import kotlin.coroutines.coroutineContext

data class PhotoSyncProgress(
    val phase: String,
    val current: Int = 0,
    val total: Int = 0,
    val detail: String = "",
)

data class PhotoSyncResult(
    val totalPhotos: Int,
    val uploaded: Int,
    val skipped: Int,
    val failed: Int,
    val message: String,
)

class PhotoSyncEngine(
    private val context: Context,
) {
    private val gallery = CameraGalleryRepository(context)
    private val galleryPrefs = GalleryCleanerPreferences(context)
    private val hashCache = PhotoSyncHashCache(context)

    suspend fun sync(
        endpoint: PhotoSyncEndpoint,
        onProgress: (PhotoSyncProgress) -> Unit,
    ): PhotoSyncResult = withContext(Dispatchers.IO) {
        val deviceId =
            Settings.Secure
                .getString(context.contentResolver, Settings.Secure.ANDROID_ID)
                ?.takeIf { it.isNotBlank() }
                ?: "unknown"
        val client = PhotoSyncClient(endpoint, deviceId)
        onProgress(PhotoSyncProgress(phase = "handshake"))
        client.handshake()

        onProgress(PhotoSyncProgress(phase = "scan"))
        val photos = gallery.loadCameraPhotos(galleryPrefs.getImagesRelativePath())
        if (photos.isEmpty()) {
            return@withContext PhotoSyncResult(
                totalPhotos = 0,
                uploaded = 0,
                skipped = 0,
                failed = 0,
                message = "No Camera photos found",
            )
        }

        val photoById = photos.associateBy { it.id.toString() }
        val items = ArrayList<PhotoSyncClient.ManifestItem>(photos.size)
        for ((index, photo) in photos.withIndex()) {
            coroutineContext.ensureActive()
            onProgress(
                PhotoSyncProgress(
                    phase = "hash",
                    current = index + 1,
                    total = photos.size,
                    detail = photo.displayName.orEmpty(),
                ),
            )
            val mediaId = photo.id.toString()
            val hash =
                hashCache.get(photo.id, photo.sizeBytes)
                    ?: run {
                        val bytes = readBytes(photo)
                        val digest = sha256(bytes)
                        hashCache.put(photo.id, photo.sizeBytes, digest)
                        digest
                    }
            items +=
                PhotoSyncClient.ManifestItem(
                    mediaId = mediaId,
                    contentHash = hash,
                    sizeBytes = photo.sizeBytes,
                    dateTakenEpochMs = photo.dateTakenEpochMs,
                    displayName = photo.displayName,
                    mimeType = photo.mimeType,
                )
        }

        onProgress(PhotoSyncProgress(phase = "manifest", total = items.size))
        val needed = client.requestNeeded(items).toSet()
        val skipped = items.size - needed.size
        var uploaded = 0
        var failed = 0
        val neededItems = items.filter { it.mediaId in needed }
        for ((index, item) in neededItems.withIndex()) {
            coroutineContext.ensureActive()
            onProgress(
                PhotoSyncProgress(
                    phase = "upload",
                    current = index + 1,
                    total = neededItems.size,
                    detail = item.displayName.orEmpty(),
                ),
            )
            val photo = photoById[item.mediaId]
            if (photo == null) {
                failed += 1
                continue
            }
            try {
                val bytes = readBytes(photo)
                val actual = sha256(bytes)
                hashCache.put(photo.id, photo.sizeBytes, actual)
                val uploadItem =
                    if (actual == item.contentHash) {
                        item
                    } else {
                        item.copy(contentHash = actual)
                    }
                client.upload(uploadItem, bytes)
                uploaded += 1
            } catch (_: java.io.IOException) {
                failed += 1
            } catch (_: org.json.JSONException) {
                failed += 1
            } catch (_: IllegalStateException) {
                failed += 1
            } catch (_: SecurityException) {
                failed += 1
            }
        }

        PhotoSyncResult(
            totalPhotos = photos.size,
            uploaded = uploaded,
            skipped = skipped,
            failed = failed,
            message = "Done: uploaded $uploaded, skipped $skipped, failed $failed",
        )
    }

    private fun readBytes(photo: CameraPhoto): ByteArray = context.contentResolver.openInputStream(photo.uri)?.use { it.readBytes() }
        ?: error("Cannot read ${photo.displayName}")

    private fun sha256(bytes: ByteArray): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(bytes)
        return digest.joinToString("") { b -> "%02x".format(b) }
    }
}
