---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `number_utils.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `NBSP`](#-constant-nbsp)
- [🔧 Function `format_amount`](#-function-format_amount)
- [🔧 Function `format_amount_with_currency`](#-function-format_amount_with_currency)
- [🔧 Function `major_units_to_minor`](#-function-major_units_to_minor)
- [🔧 Function `sqlite_max_major_amount`](#-function-sqlite_max_major_amount)
- [🔧 Function `with_currency`](#-function-with_currency)

</details>

## 📎 Constant `NBSP`

```python
NBSP = '\xa0'
```

_No docstring provided._

## 🔧 Function `format_amount`

```python
def format_amount(value: float | str, *, always_decimals: bool = True, decimals: int | None = None) -> str
```

Format amount with spaces for thousands and subscript decimal digits.

Args:

- `value` (`float | str`): The value to format.
- `always_decimals` (`bool`): When `True` (default), always show fractional digits.
  When `False`, omit decimals for whole numbers.
- `decimals` (`int | None`): Fractional digits to keep. When `None`, infer from
  the input (at least 2, at most 6) so rates with more places are preserved.

Returns:

- `str`: Formatted text (e.g. `1 234.₅₆`).

<details>
<summary>Code:</summary>

```python
def format_amount(value: float | str, *, always_decimals: bool = True, decimals: int | None = None) -> str:
    try:
        text = str(value).strip()
        is_negative = text.startswith("-")
        if is_negative:
            text = text[1:].strip()

        # Strip currency / letters that may already be in the cell.
        text = re.sub(r"[^\d.]", "", text.translate(_SUBSCRIPT_TO_ASCII))
        try:
            num = float(text)
        except (ValueError, TypeError):
            return str(value)

        places = decimals if decimals is not None else _infer_decimal_places(text)
        num_str = f"{num:.{places}f}"
        integer_part, decimal_part = num_str.split(".")

        formatted_integer = ""
        for i, digit in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                formatted_integer = " " + formatted_integer
            formatted_integer = digit + formatted_integer

        if not always_decimals and abs(num - round(num)) < 10 ** (-places):
            formatted = formatted_integer
        else:
            formatted = f"{formatted_integer}.{decimal_part.translate(_SUBSCRIPT_DIGITS)}"

        if is_negative:
            formatted = f"-{formatted}"
    except Exception:
        return str(value)
    else:
        return formatted
```

</details>

## 🔧 Function `format_amount_with_currency`

```python
def format_amount_with_currency(value: float | str, currency_symbol: str, *, always_decimals: bool = True, decimals: int | None = None) -> str
```

Format an amount and append the currency symbol with a non-breaking space.

<details>
<summary>Code:</summary>

```python
def format_amount_with_currency(
    value: float | str,
    currency_symbol: str,
    *,
    always_decimals: bool = True,
    decimals: int | None = None,
) -> str:
    return with_currency(
        format_amount(value, always_decimals=always_decimals, decimals=decimals),
        currency_symbol,
    )
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

## 🔧 Function `sqlite_max_major_amount`

```python
def sqlite_max_major_amount(subdivision: int) -> float
```

Return the largest major amount that fits in a SQLite INTEGER minor-unit column.

Args:

- `subdivision` (`int`): Minor units per major unit (e.g. `100`).

Returns:

- `float`: Maximum major-unit amount for that currency.

<details>
<summary>Code:</summary>

```python
def sqlite_max_major_amount(subdivision: int) -> float:
    scale = subdivision if subdivision > 0 else 1
    maximum = math.nextafter(_SQLITE_INT64_MAX / scale, 0.0)
    if major_units_to_minor(maximum, scale) > _SQLITE_INT64_MAX:
        maximum = math.nextafter(maximum, 0.0)
    return maximum
```

</details>

## 🔧 Function `with_currency`

```python
def with_currency(amount_text: str, currency_symbol: str) -> str
```

Join a formatted amount and currency with a non-breaking space.

Args:

- `amount_text` (`str`): Already formatted amount (may include subscript decimals).
- `currency_symbol` (`str`): Currency symbol such as `₽`.

Returns:

- `str`: `amount` + NBSP + `symbol`, or just `amount` when the symbol is empty.

<details>
<summary>Code:</summary>

```python
def with_currency(amount_text: str, currency_symbol: str) -> str:
    amount = str(amount_text).rstrip()
    symbol = str(currency_symbol or "").strip()
    if not symbol:
        return amount
    return f"{amount}{NBSP}{symbol}"
```

</details>
