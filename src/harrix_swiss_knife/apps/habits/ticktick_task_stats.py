"""Aggregate TickTick completions and build contribution / period charts."""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any, Literal

import dayplot as dp
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgb
from matplotlib.patches import Patch, Rectangle

from harrix_swiss_knife.apps.common.calendar_heatmap import (
    apply_habit_heatmap_month_separation,
    date_at_heatmap_point,
    habit_heatmap_month_separated_positions,
)
from harrix_swiss_knife.apps.common.chart_theme import (
    chart_annotation_style,
    chart_series_color,
    chart_success_color,
    intensity_bin_label,
    intensity_bin_ranges,
    map_value_to_intensity_bin,
    style_axes,
    themed_figure,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.figure import Figure

    from harrix_swiss_knife.apps.habits.ticktick_local_db import TickTickCompletion

LAST_365_DAYS_LABEL = "Last 365 days"
ChartMode = Literal["heatmap", "by_year", "by_month", "compare_last", "compare_same"]
CHART_MODE_HEATMAP: ChartMode = "heatmap"
CHART_MODE_BY_YEAR: ChartMode = "by_year"
CHART_MODE_BY_MONTH: ChartMode = "by_month"
CHART_MODE_COMPARE_LAST: ChartMode = "compare_last"
CHART_MODE_COMPARE_SAME: ChartMode = "compare_same"
CHART_MODE_LABELS: tuple[tuple[ChartMode, str], ...] = (
    (CHART_MODE_HEATMAP, "Heatmap"),
    (CHART_MODE_BY_YEAR, "By year"),
    (CHART_MODE_BY_MONTH, "By month"),
    (CHART_MODE_COMPARE_LAST, "Compare last months"),
    (CHART_MODE_COMPARE_SAME, "Compare same months"),
)
_GRAY = "#e9e9e9"
_LIGHT_GREEN = "#b7e4b7"
_DAY_TICK_STEP_THRESHOLD = 15
_YEAR_LABEL_ROTATE_THRESHOLD = 12
_MONTH_LINE_MARKER_THRESHOLD = 10
_COMPARE_CURRENT = "#cc584c"


@dataclass(frozen=True, slots=True)
class TickTickHeatmapResult:
    """Matplotlib figure plus click-mapping positions for the contribution calendar."""

    figure: Figure
    positions: dict[date, tuple[float, float]]
    start_date: date
    end_date: date


@dataclass(frozen=True, slots=True)
class TickTickMonthSeries:
    """One month line for last-months / same-months comparison charts."""

    year: int
    month: int
    label: str
    color: str
    is_current: bool
    points: list[tuple[int, int]] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class TickTickPeriodStats:
    """Summary metrics for completions in a date window."""

    start_date: date
    end_date: date
    total_completions: int
    active_days: int
    current_streak: int
    longest_streak: int
    busiest_day: date | None
    busiest_count: int
    counts_by_day: dict[date, int] = field(default_factory=dict)
    completions_by_day: dict[date, list[TickTickCompletion]] = field(default_factory=dict)


def aggregate_completions(
    completions: Sequence[TickTickCompletion],
    start_date: date,
    end_date: date,
    *,
    project_id: str | None = None,
    today: date | None = None,
) -> TickTickPeriodStats:
    """Aggregate filtered completions into per-day counts and streak metrics."""
    filtered = filter_completions_for_period(
        completions,
        start_date,
        end_date,
        project_id=project_id,
    )
    counts: dict[date, int] = {}
    by_day: dict[date, list[TickTickCompletion]] = {}
    for item in filtered:
        day = item.completed_at.date()
        counts[day] = counts.get(day, 0) + 1
        by_day.setdefault(day, []).append(item)

    for day_list in by_day.values():
        day_list.sort(key=lambda row: row.completed_at)

    busiest_day: date | None = None
    busiest_count = 0
    for day, count in counts.items():
        if count > busiest_count or (count == busiest_count and (busiest_day is None or day < busiest_day)):
            busiest_day = day
            busiest_count = count

    today_local = today or datetime.now().astimezone().date()
    streak_anchor = min(end_date, today_local)

    return TickTickPeriodStats(
        start_date=start_date,
        end_date=end_date,
        total_completions=len(filtered),
        active_days=len(counts),
        current_streak=current_streak_days(counts, streak_anchor),
        longest_streak=longest_streak_days(counts, start_date, end_date),
        busiest_day=busiest_day,
        busiest_count=busiest_count,
        counts_by_day=counts,
        completions_by_day=by_day,
    )


def available_years(completions: Sequence[TickTickCompletion], *, today_year: int | None = None) -> list[int]:
    """Return sorted calendar years that have at least one completion, capped at today."""
    years = {item.completed_at.year for item in completions}
    cap = today_year if today_year is not None else datetime.now().astimezone().year
    return sorted(year for year in years if year <= cap)


def build_compare_months_chart(
    series: Sequence[TickTickMonthSeries],
    *,
    title: str,
    figsize: tuple[float, float] = (12.0, 4.5),
    dpi: int = 100,
) -> Figure:
    """Overlay cumulative completion lines for several months (Fitness-style)."""
    figure = themed_figure(figsize=figsize, dpi=dpi)
    ax = figure.add_subplot(111)
    plotted = [item for item in series if item.points]
    if not plotted:
        ax.set_title(title)
        ax.text(0.5, 0.5, "No completed tasks", ha="center", va="center", transform=ax.transAxes)
        figure.tight_layout()
        return figure

    current: TickTickMonthSeries | None = None
    for item in plotted:
        if item.is_current:
            current = item
            continue
        _plot_month_line(ax, item, linewidth=2, linestyle="--")

    if current is not None:
        _plot_month_line(ax, current, linewidth=3, linestyle="-")

    max_day = max(point[0] for item in plotted for point in item.points)
    ax.set_xlim(1, max(max_day, 1))
    ax.set_xticks(range(1, max_day + 1, 2 if max_day > _DAY_TICK_STEP_THRESHOLD else 1))
    ax.set_xlabel("Day of month")
    ax.set_ylabel("Cumulative completed tasks")
    ax.set_title(title)
    ax.grid(visible=True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    figure.tight_layout()
    return figure


def build_contribution_heatmap(
    stats: TickTickPeriodStats,
    *,
    figsize: tuple[float, float] = (14.0, 3.2),
    dpi: int = 100,
    selected_day: date | None = None,
) -> TickTickHeatmapResult:
    """Build a green GitHub-like contribution calendar for ``stats``."""
    start_date = stats.start_date
    end_date = stats.end_date
    figure = themed_figure(figsize=figsize, dpi=dpi)
    ax = figure.add_subplot(111)

    pos_max = max((int(v) for v in stats.counts_by_day.values() if int(v) > 0), default=0)
    bins = intensity_bin_ranges(pos_max, max_bins=5)
    dark_green = chart_success_color()
    colors_list: list[tuple[float, float, float]] = [to_rgb(_GRAY)]
    if bins:
        for index in range(len(bins)):
            t = 0.0 if len(bins) == 1 else index / (len(bins) - 1)
            colors_list.append(_lerp(to_rgb(_LIGHT_GREEN), to_rgb(dark_green), t))
    else:
        colors_list.append(to_rgb(_LIGHT_GREEN))

    mapped_vmax = max(len(bins), 1)
    cmap = LinearSegmentedColormap.from_list("ticktick_contrib", colors_list, N=len(colors_list))

    day_keys = list(stats.counts_by_day.keys())
    mapped_values = [map_value_to_intensity_bin(int(stats.counts_by_day[day]), bins) for day in day_keys]
    # dayplot types `dates` as list[date | datetime | str]; list[date] is invariant.
    calendar_dates: list[date | datetime | str] = list(day_keys)

    if not calendar_dates:
        # dayplot still needs at least one sample day in range
        calendar_dates = [start_date]
        mapped_values = [0]

    cell_patches = dp.calendar(
        dates=calendar_dates,
        values=mapped_values,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        legend=False,
        color_for_none=_GRAY,
        vmin=0,
        vmax=mapped_vmax,
        cmap=cmap,
        boxstyle="round",
        ax=ax,
    )
    apply_habit_heatmap_month_separation(ax, cell_patches, start_date, end_date)

    positions, _labels, _width = habit_heatmap_month_separated_positions(start_date, end_date)
    today = datetime.now().astimezone().date()
    for day, (cx, cy) in positions.items():
        if day == selected_day:
            ax.add_patch(
                Rectangle(
                    (cx - 0.42, cy - 0.42),
                    0.84,
                    0.84,
                    fill=False,
                    edgecolor=chart_series_color(0),
                    linewidth=2.0,
                    zorder=6,
                ),
            )
        elif day == today and start_date <= today <= end_date:
            ax.add_patch(
                Rectangle(
                    (cx - 0.42, cy - 0.42),
                    0.84,
                    0.84,
                    fill=False,
                    edgecolor=chart_series_color(0),
                    linewidth=1.1,
                    linestyle="--",
                    alpha=0.85,
                    zorder=5,
                ),
            )

    norm = Normalize(vmin=0, vmax=mapped_vmax)
    handles: list[Patch] = [Patch(facecolor=_GRAY, edgecolor="none", label="None")]
    for index, (lo, hi) in enumerate(bins, start=1):
        handles.append(
            Patch(
                facecolor=cmap(norm(index)),
                edgecolor="none",
                label=intensity_bin_label(lo, hi),
            ),
        )
    ax.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        frameon=False,
        fontsize=8,
        title="Tasks",
    )
    # Legend is outside the axes on a short figure; tight_layout cannot fit it
    # and warns about top/bottom margins. Keep a fixed right gutter instead.
    figure.subplots_adjust(left=0.02, right=0.86, top=0.96, bottom=0.12)
    return TickTickHeatmapResult(
        figure=figure,
        positions=positions,
        start_date=start_date,
        end_date=end_date,
    )


def build_month_counts_chart(
    month_counts: Sequence[tuple[date, int]],
    *,
    figsize: tuple[float, float] = (12.0, 4.5),
    dpi: int = 100,
) -> Figure:
    """Bar chart of completed-task totals by calendar month."""
    figure = themed_figure(figsize=figsize, dpi=dpi)
    ax = figure.add_subplot(111)
    if not month_counts:
        ax.set_title("Completed tasks by month")
        ax.text(0.5, 0.5, "No completed tasks", ha="center", va="center", transform=ax.transAxes)
        figure.tight_layout()
        return figure
    labels = [start.strftime("%b %Y") for start, _count in month_counts]
    values = [count for _start, count in month_counts]
    bars = ax.bar(range(len(labels)), values, color=chart_success_color(), width=0.7)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Month")
    ax.set_ylabel("Completed tasks")
    ax.set_title(f"Completed tasks by month (last {len(month_counts)})")
    style_axes(ax)
    _annotate_bars(ax, bars)
    figure.tight_layout()
    return figure


def build_year_counts_chart(
    year_counts: Sequence[tuple[int, int]],
    *,
    figsize: tuple[float, float] = (12.0, 4.5),
    dpi: int = 100,
) -> Figure:
    """Bar chart of completed-task totals by calendar year."""
    figure = themed_figure(figsize=figsize, dpi=dpi)
    ax = figure.add_subplot(111)
    if not year_counts:
        ax.set_title("Completed tasks by year")
        ax.text(0.5, 0.5, "No completed tasks", ha="center", va="center", transform=ax.transAxes)
        figure.tight_layout()
        return figure
    labels = [str(year) for year, _count in year_counts]
    values = [count for _year, count in year_counts]
    bars = ax.bar(range(len(labels)), values, color=chart_success_color(), width=0.7)
    ax.set_xticks(range(len(labels)))
    rotate = len(labels) > _YEAR_LABEL_ROTATE_THRESHOLD
    ax.set_xticklabels(labels, rotation=45 if rotate else 0, ha="right" if rotate else "center")
    ax.set_xlabel("Year")
    ax.set_ylabel("Completed tasks")
    ax.set_title("Completed tasks by year")
    style_axes(ax)
    _annotate_bars(ax, bars)
    figure.tight_layout()
    return figure


def compare_last_months_series(
    completions: Sequence[TickTickCompletion],
    months_count: int,
    *,
    project_id: str | None = None,
    today: date | None = None,
) -> list[TickTickMonthSeries]:
    """Build cumulative day-of-month series for the last ``months_count`` months (newest first)."""
    today_local = today or datetime.now().astimezone().date()
    series: list[TickTickMonthSeries] = []
    for index, start in enumerate(month_starts_going_back(months_count, today=today_local)):
        days_in_month = calendar.monthrange(start.year, start.month)[1]
        is_current = index == 0
        end_day = min(today_local.day, days_in_month) if is_current else days_in_month
        label = start.strftime("%B %Y")
        if is_current:
            label = f"{label} (Current)"
        color = _COMPARE_CURRENT if is_current else chart_series_color(index)
        series.append(
            TickTickMonthSeries(
                year=start.year,
                month=start.month,
                label=label,
                color=color,
                is_current=is_current,
                points=cumulative_month_points(
                    completions,
                    start.year,
                    start.month,
                    end_day=end_day,
                    project_id=project_id,
                ),
            ),
        )
    return series


def compare_same_months_series(
    completions: Sequence[TickTickCompletion],
    month: int,
    years_count: int,
    *,
    project_id: str | None = None,
    today: date | None = None,
) -> list[TickTickMonthSeries]:
    """Build cumulative series for the same calendar month across recent years (newest first)."""
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
            color = _COMPARE_CURRENT
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
                points=cumulative_month_points(
                    completions,
                    year,
                    selected,
                    end_day=end_day,
                    project_id=project_id,
                ),
            ),
        )
    return series


