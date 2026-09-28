---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_log_calories.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_food_log_day_spans`](#-function-apply_food_log_day_spans)
- [🔧 Function `calculate_food_log_calories`](#-function-calculate_food_log_calories)
- [🔧 Function `convert_calories_per_100g_to_portion`](#-function-convert_calories_per_100g_to_portion)
- [🔧 Function `convert_portion_to_calories_per_100g`](#-function-convert_portion_to_calories_per_100g)
- [🔧 Function `effective_calories_per_100g`](#-function-effective_calories_per_100g)
- [🔧 Function `food_log_day_row_spans`](#-function-food_log_day_row_spans)
- [🔧 Function `parse_food_log_number`](#-function-parse_food_log_number)
- [🔧 Function `refresh_food_log_calorie_columns`](#-function-refresh_food_log_calorie_columns)

</details>

## 🔧 Function `apply_food_log_day_spans`

```python
def apply_food_log_day_spans(view: QTableView) -> None
```

Merge the Total per day column so each calendar day is one cell.

The day's total is aligned to the top of the merged cell.

<details>
<summary>Code:</summary>

```python
def apply_food_log_day_spans(view: QTableView) -> None:
    model = view.model()
    view.clearSpans()
    if model is None:
        return
    dates = [str(model.index(row, FOOD_LOG_COL_DATE).data() or "") for row in range(model.rowCount())]
    spans = food_log_day_row_spans(dates)
    span_starts = {start for start, _row_count in spans}
    source = _food_log_source_model(model)
    if source is not None:
        source.blockSignals(True)  # noqa: FBT003
    try:
        for row in range(model.rowCount()):
            item = _food_log_total_item(model, row)
            if item is None:
                continue
            alignment = _TOTAL_ALIGN_TOP if row in span_starts else _TOTAL_ALIGN_MIDDLE
            if item.textAlignment() != alignment:
                item.setTextAlignment(alignment)
        for start, row_count in spans:
            view.setSpan(start, FOOD_LOG_COL_TOTAL_PER_DAY, row_count, 1)
    finally:
        if source is not None:
            source.blockSignals(False)  # noqa: FBT003
```

</details>

## 🔧 Function `calculate_food_log_calories`

```python
def calculate_food_log_calories(weight: float | None, calories_per_100g: float | None) -> float
```

Return row calories from weight * kcal/100g.

Args:

- `weight` (`float | None`): Mass in grams.
- [`calories_per_100g`](portion_calories_dialog.g.md#%EF%B8%8F-method-calories_per_100g) (`float | None`): Energy per 100 g.

Returns:

- `float`: Calories for the row.

<details>
<summary>Code:</summary>

```python
def calculate_food_log_calories(
    weight: float | None,
    calories_per_100g: float | None,
) -> float:
    if calories_per_100g is not None and calories_per_100g > 0 and weight is not None and weight > 0:
        return (float(calories_per_100g) * float(weight)) / 100
    return 0.0
```

</details>

## 🔧 Function `convert_calories_per_100g_to_portion`

```python
def convert_calories_per_100g_to_portion(*, weight: float, calories_per_100g: float) -> float
```

Return serving kcal from weight * kcal/100g.

Args:

- `weight` (`float`): Mass in grams (must be > 0).
- [`calories_per_100g`](portion_calories_dialog.g.md#%EF%B8%8F-method-calories_per_100g) (`float`): Energy per 100 g.

Returns:

- `float`: Portion calories, rounded to 1 decimal place.

<details>
<summary>Code:</summary>

```python
def convert_calories_per_100g_to_portion(
    *,
    weight: float,
    calories_per_100g: float,
) -> float:
    return round((float(calories_per_100g) * float(weight)) / 100.0, 1)
