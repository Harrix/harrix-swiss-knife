"""Text casing helpers for tracker form fields."""

from __future__ import annotations


def capitalize_first_letter(text: str) -> str:
    """Uppercase the first letter, skipping leading quotes and emoji.

    Args:

    - `text` (`str`): Value from a food name or finance description field.

    Returns:

    - `str`: Stripped text with the first alphabetic character uppercased.

    """
    cleaned = text.strip()
    for index, char in enumerate(cleaned):
        if not char.isalpha():
            continue
        upper = char.upper()
        if upper == char:
            return cleaned
        return f"{cleaned[:index]}{upper}{cleaned[index + 1 :]}"
    return cleaned
