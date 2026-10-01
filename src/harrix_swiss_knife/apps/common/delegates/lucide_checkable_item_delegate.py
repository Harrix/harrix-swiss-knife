"""Item-view delegate that paints Lucide check indicators."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QRect, Qt
from PySide6.QtWidgets import (
    QApplication,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)

from harrix_swiss_knife.qt_lucide_checkbox import CHECKBOX_INDICATOR_PX, paint_lucide_checkbox

if TYPE_CHECKING:
    from PySide6.QtGui import QPainter


class LucideCheckableItemDelegate(QStyledItemDelegate):
    """Draw Lucide square / square-check over checkable item-view rows.

    Parent window stylesheets often leave `PE_IndicatorItemViewItemCheck` blank.
    This delegate keeps the normal row paint, then overlays a Lucide checkbox.

    """

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint the row, then overlay a Lucide checkbox when the item is checkable."""
        self.initStyleOption(option, index)
        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter, widget)

        check_value = index.data(Qt.ItemDataRole.CheckStateRole)
        if check_value is None and not (option.features & QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator):
            return

        rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemCheckIndicator, option, widget)
        if not rect.isValid() or rect.width() <= 0 or rect.height() <= 0:
            size = CHECKBOX_INDICATOR_PX
            rect = QRect(
                option.rect.x() + 4,
                option.rect.y() + (option.rect.height() - size) // 2,
                size,
                size,
            )

        state = Qt.CheckState.Unchecked
        if check_value is not None:
            state = check_value if isinstance(check_value, Qt.CheckState) else Qt.CheckState(int(check_value))
        paint_lucide_checkbox(
            painter,
            rect,
            checked=state == Qt.CheckState.Checked,
            partial=state == Qt.CheckState.PartiallyChecked,
            enabled=bool(option.state & QStyle.StateFlag.State_Enabled),
        )
