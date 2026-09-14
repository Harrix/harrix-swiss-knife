"""Interactive fullscreen lightbox for Vector Icons."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent, QImage, QMouseEvent, QPainter, QPaintEvent, QWheelEvent
from PySide6.QtWidgets import QWidget
from shiboken6 import isValid

from harrix_swiss_knife.apps.common.widgets.app_window_lightbox import AppWindowLightboxDialog
from harrix_swiss_knife.apps.icons.lightbox_cache import PREVIEW_RENDER_SIZE, lightbox_image_cache
from harrix_swiss_knife.apps.icons.vector_render import render_icon_to_image
from harrix_swiss_knife.toast_countdown_notification import ToastCountdownNotification

if TYPE_CHECKING:
    from collections.abc import Sequence

_SCREEN_MARGIN = 32
_ZOOM_STEP = 1.2
_MIN_ZOOM = 0.25
_MAX_ZOOM = 8.0
_DRAG_THRESHOLD = 3.0
_LOAD_TOAST_DELAY_MS = 1000

_render_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="icon-lightbox")


class IconLightboxCanvas(QWidget):
    """Paint, zoom, and drag one high-resolution icon preview."""

    backdrop_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize canvas state."""
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._path: Path | None = None
        self._image: QImage | None = None
        self._zoom = 1.0
        self._offset = QPointF()
        self._drag_start: QPointF | None = None
        self._drag_origin = QPointF()
        self._did_drag = False

    def clear_image(self) -> None:
        """Remove the current preview while keeping zoom state reset."""
        self._path = None
        self._image = None
        self._zoom = 1.0
        self._offset = QPointF()
        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Close the lightbox on a left double-click (image or backdrop)."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = None
            self._did_drag = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.backdrop_clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Pan the enlarged icon while dragging."""
        if self._drag_start is not None:
            delta = event.position() - self._drag_start
            if abs(delta.x()) + abs(delta.y()) >= _DRAG_THRESHOLD:
                self._did_drag = True
            self._offset = self._drag_origin + delta
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start panning when pressing the displayed icon."""
        if event.button() == Qt.MouseButton.LeftButton and self._image_rect().contains(event.position()):
            self._drag_start = event.position()
            self._drag_origin = QPointF(self._offset)
            self._did_drag = False
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Finish panning or close after a backdrop click."""
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return
        was_dragging = self._drag_start is not None
        did_drag = self._did_drag
        self._drag_start = None
        self._did_drag = False
        self.setCursor(Qt.CursorShape.OpenHandCursor if self._zoom > 1.0 else Qt.CursorShape.ArrowCursor)
        if was_dragging:
            event.accept()
            return
        if not did_drag and not self._image_rect().contains(event.position()):
            self.backdrop_clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        """Draw the preview over the transparent canvas."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
        if self._image is not None and not self._image.isNull():
            painter.drawImage(self._image_rect(), self._image)
        painter.end()

    def set_image(self, path: Path, image: QImage | None) -> None:
        """Show a pre-rendered image and reset the viewport."""
        self._path = path
        self._zoom = 1.0
        self._offset = QPointF()
        self._image = image
        self.update()

    def set_path(self, path: Path) -> None:
        """Load a new icon synchronously (used by tests and fallbacks)."""
        cache = lightbox_image_cache()
        image = cache.get(path, PREVIEW_RENDER_SIZE)
        if image is None:
            image = render_icon_to_image(path, PREVIEW_RENDER_SIZE)
            if image is not None and not image.isNull():
                cache.put(path, PREVIEW_RENDER_SIZE, image)
        self.set_image(path, image)

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """Zoom around the mouse pointer."""
        if event.angleDelta().y() == 0:
            event.ignore()
            return
        factor = _ZOOM_STEP if event.angleDelta().y() > 0 else 1.0 / _ZOOM_STEP
        self.zoom_by(factor, anchor=event.position())
        event.accept()

    @property
    def zoom(self) -> float:
        """Current zoom factor."""
        return self._zoom

    def zoom_by(self, factor: float, *, anchor: QPointF | None = None) -> None:
        """Change zoom while keeping `anchor` fixed on the canvas."""
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

    def _base_side(self) -> float:
        return max(64.0, min(self.width(), self.height()) - _SCREEN_MARGIN * 2)

    def _image_rect(self) -> QRectF:
        side = self._base_side() * self._zoom
        center = QPointF(self.rect().center()) + self._offset
        return QRectF(center.x() - side / 2, center.y() - side / 2, side, side)


