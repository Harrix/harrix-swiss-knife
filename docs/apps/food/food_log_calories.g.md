---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_log_calories.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `calculate_food_log_calories`](#-function-calculate_food_log_calories)
- [🔧 Function `parse_food_log_number`](#-function-parse_food_log_number)
- [🔧 Function `refresh_food_log_calorie_columns`](#-function-refresh_food_log_calorie_columns)

</details>

## 🔧 Function `calculate_food_log_calories`

```python
def calculate_food_log_calories(weight: float | None, calories_per_100g: float | None, portion_calories: float | None) -> float
```

Return row calories: portion mode wins, otherwise weight * kcal/100g.

Args:

- `weight` (`float | None`): Mass in grams.
- `calories_per_100g` (`float | None`): Energy per 100 g.
- `portion_calories` (`float | None`): Energy of the whole serving.

Returns:

- `float`: Calories for the row.

<details>
<summary>Code:</summary>

```python
def calculate_food_log_calories(
    weight: float | None,
    calories_per_100g: float | None,
    portion_calories: float | None,
) -> float:
    if portion_calories is not None and portion_calories > 0:
        return float(portion_calories)
    if calories_per_100g is not None and calories_per_100g > 0 and weight is not None and weight > 0:
        return (float(calories_per_100g) * float(weight)) / 100
    return 0.0
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

Recalculate calculated-calories and total-per-day cells in `model`.

Does not emit `dataChanged` (signals are blocked) so auto-save does not run
again.

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
        calories = calculate_food_log_calories(
            parse_food_log_number(_item_text(model, row, FOOD_LOG_COL_WEIGHT)),
            parse_food_log_number(_item_text(model, row, FOOD_LOG_COL_CALORIES_PER_100G)),
            parse_food_log_number(_item_text(model, row, FOOD_LOG_COL_PORTION_CALORIES)),
        )
        dates.append(date_str)
        row_calories.append(calories)
        if date_str:
            totals[date_str] = totals.get(date_str, 0.0) + calories

    seen_dates: set[str] = set()
    model.blockSignals(True)  # noqa: FBT003
    try:
        for row in range(row_count):
            _set_item_text(model, row, FOOD_LOG_COL_CALCULATED, f"{row_calories[row]:.1f}")
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
