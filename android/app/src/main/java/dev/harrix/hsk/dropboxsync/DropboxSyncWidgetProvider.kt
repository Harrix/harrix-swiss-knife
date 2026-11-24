package dev.harrix.hsk.dropboxsync

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
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
import dev.harrix.hsk.R
import kotlin.math.min
import kotlin.math.roundToInt

/** 1×1 home-screen widget that syncs one folder pair (or all). */
class DropboxSyncWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
    ) {
        for (appWidgetId in appWidgetIds) {
            updateAppWidget(context, appWidgetManager, appWidgetId)
        }
    }

    override fun onDeleted(
        context: Context,
        appWidgetIds: IntArray,
    ) {
        val database = SyncStateDatabase(context)
        for (id in appWidgetIds) {
            database.deleteWidgetBinding(id)
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
        private const val REQUEST_CODE_BASE = 3000
        private const val FALLBACK_CELL_SIZE_DP = 40f
        private const val ICON_INSET_FRACTION = 0.2f
        private const val CIRCLE_COLOR = 0xFF1565C0.toInt()

        fun refreshAll(context: Context) {
            val manager = AppWidgetManager.getInstance(context)
            val ids =
                manager.getAppWidgetIds(ComponentName(context, DropboxSyncWidgetProvider::class.java))
            for (id in ids) {
                updateAppWidget(context, manager, id)
            }
        }

        fun updateAppWidget(
            context: Context,
            appWidgetManager: AppWidgetManager,
            appWidgetId: Int,
            options: Bundle = appWidgetManager.getAppWidgetOptions(appWidgetId),
        ) {
            appWidgetManager.updateAppWidget(appWidgetId, buildRemoteViews(context, appWidgetId, options))
        }

        fun buildRemoteViews(
            context: Context,
            appWidgetId: Int,
            options: Bundle = Bundle.EMPTY,
        ): RemoteViews {
            val views = RemoteViews(context.packageName, R.layout.widget_dropbox_sync)
            val diameterDp = circleDiameterDp(context, options)
            val density = context.resources.displayMetrics.density
            val diameterPx = (diameterDp * density).roundToInt().coerceAtLeast(1)
            views.setImageViewBitmap(
                R.id.widget_dropbox_icon,
                createCircleIconBitmap(context, diameterPx),
            )
            val launchIntent =
                Intent(context, DropboxSyncWidgetActionReceiver::class.java).apply {
                    action = DropboxSyncWidgetActionReceiver.ACTION_SYNC
                    putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
                }
            val pendingIntent =
                PendingIntent.getBroadcast(
                    context,
                    REQUEST_CODE_BASE + appWidgetId,
                    launchIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
                )
            views.setOnClickPendingIntent(R.id.widget_dropbox_root, pendingIntent)
            return views
        }

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
                context.resources.configuration.orientation == Configuration.ORIENTATION_PORTRAIT
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
                ContextCompat.getDrawable(context, R.drawable.ic_widget_dropbox_sync)?.mutate()
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
