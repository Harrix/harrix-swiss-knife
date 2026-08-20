"""Windows GUI installer package (online/offline frozen EXE)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from harrix_swiss_knife.installer.wizard import main, run_uninstall_wizard, run_wizard

__all__ = ["main", "run_uninstall_wizard", "run_wizard"]


def __getattr__(name: str) -> Any:
    """Load wizard entry points lazily."""
    if name in {"main", "run_wizard", "run_uninstall_wizard"}:
        from harrix_swiss_knife.installer import wizard  # noqa: PLC0415

        return getattr(wizard, name)
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
