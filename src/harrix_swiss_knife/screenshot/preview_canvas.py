"""Zoomable, pannable canvas for screenshot preview with annotation tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, QSizeF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent, QPixmap, QResizeEvent, QWheelEvent
from PySide6.QtWidgets import QWidget

from harrix_swiss_knife.screenshot.annotations import Annotation, AnnotationStyle, AnnotationTool, paint_annotation

if TYPE_CHECKING:
    from PySide6.QtGui import QImage

    from harrix_swiss_knife.screenshot.annotations import AnnotationDocument

_ZOOM_STEP = 1.15
_MIN_ZOOM = 0.25
_MAX_ZOOM = 16.0
_MIN_SHAPE_POINTS = 2


class ScreenshotPreviewCanvas(QWidget):
    """Show an image fitted with aspect ratio; Ctrl+wheel zooms; middle-drag pans.

    Left-drag draws with the active `AnnotationTool` when a document is attached.

    """

    document_changed = Signal()
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
        self._crop_pending = False

    def cancel_crop(self) -> None:
        """Discard a pending crop rectangle."""
        if self._document is not None:
            self._document.cancel_draft()
        self._crop_pending = False
        self._draw_start = None
        self.update()
        self.crop_pending_changed.emit(False)  # noqa: FBT003

    def confirm_crop(self) -> bool:
        """Apply the pending crop rectangle. Return whether it succeeded."""
        document = self._document
        if document is None or document.draft is None or document.draft.tool != AnnotationTool.CROP:
            self.cancel_crop()
            return False
        if len(document.draft.points) < _MIN_SHAPE_POINTS:
            self.cancel_crop()
            return False
        rect = QRectF(document.draft.points[0], document.draft.points[-1]).normalized()
        document.cancel_draft()
        self._crop_pending = False
        self.crop_pending_changed.emit(False)  # noqa: FBT003
        if not document.apply_crop(rect):
            self.update()
            return False
        self._refresh_pixmap()
        self.document_changed.emit()
        return True

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

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Pan with middle button, or update the draft while left-dragging."""
        if self._pan_start is not None:
            delta = event.position() - self._pan_start
            self._offset = self._pan_origin + delta
            self.update()
            event.accept()
            return
        if self._draw_start is not None and self._document is not None and self._document.draft is not None:
            image_pos = self._widget_to_image(event.position())
            if image_pos is None:
                event.accept()
                return
            draft = self._document.draft
            if draft.tool == AnnotationTool.PEN:
                self._document.append_draft_point(image_pos)
            else:
                self._document.update_draft_points([self._draw_start, image_pos])
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start panning or begin a draft annotation."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_start = event.position()
            self._pan_origin = QPointF(self._offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool != AnnotationTool.NONE:
            if self._crop_pending:
                event.accept()
                return
            image_pos = self._widget_to_image(event.position())
            if image_pos is None or self._document is None:
                event.accept()
                return
            if self._tool == AnnotationTool.TEXT:
                self.text_requested.emit(image_pos)
                event.accept()
                return
            self._draw_start = image_pos
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
        """End panning or commit the draft annotation / crop."""
        if event.button() == Qt.MouseButton.MiddleButton and self._pan_start is not None:
            self._pan_start = None
            self.set_tool(self._tool)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._draw_start is not None:
            self._finish_draw(event.position())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        """Draw the fitted pixmap and the live draft overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        image_rect = self._image_rect()
        if not self._pixmap.isNull():
            painter.drawPixmap(image_rect.toRect(), self._pixmap)
        if self._document is not None and self._document.draft is not None and not image_rect.isEmpty():
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
        self.update()

    def set_style(self, color: QColor | None = None, width: float | None = None) -> None:
        """Update the stroke color and/or width for new annotations."""
        if color is not None:
            self._style.color = QColor(color)
        if width is not None:
            self._style.width = max(1.0, width)

    def set_tool(self, tool: AnnotationTool) -> None:
        """Select the drawing tool (`NONE` keeps view-only left-click)."""
        if self._crop_pending:
            if tool == self._tool:
                return
            self.cancel_crop()
        self._tool = tool
        self._draw_start = None
        if self._document is not None:
            self._document.cancel_draft()
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

    def _finish_draw(self, widget_pos: QPointF) -> None:
        document = self._document
        start = self._draw_start
        self._draw_start = None
        if document is None or start is None:
            return
        image_pos = self._widget_to_image(widget_pos)
        if image_pos is not None and document.draft is not None:
            if document.draft.tool == AnnotationTool.PEN:
                document.append_draft_point(image_pos)
            else:
                document.update_draft_points([start, image_pos])
        draft = document.draft
        if draft is not None and draft.tool == AnnotationTool.CROP and len(draft.points) >= _MIN_SHAPE_POINTS:
            from harrix_swiss_knife.screenshot.annotations import _is_meaningful  # noqa: PLC0415

            if _is_meaningful(draft):
                self._crop_pending = True
                self.crop_pending_changed.emit(True)  # noqa: FBT003
                self.update()
            else:
                document.cancel_draft()
                self.update()
            return
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

    def _image_rect(self) -> QRectF:
        size = self._fitted_size()
        if size.isEmpty():
            return QRectF()
        center = QPointF(self.rect().center()) + self._offset
        return QRectF(center.x() - size.width() / 2, center.y() - size.height() / 2, size.width(), size.height())

    def _refresh_pixmap(self) -> None:
        if self._document is not None:
            self._pixmap = QPixmap.fromImage(self._document.render(include_draft=False))
        self.update()

    def _widget_to_image(self, pos: QPointF) -> QPointF | None:
        rect = self._image_rect()
        if rect.isEmpty() or self._pixmap.isNull():
            return None
        if not rect.contains(pos):
            # Clamp to image bounds for smoother drawing near edges.
            x = min(max(pos.x(), rect.left()), rect.right())
            y = min(max(pos.y(), rect.top()), rect.bottom())
            pos = QPointF(x, y)
        rel_x = (pos.x() - rect.left()) / rect.width()
        rel_y = (pos.y() - rect.top()) / rect.height()
        return QPointF(rel_x * self._pixmap.width(), rel_y * self._pixmap.height())
