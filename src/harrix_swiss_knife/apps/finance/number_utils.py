"""Number parsing utilities for finance app."""

from __future__ import annotations


def clean_number_text(text: str) -> str:
    """Remove spaces and replace subscript digits with ASCII digits.

    Args:

    - `text` (`str`): Raw string that may contain spaces and Unicode subscript digits.

    Returns:

    - `str`: String with spaces removed and ₀–₉ replaced by 0–9.

    """
    return (
        str(text)
        .replace(" ", "")
        .replace("₀", "0")
        .replace("₁", "1")
        .replace("₂", "2")
        .replace("₃", "3")
        .replace("₄", "4")
        .replace("₅", "5")
        .replace("₆", "6")
        .replace("₇", "7")
        .replace("₈", "8")
        .replace("₉", "9")
    )
