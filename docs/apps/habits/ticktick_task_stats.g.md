---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ticktick_task_stats.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TickTickHeatmapResult`](#%EF%B8%8F-class-ticktickheatmapresult)
- [🏛️ Class `TickTickMonthSeries`](#%EF%B8%8F-class-ticktickmonthseries)
- [🏛️ Class `TickTickPeriodStats`](#%EF%B8%8F-class-ticktickperiodstats)
- [🔧 Function `aggregate_completions`](#-function-aggregate_completions)
- [🔧 Function `available_years`](#-function-available_years)
- [🔧 Function `build_compare_months_chart`](#-function-build_compare_months_chart)
- [🔧 Function `build_contribution_heatmap`](#-function-build_contribution_heatmap)
- [🔧 Function `build_month_counts_chart`](#-function-build_month_counts_chart)
- [🔧 Function `build_year_counts_chart`](#-function-build_year_counts_chart)
- [🔧 Function `compare_last_months_series`](#-function-compare_last_months_series)
- [🔧 Function `compare_same_months_series`](#-function-compare_same_months_series)
- [🔧 Function `counts_by_month`](#-function-counts_by_month)
- [🔧 Function `counts_by_year`](#-function-counts_by_year)
- [🔧 Function `cumulative_month_points`](#-function-cumulative_month_points)
- [🔧 Function `current_streak_days`](#-function-current_streak_days)
- [🔧 Function `day_from_heatmap_click`](#-function-day_from_heatmap_click)
- [🔧 Function `filter_completions_for_period`](#-function-filter_completions_for_period)
- [🔧 Function `format_period_summary`](#-function-format_period_summary)
- [🔧 Function `heatmap_cell_tooltip`](#-function-heatmap_cell_tooltip)
- [🔧 Function `latest_active_day`](#-function-latest_active_day)
- [🔧 Function `longest_streak_days`](#-function-longest_streak_days)
- [🔧 Function `month_starts_going_back`](#-function-month_starts_going_back)
- [🔧 Function `resolve_period`](#-function-resolve_period)

</details>

## 🏛️ Class `TickTickHeatmapResult`

```python
class TickTickHeatmapResult
```

Matplotlib figure plus click-mapping positions for the contribution calendar.

<details>
<summary>Code:</summary>

```python
class TickTickHeatmapResult:

    figure: Figure
    positions: dict[date, tuple[float, float]]
    start_date: date
    end_date: date
```

</details>

## 🏛️ Class `TickTickMonthSeries`

```python
class TickTickMonthSeries
```

One month line for last-months / same-months comparison charts.

<details>
<summary>Code:</summary>

```python
class TickTickMonthSeries:

    year: int
    month: int
    label: str
    color: str
    is_current: bool
    points: list[tuple[int, int]] = field(default_factory=list)
```

</details>

## 🏛️ Class `TickTickPeriodStats`

```python
class TickTickPeriodStats
```

Summary metrics for completions in a date window.

<details>
<summary>Code:</summary>

```python
class TickTickPeriodStats:

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
```

</details>

## 🔧 Function `aggregate_completions`

```python
def aggregate_completions(completions: Sequence[TickTickCompletion], start_date: date, end_date: date, *, project_id: str | None = None, today: date | None = None) -> TickTickPeriodStats
```

Aggregate filtered completions into per-day counts and streak metrics.

<details>
<summary>Code:</summary>

```python
def aggregate_completions(
    completions: Sequence[TickTickCompletion],
    start_date: date,
    end_date: date,
    *,
    project_id: str | None = None,
    today: date | None = None,
) -> TickTickPeriodStats:
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
```

</details>

## 🔧 Function `available_years`

```python
def available_years(completions: Sequence[TickTickCompletion], *, today_year: int | None = None) -> list[int]
```

Return sorted calendar years that have at least one completion, capped at today.

<details>
<summary>Code:</summary>

```python
def available_years(completions: Sequence[TickTickCompletion], *, today_year: int | None = None) -> list[int]:
    years = {item.completed_at.year for item in completions}
    cap = today_year if today_year is not None else datetime.now().astimezone().year
    return sorted(year for year in years if year <= cap)
