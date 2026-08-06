"""Helpers for Qt window modality in the multi-app process.

Finance, fitness, food, and habits share one `QApplication`. Prefer
`WindowModal` so a dialog or toast only blocks its owner window hierarchy,
not sibling apps.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


def set_owner_window_modal(widget: QWidget) -> None:
    """Make `widget` modal only to its parent window hierarchy.

    Must be called before `show()` / `exec()`; changing modality on an
    already-visible window is ignored by Qt.

    """
    widget.setWindowModality(Qt.WindowModality.WindowModal)
