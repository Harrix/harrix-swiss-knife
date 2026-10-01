"""Lucide checkbox and radio indicators via style painting (no application QSS).

Window stylesheets often blank or replace native Qt indicators. This module paints
Lucide glyphs through a shared `QProxyStyle` applied to each `QCheckBox` /
`QRadioButton`, and helpers for item-view delegates. It never uses `url(...)` QSS
(that previously broke fonts) and never calls `QApplication.setStyle`
(crash-prone).

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QProxyStyle,
    QRadioButton,
    QStyle,
    QStyleFactory,
    QStyleOption,
)

from harrix_swiss_knife.qt_lucide_icon import (
    LUCIDE_COLOR_DARK,
    LUCIDE_COLOR_GREEN,
    create_lucide_icon,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

CHECKBOX_INDICATOR_PX = 16
RADIO_INDICATOR_PX = 16
_DISABLED_COLOR = "#767676"


class LucideToggleStyle(QProxyStyle):
    """Draw Lucide glyphs for checkbox/radio indicators; leave other primitives alone."""

    def drawPrimitive(  # noqa: N802
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Paint Lucide for check/radio indicators; otherwise delegate to the base style."""
        if element in (
            QStyle.PrimitiveElement.PE_IndicatorCheckBox,
            QStyle.PrimitiveElement.PE_IndicatorItemViewItemCheck,
        ):
            paint_lucide_checkbox_from_style_option(painter, option)
            return
        if element == QStyle.PrimitiveElement.PE_IndicatorRadioButton:
            paint_lucide_radio_from_style_option(painter, option)
            return
        super().drawPrimitive(element, option, painter, widget)

    def pixelMetric(  # noqa: N802
        self,
        metric: QStyle.PixelMetric,
        option: QStyleOption | None = None,
        widget: QWidget | None = None,
    ) -> int:
        """Reserve a fixed box for check and radio indicators."""
        if metric in (
            QStyle.PixelMetric.PM_IndicatorWidth,
            QStyle.PixelMetric.PM_IndicatorHeight,
        ):
            return CHECKBOX_INDICATOR_PX
        if metric in (
            QStyle.PixelMetric.PM_ExclusiveIndicatorWidth,
            QStyle.PixelMetric.PM_ExclusiveIndicatorHeight,
        ):
            return RADIO_INDICATOR_PX
        return super().pixelMetric(metric, option, widget)


class _SharedToggleStyle:
    """Process-wide Lucide toggle style holder (avoids QApplication.setProperty)."""

    instance: LucideToggleStyle | None = None


def apply_lucide_checkbox_style(checkbox: QCheckBox) -> None:
    """Apply the shared Lucide toggle style to one `QCheckBox`."""
    style = lucide_toggle_widget_style()
    if checkbox.style() is style:
        return
    checkbox.setStyle(style)


def apply_lucide_checkboxes(root: QWidget) -> None:
    """Apply Lucide checkbox style to every `QCheckBox` under `root`."""
    if isinstance(root, QCheckBox):
        apply_lucide_checkbox_style(root)
    for checkbox in root.findChildren(QCheckBox):
        apply_lucide_checkbox_style(checkbox)


def apply_lucide_indicators(root: QWidget) -> None:
    """Apply Lucide styles to checkboxes and radio buttons under `root`."""
    apply_lucide_checkboxes(root)
    apply_lucide_radios(root)


def apply_lucide_radio_style(radio: QRadioButton) -> None:
    """Apply the shared Lucide toggle style to one `QRadioButton`."""
    style = lucide_toggle_widget_style()
    if radio.style() is style:
        return
    radio.setStyle(style)


def apply_lucide_radios(root: QWidget) -> None:
    """Apply Lucide radio style to every `QRadioButton` under `root`."""
    if isinstance(root, QRadioButton):
        apply_lucide_radio_style(root)
    for radio in root.findChildren(QRadioButton):
        apply_lucide_radio_style(radio)


