package dev.harrix.hsk.gallery

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.ImageDecoder
import android.graphics.Matrix
import android.net.Uri
import android.os.Build
import androidx.exifinterface.media.ExifInterface
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.File
import kotlin.math.abs
import kotlin.math.ceil
import kotlin.math.hypot
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt
import kotlin.math.sqrt
import android.graphics.Rect as AndroidRect

/**
 * Normalized crop rectangle on the rotated square canvas, each edge in `0f..1f`.
 * Matches [PhotoEditSaver.renderRotatedOnSquare] (image centered on a square canvas).
 */
data class NormalizedCropRect(
    val left: Float,
    val top: Float,
    val right: Float,
    val bottom: Float,
) {
    init {
        require(left in 0f..1f && top in 0f..1f && right in 0f..1f && bottom in 0f..1f)
        require(right > left && bottom > top)
    }

    val width: Float get() = right - left

    val height: Float get() = bottom - top

    companion object {
        val Full = NormalizedCropRect(0f, 0f, 1f, 1f)
    }
}

/**
 * Pre-edit original kept for session undo of crop/rotate.
 *
 * Independent from MediaStore trash undo after a delete swipe.
 */
data class PendingEditUndo(
    val photoId: Long,
    val uri: Uri,
    val originalSizeBytes: Long,
    val backupFile: File,
    /** Photo metadata from before the edit, used to put it back in the review deck. */
    val photoSnapshot: CameraPhoto,
)

/** Result of scanning the current crop for empty near-black voids. */
data class BlackVoidCropAnalysis(
    val hasSignificantVoids: Boolean,
    val suggestedCrop: NormalizedCropRect?,
) {
    companion object {
        val None = BlackVoidCropAnalysis(hasSignificantVoids = false, suggestedCrop = null)
    }
}

/** One undoable action from the current Gallery Cleaner session (LIFO). */
sealed class GallerySessionUndo {
    data class Delete(
        val photo: CameraPhoto,
    ) : GallerySessionUndo()

    data class Keep(
        val photo: CameraPhoto,
    ) : GallerySessionUndo()

    data class Edit(
        val undo: PendingEditUndo,
    ) : GallerySessionUndo()
}

