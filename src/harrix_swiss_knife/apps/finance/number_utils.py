"""Number parsing and safe arithmetic expression evaluation for finance app."""

from __future__ import annotations

import math
import re

from harrix_pylib.funcs_text import (
    clean_number_text,
    evaluate_arithmetic_expression,
    try_evaluate_arithmetic_expression,
)

_SUBSCRIPT_DIGITS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
_SUBSCRIPT_TO_ASCII = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
# Typographic non-breaking space between amount and currency (GOST / Gramota.ru).
NBSP = "\u00a0"


def format_amount(value: float | str, *, always_decimals: bool = True, decimals: int | None = None) -> str:
    """Format amount with spaces for thousands and subscript decimal digits.

    Args:

    - `value` (`float | str`): The value to format.
    - `always_decimals` (`bool`): When `True` (default), always show fractional digits.
      When `False`, omit decimals for whole numbers.
    - `decimals` (`int | None`): Fractional digits to keep. When `None`, infer from
      the input (at least 2, at most 6) so rates with more places are preserved.

    Returns:

    - `str`: Formatted text (e.g. `1 234.₅₆`).

    """
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


def format_amount_with_currency(
    value: float | str,
    currency_symbol: str,
    *,
    always_decimals: bool = True,
    decimals: int | None = None,
) -> str:
    """Format an amount and append the currency symbol with a non-breaking space."""
    return with_currency(
        format_amount(value, always_decimals=always_decimals, decimals=decimals),
        currency_symbol,
    )


def major_units_to_minor(amount_major: float, subdivision: int) -> int:
    """Convert major units to minor units without float truncation.

    `int(0.01 * 100)` can become `0` on some values; `int(19.99 * 100)` is `1998`.
    Rounding to the nearest minor unit keeps a one-kopeck revision as `1`.

    Args:

    - `amount_major` (`float`): Amount in major units (e.g. rubles).
    - `subdivision` (`int`): Minor units per major unit (e.g. `100`).

    Returns:

    - `int`: Amount in minor units (e.g. kopecks).

    """
    scale = subdivision if subdivision > 0 else 1
    return round(amount_major * scale)


def sqlite_max_major_amount(subdivision: int) -> float:
    """Return the largest major amount that fits in a SQLite INTEGER minor-unit column.

    Args:

    - `subdivision` (`int`): Minor units per major unit (e.g. `100`).

    Returns:

    - `float`: Maximum major-unit amount for that currency.

    """
    scale = subdivision if subdivision > 0 else 1
    maximum = math.nextafter(_SQLITE_INT64_MAX / scale, 0.0)
    if major_units_to_minor(maximum, scale) > _SQLITE_INT64_MAX:
        maximum = math.nextafter(maximum, 0.0)
    return maximum


def with_currency(amount_text: str, currency_symbol: str) -> str:
    """Join a formatted amount and currency with a non-breaking space.

    Args:

    - `amount_text` (`str`): Already formatted amount (may include subscript decimals).
    - `currency_symbol` (`str`): Currency symbol such as `₽`.

    Returns:

    - `str`: `amount` + NBSP + `symbol`, or just `amount` when the symbol is empty.

    """
    amount = str(amount_text).rstrip()
    symbol = str(currency_symbol or "").strip()
    if not symbol:
        return amount
    return f"{amount}{NBSP}{symbol}"


def _infer_decimal_places(cleaned: str) -> int:
    if "." not in cleaned:
        return 2
    frac = cleaned.split(".", 1)[1]
    if not frac:
        return 2
    return max(2, min(6, len(frac)))


_SQLITE_INT64_MAX = 2**63 - 1


__all__ = [
    "NBSP",
    "clean_number_text",
    "evaluate_arithmetic_expression",
    "format_amount",
    "format_amount_with_currency",
    "major_units_to_minor",
    "sqlite_max_major_amount",
    "try_evaluate_arithmetic_expression",
    "with_currency",
]
