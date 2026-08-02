package dev.harrix.hsk.ui.gallery

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.Intent
import android.content.IntentSender
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.IntentSenderRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.calculatePan
import androidx.compose.foundation.gestures.calculateZoom
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.RotateRight
import androidx.compose.material.icons.automirrored.filled.Undo
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Crop
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Done
import androidx.compose.material.icons.filled.FilterAltOff
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.SkipNext
import androidx.compose.material.icons.filled.Today
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.input.pointer.positionChanged
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import coil.request.ImageRequest
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.CameraPhoto
import dev.harrix.hsk.gallery.GalleryDateFilter
import dev.harrix.hsk.gallery.GalleryPermissions
import dev.harrix.hsk.gallery.GalleryReviewOrder
import dev.harrix.hsk.gallery.GallerySessionUndo
import dev.harrix.hsk.gallery.NormalizedCropRect
import dev.harrix.hsk.gallery.PendingEditUndo
import dev.harrix.hsk.gallery.PhotoEditSaver
import dev.harrix.hsk.ui.CompactBottomActionButton
import dev.harrix.hsk.ui.adaptiveBottomBarWidth
import dev.harrix.hsk.ui.isCompactHeight
import dev.harrix.hsk.ui.isCompactWidth
import dev.harrix.hsk.ui.performLightActionHaptic
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.DateFormat
import java.util.Date
import kotlin.math.abs
import kotlin.math.hypot
import kotlin.math.roundToInt
import kotlin.random.Random

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GalleryCleanerScreen(
    onClose: () -> Unit,
    onOpenSettings: (shootDayEpochMs: Long?) -> Unit,
    modifier: Modifier = Modifier,
    settingsRevision: Int = 0,
    viewModel: GalleryCleanerViewModel = viewModel(),
) {
    val context = LocalContext.current
    val view = LocalView.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val repository = viewModel.repository
    val preferences = viewModel.preferences
    val photoEditSaver = viewModel.photoEditSaver
    val scope = rememberCoroutineScope()

    var hasPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                GalleryPermissions.requiredPermission(),
            ) == PackageManager.PERMISSION_GRANTED,
        )
    }
    var canManageMedia by remember { mutableStateOf(repository.canTrashWithoutPrompt()) }
    var showIntro by viewModel.showIntro
    var lastIntroPref by remember { mutableStateOf(preferences.shouldShowIntro()) }
    var showManageMediaPrompt by remember { mutableStateOf(false) }
    var dontShowAgain by viewModel.dontShowAgain
    var isLoading by viewModel.isLoading
    var remainingPhotos by viewModel.remainingPhotos
    var currentPhoto by viewModel.currentPhoto
    var remainingCount by viewModel.remainingCount
    var statusMessage by viewModel.statusMessage
    var pendingTrashPhoto by viewModel.pendingTrashPhoto
    var pendingRestorePhoto by viewModel.pendingRestorePhoto

    /** Session undo stack: keeps, deletes and edits, newest last. */
    var undoStack by viewModel.undoStack
    var cardResetKey by viewModel.cardResetKey
    var menuExpanded by remember { mutableStateOf(false) }
    var dateFilter by viewModel.dateFilter
    var unreviewedOnlyMode by viewModel.unreviewedOnlyMode
    var reviewOrder by viewModel.reviewOrder
    var sessionReviewedCount by viewModel.sessionReviewedCount
    var sessionDeletedCount by viewModel.sessionDeletedCount
    var sessionFreedBytes by viewModel.sessionFreedBytes
    var showStatsDialog by viewModel.showStatsDialog
    var isEditing by viewModel.isEditing
    var editRotationDegrees by viewModel.editRotationDegrees
    var editCropRect by viewModel.editCropRect
    var editImageRevision by viewModel.editImageRevision
    var isSavingEdit by viewModel.isSavingEdit
    var pendingWritePhoto by viewModel.pendingWritePhoto
    var pendingWriteKind by viewModel.pendingWriteKind

    fun leaveCleaner() {
        viewModel.resetSession()
        onClose()
    }

    fun refreshManageMediaAccess() {
        canManageMedia = repository.canTrashWithoutPrompt()
        showManageMediaPrompt =
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
            hasPermission &&
            !showIntro &&
            !canManageMedia &&
            preferences.shouldShowManageMediaPrompt()
    }

    fun orderPhotos(photos: List<CameraPhoto>): List<CameraPhoto> = when (reviewOrder) {
        GalleryReviewOrder.Random -> photos
        GalleryReviewOrder.OldestFirst -> photos.sortedBy { it.dateTakenEpochMs }
        GalleryReviewOrder.NewestFirst -> photos.sortedByDescending { it.dateTakenEpochMs }
    }

    fun pickNext(from: List<CameraPhoto>): CameraPhoto? {
        if (from.isEmpty()) {
            return null
        }
        val ordered = orderPhotos(from)
        return when (reviewOrder) {
            GalleryReviewOrder.Random -> ordered[Random.nextInt(ordered.size)]

            GalleryReviewOrder.OldestFirst,
            GalleryReviewOrder.NewestFirst,
            -> ordered.first()
        }
    }

    fun existingEditUndo(photoId: Long): PendingEditUndo? = undoStack
        .asReversed()
        .filterIsInstance<GallerySessionUndo.Edit>()
        .map { it.undo }
        .firstOrNull { it.photoId == photoId }

    fun pushDeleteUndo(photo: CameraPhoto) {
        undoStack = undoStack + GallerySessionUndo.Delete(photo)
    }

    fun pushKeepUndo(photo: CameraPhoto) {
        undoStack = undoStack + GallerySessionUndo.Keep(photo)
    }

    fun pushEditUndo(undo: PendingEditUndo) {
        if (existingEditUndo(undo.photoId) != null) {
            return
        }
        undoStack = undoStack + GallerySessionUndo.Edit(undo)
    }

    fun removeDeleteUndo(photoId: Long) {
        val index =
            undoStack.indexOfLast {
                it is GallerySessionUndo.Delete && it.photo.id == photoId
            }
        if (index < 0) {
            return
        }
        undoStack = undoStack.toMutableList().also { it.removeAt(index) }
    }

    fun removeKeepUndo(photoId: Long) {
        val index =
            undoStack.indexOfLast {
                it is GallerySessionUndo.Keep && it.photo.id == photoId
            }
        if (index < 0) {
            return
        }
        undoStack = undoStack.toMutableList().also { it.removeAt(index) }
    }

    fun removeEditUndo(photoId: Long) {
        val index =
            undoStack.indexOfLast {
                it is GallerySessionUndo.Edit && it.undo.photoId == photoId
            }
        if (index < 0) {
            return
        }
        undoStack = undoStack.toMutableList().also { it.removeAt(index) }
    }

    fun advanceAfterReview(
        photo: CameraPhoto,
        deleted: Boolean = false,
    ) {
        view.performLightActionHaptic()
        sessionReviewedCount += 1
        if (unreviewedOnlyMode) {
            preferences.markPhotoReviewed(photo.id)
        }
        if (deleted) {
            sessionDeletedCount += 1
            sessionFreedBytes += photo.sizeBytes
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                pushDeleteUndo(photo)
            }
        } else {
            pushKeepUndo(photo)
        }
        val updated = orderPhotos(remainingPhotos.filterNot { it.id == photo.id })
        remainingPhotos = updated
        remainingCount = updated.size
        currentPhoto = pickNext(updated)
        cardResetKey += 1
        statusMessage = null
    }

    /** Show another photo without marking this one reviewed — it can appear again later. */
    fun skipPhoto(photo: CameraPhoto) {
        view.performLightActionHaptic()
        if (remainingPhotos.size <= 1) {
            cardResetKey += 1
            return
        }
        currentPhoto =
            when (reviewOrder) {
                GalleryReviewOrder.Random ->
                    pickNext(remainingPhotos.filterNot { it.id == photo.id }) ?: photo

                GalleryReviewOrder.OldestFirst,
                GalleryReviewOrder.NewestFirst,
                -> {
                    val ordered = orderPhotos(remainingPhotos)
                    val index = ordered.indexOfFirst { it.id == photo.id }
                    if (index < 0) {
                        ordered.first()
                    } else {
                        ordered[(index + 1) % ordered.size]
                    }
                }
            }
        cardResetKey += 1
        statusMessage = null
    }

    fun restoreTrashedPhoto(photo: CameraPhoto) {
        view.performLightActionHaptic()
        if (unreviewedOnlyMode) {
            preferences.unmarkPhotoReviewed(photo.id)
        }
        sessionReviewedCount = (sessionReviewedCount - 1).coerceAtLeast(0)
        sessionDeletedCount = (sessionDeletedCount - 1).coerceAtLeast(0)
        sessionFreedBytes = (sessionFreedBytes - photo.sizeBytes).coerceAtLeast(0L)
        val updated = orderPhotos(remainingPhotos + photo)
        remainingPhotos = updated
        remainingCount = updated.size
        currentPhoto = photo
        removeDeleteUndo(photo.id)
        cardResetKey += 1
        statusMessage = null
    }

    fun restoreKeptPhoto(photo: CameraPhoto) {
        view.performLightActionHaptic()
        if (unreviewedOnlyMode) {
            preferences.unmarkPhotoReviewed(photo.id)
        }
        sessionReviewedCount = (sessionReviewedCount - 1).coerceAtLeast(0)
        remainingPhotos =
            orderPhotos(
                if (remainingPhotos.any { it.id == photo.id }) {
                    remainingPhotos
                } else {
                    remainingPhotos + photo
                },
            )
        remainingCount = remainingPhotos.size
        currentPhoto = photo
        removeKeepUndo(photo.id)
        cardResetKey += 1
        statusMessage = null
    }

    fun applyFilters(photos: List<CameraPhoto>): List<CameraPhoto> {
        val byDate =
            photos.filter { photo ->
                dateFilter.contains(photo.dateTakenEpochMs / 1000L)
            }
        if (!unreviewedOnlyMode) {
            return byDate
        }
        val reviewedIds = preferences.getReviewedPhotoIds()
        return byDate.filterNot { it.id in reviewedIds }
    }

    fun applyShootDayFilter(dateTakenEpochMs: Long) {
        val next = GalleryDateFilter.forShootDay(dateTakenEpochMs)
        preferences.saveDateFilter(next)
        dateFilter = next
    }

    fun reloadPhotos() {
        isLoading = true
        statusMessage = null
        val previousOrder = reviewOrder
        dateFilter = preferences.loadDateFilter()
        unreviewedOnlyMode = preferences.isUnreviewedOnlyModeEnabled()
        reviewOrder = preferences.getReviewOrder()
        val orderChanged = previousOrder != reviewOrder
        val previousPhotoId = currentPhoto?.id
        // Date filter + unreviewed-only are applied here.
        val photos =
            orderPhotos(
                applyFilters(
                    repository.loadCameraPhotos(preferences.getImagesRelativePath()),
                ),
            )
        remainingPhotos = photos
        remainingCount = photos.size
        currentPhoto =
            if (orderChanged) {
                // Switch to a photo for the new order; keep the previous one in the pool
                // (skip) so unreviewed-only can show it again later.
                val others =
                    previousPhotoId
                        ?.let { id -> photos.filterNot { it.id == id } }
                        ?: photos
                pickNext(others) ?: pickNext(photos)
            } else {
                previousPhotoId
                    ?.let { id -> photos.firstOrNull { it.id == id } }
                    ?: pickNext(photos)
            }
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
                advanceAfterReview(photo, deleted = true)
            } else {
                cardResetKey += 1
                statusMessage = null
            }
        }

    val restoreLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.StartIntentSenderForResult(),
        ) { result ->
            val photo = pendingRestorePhoto
            pendingRestorePhoto = null
            if (result.resultCode == Activity.RESULT_OK && photo != null) {
                restoreTrashedPhoto(photo)
            } else {
                statusMessage = context.getString(R.string.gallery_cleaner_undo_failed)
            }
        }

    var writeLauncherPending by remember {
        mutableStateOf<((CameraPhoto) -> Unit)?>(null)
    }
    val writeLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.StartIntentSenderForResult(),
        ) { result ->
            val photo = pendingWritePhoto
            val kind = pendingWriteKind
            pendingWritePhoto = null
            pendingWriteKind = null
            if (result.resultCode == Activity.RESULT_OK && photo != null) {
                writeLauncherPending?.invoke(photo)
            } else {
                isSavingEdit = false
                statusMessage =
                    when (kind) {
                        PendingWriteKind.RestoreEdit ->
                            context.getString(R.string.gallery_cleaner_undo_failed)

                        else ->
                            context.getString(R.string.gallery_cleaner_edit_save_failed)
                    }
            }
            writeLauncherPending = null
        }

    fun enterEditMode() {
        if (currentPhoto == null) {
            return
        }
        isEditing = true
        editRotationDegrees = 0f
        editCropRect = NormalizedCropRect.Full
        statusMessage = null
        menuExpanded = false
    }

    fun exitEditMode() {
        isEditing = false
        editRotationDegrees = 0f
        editCropRect = NormalizedCropRect.Full
        isSavingEdit = false
        pendingWritePhoto = null
        pendingWriteKind = null
        writeLauncherPending = null
        statusMessage = null
    }

    BackHandler {
        when {
            showStatsDialog -> showStatsDialog = false
            menuExpanded -> menuExpanded = false
            isEditing -> exitEditMode()
            else -> leaveCleaner()
        }
    }

    fun applySavedPhoto(
        photo: CameraPhoto,
        sizeBytes: Long,
        keepEditUndo: Boolean,
    ) {
        val existing = existingEditUndo(photo.id)
        val updated = photo.copy(sizeBytes = sizeBytes)
        remainingPhotos = remainingPhotos.map { if (it.id == photo.id) updated else it }
        currentPhoto = updated
        if (keepEditUndo) {
            val undo =
                existing?.takeIf { it.backupFile.isFile }
                    ?: PendingEditUndo(
                        photoId = photo.id,
                        uri = photo.uri,
                        originalSizeBytes = photo.sizeBytes,
                        backupFile = photoEditSaver.editBackupFile(photo.id),
                        photoSnapshot = photo,
                    )
            pushEditUndo(undo)
        }
        editImageRevision += 1
        cardResetKey += 1
        exitEditMode()
        statusMessage = null
    }

    fun performSaveEdit(
        photo: CameraPhoto,
        requestWriteIfNeeded: Boolean,
    ) {
        isSavingEdit = true
        statusMessage = null
        scope.launch {
            val result =
                withContext(Dispatchers.IO) {
                    photoEditSaver.save(
                        photoId = photo.id,
                        uri = photo.uri,
                        mimeType = photo.mimeType,
                        rotationDegrees = editRotationDegrees,
                        crop = editCropRect,
                        existingUndo = existingEditUndo(photo.id),
                    )
                }
            when (result) {
                is PhotoEditSaver.SaveResult.Success -> {
                    applySavedPhoto(
                        photo = photo,
                        sizeBytes = result.sizeBytes,
                        keepEditUndo = result.backupCreated,
                    )
                }

                PhotoEditSaver.SaveResult.NeedsWritePermission -> {
                    if (requestWriteIfNeeded && Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                        pendingWritePhoto = photo
                        pendingWriteKind = PendingWriteKind.SaveEdit
                        writeLauncherPending = { grantedPhoto ->
                            performSaveEdit(grantedPhoto, requestWriteIfNeeded = false)
                        }
                        val sender = repository.createWriteRequest(photo.uri)
                        writeLauncher.launch(IntentSenderRequest.Builder(sender).build())
                    } else {
                        isSavingEdit = false
                        statusMessage = context.getString(R.string.gallery_cleaner_edit_save_failed)
                    }
                }

                PhotoEditSaver.SaveResult.Failed -> {
                    isSavingEdit = false
                    statusMessage = context.getString(R.string.gallery_cleaner_edit_save_failed)
                }
            }
        }
    }

    fun applyRestoredEdit(undo: PendingEditUndo) {
        view.performLightActionHaptic()
        val restored = undo.photoSnapshot.copy(sizeBytes = undo.originalSizeBytes)
        remainingPhotos =
            if (remainingPhotos.any { it.id == restored.id }) {
                remainingPhotos.map { if (it.id == restored.id) restored else it }
            } else {
                remainingPhotos + restored
            }
        remainingCount = remainingPhotos.size
        currentPhoto = restored
        removeEditUndo(undo.photoId)
        editImageRevision += 1
        cardResetKey += 1
        statusMessage = null
    }

    fun performUndoEdit(
        undo: PendingEditUndo,
        requestWriteIfNeeded: Boolean,
    ) {
        statusMessage = null
        scope.launch {
            val result =
                withContext(Dispatchers.IO) {
                    photoEditSaver.restoreFromUndo(undo)
                }
            when (result) {
                PhotoEditSaver.RestoreResult.Success -> {
                    applyRestoredEdit(undo)
                }

                PhotoEditSaver.RestoreResult.NeedsWritePermission -> {
                    if (requestWriteIfNeeded && Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                        val photo =
                            currentPhoto?.takeIf { it.id == undo.photoId }
                                ?: remainingPhotos.firstOrNull { it.id == undo.photoId }
                        if (photo == null) {
                            statusMessage = context.getString(R.string.gallery_cleaner_undo_failed)
                            return@launch
                        }
                        pendingWritePhoto = photo
                        pendingWriteKind = PendingWriteKind.RestoreEdit
                        writeLauncherPending = {
                            performUndoEdit(undo, requestWriteIfNeeded = false)
                        }
                        val sender = repository.createWriteRequest(undo.uri)
                        writeLauncher.launch(IntentSenderRequest.Builder(sender).build())
                    } else {
                        statusMessage = context.getString(R.string.gallery_cleaner_undo_failed)
                    }
                }

                PhotoEditSaver.RestoreResult.Failed -> {
                    statusMessage = context.getString(R.string.gallery_cleaner_undo_failed)
                }
            }
        }
    }

    fun requestSystemTrash(photo: CameraPhoto) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) {
            return
        }
        pendingTrashPhoto = photo
        val sender: IntentSender = repository.createTrashRequest(photo.uri)
        trashLauncher.launch(IntentSenderRequest.Builder(sender).build())
    }

    fun requestSystemRestore(photo: CameraPhoto) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) {
            return
        }
        pendingRestorePhoto = photo
        val sender: IntentSender = repository.createRestoreRequest(photo.uri)
        restoreLauncher.launch(IntentSenderRequest.Builder(sender).build())
    }

    fun deletePhoto(photo: CameraPhoto) {
        statusMessage = null
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            requestSystemTrash(photo)
        } else {
            val deleted = repository.deletePermanently(photo.uri)
            if (deleted) {
                advanceAfterReview(photo, deleted = true)
            } else {
                statusMessage = context.getString(R.string.gallery_cleaner_delete_failed)
                cardResetKey += 1
            }
        }
    }

    fun undoLastAction() {
        when (val last = undoStack.lastOrNull()) {
            is GallerySessionUndo.Edit -> {
                performUndoEdit(last.undo, requestWriteIfNeeded = true)
            }

            is GallerySessionUndo.Delete -> {
                statusMessage = null
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    requestSystemRestore(last.photo)
                }
            }

            is GallerySessionUndo.Keep -> {
                restoreKeptPhoto(last.photo)
            }

            null -> Unit
        }
    }

    fun sharePhoto(photo: CameraPhoto) {
        val mimeType = photo.mimeType?.takeIf { it.isNotBlank() } ?: "image/*"
        val shareIntent =
            Intent(Intent.ACTION_SEND).apply {
                type = mimeType
                putExtra(Intent.EXTRA_STREAM, photo.uri)
                clipData = ClipData.newUri(context.contentResolver, photo.displayName, photo.uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
        try {
            context.startActivity(
                Intent.createChooser(
                    shareIntent,
                    context.getString(R.string.gallery_cleaner_share),
                ),
            )
        } catch (_: ActivityNotFoundException) {
            statusMessage = context.getString(R.string.gallery_cleaner_share_failed)
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
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    LaunchedEffect(settingsRevision) {
        val introPref = preferences.shouldShowIntro()
        if (introPref && !lastIntroPref) {
            showIntro = true
        }
        lastIntroPref = introPref
        refreshManageMediaAccess()
    }

    LaunchedEffect(hasPermission, showIntro, settingsRevision) {
        if (!hasPermission || showIntro) {
            return@LaunchedEffect
        }
        if (!viewModel.sessionInitialized) {
            viewModel.bootstrapDateFilter()
            reloadPhotos()
            viewModel.markSessionInitialized(settingsRevision)
            return@LaunchedEffect
        }
        if (viewModel.appliedSettingsRevision != settingsRevision) {
            viewModel.markSettingsApplied(settingsRevision)
            reloadPhotos()
        }
    }

    if (showStatsDialog) {
        val reviewedTotal = preferences.reviewedPhotoCount()
        AlertDialog(
            onDismissRequest = { showStatsDialog = false },
            title = { Text(stringResource(R.string.gallery_cleaner_stats_title)) },
            text = {
                Column(
                    modifier = Modifier.dialogScrollable(),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    if (unreviewedOnlyMode) {
                        Text(
                            stringResource(
                                R.string.gallery_cleaner_stats_reviewed_total,
                                reviewedTotal,
                            ),
                        )
                        Text(
                            stringResource(
                                R.string.gallery_cleaner_stats_remaining,
                                remainingCount,
                            ),
                        )
                    }
                    Text(
                        stringResource(
                            R.string.gallery_cleaner_stats_reviewed_session,
                            sessionReviewedCount,
                        ),
                    )
                    Text(
                        stringResource(
                            R.string.gallery_cleaner_stats_deleted,
                            sessionDeletedCount,
                        ),
                    )
                    Text(
                        stringResource(
                            R.string.gallery_cleaner_stats_freed,
                            CameraGalleryRepository.formatFileSize(sessionFreedBytes),
                        ),
                    )
                }
            },
            confirmButton = {
                TextButton(onClick = { showStatsDialog = false }) {
                    Text(stringResource(R.string.gallery_cleaner_stats_ok))
                }
            },
        )
    }

    if (showIntro) {
        GalleryCleanerIntroDialog(
            dontShowAgain = dontShowAgain,
            onDontShowAgainChange = { dontShowAgain = it },
            onConfirm = {
                if (dontShowAgain) {
                    preferences.setShowIntro(false)
                }
                lastIntroPref = preferences.shouldShowIntro()
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
        contentWindowInsets = WindowInsets.safeDrawing,
        topBar = {
            Column {
                // Custom bar: default TopAppBar clips a two-line title on compact phones.
                Surface(color = MaterialTheme.colorScheme.surface) {
                    Row(
                        modifier =
                        Modifier
                            .fillMaxWidth()
                            .windowInsetsPadding(WindowInsets.statusBars)
                            .heightIn(min = 64.dp)
                            .padding(end = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        IconButton(onClick = { leaveCleaner() }) {
                            Icon(
                                imageVector = Icons.Filled.Close,
                                contentDescription = stringResource(R.string.gallery_cleaner_close),
                            )
                        }
                        Column(
                            modifier =
                            Modifier
                                .weight(1f)
                                .padding(end = 8.dp),
                        ) {
                            Text(
                                text = stringResource(R.string.gallery_cleaner_title),
                                style = MaterialTheme.typography.titleLarge,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                            )
                            Text(
                                text =
                                stringResource(
                                    R.string.gallery_cleaner_session_stats,
                                    sessionDeletedCount,
                                    CameraGalleryRepository.formatFileSize(sessionFreedBytes),
                                ),
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                            )
                        }
                        if (hasPermission && remainingCount > 0 && !isEditing) {
                            val compact = isCompactWidth()
                            Text(
                                text =
                                if (compact) {
                                    remainingCount.toString()
                                } else {
                                    stringResource(
                                        if (unreviewedOnlyMode) {
                                            R.string.gallery_cleaner_remaining_unreviewed
                                        } else {
                                            R.string.gallery_cleaner_remaining
                                        },
                                        remainingCount,
                                    )
                                },
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                                modifier =
                                Modifier
                                    .widthIn(max = if (compact) 64.dp else 140.dp)
                                    .padding(end = 4.dp),
                            )
                        }
                        if (!isEditing) {
                            Box {
                                IconButton(onClick = { menuExpanded = true }) {
                                    Icon(
                                        imageVector = Icons.Filled.MoreVert,
                                        contentDescription =
                                        stringResource(R.string.gallery_cleaner_menu),
                                    )
                                }
                                DropdownMenu(
                                    expanded = menuExpanded,
                                    onDismissRequest = { menuExpanded = false },
                                ) {
                                    if (currentPhoto != null) {
                                        DropdownMenuItem(
                                            text = {
                                                Text(
                                                    stringResource(
                                                        R.string.gallery_cleaner_filter_shoot_day,
                                                    ),
                                                )
                                            },
                                            leadingIcon = {
                                                Icon(
                                                    imageVector = Icons.Filled.Today,
                                                    contentDescription = null,
                                                )
                                            },
                                            onClick = {
                                                menuExpanded = false
                                                applyShootDayFilter(currentPhoto!!.dateTakenEpochMs)
                                                if (hasPermission && !showIntro) {
                                                    reloadPhotos()
                                                }
                                            },
                                        )
                                    }
                                    if (dateFilter.enabled) {
                                        DropdownMenuItem(
                                            text = {
                                                Text(
                                                    stringResource(
                                                        R.string.gallery_cleaner_clear_date_filter,
                                                    ),
                                                )
                                            },
                                            leadingIcon = {
                                                Icon(
                                                    imageVector = Icons.Filled.FilterAltOff,
                                                    contentDescription = null,
                                                )
                                            },
                                            onClick = {
                                                menuExpanded = false
                                                val cleared = dateFilter.withEnabled(false)
                                                preferences.saveDateFilter(cleared)
                                                dateFilter = cleared
                                                if (hasPermission && !showIntro) {
                                                    reloadPhotos()
                                                }
                                            },
                                        )
                                    }
                                    DropdownMenuItem(
                                        text = {
                                            Text(
                                                stringResource(
                                                    if (unreviewedOnlyMode) {
                                                        R.string.gallery_cleaner_disable_unreviewed_only
                                                    } else {
                                                        R.string.gallery_cleaner_enable_unreviewed_only
                                                    },
                                                ),
                                            )
                                        },
                                        leadingIcon = {
                                            Icon(
                                                imageVector =
                                                if (unreviewedOnlyMode) {
                                                    Icons.Filled.Visibility
                                                } else {
                                                    Icons.Filled.VisibilityOff
                                                },
                                                contentDescription = null,
                                            )
                                        },
                                        onClick = {
                                            menuExpanded = false
                                            val enabled = !unreviewedOnlyMode
                                            preferences.setUnreviewedOnlyModeEnabled(enabled)
                                            unreviewedOnlyMode = enabled
                                            if (hasPermission && !showIntro) {
                                                reloadPhotos()
                                            }
                                        },
                                    )
                                    DropdownMenuItem(
                                        text = {
                                            Text(stringResource(R.string.gallery_cleaner_stats))
                                        },
                                        leadingIcon = {
                                            Icon(
                                                imageVector = Icons.Filled.BarChart,
                                                contentDescription = null,
                                            )
                                        },
                                        onClick = {
                                            menuExpanded = false
                                            showStatsDialog = true
                                        },
                                    )
                                    DropdownMenuItem(
                                        text = {
                                            Text(stringResource(R.string.gallery_cleaner_settings))
                                        },
                                        leadingIcon = {
                                            Icon(
                                                imageVector = Icons.Filled.Settings,
                                                contentDescription = null,
                                            )
                                        },
                                        onClick = {
                                            menuExpanded = false
                                            onOpenSettings(currentPhoto?.dateTakenEpochMs)
                                        },
                                    )
                                }
                            }
                        }
                    }
                }
                val canEditPhoto = hasPermission && currentPhoto != null && !showIntro
                val canUndo = undoStack.isNotEmpty()
                val showSecondaryBar =
                    canEditPhoto ||
                        (!isEditing && (dateFilter.enabled || canUndo))
                if (showSecondaryBar) {
                    Row(
                        modifier =
                        Modifier
                            .fillMaxWidth()
                            .padding(start = 16.dp, end = 4.dp, top = 0.dp, bottom = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        if (!isEditing && dateFilter.enabled) {
                            val dateFormat =
                                remember {
                                    DateFormat.getDateInstance(DateFormat.SHORT)
                                }
                            val startLabel =
                                dateFormat.format(Date(dateFilter.startEpochSecInclusive * 1000L))
                            val endLabel =
                                dateFormat.format(Date(dateFilter.endEpochSecInclusive * 1000L))
                            val sameDay =
                                dateFilter.fromYear() == dateFilter.toYear() &&
                                    dateFilter.fromMonth() == dateFilter.toMonth() &&
                                    dateFilter.fromDay() == dateFilter.toDay()
                            Text(
                                text =
                                if (sameDay) {
                                    stringResource(
                                        R.string.gallery_cleaner_date_filter_active_day,
                                        startLabel,
                                    )
                                } else {
                                    stringResource(
                                        R.string.gallery_cleaner_date_filter_active,
                                        startLabel,
                                        endLabel,
                                    )
                                },
                                modifier = Modifier.weight(1f),
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                maxLines = 2,
                                overflow = TextOverflow.Ellipsis,
                            )
                        } else {
                            Spacer(modifier = Modifier.weight(1f))
                        }
                        if (canEditPhoto) {
                            if (!isEditing) {
                                IconButton(
                                    onClick = { enterEditMode() },
                                    enabled = !isSavingEdit,
                                ) {
                                    Icon(
                                        imageVector = Icons.Filled.Crop,
                                        contentDescription =
                                        stringResource(R.string.gallery_cleaner_action_crop),
                                    )
                                }
                                IconButton(
                                    onClick = { enterEditMode() },
                                    enabled = !isSavingEdit,
                                ) {
                                    Icon(
                                        imageVector = Icons.AutoMirrored.Filled.RotateRight,
                                        contentDescription =
                                        stringResource(R.string.gallery_cleaner_action_rotate),
                                    )
                                }
                            }
                        }
                        if (!isEditing && canEditPhoto) {
                            IconButton(onClick = { currentPhoto?.let { sharePhoto(it) } }) {
                                Icon(
                                    imageVector = Icons.Filled.Share,
                                    contentDescription =
                                    stringResource(R.string.gallery_cleaner_share),
                                )
                            }
                        }
                        if (!isEditing && canUndo) {
                            IconButton(onClick = { undoLastAction() }) {
                                Icon(
                                    imageVector = Icons.AutoMirrored.Filled.Undo,
                                    contentDescription =
                                    stringResource(R.string.gallery_cleaner_undo_delete),
                                )
                            }
                        }
                    }
                }
            }
        },
        bottomBar = {
            if (hasPermission && currentPhoto != null && !isEditing) {
                val photo = currentPhoto!!
                ReviewActionBar(
                    onDelete = { deletePhoto(photo) },
                    onKeep = { advanceAfterReview(photo) },
                    onSkip =
                    if (unreviewedOnlyMode) {
                        { skipPhoto(photo) }
                    } else {
                        null
                    },
                )
            }
        },
    ) { innerPadding ->
        Box(
            modifier =
            Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.background),
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
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.padding(24.dp),
                    ) {
                        Text(
                            text =
                            stringResource(
                                when {
                                    dateFilter.enabled -> R.string.gallery_cleaner_empty_filtered
                                    unreviewedOnlyMode -> R.string.gallery_cleaner_empty_unreviewed
                                    else -> R.string.gallery_cleaner_empty
                                },
                            ),
                            style = MaterialTheme.typography.bodyLarge,
                        )
                        if (dateFilter.enabled) {
                            Spacer(modifier = Modifier.height(16.dp))
                            Button(
                                onClick = {
                                    val cleared = dateFilter.withEnabled(false)
                                    preferences.saveDateFilter(cleared)
                                    dateFilter = cleared
                                    if (hasPermission && !showIntro) {
                                        reloadPhotos()
                                    }
                                },
                            ) {
                                Text(stringResource(R.string.gallery_cleaner_clear_date_filter))
                            }
                        }
                    }
                }

                else -> {
                    val photo = currentPhoto!!
                    if (isEditing) {
                        PhotoCropEditor(
                            photo = photo,
                            rotationDegrees = editRotationDegrees,
                            onRotationDegreesChange = { editRotationDegrees = it },
                            cropRect = editCropRect,
                            onCropRectChange = { editCropRect = it },
                            imageRevision = editImageRevision,
                            isSaving = isSavingEdit,
                            onSave = {
                                performSaveEdit(photo, requestWriteIfNeeded = true)
                            },
                            onDiscard = { exitEditMode() },
                            modifier = Modifier.fillMaxSize(),
                        )
                    } else {
                        SwipeablePhotoCard(
                            photo = photo,
                            resetKey = cardResetKey,
                            imageRevision = editImageRevision,
                            onDelete = { deletePhoto(photo) },
                            onKeep = { advanceAfterReview(photo) },
                            modifier = Modifier.fillMaxSize(),
                        )
                    }
                }
            }

            statusMessage?.let { message ->
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.error,
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

enum class PendingWriteKind {
    SaveEdit,
    RestoreEdit,
}

@Composable
private fun ReviewActionBar(
    onDelete: () -> Unit,
    onKeep: () -> Unit,
    modifier: Modifier = Modifier,
    onSkip: (() -> Unit)? = null,
) {
    Box(
        modifier =
        modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surfaceContainer)
            .windowInsetsPadding(WindowInsets.navigationBars),
        contentAlignment = Alignment.Center,
    ) {
        Row(
            modifier =
            Modifier
                .adaptiveBottomBarWidth()
                .padding(horizontal = 12.dp, vertical = 10.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            CompactBottomActionButton(
                onClick = onDelete,
                icon = Icons.Filled.Delete,
                label = stringResource(R.string.gallery_cleaner_action_delete),
                colors =
                ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error,
                    contentColor = MaterialTheme.colorScheme.onError,
                ),
            )
            if (onSkip != null) {
                CompactBottomActionButton(
                    onClick = onSkip,
                    icon = Icons.Filled.SkipNext,
                    label = stringResource(R.string.gallery_cleaner_action_skip),
                    outlined = true,
                )
            }
            CompactBottomActionButton(
                onClick = onKeep,
                icon = Icons.Filled.Done,
                label = stringResource(R.string.gallery_cleaner_action_keep),
            )
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
            Column(modifier = Modifier.dialogScrollable()) {
                Text(stringResource(R.string.gallery_cleaner_intro_message))
                Spacer(modifier = Modifier.height(16.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(
                        checked = dontShowAgain,
                        onCheckedChange = onDontShowAgainChange,
                    )
                    Text(
                        text = stringResource(R.string.gallery_cleaner_intro_dont_show),
                        modifier =
                        Modifier
                            .weight(1f)
                            .padding(start = 4.dp),
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
internal fun ManageMediaPromptDialog(
    onOpenSettings: () -> Unit,
    onSkip: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onSkip,
        title = { Text(stringResource(R.string.gallery_cleaner_manage_media_title)) },
        text = {
            Text(
                text = stringResource(R.string.gallery_cleaner_manage_media_message),
                modifier = Modifier.dialogScrollable(),
            )
        },
        confirmButton = {
            TextButton(onClick = onOpenSettings) {
                Text(
                    text = stringResource(R.string.gallery_cleaner_manage_media_open),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
        },
        dismissButton = {
            TextButton(onClick = onSkip) {
                Text(
                    text = stringResource(R.string.gallery_cleaner_manage_media_skip),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
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
        Button(
            onClick = onGrantClick,
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 10.dp),
        ) {
            Text(
                text = stringResource(R.string.gallery_cleaner_permission_grant),
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

@Composable
private fun Modifier.dialogScrollable(): Modifier {
    val maxHeight = (LocalConfiguration.current.screenHeightDp * 0.45f).dp
    return this
        .heightIn(max = maxHeight)
        .verticalScroll(rememberScrollState())
}

private const val PhotoMinZoom = 1f
private const val PhotoMaxZoom = 5f

@Composable
private fun SwipeablePhotoCard(
    photo: CameraPhoto,
    resetKey: Int,
    imageRevision: Int,
    onDelete: () -> Unit,
    onKeep: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val density = LocalDensity.current
    val scope = rememberCoroutineScope()
    val offsetX = remember(resetKey) { Animatable(0f) }
    val offsetY = remember(resetKey) { Animatable(0f) }
    var dragOffset by remember(resetKey) { mutableStateOf(Offset.Zero) }
    var zoomScale by remember(resetKey) { mutableFloatStateOf(PhotoMinZoom) }
    var zoomOffset by remember(resetKey) { mutableStateOf(Offset.Zero) }
    var viewportSize by remember(resetKey) { mutableStateOf(IntSize.Zero) }
    val dismissThreshold = with(density) { 96.dp.toPx() }
    val exitDistance = with(density) { 480.dp.toPx() }
    val dateLabel =
        remember(photo.dateTakenEpochMs) {
            DateFormat
                .getDateTimeInstance(DateFormat.MEDIUM, DateFormat.SHORT)
                .format(Date(photo.dateTakenEpochMs))
        }
    val sizeLabel =
        remember(photo.sizeBytes) {
            CameraGalleryRepository.formatFileSize(photo.sizeBytes)
        }
    val nameLabel =
        photo.displayName?.takeIf { it.isNotBlank() }
            ?: stringResource(R.string.gallery_cleaner_untitled)
    val isZoomed = zoomScale > 1.01f

    LaunchedEffect(resetKey) {
        offsetX.snapTo(0f)
        offsetY.snapTo(0f)
        dragOffset = Offset.Zero
        zoomScale = PhotoMinZoom
        zoomOffset = Offset.Zero
    }

    val displayOffset =
        if (dragOffset != Offset.Zero) {
            dragOffset
        } else {
            Offset(offsetX.value, offsetY.value)
        }
    val horizontalProgress = (displayOffset.x / dismissThreshold).coerceIn(-1.5f, 1.5f)
    val upwardProgress = (-displayOffset.y / dismissThreshold).coerceIn(0f, 1.5f)
    val downwardProgress = (displayOffset.y / dismissThreshold).coerceIn(0f, 1.5f)
    val travel = hypot(displayOffset.x.toDouble(), displayOffset.y.toDouble()).toFloat()

    Column(modifier = modifier.fillMaxSize()) {
        Box(
            modifier =
            Modifier
                .weight(1f)
                .fillMaxWidth()
                .onSizeChanged { viewportSize = it },
            contentAlignment = Alignment.Center,
        ) {
            if (!isZoomed &&
                horizontalProgress < -0.15f &&
                abs(displayOffset.x) >= abs(displayOffset.y)
            ) {
                SwipeHint(
                    icon = Icons.Filled.Delete,
                    label = stringResource(R.string.gallery_cleaner_swipe_left_hint),
                    color = MaterialTheme.colorScheme.error,
                    alpha = (-horizontalProgress).coerceIn(0f, 1f),
                    modifier = Modifier.align(Alignment.CenterEnd).padding(end = 24.dp),
                )
            }
            if (!isZoomed &&
                horizontalProgress > 0.15f &&
                abs(displayOffset.x) >= abs(displayOffset.y)
            ) {
                SwipeHint(
                    icon = Icons.Filled.Done,
                    label = stringResource(R.string.gallery_cleaner_swipe_right_hint),
                    color = MaterialTheme.colorScheme.primary,
                    alpha = horizontalProgress.coerceIn(0f, 1f),
                    modifier = Modifier.align(Alignment.CenterStart).padding(start = 24.dp),
                )
            }
            if (!isZoomed &&
                upwardProgress > 0.15f &&
                abs(displayOffset.y) > abs(displayOffset.x)
            ) {
                SwipeHint(
                    icon = Icons.Filled.KeyboardArrowUp,
                    label = stringResource(R.string.gallery_cleaner_swipe_up_hint),
                    color = MaterialTheme.colorScheme.primary,
                    alpha = upwardProgress.coerceIn(0f, 1f),
                    modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 24.dp),
                )
            }
            if (!isZoomed &&
                downwardProgress > 0.15f &&
                abs(displayOffset.y) > abs(displayOffset.x)
            ) {
                SwipeHint(
                    icon = Icons.Filled.KeyboardArrowDown,
                    label = stringResource(R.string.gallery_cleaner_swipe_down_hint),
                    color = MaterialTheme.colorScheme.error,
                    alpha = downwardProgress.coerceIn(0f, 1f),
                    modifier = Modifier.align(Alignment.TopCenter).padding(top = 24.dp),
                )
            }

            AsyncImage(
                model =
                ImageRequest
                    .Builder(LocalContext.current)
                    .data(photo.uri)
                    .memoryCacheKey("${photo.uri}-$imageRevision")
                    .diskCacheKey("${photo.uri}-$imageRevision")
                    .crossfade(true)
                    .build(),
                contentDescription = photo.displayName,
                contentScale = ContentScale.Fit,
                modifier =
                Modifier
                    .fillMaxSize()
                    .graphicsLayer {
                        scaleX = zoomScale
                        scaleY = zoomScale
                        translationX = zoomOffset.x
                        translationY = zoomOffset.y
                        rotationZ = if (isZoomed) 0f else displayOffset.x / 40f
                        alpha =
                            if (isZoomed) {
                                1f
                            } else {
                                1f - (travel / (exitDistance * 1.2f)).coerceIn(0f, 0.35f)
                            }
                    }
                    .offset {
                        if (isZoomed) {
                            IntOffset.Zero
                        } else {
                            IntOffset(displayOffset.x.roundToInt(), displayOffset.y.roundToInt())
                        }
                    }
                    .background(MaterialTheme.colorScheme.background)
                    .pointerInput(resetKey, photo.id) {
                        awaitEachGesture {
                            awaitFirstDown(requireUnconsumed = false)
                            var multiTouch = false
                            var gestureActive = true
                            while (gestureActive) {
                                val event = awaitPointerEvent()
                                val pressed = event.changes.filter { it.pressed }
                                if (pressed.isEmpty()) {
                                    gestureActive = false
                                } else if (pressed.size >= 2) {
                                    multiTouch = true
                                    dragOffset = Offset.Zero
                                    val zoomChange = event.calculateZoom()
                                    val panChange = event.calculatePan()
                                    val nextScale =
                                        (zoomScale * zoomChange).coerceIn(
                                            PhotoMinZoom,
                                            PhotoMaxZoom,
                                        )
                                    zoomScale = nextScale
                                    zoomOffset =
                                        clampZoomOffset(
                                            offset = zoomOffset + panChange,
                                            scale = nextScale,
                                            viewport = viewportSize,
                                        )
                                    if (nextScale <= 1.01f) {
                                        zoomScale = PhotoMinZoom
                                        zoomOffset = Offset.Zero
                                    }
                                    pressed.forEach { change ->
                                        if (change.positionChanged()) {
                                            change.consume()
                                        }
                                    }
                                } else if (!multiTouch && pressed.size == 1) {
                                    val change = pressed[0]
                                    val drag = change.position - change.previousPosition
                                    if (drag != Offset.Zero) {
                                        if (zoomScale > 1.01f) {
                                            zoomOffset =
                                                clampZoomOffset(
                                                    offset = zoomOffset + drag,
                                                    scale = zoomScale,
                                                    viewport = viewportSize,
                                                )
                                        } else {
                                            dragOffset += drag
                                        }
                                        change.consume()
                                    }
                                } else if (multiTouch && pressed.size == 1) {
                                    // After pinch, ignore leftover single-finger until lift.
                                    pressed.forEach { change ->
                                        if (change.positionChanged()) {
                                            change.consume()
                                        }
                                    }
                                }
                            }
                            if (multiTouch || zoomScale > 1.01f) {
                                dragOffset = Offset.Zero
                                scope.launch {
                                    offsetX.snapTo(0f)
                                    offsetY.snapTo(0f)
                                }
                                return@awaitEachGesture
                            }
                            val current = dragOffset
                            dragOffset = Offset.Zero
                            scope.launch {
                                offsetX.snapTo(current.x)
                                offsetY.snapTo(current.y)
                                val predominatelyVertical = abs(current.y) > abs(current.x)
                                when {
                                    predominatelyVertical &&
                                        current.y <= -dismissThreshold -> {
                                        offsetY.animateTo(-exitDistance, tween(180))
                                        onKeep()
                                    }

                                    predominatelyVertical &&
                                        current.y >= dismissThreshold -> {
                                        offsetY.animateTo(exitDistance, tween(180))
                                        onDelete()
                                    }

                                    !predominatelyVertical &&
                                        current.x <= -dismissThreshold -> {
                                        offsetX.animateTo(-exitDistance, tween(180))
                                        onDelete()
                                    }

                                    !predominatelyVertical &&
                                        current.x >= dismissThreshold -> {
                                        offsetX.animateTo(exitDistance, tween(180))
                                        onKeep()
                                    }

                                    else -> {
                                        offsetX.animateTo(0f, tween(180))
                                        offsetY.animateTo(0f, tween(180))
                                    }
                                }
                            }
                        }
                    },
            )
        }

        val compactMeta = isCompactHeight()
        Column(
            modifier =
            Modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.background)
                .padding(
                    horizontal = 16.dp,
                    vertical = if (compactMeta) 6.dp else 10.dp,
                ),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            if (compactMeta) {
                Text(
                    text = "$dateLabel · $sizeLabel",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            } else {
                Text(
                    text = nameLabel,
                    style = MaterialTheme.typography.titleSmall,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text = dateLabel,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text = sizeLabel,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
        }
    }
}

private fun clampZoomOffset(
    offset: Offset,
    scale: Float,
    viewport: IntSize,
): Offset {
    if (scale <= 1.01f || viewport.width <= 0 || viewport.height <= 0) {
        return Offset.Zero
    }
    val maxX = viewport.width * (scale - 1f) / 2f
    val maxY = viewport.height * (scale - 1f) / 2f
    return Offset(
        x = offset.x.coerceIn(-maxX, maxX),
        y = offset.y.coerceIn(-maxY, maxY),
    )
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
