"""Stay-on-top recording frame: move/resize region, countdown, start/stop."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIntValidator, QPainter, QPainterPath, QPalette, QPen, QRegion
from PySide6.QtMultimedia import QAudioDevice
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from harrix_swiss_knife.apps.common.audio_recording.pcm_utils import audio_device_id
from harrix_swiss_knife.apps.common.audio_recording.recorder import MicrophoneRecorder
from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
from harrix_swiss_knife.qt_frameless_window import frameless_stay_on_top_flags
from harrix_swiss_knife.screen_record.config import (
    SCREEN_RECORD_AUDIO_MODES,
    ScreenRecordAudio,
    ensure_screen_record_config_defaults,
    get_screen_record_audio,
    get_screen_record_countdown_seconds,
    get_screen_record_microphone_id,
    save_screen_record_settings,
)
from harrix_swiss_knife.screenshot.selection_edit import (
    HandleKind,
    collect_edge_guides,
    cursor_for_handle,
    hit_test_selection_handle,
    resize_selection_to_size,
    snap_rect_to_edges,
    transform_selection_rect,
)
from harrix_swiss_knife.screenshot.selection_guides import (
    SizeLabelKind,
    guide_label_font,
    parse_size_label,
    place_height_label_right,
    place_width_label,
)
from harrix_swiss_knife.screenshot.window_rects import list_snappable_window_rects
from harrix_swiss_knife.screenshot.window_visibility import mark_screenshot_ui

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent, QKeyEvent, QMouseEvent, QPaintEvent, QResizeEvent, QShowEvent

_BORDER = 4
_HANDLE = 8
_MOVE_HANDLE_SIZE = 12
_TOOLBAR_GAP = 16
_TOOLBAR_H = 48
_MIN_REGION = 32
_ICON = 20
_TOOLBAR_SIDE_PAD = 8
_INNER_TOOLBAR_MARGIN = 8
_EDGE_SNAP_THRESHOLD = 8
_LABEL_GAP = 6
_SIZE_HIT_PADDING = 6
_SIZE_EDITOR_PAD_X = 12
_SIZE_EDITOR_PAD_Y = 4
_SIZE_EDITOR_MIN_DIGITS = "00000"
_LABEL_COLOR = QColor(230, 230, 230, 240)
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
_AUDIO_LABELS: dict[str, str] = {
    "none": "No audio",
    "mic": "Microphone",
    "system": "System audio",
    "mic_and_system": "Mic + system",
}
_TOOLBAR_STYLE = """
#recordToolbar {
    background-color: rgba(30, 30, 30, 230);
    border-radius: 8px;
}
QPushButton {
    background-color: rgba(50, 50, 50, 220);
    border: 1px solid #888;
    border-radius: 6px;
    min-width: 36px;
    min-height: 32px;
    padding: 2px 6px;
    color: white;
}
QPushButton:hover {
    background-color: rgba(80, 80, 80, 245);
    border: 1px solid #ccc;
}
QPushButton:pressed {
    background-color: rgba(30, 30, 30, 245);
    border: 1px solid #fff;
}
QPushButton:disabled {
    color: #888;
    background-color: rgba(40, 40, 40, 180);
    border: 1px solid #555;
}
QComboBox {
    min-width: 110px;
    max-width: 180px;
    color: white;
    background-color: #333;
    border: 1px solid #888;
    border-radius: 4px;
    padding: 4px 8px;
}
QComboBox:hover {
    background-color: #444;
    border: 1px solid #ccc;
}
QComboBox:on {
    background-color: #3a3a3a;
    border: 1px solid #aaa;
}
QComboBox#recordMicCombo {
    min-width: 140px;
    max-width: 220px;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
