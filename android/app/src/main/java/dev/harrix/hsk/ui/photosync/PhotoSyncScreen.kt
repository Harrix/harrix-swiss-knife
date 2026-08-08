package dev.harrix.hsk.ui.photosync

import android.Manifest
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.GalleryPermissions
import dev.harrix.hsk.photosync.PhotoSyncConnectionStatus
import dev.harrix.hsk.photosync.PhotoSyncFormat
import dev.harrix.hsk.photosync.PhotoSyncLifetimeStats
import dev.harrix.hsk.photosync.PhotoSyncProgress
import dev.harrix.hsk.photosync.PhotoSyncResult
import dev.harrix.hsk.ui.adaptiveContentWidth

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PhotoSyncScreen(
    onClose: () -> Unit,
    onOpenSettings: () -> Unit,
    modifier: Modifier = Modifier,
    settingsRevision: Int = 0,
    viewModel: PhotoSyncViewModel = viewModel(),
) {
    val context = LocalContext.current
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    var pasteText by remember { mutableStateOf("") }
    var hasPhotoPermission by remember {
        mutableStateOf(GalleryPermissions.hasPhotosPermission(context))
    }

    LaunchedEffect(settingsRevision) {
        viewModel.refreshLifetimeStats()
    }

    val permissionLauncher =
        rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) {
            hasPhotoPermission = GalleryPermissions.hasPhotosPermission(context)
        }

    val cameraPermissionLauncher =
        rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (!granted) {
                Toast
                    .makeText(
                        context,
                        context.getString(R.string.photo_sync_camera_permission_denied),
                        Toast.LENGTH_SHORT,
                    ).show()
            }
        }

    val qrLauncher =
        rememberLauncherForActivityResult(ScanContract()) { result ->
            val contents = result.contents
            if (!contents.isNullOrBlank()) {
                viewModel.applyPairingText(contents)
            }
        }

    fun launchQrScan() {
        val hasCamera =
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED
        if (!hasCamera) {
            cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
            return
        }
        val options =
            ScanOptions()
                .setDesiredBarcodeFormats(ScanOptions.QR_CODE)
                .setPrompt(context.getString(R.string.photo_sync_scan_prompt))
                .setBeepEnabled(false)
                .setOrientationLocked(true)
                .setCaptureActivity(PhotoSyncCaptureActivity::class.java)
        qrLauncher.launch(options)
    }

    BackHandler(enabled = true) {
        if (state.isSyncing) {
            viewModel.cancelSync()
        }
        onClose()
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        contentWindowInsets = WindowInsets.safeDrawing,
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.photo_sync_title)) },
                navigationIcon = {
                    IconButton(
                        onClick = {
                            if (state.isSyncing) {
                                viewModel.cancelSync()
                            }
                            onClose()
                        },
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Close,
                            contentDescription = stringResource(R.string.photo_sync_close),
                        )
                    }
                },
                actions = {
                    IconButton(onClick = onOpenSettings, enabled = !state.isSyncing) {
                        Icon(
                            imageVector = Icons.Filled.Settings,
                            contentDescription = stringResource(R.string.photo_sync_settings),
                        )
                    }
                    IconButton(onClick = { launchQrScan() }, enabled = !state.isSyncing) {
                        Icon(
                            imageVector = Icons.Filled.QrCodeScanner,
                            contentDescription = stringResource(R.string.photo_sync_scan_qr),
                        )
                    }
                },
            )
        },
    ) { innerPadding ->
        Column(
            modifier =
            Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .adaptiveContentWidth()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                text = stringResource(R.string.photo_sync_intro),
                style = MaterialTheme.typography.bodyMedium,
            )

            OutlinedTextField(
                value = state.host,
                onValueChange = viewModel::onHostChange,
                label = { Text(stringResource(R.string.photo_sync_host)) },
                singleLine = true,
                enabled = !state.isSyncing,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.portText,
                onValueChange = viewModel::onPortChange,
                label = { Text(stringResource(R.string.photo_sync_port)) },
                singleLine = true,
                enabled = !state.isSyncing,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.token,
                onValueChange = viewModel::onTokenChange,
                label = { Text(stringResource(R.string.photo_sync_token)) },
                singleLine = true,
                enabled = !state.isSyncing,
                modifier = Modifier.fillMaxWidth(),
            )

            OutlinedTextField(
                value = pasteText,
                onValueChange = { pasteText = it },
                label = { Text(stringResource(R.string.photo_sync_paste_uri)) },
                enabled = !state.isSyncing,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedButton(
                onClick = { viewModel.applyPairingText(pasteText) },
                enabled = !state.isSyncing && pasteText.isNotBlank(),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(stringResource(R.string.photo_sync_apply_uri))
            }

            if (!hasPhotoPermission) {
                Text(
                    text = stringResource(R.string.photo_sync_need_photos_permission),
                    color = MaterialTheme.colorScheme.error,
                )
                Button(
                    onClick = {
                        permissionLauncher.launch(GalleryPermissions.requiredPermission())
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(stringResource(R.string.photo_sync_grant_photos))
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Button(
                    onClick = {
                        if (!hasPhotoPermission) {
                            permissionLauncher.launch(GalleryPermissions.requiredPermission())
                            return@Button
                        }
                        viewModel.startSync()
                    },
                    enabled =
                    !state.isSyncing &&
                        hasPhotoPermission &&
                        state.connectionStatus == PhotoSyncConnectionStatus.Connected,
                    modifier = Modifier.weight(1f),
                ) {
                    Text(stringResource(R.string.photo_sync_start))
                }
                if (state.isSyncing) {
                    OutlinedButton(
                        onClick = viewModel::cancelSync,
                        modifier = Modifier.weight(1f),
                    ) {
                        Text(stringResource(R.string.photo_sync_cancel))
                    }
                }
            }

            PendingStatusBlock(
                connectionStatus = state.connectionStatus,
                isEstimating = state.isEstimating,
                pendingCount = state.pendingCount,
                pendingBytes = state.pendingBytes,
            )

            state.progress?.let { progress ->
                SyncProgressBlock(progress)
            }

            if (state.isSyncing && state.progress == null) {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
            }

            state.lastResult?.let { result ->
                ResultBlock(result)
            }

            state.errorMessage?.let { error ->
                Text(
                    text = error,
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }

            HorizontalDivider(modifier = Modifier.padding(top = 8.dp))
            LifetimeStatsBlock(stats = state.lifetime)

            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
private fun PendingStatusBlock(
    connectionStatus: PhotoSyncConnectionStatus,
    isEstimating: Boolean,
    pendingCount: Int?,
    pendingBytes: Long?,
) {
    val statusText =
        when (connectionStatus) {
            PhotoSyncConnectionStatus.Connected ->
                stringResource(R.string.photo_sync_status_connected)

            PhotoSyncConnectionStatus.Disconnected ->
                stringResource(R.string.photo_sync_status_disconnected)

            PhotoSyncConnectionStatus.Checking ->
                stringResource(R.string.photo_sync_status_checking)

            PhotoSyncConnectionStatus.MissingConfig ->
                stringResource(R.string.photo_sync_status_missing_config)

            PhotoSyncConnectionStatus.Unknown ->
                stringResource(R.string.photo_sync_status_unknown)
        }
    val statusColor =
        when (connectionStatus) {
            PhotoSyncConnectionStatus.Connected -> MaterialTheme.colorScheme.primary
            PhotoSyncConnectionStatus.Disconnected -> MaterialTheme.colorScheme.error
            else -> MaterialTheme.colorScheme.onSurfaceVariant
        }
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            text = stringResource(R.string.photo_sync_status_label, statusText),
            style = MaterialTheme.typography.bodyMedium,
            color = statusColor,
        )
        when {
            isEstimating -> {
                Text(
                    text = stringResource(R.string.photo_sync_estimating),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }

            pendingCount != null && pendingBytes != null -> {
                Text(
                    text =
                    stringResource(
                        R.string.photo_sync_pending_summary,
                        pendingCount,
                        PhotoSyncFormat.formatBytes(pendingBytes),
                    ),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }

            connectionStatus == PhotoSyncConnectionStatus.Connected -> {
                Text(
                    text = stringResource(R.string.photo_sync_pending_unknown),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
private fun SyncProgressBlock(progress: PhotoSyncProgress) {
    val label =
        when (progress.phase) {
            "handshake" -> stringResource(R.string.photo_sync_phase_handshake)

            "scan" -> stringResource(R.string.photo_sync_phase_scan)

            "hash" ->
                stringResource(
                    R.string.photo_sync_phase_hash,
                    progress.current,
                    progress.total,
                )

            "manifest" -> stringResource(R.string.photo_sync_phase_manifest)

            "upload" ->
                stringResource(
                    R.string.photo_sync_phase_upload,
                    progress.current,
                    progress.total,
                )

            else -> progress.phase
        }
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(text = label, style = MaterialTheme.typography.bodyMedium)
        if (progress.total > 0) {
            LinearProgressIndicator(
                progress = { progress.current.toFloat() / progress.total.toFloat() },
                modifier = Modifier.fillMaxWidth(),
            )
        } else {
            LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
        }
        Text(
            text =
            stringResource(
                R.string.photo_sync_session_stats,
                PhotoSyncFormat.formatElapsed(progress.elapsedMs),
                progress.uploadedCount,
                PhotoSyncFormat.formatBytes(progress.uploadedBytes),
            ),
            style = MaterialTheme.typography.bodyMedium,
        )
        if (progress.detail.isNotBlank()) {
            Text(
                text = progress.detail,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun ResultBlock(result: PhotoSyncResult) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            text = result.message,
            style = MaterialTheme.typography.bodyLarge,
        )
        Text(
            text =
            stringResource(
                R.string.photo_sync_session_stats,
                PhotoSyncFormat.formatElapsed(result.elapsedMs),
                result.uploaded,
                PhotoSyncFormat.formatBytes(result.uploadedBytes),
            ),
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}

@Composable
private fun LifetimeStatsBlock(stats: PhotoSyncLifetimeStats) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            text = stringResource(R.string.photo_sync_lifetime_title),
            style = MaterialTheme.typography.titleMedium,
        )
        Text(
            text =
            stringResource(
                R.string.photo_sync_lifetime_summary,
                stats.syncCount,
                stats.photosUploaded,
                PhotoSyncFormat.formatBytes(stats.bytesUploaded),
            ),
            style = MaterialTheme.typography.bodyMedium,
        )
        Text(
            text = stringResource(R.string.photo_sync_lifetime_reset_hint),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}
