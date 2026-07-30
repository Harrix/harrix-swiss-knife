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
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.runtime.Composable
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
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.GalleryCleanerPreferences
import dev.harrix.hsk.gallery.GalleryDateFilter
import dev.harrix.hsk.ui.theme.AppBackground
import java.text.DateFormatSymbols
import java.util.Calendar

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
    onClose: () -> Unit,
    onOpenAllSettings: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
) {
    val titleRes =
        when (section) {
            SettingsSection.All -> R.string.settings_title
            SettingsSection.GalleryCleaner -> R.string.settings_gallery_cleaner_title
            SettingsSection.VideoCleaner -> R.string.settings_video_cleaner_title
        }

    Scaffold(
        modifier = modifier,
        containerColor = AppBackground,
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
                        containerColor = AppBackground,
                        scrolledContainerColor = AppBackground,
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
                    GalleryCleanerSettingsSection(showSectionTitle = true)
                    HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
                    VideoCleanerSettingsSection(showSectionTitle = true)
                }
                SettingsSection.GalleryCleaner -> {
                    GalleryCleanerSettingsSection(showSectionTitle = false)
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
private fun GalleryCleanerSettingsSection(
    showSectionTitle: Boolean,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val preferences = remember { GalleryCleanerPreferences(context.applicationContext) }
    var filter by remember { mutableStateOf(preferences.loadDateFilter()) }

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
            onFilterChange = { persist(it) },
        )

        Text(
            text = stringResource(R.string.settings_gallery_date_presets),
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        GalleryDatePresets(onPreset = { persist(it) })
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
private fun GalleryDateFilterEditors(
    filter: GalleryDateFilter,
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
    var toYear by remember(filter.endEpochSecInclusive) {
        mutableIntStateOf(filter.toYear())
    }
    var toMonth by remember(filter.endEpochSecInclusive) {
        mutableIntStateOf(filter.toMonth())
    }

    fun applyYearMonth() {
        onFilterChange(
            filter.withYearMonthRange(
                fromYear = fromYear,
                fromMonth = fromMonth,
                toYear = toYear,
                toMonth = toMonth,
            ),
        )
    }

    YearMonthRow(
        label = stringResource(R.string.gallery_cleaner_date_range_from),
        year = fromYear,
        month = fromMonth,
        years = years,
        monthLabels = monthLabels,
        onYearChange = {
            fromYear = it
            applyYearMonth()
        },
        onMonthChange = {
            fromMonth = it
            applyYearMonth()
        },
    )
    YearMonthRow(
        label = stringResource(R.string.gallery_cleaner_date_range_to),
        year = toYear,
        month = toMonth,
        years = years,
        monthLabels = monthLabels,
        onYearChange = {
            toYear = it
            applyYearMonth()
        },
        onMonthChange = {
            toMonth = it
            applyYearMonth()
        },
    )
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun GalleryDatePresets(onPreset: (GalleryDateFilter) -> Unit) {
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
        presets.forEach { (labelRes, factory) ->
            OutlinedButton(onClick = { onPreset(factory()) }) {
                Text(stringResource(labelRes))
            }
        }
    }
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
private fun VideoCleanerSettingsSection(
    showSectionTitle: Boolean,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        if (showSectionTitle) {
            Text(
                text = stringResource(R.string.settings_video_cleaner_title),
                style = MaterialTheme.typography.titleMedium,
            )
        }
        Text(
            text = stringResource(R.string.settings_video_cleaner_empty),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}
