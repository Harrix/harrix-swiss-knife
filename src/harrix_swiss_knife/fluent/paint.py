"""Small painting helpers shared by paint-based Fluent widgets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen

from harrix_swiss_knife.fluent.theme import mix

if TYPE_CHECKING:
    from PySide6.QtCore import QRect
    from PySide6.QtGui import QPaintDevice
    from PySide6.QtWidgets import QWidget

    from harrix_swiss_knife.fluent.tokens import FluentPalette

_SPLITTER_DOT_COUNT = 3
_SPLITTER_DOT_RADIUS = 1.75
_SPLITTER_DOT_GAP = 5.0


def antialiased_painter(device: QPaintDevice) -> QPainter:
    """Return a `QPainter` on `device` with antialiasing and smooth pixmaps."""
    painter = QPainter(device)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, on=True)
    return painter


def inset(rect: QRect | QRectF, amount: float = 0.5) -> QRectF:
    """Return `rect` shrunk by `amount` on every side (crisp 1 px strokes)."""
    result = QRectF(rect)
    return result.adjusted(amount, amount, -amount, -amount)


def paint_fluent_splitter_handle(
    device: QWidget,
    palette: FluentPalette,
    orientation: Qt.Orientation,
    *,
    hovered: bool,
    pressed: bool,
) -> None:
    """Paint a Fluent splitter handle: 1px divider, three dots on hover/press.

    Args:

    - `device` (`QWidget`): Handle widget to paint onto.
    - `palette` (`FluentPalette`): Theme colors.
    - `orientation` (`Qt.Orientation`): Parent splitter orientation.
    - `hovered` (`bool`): Pointer is over the handle.
    - `pressed` (`bool`): Handle is being dragged.

    """
    painter = antialiased_painter(device)
    rect = device.rect()
    divider = mix(palette.window_bg, palette.divider)
    pen = QPen(divider)
    pen.setWidth(1)
    painter.setPen(pen)
    if orientation == Qt.Orientation.Horizontal:
        x = rect.center().x()
        painter.drawLine(x, rect.top(), x, rect.bottom())
    else:
        y = rect.center().y()
        painter.drawLine(rect.left(), y, rect.right(), y)

    if hovered or pressed:
        fill = palette.accent_pressed if pressed else palette.accent
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill)
        cx = float(rect.center().x())
        cy = float(rect.center().y())
        span = (_SPLITTER_DOT_COUNT - 1) * _SPLITTER_DOT_GAP
        start = -span / 2
        for index in range(_SPLITTER_DOT_COUNT):
            offset = start + index * _SPLITTER_DOT_GAP
            center = QPointF(cx, cy + offset) if orientation == Qt.Orientation.Horizontal else QPointF(cx + offset, cy)
            painter.drawEllipse(center, _SPLITTER_DOT_RADIUS, _SPLITTER_DOT_RADIUS)
    painter.end()


def paint_surface(
    painter: QPainter,
    rect: QRect | QRectF,
    fill: QColor | None,
    stroke: QColor | None = None,
    radius: float = 0.0,
    *,
    stroke_width: float = 1.0,
) -> None:
    """Fill and optionally stroke a rounded rectangle.

    Args:

    - `painter` (`QPainter`): Active painter.
    - `rect` (`QRect | QRectF`): Outer bounds.
    - `fill` (`QColor | None`): Fill color; `None` leaves the inside empty.
    - `stroke` (`QColor | None`): Border color; `None` draws no border.
    - `radius` (`float`): Corner radius.
    - `stroke_width` (`float`): Border width. Defaults to `1.0`.

    """
    painter.save()
    if stroke is not None and stroke.alpha() > 0:
        pen = QPen(stroke)
        pen.setWidthF(stroke_width)
        painter.setPen(pen)
        target = inset(rect, stroke_width / 2)
    else:
        painter.setPen(Qt.PenStyle.NoPen)
        target = QRectF(rect)
    painter.setBrush(fill if fill is not None else Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(target, radius, radius)
    painter.restore()


def rounded_path(rect: QRect | QRectF, radius: float) -> QPainterPath:
    """Return a rounded-rectangle path (handy for clipping images)."""
    path = QPainterPath()
    path.addRoundedRect(QRectF(rect), radius, radius)
    return path


def with_alpha(color: QColor, alpha: int) -> QColor:
    """Return a copy of `color` with a new alpha channel (0-255)."""
    result = QColor(color)
    result.setAlpha(max(0, min(255, alpha)))
    return result
