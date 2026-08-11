package dev.harrix.hsk.gallery

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.net.Uri
import androidx.exifinterface.media.ExifInterface
import java.io.ByteArrayInputStream
import kotlin.math.abs
import kotlin.math.atan2
import kotlin.math.max
import kotlin.math.roundToInt

/**
 * Estimates a small horizon tilt from a downscaled preview (no OpenCV).
 *
 * Returns an additive [rotationDegrees] delta (clockwise, same as the photo editor)
 * that levels near-horizontal / near-vertical structure, or null when the tilt is
 * tiny, too large, or unreliable.
 */
object HorizonDetector {
    private const val MaxPreviewSide = 240
    private const val MinAbsDegrees = 0.5f
    private const val MaxAbsDegrees = 12f
    private const val BinSizeDegrees = 0.5f
    private const val MinPeakVotes = 48f
    private const val PeakDominance = 1.25f

    /**
     * @param currentRotationDegrees editor rotation already applied to the preview
     * @return clockwise degrees to add to [currentRotationDegrees], or null
     */
    fun detectDeltaDegrees(
        context: Context,
        uri: Uri,
        currentRotationDegrees: Float,
    ): Float? {
        val preview = decodePreview(context, uri) ?: return null
        try {
            val oriented =
                if (abs(currentRotationDegrees) < 0.05f) {
                    preview
                } else {
                    rotateBitmap(preview, currentRotationDegrees)
                }
            try {
                return estimateCorrectionDegrees(oriented)
            } finally {
                if (oriented !== preview && !oriented.isRecycled) {
                    oriented.recycle()
                }
            }
        } finally {
            if (!preview.isRecycled) {
                preview.recycle()
            }
        }
    }

    private fun estimateCorrectionDegrees(bitmap: Bitmap): Float? {
        val width = bitmap.width
        val height = bitmap.height
        if (width < 16 || height < 16) {
            return null
        }
        val pixels = IntArray(width * height)
        bitmap.getPixels(pixels, 0, width, 0, 0, width, height)
        val gray =
            IntArray(pixels.size) { index ->
                val c = pixels[index]
                val r = (c shr 16) and 0xff
                val g = (c shr 8) and 0xff
                val b = c and 0xff
                (r * 77 + g * 150 + b * 29) shr 8
            }
        val blurred = boxBlurGray(gray, width, height)
        val binCount = ((MaxAbsDegrees * 2f) / BinSizeDegrees).roundToInt() + 1
        val bins = FloatArray(binCount)
        var maxMag = 1
        val marginX = max(2, (width * 0.06f).roundToInt())
        val marginY = max(2, (height * 0.06f).roundToInt())
        var y = marginY
        while (y < height - marginY) {
            var x = marginX
            while (x < width - marginX) {
                val i = y * width + x
                val gx =
                    -blurred[i - width - 1] - 2 * blurred[i - 1] - blurred[i + width - 1] +
                        blurred[i - width + 1] + 2 * blurred[i + 1] + blurred[i + width + 1]
                val gy =
                    -blurred[i - width - 1] - 2 * blurred[i - width] - blurred[i - width + 1] +
                        blurred[i + width - 1] + 2 * blurred[i + width] + blurred[i + width + 1]
                val mag = abs(gx) + abs(gy)
                if (mag > maxMag) {
                    maxMag = mag
                }
                x += 2
            }
            y += 2
        }
        val threshold = max(40, (maxMag * 0.22f).roundToInt())
        y = marginY
        while (y < height - marginY) {
            var x = marginX
            while (x < width - marginX) {
                val i = y * width + x
                val gx =
                    -blurred[i - width - 1] - 2 * blurred[i - 1] - blurred[i + width - 1] +
                        blurred[i - width + 1] + 2 * blurred[i + 1] + blurred[i + width + 1]
                val gy =
                    -blurred[i - width - 1] - 2 * blurred[i - width] - blurred[i - width + 1] +
                        blurred[i + width - 1] + 2 * blurred[i + width] + blurred[i + width + 1]
                val mag = abs(gx) + abs(gy)
                if (mag >= threshold) {
                    // Line orientation (degrees): 0 = horizontal, + = right side lower.
                    val lineAngle =
                        normalizeLineAngle(
                            Math.toDegrees(atan2(gy.toDouble(), gx.toDouble())).toFloat() + 90f,
                        )
                    val weight = mag.toFloat()
                    accumulateNearAxis(bins, lineAngle, weight)
                    // Vertical structure: convert to equivalent horizon correction.
                    val verticalAsHorizon = normalizeLineAngle(lineAngle - 90f)
                    accumulateNearAxis(bins, verticalAsHorizon, weight * 0.85f)
                }
                x += 2
            }
            y += 2
        }

        var bestIndex = -1
        var bestVotes = 0f
        var secondVotes = 0f
        for (index in bins.indices) {
            val votes = bins[index]
            if (votes > bestVotes) {
                secondVotes = bestVotes
                bestVotes = votes
                bestIndex = index
            } else if (votes > secondVotes) {
                secondVotes = votes
            }
        }
        if (bestIndex < 0 || bestVotes < MinPeakVotes) {
            return null
        }
        if (secondVotes > 0f && bestVotes < secondVotes * PeakDominance) {
            return null
        }
        val correction = -MaxAbsDegrees + bestIndex * BinSizeDegrees
        val absCorrection = abs(correction)
        if (absCorrection < MinAbsDegrees || absCorrection > MaxAbsDegrees) {
            return null
        }
        return correction
    }

