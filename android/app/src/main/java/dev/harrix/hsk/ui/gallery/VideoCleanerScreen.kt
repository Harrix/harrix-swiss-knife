package dev.harrix.hsk.ui.gallery

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.Intent
import android.content.IntentSender
import android.content.pm.PackageManager
import android.content.res.Configuration
import android.graphics.Bitmap
import android.media.MediaMetadataRetriever
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.text.format.DateFormat
import android.util.Size
import android.widget.VideoView
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.IntentSenderRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.combinedClickable
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
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Deselect
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.SelectAll
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Videocam
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
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
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
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
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
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
import dev.harrix.hsk.ui.CompactWideActionButton
import dev.harrix.hsk.ui.adaptiveBottomBarWidth
import dev.harrix.hsk.ui.isCompactWidth
import dev.harrix.hsk.ui.isTablet
import dev.harrix.hsk.ui.performLightActionHaptic
import dev.harrix.hsk.ui.videoGridColumnCount
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.distinctUntilChanged
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

@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
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
    val repository = remember { CameraGalleryRepository(context.applicationContext) }
    val preferences = remember { GalleryCleanerPreferences(context.applicationContext) }

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
    var sort by viewModel.sort
    var sortMenuExpanded by remember { mutableStateOf(false) }
    var playingVideo by viewModel.playingVideo
    val gridState =
        rememberLazyGridState(
            initialFirstVisibleItemIndex = viewModel.gridFirstVisibleIndex,
            initialFirstVisibleItemScrollOffset = viewModel.gridFirstVisibleOffset,
        )

    fun leaveCleaner() {
        viewModel.resetSession()
        onClose()
    }

    BackHandler {
        when {
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
        val loaded = repository.loadCameraVideos()
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
            pendingTrashIds = emptySet()
            if (result.resultCode == Activity.RESULT_OK && ids.isNotEmpty()) {
                view.performLightActionHaptic()
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
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            pendingTrashIds = toDelete.map { it.id }.toSet()
            val sender: IntentSender = repository.createTrashRequest(uris)
            trashLauncher.launch(IntentSenderRequest.Builder(sender).build())
        } else {
            val deletedCount = repository.deletePermanently(uris)
            if (deletedCount > 0) {
                view.performLightActionHaptic()
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
    val useLandscapeSplit =
        LocalConfiguration.current.orientation == Configuration.ORIENTATION_LANDSCAPE &&
            !isTablet()

    Scaffold(
        modifier = modifier,
        contentWindowInsets = WindowInsets.safeDrawing,
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = stringResource(R.string.video_cleaner_title),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                },
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
                                DropdownMenuItem(
                                    text = { Text(stringResource(option.labelRes)) },
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
                            DropdownMenuItem(
                                text = {
                                    Text(stringResource(R.string.video_cleaner_settings))
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
                    onSelectAll =
                    if (useLandscapeSplit) {
                        { selectedIds = sortedVideos.map { it.id }.toSet() }
                    } else {
                        null
                    },
                    onDeselectAll =
                    if (useLandscapeSplit) {
                        { selectedIds = emptySet() }
                    } else {
                        null
                    },
                    canDeselect = selectedIds.isNotEmpty(),
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
                                Text(
                                    text = stringResource(R.string.video_cleaner_permission_grant),
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                )
                            }
                        }
                    }
                }

                isLoading -> {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            CircularProgressIndicator()
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(stringResource(R.string.video_cleaner_loading))
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
                        if (!useLandscapeSplit) {
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
                        }
                        LazyVerticalGrid(
                            columns = GridCells.Fixed(videoGridColumnCount()),
                            state = gridState,
                            modifier =
                            Modifier
                                .weight(1f)
                                .fillMaxWidth(),
                            contentPadding = PaddingValues(8.dp),
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            items(sortedVideos, key = { it.id }) { video ->
                                val selected = video.id in selectedIds
                                VideoGalleryItem(
                                    video = video,
                                    selected = selected,
                                    onToggle = {
                                        selectedIds =
                                            if (selected) {
                                                selectedIds - video.id
                                            } else {
                                                selectedIds + video.id
                                            }
                                    },
                                    onPlay = { playingVideo = video },
                                    onShare = { shareVideo(video) },
                                )
                            }
                        }
                    }
                }
            }

            statusMessage?.let { message ->
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium,
                    maxLines = 3,
                    overflow = TextOverflow.Ellipsis,
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
    compact: Boolean = false,
) {
    val button: @Composable () -> Unit = {
        TextButton(
            onClick = onClick,
            enabled = enabled,
            modifier =
            modifier.heightIn(
                min = if (compact) 28.dp else 40.dp,
                max = if (compact) 32.dp else Dp.Unspecified,
            ),
            contentPadding =
            PaddingValues(
                horizontal = if (compact) 6.dp else 8.dp,
                vertical = if (compact) 0.dp else 4.dp,
            ),
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(if (compact) 16.dp else 18.dp),
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = label,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                style =
                if (compact) {
                    MaterialTheme.typography.labelLarge
                } else {
                    LocalTextStyle.current
                },
            )
        }
    }
    if (compact) {
        CompositionLocalProvider(LocalMinimumInteractiveComponentSize provides 28.dp) {
            button()
        }
    } else {
        button()
    }
}

