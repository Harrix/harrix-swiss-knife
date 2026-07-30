package dev.harrix.hsk.gallery

import java.util.Calendar

/**
 * Date filter for Camera photos.
 *
 * [startEpochSecInclusive] / [endEpochSecInclusive] are local-time day bounds when set via
 * presets; year/month editors snap to the first/last second of the selected months.
 */
data class GalleryDateFilter(
    val enabled: Boolean = false,
    val startEpochSecInclusive: Long = defaultStartEpochSec(),
    val endEpochSecInclusive: Long = defaultEndEpochSec(),
) {
    fun contains(epochSec: Long): Boolean =
        !enabled || epochSec in startEpochSecInclusive..endEpochSecInclusive

    fun withEnabled(value: Boolean): GalleryDateFilter = copy(enabled = value)

    fun withYearMonthRange(
        fromYear: Int,
        fromMonth: Int,
        toYear: Int,
        toMonth: Int,
    ): GalleryDateFilter {
        val start = startOfMonthEpochSec(fromYear, fromMonth)
        val end = endOfMonthEpochSec(toYear, toMonth)
        return copy(
            startEpochSecInclusive = minOf(start, end),
            endEpochSecInclusive = maxOf(start, end),
        )
    }

    fun fromYear(): Int = calendarFor(startEpochSecInclusive).get(Calendar.YEAR)

    fun fromMonth(): Int = calendarFor(startEpochSecInclusive).get(Calendar.MONTH) + 1

    fun toYear(): Int = calendarFor(endEpochSecInclusive).get(Calendar.YEAR)

    fun toMonth(): Int = calendarFor(endEpochSecInclusive).get(Calendar.MONTH) + 1

    companion object {
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

        private fun defaultStartEpochSec(): Long {
            val now = Calendar.getInstance()
            return startOfMonthEpochSec(now.get(Calendar.YEAR), 1)
        }

        private fun defaultEndEpochSec(): Long = endOfDay(Calendar.getInstance())

        private fun calendarFor(epochSec: Long): Calendar =
            Calendar.getInstance().apply {
                timeInMillis = epochSec * 1000L
            }

        private fun startOfMonthEpochSec(
            year: Int,
            month: Int,
        ): Long {
            val cal = Calendar.getInstance()
            cal.set(year, month - 1, 1, 0, 0, 0)
            cal.set(Calendar.MILLISECOND, 0)
            return cal.timeInMillis / 1000L
        }

        private fun endOfMonthEpochSec(
            year: Int,
            month: Int,
        ): Long {
            val cal = Calendar.getInstance()
            cal.set(year, month - 1, 1, 0, 0, 0)
            cal.set(Calendar.MILLISECOND, 0)
            cal.add(Calendar.MONTH, 1)
            cal.add(Calendar.SECOND, -1)
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
