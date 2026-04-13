"""Validation helpers for dynamic SQL fragments.

These helpers are used when a *small* dynamic fragment is necessary (e.g. ORDER BY),
to keep callers from accidentally injecting raw user input.
"""

from __future__ import annotations

import re

from harrix_swiss_knife.apps.common.common import _safe_identifier

_BANNED_SUBSTRINGS = (";", "--", "/*", "*/")
_ORDER_BY_PARTS_WITH_DIRECTION = 2
_BANNED_KEYWORDS = {
    "ATTACH",
    "DETACH",
    "DROP",
    "ALTER",
    "CREATE",
    "INSERT",
    "UPDATE",
    "DELETE",
    "REPLACE",
    "TRUNCATE",
    "VACUUM",
    "PRAGMA",
    "UNION",
    "SELECT",
}

class SqlFragmentValidationError(ValueError):
    """Base error for SQL fragment validation failures."""


class EmptySqlFragmentError(SqlFragmentValidationError):
    """SQL fragment must not be empty."""

    def __init__(self) -> None:
        """Create exception with standard message."""
        super().__init__("Empty SQL fragment")


class EmptyOrderByFragmentError(SqlFragmentValidationError):
    """ORDER BY fragment must not be empty."""

    def __init__(self) -> None:
        """Create exception with standard message."""
        super().__init__("Empty ORDER BY fragment")


class UnsafeOrderByFragmentError(SqlFragmentValidationError):
    """ORDER BY fragment failed validation."""

    def __init__(self, msg: str) -> None:
        """Create exception with validation message."""
        super().__init__(msg)

    @classmethod
    def invalid_direction(cls) -> UnsafeOrderByFragmentError:
        """Direction must be ASC or DESC."""
        return cls("Unsafe ORDER BY fragment (direction must be ASC or DESC)")

    @classmethod
    def too_complex(cls) -> UnsafeOrderByFragmentError:
        """ORDER BY fragment is too complex."""
        return cls("Unsafe ORDER BY fragment (too complex)")


class UnsafeSqlFragmentError(SqlFragmentValidationError):
    """SQL fragment failed validation."""

    def __init__(self, msg: str) -> None:
        """Create exception with validation message."""
        super().__init__(msg)

    @classmethod
    def quoted_literals_not_allowed(cls) -> UnsafeSqlFragmentError:
        """Quoted literals are forbidden; use bound parameters."""
        return cls("Unsafe SQL fragment (quoted literals are not allowed; use bound parameters)")

    @classmethod
    def forbidden_characters(cls) -> UnsafeSqlFragmentError:
        """Fragment contains forbidden characters."""
        return cls("Unsafe SQL fragment (contains forbidden characters)")

    @classmethod
    def no_tokens(cls) -> UnsafeSqlFragmentError:
        """Fragment produced no tokens."""
        return cls("Unsafe SQL fragment (no tokens)")

    @classmethod
    def forbidden_keyword(cls) -> UnsafeSqlFragmentError:
        """Fragment contains forbidden keyword."""
        return cls("Unsafe SQL fragment (contains forbidden keyword)")


def validate_order_by_fragment(fragment: str) -> str:
    """Validate an ORDER BY fragment.

    Accepts a comma-separated list of identifiers with optional ASC/DESC.
    Example: `date DESC, _id ASC`
    """
    frag = _ensure_no_obvious_injection(fragment)

    parts = [p.strip() for p in frag.split(",") if p.strip()]
    if not parts:
        raise EmptyOrderByFragmentError

    validated_parts: list[str] = []
    for part in parts:
        items = part.split()
        if len(items) == 1:
            column = _safe_identifier(items[0])
            validated_parts.append(column)
            continue
        if len(items) == _ORDER_BY_PARTS_WITH_DIRECTION:
            column = _safe_identifier(items[0])
            direction = items[1].upper()
            if direction not in {"ASC", "DESC"}:
                raise UnsafeOrderByFragmentError.invalid_direction()
            validated_parts.append(f"{column} {direction}")
            continue
        raise UnsafeOrderByFragmentError.too_complex()

    return ", ".join(validated_parts)


def validate_where_fragment(fragment: str) -> str:
    """Validate a WHERE/AND fragment that must remain expression-only.

    Policy:
    - Forbids statement separators / comments.
    - Forbids high-risk SQL keywords.
    - Forbids quoted literals; values should be bound parameters (e.g. :name) or numeric.
    """
    frag = _ensure_no_obvious_injection(fragment)

    if "'" in frag or '"' in frag:
        raise UnsafeSqlFragmentError.quoted_literals_not_allowed()

    # Characters whitelist.
    if not re.fullmatch(r"[A-Za-z0-9_:\s<>=!().,%+-]+", frag):
        raise UnsafeSqlFragmentError.forbidden_characters()

    # Token whitelist.
    tokens = re.findall(
        r":[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|<=|>=|!=|=|<|>|\(|\)|,|\+|-|%|\.", frag
    )
    if not tokens:
        raise UnsafeSqlFragmentError.no_tokens()

    allowed_keywords = {"AND", "OR", "NOT", "IN", "IS", "NULL", "LIKE"}
    for token in tokens:
        if token.startswith(":"):
            continue
        if re.fullmatch(r"\d+(?:\.\d+)?", token):
            continue
        if token in {"<=", ">=", "!=", "=", "<", ">", "(", ")", ",", "+", "-", "%", "."}:
            continue
        upper = token.upper()
        if upper in _BANNED_KEYWORDS:
            raise UnsafeSqlFragmentError.forbidden_keyword()
        if upper in allowed_keywords:
            continue
        _safe_identifier(token)

    return frag


def _ensure_no_obvious_injection(fragment: str) -> str:
    frag = fragment.strip()
    if not frag:
        raise EmptySqlFragmentError
    lowered = frag.lower()
    for needle in _BANNED_SUBSTRINGS:
        if needle in frag:
            msg = f"Unsafe SQL fragment (contains {needle!r})"
            raise UnsafeSqlFragmentError(msg)
    # Fast keyword screening; token-level checks run below too.
    if any(f" {kw.lower()} " in f" {lowered} " for kw in (k.lower() for k in _BANNED_KEYWORDS)):
        raise UnsafeSqlFragmentError.forbidden_keyword()
    return frag