    private fun accumulateNearAxis(
        bins: FloatArray,
        angleDegrees: Float,
        weight: Float,
    ) {
        val absAngle = abs(angleDegrees)
        if (absAngle > MaxAbsDegrees) {
            return
        }
        val index =
            ((angleDegrees + MaxAbsDegrees) / BinSizeDegrees)
                .roundToInt()
                .coerceIn(0, bins.lastIndex)
        bins[index] += weight
    }

    /** Normalize to [-90, 90]. */
    private fun normalizeLineAngle(degrees: Float): Float {
        var value = degrees % 180f
        if (value > 90f) {
            value -= 180f
        }
        if (value <= -90f) {
            value += 180f
        }
        return value
    }

    private fun boxBlurGray(
        src: IntArray,
        width: Int,
        height: Int,
    ): IntArray {
        val tmp = IntArray(src.size)
        val out = IntArray(src.size)
        for (y in 0 until height) {
            for (x in 0 until width) {
                var sum = 0
                var count = 0
                for (dx in -1..1) {
                    val xx = (x + dx).coerceIn(0, width - 1)
                    sum += src[y * width + xx]
                    count++
                }
                tmp[y * width + x] = sum / count
            }
        }
        for (y in 0 until height) {
            for (x in 0 until width) {
                var sum = 0
                var count = 0
                for (dy in -1..1) {
                    val yy = (y + dy).coerceIn(0, height - 1)
                    sum += tmp[yy * width + x]
                    count++
                }
                out[y * width + x] = sum / count
            }
        }
        return out
    }

    private fun rotateBitmap(
        bitmap: Bitmap,
        degrees: Float,
    ): Bitmap {
        val matrix = Matrix().apply { postRotate(degrees) }
        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
    }

    private fun decodePreview(
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
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) {
            return null
        }
        var sample = 1
        val maxSide = max(bounds.outWidth, bounds.outHeight)
        while (maxSide / sample > MaxPreviewSide) {
            sample *= 2
        }
        val options =
            BitmapFactory.Options().apply {
                inSampleSize = sample
                inPreferredConfig = Bitmap.Config.RGB_565
            }
        val decoded =
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size, options) ?: return null
        val orientation =
            try {
                ExifInterface(ByteArrayInputStream(bytes)).getAttributeInt(
                    ExifInterface.TAG_ORIENTATION,
                    ExifInterface.ORIENTATION_NORMAL,
                )
            } catch (_: Exception) {
                ExifInterface.ORIENTATION_NORMAL
            }
        return applyExifOrientation(decoded, orientation)
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
