"""Dialog for microphone recording and/or audio file input before BotHub processing."""

from __future__ import annotations

import uuid
from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import (
    QAudioDevice,
    QAudioInput,
    QMediaCaptureSession,
    QMediaDevices,
    QMediaFormat,
    QMediaRecorder,
)
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import install_url_drop_handlers
from harrix_swiss_knife.integrations.bothub.speech import audio_format_from_suffix
from harrix_swiss_knife.paths import get_project_root

RECOGNIZE_BUTTON_STYLE = """QPushButton {
    background-color: #C1ECDD;
}
QPushButton:hover {
    background-color: #D1F5E8;
}
QPushButton:pressed {
    background-color: #A8E0C7;
}"""

RECORD_BUTTON_STYLE = """QPushButton {
    background-color: #e53935;
    border: 2px solid #c62828;
    border-radius: 28px;
    min-width: 56px;
    max-width: 56px;
    min-height: 56px;
    max-height: 56px;
}
QPushButton:hover {
    background-color: #ef5350;
}
QPushButton:pressed {
    background-color: #c62828;
}"""

STOP_RECORD_BUTTON_STYLE = """QPushButton {
    background-color: #b71c1c;
    border: 2px solid #7f0000;
    border-radius: 28px;
    min-width: 56px;
    max-width: 56px;
    min-height: 56px;
    max-height: 56px;
}"""

_AUDIO_FILTER = "Audio files (*.wav *.mp3 *.m4a *.ogg *.webm)"

_EMPTY_DROP_STYLE = """
    QLabel {
        border: 2px dashed #ccc;
        border-radius: 5px;
        padding: 20px;
        background-color: #f9f9f9;
    }
"""

_SELECTED_DROP_STYLE = """
    QLabel {
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 10px;
        background-color: #f0f8f0;
    }
"""


class AudioFileDropWidget(QWidget):
    """Single audio file selection with drag and drop support."""

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
        self.file_label.setText(f"Audio: {Path(file_path).name}")
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
        browse_button = QPushButton("Select Audio File")
        browse_button.clicked.connect(self._browse_file)
        button_layout.addWidget(browse_button)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_file)
        button_layout.addWidget(clear_button)

        layout.addWidget(self.file_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)


