---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_display.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `extract_food_name_from_display`](#-function-extract_food_name_from_display)
- [🔧 Function `format_food_name_with_calories`](#-function-format_food_name_with_calories)

</details>

## 🔧 Function `extract_food_name_from_display`

```python
def extract_food_name_from_display(display_text: str) -> str
```

Strip drink/recipe emoji prefixes and trailing calories suffix such as `(120 kcal/portion)`.

<details>
<summary>Code:</summary>

```python
def extract_food_name_from_display(display_text: str) -> str:
    if not display_text:
        return ""

    text = display_text.strip()
    if text.startswith(RECIPE_EMOJI):
        text = text[len(RECIPE_EMOJI) :].lstrip()
    if text.startswith(DRINK_EMOJI):
        text = text[len(DRINK_EMOJI) :].lstrip()

    pattern = r"\s+\(\d+\.?\d*\s+kcal/(?:portion|100g)\)$"
    return re.sub(pattern, "", text).strip()
```

</details>

## 🔧 Function `format_food_name_with_calories`

```python
def format_food_name_with_calories(food_name: str, calories_per_100g: float | None, default_portion_calories: float | None, *, is_drink: bool = False, is_recipe: bool = False) -> str
```

Append `(… kcal/portion)` or `(… kcal/100g)` when values exist.

Drinks get the same `DRINK_EMOJI` prefix as `tableView_food_log`.
Recipes get `RECIPE_EMOJI` (before the drink prefix when both apply).

<details>
<summary>Code:</summary>

```python
def format_food_name_with_calories(
    food_name: str,
    calories_per_100g: float | None,
    default_portion_calories: float | None,
    *,
    is_drink: bool = False,
    is_recipe: bool = False,
) -> str:
    if not food_name:
        return food_name

    cal_100g = _safe_float(calories_per_100g)
    portion_cal = _safe_float(default_portion_calories)

    calories_info = ""

    if portion_cal is not None:
        calories_info = f"({portion_cal:.0f} kcal/portion)"
    elif cal_100g is not None:
        calories_info = f"({cal_100g:.0f} kcal/100g)"

    result = f"{food_name} {calories_info}" if calories_info else food_name
    if is_drink:
        result = f"{DRINK_EMOJI} {result}"
    if is_recipe:
        result = f"{RECIPE_EMOJI} {result}"
    return result
```

</details>
