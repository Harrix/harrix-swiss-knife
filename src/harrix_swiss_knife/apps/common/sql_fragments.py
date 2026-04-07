"""Validation helpers for dynamic SQL fragments.

These helpers are used when a *small* dynamic fragment is necessary (e.g. ORDER BY),
to keep callers from accidentally injecting raw user input.
"""

from __future__ import annotations

import re

from harrix_swiss_knife.apps.common.common import _safe_identifier

_BANNED_SUBSTRINGS = (";", "--", "/*", "*/")
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


def validate_order_by_fragment(fragment: str) -> str:
    """Validate an ORDER BY fragment.

    Accepts a comma-separated list of identifiers with optional ASC/DESC.
    Example: `date DESC, _id ASC`
    """
    frag = _ensure_no_obvious_injection(fragment)

    parts = [p.strip() for p in frag.split(",") if p.strip()]
    if not parts:
        raise ValueError("Empty ORDER BY fragment")

    validated_parts: list[str] = []
    for part in parts:
        items = part.split()
        if len(items) == 1:
            column = _safe_identifier(items[0])
            validated_parts.append(column)
            continue
        if len(items) == 2:
            column = _safe_identifier(items[0])
            direction = items[1].upper()
            if direction not in {"ASC", "DESC"}:
                raise ValueError("Unsafe ORDER BY fragment (direction must be ASC or DESC)")
            validated_parts.append(f"{column} {direction}")
            continue
        raise ValueError("Unsafe ORDER BY fragment (too complex)")

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
        raise ValueError("Unsafe SQL fragment (quoted literals are not allowed; use bound parameters)")

    # Characters whitelist.
    if not re.fullmatch(r"[A-Za-z0-9_:\s<>=!().,%+-]+", frag):
        raise ValueError("Unsafe SQL fragment (contains forbidden characters)")

    # Token whitelist.
    tokens = re.findall(
        r":[A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|<=|>=|!=|=|<|>|\(|\)|,|\+|-|%|\.", frag
    )
    if not tokens:
        raise ValueError("Unsafe SQL fragment (no tokens)")

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
            raise ValueError("Unsafe SQL fragment (contains forbidden keyword)")
        if upper in allowed_keywords:
            continue
        _safe_identifier(token)

    return frag


def _ensure_no_obvious_injection(fragment: str) -> str:
    frag = fragment.strip()
    if not frag:
        raise ValueError("Empty SQL fragment")
    lowered = frag.lower()
    for needle in _BANNED_SUBSTRINGS:
        if needle in frag:
            raise ValueError(f"Unsafe SQL fragment (contains {needle!r})")
    # Fast keyword screening; token-level checks run below too.
    if any(f" {kw.lower()} " in f" {lowered} " for kw in (k.lower() for k in _BANNED_KEYWORDS)):
        raise ValueError("Unsafe SQL fragment (contains forbidden keyword)")
    return frag
