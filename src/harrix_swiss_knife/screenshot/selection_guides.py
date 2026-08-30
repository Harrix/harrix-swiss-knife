"""Composition guides for the screenshot region overlay (thirds, diagonal, size)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen

if TYPE_CHECKING:
    from PySide6.QtGui import QFontMetrics

_GRID_COLOR = QColor(210, 210, 210, 200)
_DIAGONAL_COLOR = QColor(120, 200, 255, 230)
_LABEL_COLOR = QColor(230, 230, 230, 240)
_ANGLE_COLOR = QColor(200, 200, 200, 230)
_LABEL_GAP = 4
_ARC_RADIUS = 22
_MIN_ARC_RADIUS = 8
_MIN_GUIDE_SIZE = 2


@dataclass(frozen=True)
class GuideLabel:
    """One measurement label placed relative to the selection rectangle."""

    text: str
    box: QRect
    color: QColor
    inside: bool


def diagonal_angle_degrees(width: int, height: int) -> float:
    """Return the angle (degrees) between the bottom edge and the falling diagonal."""
    if width <= 0:
        return 90.0
    if height <= 0:
        return 0.0
    return math.degrees(math.atan2(height, width))


def diagonal_length_px(width: int, height: int) -> int:
    """Return the diagonal length in whole pixels."""
    return round(math.hypot(width, height))


def format_angle_label(angle_degrees: float) -> str:
    """Return the angle text shown under the bottom-right corner."""
    return f"{angle_degrees:.4f} °"


def guide_offsets(length: int) -> tuple[int, int, int]:
    """Return 1/3, 1/2, and 2/3 offsets along `length`."""
    return length // 3, length // 2, (2 * length) // 3


def place_angle_label(
    rect: QRect,
    bounds: QRect,
    *,
    text_width: int,
    text_height: int,
    gap: int = _LABEL_GAP,
) -> tuple[QRect, bool]:
    """Place the angle label below the bottom-right corner, or inside if it does not fit."""
    x = rect.right() - text_width
    y = rect.bottom() + gap
    box = QRect(x, y, text_width, text_height)
    if bounds.contains(box):
        return box, False
    inner = QRect(rect.right() - gap - text_width, rect.bottom() - gap - text_height, text_width, text_height)
    return _clamp_inside(inner, rect, text_width, text_height, gap), True


def place_height_label(
    rect: QRect,
    bounds: QRect,
    *,
    text_width: int,
    text_height: int,
    gap: int = _LABEL_GAP,
) -> tuple[QRect, bool]:
    """Place the height label to the left of the frame, or inside if it does not fit."""
    x = rect.left() - gap - text_width
    y = rect.center().y() - text_height // 2
    box = QRect(x, y, text_width, text_height)
    if bounds.contains(box):
        return box, False
    inner = QRect(rect.left() + gap, rect.center().y() - text_height // 2, text_width, text_height)
    return _clamp_inside(inner, rect, text_width, text_height, gap), True


def place_width_label(
    rect: QRect,
    bounds: QRect,
    *,
    text_width: int,
    text_height: int,
    gap: int = _LABEL_GAP,
) -> tuple[QRect, bool]:
    """Place the width label above the frame, or inside if it does not fit."""
    x = rect.center().x() - text_width // 2
    y = rect.top() - gap - text_height
    box = QRect(x, y, text_width, text_height)
    if bounds.contains(box):
        return box, False
    inner = QRect(rect.center().x() - text_width // 2, rect.top() + gap, text_width, text_height)
    return _clamp_inside(inner, rect, text_width, text_height, gap), True


def selection_guide_labels(
    rect: QRect,
    bounds: QRect,
    metrics: QFontMetrics,
    *,
    gap: int = _LABEL_GAP,
) -> tuple[GuideLabel, GuideLabel, GuideLabel, GuideLabel]:
    """Return width, height, diagonal, and angle labels for `rect`."""
    width = rect.width()
    height = rect.height()
    width_text = str(width)
    height_text = str(height)
    diagonal_text = str(diagonal_length_px(width, height))
    angle_text = format_angle_label(diagonal_angle_degrees(width, height))

    width_box, width_inside = place_width_label(
        rect,
        bounds,
        text_width=metrics.horizontalAdvance(width_text),
        text_height=metrics.height(),
        gap=gap,
    )
    height_box, height_inside = place_height_label(
        rect,
        bounds,
        text_width=metrics.horizontalAdvance(height_text),
        text_height=metrics.height(),
        gap=gap,
    )
    angle_box, angle_inside = place_angle_label(
        rect,
        bounds,
        text_width=metrics.horizontalAdvance(angle_text),
        text_height=metrics.height(),
        gap=gap,
    )
    diagonal_box = _diagonal_label_box(
        rect,
        metrics.horizontalAdvance(diagonal_text),
        metrics.height(),
    )
    return (
        GuideLabel(width_text, width_box, _LABEL_COLOR, width_inside),
        GuideLabel(height_text, height_box, _LABEL_COLOR, height_inside),
        GuideLabel(diagonal_text, diagonal_box, _DIAGONAL_COLOR, inside=True),
        GuideLabel(angle_text, angle_box, _ANGLE_COLOR, angle_inside),
    )


def paint_selection_guides(painter: QPainter, rect: QRect, bounds: QRect) -> None:
    """Draw thirds/halves, diagonal, size labels, and the bottom-right angle."""
    if rect.width() < _MIN_GUIDE_SIZE or rect.height() < _MIN_GUIDE_SIZE:
        return
    frame = rect.adjusted(0, 0, -1, -1)
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=False)
    _paint_grid(painter, frame)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    _paint_diagonal(painter, frame)
    _paint_angle_arc(painter, frame)
    font = QFont(painter.font())
    font.setPointSize(10)
    painter.setFont(font)
    for label in selection_guide_labels(rect, bounds, painter.fontMetrics()):
        painter.setPen(label.color)
        painter.drawText(label.box, Qt.AlignmentFlag.AlignCenter, label.text)
    painter.restore()


def _clamp_inside(box: QRect, rect: QRect, text_width: int, text_height: int, gap: int) -> QRect:
    x = min(max(box.x(), rect.left() + gap), max(rect.left() + gap, rect.right() - gap - text_width))
    y = min(max(box.y(), rect.top() + gap), max(rect.top() + gap, rect.bottom() - gap - text_height))
    return QRect(x, y, text_width, text_height)


def _diagonal_label_box(rect: QRect, text_width: int, text_height: int) -> QRect:
    center = rect.center()
    return QRect(center.x() - text_width // 2, center.y() - text_height // 2, text_width, text_height)


def _paint_angle_arc(painter: QPainter, frame: QRect) -> None:
    width = frame.width()
    height = frame.height()
    angle = diagonal_angle_degrees(width, height)
    radius = min(_ARC_RADIUS, max(_MIN_ARC_RADIUS, width // 4), max(_MIN_ARC_RADIUS, height // 4))
    if radius < _MIN_ARC_RADIUS:
        return
    corner = frame.bottomRight()
    arc_rect = QRect(corner.x() - radius, corner.y() - radius, radius * 2, radius * 2)
    painter.setPen(QPen(_ANGLE_COLOR, 1))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawArc(arc_rect, 180 * 16, -int(angle * 16))


def _paint_diagonal(painter: QPainter, frame: QRect) -> None:
    painter.setPen(QPen(_DIAGONAL_COLOR, 1))
    painter.drawLine(frame.topLeft(), frame.bottomRight())


def _paint_grid(painter: QPainter, frame: QRect) -> None:
    painter.setPen(QPen(_GRID_COLOR, 1))
    left = frame.left()
    top = frame.top()
    for offset in guide_offsets(frame.width()):
        x = left + offset
        painter.drawLine(QPoint(x, frame.top()), QPoint(x, frame.bottom()))
    for offset in guide_offsets(frame.height()):
        y = top + offset
        painter.drawLine(QPoint(frame.left(), y), QPoint(frame.right(), y))