def lucide_checkbox_pixmap(
    *,
    checked: bool = False,
    partial: bool = False,
    enabled: bool = True,
    size: int = CHECKBOX_INDICATOR_PX,
) -> QPixmap:
    """Return a Lucide checkbox pixmap for the given check state."""
    if partial:
        name = "square-minus"
        color = _DISABLED_COLOR if not enabled else LUCIDE_COLOR_DARK
    elif checked:
        name = "square-check"
        color = _DISABLED_COLOR if not enabled else LUCIDE_COLOR_GREEN
    else:
        name = "square"
        color = _DISABLED_COLOR if not enabled else LUCIDE_COLOR_DARK
    return create_lucide_icon(name, size, color=color).pixmap(size, size)


def lucide_checkbox_widget_style() -> LucideToggleStyle:
    """Return the shared Lucide toggle style (lazy, process-wide)."""
    return lucide_toggle_widget_style()


def lucide_radio_pixmap(
    *,
    checked: bool = False,
    enabled: bool = True,
    size: int = RADIO_INDICATOR_PX,
) -> QPixmap:
    """Return a Lucide radio pixmap for the given check state."""
    if checked:
        name = "circle-dot"
        color = _DISABLED_COLOR if not enabled else LUCIDE_COLOR_GREEN
    else:
        name = "circle"
        color = _DISABLED_COLOR if not enabled else LUCIDE_COLOR_DARK
    return create_lucide_icon(name, size, color=color).pixmap(size, size)


def lucide_toggle_widget_style() -> LucideToggleStyle:
    """Return the shared Lucide checkbox/radio style (lazy, process-wide)."""
    if _SharedToggleStyle.instance is None:
        base = QStyleFactory.create("Fusion")
        if base is None:
            base = QStyleFactory.create("Windows")
        _SharedToggleStyle.instance = LucideToggleStyle(base)
    return _SharedToggleStyle.instance


def paint_lucide_checkbox(
    painter: QPainter,
    rect: QRect,
    *,
    checked: bool = False,
    partial: bool = False,
    enabled: bool = True,
    size: int = CHECKBOX_INDICATOR_PX,
) -> None:
    """Center a Lucide checkbox pixmap inside `rect`."""
    pixmap = lucide_checkbox_pixmap(checked=checked, partial=partial, enabled=enabled, size=size)
    _paint_centered_pixmap(painter, rect, pixmap, size)


def paint_lucide_checkbox_from_style_option(painter: QPainter, option: QStyleOption) -> None:
    """Paint a Lucide checkbox using `option.state` and `option.rect`."""
    state = option.state
    partial = bool(state & QStyle.StateFlag.State_NoChange)
    checked = bool(state & QStyle.StateFlag.State_On) and not partial
    enabled = bool(state & QStyle.StateFlag.State_Enabled)
    paint_lucide_checkbox(
        painter,
        option.rect,
        checked=checked,
        partial=partial,
        enabled=enabled,
    )


def paint_lucide_radio(
    painter: QPainter,
    rect: QRect,
    *,
    checked: bool = False,
    enabled: bool = True,
    size: int = RADIO_INDICATOR_PX,
) -> None:
    """Center a Lucide radio pixmap inside `rect`."""
    pixmap = lucide_radio_pixmap(checked=checked, enabled=enabled, size=size)
    _paint_centered_pixmap(painter, rect, pixmap, size)


def paint_lucide_radio_from_style_option(painter: QPainter, option: QStyleOption) -> None:
    """Paint a Lucide radio using `option.state` and `option.rect`."""
    state = option.state
    checked = bool(state & QStyle.StateFlag.State_On)
    enabled = bool(state & QStyle.StateFlag.State_Enabled)
    paint_lucide_radio(painter, option.rect, checked=checked, enabled=enabled)


def _paint_centered_pixmap(painter: QPainter, rect: QRect, pixmap: QPixmap, size: int) -> None:
    if pixmap.isNull():
        return
    target = QRect(
        rect.x() + (rect.width() - size) // 2,
        rect.y() + (rect.height() - size) // 2,
        size,
        size,
    )
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.drawPixmap(target, pixmap)
    painter.restore()


# Backward-compatible alias used by tests and older imports.
LucideCheckboxStyle = LucideToggleStyle
