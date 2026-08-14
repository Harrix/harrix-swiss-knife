package dev.harrix.hsk.gallery

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import android.graphics.drawable.Drawable
import androidx.core.graphics.drawable.toBitmap
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
     * Coil has already applied EXIF orientation to [drawable], so only the interactive editor
     * rotation needs to be reproduced here.
     */
    fun createPreviewBase(
        drawable: Drawable,
        imageWidth: Int,
        imageHeight: Int,
        rotationDegrees: Float,
        maxWorkspaceSide: Int = 1200,
    ): Bitmap? {
        if (imageWidth <= 0 || imageHeight <= 0) {
            return null
        }
        val sourceDiagonal = hypot(imageWidth.toDouble(), imageHeight.toDouble())
        val scale = min(1.0, maxWorkspaceSide / sourceDiagonal)
        val targetWidth = (imageWidth * scale).roundToInt().coerceAtLeast(1)
        val targetHeight = (imageHeight * scale).roundToInt().coerceAtLeast(1)
        val converted =
            try {
                drawable.toBitmap(targetWidth, targetHeight, Bitmap.Config.ARGB_8888)
            } catch (_: Exception) {
                return null
            }
        // A hardware Coil bitmap cannot be drawn onto the software preview canvas.
        val source =
            if (converted.config == Bitmap.Config.HARDWARE) {
                try {
                    converted.copy(Bitmap.Config.ARGB_8888, false)
                } catch (_: OutOfMemoryError) {
                    null
                } ?: return null
            } else {
                converted
            }
        val side =
            ceil(hypot(source.width.toDouble(), source.height.toDouble()))
                .toInt()
                .coerceAtLeast(1)
        val square =
            try {
                Bitmap.createBitmap(side, side, Bitmap.Config.ARGB_8888)
            } catch (_: OutOfMemoryError) {
                return null
            }
        Canvas(square).apply {
            drawColor(Color.BLACK)
            translate(side / 2f, side / 2f)
            rotate(rotationDegrees)
            drawBitmap(source, -source.width / 2f, -source.height / 2f, null)
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
        val blurred = softenDownsampled(downsampled, amount) ?: run {
            downsampled.recycle()
            return false
        }
        if (blurred !== downsampled) {
            downsampled.recycle()
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
                bitmapWidth = bitmap.width,
                bitmapHeight = bitmap.height,
                strokePaint = strokePaint,
            )
        }
        if (clip.isEmpty) {
            blurred.recycle()
            return true
        }

        val canvas = Canvas(bitmap)
        val checkpoint = canvas.save()
        canvas.clipPath(clip)
        canvas.drawBitmap(
            blurred,
            null,
            RectF(0f, 0f, bitmap.width.toFloat(), bitmap.height.toFloat()),
            Paint(Paint.ANTI_ALIAS_FLAG or Paint.FILTER_BITMAP_FLAG),
        )
        canvas.restoreToCount(checkpoint)
        blurred.recycle()
        return true
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

    private const val MAX_BLUR_WORKING_SIDE = 1600
}
