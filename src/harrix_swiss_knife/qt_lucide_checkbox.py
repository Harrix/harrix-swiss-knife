"""Lucide checkbox indicators via style painting (no application QSS).

Window stylesheets often blank native Qt check indicators on checkable item
views. This module paints Lucide `square` / `square-check` / `square-minus`
through a shared `QProxyStyle` applied to each `QCheckBox`, and helpers for
item-view delegates. It never uses `url(...)` QSS (that previously broke fonts)
and never calls `QApplication.setStyle` (crash-prone).

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QProxyStyle,
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
_DISABLED_COLOR = "#767676"
_STYLE_PROP = "_hsk_lucide_checkbox_style"


class LucideCheckboxStyle(QProxyStyle):
    """Draw Lucide glyphs for checkbox indicators; leave every other primitive alone."""

    def drawPrimitive(  # noqa: N802
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Paint Lucide for check indicators; otherwise delegate to the base style."""
        if element in (
            QStyle.PrimitiveElement.PE_IndicatorCheckBox,
            QStyle.PrimitiveElement.PE_IndicatorItemViewItemCheck,
        ):
            paint_lucide_checkbox_from_style_option(painter, option)
            return
        super().drawPrimitive(element, option, painter, widget)

    def pixelMetric(  # noqa: N802
        self,
        metric: QStyle.PixelMetric,
        option: QStyleOption | None = None,
        widget: QWidget | None = None,
    ) -> int:
        """Reserve a fixed box for check indicators so item views keep layout space."""
        if metric in (
            QStyle.PixelMetric.PM_IndicatorWidth,
            QStyle.PixelMetric.PM_IndicatorHeight,
        ):
            return CHECKBOX_INDICATOR_PX
        return super().pixelMetric(metric, option, widget)


def apply_lucide_checkbox_style(checkbox: QCheckBox) -> None:
    """Apply the shared Lucide checkbox style to one `QCheckBox`."""
    style = lucide_checkbox_widget_style()
    if checkbox.style() is style:
        return
    checkbox.setStyle(style)


def apply_lucide_checkboxes(root: QWidget) -> None:
    """Apply Lucide checkbox style to every `QCheckBox` under `root`."""
    if isinstance(root, QCheckBox):
        apply_lucide_checkbox_style(root)
    for checkbox in root.findChildren(QCheckBox):
        apply_lucide_checkbox_style(checkbox)


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


def lucide_checkbox_widget_style() -> LucideCheckboxStyle:
    """Return the shared Lucide checkbox style (lazy, process-wide)."""
    app = QApplication.instance()
    if isinstance(app, QApplication):
        held = app.property(_STYLE_PROP)
        if isinstance(held, LucideCheckboxStyle):
            return held
    base = QStyleFactory.create("Fusion")
    style = LucideCheckboxStyle(base)
    if isinstance(app, QApplication):
        app.setProperty(_STYLE_PROP, style)
    return style


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
