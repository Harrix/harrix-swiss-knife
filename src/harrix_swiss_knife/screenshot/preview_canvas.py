"""Zoomable, pannable canvas for screenshot preview."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, QSizeF, Qt
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent, QPixmap, QResizeEvent, QWheelEvent
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from PySide6.QtGui import QImage

_ZOOM_STEP = 1.15
_MIN_ZOOM = 0.25
_MAX_ZOOM = 16.0


class ScreenshotPreviewCanvas(QWidget):
    """Show an image fitted with aspect ratio; Ctrl+wheel zooms; middle-drag pans."""

    def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        """Create a canvas for `image` at fit zoom."""
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._pixmap = QPixmap.fromImage(image)
        self._zoom = 1.0
        self._offset = QPointF()
        self._drag_start: QPointF | None = None
        self._drag_origin = QPointF()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Pan while the middle mouse button is held."""
        if self._drag_start is not None:
            delta = event.position() - self._drag_start
            self._offset = self._drag_origin + delta
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start panning on middle-button press."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._drag_start = event.position()
            self._drag_origin = QPointF(self._offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """End middle-button panning."""
        if event.button() == Qt.MouseButton.MiddleButton and self._drag_start is not None:
            self._drag_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        """Draw the fitted (and possibly zoomed/panned) pixmap."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
        if not self._pixmap.isNull():
            painter.drawPixmap(self._image_rect().toRect(), self._pixmap)
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Repaint when the available fit area changes."""
        super().resizeEvent(event)
        self.update()

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

    def _fitted_size(self) -> QSizeF:
        if self._pixmap.isNull() or self.width() <= 0 or self.height() <= 0:
            return QSizeF()
        # Fit when larger than the viewport; never upscale at zoom 1.0.
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
