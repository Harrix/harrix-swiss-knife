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
- [🔧 Function `parse_kcal_lookup_response`](#-function-parse_kcal_lookup_response)
- [🔧 Function `_first_data_line`](#-function-_first_data_line)

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

    return KcalLookupResult(
        calories=calories,
        is_weight_mode=mode == "weight",
        is_drink=drink_raw == "yes",
        weight_g=max(0, weight_g),
    )
```

</details>

## 🔧 Function `_first_data_line`

```python
def _first_data_line(text: str) -> str
```

Return first non-empty line, stripping markdown code fences.

<details>
<summary>Code:</summary>

````python
def _first_data_line(text: str) -> str:
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        return line
    return ""
````

</details>
