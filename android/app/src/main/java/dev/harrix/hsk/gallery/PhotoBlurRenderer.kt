package dev.harrix.hsk.gallery

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
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
    fun apply(
        bitmap: Bitmap,
        strokes: List<NormalizedBlurStroke>,
        strength: Float,
    ): Boolean {
        val amount = strength.coerceIn(0f, 1f)
        val scale = (0.48f - amount * 0.42f).coerceIn(0.06f, 0.48f)
        val smallWidth = (bitmap.width * scale).roundToInt().coerceAtLeast(1)
        val smallHeight = (bitmap.height * scale).roundToInt().coerceAtLeast(1)
        val blurred =
            try {
                Bitmap.createScaledBitmap(bitmap, smallWidth, smallHeight, true)
            } catch (_: OutOfMemoryError) {
                return false
            }
        if (blurred === bitmap) {
            return true
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
}
