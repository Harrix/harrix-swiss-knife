package dev.harrix.hsk.ui.gallery

import android.app.Activity
import android.content.Intent
import android.content.IntentSender
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.IntentSenderRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Done
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
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
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import coil.compose.AsyncImage
import coil.request.ImageRequest
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.GalleryCleanerPreferences
import dev.harrix.hsk.gallery.GalleryPermissions
import dev.harrix.hsk.ui.theme.AppBackground
import dev.harrix.hsk.ui.theme.ContentSurface
import kotlin.math.abs
import kotlin.math.roundToInt
import kotlin.random.Random
import kotlinx.coroutines.launch

private val TrashHintColor = Color(0xFFE53935)
private val KeepHintColor = Color(0xFF43A047)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GalleryCleanerScreen(
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val repository = remember { CameraGalleryRepository(context.applicationContext) }
    val preferences = remember { GalleryCleanerPreferences(context.applicationContext) }

    var hasPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                GalleryPermissions.requiredPermission(),
            ) == PackageManager.PERMISSION_GRANTED,
        )
    }
    var canManageMedia by remember { mutableStateOf(repository.canTrashWithoutPrompt()) }
    var showIntro by remember { mutableStateOf(preferences.shouldShowIntro()) }
    var showManageMediaPrompt by remember { mutableStateOf(false) }
    var dontShowAgain by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    var remainingPhotos by remember { mutableStateOf<List<CameraPhoto>>(emptyList()) }
    var currentPhoto by remember { mutableStateOf<CameraPhoto?>(null) }
    var remainingCount by remember { mutableIntStateOf(0) }
    var statusMessage by remember { mutableStateOf<String?>(null) }
    var pendingTrashPhoto by remember { mutableStateOf<CameraPhoto?>(null) }
    var cardResetKey by remember { mutableIntStateOf(0) }

    fun refreshManageMediaAccess() {
        canManageMedia = repository.canTrashWithoutPrompt()
        showManageMediaPrompt =
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
                hasPermission &&
                !showIntro &&
                !canManageMedia &&
                preferences.shouldShowManageMediaPrompt()
    }

    fun pickNext(from: List<CameraPhoto>): CameraPhoto? =
        if (from.isEmpty()) {
            null
        } else {
            from[Random.nextInt(from.size)]
        }

    fun advanceAfterReview(photo: CameraPhoto) {
        val updated = remainingPhotos.filterNot { it.id == photo.id }
        remainingPhotos = updated
        remainingCount = updated.size
        currentPhoto = pickNext(updated)
        cardResetKey += 1
        statusMessage = null
    }

    fun reloadPhotos() {
        isLoading = true
        statusMessage = null
        val photos = repository.loadCameraPhotos()
        remainingPhotos = photos
        remainingCount = photos.size
        currentPhoto = pickNext(photos)
        cardResetKey += 1
        isLoading = false
        refreshManageMediaAccess()
    }

    val permissionLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.RequestPermission(),
        ) { granted ->
            hasPermission = granted
            if (granted) {
                reloadPhotos()
            }
        }

    val trashLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.StartIntentSenderForResult(),
        ) { result ->
            val photo = pendingTrashPhoto
            pendingTrashPhoto = null
            if (result.resultCode == Activity.RESULT_OK && photo != null) {
                advanceAfterReview(photo)
            } else {
                cardResetKey += 1
                statusMessage = null
            }
        }

    fun requestSystemTrash(photo: CameraPhoto) {
        pendingTrashPhoto = photo
        val sender: IntentSender = repository.createTrashRequest(photo.uri)
        trashLauncher.launch(IntentSenderRequest.Builder(sender).build())
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

    LaunchedEffect(hasPermission, showIntro) {
        if (hasPermission && !showIntro) {
            reloadPhotos()
        }
    }

    if (showIntro) {
        GalleryCleanerIntroDialog(
            dontShowAgain = dontShowAgain,
            onDontShowAgainChange = { dontShowAgain = it },
            onConfirm = {
                if (dontShowAgain) {
                    preferences.setShowIntro(false)
                }
                showIntro = false
                if (hasPermission) {
                    reloadPhotos()
                }
            },
        )
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

    Scaffold(
        modifier = modifier,
        containerColor = AppBackground,
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.gallery_cleaner_title)) },
                navigationIcon = {
                    IconButton(onClick = onClose) {
                        Icon(
                            imageVector = Icons.Filled.Close,
                            contentDescription = stringResource(R.string.gallery_cleaner_close),
                        )
                    }
                },
                actions = {
                    if (hasPermission && currentPhoto != null) {
                        Text(
                            text = stringResource(R.string.gallery_cleaner_remaining, remainingCount),
                            style = MaterialTheme.typography.labelLarge,
                            modifier = Modifier.padding(end = 16.dp),
                        )
                    }
                },
                colors =
                    TopAppBarDefaults.topAppBarColors(
                        containerColor = AppBackground,
                        scrolledContainerColor = AppBackground,
                    ),
            )
        },
    ) { innerPadding ->
        Box(
            modifier =
                Modifier
                    .padding(innerPadding)
                    .fillMaxSize()
                    .background(ContentSurface),
            contentAlignment = Alignment.Center,
        ) {
            when {
                showIntro -> {
                    // Dialog is shown above; keep blank content underneath.
                }
                !hasPermission -> {
                    PermissionRequestContent(
                        onGrantClick = {
                            permissionLauncher.launch(GalleryPermissions.requiredPermission())
                        },
                    )
                }
                isLoading -> {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        CircularProgressIndicator()
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(stringResource(R.string.gallery_cleaner_loading))
                    }
                }
                currentPhoto == null -> {
                    Text(
                        text = stringResource(R.string.gallery_cleaner_empty),
                        style = MaterialTheme.typography.bodyLarge,
                        modifier = Modifier.padding(24.dp),
                    )
                }
                else -> {
                    val photo = currentPhoto!!
                    SwipeablePhotoCard(
                        photo = photo,
                        resetKey = cardResetKey,
                        onSwipeLeft = {
                            statusMessage = null
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                                // With MANAGE_MEDIA granted, createTrashRequest runs without a dialog.
                                requestSystemTrash(photo)
                            } else {
                                val deleted = repository.deletePermanently(photo.uri)
                                if (deleted) {
                                    advanceAfterReview(photo)
                                } else {
                                    statusMessage =
                                        context.getString(R.string.gallery_cleaner_delete_failed)
                                    cardResetKey += 1
                                }
                            }
                        },
                        onSwipeRight = {
                            advanceAfterReview(photo)
                        },
                    )
                }
            }

            statusMessage?.let { message ->
                Text(
                    text = message,
                    color = TrashHintColor,
                    style = MaterialTheme.typography.bodyMedium,
                    modifier =
                        Modifier
                            .align(Alignment.BottomCenter)
                            .padding(24.dp),
                )
            }
        }
    }
}

