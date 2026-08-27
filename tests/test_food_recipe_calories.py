"""Tests for recipe calorie aggregation helpers."""

from __future__ import annotations

from harrix_swiss_knife.apps.food.recipe_calories import (
    RecipeIngredientInput,
    calculate_recipe_nutrition,
    recipe_ingredients_from_food_log_rows,
)


def test_calculate_recipe_nutrition_weight_mode() -> None:
    ingredients = [
        RecipeIngredientInput(name="Rice", weight=200, calories_per_100g=130),
        RecipeIngredientInput(name="Chicken", weight=100, calories_per_100g=165),
    ]
    nutrition = calculate_recipe_nutrition(ingredients)
    assert nutrition.total_weight == 300
    assert nutrition.total_calories == 260 + 165
    assert nutrition.calories_per_100g == round((425 / 300) * 100, 2)


def test_calculate_recipe_nutrition_portion_mode_wins() -> None:
    ingredients = [
        RecipeIngredientInput(name="Egg", weight=50, calories_per_100g=140, portion_calories=70),
        RecipeIngredientInput(name="Bread", weight=50, calories_per_100g=250),
    ]
    nutrition = calculate_recipe_nutrition(ingredients)
    assert nutrition.total_weight == 100
    assert nutrition.total_calories == 70 + 125
    assert nutrition.calories_per_100g == 195.0


def test_calculate_recipe_nutrition_zero_weight() -> None:
    ingredients = [RecipeIngredientInput(name="Spice", weight=0, portion_calories=5)]
    nutrition = calculate_recipe_nutrition(ingredients)
    assert nutrition.total_weight == 0
    assert nutrition.total_calories == 5
    assert nutrition.calories_per_100g is None


def test_recipe_ingredients_from_food_log_rows_uses_calculated() -> None:
    rows: list[dict[str, object]] = [
        {
            "name": "Milk",
            "weight": "200",
            "calories_per_100g": "64",
            "portion_calories": "",
            "calculated_calories": "128",
            "is_drink": True,
        },
        {
            "name": "Coffee",
            "weight": "30",
            "calories_per_100g": "",
            "portion_calories": "5",
            "calculated_calories": "5",
            "is_drink": True,
        },
    ]
    ingredients = recipe_ingredients_from_food_log_rows(rows)
    assert len(ingredients) == 2
    assert ingredients[0].name == "Milk"
    assert ingredients[0].portion_calories == 128
    assert ingredients[0].calories_per_100g is None
    assert ingredients[0].is_drink is True
    assert ingredients[1].portion_calories == 5
