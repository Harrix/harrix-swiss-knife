package dev.harrix.hsk.ui.gallery

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.Button
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.ListItem
import androidx.compose.material3.ListItemDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.MenuAnchorType
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import dev.harrix.hsk.R
import dev.harrix.hsk.gallery.GalleryDateFilter
import dev.harrix.hsk.ui.AutoFitText
import java.text.DateFormatSymbols
import java.util.Calendar

private const val EarliestFilterYear = 2008

/** Below this width, year/month/day stack; above, a dense single-row layout is used. */
private val DateFieldsStackBelow = 200.dp

/**
 * Date filter controls shared by Gallery Cleaner settings and the in-utility dialog.
 */
@Composable
fun GalleryDateFilterSettingsContent(
    filter: GalleryDateFilter,
    onFilterChange: (GalleryDateFilter) -> Unit,
    modifier: Modifier = Modifier,
    shootDayEpochMs: Long? = null,
    shootDayLabel: String? = null,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        DateFilterSwitchRow(
            title = stringResource(R.string.settings_gallery_date_filter_enabled),
            checked = filter.enabled,
            onCheckedChange = { checked -> onFilterChange(filter.withEnabled(checked)) },
        )

        GalleryDateFilterEditors(
            filter = filter,
            enabled = filter.enabled,
            onFilterChange = onFilterChange,
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
            filter = filter,
            enabled = filter.enabled,
            shootDayEpochMs = shootDayEpochMs,
            shootDayLabel = shootDayLabel,
            onPreset = onFilterChange,
        )
    }
}

@Composable
private fun DateFilterSwitchRow(
    title: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
) {
    ListItem(
        headlineContent = {
            AutoFitText(
                text = title,
                style = MaterialTheme.typography.bodyLarge,
                maxLines = 2,
            )
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
    // Short names fit year/month/day in one row inside AlertDialog / narrow panes.
    val monthLabels =
        remember {
            DateFormatSymbols.getInstance().shortMonths.take(12).map { it.trim().trimEnd('.') }
        }

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
    filter: GalleryDateFilter,
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
            val shootDayFilter = GalleryDateFilter.forShootDay(shootDayEpochMs)
            DatePresetButton(
                label =
                stringResource(
                    R.string.settings_gallery_filter_shoot_day_label,
                    shootDayLabel,
                ),
                selected = filter.matchesDateRange(shootDayFilter),
                enabled = enabled,
                onClick = { onPreset(shootDayFilter) },
            )
        }
        presets.forEach { (labelRes, factory) ->
            val presetFilter = factory()
            DatePresetButton(
                label = stringResource(labelRes),
                selected = filter.matchesDateRange(presetFilter),
                enabled = enabled,
                onClick = { onPreset(presetFilter) },
            )
        }
    }
}

@Composable
private fun DatePresetButton(
    label: String,
    selected: Boolean,
    enabled: Boolean,
    onClick: () -> Unit,
) {
    val padding = PaddingValues(horizontal = 12.dp, vertical = 8.dp)
    val content: @Composable () -> Unit = {
        AutoFitText(
            text = label,
            maxLines = 1,
        )
    }
    if (selected) {
        Button(
            onClick = onClick,
            enabled = enabled,
            contentPadding = padding,
            content = { content() },
        )
    } else {
        OutlinedButton(
            onClick = onClick,
            enabled = enabled,
            contentPadding = padding,
            content = { content() },
        )
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
    val days =
        remember(year, month) {
            (1..GalleryDateFilter.daysInMonth(year, month)).toList()
        }
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
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
        // Use available width (dialog is narrower than the screen), not isCompactWidth().
        BoxWithConstraints(modifier = Modifier.fillMaxWidth()) {
            val stack = maxWidth < DateFieldsStackBelow
            val dense = !stack
            if (stack) {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    SimpleDropdownField(
                        value = year.toString(),
                        options = years.map { it.toString() },
                        enabled = enabled,
                        dense = false,
                        onOptionSelect = { index -> onYearChange(years[index]) },
                        modifier = Modifier.fillMaxWidth(),
                    )
                    SimpleDropdownField(
                        value = monthLabels[month - 1],
                        options = monthLabels,
                        enabled = enabled,
                        dense = false,
                        onOptionSelect = { index -> onMonthChange(index + 1) },
                        modifier = Modifier.fillMaxWidth(),
                    )
                    SimpleDropdownField(
                        value = day.toString(),
                        options = days.map { it.toString() },
                        enabled = enabled,
                        dense = false,
                        onOptionSelect = { index -> onDayChange(days[index]) },
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            } else {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    SimpleDropdownField(
                        value = year.toString(),
                        options = years.map { it.toString() },
                        enabled = enabled,
                        dense = dense,
                        onOptionSelect = { index -> onYearChange(years[index]) },
                        modifier = Modifier.weight(1.05f),
                    )
                    SimpleDropdownField(
                        value = monthLabels[month - 1],
                        options = monthLabels,
                        enabled = enabled,
                        dense = dense,
                        onOptionSelect = { index -> onMonthChange(index + 1) },
                        modifier = Modifier.weight(1.15f),
                    )
                    SimpleDropdownField(
                        value = day.toString(),
                        options = days.map { it.toString() },
                        enabled = enabled,
                        dense = dense,
                        onOptionSelect = { index -> onDayChange(days[index]) },
                        modifier = Modifier.weight(0.8f),
                    )
                }
            }
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
    dense: Boolean = false,
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
            textStyle =
            if (dense) {
                MaterialTheme.typography.bodySmall
            } else {
                MaterialTheme.typography.bodyLarge
            },
            // Trailing chevrons eat ~48dp each; hide in dense row — field still opens the menu.
            trailingIcon =
            if (dense) {
                null
            } else {
                {
                    ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded)
                }
            },
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
                    text = {
                        AutoFitText(
                            text = option,
                            maxLines = 1,
                        )
                    },
                    onClick = {
                        onOptionSelect(index)
                        expanded = false
                    },
                )
            }
        }
    }
}
