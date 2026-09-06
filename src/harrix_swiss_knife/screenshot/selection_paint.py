"""Shared painting for ShareX-like selection frames (dim + blue border + handles)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPen

if TYPE_CHECKING:
    from PySide6.QtGui import QPixmap

SELECTION_DIM_COLOR = QColor(0, 0, 0, 120)
SELECTION_BORDER_COLOR = QColor(0, 174, 255)
SELECTION_HANDLE_FILL = QColor(0, 174, 255)
SELECTION_BORDER_WIDTH = 2
SELECTION_HANDLE_DRAW = 6


def paint_selection_frame(
    painter: QPainter,
    bounds: QRect,
    clear_rect: QRect | None,
    *,
    pixmap: QPixmap | None = None,
    pixmap_source: QRect | None = None,
    show_handles: bool = False,
    border_width: int = SELECTION_BORDER_WIDTH,
) -> None:
    """Dim `bounds`, punch a clear hole for `clear_rect`, then draw the blue frame.

    When `pixmap` is set, the clear hole is filled by redrawing that pixmap (or
    `pixmap_source` mapped into `clear_rect`). Otherwise the hole is left as
    whatever was already painted under the dim layer.

    Args:

    - `painter` (`QPainter`): Active painter.
    - `bounds` (`QRect`): Area that receives the dim overlay (widget/image bounds).
    - `clear_rect` (`QRect | None`): Undimmed selection; `None` dims everything.
    - `pixmap` (`QPixmap | None`): Optional source redrawn inside the clear hole.
    - `pixmap_source` (`QRect | None`): Source rect in pixmap pixels; defaults to
      the full pixmap scaled into `clear_rect`.
    - `show_handles` (`bool`): Draw resize handles on the frame.
    - `border_width` (`int`): Selection border thickness.

    """
    if not bounds.isValid() or bounds.isEmpty():
        return
    painter.fillRect(bounds, SELECTION_DIM_COLOR)
    if clear_rect is None or not clear_rect.isValid() or clear_rect.isEmpty():
        return
    hole = clear_rect.intersected(bounds)
    if hole.isEmpty():
        return
    if pixmap is not None and not pixmap.isNull():
        source = pixmap_source if pixmap_source is not None else QRect(QPoint(0, 0), pixmap.size())
        painter.drawPixmap(hole, pixmap, source)
    pen = QPen(SELECTION_BORDER_COLOR, border_width)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRect(hole.adjusted(0, 0, -1, -1))
    if show_handles:
        paint_selection_handles(painter, hole)


def paint_selection_handles(painter: QPainter, rect: QRect) -> None:
    """Draw the eight blue resize handles on `rect`."""
    if not rect.isValid() or rect.isEmpty():
        return
    half = SELECTION_HANDLE_DRAW // 2
    points = [
        rect.topLeft(),
        QPoint(rect.center().x(), rect.top()),
        rect.topRight(),
        QPoint(rect.left(), rect.center().y()),
        QPoint(rect.right(), rect.center().y()),
        rect.bottomLeft(),
        QPoint(rect.center().x(), rect.bottom()),
        rect.bottomRight(),
    ]
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(SELECTION_HANDLE_FILL)
    for point in points:
        painter.drawRect(point.x() - half, point.y() - half, SELECTION_HANDLE_DRAW, SELECTION_HANDLE_DRAW)
