"""Shared icon-card grid configuration for command pickers."""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QSizePolicy

CARD_ICON_SIZE = 64
CARD_SPACING = 16


def configure_action_card_grid(list_widget: QListWidget, *, min_height: int | None = None) -> None:
    """Apply the same icon-card layout used by New Markdown command picker."""
    list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    if min_height is not None:
        list_widget.setMinimumHeight(min_height)
    list_widget.setViewMode(QListWidget.ViewMode.IconMode)
    list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
    list_widget.setMovement(QListWidget.Movement.Static)
    list_widget.setSpacing(CARD_SPACING)
    list_widget.setIconSize(QSize(CARD_ICON_SIZE, CARD_ICON_SIZE))
    list_widget.setWordWrap(True)
    list_widget.setUniformItemSizes(False)
    list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    list_widget.setFrameShape(QListWidget.Shape.NoFrame)
