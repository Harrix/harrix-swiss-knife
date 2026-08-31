package dev.harrix.hsk.ui.health

import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import androidx.compose.material.icons.automirrored.filled.DirectionsWalk
import androidx.compose.material.icons.filled.FitnessCenter
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.harrix.hsk.R
import dev.harrix.hsk.health.DaySteps
import dev.harrix.hsk.health.ExerciseSessionSummary
import dev.harrix.hsk.health.ExerciseTypeCount
import dev.harrix.hsk.health.HealthConnectAvailability
import dev.harrix.hsk.health.HealthConnectReader
import dev.harrix.hsk.health.HealthConnectSnapshot
import dev.harrix.hsk.ui.AutoFitText
import dev.harrix.hsk.ui.adaptiveContentWidth
import dev.harrix.hsk.ui.theme.HskTopAppBarHeight
import dev.harrix.hsk.ui.theme.hskScaffoldContainerColor
import dev.harrix.hsk.ui.theme.hskScaffoldContentWindowInsets
import dev.harrix.hsk.ui.theme.hskTopAppBarColors
import dev.harrix.hsk.ui.theme.hskTopAppBarWindowInsets
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.format.FormatStyle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HealthConnectScreen(
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: HealthConnectViewModel = viewModel(),
) {
    val uiState = viewModel.uiState
    val permissionLauncher =
        rememberLauncherForActivityResult(viewModel.permissionContract) { granted ->
            viewModel.onPermissionsResult(granted)
        }

    BackHandler(onBack = onClose)

    Scaffold(
        modifier = modifier.fillMaxSize(),
        containerColor = hskScaffoldContainerColor(),
        contentWindowInsets = hskScaffoldContentWindowInsets(),
        topBar = {
            TopAppBar(
                windowInsets = hskTopAppBarWindowInsets(),
                colors = hskTopAppBarColors(),
                title = {
                    AutoFitText(
                        text = stringResource(R.string.health_connect_title),
                        style = MaterialTheme.typography.titleLarge,
                        maxLines = 1,
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onClose) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.health_connect_close),
                        )
                    }
                },
                actions = {
                    IconButton(
                        onClick = { viewModel.refresh() },
                        enabled = uiState !is HealthConnectUiState.Loading,
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Refresh,
                            contentDescription = stringResource(R.string.health_connect_refresh),
                        )
                    }
                },
                expandedHeight = HskTopAppBarHeight,
            )
        },
    ) { padding ->
        Column(
            modifier =
            Modifier
                .fillMaxSize()
                .padding(padding)
                .adaptiveContentWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            when (val state = uiState) {
                is HealthConnectUiState.Loading -> {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.Center,
                    ) {
                        CircularProgressIndicator()
                    }
                }

                is HealthConnectUiState.Unavailable -> {
                    UnavailableContent(availability = state.availability)
                }

                is HealthConnectUiState.NeedsPermission -> {
                    NeedsPermissionContent(
                        onRequest = {
                            permissionLauncher.launch(viewModel.requiredPermissions)
                        },
                    )
                }

                is HealthConnectUiState.Ready -> {
                    ReadyContent(
                        snapshot = state.snapshot,
                        onRequestPermissions = {
                            permissionLauncher.launch(viewModel.requiredPermissions)
                        },
                    )
                }

                is HealthConnectUiState.Error -> {
                    Text(
                        text = stringResource(R.string.health_connect_error, state.message),
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.error,
                    )
                    OutlinedButton(onClick = { viewModel.refresh() }) {
                        Text(stringResource(R.string.health_connect_retry))
                    }
                }
            }
        }
    }
}

@Composable
private fun UnavailableContent(availability: HealthConnectAvailability) {
    val message =
        when (availability) {
            HealthConnectAvailability.UpdateRequired ->
                stringResource(R.string.health_connect_install_or_update)

            else -> stringResource(R.string.health_connect_unavailable)
        }
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            text = message,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = stringResource(R.string.health_connect_samsung_sync_hint),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun NeedsPermissionContent(onRequest: () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            text = stringResource(R.string.health_connect_needs_permission),
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = stringResource(R.string.health_connect_samsung_sync_hint),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Button(onClick = onRequest) {
            Text(stringResource(R.string.health_connect_grant_access))
        }
    }
}

@Composable
private fun ReadyContent(
    snapshot: HealthConnectSnapshot,
    onRequestPermissions: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            text =
            stringResource(
                R.string.health_connect_range,
                snapshot.rangeStart.toString(),
                snapshot.rangeEnd.toString(),
            ),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text = stringResource(R.string.health_connect_samsung_sync_hint),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedButton(onClick = onRequestPermissions) {
            Text(stringResource(R.string.health_connect_grant_access))
        }

        SectionHeader(
            icon = Icons.AutoMirrored.Filled.DirectionsWalk,
            title = stringResource(R.string.health_connect_steps_section),
        )
        StepsSection(stepsByDay = snapshot.stepsByDay, total = snapshot.stepsTotal)

        SectionHeader(
            icon = Icons.Filled.FitnessCenter,
            title = stringResource(R.string.health_connect_other_workouts_section),
        )
        OtherWorkoutsSection(
            otherWorkouts = snapshot.otherWorkouts,
            exerciseTypeCounts = snapshot.exerciseTypeCounts,
        )
    }
}

@Composable
private fun SectionHeader(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Spacer(modifier = Modifier.height(4.dp))
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Icon(imageVector = icon, contentDescription = null)
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
            )
        }
        HorizontalDivider()
    }
}

@Composable
private fun StepsSection(
    stepsByDay: List<DaySteps>,
    total: Long,
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        if (stepsByDay.isEmpty() || stepsByDay.all { it.count == 0L }) {
            Text(
                text = stringResource(R.string.health_connect_steps_empty),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        } else {
            stepsByDay.forEach { day ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Text(
                        text = day.date.toString(),
                        style = MaterialTheme.typography.bodyLarge,
                    )
                    Text(
                        text =
                        stringResource(
                            R.string.health_connect_steps_value,
                            day.count,
                        ),
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium,
                    )
                }
            }
        }
        Text(
            text = stringResource(R.string.health_connect_steps_total, total),
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
        )
    }
}

@Composable
private fun OtherWorkoutsSection(
    otherWorkouts: List<ExerciseSessionSummary>,
    exerciseTypeCounts: List<ExerciseTypeCount>,
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        if (otherWorkouts.isEmpty()) {
            Text(
                text = stringResource(R.string.health_connect_other_workouts_empty),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            if (exerciseTypeCounts.isNotEmpty()) {
                Text(
                    text = stringResource(R.string.health_connect_exercise_types_hint),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                exerciseTypeCounts.forEach { entry ->
                    Text(
                        text =
                        stringResource(
                            R.string.health_connect_exercise_type_row,
                            entry.exerciseType,
                            entry.count,
                        ),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
        } else {
            val dateTimeFormatter =
                DateTimeFormatter.ofLocalizedDateTime(FormatStyle.SHORT)
            val zone = ZoneId.systemDefault()
            otherWorkouts.forEach { session ->
                val startLabel =
                    HealthConnectReader.formatZoned(session.start, zone).format(dateTimeFormatter)
                val durationLabel = HealthConnectReader.formatDuration(session.duration)
                val title =
                    session.title
                        ?: stringResource(R.string.health_connect_other_workout_untitled)
                Column(modifier = Modifier.fillMaxWidth()) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium,
                    )
                    Text(
                        text =
                        stringResource(
                            R.string.health_connect_other_workout_row,
                            startLabel,
                            durationLabel,
                            session.dataOrigin,
                        ),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}
