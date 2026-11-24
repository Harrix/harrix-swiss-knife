package dev.harrix.hsk.dropboxsync

import android.appwidget.AppWidgetManager
import android.content.Intent
import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R
import dev.harrix.hsk.ui.theme.HskAndroidTheme

/** Picker shown when a Dropbox Sync widget is added to the home screen. */
class DropboxSyncWidgetConfigActivity : AppCompatActivity() {
    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val appWidgetId =
            intent?.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, AppWidgetManager.INVALID_APPWIDGET_ID)
                ?: AppWidgetManager.INVALID_APPWIDGET_ID
        if (appWidgetId == AppWidgetManager.INVALID_APPWIDGET_ID) {
            finish()
            return
        }
        setResult(RESULT_CANCELED)
        setContent {
            HskAndroidTheme {
                val pairs = remember { SyncStateDatabase(this).listPairs() }
                Scaffold(
                    topBar = {
                        TopAppBar(title = { Text(stringResource(R.string.dropbox_sync_widget_configure)) })
                    },
                ) { padding ->
                    LazyColumn(modifier = Modifier.padding(padding)) {
                        item {
                            ListItem(
                                headlineContent = {
                                    Text(stringResource(R.string.dropbox_sync_widget_all_pairs))
                                },
                                modifier =
                                Modifier
                                    .fillMaxWidth()
                                    .clickable { bindAndFinish(appWidgetId, null) }
                                    .padding(horizontal = 4.dp),
                            )
                        }
                        items(pairs, key = { it.id }) { pair ->
                            ListItem(
                                headlineContent = { Text(pair.name) },
                                supportingContent = {
                                    Text("${pair.localPathOrUri} ↔ ${pair.remotePath}")
                                },
                                modifier =
                                Modifier
                                    .fillMaxWidth()
                                    .clickable { bindAndFinish(appWidgetId, pair.id) }
                                    .padding(horizontal = 4.dp),
                            )
                        }
                        if (pairs.isEmpty()) {
                            item {
                                Text(
                                    text = stringResource(R.string.dropbox_sync_no_pairs),
                                    style = MaterialTheme.typography.bodyMedium,
                                    modifier = Modifier.padding(16.dp),
                                )
                            }
                        }
                    }
                }
            }
        }
    }

    private fun bindAndFinish(
        appWidgetId: Int,
        pairId: Long?,
    ) {
        SyncStateDatabase(this).bindWidget(appWidgetId, pairId)
        val manager = AppWidgetManager.getInstance(this)
        DropboxSyncWidgetProvider.updateAppWidget(this, manager, appWidgetId)
        val result = Intent().putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
        setResult(RESULT_OK, result)
        finish()
    }
}
