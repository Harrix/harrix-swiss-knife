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
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Done
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.MenuAnchorType
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
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
import java.text.DateFormatSymbols
import java.util.Calendar
import kotlin.math.abs
import kotlin.math.hypot
import kotlin.math.roundToInt
import kotlin.random.Random
import kotlinx.coroutines.launch

private val TrashHintColor = Color(0xFFE53935)
private val KeepHintColor = Color(0xFF43A047)
private val KeepButtonColor = Color(0xFF9E9E9E)
private const val EarliestFilterYear = 2008

/** Calendar month in local timezone; [month] is 1–12. */
private data class YearMonthPoint(
    val year: Int,
    val month: Int,
) {
    val ordinal: Int get() = year * 12 + month
}

private data class PhotoDateRange(
    val from: YearMonthPoint,
    val to: YearMonthPoint,
) {
    fun contains(epochSec: Long): Boolean {
        val calendar =
            Calendar.getInstance().apply {
                timeInMillis = epochSec * 1000L
            }
        val point =
            YearMonthPoint(
                year = calendar.get(Calendar.YEAR),
                month = calendar.get(Calendar.MONTH) + 1,
            )
        return point.ordinal in from.ordinal..to.ordinal
    }
}

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
    var menuExpanded by remember { mutableStateOf(false) }
    var showDateRangePicker by remember { mutableStateOf(false) }
    var dateRangeFilter by remember { mutableStateOf<PhotoDateRange?>(null) }

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

    fun applyDateFilter(photos: List<CameraPhoto>): List<CameraPhoto> {
        val range = dateRangeFilter ?: return photos
        return photos.filter { photo -> range.contains(photo.dateAddedEpochSec) }
    }

    fun reloadPhotos() {
        isLoading = true
        statusMessage = null
        val photos = applyDateFilter(repository.loadCameraPhotos())
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

    if (showDateRangePicker) {
        GalleryDateRangeDialog(
            initialRange = dateRangeFilter,
            onDismiss = { showDateRangePicker = false },
            onApply = { range ->
                dateRangeFilter = range
                showDateRangePicker = false
                if (hasPermission && !showIntro) {
                    reloadPhotos()
                }
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
                            modifier = Modifier.padding(end = 4.dp),
                        )
                    }
                    Box {
                        IconButton(onClick = { menuExpanded = true }) {
                            Icon(
                                imageVector = Icons.Filled.MoreVert,
                                contentDescription = stringResource(R.string.gallery_cleaner_menu),
                            )
                        }
                        DropdownMenu(
                            expanded = menuExpanded,
                            onDismissRequest = { menuExpanded = false },
                        ) {
                            DropdownMenuItem(
                                text = {
                                    Text(stringResource(R.string.gallery_cleaner_date_range))
                                },
                                onClick = {
                                    menuExpanded = false
                                    showDateRangePicker = true
                                },
                            )
                            if (dateRangeFilter != null) {
                                DropdownMenuItem(
                                    text = {
                                        Text(
                                            stringResource(
                                                R.string.gallery_cleaner_clear_date_range,
                                            ),
                                        )
                                    },
                                    onClick = {
                                        menuExpanded = false
                                        dateRangeFilter = null
                                        if (hasPermission && !showIntro) {
                                            reloadPhotos()
                                        }
                                    },
                                )
                            }
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
            if (hasPermission && currentPhoto != null) {
                val photo = currentPhoto!!
                ReviewActionBar(
                    onDelete = {
                        statusMessage = null
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
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
                    onKeep = { advanceAfterReview(photo) },
                )
            }
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
                        text =
                            stringResource(
                                if (dateRangeFilter != null) {
                                    R.string.gallery_cleaner_empty_filtered
                                } else {
                                    R.string.gallery_cleaner_empty
                                },
                            ),
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
                        onSwipeRight = { advanceAfterReview(photo) },
                        modifier = Modifier.fillMaxSize(),
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun GalleryDateRangeDialog(
    initialRange: PhotoDateRange?,
    onDismiss: () -> Unit,
    onApply: (PhotoDateRange) -> Unit,
) {
    val now = remember { Calendar.getInstance() }
    val currentYear = now.get(Calendar.YEAR)
    val currentMonth = now.get(Calendar.MONTH) + 1
    val years = remember(currentYear) { (EarliestFilterYear..currentYear).toList().reversed() }
    val monthLabels =
        remember {
            DateFormatSymbols.getInstance().months.take(12)
        }

    var fromYear by remember {
        mutableIntStateOf(initialRange?.from?.year ?: currentYear)
    }
    var fromMonth by remember {
        mutableIntStateOf(initialRange?.from?.month ?: 1)
    }
    var toYear by remember {
        mutableIntStateOf(initialRange?.to?.year ?: currentYear)
    }
    var toMonth by remember {
        mutableIntStateOf(initialRange?.to?.month ?: currentMonth)
    }

    val from = YearMonthPoint(fromYear, fromMonth)
    val to = YearMonthPoint(toYear, toMonth)
    val rangeValid = from.ordinal <= to.ordinal

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.gallery_cleaner_date_range_title)) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                YearMonthRow(
                    label = stringResource(R.string.gallery_cleaner_date_range_from),
                    year = fromYear,
                    month = fromMonth,
                    years = years,
                    monthLabels = monthLabels,
                    onYearChange = { fromYear = it },
                    onMonthChange = { fromMonth = it },
                )
                YearMonthRow(
                    label = stringResource(R.string.gallery_cleaner_date_range_to),
                    year = toYear,
                    month = toMonth,
                    years = years,
                    monthLabels = monthLabels,
                    onYearChange = { toYear = it },
                    onMonthChange = { toMonth = it },
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onApply(PhotoDateRange(from = from, to = to)) },
                enabled = rangeValid,
            ) {
                Text(stringResource(R.string.gallery_cleaner_date_range_apply))
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.gallery_cleaner_date_range_cancel))
            }
        },
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun YearMonthRow(
    label: String,
    year: Int,
    month: Int,
    years: List<Int>,
    monthLabels: List<String>,
    onYearChange: (Int) -> Unit,
    onMonthChange: (Int) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelLarge,
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            SimpleDropdownField(
                value = year.toString(),
                options = years.map { it.toString() },
                onOptionSelected = { index -> onYearChange(years[index]) },
                modifier = Modifier.weight(1f),
            )
            SimpleDropdownField(
                value = monthLabels[month - 1],
                options = monthLabels,
                onOptionSelected = { index -> onMonthChange(index + 1) },
                modifier = Modifier.weight(1.2f),
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SimpleDropdownField(
    value: String,
    options: List<String>,
    onOptionSelected: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    var expanded by remember { mutableStateOf(false) }
    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = it },
        modifier = modifier,
    ) {
        OutlinedTextField(
            value = value,
            onValueChange = {},
            readOnly = true,
            singleLine = true,
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier =
                Modifier
                    .menuAnchor(MenuAnchorType.PrimaryNotEditable)
                    .fillMaxWidth(),
        )
        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false },
        ) {
            options.forEachIndexed { index, option ->
                DropdownMenuItem(
                    text = { Text(option) },
                    onClick = {
                        onOptionSelected(index)
                        expanded = false
                    },
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
) {
    Row(
        modifier =
            modifier
                .fillMaxWidth()
                .background(ContentSurface)
                .windowInsetsPadding(WindowInsets.navigationBars)
                .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Button(
            onClick = onDelete,
            modifier = Modifier.weight(1f),
            colors =
                ButtonDefaults.buttonColors(
                    containerColor = TrashHintColor,
                    contentColor = Color.White,
                ),
        ) {
            Icon(
                imageVector = Icons.Filled.Delete,
                contentDescription = null,
                modifier = Modifier.size(18.dp),
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(stringResource(R.string.gallery_cleaner_action_delete))
        }
        Button(
            onClick = onKeep,
            modifier = Modifier.weight(1f),
            colors =
                ButtonDefaults.buttonColors(
                    containerColor = KeepButtonColor,
                    contentColor = Color.White,
                ),
        ) {
            Icon(
                imageVector = Icons.Filled.Done,
                contentDescription = null,
                modifier = Modifier.size(18.dp),
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(stringResource(R.string.gallery_cleaner_action_keep))
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
internal fun ManageMediaPromptDialog(
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
    val offsetY = remember(resetKey) { Animatable(0f) }
    var dragOffset by remember(resetKey) { mutableStateOf(Offset.Zero) }
    val dismissThreshold = with(density) { 96.dp.toPx() }
    val exitDistance = with(density) { 480.dp.toPx() }

    LaunchedEffect(resetKey) {
        offsetX.snapTo(0f)
        offsetY.snapTo(0f)
        dragOffset = Offset.Zero
    }

    val displayOffset =
        if (dragOffset != Offset.Zero) {
            dragOffset
        } else {
            Offset(offsetX.value, offsetY.value)
        }
    val horizontalProgress = (displayOffset.x / dismissThreshold).coerceIn(-1.5f, 1.5f)
    val upwardProgress = (-displayOffset.y / dismissThreshold).coerceIn(0f, 1.5f)
    val travel = hypot(displayOffset.x.toDouble(), displayOffset.y.toDouble()).toFloat()

    Box(
        modifier =
            modifier
                .fillMaxSize()
                .padding(16.dp),
        contentAlignment = Alignment.Center,
    ) {
        if (horizontalProgress < -0.15f && abs(displayOffset.x) >= abs(displayOffset.y)) {
            SwipeHint(
                icon = Icons.Filled.Delete,
                label = stringResource(R.string.gallery_cleaner_swipe_left_hint),
                color = TrashHintColor,
                alpha = (-horizontalProgress).coerceIn(0f, 1f),
                modifier = Modifier.align(Alignment.CenterEnd).padding(end = 24.dp),
            )
        }
        if (horizontalProgress > 0.15f && abs(displayOffset.x) >= abs(displayOffset.y)) {
            SwipeHint(
                icon = Icons.Filled.Done,
                label = stringResource(R.string.gallery_cleaner_swipe_right_hint),
                color = KeepHintColor,
                alpha = horizontalProgress.coerceIn(0f, 1f),
                modifier = Modifier.align(Alignment.CenterStart).padding(start = 24.dp),
            )
        }
        if (upwardProgress > 0.15f && abs(displayOffset.y) > abs(displayOffset.x)) {
            SwipeHint(
                icon = Icons.Filled.KeyboardArrowUp,
                label = stringResource(R.string.gallery_cleaner_swipe_up_hint),
                color = KeepHintColor,
                alpha = upwardProgress.coerceIn(0f, 1f),
                modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 24.dp),
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
                        rotationZ = displayOffset.x / 40f
                        alpha = 1f - (travel / (exitDistance * 1.2f)).coerceIn(0f, 0.35f)
                    }
                    .offset {
                        IntOffset(displayOffset.x.roundToInt(), displayOffset.y.roundToInt())
                    }
                    .clip(RoundedCornerShape(12.dp))
                    .background(ContentSurface)
                    .pointerInput(resetKey, photo.id) {
                        detectDragGestures(
                            onDragEnd = {
                                val current = dragOffset
                                dragOffset = Offset.Zero
                                scope.launch {
                                    offsetX.snapTo(current.x)
                                    offsetY.snapTo(current.y)
                                    val predominatelyVertical = abs(current.y) > abs(current.x)
                                    when {
                                        predominatelyVertical && current.y <= -dismissThreshold -> {
                                            offsetY.animateTo(-exitDistance, tween(180))
                                            onSwipeRight()
                                        }
                                        !predominatelyVertical && current.x <= -dismissThreshold -> {
                                            offsetX.animateTo(-exitDistance, tween(180))
                                            onSwipeLeft()
                                        }
                                        !predominatelyVertical && current.x >= dismissThreshold -> {
                                            offsetX.animateTo(exitDistance, tween(180))
                                            onSwipeRight()
                                        }
                                        else -> {
                                            offsetX.animateTo(0f, tween(180))
                                            offsetY.animateTo(0f, tween(180))
                                        }
                                    }
                                }
                            },
                            onDragCancel = {
                                val current = dragOffset
                                dragOffset = Offset.Zero
                                scope.launch {
                                    offsetX.snapTo(current.x)
                                    offsetY.snapTo(current.y)
                                    offsetX.animateTo(0f, tween(180))
                                    offsetY.animateTo(0f, tween(180))
                                }
                            },
                            onDrag = { change, dragAmount ->
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
