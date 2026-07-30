package dev.harrix.hsk.gallery

import java.util.Calendar

/**
 * Date filter for Camera photos.
 *
 * [startEpochSecInclusive] / [endEpochSecInclusive] are inclusive local-time day bounds.
 */
data class GalleryDateFilter(
    val enabled: Boolean = false,
    val startEpochSecInclusive: Long = defaultStartEpochSec(),
    val endEpochSecInclusive: Long = defaultEndEpochSec(),
) {
    fun contains(epochSec: Long): Boolean = !enabled || epochSec in startEpochSecInclusive..endEpochSecInclusive

    fun matchesDateRange(other: GalleryDateFilter): Boolean = startEpochSecInclusive == other.startEpochSecInclusive &&
        endEpochSecInclusive == other.endEpochSecInclusive

    fun withEnabled(value: Boolean): GalleryDateFilter = copy(enabled = value)

    fun withDateRange(
        fromYear: Int,
        fromMonth: Int,
        fromDay: Int,
        toYear: Int,
        toMonth: Int,
        toDay: Int,
    ): GalleryDateFilter {
        val start =
            startOfDayEpochSec(
                fromYear,
                fromMonth,
                fromDay.coerceIn(1, daysInMonth(fromYear, fromMonth)),
            )
        val end =
            endOfDayEpochSec(
                toYear,
                toMonth,
                toDay.coerceIn(1, daysInMonth(toYear, toMonth)),
            )
        return copy(
            startEpochSecInclusive = minOf(start, end),
            endEpochSecInclusive = maxOf(start, end),
        )
    }

    fun fromYear(): Int = calendarFor(startEpochSecInclusive).get(Calendar.YEAR)

    fun fromMonth(): Int = calendarFor(startEpochSecInclusive).get(Calendar.MONTH) + 1

    fun fromDay(): Int = calendarFor(startEpochSecInclusive).get(Calendar.DAY_OF_MONTH)

    fun toYear(): Int = calendarFor(endEpochSecInclusive).get(Calendar.YEAR)

    fun toMonth(): Int = calendarFor(endEpochSecInclusive).get(Calendar.MONTH) + 1

    fun toDay(): Int = calendarFor(endEpochSecInclusive).get(Calendar.DAY_OF_MONTH)

    companion object {
        fun daysInMonth(
            year: Int,
            month: Int,
        ): Int {
            val cal = Calendar.getInstance()
            cal.set(year, month - 1, 1)
            return cal.getActualMaximum(Calendar.DAY_OF_MONTH)
        }

        fun lastDaysIncludingToday(dayCount: Int): GalleryDateFilter {
            require(dayCount >= 1)
            val end = endOfDay(Calendar.getInstance())
            val startCal =
                Calendar.getInstance().apply {
                    add(Calendar.DAY_OF_YEAR, -(dayCount - 1))
                }
            val start = startOfDay(startCal)
            return GalleryDateFilter(
                enabled = true,
                startEpochSecInclusive = start,
                endEpochSecInclusive = end,
            )
        }

        fun lastCalendarMonths(monthCount: Int): GalleryDateFilter {
            require(monthCount >= 1)
            val end = endOfDay(Calendar.getInstance())
            val startCal =
                Calendar.getInstance().apply {
                    add(Calendar.MONTH, -monthCount)
                }
            val start = startOfDay(startCal)
            return GalleryDateFilter(
                enabled = true,
                startEpochSecInclusive = start,
                endEpochSecInclusive = end,
            )
        }

        fun lastCalendarYears(yearCount: Int): GalleryDateFilter {
            require(yearCount >= 1)
            val end = endOfDay(Calendar.getInstance())
            val startCal =
                Calendar.getInstance().apply {
                    add(Calendar.YEAR, -yearCount)
                }
            val start = startOfDay(startCal)
            return GalleryDateFilter(
                enabled = true,
                startEpochSecInclusive = start,
                endEpochSecInclusive = end,
            )
        }

        /** Inclusive local calendar day of the given capture timestamp. */
        fun forShootDay(dateTakenEpochMs: Long): GalleryDateFilter {
            val day =
                Calendar.getInstance().apply {
                    timeInMillis = dateTakenEpochMs
                }
            return GalleryDateFilter(
                enabled = true,
                startEpochSecInclusive = startOfDay(day),
                endEpochSecInclusive = endOfDay(day),
            )
        }

        private fun defaultStartEpochSec(): Long {
            val now = Calendar.getInstance()
            return startOfDayEpochSec(now.get(Calendar.YEAR), 1, 1)
        }

        private fun defaultEndEpochSec(): Long = endOfDay(Calendar.getInstance())

        private fun calendarFor(epochSec: Long): Calendar = Calendar.getInstance().apply {
            timeInMillis = epochSec * 1000L
        }

        private fun startOfDayEpochSec(
            year: Int,
            month: Int,
            day: Int,
        ): Long {
            val cal = Calendar.getInstance()
            cal.set(year, month - 1, day, 0, 0, 0)
            cal.set(Calendar.MILLISECOND, 0)
            return cal.timeInMillis / 1000L
        }

        private fun endOfDayEpochSec(
            year: Int,
            month: Int,
            day: Int,
        ): Long {
            val cal = Calendar.getInstance()
            cal.set(year, month - 1, day, 23, 59, 59)
            cal.set(Calendar.MILLISECOND, 999)
            return cal.timeInMillis / 1000L
        }

        private fun startOfDay(calendar: Calendar): Long {
            val cal = calendar.clone() as Calendar
            cal.set(Calendar.HOUR_OF_DAY, 0)
            cal.set(Calendar.MINUTE, 0)
            cal.set(Calendar.SECOND, 0)
            cal.set(Calendar.MILLISECOND, 0)
            return cal.timeInMillis / 1000L
        }

        private fun endOfDay(calendar: Calendar): Long {
            val cal = calendar.clone() as Calendar
            cal.set(Calendar.HOUR_OF_DAY, 23)
            cal.set(Calendar.MINUTE, 59)
            cal.set(Calendar.SECOND, 59)
            cal.set(Calendar.MILLISECOND, 999)
            return cal.timeInMillis / 1000L
        }
    }
}
