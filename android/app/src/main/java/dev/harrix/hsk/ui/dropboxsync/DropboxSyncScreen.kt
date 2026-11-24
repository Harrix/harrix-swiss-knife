package dev.harrix.hsk.ui.dropboxsync

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Checkbox
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.harrix.hsk.R
import dev.harrix.hsk.dropboxsync.ConflictPolicy
import dev.harrix.hsk.dropboxsync.FolderPair
import dev.harrix.hsk.dropboxsync.StorageType
import dev.harrix.hsk.dropboxsync.SyncAction
import dev.harrix.hsk.dropboxsync.SyncMode
import dev.harrix.hsk.dropboxsync.SyncPhase
import dev.harrix.hsk.dropboxsync.SyncStorageAdapter
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.HskDropdownMenuItem
import dev.harrix.hsk.ui.HubUtilityIcons
import dev.harrix.hsk.ui.UtilityTopBarTitle
import dev.harrix.hsk.ui.icons.LucideIcons
import dev.harrix.hsk.ui.theme.HskTopAppBarHeight
import dev.harrix.hsk.ui.theme.hskScaffoldContainerColor
import dev.harrix.hsk.ui.theme.hskScaffoldContentWindowInsets
import dev.harrix.hsk.ui.theme.hskTopAppBarColors
import dev.harrix.hsk.ui.theme.hskTopAppBarWindowInsets
import java.io.File

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DropboxSyncScreen(
    onClose: () -> Unit,
    onOpenSettings: () -> Unit,
    modifier: Modifier = Modifier,
    pendingConfirmPairId: Long? = null,
    onPendingConfirmConsume: () -> Unit = {},
    pendingOAuthUri: Uri? = null,
    onPendingOAuthUriConsume: () -> Unit = {},
    viewModel: DropboxSyncViewModel = viewModel(),
) {
    val context = LocalContext.current
    val pairs by viewModel.pairs.collectAsStateWithLifecycle()
    val connected by viewModel.connected.collectAsStateWithLifecycle()
    val accountLabel by viewModel.accountLabel.collectAsStateWithLifecycle()
    val message by viewModel.message.collectAsStateWithLifecycle()
    val progress by viewModel.progress.collectAsStateWithLifecycle()
    val dryRun by viewModel.dryRunResult.collectAsStateWithLifecycle()
    val logs by viewModel.logs.collectAsStateWithLifecycle()
    val remoteItems by viewModel.remoteItems.collectAsStateWithLifecycle()
    val remotePath by viewModel.remotePath.collectAsStateWithLifecycle()
    val onPendingConfirmConsumeState = rememberUpdatedState(onPendingConfirmConsume)
    val onPendingOAuthUriConsumeState = rememberUpdatedState(onPendingOAuthUriConsume)

    var editingPair by remember { mutableStateOf<FolderPair?>(null) }
    var showEditor by remember { mutableStateOf(false) }
    var confirmPairId by remember { mutableStateOf<Long?>(null) }
    var logsPairId by remember { mutableStateOf<Long?>(null) }
    var showRemotePicker by remember { mutableStateOf(false) }
    var remotePickTarget by remember { mutableStateOf<((String) -> Unit)?>(null) }

    LaunchedEffect(message) {
        val text = message ?: return@LaunchedEffect
        Toast.makeText(context, text, Toast.LENGTH_SHORT).show()
        viewModel.clearMessage()
    }

    LaunchedEffect(pendingConfirmPairId) {
        if (pendingConfirmPairId != null) {
            confirmPairId = pendingConfirmPairId
            onPendingConfirmConsumeState.value()
        }
    }

    LaunchedEffect(pendingOAuthUri) {
        val uri = pendingOAuthUri ?: return@LaunchedEffect
        viewModel.handleOAuthRedirect(uri)
        onPendingOAuthUriConsumeState.value()
    }

    BackHandler(onBack = onClose)

    Scaffold(
        modifier = modifier.fillMaxSize(),
        containerColor = hskScaffoldContainerColor(),
        contentWindowInsets = hskScaffoldContentWindowInsets(),
        topBar = {
            TopAppBar(
                title = {
                    UtilityTopBarTitle(
                        icon = HubUtilityIcons.DropboxSync,
                        title = stringResource(R.string.dropbox_sync_title),
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onClose) {
                        Icon(LucideIcons.ArrowBack, contentDescription = stringResource(R.string.about_back))
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.syncAll() }) {
                        Icon(LucideIcons.Refresh, contentDescription = stringResource(R.string.dropbox_sync_sync_all))
                    }
                    IconButton(onClick = onOpenSettings) {
                        Icon(LucideIcons.Settings, contentDescription = stringResource(R.string.nav_settings))
                    }
                    IconButton(
                        onClick = {
                            editingPair = null
                            showEditor = true
                        },
                    ) {
                        Icon(LucideIcons.FolderOpen, contentDescription = stringResource(R.string.dropbox_sync_add_pair))
                    }
                },
                colors = hskTopAppBarColors(),
                windowInsets = hskTopAppBarWindowInsets(),
                expandedHeight = HskTopAppBarHeight,
            )
        },
    ) { padding ->
        LazyColumn(
            modifier =
            Modifier
                .padding(padding)
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            item {
                AccountCard(
                    connected = connected,
                    accountLabel = accountLabel,
                    onConnect = { viewModel.beginConnect { viewModel.openAuthorizeUri(it) } },
                    onDisconnect = viewModel::disconnect,
                    onManageAllFiles = {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                            val intent =
                                Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION).apply {
                                    data = Uri.parse("package:${context.packageName}")
                                }
                            context.startActivity(intent)
                        }
                    },
                )
            }
            progress?.let { current ->
                item {
                    ProgressCard(current)
                }
            }
            if (pairs.isEmpty()) {
                item {
                    Text(
                        text = stringResource(R.string.dropbox_sync_no_pairs),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
            items(pairs, key = { it.id }) { pair ->
                PairCard(
                    pair = pair,
                    onSync = { viewModel.syncPair(pair.id) },
                    onEdit = {
                        editingPair = pair
                        showEditor = true
                    },
                    onDryRun = { viewModel.dryRun(pair.id) },
                    onLogs = {
                        logsPairId = pair.id
                        viewModel.loadLogs(pair.id)
                    },
                    onClearBaseline = { viewModel.clearBaseline(pair.id) },
                    onDelete = { viewModel.deletePair(pair.id) },
                    onConfirm = { confirmPairId = pair.id },
                )
            }
        }
    }

    if (showEditor) {
        FolderPairEditorDialog(
            initial = editingPair,
            onDismiss = { showEditor = false },
            onSave = { pair ->
                viewModel.savePair(pair)
                showEditor = false
            },
            onPickRemote = { onPicked ->
                remotePickTarget = onPicked
                viewModel.loadRemoteFolder("")
                showRemotePicker = true
            },
        )
    }

    if (showRemotePicker) {
        DropboxRemotePickerScreen(
            currentPath = remotePath,
            items = remoteItems,
            onNavigate = viewModel::loadRemoteFolder,
            onCreateFolder = viewModel::createRemoteFolder,
            onSelect = { path ->
                remotePickTarget?.invoke(path)
                showRemotePicker = false
            },
            onDismiss = { showRemotePicker = false },
        )
    }

    confirmPairId?.let { pairId ->
        val pending = viewModel.pendingConfirmation(pairId)
        if (pending == null) {
            confirmPairId = null
        } else {
            MirrorLocalChangesDialog(
                actions = pending.actions,
                onDismiss = { confirmPairId = null },
                onApply = { selected ->
                    viewModel.applyConfirmation(pairId, selected)
                    confirmPairId = null
                },
            )
        }
    }

    dryRun?.let { result ->
        AlertDialog(
            onDismissRequest = viewModel::clearDryRun,
            title = { Text(stringResource(R.string.dropbox_sync_dry_run)) },
            text = { Text(result.summary) },
            confirmButton = {
                TextButton(onClick = viewModel::clearDryRun) {
                    Text(stringResource(android.R.string.ok))
                }
            },
        )
    }

    logsPairId?.let {
        SyncLogDialog(
            logs = logs,
            onDismiss = { logsPairId = null },
        )
    }
}