class IconLightboxDialog(AppWindowLightboxDialog):
    """Browse icon files with zoom, pan, keyboard navigation, and backdrop close."""

    def __init__(
        self,
        paths: Sequence[Path],
        *,
        current_index: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        """Build a modal lightbox fitted to its application window."""
        valid_paths = [path for path in paths if path.is_file()]
        super().__init__(parent, item_count=len(valid_paths), current_index=current_index)
        self._paths = valid_paths
        self._load_token = 0
        self._load_toast: ToastCountdownNotification | None = None
        self._toast_present_timer = QTimer(self)
        self._toast_present_timer.setSingleShot(True)
        self._toast_present_timer.timeout.connect(self._present_load_toast)
        self.canvas = IconLightboxCanvas(self)
        self.attach_content(self.canvas)
        self.finish_setup()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Cancel in-flight preview loads when the lightbox closes."""
        self._cancel_load()
        super().closeEvent(event)

    def empty_caption(self) -> str:
        """Caption when there are no icon files."""
        return "No icon to display"

    def show_item(self, index: int) -> None:
        """Load the icon at `index` from cache or a background render."""
        path = self._paths[index]
        self.setWindowTitle(path.name)
        self.set_caption(f"{path.name}  ·  {index + 1} / {len(self._paths)}")
        self._start_load(path)

    def _cancel_load(self) -> None:
        self._load_token += 1
        self._toast_present_timer.stop()
        self._stop_load_toast()

    def _complete_load(self, token: int, future: Future[tuple[str, QImage | None]]) -> None:
        try:
            path_str, image = future.result()
        except Exception:
            path_str, image = "", None
        if image is not None and not image.isNull() and path_str:
            lightbox_image_cache().put(Path(path_str), PREVIEW_RENDER_SIZE, image)
        else:
            image = None
        if not isValid(self) or token != self._load_token:
            return
        self._toast_present_timer.stop()
        self._stop_load_toast()
        if path_str:
            self.canvas.set_image(Path(path_str), image)

    def _present_load_toast(self) -> None:
        toast = self._load_toast
        if toast is None or not isValid(self):
            return
        toast.present(activate=False, pinned=True)
        toast.update_time()

    def _schedule_complete_load(self, token: int, future: Future[tuple[str, QImage | None]]) -> None:
        # Called from a worker thread; marshal back onto the GUI thread via `self`.
        QTimer.singleShot(0, self, partial(self._complete_load, token, future))

    def _start_load(self, path: Path) -> None:
        cached = lightbox_image_cache().get(path, PREVIEW_RENDER_SIZE)
        if cached is not None:
            self._cancel_load()
            self.canvas.set_image(path, cached)
            return

        self._cancel_load()
        self.canvas.clear_image()
        token = self._load_token
        toast = ToastCountdownNotification("Opening icon…")
        toast.start_countdown(present=False, pinned=True, activate=False)
        self._load_toast = toast
        self._toast_present_timer.start(_LOAD_TOAST_DELAY_MS)
        future = _render_executor.submit(_render_preview, path, PREVIEW_RENDER_SIZE)
        future.add_done_callback(partial(self._schedule_complete_load, token))

    def _stop_load_toast(self) -> None:
        toast = self._load_toast
        self._load_toast = None
        if toast is None:
            return
        toast.timer.stop()
        toast.close()


def _render_preview(path: Path, size: int) -> tuple[str, QImage | None]:
    image = render_icon_to_image(path, size)
    image = image.copy() if image is not None and not image.isNull() else None
    return str(path.resolve()), image