def counts_by_month(
    completions: Sequence[TickTickCompletion],
    months_count: int,
    *,
    project_id: str | None = None,
    today: date | None = None,
) -> list[tuple[date, int]]:
    """Return ``(month_start, count)`` oldest→newest for the last ``months_count`` months."""
    today_local = today or datetime.now().astimezone().date()
    month_starts = list(reversed(month_starts_going_back(months_count, today=today_local)))
    if not month_starts:
        return []
    totals = dict.fromkeys(month_starts, 0)
    for item in completions:
        if project_id is not None and item.project_id != project_id:
            continue
        day = item.completed_at.date()
        if day > today_local:
            continue
        key = date(day.year, day.month, 1)
        if key in totals:
            totals[key] += 1
    return [(start, totals[start]) for start in month_starts]


def counts_by_year(
    completions: Sequence[TickTickCompletion],
    *,
    project_id: str | None = None,
    today: date | None = None,
) -> list[tuple[int, int]]:
    """Return ``(year, count)`` ascending for years with completions (and empty gaps filled)."""
    today_local = today or datetime.now().astimezone().date()
    filtered = [
        item
        for item in completions
        if item.completed_at.date() <= today_local and (project_id is None or item.project_id == project_id)
    ]
    if not filtered:
        return []
    totals: dict[int, int] = {}
    for item in filtered:
        year = item.completed_at.year
        if year <= today_local.year:
            totals[year] = totals.get(year, 0) + 1
    if not totals:
        return []
    start_year = min(totals)
    return [(year, totals.get(year, 0)) for year in range(start_year, today_local.year + 1)]