@Composable
private fun VideoCleanerBottomBar(
    selectedCount: Int,
    selectedSizeLabel: String?,
    onDelete: () -> Unit,
    modifier: Modifier = Modifier,
    onSelectAll: (() -> Unit)? = null,
    onDeselectAll: (() -> Unit)? = null,
    canDeselect: Boolean = false,
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
    val landscapeSelect = onSelectAll != null && onDeselectAll != null
    Column(
        modifier =
        modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surfaceContainer)
            .windowInsetsPadding(WindowInsets.navigationBars)
            .padding(
                horizontal = 16.dp,
                vertical = if (landscapeSelect) 8.dp else 12.dp,
            ),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        if (onSelectAll != null && onDeselectAll != null) {
            val selectAllClick = onSelectAll
            val deselectAllClick = onDeselectAll
            Row(
                modifier = Modifier.adaptiveBottomBarWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(0.dp),
                ) {
                    VideoSelectionTextButton(
                        onClick = selectAllClick,
                        icon = Icons.Filled.SelectAll,
                        label = stringResource(R.string.video_cleaner_select_all),
                        compact = true,
                    )
                    VideoSelectionTextButton(
                        onClick = deselectAllClick,
                        icon = Icons.Filled.Deselect,
                        label = stringResource(R.string.video_cleaner_deselect_all),
                        enabled = canDeselect,
                        compact = true,
                    )
                }
                Column(modifier = Modifier.weight(1f)) {
                    if (selectedSizeLabel != null) {
                        Text(
                            text = selectedSizeLabel,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                            modifier = Modifier.padding(bottom = 4.dp),
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
        } else {
            Column(modifier = Modifier.adaptiveBottomBarWidth()) {
                if (selectedSizeLabel != null) {
                    Text(
                        text = selectedSizeLabel,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
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
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun VideoGalleryItem(
    video: CameraVideo,
    selected: Boolean,
    onToggle: () -> Unit,
    onPlay: () -> Unit,
    onShare: () -> Unit,
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
    val itemShape = MaterialTheme.shapes.medium
    Box(
        modifier =
        modifier
            .aspectRatio(1f)
            .clip(itemShape)
            .then(
                if (selected) {
                    Modifier.border(3.dp, colorScheme.primary, itemShape)
                } else {
                    Modifier
                },
            )
            .combinedClickable(
                onClick = onToggle,
                onLongClick = { menuExpanded = true },
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
                Text(
                    text = dateLabel,
                    color = Color.White,
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text = sizeLabel,
                    color = Color.White.copy(alpha = 0.9f),
                    style = MaterialTheme.typography.labelSmall,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
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
        DropdownMenu(
            expanded = menuExpanded,
            onDismissRequest = { menuExpanded = false },
        ) {
            DropdownMenuItem(
                text = { Text(stringResource(R.string.video_cleaner_play)) },
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
            DropdownMenuItem(
                text = { Text(stringResource(R.string.video_cleaner_share)) },
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
                    VideoView(context).apply {
                        setVideoURI(video.uri)
                        setOnPreparedListener { player ->
                            player.isLooping = true
                            start()
                        }
                    }
                },
                modifier =
                Modifier
                    .fillMaxSize()
                    .align(Alignment.Center),
                onRelease = { view ->
                    view.stopPlayback()
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
