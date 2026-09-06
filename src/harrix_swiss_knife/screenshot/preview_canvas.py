"""Zoomable, pannable canvas for screenshot preview with annotation tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QPointF, QRect, QRectF, QSizeF, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QPixmap, QResizeEvent, QWheelEvent
from PySide6.QtWidgets import QWidget

from harrix_swiss_knife.screenshot.annotations import (
    Annotation,
    AnnotationStyle,
    AnnotationTool,
    constrain_shape_end,
    paint_annotation,
)
from harrix_swiss_knife.screenshot.selection_edit import (
    HandleKind,
    collect_edge_guides,
    cursor_for_handle,
    hit_test_selection_handle,
    snap_all_edges,
    snap_rect_to_edges,
    transform_selection_rect,
)
from harrix_swiss_knife.screenshot.selection_paint import SELECTION_BORDER_WIDTH, paint_selection_frame

if TYPE_CHECKING:
    from PySide6.QtGui import QImage

    from harrix_swiss_knife.screenshot.annotations import AnnotationDocument

_ZOOM_STEP = 1.15
_MIN_ZOOM = 0.25
_MAX_ZOOM = 16.0
_MIN_SHAPE_POINTS = 2
_MIN_CROP = 2
_DRAG_THRESHOLD = 4
_EDGE_SNAP_THRESHOLD = 8


class ScreenshotPreviewCanvas(QWidget):
    """Show an image fitted with aspect ratio; Ctrl+wheel zooms; middle-drag pans.

    Left-drag draws with the active `AnnotationTool` when a document is attached.
    Crop mode uses the same dimmed blue selection frame as region capture.

    """

    document_changed = Signal()
    crop_mode_changed = Signal(bool)
    crop_pending_changed = Signal(bool)
    text_requested = Signal(QPointF)

    def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        """Create a canvas for `image` at fit zoom."""
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._pixmap = QPixmap.fromImage(image)
        self._zoom = 1.0
        self._offset = QPointF()
        self._pan_start: QPointF | None = None
        self._pan_origin = QPointF()
        self._document: AnnotationDocument | None = None
        self._tool = AnnotationTool.NONE
        self._style = AnnotationStyle()
        self._draw_start: QPointF | None = None
        self._draw_current: QPointF | None = None
        self._crop_pending = False
        self._crop_rect: QRect | None = None
        self._crop_origin: QPoint | None = None
        self._crop_current: QPoint | None = None
        self._crop_dragging = False
        self._crop_edit_handle: HandleKind | None = None
        self._crop_press_pos: QPoint | None = None
        self._crop_press_rect: QRect | None = None
        self._snap_x_edges: list[int] = []
        self._snap_y_edges: list[int] = []

    def cancel_crop(self) -> None:
        """Discard crop selection and leave crop mode."""
        was_crop = self._tool == AnnotationTool.CROP or self._crop_pending or self._crop_rect is not None
        if self._document is not None:
            self._document.cancel_draft()
        self._clear_crop_state()
        self._tool = AnnotationTool.NONE
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        if was_crop:
            self.crop_mode_changed.emit(False)  # noqa: FBT003
        self.crop_pending_changed.emit(False)  # noqa: FBT003

    def confirm_crop(self) -> bool:
        """Apply the pending crop rectangle. Return whether it succeeded."""
        document = self._document
        rect = self._crop_rect
        if document is None or rect is None or rect.width() < _MIN_CROP or rect.height() < _MIN_CROP:
            self.cancel_crop()
            return False
        applied = document.apply_crop(QRectF(rect))
        self._clear_crop_state()
        self._tool = AnnotationTool.NONE
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.crop_mode_changed.emit(False)  # noqa: FBT003
        self.crop_pending_changed.emit(False)  # noqa: FBT003
        if not applied:
            self.update()
            return False
        self._refresh_pixmap()
        self._rebuild_snap_edges()
        self.document_changed.emit()
        return True

    @property
    def crop_mode(self) -> bool:
        """Whether the canvas is in crop selection / edit mode."""
        return self._tool == AnnotationTool.CROP

    @property
    def crop_pending(self) -> bool:
        """Whether a crop rectangle is waiting for confirmation."""
        return self._crop_pending

    def finish_text_at(self, image_pos: QPointF, text: str) -> None:
        """Commit a text annotation at `image_pos` after the user entered `text`."""
        if self._document is None or not text.strip():
            return
        self._document.begin_draft(
            Annotation(
                tool=AnnotationTool.TEXT,
                points=[QPointF(image_pos)],
                text=text.strip(),
                style=AnnotationStyle(color=QColor(self._style.color), width=self._style.width),
            )
        )
        if self._document.commit_draft():
            self._refresh_pixmap()
            self.document_changed.emit()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Re-apply Shift constraints while a shape is being dragged."""
        if event.key() == Qt.Key.Key_Shift and not event.isAutoRepeat() and self._refresh_constrained_draft(shift=True):
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Drop Shift constraints when the key is released during a drag."""
        if (
            event.key() == Qt.Key.Key_Shift
            and not event.isAutoRepeat()
            and self._refresh_constrained_draft(shift=False)
        ):
            event.accept()
            return
        super().keyReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Pan with middle button, update crop frame, or update the draft while left-dragging."""
        if self._pan_start is not None:
            delta = event.position() - self._pan_start
            self._offset = self._pan_origin + delta
            self.update()
            event.accept()
            return

        if self._tool == AnnotationTool.CROP:
            self._crop_mouse_move(event.position())
            event.accept()
            return

        if self._draw_start is not None and self._document is not None and self._document.draft is not None:
            image_pos = self._widget_to_image(event.position())
            if image_pos is None:
                event.accept()
                return
            draft = self._document.draft
            start = self._draw_start
            if start is None:
                event.accept()
                return
            if draft.tool == AnnotationTool.PEN:
                self._document.append_draft_point(image_pos)
            else:
                self._draw_current = image_pos
                self._document.update_draft_points(
                    [
                        start,
                        constrain_shape_end(
                            draft.tool,
                            start,
                            image_pos,
                            shift=_shift_pressed(event.modifiers()),
                        ),
                    ]
                )
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start panning or begin a draft annotation / crop."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_start = event.position()
            self._pan_origin = QPointF(self._offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool == AnnotationTool.CROP:
            self._crop_mouse_press(event.position())
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool != AnnotationTool.NONE:
            image_pos = self._widget_to_image(event.position())
            if image_pos is None or self._document is None:
                event.accept()
                return
            if self._tool == AnnotationTool.TEXT:
                self.text_requested.emit(image_pos)
                event.accept()
                return
            self._draw_start = image_pos
            self._draw_current = image_pos
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            self._document.begin_draft(
                Annotation(
                    tool=self._tool,
                    points=[QPointF(image_pos), QPointF(image_pos)],
                    style=AnnotationStyle(color=QColor(self._style.color), width=self._style.width),
                )
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """End panning or commit the draft annotation / crop drag."""
        if event.button() == Qt.MouseButton.MiddleButton and self._pan_start is not None:
            self._pan_start = None
            self.set_tool(self._tool)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool == AnnotationTool.CROP:
            self._crop_mouse_release(event.position())
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._draw_start is not None:
            self._finish_draw(event.position(), shift=_shift_pressed(event.modifiers()))
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        """Draw the fitted pixmap, crop frame, and the live draft overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        image_rect = self._image_rect()
        if not self._pixmap.isNull():
            painter.drawPixmap(image_rect.toRect(), self._pixmap)

        if self._tool == AnnotationTool.CROP and not image_rect.isEmpty():
            self._paint_crop_overlay(painter, image_rect)
        elif self._document is not None and self._document.draft is not None and not image_rect.isEmpty():
            painter.save()
            painter.translate(image_rect.topLeft())
            scale_x = image_rect.width() / max(1, self._pixmap.width())
            scale_y = image_rect.height() / max(1, self._pixmap.height())
            painter.scale(scale_x, scale_y)
            paint_annotation(painter, self._document.draft)
            painter.restore()
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Repaint when the available fit area changes."""
        super().resizeEvent(event)
        self.update()

    def set_document(self, document: AnnotationDocument | None) -> None:
        """Attach an annotation document; canvas displays its rendered image."""
        self._document = document
        if document is not None:
            self._pixmap = QPixmap.fromImage(document.render())
        self._rebuild_snap_edges()
        self.update()

    def set_style(self, color: QColor | None = None, width: float | None = None) -> None:
        """Update the stroke color and/or width for new annotations."""
        if color is not None:
            self._style.color = QColor(color)
        if width is not None:
            self._style.width = max(1.0, width)

    def set_tool(self, tool: AnnotationTool) -> None:
        """Select the drawing tool (`NONE` keeps view-only left-click)."""
        previous_crop = self._tool == AnnotationTool.CROP
        if previous_crop and tool != AnnotationTool.CROP:
            self._clear_crop_state()
            self.crop_pending_changed.emit(False)  # noqa: FBT003
        self._tool = tool
        self._draw_start = None
        self._draw_current = None
        if self._document is not None and tool != AnnotationTool.CROP:
            self._document.cancel_draft()
        if tool == AnnotationTool.CROP:
            self._rebuild_snap_edges()
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.crop_mode_changed.emit(True)  # noqa: FBT003
        else:
            if previous_crop:
                self.crop_mode_changed.emit(False)  # noqa: FBT003
            if tool == AnnotationTool.NONE:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            elif tool == AnnotationTool.TEXT:
                self.setCursor(Qt.CursorShape.IBeamCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
        self._refresh_pixmap()

    @property
    def tool(self) -> AnnotationTool:
        """Active annotation tool."""
        return self._tool

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """Zoom with Ctrl+wheel around the pointer."""
        if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            event.ignore()
            return
        if event.angleDelta().y() == 0:
            event.ignore()
            return
        factor = _ZOOM_STEP if event.angleDelta().y() > 0 else 1.0 / _ZOOM_STEP
        self.zoom_by(factor, anchor=event.position())
        event.accept()

    @property
    def zoom(self) -> float:
        """Current zoom relative to the fitted size (`1.0` = fit)."""
        return self._zoom

    def zoom_by(self, factor: float, *, anchor: QPointF | None = None) -> None:
        """Multiply zoom by `factor`, keeping `anchor` fixed on the canvas."""
        old_zoom = self._zoom
        new_zoom = max(_MIN_ZOOM, min(_MAX_ZOOM, old_zoom * factor))
        if new_zoom == old_zoom:
            return
        center = QPointF(self.rect().center())
        pointer = anchor if anchor is not None else center
        relative = pointer - center - self._offset
        self._offset = pointer - center - relative * (new_zoom / old_zoom)
        self._zoom = new_zoom
        self.update()

    def _active_crop_rect(self) -> QRect | None:
        if self._crop_pending and self._crop_rect is not None:
            return self._crop_rect
        if self._crop_origin is not None and self._crop_current is not None and self._crop_dragging:
            return self._crop_drag_rect()
        return self._crop_rect

    def _clear_crop_state(self) -> None:
        self._crop_pending = False
        self._crop_rect = None
        self._crop_origin = None
        self._crop_current = None
        self._crop_dragging = False
        self._crop_edit_handle = None
        self._crop_press_pos = None
        self._crop_press_rect = None

    def _crop_drag_rect(self) -> QRect | None:
        if self._crop_origin is None or self._crop_current is None:
            return None
        bounds = self._image_bounds()
        rect = QRect(self._crop_origin, self._crop_current).normalized().intersected(bounds)
        return snap_all_edges(
            rect,
            self._snap_x_edges,
            self._snap_y_edges,
            threshold=_EDGE_SNAP_THRESHOLD,
            bounds=bounds,
            min_size=_MIN_CROP,
        )

    def _crop_mouse_move(self, widget_pos: QPointF) -> None:
        image_pos = self._widget_to_image_point(widget_pos)
        if image_pos is None:
            return

        if self._crop_pending and self._crop_rect is not None:
            if (
                self._crop_edit_handle is not None
                and self._crop_press_pos is not None
                and self._crop_press_rect is not None
            ):
                bounds = self._image_bounds()
                transformed = transform_selection_rect(
                    self._crop_press_rect,
                    self._crop_edit_handle,
                    self._crop_press_pos,
                    image_pos,
                    bounds=bounds,
                    min_size=_MIN_CROP,
                )
                self._crop_rect = snap_rect_to_edges(
                    transformed,
                    self._crop_edit_handle,
                    self._snap_x_edges,
                    self._snap_y_edges,
                    threshold=_EDGE_SNAP_THRESHOLD,
                    bounds=bounds,
                    min_size=_MIN_CROP,
                )
                self.update()
                return
            handle = hit_test_selection_handle(self._crop_rect, image_pos)
            self.setCursor(getattr(Qt.CursorShape, cursor_for_handle(handle)))
            return

        if self._crop_origin is None:
            return
        self._crop_current = image_pos
        if not self._crop_dragging:
            delta = image_pos - self._crop_origin
            if abs(delta.x()) >= _DRAG_THRESHOLD or abs(delta.y()) >= _DRAG_THRESHOLD:
                self._crop_dragging = True
        self.update()

    def _crop_mouse_press(self, widget_pos: QPointF) -> None:
        image_pos = self._widget_to_image_point(widget_pos)
        if image_pos is None:
            return

        if self._crop_pending and self._crop_rect is not None:
            handle = hit_test_selection_handle(self._crop_rect, image_pos)
            if handle is None:
                # Start a new selection.
                self._crop_pending = False
                self.crop_pending_changed.emit(False)  # noqa: FBT003
                self._crop_rect = None
            else:
                self._crop_edit_handle = handle
                self._crop_press_pos = image_pos
                self._crop_press_rect = QRect(self._crop_rect)
                self.setCursor(getattr(Qt.CursorShape, cursor_for_handle(handle)))
                return

        self._crop_origin = image_pos
        self._crop_current = image_pos
        self._crop_dragging = False
        self.update()

    def _crop_mouse_release(self, widget_pos: QPointF) -> None:
        if self._crop_pending and self._crop_edit_handle is not None:
            self._crop_edit_handle = None
            self._crop_press_pos = None
            self._crop_press_rect = None
            image_pos = self._widget_to_image_point(widget_pos)
            if image_pos is not None and self._crop_rect is not None:
                handle = hit_test_selection_handle(self._crop_rect, image_pos)
                self.setCursor(getattr(Qt.CursorShape, cursor_for_handle(handle)))
            self.update()
            return

        if self._crop_origin is None:
            return
        image_pos = self._widget_to_image_point(widget_pos)
        if image_pos is not None:
            self._crop_current = image_pos
        rect = self._crop_drag_rect()
        self._crop_origin = None
        self._crop_current = None
        self._crop_dragging = False
        if rect is None or rect.width() < _MIN_CROP or rect.height() < _MIN_CROP:
            self._crop_rect = None
            self._crop_pending = False
            self.crop_pending_changed.emit(False)  # noqa: FBT003
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.update()
            return
        self._crop_rect = rect
        self._crop_pending = True
        self.crop_pending_changed.emit(True)  # noqa: FBT003
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.update()

    def _finish_draw(self, widget_pos: QPointF, *, shift: bool) -> None:
        document = self._document
        start = self._draw_start
        self._draw_start = None
        self._draw_current = None
        if document is None or start is None:
            return
        image_pos = self._widget_to_image(widget_pos)
        if image_pos is not None and document.draft is not None:
            if document.draft.tool == AnnotationTool.PEN:
                document.append_draft_point(image_pos)
            else:
                document.update_draft_points(
                    [start, constrain_shape_end(document.draft.tool, start, image_pos, shift=shift)]
                )
        if document.commit_draft():
            self._refresh_pixmap()
            self.document_changed.emit()
        else:
            self.update()

    def _fitted_size(self) -> QSizeF:
        if self._pixmap.isNull() or self.width() <= 0 or self.height() <= 0:
            return QSizeF()
        fitted = self._pixmap.size().scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        display_w = min(fitted.width(), self._pixmap.width())
        display_h = min(fitted.height(), self._pixmap.height())
        return QSizeF(display_w * self._zoom, display_h * self._zoom)

    def _image_bounds(self) -> QRect:
        if self._pixmap.isNull():
            return QRect()
        return QRect(0, 0, self._pixmap.width(), self._pixmap.height())

    def _image_rect(self) -> QRectF:
        size = self._fitted_size()
        if size.isEmpty():
            return QRectF()
        center = QPointF(self.rect().center()) + self._offset
        return QRectF(center.x() - size.width() / 2, center.y() - size.height() / 2, size.width(), size.height())

    def _image_to_widget_rect(self, rect: QRect, image_rect: QRectF) -> QRect:
        if self._pixmap.isNull() or image_rect.isEmpty():
            return QRect()
        scale_x = image_rect.width() / max(1, self._pixmap.width())
        scale_y = image_rect.height() / max(1, self._pixmap.height())
        left = round(image_rect.left() + rect.left() * scale_x)
        top = round(image_rect.top() + rect.top() * scale_y)
        right = round(image_rect.left() + (rect.right() + 1) * scale_x) - 1
        bottom = round(image_rect.top() + (rect.bottom() + 1) * scale_y) - 1
        return QRect(QPoint(left, top), QPoint(right, bottom)).normalized()

    def _paint_crop_overlay(self, painter: QPainter, image_rect: QRectF) -> None:
        bounds = image_rect.toRect()
        crop = self._active_crop_rect()
        clear_widget: QRect | None = None
        source: QRect | None = None
        if crop is not None and crop.isValid() and not crop.isEmpty():
            clear_widget = self._image_to_widget_rect(crop, image_rect)
            source = crop
        paint_selection_frame(
            painter,
            bounds,
            clear_widget,
            pixmap=self._pixmap if clear_widget is not None else None,
            pixmap_source=source,
            show_handles=bool(self._crop_pending and clear_widget is not None),
            border_width=SELECTION_BORDER_WIDTH,
        )

    def _rebuild_snap_edges(self) -> None:
        bounds = self._image_bounds()
        self._snap_x_edges, self._snap_y_edges = collect_edge_guides((), bounds)

    def _refresh_constrained_draft(self, *, shift: bool) -> bool:
        """Recompute the live shape from the last pointer using the Shift state."""
        document = self._document
        start = self._draw_start
        current = self._draw_current
        if document is None or start is None or current is None or document.draft is None:
            return False
        if document.draft.tool == AnnotationTool.PEN:
            return False
        document.update_draft_points([start, constrain_shape_end(document.draft.tool, start, current, shift=shift)])
        self.update()
        return True

    def _refresh_pixmap(self) -> None:
        if self._document is not None:
            self._pixmap = QPixmap.fromImage(self._document.render(include_draft=False))
        self.update()

    def _widget_to_image(self, pos: QPointF) -> QPointF | None:
        point = self._widget_to_image_point(pos)
        return QPointF(point) if point is not None else None

    def _widget_to_image_point(self, pos: QPointF) -> QPoint | None:
        rect = self._image_rect()
        if rect.isEmpty() or self._pixmap.isNull():
            return None
        x = min(max(pos.x(), rect.left()), rect.right())
        y = min(max(pos.y(), rect.top()), rect.bottom())
        rel_x = (x - rect.left()) / rect.width()
        rel_y = (y - rect.top()) / rect.height()
        image_x = round(rel_x * (self._pixmap.width() - 1))
        image_y = round(rel_y * (self._pixmap.height() - 1))
        return QPoint(
            min(max(0, image_x), self._pixmap.width() - 1),
            min(max(0, image_y), self._pixmap.height() - 1),
        )


def _shift_pressed(modifiers: Qt.KeyboardModifier) -> bool:
    """Return whether Shift is in `modifiers`."""
    return bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
