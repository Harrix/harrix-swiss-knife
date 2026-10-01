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
- [🔧 Function `partition_food_item_indexes_by_filter`](#-function-partition_food_item_indexes_by_filter)

</details>

## 🔧 Function `extract_food_name_from_display`

```python
def extract_food_name_from_display(display_text: str) -> str
```

Strip drink/recipe/catalog emoji prefixes and trailing calories suffix such as `(120 kcal/portion)`.

<details>
<summary>Code:</summary>

```python
def extract_food_name_from_display(display_text: str) -> str:
    if not display_text:
        return ""

    text = display_text.strip()
    if text.startswith(RECIPE_EMOJI):
        text = text[len(RECIPE_EMOJI) :].lstrip()
    if text.startswith(FOOD_ITEM_EMOJI):
        text = text[len(FOOD_ITEM_EMOJI) :].lstrip()
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

## 🔧 Function `partition_food_item_indexes_by_filter`

```python
def partition_food_item_indexes_by_filter(texts: Sequence[str], query: str) -> tuple[list[int], list[int]]
```

Split list indexes into autocomplete matches first, then the rest.

Empty `query` treats every row as a match. Relative order inside each group
is preserved.

Args:

- `texts` (`Sequence[str]`): Display texts for each list row.
- `query` (`str`): Filter from the food name field.

Returns:

- `tuple[list[int], list[int]]`: Matching indexes, then non-matching indexes.

<details>
<summary>Code:</summary>

```python
def partition_food_item_indexes_by_filter(texts: Sequence[str], query: str) -> tuple[list[int], list[int]]:
    needle = query.strip()
    matched: list[int] = []
    unmatched: list[int] = []
    for index, text in enumerate(texts):
        if not needle or text_matches_autocomplete(text, needle):
            matched.append(index)
        else:
            unmatched.append(index)
    return matched, unmatched
```

</details>
