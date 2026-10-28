"""Fluent checkbox and radio indicators via style painting (no application QSS).

Window stylesheets often blank or replace native Qt indicators. This module paints
WinUI-style checkboxes and radios through a shared `QProxyStyle` applied to each
`QCheckBox` / `QRadioButton`, and helpers for item-view delegates. It never uses
`url(...)` QSS and never calls `QApplication.setStyle`.

Public names keep the historical `lucide_*` prefixes so call sites and tests stay
stable; the glyphs are Fluent rounded squares / circles, not Lucide SVG strokes.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QRect, QRectF, Qt
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QProxyStyle,
    QRadioButton,
    QStyle,
    QStyleFactory,
    QStyleOption,
)

from harrix_swiss_knife.fluent.theme import is_fluent_themed, mix, palette_for
from harrix_swiss_knife.fluent.tokens import RADIUS_CONTROL
from harrix_swiss_knife.qt_lucide_icon import (
    LUCIDE_COLOR_BLUE,
    LUCIDE_COLOR_DARK,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

# WinUI checkbox / radio indicator size.
CHECKBOX_INDICATOR_PX = 20
RADIO_INDICATOR_PX = 20
_DISABLED_COLOR = "#767676"
_INDICATOR_PIXMAP_CACHE: dict[tuple[str, str, str, int, float, bool, bool], QPixmap] = {}


class IndicatorColors:
    """Hex colors for idle, checked, and disabled toggle indicators."""

    def __init__(self, idle: str, checked: str, disabled: str) -> None:
        """Store the three indicator colors."""
        self.idle = idle
        self.checked = checked
        self.disabled = disabled


class LucideToggleStyle(QProxyStyle):
    """Draw Fluent glyphs for checkbox/radio indicators; leave other primitives alone."""

    def drawPrimitive(  # noqa: N802
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Paint Fluent check/radio indicators; otherwise delegate to the base style."""
        if element in (
            QStyle.PrimitiveElement.PE_IndicatorCheckBox,
            QStyle.PrimitiveElement.PE_IndicatorItemViewItemCheck,
        ):
            paint_lucide_checkbox_from_style_option(painter, option, widget)
            return
        if element == QStyle.PrimitiveElement.PE_IndicatorRadioButton:
            paint_lucide_radio_from_style_option(painter, option, widget)
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
    """Process-wide Fluent toggle style holder (avoids QApplication.setProperty)."""

    instance: LucideToggleStyle | None = None


def apply_lucide_checkbox_style(checkbox: QCheckBox) -> None:
    """Apply the shared Fluent toggle style to one `QCheckBox`."""
    style = lucide_toggle_widget_style()
    if checkbox.style() is style:
        return
    checkbox.setStyle(style)


def apply_lucide_checkboxes(root: QWidget) -> None:
    """Apply Fluent checkbox style to every `QCheckBox` under `root`."""
    if isinstance(root, QCheckBox):
        apply_lucide_checkbox_style(root)
    for checkbox in root.findChildren(QCheckBox):
        apply_lucide_checkbox_style(checkbox)


def apply_lucide_indicators(root: QWidget) -> None:
    """Apply Fluent styles to checkboxes and radio buttons under `root`."""
    apply_lucide_checkboxes(root)
    apply_lucide_radios(root)


def apply_lucide_radio_style(radio: QRadioButton) -> None:
    """Apply the shared Fluent toggle style to one `QRadioButton`."""
    style = lucide_toggle_widget_style()
    if radio.style() is style:
        return
    radio.setStyle(style)


def apply_lucide_radios(root: QWidget) -> None:
    """Apply Fluent radio style to every `QRadioButton` under `root`."""
    if isinstance(root, QRadioButton):
        apply_lucide_radio_style(root)
    for radio in root.findChildren(QRadioButton):
        apply_lucide_radio_style(radio)


def indicator_colors(widget: QWidget | None = None) -> IndicatorColors:
    """Return indicator colors: Fluent tokens in themed Windows, brand blue elsewhere."""
    if is_fluent_themed(widget):
        palette = palette_for(widget)
        return IndicatorColors(
            mix(palette.window_bg, palette.control_strong_stroke).name(),
            palette.accent.name(),
            mix(palette.window_bg, palette.text_disabled).name(),
        )
    return IndicatorColors(LUCIDE_COLOR_DARK, LUCIDE_COLOR_BLUE, _DISABLED_COLOR)


def lucide_checkbox_pixmap(
    *,
    checked: bool = False,
    partial: bool = False,
    enabled: bool = True,
    size: int = CHECKBOX_INDICATOR_PX,
    colors: IndicatorColors | None = None,
) -> QPixmap:
    """Return a Fluent checkbox pixmap for the given check state."""
    colors = colors or indicator_colors()
    return _fluent_indicator_pixmap(
        kind="checkbox",
        checked=checked,
        partial=partial,
        enabled=enabled,
        size=size,
        colors=colors,
    )


def lucide_checkbox_widget_style() -> LucideToggleStyle:
    """Return the shared Fluent toggle style (lazy, process-wide)."""
    return lucide_toggle_widget_style()


