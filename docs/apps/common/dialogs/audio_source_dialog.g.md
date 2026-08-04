---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `audio_source_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AudioFileDropWidget`](#%EF%B8%8F-class-audiofiledropwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `clear_file`](#%EF%B8%8F-method-clear_file)
  - [⚙️ Method `get_file_path`](#%EF%B8%8F-method-get_file_path)
  - [⚙️ Method `set_file_path`](#%EF%B8%8F-method-set_file_path)
- [🏛️ Class `AudioSourceDialog`](#%EF%B8%8F-class-audiosourcedialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `get_audio_path`](#%EF%B8%8F-method-get_audio_path)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `reject`](#%EF%B8%8F-method-reject)
  - [⚙️ Method `release_multimedia`](#%EF%B8%8F-method-release_multimedia)

</details>

## 🏛️ Class `AudioFileDropWidget`

```python
class AudioFileDropWidget(QWidget)
```

Single audio file selection with drag and drop support.

<details>
<summary>Code:</summary>

```python
class AudioFileDropWidget(QWidget):

    file_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize audio file drop widget."""
        super().__init__(parent)
        self.file_path = ""
        self._setup_ui()

    def clear_file(self) -> None:
        """Clear the selected file."""
        self.file_path = ""
        self.file_label.setText("Drag and drop audio file here or click button")
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)
        self.file_changed.emit()

    def get_file_path(self) -> str:
        """Return selected file path."""
        return self.file_path

    def set_file_path(self, path: str) -> None:
        """Set file path when the file exists and has a supported audio extension."""
        if not path or not Path(path).exists():
            return
        if audio_format_from_suffix(Path(path).suffix) is None:
            return
        self._set_file(path)

    def _browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select audio file", "", _AUDIO_FILTER)
        if file_path:
            self._set_file(file_path)

    def _on_drop_paths(self, paths: list[str]) -> None:
        for file_path in paths:
            if audio_format_from_suffix(Path(file_path).suffix) is not None:
                self._set_file(file_path)
                return

    def _set_file(self, file_path: str) -> None:
        self.file_path = file_path
        self.file_label.setText("Audio file selected")
        self.file_label.setStyleSheet(_SELECTED_DROP_STYLE)
        self.file_changed.emit()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        self.file_label = QLabel("Drag and drop audio file here or click button")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)
        self.file_label.setMinimumHeight(60)
        install_url_drop_handlers(self.file_label, self._on_drop_paths)

        button_layout = QHBoxLayout()
        browse_button = make_emoji_push_button("Select Audio File", "📁")
        browse_button.clicked.connect(self._browse_file)
        button_layout.addWidget(browse_button)
        clear_button = make_emoji_push_button("Clear", "🗑️")
        clear_button.clicked.connect(self.clear_file)
        button_layout.addWidget(clear_button)

        layout.addWidget(self.file_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize audio file drop widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.file_path = ""
        self._setup_ui()
```

</details>

### ⚙️ Method `clear_file`

```python
def clear_file(self) -> None
```

Clear the selected file.

<details>
<summary>Code:</summary>

```python
def clear_file(self) -> None:
        self.file_path = ""
        self.file_label.setText("Drag and drop audio file here or click button")
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)
        self.file_changed.emit()
```

</details>

### ⚙️ Method `get_file_path`

```python
def get_file_path(self) -> str
```

Return selected file path.

<details>
<summary>Code:</summary>

```python
def get_file_path(self) -> str:
        return self.file_path
```

</details>

### ⚙️ Method `set_file_path`

```python
def set_file_path(self, path: str) -> None
```

Set file path when the file exists and has a supported audio extension.

<details>
<summary>Code:</summary>

```python
def set_file_path(self, path: str) -> None:
        if not path or not Path(path).exists():
            return
        if audio_format_from_suffix(Path(path).suffix) is None:
            return
        self._set_file(path)
```

</details>

## 🏛️ Class `AudioSourceDialog`

```python
class AudioSourceDialog(QDialog)
```

Modal dialog to record audio or select an audio file for BotHub transcription.

<details>
<summary>Code:</summary>

```python
class AudioSourceDialog(QDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the audio source dialog."""
        super().__init__(parent)
        self._audio_path = ""
        self._recorder = MicrophoneRecorder(self)
        self._recorder.envelope_ready.connect(self._on_envelope_ready)
        self._recorder.recording_started.connect(self._on_recording_started)
        self._recorder.recording_stopped.connect(self._on_recording_stopped)
        self._recorder.finalized.connect(self._on_recording_finalized)
        self._recorder.start_failed.connect(self._on_start_failed)
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.positionChanged.connect(self._on_playback_position_changed)
        self._recording_timer = QTimer(self)
        self._recording_timer.setInterval(200)
        self._recording_timer.timeout.connect(self._update_recording_time_display)
        self._setup_ui()
        self._populate_microphones()

    def closeEvent(self, event) -> None:  # noqa: ANN001, N802
        """Stop recording and playback when the dialog is closed."""
        self.release_multimedia()
        super().closeEvent(event)

    def get_audio_path(self) -> str:
        """Return path to the recorded or selected audio file."""
        return self._audio_path

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle Enter and Space shortcuts for record, recognize, and playback."""
        if self._should_ignore_dialog_shortcuts():
            super().keyPressEvent(event)
            return

        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._handle_enter_shortcut():
                event.accept()
                return
        elif key == Qt.Key.Key_Space and self._handle_space_shortcut():
            event.accept()
            return

        super().keyPressEvent(event)

    def reject(self) -> None:
        """Cancel dialog and stop an active recording."""
        self.release_multimedia()
        super().reject()

    def release_multimedia(self) -> None:
        """Stop capture/playback and detach Qt Multimedia backends before destruction.

        On Windows, destroying `QMediaPlayer` / `QAudioSource` while WASAPI is still
        winding down causes a native access violation inside the Qt event loop.

        """
        was_recording = self._recorder.is_recording
        self._recorder.release()
        if was_recording:
            self._recording_timer.stop()
            self._recording_time_label.setVisible(False)
            self._update_record_button()
            self._update_recognize_enabled()
        self._stop_playback()
        # Detach sink before dialog teardown (Qt accepts nullptr; PySide stubs omit Optional).
        self._player.setAudioOutput(None)  # ty: ignore[invalid-argument-type]

    def _ask_recording_choice(self, existing_path: str) -> str | None:
        """Ask how to handle an existing audio file before a new recording."""
        can_continue = existing_path == self._recorder.recorded_path and self._can_continue_recording()

        message = QMessageBox(self)
        message.setIcon(QMessageBox.Icon.Question)
        message.setWindowTitle("Recording")

        if can_continue:
            message.setText("You already have a recording. Continue it or start a new one?")
            continue_button = message.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
            start_over_button = message.addButton("Start over", QMessageBox.ButtonRole.DestructiveRole)
            message.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            message.exec()
            clicked = message.clickedButton()
            if clicked == continue_button:
                return "continue"
            if clicked == start_over_button:
                return "start_over"
            return None

        message.setText("Start a new recording? The selected audio file will be replaced.")
        replace_button = message.addButton("Start over", QMessageBox.ButtonRole.DestructiveRole)
        message.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        message.exec()
        return "start_over" if message.clickedButton() == replace_button else None

    def _can_continue_recording(self) -> bool:
        return self._recorder.can_continue() and self._recognize_source_path() == self._recorder.recorded_path

    def _clear_dropped_file(self) -> None:
        self.file_widget.clear_file()

    def _clear_recording(self) -> None:
        self._stop_playback()
        self._recorder.clear()
        if not self._has_dropped_file():
            self._level_widget.clear()
        self._update_audio_ready_display()
        self._update_source_sections()
        self._update_playback_controls()
        self._update_recognize_enabled()

    def _current_input_device(self) -> QAudioDevice | None:
        device = self._microphone_combo.currentData()
        return device if isinstance(device, QAudioDevice) else None

    def _handle_enter_shortcut(self) -> bool:
        if self._recorder.is_recording:
            self._stop_recording()
            return True
        if self._recognize_button.isEnabled():
            self._on_accept()
            return True
        self._on_record_clicked()
        return True

    def _handle_space_shortcut(self) -> bool:
        preview_path = self._preview_audio_path()
        if self._recorder.is_recording or not preview_path or not Path(preview_path).is_file():
            return False
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._on_pause_playback_clicked()
        else:
            self._on_play_recording_clicked()
        return True

    def _has_dropped_file(self) -> bool:
        return bool(self.file_widget.get_file_path().strip())

    def _has_recorded_audio(self) -> bool:
        recorded_path = self._recorder.recorded_path
        return bool(recorded_path) and Path(recorded_path).is_file()

    def _load_waveform_for_path(self, audio_path: str) -> None:
        path = Path(audio_path)
        if not path.is_file():
            self._level_widget.clear()
            return
        pcm = audio_file_to_mono_pcm(path, project_root=get_project_root())
        if pcm:
            self._level_widget.show_overview(pcm)
        else:
            self._level_widget.clear()

    def _on_accept(self) -> None:
        dropped_path = self.file_widget.get_file_path().strip()
        if dropped_path:
            self._audio_path = dropped_path
        elif self._recorder.recorded_path:
            self._audio_path = self._recorder.recorded_path
        else:
            return
        # Release WASAPI / media player before the modal returns and the dialog is GC'd.
        self.release_multimedia()
        self.accept()

    def _on_audio_file_link_clicked(self, url: str) -> None:
        local_path = QUrl(url).toLocalFile()
        if not local_path:
            return
        folder = Path(local_path).parent
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _on_continue_recording_clicked(self) -> None:
        if self._recorder.is_recording or not self._can_continue_recording():
            return
        self._stop_playback()
        self._start_recording(append=True)

    def _on_dropped_file_changed(self) -> None:
        dropped_path = self.file_widget.get_file_path().strip()
        if dropped_path:
            self._clear_recording()
            self._stop_playback()
            self._load_waveform_for_path(dropped_path)
        else:
            self._stop_playback()
            self._level_widget.clear()
        self._update_source_sections()
        self._update_audio_ready_display()
        self._update_playback_controls()
        self._update_recognize_enabled()

    def _on_envelope_ready(self, peak_neg: float, peak_pos: float) -> None:
        self._level_widget.push_envelope(peak_neg, peak_pos)

    def _on_microphone_changed(self, _index: int) -> None:
        device = self._current_input_device()
        if device is not None:
            MicrophoneRecorder.save_device(device)

    def _on_pause_playback_clicked(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()

    def _on_play_recording_clicked(self) -> None:
        preview_path = self._preview_audio_path()
        if not preview_path:
            return
        audio_path = Path(preview_path)
        if not audio_path.is_file():
            return
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self._player.play()
            return
        source = QUrl.fromLocalFile(str(audio_path.resolve()))
        if self._player.source() != source:
            self._player.setSource(source)
        self._player.play()

    def _on_playback_position_changed(self, position: int) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            return
        duration = self._player.duration()
        if duration <= 0:
            return
        self._level_widget.set_playback_position(position / duration)

    def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self._level_widget.set_playback_position(None)
        self._update_playback_controls()

    def _on_record_clicked(self) -> None:
        if self._recorder.is_recording:
            self._stop_recording()
            return

        self._stop_playback()
        existing_path = self._recognize_source_path()
        append = False
        if existing_path:
            choice = self._ask_recording_choice(existing_path)
            if choice is None:
                return
            if choice == "continue":
                append = True
            else:
                self._clear_dropped_file()
                self._clear_recording()
        self._start_recording(append=append)

    def _on_recording_finalized(self, result: object) -> None:
        if not isinstance(result, FinalizeResult):
            return
        if not result.success:
            self._status_hint_label.setText(result.message or "Recording stopped")
            self._file_link_label.clear()
            self._file_link_label.setVisible(False)
            self._level_widget.clear()
            self._update_record_button()
            self._update_source_sections()
            self._update_playback_controls()
            self._update_recognize_enabled()
            return

        status = result.message or "Ready for recognition:"
        if result.ffmpeg_warning:
            status += result.ffmpeg_warning
        self._status_hint_label.setText(status)
        if result.normalized_pcm:
            self._level_widget.show_overview(result.normalized_pcm)
        self._update_audio_ready_display()
        self._update_record_button()
        self._update_source_sections()
        self._update_playback_controls()
        self._update_recognize_enabled()

    def _on_recording_started(self) -> None:
        self._update_source_sections()
        self._update_playback_controls()
        self._level_widget.begin_live()
        self._status_hint_label.setText("Recording…")
        self._recording_time_label.setText(format_recording_duration(self._recorder.duration_seconds()))
        self._recording_time_label.setVisible(True)
        self._recording_timer.start()
        self._file_link_label.clear()
        self._file_link_label.setVisible(False)
        self._update_record_button()
        self._update_recognize_enabled()

    def _on_recording_stopped(self) -> None:
        self._recording_timer.stop()
        self._recording_time_label.setVisible(False)
        self._update_record_button()
        self._update_recognize_enabled()

    def _on_rerecord_clicked(self) -> None:
        if self._recorder.is_recording:
            return
        self._stop_playback()
        self._clear_dropped_file()
        self._clear_recording()
        self._start_recording(append=False)

    def _on_start_failed(self, message: str) -> None:
        self._status_hint_label.setText(message)

    def _on_stop_playback_clicked(self) -> None:
        self._stop_playback()

    def _populate_microphones(self) -> None:
        self._microphone_combo.blockSignals(True)  # noqa: FBT003
        try:
            self._microphone_combo.clear()
            devices = MicrophoneRecorder.list_input_devices()
            if not devices:
                self._microphone_combo.addItem("No microphone found")
                self._microphone_combo.setEnabled(False)
                self._record_button.setEnabled(False)
                return

            self._microphone_combo.setEnabled(True)
            self._record_button.setEnabled(True)

            for device in devices:
                self._microphone_combo.addItem(device.description(), device)

            saved_id = load_saved_microphone_id()
            selected_index = -1
            if saved_id:
                for index in range(self._microphone_combo.count()):
                    device = self._microphone_combo.itemData(index)
                    if isinstance(device, QAudioDevice) and audio_device_id(device) == saved_id:
                        selected_index = index
                        break

            if selected_index >= 0:
                self._microphone_combo.setCurrentIndex(selected_index)
            else:
                default_device = MicrophoneRecorder.resolve_input_device()
                if default_device is not None:
                    default_index = self._microphone_combo.findData(default_device)
                    if default_index >= 0:
                        self._microphone_combo.setCurrentIndex(default_index)
        finally:
            self._microphone_combo.blockSignals(False)  # noqa: FBT003

    def _preview_audio_path(self) -> str:
        dropped_path = self.file_widget.get_file_path().strip()
        if dropped_path:
            return dropped_path
        return self._recorder.recorded_path

    def _recognize_source_path(self) -> str:
        dropped_path = self.file_widget.get_file_path().strip()
        if dropped_path:
            return dropped_path
        return self._recorder.recorded_path

    def _setup_ui(self) -> None:
        self.setWindowTitle("Speech to text with AI")
        self.setMinimumSize(640, 480)
        self.setModal(True)

        layout = QVBoxLayout(self)

        description = QLabel(
            "Record speech or drop an audio file, then click Recognize to convert it to text.\n"
            "Enter: record / stop / recognize · Space: play / pause"
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        mic_label = QLabel("Microphone:")
        layout.addWidget(mic_label)
        self._mic_label = mic_label

        self._microphone_combo = QComboBox()
        self._microphone_combo.currentIndexChanged.connect(self._on_microphone_changed)
        layout.addWidget(self._microphone_combo)

        record_layout = QHBoxLayout()
        record_layout.addStretch()

        record_column = QVBoxLayout()
        record_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        record_controls_row = QHBoxLayout()
        record_controls_row.setSpacing(PLAY_BUTTON_GAP)
        record_controls_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._record_button = RecordButton()
        self._record_button.setToolTip("Start/stop recording")
        self._record_button.clicked.connect(self._on_record_clicked)
        record_controls_row.addWidget(self._record_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._play_button = PlayButton()
        self._play_button.setVisible(False)
        self._play_button.clicked.connect(self._on_play_recording_clicked)
        record_controls_row.addWidget(self._play_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._pause_button = PauseButton()
        self._pause_button.setVisible(False)
        self._pause_button.clicked.connect(self._on_pause_playback_clicked)
        record_controls_row.addWidget(self._pause_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._stop_playback_button = StopPlaybackButton()
        self._stop_playback_button.setVisible(False)
        self._stop_playback_button.clicked.connect(self._on_stop_playback_clicked)
        record_controls_row.addWidget(self._stop_playback_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        record_column.addLayout(record_controls_row)

        self._record_caption = ClickableLabel("Record")
        self._record_caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._record_caption.clicked.connect(self._on_record_clicked)
        record_column.addWidget(self._record_caption)

        self._recording_time_label = QLabel("0:00")
        self._recording_time_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        recording_time_font = QFont()
        recording_time_font.setPointSize(14)
        recording_time_font.setBold(True)
        recording_time_font.setStyleHint(QFont.StyleHint.Monospace)
        self._recording_time_label.setFont(recording_time_font)
        self._recording_time_label.setVisible(False)
        record_column.addWidget(self._recording_time_label)

        record_layout.addLayout(record_column)
        record_layout.addStretch()
        layout.addLayout(record_layout)

        self._status_hint_label = QLabel("No audio selected yet")
        self._status_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_hint_label)

        self._file_link_label = QLabel()
        self._file_link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._file_link_label.setTextFormat(Qt.TextFormat.RichText)
        self._file_link_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self._file_link_label.setOpenExternalLinks(False)
        self._file_link_label.linkActivated.connect(self._on_audio_file_link_clicked)
        self._file_link_label.setVisible(False)
        layout.addWidget(self._file_link_label)

        self._level_widget = AudioLevelWidget()
        self._level_widget.setStyleSheet("background-color: #1e1e1e; border: 1px solid #424242; border-radius: 6px;")
        layout.addWidget(self._level_widget)

        or_label = QLabel("— or —")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(or_label)
        self._or_label = or_label

        file_label = QLabel("Audio file:")
        layout.addWidget(file_label)
        self._file_section_label = file_label

        self.file_widget = AudioFileDropWidget()
        self.file_widget.file_changed.connect(self._on_dropped_file_changed)
        layout.addWidget(self.file_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self._continue_recording_button = make_emoji_push_button("Continue recording", "▶️")
        self._continue_recording_button.clicked.connect(self._on_continue_recording_clicked)
        self._continue_recording_button.setVisible(False)
        button_layout.addWidget(self._continue_recording_button)

        self._rerecord_button = make_emoji_push_button("Re-record", "🔄")
        self._rerecord_button.clicked.connect(self._on_rerecord_clicked)
        self._rerecord_button.setVisible(False)
        button_layout.addWidget(self._rerecord_button)

        cancel_button = make_emoji_push_button("Cancel", "❌")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self._recognize_button = make_emoji_push_button("Recognize", "🎙️")
        recognize_font = QFont()
        recognize_font.setBold(True)
        self._recognize_button.setFont(recognize_font)
        self._recognize_button.setStyleSheet(RECOGNIZE_BUTTON_STYLE)
        self._recognize_button.setEnabled(False)
        self._recognize_button.clicked.connect(self._on_accept)
        button_layout.addWidget(self._recognize_button)

        layout.addLayout(button_layout)
        self._update_record_button()
        self._update_source_sections()
        self._update_recording_action_buttons()

    def _should_ignore_dialog_shortcuts(self) -> bool:
        focus_widget = self.focusWidget()
        if focus_widget is not None and isinstance(focus_widget, (QLineEdit, QTextEdit, QPlainTextEdit)):
            return True
        combo_view = self._microphone_combo.view()
        return combo_view is not None and combo_view.isVisible()

    def _start_recording(self, *, append: bool) -> None:
        device = self._current_input_device()
        if device is None:
            self._status_hint_label.setText("No microphone selected")
            return

        if not append:
            self._clear_dropped_file()

        result = self._recorder.start(device, append=append)
        if not result.success and result.message:
            self._status_hint_label.setText(result.message)

    def _stop_playback(self) -> None:
        if self._player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self._player.stop()
        if self._player.source().isValid():
            self._player.setSource(QUrl())
        self._level_widget.set_playback_position(None)
        self._update_playback_controls()

    def _stop_recording(self) -> None:
        self._recorder.stop()

    def _update_audio_ready_display(self) -> None:
        if self._recorder.is_recording:
            return

        audio_path = self._recognize_source_path()
        if not audio_path or not Path(audio_path).exists():
            self._status_hint_label.setText("No audio selected yet")
            self._file_link_label.clear()
            self._file_link_label.setVisible(False)
            return

        path = Path(audio_path)
        file_url = QUrl.fromLocalFile(str(path.resolve())).toString()
        size_text = format_file_size(path.stat().st_size)
        self._status_hint_label.setText("Ready for recognition:")
        self._file_link_label.setText(
            f'<a href="{file_url}" style="color:#1565c0; text-decoration: underline;">{path.name}</a> · {size_text}'
        )
        self._file_link_label.setVisible(True)

    def _update_playback_controls(self) -> None:
        preview_path = self._preview_audio_path()
        has_preview = bool(preview_path) and Path(preview_path).is_file() and not self._recorder.is_recording
        if not has_preview:
            self._play_button.setVisible(False)
            self._pause_button.setVisible(False)
            self._stop_playback_button.setVisible(False)
            return

        playback_state = self._player.playbackState()
        is_playing = playback_state == QMediaPlayer.PlaybackState.PlayingState
        is_paused = playback_state == QMediaPlayer.PlaybackState.PausedState
        is_active = is_playing or is_paused

        self._play_button.setVisible(not is_playing)
        self._pause_button.setVisible(is_playing)
        self._stop_playback_button.setVisible(is_active)

    def _update_recognize_enabled(self) -> None:
        has_file = bool(self.file_widget.get_file_path().strip())
        has_recording = bool(self._recorder.recorded_path)
        self._recognize_button.setEnabled((has_file or has_recording) and not self._recorder.is_recording)
        self._update_recording_action_buttons()

    def _update_record_button(self) -> None:
        self._record_button.set_recording(recording=self._recorder.is_recording)
        if self._recorder.is_recording:
            self._record_caption.setText("Stop")
            self._record_caption.setStyleSheet(RECORD_CAPTION_STOP_STYLE)
        else:
            self._record_caption.setText("Record")
            self._record_caption.setStyleSheet(RECORD_CAPTION_IDLE_STYLE)

    def _update_recording_action_buttons(self) -> None:
        show_recording_actions = (
            self._has_recorded_audio() and not self._recorder.is_recording and not self._has_dropped_file()
        )
        self._rerecord_button.setVisible(show_recording_actions)
        self._continue_recording_button.setVisible(show_recording_actions and self._can_continue_recording())

    def _update_recording_time_display(self) -> None:
        if not self._recorder.is_recording:
            return
        self._recording_time_label.setText(format_recording_duration(self._recorder.duration_seconds()))

    def _update_source_sections(self) -> None:
        """Show recording or file picker section depending on the active audio source."""
        has_dropped = self._has_dropped_file()
        has_recorded = self._has_recorded_audio()
        show_file_section = not has_recorded and not self._recorder.is_recording
        show_recording_parts = not has_dropped

        self._mic_label.setVisible(show_recording_parts)
        self._microphone_combo.setVisible(show_recording_parts)
        self._record_button.setVisible(show_recording_parts)
        self._record_caption.setVisible(show_recording_parts)
        self._or_label.setVisible(show_file_section)
        self._file_section_label.setVisible(show_file_section)
        self.file_widget.setVisible(show_file_section)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the audio source dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._audio_path = ""
        self._recorder = MicrophoneRecorder(self)
        self._recorder.envelope_ready.connect(self._on_envelope_ready)
        self._recorder.recording_started.connect(self._on_recording_started)
        self._recorder.recording_stopped.connect(self._on_recording_stopped)
        self._recorder.finalized.connect(self._on_recording_finalized)
        self._recorder.start_failed.connect(self._on_start_failed)
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.positionChanged.connect(self._on_playback_position_changed)
        self._recording_timer = QTimer(self)
        self._recording_timer.setInterval(200)
        self._recording_timer.timeout.connect(self._update_recording_time_display)
        self._setup_ui()
        self._populate_microphones()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event) -> None
```

Stop recording and playback when the dialog is closed.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event) -> None:  # noqa: ANN001, N802
        self.release_multimedia()
        super().closeEvent(event)
```

</details>

### ⚙️ Method `get_audio_path`

```python
def get_audio_path(self) -> str
```

Return path to the recorded or selected audio file.

<details>
<summary>Code:</summary>

```python
def get_audio_path(self) -> str:
        return self._audio_path
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Handle Enter and Space shortcuts for record, recognize, and playback.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if self._should_ignore_dialog_shortcuts():
            super().keyPressEvent(event)
            return

        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._handle_enter_shortcut():
                event.accept()
                return
        elif key == Qt.Key.Key_Space and self._handle_space_shortcut():
            event.accept()
            return

        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `reject`

```python
def reject(self) -> None
```

Cancel dialog and stop an active recording.

<details>
<summary>Code:</summary>

```python
def reject(self) -> None:
        self.release_multimedia()
        super().reject()
```

</details>

### ⚙️ Method `release_multimedia`

```python
def release_multimedia(self) -> None
```

Stop capture/playback and detach Qt Multimedia backends before destruction.

On Windows, destroying `QMediaPlayer` / `QAudioSource` while WASAPI is still
winding down causes a native access violation inside the Qt event loop.

<details>
<summary>Code:</summary>

```python
def release_multimedia(self) -> None:
        was_recording = self._recorder.is_recording
        self._recorder.release()
        if was_recording:
            self._recording_timer.stop()
            self._recording_time_label.setVisible(False)
            self._update_record_button()
            self._update_recognize_enabled()
        self._stop_playback()
        # Detach sink before dialog teardown (Qt accepts nullptr; PySide stubs omit Optional).
        self._player.setAudioOutput(None)  # ty: ignore[invalid-argument-type]
```

</details>
