---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `portion_weight_parser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PortionWeightResult`](#%EF%B8%8F-class-portionweightresult)
  - [📎 Attribute `is_drink`](#-attribute-is_drink)
  - [📎 Attribute `weight_g`](#-attribute-weight_g)
- [🔧 Function `parse_portion_weight_response`](#-function-parse_portion_weight_response)

</details>

## 🏛️ Class `PortionWeightResult`

```python
class PortionWeightResult
```

Parsed fields for portion weight lookup from the manual food entry form.

<details>
<summary>Code:</summary>

```python
class PortionWeightResult:

    is_drink: bool
    weight_g: int
```

</details>

### 📎 Attribute `is_drink`

```python
is_drink: bool
```

_No docstring provided._

### 📎 Attribute `weight_g`

```python
weight_g: int
```

_No docstring provided._

## 🔧 Function `parse_portion_weight_response`

```python
def parse_portion_weight_response(text: str) -> PortionWeightResult | None
```

Parse a TSV line: Drink, Weight.

<details>
<summary>Code:</summary>

```python
def parse_portion_weight_response(text: str) -> PortionWeightResult | None:
    line = _first_data_line(text)
    if not line:
        return None

    parts = line.split("\t")
    if len(parts) != _TSV_COLUMN_COUNT:
        return None

    drink_raw = parts[0].strip().lower()
    if drink_raw not in {"yes", "no"}:
        return None

    try:
        weight_g = int(float(parts[1].strip().replace(",", ".")))
    except ValueError:
        return None

    if weight_g < 0:
        return None

    return PortionWeightResult(is_drink=drink_raw == "yes", weight_g=weight_g)
```

</details>
