package dev.harrix.hsk.ui.settings

import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Palette
import androidx.compose.material.icons.filled.PhotoLibrary
import androidx.compose.material.icons.filled.Security
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.ListItemDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.MenuAnchorType
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.CameraGalleryRepository
import dev.harrix.hsk.gallery.GalleryCleanerPreferences
import dev.harrix.hsk.gallery.GalleryDateFilter
import dev.harrix.hsk.gallery.GalleryPermissions
import dev.harrix.hsk.gallery.GalleryReviewOrder
import dev.harrix.hsk.gallery.MediaFolderPaths
import dev.harrix.hsk.ui.adaptiveContentWidth
import dev.harrix.hsk.ui.gallery.GalleryDateFilterSettingsContent
import dev.harrix.hsk.ui.isCompactWidth
import dev.harrix.hsk.ui.theme.AppLanguage
import dev.harrix.hsk.ui.theme.ThemeMode
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.DateFormat
import java.util.Date

enum class SettingsSection {
    All,
    GalleryCleaner,
    VideoCleaner,
}

private enum class HskSettingsPage {
    Hub,
    Appearance,
    Gallery,
    Permissions,
}

private data class GalleryFolderStats(
    val totalCount: Int,
    val totalBytes: Long,
    val reviewedHistoryCount: Int,
    val reviewedInFolderCount: Int,
    val unreviewedCount: Int,
    val filteredCount: Int?,
    val filteredBytes: Long?,
)

private sealed interface GalleryStatsDialogState {
    data object Loading : GalleryStatsDialogState

    data object NoPermission : GalleryStatsDialogState

    data class Ready(
        val stats: GalleryFolderStats,
    ) : GalleryStatsDialogState
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    section: SettingsSection,
    themeMode: ThemeMode,
    onThemeModeChange: (ThemeMode) -> Unit,
    appLanguage: AppLanguage,
    onAppLanguageChange: (AppLanguage) -> Unit,
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
    onOpenAllSettings: (() -> Unit)? = null,
    currentShootDayEpochMs: Long? = null,
) {
    var page by rememberSaveable(section) {
        mutableStateOf(
            when (section) {
                SettingsSection.All -> HskSettingsPage.Hub
                SettingsSection.GalleryCleaner -> HskSettingsPage.Gallery
                SettingsSection.VideoCleaner -> HskSettingsPage.Hub
            },
        )
    }

    val pageTitle =
        when (page) {
            HskSettingsPage.Hub -> stringResource(R.string.settings_title)
            HskSettingsPage.Appearance -> stringResource(R.string.settings_appearance_title)
            HskSettingsPage.Gallery -> stringResource(R.string.settings_gallery_cleaner_title)
            HskSettingsPage.Permissions -> stringResource(R.string.settings_permissions_title)
        }

    fun goBack() {
        if (page == HskSettingsPage.Hub) {
            onClose()
        } else {
            page = HskSettingsPage.Hub
        }
    }

    BackHandler(onBack = { goBack() })

    Scaffold(
        modifier = modifier,
        contentWindowInsets = WindowInsets.safeDrawing,
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = pageTitle,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                },
                navigationIcon = {
                    IconButton(onClick = { goBack() }) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.settings_back),
                        )
                    }
                },
            )
        },
    ) { innerPadding ->
        when (page) {
            HskSettingsPage.Hub -> {
                Column(
                    modifier =
                    Modifier
                        .padding(innerPadding)
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .adaptiveContentWidth(),
                ) {
                    SettingsHubRow(
                        title = stringResource(R.string.settings_appearance_title),
                        summary = stringResource(R.string.settings_appearance_summary),
                        icon = Icons.Filled.Palette,
                        onClick = { page = HskSettingsPage.Appearance },
                    )
                    HorizontalDivider()
                    SettingsCategoryHeader(text = stringResource(R.string.settings_category_tools))
                    SettingsHubRow(
                        title = stringResource(R.string.settings_gallery_cleaner_title),
                        summary = stringResource(R.string.settings_gallery_cleaner_summary),
                        icon = Icons.Filled.PhotoLibrary,
                        onClick = { page = HskSettingsPage.Gallery },
                    )
                    HorizontalDivider()
                    SettingsCategoryHeader(text = stringResource(R.string.settings_category_main))
                    SettingsHubRow(
                        title = stringResource(R.string.settings_permissions_title),
                        summary = stringResource(R.string.settings_permissions_summary),
                        icon = Icons.Filled.Security,
                        onClick = { page = HskSettingsPage.Permissions },
                    )
                }
            }

            HskSettingsPage.Appearance -> {
                SettingsDetailPane(innerPadding = innerPadding) {
                    AppearanceSettingsSection(
                        themeMode = themeMode,
                        onThemeModeChange = onThemeModeChange,
                        appLanguage = appLanguage,
                        onAppLanguageChange = onAppLanguageChange,
                    )
                }
            }

            HskSettingsPage.Gallery -> {
                SettingsDetailPane(innerPadding = innerPadding) {
                    GalleryCleanerSettingsSection(
                        currentShootDayEpochMs = currentShootDayEpochMs,
                    )
                    if (onOpenAllSettings != null && section != SettingsSection.All) {
                        TextButton(onClick = onOpenAllSettings) {
                            Text(stringResource(R.string.settings_open_all))
                        }
                    }
                }
            }

            HskSettingsPage.Permissions -> {
                SettingsDetailPane(innerPadding = innerPadding) {
                    PermissionsSettingsSection()
                }
            }
        }
    }
}

