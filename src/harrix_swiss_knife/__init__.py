"""Harrix Swiss Knife — Python application for automating personal tasks in Windows."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .actions.common.base import ActionBase

__all__ = [
    "ActionBase",
]


def __getattr__(name: str) -> Any:
    """Load `ActionBase` lazily so installer imports stay isolated."""
    if name == "ActionBase":
        from .actions.common.base import ActionBase  # noqa: PLC0415

        return ActionBase
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
