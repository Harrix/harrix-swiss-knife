package dev.harrix.hsk.gallery

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.URL
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.floor
import kotlin.math.ln
import kotlin.math.tan

/**
 * Builds a small static map bitmap from OpenStreetMap tiles (no API key).
 * Used as an in-app preview; tapping the preview opens Google Maps.
 */
object OsmStaticMapPreview {
    private const val TileSize = 256
    private const val DefaultZoom = 15
    private const val UserAgent =
        "HarrixSwissKnife/1.0 (dev.harrix.hsk; Android; photo location preview)"
    private const val ConnectTimeoutMs = 8_000
    private const val ReadTimeoutMs = 8_000

    suspend fun render(
        latitude: Double,
        longitude: Double,
        widthPx: Int = 640,
        heightPx: Int = 360,
        zoom: Int = DefaultZoom,
    ): Bitmap? = withContext(Dispatchers.IO) {
        val width = widthPx.coerceIn(120, 1280)
        val height = heightPx.coerceIn(120, 1280)
        val z = zoom.coerceIn(1, 18)
        val centerX = lonToWorldX(longitude, z)
        val centerY = latToWorldY(latitude, z)
        val left = centerX - width / 2.0
        val top = centerY - height / 2.0
        val right = left + width
        val bottom = top + height
        val tileMinX = floor(left / TileSize).toInt()
        val tileMinY = floor(top / TileSize).toInt()
        val tileMaxX = floor((right - 1) / TileSize).toInt()
        val tileMaxY = floor((bottom - 1) / TileSize).toInt()
        val maxTileIndex = (1 shl z) - 1

        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawColor(Color.rgb(0xE0, 0xE0, 0xE0))

        var loadedAny = false
        for (ty in tileMinY..tileMaxY) {
            if (ty < 0 || ty > maxTileIndex) {
                continue
            }
            for (tx in tileMinX..tileMaxX) {
                val wrappedX =
                    ((tx % (maxTileIndex + 1)) + (maxTileIndex + 1)) % (maxTileIndex + 1)
                val tile = downloadTile(z, wrappedX, ty) ?: continue
                loadedAny = true
                val drawX = (tx * TileSize - left).toFloat()
                val drawY = (ty * TileSize - top).toFloat()
                canvas.drawBitmap(tile, drawX, drawY, null)
                if (!tile.isRecycled) {
                    tile.recycle()
                }
            }
        }
        if (!loadedAny) {
            bitmap.recycle()
            return@withContext null
        }
        drawPin(canvas, width / 2f, height / 2f)
        bitmap
    }

    private fun lonToWorldX(
        longitude: Double,
        zoom: Int,
    ): Double {
        val n = 1 shl zoom
        return (longitude + 180.0) / 360.0 * n * TileSize
    }

    private fun latToWorldY(
        latitude: Double,
        zoom: Int,
    ): Double {
        val lat = latitude.coerceIn(-85.05112878, 85.05112878)
        val latRad = Math.toRadians(lat)
        val n = 1 shl zoom
        return (1.0 - ln(tan(latRad) + 1.0 / cos(latRad)) / PI) / 2.0 * n * TileSize
    }

    private fun downloadTile(
        zoom: Int,
        x: Int,
        y: Int,
    ): Bitmap? {
        val connection =
            (URL("https://tile.openstreetmap.org/$zoom/$x/$y.png").openConnection() as HttpURLConnection)
                .apply {
                    connectTimeout = ConnectTimeoutMs
                    readTimeout = ReadTimeoutMs
                    instanceFollowRedirects = true
                    setRequestProperty("User-Agent", UserAgent)
                    setRequestProperty("Accept", "image/png")
                }
        return try {
            if (connection.responseCode != HttpURLConnection.HTTP_OK) {
                null
            } else {
                connection.inputStream.use { stream ->
                    BitmapFactory.decodeStream(stream)
                }
            }
        } catch (_: Exception) {
            null
        } finally {
            connection.disconnect()
        }
    }

    private fun drawPin(
        canvas: Canvas,
        cx: Float,
        cy: Float,
    ) {
        val stemPaint =
            Paint(Paint.ANTI_ALIAS_FLAG).apply {
                color = Color.rgb(0xD3, 0x2F, 0x2F)
                style = Paint.Style.FILL
            }
        val borderPaint =
            Paint(Paint.ANTI_ALIAS_FLAG).apply {
                color = Color.WHITE
                style = Paint.Style.STROKE
                strokeWidth = 3f
            }
        val tipY = cy + 18f
        val headCy = cy - 4f
        val path =
            Path().apply {
                moveTo(cx, tipY)
                lineTo(cx - 12f, headCy + 4f)
                quadTo(cx - 16f, headCy - 16f, cx, headCy - 18f)
                quadTo(cx + 16f, headCy - 16f, cx + 12f, headCy + 4f)
                close()
            }
        canvas.drawPath(path, stemPaint)
        canvas.drawPath(path, borderPaint)
        canvas.drawCircle(
            cx,
            headCy - 2f,
            5f,
            Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.WHITE },
        )
    }
}
