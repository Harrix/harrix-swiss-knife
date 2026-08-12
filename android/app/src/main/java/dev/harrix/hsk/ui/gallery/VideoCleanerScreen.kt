package dev.harrix.hsk.ui.gallery

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.Intent
import android.content.IntentSender
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.media.MediaMetadataRetriever
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.text.format.DateFormat
import android.util.Size
import android.view.ViewGroup
import android.widget.FrameLayout
import android.widget.MediaController
import android.widget.VideoView
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.IntentSenderRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.grid.rememberLazyGridState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowDownward
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Deselect
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.SelectAll
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Videocam
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LocalMinimumInteractiveComponentSize
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraVideo
import dev.harrix.hsk.gallery.GalleryCleanerPreferences
import dev.harrix.hsk.gallery.GalleryPermissions
import dev.harrix.hsk.gallery.VideoCleanerPreferences
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.CompactWideActionButton
import dev.harrix.hsk.ui.HskDropdownMenuItem
import dev.harrix.hsk.ui.OverflowTextTooltipBox
import dev.harrix.hsk.ui.TypeYesConfirmDialog
import dev.harrix.hsk.ui.adaptiveBottomBarWidth
import dev.harrix.hsk.ui.isCompactWidth
import dev.harrix.hsk.ui.performLightActionHaptic
import dev.harrix.hsk.ui.theme.HskTopAppBarHeight
import dev.harrix.hsk.ui.theme.hskScaffoldContainerColor
import dev.harrix.hsk.ui.theme.hskScaffoldContentWindowInsets
import dev.harrix.hsk.ui.theme.hskTopAppBarColors
import dev.harrix.hsk.ui.theme.hskTopAppBarWindowInsets
import dev.harrix.hsk.ui.videoGridColumnCount
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.Date