@Composable
private fun AccountCard(
    connected: Boolean,
    accountLabel: String,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit,
    onManageAllFiles: () -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
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

@Composable
private fun ProgressCard(progress: dev.harrix.hsk.dropboxsync.SyncProgress) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(progress.pairName, style = MaterialTheme.typography.titleSmall)
            Spacer(modifier = Modifier.height(4.dp))
            Text(progress.message ?: progress.phase.name)
            if (progress.phase == SyncPhase.Transferring || progress.phase == SyncPhase.Comparing) {
                Spacer(modifier = Modifier.height(8.dp))
                LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
            }
        }
    }
}

@Composable
private fun PairCard(
    pair: FolderPair,
    onSync: () -> Unit,
    onEdit: () -> Unit,
    onDryRun: () -> Unit,
    onLogs: () -> Unit,
    onClearBaseline: () -> Unit,
    onDelete: () -> Unit,
    onConfirm: () -> Unit,
) {
    var menuExpanded by remember { mutableStateOf(false) }
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(pair.name, style = MaterialTheme.typography.titleMedium)
                    Text(
                        text =
                        if (pair.mode == SyncMode.TwoWay) {
                            stringResource(R.string.dropbox_sync_mode_two_way)
                        } else {
                            stringResource(R.string.dropbox_sync_mode_mirror)
                        },
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.primary,
                    )
                }
                IconButton(onClick = { menuExpanded = true }) {
                    Icon(LucideIcons.MoreVert, contentDescription = null)
                }
                DropdownMenu(expanded = menuExpanded, onDismissRequest = { menuExpanded = false }) {
                    HskDropdownMenuItem(
                        text = { Text(stringResource(R.string.dropbox_sync_dry_run)) },
                        onClick = {
                            menuExpanded = false
                            onDryRun()
                        },
                    )
                    HskDropdownMenuItem(
                        text = { Text(stringResource(R.string.dropbox_sync_edit_pair)) },
                        onClick = {
                            menuExpanded = false
                            onEdit()
                        },
                    )
                    HskDropdownMenuItem(
                        text = { Text(stringResource(R.string.dropbox_sync_logs)) },
                        onClick = {
                            menuExpanded = false
                            onLogs()
                        },
                    )
                    HskDropdownMenuItem(
                        text = { Text(stringResource(R.string.dropbox_sync_clear_baseline)) },
                        onClick = {
                            menuExpanded = false
                            onClearBaseline()
                        },
                    )
                    HskDropdownMenuItem(
                        text = { Text(stringResource(R.string.dropbox_sync_review_local_changes)) },
                        onClick = {
                            menuExpanded = false
                            onConfirm()
                        },
                    )
                    HskDropdownMenuItem(
                        text = { Text(stringResource(R.string.dropbox_sync_delete_pair)) },
                        onClick = {
                            menuExpanded = false
                            onDelete()
                        },
                    )
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text("${pair.localPathOrUri} ↔ ${pair.remotePath}", style = MaterialTheme.typography.bodySmall)
            pair.lastSummary?.let {
                Spacer(modifier = Modifier.height(4.dp))
                Text(it, style = MaterialTheme.typography.bodySmall)
            }
            Spacer(modifier = Modifier.height(8.dp))
            Button(onClick = onSync) {
                Text(stringResource(R.string.dropbox_sync_sync_pair))
            }
        }
    }
}

