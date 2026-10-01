"""Item-view delegate that paints Lucide check indicators."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QStyledItemDelegate, QWidget

from harrix_swiss_knife.qt_lucide_checkbox import LucideToggleStyle, lucide_toggle_widget_style

if TYPE_CHECKING:
    from PySide6.QtCore import QModelIndex, QPersistentModelIndex
    from PySide6.QtGui import QPainter
    from PySide6.QtWidgets import QStyleOptionViewItem


class LucideCheckableItemDelegate(QStyledItemDelegate):
    """Draw Lucide square / square-check for checkable item-view rows.

    Applies the shared `LucideToggleStyle` to the parent view so
    `PE_IndicatorItemViewItemCheck` is Lucide only (no native gray box underneath).

    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Install on `parent` and give that view the Lucide toggle style."""
        super().__init__(parent)
        if parent is not None and not isinstance(parent.style(), LucideToggleStyle):
            parent.setStyle(lucide_toggle_widget_style())

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint the row; the view style draws the Lucide check indicator."""
        super().paint(painter, option, index)