enum class VideoSort(
    val labelRes: Int,
    val icon: ImageVector,
) {
    DATE_DESC(R.string.video_cleaner_sort_date_desc, Icons.Filled.CalendarMonth),
    DATE_ASC(R.string.video_cleaner_sort_date_asc, Icons.Filled.CalendarMonth),
    SIZE_DESC(R.string.video_cleaner_sort_size_desc, Icons.Filled.ArrowDownward),
    SIZE_ASC(R.string.video_cleaner_sort_size_asc, Icons.Filled.ArrowUpward),
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VideoCleanerScreen(
    onClose: () -> Unit,
    onOpenSettings: () -> Unit,
    modifier: Modifier = Modifier,
    settingsRevision: Int = 0,
    viewModel: VideoCleanerViewModel = viewModel(),
) {
    val context = LocalContext.current
    val view = LocalView.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val scope = rememberCoroutineScope()
    val repository = remember { CameraGalleryRepository(context.applicationContext) }
    val preferences = remember { GalleryCleanerPreferences(context.applicationContext) }
    val videoPreferences = remember { VideoCleanerPreferences(context.applicationContext) }

    var hasPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                GalleryPermissions.requiredVideoPermission(),
            ) == PackageManager.PERMISSION_GRANTED,
        )
    }
    var showManageMediaPrompt by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    var videos by remember { mutableStateOf<List<CameraVideo>>(emptyList()) }
    var selectedIds by viewModel.selectedIds
    var statusMessage by viewModel.statusMessage
    var pendingTrashIds by viewModel.pendingTrashIds
    var pendingTrashBytes by viewModel.pendingTrashBytes
    var sort by viewModel.sort
    var sortMenuExpanded by remember { mutableStateOf(false) }
    var playingVideo by viewModel.playingVideo
    var detailsVideo by remember { mutableStateOf<CameraVideo?>(null) }
    var sessionDeletedCount by viewModel.sessionDeletedCount
    var sessionFreedBytes by viewModel.sessionFreedBytes
    var showStatsDialog by viewModel.showStatsDialog
    val gridState =
        rememberLazyGridState(
            initialFirstVisibleItemIndex = viewModel.gridFirstVisibleIndex,
            initialFirstVisibleItemScrollOffset = viewModel.gridFirstVisibleOffset,
        )

    fun leaveCleaner() {
        viewModel.resetSession()
        onClose()
    }

    fun recordSuccessfulDeletes(
        count: Int,
        sizeBytes: Long,
    ) {
        if (count <= 0) {
            return
        }
        sessionDeletedCount += count
        sessionFreedBytes += sizeBytes
        videoPreferences.recordDeletedVideos(count = count, sizeBytes = sizeBytes)
    }

    BackHandler {
        when {
            detailsVideo != null -> detailsVideo = null
            showStatsDialog -> showStatsDialog = false
            playingVideo != null -> playingVideo = null
            sortMenuExpanded -> sortMenuExpanded = false
            selectedIds.isNotEmpty() -> selectedIds = emptySet()
            else -> leaveCleaner()
        }
    }

    LaunchedEffect(gridState) {
        snapshotFlow {
            gridState.firstVisibleItemIndex to gridState.firstVisibleItemScrollOffset
        }.distinctUntilChanged()
            .collect { (index, offset) ->
                viewModel.gridFirstVisibleIndex = index
                viewModel.gridFirstVisibleOffset = offset
            }
    }

    fun refreshManageMediaAccess() {
        showManageMediaPrompt =
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
            hasPermission &&
            !repository.canTrashWithoutPrompt() &&
            preferences.shouldShowManageMediaPrompt()
    }

    fun reloadVideos() {
        isLoading = true
        statusMessage = null
        scope.launch {
            val loaded =
                withContext(Dispatchers.IO) {
                    repository.loadCameraVideos()
                }
            videos = loaded
            val loadedIds = loaded.map { it.id }.toSet()
            selectedIds = selectedIds.intersect(loadedIds)
            playingVideo =
                playingVideo
                    ?.id
                    ?.let { id -> loaded.firstOrNull { it.id == id } }
            isLoading = false
            refreshManageMediaAccess()
            viewModel.sessionInitialized = true
        }
    }

    val permissionLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.RequestPermission(),
        ) { granted ->
            hasPermission = granted
            if (granted) {
                reloadVideos()
            }
        }

    val trashLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.StartIntentSenderForResult(),
        ) { result ->
            val ids = pendingTrashIds
            val bytes = pendingTrashBytes
            pendingTrashIds = emptySet()
            pendingTrashBytes = 0L
            if (result.resultCode == Activity.RESULT_OK && ids.isNotEmpty()) {
                view.performLightActionHaptic()
                recordSuccessfulDeletes(count = ids.size, sizeBytes = bytes)
                videos = videos.filterNot { it.id in ids }
                selectedIds = selectedIds - ids
                statusMessage = null
            } else {
                statusMessage = null
            }
        }

    fun trashSelected() {
        val toDelete = videos.filter { it.id in selectedIds }
        if (toDelete.isEmpty()) {
            return
        }
        statusMessage = null
        val uris = toDelete.map { it.uri }
        val deleteBytes = toDelete.sumOf { it.sizeBytes }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            pendingTrashIds = toDelete.map { it.id }.toSet()
            pendingTrashBytes = deleteBytes
            val sender: IntentSender = repository.createTrashRequest(uris)
            trashLauncher.launch(IntentSenderRequest.Builder(sender).build())
        } else {
            val deletedCount = repository.deletePermanently(uris)
            if (deletedCount > 0) {
                view.performLightActionHaptic()
                recordSuccessfulDeletes(count = deletedCount, sizeBytes = deleteBytes)
                reloadVideos()
            } else {
                statusMessage = context.getString(R.string.video_cleaner_delete_failed)
            }
        }
    }

    fun shareVideo(video: CameraVideo) {
        val shareIntent =
            Intent(Intent.ACTION_SEND).apply {
                type = "video/*"
                putExtra(Intent.EXTRA_STREAM, video.uri)
                clipData =
                    ClipData.newUri(
                        context.contentResolver,
                        video.displayName ?: context.getString(R.string.video_cleaner_untitled),
                        video.uri,
                    )
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
        try {
            context.startActivity(
                Intent.createChooser(
                    shareIntent,
                    context.getString(R.string.video_cleaner_share),
                ),
            )
        } catch (_: ActivityNotFoundException) {
            statusMessage = context.getString(R.string.video_cleaner_share_failed)
        }
    }

    DisposableEffect(lifecycleOwner) {
        val observer =
            LifecycleEventObserver { _, event ->
                if (event == Lifecycle.Event.ON_RESUME) {
                    refreshManageMediaAccess()
                }
            }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    LaunchedEffect(hasPermission) {
        if (hasPermission) {
            reloadVideos()
        }
    }

    LaunchedEffect(settingsRevision) {
        refreshManageMediaAccess()
    }

    val totalBytes = remember(videos) { videos.sumOf { it.sizeBytes } }

    if (showStatsDialog) {
        var statsTick by remember { mutableIntStateOf(0) }
        var showResetStatsConfirm by remember { mutableStateOf(false) }
        val lifetimeDeleted = remember(statsTick) { videoPreferences.totalDeletedCount() }
        val lifetimeFreed = remember(statsTick) { videoPreferences.totalFreedBytes() }
        val canResetStats = lifetimeDeleted > 0 || lifetimeFreed > 0L
        AlertDialog(
            onDismissRequest = { showStatsDialog = false },
            title = { AutoFitText(text = stringResource(R.string.video_cleaner_stats_title), maxLines = 2) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    AutoFitText(
                        text = stringResource(
                            R.string.video_cleaner_stats_in_folder,
                            videos.size,
                        ),
                        maxLines = 1,
                    )
                    AutoFitText(
                        text = stringResource(
                            R.string.video_cleaner_stats_folder_size,
                            CameraGalleryRepository.formatFileSize(totalBytes),
                        ),
                        maxLines = 1,
                    )
                    AutoFitText(
                        text = stringResource(
                            R.string.video_cleaner_stats_deleted_session,
                            sessionDeletedCount,
                        ),
                        maxLines = 1,
                    )
                    AutoFitText(
                        text = stringResource(
                            R.string.video_cleaner_stats_freed_session,
                            CameraGalleryRepository.formatFileSize(sessionFreedBytes),
                        ),
                        maxLines = 1,
                    )
                    AutoFitText(
                        text = stringResource(
                            R.string.video_cleaner_stats_deleted,
                            lifetimeDeleted,
                        ),
                        maxLines = 1,
                    )
                    AutoFitText(
                        text = stringResource(
                            R.string.video_cleaner_stats_freed,
                            CameraGalleryRepository.formatFileSize(lifetimeFreed),
                        ),
                        maxLines = 1,
                    )
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { showResetStatsConfirm = true },
                    enabled = canResetStats,
                ) {
                    AutoFitText(text = stringResource(R.string.video_cleaner_stats_reset), maxLines = 2)
                }
            },
            confirmButton = {
                TextButton(onClick = { showStatsDialog = false }) {
                    AutoFitText(text = stringResource(R.string.video_cleaner_stats_ok), maxLines = 2)
                }
            },
        )
        if (showResetStatsConfirm) {
            TypeYesConfirmDialog(
                title = stringResource(R.string.video_cleaner_stats_reset),
                message = stringResource(R.string.settings_video_reset_stats_hint),
                confirmLabel = stringResource(R.string.video_cleaner_stats_reset),
                onConfirm = {
                    videoPreferences.clearLifetimeDeleteStats()
                    sessionDeletedCount = 0
                    sessionFreedBytes = 0L
                    statsTick += 1
                    showResetStatsConfirm = false
                },
                onDismissRequest = { showResetStatsConfirm = false },
            )
        }
    }

    if (showManageMediaPrompt) {
        ManageMediaPromptDialog(
            onOpenSettings = {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    val intent =
                        Intent(Settings.ACTION_REQUEST_MANAGE_MEDIA).apply {
                            data = Uri.parse("package:${context.packageName}")
                        }
                    context.startActivity(intent)
                }
            },
            onSkip = {
                preferences.setShowManageMediaPrompt(false)
                showManageMediaPrompt = false
            },
        )
    }

    playingVideo?.let { video ->
        VideoPlaybackDialog(
            video = video,
            onDismiss = { playingVideo = null },
        )
    }

    detailsVideo?.let { video ->
        VideoFileDetailsSheet(
            video = video,
            onDismissRequest = { detailsVideo = null },
        )
    }

    val sortedVideos =
        remember(videos, sort) {
            when (sort) {
                VideoSort.DATE_DESC -> videos.sortedByDescending { it.dateAddedEpochSec }
                VideoSort.DATE_ASC -> videos.sortedBy { it.dateAddedEpochSec }
                VideoSort.SIZE_DESC -> videos.sortedByDescending { it.sizeBytes }
                VideoSort.SIZE_ASC -> videos.sortedBy { it.sizeBytes }
            }
        }
    val selectedVideos = sortedVideos.filter { it.id in selectedIds }
    val selectedBytes = selectedVideos.sumOf { it.sizeBytes }

    Scaffold(
        modifier = modifier,
        containerColor = hskScaffoldContainerColor(),
        contentWindowInsets = hskScaffoldContentWindowInsets(),
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        AutoFitText(
                            text = stringResource(R.string.video_cleaner_title),
                            maxLines = 1,
                        )
                        if (hasPermission) {
                            AutoFitText(
                                text =
                                stringResource(
                                    R.string.video_cleaner_header_sizes,
                                    CameraGalleryRepository.formatFileSize(totalBytes),
                                    CameraGalleryRepository.formatFileSize(selectedBytes),
                                ),
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                maxLines = 1,
                            )
                        }
                    }
                },
                colors = hskTopAppBarColors(),
                windowInsets = hskTopAppBarWindowInsets(),
                expandedHeight = HskTopAppBarHeight,
                navigationIcon = {
                    IconButton(onClick = { leaveCleaner() }) {
                        Icon(
                            imageVector = Icons.Filled.Close,
                            contentDescription = stringResource(R.string.video_cleaner_close),
                        )
                    }
                },
                actions = {
                    Box {
                        IconButton(onClick = { sortMenuExpanded = true }) {
                            Icon(
                                imageVector = Icons.Filled.MoreVert,
                                contentDescription = stringResource(R.string.video_cleaner_settings),
                            )
                        }
                        DropdownMenu(
                            expanded = sortMenuExpanded,
                            onDismissRequest = { sortMenuExpanded = false },
                        ) {
                            VideoSort.entries.forEach { option ->
                                HskDropdownMenuItem(
                                    text = { AutoFitText(text = stringResource(option.labelRes), maxLines = 1) },
                                    leadingIcon = {
                                        Icon(
                                            imageVector = option.icon,
                                            contentDescription = null,
                                        )
                                    },
                                    onClick = {
                                        sort = option
                                        sortMenuExpanded = false
                                    },
                                )
                            }
                            HorizontalDivider()
                            HskDropdownMenuItem(
                                text = {
                                    AutoFitText(text = stringResource(R.string.video_cleaner_stats), maxLines = 1)
                                },
                                leadingIcon = {
                                    Icon(
                                        imageVector = Icons.Filled.BarChart,
                                        contentDescription = null,
                                    )
                                },
                                onClick = {
                                    sortMenuExpanded = false
                                    showStatsDialog = true
                                },
                            )
                            HskDropdownMenuItem(
                                text = {
                                    AutoFitText(text = stringResource(R.string.video_cleaner_settings), maxLines = 1)
                                },
                                leadingIcon = {
                                    Icon(
                                        imageVector = Icons.Filled.Settings,
                                        contentDescription = null,
                                    )
                                },
                                onClick = {
                                    sortMenuExpanded = false
                                    onOpenSettings()
                                },
                            )
                        }
                    }
                },
            )
        },
        bottomBar = {
            if (hasPermission && sortedVideos.isNotEmpty()) {
                VideoCleanerBottomBar(
                    selectedCount = selectedIds.size,
                    selectedSizeLabel =
                    if (selectedIds.isEmpty()) {
                        null
                    } else {
                        stringResource(
                            R.string.video_cleaner_selected_size,
                            CameraGalleryRepository.formatFileSize(selectedBytes),
                        )
                    },
                    onDelete = { trashSelected() },
                )
            }
        },
    ) { innerPadding ->
        Box(
            modifier =
            Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.surface),
        ) {
            when {
                !hasPermission -> {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Column(
                            modifier = Modifier.padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                        ) {
                            Text(
                                text = stringResource(R.string.video_cleaner_permission_title),
                                style = MaterialTheme.typography.titleMedium,
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = stringResource(R.string.video_cleaner_permission_message),
                                style = MaterialTheme.typography.bodyMedium,
                            )
                            Spacer(modifier = Modifier.height(20.dp))
                            Button(
                                onClick = {
                                    permissionLauncher.launch(
                                        GalleryPermissions.requiredVideoPermission(),
                                    )
                                },
                                contentPadding =
                                PaddingValues(horizontal = 16.dp, vertical = 10.dp),
                            ) {
                                AutoFitText(
                                    text = stringResource(R.string.video_cleaner_permission_grant),
                                    maxLines = 2,
                                )
                            }
                        }
                    }
                }

                isLoading || (hasPermission && !viewModel.sessionInitialized) -> {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            CircularProgressIndicator()
                            Spacer(modifier = Modifier.height(16.dp))
                            AutoFitText(text = stringResource(R.string.video_cleaner_loading), maxLines = 1)
                        }
                    }
                }

                sortedVideos.isEmpty() -> {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text(
                            text = stringResource(R.string.video_cleaner_empty),
                            style = MaterialTheme.typography.bodyLarge,
                            modifier = Modifier.padding(24.dp),
                        )
                    }
                }

                else -> {
                    Column(modifier = Modifier.fillMaxSize()) {
                        Row(
                            modifier =
                            Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 4.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            VideoSelectionTextButton(
                                onClick = {
                                    selectedIds = sortedVideos.map { it.id }.toSet()
                                },
                                icon = Icons.Filled.SelectAll,
                                label = stringResource(R.string.video_cleaner_select_all),
                                modifier = Modifier.weight(1f, fill = false),
                            )
                            VideoSelectionTextButton(
                                onClick = { selectedIds = emptySet() },
                                icon = Icons.Filled.Deselect,
                                label = stringResource(R.string.video_cleaner_deselect_all),
                                enabled = selectedIds.isNotEmpty(),
                                modifier = Modifier.weight(1f, fill = false),
                            )
                        }
                        val sortedVideoIds = remember(sortedVideos) { sortedVideos.map { it.id } }
                        LazyVerticalGrid(
                            columns = GridCells.Fixed(videoGridColumnCount()),
                            state = gridState,
                            modifier =
                            Modifier
                                .weight(1f)
                                .fillMaxWidth()
                                .lazyGridDragSelect(
                                    lazyGridState = gridState,
                                    itemIds = sortedVideoIds,
                                    selectedIds = selectedIds,
                                    onSelectedIdsChange = { selectedIds = it },
                                ),
                            contentPadding = PaddingValues(0.dp),
                            horizontalArrangement = Arrangement.spacedBy(1.dp),
                            verticalArrangement = Arrangement.spacedBy(1.dp),
                        ) {
                            items(sortedVideos, key = { it.id }) { video ->
                                VideoGalleryItem(
                                    video = video,
                                    selected = video.id in selectedIds,
                                    onPlay = { playingVideo = video },
                                    onShare = { shareVideo(video) },
                                    onFileDetails = { detailsVideo = video },
                                )
                            }
                        }
                    }
                }
            }

            statusMessage?.let { message ->
                AutoFitText(
                    text = message,
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium,
                    maxLines = 3,
                    modifier =
                    Modifier
                        .align(Alignment.BottomCenter)
                        .padding(16.dp)
                        .background(
                            MaterialTheme.colorScheme.surface.copy(alpha = 0.92f),
                            shape = MaterialTheme.shapes.small,
                        )
                        .padding(horizontal = 12.dp, vertical = 8.dp),
                )
            }
        }
    }
}