def lucide_radio_pixmap(
    *,
    checked: bool = False,
    enabled: bool = True,
    size: int = RADIO_INDICATOR_PX,
    colors: IndicatorColors | None = None,
) -> QPixmap:
    """Return a Fluent radio pixmap for the given check state."""
    colors = colors or indicator_colors()
    return _fluent_indicator_pixmap(
        kind="radio",
        checked=checked,
        partial=False,
        enabled=enabled,
        size=size,
        colors=colors,
    )


def lucide_toggle_widget_style() -> LucideToggleStyle:
    """Return the shared Fluent checkbox/radio style (lazy, process-wide)."""
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
    colors: IndicatorColors | None = None,
) -> None:
    """Center a Fluent checkbox pixmap inside `rect`."""
    pixmap = lucide_checkbox_pixmap(checked=checked, partial=partial, enabled=enabled, size=size, colors=colors)
    _paint_centered_pixmap(painter, rect, pixmap, size)


def paint_lucide_checkbox_from_style_option(
    painter: QPainter,
    option: QStyleOption,
    widget: QWidget | None = None,
) -> None:
    """Paint a Fluent checkbox using `option.state` and `option.rect`."""
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
        colors=indicator_colors(widget),
    )


def paint_lucide_radio(
    painter: QPainter,
    rect: QRect,
    *,
    checked: bool = False,
    enabled: bool = True,
    size: int = RADIO_INDICATOR_PX,
    colors: IndicatorColors | None = None,
) -> None:
    """Center a Fluent radio pixmap inside `rect`."""
    pixmap = lucide_radio_pixmap(checked=checked, enabled=enabled, size=size, colors=colors)
    _paint_centered_pixmap(painter, rect, pixmap, size)


def paint_lucide_radio_from_style_option(
    painter: QPainter,
    option: QStyleOption,
    widget: QWidget | None = None,
) -> None:
    """Paint a Fluent radio using `option.state` and `option.rect`."""
    state = option.state
    checked = bool(state & QStyle.StateFlag.State_On)
    enabled = bool(state & QStyle.StateFlag.State_Enabled)
    paint_lucide_radio(painter, option.rect, checked=checked, enabled=enabled, colors=indicator_colors(widget))


def _draw_checkbox(painter: QPainter, size: int, *, checked: bool, partial: bool, fill: QColor, stroke: QColor) -> None:
    box = QRectF(1.5, 1.5, size - 3.0, size - 3.0)
    radius = float(RADIUS_CONTROL)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    if checked or partial:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill)
        painter.drawRoundedRect(box, radius, radius)
        painter.setPen(
            QPen(QColor("#ffffff"), 1.75, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if partial:
            y = box.center().y()
            painter.drawLine(int(box.left() + 3.5), int(y), int(box.right() - 3.5), int(y))
        else:
            path = QPainterPath()
            path.moveTo(box.left() + 3.5, box.center().y())
            path.lineTo(box.left() + 7.0, box.bottom() - 4.5)
            path.lineTo(box.right() - 3.5, box.top() + 4.0)
            painter.drawPath(path)
    else:
        painter.setPen(QPen(stroke, 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(box, radius, radius)


def _draw_radio(painter: QPainter, size: int, *, checked: bool, fill: QColor, stroke: QColor) -> None:
    outer = QRectF(1.5, 1.5, size - 3.0, size - 3.0)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.setPen(QPen(fill if checked else stroke, 1.5))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(outer)
    if checked:
        inset = 5.0
        inner = outer.adjusted(inset, inset, -inset, -inset)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill)
        painter.drawEllipse(inner)


def _fluent_indicator_device_pixel_ratio() -> float:
    app = QGuiApplication.instance()
    if app is not None:
        screen = app.primaryScreen()
        if screen is not None:
            ratio = float(screen.devicePixelRatio())
            if ratio > 0:
                return ratio
    return 1.0


def _fluent_indicator_pixmap(
    *,
    kind: str,
    checked: bool,
    partial: bool,
    enabled: bool,
    size: int,
    colors: IndicatorColors,
) -> QPixmap:
    """Rasterize a Fluent checkbox or radio at `size`."""
    ratio = _fluent_indicator_device_pixel_ratio()
    fill_hex = colors.checked if enabled else colors.disabled
    stroke_hex = colors.idle if enabled else colors.disabled
    cache_key = (kind, fill_hex, stroke_hex, size, ratio, checked, partial)
    cached = _INDICATOR_PIXMAP_CACHE.get(cache_key)
    if cached is not None:
        return cached

    physical = max(1, round(size * ratio))
    pixmap = QPixmap(physical, physical)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.scale(ratio, ratio)
    fill = QColor(fill_hex)
    stroke = QColor(stroke_hex)
    if kind == "radio":
        _draw_radio(painter, size, checked=checked, fill=fill, stroke=stroke)
    else:
        _draw_checkbox(painter, size, checked=checked, partial=partial, fill=fill, stroke=stroke)
    painter.end()
    pixmap.setDevicePixelRatio(ratio)
    _INDICATOR_PIXMAP_CACHE[cache_key] = pixmap
    return pixmap


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
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
    painter.drawPixmap(target, pixmap)
    painter.restore()


# Backward-compatible alias used by tests and older imports.
LucideCheckboxStyle = LucideToggleStyle