@Composable
private fun SettingsDetailPane(
    innerPadding: PaddingValues,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(
        modifier =
        Modifier
            .padding(innerPadding)
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 8.dp)
            .adaptiveContentWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
        content = content,
    )
}

@Composable
private fun SettingsCategoryHeader(text: String) {
    Text(
        text = text,
        style = MaterialTheme.typography.labelLarge,
        color = MaterialTheme.colorScheme.primary,
        modifier =
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 12.dp),
    )
}

@Composable
private fun SettingsHubRow(
    title: String,
    summary: String,
    icon: ImageVector,
    onClick: () -> Unit,
) {
    ListItem(
        headlineContent = {
            Text(
                text = title,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        },
        supportingContent = {
            Text(
                text = summary,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
        },
        leadingContent = {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        },
        colors =
        ListItemDefaults.colors(
            containerColor = MaterialTheme.colorScheme.surface,
        ),
        modifier =
        Modifier
            .fillMaxWidth()
            .clickable(
                role = Role.Button,
                onClick = onClick,
            ),
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AppearanceSettingsSection(
    themeMode: ThemeMode,
    onThemeModeChange: (ThemeMode) -> Unit,
    appLanguage: AppLanguage,
    onAppLanguageChange: (AppLanguage) -> Unit,
    modifier: Modifier = Modifier,
) {
    val options =
        listOf(
            ThemeMode.System to R.string.settings_theme_system,
            ThemeMode.Light to R.string.settings_theme_light,
            ThemeMode.Dark to R.string.settings_theme_dark,
        )
    var languageMenuExpanded by remember { mutableStateOf(false) }
    val systemLanguageLabel = stringResource(R.string.settings_language_system)
    val languageLabel =
        if (appLanguage == AppLanguage.System) {
            systemLanguageLabel
        } else {
            appLanguage.nativeLabel
        }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text = stringResource(R.string.settings_language_title),
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        ExposedDropdownMenuBox(
            expanded = languageMenuExpanded,
            onExpandedChange = { languageMenuExpanded = it },
            modifier = Modifier.fillMaxWidth(),
        ) {
            OutlinedTextField(
                value = languageLabel,
                onValueChange = {},
                readOnly = true,
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = languageMenuExpanded) },
                modifier =
                Modifier
                    .menuAnchor(MenuAnchorType.PrimaryNotEditable)
                    .fillMaxWidth(),
            )
            ExposedDropdownMenu(
                expanded = languageMenuExpanded,
                onDismissRequest = { languageMenuExpanded = false },
            ) {
                AppLanguage.entries.forEach { language ->
                    val optionLabel =
                        if (language == AppLanguage.System) {
                            systemLanguageLabel
                        } else {
                            language.nativeLabel
                        }
                    DropdownMenuItem(
                        text = {
                            Text(
                                text = optionLabel,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                            )
                        },
                        onClick = {
                            languageMenuExpanded = false
                            if (language != appLanguage) {
                                onAppLanguageChange(language)
                            }
                        },
                    )
                }
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = stringResource(R.string.settings_theme_title),
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        SingleChoiceSegmentedButtonRow(modifier = Modifier.fillMaxWidth()) {
            options.forEachIndexed { index, (mode, labelRes) ->
                SegmentedButton(
                    selected = themeMode == mode,
                    onClick = { onThemeModeChange(mode) },
                    shape =
                    SegmentedButtonDefaults.itemShape(
                        index = index,
                        count = options.size,
                    ),
                ) {
                    Text(
                        text = stringResource(labelRes),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                }
            }
        }
    }
}

@Composable
private fun PermissionsSettingsSection(modifier: Modifier = Modifier) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    var hasPhotosPermission by remember {
        mutableStateOf(GalleryPermissions.hasPhotosPermission(context))
    }
    var hasVideosPermission by remember {
        mutableStateOf(GalleryPermissions.hasVideosPermission(context))
    }
    var canManageMedia by remember {
        mutableStateOf(GalleryPermissions.canManageMedia(context))
    }
    val preferences = remember { GalleryCleanerPreferences(context.applicationContext) }
    var manageMediaTipEnabled by remember {
        mutableStateOf(preferences.shouldShowManageMediaPrompt())
    }
    var manageMediaTipMessage by remember { mutableStateOf<String?>(null) }

    fun refreshPermissionStatus() {
        hasPhotosPermission = GalleryPermissions.hasPhotosPermission(context)
        hasVideosPermission = GalleryPermissions.hasVideosPermission(context)
        canManageMedia = GalleryPermissions.canManageMedia(context)
    }

    DisposableEffect(lifecycleOwner) {
        val observer =
            LifecycleEventObserver { _, event ->
                if (event == Lifecycle.Event.ON_RESUME) {
                    refreshPermissionStatus()
                }
            }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    val photosStatusRes =
        if (hasPhotosPermission) {
            R.string.settings_photos_access_granted
        } else {
            R.string.settings_photos_access_denied
        }
    val videosStatusRes =
        if (hasVideosPermission) {
            R.string.settings_videos_access_granted
        } else {
            R.string.settings_videos_access_denied
        }
    val manageMediaStatusRes =
        when {
            !GalleryPermissions.isManageMediaAvailable() ->
                R.string.settings_manage_media_unavailable

            canManageMedia -> R.string.settings_manage_media_granted

            else -> R.string.settings_manage_media_denied
        }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text = stringResource(photosStatusRes),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = stringResource(videosStatusRes),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        SettingsFullWidthOutlinedButton(
            onClick = {
                context.startActivity(GalleryPermissions.appDetailsSettingsIntent(context))
            },
            label = stringResource(R.string.settings_open_app_permissions),
        )
        Text(
            text = stringResource(manageMediaStatusRes),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = stringResource(R.string.settings_manage_media_hint),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        SettingsFullWidthOutlinedButton(
            onClick = {
                GalleryPermissions.manageMediaSettingsIntent(context)?.let { intent ->
                    context.startActivity(intent)
                }
            },
            enabled = GalleryPermissions.isManageMediaAvailable(),
            label = stringResource(R.string.settings_open_manage_media),
        )
        SettingsFullWidthOutlinedButton(
            onClick = {
                preferences.setShowManageMediaPrompt(true)
                manageMediaTipEnabled = true
                manageMediaTipMessage =
                    context.getString(R.string.settings_show_manage_media_tip_done)
            },
            enabled = !manageMediaTipEnabled,
            label = stringResource(R.string.settings_show_manage_media_tip),
        )
        manageMediaTipMessage?.let { message ->
            Text(
                text = message,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun GalleryCleanerSettingsSection(
    modifier: Modifier = Modifier,
    currentShootDayEpochMs: Long? = null,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val preferences = remember { GalleryCleanerPreferences(context.applicationContext) }
    val repository = remember { CameraGalleryRepository(context.applicationContext) }
    var filter by remember { mutableStateOf(preferences.loadDateFilter()) }
    var unreviewedOnlyMode by remember {
        mutableStateOf(preferences.isUnreviewedOnlyModeEnabled())
    }
    var reviewOrder by remember { mutableStateOf(preferences.getReviewOrder()) }
    var imagesRelativePath by remember { mutableStateOf(preferences.getImagesRelativePath()) }
    var folderMessage by remember { mutableStateOf<String?>(null) }
    var reviewedCount by remember { mutableIntStateOf(preferences.reviewedPhotoCount()) }
    var lifetimeDeletedCount by remember { mutableIntStateOf(preferences.totalDeletedCount()) }
    var lifetimeFreedBytes by remember { mutableLongStateOf(preferences.totalFreedBytes()) }
    var clearMessage by remember { mutableStateOf<String?>(null) }
    var resetStatsMessage by remember { mutableStateOf<String?>(null) }
    var resetMessage by remember { mutableStateOf<String?>(null) }
    var introEnabled by remember { mutableStateOf(preferences.shouldShowIntro()) }
    var introMessage by remember { mutableStateOf<String?>(null) }
    var statsState by remember { mutableStateOf<GalleryStatsDialogState?>(null) }
    val shootDayLabel =
        remember(currentShootDayEpochMs) {
            currentShootDayEpochMs?.let { epochMs ->
                DateFormat
                    .getDateInstance(DateFormat.MEDIUM)
                    .format(Date(epochMs))
            }
        }
    val folderPicker =
        rememberLauncherForActivityResult(
            ActivityResultContracts.OpenDocumentTree(),
        ) { uri ->
            if (uri == null) {
                return@rememberLauncherForActivityResult
            }
            val path = MediaFolderPaths.fromTreeUri(uri)
            if (path == null) {
                folderMessage =
                    context.getString(R.string.settings_gallery_images_folder_invalid)
                return@rememberLauncherForActivityResult
            }
            preferences.setImagesRelativePath(path)
            imagesRelativePath = path
            folderMessage = null
        }

    fun persist(next: GalleryDateFilter) {
        filter = next
        preferences.saveDateFilter(next)
    }

    fun collectStatistics() {
        if (!GalleryPermissions.hasPhotosPermission(context)) {
            statsState = GalleryStatsDialogState.NoPermission
            return
        }
        statsState = GalleryStatsDialogState.Loading
        val relativePath = imagesRelativePath
        val dateFilter = filter
        val reviewedIds = preferences.getReviewedPhotoIds()
        scope.launch {
            val result =
                withContext(Dispatchers.IO) {
                    val photos = repository.loadCameraPhotos(relativePath)
                    val reviewedInFolder = photos.count { it.id in reviewedIds }
                    val filtered =
                        if (dateFilter.enabled) {
                            photos.filter { photo ->
                                dateFilter.contains(photo.dateTakenEpochMs / 1000L)
                            }
                        } else {
                            null
                        }
                    GalleryFolderStats(
                        totalCount = photos.size,
                        totalBytes = photos.sumOf { it.sizeBytes },
                        reviewedHistoryCount = reviewedIds.size,
                        reviewedInFolderCount = reviewedInFolder,
                        unreviewedCount = photos.size - reviewedInFolder,
                        filteredCount = filtered?.size,
                        filteredBytes = filtered?.sumOf { it.sizeBytes },
                    )
                }
            statsState = GalleryStatsDialogState.Ready(result)
            reviewedCount = result.reviewedHistoryCount
        }
    }

    when (val state = statsState) {
        null -> Unit

        GalleryStatsDialogState.Loading -> {
            AlertDialog(
                onDismissRequest = {},
                title = { Text(stringResource(R.string.settings_gallery_stats_title)) },
                text = {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(16.dp),
                    ) {
                        CircularProgressIndicator()
                        Text(stringResource(R.string.settings_gallery_stats_collecting))
                    }
                },
                confirmButton = {},
            )
        }

        GalleryStatsDialogState.NoPermission -> {
            AlertDialog(
                onDismissRequest = { statsState = null },
                title = { Text(stringResource(R.string.settings_gallery_stats_title)) },
                text = { Text(stringResource(R.string.settings_gallery_stats_no_permission)) },
                confirmButton = {
                    TextButton(onClick = { statsState = null }) {
                        Text(stringResource(R.string.settings_gallery_stats_ok))
                    }
                },
            )
        }

        is GalleryStatsDialogState.Ready -> {
            val stats = state.stats
            AlertDialog(
                onDismissRequest = { statsState = null },
                title = { Text(stringResource(R.string.settings_gallery_stats_title)) },
                text = {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(
                            stringResource(
                                R.string.settings_gallery_stats_total,
                                stats.totalCount,
                            ),
                        )
                        Text(
                            stringResource(
                                R.string.settings_gallery_stats_size,
                                CameraGalleryRepository.formatFileSize(stats.totalBytes),
                            ),
                        )
                        Text(
                            stringResource(
                                R.string.settings_gallery_stats_reviewed_history,
                                stats.reviewedHistoryCount,
                            ),
                        )
                        Text(
                            stringResource(
                                R.string.settings_gallery_stats_reviewed_in_folder,
                                stats.reviewedInFolderCount,
                            ),
                        )
                        Text(
                            stringResource(
                                R.string.settings_gallery_stats_unreviewed,
                                stats.unreviewedCount,
                            ),
                        )
                        if (stats.filteredCount != null && stats.filteredBytes != null) {
                            Text(
                                stringResource(
                                    R.string.settings_gallery_stats_filtered,
                                    stats.filteredCount,
                                ),
                            )
                            Text(
                                stringResource(
                                    R.string.settings_gallery_stats_filtered_size,
                                    CameraGalleryRepository.formatFileSize(stats.filteredBytes),
                                ),
                            )
                        }
                    }
                },
                confirmButton = {
                    TextButton(onClick = { statsState = null }) {
                        Text(stringResource(R.string.settings_gallery_stats_ok))
                    }
                },
            )
        }
    }

    val body: @Composable ColumnScope.() -> Unit = {
        SettingsFullWidthOutlinedButton(
            onClick = {
                preferences.setShowIntro(true)
                introEnabled = true
                introMessage = context.getString(R.string.settings_gallery_show_intro_done)
            },
            enabled = !introEnabled,
            label = stringResource(R.string.settings_gallery_show_intro),
        )
        introMessage?.let { message ->
            Text(
                text = message,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }

        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(
                text = stringResource(R.string.settings_gallery_images_folder),
                style = MaterialTheme.typography.bodyLarge,
            )
            Text(
                text = stringResource(R.string.settings_gallery_images_folder_hint),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            val folderLabel = MediaFolderPaths.displayLabel(imagesRelativePath)
            Text(
                text =
                stringResource(R.string.settings_gallery_images_folder_current, folderLabel) +
                    if (imagesRelativePath == null) {
                        stringResource(R.string.settings_gallery_images_folder_default_suffix)
                    } else {
                        ""
                    },
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
            val folderButtonPadding = PaddingValues(horizontal = 12.dp, vertical = 10.dp)
            if (isCompactWidth()) {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    OutlinedButton(
                        onClick = { folderPicker.launch(null) },
                        modifier = Modifier.fillMaxWidth(),
                        contentPadding = folderButtonPadding,
                    ) {
                        Text(
                            text = stringResource(R.string.settings_gallery_images_folder_choose),
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                    OutlinedButton(
                        onClick = {
                            preferences.resetImagesFolderToDefault()
                            imagesRelativePath = null
                            folderMessage = null
                        },
                        enabled = imagesRelativePath != null,
                        modifier = Modifier.fillMaxWidth(),
                        contentPadding = folderButtonPadding,
                    ) {
                        Text(
                            text = stringResource(R.string.settings_gallery_images_folder_restore),
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                }
            } else {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    OutlinedButton(
                        onClick = { folderPicker.launch(null) },
                        modifier = Modifier.weight(1f),
                        contentPadding = folderButtonPadding,
                    ) {
                        Text(
                            text = stringResource(R.string.settings_gallery_images_folder_choose),
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                    OutlinedButton(
                        onClick = {
                            preferences.resetImagesFolderToDefault()
                            imagesRelativePath = null
                            folderMessage = null
                        },
                        enabled = imagesRelativePath != null,
                        modifier = Modifier.weight(1f),
                        contentPadding = folderButtonPadding,
                    ) {
                        Text(
                            text = stringResource(R.string.settings_gallery_images_folder_restore),
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                }
            }
            folderMessage?.let { message ->
                Text(
                    text = message,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error,
                )
            }
        }

        HorizontalDivider(modifier = Modifier.padding(vertical = 4.dp))

        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(
                text = stringResource(R.string.settings_gallery_review_order),
                style = MaterialTheme.typography.bodyLarge,
            )
            Text(
                text = stringResource(R.string.settings_gallery_review_order_hint),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            val orderOptions =
                listOf(
                    GalleryReviewOrder.Random to R.string.settings_gallery_review_order_random,
                    GalleryReviewOrder.OldestFirst to R.string.settings_gallery_review_order_oldest,
                    GalleryReviewOrder.NewestFirst to R.string.settings_gallery_review_order_newest,
                )
            orderOptions.forEach { (order, labelRes) ->
                Row(
                    modifier =
                    Modifier
                        .fillMaxWidth()
                        .clickable {
                            reviewOrder = order
                            preferences.setReviewOrder(order)
                        },
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    RadioButton(
                        selected = reviewOrder == order,
                        onClick = {
                            reviewOrder = order
                            preferences.setReviewOrder(order)
                        },
                    )
                    Text(
                        text = stringResource(labelRes),
                        style = MaterialTheme.typography.bodyLarge,
                        modifier = Modifier.padding(start = 4.dp),
                    )
                }
            }
        }

        HorizontalDivider(modifier = Modifier.padding(vertical = 4.dp))

        SettingsSwitchRow(
            title = stringResource(R.string.settings_gallery_unreviewed_only),
            description = stringResource(R.string.settings_gallery_unreviewed_only_hint),
            checked = unreviewedOnlyMode,
            onCheckedChange = { checked ->
                unreviewedOnlyMode = checked
                preferences.setUnreviewedOnlyModeEnabled(checked)
            },
        )

        Text(
            text = stringResource(R.string.settings_gallery_reviewed_count, reviewedCount),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        SettingsFullWidthOutlinedButton(
            onClick = { collectStatistics() },
            enabled = statsState !is GalleryStatsDialogState.Loading,
            label = stringResource(R.string.settings_gallery_collect_stats),
        )
        SettingsFullWidthOutlinedButton(
            onClick = {
                val cleared = preferences.reviewedPhotoCount()
                preferences.clearReviewedPhotos()
                reviewedCount = 0
                clearMessage =
                    context.getString(R.string.settings_gallery_clear_reviewed_done, cleared)
            },
            enabled = reviewedCount > 0,
            label = stringResource(R.string.settings_gallery_clear_reviewed),
        )
        clearMessage?.let { message ->
            Text(
                text = message,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Text(
            text =
            stringResource(
                R.string.gallery_cleaner_stats_deleted,
                lifetimeDeletedCount,
            ),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text =
            stringResource(
                R.string.gallery_cleaner_stats_freed,
                CameraGalleryRepository.formatFileSize(lifetimeFreedBytes),
            ),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = stringResource(R.string.settings_gallery_reset_stats_hint),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        SettingsFullWidthOutlinedButton(
            onClick = {
                preferences.clearLifetimeDeleteStats()
                lifetimeDeletedCount = 0
                lifetimeFreedBytes = 0L
                resetStatsMessage = context.getString(R.string.settings_gallery_reset_stats_done)
            },
            enabled = lifetimeDeletedCount > 0 || lifetimeFreedBytes > 0L,
            label = stringResource(R.string.settings_gallery_reset_stats),
        )
        resetStatsMessage?.let { message ->
            Text(
                text = message,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }

        HorizontalDivider(modifier = Modifier.padding(vertical = 4.dp))

        GalleryDateFilterSettingsContent(
            filter = filter,
            onFilterChange = { persist(it) },
            shootDayEpochMs = currentShootDayEpochMs,
            shootDayLabel = shootDayLabel,
        )

        HorizontalDivider(modifier = Modifier.padding(vertical = 4.dp))

        Text(
            text = stringResource(R.string.settings_gallery_reset_hint),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        SettingsFullWidthOutlinedButton(
            onClick = {
                preferences.resetSettingsToDefaults()
                filter = preferences.loadDateFilter()
                unreviewedOnlyMode = preferences.isUnreviewedOnlyModeEnabled()
                reviewOrder = preferences.getReviewOrder()
                imagesRelativePath = preferences.getImagesRelativePath()
                folderMessage = null
                introEnabled = preferences.shouldShowIntro()
                introMessage = null
                clearMessage = null
                resetStatsMessage = null
                resetMessage = context.getString(R.string.settings_gallery_reset_done)
            },
            label = stringResource(R.string.settings_gallery_reset),
        )
        resetMessage?.let { message ->
            Text(
                text = message,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
        content = body,
    )
}

@Composable
private fun SettingsFullWidthOutlinedButton(
    onClick: () -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    OutlinedButton(
        onClick = onClick,
        enabled = enabled,
        modifier = modifier.fillMaxWidth(),
        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 10.dp),
    ) {
        Text(
            text = label,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
            textAlign = TextAlign.Center,
        )
    }
}

@Composable
private fun SettingsSwitchRow(
    title: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
    description: String? = null,
) {
    ListItem(
        headlineContent = {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyLarge,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
        },
        supportingContent =
        description?.let {
            {
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 4,
                    overflow = TextOverflow.Ellipsis,
                )
            }
        },
        trailingContent = {
            Switch(
                checked = checked,
                onCheckedChange = onCheckedChange,
            )
        },
        colors =
        ListItemDefaults.colors(
            containerColor = MaterialTheme.colorScheme.surface,
        ),
        modifier =
        modifier
            .fillMaxWidth()
            .clickable(
                role = Role.Switch,
                onClick = { onCheckedChange(!checked) },
            ),
    )
}
