package dev.harrix.hsk.gallery

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.net.Uri
import androidx.exifinterface.media.ExifInterface
import java.io.ByteArrayInputStream
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.hypot
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt
import kotlin.math.sin

/**
 * Fast document / rectangle corner detection for perspective mode.
 *
 * Works on a heavily downscaled preview (no OpenCV). Returns null when no
 * plausible quadrilateral is found so the UI can keep the current crop-rect frame.
 */
object PerspectiveQuadDetector {
    private const val MaxPreviewSide = 240
    private const val MinAreaRatio = 0.08f
    private const val MinSideRatio = 0.08f
    private const val MaxCosine = 0.85f

    /**
     * Detect a perspective quad in square-workspace coordinates (`0..1`), matching
     * the rotated image placement used by the photo editor.
     */
    fun detect(
        context: Context,
        uri: Uri,
        imageWidth: Int,
        imageHeight: Int,
        rotationDegrees: Float,
    ): NormalizedPerspectiveQuad? {
        if (imageWidth <= 0 || imageHeight <= 0) {
            return null
        }
        val preview = decodePreview(context, uri) ?: return null
        try {
            val cornersPx = detectCornersInBitmap(preview) ?: return null
            val content = PhotoEditSaver.imageContentCrop(imageWidth, imageHeight)
            val workspaceCorners =
                cornersPx.map { (x, y) ->
                    val nx = (x / preview.width.toFloat()).coerceIn(0f, 1f)
                    val ny = (y / preview.height.toFloat()).coerceIn(0f, 1f)
                    val wx = content.left + nx * content.width
                    val wy = content.top + ny * content.height
                    rotateWorkspacePoint(wx, wy, rotationDegrees)
                }
            val ordered = orderCorners(workspaceCorners) ?: return null
            val quad =
                NormalizedPerspectiveQuad(
                    topLeft = NormalizedPoint(ordered[0].first, ordered[0].second),
                    topRight = NormalizedPoint(ordered[1].first, ordered[1].second),
                    bottomRight = NormalizedPoint(ordered[2].first, ordered[2].second),
                    bottomLeft = NormalizedPoint(ordered[3].first, ordered[3].second),
                )
            val clamped = PhotoEditSaver.clampPerspectiveQuad(quad)
            return clamped.takeIf { isReasonableQuad(it) }
        } finally {
            preview.recycle()
        }
    }

    private fun detectCornersInBitmap(bitmap: Bitmap): List<Pair<Float, Float>>? {
        val width = bitmap.width
        val height = bitmap.height
        if (width < 16 || height < 16) {
            return null
        }
        val pixels = IntArray(width * height)
        bitmap.getPixels(pixels, 0, width, 0, 0, width, height)
        val gray = IntArray(pixels.size) { index ->
            val c = pixels[index]
            val r = (c shr 16) and 0xff
            val g = (c shr 8) and 0xff
            val b = c and 0xff
            (r * 77 + g * 150 + b * 29) shr 8
        }

        val blurred = boxBlurGray(gray, width, height)
        val edges = sobelEdges(blurred, width, height)
        var maxMag = 1
        for (v in edges) {
            if (v > maxMag) {
                maxMag = v
            }
        }
        val threshold = max(36, (maxMag * 0.28f).roundToInt())
        val marginX = max(2, (width * 0.03f).roundToInt())
        val marginY = max(2, (height * 0.03f).roundToInt())
        val edgePoints = ArrayList<Pair<Float, Float>>(width * height / 16)
        // Step by 2 for speed; still dense enough for extreme-corner estimation.
        // Skip outer margin so photo-frame edges do not always win over a document.
        var y = marginY
        while (y < height - marginY) {
            var x = marginX
            while (x < width - marginX) {
                if (edges[y * width + x] >= threshold) {
                    edgePoints += x.toFloat() to y.toFloat()
                }
                x += 2
            }
            y += 2
        }
        if (edgePoints.size < 32) {
            return null
        }

        val hull = convexHull(edgePoints)
        val candidates =
            when {
                hull.size >= 4 -> hull
                else -> edgePoints
            }
        val extreme = extremeCorners(candidates) ?: return null
        if (!isValidImageQuad(extreme, width, height)) {
            val approx = approximateHullToQuad(hull) ?: return null
            if (!isValidImageQuad(approx, width, height)) {
                return null
            }
            return approx
        }
        return extreme
    }

