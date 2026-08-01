package dev.harrix.hsk.ui.gallery

import android.app.Activity
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
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowDownward
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Settings
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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraVideo
import dev.harrix.hsk.gallery.GalleryCleanerPreferences
import dev.harrix.hsk.gallery.GalleryPermissions
import dev.harrix.hsk.ui.CompactWideActionButton
import dev.harrix.hsk.ui.adaptiveBottomBarWidth
import dev.harrix.hsk.ui.isCompactWidth
import dev.harrix.hsk.ui.performLightActionHaptic
import dev.harrix.hsk.ui.videoGridColumnCount
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.Date

private enum class VideoSort(
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
    var selectedIds by remember { mutableStateOf<Set<Long>>(emptySet()) }
    var statusMessage by remember { mutableStateOf<String?>(null) }
    var pendingTrashIds by remember { mutableStateOf<Set<Long>>(emptySet()) }
    var sort by remember { mutableStateOf(VideoSort.DATE_DESC) }
    var sortMenuExpanded by remember { mutableStateOf(false) }
    var playingVideo by remember { mutableStateOf<CameraVideo?>(null) }

    BackHandler {
        when {
            playingVideo != null -> playingVideo = null
            sortMenuExpanded -> sortMenuExpanded = false
            selectedIds.isNotEmpty() -> selectedIds = emptySet()
            else -> onClose()
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
        selectedIds = selectedIds.intersect(loaded.map { it.id }.toSet())
        isLoading = false
        refreshManageMediaAccess()
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
                    IconButton(onClick = onClose) {
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
                        Row(
                            modifier =
                            Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 4.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            TextButton(
                                onClick = {
                                    selectedIds = sortedVideos.map { it.id }.toSet()
                                },
                                modifier = Modifier.weight(1f, fill = false),
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 8.dp),
                            ) {
                                Text(
                                    text = stringResource(R.string.video_cleaner_select_all),
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                )
                            }
                            TextButton(
                                onClick = { selectedIds = emptySet() },
                                enabled = selectedIds.isNotEmpty(),
                                modifier = Modifier.weight(1f, fill = false),
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 8.dp),
                            ) {
                                Text(
                                    text = stringResource(R.string.video_cleaner_deselect_all),
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                )
                            }
                        }
                        LazyVerticalGrid(
                            columns = GridCells.Fixed(videoGridColumnCount()),
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
                                    onLongPress = { playingVideo = video },
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
                Text(
                    text = selectedSizeLabel,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.padding(bottom = 8.dp),
                )
            }
            val colorScheme = MaterialTheme.colorScheme
            CompactWideActionButton(
                onClick = onDelete,
                icon = Icons.Filled.Delete,
                label = deleteLabel,
                enabled = selectedCount > 0,
                colors =
                ButtonDefaults.buttonColors(
                    containerColor = colorScheme.error,
                    contentColor = colorScheme.onError,
                    disabledContainerColor = colorScheme.onSurface.copy(alpha = 0.12f),
                    disabledContentColor = colorScheme.onSurface.copy(alpha = 0.38f),
                ),
            )
        }
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun VideoGalleryItem(
    video: CameraVideo,
    selected: Boolean,
    onToggle: () -> Unit,
    onLongPress: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
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
                onLongClick = onLongPress,
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