class AudioSourceDialog(QDialog):
    """Modal dialog to record audio or select an audio file for BotHub transcription."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the audio source dialog."""
        super().__init__(parent)
        self._audio_path = ""
        self._recorded_path = ""
        self._is_recording = False
        self._capture_session = QMediaCaptureSession(self)
        self._audio_input = QAudioInput(self)
        self._recorder = QMediaRecorder(self)
        self._capture_session.setAudioInput(self._audio_input)
        self._capture_session.setRecorder(self._recorder)
        self._recorder.recorderStateChanged.connect(self._on_recorder_state_changed)
        self._recorder.errorOccurred.connect(self._on_recorder_error)
        self._setup_ui()
        self._populate_microphones()

    def get_audio_path(self) -> str:
        """Return path to the recorded or selected audio file."""
        return self._audio_path

    def _clear_dropped_file(self) -> None:
        self.file_widget.clear_file()

    def _clear_recording(self) -> None:
        self._recorded_path = ""
        self._status_label.setText("No recording yet")

    def _on_accept(self) -> None:
        dropped_path = self.file_widget.get_file_path().strip()
        if dropped_path:
            self._audio_path = dropped_path
        elif self._recorded_path:
            self._audio_path = self._recorded_path
        else:
            return
        self.accept()

    def _on_dropped_file_changed(self) -> None:
        if self.file_widget.get_file_path():
            self._clear_recording()
        self._update_recognize_enabled()

    def _on_microphone_changed(self, index: int) -> None:
        device = self._microphone_combo.itemData(index)
        if isinstance(device, QAudioDevice):
            self._audio_input.setDevice(device)

    def _on_recorder_error(self) -> None:
        error = self._recorder.error()
        if error != QMediaRecorder.Error.NoError:
            self._status_label.setText(f"Recording error: {self._recorder.errorString()}")
            self._is_recording = False
            self._update_record_button()

    def _on_recorder_state_changed(self, state: QMediaRecorder.RecorderState) -> None:
        if state == QMediaRecorder.RecorderState.RecordingState:
            self._is_recording = True
            self._status_label.setText("Recording…")
        elif state == QMediaRecorder.RecorderState.StoppedState and self._is_recording:
            self._is_recording = False
            output = self._recorder.actualLocation().toLocalFile()
            if output and Path(output).exists():
                self._recorded_path = output
                self._status_label.setText(f"Recorded: {Path(output).name}")
            else:
                self._status_label.setText("Recording stopped")
        self._update_record_button()
        self._update_recognize_enabled()

    def _on_record_clicked(self) -> None:
        if self._is_recording:
            self._recorder.stop()
            return

        self._clear_dropped_file()
        output_path = self._new_recording_path()
        media_format = QMediaFormat(QMediaFormat.FileFormat.Wave)
        self._recorder.setMediaFormat(media_format)
        self._recorder.setOutputLocation(QUrl.fromLocalFile(str(output_path)))
        self._recorder.record()

    def _populate_microphones(self) -> None:
        self._microphone_combo.clear()
        devices = QMediaDevices.audioInputs()
        if not devices:
            self._microphone_combo.addItem("No microphone found")
            self._microphone_combo.setEnabled(False)
            self._record_button.setEnabled(False)
            return

        for device in devices:
            self._microphone_combo.addItem(device.description(), device)

        default_device = QMediaDevices.defaultAudioInput()
        default_index = self._microphone_combo.findData(default_device)
        if default_index >= 0:
            self._microphone_combo.setCurrentIndex(default_index)
        self._on_microphone_changed(self._microphone_combo.currentIndex())

    def _setup_ui(self) -> None:
        self.setWindowTitle("Fix speech with AI")
        self.setMinimumSize(640, 480)
        self.setModal(True)

        layout = QVBoxLayout(self)

        description = QLabel(
            "Record speech or drop an audio file, then click Recognize to transcribe and fix the text."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        mic_label = QLabel("Microphone:")
        layout.addWidget(mic_label)

        self._microphone_combo = QComboBox()
        self._microphone_combo.currentIndexChanged.connect(self._on_microphone_changed)
        layout.addWidget(self._microphone_combo)

        record_layout = QHBoxLayout()
        record_layout.addStretch()

        record_column = QVBoxLayout()
        record_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._record_button = QPushButton("")
        self._record_button.setToolTip("Start/stop recording")
        self._record_button.clicked.connect(self._on_record_clicked)
        record_column.addWidget(self._record_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._record_caption = QLabel("Record")
        self._record_caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        record_column.addWidget(self._record_caption)

        record_layout.addLayout(record_column)
        record_layout.addStretch()
        layout.addLayout(record_layout)

        self._status_label = QLabel("No recording yet")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)

        or_label = QLabel("— or —")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(or_label)

        file_label = QLabel("Audio file:")
        layout.addWidget(file_label)

        self.file_widget = AudioFileDropWidget()
        self.file_widget.file_changed.connect(self._on_dropped_file_changed)
        layout.addWidget(self.file_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self._recognize_button = QPushButton("Recognize")
        recognize_font = QFont()
        recognize_font.setBold(True)
        self._recognize_button.setFont(recognize_font)
        self._recognize_button.setStyleSheet(RECOGNIZE_BUTTON_STYLE)
        self._recognize_button.setEnabled(False)
        self._recognize_button.setDefault(True)
        self._recognize_button.clicked.connect(self._on_accept)
        button_layout.addWidget(self._recognize_button)

        layout.addLayout(button_layout)
        self._update_record_button()

    def _update_recognize_enabled(self) -> None:
        has_file = bool(self.file_widget.get_file_path().strip())
        has_recording = bool(self._recorded_path)
        self._recognize_button.setEnabled((has_file or has_recording) and not self._is_recording)

    def _update_record_button(self) -> None:
        if self._is_recording:
            self._record_button.setStyleSheet(STOP_RECORD_BUTTON_STYLE)
            self._record_caption.setText("Stop")
        else:
            self._record_button.setStyleSheet(RECORD_BUTTON_STYLE)
            self._record_caption.setText("Record")

    def _new_recording_path(self) -> Path:
        temp_dir = get_project_root() / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir / f"hsk-speech-{uuid.uuid4().hex}.wav"
