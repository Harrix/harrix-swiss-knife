"""Hit-testing, handles, and transforms for editable screenshot annotations."""

from __future__ import annotations

import math
from itertools import pairwise
from typing import Literal

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QFont, QFontMetricsF, QPainter, QPen

from harrix_swiss_knife.screenshot.annotations import Annotation, AnnotationTool, constrain_shape_end
from harrix_swiss_knife.screenshot.selection_edit import cursor_for_handle
from harrix_swiss_knife.screenshot.selection_paint import (
    SELECTION_BORDER_COLOR,
    SELECTION_HANDLE_DRAW,
    SELECTION_HANDLE_FILL,
)

AnnotationHandle = Literal["move", "start", "end", "n", "s", "e", "w", "ne", "nw", "se", "sw"]

_BOX_TOOLS = frozenset({AnnotationTool.ELLIPSE, AnnotationTool.PEN, AnnotationTool.RECTANGLE})
_LINE_TOOLS = frozenset({AnnotationTool.ARROW, AnnotationTool.LINE})
_MIN_BOX = 2.0
_MIN_SHAPE_POINTS = 2
_NEAR_ZERO = 1e-6
_HIT_PADDING = 6.0


def annotation_bounds(annotation: Annotation) -> QRectF:
    """Axis-aligned bounds of `annotation` in image coordinates."""
    points = annotation.points
    if not points:
        return QRectF()
    if annotation.tool == AnnotationTool.TEXT:
        return _text_bounds(annotation)
    if annotation.tool in {AnnotationTool.RECTANGLE, AnnotationTool.ELLIPSE, AnnotationTool.CROP}:
        if len(points) < _MIN_SHAPE_POINTS:
            return QRectF(points[0], points[0])
        return QRectF(points[0], points[-1]).normalized()
    return _points_bounds(points)


def apply_annotation_edit(
    annotation: Annotation,
    handle: AnnotationHandle,
    origin_points: list[QPointF],
    press: QPointF,
    current: QPointF,
    *,
    shift: bool,
) -> list[QPointF]:
    """Return updated points for `handle` dragged from `press` to `current`."""
    if handle == "move" or annotation.tool == AnnotationTool.TEXT:
        delta = current - press
        return [QPointF(p.x() + delta.x(), p.y() + delta.y()) for p in origin_points]
    if annotation.tool in _LINE_TOOLS:
        return _edit_line_points(annotation.tool, handle, origin_points, current, shift=shift)
    origin_rect = annotation_bounds(
        Annotation(tool=annotation.tool, points=origin_points, style=annotation.style, text=annotation.text)
    )
    if origin_rect.isEmpty():
        delta = current - press
        return [QPointF(p.x() + delta.x(), p.y() + delta.y()) for p in origin_points]
    new_rect = _transform_rect(origin_rect, handle, press, current)
    if shift and annotation.tool in {AnnotationTool.ELLIPSE, AnnotationTool.RECTANGLE}:
        new_rect = _square_rect_from_handle(origin_rect, new_rect, handle)
    if annotation.tool in {AnnotationTool.RECTANGLE, AnnotationTool.ELLIPSE}:
        return [new_rect.topLeft(), new_rect.bottomRight()]
    return _map_points_from_rect(origin_points, origin_rect, new_rect)


def cursor_for_annotation_handle(handle: AnnotationHandle | None) -> str:
    """Return a Qt cursor shape name for an annotation handle."""
    if handle in {None, "start", "end", "move"}:
        return "SizeAllCursor" if handle else "CrossCursor"
    return cursor_for_handle(handle)


def hit_test_annotation(
    annotation: Annotation,
    pos: QPointF,
    *,
    handle_size: float,
) -> AnnotationHandle | None:
    """Return the handle under `pos`, preferring resize handles over move."""
    bounds = annotation_bounds(annotation)
    if bounds.isNull():
        return None
    for handle, point in _handle_points(annotation, bounds):
        if _handle_rect(point, handle_size).contains(pos):
            return handle
    padding = max(handle_size, annotation.style.width, _HIT_PADDING)
    if annotation.tool in _LINE_TOOLS:
        if len(annotation.points) < _MIN_SHAPE_POINTS:
            return None
        if _distance_to_segment(pos, annotation.points[0], annotation.points[-1]) <= padding:
            return "move"
        return None
    if annotation.tool == AnnotationTool.PEN:
        if _hit_polyline(annotation.points, pos, padding) or bounds.adjusted(
            -padding, -padding, padding, padding
        ).contains(pos):
            return "move"
        return None
    if annotation.tool == AnnotationTool.ELLIPSE:
        return "move" if _hit_ellipse_stroke(bounds, pos, padding) else None
    if annotation.tool == AnnotationTool.RECTANGLE:
        return "move" if _hit_rect_stroke(bounds, pos, padding) else None
    inflated = bounds.adjusted(-padding, -padding, padding, padding)
    if inflated.contains(pos):
        return "move"
    return None


