package dev.harrix.hsk.photosync

import android.content.Context
import android.provider.Settings
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.GalleryCleanerPreferences
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.withContext
import java.io.IOException
import java.security.MessageDigest
import kotlin.coroutines.coroutineContext

enum class PhotoSyncConnectionStatus {
    Unknown,
    Checking,
    Connected,
    Disconnected,
    MissingConfig,
}

data class PhotoSyncProgress(
    val phase: String,
    val current: Int = 0,
    val total: Int = 0,
    val detail: String = "",
    val elapsedMs: Long = 0L,
    val uploadedCount: Int = 0,
    val uploadedBytes: Long = 0L,
    val pendingCount: Int = 0,
    val pendingBytes: Long = 0L,
)

data class PhotoSyncResult(
    val totalPhotos: Int,
    val uploaded: Int,
    val skipped: Int,
    val failed: Int,
    val uploadedBytes: Long,
    val elapsedMs: Long,
    val cancelled: Boolean = false,
    val message: String,
)

data class PhotoSyncPendingEstimate(
    val pendingCount: Int,
    val pendingBytes: Long,
    val totalPhotos: Int,
)

class PhotoSyncEngine(
    private val context: Context,
) {
    private val gallery = CameraGalleryRepository(context)
    private val galleryPrefs = GalleryCleanerPreferences(context)
    private val hashCache = PhotoSyncHashCache(context)

    fun deviceId(): String = Settings.Secure
        .getString(context.contentResolver, Settings.Secure.ANDROID_ID)
        ?.takeIf { it.isNotBlank() }
        ?: "unknown"

    /**
     * True only when the desktop receiver answers a real handshake (host reachable + token OK).
     */
    suspend fun probeConnection(endpoint: PhotoSyncEndpoint): Boolean = try {
        PhotoSyncClient(endpoint, deviceId()).handshake()
        true
    } catch (error: CancellationException) {
        throw error
    } catch (_: IOException) {
        false
    }

    suspend fun estimatePending(endpoint: PhotoSyncEndpoint): PhotoSyncPendingEstimate = withContext(Dispatchers.IO) {
        val client = PhotoSyncClient(endpoint, deviceId())
        client.handshake()
        val photos = gallery.loadCameraPhotos(galleryPrefs.getImagesRelativePath())
        if (photos.isEmpty()) {
            return@withContext PhotoSyncPendingEstimate(0, 0L, 0)
        }
        val items = buildManifestItems(photos) { _, _, _ -> }
        val needed = client.requestNeeded(items).toSet()
        val pendingBytes =
            items
                .filter { it.mediaId in needed }
                .sumOf { it.sizeBytes.coerceAtLeast(0L) }
        PhotoSyncPendingEstimate(
            pendingCount = needed.size,
            pendingBytes = pendingBytes,
            totalPhotos = photos.size,
        )
    }

    suspend fun sync(
        endpoint: PhotoSyncEndpoint,
        onProgress: (PhotoSyncProgress) -> Unit,
    ): PhotoSyncResult = withContext(Dispatchers.IO) {
        val startedAt = System.currentTimeMillis()
        fun elapsed(): Long = System.currentTimeMillis() - startedAt

        val client = PhotoSyncClient(endpoint, deviceId())
        onProgress(
            PhotoSyncProgress(phase = "handshake", elapsedMs = elapsed()),
        )
        try {
            client.handshake()
        } catch (error: IOException) {
            throw mapDesktopFailure(error)
        }

        onProgress(PhotoSyncProgress(phase = "scan", elapsedMs = elapsed()))
        val photos = gallery.loadCameraPhotos(galleryPrefs.getImagesRelativePath())
        if (photos.isEmpty()) {
            return@withContext PhotoSyncResult(
                totalPhotos = 0,
                uploaded = 0,
                skipped = 0,
                failed = 0,
                uploadedBytes = 0L,
                elapsedMs = elapsed(),
                message = "No Camera photos found",
            )
        }

        val photoById = photos.associateBy { it.id.toString() }
        val items =
            buildManifestItems(photos) { index, total, detail ->
                onProgress(
                    PhotoSyncProgress(
                        phase = "hash",
                        current = index,
                        total = total,
                        detail = detail,
                        elapsedMs = elapsed(),
                    ),
                )
            }

        onProgress(
            PhotoSyncProgress(
                phase = "manifest",
                total = items.size,
                elapsedMs = elapsed(),
            ),
        )
        val needed =
            try {
                client.requestNeeded(items).toSet()
            } catch (error: IOException) {
                throw mapDesktopFailure(error)
            }
        val skipped = items.size - needed.size
        val neededItems = items.filter { it.mediaId in needed }
        val pendingBytesTotal = neededItems.sumOf { it.sizeBytes.coerceAtLeast(0L) }
        var uploaded = 0
        var failed = 0
        var uploadedBytes = 0L

        for ((index, item) in neededItems.withIndex()) {
            coroutineContext.ensureActive()
            onProgress(
                PhotoSyncProgress(
                    phase = "upload",
                    current = index + 1,
                    total = neededItems.size,
                    detail = item.displayName.orEmpty(),
                    elapsedMs = elapsed(),
                    uploadedCount = uploaded,
                    uploadedBytes = uploadedBytes,
                    pendingCount = neededItems.size - index,
                    pendingBytes = (pendingBytesTotal - uploadedBytes).coerceAtLeast(0L),
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
                        item.copy(contentHash = actual, sizeBytes = bytes.size.toLong())
                    }
                client.upload(uploadItem, bytes)
                uploaded += 1
                uploadedBytes += bytes.size.toLong()
            } catch (error: CancellationException) {
                throw error
            } catch (error: IOException) {
                if (PhotoSyncNetwork.isDesktopUnavailable(error)) {
                    throw PhotoSyncDesktopGoneException()
                }
                failed += 1
            } catch (_: org.json.JSONException) {
                failed += 1
            } catch (_: IllegalStateException) {
                failed += 1
            } catch (_: SecurityException) {
                failed += 1
            }
        }

        val elapsedMs = elapsed()
        PhotoSyncResult(
            totalPhotos = photos.size,
            uploaded = uploaded,
            skipped = skipped,
            failed = failed,
            uploadedBytes = uploadedBytes,
            elapsedMs = elapsedMs,
            cancelled = false,
            message =
            buildResultMessage(
                uploaded = uploaded,
                skipped = skipped,
                failed = failed,
                uploadedBytes = uploadedBytes,
                elapsedMs = elapsedMs,
                cancelled = false,
            ),
        )
    }

    private suspend fun buildManifestItems(
        photos: List<CameraPhoto>,
        onHashProgress: (index: Int, total: Int, detail: String) -> Unit,
    ): List<PhotoSyncClient.ManifestItem> {
        val items = ArrayList<PhotoSyncClient.ManifestItem>(photos.size)
        for ((index, photo) in photos.withIndex()) {
            coroutineContext.ensureActive()
            onHashProgress(index + 1, photos.size, photo.displayName.orEmpty())
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
        return items
    }

    private fun mapDesktopFailure(error: IOException): IOException = if (PhotoSyncNetwork.isDesktopUnavailable(error)) {
        PhotoSyncDesktopGoneException()
    } else {
        error
    }

    private fun buildResultMessage(
        uploaded: Int,
        skipped: Int,
        failed: Int,
        uploadedBytes: Long,
        elapsedMs: Long,
        cancelled: Boolean,
    ): String {
        val prefix = if (cancelled) "Cancelled" else "Done"
        return "$prefix: uploaded $uploaded, skipped $skipped, failed $failed, " +
            "${PhotoSyncFormat.formatBytes(uploadedBytes)}, " +
            PhotoSyncFormat.formatElapsed(elapsedMs)
    }

    private fun readBytes(photo: CameraPhoto): ByteArray = context.contentResolver.openInputStream(photo.uri)?.use { it.readBytes() }
        ?: error("Cannot read ${photo.displayName}")

    private fun sha256(bytes: ByteArray): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(bytes)
        return digest.joinToString("") { b -> "%02x".format(b) }
    }
}
