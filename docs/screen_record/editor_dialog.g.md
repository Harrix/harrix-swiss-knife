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
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._path = path.resolve()
        self._duration_ms = 0
        self._in_ms = 0
        self._out_ms = 0
        self._slider_dragging = False
        self._muted = False
        self._initial_frame_ready = False
        self._scrub_pending_ms: int | None = None
        self._wanted_frame_ms: int | None = None
        self._grab_for_ms: int | None = None
        self._frame_source: QPixmap | None = None
        self._scrub_timer = QTimer(self)
        self._scrub_timer.setSingleShot(True)
        self._scrub_timer.setInterval(_SCRUB_INTERVAL_MS)
        self._scrub_timer.timeout.connect(self._flush_scrub_seek)

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self._preview_stack = QStackedWidget(central)
        self._preview_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._video = QVideoWidget(self._preview_stack)
        self._video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._frame_label = QLabel(self._preview_stack)
        self._frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._frame_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._frame_label.setMinimumSize(1, 1)
        self._frame_label.setStyleSheet("QLabel { background-color: #111; color: #aaa; }")
        self._frame_label.setText("Loading frame…")
        self._preview_stack.addWidget(self._video)
        self._preview_stack.addWidget(self._frame_label)
        self._preview_stack.setCurrentIndex(_STACK_FRAME)
        root.addWidget(self._preview_stack, stretch=1)

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

        self._trim_label = QLabel("Keep: 0:00.000 → 0:00.000", central)
        root.addWidget(self._trim_label)

        transport = QHBoxLayout()
        self._play_btn = QPushButton(central)
        self._play_btn.setIcon(create_lucide_icon("play", _ICON))
        self._play_btn.setText("Play")
        self._play_btn.setToolTip("Play / Pause (Space)")
        self._play_btn.clicked.connect(self._toggle_play)
        transport.addWidget(self._play_btn)

        stop_btn = make_lucide_push_button("Stop", "square-stop")
        stop_btn.setToolTip("Stop and jump to the start of the kept range")
        stop_btn.clicked.connect(self._stop)
        transport.addWidget(stop_btn)

        self._mute_btn = QPushButton(central)
        self._mute_btn.setIcon(create_lucide_icon("volume-2", _ICON))
        self._mute_btn.setText("Mute")
        self._mute_btn.setToolTip("Mute / unmute playback")
        self._mute_btn.clicked.connect(self._toggle_mute)
        transport.addWidget(self._mute_btn)

        transport.addSpacing(12)

        prev_btn = make_lucide_push_button("Prev frame", "skip-back")
        prev_btn.setToolTip("Previous frame (~33 ms)")
        prev_btn.clicked.connect(lambda: self._step_frame(-_FRAME_MS))
        transport.addWidget(prev_btn)

        next_btn = make_lucide_push_button("Next frame", "skip-forward")
        next_btn.setToolTip("Next frame (~33 ms)")
        next_btn.clicked.connect(lambda: self._step_frame(_FRAME_MS))
        transport.addWidget(next_btn)

        delete_left_btn = make_lucide_push_button("Delete left", "scissors")
        delete_left_btn.setToolTip("Remove everything before the playhead (CapCut-style)")
        delete_left_btn.clicked.connect(self._delete_left)
        transport.addWidget(delete_left_btn)

        delete_right_btn = make_lucide_push_button("Delete right", "scissors")
        delete_right_btn.setToolTip("Remove everything after the playhead (CapCut-style)")
        delete_right_btn.clicked.connect(self._delete_right)
        transport.addWidget(delete_right_btn)

        transport.addStretch(1)
        root.addLayout(transport)

        export_row = QHBoxLayout()
        export_row.addWidget(QLabel("Save as:", central))
        self._format = QComboBox(central)
        self._format.addItem("MP4", "mp4")
        self._format.addItem("GIF", "gif")
        self._format.addItem("AVIF", "avif")
        self._format.addItem("AVIF optimized", "avif_optimized")
        self._format.setToolTip(
            "Export format. AVIF optimized uses the same pipeline as Images → Optimize (ffmpeg + avifenc)."
        )
        export_row.addWidget(self._format)

        self._remove_audio = QCheckBox("Remove audio", central)
        self._remove_audio.setToolTip("Strip audio from the exported file (always for GIF/AVIF)")
        self._remove_audio.setChecked(False)
        export_row.addWidget(self._remove_audio)

        save_btn = make_lucide_push_button("Save As…", "save")
        save_btn.setToolTip("Export the kept (trimmed) range")
        save_btn.clicked.connect(self._save_as)
        export_row.addWidget(save_btn)

        folder_btn = make_lucide_push_button("Open folder", "folder-open")
        folder_btn.setToolTip("Open containing folder in Explorer")
        folder_btn.clicked.connect(self._open_folder)
        export_row.addWidget(folder_btn)

        close_btn = make_lucide_push_button("Close", "x")
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
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.positionChanged.connect(self._on_position_changed)

        self._grab_process = QProcess(self)
        self._grab_process.finished.connect(self._on_frame_grab_finished)

        space = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        space.setContext(Qt.ShortcutContext.WindowShortcut)
        space.activated.connect(self._toggle_play)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop playback and clear the shared editor reference."""
        self._scrub_timer.stop()
        self._wanted_frame_ms = None
        if self._grab_process.state() != QProcess.ProcessState.NotRunning:
            self._grab_process.kill()
            self._grab_process.waitForFinished(500)
        self._player.stop()
        if _editor_holder["window"] is self:
            _editor_holder["window"] = None
        super().closeEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep the scrub pixmap fitted when the window is resized."""
        super().resizeEvent(event)
        self._refit_frame_pixmap()

    def _apply_scrub_now(self) -> None:
        if self._scrub_pending_ms is None:
            return
        target = self._scrub_pending_ms
        self._scrub_pending_ms = None
        self._seek_preview(target)
        self._scrub_timer.start()

    def _clamp_position(self, position_ms: int) -> int:
        lo = max(0, self._in_ms)
        hi = self._out_ms if self._out_ms > 0 else self._duration_ms
        if self._duration_ms > 0:
            hi = min(hi, self._duration_ms)
        # Stay slightly before the true end so backends keep a visible last frame.
        if hi > lo:
            hi = max(lo, hi - 1)
        return max(lo, min(position_ms, hi))

    def _delete_left(self) -> None:
        """Discard everything before the playhead; jump to the new start."""
        pos = self._clamp_position(self._position.value() if self._slider_dragging else self._player.position())
        if self._out_ms > 0 and pos >= self._out_ms:
            pos = max(self._in_ms, self._out_ms - 1)
        self._in_ms = max(0, pos)
        self._sync_slider_range()
        self._update_trim_label()
        self._seek_to(self._in_ms)

    def _delete_right(self) -> None:
        """Discard everything after the playhead; jump to the new end."""
        pos = self._clamp_position(self._position.value() if self._slider_dragging else self._player.position())
        self._out_ms = max(self._in_ms + 1, pos if pos > self._in_ms else self._in_ms + 1)
        if self._duration_ms > 0:
            self._out_ms = min(self._out_ms, self._duration_ms)
        self._sync_slider_range()
        self._update_trim_label()
        self._seek_to(self._out_ms)

    def _flush_scrub_seek(self) -> None:
        """Apply the latest scrub position after the throttle cooldown."""
        if not self._slider_dragging or self._scrub_pending_ms is None:
            return
        self._apply_scrub_now()

    def _keep_end_ms(self) -> int:
        if self._out_ms > 0:
            return self._out_ms
        return self._duration_ms

    def _on_duration_changed(self, duration: int) -> None:
        self._duration_ms = max(0, duration)
        self._out_ms = self._duration_ms
        self._in_ms = 0
        self._sync_slider_range()
        self._update_trim_label()
        self._update_time_label(self._player.position())
        if self._duration_ms > 0:
            self._show_initial_frame()

    def _on_frame_grab_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        jpeg = self._grab_process.readAllStandardOutput()
        grabbed_ms = self._grab_for_ms
        self._grab_for_ms = None
        if exit_code == 0 and not jpeg.isEmpty() and grabbed_ms is not None:
            pixmap = QPixmap()
            if pixmap.loadFromData(jpeg, "JPG"):  # ty: ignore[no-matching-overload]
                self._frame_source = pixmap
                self._frame_label.setText("")
                self._refit_frame_pixmap()
                if self._player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                    self._preview_stack.setCurrentIndex(_STACK_FRAME)

        wanted = self._wanted_frame_ms
        if wanted is not None and wanted != grabbed_ms:
            self._start_frame_grab(wanted)

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status in {
            QMediaPlayer.MediaStatus.LoadedMedia,
            QMediaPlayer.MediaStatus.BufferedMedia,
        }:
            self._show_initial_frame()
            return
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._seek_to(self._keep_end_ms())

    def _on_position_changed(self, position: int) -> None:
        if not self._slider_dragging:
            self._position.blockSignals(True)  # noqa: FBT003
            self._position.setValue(self._clamp_position(position))
            self._position.blockSignals(False)  # noqa: FBT003
            self._update_time_label(position)
        if (
            self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
            and self._keep_end_ms() > 0
            and position >= self._keep_end_ms()
        ):
            self._seek_to(self._keep_end_ms())

    def _on_slider_pressed(self) -> None:
        self._slider_dragging = True
        self._scrub_pending_ms = None
        self._scrub_timer.stop()
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        self._preview_stack.setCurrentIndex(_STACK_FRAME)

    def _on_slider_released(self) -> None:
        self._scrub_timer.stop()
        pending = self._scrub_pending_ms
        self._scrub_pending_ms = None
        self._slider_dragging = False
        self._seek_to(pending if pending is not None else self._position.value())

    def _on_slider_value_changed(self, value: int) -> None:
        if not self._slider_dragging:
            return
        self._update_time_label(value)
        self._scrub_pending_ms = value
        # Seek immediately, then throttle further seeks (~20 fps) like CapCut.
        if not self._scrub_timer.isActive():
            self._apply_scrub_now()

    def _on_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self._play_btn.setText("Pause" if playing else "Play")
        self._play_btn.setIcon(create_lucide_icon("pause" if playing else "play", _ICON))
        if playing:
            self._wanted_frame_ms = None
            self._preview_stack.setCurrentIndex(_STACK_VIDEO)
        else:
            self._preview_stack.setCurrentIndex(_STACK_FRAME)

    def _open_folder(self) -> None:
        folder = self._path.parent
        if not folder.is_dir():
            QMessageBox.warning(self, "Recording", f"Folder not found:\n{folder}")
            return
        if sys.platform == "win32":
            os.startfile(folder)  # noqa: S606
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _refit_frame_pixmap(self) -> None:
        source = self._frame_source
        if source is None or source.isNull():
            return
        fitted = source.scaled(
            self._frame_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._frame_label.setPixmap(fitted)

    def _request_accurate_frame(self, position_ms: int) -> None:
        """Queue an ffmpeg decode to the exact timestamp (not keyframe-only)."""
        target = self._clamp_position(position_ms)
        self._wanted_frame_ms = target
        if self._grab_process.state() == QProcess.ProcessState.NotRunning:
            self._start_frame_grab(target)

    def _save_as(self) -> None:
        fmt_raw = self._format.currentData()
        fmt: ExportFormat = fmt_raw if fmt_raw in {"mp4", "gif", "avif", "avif_optimized"} else "mp4"
        file_ext = "avif" if fmt.startswith("avif") else fmt
        default_name = f"{self._path.stem}_edit.{file_ext}"
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
        if destination.suffix.lower() != f".{file_ext}":
            destination = destination.with_suffix(f".{file_ext}")

        remove_audio = self._remove_audio.isChecked() or fmt != "mp4"
        request = ExportRequest(
            source=self._path,
            destination=destination,
            format=fmt,
            start_ms=self._in_ms,
            end_ms=self._keep_end_ms(),
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

    def _seek_preview(self, position_ms: int) -> None:
        """Seek player playhead and show an accurate ffmpeg preview frame."""
        target = self._clamp_position(position_ms)
        state = self._player.playbackState()
        if state == QMediaPlayer.PlaybackState.StoppedState:
            was_muted = self._audio.isMuted()
            self._audio.setMuted(True)
            self._player.play()
            self._player.pause()
            self._audio.setMuted(was_muted or self._muted)
        elif state == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        self._player.setPosition(target)
        if self._player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
            self._preview_stack.setCurrentIndex(_STACK_FRAME)
            self._request_accurate_frame(target)

    def _seek_to(self, position_ms: int) -> None:
        """Seek while staying in Paused/Playing — `stop()` clears the video to black."""
        target = self._clamp_position(position_ms)
        self._seek_preview(target)
        self._position.blockSignals(True)  # noqa: FBT003
        self._position.setValue(target)
        self._position.blockSignals(False)  # noqa: FBT003
        self._update_time_label(target)

    def _show_initial_frame(self) -> None:
        if self._initial_frame_ready:
            return
        self._initial_frame_ready = True
        self._seek_to(self._in_ms)

    def _start_frame_grab(self, position_ms: int) -> None:
        args = ffmpeg_frame_grab_args(self._path, position_ms)
        if args is None:
            self._wanted_frame_ms = None
            self._frame_label.setText("ffmpeg not found — scrub preview unavailable")
            return
        self._grab_for_ms = position_ms
        self._grab_process.setProgram(args[0])
        self._grab_process.setArguments(args[1:])
        self._grab_process.start()

    def _step_frame(self, delta_ms: int) -> None:
        base = self._position.value() if self._slider_dragging else self._player.position()
        # Prefer the last accurate scrub target when the media backend snaps to keyframes.
        if (
            self._wanted_frame_ms is not None
            and self._player.playbackState() != QMediaPlayer.PlaybackState.PlayingState
        ):
            base = self._wanted_frame_ms
        pos = self._clamp_position(base + delta_ms)
        self._seek_to(pos)

    def _stop(self) -> None:
        # Never call player.stop() here — it clears the video surface to black.
        self._scrub_timer.stop()
        self._scrub_pending_ms = None
        self._slider_dragging = False
        start = self._in_ms
        self._seek_to(start)
        # Force UI even if the media backend reports a stale position.
        self._position.blockSignals(True)  # noqa: FBT003
        self._position.setValue(start)
        self._position.blockSignals(False)  # noqa: FBT003
        self._update_time_label(start)

    def _sync_slider_range(self) -> None:
        lo = max(0, self._in_ms)
        hi = max(lo, self._keep_end_ms())
        self._position.setRange(lo, hi)

    def _toggle_mute(self) -> None:
        self._muted = not self._muted
        self._audio.setMuted(self._muted)
        self._mute_btn.setText("Unmute" if self._muted else "Mute")
        self._mute_btn.setIcon(create_lucide_icon("volume-x" if self._muted else "volume-2", _ICON))

    def _toggle_play(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            self._request_accurate_frame(self._player.position())
            return
        pos = self._position.value() if self._slider_dragging else self._player.position()
        end = self._keep_end_ms()
        # At (or past) the end of the kept range — restart from the start.
        if pos < self._in_ms or (end > 0 and pos >= end - 1):
            self._seek_to(self._in_ms)
        self._preview_stack.setCurrentIndex(_STACK_VIDEO)
        self._player.play()

    def _update_time_label(self, position: int) -> None:
        self._time_label.setText(f"{_format_ms(position)} / {_format_ms(self._keep_end_ms())}")

    def _update_trim_label(self) -> None:
        kept = max(0, self._keep_end_ms() - self._in_ms)
        self._trim_label.setText(
            f"Keep: {_format_ms(self._in_ms)} → {_format_ms(self._keep_end_ms())}  ({_format_ms(kept)})"
        )
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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._path = path.resolve()
        self._duration_ms = 0
        self._in_ms = 0
        self._out_ms = 0
        self._slider_dragging = False
        self._muted = False
        self._initial_frame_ready = False
        self._scrub_pending_ms: int | None = None
        self._wanted_frame_ms: int | None = None
        self._grab_for_ms: int | None = None
        self._frame_source: QPixmap | None = None
        self._scrub_timer = QTimer(self)
        self._scrub_timer.setSingleShot(True)
        self._scrub_timer.setInterval(_SCRUB_INTERVAL_MS)
        self._scrub_timer.timeout.connect(self._flush_scrub_seek)

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self._preview_stack = QStackedWidget(central)
        self._preview_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._video = QVideoWidget(self._preview_stack)
        self._video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._frame_label = QLabel(self._preview_stack)
        self._frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._frame_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._frame_label.setMinimumSize(1, 1)
        self._frame_label.setStyleSheet("QLabel { background-color: #111; color: #aaa; }")
        self._frame_label.setText("Loading frame…")
        self._preview_stack.addWidget(self._video)
        self._preview_stack.addWidget(self._frame_label)
        self._preview_stack.setCurrentIndex(_STACK_FRAME)
        root.addWidget(self._preview_stack, stretch=1)

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

        self._trim_label = QLabel("Keep: 0:00.000 → 0:00.000", central)
        root.addWidget(self._trim_label)

        transport = QHBoxLayout()
        self._play_btn = QPushButton(central)
        self._play_btn.setIcon(create_lucide_icon("play", _ICON))
        self._play_btn.setText("Play")
        self._play_btn.setToolTip("Play / Pause (Space)")
        self._play_btn.clicked.connect(self._toggle_play)
        transport.addWidget(self._play_btn)

        stop_btn = make_lucide_push_button("Stop", "square-stop")
        stop_btn.setToolTip("Stop and jump to the start of the kept range")
        stop_btn.clicked.connect(self._stop)
        transport.addWidget(stop_btn)

        self._mute_btn = QPushButton(central)
        self._mute_btn.setIcon(create_lucide_icon("volume-2", _ICON))
        self._mute_btn.setText("Mute")
        self._mute_btn.setToolTip("Mute / unmute playback")
        self._mute_btn.clicked.connect(self._toggle_mute)
        transport.addWidget(self._mute_btn)

        transport.addSpacing(12)

        prev_btn = make_lucide_push_button("Prev frame", "skip-back")
        prev_btn.setToolTip("Previous frame (~33 ms)")
        prev_btn.clicked.connect(lambda: self._step_frame(-_FRAME_MS))
        transport.addWidget(prev_btn)

        next_btn = make_lucide_push_button("Next frame", "skip-forward")
        next_btn.setToolTip("Next frame (~33 ms)")
        next_btn.clicked.connect(lambda: self._step_frame(_FRAME_MS))
        transport.addWidget(next_btn)

        delete_left_btn = make_lucide_push_button("Delete left", "scissors")
        delete_left_btn.setToolTip("Remove everything before the playhead (CapCut-style)")
        delete_left_btn.clicked.connect(self._delete_left)
        transport.addWidget(delete_left_btn)

        delete_right_btn = make_lucide_push_button("Delete right", "scissors")
        delete_right_btn.setToolTip("Remove everything after the playhead (CapCut-style)")
        delete_right_btn.clicked.connect(self._delete_right)
        transport.addWidget(delete_right_btn)

        transport.addStretch(1)
        root.addLayout(transport)

        export_row = QHBoxLayout()
        export_row.addWidget(QLabel("Save as:", central))
        self._format = QComboBox(central)
        self._format.addItem("MP4", "mp4")
        self._format.addItem("GIF", "gif")
        self._format.addItem("AVIF", "avif")
        self._format.addItem("AVIF optimized", "avif_optimized")
        self._format.setToolTip(
            "Export format. AVIF optimized uses the same pipeline as Images → Optimize (ffmpeg + avifenc)."
        )
        export_row.addWidget(self._format)

        self._remove_audio = QCheckBox("Remove audio", central)
        self._remove_audio.setToolTip("Strip audio from the exported file (always for GIF/AVIF)")
        self._remove_audio.setChecked(False)
        export_row.addWidget(self._remove_audio)

        save_btn = make_lucide_push_button("Save As…", "save")
        save_btn.setToolTip("Export the kept (trimmed) range")
        save_btn.clicked.connect(self._save_as)
        export_row.addWidget(save_btn)

        folder_btn = make_lucide_push_button("Open folder", "folder-open")
        folder_btn.setToolTip("Open containing folder in Explorer")
        folder_btn.clicked.connect(self._open_folder)
        export_row.addWidget(folder_btn)

        close_btn = make_lucide_push_button("Close", "x")
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
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.positionChanged.connect(self._on_position_changed)

        self._grab_process = QProcess(self)
        self._grab_process.finished.connect(self._on_frame_grab_finished)

        space = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        space.setContext(Qt.ShortcutContext.WindowShortcut)
        space.activated.connect(self._toggle_play)
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
        self._scrub_timer.stop()
        self._wanted_frame_ms = None
        if self._grab_process.state() != QProcess.ProcessState.NotRunning:
            self._grab_process.kill()
            self._grab_process.waitForFinished(500)
        self._player.stop()
        if _editor_holder["window"] is self:
            _editor_holder["window"] = None
        super().closeEvent(event)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Keep the scrub pixmap fitted when the window is resized.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._refit_frame_pixmap()
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
