"""Which action output file the main window should display (thread-safe)."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

_lock = threading.Lock()
_active_holder: list[Path | None] = [None]


def get_active_action_output() -> Path | None:
    """Return the active output path, or ``None`` if no action has run yet."""
    with _lock:
        return _active_holder[0]


def register_active_action_output(path: Path) -> None:
    """Mark ``path`` as the file the UI should poll for action output."""
    with _lock:
        _active_holder[0] = path.resolve()
