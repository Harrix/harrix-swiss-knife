"""Common utilities for working with databases."""

from __future__ import annotations

import re


def _safe_identifier(identifier: str) -> str:
    """Return `identifier` unchanged if it is a valid SQL identifier.

    The function guarantees that the returned string is composed only of
    ASCII letters, digits, or underscores and does **not** start with a digit.
    It is therefore safe to interpolate directly into an SQL statement.

    Args:

    - `identifier` (`str`): A candidate string that must be validated to be
      used as a table or column name.

    Returns:

    - `str`: The validated identifier (identical to the input).

    Raises:

    - `ValueError`: If `identifier` contains forbidden characters.

    """
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        msg = f"Illegal SQL identifier: {identifier!r}"
        raise ValueError(msg)
    return identifier

