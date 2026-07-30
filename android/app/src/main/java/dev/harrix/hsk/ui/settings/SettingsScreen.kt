package dev.harrix.hsk.ui.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Checkbox
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.MenuAnchorType
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.GalleryCleanerPreferences
import dev.harrix.hsk.gallery.GalleryDateFilter
import dev.harrix.hsk.gallery.GalleryPermissions
import dev.harrix.hsk.ui.theme.ThemeMode
import java.text.DateFormat
import java.text.DateFormatSymbols
import java.util.Calendar
import java.util.Date

enum class SettingsSection {
    All,
    GalleryCleaner,
    VideoCleaner,
}

private const val EarliestFilterYear = 2008

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    section: SettingsSection,
    themeMode: ThemeMode,
    onThemeModeChange: (ThemeMode) -> Unit,
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
    onOpenAllSettings: (() -> Unit)? = null,
    currentShootDayEpochMs: Long? = null,
) {
    val titleRes =
        when (section) {
            SettingsSection.All -> R.string.settings_title
            SettingsSection.GalleryCleaner -> R.string.settings_gallery_cleaner_title
            SettingsSection.VideoCleaner -> R.string.settings_video_cleaner_title
        }
    val background = MaterialTheme.colorScheme.background

    Scaffold(
        modifier = modifier,
        containerColor = background,
        topBar = {
            TopAppBar(
                title = { Text(stringResource(titleRes)) },
                navigationIcon = {
                    IconButton(onClick = onClose) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.settings_back),
                        )
                    }
                },
                colors =
                TopAppBarDefaults.topAppBarColors(
                    containerColor = background,
                    scrolledContainerColor = background,
                ),
            )
        },
    ) { innerPadding ->
        Column(
            modifier =
            Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            when (section) {
                SettingsSection.All -> {
                    AppearanceSettingsSection(
                        themeMode = themeMode,
                        onThemeModeChange = onThemeModeChange,
                    )
                    HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
                    GalleryCleanerSettingsSection(
                        showSectionTitle = true,
                        currentShootDayEpochMs = currentShootDayEpochMs,
                    )
                    HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
                    VideoCleanerSettingsSection(showSectionTitle = true)
                }

                SettingsSection.GalleryCleaner -> {
                    GalleryCleanerSettingsSection(
                        showSectionTitle = false,
                        currentShootDayEpochMs = currentShootDayEpochMs,
                    )
                }

                SettingsSection.VideoCleaner -> {
                    VideoCleanerSettingsSection(showSectionTitle = false)
                }
            }

            if (onOpenAllSettings != null && section != SettingsSection.All) {
                Spacer(modifier = Modifier.height(16.dp))
                HorizontalDivider()
                TextButton(
                    onClick = onOpenAllSettings,
                    modifier = Modifier.align(Alignment.Start),
                ) {
                    Text(stringResource(R.string.settings_open_all))
                }
            }
        }
    }
}

@Composable
private fun AppearanceSettingsSection(
    themeMode: ThemeMode,
    onThemeModeChange: (ThemeMode) -> Unit,
    modifier: Modifier = Modifier,
) {
    val options =
        listOf(
            ThemeMode.System to R.string.settings_theme_system,
            ThemeMode.Light to R.string.settings_theme_light,
            ThemeMode.Dark to R.string.settings_theme_dark,
        )

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text = stringResource(R.string.settings_appearance_title),
            style = MaterialTheme.typography.titleMedium,
        )
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
                    Text(stringResource(labelRes))
                }
            }
        }
    }
}

private enum class MediaPermissionKind {
    Photos,
    Videos,
}

