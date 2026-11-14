---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `fmt_compact`](#-function-fmt_compact)
- [🔧 Function `fmt_date`](#-function-fmt_date)
- [🔧 Function `fmt_money`](#-function-fmt_money)
- [🔧 Function `fmt_number`](#-function-fmt_number)
- [🔧 Function `setup_date_axis`](#-function-setup_date_axis)

</details>

## 🔧 Function `fmt_compact`

```python
def fmt_compact(value: float, *, unit: str = '') -> str
```

Format a value for an axis tick or a point chip (`1.31M`, `25.6K`).

Args:

- `value` (`float`): Number to format.
- `unit` (`str`): Optional suffix such as `₽`, joined with a non-breaking space.

Returns:

- `str`: Compact text. Whole counts stay integers (`10`, not `10.0`).

<details>
<summary>Code:</summary>

```python
def fmt_compact(value: float, *, unit: str = "") -> str:
    number = float(value)
    sign = "-" if number < 0 else ""
    magnitude = abs(number)
    if magnitude >= _MILLION:
        body = f"{magnitude / _MILLION:.2f}".rstrip("0").rstrip(".")
        suffix = "M"
    elif magnitude >= _THOUSAND:
        body = f"{magnitude / _THOUSAND:.1f}".rstrip("0").rstrip(".")
        suffix = "K"
    elif abs(magnitude - round(magnitude)) < _WHOLE_EPSILON:
        body = str(round(magnitude))
        suffix = ""
    else:
        body = f"{magnitude:.1f}".rstrip("0").rstrip(".")
        suffix = ""
    text = f"{sign}{body}{suffix}"
    if unit:
        return f"{text}{_NBSP}{unit}"
    return text
```

</details>

## 🔧 Function `fmt_date`

```python
def fmt_date(value: date | datetime) -> str
```

Format a calendar day as `Sat, 14 Nov 2026`.

A datetime that carries a clock time appends `HH:MM`.

<details>
<summary>Code:</summary>

```python
def fmt_date(value: date | datetime) -> str:
    day = value.date() if isinstance(value, datetime) else value
    text = f"{_WEEKDAYS[day.weekday()]}, {day.day} {_MONTHS[day.month - 1]} {day.year}"
    if isinstance(value, datetime) and (value.hour or value.minute or value.second):
        text = f"{text} {value.strftime('%H:%M')}"
    return text
```

</details>

## 🔧 Function `fmt_money`

```python
def fmt_money(value: float, currency_symbol: str, *, decimals: int = 2) -> str
```

Format money with a space thousands separator and the currency symbol.

Fractional digits follow [`format_amount`](../finance/number_utils.g.md#-function-format_amount) (subscript), matching Transactions.

<details>
<summary>Code:</summary>

```python
def fmt_money(value: float, currency_symbol: str, *, decimals: int = 2) -> str:
    format_amount_with_currency = _finance_amounts()[2]
    places = 0 if _is_whole(value) and decimals == 0 else decimals
    if places == 0:
        return format_amount_with_currency(f"{value:.2f}", currency_symbol, always_decimals=False, decimals=2)
    return format_amount_with_currency(f"{value:.{places}f}", currency_symbol, always_decimals=True, decimals=places)
```

</details>

## 🔧 Function `fmt_number`

```python
def fmt_number(value: float, *, decimals: int | None = None) -> str
```

Format a number with a space thousands separator.

Args:

- `value` (`float`): Number to format.
- `decimals` (`int | None`): Fractional digits. When omitted, whole numbers
  stay integers and other values keep two places.

Returns:

- `str`: Text such as `1 314 733.₄₇` or `10`.

<details>
<summary>Code:</summary>

```python
def fmt_number(value: float, *, decimals: int | None = None) -> str:
    format_amount = _finance_amounts()[1]
    if decimals is None:
        decimals = 0 if _is_whole(value) else 2
    if decimals <= 0:
        return format_amount(f"{value:.2f}", always_decimals=False, decimals=2)
    return format_amount(f"{value:.{decimals}f}", always_decimals=True, decimals=decimals)
```

</details>

## 🔧 Function `setup_date_axis`

```python
def setup_date_axis(ax: Axes, *, period: str | None = None) -> None
```

Use an even date locator and horizontal concise labels.

Args:

- `ax` (`Axes`): Axes whose horizontal values are Matplotlib date numbers.
- `period` (`str | None`): `Days`, `Months`, or `Years`. All three share
  `AutoDateLocator`; the period only loosens the tick budget.

<details>
<summary>Code:</summary>

```python
def setup_date_axis(ax: Axes, *, period: str | None = None) -> None:
    if period == "Years":
        locator = mdates.AutoDateLocator(minticks=3, maxticks=8)
    elif period == "Months":
        locator = mdates.AutoDateLocator(minticks=4, maxticks=12)
    else:
        locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.tick_params(axis="x", labelrotation=0)
    for label in ax.get_xticklabels():
        label.set_rotation(0)
        label.set_ha("center")
```

</details>
