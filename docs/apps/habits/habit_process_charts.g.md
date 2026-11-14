---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_process_charts.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `aggregate_daily_values`](#-function-aggregate_daily_values)
- [🔧 Function `build_habit_by_month_chart`](#-function-build_habit_by_month_chart)
- [🔧 Function `build_habit_compare_chart`](#-function-build_habit_compare_chart)
- [🔧 Function `compare_last_months_series`](#-function-compare_last_months_series)
- [🔧 Function `compare_same_months_series`](#-function-compare_same_months_series)
- [🔧 Function `counts_by_month`](#-function-counts_by_month)
- [🔧 Function `cumulative_habit_month_points`](#-function-cumulative_habit_month_points)
- [🔧 Function `habit_is_bool_flag`](#-function-habit_is_bool_flag)

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
