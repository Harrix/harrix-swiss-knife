"""Calorie totals for recipe ingredients and average kcal per 100 g."""

from __future__ import annotations

from dataclasses import dataclass

from harrix_swiss_knife.apps.food.food_log_calories import calculate_food_log_calories


@dataclass(frozen=True, slots=True)
class RecipeIngredientInput:
    """One ingredient used when computing recipe nutrition."""

    name: str
    weight: float | None = None
    calories_per_100g: float | None = None
    portion_calories: float | None = None
    name_en: str | None = None
    is_drink: bool = False


@dataclass(frozen=True, slots=True)
class RecipeNutrition:
    """Aggregated weight and calories for a recipe."""

    total_weight: float
    total_calories: float
    calories_per_100g: float | None


def calculate_recipe_nutrition(ingredients: list[RecipeIngredientInput]) -> RecipeNutrition:
    """Sum ingredient calories and derive average kcal per 100 g.

    Args:

    - `ingredients` (`list[RecipeIngredientInput]`): Recipe composition rows.

    Returns:

    - `RecipeNutrition`: Totals; `calories_per_100g` is `None` when total weight is 0.

    """
    total_weight = 0.0
    total_calories = 0.0
    for ingredient in ingredients:
        weight = float(ingredient.weight) if ingredient.weight is not None else 0.0
        if weight > 0:
            total_weight += weight
        total_calories += calculate_food_log_calories(
            ingredient.weight,
            ingredient.calories_per_100g,
            ingredient.portion_calories,
        )

    if total_weight <= 0:
        return RecipeNutrition(total_weight=0.0, total_calories=total_calories, calories_per_100g=None)

    calories_per_100g = round((total_calories / total_weight) * 100, 2)
    return RecipeNutrition(
        total_weight=total_weight,
        total_calories=total_calories,
        calories_per_100g=calories_per_100g,
    )


def recipe_ingredients_from_food_log_rows(
    rows: list[dict[str, object]],
) -> list[RecipeIngredientInput]:
    """Build recipe ingredients from selected food-log table row dicts.

    Each dict may include `name`, `name_en`, `weight`, `calories_per_100g`,
    `portion_calories`, `calculated_calories`, and `is_drink`. When
    `portion_calories` is missing or zero but `calculated_calories` is set, the
    calculated value is stored as `portion_calories` so the snapshot keeps the
    exact kcal used on the log row.

    Args:

    - `rows` (`list[dict[str, object]]`): Selected log rows as plain dicts.

    Returns:

    - `list[RecipeIngredientInput]`: Ingredient snapshots for saving a recipe.

    """
    ingredients: list[RecipeIngredientInput] = []
    for row in rows:
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        weight = _optional_float(row.get("weight"))
        calories_per_100g = _optional_float(row.get("calories_per_100g"))
        portion_calories = _optional_float(row.get("portion_calories"))
        calculated = _optional_float(row.get("calculated_calories"))
        if (portion_calories is None or portion_calories <= 0) and calculated is not None and calculated > 0:
            portion_calories = calculated
            calories_per_100g = None
        name_en_raw = row.get("name_en")
        name_en = str(name_en_raw).strip() if name_en_raw not in (None, "") else None
        is_drink = bool(row.get("is_drink"))
        ingredients.append(
            RecipeIngredientInput(
                name=name,
                weight=weight,
                calories_per_100g=calories_per_100g,
                portion_calories=portion_calories,
                name_en=name_en,
                is_drink=is_drink,
            )
        )
    return ingredients


def _optional_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None
