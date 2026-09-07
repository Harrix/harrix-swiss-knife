"""Magnetic snapping of annotation points to other annotation edges."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF

from harrix_swiss_knife.screenshot.annotation_edit import AnnotationHandle, annotation_bounds
from harrix_swiss_knife.screenshot.annotations import Annotation, AnnotationTool

if TYPE_CHECKING:
    from collections.abc import Sequence

ANNOTATION_SNAP_THRESHOLD = 8.0

_BOX_SHIFT_TOOLS = frozenset({AnnotationTool.ELLIPSE, AnnotationTool.RECTANGLE})
_LINE_TOOLS = frozenset({AnnotationTool.ARROW, AnnotationTool.LINE})
_MIN_BOX = 2.0
_MIN_SHAPE_POINTS = 2
_NEAR_ZERO = 1e-6


@dataclass(frozen=True, slots=True)
class AnnotationSnapResult:
    """Snapped points plus active guide coordinates in image space."""

    points: list[QPointF]
    x_guide: float | None = None
    y_guide: float | None = None


def collect_annotation_guides(
    annotations: Sequence[Annotation],
    *,
    exclude_index: int | None = None,
    bounds: QRectF | None = None,
) -> tuple[list[float], list[float]]:
    """Collect unique X/Y guides from `annotations` (and optional image `bounds`)."""
    xs: set[float] = set()
    ys: set[float] = set()
    if bounds is not None and bounds.isValid():
        xs.add(bounds.left())
        xs.add(bounds.right())
        ys.add(bounds.top())
        ys.add(bounds.bottom())
    for index, item in enumerate(annotations):
        if index == exclude_index:
            continue
        for point in item.points:
            xs.add(point.x())
            ys.add(point.y())
        if item.tool in _LINE_TOOLS:
            if len(item.points) >= _MIN_SHAPE_POINTS:
                start, end = item.points[0], item.points[-1]
                xs.add((start.x() + end.x()) / 2)
                ys.add((start.y() + end.y()) / 2)
            continue
        frame = annotation_bounds(item)
        if frame.isNull() or not frame.isValid():
            continue
        xs.update((frame.left(), frame.right(), frame.center().x()))
        ys.update((frame.top(), frame.bottom(), frame.center().y()))
    return sorted(xs), sorted(ys)


def snap_annotation_edit(
    annotation: Annotation,
    handle: AnnotationHandle,
    points: list[QPointF],
    x_guides: Sequence[float],
    y_guides: Sequence[float],
    *,
    threshold: float = ANNOTATION_SNAP_THRESHOLD,
    shift: bool = False,
) -> AnnotationSnapResult:
    """Snap `points` of an in-progress edit to nearby annotation guides."""
    if not points or (not x_guides and not y_guides):
        return AnnotationSnapResult([QPointF(p) for p in points])
    if handle in {"start", "end"} and annotation.tool in _LINE_TOOLS:
        return _snap_line_endpoint(handle, points, x_guides, y_guides, threshold=threshold, shift=shift)
    if handle == "move":
        return _snap_translate(annotation, points, x_guides, y_guides, threshold=threshold)
    if shift and annotation.tool in _BOX_SHIFT_TOOLS:
        return AnnotationSnapResult([QPointF(p) for p in points])
    return _snap_box_handles(annotation, handle, points, x_guides, y_guides, threshold=threshold)


def snap_point(
    point: QPointF,
    x_guides: Sequence[float],
    y_guides: Sequence[float],
    *,
    threshold: float = ANNOTATION_SNAP_THRESHOLD,
    snap_x: bool = True,
    snap_y: bool = True,
) -> tuple[QPointF, float | None, float | None]:
    """Snap `point` independently on each axis; return the point and active guides."""
    x, x_guide = (point.x(), None)
    y, y_guide = (point.y(), None)
    if snap_x:
        x, x_guide = _snap_value(point.x(), x_guides, threshold)
    if snap_y:
        y, y_guide = _snap_value(point.y(), y_guides, threshold)
    return QPointF(x, y), x_guide, y_guide


def snap_shape_end(
    tool: AnnotationTool,
    start: QPointF,
    end: QPointF,
    x_guides: Sequence[float],
    y_guides: Sequence[float],
    *,
    threshold: float = ANNOTATION_SNAP_THRESHOLD,
    shift: bool = False,
) -> tuple[QPointF, float | None, float | None]:
    """Snap a draft shape's free end after Shift constraints have been applied."""
    if shift and tool in _BOX_SHIFT_TOOLS:
        return QPointF(end), None, None
    snap_x = True
    snap_y = True
    if shift:
        snap_x, snap_y = _axis_snap_flags(start, end)
        if not snap_x and not snap_y:
            return QPointF(end), None, None
    return snap_point(end, x_guides, y_guides, threshold=threshold, snap_x=snap_x, snap_y=snap_y)


def _axis_snap_flags(fixed: QPointF, moving: QPointF) -> tuple[bool, bool]:
    """Return `(snap_x, snap_y)` for a Shift-constrained line (skip 45°)."""
    if abs(moving.y() - fixed.y()) <= _NEAR_ZERO:
        return True, False
    if abs(moving.x() - fixed.x()) <= _NEAR_ZERO:
        return False, True
    return False, False