@Composable
private fun VideoSelectionTextButton(
    onClick: () -> Unit,
    icon: ImageVector,
    label: String,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    var labelOverflows by remember(label) { mutableStateOf(false) }
    OverflowTextTooltipBox(
        text = label,
        enabled = labelOverflows,
        modifier = modifier,
    ) {
        TextButton(
            onClick = onClick,
            enabled = enabled,
            modifier = Modifier.heightIn(min = 40.dp),
            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 4.dp),
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(18.dp),
            )
            Spacer(modifier = Modifier.width(4.dp))
            AutoFitText(
                text = label,
                modifier = Modifier.weight(1f, fill = false),
                maxLines = 1,
                textAlign = TextAlign.Center,
                style = LocalTextStyle.current,
                enableOverflowTooltip = false,
                onOverflowChange = { labelOverflows = it },
            )
        }
    }
}

@Composable
private fun VideoCleanerBottomBar(
    selectedCount: Int,
    selectedSizeLabel: String?,
    onDelete: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val compact = isCompactWidth()
    val deleteLabel =
        stringResource(
            if (compact) {
                R.string.video_cleaner_delete_selected_short
            } else {
                R.string.video_cleaner_delete_selected
            },
            selectedCount,
        )
    val colorScheme = MaterialTheme.colorScheme
    val deleteColors =
        ButtonDefaults.buttonColors(
            containerColor = colorScheme.error,
            contentColor = colorScheme.onError,
            disabledContainerColor = colorScheme.onSurface.copy(alpha = 0.12f),
            disabledContentColor = colorScheme.onSurface.copy(alpha = 0.38f),
        )
    Column(
        modifier =
        modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surfaceContainer)
            .windowInsetsPadding(WindowInsets.navigationBars)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Column(modifier = Modifier.adaptiveBottomBarWidth()) {
            if (selectedSizeLabel != null) {
                AutoFitText(
                    text = selectedSizeLabel,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    modifier = Modifier.padding(bottom = 8.dp),
                )
            }
            CompactWideActionButton(
                onClick = onDelete,
                icon = Icons.Filled.Delete,
                label = deleteLabel,
                enabled = selectedCount > 0,
                colors = deleteColors,
            )
        }
    }
}

