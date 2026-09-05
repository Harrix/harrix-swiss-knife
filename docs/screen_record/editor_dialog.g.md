---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `editor_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RecordingEditorWindow`](#%EF%B8%8F-class-recordingeditorwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
- [🔧 Function `show_recording_editor`](#-function-show_recording_editor)

</details>

## 🏛️ Class `RecordingEditorWindow`

```python
class RecordingEditorWindow(QMainWindow)
```

Trim, preview, and export a recorded MP4.

<details>
<summary>Code:</summary>

```python
class RecordingEditorWindow(QMainWindow):

    def __init__(self, path: Path, parent: QWidget | None = None) -> None:
        """Create an editor for `path`."""
        super().__init__(parent)
        self.setWindowTitle(f"Recording editor — {path.name}")
        self.setMinimumSize(_MIN_W, _MIN_H)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self._path = path.resolve()
        self._duration_ms = 0
        self._in_ms = 0
        self._out_ms = 0
        self._slider_dragging = False
        self._muted = False

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self._video = QVideoWidget(central)
        self._video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(self._video, stretch=1)

        self._path_label = QLabel(str(self._path), central)
        self._path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._path_label.setWordWrap(True)
        root.addWidget(self._path_label)

        self._time_label = QLabel("0:00.000 / 0:00.000", central)
        root.addWidget(self._time_label)

        self._position = QSlider(Qt.Orientation.Horizontal, central)
        self._position.setRange(0, 0)
        self._position.sliderPressed.connect(self._on_slider_pressed)
        self._position.sliderReleased.connect(self._on_slider_released)
        self._position.valueChanged.connect(self._on_slider_value_changed)
        root.addWidget(self._position)

        self._trim_label = QLabel("In: 0:00.000  —  Out: 0:00.000", central)
        root.addWidget(self._trim_label)

        transport = QHBoxLayout()
        self._play_btn = QPushButton(central)
        self._play_btn.setIcon(create_emoji_icon("▶️", _ICON))
        self._play_btn.setText("Play")
        self._play_btn.setToolTip("Play / Pause within the trim range")
        self._play_btn.clicked.connect(self._toggle_play)
        transport.addWidget(self._play_btn)

        stop_btn = make_emoji_push_button("Stop", "⏹️")
        stop_btn.setToolTip("Stop and jump to In point")
        stop_btn.clicked.connect(self._stop)
        transport.addWidget(stop_btn)

        self._mute_btn = QPushButton(central)
        self._mute_btn.setIcon(create_emoji_icon("🔊", _ICON))
        self._mute_btn.setText("Mute")
        self._mute_btn.setToolTip("Mute / unmute playback")
        self._mute_btn.clicked.connect(self._toggle_mute)
        transport.addWidget(self._mute_btn)

        transport.addSpacing(12)

        prev_btn = make_emoji_push_button("Prev", "⏮️")
        prev_btn.setToolTip("Previous frame (~33 ms)")
        prev_btn.clicked.connect(lambda: self._step_frame(-_FRAME_MS))
        transport.addWidget(prev_btn)

        next_btn = make_emoji_push_button("Next", "⏭️")
        next_btn.setToolTip("Next frame (~33 ms)")
        next_btn.clicked.connect(lambda: self._step_frame(_FRAME_MS))
        transport.addWidget(next_btn)

        set_in_btn = make_emoji_push_button("Set In", "◀️")
        set_in_btn.setToolTip("Set trim start to current position")
        set_in_btn.clicked.connect(self._set_in)
        transport.addWidget(set_in_btn)

        set_out_btn = make_emoji_push_button("Set Out", "▶️")
        set_out_btn.setToolTip("Set trim end to current position")
        set_out_btn.clicked.connect(self._set_out)
        transport.addWidget(set_out_btn)

        transport.addStretch(1)
        root.addLayout(transport)

        export_row = QHBoxLayout()
        export_row.addWidget(QLabel("Save as:", central))
        self._format = QComboBox(central)
        self._format.addItem("MP4", "mp4")
        self._format.addItem("GIF", "gif")
        self._format.addItem("AVIF", "avif")
        self._format.setToolTip("Export format")
        export_row.addWidget(self._format)

        self._remove_audio = QCheckBox("Remove audio", central)
        self._remove_audio.setToolTip("Strip audio from the exported file (always for GIF/AVIF)")
        self._remove_audio.setChecked(False)
        export_row.addWidget(self._remove_audio)

        save_btn = make_emoji_push_button("Save As…", "💾")
        save_btn.setToolTip("Export the trimmed range")
        save_btn.clicked.connect(self._save_as)
        export_row.addWidget(save_btn)

        folder_btn = make_emoji_push_button("Open folder", "📂")
        folder_btn.setToolTip("Open containing folder in Explorer")
        folder_btn.clicked.connect(self._open_folder)
        export_row.addWidget(folder_btn)

        close_btn = make_emoji_push_button("Close", "❌")
        close_btn.setToolTip("Close editor")
        close_btn.clicked.connect(self.close)
        export_row.addWidget(close_btn)
        export_row.addStretch(1)
        root.addLayout(export_row)

        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self._player.setVideoOutput(self._video)
        self._player.setSource(QUrl.fromLocalFile(str(self._path)))
        self._player.playbackStateChanged.connect(self._on_state_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.positionChanged.connect(self._on_position_changed)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop playback and clear the shared editor reference."""
        self._player.stop()
        if _editor_holder["window"] is self:
            _editor_holder["window"] = None
        super().closeEvent(event)

    def _on_duration_changed(self, duration: int) -> None:
        self._duration_ms = max(0, duration)
        self._out_ms = self._duration_ms
        self._in_ms = 0
        self._position.setRange(0, self._duration_ms)
        self._update_trim_label()
        self._update_time_label(self._player.position())

    def _on_position_changed(self, position: int) -> None:
        if not self._slider_dragging:
            self._position.blockSignals(True)  # noqa: FBT003
            self._position.setValue(position)
            self._position.blockSignals(False)  # noqa: FBT003
        self._update_time_label(position)
        if (
            self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
            and self._out_ms > 0
            and position >= self._out_ms
        ):
            self._player.pause()
            self._player.setPosition(self._out_ms)

    def _on_slider_pressed(self) -> None:
        self._slider_dragging = True

    def _on_slider_released(self) -> None:
        self._slider_dragging = False
        self._player.setPosition(self._position.value())

    def _on_slider_value_changed(self, value: int) -> None:
        if self._slider_dragging:
            self._update_time_label(value)

    def _on_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self._play_btn.setText("Pause" if playing else "Play")
        self._play_btn.setIcon(create_emoji_icon("⏸️" if playing else "▶️", _ICON))

    def _open_folder(self) -> None:
        folder = self._path.parent
        if not folder.is_dir():
            QMessageBox.warning(self, "Recording", f"Folder not found:\n{folder}")
            return
        if sys.platform == "win32":
            os.startfile(folder)  # noqa: S606
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _save_as(self) -> None:
        fmt_raw = self._format.currentData()
        fmt: ExportFormat = fmt_raw if fmt_raw in {"mp4", "gif", "avif"} else "mp4"
        default_name = f"{self._path.stem}_edit.{fmt}"
        suggested = str(self._path.with_name(default_name))
        filter_text = _FORMAT_FILTERS[fmt]
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save recording",
            suggested,
            f"{filter_text};;All files (*.*)",
        )
        if not path_str:
            return
        destination = Path(path_str)
        if destination.suffix.lower() != f".{fmt}":
            destination = destination.with_suffix(f".{fmt}")

        remove_audio = self._remove_audio.isChecked() or fmt != "mp4"
        request = ExportRequest(
            source=self._path,
            destination=destination,
            format=fmt,
            start_ms=self._in_ms,
            end_ms=self._out_ms if self._out_ms > 0 else self._duration_ms,
            remove_audio=remove_audio,
        )

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.setEnabled(False)
        try:
            result = export_recording(request)
        finally:
            self.setEnabled(True)
            QApplication.restoreOverrideCursor()

        if not result.ok:
            QMessageBox.warning(self, "Export failed", result.message or "Unknown export error")
            return
        QMessageBox.information(self, "Export", f"Saved:\n{result.path}")

    def _set_in(self) -> None:
        pos = self._player.position()
        self._in_ms = max(0, min(pos, self._out_ms - 1 if self._out_ms > 0 else pos))
        self._update_trim_label()

    def _set_out(self) -> None:
        pos = self._player.position()
        if self._duration_ms > 0:
            pos = min(pos, self._duration_ms)
        self._out_ms = max(self._in_ms + 1, pos)
        self._update_trim_label()

    def _step_frame(self, delta_ms: int) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        pos = max(0, min(self._duration_ms, self._player.position() + delta_ms))
        self._player.setPosition(pos)

    def _stop(self) -> None:
        self._player.stop()
        self._player.setPosition(self._in_ms)
        self._position.blockSignals(True)  # noqa: FBT003
        self._position.setValue(self._in_ms)
        self._position.blockSignals(False)  # noqa: FBT003
        self._update_time_label(self._in_ms)

    def _toggle_mute(self) -> None:
        self._muted = not self._muted
        self._audio.setMuted(self._muted)
        self._mute_btn.setText("Unmute" if self._muted else "Mute")
        self._mute_btn.setIcon(create_emoji_icon("🔇" if self._muted else "🔊", _ICON))

    def _toggle_play(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            return
        pos = self._player.position()
        if pos < self._in_ms or (self._out_ms > 0 and pos >= self._out_ms):
            self._player.setPosition(self._in_ms)
        self._player.play()

    def _update_time_label(self, position: int) -> None:
        self._time_label.setText(f"{_format_ms(position)} / {_format_ms(self._duration_ms)}")

    def _update_trim_label(self) -> None:
        self._trim_label.setText(f"In: {_format_ms(self._in_ms)}  —  Out: {_format_ms(self._out_ms)}")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, path: Path, parent: QWidget | None = None) -> None
```

Create an editor for `path`.

<details>
<summary>Code:</summary>

```python
def __init__(self, path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Recording editor — {path.name}")
        self.setMinimumSize(_MIN_W, _MIN_H)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self._path = path.resolve()
        self._duration_ms = 0
        self._in_ms = 0
        self._out_ms = 0
        self._slider_dragging = False
        self._muted = False

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self._video = QVideoWidget(central)
        self._video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(self._video, stretch=1)

        self._path_label = QLabel(str(self._path), central)
        self._path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._path_label.setWordWrap(True)
        root.addWidget(self._path_label)

        self._time_label = QLabel("0:00.000 / 0:00.000", central)
        root.addWidget(self._time_label)

        self._position = QSlider(Qt.Orientation.Horizontal, central)
        self._position.setRange(0, 0)
        self._position.sliderPressed.connect(self._on_slider_pressed)
        self._position.sliderReleased.connect(self._on_slider_released)
        self._position.valueChanged.connect(self._on_slider_value_changed)
        root.addWidget(self._position)

        self._trim_label = QLabel("In: 0:00.000  —  Out: 0:00.000", central)
        root.addWidget(self._trim_label)

        transport = QHBoxLayout()
        self._play_btn = QPushButton(central)
        self._play_btn.setIcon(create_emoji_icon("▶️", _ICON))
        self._play_btn.setText("Play")
        self._play_btn.setToolTip("Play / Pause within the trim range")
        self._play_btn.clicked.connect(self._toggle_play)
        transport.addWidget(self._play_btn)

        stop_btn = make_emoji_push_button("Stop", "⏹️")
        stop_btn.setToolTip("Stop and jump to In point")
        stop_btn.clicked.connect(self._stop)
        transport.addWidget(stop_btn)

        self._mute_btn = QPushButton(central)
        self._mute_btn.setIcon(create_emoji_icon("🔊", _ICON))
        self._mute_btn.setText("Mute")
        self._mute_btn.setToolTip("Mute / unmute playback")
        self._mute_btn.clicked.connect(self._toggle_mute)
        transport.addWidget(self._mute_btn)

        transport.addSpacing(12)

        prev_btn = make_emoji_push_button("Prev", "⏮️")
        prev_btn.setToolTip("Previous frame (~33 ms)")
        prev_btn.clicked.connect(lambda: self._step_frame(-_FRAME_MS))
        transport.addWidget(prev_btn)

        next_btn = make_emoji_push_button("Next", "⏭️")
        next_btn.setToolTip("Next frame (~33 ms)")
        next_btn.clicked.connect(lambda: self._step_frame(_FRAME_MS))
        transport.addWidget(next_btn)

        set_in_btn = make_emoji_push_button("Set In", "◀️")
        set_in_btn.setToolTip("Set trim start to current position")
        set_in_btn.clicked.connect(self._set_in)
        transport.addWidget(set_in_btn)

        set_out_btn = make_emoji_push_button("Set Out", "▶️")
        set_out_btn.setToolTip("Set trim end to current position")
        set_out_btn.clicked.connect(self._set_out)
        transport.addWidget(set_out_btn)

        transport.addStretch(1)
        root.addLayout(transport)

        export_row = QHBoxLayout()
        export_row.addWidget(QLabel("Save as:", central))
        self._format = QComboBox(central)
        self._format.addItem("MP4", "mp4")
        self._format.addItem("GIF", "gif")
        self._format.addItem("AVIF", "avif")
        self._format.setToolTip("Export format")
        export_row.addWidget(self._format)

        self._remove_audio = QCheckBox("Remove audio", central)
        self._remove_audio.setToolTip("Strip audio from the exported file (always for GIF/AVIF)")
        self._remove_audio.setChecked(False)
        export_row.addWidget(self._remove_audio)

        save_btn = make_emoji_push_button("Save As…", "💾")
        save_btn.setToolTip("Export the trimmed range")
        save_btn.clicked.connect(self._save_as)
        export_row.addWidget(save_btn)

        folder_btn = make_emoji_push_button("Open folder", "📂")
        folder_btn.setToolTip("Open containing folder in Explorer")
        folder_btn.clicked.connect(self._open_folder)
        export_row.addWidget(folder_btn)

        close_btn = make_emoji_push_button("Close", "❌")
        close_btn.setToolTip("Close editor")
        close_btn.clicked.connect(self.close)
        export_row.addWidget(close_btn)
        export_row.addStretch(1)
        root.addLayout(export_row)

        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self._player.setVideoOutput(self._video)
        self._player.setSource(QUrl.fromLocalFile(str(self._path)))
        self._player.playbackStateChanged.connect(self._on_state_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.positionChanged.connect(self._on_position_changed)
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Stop playback and clear the shared editor reference.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._player.stop()
        if _editor_holder["window"] is self:
            _editor_holder["window"] = None
        super().closeEvent(event)
```

</details>

## 🔧 Function `show_recording_editor`

```python
def show_recording_editor(path: Path) -> RecordingEditorWindow
```

Show `path` in the shared recording editor window.

<details>
<summary>Code:</summary>

```python
def show_recording_editor(path: Path) -> RecordingEditorWindow:
    previous = _editor_holder["window"]
    if previous is not None and isValid(previous):
        previous.close()
    if not path.is_file() or path.stat().st_size <= 0:
        msg = f"Recording file is missing or empty:\n{path}"
        raise FileNotFoundError(msg)
    window = RecordingEditorWindow(path)
    _editor_holder["window"] = window
    window.show()
    window.raise_()
    window.activateWindow()
    return window
```

</details>