@Composable
private fun MediaPermissionSettingsBlock(
    kind: MediaPermissionKind,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    var hasMediaPermission by remember {
        mutableStateOf(
            when (kind) {
                MediaPermissionKind.Photos -> GalleryPermissions.hasPhotosPermission(context)
                MediaPermissionKind.Videos -> GalleryPermissions.hasVideosPermission(context)
            },
        )
    }
    var canManageMedia by remember {
        mutableStateOf(GalleryPermissions.canManageMedia(context))
    }

    fun refreshPermissionStatus() {
        hasMediaPermission =
            when (kind) {
                MediaPermissionKind.Photos -> GalleryPermissions.hasPhotosPermission(context)
                MediaPermissionKind.Videos -> GalleryPermissions.hasVideosPermission(context)
            }
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

    val mediaStatusRes =
        when (kind) {
            MediaPermissionKind.Photos ->
                if (hasMediaPermission) {
                    R.string.settings_photos_access_granted
                } else {
                    R.string.settings_photos_access_denied
                }

            MediaPermissionKind.Videos ->
                if (hasMediaPermission) {
                    R.string.settings_videos_access_granted
                } else {
                    R.string.settings_videos_access_denied
                }
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
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            text = stringResource(R.string.settings_permissions_title),
            style = MaterialTheme.typography.titleSmall,
        )
        Text(
            text = stringResource(mediaStatusRes),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedButton(
            onClick = {
                context.startActivity(GalleryPermissions.appDetailsSettingsIntent(context))
            },
        ) {
            Text(stringResource(R.string.settings_open_app_permissions))
        }
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
        OutlinedButton(
            onClick = {
                GalleryPermissions.manageMediaSettingsIntent(context)?.let { intent ->
                    context.startActivity(intent)
                }
            },
            enabled = GalleryPermissions.isManageMediaAvailable(),
        ) {
            Text(stringResource(R.string.settings_open_manage_media))
        }
    }
}

@Composable
private fun GalleryCleanerSettingsSection(
    showSectionTitle: Boolean,
    modifier: Modifier = Modifier,
    currentShootDayEpochMs: Long? = null,
) {
    val context = LocalContext.current
    val preferences = remember { GalleryCleanerPreferences(context.applicationContext) }
    var filter by remember { mutableStateOf(preferences.loadDateFilter()) }
    var unreviewedOnlyMode by remember {
        mutableStateOf(preferences.isUnreviewedOnlyModeEnabled())
    }
    var reviewedCount by remember { mutableIntStateOf(preferences.reviewedPhotoCount()) }
    var clearMessage by remember { mutableStateOf<String?>(null) }
    val shootDayLabel =
        remember(currentShootDayEpochMs) {
            currentShootDayEpochMs?.let { epochMs ->
                DateFormat
                    .getDateInstance(DateFormat.MEDIUM)
                    .format(Date(epochMs))
            }
        }

    fun persist(next: GalleryDateFilter) {
        filter = next
        preferences.saveDateFilter(next)
    }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (showSectionTitle) {
            Text(
                text = stringResource(R.string.settings_gallery_cleaner_title),
                style = MaterialTheme.typography.titleMedium,
            )
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Checkbox(
                checked = unreviewedOnlyMode,
                onCheckedChange = { checked ->
                    unreviewedOnlyMode = checked
                    preferences.setUnreviewedOnlyModeEnabled(checked)
                },
            )
            Column(
                modifier =
                Modifier
                    .weight(1f)
                    .padding(start = 4.dp),
            ) {
                Text(
                    text = stringResource(R.string.settings_gallery_unreviewed_only),
                    style = MaterialTheme.typography.bodyLarge,
                )
                Text(
                    text = stringResource(R.string.settings_gallery_unreviewed_only_hint),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        Text(
            text = stringResource(R.string.settings_gallery_reviewed_count, reviewedCount),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedButton(
            onClick = {
                val cleared = preferences.reviewedPhotoCount()
                preferences.clearReviewedPhotos()
                reviewedCount = 0
                clearMessage =
                    context.getString(R.string.settings_gallery_clear_reviewed_done, cleared)
            },
            enabled = reviewedCount > 0,
        ) {
            Text(stringResource(R.string.settings_gallery_clear_reviewed))
        }
        clearMessage?.let { message ->
            Text(
                text = message,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }

        HorizontalDivider(modifier = Modifier.padding(vertical = 4.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Checkbox(
                checked = filter.enabled,
                onCheckedChange = { checked -> persist(filter.withEnabled(checked)) },
            )
            Text(
                text = stringResource(R.string.settings_gallery_date_filter_enabled),
                style = MaterialTheme.typography.bodyLarge,
                modifier =
                Modifier
                    .weight(1f)
                    .padding(start = 4.dp),
            )
        }

        GalleryDateFilterEditors(
            filter = filter,
            enabled = filter.enabled,
            onFilterChange = { persist(it) },
        )

        Text(
            text = stringResource(R.string.settings_gallery_date_presets),
            style = MaterialTheme.typography.labelLarge,
            color =
                if (filter.enabled) {
                    MaterialTheme.colorScheme.onSurfaceVariant
                } else {
                    MaterialTheme.colorScheme.onSurface.copy(alpha = 0.38f)
                },
        )
        GalleryDatePresets(
            enabled = filter.enabled,
            shootDayEpochMs = currentShootDayEpochMs,
            shootDayLabel = shootDayLabel,
            onPreset = { persist(it) },
        )

        HorizontalDivider(modifier = Modifier.padding(vertical = 4.dp))

        MediaPermissionSettingsBlock(kind = MediaPermissionKind.Photos)
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
private fun GalleryDateFilterEditors(
    filter: GalleryDateFilter,
    enabled: Boolean,
    onFilterChange: (GalleryDateFilter) -> Unit,
) {
    val now = remember { Calendar.getInstance() }
    val currentYear = now.get(Calendar.YEAR)
    val years = remember(currentYear) { (EarliestFilterYear..currentYear).toList().reversed() }
    val monthLabels = remember { DateFormatSymbols.getInstance().months.take(12) }

    var fromYear by remember(filter.startEpochSecInclusive) {
        mutableIntStateOf(filter.fromYear())
    }
    var fromMonth by remember(filter.startEpochSecInclusive) {
        mutableIntStateOf(filter.fromMonth())
    }
    var fromDay by remember(filter.startEpochSecInclusive) {
        mutableIntStateOf(filter.fromDay())
    }
    var toYear by remember(filter.endEpochSecInclusive) {
        mutableIntStateOf(filter.toYear())
    }
    var toMonth by remember(filter.endEpochSecInclusive) {
        mutableIntStateOf(filter.toMonth())
    }
    var toDay by remember(filter.endEpochSecInclusive) {
        mutableIntStateOf(filter.toDay())
    }

    fun applyDateRange() {
        onFilterChange(
            filter.withDateRange(
                fromYear = fromYear,
                fromMonth = fromMonth,
                fromDay = fromDay,
                toYear = toYear,
                toMonth = toMonth,
                toDay = toDay,
            ),
        )
    }

    fun clampDay(
        year: Int,
        month: Int,
        day: Int,
    ): Int = day.coerceIn(1, GalleryDateFilter.daysInMonth(year, month))

    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        YearMonthDayRow(
            label = stringResource(R.string.gallery_cleaner_date_range_from),
            year = fromYear,
            month = fromMonth,
            day = fromDay,
            years = years,
            monthLabels = monthLabels,
            enabled = enabled,
            onYearChange = { year ->
                fromYear = year
                fromDay = clampDay(year, fromMonth, fromDay)
                applyDateRange()
            },
            onMonthChange = { month ->
                fromMonth = month
                fromDay = clampDay(fromYear, month, fromDay)
                applyDateRange()
            },
            onDayChange = { day ->
                fromDay = day
                applyDateRange()
            },
        )
        YearMonthDayRow(
            label = stringResource(R.string.gallery_cleaner_date_range_to),
            year = toYear,
            month = toMonth,
            day = toDay,
            years = years,
            monthLabels = monthLabels,
            enabled = enabled,
            onYearChange = { year ->
                toYear = year
                toDay = clampDay(year, toMonth, toDay)
                applyDateRange()
            },
            onMonthChange = { month ->
                toMonth = month
                toDay = clampDay(toYear, month, toDay)
                applyDateRange()
            },
            onDayChange = { day ->
                toDay = day
                applyDateRange()
            },
        )
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun GalleryDatePresets(
    enabled: Boolean,
    onPreset: (GalleryDateFilter) -> Unit,
    shootDayEpochMs: Long? = null,
    shootDayLabel: String? = null,
) {
    val presets =
        listOf(
            R.string.settings_gallery_preset_1_day to
                { GalleryDateFilter.lastDaysIncludingToday(1) },
            R.string.settings_gallery_preset_2_days to
                { GalleryDateFilter.lastDaysIncludingToday(2) },
            R.string.settings_gallery_preset_week to
                { GalleryDateFilter.lastDaysIncludingToday(7) },
            R.string.settings_gallery_preset_1_month to
                { GalleryDateFilter.lastCalendarMonths(1) },
            R.string.settings_gallery_preset_1_year to
                { GalleryDateFilter.lastCalendarYears(1) },
        )

    FlowRow(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        if (shootDayEpochMs != null && shootDayLabel != null) {
            OutlinedButton(
                onClick = { onPreset(GalleryDateFilter.forShootDay(shootDayEpochMs)) },
                enabled = enabled,
            ) {
                Text(
                    stringResource(
                        R.string.settings_gallery_filter_shoot_day_label,
                        shootDayLabel,
                    ),
                )
            }
        }
        presets.forEach { (labelRes, factory) ->
            OutlinedButton(
                onClick = { onPreset(factory()) },
                enabled = enabled,
            ) {
                Text(stringResource(labelRes))
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun YearMonthDayRow(
    label: String,
    year: Int,
    month: Int,
    day: Int,
    years: List<Int>,
    monthLabels: List<String>,
    enabled: Boolean,
    onYearChange: (Int) -> Unit,
    onMonthChange: (Int) -> Unit,
    onDayChange: (Int) -> Unit,
) {
    val days = remember(year, month) {
        (1..GalleryDateFilter.daysInMonth(year, month)).toList()
    }
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelLarge,
            color =
                if (enabled) {
                    MaterialTheme.colorScheme.onSurface
                } else {
                    MaterialTheme.colorScheme.onSurface.copy(alpha = 0.38f)
                },
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            SimpleDropdownField(
                value = year.toString(),
                options = years.map { it.toString() },
                enabled = enabled,
                onOptionSelect = { index -> onYearChange(years[index]) },
                modifier = Modifier.weight(1.1f),
            )
            SimpleDropdownField(
                value = monthLabels[month - 1],
                options = monthLabels,
                enabled = enabled,
                onOptionSelect = { index -> onMonthChange(index + 1) },
                modifier = Modifier.weight(1.4f),
            )
            SimpleDropdownField(
                value = day.toString(),
                options = days.map { it.toString() },
                enabled = enabled,
                onOptionSelect = { index -> onDayChange(days[index]) },
                modifier = Modifier.weight(0.9f),
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SimpleDropdownField(
    value: String,
    options: List<String>,
    enabled: Boolean,
    onOptionSelect: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    var expanded by remember { mutableStateOf(false) }
    ExposedDropdownMenuBox(
        expanded = expanded && enabled,
        onExpandedChange = { if (enabled) expanded = it },
        modifier = modifier,
    ) {
        OutlinedTextField(
            value = value,
            onValueChange = {},
            readOnly = true,
            enabled = enabled,
            singleLine = true,
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier =
                Modifier
                    .menuAnchor(MenuAnchorType.PrimaryNotEditable, enabled = enabled)
                    .fillMaxWidth(),
        )
        ExposedDropdownMenu(
            expanded = expanded && enabled,
            onDismissRequest = { expanded = false },
        ) {
            options.forEachIndexed { index, option ->
                DropdownMenuItem(
                    text = { Text(option) },
                    onClick = {
                        onOptionSelect(index)
                        expanded = false
                    },
                )
            }
        }
    }
}

@Composable
private fun VideoCleanerSettingsSection(
    showSectionTitle: Boolean,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (showSectionTitle) {
            Text(
                text = stringResource(R.string.settings_video_cleaner_title),
                style = MaterialTheme.typography.titleMedium,
            )
        }
        MediaPermissionSettingsBlock(kind = MediaPermissionKind.Videos)
    }
}
