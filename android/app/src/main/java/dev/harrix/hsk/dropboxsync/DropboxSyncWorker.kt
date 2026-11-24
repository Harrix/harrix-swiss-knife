package dev.harrix.hsk.dropboxsync

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.ExistingWorkPolicy
import androidx.work.ForegroundInfo
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.OutOfQuotaPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import dev.harrix.hsk.MainActivity
import dev.harrix.hsk.R
import java.util.concurrent.TimeUnit

class DropboxSyncWorker(
    appContext: Context,
    params: WorkerParameters,
) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        val pairId = inputData.getLong(KEY_PAIR_ID, -1L)
        val triggerName = inputData.getString(KEY_TRIGGER) ?: SyncTrigger.Scheduled.name
        val trigger = runCatching { SyncTrigger.valueOf(triggerName) }.getOrDefault(SyncTrigger.Scheduled)
        val engine = SyncEngine.get(applicationContext)
        val database = SyncStateDatabase(applicationContext)
        val pairs =
            if (pairId > 0L) {
                listOfNotNull(database.getPair(pairId))
            } else {
                database.listPairs().filter { it.enabled }
            }
        if (pairs.isEmpty()) {
            return Result.success()
        }
        for (pair in pairs) {
            setForeground(
                createForegroundInfo(
                    applicationContext.getString(R.string.dropbox_sync_syncing_pair, pair.name),
                ),
            )
            val result = engine.syncPair(pair.id, trigger)
            if (result.status == SyncRunStatus.NeedsConfirmation) {
                showConfirmationNotification(pair, result.pendingConfirmation.size)
            }
        }
        DropboxSyncWidgetProvider.refreshAll(applicationContext)
        return Result.success()
    }

    private fun createForegroundInfo(text: String): ForegroundInfo {
        ensureChannel()
        val openIntent =
            Intent(applicationContext, MainActivity::class.java).apply {
                action = ACTION_OPEN_DROPBOX_SYNC
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
        val pending =
            PendingIntent.getActivity(
                applicationContext,
                2001,
                openIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
        val notification =
            NotificationCompat
                .Builder(applicationContext, CHANNEL_ID)
                .setContentTitle(applicationContext.getString(R.string.dropbox_sync_title))
                .setContentText(text)
                .setSmallIcon(R.drawable.ic_widget_dropbox_sync)
                .setContentIntent(pending)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .build()
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ForegroundInfo(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC,
            )
        } else {
            ForegroundInfo(NOTIFICATION_ID, notification)
        }
    }

    private fun showConfirmationNotification(
        pair: FolderPair,
        count: Int,
    ) {
        ensureChannel()
        val openIntent =
            Intent(applicationContext, MainActivity::class.java).apply {
                action = ACTION_OPEN_DROPBOX_CONFIRM
                putExtra(EXTRA_PAIR_ID, pair.id)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
        val pending =
            PendingIntent.getActivity(
                applicationContext,
                2100 + pair.id.toInt(),
                openIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
        val notification =
            NotificationCompat
                .Builder(applicationContext, CHANNEL_ID)
                .setContentTitle(applicationContext.getString(R.string.dropbox_sync_needs_confirmation_title))
                .setContentText(
                    applicationContext.getString(
                        R.string.dropbox_sync_needs_confirmation_text,
                        pair.name,
                        count,
                    ),
                ).setSmallIcon(R.drawable.ic_widget_dropbox_sync)
                .setContentIntent(pending)
                .setAutoCancel(true)
                .build()
        val manager =
            applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify(CONFIRM_NOTIFICATION_BASE + pair.id.toInt(), notification)
    }

    private fun ensureChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val manager =
            applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channel =
            NotificationChannel(
                CHANNEL_ID,
                applicationContext.getString(R.string.dropbox_sync_title),
                NotificationManager.IMPORTANCE_LOW,
            )
        manager.createNotificationChannel(channel)
    }

    companion object {
        const val KEY_PAIR_ID = "pair_id"
        const val KEY_TRIGGER = "trigger"
        const val ACTION_OPEN_DROPBOX_SYNC = "dev.harrix.hsk.action.OPEN_DROPBOX_SYNC"
        const val ACTION_OPEN_DROPBOX_CONFIRM = "dev.harrix.hsk.action.OPEN_DROPBOX_CONFIRM"
        const val EXTRA_PAIR_ID = "pair_id"
        private const val UNIQUE_PERIODIC = "dropbox_sync_periodic"
        private const val CHANNEL_ID = "dropbox_sync"
        private const val NOTIFICATION_ID = 42001
        private const val CONFIRM_NOTIFICATION_BASE = 42100

        fun enqueueOneShot(
            context: Context,
            pairId: Long? = null,
            trigger: SyncTrigger = SyncTrigger.Manual,
        ) {
            val data =
                workDataOf(
                    KEY_PAIR_ID to (pairId ?: -1L),
                    KEY_TRIGGER to trigger.name,
                )
            val request =
                OneTimeWorkRequestBuilder<DropboxSyncWorker>()
                    .setInputData(data)
                    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
                    .build()
            WorkManager.getInstance(context).enqueueUniqueWork(
                "dropbox_sync_one_shot" + (pairId?.let { "_$it" } ?: "_all"),
                ExistingWorkPolicy.KEEP,
                request,
            )
        }

        fun schedulePeriodic(context: Context) {
            val prefs = DropboxSyncPreferences(context)
            val minutes = prefs.getScheduleMinutes()
            val workManager = WorkManager.getInstance(context)
            if (minutes <= 0) {
                workManager.cancelUniqueWork(UNIQUE_PERIODIC)
                return
            }
            val constraints =
                Constraints
                    .Builder()
                    .setRequiredNetworkType(
                        if (prefs.isWifiOnly()) NetworkType.UNMETERED else NetworkType.CONNECTED,
                    ).setRequiresCharging(prefs.isRequireCharging())
                    .setRequiresBatteryNotLow(prefs.isIgnoreBatteryLow())
                    .build()
            val request =
                PeriodicWorkRequestBuilder<DropboxSyncWorker>(minutes.toLong(), TimeUnit.MINUTES)
                    .setConstraints(constraints)
                    .setInputData(
                        workDataOf(
                            KEY_PAIR_ID to -1L,
                            KEY_TRIGGER to SyncTrigger.Scheduled.name,
                        ),
                    ).build()
            workManager.enqueueUniquePeriodicWork(
                UNIQUE_PERIODIC,
                ExistingPeriodicWorkPolicy.UPDATE,
                request,
            )
        }
    }
}
