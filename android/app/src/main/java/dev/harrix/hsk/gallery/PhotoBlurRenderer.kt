package dev.harrix.hsk.gallery

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.ImageDecoder
import android.graphics.Matrix
import android.graphics.Paint
import android.graphics.Path
import android.graphics.PorterDuff
import android.graphics.PorterDuffXfermode
import android.graphics.RectF
import android.net.Uri
import android.os.Build
import androidx.exifinterface.media.ExifInterface
import java.io.ByteArrayInputStream
import kotlin.math.ceil
import kotlin.math.hypot
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

/** One blur-brush stroke on the normalized rotated square canvas. */
data class NormalizedBlurStroke(
    val points: List<NormalizedPoint>,
    /** Brush radius as a fraction of the square workspace side. */
    val radius: Float,
)

/**
 * Paints a downsampled, filtered copy of a bitmap through the union of brush strokes.
 *
 * Downsampling supplies a scalable low-pass blur without allocating another full-resolution
 * bitmap, which is important for large phone photos.
 */
internal object PhotoBlurRenderer {
    /**
     * Creates a small square workspace that matches Photo Editor export geometry.
     *
     * Decodes a software bitmap from [uri] so the preview never depends on Coil hardware
     * bitmaps, which draw as black on a software canvas.
     */
    fun createPreviewBase(
        context: Context,
        uri: Uri,
        rotationDegrees: Float,
        maxWorkspaceSide: Int = 1200,
    ): Bitmap? {
        val decoded = decodeSoftwareBitmap(context, uri) ?: return null
        val sourceDiagonal = hypot(decoded.width.toDouble(), decoded.height.toDouble())
        val scale = min(1.0, maxWorkspaceSide / sourceDiagonal.coerceAtLeast(1.0))
        val source =
            if (scale < 0.999) {
                val targetWidth = (decoded.width * scale).roundToInt().coerceAtLeast(1)
                val targetHeight = (decoded.height * scale).roundToInt().coerceAtLeast(1)
                val scaled =
                    try {
                        Bitmap.createScaledBitmap(decoded, targetWidth, targetHeight, true)
                    } catch (_: OutOfMemoryError) {
                        decoded.recycle()
                        return null
                    }
                if (scaled !== decoded) {
                    decoded.recycle()
                }
                toSoftwareBitmap(scaled) ?: return null
            } else {
                toSoftwareBitmap(decoded) ?: return null
            }
        val side =
            ceil(hypot(source.width.toDouble(), source.height.toDouble()))
                .toInt()
                .coerceAtLeast(1)
        val square =
            try {
                Bitmap.createBitmap(side, side, Bitmap.Config.ARGB_8888)
            } catch (_: OutOfMemoryError) {
                source.recycle()
                return null
            }
        Canvas(square).apply {
            drawColor(Color.BLACK)
            translate(side / 2f, side / 2f)
            rotate(rotationDegrees)
            drawBitmap(source, -source.width / 2f, -source.height / 2f, null)
        }
        if (source !== square) {
            source.recycle()
        }
        return square
    }

