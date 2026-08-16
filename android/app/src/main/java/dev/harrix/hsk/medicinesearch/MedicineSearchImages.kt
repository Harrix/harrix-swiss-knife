package dev.harrix.hsk.medicinesearch

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
import java.io.IOException
import kotlin.math.max
import kotlin.math.roundToInt

/**
 * Downscales gallery photos before they are sent to the AI provider.
 */
object MedicineSearchImages {
    const val MAX_SIDE = 1600
    private const val JPEG_QUALITY = 85

    fun loadForAi(
        context: Context,
        uri: Uri,
    ): Pair<ByteArray, String> {
        val original = decode(context, uri) ?: throw IOException("Failed to read photo")
        val scaled = downscale(original)
        if (scaled !== original && !original.isRecycled) {
            original.recycle()
        }
        return try {
            val bytes = encodeJpeg(scaled)
            if (bytes.isEmpty()) {
                throw IOException("Failed to encode photo")
            }
            bytes to "image/jpeg"
        } finally {
            if (!scaled.isRecycled) {
                scaled.recycle()
            }
        }
    }

    private fun decode(
        context: Context,
        uri: Uri,
    ): Bitmap? {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            return try {
                val source = ImageDecoder.createSource(context.contentResolver, uri)
                ImageDecoder.decodeBitmap(source) { decoder, info, _ ->
                    decoder.allocator = ImageDecoder.ALLOCATOR_SOFTWARE
                    val width = info.size.width
                    val height = info.size.height
                    val longest = max(width, height)
                    if (longest > MAX_SIDE) {
                        val scale = MAX_SIDE.toFloat() / longest
                        decoder.setTargetSize(
                            (width * scale).roundToInt().coerceAtLeast(1),
                            (height * scale).roundToInt().coerceAtLeast(1),
                        )
                    }
                }
            } catch (_: Exception) {
                null
            }
        }
        return decodeLegacy(context, uri)
    }

    private fun decodeLegacy(
        context: Context,
        uri: Uri,
    ): Bitmap? {
        val bytes =
            try {
                context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
            } catch (_: Exception) {
                null
            } ?: return null
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeByteArray(bytes, 0, bytes.size, bounds)
        val longest = max(bounds.outWidth, bounds.outHeight)
        val options =
            BitmapFactory.Options().apply {
                inSampleSize = sampleSize(longest, MAX_SIDE)
            }
        val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size, options) ?: return null
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

    private fun sampleSize(
        longest: Int,
        maxSide: Int,
    ): Int {
        if (longest <= maxSide || longest <= 0) {
            return 1
        }
        var sample = 1
        while (longest / (sample * 2) >= maxSide) {
            sample *= 2
        }
        return sample
    }

    private fun downscale(bitmap: Bitmap): Bitmap {
        val longest = max(bitmap.width, bitmap.height)
        if (longest <= MAX_SIDE) {
            return bitmap
        }
        val scale = MAX_SIDE.toFloat() / longest
        val width = (bitmap.width * scale).roundToInt().coerceAtLeast(1)
        val height = (bitmap.height * scale).roundToInt().coerceAtLeast(1)
        return Bitmap.createScaledBitmap(bitmap, width, height, true)
    }

    private fun encodeJpeg(bitmap: Bitmap): ByteArray {
        val output = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, JPEG_QUALITY, output)
        return output.toByteArray()
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
}
