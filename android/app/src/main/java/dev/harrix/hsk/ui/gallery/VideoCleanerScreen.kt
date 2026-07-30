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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.MoreVert
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
import androidx.compose.material3.TopAppBarDefaults
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
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
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
import dev.harrix.hsk.ui.performLightActionHaptic
import dev.harrix.hsk.ui.theme.AppBackground
import dev.harrix.hsk.ui.theme.AppRed
import dev.harrix.hsk.ui.theme.ContentSurface
import java.util.Date
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

private val TrashButtonColor = AppRed
private val SelectedBorderColor = Color(0xFF2F6BFF)
private const val GalleryColumns = 3

private enum class VideoSort(
    val labelRes: Int,
) {
    DATE_DESC(R.string.video_cleaner_sort_date_desc),
    DATE_ASC(R.string.video_cleaner_sort_date_asc),
    SIZE_DESC(R.string.video_cleaner_sort_size_desc),
    SIZE_ASC(R.string.video_cleaner_sort_size_asc),
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
@Composable
fun VideoCleanerScreen(
    onClose: () -> Unit,
    onOpenSettings: () -> Unit,
    modifier: Modifier = Modifier,
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
        containerColor = AppBackground,
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.video_cleaner_title)) },
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
                                onClick = {
                                    sortMenuExpanded = false
                                    onOpenSettings()
                                },
                            )
                        }
                    }
                },
                colors =
                    TopAppBarDefaults.topAppBarColors(
                        containerColor = AppBackground,
                        scrolledContainerColor = AppBackground,
                    ),
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
        Column(
            modifier =
                Modifier
                    .padding(innerPadding)
                    .fillMaxSize()
                    .background(ContentSurface),
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
                            ) {
                                Text(stringResource(R.string.video_cleaner_permission_grant))
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
                    Row(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        TextButton(
                            onClick = {
                                selectedIds = sortedVideos.map { it.id }.toSet()
                            },
                        ) {
                            Text(stringResource(R.string.video_cleaner_select_all))
                        }
                        TextButton(
                            onClick = { selectedIds = emptySet() },
                            enabled = selectedIds.isNotEmpty(),
                        ) {
                            Text(stringResource(R.string.video_cleaner_deselect_all))
                        }
                    }
                    LazyVerticalGrid(
                        columns = GridCells.Fixed(GalleryColumns),
                        modifier = Modifier.fillMaxSize(),
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

            statusMessage?.let { message ->
                Text(
                    text = message,
                    color = TrashButtonColor,
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(16.dp),
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
    Column(
        modifier =
            modifier
                .fillMaxWidth()
                .background(AppBackground)
                .windowInsetsPadding(WindowInsets.navigationBars)
                .padding(horizontal = 16.dp, vertical = 12.dp),
    ) {
        if (selectedSizeLabel != null) {
            Text(
                text = selectedSizeLabel,
                style = MaterialTheme.typography.bodySmall,
                color = Color(0xFF5F6368),
                modifier = Modifier.padding(bottom = 8.dp),
            )
        }
        Button(
            onClick = onDelete,
            enabled = selectedCount > 0,
            modifier = Modifier.fillMaxWidth(),
            colors =
                ButtonDefaults.buttonColors(
                    containerColor = TrashButtonColor,
                    contentColor = Color.White,
                    disabledContainerColor = Color(0xFFBDBDBD),
                    disabledContentColor = Color.White,
                ),
        ) {
            Icon(
                imageVector = Icons.Filled.Delete,
                contentDescription = null,
                modifier = Modifier.size(18.dp),
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(stringResource(R.string.video_cleaner_delete_selected, selectedCount))
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

    Box(
        modifier =
            modifier
                .aspectRatio(1f)
                .clip(RoundedCornerShape(10.dp))
                .then(
                    if (selected) {
                        Modifier.border(3.dp, SelectedBorderColor, RoundedCornerShape(10.dp))
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
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text = sizeLabel,
                    color = Color.White.copy(alpha = 0.9f),
                    fontSize = 11.sp,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
        }
        if (selected) {
            Icon(
                imageVector = Icons.Filled.CheckCircle,
                contentDescription = null,
                tint = SelectedBorderColor,
                modifier =
                    Modifier
                        .align(Alignment.TopEnd)
                        .padding(6.dp)
                        .size(22.dp)
                        .background(Color.White, CircleShape),
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
        modifier = modifier.background(Color(0xFF1A1A1A)),
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
                tint = Color(0xFF9E9E9E),
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
                    .background(Color.Black),
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
                        .fillMaxWidth()
                        .align(Alignment.Center)
                        .aspectRatio(9f / 16f),
                onRelease = { view ->
                    view.stopPlayback()
                },
            )
            IconButton(
                onClick = onDismiss,
                modifier =
                    Modifier
                        .align(Alignment.TopEnd)
                        .padding(12.dp),
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
