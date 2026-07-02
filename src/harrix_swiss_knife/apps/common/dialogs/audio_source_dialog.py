"""Dialog for microphone recording and/or audio file input before BotHub processing."""

from __future__ import annotations

import array
import uuid
import wave
from collections import deque
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPaintEvent, QPen
from PySide6.QtMultimedia import QAudioDevice, QAudioFormat, QAudioSource, QMediaDevices
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
from harrix_swiss_knife.integrations.bothub.speech import MIN_AUDIO_BYTES, audio_format_from_suffix
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

RECORDING_BUTTON_STYLE = """QPushButton {
    background-color: #43a047;
    border: 2px solid #2e7d32;
    border-radius: 28px;
    min-width: 56px;
    max-width: 56px;
    min-height: 56px;
    max-height: 56px;
}
QPushButton:hover {
    background-color: #66bb6a;
}
QPushButton:pressed {
    background-color: #388e3c;
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

_LEVEL_BAR_COUNT = 48


def _pcm_peak_level(data: bytes, sample_format: QAudioFormat.SampleFormat) -> float:
    """Return normalized peak level (0..1) from raw PCM bytes."""
    if not data:
        return 0.0
    if sample_format == QAudioFormat.SampleFormat.Int16:
        samples = array.array("h")
        samples.frombytes(data)
        if not samples:
            return 0.0
        peak = max(abs(sample) for sample in samples)
        return min(1.0, peak / 32768.0)
    if sample_format == QAudioFormat.SampleFormat.Float:
        floats = array.array("f")
        floats.frombytes(data)
        if not floats:
            return 0.0
        peak = max(abs(sample) for sample in floats)
        return min(1.0, peak)
    return 0.0


class AudioLevelWidget(QWidget):
    """Simple scrolling bar chart for live microphone level."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize level widget."""
        super().__init__(parent)
        self._levels: deque[float] = deque([0.0] * _LEVEL_BAR_COUNT, maxlen=_LEVEL_BAR_COUNT)
        self.setMinimumHeight(56)
        self.setVisible(False)

    def clear(self) -> None:
        """Reset bars to zero."""
        self._levels = deque([0.0] * _LEVEL_BAR_COUNT, maxlen=_LEVEL_BAR_COUNT)
        self.update()

    def push_level(self, level: float) -> None:
        """Append a new bar level and repaint."""
        self._levels.append(max(0.0, min(1.0, level)))
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint scrolling level bars."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(event.rect(), QColor("#f5f5f5"))

        width = self.width()
        height = self.height()
        if width <= 0 or height <= 0:
            return

        bar_gap = 2
        bar_width = max(2, (width - bar_gap * (_LEVEL_BAR_COUNT + 1)) // _LEVEL_BAR_COUNT)
        max_bar_height = max(4, height - 12)
        baseline = height - 6

        painter.setPen(Qt.PenStyle.NoPen)
        for index, level in enumerate(self._levels):
            bar_height = max(2, int(level * max_bar_height))
            x = bar_gap + index * (bar_width + bar_gap)
            y = baseline - bar_height
            color = QColor("#43a047") if level > 0.05 else QColor("#c8e6c9")  # noqa: PLR2004
            painter.setBrush(color)
            painter.drawRoundedRect(x, y, bar_width, bar_height, 1, 1)

        painter.setPen(QPen(QColor("#bdbdbd"), 1))
        painter.drawLine(0, baseline, width, baseline)


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
        self._audio_source: QAudioSource | None = None
        self._audio_io = None
        self._wav_file: wave.Wave_write | None = None
        self._audio_format = QAudioFormat()
        self._recording_path = Path()
        self._setup_ui()
        self._populate_microphones()

    def closeEvent(self, event) -> None:  # noqa: ANN001, N802
        """Stop recording when the dialog is closed."""
        if self._is_recording:
            self._stop_recording()
        super().closeEvent(event)

    def get_audio_path(self) -> str:
        """Return path to the recorded or selected audio file."""
        return self._audio_path

    def reject(self) -> None:
        """Cancel dialog and stop an active recording."""
        if self._is_recording:
            self._stop_recording()
        super().reject()

    def _clear_dropped_file(self) -> None:
        self.file_widget.clear_file()

    def _clear_recording(self) -> None:
        self._recorded_path = ""
        self._status_label.setText("No recording yet")

    def _current_input_device(self) -> QAudioDevice | None:
        device = self._microphone_combo.currentData()
        return device if isinstance(device, QAudioDevice) else None

    def _finalize_recording(self) -> None:
        output = str(self._recording_path)
        if not output or not Path(output).exists():
            self._status_label.setText("Recording stopped")
            self._level_widget.setVisible(False)
            self._update_record_button()
            self._update_recognize_enabled()
            return

        size = Path(output).stat().st_size
        if size < MIN_AUDIO_BYTES:
            self._recorded_path = ""
            self._status_label.setText(f"Recording too short ({size} bytes). Try again.")
        else:
            self._recorded_path = output
            self._status_label.setText(f"Recorded: {Path(output).name} ({size // 1024} KB)")
        self._level_widget.setVisible(False)
        self._update_record_button()
        self._update_recognize_enabled()

    def _on_accept(self) -> None:
        dropped_path = self.file_widget.get_file_path().strip()
        if dropped_path:
            self._audio_path = dropped_path
        elif self._recorded_path:
            self._audio_path = self._recorded_path
        else:
            return
        self.accept()

    def _on_audio_ready(self) -> None:
        if self._audio_io is None or self._wav_file is None:
            return
        data = bytes(self._audio_io.readAll())
        if not data:
            return
        self._wav_file.writeframes(data)
        level = _pcm_peak_level(data, self._audio_format.sampleFormat())
        self._level_widget.push_level(min(1.0, level * 2.5))

    def _on_dropped_file_changed(self) -> None:
        if self.file_widget.get_file_path():
            self._clear_recording()
        self._update_recognize_enabled()

    def _on_record_clicked(self) -> None:
        if self._is_recording:
            self._stop_recording()
            return
        self._start_recording()

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

        self._level_widget = AudioLevelWidget()
        layout.addWidget(self._level_widget)

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

    def _start_recording(self) -> None:
        device = self._current_input_device()
        if device is None:
            self._status_label.setText("No microphone selected")
            return

        self._clear_dropped_file()
        self._recording_path = self._new_recording_path()
        self._recorded_path = ""
        self._audio_format = device.preferredFormat()

        try:
            self._wav_file = wave.open(str(self._recording_path), "wb")  # noqa: SIM115
            self._wav_file.setnchannels(self._audio_format.channelCount())
            self._wav_file.setsampwidth(self._audio_format.bytesPerSample())
            self._wav_file.setframerate(self._audio_format.sampleRate())

            self._audio_source = QAudioSource(device, self._audio_format, self)
            self._audio_io = self._audio_source.start()
            self._audio_io.readyRead.connect(self._on_audio_ready)
        except OSError as exc:
            self._cleanup_recording_handles()
            self._status_label.setText(f"Recording error: {exc}")
            return

        self._is_recording = True
        self._level_widget.clear()
        self._level_widget.setVisible(True)
        self._status_label.setText("Recording…")
        self._update_record_button()
        self._update_recognize_enabled()

    def _stop_recording(self) -> None:
        if self._audio_source is not None:
            self._audio_source.stop()
        self._cleanup_recording_handles()
        self._is_recording = False
        self._update_record_button()
        self._update_recognize_enabled()
        QTimer.singleShot(100, self._finalize_recording)

    def _cleanup_recording_handles(self) -> None:
        if self._wav_file is not None:
            self._wav_file.close()
            self._wav_file = None
        if self._audio_source is not None:
            self._audio_source.deleteLater()
            self._audio_source = None
        self._audio_io = None

    def _update_recognize_enabled(self) -> None:
        has_file = bool(self.file_widget.get_file_path().strip())
        has_recording = bool(self._recorded_path)
        self._recognize_button.setEnabled((has_file or has_recording) and not self._is_recording)

    def _update_record_button(self) -> None:
        if self._is_recording:
            self._record_button.setStyleSheet(RECORDING_BUTTON_STYLE)
            self._record_caption.setText("Stop")
        else:
            self._record_button.setStyleSheet(RECORD_BUTTON_STYLE)
            self._record_caption.setText("Record")

    def _new_recording_path(self) -> Path:
        temp_dir = get_project_root() / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir / f"hsk-speech-{uuid.uuid4().hex}.wav"
