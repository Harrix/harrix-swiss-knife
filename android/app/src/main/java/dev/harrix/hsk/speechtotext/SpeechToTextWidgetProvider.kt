package dev.harrix.hsk.speechtotext

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import dev.harrix.hsk.MainActivity
import dev.harrix.hsk.R

/** 1×1 home-screen widget that opens Speech to Text. */
class SpeechToTextWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
    ) {
        for (appWidgetId in appWidgetIds) {
            appWidgetManager.updateAppWidget(appWidgetId, buildRemoteViews(context))
        }
    }

    companion object {
        const val ACTION_OPEN_SPEECH_TO_TEXT = "dev.harrix.hsk.action.OPEN_SPEECH_TO_TEXT"

        fun buildRemoteViews(context: Context): RemoteViews {
            val views = RemoteViews(context.packageName, R.layout.widget_speech_to_text)
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

        private const val REQUEST_CODE_OPEN_SPEECH_TO_TEXT = 1001
    }
}
