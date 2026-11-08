"""Custom widgets for finance tracker."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel


class ClickableCategoryLabel(QLabel):
    """Status label for the currently selected category (not a combo box)."""
