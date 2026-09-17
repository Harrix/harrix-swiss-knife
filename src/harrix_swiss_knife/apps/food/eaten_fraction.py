"""Scale food-log weight after eating a fraction of a row."""

from __future__ import annotations

ATE_HALF = 0.5
ATE_THIRD = 1 / 3
ATE_TWO_THIRDS = 2 / 3


def scale_food_log_eaten_weight(*, weight: float | None, fraction: float) -> float | None:
    """Return weight after eating `fraction` of the row (kcal/100g unchanged).

    Args:

    - `weight` (`float | None`): Logged mass in grams.
    - `fraction` (`float`): Share actually eaten, in `(0, 1]`.

    Returns:

    - `float | None`: New weight.

    """
    return _scale_amount(weight, fraction)


def _scale_amount(value: float | None, fraction: float) -> float | None:
    if value is None:
        return None
    return round(value * fraction, 1)
