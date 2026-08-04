---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `simple_recording_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `SimpleRecordingDialog`](#%EF%B8%8F-class-simplerecordingdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `get_audio_path`](#%EF%B8%8F-method-get_audio_path)
  - [⚙️ Method `reject`](#%EF%B8%8F-method-reject)
  - [⚙️ Method `release_multimedia`](#%EF%B8%8F-method-release_multimedia)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)

</details>

## 🏛️ Class `SimpleRecordingDialog`

```python
class SimpleRecordingDialog(QDialog)
```

Modal dialog that starts recording on open; waveform, mic picker, and Stop.

<details>
<summary>Code:</summary>

```python
class SimpleRecordingDialog(QDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the simple recording dialog."""
        super().__init__(parent)
        self._audio_path = ""
        self._auto_start_scheduled = False
        self._accept_pending = False
        self._status_label = QLabel("")
        self._recorder = MicrophoneRecorder(self)
        self._recorder.envelope_ready.connect(self._on_envelope_ready)
        self._recorder.recording_started.connect(self._on_recording_started)
        self._recorder.recording_stopped.connect(self._on_recording_stopped)
        self._recorder.finalized.connect(self._on_recording_finalized)
        self._recorder.start_failed.connect(self._on_start_failed)
        self._setup_ui()
        self._populate_microphones()

    def closeEvent(self, event) -> None:  # noqa: ANN001, N802
        """Stop recording when the dialog is closed."""
        self.release_multimedia()
        super().closeEvent(event)

    def get_audio_path(self) -> str:
        """Return path to the recorded audio file."""
        return self._audio_path

    def reject(self) -> None:
        """Cancel dialog and discard an active recording."""
        self._accept_pending = False
        self.release_multimedia()
        super().reject()

    def release_multimedia(self) -> None:
        """Stop capture and free Qt Multimedia backends before destruction."""
        self._recorder.release()
        self._update_stop_button()

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Auto-start recording after the dialog becomes visible."""
        super().showEvent(event)
        if self._auto_start_scheduled:
            return
        self._auto_start_scheduled = True
        QTimer.singleShot(0, self._start_recording_with_current_device)

    def _current_input_device(self) -> QAudioDevice | None:
        device = self._microphone_combo.currentData()
        return device if isinstance(device, QAudioDevice) else None

    def _on_envelope_ready(self, peak_neg: float, peak_pos: float) -> None:
        self._level_widget.push_envelope(peak_neg, peak_pos)

    def _on_microphone_changed(self, _index: int) -> None:
        """Persist mic choice; discard current capture and start a fresh recording."""
        if self._accept_pending:
            return

        device = self._current_input_device()
        if device is None:
            return

        MicrophoneRecorder.save_device(device)
        if self._recorder.is_recording:
            self._recorder.release()
        self._audio_path = ""
        self._recorder.clear()
        self._level_widget.clear()
        self._status_label.clear()
        self._status_label.setVisible(False)
        self._start_recording_with_current_device()

    def _on_recording_finalized(self, result: object) -> None:
        if not isinstance(result, FinalizeResult):
            return
        self._update_stop_button()
        if not result.success:
            self._accept_pending = False
            self._status_label.setText(result.message or "Recording stopped")
            self._status_label.setVisible(True)
            self._level_widget.clear()
            self._stop_button.setEnabled(False)
            return

        self._audio_path = result.recorded_path
        if result.normalized_pcm:
            self._level_widget.show_overview(result.normalized_pcm)
        if self._accept_pending:
            self._accept_pending = False
            self.release_multimedia()
            self.accept()

    def _on_recording_started(self) -> None:
        self._status_label.clear()
        self._status_label.setVisible(False)
        self._level_widget.begin_live()
        self._update_stop_button()

    def _on_recording_stopped(self) -> None:
        self._update_stop_button()

    def _on_start_failed(self, message: str) -> None:
        self._status_label.setText(message)
        self._status_label.setVisible(True)
        self._stop_button.setEnabled(False)
        self._update_stop_button()

    def _on_stop_clicked(self) -> None:
        if not self._recorder.is_recording:
            return
        self._accept_pending = True
        self._stop_button.setEnabled(False)
        self._microphone_combo.setEnabled(False)
        self._recorder.stop()

    def _populate_microphones(self) -> None:
        self._microphone_combo.blockSignals(True)  # noqa: FBT003
        try:
            self._microphone_combo.clear()
            devices = MicrophoneRecorder.list_input_devices()
            if not devices:
                self._microphone_combo.addItem("No microphone found")
                self._microphone_combo.setEnabled(False)
                self._stop_button.setEnabled(False)
                return

            self._microphone_combo.setEnabled(True)
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

    def _setup_ui(self) -> None:
        self.setWindowTitle("Recording")
        self.setMinimumSize(480, 260)
        self.setModal(True)

        layout = QVBoxLayout(self)

        mic_label = QLabel("Microphone:")
        layout.addWidget(mic_label)

        self._microphone_combo = QComboBox()
        self._microphone_combo.currentIndexChanged.connect(self._on_microphone_changed)
        layout.addWidget(self._microphone_combo)

        self._level_widget = AudioLevelWidget()
        self._level_widget.setStyleSheet("background-color: #1e1e1e; border: 1px solid #424242; border-radius: 6px;")
        self._level_widget.setMinimumHeight(96)
        layout.addWidget(self._level_widget)

        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

        controls = QHBoxLayout()
        controls.addStretch()

        column = QVBoxLayout()
        column.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._stop_button = RecordButton()
        self._stop_button.set_recording(recording=True)
        self._stop_button.setToolTip("Stop recording")
        self._stop_button.clicked.connect(self._on_stop_clicked)
        column.addWidget(self._stop_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._stop_caption = ClickableLabel("Stop")
        self._stop_caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._stop_caption.setStyleSheet(RECORD_CAPTION_STOP_STYLE)
        self._stop_caption.clicked.connect(self._on_stop_clicked)
        column.addWidget(self._stop_caption)

        controls.addLayout(column)
        controls.addStretch()
        layout.addLayout(controls)

    def _start_recording_with_current_device(self) -> None:
        if self._accept_pending:
            return
        if self._recorder.is_recording:
            return

        device = self._current_input_device()
        if device is None:
            self._status_label.setText("No microphone found")
            self._status_label.setVisible(True)
            self._stop_button.setEnabled(False)
            return

        MicrophoneRecorder.save_device(device)
        result = self._recorder.start(device, append=False)
        if not result.success:
            self._status_label.setText(result.message or "Recording error")
            self._status_label.setVisible(True)
            self._stop_button.setEnabled(False)

    def _update_stop_button(self) -> None:
        recording = self._recorder.is_recording
        self._stop_button.set_recording(recording=recording or self._accept_pending)
        self._stop_button.setEnabled(recording)
        self._stop_caption.setEnabled(recording)
        if not self._accept_pending:
            self._microphone_combo.setEnabled(
                self._microphone_combo.count() > 0 and self._current_input_device() is not None
            )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the simple recording dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._audio_path = ""
        self._auto_start_scheduled = False
        self._accept_pending = False
        self._status_label = QLabel("")
        self._recorder = MicrophoneRecorder(self)
        self._recorder.envelope_ready.connect(self._on_envelope_ready)
        self._recorder.recording_started.connect(self._on_recording_started)
        self._recorder.recording_stopped.connect(self._on_recording_stopped)
        self._recorder.finalized.connect(self._on_recording_finalized)
        self._recorder.start_failed.connect(self._on_start_failed)
        self._setup_ui()
        self._populate_microphones()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event) -> None
```

Stop recording when the dialog is closed.

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

Return path to the recorded audio file.

<details>
<summary>Code:</summary>

```python
def get_audio_path(self) -> str:
        return self._audio_path
```

</details>

### ⚙️ Method `reject`

```python
def reject(self) -> None
```

Cancel dialog and discard an active recording.

<details>
<summary>Code:</summary>

```python
def reject(self) -> None:
        self._accept_pending = False
        self.release_multimedia()
        super().reject()
```

</details>

### ⚙️ Method `release_multimedia`

```python
def release_multimedia(self) -> None
```

Stop capture and free Qt Multimedia backends before destruction.

<details>
<summary>Code:</summary>

```python
def release_multimedia(self) -> None:
        self._recorder.release()
        self._update_stop_button()
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Auto-start recording after the dialog becomes visible.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        if self._auto_start_scheduled:
            return
        self._auto_start_scheduled = True
        QTimer.singleShot(0, self._start_recording_with_current_device)
```

</details>
