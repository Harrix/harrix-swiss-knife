---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_process_charts.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HabitPeriodStats`](#%EF%B8%8F-class-habitperiodstats)
- [🔧 Function `aggregate_daily_values`](#-function-aggregate_daily_values)
- [🔧 Function `build_habit_by_month_chart`](#-function-build_habit_by_month_chart)
- [🔧 Function `build_habit_compare_chart`](#-function-build_habit_compare_chart)
- [🔧 Function `compare_last_months_series`](#-function-compare_last_months_series)
- [🔧 Function `compare_same_months_series`](#-function-compare_same_months_series)
- [🔧 Function `counts_by_month`](#-function-counts_by_month)
- [🔧 Function `cumulative_habit_month_points`](#-function-cumulative_habit_month_points)
- [🔧 Function `habit_calendar_model`](#-function-habit_calendar_model)
- [🔧 Function `habit_is_bool_flag`](#-function-habit_is_bool_flag)
- [🔧 Function `habit_legend_colors`](#-function-habit_legend_colors)
- [🔧 Function `habit_period_stats`](#-function-habit_period_stats)
- [🔧 Function `habit_timeline_bars`](#-function-habit_timeline_bars)
- [🔧 Function `habit_token_color`](#-function-habit_token_color)
- [🔧 Function `recorded_daily`](#-function-recorded_daily)

</details>

## 🏛️ Class `HabitPeriodStats`

```python
class HabitPeriodStats
```

Counts for the compact Habits chart summary. Missing days are not failures.

<details>
<summary>Code:</summary>

```python
class HabitPeriodStats:

    completed: int
    counted: int
    completion_percent: float | None
    current_streak: int
    longest_streak: int
    total: int
    is_bool: bool
```

</details>

## 🔧 Function `aggregate_daily_values`

```python
def aggregate_daily_values(rows: Sequence[tuple[str, int]], *, is_bool: bool) -> dict[date, int]
```

Sum process rows per calendar day (done-day count or numeric sum).

<details>
<summary>Code:</summary>

```python
def aggregate_daily_values(
    rows: Sequence[tuple[str, int]],
    *,
    is_bool: bool,
) -> dict[date, int]:
    daily: dict[date, int] = {}
    for raw_date, raw_value in rows:
        day = date.fromisoformat(str(raw_date)[:10])
        contribution = _day_contribution(int(raw_value), is_bool=is_bool)
        if contribution == 0 and is_bool:
            continue
        daily[day] = daily.get(day, 0) + contribution
    return daily
```

</details>

## 🔧 Function `build_habit_by_month_chart`

```python
def build_habit_by_month_chart(month_counts: Sequence[tuple[date, int]], *, habit_name: str, is_bool: bool, figsize: tuple[float, float]) -> Figure
```

Bar chart of monthly habit totals.

<details>
<summary>Code:</summary>

```python
def build_habit_by_month_chart(
    month_counts: Sequence[tuple[date, int]],
    *,
    habit_name: str,
    is_bool: bool,
    figsize: tuple[float, float],
) -> Figure:
    measure = "Done days" if is_bool else "Total"
    figure = build_month_counts_chart(month_counts, figsize=figsize)
    ax = figure.axes[0] if figure.axes else figure.add_subplot(111)
    ax.set_ylabel(measure)
    ax.set_title(f"{habit_name}: {measure} by month (last {len(month_counts)})")
    return figure
```

</details>

## 🔧 Function `build_habit_compare_chart`

```python
def build_habit_compare_chart(series: Sequence[TickTickMonthSeries], *, title: str, is_bool: bool, figsize: tuple[float, float]) -> Figure
```

Overlay cumulative month lines for a habit.

<details>
<summary>Code:</summary>

```python
def build_habit_compare_chart(
    series: Sequence[TickTickMonthSeries],
    *,
    title: str,
    is_bool: bool,
    figsize: tuple[float, float],
) -> Figure:
    ylabel = "Cumulative done days" if is_bool else "Cumulative total"
    figure = build_compare_months_chart(series, title=title, figsize=figsize)
    if figure.axes:
        figure.axes[0].set_ylabel(ylabel)
    return figure
```

</details>

## 🔧 Function `compare_last_months_series`

```python
def compare_last_months_series(daily: dict[date, int], months_count: int, *, today: date | None = None) -> list[TickTickMonthSeries]
```

Cumulative day-of-month lines for the last ``months_count`` months.

<details>
<summary>Code:</summary>

```python
def compare_last_months_series(
    daily: dict[date, int],
    months_count: int,
    *,
    today: date | None = None,
) -> list[TickTickMonthSeries]:
    today_local = today or datetime.now().astimezone().date()
    return [
        TickTickMonthSeries(
            year=window.year,
            month=window.month,
            label=window.label,
            color=window.color,
            is_current=window.is_current,
            points=cumulative_habit_month_points(daily, window.year, window.month, end_day=window.end_day),
        )
        for window in compare_last_month_windows(months_count, today=today_local)
    ]
