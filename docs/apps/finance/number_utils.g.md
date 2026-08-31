---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `number_utils.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `format_amount`](#-function-format_amount)
- [🔧 Function `major_units_to_minor`](#-function-major_units_to_minor)

</details>

## 🔧 Function `format_amount`

```python
def format_amount(value: float | str) -> str
```

Format amount with spaces for thousands separator and subscript decimals.

Args:

- `value` (`float | str`): The value to format.

Returns:

- `str`: The formatted text with spaces as thousands separators and subscript decimal digits.

<details>
<summary>Code:</summary>

```python
def format_amount(value: float | str) -> str:
    try:
        text = str(value)
        is_negative = text.startswith("-")
        if is_negative:
            text = text[1:]

        try:
            num = float(text)
        except (ValueError, TypeError):
            return str(value)

        if "." in str(num):
            integer_part, decimal_part = str(num).split(".")
        else:
            integer_part = str(int(num))
            decimal_part = "00"

        formatted_integer = ""
        for i, digit in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                formatted_integer = " " + formatted_integer
            formatted_integer = digit + formatted_integer

        subscript_map = {
            "0": "₀",
            "1": "₁",
            "2": "₂",
            "3": "₃",
            "4": "₄",
            "5": "₅",
            "6": "₆",
            "7": "₇",
            "8": "₈",
            "9": "₉",
        }
        subscript_decimal = "".join(subscript_map.get(digit, digit) for digit in decimal_part)

        formatted = formatted_integer if num == int(num) else f"{formatted_integer}.{subscript_decimal}"
        if is_negative:
            formatted = "-" + formatted
    except Exception:
        return str(value)
    else:
        return formatted
```

</details>

## 🔧 Function `major_units_to_minor`

```python
def major_units_to_minor(amount_major: float, subdivision: int) -> int
```

Convert major units to minor units without float truncation.

`int(0.01 * 100)` can become `0` on some values; `int(19.99 * 100)` is `1998`.
Rounding to the nearest minor unit keeps a one-kopeck revision as `1`.

Args:

- `amount_major` (`float`): Amount in major units (e.g. rubles).
- `subdivision` (`int`): Minor units per major unit (e.g. `100`).

Returns:

- `int`: Amount in minor units (e.g. kopecks).

<details>
<summary>Code:</summary>

```python
def major_units_to_minor(amount_major: float, subdivision: int) -> int:
    scale = subdivision if subdivision > 0 else 1
    return round(amount_major * scale)
```

</details>
