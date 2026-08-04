package dev.harrix.hsk.ui.gallery

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.Intent
import android.content.IntentSender
import android.content.pm.PackageManager
import android.content.res.Configuration
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
import androidx.compose.foundation.layout.WindowInsetsSides
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.only
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
import androidx.compose.material.icons.filled.FilterAlt
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
import androidx.compose.runtime.mutableIntStateOf
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
import androidx.compose.ui.text.style.TextAlign
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
import dev.harrix.hsk.gallery.PendingEditUndo
import dev.harrix.hsk.gallery.PhotoEditSaver
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.CompactBottomActionButton
import dev.harrix.hsk.ui.adaptiveBottomBarWidth
import dev.harrix.hsk.ui.isCompactHeight
import dev.harrix.hsk.ui.isCompactWidth
import dev.harrix.hsk.ui.isTablet
import dev.harrix.hsk.ui.performLightActionHaptic
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.DateFormat
import java.util.Date
import kotlin.math.abs
import kotlin.math.hypot
import kotlin.math.roundToInt

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
    var showDateFilterDialog by remember { mutableStateOf(false) }
    var dateFilter by viewModel.dateFilter
    var unreviewedOnlyMode by viewModel.unreviewedOnlyMode
    var reviewOrder by viewModel.reviewOrder
    var sessionReviewedCount by viewModel.sessionReviewedCount
    var sessionDeletedCount by viewModel.sessionDeletedCount
    var sessionFreedBytes by viewModel.sessionFreedBytes
    var showStatsDialog by viewModel.showStatsDialog
    var isEditing by viewModel.isEditing
    var unreviewedCountIgnoringDateFilter by viewModel.unreviewedCountIgnoringDateFilter
    var editImageRevision by viewModel.editImageRevision
    var pendingWritePhoto by viewModel.pendingWritePhoto

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
        // Shuffle once per load; session navigation stays sequential so undo/skip keep order.
        GalleryReviewOrder.Random -> photos.shuffled()

        GalleryReviewOrder.OldestFirst -> photos.sortedBy { it.dateTakenEpochMs }

        GalleryReviewOrder.NewestFirst -> photos.sortedByDescending { it.dateTakenEpochMs }
    }

    fun pickNext(from: List<CameraPhoto>): CameraPhoto? = from.firstOrNull()

    /**
     * Puts [photo] back into the session deck immediately before the current photo
     * (or at the front), then focuses it — same encounter order as skip after several undos.
     */
    fun reinsertAsCurrent(photo: CameraPhoto) {
        val without = remainingPhotos.filterNot { it.id == photo.id }
        val currentId = currentPhoto?.id
        val insertAt =
            when {
                currentId == null || currentId == photo.id -> 0

                else ->
                    without
                        .indexOfFirst { it.id == currentId }
                        .takeIf { it >= 0 }
                        ?: without.size
            }
        remainingPhotos = without.toMutableList().also { it.add(insertAt, photo) }
        remainingCount = remainingPhotos.size
        currentPhoto = photo
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
            unreviewedCountIgnoringDateFilter =
                (unreviewedCountIgnoringDateFilter - 1).coerceAtLeast(0)
        }
        if (deleted) {
            sessionDeletedCount += 1
            sessionFreedBytes += photo.sizeBytes
            preferences.recordDeletedPhoto(photo.sizeBytes)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                pushDeleteUndo(photo)
            }
        } else {
            pushKeepUndo(photo)
        }
        val index = remainingPhotos.indexOfFirst { it.id == photo.id }
        val updated = remainingPhotos.filterNot { it.id == photo.id }
        remainingPhotos = updated
        remainingCount = updated.size
        currentPhoto =
            when {
                updated.isEmpty() -> null
                index < 0 -> updated.first()
                index >= updated.size -> updated.first()
                else -> updated[index]
            }
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
        val index = remainingPhotos.indexOfFirst { it.id == photo.id }
        val nextIndex =
            if (index < 0) {
                0
            } else {
                (index + 1) % remainingPhotos.size
            }
        currentPhoto = remainingPhotos[nextIndex]
        cardResetKey += 1
        statusMessage = null
    }

    fun restoreTrashedPhoto(photo: CameraPhoto) {
        view.performLightActionHaptic()
        if (unreviewedOnlyMode) {
            preferences.unmarkPhotoReviewed(photo.id)
            unreviewedCountIgnoringDateFilter += 1
        }
        sessionReviewedCount = (sessionReviewedCount - 1).coerceAtLeast(0)
        sessionDeletedCount = (sessionDeletedCount - 1).coerceAtLeast(0)
        sessionFreedBytes = (sessionFreedBytes - photo.sizeBytes).coerceAtLeast(0L)
        preferences.recordRestoredDeletedPhoto(photo.sizeBytes)
        reinsertAsCurrent(photo)
        removeDeleteUndo(photo.id)
        cardResetKey += 1
        statusMessage = null
    }

    fun restoreKeptPhoto(photo: CameraPhoto) {
        view.performLightActionHaptic()
        if (unreviewedOnlyMode) {
            preferences.unmarkPhotoReviewed(photo.id)
            unreviewedCountIgnoringDateFilter += 1
        }
        sessionReviewedCount = (sessionReviewedCount - 1).coerceAtLeast(0)
        reinsertAsCurrent(photo)
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

    fun reloadPhotos(markInitializedRevision: Int? = null) {
        isLoading = true
        statusMessage = null
        val previousOrder = reviewOrder
        dateFilter = preferences.loadDateFilter()
        unreviewedOnlyMode = preferences.isUnreviewedOnlyModeEnabled()
        reviewOrder = preferences.getReviewOrder()
        val orderChanged = previousOrder != reviewOrder
        val previousPhotoId = currentPhoto?.id
        val imagesPath = preferences.getImagesRelativePath()
        scope.launch {
            val loaded =
                withContext(Dispatchers.IO) {
                    repository.loadCameraPhotos(imagesPath)
                }
            unreviewedCountIgnoringDateFilter =
                if (unreviewedOnlyMode) {
                    val reviewedIds = preferences.getReviewedPhotoIds()
                    loaded.count { it.id !in reviewedIds }
                } else {
                    0
                }
            val photos = orderPhotos(applyFilters(loaded))
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
            markInitializedRevision?.let { viewModel.markSessionInitialized(it) }
        }
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
        mutableStateOf<(() -> Unit)?>(null)
    }
    val writeLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.StartIntentSenderForResult(),
        ) { result ->
            pendingWritePhoto = null
            if (result.resultCode == Activity.RESULT_OK) {
                writeLauncherPending?.invoke()
            } else {
                statusMessage = context.getString(R.string.gallery_cleaner_undo_failed)
            }
            writeLauncherPending = null
        }

    fun enterEditMode() {
        if (currentPhoto == null) {
            return
        }
        isEditing = true
        statusMessage = null
        menuExpanded = false
    }

    fun exitEditMode() {
        isEditing = false
        statusMessage = null
    }

    BackHandler {
        when {
            showDateFilterDialog -> {
                showDateFilterDialog = false
                if (hasPermission && !showIntro) {
                    reloadPhotos()
                }
            }

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

    fun applyRestoredEdit(undo: PendingEditUndo) {
        view.performLightActionHaptic()
        val restored = undo.photoSnapshot.copy(sizeBytes = undo.originalSizeBytes)
        if (remainingPhotos.any { it.id == restored.id }) {
            remainingPhotos =
                remainingPhotos.map { photo ->
                    if (photo.id == restored.id) {
                        restored
                    } else {
                        photo
                    }
                }
            remainingCount = remainingPhotos.size
            currentPhoto = restored
        } else {
            reinsertAsCurrent(restored)
        }
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
            reloadPhotos(markInitializedRevision = settingsRevision)
            return@LaunchedEffect
        }
        if (viewModel.appliedSettingsRevision != settingsRevision) {
            viewModel.markSettingsApplied(settingsRevision)
            reloadPhotos()
        }
    }

    if (showDateFilterDialog) {
        val shootDayEpochMs = currentPhoto?.dateTakenEpochMs
        val shootDayLabel =
            remember(shootDayEpochMs) {
                shootDayEpochMs?.let { epochMs ->
                    DateFormat
                        .getDateInstance(DateFormat.MEDIUM)
                        .format(Date(epochMs))
                }
            }
        AlertDialog(
            onDismissRequest = {
                showDateFilterDialog = false
                if (hasPermission && !showIntro) {
                    reloadPhotos()
                }
            },
            title = { AutoFitText(text = stringResource(R.string.gallery_cleaner_date_filter), maxLines = 2) },
            text = {
                GalleryDateFilterSettingsContent(
                    filter = dateFilter,
                    onFilterChange = { next ->
                        preferences.saveDateFilter(next)
                        dateFilter = next
                    },
                    shootDayEpochMs = shootDayEpochMs,
                    shootDayLabel = shootDayLabel,
                    modifier = Modifier.dialogScrollable(),
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        showDateFilterDialog = false
                        if (hasPermission && !showIntro) {
                            reloadPhotos()
                        }
                    },
                ) {
                    AutoFitText(text = stringResource(R.string.gallery_cleaner_stats_ok), maxLines = 2)
                }
            },
        )
    }

    if (showStatsDialog) {
        var statsTick by remember { mutableIntStateOf(0) }
        val reviewedTotal = remember(statsTick) { preferences.reviewedPhotoCount() }
        val lifetimeDeleted = remember(statsTick) { preferences.totalDeletedCount() }
        val lifetimeFreed = remember(statsTick) { preferences.totalFreedBytes() }
        val canResetStats = lifetimeDeleted > 0 || lifetimeFreed > 0L
        AlertDialog(
            onDismissRequest = { showStatsDialog = false },
            title = { AutoFitText(text = stringResource(R.string.gallery_cleaner_stats_title), maxLines = 2) },
            text = {
                Column(
                    modifier = Modifier.dialogScrollable(),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    if (unreviewedOnlyMode) {
                        AutoFitText(
                            text = stringResource(
                                R.string.gallery_cleaner_stats_reviewed_total,
                                reviewedTotal,
                            ),
                            maxLines = 1,
                        )
                        AutoFitText(
                            text = stringResource(
                                R.string.gallery_cleaner_stats_remaining,
                                remainingCount,
                            ),
                            maxLines = 1,
                        )
                    }
                    AutoFitText(
                        text = stringResource(
                            R.string.gallery_cleaner_stats_reviewed_session,
                            sessionReviewedCount,
                        ),
                        maxLines = 1,
                    )
                    AutoFitText(
                        text = stringResource(
                            R.string.gallery_cleaner_stats_deleted,
                            lifetimeDeleted,
                        ),
                        maxLines = 1,
                    )
                    AutoFitText(
                        text = stringResource(
                            R.string.gallery_cleaner_stats_freed,
                            CameraGalleryRepository.formatFileSize(lifetimeFreed),
                        ),
                        maxLines = 1,
                    )
                }
            },
            dismissButton = {
                TextButton(
                    onClick = {
                        preferences.clearLifetimeDeleteStats()
                        sessionDeletedCount = 0
                        sessionFreedBytes = 0L
                        statsTick += 1
                    },
                    enabled = canResetStats,
                ) {
                    AutoFitText(text = stringResource(R.string.gallery_cleaner_stats_reset), maxLines = 2)
                }
            },
            confirmButton = {
                TextButton(onClick = { showStatsDialog = false }) {
                    AutoFitText(text = stringResource(R.string.gallery_cleaner_stats_ok), maxLines = 2)
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

    val isLandscape =
        LocalConfiguration.current.orientation == Configuration.ORIENTATION_LANDSCAPE
    // Split layout is for phones only; tablets keep the original stacked layout.
    val useLandscapeSplit = isLandscape && !isTablet()
    val canEditPhoto = hasPermission && currentPhoto != null && !showIntro
    val canUndo = undoStack.isNotEmpty()
    val showSecondaryBar =
        canEditPhoto ||
            (!isEditing && (dateFilter.enabled || canUndo))

    Scaffold(
        modifier =
        modifier.windowInsetsPadding(
            WindowInsets.safeDrawing.only(WindowInsetsSides.Horizontal),
        ),
        contentWindowInsets = WindowInsets.safeDrawing.only(WindowInsetsSides.Vertical),
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
                        IconButton(
                            onClick = {
                                if (isEditing) {
                                    exitEditMode()
                                } else {
                                    leaveCleaner()
                                }
                            },
                        ) {
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
                            AutoFitText(
                                text = stringResource(R.string.gallery_cleaner_title),
                                style = MaterialTheme.typography.titleLarge,
                                maxLines = 1,
                            )
                            AutoFitText(
                                text =
                                stringResource(
                                    R.string.gallery_cleaner_session_stats,
                                    sessionDeletedCount,
                                    CameraGalleryRepository.formatFileSize(sessionFreedBytes),
                                ),
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                maxLines = 1,
                            )
                        }
                        if (hasPermission && remainingCount > 0 && !isEditing) {
                            val compact = isCompactWidth()
                            AutoFitText(
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
                                    DropdownMenuItem(
                                        text = {
                                            AutoFitText(
                                                text = stringResource(
                                                    R.string.gallery_cleaner_date_filter,
                                                ),
                                                maxLines = 2,
                                            )
                                        },
                                        leadingIcon = {
                                            Icon(
                                                imageVector = Icons.Filled.FilterAlt,
                                                contentDescription = null,
                                            )
                                        },
                                        onClick = {
                                            menuExpanded = false
                                            showDateFilterDialog = true
                                        },
                                    )
                                    if (currentPhoto != null) {
                                        DropdownMenuItem(
                                            text = {
                                                AutoFitText(
                                                    text = stringResource(
                                                        R.string.gallery_cleaner_filter_shoot_day,
                                                    ),
                                                    maxLines = 2,
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
                                                AutoFitText(
                                                    text = stringResource(
                                                        R.string.gallery_cleaner_clear_date_filter,
                                                    ),
                                                    maxLines = 2,
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
                                            AutoFitText(
                                                text = stringResource(
                                                    if (unreviewedOnlyMode) {
                                                        R.string.gallery_cleaner_disable_unreviewed_only
                                                    } else {
                                                        R.string.gallery_cleaner_enable_unreviewed_only
                                                    },
                                                ),
                                                maxLines = 2,
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
                                            AutoFitText(text = stringResource(R.string.gallery_cleaner_stats), maxLines = 2)
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
                                            AutoFitText(text = stringResource(R.string.gallery_cleaner_settings), maxLines = 2)
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
                if (showSecondaryBar && !useLandscapeSplit) {
                    PhotoSecondaryActionsRow(
                        dateFilter = dateFilter,
                        isEditing = isEditing,
                        canEditPhoto = canEditPhoto,
                        canUndo = canUndo,
                        isSavingEdit = false,
                        onCrop = { enterEditMode() },
                        onRotate = { enterEditMode() },
                        onShare = { currentPhoto?.let { sharePhoto(it) } },
                        onUndo = { undoLastAction() },
                    )
                }
            }
        },
        bottomBar = {
            val showPortraitActions =
                hasPermission && currentPhoto != null && !isEditing && !useLandscapeSplit
            if (showPortraitActions) {
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

                isLoading || (hasPermission && !showIntro && !viewModel.sessionInitialized) -> {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        CircularProgressIndicator()
                        Spacer(modifier = Modifier.height(16.dp))
                        AutoFitText(text = stringResource(R.string.gallery_cleaner_loading), maxLines = 1)
                    }
                }

                currentPhoto == null -> {
                    val suggestClearDateFilter =
                        dateFilter.enabled &&
                            unreviewedOnlyMode &&
                            unreviewedCountIgnoringDateFilter > 0
                    val congratsUnreviewedDone =
                        unreviewedOnlyMode && unreviewedCountIgnoringDateFilter == 0
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.padding(24.dp),
                    ) {
                        Text(
                            text =
                            stringResource(
                                when {
                                    suggestClearDateFilter ->
                                        R.string.gallery_cleaner_empty_filtered_has_unreviewed

                                    congratsUnreviewedDone ->
                                        R.string.gallery_cleaner_congrats_unreviewed

                                    dateFilter.enabled -> R.string.gallery_cleaner_empty_filtered

                                    unreviewedOnlyMode -> R.string.gallery_cleaner_empty_unreviewed

                                    else -> R.string.gallery_cleaner_empty
                                },
                            ),
                            style =
                            if (congratsUnreviewedDone) {
                                MaterialTheme.typography.titleMedium
                            } else {
                                MaterialTheme.typography.bodyLarge
                            },
                            textAlign = TextAlign.Center,
                        )
                        if (dateFilter.enabled &&
                            (suggestClearDateFilter || !congratsUnreviewedDone)
                        ) {
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
                                AutoFitText(text = stringResource(R.string.gallery_cleaner_clear_date_filter), maxLines = 2)
                            }
                        }
                    }
                }

                else -> {
                    val photo = currentPhoto!!
                    if (isEditing) {
                        EditablePhotoHost(
                            photo = photo,
                            imageRevision = editImageRevision,
                            existingUndo = existingEditUndo(photo.id),
                            allowSaveCopyFallback = false,
                            repository = repository,
                            onSave = { result ->
                                applySavedPhoto(
                                    photo = photo,
                                    sizeBytes = result.sizeBytes,
                                    keepEditUndo = result.backupCreated,
                                )
                            },
                            onDiscard = { exitEditMode() },
                            onError = { message -> statusMessage = message },
                            modifier = Modifier.fillMaxSize(),
                        )
                    } else if (useLandscapeSplit) {
                        Row(modifier = Modifier.fillMaxSize()) {
                            SwipeablePhotoCard(
                                photo = photo,
                                resetKey = cardResetKey,
                                imageRevision = editImageRevision,
                                onDelete = { deletePhoto(photo) },
                                onKeep = { advanceAfterReview(photo) },
                                showMetadata = false,
                                modifier =
                                Modifier
                                    .weight(1f)
                                    .fillMaxHeight()
                                    .padding(8.dp),
                            )
                            Column(
                                modifier =
                                Modifier
                                    .width(300.dp)
                                    .fillMaxHeight()
                                    .padding(horizontal = 12.dp, vertical = 8.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp),
                            ) {
                                if (showSecondaryBar) {
                                    PhotoSecondaryActionsRow(
                                        dateFilter = dateFilter,
                                        isEditing = isEditing,
                                        canEditPhoto = canEditPhoto,
                                        canUndo = canUndo,
                                        isSavingEdit = false,
                                        onCrop = { enterEditMode() },
                                        onRotate = { enterEditMode() },
                                        onShare = { sharePhoto(photo) },
                                        onUndo = { undoLastAction() },
                                        compact = true,
                                    )
                                }
                                PhotoMetaInfo(
                                    photo = photo,
                                    compact = false,
                                    endAligned = true,
                                    modifier = Modifier.fillMaxWidth(),
                                )
                                Spacer(modifier = Modifier.weight(1f))
                                ReviewActionBar(
                                    onDelete = { deletePhoto(photo) },
                                    onKeep = { advanceAfterReview(photo) },
                                    onSkip =
                                    if (unreviewedOnlyMode) {
                                        { skipPhoto(photo) }
                                    } else {
                                        null
                                    },
                                    embedded = true,
                                    modifier = Modifier.fillMaxWidth(),
                                )
                            }
                        }
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

@Composable
private fun ReviewActionBar(
    onDelete: () -> Unit,
    onKeep: () -> Unit,
    modifier: Modifier = Modifier,
    onSkip: (() -> Unit)? = null,
    embedded: Boolean = false,
) {
    val barModifier =
        if (embedded) {
            modifier.fillMaxWidth()
        } else {
            modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.surfaceContainer)
                .windowInsetsPadding(WindowInsets.navigationBars)
        }
    Box(
        modifier = barModifier,
        contentAlignment = Alignment.Center,
    ) {
        Row(
            modifier =
            Modifier
                .then(if (embedded) Modifier.fillMaxWidth() else Modifier.adaptiveBottomBarWidth())
                .padding(
                    horizontal = if (embedded) 0.dp else 12.dp,
                    vertical = if (embedded) 0.dp else 10.dp,
                ),
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
                colors =
                ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.secondary,
                    contentColor = MaterialTheme.colorScheme.onSecondary,
                ),
            )
        }
    }
}

@Composable
private fun PhotoSecondaryActionsRow(
    dateFilter: GalleryDateFilter,
    isEditing: Boolean,
    canEditPhoto: Boolean,
    canUndo: Boolean,
    isSavingEdit: Boolean,
    onCrop: () -> Unit,
    onRotate: () -> Unit,
    onShare: () -> Unit,
    onUndo: () -> Unit,
    modifier: Modifier = Modifier,
    compact: Boolean = false,
) {
    Row(
        modifier =
        modifier
            .fillMaxWidth()
            .padding(
                start = if (compact) 0.dp else 16.dp,
                end = if (compact) 0.dp else 4.dp,
                top = 0.dp,
                bottom = if (compact) 0.dp else 4.dp,
            ),
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
            AutoFitText(
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
                maxLines = if (compact) 1 else 2,
            )
        } else {
            Spacer(modifier = Modifier.weight(1f))
        }
        if (canEditPhoto && !isEditing) {
            IconButton(
                onClick = onCrop,
                enabled = !isSavingEdit,
            ) {
                Icon(
                    imageVector = Icons.Filled.Crop,
                    contentDescription =
                    stringResource(R.string.gallery_cleaner_action_crop),
                )
            }
            IconButton(
                onClick = onRotate,
                enabled = !isSavingEdit,
            ) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.RotateRight,
                    contentDescription =
                    stringResource(R.string.gallery_cleaner_action_rotate),
                )
            }
            IconButton(onClick = onShare) {
                Icon(
                    imageVector = Icons.Filled.Share,
                    contentDescription =
                    stringResource(R.string.gallery_cleaner_share),
                )
            }
        }
        if (!isEditing && canUndo) {
            IconButton(onClick = onUndo) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.Undo,
                    contentDescription =
                    stringResource(R.string.gallery_cleaner_undo_delete),
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
        title = { AutoFitText(text = stringResource(R.string.gallery_cleaner_intro_title), maxLines = 2) },
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
                AutoFitText(text = stringResource(R.string.gallery_cleaner_intro_ok), maxLines = 2)
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
        title = { AutoFitText(text = stringResource(R.string.gallery_cleaner_manage_media_title), maxLines = 2) },
        text = {
            Text(
                text = stringResource(R.string.gallery_cleaner_manage_media_message),
                modifier = Modifier.dialogScrollable(),
            )
        },
        confirmButton = {
            TextButton(onClick = onOpenSettings) {
                AutoFitText(
                    text = stringResource(R.string.gallery_cleaner_manage_media_open),
                    maxLines = 2,
                )
            }
        },
        dismissButton = {
            TextButton(onClick = onSkip) {
                AutoFitText(
                    text = stringResource(R.string.gallery_cleaner_manage_media_skip),
                    maxLines = 2,
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
            AutoFitText(
                text = stringResource(R.string.gallery_cleaner_permission_grant),
                maxLines = 2,
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
    showMetadata: Boolean = true,
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
                    color = MaterialTheme.colorScheme.secondary,
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
                    color = MaterialTheme.colorScheme.secondary,
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

        if (showMetadata) {
            PhotoMetaInfo(
                photo = photo,
                compact = isCompactHeight(),
                modifier =
                Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.background),
            )
        }
    }
}

@Composable
private fun PhotoMetaInfo(
    photo: CameraPhoto,
    compact: Boolean,
    modifier: Modifier = Modifier,
    endAligned: Boolean = false,
) {
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
    val textAlign = if (endAligned) TextAlign.End else TextAlign.Start
    Column(
        modifier =
        modifier.padding(
            horizontal = if (endAligned) 0.dp else 16.dp,
            vertical = if (compact) 6.dp else 10.dp,
        ),
        horizontalAlignment = if (endAligned) Alignment.End else Alignment.Start,
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        if (compact) {
            AutoFitText(
                text = "$dateLabel · $sizeLabel",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 1,
                textAlign = textAlign,
                modifier = if (endAligned) Modifier.fillMaxWidth() else Modifier,
            )
        } else {
            AutoFitText(
                text = nameLabel,
                style = MaterialTheme.typography.titleSmall,
                maxLines = 1,
                textAlign = textAlign,
                modifier = if (endAligned) Modifier.fillMaxWidth() else Modifier,
            )
            AutoFitText(
                text = dateLabel,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 1,
                textAlign = textAlign,
                modifier = if (endAligned) Modifier.fillMaxWidth() else Modifier,
            )
            AutoFitText(
                text = sizeLabel,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 1,
                textAlign = textAlign,
                modifier = if (endAligned) Modifier.fillMaxWidth() else Modifier,
            )
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