```

</details>

## 🔧 Function `compare_same_months_series`

```python
def compare_same_months_series(daily: dict[date, int], month: int, years_count: int, *, today: date | None = None) -> list[TickTickMonthSeries]
```

Cumulative lines for the same calendar month across recent years.

<details>
<summary>Code:</summary>

```python
def compare_same_months_series(
    daily: dict[date, int],
    month: int,
    years_count: int,
    *,
    today: date | None = None,
) -> list[TickTickMonthSeries]:
    today_local = today or datetime.now().astimezone().date()
    return [
        TickTickMonthSeries(
            year=window.year,
            month=window.month,
            label=window.label,
            color=window.color,
            is_current=window.is_current,
            points=cumulative_habit_month_points(daily, window.year, window.month, end_day=window.end_day),
        )
        for window in compare_same_month_windows(month, years_count, today=today_local)
    ]
```

</details>

## 🔧 Function `counts_by_month`

```python
def counts_by_month(daily: dict[date, int], months_count: int, *, today: date | None = None) -> list[tuple[date, int]]
```

Return ``(month_start, total)`` oldest→newest for the last ``months_count`` months.

<details>
<summary>Code:</summary>

```python
def counts_by_month(
    daily: dict[date, int],
    months_count: int,
    *,
    today: date | None = None,
) -> list[tuple[date, int]]:
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
```

</details>

## 🔧 Function `cumulative_habit_month_points`

```python
def cumulative_habit_month_points(daily: dict[date, int], year: int, month: int, *, end_day: int) -> list[tuple[int, int]]
```

Return ``(day_of_month, cumulative_total)`` through ``end_day``.

<details>
<summary>Code:</summary>

```python
def cumulative_habit_month_points(
    daily: dict[date, int],
    year: int,
    month: int,
    *,
    end_day: int,
) -> list[tuple[int, int]]:
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
```

</details>

## 🔧 Function `habit_calendar_model`

```python
def habit_calendar_model(recorded: dict[date, int], start: date, end: date, *, is_bool: bool) -> tuple[dict[date, str | None], dict[date, str], list[tuple[str, str]], int]
```

Return cell tokens, numeric marks, legend tokens, and the positive bin count.

`None` means no database row. A stored `0` is not the same token.

<details>
<summary>Code:</summary>

```python
def habit_calendar_model(
    recorded: dict[date, int],
    start: date,
    end: date,
    *,
    is_bool: bool,
) -> tuple[dict[date, str | None], dict[date, str], list[tuple[str, str]], int]:
    tokens: dict[date, str | None] = {}
    marks: dict[date, str] = {}
    saw_absent = False
    saw_zero = False
    saw_done = False
    saw_negative = False
    positives: list[int] = []
    for day in calendar_days(start, end):
        if day not in recorded:
            tokens[day] = None
            saw_absent = True
            continue
        value = int(recorded[day])
        if is_bool:
            if value > 0:
                tokens[day] = "done"
                saw_done = True
            else:
                tokens[day] = "not_done"
                saw_zero = True
            continue
        if value == 0:
            tokens[day] = "zero"
            saw_zero = True
        elif value < 0:
            tokens[day] = "negative"
            saw_negative = True
            marks[day] = str(value)
        else:
            positives.append(value)
            tokens[day] = "positive"
            marks[day] = str(value)

    ranges = [] if is_bool else quantile_intensity_ranges(positives, max_bins=4)
    if not is_bool:
        for day, state in list(tokens.items()):
            if state != "positive":
                continue
            index = 0
            value = int(recorded[day])
            for bin_index, (lo, hi) in enumerate(ranges):
                if lo <= value <= hi:
                    index = bin_index
                    break
            tokens[day] = f"bin:{index}"

    legend: list[tuple[str, str]] = []
    if saw_absent:
        legend.append(("absent", "No data"))
    if is_bool:
        if saw_zero:
            legend.append(("not_done", "Not done"))
        if saw_done:
            legend.append(("done", "Done"))
    else:
        if saw_zero:
            legend.append(("zero", "0"))
        if saw_negative:
            legend.append(("negative", "Negative"))
        for index, (lo, hi) in enumerate(ranges):
            label = str(lo) if lo == hi else f"{lo}-{hi}"
            legend.append((f"bin:{index}", label))
    return tokens, marks, legend, len(ranges)
```

</details>

## 🔧 Function `habit_is_bool_flag`

```python
def habit_is_bool_flag(db_rows: list[Any] | None) -> bool
```

Return whether habit metadata marks the habit as boolean-only.

<details>
<summary>Code:</summary>

```python
def habit_is_bool_flag(db_rows: list[Any] | None) -> bool:
    if not db_rows or not db_rows[0]:
        return False
    raw = db_rows[0][0]
    return raw == 1
```

</details>

## 🔧 Function `habit_legend_colors`

```python
def habit_legend_colors(legend: list[tuple[str, str]], *, bin_count: int) -> list[tuple[str, str]]
```

Resolve legend tokens to theme colors. No-data uses a faint swatch, not the zero fill.

<details>
<summary>Code:</summary>

```python
def habit_legend_colors(legend: list[tuple[str, str]], *, bin_count: int) -> list[tuple[str, str]]:
    painted: list[tuple[str, str]] = []
    for state, label in legend:
        if state == "absent":
            painted.append((heatmap_absent_color(), label))
            continue
        color = habit_token_color(state, bin_count=bin_count)
        if color is not None:
            painted.append((color, label))
    return painted
