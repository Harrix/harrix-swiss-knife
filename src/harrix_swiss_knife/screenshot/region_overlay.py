"""Fullscreen frozen-desktop overlay for ShareX-like region selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QDialog

from harrix_swiss_knife.screenshot.dpi import (
    crop_pixmap_from_logical_rect,
    logical_rect_to_pixel_rect,
    pixmap_device_pixel_ratio,
)
from harrix_swiss_knife.screenshot.shutter_button import ShutterPanel, position_panel_on_left_edge
from harrix_swiss_knife.screenshot.window_visibility import mark_screenshot_ui

if TYPE_CHECKING:
    from PySide6.QtGui import QKeyEvent, QMouseEvent, QPaintEvent

_MIN_SELECTION = 2
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

    """

    def __init__(self, frozen: QPixmap, geometry: QRect, *, with_shutter_controls: bool = False) -> None:
        """Create a fullscreen overlay for region selection, displaying the frozen desktop.

        Args:

        - `frozen` (`QPixmap`): Stitched screenshot of the virtual desktop to display as background.
        - `geometry` (`QRect`): The target geometry in global (screen) coordinates for overlay placement.
        - `with_shutter_controls` (`bool`): If `True`, embed arrange/close buttons on the left edge.

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
        self.setGeometry(geometry)

        self._frozen = frozen
        self._origin: QPoint | None = None
        self._current: QPoint | None = None
        self._crop: QImage | None = None

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

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Escape clears an in-progress drag; otherwise cancels the capture."""
        if event.key() == Qt.Key.Key_Escape:
            if self._origin is not None:
                self._origin = None
                self._current = None
                self.update()
                return
            self._crop = None
            self.reject()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Update the selection rectangle while dragging."""
        if self._origin is None:
            return
        self._current = event.position().toPoint()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start a new selection rectangle."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._origin = event.position().toPoint()
        self._current = self._origin
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Finish selection and crop the frozen pixmap."""
        if event.button() != Qt.MouseButton.LeftButton or self._origin is None:
            return
        self._current = event.position().toPoint()
        rect = self._selection_rect()
        self._origin = None
        self._current = None

        if rect is None or rect.width() < _MIN_SELECTION or rect.height() < _MIN_SELECTION:
            self._crop = None
            self.reject()
            return

        self._crop = crop_pixmap_from_logical_rect(self._frozen, rect)
        if self._crop is None or self._crop.isNull():
            self._crop = None
            self.reject()
            return

        self.accept()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Draw frozen desktop, dim overlay, and clear selection region."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=False)
        painter.drawPixmap(self.rect(), self._frozen)
        painter.fillRect(self.rect(), _DIM_COLOR)

        rect = self._selection_rect()
        if rect is not None and rect.isValid():
            source = logical_rect_to_pixel_rect(rect, pixmap_device_pixel_ratio(self._frozen))
            painter.drawPixmap(rect, self._frozen, source)
            pen = QPen(_BORDER_COLOR, _BORDER_WIDTH)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(0, 0, -1, -1))

    def _selection_rect(self) -> QRect | None:
        if self._origin is None or self._current is None:
            return None
        return QRect(self._origin, self._current).normalized()