    fun apply(
        bitmap: Bitmap,
        strokes: List<NormalizedBlurStroke>,
        strength: Float,
    ): Boolean {
        val amount = strength.coerceIn(0f, 1f)
        val requestedScale = (0.48f - amount * 0.42f).coerceIn(0.06f, 0.48f)
        val memorySafeScale =
            MAX_BLUR_WORKING_SIDE.toFloat() /
                max(bitmap.width, bitmap.height).coerceAtLeast(1)
        val scale = min(requestedScale, memorySafeScale).coerceAtMost(0.95f)
        val smallWidth = (bitmap.width * scale).roundToInt().coerceAtLeast(1)
        val smallHeight = (bitmap.height * scale).roundToInt().coerceAtLeast(1)
        val downsampled =
            try {
                Bitmap.createScaledBitmap(bitmap, smallWidth, smallHeight, true)
            } catch (_: OutOfMemoryError) {
                return false
            }
        if (downsampled === bitmap) {
            return true
        }
        val blurred =
            softenDownsampled(downsampled, amount) ?: run {
                downsampled.recycle()
                return false
            }
        if (blurred !== downsampled) {
            downsampled.recycle()
        }
        val working =
            ensureMutableArgb(blurred) ?: run {
                blurred.recycle()
                return false
            }
        if (working !== blurred) {
            blurred.recycle()
        }
        val mask =
            createStrokeMask(working.width, working.height, strokes) ?: run {
                working.recycle()
                return false
            }
        if (mask.width <= 1 || mask.height <= 1) {
            mask.recycle()
            working.recycle()
            return true
        }
        val feathered =
            featherMask(mask, strokes, working.width) ?: mask
        if (feathered !== mask) {
            mask.recycle()
        }
        Canvas(working).drawBitmap(
            feathered,
            0f,
            0f,
            Paint().apply {
                xfermode = PorterDuffXfermode(PorterDuff.Mode.DST_IN)
            },
        )
        feathered.recycle()
        Canvas(bitmap).drawBitmap(
            working,
            null,
            RectF(0f, 0f, bitmap.width.toFloat(), bitmap.height.toFloat()),
            Paint(Paint.ANTI_ALIAS_FLAG or Paint.FILTER_BITMAP_FLAG),
        )
        working.recycle()
        return true
    }

