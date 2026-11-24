package dev.harrix.hsk.dropboxsync

import android.appwidget.AppWidgetManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

/** Handles home-screen widget taps and starts a one-shot sync. */
class DropboxSyncWidgetActionReceiver : BroadcastReceiver() {
    override fun onReceive(
        context: Context,
        intent: Intent?,
    ) {
        if (intent?.action != ACTION_SYNC) return
        val appWidgetId =
            intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, AppWidgetManager.INVALID_APPWIDGET_ID)
        if (appWidgetId == AppWidgetManager.INVALID_APPWIDGET_ID) return
        val pairId = SyncStateDatabase(context).getWidgetPairId(appWidgetId)
        DropboxSyncWorker.enqueueOneShot(
            context = context,
            pairId = pairId,
            trigger = SyncTrigger.Widget,
        )
    }

    companion object {
        const val ACTION_SYNC = "dev.harrix.hsk.action.DROPBOX_WIDGET_SYNC"
    }
}
