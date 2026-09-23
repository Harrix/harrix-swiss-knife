"""Number parsing and safe arithmetic expression evaluation for finance app."""

from __future__ import annotations

import math

from harrix_pylib.funcs_text import (
    clean_number_text,
    evaluate_arithmetic_expression,
    try_evaluate_arithmetic_expression,
)


def format_amount(value: float | str) -> str:
    """Format amount with spaces for thousands separator and subscript decimals.

    Args:

    - `value` (`float | str`): The value to format.

    Returns:

    - `str`: The formatted text with spaces as thousands separators and subscript decimal digits.

    """
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


_SQLITE_INT64_MAX = 2**63 - 1


__all__ = [
    "clean_number_text",
    "evaluate_arithmetic_expression",
    "format_amount",
    "major_units_to_minor",
    "sqlite_max_major_amount",
    "try_evaluate_arithmetic_expression",
]
