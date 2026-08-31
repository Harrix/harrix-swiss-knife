package dev.harrix.hsk.health

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.request.AggregateGroupByPeriodRequest
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.Duration
import java.time.Instant
import java.time.LocalDate
import java.time.Period
import java.time.ZoneId
import java.time.ZonedDateTime

/** Availability of the Health Connect SDK on this device. */
enum class HealthConnectAvailability {
    Available,
    UpdateRequired,
    Unavailable,
}

/** One calendar day of aggregated step counts. */
data class DaySteps(
    val date: LocalDate,
    val count: Long,
)

/** A single exercise session from Health Connect. */
data class ExerciseSessionSummary(
    val start: Instant,
    val end: Instant,
    val duration: Duration,
    val exerciseType: Int,
    val title: String?,
    val dataOrigin: String,
)

/** Count of sessions for one exercise type code. */
data class ExerciseTypeCount(
    val exerciseType: Int,
    val count: Int,
)

/** Snapshot loaded for the Health Connect test screen. */
data class HealthConnectSnapshot(
    val stepsByDay: List<DaySteps>,
    val stepsTotal: Long,
    val otherWorkouts: List<ExerciseSessionSummary>,
    val exerciseTypeCounts: List<ExerciseTypeCount>,
    val rangeStart: LocalDate,
    val rangeEnd: LocalDate,
)

/**
 * Reads step and exercise data from Health Connect (Samsung Health syncs into it).
 */
class HealthConnectReader(
    private val context: Context,
) {
    val permissions: Set<String> =
        setOf(
            HealthPermission.getReadPermission(StepsRecord::class),
            HealthPermission.getReadPermission(ExerciseSessionRecord::class),
        )

    fun createPermissionContract() = PermissionController.createRequestPermissionResultContract()

    fun availability(): HealthConnectAvailability {
        val status = HealthConnectClient.getSdkStatus(context)
        return when (status) {
            HealthConnectClient.SDK_AVAILABLE -> HealthConnectAvailability.Available

            HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED ->
                HealthConnectAvailability.UpdateRequired

            else -> HealthConnectAvailability.Unavailable
        }
    }

    fun clientOrNull(): HealthConnectClient? {
        if (availability() != HealthConnectAvailability.Available) {
            return null
        }
        return HealthConnectClient.getOrCreate(context)
    }

    suspend fun hasAllPermissions(client: HealthConnectClient): Boolean {
        val granted = client.permissionController.getGrantedPermissions()
        return granted.containsAll(permissions)
    }

    /**
     * Load the last [dayCount] calendar days of steps and exercise sessions
     * (ending today, local zone).
     */
    suspend fun loadSnapshot(
        client: HealthConnectClient,
        dayCount: Int = DEFAULT_DAY_COUNT,
    ): HealthConnectSnapshot {
        val zone = ZoneId.systemDefault()
        val today = LocalDate.now(zone)
        val rangeStart = today.minusDays((dayCount - 1).toLong())
        val startLocal = rangeStart.atStartOfDay()
        val endLocal = today.plusDays(1).atStartOfDay()
        val startInstant = rangeStart.atStartOfDay(zone).toInstant()
        val endInstant = today.plusDays(1).atStartOfDay(zone).toInstant()

        val stepsByDay =
            readStepsByDay(
                client,
                rangeStart,
                today,
                TimeRangeFilter.between(startLocal, endLocal),
            )
        val sessions =
            readExerciseSessions(
                client,
                TimeRangeFilter.between(startInstant, endInstant),
            )
        val otherWorkouts =
            sessions
                .filter { it.exerciseType == ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT }
                .sortedByDescending { it.start }
        val typeCounts =
            sessions
                .groupingBy { it.exerciseType }
                .eachCount()
                .entries
                .map { ExerciseTypeCount(it.key, it.value) }
                .sortedByDescending { it.count }

        return HealthConnectSnapshot(
            stepsByDay = stepsByDay,
            stepsTotal = stepsByDay.sumOf { it.count },
            otherWorkouts = otherWorkouts,
            exerciseTypeCounts = typeCounts,
            rangeStart = rangeStart,
            rangeEnd = today,
        )
    }

    private suspend fun readStepsByDay(
        client: HealthConnectClient,
        rangeStart: LocalDate,
        rangeEnd: LocalDate,
        timeFilter: TimeRangeFilter,
    ): List<DaySteps> {
        val response =
            client.aggregateGroupByPeriod(
                AggregateGroupByPeriodRequest(
                    metrics = setOf(StepsRecord.COUNT_TOTAL),
                    timeRangeFilter = timeFilter,
                    timeRangeSlicer = Period.ofDays(1),
                ),
            )
        val byDate =
            response.associate { result ->
                val day = result.startTime.toLocalDate()
                day to (result.result[StepsRecord.COUNT_TOTAL] ?: 0L)
            }
        val days = mutableListOf<DaySteps>()
        var day = rangeStart
        while (!day.isAfter(rangeEnd)) {
            days += DaySteps(date = day, count = byDate[day] ?: 0L)
            day = day.plusDays(1)
        }
        return days.asReversed()
    }

    private suspend fun readExerciseSessions(
        client: HealthConnectClient,
        timeFilter: TimeRangeFilter,
    ): List<ExerciseSessionSummary> {
        val response =
            client.readRecords(
                ReadRecordsRequest(
                    recordType = ExerciseSessionRecord::class,
                    timeRangeFilter = timeFilter,
                ),
            )
        return response.records.map { record ->
            ExerciseSessionSummary(
                start = record.startTime,
                end = record.endTime,
                duration = Duration.between(record.startTime, record.endTime),
                exerciseType = record.exerciseType,
                title = record.title?.takeIf { it.isNotBlank() },
                dataOrigin = record.metadata.dataOrigin.packageName,
            )
        }
    }

    companion object {
        const val DEFAULT_DAY_COUNT = 7

        fun formatDuration(duration: Duration): String {
            val totalSeconds = duration.seconds.coerceAtLeast(0)
            val hours = totalSeconds / 3600
            val minutes = (totalSeconds % 3600) / 60
            val seconds = totalSeconds % 60
            return when {
                hours > 0 -> "%d:%02d:%02d".format(hours, minutes, seconds)
                else -> "%d:%02d".format(minutes, seconds)
            }
        }

        fun formatZoned(
            instant: Instant,
            zone: ZoneId = ZoneId.systemDefault(),
        ): ZonedDateTime = instant.atZone(zone)
    }
}
