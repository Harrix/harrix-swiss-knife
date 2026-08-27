---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `recipe_calories.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RecipeIngredientInput`](#%EF%B8%8F-class-recipeingredientinput)
- [🏛️ Class `RecipeNutrition`](#%EF%B8%8F-class-recipenutrition)
- [🔧 Function `calculate_recipe_nutrition`](#-function-calculate_recipe_nutrition)
- [🔧 Function `recipe_ingredients_from_food_log_rows`](#-function-recipe_ingredients_from_food_log_rows)

</details>

## 🏛️ Class `RecipeIngredientInput`

```python
class RecipeIngredientInput
```

One ingredient used when computing recipe nutrition.

<details>
<summary>Code:</summary>

```python
class RecipeIngredientInput:

    name: str
    weight: float | None = None
    calories_per_100g: float | None = None
    portion_calories: float | None = None
    name_en: str | None = None
    is_drink: bool = False
```

</details>

## 🏛️ Class `RecipeNutrition`

```python
class RecipeNutrition
```

Aggregated weight and calories for a recipe.

<details>
<summary>Code:</summary>

```python
class RecipeNutrition:

    total_weight: float
    total_calories: float
    calories_per_100g: float | None
```

</details>

## 🔧 Function `calculate_recipe_nutrition`

```python
def calculate_recipe_nutrition(ingredients: list[RecipeIngredientInput]) -> RecipeNutrition
```

Sum ingredient calories and derive average kcal per 100 g.

Args:

- `ingredients` (`list[RecipeIngredientInput]`): Recipe composition rows.

Returns:

- [`RecipeNutrition`](#%EF%B8%8F-class-recipenutrition): Totals; `calories_per_100g` is `None` when total weight is 0.

<details>
<summary>Code:</summary>

```python
def calculate_recipe_nutrition(ingredients: list[RecipeIngredientInput]) -> RecipeNutrition:
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
```

</details>

## 🔧 Function `recipe_ingredients_from_food_log_rows`

```python
def recipe_ingredients_from_food_log_rows(rows: list[dict[str, object]]) -> list[RecipeIngredientInput]
```

Build recipe ingredients from selected food-log table row dicts.

Each dict may include `name`, `name_en`, `weight`, `calories_per_100g`,
`portion_calories`, `calculated_calories`, and `is_drink`. When
`portion_calories` is missing or zero but `calculated_calories` is set, the
calculated value is stored as `portion_calories` so the snapshot keeps the
exact kcal used on the log row.

Args:

- `rows` (`list[dict[str, object]]`): Selected log rows as plain dicts.

Returns:

- `list[RecipeIngredientInput]`: Ingredient snapshots for saving a recipe.

<details>
<summary>Code:</summary>

```python
def recipe_ingredients_from_food_log_rows(
    rows: list[dict[str, object]],
) -> list[RecipeIngredientInput]:
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
```

</details>
