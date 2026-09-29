"""Screenshot annotation model: tools, strokes, undo, and rasterization."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRect, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import QGraphicsBlurEffect, QGraphicsPixmapItem, QGraphicsScene

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
_HIGHLIGHT_ALPHA = 96
# ShareX blur tool: a rectangle that gaussian-blurs the pixels underneath.
_BLUR_RADIUS = 40.0
_BLUR_PAD_FACTOR = 3
# ShareX pixelate tool: averaged blocks over the pixels underneath. Larger than ShareX's 10.
_PIXELATE_BLOCK = 20
# ShareX step tool: a small filled circle with the next number, stamped from the click.
_STEP_DEFAULT_RADIUS = 18.0
_STEP_MIN_RADIUS = 10.0
_STEP_FONT_RATIO = 0.58
_STEP_LABEL_LUMINANCE = 160


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
        self._redo: list[_HistoryEntry] = []
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

    def apply_resize(self, width: int, height: int) -> bool:
        """Scale the composite to the given pixel size and clear annotations.

        Returns `False` when the target is empty, larger than the image, or unchanged.

        """
        target_w = int(width)
        target_h = int(height)
        if target_w < 1 or target_h < 1:
            return False
        if target_w > self._base.width() or target_h > self._base.height():
            return False
        if target_w == self._base.width() and target_h == self._base.height():
            return False
        composite = self.render(include_draft=False)
        scaled = composite.scaled(
            target_w,
            target_h,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        if scaled.isNull():
            return False
        self._push_history()
        self._base = scaled
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

    def bring_forward(self, indices: Sequence[int]) -> list[int] | None:
        """Move selected annotations one step toward the front. Return new indices."""
        return self._reorder_step(indices, direction=1)

    def bring_to_front(self, indices: Sequence[int]) -> list[int] | None:
        """Move selected annotations to the top of the stack. Return new indices."""
        return self._move_selected_block(indices, to_front=True)

    @property
    def can_redo(self) -> bool:
        """Whether `redo` can restore a later state."""
        return bool(self._redo)

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

    def delete_all(self) -> bool:
        """Remove every annotation in one undo step."""
        if not self._annotations:
            return False
        self._push_history()
        self._annotations = []
        self._draft = None
        return True

    def delete_at(self, index: int) -> bool:
        """Remove the annotation at `index` and record undo. Return whether it was deleted."""
        if index < 0 or index >= len(self._annotations):
            return False
        self._push_history()
        del self._annotations[index]
        return True

    def delete_indices(self, indices: Sequence[int]) -> bool:
        """Remove annotations at `indices` in one undo step. Return whether any were deleted."""
        unique = sorted({index for index in indices if 0 <= index < len(self._annotations)}, reverse=True)
        if not unique:
            return False
        self._push_history()
        for index in unique:
            del self._annotations[index]
        return True

    @property
    def draft(self) -> Annotation | None:
        """In-progress annotation while the mouse is dragged."""
        return self._draft

    def flatten(self) -> bool:
        """Bake annotations into the base image and clear the annotation list."""
        if not self._annotations:
            return False
        self._push_history()
        self._base = composite_annotations(self._base, self._annotations)
        self._annotations = []
        self._draft = None
        return True

    def insert_annotations(self, items: Sequence[Annotation]) -> list[int]:
        """Append clones of `items` and return their new indices."""
        if not items:
            return []
        self._push_history()
        start = len(self._annotations)
        for item in items:
            self._annotations.append(_clone_annotation(item))
        return list(range(start, len(self._annotations)))

    def redo(self) -> bool:
        """Restore the next document state after an undo."""
        if not self._redo:
            return False
        self._history.append(self._snapshot())
        entry = self._redo.pop()
        self._restore(entry)
        return True

    def render(self, *, include_draft: bool = True) -> QImage:
        """Return base image with committed annotations painted.

        When `include_draft` is `True`, also paint the in-progress annotation.

        """
        items = list(self._annotations)
        if include_draft and self._draft is not None:
            items.append(self._draft)
        return composite_annotations(self._base, items)

    def save_undo_checkpoint(self) -> None:
        """Snapshot the current document so the next mutation can be undone."""
        self._push_history()

    def send_backward(self, indices: Sequence[int]) -> list[int] | None:
        """Move selected annotations one step toward the back. Return new indices."""
        return self._reorder_step(indices, direction=-1)

    def send_to_back(self, indices: Sequence[int]) -> list[int] | None:
        """Move selected annotations to the bottom of the stack. Return new indices."""
        return self._move_selected_block(indices, to_front=False)

    def set_draft_text(self, text: str) -> None:
        """Set text on the current draft (for the text tool)."""
        if self._draft is not None:
            self._draft.text = text

    def undo(self) -> bool:
        """Restore the previous document state."""
        if not self._history:
            return False
        self._redo.append(self._snapshot())
        entry = self._history.pop()
        self._restore(entry)
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

    def _move_selected_block(self, indices: Sequence[int], *, to_front: bool) -> list[int] | None:
        selected = sorted({index for index in indices if 0 <= index < len(self._annotations)})
        if not selected:
            return None
        if to_front and selected == list(range(len(self._annotations) - len(selected), len(self._annotations))):
            return None
        if not to_front and selected == list(range(len(selected))):
            return None
        self._push_history()
        items = [self._annotations[index] for index in selected]
        for index in reversed(selected):
            del self._annotations[index]
        if to_front:
            self._annotations.extend(items)
            return list(range(len(self._annotations) - len(items), len(self._annotations)))
        self._annotations[0:0] = items
        return list(range(len(items)))

    def _push_history(self) -> None:
        self._history.append(self._snapshot())
        self._redo.clear()
        if len(self._history) > _MAX_UNDO:
            del self._history[0]

    def _reorder_step(self, indices: Sequence[int], *, direction: int) -> list[int] | None:
        selected = {index for index in indices if 0 <= index < len(self._annotations)}
        if not selected:
            return None
        order = sorted(selected, reverse=direction > 0)
        moved = False
        for index in order:
            neighbor = index + direction
            if neighbor < 0 or neighbor >= len(self._annotations) or neighbor in selected:
                continue
            if not moved:
                self._push_history()
                moved = True
            self._annotations[index], self._annotations[neighbor] = (
                self._annotations[neighbor],
                self._annotations[index],
            )
            selected.remove(index)
            selected.add(neighbor)
        return sorted(selected) if moved else None

    def _restore(self, entry: _HistoryEntry) -> None:
        self._base = entry.base
        self._annotations = entry.annotations
        self._draft = None

    def _snapshot(self) -> _HistoryEntry:
        return _HistoryEntry(
            base=self._base.copy(),
            annotations=[_clone_annotation(item) for item in self._annotations],
        )


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
    STEP = "step"
    LINE = "line"
    PEN = "pen"
    HIGHLIGHT = "highlight"
    BLUR = "blur"
    PIXELATE = "pixelate"
    SMART_ERASER = "smart_eraser"
    TEXT = "text"
    CROP = "crop"
    EYEDROPPER = "eyedropper"


@dataclass
class _HistoryEntry:
    base: QImage
    annotations: list[Annotation]


def clone_annotation(item: Annotation) -> Annotation:
    """Return a deep copy of `item`."""
    return _clone_annotation(item)


def composite_annotations(base: QImage, annotations: Sequence[Annotation]) -> QImage:
    """Paint `annotations` onto a copy of `base`, applying blur and pixelate in order."""
    result = base.copy()
    if result.isNull() or not annotations:
        return result
    painter: QPainter | None = None
    for item in annotations:
        if item.tool in RASTER_EFFECT_TOOLS:
            if painter is not None and painter.isActive():
                painter.end()
                painter = None
            if item.tool == AnnotationTool.BLUR:
                _apply_blur(result, item)
            else:
                _apply_pixelate(result, item)
            continue
        if painter is None or not painter.isActive():
            painter = QPainter(result)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        paint_annotation(painter, item)
    if painter is not None and painter.isActive():
        painter.end()
    return result


def constrain_shape_end(tool: AnnotationTool, start: QPointF, end: QPointF, *, shift: bool) -> QPointF:
    """Return the free or Shift-constrained end point for `tool`.

    Shift snaps arrows and lines to 0°/45°/90° steps and makes rectangles
    and ellipses square or circular, keeping the start corner fixed.

    """
    if tool == AnnotationTool.STEP:
        return _snap_end_to_square(start, end)
    if not shift:
        return QPointF(end)
    if tool in _LINE_SHIFT_TOOLS:
        return _snap_end_to_45_degrees(start, end)
    if tool in _SQUARE_SHIFT_TOOLS:
        return _snap_end_to_square(start, end)
    return QPointF(end)


def next_step_number(annotations: Sequence[Annotation]) -> int:
    """Return the next ShareX-style step number after the highest one already placed."""
    highest = 0
    for item in annotations:
        if item.tool != AnnotationTool.STEP:
            continue
        try:
            number = int(item.text)
        except ValueError:
            continue
        highest = max(highest, number)
    return highest + 1


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
    if tool == AnnotationTool.STEP:
        _paint_step(painter, annotation, rect)
        return
    if tool == AnnotationTool.HIGHLIGHT:
        fill = QColor(annotation.style.color)
        fill.setAlpha(_HIGHLIGHT_ALPHA)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill)
        painter.drawRect(rect)
        return
    if tool in RASTER_EFFECT_TOOLS:
        return
    if tool == AnnotationTool.SMART_ERASER:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=False)
        painter.fillRect(rect.toAlignedRect(), QColor(annotation.style.color))
        painter.restore()
        return
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


def sample_composited_color(base: QImage, annotations: Sequence[Annotation], point: QPointF) -> QColor:
    """Return the pixel at `point` after painting `annotations` onto `base`."""
    image = composite_annotations(base, annotations)
    if image.isNull() or image.width() <= 0 or image.height() <= 0:
        return QColor(255, 255, 255)
    x = min(max(0, int(point.x())), image.width() - 1)
    y = min(max(0, int(point.y())), image.height() - 1)
    return QColor(image.pixelColor(x, y))


def step_circle_points(center: QPointF, edge: QPointF, *, clicked: bool = False) -> list[QPointF]:
    """Return the bounding square of a step circle centered on `center`.

    A click uses the default radius. A drag uses the distance to `edge`, and never
    shrinks below the minimum so the number still fits.

    """
    if clicked:
        radius = _STEP_DEFAULT_RADIUS
    else:
        radius = math.hypot(edge.x() - center.x(), edge.y() - center.y())
        radius = max(radius, _STEP_MIN_RADIUS)
    return [
        QPointF(center.x() - radius, center.y() - radius),
        QPointF(center.x() + radius, center.y() + radius),
    ]


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


def _apply_blur(image: QImage, annotation: Annotation) -> None:
    """Gaussian-blur the rectangle of `annotation` in place, keeping a hard edge."""
    if len(annotation.points) < _MIN_SHAPE_POINTS or image.isNull():
        return
    rect = QRectF(annotation.points[0], annotation.points[-1]).normalized().toAlignedRect()
    rect = rect.intersected(image.rect())
    if rect.width() < _MIN_CROP_SIZE or rect.height() < _MIN_CROP_SIZE:
        return
    patch = _blurred_patch(image, rect, _BLUR_RADIUS)
    if patch.isNull():
        return
    painter = QPainter(image)
    painter.drawImage(rect.topLeft(), patch)
    painter.end()


def _apply_pixelate(image: QImage, annotation: Annotation) -> None:
    """Pixelate the rectangle of `annotation` in place, keeping a hard edge."""
    if len(annotation.points) < _MIN_SHAPE_POINTS or image.isNull():
        return
    rect = QRectF(annotation.points[0], annotation.points[-1]).normalized().toAlignedRect()
    rect = rect.intersected(image.rect())
    if rect.width() < _MIN_CROP_SIZE or rect.height() < _MIN_CROP_SIZE:
        return
    patch = _pixelate_patch(image, rect, _PIXELATE_BLOCK)
    if patch.isNull():
        return
    painter = QPainter(image)
    painter.drawImage(rect.topLeft(), patch)
    painter.end()


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


def _blurred_patch(source: QImage, rect: QRect, radius: float) -> QImage:
    """Return `rect` blurred from a padded copy so the edge stays opaque."""
    pad = max(1, math.ceil(radius * _BLUR_PAD_FACTOR))
    padded = QRect(rect).adjusted(-pad, -pad, pad, pad).intersected(source.rect())
    if padded.isEmpty():
        return QImage()
    patch = source.copy(padded).convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
    blurred = _gaussian_blur(patch, radius)
    inner = QRect(rect.x() - padded.x(), rect.y() - padded.y(), rect.width(), rect.height())
    inner = inner.intersected(blurred.rect())
    if inner.isEmpty():
        return QImage()
    return blurred.copy(inner)


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


def _gaussian_blur(image: QImage, radius: float) -> QImage:
    """Blur `image` with Qt's gaussian effect and crop back to the original size."""
    item = QGraphicsPixmapItem(QPixmap.fromImage(image))
    effect = QGraphicsBlurEffect()
    effect.setBlurRadius(radius)
    effect.setBlurHints(QGraphicsBlurEffect.BlurHint.QualityHint)
    item.setGraphicsEffect(effect)
    scene = QGraphicsScene()
    scene.addItem(item)
    result = QImage(image.size(), QImage.Format.Format_ARGB32_Premultiplied)
    result.fill(Qt.GlobalColor.transparent)
    painter = QPainter(result)
    scene.render(painter, QRectF(result.rect()), QRectF(0, 0, image.width(), image.height()))
    painter.end()
    return result


