package dev.harrix.hsk.ui.photoeditor

import android.net.Uri
import android.text.format.DateFormat
import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.grid.rememberLazyGridState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import coil.request.ImageRequest
import coil.size.Size
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.EditableImageCache
import dev.harrix.hsk.gallery.GalleryCleanerPreferences
import dev.harrix.hsk.gallery.GalleryPermissions
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.gallery.EditablePhotoHost
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PhotoEditorScreen(
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
    initialUri: Uri? = null,
    onInitialUriConsume: () -> Unit = {},
    settingsRevision: Int = 0,
    viewModel: PhotoEditorViewModel = viewModel(),
) {
    var currentPhoto by viewModel.currentPhoto
    var imageRevision by viewModel.imageRevision
    var isOpeningPhoto by viewModel.isOpeningPhoto
    var galleryPhotos by viewModel.galleryPhotos
    var isGalleryLoading by viewModel.isGalleryLoading
    val galleryThumbRevisions by viewModel.galleryThumbRevisions
    val repository = viewModel.repository
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val preferences = remember { GalleryCleanerPreferences(context.applicationContext) }
    val openFailedMessage = stringResource(R.string.photo_editor_open_failed)
    val savedMessage = stringResource(R.string.photo_editor_saved)
    val savedAsCopyFallbackFolder = "Pictures/HSK"
    val onInitialUriConsumeState = rememberUpdatedState(onInitialUriConsume)

    var hasPermission by remember {
        mutableStateOf(GalleryPermissions.hasPhotosPermission(context))
    }
    val gridState =
        rememberLazyGridState(
            initialFirstVisibleItemIndex = viewModel.gridFirstVisibleIndex,
            initialFirstVisibleItemScrollOffset = viewModel.gridFirstVisibleOffset,
        )

    fun showToast(
        message: String,
        long: Boolean = false,
    ) {
        Toast
            .makeText(
                context,
                message,
                if (long) Toast.LENGTH_LONG else Toast.LENGTH_SHORT,
            ).show()
    }

    val pickMedia =
        rememberLauncherForActivityResult(
            ActivityResultContracts.PickVisualMedia(),
        ) { uri ->
            if (uri != null && !viewModel.loadFromUri(uri)) {
                showToast(openFailedMessage)
            }
        }

    val permissionLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions(),
        ) { result ->
            hasPermission =
                result[GalleryPermissions.requiredPermission()] == true ||
                GalleryPermissions.hasPhotosPermission(context)
        }

    fun reloadGallery() {
        if (!hasPermission) {
            galleryPhotos = emptyList()
            isGalleryLoading = false
            return
        }
        isGalleryLoading = true
        scope.launch {
            val loaded =
                withContext(Dispatchers.IO) {
                    repository.loadCameraPhotos(preferences.getImagesRelativePath())
                }
            galleryPhotos = loaded
            isGalleryLoading = false
            viewModel.galleryInitialized = true
            viewModel.markSettingsApplied(settingsRevision)
        }
    }

    LaunchedEffect(initialUri) {
        val uri = initialUri ?: return@LaunchedEffect
        if (!viewModel.applyIncomingUri(uri)) {
            showToast(openFailedMessage)
        }
        onInitialUriConsumeState.value()
    }

    LaunchedEffect(hasPermission, settingsRevision) {
        val needsReload =
            !viewModel.galleryInitialized ||
                viewModel.appliedSettingsRevision != settingsRevision
        if (needsReload) {
            reloadGallery()
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

    fun leaveEditor() {
        viewModel.resetSession()
        onClose()
    }

    fun openPicker() {
        pickMedia.launch(
            PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly),
        )
    }

    BackHandler {
        if (currentPhoto != null) {
            viewModel.clearPhoto()
        } else {
            leaveEditor()
        }
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        containerColor = hskScaffoldContainerColor(),
        contentWindowInsets = hskScaffoldContentWindowInsets(),
        topBar = {
            TopAppBar(
                title = {
                    AutoFitText(
                        text = stringResource(R.string.photo_editor_title),
                        maxLines = 1,
                    )
                },
                colors = hskTopAppBarColors(),
                windowInsets = hskTopAppBarWindowInsets(),
                expandedHeight = HskTopAppBarHeight,
                navigationIcon = {
                    val editing = currentPhoto != null
                    IconButton(
                        onClick = {
                            if (editing) {
                                viewModel.clearPhoto()
                            } else {
                                leaveEditor()
                            }
                        },
                    ) {
                        Icon(
                            imageVector =
                            if (editing) {
                                Icons.AutoMirrored.Filled.ArrowBack
                            } else {
                                Icons.Filled.Close
                            },
                            contentDescription =
                            stringResource(
                                if (editing) {
                                    R.string.photo_editor_back_to_gallery
                                } else {
                                    R.string.photo_editor_close
                                },
                            ),
                        )
                    }
                },
            )
        },
    ) { innerPadding ->
        Box(
            modifier =
            Modifier
                .padding(innerPadding)
                .fillMaxSize(),
        ) {
            when {
                isOpeningPhoto -> {
                    CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                }

                currentPhoto != null -> {
                    val photo = currentPhoto!!
                    EditablePhotoHost(
                        photo = photo,
                        imageRevision = imageRevision,
                        allowSaveCopyFallback = false,
                        showSaveCopyButton = true,
                        repository = repository,
                        onSave = { result ->
                            viewModel.applySaved(result.photo, result.sizeBytes)
                            if (!result.appliedPerspective && !result.appliedBlur) {
                                if (result.savedAsCopy) {
                                    reloadGallery()
                                }
                                showToast(
                                    message =
                                    if (result.savedAsCopy) {
                                        context.getString(
                                            R.string.photo_editor_saved_as_copy,
                                            result.copyFolderLabel
                                                ?: savedAsCopyFallbackFolder,
                                        )
                                    } else {
                                        savedMessage
                                    },
                                    long = result.savedAsCopy,
                                )
                                viewModel.clearPhoto()
                            }
                        },
                        onDiscard = {
                            imageRevision += 1
                        },
                        onError = { message -> showToast(message, long = true) },
                        modifier = Modifier.fillMaxSize(),
                    )
                }

                else -> {
                    Column(modifier = Modifier.fillMaxSize()) {
                        Button(
                            onClick = { openPicker() },
                            modifier =
                            Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 16.dp, vertical = 8.dp),
                            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 10.dp),
                        ) {
                            AutoFitText(
                                text = stringResource(R.string.photo_editor_open_photo),
                                maxLines = 2,
                            )
                        }
                        PullToRefreshBox(
                            isRefreshing = isGalleryLoading,
                            onRefresh = {
                                if (hasPermission && !isGalleryLoading) {
                                    reloadGallery()
                                }
                            },
                            modifier =
                            Modifier
                                .weight(1f)
                                .fillMaxWidth(),
                        ) {
                            when {
                                !hasPermission -> {
                                    PhotoEditorPermissionPane(
                                        onGrant = {
                                            permissionLauncher.launch(
                                                GalleryPermissions.photoPermissionsToRequest(),
                                            )
                                        },
                                    )
                                }

                                isGalleryLoading || !viewModel.galleryInitialized -> {
                                    Column(
                                        modifier = Modifier.align(Alignment.Center),
                                        horizontalAlignment = Alignment.CenterHorizontally,
                                    ) {
                                        CircularProgressIndicator()
                                        Spacer(modifier = Modifier.height(16.dp))
                                        AutoFitText(
                                            text =
                                            stringResource(R.string.photo_editor_gallery_loading),
                                            maxLines = 1,
                                        )
                                    }
                                }

                                galleryPhotos.isEmpty() -> {
                                    Text(
                                        text = stringResource(R.string.photo_editor_gallery_empty),
                                        style = MaterialTheme.typography.bodyLarge,
                                        textAlign = TextAlign.Center,
                                        modifier =
                                        Modifier
                                            .align(Alignment.Center)
                                            .padding(24.dp),
                                    )
                                }

                                else -> {
                                    LazyVerticalGrid(
                                        columns = GridCells.Fixed(videoGridColumnCount()),
                                        state = gridState,
                                        modifier = Modifier.fillMaxSize(),
                                        contentPadding = PaddingValues(0.dp),
                                        horizontalArrangement = Arrangement.spacedBy(1.dp),
                                        verticalArrangement = Arrangement.spacedBy(1.dp),
                                    ) {
                                        items(galleryPhotos, key = { it.id }) { photo ->
                                            PhotoEditorGalleryItem(
                                                photo = photo,
                                                thumbRevision =
                                                galleryThumbRevisions[photo.id] ?: 0,
                                                onClick = {
                                                    viewModel.openGalleryPhoto(photo)
                                                },
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun PhotoEditorPermissionPane(
    onGrant: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier =
        modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = stringResource(R.string.photo_editor_permission_title),
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = stringResource(R.string.photo_editor_permission_message),
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
        )
        Spacer(modifier = Modifier.height(20.dp))
        Button(
            onClick = onGrant,
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 10.dp),
        ) {
            AutoFitText(
                text = stringResource(R.string.photo_editor_permission_grant),
                maxLines = 2,
            )
        }
    }
}

@Composable
private fun PhotoEditorGalleryItem(
    photo: CameraPhoto,
    thumbRevision: Int,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val dateLabel =
        remember(photo.dateTakenEpochMs, photo.dateAddedEpochSec) {
            val epochMs =
                if (photo.dateTakenEpochMs > 0L) {
                    photo.dateTakenEpochMs
                } else {
                    photo.dateAddedEpochSec * 1000L
                }
            DateFormat.getMediumDateFormat(context).format(Date(epochMs))
        }
    val sizeLabel =
        remember(photo.sizeBytes) {
            CameraGalleryRepository.formatFileSize(photo.sizeBytes)
        }
    val cacheKey =
        EditableImageCache.key(photo.uri, photo.sizeBytes, thumbRevision)

    Box(
        modifier =
        modifier
            .aspectRatio(1f)
            .clickable(onClick = onClick),
    ) {
        AsyncImage(
            model =
            ImageRequest
                .Builder(context)
                .data(photo.uri)
                .memoryCacheKey(cacheKey)
                .diskCacheKey(cacheKey)
                .size(Size(THUMBNAIL_SIZE_PX, THUMBNAIL_SIZE_PX))
                .crossfade(true)
                .build(),
            contentDescription = photo.displayName,
            contentScale = ContentScale.Crop,
            modifier = Modifier.fillMaxSize(),
        )
        Box(
            modifier =
            Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .background(
                    Brush.verticalGradient(
                        colors =
                        listOf(
                            Color.Transparent,
                            Color.Black.copy(alpha = 0.72f),
                        ),
                    ),
                )
                .padding(horizontal = 6.dp, vertical = 6.dp),
        ) {
            Column {
                AutoFitText(
                    text = dateLabel,
                    color = Color.White,
                    style = MaterialTheme.typography.labelSmall,
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
    }
}

private const val THUMBNAIL_SIZE_PX = 512