@Composable
private fun VideoGalleryItem(
    video: CameraVideo,
    selected: Boolean,
    onPlay: () -> Unit,
    onShare: () -> Unit,
    onFileDetails: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var menuExpanded by remember { mutableStateOf(false) }
    val dateLabel =
        remember(video.dateAddedEpochSec) {
            DateFormat
                .getMediumDateFormat(context)
                .format(Date(video.dateAddedEpochSec * 1000L))
        }
    val sizeLabel =
        remember(video.sizeBytes) {
            CameraGalleryRepository.formatFileSize(video.sizeBytes)
        }

    val colorScheme = MaterialTheme.colorScheme
    // Selection taps/long-press are handled by [lazyGridDragSelect] on the grid.
    Box(
        modifier =
        modifier
            .aspectRatio(1f)
            .then(
                if (selected) {
                    Modifier.border(3.dp, colorScheme.primary)
                } else {
                    Modifier
                },
            ),
    ) {
        VideoThumbnail(
            uri = video.uri,
            modifier = Modifier.fillMaxSize(),
        )
        Box(
            modifier =
            Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
                .background(
                    Brush.verticalGradient(
                        colors = listOf(Color.Transparent, Color.Black.copy(alpha = 0.75f)),
                    ),
                )
                .padding(horizontal = 6.dp, vertical = 6.dp),
        ) {
            Column {
                AutoFitText(
                    text = dateLabel,
                    color = Color.White,
                    style = MaterialTheme.typography.labelSmall.copy(
                        fontWeight = FontWeight.SemiBold,
                    ),
                    maxLines = 1,
                )
                AutoFitText(
                    text = sizeLabel,
                    color = Color.White.copy(alpha = 0.9f),
                    style = MaterialTheme.typography.labelSmall,
                    maxLines = 1,
                )
            }
        }
        Box(modifier = Modifier.align(Alignment.TopStart)) {
            CompositionLocalProvider(LocalMinimumInteractiveComponentSize provides 24.dp) {
                IconButton(
                    onClick = { menuExpanded = true },
                    modifier = Modifier.size(32.dp),
                ) {
                    Icon(
                        imageVector = Icons.Filled.MoreVert,
                        contentDescription = stringResource(R.string.video_cleaner_more_actions),
                        tint = Color.White,
                        modifier =
                        Modifier
                            .size(20.dp)
                            .background(Color.Black.copy(alpha = 0.45f), CircleShape)
                            .padding(2.dp),
                    )
                }
            }
            DropdownMenu(
                expanded = menuExpanded,
                onDismissRequest = { menuExpanded = false },
            ) {
                HskDropdownMenuItem(
                    text = {
                        AutoFitText(text = stringResource(R.string.video_cleaner_play), maxLines = 1)
                    },
                    onClick = {
                        menuExpanded = false
                        onPlay()
                    },
                    leadingIcon = {
                        Icon(
                            imageVector = Icons.Filled.PlayArrow,
                            contentDescription = null,
                        )
                    },
                )
                HskDropdownMenuItem(
                    text = {
                        AutoFitText(text = stringResource(R.string.video_cleaner_share), maxLines = 1)
                    },
                    onClick = {
                        menuExpanded = false
                        onShare()
                    },
                    leadingIcon = {
                        Icon(
                            imageVector = Icons.Filled.Share,
                            contentDescription = null,
                        )
                    },
                )
                HskDropdownMenuItem(
                    text = {
                        AutoFitText(
                            text = stringResource(R.string.photo_file_details_title),
                            maxLines = 1,
                        )
                    },
                    onClick = {
                        menuExpanded = false
                        onFileDetails()
                    },
                    leadingIcon = {
                        Icon(
                            imageVector = Icons.Filled.Info,
                            contentDescription = null,
                        )
                    },
                )
            }
        }
        if (selected) {
            Icon(
                imageVector = Icons.Filled.CheckCircle,
                contentDescription = null,
                tint = colorScheme.primary,
                modifier =
                Modifier
                    .align(Alignment.TopEnd)
                    .padding(6.dp)
                    .size(22.dp)
                    .background(colorScheme.onPrimary, CircleShape),
            )
        }
    }
}