    private fun createStrokeMask(
        width: Int,
        height: Int,
        strokes: List<NormalizedBlurStroke>,
    ): Bitmap? {
        val mask =
            try {
                Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
            } catch (_: OutOfMemoryError) {
                return null
            }
        val clip = Path()
        val strokePaint =
            Paint(Paint.ANTI_ALIAS_FLAG).apply {
                style = Paint.Style.STROKE
                strokeCap = Paint.Cap.ROUND
                strokeJoin = Paint.Join.ROUND
            }
        strokes.forEach { stroke ->
            addStrokeToPath(
                destination = clip,
                stroke = stroke,
                bitmapWidth = width,
                bitmapHeight = height,
                strokePaint = strokePaint,
            )
        }
        if (clip.isEmpty) {
            mask.recycle()
            return Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888)
        }
        Canvas(mask).drawPath(
            clip,
            Paint(Paint.ANTI_ALIAS_FLAG).apply {
                color = Color.WHITE
                style = Paint.Style.FILL
            },
        )
        return mask
    }

    private fun featherMask(
        mask: Bitmap,
        strokes: List<NormalizedBlurStroke>,
        workingWidth: Int,
    ): Bitmap? {
        val radiusPx =
            strokes.maxOfOrNull { stroke ->
                stroke.radius.coerceIn(
                    PhotoEditSaver.MIN_BLUR_BRUSH_RADIUS,
                    PhotoEditSaver.MAX_BLUR_BRUSH_RADIUS,
                ) * workingWidth
            } ?: return mask
        val featherPx = (radiusPx * FEATHER_RADIUS_FRACTION).coerceIn(MIN_FEATHER_PX, MAX_FEATHER_PX)
        val scale = (2f / featherPx).coerceIn(MIN_FEATHER_SCALE, MAX_FEATHER_SCALE)
        val tinyWidth = (mask.width * scale).roundToInt().coerceAtLeast(1)
        val tinyHeight = (mask.height * scale).roundToInt().coerceAtLeast(1)
        val tiny =
            try {
                Bitmap.createScaledBitmap(mask, tinyWidth, tinyHeight, true)
            } catch (_: OutOfMemoryError) {
                return null
            }
        val feathered =
            try {
                Bitmap.createScaledBitmap(tiny, mask.width, mask.height, true)
            } catch (_: OutOfMemoryError) {
                tiny.recycle()
                return null
            }
        if (tiny !== feathered) {
            tiny.recycle()
        }
        return feathered
    }

    private fun ensureMutableArgb(bitmap: Bitmap): Bitmap? {
        if (bitmap.config == Bitmap.Config.ARGB_8888 && bitmap.isMutable) {
            return bitmap
        }
        return try {
            bitmap.copy(Bitmap.Config.ARGB_8888, true)
        } catch (_: OutOfMemoryError) {
            null
        }
    }

    /**
     * Adds a second downscale/upscale pass so the preview shows real blur instead of only
     * reduced resolution. The same path is used for final export.
     */
    private fun softenDownsampled(
        bitmap: Bitmap,
        strength: Float,
    ): Bitmap? {
        val scale = (0.88f - strength * 0.72f).coerceIn(0.16f, 0.88f)
        val tinyWidth = (bitmap.width * scale).roundToInt().coerceAtLeast(1)
        val tinyHeight = (bitmap.height * scale).roundToInt().coerceAtLeast(1)
        val tiny =
            try {
                Bitmap.createScaledBitmap(bitmap, tinyWidth, tinyHeight, true)
            } catch (_: OutOfMemoryError) {
                return null
            }
        val softened =
            try {
                Bitmap.createScaledBitmap(tiny, bitmap.width, bitmap.height, true)
            } catch (_: OutOfMemoryError) {
                tiny.recycle()
                return null
            }
        if (tiny !== softened) {
            tiny.recycle()
        }
        return softened
    }

    private fun addStrokeToPath(
        destination: Path,
        stroke: NormalizedBlurStroke,
        bitmapWidth: Int,
        bitmapHeight: Int,
        strokePaint: Paint,
    ) {
        val points = stroke.points
        if (points.isEmpty()) {
            return
        }
        val radiusPx =
            stroke.radius
                .coerceIn(
                    PhotoEditSaver.MIN_BLUR_BRUSH_RADIUS,
                    PhotoEditSaver.MAX_BLUR_BRUSH_RADIUS,
                ) * bitmapWidth
        if (points.size == 1) {
            destination.addCircle(
                points.first().x.coerceIn(0f, 1f) * bitmapWidth,
                points.first().y.coerceIn(0f, 1f) * bitmapHeight,
                radiusPx,
                Path.Direction.CW,
            )
            return
        }
        val centerLine =
            Path().apply {
                moveTo(
                    points.first().x.coerceIn(0f, 1f) * bitmapWidth,
                    points.first().y.coerceIn(0f, 1f) * bitmapHeight,
                )
                points.drop(1).forEach { point ->
                    lineTo(
                        point.x.coerceIn(0f, 1f) * bitmapWidth,
                        point.y.coerceIn(0f, 1f) * bitmapHeight,
                    )
                }
            }
        strokePaint.strokeWidth = radiusPx * 2f
        val outline = Path()
        strokePaint.getFillPath(centerLine, outline)
        destination.addPath(outline)
    }

    private fun decodeSoftwareBitmap(
        context: Context,
        uri: Uri,
    ): Bitmap? {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            return try {
                val source = ImageDecoder.createSource(context.contentResolver, uri)
                ImageDecoder.decodeBitmap(source) { decoder, _, _ ->
                    decoder.allocator = ImageDecoder.ALLOCATOR_SOFTWARE
                }
            } catch (_: Exception) {
                null
            }
        }
        val bytes =
            try {
                context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
            } catch (_: Exception) {
                null
            } ?: return null
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

    private fun toSoftwareBitmap(bitmap: Bitmap): Bitmap? {
        if (bitmap.config != Bitmap.Config.HARDWARE) {
            return bitmap
        }
        val software =
            try {
                bitmap.copy(Bitmap.Config.ARGB_8888, false)
            } catch (_: OutOfMemoryError) {
                null
            }
        bitmap.recycle()
        return software
    }

    private const val MAX_BLUR_WORKING_SIDE = 1600
    private const val FEATHER_RADIUS_FRACTION = 0.42f
    private const val MIN_FEATHER_PX = 6f
    private const val MAX_FEATHER_PX = 72f
    private const val MIN_FEATHER_SCALE = 0.06f
    private const val MAX_FEATHER_SCALE = 0.4f
}