def _best_snap_delta(
    values: Sequence[float],
    targets: Sequence[float],
    threshold: float,
) -> tuple[float, float | None]:
    best_delta = 0.0
    best_dist = threshold + 1.0
    best_target: float | None = None
    for value in values:
        for target in targets:
            delta = target - value
            dist = abs(delta)
            if dist < best_dist:
                best_dist = dist
                best_delta = delta
                best_target = target
    if best_dist <= threshold:
        return best_delta, best_target
    return 0.0, None


def _candidate_axes(annotation: Annotation, points: list[QPointF]) -> tuple[list[float], list[float]]:
    xs = [p.x() for p in points]
    ys = [p.y() for p in points]
    if annotation.tool in _LINE_TOOLS:
        return xs, ys
    frame = annotation_bounds(
        Annotation(tool=annotation.tool, points=points, style=annotation.style, text=annotation.text)
    )
    if not frame.isNull() and frame.isValid():
        xs.extend((frame.left(), frame.right(), frame.center().x()))
        ys.extend((frame.top(), frame.bottom(), frame.center().y()))
    return xs, ys


def _enforce_min_size(rect: QRectF, handle: AnnotationHandle) -> QRectF:
    result = QRectF(rect)
    if result.width() < _MIN_BOX:
        if "w" in handle:
            result.setLeft(result.right() - _MIN_BOX)
        else:
            result.setWidth(_MIN_BOX)
    if result.height() < _MIN_BOX:
        if "n" in handle:
            result.setTop(result.bottom() - _MIN_BOX)
        else:
            result.setHeight(_MIN_BOX)
    return result


def _map_points_from_rect(points: list[QPointF], origin: QRectF, target: QRectF) -> list[QPointF]:
    ox, oy = origin.left(), origin.top()
    sx = target.width() / origin.width() if origin.width() >= _MIN_BOX else 1.0
    sy = target.height() / origin.height() if origin.height() >= _MIN_BOX else 1.0
    return [QPointF(target.left() + (p.x() - ox) * sx, target.top() + (p.y() - oy) * sy) for p in points]


def _snap_box_handles(
    annotation: Annotation,
    handle: AnnotationHandle,
    points: list[QPointF],
    x_guides: Sequence[float],
    y_guides: Sequence[float],
    *,
    threshold: float,
) -> AnnotationSnapResult:
    origin = annotation_bounds(
        Annotation(tool=annotation.tool, points=points, style=annotation.style, text=annotation.text)
    )
    if origin.isNull() or origin.isEmpty():
        return AnnotationSnapResult([QPointF(p) for p in points])
    left, top, right, bottom = origin.left(), origin.top(), origin.right(), origin.bottom()
    x_guide: float | None = None
    y_guide: float | None = None
    if "w" in handle:
        left, x_guide = _snap_value(left, x_guides, threshold)
    elif "e" in handle:
        right, x_guide = _snap_value(right, x_guides, threshold)
    if "n" in handle:
        top, y_guide = _snap_value(top, y_guides, threshold)
    elif "s" in handle:
        bottom, y_guide = _snap_value(bottom, y_guides, threshold)
    snapped = _enforce_min_size(QRectF(QPointF(left, top), QPointF(right, bottom)).normalized(), handle)
    if annotation.tool in {AnnotationTool.ELLIPSE, AnnotationTool.RECTANGLE}:
        return AnnotationSnapResult([snapped.topLeft(), snapped.bottomRight()], x_guide, y_guide)
    return AnnotationSnapResult(_map_points_from_rect(points, origin, snapped), x_guide, y_guide)


def _snap_line_endpoint(
    handle: AnnotationHandle,
    points: list[QPointF],
    x_guides: Sequence[float],
    y_guides: Sequence[float],
    *,
    threshold: float,
    shift: bool,
) -> AnnotationSnapResult:
    index = 0 if handle == "start" else len(points) - 1
    fixed = points[-1] if handle == "start" else points[0]
    moving = points[index]
    snap_x = True
    snap_y = True
    if shift:
        snap_x, snap_y = _axis_snap_flags(fixed, moving)
        if not snap_x and not snap_y:
            return AnnotationSnapResult([QPointF(p) for p in points])
    snapped, x_guide, y_guide = snap_point(
        moving,
        x_guides,
        y_guides,
        threshold=threshold,
        snap_x=snap_x,
        snap_y=snap_y,
    )
    result = [QPointF(p) for p in points]
    result[index] = snapped
    return AnnotationSnapResult(result, x_guide, y_guide)


def _snap_translate(
    annotation: Annotation,
    points: list[QPointF],
    x_guides: Sequence[float],
    y_guides: Sequence[float],
    *,
    threshold: float,
) -> AnnotationSnapResult:
    xs, ys = _candidate_axes(annotation, points)
    dx, x_guide = _best_snap_delta(xs, x_guides, threshold)
    dy, y_guide = _best_snap_delta(ys, y_guides, threshold)
    return AnnotationSnapResult([QPointF(p.x() + dx, p.y() + dy) for p in points], x_guide, y_guide)


def _snap_value(value: float, targets: Sequence[float], threshold: float) -> tuple[float, float | None]:
    best = value
    best_dist = threshold + 1.0
    for target in targets:
        dist = abs(value - target)
        if dist < best_dist:
            best_dist = dist
            best = target
    if best_dist <= threshold:
        return best, best
    return value, None
