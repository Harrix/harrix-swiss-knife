package dev.harrix.hsk.gallery

import android.content.ContentValues
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.ImageDecoder
import android.graphics.Matrix
import android.graphics.Paint
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import androidx.exifinterface.media.ExifInterface
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.math.abs
import kotlin.math.ceil
import kotlin.math.hypot
import kotlin.math.min
import kotlin.math.roundToInt

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

/** Normalized point on the rotated square canvas (`0f..1f`). */
data class NormalizedPoint(
    val x: Float,
    val y: Float,
)

/**
 * Perspective crop quad on the rotated square canvas (corners in `0f..1f`).
 * Order is clockwise from top-left, matching [Matrix.setPolyToPoly] source points.
 */
data class NormalizedPerspectiveQuad(
    val topLeft: NormalizedPoint,
    val topRight: NormalizedPoint,
    val bottomRight: NormalizedPoint,
    val bottomLeft: NormalizedPoint,
) {
    fun corners(): List<NormalizedPoint> = listOf(topLeft, topRight, bottomRight, bottomLeft)

    /** Axis-aligned bounds of the four corners (for returning to rect crop mode). */
    fun boundingRect(): NormalizedCropRect {
        val xs = corners().map { it.x }
        val ys = corners().map { it.y }
        val left = xs.minOrNull() ?: 0f
        val top = ys.minOrNull() ?: 0f
        val right = xs.maxOrNull() ?: 1f
        val bottom = ys.maxOrNull() ?: 1f
        return PhotoEditSaver.clampCropRectFree(
            NormalizedCropRect(
                left,
                top,
                right.coerceAtLeast(left + 0.06f),
                bottom.coerceAtLeast(top + 0.06f),
            ),
        )
    }

    companion object {
        fun fromRect(rect: NormalizedCropRect): NormalizedPerspectiveQuad = NormalizedPerspectiveQuad(
            topLeft = NormalizedPoint(rect.left, rect.top),
            topRight = NormalizedPoint(rect.right, rect.top),
            bottomRight = NormalizedPoint(rect.right, rect.bottom),
            bottomLeft = NormalizedPoint(rect.left, rect.bottom),
        )
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

/** Result of checking whether the crop frame covers empty zones outside the photo. */
data class CropInsetAnalysis(
    val hasEmptyZones: Boolean,
    val suggestedCrop: NormalizedCropRect?,
) {
    companion object {
        val None = CropInsetAnalysis(hasEmptyZones = false, suggestedCrop = null)
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

    sealed class CopyResult {
        data class Success(
            val uri: Uri,
            val sizeBytes: Long,
            /** Folder label shown in the toast, e.g. `DCIM/Camera` or `Pictures/HSK`. */
            val folderLabel: String,
        ) : CopyResult()

        data object Failed : CopyResult()
    }

    fun save(
        photoId: Long,
        uri: Uri,
        mimeType: String?,
        rotationDegrees: Float,
        crop: NormalizedCropRect,
        /**
         * When non-null, applies perspective warp instead of axis-aligned [crop].
         */
        perspectiveQuad: NormalizedPerspectiveQuad? = null,
        blurStrokes: List<NormalizedBlurStroke> = emptyList(),
        blurStrength: Float = 0.5f,
        /**
         * When non-null and still valid, keeps that pre-edit original across repeated saves
         * on the same photo for the session.
         */
        existingUndo: PendingEditUndo? = null,
    ): SaveResult {
        val targetUri = MediaStoreImageUri.resolve(context, uri)
        val encoded =
            renderEditedBytes(
                targetUri,
                mimeType,
                rotationDegrees,
                crop,
                perspectiveQuad,
                blurStrokes,
                blurStrength,
            )
                ?: return SaveResult.Failed

        val reuseBackup =
            existingUndo != null &&
                existingUndo.photoId == photoId &&
                existingUndo.uri == targetUri &&
                existingUndo.backupFile.isFile
        var backupCreated = false
        if (!reuseBackup) {
            when (backupOriginal(targetUri, photoId)) {
                BackupResult.NeedsWritePermission -> return SaveResult.NeedsWritePermission
                BackupResult.Failed -> return SaveResult.Failed
                BackupResult.Success -> backupCreated = true
            }
        }

        return when (val written = writeBytes(targetUri, encoded)) {
            is SaveResult.Success -> written.copy(backupCreated = backupCreated || reuseBackup)

            else -> {
                if (backupCreated && !reuseBackup) {
                    clearEditBackup(photoId)
                }
                written
            }
        }
    }

    /**
     * Writes the edited image as a new file next to [sourceUri] when its MediaStore
     * folder is known (`*_copy`); otherwise falls back to Pictures/HSK.
     */
    fun saveAsCopy(
        sourceUri: Uri,
        mimeType: String?,
        rotationDegrees: Float,
        crop: NormalizedCropRect,
        perspectiveQuad: NormalizedPerspectiveQuad? = null,
        blurStrokes: List<NormalizedBlurStroke> = emptyList(),
        blurStrength: Float = 0.5f,
        displayName: String? = null,
    ): CopyResult {
        val source = MediaStoreImageUri.resolve(context, sourceUri)
        val encoded =
            renderEditedBytes(
                source,
                mimeType,
                rotationDegrees,
                crop,
                perspectiveQuad,
                blurStrokes,
                blurStrength,
            )
                ?: return CopyResult.Failed
        val written =
            PhotoEditCopyStore(context).writeCopy(
                sourceUri = source,
                encoded = encoded,
                mimeType = resolvedOutputMime(mimeType),
                displayName = displayName,
            ) ?: return CopyResult.Failed
        return CopyResult.Success(
            uri = written.uri,
            sizeBytes = written.sizeBytes,
            folderLabel = written.folderLabel,
        )
    }

    private fun renderEditedBytes(
        uri: Uri,
        mimeType: String?,
        rotationDegrees: Float,
        crop: NormalizedCropRect,
        perspectiveQuad: NormalizedPerspectiveQuad? = null,
        blurStrokes: List<NormalizedBlurStroke> = emptyList(),
        blurStrength: Float = 0.5f,
    ): ByteArray? {
        val oriented = decodeOrientedBitmap(uri) ?: return null
        val workspace =
            renderRotatedOnSquare(oriented, rotationDegrees) ?: run {
                oriented.recycle()
                return null
            }
        if (workspace !== oriented) {
            oriented.recycle()
        }
        if (blurStrokes.isNotEmpty() &&
            !PhotoBlurRenderer.apply(
                bitmap = workspace,
                strokes = blurStrokes,
                strength = blurStrength,
            )
        ) {
            workspace.recycle()
            return null
        }
        val cropped =
            if (perspectiveQuad != null) {
                perspectiveCropBitmap(workspace, clampPerspectiveQuad(perspectiveQuad))
            } else {
                cropBitmap(workspace, clampCropRectFree(crop))
            } ?: run {
                workspace.recycle()
                return null
            }
        if (cropped !== workspace) {
            workspace.recycle()
        }
        val width = cropped.width
        val height = cropped.height
        val encoded =
            encodeBitmap(cropped, mimeType) ?: run {
                cropped.recycle()
                return null
            }
        cropped.recycle()
        val resolvedMime = resolvedOutputMime(mimeType)
        return ExifPreserver.withPreservedExif(
            context = context,
            sourceUri = uri,
            mimeType = resolvedMime,
            encoded = encoded,
            width = width,
            height = height,
            fileExtension = extensionForMime(resolvedMime),
        )
    }

    private fun resolvedOutputMime(mimeType: String?): String = when {
        mimeType.equals("image/png", ignoreCase = true) -> "image/png"
        mimeType.equals("image/webp", ignoreCase = true) -> "image/webp"
        else -> "image/jpeg"
    }

    private fun extensionForMime(mimeType: String): String = when (mimeType.lowercase(Locale.US)) {
        "image/png" -> "png"
        "image/webp" -> "webp"
        else -> "jpg"
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
     * If [crop] covers empty canvas outside the photo (letterbox and/or rotation gaps),
     * returns the maximum-area axis-aligned frame that fits entirely inside the photo.
     * Works at any [rotationDegrees], including 0°.
     */
    fun analyzeCropEmptyZones(
        imageWidth: Int,
        imageHeight: Int,
        rotationDegrees: Float,
        crop: NormalizedCropRect,
    ): CropInsetAnalysis {
        if (imageWidth <= 0 || imageHeight <= 0) {
            return CropInsetAnalysis.None
        }
        val geometry =
            photoGeometry(imageWidth, imageHeight, rotationDegrees)
                ?: return CropInsetAnalysis.None
        if (!cropCoversEmptyZones(crop, geometry)) {
            return CropInsetAnalysis.None
        }
        val suggested =
            maxAreaInscribedCrop(geometry) ?: return CropInsetAnalysis.None
        if (rectsAlmostEqual(suggested, crop)) {
            return CropInsetAnalysis.None
        }
        return CropInsetAnalysis(hasEmptyZones = true, suggestedCrop = suggested)
    }

    fun cropWithoutEmptyZones(
        imageWidth: Int,
        imageHeight: Int,
        rotationDegrees: Float,
        crop: NormalizedCropRect,
    ): NormalizedCropRect? = analyzeCropEmptyZones(
        imageWidth = imageWidth,
        imageHeight = imageHeight,
        rotationDegrees = rotationDegrees,
        crop = crop,
    ).suggestedCrop

    /**
     * Largest axis-aligned rectangle that stays entirely inside the photo on the
     * square canvas (accounts for letterbox and [rotationDegrees]).
     */
    fun photoInscribedBounds(
        imageWidth: Int,
        imageHeight: Int,
        rotationDegrees: Float,
    ): NormalizedCropRect {
        val geometry =
            photoGeometry(imageWidth, imageHeight, rotationDegrees)
                ?: return imageContentCrop(imageWidth, imageHeight)
        return maxAreaInscribedCrop(geometry)
            ?: imageContentCrop(imageWidth, imageHeight)
    }

    private data class PhotoGeometry(
        val halfWidth: Float,
        val halfHeight: Float,
        val cos: Float,
        val sin: Float,
    )

    /**
     * Unrotated photo half-size in normalized square coords (same as [imageContentCrop]),
     * plus rotation used by [renderRotatedOnSquare] (clockwise, y-down).
     */
    private fun photoGeometry(
        imageWidth: Int,
        imageHeight: Int,
        rotationDegrees: Float,
    ): PhotoGeometry? {
        val diag = hypot(imageWidth.toFloat(), imageHeight.toFloat())
        if (diag <= 0f) {
            return null
        }
        val rad = Math.toRadians(rotationDegrees.toDouble())
        return PhotoGeometry(
            halfWidth = imageWidth / (2f * diag),
            halfHeight = imageHeight / (2f * diag),
            cos = kotlin.math.cos(rad).toFloat(),
            sin = kotlin.math.sin(rad).toFloat(),
        )
    }

    private fun isInsidePhoto(
        x: Float,
        y: Float,
        geometry: PhotoGeometry,
    ): Boolean {
        val sx = x - 0.5f
        val sy = y - 0.5f
        val localX = sx * geometry.cos + sy * geometry.sin
        val localY = -sx * geometry.sin + sy * geometry.cos
        return abs(localX) <= geometry.halfWidth + CropInsetEpsilon &&
            abs(localY) <= geometry.halfHeight + CropInsetEpsilon
    }

    private fun cropCoversEmptyZones(
        crop: NormalizedCropRect,
        geometry: PhotoGeometry,
    ): Boolean {
        val midX = (crop.left + crop.right) * 0.5f
        val midY = (crop.top + crop.bottom) * 0.5f
        val samples =
            arrayOf(
                crop.left to crop.top,
                crop.right to crop.top,
                crop.left to crop.bottom,
                crop.right to crop.bottom,
                crop.left to midY,
                crop.right to midY,
                midX to crop.top,
                midX to crop.bottom,
            )
        return samples.any { (x, y) -> !isInsidePhoto(x, y, geometry) }
    }

    private fun rectsAlmostEqual(
        a: NormalizedCropRect,
        b: NormalizedCropRect,
    ): Boolean = abs(a.left - b.left) <= CropInsetRectEpsilon &&
        abs(a.top - b.top) <= CropInsetRectEpsilon &&
        abs(a.right - b.right) <= CropInsetRectEpsilon &&
        abs(a.bottom - b.bottom) <= CropInsetRectEpsilon

    /**
     * Maximum-area axis-aligned rectangle inside the photo. For a centered rotated
     * rectangle the optimum shares the photo center; half-sizes come from active
     * edge constraints (with a dense search as backup).
     */
    private fun maxAreaInscribedCrop(geometry: PhotoGeometry): NormalizedCropRect? {
        var bestHalfW = 0f
        var bestHalfH = 0f
        var bestArea = 0f

        fun consider(
            halfW: Float,
            halfH: Float,
        ) {
            if (halfW <= CropInsetMinHalf || halfH <= CropInsetMinHalf) {
                return
            }
            if (!aaRectInsidePhoto(halfW, halfH, geometry)) {
                return
            }
            val area = halfW * halfH
            if (area > bestArea) {
                bestArea = area
                bestHalfW = halfW
                bestHalfH = halfH
            }
        }

        val cos = geometry.cos
        val sin = geometry.sin
        val hw = geometry.halfWidth
        val hh = geometry.halfHeight
        // Corner on both photo edges: solve for all sign combinations.
        for (signX in floatArrayOf(-1f, 1f)) {
            for (signY in floatArrayOf(-1f, 1f)) {
                val rhsX = signX * hw
                val rhsY = signY * hh
                // Inverse of [cos, sin; -sin, cos] is [cos, -sin; sin, cos].
                val halfW = cos * rhsX - sin * rhsY
                val halfH = sin * rhsX + cos * rhsY
                if (halfW > 0f && halfH > 0f) {
                    consider(halfW, halfH)
                }
            }
        }

        val maxHalfH =
            min(
                if (abs(sin) > CropInsetEpsilon) hw / abs(sin) else Float.MAX_VALUE,
                if (abs(cos) > CropInsetEpsilon) hh / abs(cos) else Float.MAX_VALUE,
            ).coerceIn(CropInsetMinHalf, 0.5f)
        val steps = 256
        for (step in 1..steps) {
            val halfH = maxHalfH * step / steps
            consider(maxHalfWidthForHalfHeight(halfH, geometry), halfH)
        }

        if (bestHalfW <= CropInsetMinHalf || bestHalfH <= CropInsetMinHalf) {
            return null
        }
        return clampCropRectFree(
            NormalizedCropRect(
                left = 0.5f - bestHalfW,
                top = 0.5f - bestHalfH,
                right = 0.5f + bestHalfW,
                bottom = 0.5f + bestHalfH,
            ),
        )
    }

    private fun aaRectInsidePhoto(
        halfW: Float,
        halfH: Float,
        geometry: PhotoGeometry,
    ): Boolean {
        val corners =
            arrayOf(
                0.5f - halfW to 0.5f - halfH,
                0.5f + halfW to 0.5f - halfH,
                0.5f - halfW to 0.5f + halfH,
                0.5f + halfW to 0.5f + halfH,
            )
        return corners.all { (x, y) ->
            x in 0f..1f && y in 0f..1f && isInsidePhoto(x, y, geometry)
        }
    }

    private fun maxHalfWidthForHalfHeight(
        halfH: Float,
        geometry: PhotoGeometry,
    ): Float {
        if (!aaRectInsidePhoto(CropInsetMinHalf, halfH, geometry)) {
            return 0f
        }
        var low = CropInsetMinHalf
        var high = 0.5f
        repeat(48) {
            val mid = (low + high) * 0.5f
            if (aaRectInsidePhoto(mid, halfH, geometry)) {
                low = mid
            } else {
                high = mid
            }
        }
        return low
    }

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
     * Draws [bitmap] centered on a black square large enough for any rotation, then rotates it.
     */
    private fun renderRotatedOnSquare(
        bitmap: Bitmap,
        degrees: Float,
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
        canvas.drawColor(Color.BLACK)
        canvas.translate(diag / 2f, diag / 2f)
        canvas.rotate(degrees)
        canvas.drawBitmap(bitmap, -bitmap.width / 2f, -bitmap.height / 2f, null)
        return square
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

    /**
     * Warps the perspective quad on [bitmap] into an axis-aligned rectangle.
     * Destination size uses average edge lengths (Photoshop-style).
     */
    private fun perspectiveCropBitmap(
        bitmap: Bitmap,
        quad: NormalizedPerspectiveQuad,
    ): Bitmap? {
        if (!isPerspectiveQuadValid(quad)) {
            return null
        }
        val bw = bitmap.width.toFloat()
        val bh = bitmap.height.toFloat()
        if (bw <= 0f || bh <= 0f) {
            return null
        }
        val tlX = quad.topLeft.x * bw
        val tlY = quad.topLeft.y * bh
        val trX = quad.topRight.x * bw
        val trY = quad.topRight.y * bh
        val brX = quad.bottomRight.x * bw
        val brY = quad.bottomRight.y * bh
        val blX = quad.bottomLeft.x * bw
        val blY = quad.bottomLeft.y * bh
        val topLen = hypot(trX - tlX, trY - tlY)
        val bottomLen = hypot(brX - blX, brY - blY)
        val leftLen = hypot(blX - tlX, blY - tlY)
        val rightLen = hypot(brX - trX, brY - trY)
        val dstW = ((topLen + bottomLen) / 2f).roundToInt().coerceAtLeast(1)
        val dstH = ((leftLen + rightLen) / 2f).roundToInt().coerceAtLeast(1)
        val matrix = Matrix()
        val mapped =
            matrix.setPolyToPoly(
                floatArrayOf(tlX, tlY, trX, trY, brX, brY, blX, blY),
                0,
                floatArrayOf(0f, 0f, dstW.toFloat(), 0f, dstW.toFloat(), dstH.toFloat(), 0f, dstH.toFloat()),
                0,
                4,
            )
        if (!mapped) {
            return null
        }
        val out =
            try {
                Bitmap.createBitmap(dstW, dstH, Bitmap.Config.ARGB_8888)
            } catch (_: OutOfMemoryError) {
                return null
            }
        val canvas = Canvas(out)
        canvas.drawColor(Color.BLACK)
        val paint = Paint(Paint.FILTER_BITMAP_FLAG or Paint.ANTI_ALIAS_FLAG)
        canvas.drawBitmap(bitmap, matrix, paint)
        return out
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
            ExifPreserver.syncMediaStoreDateTaken(context, uri, bytes)
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
        private const val CropInsetMinHalf = 0.02f
        private const val CropInsetEpsilon = 1e-4f
        private const val CropInsetRectEpsilon = 0.004f
        private const val PerspectiveMinEdge = 0.06f
        const val MIN_BLUR_BRUSH_RADIUS = 0.015f
        const val MAX_BLUR_BRUSH_RADIUS = 0.18f

        /** True when [MediaStore.createWriteRequest] can be used for [uri] on this API level. */
        fun canRequestMediaStoreWrite(uri: Uri): Boolean {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) {
                return false
            }
            if (uri.authority != MediaStore.AUTHORITY) {
                return false
            }
            val path = uri.path.orEmpty().lowercase(Locale.US)
            // Photo Picker / grant URIs share authority "media" but are not writable.
            if (path.contains("/picker/") || path.contains("photopicker")) {
                return false
            }
            // Classic MediaStore image rows, e.g. /external/images/media/123
            return path.contains("/images/media/")
        }

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
         * Largest rectangle with [imageAspect] that fits entirely inside [rect]
         * (centered). Preserving area would spill into letterbox when switching
         * e.g. landscape photo content → 3:4.
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
            // Dummy size only supplies the target aspect; [fitCropIntoBounds] sizes it.
            val aspectSeed =
                NormalizedCropRect(
                    left = 0f,
                    top = 0f,
                    right = aspect.coerceIn(0.06f, 1f),
                    bottom = 1f,
                )
            return clampCropRect(fitCropIntoBounds(aspectSeed, rect), aspect)
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
         * Keep [rect] inside [bounds], preserving size when possible (for drag moves).
         * If [imageAspect] is set, the result keeps that aspect ratio.
         */
        fun clampCropRectInsideBounds(
            rect: NormalizedCropRect,
            bounds: NormalizedCropRect,
            imageAspect: Float? = null,
            minNormalizedSide: Float = 0.06f,
        ): NormalizedCropRect {
            val bw = bounds.width.coerceAtLeast(minNormalizedSide)
            val bh = bounds.height.coerceAtLeast(minNormalizedSide)
            if (imageAspect == null) {
                val width = rect.width.coerceIn(minNormalizedSide, bw)
                val height = rect.height.coerceIn(minNormalizedSide, bh)
                val left =
                    rect.left.coerceIn(
                        bounds.left,
                        (bounds.right - width).coerceAtLeast(bounds.left),
                    )
                val top =
                    rect.top.coerceIn(
                        bounds.top,
                        (bounds.bottom - height).coerceAtLeast(bounds.top),
                    )
                return NormalizedCropRect(left, top, left + width, top + height)
            }

            val aspect = imageAspect.coerceAtLeast(1e-6f)
            var width = rect.width.coerceAtLeast(minNormalizedSide)
            var height = width / aspect
            if (height < minNormalizedSide) {
                height = minNormalizedSide
                width = height * aspect
            }
            if (width > bw || height > bh) {
                if (bw / bh > aspect) {
                    height = bh
                    width = height * aspect
                } else {
                    width = bw
                    height = width / aspect
                }
            }
            val left =
                rect.left.coerceIn(
                    bounds.left,
                    (bounds.right - width).coerceAtLeast(bounds.left),
                )
            val top =
                rect.top.coerceIn(
                    bounds.top,
                    (bounds.bottom - height).coerceAtLeast(bounds.top),
                )
            return NormalizedCropRect(left, top, left + width, top + height)
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

        /** Clamp each corner into `0..1` and keep a convex, non-degenerate quad when possible. */
        fun clampPerspectiveQuad(
            quad: NormalizedPerspectiveQuad,
            minEdge: Float = PerspectiveMinEdge,
        ): NormalizedPerspectiveQuad {
            val clamped =
                NormalizedPerspectiveQuad(
                    topLeft = clampPoint(quad.topLeft),
                    topRight = clampPoint(quad.topRight),
                    bottomRight = clampPoint(quad.bottomRight),
                    bottomLeft = clampPoint(quad.bottomLeft),
                )
            if (isPerspectiveQuadValid(clamped, minEdge)) {
                return clamped
            }
            return NormalizedPerspectiveQuad.fromRect(clamped.boundingRect())
        }

        /**
         * Move one corner by [dx]/[dy] (normalized). Returns previous quad if the result
         * would be non-convex or degenerate.
         */
        fun dragPerspectiveCorner(
            quad: NormalizedPerspectiveQuad,
            cornerIndex: Int,
            dx: Float,
            dy: Float,
            minEdge: Float = PerspectiveMinEdge,
        ): NormalizedPerspectiveQuad {
            val corners = quad.corners().toMutableList()
            if (cornerIndex !in corners.indices) {
                return quad
            }
            corners[cornerIndex] =
                clampPoint(
                    NormalizedPoint(
                        x = corners[cornerIndex].x + dx,
                        y = corners[cornerIndex].y + dy,
                    ),
                )
            val next = quadFromCorners(corners)
            return if (isPerspectiveQuadValid(next, minEdge)) next else quad
        }

        /** Translate all corners; rejects moves that push any corner outside `0..1`. */
        fun movePerspectiveQuad(
            quad: NormalizedPerspectiveQuad,
            dx: Float,
            dy: Float,
        ): NormalizedPerspectiveQuad {
            val corners = quad.corners()
            val minX = corners.minOf { it.x }
            val maxX = corners.maxOf { it.x }
            val minY = corners.minOf { it.y }
            val maxY = corners.maxOf { it.y }
            val shiftX = dx.coerceIn(-minX, 1f - maxX)
            val shiftY = dy.coerceIn(-minY, 1f - maxY)
            if (shiftX == 0f && shiftY == 0f) {
                return quad
            }
            return NormalizedPerspectiveQuad(
                topLeft = NormalizedPoint(
                    quad.topLeft.x + shiftX,
                    quad.topLeft.y + shiftY,
                ),
                topRight = NormalizedPoint(
                    quad.topRight.x + shiftX,
                    quad.topRight.y + shiftY,
                ),
                bottomRight = NormalizedPoint(
                    quad.bottomRight.x + shiftX,
                    quad.bottomRight.y + shiftY,
                ),
                bottomLeft = NormalizedPoint(
                    quad.bottomLeft.x + shiftX,
                    quad.bottomLeft.y + shiftY,
                ),
            )
        }

        fun isPerspectiveQuadValid(
            quad: NormalizedPerspectiveQuad,
            minEdge: Float = PerspectiveMinEdge,
        ): Boolean {
            val c = quad.corners()
            if (c.any { it.x !in 0f..1f || it.y !in 0f..1f }) {
                return false
            }
            for (i in 0..3) {
                val a = c[i]
                val b = c[(i + 1) % 4]
                if (hypot(b.x - a.x, b.y - a.y) < minEdge) {
                    return false
                }
            }
            return isConvexQuad(c)
        }

        private fun clampPoint(point: NormalizedPoint): NormalizedPoint = NormalizedPoint(
            point.x.coerceIn(0f, 1f),
            point.y.coerceIn(0f, 1f),
        )

        private fun quadFromCorners(
            corners: List<NormalizedPoint>,
        ): NormalizedPerspectiveQuad = NormalizedPerspectiveQuad(
            topLeft = corners[0],
            topRight = corners[1],
            bottomRight = corners[2],
            bottomLeft = corners[3],
        )

        private fun isConvexQuad(corners: List<NormalizedPoint>): Boolean {
            if (corners.size != 4) {
                return false
            }
            var sign = 0
            for (i in 0..3) {
                val a = corners[i]
                val b = corners[(i + 1) % 4]
                val c = corners[(i + 2) % 4]
                val cross = (b.x - a.x) * (c.y - b.y) - (b.y - a.y) * (c.x - b.x)
                if (abs(cross) < 1e-6f) {
                    return false
                }
                val nextSign = if (cross > 0f) 1 else -1
                if (sign == 0) {
                    sign = nextSign
                } else if (sign != nextSign) {
                    return false
                }
            }
            return true
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
