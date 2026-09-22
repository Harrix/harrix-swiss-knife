"""Compact integer and decimal spin boxes with narrow stacked step buttons."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QDoubleSpinBox, QProxyStyle, QSpinBox, QStyle

if TYPE_CHECKING:
    from PySide6.QtWidgets import QStyleOptionComplex, QWidget

_BUTTON_WIDTH_PX = 11
_BUTTON_RIGHT_MARGIN_PX = 5
_BUTTON_VERTICAL_MARGIN_PX = 2


class CompactDoubleSpinBox(QDoubleSpinBox):
    """Decimal spin box with narrow up/down buttons stacked on the right."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a compact decimal spin box."""
        super().__init__(parent)
        self._compact_style = _CompactSpinBoxStyle()
        self.setStyle(self._compact_style)


class CompactSpinBox(QSpinBox):
    """Integer spin box with narrow up/down buttons stacked on the right."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a compact integer spin box."""
        super().__init__(parent)
        self._compact_style = _CompactSpinBoxStyle()
        self.setStyle(self._compact_style)


class _CompactSpinBoxStyle(QProxyStyle):
    """Change only spin-button geometry while retaining native painting."""

    def subControlRect(  # noqa: N802
        self,
        control: QStyle.ComplexControl,
        option: QStyleOptionComplex,
        sub_control: QStyle.SubControl,
        widget: QWidget,
    ) -> QRect:
        """Return narrow vertically stacked spin-button rectangles."""
        rect = super().subControlRect(control, option, sub_control, widget)
        if control != QStyle.ComplexControl.CC_SpinBox:
            return rect

        spin_rect = option.rect
        button_width = min(_BUTTON_WIDTH_PX, spin_rect.width())
        button_x = spin_rect.right() - _BUTTON_RIGHT_MARGIN_PX - button_width + 1
        buttons_height = max(0, spin_rect.height() - 2 * _BUTTON_VERTICAL_MARGIN_PX)
        upper_height = (buttons_height + 1) // 2
        buttons_y = spin_rect.top() + _BUTTON_VERTICAL_MARGIN_PX

        if sub_control == QStyle.SubControl.SC_SpinBoxUp:
            return QRect(button_x, buttons_y, button_width, upper_height)
        if sub_control == QStyle.SubControl.SC_SpinBoxDown:
            return QRect(
                button_x,
                buttons_y + upper_height,
                button_width,
                buttons_height - upper_height,
            )
        if sub_control == QStyle.SubControl.SC_SpinBoxEditField:
            rect.setRight(button_x - 1)
        return rect
