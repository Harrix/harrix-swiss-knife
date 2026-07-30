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
import kotlin.math.ceil
import kotlin.math.hypot
import kotlin.math.min
import kotlin.math.roundToInt

/**
 * Normalized crop rectangle in the rotation workspace (square), each edge in `0f..1f`.
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

class PhotoEditSaver(
    private val context: Context,
) {
    sealed class SaveResult {
        data class Success(
            val sizeBytes: Long,
        ) : SaveResult()

        data object NeedsWritePermission : SaveResult()

        data object Failed : SaveResult()
    }

    fun save(
        uri: Uri,
        mimeType: String?,
        rotationDegrees: Float,
        crop: NormalizedCropRect,
    ): SaveResult {
        val oriented =
            decodeOrientedBitmap(uri) ?: return SaveResult.Failed
        val workspace =
            renderRotatedOnSquare(oriented, rotationDegrees) ?: run {
                oriented.recycle()
                return SaveResult.Failed
            }
        if (workspace !== oriented) {
            oriented.recycle()
        }
        val cropped =
            cropBitmap(workspace, crop) ?: run {
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

        return writeBytes(uri, encoded)
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
            SaveResult.Success(bytes.size.toLong())
        } ?: SaveResult.Failed
    } catch (_: SecurityException) {
        SaveResult.NeedsWritePermission
    } catch (_: Exception) {
        SaveResult.Failed
    }

    companion object {
        private const val JPEG_QUALITY = 95

        /**
         * Square workspace that fits in the viewport and can hold the image at any rotation.
         */
        fun rotationWorkspaceRect(
            viewportWidth: Float,
            viewportHeight: Float,
            imageWidth: Int,
            imageHeight: Int,
        ): FittedRect {
            val diag = hypot(imageWidth.toFloat(), imageHeight.toFloat())
            val hasInvalidSize =
                diag <= 0f || viewportWidth <= 0f || viewportHeight <= 0f
            if (hasInvalidSize) {
                return FittedRect(0f, 0f, 0f, 0f)
            }
            val scale = min(viewportWidth / diag, viewportHeight / diag)
            val box = diag * scale
            val left = (viewportWidth - box) / 2f
            val top = (viewportHeight - box) / 2f
            return FittedRect(left, top, box, box)
        }

        /**
         * Draw size of the unrotated image inside [workspace].
         */
        fun imageDrawSizeInWorkspace(
            imageWidth: Int,
            imageHeight: Int,
            workspace: FittedRect,
        ): Pair<Float, Float> {
            val diag = hypot(imageWidth.toFloat(), imageHeight.toFloat())
            if (diag <= 0f || workspace.width <= 0f) {
                return 0f to 0f
            }
            val scale = workspace.width / diag
            return imageWidth * scale to imageHeight * scale
        }

        /**
         * Crop covering only the image pixels inside the square workspace (no black bars).
         */
        fun imageContentCrop(
            imageWidth: Int,
            imageHeight: Int,
        ): NormalizedCropRect {
            val diag = hypot(imageWidth.toFloat(), imageHeight.toFloat())
            if (diag <= 0f || imageHeight <= 0) {
                return NormalizedCropRect.Full
            }
            val width = (imageWidth / diag).coerceIn(0f, 1f)
            val height = (imageHeight / diag).coerceIn(0f, 1f)
            val left = ((1f - width) / 2f).coerceIn(0f, 1f)
            val top = ((1f - height) / 2f).coerceIn(0f, 1f)
            return clampCropRect(
                rect =
                NormalizedCropRect(
                    left = left,
                    top = top,
                    right = (left + width).coerceIn(0f, 1f),
                    bottom = (top + height).coerceIn(0f, 1f),
                ),
                imageAspect = imageWidth.toFloat() / imageHeight.toFloat(),
            )
        }

        /**
         * Clamp crop to `0..1`, keeping [imageAspect] (`width / height` of the source file).
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
