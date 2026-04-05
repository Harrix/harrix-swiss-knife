"""String formatting for food names shown in lists and autocompletion."""

from __future__ import annotations

import re


def extract_food_name_from_display(display_text: str) -> str:
    """Strip trailing calories suffix such as ``(120 kcal/portion)``."""
    if not display_text:
        return ""

    pattern = r"\s+\(\d+\.?\d*\s+kcal/(?:portion|100g)\)$"
    clean_name = re.sub(pattern, "", display_text)

    return clean_name.strip()


def format_food_name_with_calories(
    food_name: str,
    calories_per_100g: float | None,
    default_portion_calories: float | None,
) -> str:
    """Append ``(… kcal/portion)`` or ``(… kcal/100g)`` when values exist."""
    if not food_name:
        return food_name

    cal_100g = _safe_float(calories_per_100g)
    portion_cal = _safe_float(default_portion_calories)

    calories_info = ""

    if portion_cal is not None:
        calories_info = f"({portion_cal:.0f} kcal/portion)"
    elif cal_100g is not None:
        calories_info = f"({cal_100g:.0f} kcal/100g)"

    if calories_info:
        return f"{food_name} {calories_info}"
    return food_name


def _safe_float(value: float | str | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, float):
        return value
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
