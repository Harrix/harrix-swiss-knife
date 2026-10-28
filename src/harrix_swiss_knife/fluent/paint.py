"""Small painting helpers shared by paint-based Fluent widgets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen

if TYPE_CHECKING:
    from PySide6.QtCore import QRect
    from PySide6.QtGui import QPaintDevice


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
