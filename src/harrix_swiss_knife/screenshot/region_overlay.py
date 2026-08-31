"""Fullscreen frozen-desktop overlay for ShareX-like region selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QFontMetrics, QImage, QIntValidator, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QDialog, QLineEdit, QWidget

from harrix_swiss_knife.screenshot.dpi import (
    crop_pixmap_from_logical_rect,
    logical_rect_to_pixel_rect,
    pixmap_device_pixel_ratio,
)
from harrix_swiss_knife.screenshot.selection_edit import (
    ArrowDir,
    HandleKind,
    collect_edge_guides,
    cursor_for_handle,
    hit_test_selection_handle,
    nudge_selection_rect,
    resize_selection_to_size,
    snap_rect_to_edges,
    transform_selection_rect,
)
from harrix_swiss_knife.screenshot.selection_guides import (
    SizeLabelKind,
    guide_label_font,
    hit_test_size_label,
    paint_selection_guides,
    parse_size_label,
    selection_guide_labels,
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
_HANDLE_DRAW = 6
_EDGE_SNAP_THRESHOLD = 8
_ARROW_STEP = 1
_ARROW_STEP_SHIFT = 10
_DIM_COLOR = QColor(0, 0, 0, 120)
_BORDER_COLOR = QColor(0, 174, 255)
_HANDLE_FILL = QColor(0, 174, 255)
_BORDER_WIDTH = 2
_GUIDE_BORDER_WIDTH = 1
_SIZE_EDITOR_PAD_X = 12
_SIZE_EDITOR_PAD_Y = 4
_SIZE_EDITOR_MIN_DIGITS = "00000"
_SIZE_EDITOR_STYLE = """
QLineEdit {
    color: rgb(230, 230, 230);
    background-color: rgba(20, 20, 20, 220);
    border: 1px solid rgb(0, 174, 255);
    font-weight: bold;
    padding: 0px 4px;
    selection-background-color: rgb(0, 174, 255);
}
"""

RESULT_TOGGLE_ARRANGE = 2
RESULT_TOGGLE_KEEP_WINDOWS = 3

_ARROW_KEYS: dict[Qt.Key, ArrowDir] = {
    Qt.Key.Key_Left: "left",
    Qt.Key.Key_Right: "right",
    Qt.Key.Key_Up: "up",
    Qt.Key.Key_Down: "down",
}


class RegionOverlay(QDialog):
    """Overlay that shows a frozen desktop grab and lets the user select a region.

    With `with_shutter_controls=True`, arrange/adjust/guides/keep-Windows/
    clipboard/close buttons are embedded as child widgets. Arrange finishes
    with `RESULT_TOGGLE_ARRANGE`. Keep Windows finishes with
    `RESULT_TOGGLE_KEEP_WINDOWS` so the capture loop can hide or restore app
    Windows and grab again. Clipboard-only skips the preview after capture.
    Adjust (checkable) keeps the next selection editable: move/resize with
    handles, Enter or double-click to capture. Double-click the width or height
    numbers (when guides are on) to type a size; Enter or a click elsewhere
    applies it. Guides (checkable) draw a thinner frame with thirds, halves,
    diagonal, size, and angle.

    When `window_rects` is provided, hovering highlights the most specific region under
    the pointer; a click without a drag captures (or edits) that region.

    """

    def __init__(
        self,
        frozen: QPixmap,
        geometry: QRect,
        *,
        with_shutter_controls: bool = False,
        window_rects: Sequence[QRect] | None = None,
        keep_windows: bool = False,
        clipboard_only: bool = False,
        adjust_mode: bool = False,
        guides_mode: bool = False,
    ) -> None:
        """Create a fullscreen overlay for region selection, displaying the frozen desktop.

        Args:

        - `frozen` (`QPixmap`): Stitched screenshot of the virtual desktop to display as background.
        - `geometry` (`QRect`): The target geometry in global (screen) coordinates for overlay placement.
        - `with_shutter_controls` (`bool`): If `True`, embed shutter controls on the left edge.
        - `window_rects` (`Sequence[QRect] | None`): Snappable window bounds in global logical pixels.
        - `keep_windows` (`bool`): If `True`, start with the keep-Windows shutter button on.
        - `clipboard_only` (`bool`): If `True`, start with the clipboard-only shutter button on.
        - `adjust_mode` (`bool`): If `True`, start with adjust-region enabled.
        - `guides_mode` (`bool`): If `True`, start with composition guides enabled.

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
        self._panel: ShutterPanel | None = None
        self._keep_windows = keep_windows
        self._clipboard_only = clipboard_only
        self._guides_enabled = False
        self._edit_rect: QRect | None = None
        self._edit_handle: HandleKind | None = None
        self._edit_press_pos: QPoint | None = None
        self._edit_press_rect: QRect | None = None
        self._size_edit_kind: SizeLabelKind | None = None
        self._size_edit_closing = False
        self._suppress_confirm_once = False
        self._size_editor = self._make_size_editor()
        origin = geometry.topLeft()
        self._window_rects_local = [
            rect.translated(-origin.x(), -origin.y()).intersected(QRect(0, 0, geometry.width(), geometry.height()))
            for rect in (window_rects or ())
        ]
        self._window_rects_local = [rect for rect in self._window_rects_local if rect.isValid() and not rect.isEmpty()]
        self._snap_x_edges, self._snap_y_edges = collect_edge_guides(self._window_rects_local, self.rect())

        if with_shutter_controls:
            panel = ShutterPanel(self)
            panel.set_mode("selection")
            panel.set_keep_windows(enabled=keep_windows)
            panel.set_clipboard_only(enabled=clipboard_only)
            panel.triggered.connect(lambda: self.done(RESULT_TOGGLE_ARRANGE))
            panel.cancelled.connect(self.reject)
            panel.keep_windows_toggled.connect(lambda _enabled: self.done(RESULT_TOGGLE_KEEP_WINDOWS))
            panel.guides_toggled.connect(lambda enabled: self._set_guides_enabled(enabled=enabled))
            panel.geometry_changed.connect(lambda: position_panel_on_left_edge(panel, geometry))
            if adjust_mode:
                panel.set_adjust_mode(enabled=True)
            if guides_mode:
                panel.set_guides_mode(enabled=True)
            position_panel_on_left_edge(panel, geometry)
            panel.show()
            self._panel = panel

    @property
    def adjust_mode(self) -> bool:
        """Whether the next selection should stay editable until confirmed."""
        return self._panel is not None and self._panel.adjust_mode

    @property
    def clipboard_only(self) -> bool:
        """Whether capture should skip the preview and only copy to the clipboard."""
        if self._panel is not None:
            return self._panel.clipboard_only
        return self._clipboard_only

    @property
    def cropped_image(self) -> QImage | None:
        """Return the selected crop, or `None` if cancelled / empty."""
        return self._crop

    def event(self, event: QEvent) -> bool:
        """Accept Escape as a shortcut override so it is not stolen by other Windows.

        Args:

        - `event` (`QEvent`): The event being delivered to the overlay.

        """
        editor = getattr(self, "_size_editor", None)
        if editor is not None and editor.isVisible() and event.type() == QEvent.Type.ShortcutOverride:
            return super().event(event)
        if event.type() == QEvent.Type.ShortcutOverride and (
            _is_escape_key(event) or _is_arrow_key(event) or _is_enter_key(event)
        ):
            event.accept()
            return True
        return super().event(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Escape cancels the typed size; Enter applies it without capturing."""
        if watched is self._size_editor and event.type() == QEvent.Type.KeyPress:
            if _is_escape_key(event):
                self._cancel_size_edit()
                return True
            if _is_enter_key(event):
                self._commit_size_edit(from_enter=True)
                return True
        return super().eventFilter(watched, event)

    @property
    def guides_mode(self) -> bool:
        """Whether composition guides are drawn on the selection frame."""
        return self._guides_enabled

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        """Release the keyboard grab when the overlay is hidden."""
        self._close_size_editor()
        release_screenshot_keyboard(self)
        super().hideEvent(event)

    @property
    def keep_windows(self) -> bool:
        """Whether application Windows should stay visible in the next grab."""
        if self._panel is not None:
            return self._panel.keep_windows
        return self._keep_windows

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Enter confirms; arrows nudge/resize; Escape clears the frame or cancels."""
        if self._size_editor.isVisible():
            if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
                self._commit_size_edit(from_enter=True)
                event.accept()
                return
            if event.key() == Qt.Key.Key_Escape:
                self._cancel_size_edit()
                event.accept()
                return
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter} and self._edit_rect is not None:
            if self._suppress_confirm_once:
                self._suppress_confirm_once = False
                event.accept()
                return
            self._finish_with_rect(self._edit_rect)
            event.accept()
            return
        if event.key() == Qt.Key.Key_Escape:
            if self._edit_rect is not None:
                self._clear_edit_rect()
                event.accept()
                return
            self._crop = None
            self.reject()
            event.accept()
            return
        direction = _ARROW_KEYS.get(event.key())
        if direction is not None and self._edit_rect is not None:
            self._nudge_edit_rect(direction, event.modifiers())
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Double-click a size number to type it, or the frame to capture."""
        if event.button() != Qt.MouseButton.LeftButton or self._edit_rect is None:
            return
        pos = event.position().toPoint()
        kind = self._hit_size_label(pos)
        if kind is not None:
            self._start_size_edit(kind)
            event.accept()
            return
        if self._edit_rect.contains(pos):
            self._finish_with_rect(self._edit_rect)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Update snap, free-drag selection, or editable frame move/resize."""
        pos = event.position().toPoint()

        if self._edit_rect is not None:
            if self._edit_handle is not None and self._edit_press_pos is not None and self._edit_press_rect is not None:
                transformed = transform_selection_rect(
                    self._edit_press_rect,
                    self._edit_handle,
                    self._edit_press_pos,
                    pos,
                    bounds=self.rect(),
                    min_size=_MIN_SELECTION,
                )
                self._edit_rect = snap_rect_to_edges(
                    transformed,
                    self._edit_handle,
                    self._snap_x_edges,
                    self._snap_y_edges,
                    threshold=_EDGE_SNAP_THRESHOLD,
                    bounds=self.rect(),
                    min_size=_MIN_SELECTION,
                )
                self.update()
                return
            if self._hit_size_label(pos) is not None:
                self.setCursor(Qt.CursorShape.IBeamCursor)
                return
            self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, pos))
            return

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
        """Start free selection, snap capture, or begin editing an adjustable frame."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.position().toPoint()

        if self._size_editor.isVisible():
            self._commit_size_edit()
        if self._edit_rect is not None:
            if self._hit_size_label(pos) is not None:
                return
            handle = hit_test_selection_handle(self._edit_rect, pos)
            if handle is None:
                return
            self._edit_handle = handle
            self._edit_press_pos = pos
            self._edit_press_rect = QRect(self._edit_rect)
            self._apply_edit_cursor(handle)
            return

        self._origin = pos
        self._current = pos
        self._dragging = False
        self._update_snap_at(pos)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Finish free selection, enter edit mode, or end a frame edit drag."""
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self._edit_rect is not None:
            self._edit_handle = None
            self._edit_press_pos = None
            self._edit_press_rect = None
            self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, event.position().toPoint()))
            self.update()
            return

        if self._origin is None:
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

        if self._adjust_mode_enabled():
            self._enter_edit_rect(capture_rect)
            return

        self._finish_with_rect(capture_rect)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Draw frozen desktop, dim overlay, selection/snap, and edit handles."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=False)
        painter.drawPixmap(self.rect(), self._frozen)
        painter.fillRect(self.rect(), _DIM_COLOR)

        rect = self._active_highlight_rect()
        if rect is not None and rect.isValid():
            source = logical_rect_to_pixel_rect(rect, pixmap_device_pixel_ratio(self._frozen))
            painter.drawPixmap(rect, self._frozen, source)
            guides_on = self._guides_enabled
            pen = QPen(_BORDER_COLOR, _GUIDE_BORDER_WIDTH if guides_on else _BORDER_WIDTH)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(0, 0, -1, -1))
            if guides_on:
                skip = self._size_edit_kind if self._size_editor.isVisible() else None
                paint_selection_guides(painter, rect, self.rect(), skip_size=skip)
            if self._edit_rect is not None:
                self._paint_edit_handles(painter, rect)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Take keyboard focus so Escape cancels capture on Tool overlays."""
        super().showEvent(event)
        claim_screenshot_keyboard(self)
        self._update_snap_at(self.mapFromGlobal(QCursor.pos()))

    def _active_highlight_rect(self) -> QRect | None:
        """Return the rectangle currently shown as the clear selection / snap region."""
        if self._edit_rect is not None:
            return self._edit_rect
        if self._dragging:
            return self._selection_rect()
        if self._snap_rect is not None:
            return self._snap_rect
        return self._selection_rect()

    def _adjust_mode_enabled(self) -> bool:
        return self._panel is not None and self._panel.adjust_mode

    def _apply_edit_cursor(self, handle: HandleKind | None) -> None:
        shape_name = cursor_for_handle(handle)
        self.setCursor(getattr(Qt.CursorShape, shape_name))

    def _cancel_size_edit(self) -> None:
        self._close_size_editor()

    def _clear_edit_rect(self) -> None:
        self._close_size_editor()
        self._edit_rect = None
        self._edit_handle = None
        self._edit_press_pos = None
        self._edit_press_rect = None
        self.setCursor(Qt.CursorShape.CrossCursor)
        if self._panel is not None:
            self._panel.set_edit_keys_visible(visible=False)
        self._update_snap_at(self.mapFromGlobal(QCursor.pos()))
        self.update()

    def _clear_suppress_confirm(self) -> None:
        self._suppress_confirm_once = False

    def _close_size_editor(self) -> None:
        if self._size_edit_closing:
            return
        self._size_edit_closing = True
        try:
            self._size_edit_kind = None
            if self._size_editor.isVisible():
                self._size_editor.hide()
            if QWidget.keyboardGrabber() is self._size_editor:
                self._size_editor.releaseKeyboard()
            if self.isVisible() and QWidget.keyboardGrabber() is None:
                QTimer.singleShot(0, self._restore_overlay_keyboard)
            self.update()
        finally:
            self._size_edit_closing = False

    def _commit_size_edit(self, *, from_enter: bool = False) -> None:
        if self._size_edit_closing:
            return
        kind = self._size_edit_kind
        rect = self._edit_rect
        text = self._size_editor.text()
        if from_enter:
            self._suppress_confirm_once = True
            QTimer.singleShot(0, self._clear_suppress_confirm)
        self._close_size_editor()
        if kind is None or rect is None:
            return
        parsed = parse_size_label(text)
        if parsed is None:
            return
        self._edit_rect = resize_selection_to_size(
            rect,
            width=parsed if kind == "width" else None,
            height=parsed if kind == "height" else None,
            bounds=self.rect(),
            min_size=_MIN_SELECTION,
        )
        self.update()

    def _enter_edit_rect(self, rect: QRect) -> None:
        self._close_size_editor()
        self._edit_rect = QRect(rect)
        self._snap_rect = None
        self._origin = None
        self._current = None
        self._dragging = False
        self._snap_x_edges, self._snap_y_edges = collect_edge_guides(self._window_rects_local, self.rect())
        if self._panel is not None:
            self._panel.set_edit_keys_visible(visible=True)
        self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, self.mapFromGlobal(QCursor.pos())))
        self.update()

    def _finish_with_rect(self, rect: QRect) -> None:
        """Crop `rect` from the frozen desktop and accept the dialog."""
        self._crop = crop_pixmap_from_logical_rect(self._frozen, rect)
        if self._crop is None or self._crop.isNull():
            self._crop = None
            self.reject()
            return
        self.accept()

    def _guide_metrics(self) -> QFontMetrics:
        return QFontMetrics(guide_label_font(self.font()))

    def _hit_size_label(self, pos: QPoint) -> SizeLabelKind | None:
        if self._edit_rect is None or not self._guides_enabled:
            return None
        return hit_test_size_label(self._edit_rect, self.rect(), pos, self._guide_metrics())

    def _make_size_editor(self) -> QLineEdit:
        editor = QLineEdit(self)
        editor.hide()
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor.setMaxLength(5)
        editor.setStyleSheet(_SIZE_EDITOR_STYLE)
        editor.setFont(guide_label_font(self.font()))
        editor.editingFinished.connect(self._commit_size_edit)
        editor.installEventFilter(self)
        return editor

    def _nudge_edit_rect(self, direction: ArrowDir, modifiers: Qt.KeyboardModifier) -> None:
        if self._edit_rect is None:
            return
        step = _ARROW_STEP_SHIFT if modifiers & Qt.KeyboardModifier.ShiftModifier else _ARROW_STEP
        resize = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        self._edit_rect = nudge_selection_rect(
            self._edit_rect,
            direction,
            step=step,
            resize=resize,
            bounds=self.rect(),
            min_size=_MIN_SELECTION,
        )
        self.update()

    def _paint_edit_handles(self, painter: QPainter, rect: QRect) -> None:
        half = _HANDLE_DRAW // 2
        points = [
            rect.topLeft(),
            QPoint(rect.center().x(), rect.top()),
            rect.topRight(),
            QPoint(rect.left(), rect.center().y()),
            QPoint(rect.right(), rect.center().y()),
            rect.bottomLeft(),
            QPoint(rect.center().x(), rect.bottom()),
            rect.bottomRight(),
        ]
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_HANDLE_FILL)
        for point in points:
            painter.drawRect(point.x() - half, point.y() - half, _HANDLE_DRAW, _HANDLE_DRAW)

    def _restore_overlay_keyboard(self) -> None:
        if not self.isVisible() or self._size_editor.isVisible():
            return
        if QWidget.keyboardGrabber() is None:
            self.grabKeyboard()
            self.setFocus(Qt.FocusReason.OtherFocusReason)

    def _selection_rect(self) -> QRect | None:
        if self._origin is None or self._current is None:
            return None
        return QRect(self._origin, self._current).normalized()

    def _set_guides_enabled(self, *, enabled: bool) -> None:
        self._guides_enabled = enabled
        if not enabled:
            self._close_size_editor()
        self.update()

    def _size_editor_geometry(self, box: QRect) -> QRect:
        metrics = self._guide_metrics()
        min_width = metrics.horizontalAdvance(_SIZE_EDITOR_MIN_DIGITS) + _SIZE_EDITOR_PAD_X
        width = max(box.width() + _SIZE_EDITOR_PAD_X, min_width)
        height = max(box.height() + _SIZE_EDITOR_PAD_Y, metrics.height() + _SIZE_EDITOR_PAD_Y)
        geo = QRect(box.center().x() - width // 2, box.center().y() - height // 2, width, height)
        if geo.left() < 0:
            geo.moveLeft(0)
        if geo.top() < 0:
            geo.moveTop(0)
        if geo.right() > self.width() - 1:
            geo.moveRight(self.width() - 1)
        if geo.bottom() > self.height() - 1:
            geo.moveBottom(self.height() - 1)
        return geo

    def _size_label_box(self, kind: SizeLabelKind) -> QRect:
        if self._edit_rect is None:
            return QRect()
        width_label, height_label, _, _ = selection_guide_labels(
            self._edit_rect,
            self.rect(),
            self._guide_metrics(),
        )
        return width_label.box if kind == "width" else height_label.box

    def _start_size_edit(self, kind: SizeLabelKind) -> None:
        if self._edit_rect is None:
            return
        if self._size_editor.isVisible():
            self._commit_size_edit()
        self._size_edit_kind = kind
        value = self._edit_rect.width() if kind == "width" else self._edit_rect.height()
        max_value = self.rect().width() if kind == "width" else self.rect().height()
        self._size_editor.setValidator(QIntValidator(_MIN_SELECTION, max_value, self._size_editor))
        self._size_editor.setFont(guide_label_font(self.font()))
        self._size_editor.setGeometry(self._size_editor_geometry(self._size_label_box(kind)))
        self._size_editor.setText(str(value))
        self._size_editor.show()
        self._size_editor.raise_()
        if QWidget.keyboardGrabber() is self:
            self.releaseKeyboard()
        self._size_editor.setFocus(Qt.FocusReason.MouseFocusReason)
        self._size_editor.selectAll()
        self._size_editor.grabKeyboard()
        self.update()

    def _update_snap_at(self, pos: QPoint) -> None:
        """Refresh the hover snap rectangle for `pos` and repaint when it changes."""
        if self._edit_rect is not None:
            return
        new_snap = snap_rect_at_point(pos, self._window_rects_local)
        if new_snap == self._snap_rect:
            return
        self._snap_rect = new_snap
        self.update()


def _is_arrow_key(event: QEvent) -> bool:
    key = getattr(event, "key", None)
    return callable(key) and key() in _ARROW_KEYS


def _is_enter_key(event: QEvent) -> bool:
    key = getattr(event, "key", None)
    return callable(key) and key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}


def _is_escape_key(event: QEvent) -> bool:
    key = getattr(event, "key", None)
    return callable(key) and key() == Qt.Key.Key_Escape