"""

_COMBO_POPUP_STYLE = """
QAbstractItemView {
    background-color: #2a2a2a;
    color: #ffffff;
    border: 1px solid #666;
    outline: 0;
    padding: 2px;
}
QAbstractItemView::item {
    min-height: 26px;
    padding: 4px 10px;
    color: #ffffff;
    background-color: #2a2a2a;
}
QAbstractItemView::item:hover {
    background-color: #3a7ca5;
    color: #ffffff;
}
QAbstractItemView::item:selected {
    background-color: #2f6a8f;
    color: #ffffff;
}
QAbstractItemView::item:selected:hover {
    background-color: #3a7ca5;
    color: #ffffff;
}
"""


def hit_test_record_frame_handle(
    rect: QRect,
    pos: QPoint,
    *,
    handle_size: int = _HANDLE,
    border: int = _BORDER,
) -> HandleKind | None:
    """Return the frame handle under `pos`. The top-left corner moves the region."""
    grip = max(handle_size, _MOVE_HANDLE_SIZE // 2)
    nw = QRect(rect.left() - grip, rect.top() - grip, grip * 2, grip * 2)
    if nw.contains(pos):
        return "move"
    handle = hit_test_selection_handle(rect, pos, handle_size=handle_size)
    if handle is None:
        ring = rect.adjusted(-border, -border, border, border)
        if ring.contains(pos) and not rect.contains(pos):
            return "move"
    return handle


class RecordFrameWindow(QWidget):
    """Hollow border around a recording region with a toolbar under it."""

    start_requested = Signal(object)  # ScreenRecordAudio
    stop_requested = Signal()
    abort_requested = Signal()
    region_changed = Signal(QRect)

    def __init__(self, region: QRect, parent: QWidget | None = None) -> None:
        """Create a frame for `region` (global logical coordinates)."""
        super().__init__(parent)
        mark_screenshot_ui(self)
        ensure_screen_record_config_defaults()
        self.setWindowFlags(frameless_stay_on_top_flags() | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, on=True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._region = QRect(region)
        self._left_pad = 0
        self._top_pad = 0
        self._right_pad = 0
        self._toolbar_inside = False
        self._locked = False
        self._drag_handle: HandleKind | None = None
        self._press_pos: QPoint | None = None
        self._press_region: QRect | None = None
        self._countdown_left = 0
        self._recording = False
        self._elapsed_ms = 0
        self._snap_x_edges: list[int] = []
        self._snap_y_edges: list[int] = []
        self._size_edit_kind: SizeLabelKind | None = None
        self._size_edit_closing = False
        self._size_editor = self._make_size_editor()

        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._on_countdown_tick)
        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.setInterval(250)
        self._elapsed_timer.timeout.connect(self._on_elapsed_tick)

        self._countdown_overlay = _CountdownOverlay()

        self._status = QLabel(self)
        self._status.setStyleSheet("color: white; font-weight: bold; padding: 0 4px;")
        self._status.setToolTip("Recording status")

        self._audio = _DarkComboBox(self)
        self._audio.setToolTip("Audio source for the recording (saved in config-temp.json)")
        for mode in ("none", "mic", "system", "mic_and_system"):
            self._audio.addItem(_AUDIO_LABELS[mode], mode)
        current = get_screen_record_audio()
        index = self._audio.findData(current)
        self._audio.blockSignals(True)  # noqa: FBT003
        if index >= 0:
            self._audio.setCurrentIndex(index)
        self._audio.blockSignals(False)  # noqa: FBT003
        self._audio.currentIndexChanged.connect(self._on_audio_changed)
        _prepare_combo_popup(self._audio)

        self._mic = _DarkComboBox(self)
        self._mic.setObjectName("recordMicCombo")
        self._mic.setToolTip("Microphone (saved in config.json)")
        self._populate_microphones()
        self._mic.currentIndexChanged.connect(self._on_mic_changed)
        _prepare_combo_popup(self._mic)

        countdown = get_screen_record_countdown_seconds()
        self._record_btn = self._make_tool_button("⏺️", "Record now (start immediately)")
        self._record_btn.clicked.connect(self._on_record_now)
        self._countdown_btn = self._make_tool_button(
            "⏱️",
            f"Countdown {countdown}s then record",
            text=str(countdown) if countdown else "0",
        )
        self._countdown_btn.clicked.connect(self._on_countdown_start)
        self._stop_btn = self._make_tool_button("⏹️", "Stop recording and open editor")
        self._stop_btn.clicked.connect(self.stop_requested.emit)
        self._abort_btn = self._make_tool_button("❌", "Abort without saving")
        self._abort_btn.clicked.connect(self.abort_requested.emit)

        bar = QWidget(self)
        bar.setObjectName("recordToolbar")
        bar.setCursor(Qt.CursorShape.ArrowCursor)
        bar.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, on=True)
        bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        bar.setStyleSheet(_TOOLBAR_STYLE)
        row = QHBoxLayout(bar)
        row.setContentsMargins(8, 6, 8, 6)
        row.setSpacing(6)
        row.addWidget(self._status)
        row.addWidget(self._audio)
        row.addWidget(self._mic)
        row.addWidget(self._record_btn)
        row.addWidget(self._countdown_btn)
        row.addWidget(self._stop_btn)
        row.addWidget(self._abort_btn)
        self._toolbar = bar
        self._toolbar_filter = _ToolbarCursorFilter(self)
        bar.installEventFilter(self._toolbar_filter)
        for child in bar.findChildren(QWidget):
            if isinstance(child, QPushButton):
                child.setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                child.setCursor(Qt.CursorShape.ArrowCursor)
            child.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, on=True)
            child.installEventFilter(self._toolbar_filter)

        self._status.setText("Ready")
        self._status.setToolTip("Ready — drag top-left to move, other handles to resize")
        self._update_idle_controls(visible=True)
        self._update_mic_visibility()
        self._refresh_snap_guides()
        self._apply_geometry()

    def cancel_countdown(self) -> None:
        """Stop a pending countdown without starting capture."""
        self._countdown_timer.stop()
        self._countdown_left = 0
        self._countdown_overlay.hide_countdown()
        if not self._recording:
            self._update_idle_controls(visible=True)
            self._status.setText("Ready")
            self._status.setToolTip("Ready — drag top-left to move, other handles to resize")

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Hide the countdown overlay with the frame."""
        self._close_size_editor()
        self._countdown_overlay.hide_countdown()
        self._countdown_overlay.close()
        super().closeEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Escape cancels a typed size; Enter applies it."""
        if watched is self._size_editor and event.type() == QEvent.Type.KeyPress:
            key_event = cast("QKeyEvent", event)
            if key_event.key() == Qt.Key.Key_Escape:
                self._cancel_size_edit()
                return True
            if key_event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
                self._commit_size_edit()
                return True
        return super().eventFilter(watched, event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Edit width/height when double-clicking the size labels."""
        if self._locked or event.button() != Qt.MouseButton.LeftButton:
            event.accept()
            return
        pos = event.position().toPoint()
        if self._is_over_toolbar(pos):
            event.ignore()
            return
        kind = self._hit_size_label(pos)
        if kind is not None:
            self._start_size_edit(kind)
            event.accept()
            return
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Drag move/resize the region (with window edge snap), or update cursor."""
        if self._locked:
            event.accept()
            return
        pos = event.position().toPoint()
        if self._is_over_toolbar(pos):
            self.unsetCursor()
            event.ignore()
            return
        if self._size_editor.isVisible():
            event.accept()
            return
        if self._drag_handle is not None and self._press_pos is not None and self._press_region is not None:
            bounds = self._virtual_bounds()
            if self._drag_handle == "move":
                delta = event.globalPosition().toPoint() - self._press_pos
                moved = self._press_region.translated(delta)
                moved.moveLeft(max(bounds.left(), min(moved.left(), bounds.right() - moved.width() + 1)))
                moved.moveTop(max(bounds.top(), min(moved.top(), bounds.bottom() - moved.height() + 1)))
                snapped = snap_rect_to_edges(
                    moved,
                    "move",
                    self._snap_x_edges,
                    self._snap_y_edges,
                    threshold=_EDGE_SNAP_THRESHOLD,
                    bounds=bounds,
                    min_size=_MIN_REGION,
                )
                self._set_region(snapped)
            else:
                new_rect = transform_selection_rect(
                    self._press_region,
                    self._drag_handle,
                    self._press_pos,
                    event.globalPosition().toPoint(),
                    bounds=bounds,
                    min_size=_MIN_REGION,
                )
                snapped = snap_rect_to_edges(
                    new_rect,
                    self._drag_handle,
                    self._snap_x_edges,
                    self._snap_y_edges,
                    threshold=_EDGE_SNAP_THRESHOLD,
                    bounds=bounds,
                    min_size=_MIN_REGION,
                )
                self._set_region(snapped)
            event.accept()
            return
        if self._hit_size_label(pos) is not None:
            self.setCursor(Qt.CursorShape.IBeamCursor)
            event.accept()
            return
        handle = hit_test_record_frame_handle(self._region_local_rect(), pos)
        self.setCursor(getattr(Qt.CursorShape, cursor_for_handle(handle)) if handle else Qt.CursorShape.ArrowCursor)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Begin move/resize from a border handle."""
        if self._locked or event.button() != Qt.MouseButton.LeftButton:
            event.accept()
            return
        pos = event.position().toPoint()
        if self._is_over_toolbar(pos):
            event.ignore()
            return
        if self._size_editor.isVisible():
            if self._size_editor.geometry().contains(pos):
                event.accept()
                return
            self._commit_size_edit()
            event.accept()
            return
        if self._hit_size_label(pos) is not None:
            event.accept()
            return
        handle = hit_test_record_frame_handle(self._region_local_rect(), pos)
        if handle is None:
            event.accept()
            return
        self._refresh_snap_guides()
        self._drag_handle = handle
        self._press_pos = event.globalPosition().toPoint()
        self._press_region = QRect(self._region)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """End move/resize."""
        if self._is_over_toolbar(event.position().toPoint()):
            self._drag_handle = None
            self._press_pos = None
            self._press_region = None
            event.ignore()
            return
        self._drag_handle = None
        self._press_pos = None
        self._press_region = None
        event.accept()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        """Draw the recording border, handles, and size labels."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        rect = self._region_local_rect()
        color = QColor(220, 40, 40) if self._recording else QColor(0, 174, 255)
        pen = QPen(color, _BORDER)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rect.adjusted(-_BORDER // 2, -_BORDER // 2, _BORDER // 2, _BORDER // 2))
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        for box in self._handle_boxes():
            painter.drawRect(box)
        if not self._recording:
            painter.setFont(guide_label_font(self.font()))
            for kind, box, text in self._size_label_entries():
                if self._size_edit_kind == kind and self._size_editor.isVisible():
                    continue
                painter.setPen(_LABEL_COLOR)
                painter.drawText(box, Qt.AlignmentFlag.AlignCenter, text)
        painter.end()

    @property
    def region(self) -> QRect:
        """Current recording rectangle in global logical coordinates."""
        return QRect(self._region)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep the click-through hole and toolbar aligned."""
        super().resizeEvent(event)
        self._layout_toolbar()
        self._update_mask()
        if self._countdown_overlay.isVisible():
            self._countdown_overlay.place_over(self._region)

    def set_recording(self, *, active: bool) -> None:
        """Update UI for recording vs idle."""
        self._recording = active
        self._locked = active
        self._close_size_editor()
        self._countdown_overlay.hide_countdown()
        self._update_idle_controls(visible=not active)
        self._stop_btn.setVisible(active)
        self._stop_btn.setEnabled(active)
        if active:
            self._elapsed_ms = 0
            self._elapsed_timer.start()
            self._status.setText("00:00")
            self._status.setToolTip("Recording in progress")
        else:
            self._elapsed_timer.stop()
            self._status.setText("Ready")
            self._status.setToolTip("Ready — drag top-left to move, other handles to resize")
        self._apply_geometry()

    def set_status(self, text: str) -> None:
        """Replace the status label text."""
        self._status.setText(text)
        self._status.setToolTip(text)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Finalize toolbar geometry after the first layout pass."""
        super().showEvent(event)
        self._layout_toolbar()
        self._update_mask()
        self._refresh_snap_guides()

    def _apply_geometry(self) -> None:
        self._toolbar.adjustSize()
        hint = self._toolbar.sizeHint()
        toolbar_h = max(hint.height(), _TOOLBAR_H - 4)
        toolbar_w = max(hint.width(), 200) + _TOOLBAR_SIDE_PAD * 2
        metrics = self._guide_metrics()
        desired_top = metrics.height() + _LABEL_GAP + 4
        desired_right = metrics.horizontalAdvance(_SIZE_EDITOR_MIN_DIGITS) + _LABEL_GAP + 4
        bounds = self._virtual_bounds()

        base_w = self._region.width() + _BORDER * 2 + desired_right
        win_w = max(base_w, toolbar_w)
        self._left_pad = max(0, (win_w - base_w) // 2)
        self._right_pad = desired_right
        self._toolbar_inside = not self._toolbar_fits_below(toolbar_h)
        win_h = desired_top + self._region.height() + _BORDER * 2
        if not self._toolbar_inside:
            win_h += _TOOLBAR_GAP + toolbar_h

        geo_x = self._region.x() - _BORDER - self._left_pad
        geo_y = max(self._region.y() - _BORDER - desired_top, bounds.top())
        self._top_pad = max(0, self._region.y() - _BORDER - geo_y)

        if geo_x + win_w - 1 > bounds.right():
            overflow = geo_x + win_w - 1 - bounds.right()
            self._right_pad = max(0, self._right_pad - overflow)
            win_w = max(self._region.width() + _BORDER * 2 + self._right_pad, toolbar_w)
            self._left_pad = max(0, (win_w - (self._region.width() + _BORDER * 2 + self._right_pad)) // 2)
            geo_x = self._region.x() - _BORDER - self._left_pad

        win_h = self._top_pad + self._region.height() + _BORDER * 2
        if not self._toolbar_inside:
            win_h += _TOOLBAR_GAP + toolbar_h

        self.setGeometry(QRect(geo_x, geo_y, win_w, win_h))
        self._layout_toolbar()
        self._update_mask()
        if self._countdown_overlay.isVisible():
            self._countdown_overlay.place_over(self._region)
        if self._size_editor.isVisible() and self._size_edit_kind is not None:
            box = next(
                (entry[1] for entry in self._size_label_entries() if entry[0] == self._size_edit_kind),
                QRect(),
            )
            self._size_editor.setGeometry(self._size_editor_geometry(box))
            self._size_editor.raise_()

    def _cancel_size_edit(self) -> None:
        self._close_size_editor()

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
            self.update()
        finally:
            self._size_edit_closing = False

    def _commit_size_edit(self) -> None:
        if self._size_edit_closing:
            return
        kind = self._size_edit_kind
        text = self._size_editor.text()
        self._close_size_editor()
        if kind is None:
            return
        parsed = parse_size_label(text)
        if parsed is None:
            return
        new_region = resize_selection_to_size(
            self._region,
            width=parsed if kind == "width" else None,
            height=parsed if kind == "height" else None,
            bounds=self._virtual_bounds(),
            min_size=_MIN_REGION,
        )
        self._set_region(new_region)

    def _current_audio(self) -> ScreenRecordAudio:
        data = self._audio.currentData()
        mode = str(data) if data is not None else "none"
        if mode in SCREEN_RECORD_AUDIO_MODES:
            return cast("ScreenRecordAudio", mode)
        return "none"

    def _exclude_hwnds(self) -> list[int]:
        handles: list[int] = []
        for widget in (self, self._countdown_overlay):
            try:
                handle = int(widget.winId())
            except RuntimeError:
                continue
            if handle:
                handles.append(handle)
        return handles

    def _guide_metrics(self) -> QFontMetrics:
        return QFontMetrics(guide_label_font(self.font()))

    def _handle_boxes(self) -> list[QRect]:
        rect = self._region_local_rect()
        half = _HANDLE // 2
        move_half = _MOVE_HANDLE_SIZE // 2
        boxes = [
            QRect(
                rect.left() - move_half,
                rect.top() - move_half,
                _MOVE_HANDLE_SIZE,
                _MOVE_HANDLE_SIZE,
            ),
        ]
        for hx, hy in (
            (rect.center().x(), rect.top()),
            (rect.right(), rect.top()),
            (rect.left(), rect.center().y()),
            (rect.right(), rect.center().y()),
            (rect.left(), rect.bottom()),
            (rect.center().x(), rect.bottom()),
            (rect.right(), rect.bottom()),
        ):
            boxes.append(QRect(hx - half, hy - half, _HANDLE, _HANDLE))
        return boxes

    def _hit_size_label(self, pos: QPoint) -> SizeLabelKind | None:
        if self._recording or self._locked:
            return None
        for kind, box, _text in self._size_label_entries():
            if box.adjusted(-_SIZE_HIT_PADDING, -_SIZE_HIT_PADDING, _SIZE_HIT_PADDING, _SIZE_HIT_PADDING).contains(pos):
                return kind
        return None

    def _is_over_toolbar(self, pos: QPoint) -> bool:
        return self._toolbar.geometry().contains(pos)

    def _layout_toolbar(self) -> None:
        self._toolbar.adjustSize()
        hint = self._toolbar.sizeHint()
        width = min(max(hint.width(), 160), max(160, self.width() - _TOOLBAR_SIDE_PAD * 2))
        height = max(hint.height(), _TOOLBAR_H - 4)
        x = max(0, (self.width() - width) // 2)
        region = self._region_local_rect()
        if self._toolbar_inside:
            y = region.bottom() - height - _INNER_TOOLBAR_MARGIN + 1
            y = max(region.top() + _INNER_TOOLBAR_MARGIN, y)
        else:
            y = region.bottom() + _BORDER + _TOOLBAR_GAP + 1
        self._toolbar.setGeometry(x, y, width, height)
        self._toolbar.raise_()

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

    def _make_tool_button(self, emoji: str, tip: str, *, text: str = "") -> QPushButton:
        button = QPushButton(self)
        button.setIcon(create_emoji_icon(emoji, _ICON))
        button.setIconSize(QSize(_ICON, _ICON))
        button.setToolTip(tip)
        button.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        if text:
            button.setText(text)
        return button

    def _needs_microphone(self) -> bool:
        return self._current_audio() in {"mic", "mic_and_system"}

    def _on_audio_changed(self, _index: int) -> None:
        mode = self._current_audio()
        save_screen_record_settings(audio=mode)
        self._update_mic_visibility()
        self._apply_geometry()

    def _on_countdown_start(self) -> None:
        seconds = get_screen_record_countdown_seconds()
        if seconds <= 0:
            self._on_record_now()
            return
        self._close_size_editor()
        self._record_btn.setEnabled(False)
        self._countdown_btn.setEnabled(False)
        self._audio.setEnabled(False)
        self._mic.setEnabled(False)
        self._countdown_left = seconds
        self._status.setText("Countdown")
        self._status.setToolTip(f"Starting in {self._countdown_left}s")
        self._countdown_overlay.show_number(self._countdown_left, self._region)
        self._countdown_timer.start()

    def _on_countdown_tick(self) -> None:
        self._countdown_left -= 1
        if self._countdown_left <= 0:
            self._countdown_timer.stop()
            self._countdown_overlay.hide_countdown()
            self._persist_current_mic()
            self.start_requested.emit(self._current_audio())
            return
        self._status.setToolTip(f"Starting in {self._countdown_left}s")
        self._countdown_overlay.show_number(self._countdown_left, self._region)

    def _on_elapsed_tick(self) -> None:
        self._elapsed_ms += 250
        total = self._elapsed_ms // 1000
        self._status.setText(f"{total // 60:02d}:{total % 60:02d}")

    def _on_mic_changed(self, _index: int) -> None:
        device = self._mic.currentData()
        if isinstance(device, QAudioDevice):
            save_screen_record_settings(microphone_id=audio_device_id(device))

    def _on_record_now(self) -> None:
        self._countdown_timer.stop()
        self._countdown_overlay.hide_countdown()
        self._close_size_editor()
        self._persist_current_mic()
        self.start_requested.emit(self._current_audio())

    def _persist_current_mic(self) -> None:
        if not self._needs_microphone():
            return
        device = self._mic.currentData()
        if isinstance(device, QAudioDevice):
            save_screen_record_settings(microphone_id=audio_device_id(device))

    def _populate_microphones(self) -> None:
        self._mic.blockSignals(True)  # noqa: FBT003
        self._mic.clear()
        devices = MicrophoneRecorder.list_input_devices()
        if not devices:
            self._mic.addItem("No microphone found")
            self._mic.setEnabled(False)
            self._mic.blockSignals(False)  # noqa: FBT003
            return
        saved_id = get_screen_record_microphone_id()
        selected = 0
        for index, device in enumerate(devices):
            self._mic.addItem(device.description(), device)
            if saved_id and audio_device_id(device) == saved_id:
                selected = index
        self._mic.setCurrentIndex(selected)
        self._mic.setEnabled(True)
        self._mic.blockSignals(False)  # noqa: FBT003

    def _refresh_snap_guides(self) -> None:
        bounds = self._virtual_bounds()
        rects = list_snappable_window_rects(exclude_hwnds=self._exclude_hwnds())
        self._snap_x_edges, self._snap_y_edges = collect_edge_guides(rects, bounds)

    def _region_local_rect(self) -> QRect:
        return QRect(
            _BORDER + self._left_pad,
            _BORDER + self._top_pad,
            self._region.width(),
            self._region.height(),
        )

    def _set_region(self, region: QRect) -> None:
        if region.width() < _MIN_REGION or region.height() < _MIN_REGION:
            return
        self._region = QRect(region)
        self._apply_geometry()
        self.region_changed.emit(self._region)

    def _size_editor_geometry(self, box: QRect) -> QRect:
        metrics = self._guide_metrics()
        min_width = metrics.horizontalAdvance(_SIZE_EDITOR_MIN_DIGITS) + _SIZE_EDITOR_PAD_X
        width = max(box.width() + _SIZE_EDITOR_PAD_X, min_width)
        height = max(box.height() + _SIZE_EDITOR_PAD_Y, metrics.height() + _SIZE_EDITOR_PAD_Y)
        geo = QRect(box.center().x() - width // 2, box.center().y() - height // 2, width, height)
        area = self.rect()
        if geo.left() < area.left():
            geo.moveLeft(area.left())
        if geo.top() < area.top():
            geo.moveTop(area.top())
        if geo.right() > area.right():
            geo.moveRight(area.right())
        if geo.bottom() > area.bottom():
            geo.moveBottom(area.bottom())
        return geo

    def _size_label_entries(self) -> list[tuple[SizeLabelKind, QRect, str]]:
        rect = self._region_local_rect()
        bounds = self.rect()
        metrics = self._guide_metrics()
        width_text = str(self._region.width())
        height_text = str(self._region.height())
        width_box, _ = place_width_label(
            rect,
            bounds,
            text_width=metrics.horizontalAdvance(width_text),
            text_height=metrics.height(),
            gap=_LABEL_GAP,
        )
        height_box, _ = place_height_label_right(
            rect,
            bounds,
            text_width=metrics.horizontalAdvance(height_text),
            text_height=metrics.height(),
            gap=_LABEL_GAP,
        )
        return [("width", width_box, width_text), ("height", height_box, height_text)]

    def _start_size_edit(self, kind: SizeLabelKind) -> None:
        if self._recording or self._locked:
            return
        if self._size_editor.isVisible():
            self._commit_size_edit()
        self._size_edit_kind = kind
        value = self._region.width() if kind == "width" else self._region.height()
        bounds = self._virtual_bounds()
        max_value = bounds.width() if kind == "width" else bounds.height()
        self._size_editor.setValidator(QIntValidator(_MIN_REGION, max_value, self._size_editor))
        self._size_editor.setFont(guide_label_font(self.font()))
        box = next((entry[1] for entry in self._size_label_entries() if entry[0] == kind), QRect())
        self._size_editor.setGeometry(self._size_editor_geometry(box))
        self._size_editor.setText(str(value))
        self._size_editor.show()
        self._size_editor.raise_()
        self._size_editor.setFocus(Qt.FocusReason.MouseFocusReason)
        self._size_editor.selectAll()
        self._size_editor.grabKeyboard()
        self.update()

    def _toolbar_fits_below(self, toolbar_h: int) -> bool:
        """Return whether the toolbar fits under the region on the virtual desktop."""
        bounds = self._virtual_bounds()
        return self._region.bottom() + _TOOLBAR_GAP + toolbar_h <= bounds.bottom()

    def _update_idle_controls(self, *, visible: bool) -> None:
        self._audio.setVisible(visible)
        self._record_btn.setVisible(visible)
        self._countdown_btn.setVisible(visible)
        self._audio.setEnabled(visible)
        self._record_btn.setEnabled(visible)
        self._countdown_btn.setEnabled(visible)
        self._stop_btn.setVisible(not visible)
        self._stop_btn.setEnabled(not visible)
        self._update_mic_visibility()

    def _update_mask(self) -> None:
        """Leave a click-through hole inside the border; keep toolbar and size labels."""
        full = QRegion(self.rect())
        hole = QRegion(self._region_local_rect())
        toolbar = QRegion(self._toolbar.geometry())
        labels = QRegion()
        for _kind, box, _text in self._size_label_entries():
            labels = labels.united(
                QRegion(box.adjusted(-_SIZE_HIT_PADDING, -_SIZE_HIT_PADDING, _SIZE_HIT_PADDING, _SIZE_HIT_PADDING))
            )
        if self._size_editor.isVisible():
            labels = labels.united(QRegion(self._size_editor.geometry()))
        handles = QRegion()
        for box in self._handle_boxes():
            handles = handles.united(QRegion(box))
        self.setMask(full.subtracted(hole).united(toolbar).united(labels).united(handles))

    def _update_mic_visibility(self) -> None:
        show = (not self._recording) and self._needs_microphone() and self._audio.isVisible()
        self._mic.setVisible(show)
        self._mic.setEnabled(show and self._mic.count() > 0 and self._mic.itemData(0) is not None)

    def _virtual_bounds(self) -> QRect:
        app = QApplication.instance()
        if app is None:
            return self._region
        screen = app.primaryScreen()
        if screen is None:
            return self._region
        return screen.virtualGeometry()


class _CountdownOverlay(QWidget):
    """Large white countdown digits with a gray outline, centered in the region."""

    def __init__(self) -> None:
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(frameless_stay_on_top_flags() | Qt.WindowType.Tool | Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._number = 0

    def hide_countdown(self) -> None:
        """Hide the overlay."""
        self.hide()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        """Draw outlined countdown digits."""
        if self._number <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        text = str(self._number)
        side = min(self.width(), self.height())
        pixel = max(48, int(side * 0.55))
        font = QFont()
        font.setBold(True)
        font.setPixelSize(pixel)
        path = QPainterPath()
        # Baseline roughly centered; Qt text path uses baseline y.
        metrics_ascent = int(pixel * 0.75)
        x = (self.width() - pixel * max(1, len(text)) * 0.6) / 2
        y = (self.height() + metrics_ascent) / 2
        path.addText(x, y, font, text)
        # Center the path geometrically.
        bounds = path.boundingRect()
        path.translate(
            (self.width() - bounds.width()) / 2 - bounds.left(),
            (self.height() - bounds.height()) / 2 - bounds.top(),
        )
        outline = QPen(QColor(110, 110, 110), max(4, pixel // 18))
        outline.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.strokePath(path, outline)
        painter.fillPath(path, QColor(255, 255, 255))
        painter.end()

    def place_over(self, region: QRect) -> None:
        """Center the overlay on `region` (global logical coordinates)."""
        if region.isEmpty():
            return
        side = max(80, min(region.width(), region.height(), 280))
        geo = QRect(0, 0, side, side)
        geo.moveCenter(region.center())
        self.setGeometry(geo)

    def show_number(self, number: int, region: QRect) -> None:
        """Show `number` centered over `region`."""
        self._number = max(0, number)
        self.place_over(region)
        self.show()
        self.raise_()
        self.update()


class _DarkComboBox(QComboBox):
    """Combo whose popup stays dark (avoids a white flash over a translucent parent)."""

    def showPopup(self) -> None:  # noqa: N802
        """Force an opaque dark popup before it becomes visible."""
        view = self.view()
        view.setStyleSheet(_COMBO_POPUP_STYLE)
        view.setAutoFillBackground(True)
        popup = view.window()
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=False)
        popup.setStyleSheet("background-color: #2a2a2a; color: #ffffff;")
        super().showPopup()
        # Re-apply after Qt creates the native popup window.
        popup = view.window()
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=False)
        popup.setStyleSheet("background-color: #2a2a2a; color: #ffffff;")
        view.setStyleSheet(_COMBO_POPUP_STYLE)


class _ToolbarCursorFilter(QObject):
    """Keep the arrow cursor on the toolbar and clear the parent resize cursor."""

    def __init__(self, frame: RecordFrameWindow) -> None:
        super().__init__(frame)
        self._frame = frame

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() in {QEvent.Type.Enter, QEvent.Type.HoverEnter, QEvent.Type.MouseMove}:
            self._frame.unsetCursor()
            if isinstance(watched, QWidget):
                if isinstance(watched, QPushButton):
                    watched.setCursor(Qt.CursorShape.PointingHandCursor)
                else:
                    watched.setCursor(Qt.CursorShape.ArrowCursor)
        return False


def _prepare_combo_popup(combo: QComboBox) -> None:
    """Apply a dark palette/stylesheet so the list never flashes white."""
    view = combo.view()
    view.setStyleSheet(_COMBO_POPUP_STYLE)
    view.setAutoFillBackground(True)
    view.setMouseTracking(True)
    palette = view.palette()
    palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Window, QColor(42, 42, 42))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(58, 124, 165))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(42, 42, 42))
    view.setPalette(palette)
    combo.setPalette(palette)