@Composable
private fun GalleryCleanerIntroDialog(
    dontShowAgain: Boolean,
    onDontShowAgainChange: (Boolean) -> Unit,
    onConfirm: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onConfirm,
        title = { Text(stringResource(R.string.gallery_cleaner_intro_title)) },
        text = {
            Column {
                Text(stringResource(R.string.gallery_cleaner_intro_message))
                Spacer(modifier = Modifier.height(16.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(
                        checked = dontShowAgain,
                        onCheckedChange = onDontShowAgainChange,
                    )
                    Text(
                        text = stringResource(R.string.gallery_cleaner_intro_dont_show),
                        modifier = Modifier.padding(start = 4.dp),
                    )
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onConfirm) {
                Text(stringResource(R.string.gallery_cleaner_intro_ok))
            }
        },
    )
}

@Composable
private fun ManageMediaPromptDialog(
    onOpenSettings: () -> Unit,
    onSkip: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onSkip,
        title = { Text(stringResource(R.string.gallery_cleaner_manage_media_title)) },
        text = { Text(stringResource(R.string.gallery_cleaner_manage_media_message)) },
        confirmButton = {
            TextButton(onClick = onOpenSettings) {
                Text(stringResource(R.string.gallery_cleaner_manage_media_open))
            }
        },
        dismissButton = {
            TextButton(onClick = onSkip) {
                Text(stringResource(R.string.gallery_cleaner_manage_media_skip))
            }
        },
    )
}