class PhotoEditSaver(
    private val context: Context,
) {
    sealed class SaveResult {
        data class Success(
            val sizeBytes: Long,
            /** Set when a new pre-edit backup was written for undo. */
            val backupCreated: Boolean,
        ) : SaveResult()

        data object NeedsWritePermission : SaveResult()

        data object Failed : SaveResult()
    }

    sealed class RestoreResult {
        data object Success : RestoreResult()

        data object NeedsWritePermission : RestoreResult()

        data object Failed : RestoreResult()
    }

    fun save(
        photoId: Long,
        uri: Uri,
        mimeType: String?,
        rotationDegrees: Float,
        crop: NormalizedCropRect,
        /**
         * When non-null and still valid, keeps that pre-edit original across repeated saves
         * on the same photo for the session.
         */
        existingUndo: PendingEditUndo? = null,
    ): SaveResult {
        val oriented =
            decodeOrientedBitmap(uri) ?: return SaveResult.Failed
        // Editor already applied the chosen aspect (original / 90° / free).
        val squareCrop = clampCropRectFree(crop)
        val workspace =
            renderRotatedOnSquare(oriented, rotationDegrees) ?: run {
                oriented.recycle()
                return SaveResult.Failed
            }
        if (workspace !== oriented) {
            oriented.recycle()
        }
        val cropped =
            cropBitmap(workspace, squareCrop) ?: run {
                workspace.recycle()
                return SaveResult.Failed
            }
        if (cropped !== workspace) {
            workspace.recycle()
        }

        val encoded =
            encodeBitmap(cropped, mimeType) ?: run {
                cropped.recycle()
                return SaveResult.Failed
            }
        cropped.recycle()

        val reuseBackup =
            existingUndo != null &&
                existingUndo.photoId == photoId &&
                existingUndo.uri == uri &&
                existingUndo.backupFile.isFile
        var backupCreated = false
        if (!reuseBackup) {
            when (backupOriginal(uri, photoId)) {
                BackupResult.NeedsWritePermission -> return SaveResult.NeedsWritePermission
                BackupResult.Failed -> return SaveResult.Failed
                BackupResult.Success -> backupCreated = true
            }
        }

        return when (val written = writeBytes(uri, encoded)) {
            is SaveResult.Success -> written.copy(backupCreated = backupCreated || reuseBackup)

            else -> {
                if (backupCreated && !reuseBackup) {
                    clearEditBackup(photoId)
                }
                written
            }
        }
    }

    fun restoreFromUndo(undo: PendingEditUndo): RestoreResult {
        if (!undo.backupFile.isFile) {
            return RestoreResult.Failed
        }
        val bytes =
            try {
                undo.backupFile.readBytes()
            } catch (_: Exception) {
                return RestoreResult.Failed
            }
        return when (val written = writeBytes(undo.uri, bytes)) {
            is SaveResult.Success -> {
                clearEditBackup(undo.photoId)
                RestoreResult.Success
            }

            SaveResult.NeedsWritePermission -> RestoreResult.NeedsWritePermission

            SaveResult.Failed -> RestoreResult.Failed
        }
    }

    fun editBackupFile(photoId: Long): File = File(context.cacheDir, "$EDIT_UNDO_BACKUP_PREFIX$photoId.bak")

    fun clearEditBackup(photoId: Long) {
        runCatching { editBackupFile(photoId).delete() }
    }

    fun clearAllEditBackups() {
        val dir = context.cacheDir
        dir.listFiles()?.forEach { file ->
            if (file.name.startsWith(EDIT_UNDO_BACKUP_PREFIX) && file.name.endsWith(".bak")) {
                runCatching { file.delete() }
            }
        }
    }

    /**
     * Analyzes [crop] on the rotated square canvas for empty near-black voids inside the
     * photo (letterbox bars). Off-image padding uses a non-black sentinel so rotation
     * triangles are not mistaken for black bars. When voids are significant,
     * [BlackVoidCropAnalysis.suggestedCrop] is the largest axis-aligned rectangle inside
     * [crop] that stays on non-black photo content.
     */
    fun analyzeBlackVoidsInCrop(
        uri: Uri,
        rotationDegrees: Float,
        crop: NormalizedCropRect,
        maxAnalyzeSide: Int = BlackBarAnalyzeMaxSide,
    ): BlackVoidCropAnalysis {
        val oriented = decodeOrientedBitmap(uri) ?: return BlackVoidCropAnalysis.None
        val analyze =
            scaleBitmapToMaxSide(oriented, maxAnalyzeSide) ?: run {
                oriented.recycle()
                return BlackVoidCropAnalysis.None
            }
        if (analyze !== oriented) {
            oriented.recycle()
        }
        val square =
            renderRotatedOnSquare(
                bitmap = analyze,
                degrees = rotationDegrees,
                backgroundColor = OutsideCanvasColor,
            ) ?: run {
                analyze.recycle()
                return BlackVoidCropAnalysis.None
            }
        if (square !== analyze) {
            analyze.recycle()
        }
        val width = square.width
        val height = square.height
        val search =
            AndroidRect(
                (crop.left * width).roundToInt().coerceIn(0, width - 1),
                (crop.top * height).roundToInt().coerceIn(0, height - 1),
                (crop.right * width).roundToInt().coerceIn(1, width),
                (crop.bottom * height).roundToInt().coerceIn(1, height),
            )
        if (search.width() < 2 || search.height() < 2) {
            square.recycle()
            return BlackVoidCropAnalysis.None
        }
        val pixels = IntArray(width * height)
        square.getPixels(pixels, 0, width, 0, 0, width, height)
        square.recycle()

        val voidRatio = voidRatioInRect(pixels, width, search)
        if (voidRatio < BlackVoidMinRatio) {
            return BlackVoidCropAnalysis.None
        }
        val content =
            largestContentRectInside(pixels, width, height, search) ?: return BlackVoidCropAnalysis.None
        val suggested =
            clampCropRectFree(
                NormalizedCropRect(
                    left = content.left / width.toFloat(),
                    top = content.top / height.toFloat(),
                    right = content.right / width.toFloat(),
                    bottom = content.bottom / height.toFloat(),
                ),
            )
        // Must meaningfully shrink the frame; otherwise voids are photo-dark noise.
        val areaRatio =
            (suggested.width * suggested.height) /
                (crop.width * crop.height).coerceAtLeast(1e-6f)
        if (areaRatio > BlackVoidMaxKeepAreaRatio) {
            return BlackVoidCropAnalysis.None
        }
        return BlackVoidCropAnalysis(
            hasSignificantVoids = true,
            suggestedCrop = suggested,
        )
    }

    fun cropWithoutBlackBars(
        uri: Uri,
        rotationDegrees: Float,
        crop: NormalizedCropRect,
        maxAnalyzeSide: Int = BlackBarAnalyzeMaxSide,
    ): NormalizedCropRect? = analyzeBlackVoidsInCrop(
        uri = uri,
        rotationDegrees = rotationDegrees,
        crop = crop,
        maxAnalyzeSide = maxAnalyzeSide,
    ).suggestedCrop

    private sealed class BackupResult {
        data object Success : BackupResult()

        data object NeedsWritePermission : BackupResult()

        data object Failed : BackupResult()
    }

    private fun backupOriginal(
        uri: Uri,
        photoId: Long,
    ): BackupResult {
        val bytes =
            try {
                context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
            } catch (_: SecurityException) {
                return BackupResult.NeedsWritePermission
            } catch (_: Exception) {
                return BackupResult.Failed
            } ?: return BackupResult.Failed
        return try {
            editBackupFile(photoId).writeBytes(bytes)
            BackupResult.Success
        } catch (_: Exception) {
            BackupResult.Failed
        }
    }

    private fun decodeOrientedBitmap(uri: Uri): Bitmap? {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            return try {
                val source = ImageDecoder.createSource(context.contentResolver, uri)
                ImageDecoder.decodeBitmap(source) { decoder, _, _ ->
                    decoder.isMutableRequired = true
                    decoder.allocator = ImageDecoder.ALLOCATOR_SOFTWARE
                }
            } catch (_: Exception) {
                null
            }
        }

        val bytes =
            context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
                ?: return null
        val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size) ?: return null
        val orientation =
            try {
                ExifInterface(ByteArrayInputStream(bytes)).getAttributeInt(
                    ExifInterface.TAG_ORIENTATION,
                    ExifInterface.ORIENTATION_NORMAL,
                )
            } catch (_: Exception) {
                ExifInterface.ORIENTATION_NORMAL
            }
        return applyExifOrientation(bitmap, orientation)
    }

    private fun applyExifOrientation(
        bitmap: Bitmap,
        orientation: Int,
    ): Bitmap {
        val matrix = Matrix()
        when (orientation) {
            ExifInterface.ORIENTATION_FLIP_HORIZONTAL -> matrix.preScale(-1f, 1f)

            ExifInterface.ORIENTATION_ROTATE_180 -> matrix.postRotate(180f)

            ExifInterface.ORIENTATION_FLIP_VERTICAL -> matrix.preScale(1f, -1f)

            ExifInterface.ORIENTATION_TRANSPOSE -> {
                matrix.postRotate(90f)
                matrix.preScale(-1f, 1f)
            }

            ExifInterface.ORIENTATION_ROTATE_90 -> matrix.postRotate(90f)

            ExifInterface.ORIENTATION_TRANSVERSE -> {
                matrix.postRotate(270f)
                matrix.preScale(-1f, 1f)
            }

            ExifInterface.ORIENTATION_ROTATE_270 -> matrix.postRotate(270f)

            else -> return bitmap
        }
        val transformed =
            Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
        if (transformed !== bitmap) {
            bitmap.recycle()
        }
        return transformed
    }

    /**
     * Draws [bitmap] centered on a square large enough for any rotation, then rotates it.
     * [backgroundColor] fills off-image pixels: black for the saved file, a non-black
     * sentinel when analyzing black bars so rotation padding is not treated as voids.
     */
    private fun renderRotatedOnSquare(
        bitmap: Bitmap,
        degrees: Float,
        backgroundColor: Int = Color.BLACK,
    ): Bitmap? {
        val diag =
            ceil(hypot(bitmap.width.toDouble(), bitmap.height.toDouble()))
                .toInt()
                .coerceAtLeast(1)
        val square =
            try {
                Bitmap.createBitmap(diag, diag, Bitmap.Config.ARGB_8888)
            } catch (_: OutOfMemoryError) {
                return null
            }
        val canvas = Canvas(square)
        canvas.drawColor(backgroundColor)
        canvas.translate(diag / 2f, diag / 2f)
        canvas.rotate(degrees)
        canvas.drawBitmap(bitmap, -bitmap.width / 2f, -bitmap.height / 2f, null)
        return square
    }

    private fun scaleBitmapToMaxSide(
        bitmap: Bitmap,
        maxSide: Int,
    ): Bitmap? {
        val longest = max(bitmap.width, bitmap.height)
        if (longest <= maxSide) {
            return bitmap
        }
        val scale = maxSide.toFloat() / longest.toFloat()
        val width = (bitmap.width * scale).roundToInt().coerceAtLeast(1)
        val height = (bitmap.height * scale).roundToInt().coerceAtLeast(1)
        return try {
            Bitmap.createScaledBitmap(bitmap, width, height, true)
        } catch (_: OutOfMemoryError) {
            null
        }
    }

    private fun isOutsidePixel(color: Int): Boolean = color == OutsideCanvasColor

    private fun isVoidPixel(color: Int): Boolean {
        if (isOutsidePixel(color)) {
            return false
        }
        val r = Color.red(color)
        val g = Color.green(color)
        val b = Color.blue(color)
        return r <= BlackBarChannelMax &&
            g <= BlackBarChannelMax &&
            b <= BlackBarChannelMax
    }

    private fun voidRatioInRect(
        pixels: IntArray,
        width: Int,
        rect: AndroidRect,
    ): Float {
        val sampleStep =
            max(1, min(rect.width(), rect.height()) / BlackBarSampleDivisor).coerceAtLeast(1)
        var voids = 0
        var total = 0
        var y = rect.top
        while (y < rect.bottom) {
            var x = rect.left
            while (x < rect.right) {
                if (isVoidPixel(pixels[y * width + x])) {
                    voids += 1
                }
                total += 1
                x += sampleStep
            }
            y += sampleStep
        }
        if (total == 0) {
            return 0f
        }
        return voids.toFloat() / total.toFloat()
    }

    /**
     * Grows the largest axis-aligned rectangle of non-void pixels inside [search]
     * from a content seed near the center (inscribed in rotated photo content).
     */
    private fun largestContentRectInside(
        pixels: IntArray,
        width: Int,
        height: Int,
        search: AndroidRect,
    ): AndroidRect? {
        val seed =
            findContentSeed(pixels, width, search) ?: return null
        var left = seed.first
        var right = seed.first
        var top = seed.second
        var bottom = seed.second
        var expanded = true
        while (expanded) {
            expanded = false
            if (left > search.left &&
                isContentColumn(pixels, width, left - 1, top, bottom)
            ) {
                left -= 1
                expanded = true
            }
            if (right + 1 < search.right &&
                isContentColumn(pixels, width, right + 1, top, bottom)
            ) {
                right += 1
                expanded = true
            }
            if (top > search.top &&
                isContentRow(pixels, width, top - 1, left, right)
            ) {
                top -= 1
                expanded = true
            }
            if (bottom + 1 < search.bottom &&
                isContentRow(pixels, width, bottom + 1, left, right)
            ) {
                bottom += 1
                expanded = true
            }
        }
        val contentWidth = right - left + 1
        val contentHeight = bottom - top + 1
        val minSide =
            max(
                2,
                (min(search.width(), search.height()) * BlackBarMinContentFraction).roundToInt(),
            )
        if (contentWidth < minSide || contentHeight < minSide) {
            return null
        }
        return AndroidRect(left, top, right + 1, bottom + 1)
    }

    private fun findContentSeed(
        pixels: IntArray,
        width: Int,
        search: AndroidRect,
    ): Pair<Int, Int>? {
        val cx = (search.left + search.right - 1) / 2
        val cy = (search.top + search.bottom - 1) / 2
        if (isContentPixel(pixels, width, cx, cy, search)) {
            return cx to cy
        }
        val maxRadius = max(search.width(), search.height()).coerceAtLeast(1)
        for (radius in 1..maxRadius) {
            val y0 = (cy - radius).coerceAtLeast(search.top)
            val y1 = (cy + radius).coerceAtMost(search.bottom - 1)
            val x0 = (cx - radius).coerceAtLeast(search.left)
            val x1 = (cx + radius).coerceAtMost(search.right - 1)
            // Top and bottom edges of the ring.
            for (x in x0..x1) {
                if (isContentPixel(pixels, width, x, y0, search)) {
                    return x to y0
                }
                if (isContentPixel(pixels, width, x, y1, search)) {
                    return x to y1
                }
            }
            // Left and right edges (corners already checked).
            for (y in (y0 + 1) until y1) {
                if (isContentPixel(pixels, width, x0, y, search)) {
                    return x0 to y
                }
                if (isContentPixel(pixels, width, x1, y, search)) {
                    return x1 to y
                }
            }
        }
        return null
    }

    private fun isContentPixel(
        pixels: IntArray,
        width: Int,
        x: Int,
        y: Int,
        search: AndroidRect,
    ): Boolean {
        val insideX = x in search.left until search.right
        val insideY = y in search.top until search.bottom
        if (!insideX || !insideY) {
            return false
        }
        return !isOutsidePixel(pixels[y * width + x]) &&
            !isVoidPixel(pixels[y * width + x])
    }

    private fun isContentColumn(
        pixels: IntArray,
        width: Int,
        x: Int,
        top: Int,
        bottom: Int,
    ): Boolean {
        for (y in top..bottom) {
            val color = pixels[y * width + x]
            if (isOutsidePixel(color) || isVoidPixel(color)) {
                return false
            }
        }
        return true
    }

    private fun isContentRow(
        pixels: IntArray,
        width: Int,
        y: Int,
        left: Int,
        right: Int,
    ): Boolean {
        for (x in left..right) {
            val color = pixels[y * width + x]
            if (isOutsidePixel(color) || isVoidPixel(color)) {
                return false
            }
        }
        return true
    }

    private fun cropBitmap(
        bitmap: Bitmap,
        crop: NormalizedCropRect,
    ): Bitmap? {
        val left = (crop.left * bitmap.width).roundToInt().coerceIn(0, bitmap.width - 1)
        val top = (crop.top * bitmap.height).roundToInt().coerceIn(0, bitmap.height - 1)
        val right = (crop.right * bitmap.width).roundToInt().coerceIn(left + 1, bitmap.width)
        val bottom = (crop.bottom * bitmap.height).roundToInt().coerceIn(top + 1, bitmap.height)
        val width = right - left
        val height = bottom - top
        if (width <= 0 || height <= 0) {
            return null
        }
        val isFullFrame =
            left == 0 &&
                top == 0 &&
                width == bitmap.width &&
                height == bitmap.height
        if (isFullFrame) {
            return bitmap
        }
        return Bitmap.createBitmap(bitmap, left, top, width, height)
    }

    private fun encodeBitmap(
        bitmap: Bitmap,
        mimeType: String?,
    ): ByteArray? {
        val stream = ByteArrayOutputStream()
        val ok =
            when {
                mimeType.equals("image/png", ignoreCase = true) ->
                    bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)

                mimeType.equals("image/webp", ignoreCase = true) -> {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                        bitmap.compress(Bitmap.CompressFormat.WEBP_LOSSLESS, 100, stream)
                    } else {
                        @Suppress("DEPRECATION")
                        bitmap.compress(Bitmap.CompressFormat.WEBP, 100, stream)
                    }
                }

                else -> bitmap.compress(Bitmap.CompressFormat.JPEG, JPEG_QUALITY, stream)
            }
        return if (ok) stream.toByteArray() else null
    }

    private fun writeBytes(
        uri: Uri,
        bytes: ByteArray,
    ): SaveResult = try {
        context.contentResolver.openOutputStream(uri, "wt")?.use { output ->
            output.write(bytes)
            output.flush()
            SaveResult.Success(sizeBytes = bytes.size.toLong(), backupCreated = false)
        } ?: SaveResult.Failed
    } catch (_: SecurityException) {
        SaveResult.NeedsWritePermission
    } catch (_: Exception) {
        SaveResult.Failed
    }

    companion object {
        private const val JPEG_QUALITY = 95
        private const val EDIT_UNDO_BACKUP_PREFIX = "gallery_cleaner_edit_undo_"
        private const val BlackBarAnalyzeMaxSide = 512
        private const val BlackBarSampleDivisor = 128
        private const val BlackBarChannelMax = 12
        private const val BlackBarMinContentFraction = 0.08f
        private const val BlackVoidMinRatio = 0.02f
        private const val BlackVoidMaxKeepAreaRatio = 0.98f

        /**
         * Off-image fill during void analysis. Must not look near-black; save path still
         * uses [Color.BLACK] so exported letterbox stays black.
         */
        private val OutsideCanvasColor: Int = Color.rgb(255, 0, 255)

        /**
         * Largest square that fits in the viewport (centered). Crop and rotation use this
         * canvas; areas outside the photo are black.
         */
        fun fittedSquareInViewport(
            viewportWidth: Float,
            viewportHeight: Float,
        ): FittedRect {
            if (viewportWidth <= 0f || viewportHeight <= 0f) {
                return FittedRect(0f, 0f, 0f, 0f)
            }
            val side = min(viewportWidth, viewportHeight)
            val left = (viewportWidth - side) / 2f
            val top = (viewportHeight - side) / 2f
            return FittedRect(left, top, side, side)
        }

        /**
         * Draw size of the unrotated image inside a square workspace (same proportions as
         * [renderRotatedOnSquare]).
         */
        fun imageDrawSizeInWorkspace(
            imageWidth: Int,
            imageHeight: Int,
            workspace: FittedRect,
        ): Pair<Float, Float> {
            if (imageWidth <= 0 || imageHeight <= 0 || workspace.width <= 0f) {
                return 0f to 0f
            }
            val diag = hypot(imageWidth.toFloat(), imageHeight.toFloat())
            if (diag <= 0f) {
                return 0f to 0f
            }
            return (imageWidth / diag) * workspace.width to (imageHeight / diag) * workspace.height
        }

        /**
         * Initial crop covering the unrotated photo inside the square (letterbox is excluded).
         */
        fun imageContentCrop(
            imageWidth: Int,
            imageHeight: Int,
        ): NormalizedCropRect {
            if (imageWidth <= 0 || imageHeight <= 0) {
                return NormalizedCropRect.Full
            }
            val diag = hypot(imageWidth.toFloat(), imageHeight.toFloat())
            if (diag <= 0f) {
                return NormalizedCropRect.Full
            }
            val width = (imageWidth / diag).coerceIn(0f, 1f)
            val height = (imageHeight / diag).coerceIn(0f, 1f)
            val left = ((1f - width) / 2f).coerceIn(0f, 1f)
            val top = ((1f - height) / 2f).coerceIn(0f, 1f)
            return NormalizedCropRect(left, top, left + width, top + height)
        }

        /**
         * Clamp crop to `0..1` of the square workspace without forcing aspect ratio.
         */
        fun clampCropRectFree(
            rect: NormalizedCropRect,
            minNormalizedSide: Float = 0.06f,
        ): NormalizedCropRect {
            var left = rect.left
            var top = rect.top
            var right = rect.right
            var bottom = rect.bottom
            if (right < left) {
                val tmp = left
                left = right
                right = tmp
            }
            if (bottom < top) {
                val tmp = top
                top = bottom
                bottom = tmp
            }
            var width = (right - left).coerceAtLeast(minNormalizedSide)
            var height = (bottom - top).coerceAtLeast(minNormalizedSide)
            if (width > 1f) {
                width = 1f
            }
            if (height > 1f) {
                height = 1f
            }
            left = left.coerceIn(0f, 1f - width)
            top = top.coerceIn(0f, 1f - height)
            return NormalizedCropRect(left, top, left + width, top + height)
        }

        /**
         * Clamp crop to `0..1` of the square workspace, keeping [imageAspect]
         * (`width / height`). Position is free: the frame may sit partly or mostly
         * on black letterbox around the photo.
         */
        fun clampCropRect(
            rect: NormalizedCropRect,
            imageAspect: Float,
            minNormalizedSide: Float = 0.06f,
        ): NormalizedCropRect {
            val aspect = imageAspect.coerceAtLeast(1e-6f)
            var left = rect.left
            var top = rect.top
            var right = rect.right
            var bottom = rect.bottom
            if (right < left) {
                val tmp = left
                left = right
                right = tmp
            }
            if (bottom < top) {
                val tmp = top
                top = bottom
                bottom = tmp
            }
            var width = (right - left).coerceAtLeast(minNormalizedSide)
            var height = width / aspect
            if (height < minNormalizedSide) {
                height = minNormalizedSide
                width = height * aspect
            }
            if (width > 1f) {
                width = 1f
                height = width / aspect
            }
            if (height > 1f) {
                height = 1f
                width = height * aspect
            }
            left = left.coerceIn(0f, 1f - width)
            top = top.coerceIn(0f, 1f - height)
            return NormalizedCropRect(left, top, left + width, top + height)
        }

        /**
         * Rebuild [rect] with [imageAspect], keeping the center and roughly the same
         * area (so repeated calls do not shrink the frame).
         */
        fun fitCropToAspect(
            rect: NormalizedCropRect,
            imageAspect: Float,
        ): NormalizedCropRect {
            val aspect = imageAspect.coerceAtLeast(1e-6f)
            val currentAspect = rect.width / rect.height.coerceAtLeast(1e-6f)
            if (abs(currentAspect - aspect) < 0.001f) {
                return clampCropRect(rect, aspect)
            }
            val centerX = (rect.left + rect.right) / 2f
            val centerY = (rect.top + rect.bottom) / 2f
            val area = (rect.width * rect.height).coerceAtLeast(0.06f * 0.06f)
            var width = sqrt(area * aspect)
            var height = width / aspect
            if (width > 1f) {
                width = 1f
                height = width / aspect
            }
            if (height > 1f) {
                height = 1f
                width = height * aspect
            }
            val left = (centerX - width / 2f).coerceIn(0f, 1f - width)
            val top = (centerY - height / 2f).coerceIn(0f, 1f - height)
            return clampCropRect(
                NormalizedCropRect(left, top, left + width, top + height),
                aspect,
            )
        }

        /**
         * Largest rectangle with [rect]'s aspect ratio that fits inside [bounds]
         * (both in normalized square workspace coordinates), centered in [bounds].
         */
        fun fitCropIntoBounds(
            rect: NormalizedCropRect,
            bounds: NormalizedCropRect,
        ): NormalizedCropRect {
            val aspect = (rect.width / rect.height.coerceAtLeast(1e-6f)).coerceAtLeast(1e-6f)
            val bw = bounds.width.coerceAtLeast(1e-6f)
            val bh = bounds.height.coerceAtLeast(1e-6f)
            val width: Float
            val height: Float
            if (bw / bh > aspect) {
                height = bh
                width = height * aspect
            } else {
                width = bw
                height = width / aspect
            }
            val left = bounds.left + (bw - width) / 2f
            val top = bounds.top + (bh - height) / 2f
            return clampCropRectFree(
                NormalizedCropRect(left, top, left + width, top + height),
            )
        }

        /**
         * Swap width/height around the center (aspect ↔ 1/aspect) without shrinking.
         * Scales down only if the swapped rect would not fit in the square.
         */
        fun swapCropDimensions(rect: NormalizedCropRect): NormalizedCropRect {
            val centerX = (rect.left + rect.right) / 2f
            val centerY = (rect.top + rect.bottom) / 2f
            var width = rect.height
            var height = rect.width
            if (width > 1f) {
                val scale = 1f / width
                width = 1f
                height = (height * scale).coerceAtMost(1f)
            }
            if (height > 1f) {
                val scale = 1f / height
                height = 1f
                width = (width * scale).coerceAtMost(1f)
            }
            width = width.coerceAtLeast(0.06f)
            height = height.coerceAtLeast(0.06f)
            val left = (centerX - width / 2f).coerceIn(0f, 1f - width)
            val top = (centerY - height / 2f).coerceIn(0f, 1f - height)
            return NormalizedCropRect(left, top, left + width, top + height)
        }
    }

    data class FittedRect(
        val left: Float,
        val top: Float,
        val width: Float,
        val height: Float,
    ) {
        val right: Float get() = left + width
        val bottom: Float get() = top + height
    }
}