```

</details>

## 🔧 Function `build_compare_months_chart`

```python
def build_compare_months_chart(series: Sequence[TickTickMonthSeries], *, title: str, figsize: tuple[float, float] = (12.0, 4.5), dpi: int = 100) -> Figure
```

Overlay cumulative completion lines for several months (Fitness-style).

<details>
<summary>Code:</summary>

```python
def build_compare_months_chart(
    series: Sequence[TickTickMonthSeries],
    *,
    title: str,
    figsize: tuple[float, float] = (12.0, 4.5),
    dpi: int = 100,
) -> Figure:
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
```

</details>

## 🔧 Function `build_contribution_heatmap`

```python
def build_contribution_heatmap(stats: TickTickPeriodStats, *, figsize: tuple[float, float] = (14.0, 3.2), dpi: int = 100) -> TickTickHeatmapResult
```

Build a green GitHub-like contribution calendar for `[`stats`](../icons/thumb_cache.g.md#%EF%B8%8F-method-stats)`.

<details>
<summary>Code:</summary>

```python
def build_contribution_heatmap(
    stats: TickTickPeriodStats,
    *,
    figsize: tuple[float, float] = (14.0, 3.2),
    dpi: int = 100,
) -> TickTickHeatmapResult:
    start_date = stats.start_date
    end_date = stats.end_date
    figure = themed_figure(figsize=figsize, dpi=dpi)
    ax = figure.add_subplot(111)

    display_values = set(stats.counts_by_day.values())
    display_values.add(0)
    pos_values = sorted(v for v in display_values if v > 0)

    value_to_mapped: dict[int, int] = {0: 0, **{value: index for index, value in enumerate(pos_values, start=1)}}
    colors_list: list[tuple[float, float, float]] = [to_rgb(_GRAY)]
    if pos_values:
        n = len(pos_values)
        for index in range(n):
            t = 0.0 if n == 1 else index / (n - 1)
            colors_list.append(_lerp(to_rgb(_LIGHT_GREEN), to_rgb(_DARK_GREEN), t))
    else:
        colors_list.append(to_rgb(_GRAY))

    mapped_vmax = max(value_to_mapped.values()) if value_to_mapped else 1
    cmap = LinearSegmentedColormap.from_list("ticktick_contrib", colors_list, N=len(colors_list))

    day_keys = list(stats.counts_by_day.keys())
    mapped_values = [value_to_mapped.get(int(stats.counts_by_day[day]), 0) for day in day_keys]
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
        vmax=max(mapped_vmax, 1),
        cmap=cmap,
        boxstyle="round",
        ax=ax,
    )
    apply_habit_heatmap_month_separation(ax, cell_patches, start_date, end_date)

    legend_order = [0, *pos_values]
    norm = Normalize(vmin=0, vmax=max(mapped_vmax, 1))
    handles: list[Patch] = []
    for value in legend_order:
        if value == 0:
            color: Any = _GRAY
        else:
            color = cmap(norm(value_to_mapped[value]))
        handles.append(Patch(facecolor=color, edgecolor="none", label=str(value)))
    if handles:
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
    else:
        figure.tight_layout()
    positions, _labels, _width = habit_heatmap_month_separated_positions(start_date, end_date)
    return TickTickHeatmapResult(
        figure=figure,
        positions=positions,
        start_date=start_date,
        end_date=end_date,
    )
```

</details>

## 🔧 Function `build_month_counts_chart`

```python
def build_month_counts_chart(month_counts: Sequence[tuple[date, int]], *, figsize: tuple[float, float] = (12.0, 4.5), dpi: int = 100) -> Figure
```

Bar chart of completed-task totals by calendar month.

<details>
<summary>Code:</summary>

```python
def build_month_counts_chart(
    month_counts: Sequence[tuple[date, int]],
    *,
    figsize: tuple[float, float] = (12.0, 4.5),
    dpi: int = 100,
) -> Figure:
    figure = themed_figure(figsize=figsize, dpi=dpi)
    ax = figure.add_subplot(111)
    if not month_counts:
        ax.set_title("Completed tasks by month")
        ax.text(0.5, 0.5, "No completed tasks", ha="center", va="center", transform=ax.transAxes)
        figure.tight_layout()
        return figure
    labels = [start.strftime("%b %Y") for start, _count in month_counts]
    values = [count for _start, count in month_counts]
    bars = ax.bar(range(len(labels)), values, color=_BAR_GREEN, width=0.7)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Month")
    ax.set_ylabel("Completed tasks")
    ax.set_title(f"Completed tasks by month (last {len(month_counts)})")
    ax.grid(visible=True, axis="y", alpha=0.3)
    _annotate_bars(ax, bars)
    figure.tight_layout()
    return figure
```

</details>

## 🔧 Function `build_year_counts_chart`

```python
def build_year_counts_chart(year_counts: Sequence[tuple[int, int]], *, figsize: tuple[float, float] = (12.0, 4.5), dpi: int = 100) -> Figure
```

Bar chart of completed-task totals by calendar year.

<details>
<summary>Code:</summary>

```python
def build_year_counts_chart(
    year_counts: Sequence[tuple[int, int]],
    *,
    figsize: tuple[float, float] = (12.0, 4.5),
    dpi: int = 100,
) -> Figure:
    figure = themed_figure(figsize=figsize, dpi=dpi)
    ax = figure.add_subplot(111)
    if not year_counts:
        ax.set_title("Completed tasks by year")
        ax.text(0.5, 0.5, "No completed tasks", ha="center", va="center", transform=ax.transAxes)
        figure.tight_layout()
        return figure
    labels = [str(year) for year, _count in year_counts]
    values = [count for _year, count in year_counts]
    bars = ax.bar(range(len(labels)), values, color=_BAR_GREEN, width=0.7)
    ax.set_xticks(range(len(labels)))
    rotate = len(labels) > _YEAR_LABEL_ROTATE_THRESHOLD
    ax.set_xticklabels(labels, rotation=45 if rotate else 0, ha="right" if rotate else "center")
    ax.set_xlabel("Year")
    ax.set_ylabel("Completed tasks")
    ax.set_title("Completed tasks by year")
    ax.grid(visible=True, axis="y", alpha=0.3)
    _annotate_bars(ax, bars)
    figure.tight_layout()
    return figure
```

</details>

## 🔧 Function `compare_last_months_series`

```python
def compare_last_months_series(completions: Sequence[TickTickCompletion], months_count: int, *, project_id: str | None = None, today: date | None = None) -> list[TickTickMonthSeries]
```

Build cumulative day-of-month series for the last ``months_count`` months (newest first).

<details>
<summary>Code:</summary>

```python
def compare_last_months_series(
    completions: Sequence[TickTickCompletion],
    months_count: int,
    *,
    project_id: str | None = None,
    today: date | None = None,
) -> list[TickTickMonthSeries]:
    today_local = today or datetime.now().astimezone().date()
    series: list[TickTickMonthSeries] = []
    for index, start in enumerate(month_starts_going_back(months_count, today=today_local)):
        days_in_month = calendar.monthrange(start.year, start.month)[1]
        is_current = index == 0
        end_day = min(today_local.day, days_in_month) if is_current else days_in_month
        label = start.strftime("%B %Y")
        if is_current:
            label = f"{label} (Current)"
        color = _COMPARE_CURRENT if is_current else _COMPARE_PALETTE[(index - 1) % len(_COMPARE_PALETTE)]
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
```

</details>

## 🔧 Function `compare_same_months_series`

```python
def compare_same_months_series(completions: Sequence[TickTickCompletion], month: int, years_count: int, *, project_id: str | None = None, today: date | None = None) -> list[TickTickMonthSeries]
```

Build cumulative series for the same calendar month across recent years (newest first).

<details>
<summary>Code:</summary>

```python
def compare_same_months_series(
    completions: Sequence[TickTickCompletion],
    month: int,
    years_count: int,
    *,
    project_id: str | None = None,
    today: date | None = None,
) -> list[TickTickMonthSeries]:
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
            color = _COMPARE_PALETTE[color_index % len(_COMPARE_PALETTE)]
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
```

</details>

## 🔧 Function `counts_by_month`

```python
def counts_by_month(completions: Sequence[TickTickCompletion], months_count: int, *, project_id: str | None = None, today: date | None = None) -> list[tuple[date, int]]
```

Return ``(month_start, count)`` oldest→newest for the last ``months_count`` months.

<details>
<summary>Code:</summary>

```python
def counts_by_month(
    completions: Sequence[TickTickCompletion],
    months_count: int,
    *,
    project_id: str | None = None,
    today: date | None = None,
) -> list[tuple[date, int]]:
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
```

</details>

## 🔧 Function `counts_by_year`

```python
def counts_by_year(completions: Sequence[TickTickCompletion], *, project_id: str | None = None, today: date | None = None) -> list[tuple[int, int]]
```

Return ``(year, count)`` ascending for years with completions (and empty gaps filled).

<details>
<summary>Code:</summary>

```python
def counts_by_year(
    completions: Sequence[TickTickCompletion],
    *,
    project_id: str | None = None,
    today: date | None = None,
) -> list[tuple[int, int]]:
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
```

</details>

## 🔧 Function `cumulative_month_points`

```python
def cumulative_month_points(completions: Sequence[TickTickCompletion], year: int, month: int, *, end_day: int, project_id: str | None = None) -> list[tuple[int, int]]
```

Return ``(day_of_month, cumulative_count)`` through ``end_day`` for one calendar month.

<details>
<summary>Code:</summary>

```python
def cumulative_month_points(
    completions: Sequence[TickTickCompletion],
    year: int,
    month: int,
    *,
    end_day: int,
    project_id: str | None = None,
) -> list[tuple[int, int]]:
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
```

</details>

## 🔧 Function `current_streak_days`

```python
def current_streak_days(counts_by_day: dict[date, int], anchor: date) -> int
```

Count consecutive active days ending at ``anchor`` (or ``anchor - 1`` if today empty).

<details>
<summary>Code:</summary>

```python
def current_streak_days(counts_by_day: dict[date, int], anchor: date) -> int:
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
```

</details>

## 🔧 Function `day_from_heatmap_click`

```python
def day_from_heatmap_click(result: TickTickHeatmapResult, x: float, y: float) -> date | None
```

Map axes data coordinates from a canvas click to a calendar day.

<details>
<summary>Code:</summary>

```python
def day_from_heatmap_click(
    result: TickTickHeatmapResult,
    x: float,
    y: float,
) -> date | None:
    return date_at_heatmap_point(result.positions, x, y)
```

</details>

## 🔧 Function `filter_completions_for_period`

```python
def filter_completions_for_period(completions: Sequence[TickTickCompletion], start_date: date, end_date: date, *, project_id: str | None = None) -> list[TickTickCompletion]
```

Keep completions in ``[start_date, end_date]``, optionally for one project.

<details>
<summary>Code:</summary>

```python
def filter_completions_for_period(
    completions: Sequence[TickTickCompletion],
    start_date: date,
    end_date: date,
    *,
    project_id: str | None = None,
) -> list[TickTickCompletion]:
    selected: list[TickTickCompletion] = []
    for item in completions:
        if project_id and item.project_id != project_id:
            continue
        day = item.completed_at.date()
        if start_date <= day <= end_date:
            selected.append(item)
    return selected
```

</details>

## 🔧 Function `format_period_summary`

```python
def format_period_summary(stats: TickTickPeriodStats) -> str
```

Return a one-line summary for the TickTick stats tab header.

<details>
<summary>Code:</summary>

```python
def format_period_summary(stats: TickTickPeriodStats) -> str:
    busiest = "—"
    if stats.busiest_day is not None and stats.busiest_count > 0:
        busiest = f"{stats.busiest_day.isoformat()} ({stats.busiest_count})"
    return (
        f"Completions: {stats.total_completions} · Active days: {stats.active_days} · "
        f"Current streak: {stats.current_streak} · Longest streak: {stats.longest_streak} · "
        f"Busiest day: {busiest}"
    )
```

</details>

## 🔧 Function `heatmap_cell_tooltip`

```python
def heatmap_cell_tooltip(day: date, count: int) -> str
```

Return hover text for one contribution-calendar cell.

<details>
<summary>Code:</summary>

```python
def heatmap_cell_tooltip(day: date, count: int) -> str:
    unit = "task" if count == 1 else "tasks"
    return f"{day.isoformat()}: {count} {unit}"
```

</details>

## 🔧 Function `latest_active_day`

```python
def latest_active_day(stats: TickTickPeriodStats) -> date | None
```

Return the most recent day in `[`stats`](../icons/thumb_cache.g.md#%EF%B8%8F-method-stats)` that has at least one completion.

<details>
<summary>Code:</summary>

```python
def latest_active_day(stats: TickTickPeriodStats) -> date | None:
    if not stats.counts_by_day:
        return None
    return max(stats.counts_by_day)
```

</details>

## 🔧 Function `longest_streak_days`

```python
def longest_streak_days(counts_by_day: dict[date, int], start_date: date, end_date: date) -> int
```

Return the longest run of consecutive active days inside the period.

<details>
<summary>Code:</summary>

```python
def longest_streak_days(counts_by_day: dict[date, int], start_date: date, end_date: date) -> int:
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
```

</details>

## 🔧 Function `month_starts_going_back`

```python
def month_starts_going_back(months_count: int, *, today: date) -> list[date]
```

Return first-of-month dates newest first for ``months_count`` months ending at ``today``.

<details>
<summary>Code:</summary>

```python
def month_starts_going_back(months_count: int, *, today: date) -> list[date]:
    count = max(int(months_count), 0)
    if count <= 0:
        return []
    cursor = date(today.year, today.month, 1)
    result: list[date] = []
    for _ in range(count):
        result.append(cursor)
        cursor = date(cursor.year - 1, 12, 1) if cursor.month == 1 else date(cursor.year, cursor.month - 1, 1)
    return result
```

</details>

## 🔧 Function `resolve_period`

```python
def resolve_period(*, year: int | None, today: date | None = None) -> tuple[date, date]
```

Return inclusive ``(start, end)`` for a calendar year or last 365 days.

<details>
<summary>Code:</summary>

```python
def resolve_period(
    *,
    year: int | None,
    today: date | None = None,
) -> tuple[date, date]:
    today_local = today or datetime.now().astimezone().date()
    if year is None:
        return today_local - timedelta(days=365), today_local
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    if year == today_local.year:
        end = today_local
    return start, end
```

</details>
