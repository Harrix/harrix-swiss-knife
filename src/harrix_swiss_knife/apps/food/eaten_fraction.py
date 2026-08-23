"""Scale food-log weight and portion calories after eating a fraction."""

from __future__ import annotations

ATE_HALF = 0.5
ATE_THIRD = 1 / 3
ATE_TWO_THIRDS = 2 / 3


def scale_food_log_eaten_amounts(
    *,
    weight: float | None,
    portion_calories: float | None,
    fraction: float,
) -> tuple[float | None, float | None]:
    """Return `(weight, portion_calories)` after eating `fraction` of the row.

    If the row uses calories per 100 g (`portion_calories` empty or 0), only
    the mass changes. If it uses calories per serving, both mass and serving
    calories are scaled.

    Args:

    - `weight` (`float | None`): Logged mass in grams.
    - `portion_calories` (`float | None`): Calories for the serving, if used.
    - `fraction` (`float`): Share actually eaten, in `(0, 1]`.

    Returns:

    - `tuple[float | None, float | None]`: New weight and portion calories.

    """
    new_weight = _scale_amount(weight, fraction)
    if portion_calories is not None and portion_calories > 0:
        return new_weight, _scale_amount(portion_calories, fraction)
    return new_weight, portion_calories


def _scale_amount(value: float | None, fraction: float) -> float | None:
    if value is None:
        return None
    return round(value * fraction, 1)
