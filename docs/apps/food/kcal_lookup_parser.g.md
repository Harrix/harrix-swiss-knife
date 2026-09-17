---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `kcal_lookup_parser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `KcalLookupResult`](#%EF%B8%8F-class-kcallookupresult)
- [🔧 Function `calories_from_kcal_lookup`](#-function-calories_from_kcal_lookup)
- [🔧 Function `normalize_kcal_lookup_mode`](#-function-normalize_kcal_lookup_mode)
- [🔧 Function `parse_kcal_lookup_response`](#-function-parse_kcal_lookup_response)

</details>

## 🏛️ Class `KcalLookupResult`

```python
class KcalLookupResult
```

Parsed kcal lookup fields for the manual food entry form.

<details>
<summary>Code:</summary>

```python
class KcalLookupResult:

    calories: float
    is_weight_mode: bool
    is_drink: bool
    weight_g: int
```

</details>

## 🔧 Function `calories_from_kcal_lookup`

```python
def calories_from_kcal_lookup(result: KcalLookupResult) -> float | None
```

Map an AI lookup to kcal/100g for food_log (mass unchanged).

Weight mode uses the value as kcal per 100 g. Portion mode converts serving
calories using the returned weight.

Args:

- `result` ([`KcalLookupResult`](#%EF%B8%8F-class-kcallookupresult)): Parsed BotHub lookup.

Returns:

- `float | None`: Energy per 100 g, or `None` when it cannot be derived.

<details>
<summary>Code:</summary>

```python
def calories_from_kcal_lookup(result: KcalLookupResult) -> float | None:
    if result.is_weight_mode:
        return result.calories if result.calories > 0 else None
    if result.weight_g <= 0 or result.calories <= 0:
        return None
    return convert_portion_to_calories_per_100g(
        weight=float(result.weight_g),
        portion_calories=result.calories,
    )
```

</details>

## 🔧 Function `normalize_kcal_lookup_mode`

```python
def normalize_kcal_lookup_mode(result: KcalLookupResult) -> KcalLookupResult
```

Switch portion → weight when Calories look like kcal per 100 g, not total for Weight.

<details>
<summary>Code:</summary>

```python
def normalize_kcal_lookup_mode(result: KcalLookupResult) -> KcalLookupResult:
    if result.is_weight_mode or result.weight_g <= 0 or result.calories <= 0:
        return result
    implied_per_100g = (result.calories / result.weight_g) * 100
    if implied_per_100g <= _MAX_IMPLIED_KCAL_PER_100G:
        return result
    return KcalLookupResult(
        calories=result.calories,
        is_weight_mode=True,
        is_drink=result.is_drink,
        weight_g=result.weight_g,
    )
```

</details>

## 🔧 Function `parse_kcal_lookup_response`

```python
def parse_kcal_lookup_response(text: str) -> KcalLookupResult | None
```

Parse a TSV line: Calories, Mode, Drink, Weight.

<details>
<summary>Code:</summary>

```python
def parse_kcal_lookup_response(text: str) -> KcalLookupResult | None:
    line = _first_data_line(text)
    if not line:
        return None

    parts = line.split("\t")
    if len(parts) != _TSV_COLUMN_COUNT:
        return None

    try:
        calories = float(parts[0].strip().replace(",", "."))
    except ValueError:
        return None

    mode = parts[1].strip().lower()
    if mode not in {"weight", "portion"}:
        return None

    drink_raw = parts[2].strip().lower()
    if drink_raw not in {"yes", "no"}:
        return None

    try:
        weight_g = int(float(parts[3].strip().replace(",", ".")))
    except ValueError:
        return None

    if calories < 0 or weight_g < 0:
        return None

    result = KcalLookupResult(
        calories=calories,
        is_weight_mode=mode == "weight",
        is_drink=drink_raw == "yes",
        weight_g=max(0, weight_g),
    )
    return normalize_kcal_lookup_mode(result)
```

</details>