    private fun extremeCorners(points: List<Pair<Float, Float>>): List<Pair<Float, Float>>? {
        if (points.size < 4) {
            return null
        }
        val tl = points.minBy { it.first + it.second }
        val br = points.maxBy { it.first + it.second }
        val tr = points.maxBy { it.first - it.second }
        val bl = points.minBy { it.first - it.second }
        val corners = listOf(tl, tr, br, bl)
        return corners.takeIf { setOf(tl, tr, br, bl).size == 4 }
    }

    private fun approximateHullToQuad(
        hull: List<Pair<Float, Float>>,
    ): List<Pair<Float, Float>>? {
        if (hull.size < 4) {
            return null
        }
        if (hull.size == 4) {
            return orderCorners(hull)
        }
        var lo = 0.5f
        var hi =
            hull.maxOf {
                hypot(it.first.toDouble(), it.second.toDouble())
            }.toFloat().coerceAtLeast(2f)
        var best: List<Pair<Float, Float>>? = null
        repeat(18) {
            val mid = (lo + hi) * 0.5f
            val approx = douglasPeuckerClosed(hull, mid)
            when {
                approx.size > 4 -> lo = mid

                approx.size < 4 -> hi = mid

                else -> {
                    best = approx
                    hi = mid
                }
            }
        }
        return best?.let { orderCorners(it) } ?: extremeCorners(hull)
    }

    private fun isValidImageQuad(
        corners: List<Pair<Float, Float>>,
        width: Int,
        height: Int,
    ): Boolean {
        if (corners.size != 4) {
            return false
        }
        val area = abs(shoelace(corners))
        val imageArea = width.toFloat() * height.toFloat()
        if (area < imageArea * MinAreaRatio) {
            return false
        }
        val minSide = min(width, height) * MinSideRatio
        for (i in 0..3) {
            val a = corners[i]
            val b = corners[(i + 1) % 4]
            if (hypot((a.first - b.first).toDouble(), (a.second - b.second).toDouble()) < minSide) {
                return false
            }
        }
        // Reject near-collinear corners (very flat angles).
        for (i in 0..3) {
            val prev = corners[(i + 3) % 4]
            val cur = corners[i]
            val next = corners[(i + 1) % 4]
            val ax = prev.first - cur.first
            val ay = prev.second - cur.second
            val bx = next.first - cur.first
            val by = next.second - cur.second
            val dot = ax * bx + ay * by
            val denom =
                hypot(ax.toDouble(), ay.toDouble()) * hypot(bx.toDouble(), by.toDouble())
            if (denom < 1e-3) {
                return false
            }
            if (abs(dot / denom) > MaxCosine) {
                return false
            }
        }
        return true
    }

    private fun isReasonableQuad(quad: NormalizedPerspectiveQuad): Boolean {
        val corners =
            quad.corners().map { it.x to it.y }
        val area = abs(shoelace(corners))
        return area >= MinAreaRatio
    }

    private fun orderCorners(
        corners: List<Pair<Float, Float>>,
    ): List<Pair<Float, Float>>? {
        if (corners.size != 4) {
            return null
        }
        val tl = corners.minBy { it.first + it.second }
        val br = corners.maxBy { it.first + it.second }
        val remaining = corners.filter { it != tl && it != br }
        if (remaining.size != 2) {
            return extremeCorners(corners)
        }
        val tr = remaining.maxBy { it.first - it.second }
        val bl = remaining.minBy { it.first - it.second }
        return listOf(tl, tr, br, bl)
    }

    private fun rotateWorkspacePoint(
        x: Float,
        y: Float,
        degrees: Float,
    ): Pair<Float, Float> {
        if (abs(degrees) < 0.05f) {
            return x to y
        }
        val rad = Math.toRadians(degrees.toDouble())
        val cos = cos(rad).toFloat()
        val sin = sin(rad).toFloat()
        val sx = x - 0.5f
        val sy = y - 0.5f
        // Clockwise rotation with y-down (matches Compose rotationZ / canvas).
        return (0.5f + sx * cos - sy * sin) to (0.5f + sx * sin + sy * cos)
    }

    private fun shoelace(points: List<Pair<Float, Float>>): Float {
        var sum = 0f
        for (i in points.indices) {
            val j = (i + 1) % points.size
            sum += points[i].first * points[j].second
            sum -= points[j].first * points[i].second
        }
        return sum * 0.5f
    }

