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
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `region (property)`](#%EF%B8%8F-method-region-property)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `set_recording`](#%EF%B8%8F-method-set_recording)
  - [⚙️ Method `set_status`](#%EF%B8%8F-method-set_status)

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
        self.setWindowFlags(frameless_stay_on_top_flags() | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._region = QRect(region)
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
        self._status.setStyleSheet("color: white; font-weight: bold; padding: 0 6px;")

        self._audio = QComboBox(self)
        for mode in ("none", "mic", "system", "mic_and_system"):
            self._audio.addItem(_AUDIO_LABELS[mode], mode)
        current = get_screen_record_audio()
        index = self._audio.findData(current)
        if index >= 0:
            self._audio.setCurrentIndex(index)
        self._audio.currentIndexChanged.connect(self._on_audio_changed)

        self._record_btn = QPushButton(self)
        self._record_btn.setIcon(create_emoji_icon("⏺️", _ICON))
        self._record_btn.setIconSize(QSize(_ICON, _ICON))
        self._record_btn.setToolTip("Record now")
        self._record_btn.clicked.connect(self._on_record_now)

        countdown = get_screen_record_countdown_seconds()
        self._countdown_btn = QPushButton(self)
        self._countdown_btn.setIcon(create_emoji_icon("⏱️", _ICON))
        self._countdown_btn.setIconSize(QSize(_ICON, _ICON))
        self._countdown_btn.setToolTip(f"Countdown {countdown}s then record")
        self._countdown_btn.setText(str(countdown) if countdown else "0")
        self._countdown_btn.clicked.connect(self._on_countdown_start)

        self._stop_btn = QPushButton(self)
        self._stop_btn.setIcon(create_emoji_icon("⏹️", _ICON))
        self._stop_btn.setIconSize(QSize(_ICON, _ICON))
        self._stop_btn.setToolTip("Stop and save")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self.stop_requested.emit)

        self._abort_btn = QPushButton(self)
        self._abort_btn.setIcon(create_emoji_icon("❌", _ICON))
        self._abort_btn.setIconSize(QSize(_ICON, _ICON))
        self._abort_btn.setToolTip("Abort")
        self._abort_btn.clicked.connect(self.abort_requested.emit)

        bar = QWidget(self)
        bar.setObjectName("recordToolbar")
        bar.setStyleSheet(
            "#recordToolbar { background-color: rgba(30,30,30,230); border-radius: 8px; }"
            "QPushButton { background: rgba(50,50,50,220); border: 1px solid #888; "
            "border-radius: 6px; min-width: 36px; min-height: 32px; color: white; }"
            "QComboBox { min-width: 120px; color: white; background: #333; }"
        )
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

        root = QVBoxLayout(self)
        root.setContentsMargins(_BORDER, _BORDER, _BORDER, _BORDER)
        root.addStretch(1)
        root.addWidget(bar, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._status.setText("Ready — move/resize frame, then record")
        self._apply_geometry()
        self._update_mask()

    def cancel_countdown(self) -> None:
        """Stop a pending countdown without starting capture."""
        self._countdown_timer.stop()
        self._countdown_left = 0
        self._record_btn.setEnabled(True)
        self._countdown_btn.setEnabled(True)
        self._audio.setEnabled(True)
        if not self._recording:
            self._status.setText("Ready — move/resize frame, then record")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Drag move/resize the region, or update the resize cursor."""
        if self._locked:
            event.accept()
            return
        pos = event.position().toPoint()
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
            QRect(_BORDER, _BORDER, self._region.width(), self._region.height()),
            pos,
            handle_size=_HANDLE,
        )
        if handle is None:
            inner = QRect(_BORDER, _BORDER, self._region.width(), self._region.height())
            if not inner.contains(pos):
                handle = "move"
        self.setCursor(getattr(Qt.CursorShape, cursor_for_handle(handle)) if handle else Qt.CursorShape.ArrowCursor)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Begin move/resize from a border handle."""
        if self._locked or event.button() != Qt.MouseButton.LeftButton:
            event.accept()
            return
        pos = event.position().toPoint()
        handle = hit_test_selection_handle(
            QRect(_BORDER, _BORDER, self._region.width(), self._region.height()),
            pos,
            handle_size=_HANDLE,
        )
        if handle is None and self._toolbar.geometry().contains(pos):
            event.ignore()
            return
        if handle is None:
            # Drag from border ring → move
            inner = QRect(_BORDER, _BORDER, self._region.width(), self._region.height())
            if not inner.contains(pos):
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
        self._drag_handle = None
        self._press_pos = None
        self._press_region = None
        event.accept()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        """Draw the recording border and handles."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        rect = QRect(_BORDER, _BORDER, self._region.width(), self._region.height())
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
        """Keep the click-through hole aligned with the region."""
        super().resizeEvent(event)
        self._update_mask()

    def set_recording(self, *, active: bool) -> None:
        """Update UI for recording vs idle."""
        self._recording = active
        self._locked = active
        self._record_btn.setEnabled(not active)
        self._countdown_btn.setEnabled(not active)
        self._audio.setEnabled(not active)
        self._stop_btn.setEnabled(active)
        if active:
            self._elapsed_ms = 0
            self._elapsed_timer.start()
            self._status.setText("Recording 00:00")
        else:
            self._elapsed_timer.stop()
            self._status.setText("Ready — move/resize frame, then record")

    def set_status(self, text: str) -> None:
        """Replace the status label text."""
        self._status.setText(text)

    def _apply_geometry(self) -> None:
        geo = QRect(
            self._region.x() - _BORDER,
            self._region.y() - _BORDER,
            self._region.width() + _BORDER * 2,
            self._region.height() + _BORDER * 2 + _TOOLBAR_H,
        )
        self.setGeometry(geo)
        self._update_mask()

    def _current_audio(self) -> ScreenRecordAudio:
        data = self._audio.currentData()
        mode = str(data) if data is not None else "none"
        if mode in SCREEN_RECORD_AUDIO_MODES:
            return cast("ScreenRecordAudio", mode)
        return "none"

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
        self._status.setText(f"Starting in {self._countdown_left}…")
        self._countdown_timer.start()

    def _on_countdown_tick(self) -> None:
        self._countdown_left -= 1
        if self._countdown_left <= 0:
            self._countdown_timer.stop()
            self.start_requested.emit(self._current_audio())
            return
        self._status.setText(f"Starting in {self._countdown_left}…")

    def _on_elapsed_tick(self) -> None:
        self._elapsed_ms += 250
        total = self._elapsed_ms // 1000
        self._status.setText(f"Recording {total // 60:02d}:{total % 60:02d}")

    def _on_record_now(self) -> None:
        self._countdown_timer.stop()
        self.start_requested.emit(self._current_audio())

    def _set_region(self, region: QRect) -> None:
        if region.width() < _MIN_REGION or region.height() < _MIN_REGION:
            return
        self._region = QRect(region)
        self._apply_geometry()
        self.region_changed.emit(self._region)

    def _update_mask(self) -> None:
        """Leave a click-through hole inside the border; keep toolbar clickable."""
        full = QRegion(self.rect())
        hole = QRegion(
            QRect(_BORDER, _BORDER, max(1, self._region.width()), max(1, self._region.height())),
        )
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
        self.setWindowFlags(frameless_stay_on_top_flags() | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._region = QRect(region)
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
        self._status.setStyleSheet("color: white; font-weight: bold; padding: 0 6px;")

        self._audio = QComboBox(self)
        for mode in ("none", "mic", "system", "mic_and_system"):
            self._audio.addItem(_AUDIO_LABELS[mode], mode)
        current = get_screen_record_audio()
        index = self._audio.findData(current)
        if index >= 0:
            self._audio.setCurrentIndex(index)
        self._audio.currentIndexChanged.connect(self._on_audio_changed)

        self._record_btn = QPushButton(self)
        self._record_btn.setIcon(create_emoji_icon("⏺️", _ICON))
        self._record_btn.setIconSize(QSize(_ICON, _ICON))
        self._record_btn.setToolTip("Record now")
        self._record_btn.clicked.connect(self._on_record_now)

        countdown = get_screen_record_countdown_seconds()
        self._countdown_btn = QPushButton(self)
        self._countdown_btn.setIcon(create_emoji_icon("⏱️", _ICON))
        self._countdown_btn.setIconSize(QSize(_ICON, _ICON))
        self._countdown_btn.setToolTip(f"Countdown {countdown}s then record")
        self._countdown_btn.setText(str(countdown) if countdown else "0")
        self._countdown_btn.clicked.connect(self._on_countdown_start)

        self._stop_btn = QPushButton(self)
        self._stop_btn.setIcon(create_emoji_icon("⏹️", _ICON))
        self._stop_btn.setIconSize(QSize(_ICON, _ICON))
        self._stop_btn.setToolTip("Stop and save")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self.stop_requested.emit)

        self._abort_btn = QPushButton(self)
        self._abort_btn.setIcon(create_emoji_icon("❌", _ICON))
        self._abort_btn.setIconSize(QSize(_ICON, _ICON))
        self._abort_btn.setToolTip("Abort")
        self._abort_btn.clicked.connect(self.abort_requested.emit)

        bar = QWidget(self)
        bar.setObjectName("recordToolbar")
        bar.setStyleSheet(
            "#recordToolbar { background-color: rgba(30,30,30,230); border-radius: 8px; }"
            "QPushButton { background: rgba(50,50,50,220); border: 1px solid #888; "
            "border-radius: 6px; min-width: 36px; min-height: 32px; color: white; }"
            "QComboBox { min-width: 120px; color: white; background: #333; }"
        )
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

        root = QVBoxLayout(self)
        root.setContentsMargins(_BORDER, _BORDER, _BORDER, _BORDER)
        root.addStretch(1)
        root.addWidget(bar, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._status.setText("Ready — move/resize frame, then record")
        self._apply_geometry()
        self._update_mask()
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
        self._record_btn.setEnabled(True)
        self._countdown_btn.setEnabled(True)
        self._audio.setEnabled(True)
        if not self._recording:
            self._status.setText("Ready — move/resize frame, then record")
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Drag move/resize the region, or update the resize cursor.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._locked:
            event.accept()
            return
        pos = event.position().toPoint()
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
            QRect(_BORDER, _BORDER, self._region.width(), self._region.height()),
            pos,
            handle_size=_HANDLE,
        )
        if handle is None:
            inner = QRect(_BORDER, _BORDER, self._region.width(), self._region.height())
            if not inner.contains(pos):
                handle = "move"
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
        handle = hit_test_selection_handle(
            QRect(_BORDER, _BORDER, self._region.width(), self._region.height()),
            pos,
            handle_size=_HANDLE,
        )
        if handle is None and self._toolbar.geometry().contains(pos):
            event.ignore()
            return
        if handle is None:
            # Drag from border ring → move
            inner = QRect(_BORDER, _BORDER, self._region.width(), self._region.height())
            if not inner.contains(pos):
                handle = "move"
        if handle is None:
            event.accept()
            return
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

Draw the recording border and handles.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        rect = QRect(_BORDER, _BORDER, self._region.width(), self._region.height())
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

Keep the click-through hole aligned with the region.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._update_mask()
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
        self._record_btn.setEnabled(not active)
        self._countdown_btn.setEnabled(not active)
        self._audio.setEnabled(not active)
        self._stop_btn.setEnabled(active)
        if active:
            self._elapsed_ms = 0
            self._elapsed_timer.start()
            self._status.setText("Recording 00:00")
        else:
            self._elapsed_timer.stop()
            self._status.setText("Ready — move/resize frame, then record")
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
```

</details>