@Composable
private fun VideoThumbnail(
    uri: Uri,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var bitmap by remember(uri) { mutableStateOf<Bitmap?>(null) }

    LaunchedEffect(uri) {
        bitmap =
            withContext(Dispatchers.IO) {
                loadVideoThumbnail(context, uri)
            }
    }

    Box(
        modifier = modifier.background(MaterialTheme.colorScheme.surfaceContainerHighest),
        contentAlignment = Alignment.Center,
    ) {
        val frame = bitmap
        if (frame != null) {
            Image(
                bitmap = frame.asImageBitmap(),
                contentDescription = null,
                contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxSize(),
            )
        } else {
            Icon(
                imageVector = Icons.Filled.Videocam,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(36.dp),
            )
        }
    }
}

@Composable
private fun VideoPlaybackDialog(
    video: CameraVideo,
    onDismiss: () -> Unit,
) {
    Dialog(
        onDismissRequest = onDismiss,
        properties =
        DialogProperties(
            usePlatformDefaultWidth = false,
            dismissOnBackPress = true,
            dismissOnClickOutside = true,
        ),
    ) {
        Box(
            modifier =
            Modifier
                .fillMaxSize()
                .background(Color.Black)
                .windowInsetsPadding(WindowInsets.safeDrawing),
        ) {
            AndroidView(
                factory = { context ->
                    val container =
                        FrameLayout(context).apply {
                            layoutParams =
                                ViewGroup.LayoutParams(
                                    ViewGroup.LayoutParams.MATCH_PARENT,
                                    ViewGroup.LayoutParams.MATCH_PARENT,
                                )
                        }
                    val videoView =
                        VideoView(context).apply {
                            layoutParams =
                                FrameLayout.LayoutParams(
                                    FrameLayout.LayoutParams.MATCH_PARENT,
                                    FrameLayout.LayoutParams.MATCH_PARENT,
                                )
                        }
                    val controller =
                        MediaController(context).apply {
                            setAnchorView(container)
                        }
                    videoView.setMediaController(controller)
                    videoView.setVideoURI(video.uri)
                    videoView.setOnPreparedListener {
                        videoView.start()
                        controller.show()
                    }
                    container.addView(videoView)
                    container.tag = videoView
                    container
                },
                modifier =
                Modifier
                    .fillMaxSize()
                    .align(Alignment.Center),
                onRelease = { view ->
                    (view.tag as? VideoView)?.stopPlayback()
                },
            )
            IconButton(
                onClick = onDismiss,
                modifier =
                Modifier
                    .align(Alignment.TopEnd)
                    .padding(4.dp),
            ) {
                Icon(
                    imageVector = Icons.Filled.Close,
                    contentDescription = stringResource(R.string.video_cleaner_play_close),
                    tint = Color.White,
                )
            }
        }
    }
}

private fun loadVideoThumbnail(
    context: android.content.Context,
    uri: Uri,
): Bitmap? {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        try {
            return context.contentResolver.loadThumbnail(uri, Size(512, 512), null)
        } catch (_: Exception) {
            // Fall through to MediaMetadataRetriever.
        }
    }
    val retriever = MediaMetadataRetriever()
    return try {
        retriever.setDataSource(context, uri)
        retriever.getFrameAtTime(0L, MediaMetadataRetriever.OPTION_CLOSEST_SYNC)
    } catch (_: Exception) {
        null
    } finally {
        try {
            retriever.release()
        } catch (_: Exception) {
            // Ignore release errors on older APIs.
        }
    }
}