@Composable
private fun FolderPairEditorDialog(
    initial: FolderPair?,
    onDismiss: () -> Unit,
    onSave: (FolderPair) -> Unit,
    onPickRemote: ((String) -> Unit) -> Unit,
) {
    val context = LocalContext.current
    var name by remember { mutableStateOf(initial?.name.orEmpty()) }
    var localPath by remember { mutableStateOf(initial?.localPathOrUri.orEmpty()) }
    var storageType by remember { mutableStateOf(initial?.storageType ?: StorageType.Direct) }
    var remotePath by remember { mutableStateOf(initial?.remotePath.orEmpty()) }
    var mode by remember { mutableStateOf(initial?.mode ?: SyncMode.TwoWay) }
    var confirmLocal by remember { mutableStateOf(initial?.confirmLocalChanges ?: true) }
    var conflictPolicy by remember { mutableStateOf(initial?.conflictPolicy ?: ConflictPolicy.KeepBoth) }

    val treeLauncher =
        rememberLauncherForActivityResult(ActivityResultContracts.OpenDocumentTree()) { uri ->
            if (uri != null) {
                context.contentResolver.takePersistableUriPermission(
                    uri,
                    Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION,
                )
                localPath = uri.toString()
                storageType = StorageType.Saf
                if (name.isBlank()) {
                    name = uri.lastPathSegment?.substringAfterLast(':') ?: "Pair"
                }
            }
        }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                if (initial == null) {
                    stringResource(R.string.dropbox_sync_add_pair)
                } else {
                    stringResource(R.string.dropbox_sync_edit_pair)
                },
            )
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                androidx.compose.material3.OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text(stringResource(R.string.dropbox_sync_pair_name)) },
                    modifier = Modifier.fillMaxWidth(),
                )
                Text(stringResource(R.string.dropbox_sync_local_folder), style = MaterialTheme.typography.labelLarge)
                AutoFitText(text = localPath.ifBlank { stringResource(R.string.dropbox_sync_no_local_folder) }, maxLines = 2)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(
                        onClick = {
                            val root = SyncStorageAdapter.defaultInternalRoot()
                            val folder = File(root, name.ifBlank { "DropboxSync" })
                            folder.mkdirs()
                            localPath = folder.absolutePath
                            storageType = StorageType.Direct
                        },
                    ) {
                        Text(stringResource(R.string.dropbox_sync_use_internal))
                    }
                    OutlinedButton(onClick = { treeLauncher.launch(null) }) {
                        Text(stringResource(R.string.dropbox_sync_use_saf))
                    }
                }
                Text(stringResource(R.string.dropbox_sync_remote_folder), style = MaterialTheme.typography.labelLarge)
                AutoFitText(text = remotePath.ifBlank { "/" }, maxLines = 2)
                OutlinedButton(
                    onClick = {
                        onPickRemote { picked -> remotePath = picked }
                    },
                ) {
                    Text(stringResource(R.string.dropbox_sync_pick_remote))
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(stringResource(R.string.dropbox_sync_mode_two_way))
                    Spacer(modifier = Modifier.width(8.dp))
                    Checkbox(
                        checked = mode == SyncMode.TwoWay,
                        onCheckedChange = { mode = if (it) SyncMode.TwoWay else SyncMode.DownloadMirror },
                    )
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(stringResource(R.string.dropbox_sync_mode_mirror))
                    Spacer(modifier = Modifier.width(8.dp))
                    Checkbox(
                        checked = mode == SyncMode.DownloadMirror,
                        onCheckedChange = { mode = if (it) SyncMode.DownloadMirror else SyncMode.TwoWay },
                    )
                }
                if (mode == SyncMode.DownloadMirror) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Checkbox(checked = confirmLocal, onCheckedChange = { confirmLocal = it })
                        Text(stringResource(R.string.dropbox_sync_confirm_local_changes))
                    }
                }
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    if (name.isBlank() || localPath.isBlank() || remotePath.isBlank()) {
                        Toast.makeText(context, R.string.dropbox_sync_pair_incomplete, Toast.LENGTH_SHORT).show()
                        return@TextButton
                    }
                    onSave(
                        FolderPair(
                            id = initial?.id ?: 0L,
                            name = name.trim(),
                            localPathOrUri = localPath.trim(),
                            storageType = storageType,
                            remotePath = remotePath.trim(),
                            mode = mode,
                            conflictPolicy = conflictPolicy,
                            confirmLocalChanges = confirmLocal,
                        ),
                    )
                },
            ) {
                Text(stringResource(R.string.dropbox_sync_save))
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(android.R.string.cancel))
            }
        },
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DropboxRemotePickerScreen(
    currentPath: String,
    items: List<dev.harrix.hsk.dropboxsync.DropboxRemoteItem>,
    onNavigate: (String) -> Unit,
    onCreateFolder: (String) -> Unit,
    onSelect: (String) -> Unit,
    onDismiss: () -> Unit,
) {
    var newFolder by remember { mutableStateOf("") }
    val folders = remember(items) { items.filter { it.isDir } }
    val canGoUp = currentPath.isNotBlank() && currentPath != "/"
    val parentPath =
        remember(currentPath) {
            currentPath.trimEnd('/').substringBeforeLast('/', missingDelimiterValue = "")
        }

    Dialog(
        onDismissRequest = onDismiss,
        properties =
        DialogProperties(
            usePlatformDefaultWidth = false,
            decorFitsSystemWindows = false,
            dismissOnBackPress = true,
            dismissOnClickOutside = false,
        ),
    ) {
        BackHandler {
            if (canGoUp) {
                onNavigate(parentPath)
            } else {
                onDismiss()
            }
        }
        Surface(modifier = Modifier.fillMaxSize(), color = hskScaffoldContainerColor()) {
            Scaffold(
                modifier = Modifier.fillMaxSize(),
                containerColor = hskScaffoldContainerColor(),
                contentWindowInsets = hskScaffoldContentWindowInsets(),
                topBar = {
                    TopAppBar(
                        title = {
                            Column {
                                Text(
                                    text = stringResource(R.string.dropbox_sync_pick_remote),
                                    style = MaterialTheme.typography.titleMedium,
                                )
                                Text(
                                    text = currentPath.ifBlank { "/" },
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                )
                            }
                        },
                        navigationIcon = {
                            IconButton(
                                onClick = {
                                    if (canGoUp) {
                                        onNavigate(parentPath)
                                    } else {
                                        onDismiss()
                                    }
                                },
                            ) {
                                Icon(
                                    LucideIcons.ArrowBack,
                                    contentDescription = stringResource(R.string.about_back),
                                )
                            }
                        },
                        colors = hskTopAppBarColors(),
                        windowInsets = hskTopAppBarWindowInsets(),
                        expandedHeight = HskTopAppBarHeight,
                    )
                },
                bottomBar = {
                    Surface(tonalElevation = 2.dp) {
                        Column(
                            modifier =
                            Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 16.dp, vertical = 10.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                            ) {
                                OutlinedTextField(
                                    value = newFolder,
                                    onValueChange = { newFolder = it },
                                    label = { Text(stringResource(R.string.dropbox_sync_new_remote_folder)) },
                                    singleLine = true,
                                    modifier = Modifier.weight(1f),
                                )
                                TextButton(
                                    onClick = {
                                        if (newFolder.isNotBlank()) {
                                            onCreateFolder(newFolder.trim())
                                            newFolder = ""
                                        }
                                    },
                                ) {
                                    Text(stringResource(R.string.dropbox_sync_create_folder))
                                }
                            }
                            Button(
                                onClick = { onSelect(currentPath.ifBlank { "" }) },
                                modifier = Modifier.fillMaxWidth(),
                            ) {
                                Text(stringResource(R.string.dropbox_sync_use_this_folder))
                            }
                        }
                    }
                },
            ) { padding ->
                LazyColumn(
                    modifier =
                    Modifier
                        .padding(padding)
                        .fillMaxSize(),
                    contentPadding = PaddingValues(vertical = 4.dp),
                ) {
                    if (canGoUp) {
                        item(key = "__parent__") {
                            RemoteFolderRow(
                                name = "..",
                                onClick = { onNavigate(parentPath) },
                            )
                            HorizontalDivider()
                        }
                    }
                    items(folders, key = { it.pathLower }) { item ->
                        RemoteFolderRow(
                            name = item.name,
                            onClick = { onNavigate(item.pathDisplay) },
                        )
                        HorizontalDivider()
                    }
                }
            }
        }
    }
}

