package dev.harrix.hsk.ui.dropboxsync

import android.os.Build
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R

@Composable
fun DropboxAccountCard(
    connected: Boolean,
    accountLabel: String,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit,
    onManageAllFiles: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text =
                if (connected) {
                    stringResource(R.string.dropbox_sync_connected, accountLabel.ifBlank { "Dropbox" })
                } else {
                    stringResource(R.string.dropbox_sync_not_connected)
                },
                style = MaterialTheme.typography.titleMedium,
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                if (connected) {
                    OutlinedButton(onClick = onDisconnect) {
                        Text(stringResource(R.string.dropbox_sync_disconnect))
                    }
                } else {
                    Button(onClick = onConnect) {
                        Text(stringResource(R.string.dropbox_sync_connect))
                    }
                }
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    OutlinedButton(onClick = onManageAllFiles) {
                        Text(stringResource(R.string.dropbox_sync_all_files_access))
                    }
                }
            }
        }
    }
}
