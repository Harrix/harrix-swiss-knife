package dev.harrix.hsk.speechtotext

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.content.res.Configuration
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.drawable.Drawable
import android.os.Bundle
import android.widget.RemoteViews
import androidx.core.content.ContextCompat
import androidx.core.graphics.createBitmap
import androidx.core.graphics.drawable.DrawableCompat
import androidx.core.graphics.withSave
import dev.harrix.hsk.MainActivity
import dev.harrix.hsk.R
import kotlin.math.min
import kotlin.math.roundToInt

/** 1×1 home-screen widget that opens Speech to Text and starts recording. */
class SpeechToTextWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
    ) {
        for (appWidgetId in appWidgetIds) {
            updateAppWidget(context, appWidgetManager, appWidgetId)
        }
    }

    override fun onAppWidgetOptionsChanged(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int,
        newOptions: Bundle,
    ) {
        updateAppWidget(context, appWidgetManager, appWidgetId, newOptions)
        super.onAppWidgetOptionsChanged(context, appWidgetManager, appWidgetId, newOptions)
    }

    companion object {
        const val ACTION_OPEN_SPEECH_TO_TEXT = "dev.harrix.hsk.action.OPEN_SPEECH_TO_TEXT"

        private const val REQUEST_CODE_OPEN_SPEECH_TO_TEXT = 1001
        private const val FALLBACK_CELL_SIZE_DP = 40f
        private const val ICON_INSET_FRACTION = 0.2f
        private const val CIRCLE_COLOR = 0xFF1565C0.toInt()

        fun updateAppWidget(
            context: Context,
            appWidgetManager: AppWidgetManager,
            appWidgetId: Int,
            options: Bundle = appWidgetManager.getAppWidgetOptions(appWidgetId),
        ) {
            appWidgetManager.updateAppWidget(appWidgetId, buildRemoteViews(context, options))
        }

        fun buildRemoteViews(
            context: Context,
            options: Bundle = Bundle.EMPTY,
        ): RemoteViews {
            val views = RemoteViews(context.packageName, R.layout.widget_speech_to_text)
            val diameterDp = circleDiameterDp(context, options)
            val density = context.resources.displayMetrics.density
            val diameterPx = (diameterDp * density).roundToInt().coerceAtLeast(1)
            views.setImageViewBitmap(
                R.id.widget_speech_icon,
                createCircleIconBitmap(context, diameterPx),
            )
            val launchIntent =
                Intent(context, MainActivity::class.java).apply {
                    action = ACTION_OPEN_SPEECH_TO_TEXT
                    flags =
                        Intent.FLAG_ACTIVITY_NEW_TASK or
                        Intent.FLAG_ACTIVITY_CLEAR_TOP or
                        Intent.FLAG_ACTIVITY_SINGLE_TOP
                }
            val flags = PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            val pendingIntent =
                PendingIntent.getActivity(
                    context,
                    REQUEST_CODE_OPEN_SPEECH_TO_TEXT,
                    launchIntent,
                    flags,
                )
            views.setOnClickPendingIntent(R.id.widget_speech_root, pendingIntent)
            return views
        }

        /**
         * Diameter of the inscribed circle in the widget cell: `min(width, height)` in dp.
         *
         * Launchers report portrait/landscape bounds via min/max options; the current
         * orientation picks the active width and height of the 1×1 zone.
         */
        internal fun circleDiameterDp(
            context: Context,
            options: Bundle,
        ): Float {
            val (widthDp, heightDp) = cellSizeDp(context, options)
            val diameter = min(widthDp, heightDp)
            return if (diameter > 0f) diameter else FALLBACK_CELL_SIZE_DP
        }

        private fun cellSizeDp(
            context: Context,
            options: Bundle,
        ): Pair<Float, Float> {
            val portrait =
                context.resources.configuration.orientation ==
                    Configuration.ORIENTATION_PORTRAIT
            val width =
                options
                    .getInt(
                        if (portrait) {
                            AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH
                        } else {
                            AppWidgetManager.OPTION_APPWIDGET_MAX_WIDTH
                        },
                    ).toFloat()
            val height =
                options
                    .getInt(
                        if (portrait) {
                            AppWidgetManager.OPTION_APPWIDGET_MAX_HEIGHT
                        } else {
                            AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT
                        },
                    ).toFloat()
            return width to height
        }

        private fun createCircleIconBitmap(
            context: Context,
            diameterPx: Int,
        ): Bitmap {
            val bitmap = createBitmap(diameterPx, diameterPx)
            val canvas = Canvas(bitmap)
            val paint =
                Paint(Paint.ANTI_ALIAS_FLAG).apply {
                    color = CIRCLE_COLOR
                    style = Paint.Style.FILL
                }
            val radius = diameterPx / 2f
            canvas.drawCircle(radius, radius, radius, paint)

            val icon =
                ContextCompat.getDrawable(context, R.drawable.ic_widget_mic)?.mutate()
                    ?: return bitmap
            DrawableCompat.setTint(icon, ContextCompat.getColor(context, android.R.color.white))
            val inset = (diameterPx * ICON_INSET_FRACTION).roundToInt()
            drawDrawableCentered(canvas, icon, diameterPx, inset)
            return bitmap
        }

        private fun drawDrawableCentered(
            canvas: Canvas,
            drawable: Drawable,
            sizePx: Int,
            insetPx: Int,
        ) {
            val left = insetPx
            val top = insetPx
            val right = sizePx - insetPx
            val bottom = sizePx - insetPx
            if (right <= left || bottom <= top) return
            canvas.withSave {
                drawable.setBounds(left, top, right, bottom)
                drawable.draw(this)
            }
        }
    }
}
