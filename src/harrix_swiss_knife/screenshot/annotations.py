"""Screenshot annotation model: tools, strokes, undo, and rasterization."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPainterPath, QPen, QPolygonF

if TYPE_CHECKING:
    from collections.abc import Sequence

_MAX_UNDO = 40
_ARROW_HEAD_LEN = 18.0
_ARROW_HEAD_ANGLE = math.radians(24)
_MIN_CROP_SIZE = 2
_MIN_SHAPE_POINTS = 2
_MIN_DRAG_MANHATTAN = 3
_MIN_POLYGON_VERTICES = 3
_LENGTH_EPS = 1e-6


@dataclass(slots=True)
class Annotation:
    """One drawable mark in image coordinates."""

    tool: AnnotationTool
    points: list[QPointF]
    style: AnnotationStyle
    text: str = ""


class AnnotationDocument:
    """Editable screenshot with a list of annotations and undo history."""

    def __init__(self, image: QImage) -> None:
        """Start from a copy of `image` with an empty annotation list."""
        self._base = image.copy()
        self._annotations: list[Annotation] = []
        self._history: list[_HistoryEntry] = []
        self._draft: Annotation | None = None

    @property
    def annotations(self) -> list[Annotation]:
        """Committed annotations (image coordinates)."""
        return self._annotations

    def append_draft_point(self, point: QPointF) -> None:
        """Add a freehand point to the draft."""
        if self._draft is None:
            return
        self._draft.points.append(QPointF(point))

    def apply_crop(self, rect: QRectF) -> bool:
        """Crop the composite to `rect` (image coords) and clear annotations."""
        bounds = QRectF(self._base.rect()).intersected(rect.normalized())
        if bounds.width() < _MIN_CROP_SIZE or bounds.height() < _MIN_CROP_SIZE:
            return False
        composite = self.render()
        cropped = composite.copy(bounds.toRect())
        if cropped.isNull():
            return False
        self._push_history()
        self._base = cropped
        self._annotations = []
        self._draft = None
        return True

    @property
    def base_image(self) -> QImage:
        """Underlying image without the current draft."""
        return self._base

    def begin_draft(self, annotation: Annotation) -> None:
        """Start a new in-progress annotation."""
        self._draft = annotation

    @property
    def can_undo(self) -> bool:
        """Whether `undo` can restore a previous state."""
        return bool(self._history)

    def cancel_draft(self) -> None:
        """Discard the in-progress annotation."""
        self._draft = None

    def commit_draft(self) -> bool:
        """Commit the draft if it is drawable; return whether anything was added."""
        draft = self._draft
        self._draft = None
        if draft is None or not _is_meaningful(draft):
            return False
        self._push_history()
        self._annotations.append(draft)
        return True

    @property
    def draft(self) -> Annotation | None:
        """In-progress annotation while the mouse is dragged."""
        return self._draft

    def render(self, *, include_draft: bool = True) -> QImage:
        """Return base image with committed annotations painted.

        When `include_draft` is `True`, also paint the in-progress annotation.

        """
        result = self._base.copy()
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        for item in self._annotations:
            paint_annotation(painter, item)
        if include_draft and self._draft is not None:
            paint_annotation(painter, self._draft)
        painter.end()
        return result

    def set_draft_text(self, text: str) -> None:
        """Set text on the current draft (for the text tool)."""
        if self._draft is not None:
            self._draft.text = text

    def undo(self) -> bool:
        """Restore the previous document state."""
        if not self._history:
            return False
        entry = self._history.pop()
        self._base = entry.base
        self._annotations = entry.annotations
        self._draft = None
        return True

    def update_draft_points(self, points: Sequence[QPointF]) -> None:
        """Replace draft points (image coordinates)."""
        if self._draft is None:
            return
        self._draft.points = [QPointF(p) for p in points]

    def _push_history(self) -> None:
        self._history.append(
            _HistoryEntry(
                base=self._base.copy(),
                annotations=[_clone_annotation(item) for item in self._annotations],
            )
        )
        if len(self._history) > _MAX_UNDO:
            del self._history[0]


@dataclass(slots=True)
class AnnotationStyle:
    """Stroke style shared by shape tools."""

    color: QColor = field(default_factory=lambda: QColor("#de2b26"))
    width: float = 3.0


class AnnotationTool(Enum):
    """Active drawing tool in the screenshot preview."""

    NONE = "none"
    ARROW = "arrow"
    RECTANGLE = "rectangle"
    ELLIPSE = "ellipse"
    LINE = "line"
    PEN = "pen"
    TEXT = "text"
    CROP = "crop"


@dataclass
class _HistoryEntry:
    base: QImage
    annotations: list[Annotation]


def paint_annotation(painter: QPainter, annotation: Annotation) -> None:
    """Draw `annotation` onto `painter` in image coordinates."""
    points = annotation.points
    if not points:
        return
    pen = QPen(annotation.style.color)
    pen.setWidthF(max(1.0, annotation.style.width))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    tool = annotation.tool
    if tool == AnnotationTool.PEN:
        if len(points) == 1:
            painter.drawPoint(points[0])
        else:
            painter.drawPolyline(QPolygonF(points))
        return
    if tool == AnnotationTool.TEXT:
        font = QFont()
        font.setPointSizeF(max(10.0, annotation.style.width * 4))
        painter.setFont(font)
        painter.drawText(points[0], annotation.text or "…")
        return
    if len(points) < _MIN_SHAPE_POINTS:
        return
    start, end = points[0], points[-1]
    if tool == AnnotationTool.LINE:
        painter.drawLine(start, end)
        return
    if tool == AnnotationTool.ARROW:
        _draw_filled_arrow(painter, start, end, annotation.style.color, annotation.style.width)
        return
    rect = QRectF(start, end).normalized()
    if tool == AnnotationTool.RECTANGLE:
        painter.drawRect(rect)
        return
    if tool == AnnotationTool.ELLIPSE:
        painter.drawEllipse(rect)
        return
    if tool == AnnotationTool.CROP:
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRect(rect)


def _clone_annotation(item: Annotation) -> Annotation:
    return Annotation(
        tool=item.tool,
        points=[QPointF(p) for p in item.points],
        text=item.text,
        style=AnnotationStyle(color=QColor(item.style.color), width=item.style.width),
    )


def _draw_filled_arrow(
    painter: QPainter,
    start: QPointF,
    end: QPointF,
    color: QColor,
    width: float,
) -> None:
    """Draw a thin round-capped shaft and a solid isosceles head.

    The tail is a straight line with a slightly rounded far end. The head is an
    isosceles triangle whose back edge is perpendicular to the shaft; vertices
    are slightly rounded so the corners are not sharp.

    """
    dx = end.x() - start.x()
    dy = end.y() - start.y()
    length = math.hypot(dx, dy)
    if length < 1:
        return
    stroke = max(1.0, width)
    head = max(_ARROW_HEAD_LEN, stroke * 5.5)
    head = min(head, length * 0.5)
    ux, uy = dx / length, dy / length
    base = QPointF(end.x() - ux * head, end.y() - uy * head)
    half_base = head * math.tan(_ARROW_HEAD_ANGLE)
    px, py = -uy, ux
    left = QPointF(base.x() + px * half_base, base.y() + py * half_base)
    right = QPointF(base.x() - px * half_base, base.y() - py * half_base)
    # Hide the round cap inside the head so the shaft meets the flat back edge.
    shaft_end = QPointF(base.x() + ux * stroke * 0.5, base.y() + uy * stroke * 0.5)
    pen = QPen(color)
    pen.setWidthF(stroke)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawLine(start, shaft_end)
    corner = min(max(1.2, stroke * 0.75), head * 0.16, half_base * 0.28)
    painter.fillPath(_rounded_polygon_path([end, left, right], corner), color)


def _is_meaningful(annotation: Annotation) -> bool:
    if annotation.tool == AnnotationTool.TEXT:
        return bool(annotation.text.strip()) and bool(annotation.points)
    if annotation.tool == AnnotationTool.PEN:
        return len(annotation.points) >= 1
    if len(annotation.points) < _MIN_SHAPE_POINTS:
        return False
    start, end = annotation.points[0], annotation.points[-1]
    return (end - start).manhattanLength() >= _MIN_DRAG_MANHATTAN


def _rounded_polygon_path(vertices: list[QPointF], radius: float) -> QPainterPath:
    """Build a closed polygon path with quadratic rounding at each vertex."""
    path = QPainterPath()
    count = len(vertices)
    if count < _MIN_POLYGON_VERTICES:
        return path
    corners: list[tuple[QPointF, QPointF, QPointF]] = []
    for index, curr in enumerate(vertices):
        prev_pt = vertices[index - 1]
        next_pt = vertices[(index + 1) % count]
        to_prev = QPointF(prev_pt.x() - curr.x(), prev_pt.y() - curr.y())
        to_next = QPointF(next_pt.x() - curr.x(), next_pt.y() - curr.y())
        dist_prev = math.hypot(to_prev.x(), to_prev.y())
        dist_next = math.hypot(to_next.x(), to_next.y())
        if dist_prev < _LENGTH_EPS or dist_next < _LENGTH_EPS:
            corners.append((curr, curr, curr))
            continue
        corner = min(max(0.0, radius), dist_prev * 0.45, dist_next * 0.45)
        p1 = QPointF(curr.x() + to_prev.x() / dist_prev * corner, curr.y() + to_prev.y() / dist_prev * corner)
        p2 = QPointF(curr.x() + to_next.x() / dist_next * corner, curr.y() + to_next.y() / dist_next * corner)
        corners.append((p1, curr, p2))
    path.moveTo(corners[-1][2])
    for p1, vertex, p2 in corners:
        path.lineTo(p1)
        path.quadTo(vertex, p2)
    path.closeSubpath()
    return path
