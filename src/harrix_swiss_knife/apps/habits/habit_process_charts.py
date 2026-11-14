"""Habit process charts: monthly totals and cumulative month comparisons."""

from __future__ import annotations

import calendar
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common.chart_theme import chart_series_color
from harrix_swiss_knife.apps.common.ui_chrome import BUTTON_DANGER_BG
from harrix_swiss_knife.apps.habits.ticktick_task_stats import (
    TickTickMonthSeries,
    build_compare_months_chart,
    build_month_counts_chart,
    month_starts_going_back,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.figure import Figure

HabitChartMode = str
CHART_MODE_HEATMAP = "heatmap"
CHART_MODE_BY_MONTH = "by_month"
CHART_MODE_COMPARE_LAST = "compare_last"
CHART_MODE_COMPARE_SAME = "compare_same"
HABIT_CHART_MODE_LABELS: tuple[tuple[str, str], ...] = (
    (CHART_MODE_HEATMAP, "Heatmap"),
    (CHART_MODE_BY_MONTH, "By month"),
    (CHART_MODE_COMPARE_LAST, "Compare last months"),
    (CHART_MODE_COMPARE_SAME, "Compare same months"),
)


def aggregate_daily_values(
    rows: Sequence[tuple[str, int]],
    *,
    is_bool: bool,
) -> dict[date, int]:
    """Sum process rows per calendar day (done-day count or numeric sum)."""
    daily: dict[date, int] = {}
    for raw_date, raw_value in rows:
        day = date.fromisoformat(str(raw_date)[:10])
        contribution = _day_contribution(int(raw_value), is_bool=is_bool)
        if contribution == 0 and is_bool:
            continue
        daily[day] = daily.get(day, 0) + contribution
    return daily


def build_habit_by_month_chart(
    month_counts: Sequence[tuple[date, int]],
    *,
    habit_name: str,
    is_bool: bool,
    figsize: tuple[float, float],
) -> Figure:
    """Bar chart of monthly habit totals."""
    measure = "Done days" if is_bool else "Total"
    figure = build_month_counts_chart(month_counts, figsize=figsize)
    ax = figure.axes[0] if figure.axes else figure.add_subplot(111)
    ax.set_ylabel(measure)
    ax.set_title(f"{habit_name}: {measure} by month (last {len(month_counts)})")
    return figure


def build_habit_compare_chart(
    series: Sequence[TickTickMonthSeries],
    *,
    title: str,
    is_bool: bool,
    figsize: tuple[float, float],
) -> Figure:
    """Overlay cumulative month lines for a habit."""
    ylabel = "Cumulative done days" if is_bool else "Cumulative total"
    figure = build_compare_months_chart(series, title=title, figsize=figsize)
    if figure.axes:
        figure.axes[0].set_ylabel(ylabel)
    return figure


def compare_last_months_series(
    daily: dict[date, int],
    months_count: int,
    *,
    today: date | None = None,
) -> list[TickTickMonthSeries]:
    """Cumulative day-of-month lines for the last ``months_count`` months."""
    today_local = today or datetime.now().astimezone().date()
    series: list[TickTickMonthSeries] = []
    for index, start in enumerate(month_starts_going_back(months_count, today=today_local)):
        days_in_month = calendar.monthrange(start.year, start.month)[1]
        is_current = index == 0
        end_day = min(today_local.day, days_in_month) if is_current else days_in_month
        label = start.strftime("%B %Y")
        if is_current:
            label = f"{label} (Current)"
        color = BUTTON_DANGER_BG if is_current else chart_series_color(index)
        series.append(
            TickTickMonthSeries(
                year=start.year,
                month=start.month,
                label=label,
                color=color,
                is_current=is_current,
                points=cumulative_habit_month_points(daily, start.year, start.month, end_day=end_day),
            ),
        )
    return series


def compare_same_months_series(
    daily: dict[date, int],
    month: int,
    years_count: int,
    *,
    today: date | None = None,
) -> list[TickTickMonthSeries]:
    """Cumulative lines for the same calendar month across recent years."""
    today_local = today or datetime.now().astimezone().date()
    selected = max(1, min(int(month), 12))
    series: list[TickTickMonthSeries] = []
    color_index = 0
    for offset in range(max(int(years_count), 0)):
        year = today_local.year - offset
        if year == today_local.year and today_local.month < selected:
            continue
        days_in_month = calendar.monthrange(year, selected)[1]
        is_current = year == today_local.year and today_local.month == selected
        if year == today_local.year and today_local.month == selected:
            end_day = min(today_local.day, days_in_month)
        elif year == today_local.year:
            end_day = days_in_month
        else:
            end_day = days_in_month
        label = date(year, selected, 1).strftime("%B %Y")
        if is_current:
            label = f"{label} (Current)"
            color = BUTTON_DANGER_BG
        else:
            color = chart_series_color(color_index + 1)
            color_index += 1
        series.append(
            TickTickMonthSeries(
                year=year,
                month=selected,
                label=label,
                color=color,
                is_current=is_current,
                points=cumulative_habit_month_points(daily, year, selected, end_day=end_day),
            ),
        )
    return series


def counts_by_month(
    daily: dict[date, int],
    months_count: int,
    *,
    today: date | None = None,
) -> list[tuple[date, int]]:
    """Return ``(month_start, total)`` oldest→newest for the last ``months_count`` months."""
    today_local = today or datetime.now().astimezone().date()
    month_starts = list(reversed(month_starts_going_back(months_count, today=today_local)))
    if not month_starts:
        return []
    totals = dict.fromkeys(month_starts, 0)
    for day, value in daily.items():
        if day > today_local:
            continue
        key = date(day.year, day.month, 1)
        if key in totals:
            totals[key] += value
    return [(start, totals[start]) for start in month_starts]


def cumulative_habit_month_points(
    daily: dict[date, int],
    year: int,
    month: int,
    *,
    end_day: int,
) -> list[tuple[int, int]]:
    """Return ``(day_of_month, cumulative_total)`` through ``end_day``."""
    days_in_month = calendar.monthrange(year, month)[1]
    limit = max(1, min(int(end_day), days_in_month))
    per_day: dict[int, int] = {}
    for day, value in daily.items():
        if day.year != year or day.month != month or day.day > limit:
            continue
        per_day[day.day] = per_day.get(day.day, 0) + value
    if not per_day:
        return []
    points: list[tuple[int, int]] = []
    running = 0
    for day in sorted(per_day):
        running += per_day[day]
        points.append((day, running))
    if points[-1][0] < limit:
        points.append((limit, running))
    return points


def habit_is_bool_flag(db_rows: list[Any] | None) -> bool:
    """Return whether habit metadata marks the habit as boolean-only."""
    if not db_rows or not db_rows[0]:
        return False
    raw = db_rows[0][0]
    return raw == 1


def _day_contribution(value: int, *, is_bool: bool) -> int:
    if is_bool:
        return 1 if value > 0 else 0
    return value
