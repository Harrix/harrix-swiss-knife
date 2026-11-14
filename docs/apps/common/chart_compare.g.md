---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_compare.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CompareMonthWindow`](#%EF%B8%8F-class-comparemonthwindow)
- [🔧 Function `compare_last_month_windows`](#-function-compare_last_month_windows)
- [🔧 Function `compare_same_month_windows`](#-function-compare_same_month_windows)
- [🔧 Function `month_starts_going_back`](#-function-month_starts_going_back)

</details>

## 🏛️ Class `CompareMonthWindow`

```python
class CompareMonthWindow
```

One month column or cumulative line in a comparison chart.

<details>
<summary>Code:</summary>

```python
class CompareMonthWindow:

    year: int
    month: int
    end_day: int
    label: str
    is_current: bool
    color: str
```

</details>

## 🔧 Function `compare_last_month_windows`

```python
def compare_last_month_windows(months_count: int, *, today: date) -> list[CompareMonthWindow]
```

Return newest-first Windows for the last `months_count` months.

The newest month stops on `today` when that month is still in progress.

<details>
<summary>Code:</summary>

```python
def compare_last_month_windows(months_count: int, *, today: date) -> list[CompareMonthWindow]:
    windows: list[CompareMonthWindow] = []
    for index, start in enumerate(month_starts_going_back(months_count, today=today)):
        days_in_month = calendar.monthrange(start.year, start.month)[1]
        is_current = index == 0
        end_day = min(today.day, days_in_month) if is_current else days_in_month
        label = start.strftime("%B %Y")
        if is_current:
            label = f"{label} (Current)"
        windows.append(
            CompareMonthWindow(
                year=start.year,
                month=start.month,
                end_day=end_day,
                label=label,
                is_current=is_current,
                color=chart_series_color(0 if is_current else max(index, 1)),
            ),
        )
    return windows
```

</details>

## 🔧 Function `compare_same_month_windows`

```python
def compare_same_month_windows(month: int, years_count: int, *, today: date) -> list[CompareMonthWindow]
```

Return newest-first Windows for one calendar month across recent years.

A month that has not started yet in the current year is skipped.

<details>
<summary>Code:</summary>

```python
def compare_same_month_windows(month: int, years_count: int, *, today: date) -> list[CompareMonthWindow]:
    selected = max(1, min(int(month), 12))
    windows: list[CompareMonthWindow] = []
    color_index = 0
    for offset in range(max(int(years_count), 0)):
        year = today.year - offset
        if year == today.year and today.month < selected:
            continue
        days_in_month = calendar.monthrange(year, selected)[1]
        is_current = year == today.year and today.month == selected
        end_day = min(today.day, days_in_month) if is_current else days_in_month
        label = date(year, selected, 1).strftime("%B %Y")
        if is_current:
            label = f"{label} (Current)"
            color = chart_series_color(0)
        else:
            color = chart_series_color(color_index + 1)
            color_index += 1
        windows.append(
            CompareMonthWindow(
                year=year,
                month=selected,
                end_day=end_day,
                label=label,
                is_current=is_current,
                color=color,
            ),
        )
    return windows
```

</details>

## 🔧 Function `month_starts_going_back`

```python
def month_starts_going_back(months_count: int, *, today: date) -> list[date]
```

Return first-of-month dates, newest first, for `months_count` months ending at `today`.

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
