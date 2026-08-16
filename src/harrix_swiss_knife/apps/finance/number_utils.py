"""Number parsing and safe arithmetic expression evaluation for finance app."""

from __future__ import annotations

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


__all__ = [
    "clean_number_text",
    "evaluate_arithmetic_expression",
    "format_amount",
    "try_evaluate_arithmetic_expression",
]
