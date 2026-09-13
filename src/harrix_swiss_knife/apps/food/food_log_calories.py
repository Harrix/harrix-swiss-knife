"""Local calorie totals for `tableView_food_log` without reloading the table."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from PySide6.QtGui import QStandardItemModel

FOOD_LOG_COL_WEIGHT = 2
FOOD_LOG_COL_CALORIES_PER_100G = 3
FOOD_LOG_COL_PORTION_CALORIES = 4
FOOD_LOG_COL_CALCULATED = 5
FOOD_LOG_COL_DATE = 6
FOOD_LOG_COL_TOTAL_PER_DAY = 8

FoodLogCalorieMode = Literal["portion", "per_100g"]


def calculate_food_log_calories(
    weight: float | None,
    calories_per_100g: float | None,
    portion_calories: float | None,
) -> float:
    """Return row calories: portion mode wins, otherwise weight * kcal/100g.

    Args:

    - `weight` (`float | None`): Mass in grams.
    - `calories_per_100g` (`float | None`): Energy per 100 g.
    - `portion_calories` (`float | None`): Energy of the whole serving.

    Returns:

    - `float`: Calories for the row.

    """
    if portion_calories is not None and portion_calories > 0:
        return float(portion_calories)
    if calories_per_100g is not None and calories_per_100g > 0 and weight is not None and weight > 0:
        return (float(calories_per_100g) * float(weight)) / 100
    return 0.0


def convert_calories_per_100g_to_portion(
    *,
    weight: float,
    calories_per_100g: float,
) -> float:
    """Return portion calories for `weight` g at `calories_per_100g`.

    Args:

    - `weight` (`float`): Mass in grams (must be > 0).
    - `calories_per_100g` (`float`): Energy per 100 g.

    Returns:

    - `float`: Energy of the whole serving, rounded to 1 decimal place.

    """
    return round((float(calories_per_100g) * float(weight)) / 100.0, 1)


def convert_portion_to_calories_per_100g(
    *,
    weight: float,
    portion_calories: float,
) -> float:
    """Return kcal/100g implied by `portion_calories` for `weight` g.

    Args:

    - `weight` (`float`): Mass in grams (must be > 0).
    - `portion_calories` (`float`): Energy of the whole serving.

    Returns:

    - `float`: Energy per 100 g, rounded to 1 decimal place.

    """
    return round((float(portion_calories) / float(weight)) * 100.0, 1)


def food_log_calorie_mode(
    calories_per_100g: float | None,
    portion_calories: float | None,
) -> FoodLogCalorieMode | None:
    """Return whether the row uses portion calories or kcal/100g.

    Portion mode wins when both are set (same rule as `calculate_food_log_calories`).

    Args:

    - `calories_per_100g` (`float | None`): Energy per 100 g.
    - `portion_calories` (`float | None`): Energy of the whole serving.

    Returns:

    - `FoodLogCalorieMode | None`: `"portion"`, `"per_100g"`, or `None` when neither applies.

    """
    if portion_calories is not None and portion_calories > 0:
        return "portion"
    if calories_per_100g is not None and calories_per_100g > 0:
        return "per_100g"
    return None


def parse_food_log_number(value: object) -> float | None:
    """Parse a table cell or database value as `float`.

    Args:

    - `value` (`object`): Cell text or stored number.

    Returns:

    - `float | None`: Parsed number, or `None` when empty or invalid.

    """
    if value is None or value == "":
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def refresh_food_log_calorie_columns(model: QStandardItemModel) -> dict[str, float]:
    """Recalculate calculated-calories and total-per-day cells in `model`.

    Does not emit `dataChanged` (signals are blocked) so auto-save does not run
    again.

    Args:

    - `model` (`QStandardItemModel`): Food-log source model.

    Returns:

    - `dict[str, float]`: Date → calories summed from rows currently in `model`.

    """
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


def _item_text(model: QStandardItemModel, row: int, column: int) -> str:
    item = model.item(row, column)
    return item.text() if item is not None else ""


def _set_item_text(model: QStandardItemModel, row: int, column: int, text: str) -> None:
    item = model.item(row, column)
    if item is not None:
        item.setText(text)
