"""Shared icon-card grid configuration for command pickers."""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QSizePolicy

CARD_ICON_SIZE = 64
CARD_SPACING = 8
# Wider cells so command titles wrap on fewer lines (default IconMode width ≈ icon size).
CARD_GRID_CELL_WIDTH = 140
CARD_TEXT_AREA_HEIGHT = 36
CARD_GRID_CELL_HEIGHT = CARD_ICON_SIZE + CARD_TEXT_AREA_HEIGHT
CARD_MIN_SCALE = 0.82


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
    list_widget.setGridSize(QSize(CARD_GRID_CELL_WIDTH, CARD_GRID_CELL_HEIGHT))
    list_widget.setWordWrap(True)
    list_widget.setUniformItemSizes(False)
    list_widget.setStyleSheet(
        "QListWidget::item { padding-top: 0px; padding-bottom: 0px; margin: 0px; }",
    )
    list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    list_widget.setFrameShape(QListWidget.Shape.NoFrame)


def resolve_action_card_grid_metrics(available_width: int, item_count: int) -> tuple[int, int]:
    """Return adaptive `(cell_width, icon_size)` metrics for an icon-card row."""
    if available_width <= 0 or item_count <= 0:
        return CARD_GRID_CELL_WIDTH, CARD_ICON_SIZE

    columns = min(item_count, max(1, (available_width + CARD_SPACING) // (CARD_GRID_CELL_WIDTH + CARD_SPACING)))
    if columns < item_count:
        extra_columns = columns + 1
        width_for_extra = (available_width - (extra_columns - 1) * CARD_SPACING) // extra_columns
        if width_for_extra / CARD_GRID_CELL_WIDTH >= CARD_MIN_SCALE:
            columns = extra_columns

    cell_width = (available_width - (columns - 1) * CARD_SPACING) // columns
    cell_width = max(1, cell_width)
    scale = min(1.0, cell_width / CARD_GRID_CELL_WIDTH)
    icon_size = max(48, round(CARD_ICON_SIZE * scale))
    return cell_width, icon_size


def sync_action_card_grid(list_widget: QListWidget) -> bool:
    """Fit as many cards as practical into each row at the current width."""
    cell_width, icon_size = resolve_action_card_grid_metrics(
        list_widget.viewport().width(),
        list_widget.count(),
    )
    grid_size = QSize(cell_width, icon_size + CARD_TEXT_AREA_HEIGHT)
    icon_qsize = QSize(icon_size, icon_size)
    if list_widget.gridSize() == grid_size and list_widget.iconSize() == icon_qsize:
        return False
    list_widget.setIconSize(icon_qsize)
    list_widget.setGridSize(grid_size)
    list_widget.doItemsLayout()
    return True
