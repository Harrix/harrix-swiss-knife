"""Read-only checkbox display for boolean columns stored as 1/0."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QLocale, QModelIndex, QPersistentModelIndex, QRect, Qt
from PySide6.QtWidgets import (
    QApplication,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)

from harrix_swiss_knife.qt_lucide_checkbox import CHECKBOX_INDICATOR_PX, paint_lucide_checkbox

if TYPE_CHECKING:
    from PySide6.QtGui import QPainter

_TRUTHY_VALUES = frozenset({"1", "true", "yes"})


class CheckboxDisplayDelegate(QStyledItemDelegate):
    """Paint a centered Lucide checkbox instead of raw 1/0 text."""

    def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Hide stored 1/0 text; the checkbox is drawn in `paint`."""
        return ""

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw the row background and a centered Lucide checkbox indicator."""
        self.initStyleOption(option, index)
        option.text = ""
        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, widget)

        size = CHECKBOX_INDICATOR_PX
        rect = QRect(
            option.rect.x() + (option.rect.width() - size) // 2,
            option.rect.y() + (option.rect.height() - size) // 2,
            size,
            size,
        )
        paint_lucide_checkbox(
            painter,
            rect,
            checked=is_checkbox_cell_checked(index.data(Qt.ItemDataRole.DisplayRole)),
            enabled=bool(option.state & QStyle.StateFlag.State_Enabled),
        )


def is_checkbox_cell_checked(value: object) -> bool:
    """Return whether a model cell value represents a checked flag.

    Args:

    - `value` (`object`): Raw cell value from the model.

    Returns:

    - `bool`: `True` for `1`, `true`, `yes`, or a non-zero integer.

    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    text = str(value).strip().lower()
    return text in _TRUTHY_VALUES