def hit_test_topmost(
    annotations: list[Annotation],
    pos: QPointF,
    *,
    handle_size: float,
    selected_index: int | None = None,
) -> tuple[int, AnnotationHandle] | None:
    """Hit-test from front to back; selected handles are checked first."""
    if selected_index is not None and 0 <= selected_index < len(annotations):
        handle = hit_test_annotation(annotations[selected_index], pos, handle_size=handle_size)
        if handle is not None:
            return selected_index, handle
    for index in range(len(annotations) - 1, -1, -1):
        if index == selected_index:
            continue
        handle = hit_test_annotation(annotations[index], pos, handle_size=handle_size)
        if handle is not None:
            return index, handle
    return None


def paint_annotation_selection(painter: QPainter, annotation: Annotation, *, handle_size: float) -> None:
    """Draw the selection frame and handles for `annotation`."""
    bounds = annotation_bounds(annotation)
    if bounds.isNull():
        return
    pad = max(handle_size * 0.5, _MIN_BOX)
    frame = bounds.adjusted(-pad, -pad, pad, pad)
    pen = QPen(SELECTION_BORDER_COLOR, 1.0)
    pen.setStyle(Qt.PenStyle.DashLine)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRect(frame)
    half = max(SELECTION_HANDLE_DRAW / 2, handle_size / 2)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(SELECTION_HANDLE_FILL)
    for _handle, point in _handle_points(annotation, bounds):
        painter.drawRect(QRectF(point.x() - half, point.y() - half, half * 2, half * 2))


def _distance_to_segment(point: QPointF, start: QPointF, end: QPointF) -> float:
    dx = end.x() - start.x()
    dy = end.y() - start.y()
    length2 = dx * dx + dy * dy
    if length2 < _NEAR_ZERO:
        return math.hypot(point.x() - start.x(), point.y() - start.y())
    t = max(0.0, min(1.0, ((point.x() - start.x()) * dx + (point.y() - start.y()) * dy) / length2))
    proj = QPointF(start.x() + t * dx, start.y() + t * dy)
    return math.hypot(point.x() - proj.x(), point.y() - proj.y())


def _edit_line_points(
    tool: AnnotationTool,
    handle: AnnotationHandle,
    origin_points: list[QPointF],
    current: QPointF,
    *,
    shift: bool,
) -> list[QPointF]:
    start = QPointF(origin_points[0])
    end = QPointF(origin_points[-1])
    if handle == "start":
        return [constrain_shape_end(tool, end, current, shift=shift), end]
    return [start, constrain_shape_end(tool, start, current, shift=shift)]


def _handle_points(annotation: Annotation, bounds: QRectF) -> list[tuple[AnnotationHandle, QPointF]]:
    if annotation.tool in _LINE_TOOLS and len(annotation.points) >= _MIN_SHAPE_POINTS:
        return [("start", QPointF(annotation.points[0])), ("end", QPointF(annotation.points[-1]))]
    if annotation.tool == AnnotationTool.TEXT:
        return [("move", bounds.center())]
    if annotation.tool in _BOX_TOOLS or annotation.tool == AnnotationTool.CROP:
        return [
            ("nw", bounds.topLeft()),
            ("n", QPointF(bounds.center().x(), bounds.top())),
            ("ne", bounds.topRight()),
            ("e", QPointF(bounds.right(), bounds.center().y())),
            ("se", bounds.bottomRight()),
            ("s", QPointF(bounds.center().x(), bounds.bottom())),
            ("sw", bounds.bottomLeft()),
            ("w", QPointF(bounds.left(), bounds.center().y())),
        ]
    return []


def _handle_rect(point: QPointF, handle_size: float) -> QRectF:
    half = max(handle_size, SELECTION_HANDLE_DRAW) / 2
    return QRectF(point.x() - half, point.y() - half, half * 2, half * 2)


def _hit_ellipse_stroke(bounds: QRectF, pos: QPointF, padding: float) -> bool:
    outer = bounds.adjusted(-padding, -padding, padding, padding)
    if not _point_in_ellipse(outer, pos):
        return False
    inner = bounds.adjusted(padding, padding, -padding, -padding)
    return not (inner.width() > _MIN_BOX and inner.height() > _MIN_BOX and _point_in_ellipse(inner, pos))