    private fun boxBlurGray(
        src: IntArray,
        width: Int,
        height: Int,
    ): IntArray {
        val tmp = IntArray(src.size)
        val out = IntArray(src.size)
        // Horizontal
        for (y in 0 until height) {
            val row = y * width
            for (x in 0 until width) {
                var sum = 0
                var count = 0
                for (dx in -1..1) {
                    val xx = (x + dx).coerceIn(0, width - 1)
                    sum += src[row + xx]
                    count++
                }
                tmp[row + x] = sum / count
            }
        }
        // Vertical
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

    private fun sobelEdges(
        gray: IntArray,
        width: Int,
        height: Int,
    ): IntArray {
        val out = IntArray(gray.size)
        for (y in 1 until height - 1) {
            for (x in 1 until width - 1) {
                val i = y * width + x
                val tl = gray[i - width - 1]
                val t = gray[i - width]
                val tr = gray[i - width + 1]
                val l = gray[i - 1]
                val r = gray[i + 1]
                val bl = gray[i + width - 1]
                val b = gray[i + width]
                val br = gray[i + width + 1]
                val gx = -tl + tr - 2 * l + 2 * r - bl + br
                val gy = -tl - 2 * t - tr + bl + 2 * b + br
                out[i] = min(255, abs(gx) + abs(gy))
            }
        }
        return out
    }

    private fun convexHull(points: List<Pair<Float, Float>>): List<Pair<Float, Float>> {
        if (points.size <= 3) {
            return points
        }
        val sorted =
            points.distinct().sortedWith(compareBy({ it.first }, { it.second }))
        if (sorted.size <= 3) {
            return sorted
        }

        fun cross(
            o: Pair<Float, Float>,
            a: Pair<Float, Float>,
            b: Pair<Float, Float>,
        ): Float = (a.first - o.first) * (b.second - o.second) -
            (a.second - o.second) * (b.first - o.first)

        val lower = ArrayList<Pair<Float, Float>>()
        for (p in sorted) {
            while (lower.size >= 2 &&
                cross(lower[lower.size - 2], lower[lower.size - 1], p) <= 0f
            ) {
                lower.removeAt(lower.size - 1)
            }
            lower += p
        }
        val upper = ArrayList<Pair<Float, Float>>()
        for (i in sorted.indices.reversed()) {
            val p = sorted[i]
            while (upper.size >= 2 &&
                cross(upper[upper.size - 2], upper[upper.size - 1], p) <= 0f
            ) {
                upper.removeAt(upper.size - 1)
            }
            upper += p
        }
        lower.removeAt(lower.lastIndex)
        upper.removeAt(upper.lastIndex)
        return lower + upper
    }

    private fun douglasPeuckerClosed(
        points: List<Pair<Float, Float>>,
        epsilon: Float,
    ): List<Pair<Float, Float>> {
        if (points.size <= 4) {
            return points
        }
        // Treat as open polyline from first to last; hull is already closed conceptually.
        val open = if (points.first() == points.last()) points.dropLast(1) else points
        val simplified = douglasPeucker(open, epsilon)
        return simplified
    }

    private fun douglasPeucker(
        points: List<Pair<Float, Float>>,
        epsilon: Float,
    ): List<Pair<Float, Float>> {
        if (points.size < 3) {
            return points
        }
        var maxDist = 0f
        var index = 0
        val start = points.first()
        val end = points.last()
        for (i in 1 until points.lastIndex) {
            val d = pointLineDistance(points[i], start, end)
            if (d > maxDist) {
                index = i
                maxDist = d
            }
        }
        if (maxDist <= epsilon) {
            return listOf(start, end)
        }
        val left = douglasPeucker(points.subList(0, index + 1), epsilon)
        val right = douglasPeucker(points.subList(index, points.size), epsilon)
        return left.dropLast(1) + right
    }

    private fun pointLineDistance(
        p: Pair<Float, Float>,
        a: Pair<Float, Float>,
        b: Pair<Float, Float>,
    ): Float {
        val dx = b.first - a.first
        val dy = b.second - a.second
        if (dx == 0f && dy == 0f) {
            return hypot((p.first - a.first).toDouble(), (p.second - a.second).toDouble()).toFloat()
        }
        val num = abs(dy * p.first - dx * p.second + b.first * a.second - b.second * a.first)
        val den = hypot(dx.toDouble(), dy.toDouble()).toFloat()
        return num / den
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