```

</details>

## 🔧 Function `habit_period_stats`

```python
def habit_period_stats(recorded: dict[date, int], start: date, end: date, *, is_bool: bool, today: date) -> HabitPeriodStats
```

Summarize recorded days only. Future days and days with no row are ignored.

<details>
<summary>Code:</summary>

```python
def habit_period_stats(
    recorded: dict[date, int],
    start: date,
    end: date,
    *,
    is_bool: bool,
    today: date,
) -> HabitPeriodStats:
    last = min(end, today)
    active: dict[date, int] = {}
    completed = 0
    counted = 0
    total = 0
    for day, raw_value in recorded.items():
        if day < start or day > last:
            continue
        value = int(raw_value)
        total += value
        if is_bool:
            counted += 1
            if value > 0:
                completed += 1
                active[day] = 1
            else:
                active[day] = 0
        elif value > 0:
            completed += 1
            active[day] = value
    percent = (100.0 * completed / counted) if is_bool and counted else None
    return HabitPeriodStats(
        completed=completed,
        counted=counted,
        completion_percent=percent,
        current_streak=current_streak_days(active, last),
        longest_streak=longest_streak_days(active, start, last) if last >= start else 0,
        total=total,
        is_bool=is_bool,
    )
```

</details>

## 🔧 Function `habit_timeline_bars`

```python
def habit_timeline_bars(recorded: dict[date, int], start: date, end: date, *, is_bool: bool, today: date) -> tuple[list[TimelineBar], bool]
```

Weekly completion bars, or weekly numeric totals.

The second value is `True` when the axis is a 0-100 percent scale.

<details>
<summary>Code:</summary>

```python
def habit_timeline_bars(
    recorded: dict[date, int],
    start: date,
    end: date,
    *,
    is_bool: bool,
    today: date,
) -> tuple[list[TimelineBar], bool]:
    last = min(end, today)
    bars: list[TimelineBar] = []
    for span_start, span_end in week_spans(start, last):
        if is_bool:
            counted_days = [day for day in calendar_days(span_start, span_end) if day in recorded]
            if not counted_days:
                continue
            done = sum(1 for day in counted_days if recorded[day] > 0)
            counted = len(counted_days)
            percent = 100.0 * done / counted
            window_start = span_end - timedelta(days=29)
            window = [day for day in calendar_days(window_start, span_end) if start <= day <= last and day in recorded]
            rolling = (100.0 * sum(1 for day in window if recorded[day] > 0) / len(window)) if window else None
            tooltip = (
                f"{fmt_date(span_start)} - {fmt_date(span_end)}\nDone: {done}\nCounted days: {counted}\n{percent:.0f}%"
            )
            bars.append(TimelineBar(span_start, span_end, percent, rolling, tooltip))
            continue
        present = [day for day in calendar_days(span_start, span_end) if day in recorded]
        if not present:
            continue
        total = sum(int(recorded[day]) for day in present)
        window = [
            day
            for day in calendar_days(span_end - timedelta(days=6), span_end)
            if start <= day <= last and day in recorded
        ]
        average = (sum(int(recorded[day]) for day in window) / len(window)) if window else None
        tooltip = (
            f"{fmt_date(span_start)} - {fmt_date(span_end)}\n"
            f"Total: {fmt_number(total, decimals=0)}\nRecorded days: {len(present)}"
        )
        bars.append(TimelineBar(span_start, span_end, float(total), average, tooltip))
    return bars, is_bool
```

</details>

## 🔧 Function `habit_token_color`

```python
def habit_token_color(state: str | None, *, bin_count: int) -> str | None
```

Map a calendar token to a fill. `None` and `absent` stay unfilled.

<details>
<summary>Code:</summary>

```python
def habit_token_color(state: str | None, *, bin_count: int) -> str | None:
    if state is None or state == "absent":
        return None
    if state in {"not_done", "zero"}:
        return heatmap_zero_color()
    if state == "done":
        return chart_series_color(0)
    if state == "negative":
        return FluentTheme.instance().palette().caution.name()
    if state.startswith("bin:"):
        colors = accent_heatmap_colors(max(bin_count, 1))
        if not colors:
            return chart_series_color(0)
        index = int(state.split(":", maxsplit=1)[1])
        return colors[max(0, min(index, len(colors) - 1))]
    return heatmap_zero_color()
```

</details>

## 🔧 Function `recorded_daily`

```python
def recorded_daily(rows: Sequence[tuple[Any, Any]]) -> dict[date, int]
```

Sum raw process rows per day. Days with no row are omitted.

<details>
<summary>Code:</summary>

```python
def recorded_daily(rows: Sequence[tuple[Any, Any]]) -> dict[date, int]:
    daily: dict[date, int] = {}
    for raw_date, raw_value in rows:
        day = date.fromisoformat(str(raw_date)[:10])
        daily[day] = daily.get(day, 0) + int(raw_value)
    return daily
```

</details>
