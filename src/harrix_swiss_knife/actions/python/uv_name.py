"""Validation helpers for uv project and library names."""

from __future__ import annotations

import re

_UV_PROJECT_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")


def validate_uv_project_name(name: str) -> str | None:
    """Return an error message when *name* is invalid, otherwise `None`."""
    stripped = name.strip()
    if not stripped:
        return "Name must not be empty."
    if " " in name:
        return "Name must not contain spaces."
    if not _UV_PROJECT_NAME_RE.fullmatch(stripped):
        return "Name must contain only English letters, digits, hyphens, and underscores."
    return None
