"""Stay-on-top recording frame: move/resize region, countdown, start/stop."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QRegion
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
from harrix_swiss_knife.qt_frameless_window import frameless_stay_on_top_flags
from harrix_swiss_knife.screen_record.config import (
    SCREEN_RECORD_AUDIO_MODES,
    ScreenRecordAudio,
    get_screen_record_audio,
    get_screen_record_countdown_seconds,
    save_screen_record_settings,
)
from harrix_swiss_knife.screenshot.selection_edit import (
    HandleKind,
    cursor_for_handle,
    hit_test_selection_handle,
    transform_selection_rect,
)
from harrix_swiss_knife.screenshot.window_visibility import mark_screenshot_ui

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent, QPaintEvent, QResizeEvent, QShowEvent

_BORDER = 4
_HANDLE = 8
_TOOLBAR_GAP = 16
_TOOLBAR_H = 48
_MIN_REGION = 32
_ICON = 20
_TOOLBAR_SIDE_PAD = 8
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
    background: rgba(50, 50, 50, 220);
    border: 1px solid #888;
    border-radius: 6px;
    min-width: 36px;
    min-height: 32px;
    color: white;
}
QComboBox {
    min-width: 110px;
    max-width: 140px;
    color: white;
    background: #333;
    border: 1px solid #888;
    border-radius: 4px;
    padding: 4px 8px;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #2a2a2a;
    color: white;
    selection-background-color: #3a7ca5;
    selection-color: white;
    border: 1px solid #666;
    outline: 0;
}
"""


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
        self.setWindowFlags(frameless_stay_on_top_flags() | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, on=True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._region = QRect(region)
        self._left_pad = 0
        self._locked = False
        self._drag_handle: HandleKind | None = None
        self._press_pos: QPoint | None = None
        self._press_region: QRect | None = None
        self._countdown_left = 0
        self._recording = False
        self._elapsed_ms = 0

        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._on_countdown_tick)
        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.setInterval(250)
        self._elapsed_timer.timeout.connect(self._on_elapsed_tick)

        self._status = QLabel(self)
        self._status.setStyleSheet("color: white; font-weight: bold; padding: 0 4px;")
        self._status.setToolTip("Recording status")

        self._audio = QComboBox(self)
        self._audio.setToolTip("Audio source for the recording")
        for mode in ("none", "mic", "system", "mic_and_system"):
            self._audio.addItem(_AUDIO_LABELS[mode], mode)
        current = get_screen_record_audio()
        index = self._audio.findData(current)
        if index >= 0:
            self._audio.setCurrentIndex(index)
        self._audio.currentIndexChanged.connect(self._on_audio_changed)

        countdown = get_screen_record_countdown_seconds()
        self._record_btn = self._make_tool_button("⏺️", "Record now (start immediately)")
        self._record_btn.clicked.connect(self._on_record_now)
        self._countdown_btn = self._make_tool_button(
            "⏱️",
            f"Countdown {countdown}s then record",
            text=str(countdown) if countdown else "0",
        )
        self._countdown_btn.clicked.connect(self._on_countdown_start)
        self._stop_btn = self._make_tool_button("⏹️", "Stop recording and open preview")
        self._stop_btn.clicked.connect(self.stop_requested.emit)
        self._abort_btn = self._make_tool_button("❌", "Abort without saving")
        self._abort_btn.clicked.connect(self.abort_requested.emit)

        bar = QWidget(self)
        bar.setObjectName("recordToolbar")
        bar.setCursor(Qt.CursorShape.ArrowCursor)
        bar.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, on=True)
        bar.setStyleSheet(_TOOLBAR_STYLE)
        row = QHBoxLayout(bar)
        row.setContentsMargins(8, 6, 8, 6)
        row.setSpacing(6)
        row.addWidget(self._status)
        row.addWidget(self._audio)
        row.addWidget(self._record_btn)
        row.addWidget(self._countdown_btn)
        row.addWidget(self._stop_btn)
        row.addWidget(self._abort_btn)
        self._toolbar = bar
        self._toolbar_filter = _ToolbarCursorFilter(self)
        bar.installEventFilter(self._toolbar_filter)
        for child in bar.findChildren(QWidget):
            child.setCursor(Qt.CursorShape.ArrowCursor)
            child.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, on=True)
            child.installEventFilter(self._toolbar_filter)

        self._status.setText("Ready")
        self._status.setToolTip("Ready — move/resize frame, then record")
        self._update_idle_controls(visible=True)
        self._apply_geometry()

    def cancel_countdown(self) -> None:
        """Stop a pending countdown without starting capture."""
        self._countdown_timer.stop()
        self._countdown_left = 0
        if not self._recording:
            self._update_idle_controls(visible=True)
            self._status.setText("Ready")
            self._status.setToolTip("Ready — move/resize frame, then record")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Drag move/resize the region, or update the resize cursor."""
        if self._locked:
            event.accept()
            return
        pos = event.position().toPoint()
        if self._is_over_toolbar(pos):
            self.unsetCursor()
            event.ignore()
            return
        if self._drag_handle is not None and self._press_pos is not None and self._press_region is not None:
            bounds = self._virtual_bounds()
            if self._drag_handle == "move":
                delta = event.globalPosition().toPoint() - self._press_pos
                moved = self._press_region.translated(delta)
                moved.moveLeft(max(bounds.left(), min(moved.left(), bounds.right() - moved.width() + 1)))
                moved.moveTop(max(bounds.top(), min(moved.top(), bounds.bottom() - moved.height() + 1)))
                self._set_region(moved)
            else:
                new_rect = transform_selection_rect(
                    self._press_region,
                    self._drag_handle,
                    self._press_pos,
                    event.globalPosition().toPoint(),
                    bounds=bounds,
                    min_size=_MIN_REGION,
                )
                self._set_region(new_rect)
            event.accept()
            return
        handle = hit_test_selection_handle(
            self._region_local_rect(),
            pos,
            handle_size=_HANDLE,
        )
        if handle is None:
            ring = self._border_ring_rect()
            if ring.contains(pos) and not self._region_local_rect().contains(pos):
                handle = "move"
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
        handle = hit_test_selection_handle(
            self._region_local_rect(),
            pos,
            handle_size=_HANDLE,
        )
        if handle is None:
            ring = self._border_ring_rect()
            if ring.contains(pos) and not self._region_local_rect().contains(pos):
                handle = "move"
        if handle is None:
            event.accept()
            return
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
        """Draw the recording border and handles."""
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
        half = _HANDLE // 2
        for hx, hy in (
            (rect.left(), rect.top()),
            (rect.center().x(), rect.top()),
            (rect.right(), rect.top()),
            (rect.left(), rect.center().y()),
            (rect.right(), rect.center().y()),
            (rect.left(), rect.bottom()),
            (rect.center().x(), rect.bottom()),
            (rect.right(), rect.bottom()),
        ):
            painter.drawRect(hx - half, hy - half, _HANDLE, _HANDLE)
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

    def set_recording(self, *, active: bool) -> None:
        """Update UI for recording vs idle."""
        self._recording = active
        self._locked = active
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
            self._status.setToolTip("Ready — move/resize frame, then record")
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

    def _apply_geometry(self) -> None:
        self._toolbar.adjustSize()
        toolbar_w = max(self._toolbar.sizeHint().width(), 200) + _TOOLBAR_SIDE_PAD * 2
        content_w = self._region.width() + _BORDER * 2
        win_w = max(content_w, toolbar_w)
        self._left_pad = max(0, (win_w - content_w) // 2)
        geo = QRect(
            self._region.x() - _BORDER - self._left_pad,
            self._region.y() - _BORDER,
            win_w,
            self._region.height() + _BORDER * 2 + _TOOLBAR_GAP + _TOOLBAR_H,
        )
        self.setGeometry(geo)
        self._layout_toolbar()
        self._update_mask()

    def _border_ring_rect(self) -> QRect:
        """Outer rectangle covering the border around the region (not the toolbar)."""
        local = self._region_local_rect()
        return local.adjusted(-_BORDER, -_BORDER, _BORDER, _BORDER)

    def _current_audio(self) -> ScreenRecordAudio:
        data = self._audio.currentData()
        mode = str(data) if data is not None else "none"
        if mode in SCREEN_RECORD_AUDIO_MODES:
            return cast("ScreenRecordAudio", mode)
        return "none"

    def _is_over_toolbar(self, pos: QPoint) -> bool:
        return self._toolbar.geometry().contains(pos)

    def _layout_toolbar(self) -> None:
        self._toolbar.adjustSize()
        hint = self._toolbar.sizeHint()
        width = min(max(hint.width(), 160), max(160, self.width() - _TOOLBAR_SIDE_PAD * 2))
        height = max(hint.height(), _TOOLBAR_H - 4)
        x = max(0, (self.width() - width) // 2)
        y = _BORDER + self._region.height() + _BORDER + _TOOLBAR_GAP
        self._toolbar.setGeometry(x, y, width, height)
        self._toolbar.raise_()

    def _make_tool_button(self, emoji: str, tip: str, *, text: str = "") -> QPushButton:
        button = QPushButton(self)
        button.setIcon(create_emoji_icon(emoji, _ICON))
        button.setIconSize(QSize(_ICON, _ICON))
        button.setToolTip(tip)
        button.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        if text:
            button.setText(text)
        return button

    def _on_audio_changed(self, _index: int) -> None:
        mode = self._current_audio()
        save_screen_record_settings(audio=mode)

    def _on_countdown_start(self) -> None:
        seconds = get_screen_record_countdown_seconds()
        if seconds <= 0:
            self._on_record_now()
            return
        self._record_btn.setEnabled(False)
        self._countdown_btn.setEnabled(False)
        self._audio.setEnabled(False)
        self._countdown_left = seconds
        self._status.setText(f"{self._countdown_left}…")
        self._status.setToolTip(f"Starting in {self._countdown_left}s")
        self._countdown_timer.start()

    def _on_countdown_tick(self) -> None:
        self._countdown_left -= 1
        if self._countdown_left <= 0:
            self._countdown_timer.stop()
            self.start_requested.emit(self._current_audio())
            return
        self._status.setText(f"{self._countdown_left}…")
        self._status.setToolTip(f"Starting in {self._countdown_left}s")

    def _on_elapsed_tick(self) -> None:
        self._elapsed_ms += 250
        total = self._elapsed_ms // 1000
        self._status.setText(f"{total // 60:02d}:{total % 60:02d}")

    def _on_record_now(self) -> None:
        self._countdown_timer.stop()
        self.start_requested.emit(self._current_audio())

    def _region_local_rect(self) -> QRect:
        return QRect(_BORDER + self._left_pad, _BORDER, self._region.width(), self._region.height())

    def _set_region(self, region: QRect) -> None:
        if region.width() < _MIN_REGION or region.height() < _MIN_REGION:
            return
        self._region = QRect(region)
        self._apply_geometry()
        self.region_changed.emit(self._region)

    def _update_idle_controls(self, *, visible: bool) -> None:
        self._audio.setVisible(visible)
        self._record_btn.setVisible(visible)
        self._countdown_btn.setVisible(visible)
        self._audio.setEnabled(visible)
        self._record_btn.setEnabled(visible)
        self._countdown_btn.setEnabled(visible)
        self._stop_btn.setVisible(not visible)
        self._stop_btn.setEnabled(not visible)

    def _update_mask(self) -> None:
        """Leave a click-through hole inside the border; keep toolbar clickable."""
        full = QRegion(self.rect())
        hole = QRegion(self._region_local_rect())
        toolbar = QRegion(self._toolbar.geometry())
        self.setMask(full.subtracted(hole).united(toolbar))

    def _virtual_bounds(self) -> QRect:
        app = QApplication.instance()
        if app is None:
            return self._region
        screen = app.primaryScreen()
        if screen is None:
            return self._region
        return screen.virtualGeometry()


class _ToolbarCursorFilter(QObject):
    """Keep the arrow cursor on the toolbar and clear the parent resize cursor."""

    def __init__(self, frame: RecordFrameWindow) -> None:
        super().__init__(frame)
        self._frame = frame

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() in {QEvent.Type.Enter, QEvent.Type.HoverEnter, QEvent.Type.MouseMove}:
            self._frame.unsetCursor()
            if isinstance(watched, QWidget):
                watched.setCursor(Qt.CursorShape.ArrowCursor)
        return False