@Composable
private fun PermissionRequestContent(
    onGrantClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = stringResource(R.string.gallery_cleaner_permission_title),
            style = MaterialTheme.typography.titleMedium,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = stringResource(R.string.gallery_cleaner_permission_message),
            style = MaterialTheme.typography.bodyMedium,
        )
        Spacer(modifier = Modifier.height(20.dp))
        Button(onClick = onGrantClick) {
            Text(stringResource(R.string.gallery_cleaner_permission_grant))
        }
    }
}

@Composable
private fun SwipeablePhotoCard(
    photo: CameraPhoto,
    resetKey: Int,
    onSwipeLeft: () -> Unit,
    onSwipeRight: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val density = LocalDensity.current
    val scope = rememberCoroutineScope()
    val offsetX = remember(resetKey) { Animatable(0f) }
    var dragOffset by remember(resetKey) { mutableFloatStateOf(0f) }
    val dismissThreshold = with(density) { 96.dp.toPx() }
    val exitDistance = with(density) { 480.dp.toPx() }

    LaunchedEffect(resetKey) {
        offsetX.snapTo(0f)
        dragOffset = 0f
    }

    val displayOffset = if (dragOffset != 0f) dragOffset else offsetX.value
    val progress = (displayOffset / dismissThreshold).coerceIn(-1.5f, 1.5f)

    Box(
        modifier =
            modifier
                .fillMaxSize()
                .padding(16.dp),
        contentAlignment = Alignment.Center,
    ) {
        if (progress < -0.15f) {
            SwipeHint(
                icon = Icons.Filled.Delete,
                label = stringResource(R.string.gallery_cleaner_swipe_left_hint),
                color = TrashHintColor,
                alpha = (-progress).coerceIn(0f, 1f),
                modifier = Modifier.align(Alignment.CenterEnd).padding(end = 24.dp),
            )
        }
        if (progress > 0.15f) {
            SwipeHint(
                icon = Icons.Filled.Done,
                label = stringResource(R.string.gallery_cleaner_swipe_right_hint),
                color = KeepHintColor,
                alpha = progress.coerceIn(0f, 1f),
                modifier = Modifier.align(Alignment.CenterStart).padding(start = 24.dp),
            )
        }

        AsyncImage(
            model =
                ImageRequest
                    .Builder(LocalContext.current)
                    .data(photo.uri)
                    .crossfade(true)
                    .build(),
            contentDescription = photo.displayName,
            contentScale = ContentScale.Fit,
            modifier =
                Modifier
                    .fillMaxSize()
                    .graphicsLayer {
                        rotationZ = displayOffset / 40f
                        alpha = 1f - (abs(displayOffset) / (exitDistance * 1.2f)).coerceIn(0f, 0.35f)
                    }
                    .offset { IntOffset(displayOffset.roundToInt(), 0) }
                    .clip(RoundedCornerShape(12.dp))
                    .background(Color(0xFFF3F3F5))
                    .pointerInput(resetKey, photo.id) {
                        detectHorizontalDragGestures(
                            onDragEnd = {
                                val current = dragOffset
                                dragOffset = 0f
                                scope.launch {
                                    offsetX.snapTo(current)
                                    when {
                                        current <= -dismissThreshold -> {
                                            offsetX.animateTo(-exitDistance, tween(180))
                                            onSwipeLeft()
                                        }
                                        current >= dismissThreshold -> {
                                            offsetX.animateTo(exitDistance, tween(180))
                                            onSwipeRight()
                                        }
                                        else -> {
                                            offsetX.animateTo(0f, tween(180))
                                        }
                                    }
                                }
                            },
                            onDragCancel = {
                                val current = dragOffset
                                dragOffset = 0f
                                scope.launch {
                                    offsetX.snapTo(current)
                                    offsetX.animateTo(0f, tween(180))
                                }
                            },
                            onHorizontalDrag = { change, dragAmount ->
                                change.consume()
                                dragOffset += dragAmount
                            },
                        )
                    },
        )
    }
}

@Composable
private fun SwipeHint(
    icon: ImageVector,
    label: String,
    color: Color,
    alpha: Float,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.graphicsLayer { this.alpha = alpha },
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = color,
            modifier = Modifier.size(36.dp),
        )
        Text(
            text = label,
            color = color,
            style = MaterialTheme.typography.labelLarge,
        )
    }
}