def _hit_polyline(points: list[QPointF], pos: QPointF, padding: float) -> bool:
    if not points:
        return False
    if len(points) < _MIN_SHAPE_POINTS:
        return math.hypot(pos.x() - points[0].x(), pos.y() - points[0].y()) <= padding
    return any(_distance_to_segment(pos, start, end) <= padding for start, end in pairwise(points))


def _hit_rect_stroke(bounds: QRectF, pos: QPointF, padding: float) -> bool:
    outer = bounds.adjusted(-padding, -padding, padding, padding)
    if not outer.contains(pos):
        return False
    inner = bounds.adjusted(padding, padding, -padding, -padding)
    return not (inner.width() > _MIN_BOX and inner.height() > _MIN_BOX and inner.contains(pos))


def _map_points_from_rect(points: list[QPointF], origin: QRectF, target: QRectF) -> list[QPointF]:
    ox, oy = origin.left(), origin.top()
    sx = target.width() / origin.width() if origin.width() >= _MIN_BOX else 1.0
    sy = target.height() / origin.height() if origin.height() >= _MIN_BOX else 1.0
    return [QPointF(target.left() + (p.x() - ox) * sx, target.top() + (p.y() - oy) * sy) for p in points]


def _point_in_ellipse(bounds: QRectF, pos: QPointF) -> bool:
    if bounds.width() <= 0 or bounds.height() <= 0:
        return False
    rx = bounds.width() / 2
    ry = bounds.height() / 2
    if rx < _MIN_BOX or ry < _MIN_BOX:
        return bounds.contains(pos)
    dx = (pos.x() - bounds.center().x()) / rx
    dy = (pos.y() - bounds.center().y()) / ry
    return dx * dx + dy * dy <= 1.0


def _points_bounds(points: list[QPointF]) -> QRectF:
    xs = [p.x() for p in points]
    ys = [p.y() for p in points]
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    return QRectF(QPointF(left, top), QPointF(max(left + 1, right), max(top + 1, bottom)))


def _square_rect_from_handle(origin: QRectF, current: QRectF, handle: AnnotationHandle) -> QRectF:
    size = min(abs(current.width()), abs(current.height()))
    size = max(size, _MIN_BOX)
    left, top, right, bottom = origin.left(), origin.top(), origin.right(), origin.bottom()
    if "w" in handle:
        left = right - size
    if "e" in handle:
        right = left + size
    if "n" in handle:
        top = bottom - size
    if "s" in handle:
        bottom = top + size
    if handle == "n":
        left = origin.center().x() - size / 2
        right = left + size
    if handle == "s":
        left = origin.center().x() - size / 2
        right = left + size
    if handle == "w":
        top = origin.center().y() - size / 2
        bottom = top + size
    if handle == "e":
        top = origin.center().y() - size / 2
        bottom = top + size
    return QRectF(QPointF(left, top), QPointF(right, bottom)).normalized()


def _text_bounds(annotation: Annotation) -> QRectF:
    if not annotation.points:
        return QRectF()
    origin = annotation.points[0]
    font = QFont()
    font.setPointSizeF(max(10.0, annotation.style.width * 4))
    metrics = QFontMetricsF(font)
    text = annotation.text or "…"
    width = max(metrics.horizontalAdvance(text), 8.0)
    height = max(metrics.height(), 10.0)
    return QRectF(origin.x(), origin.y() - metrics.ascent(), width, height)


def _transform_rect(origin: QRectF, handle: AnnotationHandle, press: QPointF, current: QPointF) -> QRectF:
    delta = current - press
    left, top, right, bottom = origin.left(), origin.top(), origin.right(), origin.bottom()
    if handle == "move":
        return origin.translated(delta)
    if "w" in handle:
        left = origin.left() + delta.x()
    if "e" in handle:
        right = origin.right() + delta.x()
    if "n" in handle:
        top = origin.top() + delta.y()
    if "s" in handle:
        bottom = origin.bottom() + delta.y()
    rect = QRectF(QPointF(left, top), QPointF(right, bottom)).normalized()
    if rect.width() < _MIN_BOX:
        if "w" in handle:
            rect.setLeft(rect.right() - _MIN_BOX)
        else:
            rect.setWidth(_MIN_BOX)
    if rect.height() < _MIN_BOX:
        if "n" in handle:
            rect.setTop(rect.bottom() - _MIN_BOX)
        else:
            rect.setHeight(_MIN_BOX)
    return rect
