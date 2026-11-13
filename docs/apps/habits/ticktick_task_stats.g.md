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
- [🏛️ Class `TickTickPeriodStats`](#%EF%B8%8F-class-ticktickperiodstats)
- [🔧 Function `aggregate_completions`](#-function-aggregate_completions)
- [🔧 Function `available_years`](#-function-available_years)
- [🔧 Function `build_contribution_heatmap`](#-function-build_contribution_heatmap)
- [🔧 Function `current_streak_days`](#-function-current_streak_days)
- [🔧 Function `day_from_heatmap_click`](#-function-day_from_heatmap_click)
- [🔧 Function `filter_completions_for_period`](#-function-filter_completions_for_period)
- [🔧 Function `format_period_summary`](#-function-format_period_summary)
- [🔧 Function `longest_streak_days`](#-function-longest_streak_days)
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
