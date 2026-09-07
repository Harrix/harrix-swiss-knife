"""Screenshot annotation model: tools, strokes, undo, and rasterization."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFontMetricsF, QImage, QPainter, QPainterPath, QPen, QPolygonF

if TYPE_CHECKING:
    from collections.abc import Sequence

_MAX_UNDO = 40
# ShareX Classic proportions: shaft stroke, head half-width = 2x stroke, concave back.
_ARROW_HEAD_WIDTH_MULT = 2.0
_ARROW_HEAD_LENGTH_RATIO = 3.0
_ARROW_HEAD_BACK_CURVE_CONTROL_RATIO = 2.0
_ARROW_HEAD_MAX_LENGTH_FRAC = 0.45
_MIN_CROP_SIZE = 2
_MIN_SHAPE_POINTS = 2
_MIN_DRAG_MANHATTAN = 3
_SHIFT_ANGLE_STEP = math.pi / 4


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

    def delete_at(self, index: int) -> bool:
        """Remove the annotation at `index` and record undo. Return whether it was deleted."""
        if index < 0 or index >= len(self._annotations):
            return False
        self._push_history()
        del self._annotations[index]
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

    def save_undo_checkpoint(self) -> None:
        """Snapshot the current document so the next mutation can be undone."""
        self._push_history()

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

    def update_annotation_points(self, index: int, points: Sequence[QPointF]) -> None:
        """Replace points of a committed annotation (image coordinates)."""
        if index < 0 or index >= len(self._annotations):
            return
        self._annotations[index].points = [QPointF(p) for p in points]

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
    """Stroke / text style shared by annotation tools."""

    color: QColor = field(default_factory=lambda: QColor("#de2b26"))
    width: float = 3.0
    font_family: str = ""
    font_size: float = 26.0
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikeout: bool = False
    align: str = "left"
    background_fill: bool = False


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
    EYEDROPPER = "eyedropper"


@dataclass
class _HistoryEntry:
    base: QImage
    annotations: list[Annotation]


def constrain_shape_end(tool: AnnotationTool, start: QPointF, end: QPointF, *, shift: bool) -> QPointF:
    """Return the free or Shift-constrained end point for `tool`.

    Shift snaps arrows and lines to 0°/45°/90° steps and makes rectangles
    and ellipses square or circular, keeping the start corner fixed.

    """
    if not shift:
        return QPointF(end)
    if tool in _LINE_SHIFT_TOOLS:
        return _snap_end_to_45_degrees(start, end)
    if tool in _SQUARE_SHIFT_TOOLS:
        return _snap_end_to_square(start, end)
    return QPointF(end)


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
        _paint_text_annotation(painter, annotation)
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


def _arrow_head_geometry(
    start: QPointF,
    end: QPointF,
    stroke: float,
) -> tuple[QPointF, QPointF, QPointF, QPointF] | None:
    """Return tip, left wing, right wing, and concave back-curve control.

    Proportions match ShareX Classic (half-width 2x stroke, length 3x half-width).
    The shaft ends at the control point so thickness stays uniform and the round
    start cap stays visible.

    """
    dx = end.x() - start.x()
    dy = end.y() - start.y()
    length = math.hypot(dx, dy)
    if length < 1:
        return None
    half_width = max(1.0, stroke) * _ARROW_HEAD_WIDTH_MULT
    head_length = half_width * _ARROW_HEAD_LENGTH_RATIO
    head_length = min(head_length, length * _ARROW_HEAD_MAX_LENGTH_FRAC)
    back_control = min(half_width * _ARROW_HEAD_BACK_CURVE_CONTROL_RATIO, head_length * 0.85)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    base_x = end.x() - ux * head_length
    base_y = end.y() - uy * head_length
    left = QPointF(base_x + px * half_width, base_y + py * half_width)
    right = QPointF(base_x - px * half_width, base_y - py * half_width)
    control = QPointF(end.x() - ux * back_control, end.y() - uy * back_control)
    return end, left, right, control


def _arrow_head_path(start: QPointF, end: QPointF, stroke: float) -> QPainterPath | None:
    """Build the classic ShareX arrowhead: tip, wings, concave quadratic back."""
    geometry = _arrow_head_geometry(start, end, stroke)
    if geometry is None:
        return None
    tip, left, right, control = geometry
    path = QPainterPath()
    path.moveTo(tip)
    path.lineTo(left)
    path.quadTo(control, right)
    path.closeSubpath()
    return path


def _clone_annotation(item: Annotation) -> Annotation:
    style = item.style
    return Annotation(
        tool=item.tool,
        points=[QPointF(p) for p in item.points],
        text=item.text,
        style=AnnotationStyle(
            color=QColor(style.color),
            width=style.width,
            font_family=style.font_family,
            font_size=style.font_size,
            bold=style.bold,
            italic=style.italic,
            underline=style.underline,
            strikeout=style.strikeout,
            align=style.align,
            background_fill=style.background_fill,
        ),
    )


def _paint_text_annotation(painter: QPainter, annotation: Annotation) -> None:
    from harrix_swiss_knife.screenshot.text_style import annotation_qfont  # noqa: PLC0415

    rect = text_annotation_rect(annotation)
    if rect.isNull() or rect.isEmpty():
        return
    if annotation.style.background_fill:
        painter.fillRect(rect, QColor(255, 255, 255, 235))
    font = annotation_qfont(annotation.style)
    painter.setFont(font)
    painter.setPen(QPen(annotation.style.color))
    align = annotation.style.align
    flags = int(Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap)
    if align == "center":
        flags |= int(Qt.AlignmentFlag.AlignHCenter)
    elif align == "right":
        flags |= int(Qt.AlignmentFlag.AlignRight)
    else:
        flags |= int(Qt.AlignmentFlag.AlignLeft)
    painter.drawText(rect, flags, annotation.text or "")


def text_annotation_rect(annotation: Annotation) -> QRectF:
    """Return the axis-aligned text box for `annotation` in image coordinates."""
    points = annotation.points
    if not points:
        return QRectF()
    if len(points) >= _MIN_SHAPE_POINTS:
        return QRectF(points[0], points[-1]).normalized()
    # Legacy single-point text: size from font metrics.
    from harrix_swiss_knife.screenshot.text_style import annotation_qfont  # noqa: PLC0415

    origin = points[0]
    metrics = QFontMetricsF(annotation_qfont(annotation.style))
    text = annotation.text or "…"
    width = max(metrics.horizontalAdvance(text), 8.0)
    height = max(metrics.height(), 10.0)
    return QRectF(origin.x(), origin.y() - metrics.ascent(), width, height)


def _draw_filled_arrow(
    painter: QPainter,
    start: QPointF,
    end: QPointF,
    color: QColor,
    width: float,
) -> None:
    """Draw a round-capped shaft and a ShareX-classic filled head.

    The shaft keeps constant thickness from a rounded tail to the concave notch.
    The head is filled and stroked so it reads as a solid triangle with the
    classic inward rear curve.

    """
    stroke = max(1.0, width)
    geometry = _arrow_head_geometry(start, end, stroke)
    if geometry is None:
        return
    tip, left, right, control = geometry
    head = QPainterPath()
    head.moveTo(tip)
    head.lineTo(left)
    head.quadTo(control, right)
    head.closeSubpath()

    pen = QPen(color)
    pen.setWidthF(stroke)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawLine(start, control)
    painter.setBrush(color)
    painter.drawPath(head)


def _is_meaningful(annotation: Annotation) -> bool:
    if annotation.tool == AnnotationTool.TEXT:
        return bool(annotation.text.strip()) and bool(annotation.points)
    if annotation.tool == AnnotationTool.PEN:
        return len(annotation.points) >= 1
    if len(annotation.points) < _MIN_SHAPE_POINTS:
        return False
    start, end = annotation.points[0], annotation.points[-1]
    return (end - start).manhattanLength() >= _MIN_DRAG_MANHATTAN


def _snap_end_to_45_degrees(start: QPointF, end: QPointF) -> QPointF:
    """Snap `end` so the segment from `start` lies on a 45° multiple."""
    dx = end.x() - start.x()
    dy = end.y() - start.y()
    length = math.hypot(dx, dy)
    if length < 1:
        return QPointF(end)
    angle = math.atan2(dy, dx)
    snapped = round(angle / _SHIFT_ANGLE_STEP) * _SHIFT_ANGLE_STEP
    return QPointF(start.x() + math.cos(snapped) * length, start.y() + math.sin(snapped) * length)


def _snap_end_to_square(start: QPointF, end: QPointF) -> QPointF:
    """Keep the start corner and make width and height equal.

    Uses the shorter side so the shape stays inside the dragged rectangle.

    """
    dx = end.x() - start.x()
    dy = end.y() - start.y()
    size = min(abs(dx), abs(dy))
    if size < 1:
        return QPointF(end)
    sx = math.copysign(size, dx) if dx != 0 else 0.0
    sy = math.copysign(size, dy) if dy != 0 else 0.0
    return QPointF(start.x() + sx, start.y() + sy)


_LINE_SHIFT_TOOLS = frozenset({AnnotationTool.ARROW, AnnotationTool.LINE})
_SQUARE_SHIFT_TOOLS = frozenset({AnnotationTool.ELLIPSE, AnnotationTool.RECTANGLE})
