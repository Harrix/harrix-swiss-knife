"""Read-only checkbox display for boolean columns stored as 1/0."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QLocale, QModelIndex, QPersistentModelIndex, QRect, QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionButton,
    QStyleOptionViewItem,
)

if TYPE_CHECKING:
    from PySide6.QtGui import QPainter

_TRUTHY_VALUES = frozenset({"1", "true", "yes"})


class CheckboxDisplayDelegate(QStyledItemDelegate):
    """Paint a centered native checkbox instead of raw 1/0 text."""

    def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Hide stored 1/0 text; the checkbox is drawn in `paint`."""
        return ""

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw the row background and a centered checkbox indicator."""
        self.initStyleOption(option, index)
        option.text = ""
        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, widget)

        indicator = QStyleOptionButton()
        indicator.state = QStyle.StateFlag.State_Enabled
        if is_checkbox_cell_checked(index.data(Qt.ItemDataRole.DisplayRole)):
            indicator.state |= QStyle.StateFlag.State_On
        else:
            indicator.state |= QStyle.StateFlag.State_Off
        size = style.sizeFromContents(QStyle.ContentsType.CT_CheckBox, indicator, QSize(), widget)
        if size.width() <= 0 or size.height() <= 0:
            size = QSize(16, 16)
        indicator.rect = QRect(
            option.rect.x() + (option.rect.width() - size.width()) // 2,
            option.rect.y() + (option.rect.height() - size.height()) // 2,
            size.width(),
            size.height(),
        )
        style.drawControl(QStyle.ControlElement.CE_CheckBox, indicator, painter, widget)


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
