"""Fullscreen frozen-desktop overlay for ShareX-like region selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QPoint, QRect, Qt
from PySide6.QtGui import QColor, QCursor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QDialog

from harrix_swiss_knife.screenshot.dpi import (
    crop_pixmap_from_logical_rect,
    logical_rect_to_pixel_rect,
    pixmap_device_pixel_ratio,
)
from harrix_swiss_knife.screenshot.shutter_button import ShutterPanel, position_panel_on_left_edge
from harrix_swiss_knife.screenshot.window_rects import snap_rect_at_point
from harrix_swiss_knife.screenshot.window_visibility import (
    claim_screenshot_keyboard,
    mark_screenshot_ui,
    release_screenshot_keyboard,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from PySide6.QtGui import QHideEvent, QKeyEvent, QMouseEvent, QPaintEvent, QShowEvent

_MIN_SELECTION = 2
_DRAG_THRESHOLD = 4
_DIM_COLOR = QColor(0, 0, 0, 120)
_BORDER_COLOR = QColor(0, 174, 255)
_BORDER_WIDTH = 2

RESULT_TOGGLE_ARRANGE = 2


class RegionOverlay(QDialog):
    """Overlay that shows a frozen desktop grab and lets the user select a region.

    With `with_shutter_controls=True`, arrange/close buttons are embedded as child
    widgets, so they receive clicks even when other application dialogs are modal —
    the overlay itself runs modally via `exec()` and owns all input. Clicking
    the arrange button finishes the dialog with `RESULT_TOGGLE_ARRANGE`.

    When `window_rects` is provided (global logical coordinates at grab time), moving
    the cursor highlights the top-most window under the pointer. A click without a
    drag captures that window; dragging beyond a small threshold starts a free region.

    """

    def __init__(
        self,
        frozen: QPixmap,
        geometry: QRect,
        *,
        with_shutter_controls: bool = False,
        window_rects: Sequence[QRect] | None = None,
    ) -> None:
        """Create a fullscreen overlay for region selection, displaying the frozen desktop.

        Args:

        - `frozen` (`QPixmap`): Stitched screenshot of the virtual desktop to display as background.
        - `geometry` (`QRect`): The target geometry in global (screen) coordinates for overlay placement.
        - `with_shutter_controls` (`bool`): If `True`, embed arrange/close buttons on the left edge.
        - `window_rects` (`Sequence[QRect] | None`): Snappable window bounds in global logical pixels.

        """
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.Window
        )
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setGeometry(geometry)

        self._frozen = frozen
        self._origin: QPoint | None = None
        self._current: QPoint | None = None
        self._crop: QImage | None = None
        self._dragging = False
        self._snap_rect: QRect | None = None
        origin = geometry.topLeft()
        self._window_rects_local = [
            rect.translated(-origin.x(), -origin.y()).intersected(QRect(0, 0, geometry.width(), geometry.height()))
            for rect in (window_rects or ())
        ]
        self._window_rects_local = [rect for rect in self._window_rects_local if rect.isValid() and not rect.isEmpty()]

        if with_shutter_controls:
            panel = ShutterPanel(self)
            panel.set_mode("selection")
            panel.triggered.connect(lambda: self.done(RESULT_TOGGLE_ARRANGE))
            panel.cancelled.connect(self.reject)
            position_panel_on_left_edge(panel, geometry)
            panel.show()

    @property
    def cropped_image(self) -> QImage | None:
        """Return the selected crop, or `None` if cancelled / empty."""
        return self._crop

    def event(self, event: QEvent) -> bool:
        """Accept Escape as a shortcut override so it is not stolen by other Windows.

        Args:

        - `event` (`QEvent`): The event being delivered to the overlay.

        """
        if event.type() == QEvent.Type.ShortcutOverride and _is_escape_key(event):
            event.accept()
            return True
        return super().event(event)

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        """Release the keyboard grab when the overlay is hidden."""
        release_screenshot_keyboard(self)
        super().hideEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Escape cancels the screenshot capture."""
        if event.key() == Qt.Key.Key_Escape:
            self._crop = None
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Update snap highlight while hovering, or the selection rectangle while dragging."""
        pos = event.position().toPoint()
        if self._origin is None:
            self._update_snap_at(pos)
            return

        self._current = pos
        if not self._dragging:
            delta = pos - self._origin
            if abs(delta.x()) >= _DRAG_THRESHOLD or abs(delta.y()) >= _DRAG_THRESHOLD:
                self._dragging = True
                self._snap_rect = None
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start a free selection, or remember a window snap for click-to-capture."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.position().toPoint()
        self._origin = pos
        self._current = pos
        self._dragging = False
        self._update_snap_at(pos)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Finish selection: snap click, free-drag crop, or keep selecting."""
        if event.button() != Qt.MouseButton.LeftButton or self._origin is None:
            return
        pos = event.position().toPoint()
        self._current = pos

        capture_rect: QRect | None
        if self._dragging:
            capture_rect = self._selection_rect()
        elif self._snap_rect is not None:
            capture_rect = QRect(self._snap_rect)
        else:
            capture_rect = None

        was_dragging = self._dragging
        self._origin = None
        self._current = None
        self._dragging = False

        if capture_rect is None:
            # Click on empty desktop: stay in selection mode.
            self._update_snap_at(pos)
            self.update()
            return

        if capture_rect.width() < _MIN_SELECTION or capture_rect.height() < _MIN_SELECTION:
            self._crop = None
            if was_dragging:
                self.reject()
            else:
                self._update_snap_at(pos)
                self.update()
            return

        self._finish_with_rect(capture_rect)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Draw frozen desktop, dim overlay, and clear selection or snap region."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=False)
        painter.drawPixmap(self.rect(), self._frozen)
        painter.fillRect(self.rect(), _DIM_COLOR)

        rect = self._active_highlight_rect()
        if rect is not None and rect.isValid():
            source = logical_rect_to_pixel_rect(rect, pixmap_device_pixel_ratio(self._frozen))
            painter.drawPixmap(rect, self._frozen, source)
            pen = QPen(_BORDER_COLOR, _BORDER_WIDTH)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(0, 0, -1, -1))

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Take keyboard focus so Escape cancels capture on Tool overlays."""
        super().showEvent(event)
        claim_screenshot_keyboard(self)
        self._update_snap_at(self.mapFromGlobal(QCursor.pos()))

    def _active_highlight_rect(self) -> QRect | None:
        """Return the rectangle currently shown as the clear selection / snap region."""
        if self._dragging:
            return self._selection_rect()
        if self._snap_rect is not None:
            return self._snap_rect
        return self._selection_rect()

    def _finish_with_rect(self, rect: QRect) -> None:
        """Crop `rect` from the frozen desktop and accept the dialog."""
        self._crop = crop_pixmap_from_logical_rect(self._frozen, rect)
        if self._crop is None or self._crop.isNull():
            self._crop = None
            self.reject()
            return
        self.accept()

    def _selection_rect(self) -> QRect | None:
        if self._origin is None or self._current is None:
            return None
        return QRect(self._origin, self._current).normalized()

    def _update_snap_at(self, pos: QPoint) -> None:
        """Refresh the hover snap rectangle for `pos` and repaint when it changes."""
        new_snap = snap_rect_at_point(pos, self._window_rects_local)
        if new_snap == self._snap_rect:
            return
        self._snap_rect = new_snap
        self.update()


def _is_escape_key(event: QEvent) -> bool:
    key = getattr(event, "key", None)
    return callable(key) and key() == Qt.Key.Key_Escape
