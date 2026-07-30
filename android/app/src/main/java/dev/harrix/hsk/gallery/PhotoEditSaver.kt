package dev.harrix.hsk.gallery

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.ImageDecoder
import android.graphics.Matrix
import android.net.Uri
import android.os.Build
import androidx.exifinterface.media.ExifInterface
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

/**
 * Normalized crop rectangle in rotated-image space, each edge in `0f..1f`.
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
        rotationQuarterTurns: Int,
        crop: NormalizedCropRect,
    ): SaveResult {
        val oriented =
            decodeOrientedBitmap(uri) ?: return SaveResult.Failed
        val rotated =
            rotateBitmap(oriented, positiveMod(rotationQuarterTurns, 4))
        if (rotated !== oriented) {
            oriented.recycle()
        }
        val cropped =
            cropBitmap(rotated, crop) ?: run {
                if (rotated !== oriented) {
                    // already recycled oriented if different; rotated still live
                }
                rotated.recycle()
                return SaveResult.Failed
            }
        if (cropped !== rotated) {
            rotated.recycle()
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

    private fun rotateBitmap(
        bitmap: Bitmap,
        quarterTurns: Int,
    ): Bitmap {
        if (quarterTurns == 0) {
            return bitmap
        }
        val matrix = Matrix().apply { postRotate(quarterTurns * 90f) }
        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
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

        fun positiveMod(
            value: Int,
            mod: Int,
        ): Int = ((value % mod) + mod) % mod

        /**
         * Fitted image rectangle inside [viewportWidth] x [viewportHeight] for ContentScale.Fit.
         */
        fun fittedImageRect(
            viewportWidth: Float,
            viewportHeight: Float,
            imageWidth: Int,
            imageHeight: Int,
            rotationQuarterTurns: Int,
        ): FittedRect {
            val turns = positiveMod(rotationQuarterTurns, 4)
            val contentW = if (turns % 2 == 0) imageWidth.toFloat() else imageHeight.toFloat()
            val contentH = if (turns % 2 == 0) imageHeight.toFloat() else imageWidth.toFloat()
            val hasInvalidSize =
                contentW <= 0f ||
                    contentH <= 0f ||
                    viewportWidth <= 0f ||
                    viewportHeight <= 0f
            if (hasInvalidSize) {
                return FittedRect(0f, 0f, 0f, 0f)
            }
            val scale = min(viewportWidth / contentW, viewportHeight / contentH)
            val drawW = contentW * scale
            val drawH = contentH * scale
            val left = (viewportWidth - drawW) / 2f
            val top = (viewportHeight - drawH) / 2f
            return FittedRect(left, top, drawW, drawH)
        }

        fun clampCropRect(
            rect: NormalizedCropRect,
            minNormalizedSide: Float = 0.08f,
        ): NormalizedCropRect {
            var left = rect.left
            var top = rect.top
            var right = rect.right
            var bottom = rect.bottom
            var width = right - left
            var height = bottom - top
            val aspect = width / height
            width = max(width, minNormalizedSide)
            height = width / aspect
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
            right = left + width
            bottom = top + height
            return NormalizedCropRect(left, top, right, bottom)
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
