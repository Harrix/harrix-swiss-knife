---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `calendar_heatmap.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_habit_heatmap_month_separation`](#-function-apply_habit_heatmap_month_separation)
- [🔧 Function `date_at_heatmap_point`](#-function-date_at_heatmap_point)
- [🔧 Function `habit_heatmap_month_column_count`](#-function-habit_heatmap_month_column_count)
- [🔧 Function `habit_heatmap_month_ranges`](#-function-habit_heatmap_month_ranges)
- [🔧 Function `habit_heatmap_month_separated_positions`](#-function-habit_heatmap_month_separated_positions)
- [🔧 Function `habit_heatmap_week_start`](#-function-habit_heatmap_week_start)
- [🔧 Function `habit_heatmap_weekday_index`](#-function-habit_heatmap_weekday_index)
- [🔧 Function `heatmap_year_after_step`](#-function-heatmap_year_after_step)
- [🔧 Function `numeric_habit_heatmap_cell_labels`](#-function-numeric_habit_heatmap_cell_labels)

</details>

## 🔧 Function `apply_habit_heatmap_month_separation`

```python
def apply_habit_heatmap_month_separation(ax: Any, cell_patches: list[Any], start_date: date, end_date: date, *, cell_inset: float = HEATMAP_CELL_INSET, month_gap: float = HEATMAP_MONTH_GAP) -> None
```

Shift dayplot cells and month labels into LeetCode-style month blocks.

<details>
<summary>Code:</summary>

```python
def apply_habit_heatmap_month_separation(
    ax: Any,
    cell_patches: list[Any],
    start_date: date,
    end_date: date,
    *,
    cell_inset: float = HEATMAP_CELL_INSET,
    month_gap: float = HEATMAP_MONTH_GAP,
) -> None:
    positions, month_labels, total_width = habit_heatmap_month_separated_positions(
        start_date,
        end_date,
        month_gap=month_gap,
    )
    for index, patch in enumerate(cell_patches):
        week_x, weekday_y = positions[start_date + timedelta(days=index)]
        patch.set_x(week_x + cell_inset)
        patch.set_y(weekday_y + cell_inset)

    month_texts = [text for text in ax.texts if text.get_position()[1] > HEATMAP_MONTH_LABEL_Y_MIN]
    for text, (_label, month_x) in zip(month_texts, month_labels, strict=False):
        text.set_position((month_x + HEATMAP_MONTH_LABEL_X_INSET, text.get_position()[1]))

    ax.set_xlim(-0.5, total_width + 0.5)
```

</details>

## 🔧 Function `date_at_heatmap_point`

```python
def date_at_heatmap_point(positions: dict[date, tuple[float, float]], x: float, y: float, *, cell_inset: float = HEATMAP_CELL_INSET, max_distance: float = 0.55) -> date | None
```

Return the calendar day whose cell center is nearest to ``(x, y)``, if close enough.

<details>
<summary>Code:</summary>

```python
def date_at_heatmap_point(
    positions: dict[date, tuple[float, float]],
    x: float,
    y: float,
    *,
    cell_inset: float = HEATMAP_CELL_INSET,
    max_distance: float = 0.55,
) -> date | None:
    best_day: date | None = None
    best_dist = max_distance
    half = 0.5 - cell_inset
    for day, (week_x, weekday_y) in positions.items():
        cx = week_x + cell_inset + half
        cy = weekday_y + cell_inset + half
        dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best_day = day
    return best_day
```

</details>

## 🔧 Function `habit_heatmap_month_column_count`

```python
def habit_heatmap_month_column_count(month_start: date, month_end: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON) -> int
```

Return how many week columns a (possibly partial) month occupies.

<details>
<summary>Code:</summary>

```python
def habit_heatmap_month_column_count(
    month_start: date,
    month_end: date,
    *,
    week_starts_on: int = HEATMAP_WEEK_STARTS_ON,
) -> int:
    first_week = habit_heatmap_week_start(month_start, week_starts_on=week_starts_on)
    last_week = habit_heatmap_week_start(month_end, week_starts_on=week_starts_on)
    return (last_week - first_week).days // 7 + 1
```

</details>

## 🔧 Function `habit_heatmap_month_ranges`

```python
def habit_heatmap_month_ranges(start_date: date, end_date: date) -> list[tuple[date, date]]
```

Return inclusive visible ``(month_start, month_end)`` ranges in ``[start_date, end_date]``.

<details>
<summary>Code:</summary>

```python
def habit_heatmap_month_ranges(start_date: date, end_date: date) -> list[tuple[date, date]]:
    ranges: list[tuple[date, date]] = []
    cursor = start_date
    while cursor <= end_date:
        last_day = monthrange(cursor.year, cursor.month)[1]
        month_end = min(end_date, date(cursor.year, cursor.month, last_day))
        ranges.append((cursor, month_end))
        cursor = month_end + timedelta(days=1)
    return ranges
```

</details>

## 🔧 Function `habit_heatmap_month_separated_positions`

```python
def habit_heatmap_month_separated_positions(start_date: date, end_date: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON, month_gap: float = HEATMAP_MONTH_GAP) -> tuple[dict[date, tuple[float, float]], list[tuple[str, float]], float]
```

Return LeetCode-style cell positions with a gap between month blocks.

Each month is its own Sunday-start week grid. A week that spans two months is
split so January days stay in January and February days start a new block.

Returns:

- `positions`: `day -> (week_x, weekday_y)` in dayplot week units
- `month_labels`: `(abbreviation, x)` for the first column of each month
- `total_width`: right edge of the last month block in week units

<details>
<summary>Code:</summary>

```python
def habit_heatmap_month_separated_positions(
    start_date: date,
    end_date: date,
    *,
    week_starts_on: int = HEATMAP_WEEK_STARTS_ON,
    month_gap: float = HEATMAP_MONTH_GAP,
) -> tuple[dict[date, tuple[float, float]], list[tuple[str, float]], float]:
    positions: dict[date, tuple[float, float]] = {}
    month_labels: list[tuple[str, float]] = []
    x_cursor = 0.0

    for month_start, month_end in habit_heatmap_month_ranges(start_date, end_date):
        month_week0 = habit_heatmap_week_start(month_start, week_starts_on=week_starts_on)
        month_labels.append((month_start.strftime("%b"), x_cursor))
        day = month_start
        while day <= month_end:
            week_x = x_cursor + (habit_heatmap_week_start(day, week_starts_on=week_starts_on) - month_week0).days // 7
            positions[day] = (float(week_x), float(habit_heatmap_weekday_index(day, week_starts_on=week_starts_on)))
            day += timedelta(days=1)
        x_cursor += habit_heatmap_month_column_count(month_start, month_end, week_starts_on=week_starts_on) + month_gap

    total_width = x_cursor - month_gap if month_labels else 0.0
    return positions, month_labels, total_width
```

</details>

## 🔧 Function `habit_heatmap_week_start`

```python
def habit_heatmap_week_start(day: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON) -> date
```

Return the first day of the heatmap week that contains `[`day`](../habits/dashboard_widgets.g.md#%EF%B8%8F-method-day)`.

<details>
<summary>Code:</summary>

```python
def habit_heatmap_week_start(day: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON) -> date:
    return day - timedelta(days=habit_heatmap_weekday_index(day, week_starts_on=week_starts_on))
```

</details>

## 🔧 Function `habit_heatmap_weekday_index`

```python
def habit_heatmap_weekday_index(day: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON) -> int
```

Return 0-based heatmap row for `[`day`](../habits/dashboard_widgets.g.md#%EF%B8%8F-method-day)` (Sunday-first by default).

<details>
<summary>Code:</summary>

```python
def habit_heatmap_weekday_index(day: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON) -> int:
    return (day.weekday() - week_starts_on) % 7
```

</details>

## 🔧 Function `heatmap_year_after_step`

```python
def heatmap_year_after_step(selected: str, years: list[int], *, step: int, today_year: int) -> int | None
```

Return the next filter year after a heatmap prev/next step.

Args:

- `selected` (`str`): Current year-filter text, including `Last 365 days`.
- `years` (`list[int]`): Years shown in the Charts year list.
- `step` (`int`): `-1` for previous year, `1` for next year.
- `today_year` (`int`): Current calendar year; later years are ignored.

Returns:

- `int | None`: Year to select, or `None` when the step is not available.

<details>
<summary>Code:</summary>

```python
def heatmap_year_after_step(
    selected: str,
    years: list[int],
    *,
    step: int,
    today_year: int,
) -> int | None:
    years_sorted = sorted({int(year) for year in years if year})
    years_sorted = [year for year in years_sorted if year <= today_year]
    if not years_sorted:
        return None
    if selected == "Last 365 days" or not str(selected).strip():
        return years_sorted[-1] if step < 0 else None
    try:
        current = int(selected)
    except (TypeError, ValueError):
        current = today_year
    if step < 0:
        older = [year for year in years_sorted if year < current]
        return older[-1] if older else None
    newer = [year for year in years_sorted if year > current]
    return newer[0] if newer else None
```

</details>

## 🔧 Function `numeric_habit_heatmap_cell_labels`

```python
def numeric_habit_heatmap_cell_labels(start_date: date, cell_count: int, date_values: dict[date, int]) -> list[tuple[int, int]]
```

Return ``(cell_index, value)`` for numeric heatmap cells that are not 0.

<details>
<summary>Code:</summary>

```python
def numeric_habit_heatmap_cell_labels(
    start_date: date,
    cell_count: int,
    date_values: dict[date, int],
) -> list[tuple[int, int]]:
    labels: list[tuple[int, int]] = []
    for index in range(cell_count):
        value = int(date_values.get(start_date + timedelta(days=index), 0))
        if value != 0:
            labels.append((index, value))
    return labels
```

</details>