def _is_meaningful(annotation: Annotation) -> bool:
    if annotation.tool == AnnotationTool.TEXT:
        return bool(annotation.text.strip()) and bool(annotation.points)
    if annotation.tool == AnnotationTool.PEN:
        return len(annotation.points) >= 1
    if len(annotation.points) < _MIN_SHAPE_POINTS:
        return False
    start, end = annotation.points[0], annotation.points[-1]
    return (end - start).manhattanLength() >= _MIN_DRAG_MANHATTAN


def _paint_step(painter: QPainter, annotation: Annotation, rect: QRectF) -> None:
    """Fill a circle and center its step number in a contrasting color."""
    if rect.width() < 1 or rect.height() < 1:
        return
    fill = QColor(annotation.style.color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(fill)
    painter.drawEllipse(rect)
    label = annotation.text.strip() or "1"
    font = QFont()
    font.setBold(True)
    font.setPixelSize(_step_font_px(min(rect.width(), rect.height()), len(label)))
    painter.setFont(font)
    painter.setPen(QPen(_step_label_color(fill)))
    painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), label)


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


def _pixelate_patch(source: QImage, rect: QRect, block: int) -> QImage:
    """Return `rect` as averaged blocks of `block` pixels, clipped to that rectangle."""
    patch = source.copy(rect)
    if patch.isNull() or block < _MIN_CROP_SIZE:
        return patch
    blocks_x = max(1, math.ceil(patch.width() / block))
    blocks_y = max(1, math.ceil(patch.height() / block))
    small = patch.scaled(
        blocks_x,
        blocks_y,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    return small.scaled(
        patch.width(),
        patch.height(),
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.FastTransformation,
    )


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


def _step_font_px(side: float, length: int) -> int:
    digits = max(1, length)
    return max(8, int(side * _STEP_FONT_RATIO / digits))


def _step_label_color(fill: QColor) -> QColor:
    luminance = 0.299 * fill.red() + 0.587 * fill.green() + 0.114 * fill.blue()
    if luminance >= _STEP_LABEL_LUMINANCE:
        return QColor(0, 0, 0)
    return QColor(255, 255, 255)


RASTER_EFFECT_TOOLS = frozenset({AnnotationTool.BLUR, AnnotationTool.PIXELATE})


_LINE_SHIFT_TOOLS = frozenset({AnnotationTool.ARROW, AnnotationTool.LINE})
_SQUARE_SHIFT_TOOLS = frozenset(
    {
        AnnotationTool.BLUR,
        AnnotationTool.ELLIPSE,
        AnnotationTool.HIGHLIGHT,
        AnnotationTool.PIXELATE,
        AnnotationTool.RECTANGLE,
        AnnotationTool.SMART_ERASER,
    }
)