def cumulative_month_points(
    completions: Sequence[TickTickCompletion],
    year: int,
    month: int,
    *,
    end_day: int,
    project_id: str | None = None,
) -> list[tuple[int, int]]:
    """Return ``(day_of_month, cumulative_count)`` through ``end_day`` for one calendar month."""
    days_in_month = calendar.monthrange(year, month)[1]
    limit = max(1, min(int(end_day), days_in_month))
    per_day: dict[int, int] = {}
    for item in completions:
        if project_id is not None and item.project_id != project_id:
            continue
        stamp = item.completed_at
        if stamp.year != year or stamp.month != month:
            continue
        if stamp.day > limit:
            continue
        per_day[stamp.day] = per_day.get(stamp.day, 0) + 1
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


def current_streak_days(counts_by_day: dict[date, int], anchor: date) -> int:
    """Count consecutive active days ending at ``anchor`` (or ``anchor - 1`` if today empty)."""
    if counts_by_day.get(anchor, 0) > 0:
        cursor = anchor
    elif counts_by_day.get(anchor - timedelta(days=1), 0) > 0:
        cursor = anchor - timedelta(days=1)
    else:
        return 0
    streak = 0
    while counts_by_day.get(cursor, 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def day_from_heatmap_click(
    result: TickTickHeatmapResult,
    x: float,
    y: float,
) -> date | None:
    """Map axes data coordinates from a canvas click to a calendar day."""
    return date_at_heatmap_point(result.positions, x, y)


def filter_completions_for_period(
    completions: Sequence[TickTickCompletion],
    start_date: date,
    end_date: date,
    *,
    project_id: str | None = None,
) -> list[TickTickCompletion]:
    """Keep completions in ``[start_date, end_date]``, optionally for one project."""
    selected: list[TickTickCompletion] = []
    for item in completions:
        if project_id and item.project_id != project_id:
            continue
        day = item.completed_at.date()
        if start_date <= day <= end_date:
            selected.append(item)
    return selected


def format_period_summary(stats: TickTickPeriodStats) -> str:
    """Return a one-line summary for the TickTick stats tab header."""
    busiest = "—"
    if stats.busiest_day is not None and stats.busiest_count > 0:
        busiest = f"{stats.busiest_day.isoformat()} ({stats.busiest_count})"
    return (
        f"Completions: {stats.total_completions} · Active days: {stats.active_days} · "
        f"Current streak: {stats.current_streak} · Longest streak: {stats.longest_streak} · "
        f"Busiest day: {busiest}"
    )


def heatmap_cell_tooltip(day: date, count: int) -> str:
    """Return hover text for one contribution-calendar cell."""
    unit = "task" if count == 1 else "tasks"
    return f"{day.isoformat()}: {count} {unit}"


def latest_active_day(stats: TickTickPeriodStats) -> date | None:
    """Return the most recent day in ``stats`` that has at least one completion."""
    if not stats.counts_by_day:
        return None
    return max(stats.counts_by_day)


def longest_streak_days(counts_by_day: dict[date, int], start_date: date, end_date: date) -> int:
    """Return the longest run of consecutive active days inside the period."""
    best = 0
    run = 0
    day = start_date
    while day <= end_date:
        if counts_by_day.get(day, 0) > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0
        day += timedelta(days=1)
    return best


def month_starts_going_back(months_count: int, *, today: date) -> list[date]:
    """Return first-of-month dates newest first for ``months_count`` months ending at ``today``."""
    count = max(int(months_count), 0)
    if count <= 0:
        return []
    cursor = date(today.year, today.month, 1)
    result: list[date] = []
    for _ in range(count):
        result.append(cursor)
        cursor = date(cursor.year - 1, 12, 1) if cursor.month == 1 else date(cursor.year, cursor.month - 1, 1)
    return result


def resolve_period(
    *,
    year: int | None,
    today: date | None = None,
) -> tuple[date, date]:
    """Return inclusive ``(start, end)`` for a calendar year or last 365 days."""
    today_local = today or datetime.now().astimezone().date()
    if year is None:
        return today_local - timedelta(days=365), today_local
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    if year == today_local.year:
        end = today_local
    return start, end


def _annotate_bars(ax: Any, bars: Any) -> None:
    for bar in bars:
        height = bar.get_height()
        if height <= 0:
            continue
        ax.annotate(
            f"{int(height)}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def _lerp(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    t: float,
) -> tuple[float, float, float]:
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t,
    )


def _plot_month_line(ax: Any, item: TickTickMonthSeries, *, linewidth: float, linestyle: str) -> None:
    x_values = [point[0] for point in item.points]
    y_values = [point[1] for point in item.points]
    ax.plot(
        x_values,
        y_values,
        color=item.color,
        linestyle=linestyle,
        linewidth=linewidth,
        alpha=0.85,
        label=item.label,
        marker="o" if len(x_values) <= _MONTH_LINE_MARKER_THRESHOLD else None,
        markersize=4,
    )
    if x_values and y_values:
        last_x = x_values[-1]
        last_y = y_values[-1]
        month_year = item.label.replace(" (Current)", "")
        ax.annotate(
            f"{month_year}: {last_y}",
            (last_x, last_y),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            **chart_annotation_style(),
        )
