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


def edited_source_text_differs(stored: str, edited: str) -> bool:
    """Return whether a manual edit changed source text enough to drop its translation.

    Comparison ignores surrounding whitespace and letter case, so saving the same
    words again does not clear an existing English field.

    Args:

    - `stored` (`str`): Value currently saved in the database.
    - `edited` (`str`): Value about to be saved from the table cell.

    Returns:

    - `bool`: `True` when the English translation for this row should be cleared.

    """
    return stored.strip().casefold() != edited.strip().casefold()