```

</details>

## 🔧 Function `convert_portion_to_calories_per_100g`

```python
def convert_portion_to_calories_per_100g(*, weight: float, portion_calories: float) -> float
```

Return kcal/100g implied by [`portion_calories`](portion_calories_dialog.g.md#%EF%B8%8F-method-portion_calories) for `weight` g.

Args:

- `weight` (`float`): Mass in grams (must be > 0).
- [`portion_calories`](portion_calories_dialog.g.md#%EF%B8%8F-method-portion_calories) (`float`): Energy of the whole serving.

Returns:

- `float`: Energy per 100 g, rounded to 1 decimal place.

<details>
<summary>Code:</summary>

```python
def convert_portion_to_calories_per_100g(
    *,
    weight: float,
    portion_calories: float,
) -> float:
    return round((float(portion_calories) / float(weight)) * 100.0, 1)
```

</details>

## 🔧 Function `effective_calories_per_100g`

```python
def effective_calories_per_100g(calories_per_100g: float | None, *, portion_calories: float | None = None, weight: float | None = None) -> float | None
```

Return kcal/100g from stored value or by converting portion data.

<details>
<summary>Code:</summary>

```python
def effective_calories_per_100g(
    calories_per_100g: float | None,
    *,
    portion_calories: float | None = None,
    weight: float | None = None,
) -> float | None:
    if calories_per_100g is not None and calories_per_100g > 0:
        return float(calories_per_100g)
    if portion_calories is not None and portion_calories > 0 and weight is not None and weight > 0:
        return convert_portion_to_calories_per_100g(weight=weight, portion_calories=portion_calories)
    if calories_per_100g is not None and calories_per_100g == 0:
        return 0.0
    return None
```

</details>

## 🔧 Function `food_log_day_row_spans`

```python
def food_log_day_row_spans(dates: list[str]) -> list[tuple[int, int]]
```

Return `(start_row, row_count)` for days that occupy more than one row.

<details>
<summary>Code:</summary>

```python
def food_log_day_row_spans(dates: list[str]) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0
    row_count = len(dates)
    while start < row_count:
        day = dates[start]
        end = start + 1
        while end < row_count and day and dates[end] == day:
            end += 1
        if day and end - start > 1:
            spans.append((start, end - start))
        start = end
    return spans
```

</details>

## 🔧 Function `parse_food_log_number`

```python
def parse_food_log_number(value: object) -> float | None
```

Parse a table cell or database value as `float`.

Args:

- `value` (`object`): Cell text or stored number.

Returns:

- `float | None`: Parsed number, or `None` when empty or invalid.

<details>
<summary>Code:</summary>

```python
def parse_food_log_number(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None
```

</details>

## 🔧 Function `refresh_food_log_calorie_columns`

```python
def refresh_food_log_calorie_columns(model: QStandardItemModel) -> dict[str, float]
```

Recalculate calories and total-per-day cells in `model`.

Does not emit `dataChanged` (signals are blocked) so auto-save does not run
again. The kcal/100g column stores density; day totals are derived from it.

Args:

- `model` (`QStandardItemModel`): Food-log source model.

Returns:

- `dict[str, float]`: Date → calories summed from rows currently in `model`.

<details>
<summary>Code:</summary>

```python
def refresh_food_log_calorie_columns(model: QStandardItemModel) -> dict[str, float]:
    row_count = model.rowCount()
    row_calories: list[float] = []
    dates: list[str] = []
    totals: dict[str, float] = {}

    for row in range(row_count):
        date_str = _item_text(model, row, FOOD_LOG_COL_DATE)
        # kcal/100g column for editing; day totals are derived from it.
        calories = calculate_food_log_calories(
            parse_food_log_number(_item_text(model, row, FOOD_LOG_COL_WEIGHT)),
            parse_food_log_number(_item_text(model, row, FOOD_LOG_COL_CALORIES)),
        )
        dates.append(date_str)
        row_calories.append(calories)
        if date_str:
            totals[date_str] = totals.get(date_str, 0.0) + calories

    seen_dates: set[str] = set()
    model.blockSignals(True)  # noqa: FBT003
    try:
        for row in range(row_count):
            date_str = dates[row]
            is_first = bool(date_str) and date_str not in seen_dates
            if is_first:
                seen_dates.add(date_str)
            total_text = f"{totals[date_str]:.1f}" if is_first else ""
            _set_item_text(model, row, FOOD_LOG_COL_TOTAL_PER_DAY, total_text)
    finally:
        model.blockSignals(False)  # noqa: FBT003

    return totals
```

</details>
