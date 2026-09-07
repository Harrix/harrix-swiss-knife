---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `record_frame.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RecordFrameWindow`](#%EF%B8%8F-class-recordframewindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `cancel_countdown`](#%EF%B8%8F-method-cancel_countdown)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `mouseDoubleClickEvent`](#%EF%B8%8F-method-mousedoubleclickevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `region (property)`](#%EF%B8%8F-method-region-property)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `set_recording`](#%EF%B8%8F-method-set_recording)
  - [⚙️ Method `set_status`](#%EF%B8%8F-method-set_status)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)
- [🔧 Function `hit_test_record_frame_handle`](#-function-hit_test_record_frame_handle)

</details>

## 🏛️ Class `RecordFrameWindow`

```python
class RecordFrameWindow(QWidget)
```

Hollow border around a recording region with a toolbar under it.

<details>
<summary>Code:</summary>

```python
class RecordFrameWindow(QWidget):

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
        self._record_btn = self._make_tool_button(
            "circle-dot",
            "Record now (start immediately)",
            color=_RECORD_ICON_COLOR,
        )
        self._record_btn.clicked.connect(self._on_record_now)
        self._countdown_btn = self._make_tool_button(
            "timer",
            f"Countdown {countdown}s then record",
            text=str(countdown) if countdown else "0",
        )
        self._countdown_btn.clicked.connect(self._on_countdown_start)
        self._stop_btn = self._make_tool_button(
            "square-stop",
            "Stop recording and open editor",
            color=_STOP_ICON_COLOR,
        )
        self._stop_btn.clicked.connect(self.stop_requested.emit)
        self._abort_btn = self._make_tool_button("x", "Abort without saving")
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

    def _make_tool_button(
        self,
        name: str,
        tip: str,
        *,
        text: str = "",
        color: QColor | None = None,
    ) -> QPushButton:
        button = QPushButton(self)
        button.setIcon(create_lucide_icon(name, _ICON, color=color))
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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, region: QRect, parent: QWidget | None = None) -> None
```

Create a frame for [`region`](#%EF%B8%8F-method-region-property) (global logical coordinates).

<details>
<summary>Code:</summary>

```python
def __init__(self, region: QRect, parent: QWidget | None = None) -> None:
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
        self._record_btn = self._make_tool_button(
            "circle-dot",
            "Record now (start immediately)",
            color=_RECORD_ICON_COLOR,
        )
        self._record_btn.clicked.connect(self._on_record_now)
        self._countdown_btn = self._make_tool_button(
            "timer",
            f"Countdown {countdown}s then record",
            text=str(countdown) if countdown else "0",
        )
        self._countdown_btn.clicked.connect(self._on_countdown_start)
        self._stop_btn = self._make_tool_button(
            "square-stop",
            "Stop recording and open editor",
            color=_STOP_ICON_COLOR,
        )
        self._stop_btn.clicked.connect(self.stop_requested.emit)
        self._abort_btn = self._make_tool_button("x", "Abort without saving")
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
```

</details>

### ⚙️ Method `cancel_countdown`

```python
def cancel_countdown(self) -> None
```

Stop a pending countdown without starting capture.

<details>
<summary>Code:</summary>

```python
def cancel_countdown(self) -> None:
        self._countdown_timer.stop()
        self._countdown_left = 0
        self._countdown_overlay.hide_countdown()
        if not self._recording:
            self._update_idle_controls(visible=True)
            self._status.setText("Ready")
            self._status.setToolTip("Ready — drag top-left to move, other handles to resize")
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Hide the countdown overlay with the frame.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._close_size_editor()
        self._countdown_overlay.hide_countdown()
        self._countdown_overlay.close()
        super().closeEvent(event)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Escape cancels a typed size; Enter applies it.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._size_editor and event.type() == QEvent.Type.KeyPress:
            key_event = cast("QKeyEvent", event)
            if key_event.key() == Qt.Key.Key_Escape:
                self._cancel_size_edit()
                return True
            if key_event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
                self._commit_size_edit()
                return True
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `mouseDoubleClickEvent`

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None
```

Edit width/height when double-clicking the size labels.

<details>
<summary>Code:</summary>

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
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
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Drag move/resize the region (with window edge snap), or update cursor.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
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
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Begin move/resize from a border handle.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
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
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

End move/resize.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
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
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Draw the recording border, handles, and size labels.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
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
```

</details>

### ⚙️ Method `region (property)`

```python
def region(self) -> QRect
```

Current recording rectangle in global logical coordinates.

<details>
<summary>Code:</summary>

```python
def region(self) -> QRect:
        return QRect(self._region)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Keep the click-through hole and toolbar aligned.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._layout_toolbar()
        self._update_mask()
        if self._countdown_overlay.isVisible():
            self._countdown_overlay.place_over(self._region)
```

</details>

### ⚙️ Method `set_recording`

```python
def set_recording(self, *, active: bool) -> None
```

Update UI for recording vs idle.

<details>
<summary>Code:</summary>

```python
def set_recording(self, *, active: bool) -> None:
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
```

</details>

### ⚙️ Method `set_status`

```python
def set_status(self, text: str) -> None
```

Replace the status label text.

<details>
<summary>Code:</summary>

```python
def set_status(self, text: str) -> None:
        self._status.setText(text)
        self._status.setToolTip(text)
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Finalize toolbar geometry after the first layout pass.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self._layout_toolbar()
        self._update_mask()
        self._refresh_snap_guides()
```

</details>

## 🔧 Function `hit_test_record_frame_handle`

```python
def hit_test_record_frame_handle(rect: QRect, pos: QPoint, *, handle_size: int = _HANDLE, border: int = _BORDER) -> HandleKind | None
```

Return the frame handle under `pos`. The top-left corner moves the region.

<details>
<summary>Code:</summary>

```python
def hit_test_record_frame_handle(
    rect: QRect,
    pos: QPoint,
    *,
    handle_size: int = _HANDLE,
    border: int = _BORDER,
) -> HandleKind | None:
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
```

</details>