@Composable
private fun RemoteFolderRow(
    name: String,
    onClick: () -> Unit,
) {
    Row(
        modifier =
        Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            painter = painterResource(R.drawable.ic_folder_harrix),
            contentDescription = null,
            modifier = Modifier.size(28.dp),
            tint = Color.Unspecified,
        )
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = name,
            style = MaterialTheme.typography.bodyLarge,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun MirrorLocalChangesDialog(
    actions: List<SyncAction>,
    onDismiss: () -> Unit,
    onApply: (Set<String>) -> Unit,
) {
    var selected by remember {
        mutableStateOf(actions.map { it.pathLower }.toSet())
    }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.dropbox_sync_review_local_changes)) },
        text = {
            LazyColumn(modifier = Modifier.height(320.dp)) {
                items(actions, key = { it.pathLower }) { action ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Checkbox(
                            checked = action.pathLower in selected,
                            onCheckedChange = { checked ->
                                selected =
                                    if (checked) {
                                        selected + action.pathLower
                                    } else {
                                        selected - action.pathLower
                                    }
                            },
                        )
                        Column {
                            Text(action.relativePath)
                            Text(
                                text =
                                when (action) {
                                    is SyncAction.DeleteLocal ->
                                        stringResource(R.string.dropbox_sync_action_delete_local)

                                    is SyncAction.Download ->
                                        stringResource(R.string.dropbox_sync_action_overwrite)

                                    else -> action::class.simpleName.orEmpty()
                                },
                                style = MaterialTheme.typography.bodySmall,
                            )
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = { onApply(selected) }) {
                Text(stringResource(R.string.dropbox_sync_apply_selected))
            }
        },
        dismissButton = {
            TextButton(onClick = { onApply(emptySet()) }) {
                Text(stringResource(R.string.dropbox_sync_keep_all_local))
            }
        },
    )
}

@Composable
private fun SyncLogDialog(
    logs: List<dev.harrix.hsk.dropboxsync.SyncLogRow>,
    onDismiss: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.dropbox_sync_logs)) },
        text = {
            LazyColumn(modifier = Modifier.height(320.dp)) {
                items(logs, key = { it.id }) { log ->
                    Text(
                        text = "${log.status}: ↓${log.downloaded} ↑${log.uploaded} same${log.skippedIdentical}",
                        modifier = Modifier.padding(vertical = 4.dp),
                    )
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(android.R.string.ok))
            }
        },
    )
}
