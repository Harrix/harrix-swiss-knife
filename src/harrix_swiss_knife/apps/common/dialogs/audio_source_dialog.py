"""Dialog for microphone recording and/or audio file input before BotHub processing."""

from __future__ import annotations

import array
import uuid
import wave
from collections import deque
from pathlib import Path
from typing import Literal

import harrix_pylib as h
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, QUrl, Signal
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QEnterEvent,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QPolygonF,
)
from PySide6.QtMultimedia import QAudioDevice, QAudioFormat, QAudioOutput, QAudioSource, QMediaDevices, QMediaPlayer
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.audio_compress import (
    FfmpegNotFoundError,
    audio_file_to_mono_pcm,
    wav_to_m4a,
)
from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import install_url_drop_handlers
from harrix_swiss_knife.integrations.bothub.speech import MIN_AUDIO_BYTES, audio_format_from_suffix
from harrix_swiss_knife.paths import get_config_path_str, get_project_root, get_temp_config_path
from harrix_swiss_knife.qt_emoji_icon import make_emoji_push_button

RECOGNIZE_BUTTON_STYLE = """QPushButton {
    background-color: #C1ECDD;
}
QPushButton:hover {
    background-color: #D1F5E8;
}
QPushButton:pressed {
    background-color: #A8E0C7;
}"""

_RECORD_BUTTON_SIZE = 56
_PLAY_BUTTON_SIZE = 40
_PLAY_BUTTON_GAP = 12

_RECORD_CAPTION_IDLE_STYLE = """
    QLabel {
        color: #c62828;
    }
    QLabel:hover {
        color: #e53935;
    }
"""

_RECORD_CAPTION_STOP_STYLE = """
    QLabel {
        color: #1a1a1a;
    }
    QLabel:hover {
        color: #333333;
    }
"""

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

_LEVEL_BAR_COUNT = 120
_BYTES_PER_KIB = 1024
_BYTES_PER_MIB = 1024 * 1024
_LEVEL_GAIN = 2.0
_WAVEFORM_BG = QColor("#1e1e1e")
_WAVEFORM_GRID = QColor("#3a3a3a")
_WAVEFORM_CENTER = QColor("#616161")
_WAVEFORM_FILL = QColor(76, 175, 80, 200)
_WAVEFORM_OUTLINE = QColor("#81c784")
_WAVEFORM_LIVE_FILL = QColor(102, 187, 106, 210)
_WAVEFORM_PLAYHEAD = QColor("#ffeb3b")
_TEMP_MICROPHONE_ID_KEY = "speech_microphone_id"


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


class AudioLevelWidget(QWidget):
    """Live scrolling and full-recording waveform display."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize waveform widget."""
        super().__init__(parent)
        self._mode: Literal["idle", "live", "overview"] = "idle"
        self._live_buckets: deque[tuple[float, float]] = deque(
            [(0.0, 0.0)] * _LEVEL_BAR_COUNT,
            maxlen=_LEVEL_BAR_COUNT,
        )
        self._overview_pcm = b""
        self._playback_ratio: float | None = None
        self.setMinimumHeight(72)
        self.setVisible(False)

    def begin_live(self) -> None:
        """Switch to scrolling live waveform mode."""
        self._mode = "live"
        self._overview_pcm = b""
        self._playback_ratio = None
        self._live_buckets = deque([(0.0, 0.0)] * _LEVEL_BAR_COUNT, maxlen=_LEVEL_BAR_COUNT)
        self.setVisible(True)
        self.update()

    def clear(self) -> None:
        """Reset widget to idle state."""
        self._mode = "idle"
        self._overview_pcm = b""
        self._playback_ratio = None
        self._live_buckets = deque([(0.0, 0.0)] * _LEVEL_BAR_COUNT, maxlen=_LEVEL_BAR_COUNT)
        self.setVisible(False)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Paint live or overview waveform."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        if width <= 0 or height <= 0:
            return

        painter.fillRect(0, 0, width, height, _WAVEFORM_BG)
        center_y = height / 2.0
        margin = 8
        half_height = max(4.0, (height - margin * 2) / 2.0)

        for ratio in (0.25, 0.75):
            grid_y = margin + ratio * (height - margin * 2)
            painter.setPen(QPen(_WAVEFORM_GRID, 1, Qt.PenStyle.DotLine))
            painter.drawLine(0, int(grid_y), width, int(grid_y))

        painter.setPen(QPen(_WAVEFORM_CENTER, 1))
        painter.drawLine(0, int(center_y), width, int(center_y))

        if self._mode == "live":
            buckets = list(self._live_buckets)
            fill_color = _WAVEFORM_LIVE_FILL
        elif self._mode == "overview" and self._overview_pcm:
            bucket_count = max(32, width // 2)
            buckets = _waveform_buckets_from_pcm(self._overview_pcm, bucket_count)
            fill_color = _WAVEFORM_FILL
        else:
            return

        if not buckets:
            return

        path = QPainterPath()
        path.moveTo(0.0, center_y)
        bucket_width = width / len(buckets)
        for index, (_peak_neg, peak_pos) in enumerate(buckets):
            x = index * bucket_width + bucket_width / 2.0
            path.lineTo(x, center_y - peak_pos * half_height)

        last_x = (len(buckets) - 1) * bucket_width + bucket_width / 2.0
        path.lineTo(last_x, center_y)

        for index in range(len(buckets) - 1, -1, -1):
            peak_neg, _peak_pos = buckets[index]
            x = index * bucket_width + bucket_width / 2.0
            path.lineTo(x, center_y - peak_neg * half_height)

        path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill_color)
        painter.drawPath(path)

        painter.setPen(QPen(_WAVEFORM_OUTLINE, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        if self._mode == "overview" and self._playback_ratio is not None:
            playhead_x = max(0.0, min(float(width), self._playback_ratio * width))
            painter.setPen(QPen(_WAVEFORM_PLAYHEAD, 2))
            painter.drawLine(int(playhead_x), 0, int(playhead_x), height)

    def push_envelope(self, peak_neg: float, peak_pos: float) -> None:
        """Append one live waveform bucket and repaint."""
        if self._mode != "live":
            return
        self._live_buckets.append((peak_neg, peak_pos))
        self.update()

    def resizeEvent(self, event) -> None:  # noqa: ANN001, N802
        """Repaint overview buckets when the widget is resized."""
        super().resizeEvent(event)
        if self._mode == "overview":
            self.update()

    def set_playback_position(self, ratio: float | None) -> None:
        """Set playhead position from 0 to 1, or hide it when ``ratio`` is None."""
        if self._playback_ratio != ratio:
            self._playback_ratio = ratio
            self.update()

    def show_overview(self, pcm_data: bytes) -> None:
        """Show the full recording waveform."""
        self._mode = "overview"
        self._overview_pcm = pcm_data
        self._playback_ratio = None
        self.setVisible(bool(pcm_data))
        self.update()


class AudioSourceDialog(QDialog):
    """Modal dialog to record audio or select an audio file for BotHub transcription."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the audio source dialog."""
        super().__init__(parent)
        self._audio_path = ""
        self._recorded_path = ""
        self._recording_wav_path = ""
        self._is_recording = False
        self._audio_source: QAudioSource | None = None
        self._audio_io = None
        self._audio_format = QAudioFormat()
        self._recording_path = Path()
        self._pcm_chunks: list[bytes] = []
        self._wav_params: tuple[int, int, int, int, str, str] | None = None
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.positionChanged.connect(self._on_playback_position_changed)
        self._setup_ui()
        self._populate_microphones()

    def closeEvent(self, event) -> None:  # noqa: ANN001, N802
        """Stop recording and playback when the dialog is closed."""
        self._stop_playback()
        if self._is_recording:
            self._stop_recording()
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
        self._stop_playback()
        if self._is_recording:
            self._stop_recording()
        super().reject()

    def _ask_recording_choice(self, existing_path: str) -> str | None:
        """Ask how to handle an existing audio file before a new recording."""
        can_continue = existing_path == self._recorded_path and self._can_continue_recording()

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
        return (
            bool(self._recording_wav_path)
            and Path(self._recording_wav_path).is_file()
            and bool(self._recorded_path)
            and self._recognize_source_path() == self._recorded_path
        )

    def _cleanup_recording_handles(self) -> None:
        if self._audio_source is not None:
            self._audio_source.deleteLater()
            self._audio_source = None
        self._audio_io = None

    def _clear_dropped_file(self) -> None:
        self.file_widget.clear_file()

    def _clear_recording(self) -> None:
        self._stop_playback()
        self._recorded_path = ""
        self._recording_wav_path = ""
        if not self._has_dropped_file():
            self._level_widget.clear()
        self._update_audio_ready_display()
        self._update_source_sections()
        self._update_playback_controls()
        self._update_recognize_enabled()

    def _current_input_device(self) -> QAudioDevice | None:
        device = self._microphone_combo.currentData()
        return device if isinstance(device, QAudioDevice) else None

    def _finalize_recording(self) -> None:
        output = self._recording_path
        pcm_data = b"".join(self._pcm_chunks)
        self._pcm_chunks = []

        if not output or not pcm_data or self._wav_params is None:
            self._status_hint_label.setText("Recording stopped")
            self._file_link_label.clear()
            self._file_link_label.setVisible(False)
            self._level_widget.clear()
            self._update_record_button()
            self._update_source_sections()
            self._update_playback_controls()
            self._update_recognize_enabled()
            return

        try:
            wav_params = _wav_params_from_audio_format(self._audio_format)
            normalized_pcm = _normalize_pcm_to_int16_mono(pcm_data, self._audio_format)
            _write_wav(output, wav_params, normalized_pcm)
        except OSError as exc:
            self._recorded_path = ""
            self._recording_wav_path = ""
            self._status_hint_label.setText(f"Recording error: {exc}")
            self._file_link_label.clear()
            self._file_link_label.setVisible(False)
            self._level_widget.clear()
            self._update_record_button()
            self._update_source_sections()
            self._update_playback_controls()
            self._update_recognize_enabled()
            return

        size = output.stat().st_size
        if size < MIN_AUDIO_BYTES:
            self._recorded_path = ""
            self._recording_wav_path = ""
            self._status_hint_label.setText(f"Recording too short ({_format_file_size(size)}). Try again.")
            self._file_link_label.clear()
            self._file_link_label.setVisible(False)
            self._level_widget.clear()
        else:
            final_path = output
            ffmpeg_warning = ""
            try:
                final_path = wav_to_m4a(output, project_root=get_project_root())
                self._recording_wav_path = str(output)
            except FfmpegNotFoundError:
                ffmpeg_warning = " (ffmpeg not found — saved as WAV, file is large)"
                self._recording_wav_path = str(output)
            except RuntimeError as exc:
                self._recorded_path = ""
                self._recording_wav_path = ""
                self._status_hint_label.setText(f"Recording error: {exc}")
                self._file_link_label.clear()
                self._file_link_label.setVisible(False)
                self._level_widget.clear()
                self._update_record_button()
                self._update_source_sections()
                self._update_playback_controls()
                self._update_recognize_enabled()
                return

            self._recorded_path = str(final_path)
            status = "Ready for recognition:"
            if ffmpeg_warning:
                status += ffmpeg_warning
            self._status_hint_label.setText(status)
            self._level_widget.show_overview(normalized_pcm)
        self._update_audio_ready_display()
        self._update_record_button()
        self._update_source_sections()
        self._update_playback_controls()
        self._update_recognize_enabled()

    def _handle_enter_shortcut(self) -> bool:
        if self._is_recording:
            self._stop_recording()
            return True
        if self._recognize_button.isEnabled():
            self._on_accept()
            return True
        self._on_record_clicked()
        return True

    def _handle_space_shortcut(self) -> bool:
        preview_path = self._preview_audio_path()
        if self._is_recording or not preview_path or not Path(preview_path).is_file():
            return False
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._on_pause_playback_clicked()
        else:
            self._on_play_recording_clicked()
        return True

    def _has_dropped_file(self) -> bool:
        return bool(self.file_widget.get_file_path().strip())

    def _has_recorded_audio(self) -> bool:
        return bool(self._recorded_path) and Path(self._recorded_path).is_file()

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

    def _new_recording_path(self) -> Path:
        temp_dir = get_project_root() / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir / f"hsk-speech-{uuid.uuid4().hex}.wav"

    def _on_accept(self) -> None:
        self._stop_playback()
        dropped_path = self.file_widget.get_file_path().strip()
        if dropped_path:
            self._audio_path = dropped_path
        elif self._recorded_path:
            self._audio_path = self._recorded_path
        else:
            return
        self.accept()

    def _on_audio_file_link_clicked(self, url: str) -> None:
        local_path = QUrl(url).toLocalFile()
        if not local_path:
            return
        folder = Path(local_path).parent
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _on_audio_ready(self) -> None:
        if self._audio_io is None:
            return
        data = bytes(self._audio_io.readAll().data())
        if not data:
            return
        self._pcm_chunks.append(data)
        peak_neg, peak_pos = _pcm_chunk_envelope(data, self._audio_format)
        self._level_widget.push_envelope(peak_neg, peak_pos)

    def _on_continue_recording_clicked(self) -> None:
        if self._is_recording or not self._can_continue_recording():
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

    def _on_microphone_changed(self, _index: int) -> None:
        device = self._current_input_device()
        if device is not None:
            _save_microphone_id(device)

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
        if self._is_recording:
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

    def _on_rerecord_clicked(self) -> None:
        if self._is_recording:
            return
        self._stop_playback()
        self._clear_dropped_file()
        self._clear_recording()
        self._start_recording(append=False)

    def _on_stop_playback_clicked(self) -> None:
        self._stop_playback()

    def _populate_microphones(self) -> None:
        self._microphone_combo.blockSignals(True)  # noqa: FBT003
        try:
            self._microphone_combo.clear()
            devices = QMediaDevices.audioInputs()
            if not devices:
                self._microphone_combo.addItem("No microphone found")
                self._microphone_combo.setEnabled(False)
                self._record_button.setEnabled(False)
                return

            self._microphone_combo.setEnabled(True)
            self._record_button.setEnabled(True)

            for device in devices:
                self._microphone_combo.addItem(device.description(), device)

            saved_id = _load_saved_microphone_id()
            selected_index = -1
            if saved_id:
                for index in range(self._microphone_combo.count()):
                    device = self._microphone_combo.itemData(index)
                    if isinstance(device, QAudioDevice) and _audio_device_id(device) == saved_id:
                        selected_index = index
                        break

            if selected_index >= 0:
                self._microphone_combo.setCurrentIndex(selected_index)
            else:
                default_device = QMediaDevices.defaultAudioInput()
                default_index = self._microphone_combo.findData(default_device)
                if default_index >= 0:
                    self._microphone_combo.setCurrentIndex(default_index)
        finally:
            self._microphone_combo.blockSignals(False)  # noqa: FBT003

    def _preview_audio_path(self) -> str:
        dropped_path = self.file_widget.get_file_path().strip()
        if dropped_path:
            return dropped_path
        return self._recorded_path

    def _recognize_source_path(self) -> str:
        dropped_path = self.file_widget.get_file_path().strip()
        if dropped_path:
            return dropped_path
        return self._recorded_path

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
        record_controls_row.setSpacing(_PLAY_BUTTON_GAP)
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

        self._audio_format = _recording_format_for_device(device)
        new_params = _wav_params_from_audio_format(self._audio_format)

        if append:
            if not self._recording_wav_path:
                append = False
            else:
                recorded_path = Path(self._recording_wav_path)
            if append and not recorded_path.exists():
                append = False
            if append:
                try:
                    existing_params, existing_pcm = _read_wav_pcm(recorded_path)
                except (OSError, wave.Error) as exc:
                    self._status_hint_label.setText(f"Cannot continue recording: {exc}")
                    return
                if not _wav_params_match_audio_format(existing_params, self._audio_format):
                    self._status_hint_label.setText("Cannot continue: microphone format changed. Start over.")
                    return
                self._recording_path = recorded_path
                self._wav_params = existing_params
                self._pcm_chunks = [existing_pcm] if existing_pcm else []
        if not append:
            self._clear_dropped_file()
            self._recording_path = self._new_recording_path()
            self._recorded_path = ""
            self._recording_wav_path = ""
            self._wav_params = new_params
            self._pcm_chunks = []

        try:
            self._audio_source = QAudioSource(device, self._audio_format, self)
            self._audio_io = self._audio_source.start()
            self._audio_io.readyRead.connect(self._on_audio_ready)
        except OSError as exc:
            self._cleanup_recording_handles()
            self._status_hint_label.setText(f"Recording error: {exc}")
            return

        self._is_recording = True
        self._update_source_sections()
        self._update_playback_controls()
        self._level_widget.begin_live()
        self._status_hint_label.setText("Recording…")
        self._file_link_label.clear()
        self._file_link_label.setVisible(False)
        self._update_record_button()
        self._update_recognize_enabled()

    def _stop_playback(self) -> None:
        if self._player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self._player.stop()
        self._level_widget.set_playback_position(None)
        self._update_playback_controls()

    def _stop_recording(self) -> None:
        if self._audio_source is not None:
            self._audio_source.stop()
        self._cleanup_recording_handles()
        self._is_recording = False
        self._update_record_button()
        self._update_recognize_enabled()
        QTimer.singleShot(100, self._finalize_recording)

    def _update_audio_ready_display(self) -> None:
        if self._is_recording:
            return

        audio_path = self._recognize_source_path()
        if not audio_path or not Path(audio_path).exists():
            self._status_hint_label.setText("No audio selected yet")
            self._file_link_label.clear()
            self._file_link_label.setVisible(False)
            return

        path = Path(audio_path)
        file_url = QUrl.fromLocalFile(str(path.resolve())).toString()
        size_text = _format_file_size(path.stat().st_size)
        self._status_hint_label.setText("Ready for recognition:")
        self._file_link_label.setText(
            f'<a href="{file_url}" style="color:#1565c0; text-decoration: underline;">{path.name}</a> · {size_text}'
        )
        self._file_link_label.setVisible(True)

    def _update_playback_controls(self) -> None:
        preview_path = self._preview_audio_path()
        has_preview = bool(preview_path) and Path(preview_path).is_file() and not self._is_recording
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
        has_recording = bool(self._recorded_path)
        self._recognize_button.setEnabled((has_file or has_recording) and not self._is_recording)
        self._update_recording_action_buttons()

    def _update_record_button(self) -> None:
        self._record_button.set_recording(recording=self._is_recording)
        if self._is_recording:
            self._record_caption.setText("Stop")
            self._record_caption.setStyleSheet(_RECORD_CAPTION_STOP_STYLE)
        else:
            self._record_caption.setText("Record")
            self._record_caption.setStyleSheet(_RECORD_CAPTION_IDLE_STYLE)

    def _update_recording_action_buttons(self) -> None:
        show_recording_actions = self._has_recorded_audio() and not self._is_recording and not self._has_dropped_file()
        self._rerecord_button.setVisible(show_recording_actions)
        self._continue_recording_button.setVisible(show_recording_actions and self._can_continue_recording())

    def _update_source_sections(self) -> None:
        """Show recording or file picker section depending on the active audio source."""
        has_dropped = self._has_dropped_file()
        has_recorded = self._has_recorded_audio()
        show_file_section = not has_recorded and not self._is_recording
        show_recording_parts = not has_dropped

        self._mic_label.setVisible(show_recording_parts)
        self._microphone_combo.setVisible(show_recording_parts)
        self._record_button.setVisible(show_recording_parts)
        self._record_caption.setVisible(show_recording_parts)
        self._or_label.setVisible(show_file_section)
        self._file_section_label.setVisible(show_file_section)
        self.file_widget.setVisible(show_file_section)


class ClickableLabel(QLabel):
    """Label that emits ``clicked`` on left mouse press."""

    clicked = Signal()

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        """Initialize clickable label."""
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit ``clicked`` for left-button presses."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class PauseButton(QPushButton):
    """Pause button with two vertical bars."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize pause button."""
        super().__init__(parent)
        self.setFixedSize(_PLAY_BUTTON_SIZE, _PLAY_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Pause playback")
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Highlight the pause icon on hover."""
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: ANN001, N802
        """Restore the pause icon when the pointer leaves."""
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Draw the pause icon."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor("#1565c0")
        if self.isDown():
            color = QColor("#0d47a1")
        elif self.underMouse():
            color = QColor("#1e88e5")

        bar_width = 5.0
        bar_height = 18.0
        gap = 5.0
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        left_x = center_x - gap / 2.0 - bar_width
        right_x = center_x + gap / 2.0
        top_y = center_y - bar_height / 2.0

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(QRectF(left_x, top_y, bar_width, bar_height), 1.5, 1.5)
        painter.drawRoundedRect(QRectF(right_x, top_y, bar_width, bar_height), 1.5, 1.5)


class PlayButton(QPushButton):
    """Triangle play button for previewing a finished recording."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize play button."""
        super().__init__(parent)
        self.setFixedSize(_PLAY_BUTTON_SIZE, _PLAY_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Play recording")
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Repaint on hover."""
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: ANN001, N802
        """Repaint when hover ends."""
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Paint a right-pointing triangle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor("#2e7d32")
        if self.isDown():
            color = QColor("#1b5e20")
        elif self.underMouse():
            color = QColor("#43a047")

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        triangle_height = 18.0
        triangle_width = 16.0
        left = center_x - triangle_width / 2.0 + 1.0
        top = center_y - triangle_height / 2.0
        triangle = QPolygonF(
            [
                QPointF(left, top),
                QPointF(left, top + triangle_height),
                QPointF(left + triangle_width, center_y),
            ]
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawPolygon(triangle)


class RecordButton(QPushButton):
    """Record control: red ring + dot when idle, black rounded stop square while recording."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize record button."""
        super().__init__(parent)
        self._recording = False
        self.setFixedSize(_RECORD_BUTTON_SIZE, _RECORD_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Repaint on hover."""
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: ANN001, N802
        """Repaint when hover ends."""
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Paint record ring or stop square."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0

        if self._recording:
            stop_side = 22.0
            corner_radius = 5.0
            stop_color = QColor("#000000")
            if self.isDown():
                stop_color = QColor("#333333")
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(stop_color)
            painter.drawRoundedRect(
                QRectF(
                    center_x - stop_side / 2.0,
                    center_y - stop_side / 2.0,
                    stop_side,
                    stop_side,
                ),
                corner_radius,
                corner_radius,
            )
            return

        red = QColor("#e53935")
        if self.isDown():
            red = QColor("#c62828")
        elif self.underMouse():
            red = QColor("#ef5350")

        outer_radius = 23.0
        ring_width = 2.5
        inner_radius = 16.0

        painter.setPen(QPen(red, ring_width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(
            QRectF(
                center_x - outer_radius,
                center_y - outer_radius,
                outer_radius * 2.0,
                outer_radius * 2.0,
            )
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(red)
        painter.drawEllipse(
            QRectF(
                center_x - inner_radius,
                center_y - inner_radius,
                inner_radius * 2.0,
                inner_radius * 2.0,
            )
        )

    def set_recording(self, *, recording: bool) -> None:
        """Switch between record and stop appearance."""
        if self._recording != recording:
            self._recording = recording
            self.update()


class StopPlaybackButton(QPushButton):
    """Stop button for ending audio preview."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize stop button."""
        super().__init__(parent)
        self.setFixedSize(_PLAY_BUTTON_SIZE, _PLAY_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Stop playback")
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Highlight the stop icon on hover."""
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: ANN001, N802
        """Restore the stop icon when the pointer leaves."""
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Draw the stop icon."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor("#212121")
        if self.isDown():
            color = QColor("#000000")
        elif self.underMouse():
            color = QColor("#424242")

        side = 16.0
        corner_radius = 3.0
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(
            QRectF(center_x - side / 2.0, center_y - side / 2.0, side, side),
            corner_radius,
            corner_radius,
        )


def _audio_device_id(device: QAudioDevice) -> str:
    """Return a stable hex id for ``device``."""
    return device.id().data().hex()


def _format_file_size(num_bytes: int) -> str:
    """Return human-readable file size in B, KB, or MB."""
    if num_bytes < _BYTES_PER_KIB:
        return f"{num_bytes} B"
    if num_bytes < _BYTES_PER_MIB:
        return f"{num_bytes / _BYTES_PER_KIB:.1f} KB"
    return f"{num_bytes / _BYTES_PER_MIB:.2f} MB"


def _load_saved_microphone_id() -> str:
    """Load last used microphone id from config-temp."""
    try:
        temp_config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return ""
    return str(temp_config.get(_TEMP_MICROPHONE_ID_KEY, "")).strip()


def _normalize_pcm_to_int16_mono(pcm_data: bytes, audio_format: QAudioFormat) -> bytes:
    """Convert captured PCM to mono int16 suitable for standard WAV files."""
    if not pcm_data:
        return pcm_data

    sample_format = audio_format.sampleFormat()
    channel_count = max(1, audio_format.channelCount())

    if sample_format == QAudioFormat.SampleFormat.Float:
        floats = array.array("f")
        floats.frombytes(pcm_data)
        samples = array.array(
            "h",
            (max(-32768, min(32767, int(sample * 32767.0))) for sample in floats),
        )
    elif sample_format == QAudioFormat.SampleFormat.Int16:
        samples = array.array("h")
        samples.frombytes(pcm_data)
    elif sample_format == QAudioFormat.SampleFormat.Int32:
        ints32 = array.array("i")
        ints32.frombytes(pcm_data)
        samples = array.array("h", (max(-32768, min(32767, sample >> 16)) for sample in ints32))
    elif sample_format == QAudioFormat.SampleFormat.UInt8:
        samples = array.array("h", ((byte - 128) << 8 for byte in pcm_data))
    else:
        return pcm_data

    if channel_count == 1:
        return samples.tobytes()

    mono = array.array("h")
    for index in range(0, len(samples) - channel_count + 1, channel_count):
        mixed = sum(samples[index + channel] for channel in range(channel_count))
        mono.append(int(mixed / channel_count))
    return mono.tobytes()


def _pcm_chunk_envelope(pcm_data: bytes, audio_format: QAudioFormat) -> tuple[float, float]:
    """Return normalized negative and positive peaks for a PCM chunk."""
    if not pcm_data:
        return (0.0, 0.0)
    mono_pcm = _normalize_pcm_to_int16_mono(pcm_data, audio_format)
    samples = array.array("h")
    samples.frombytes(mono_pcm)
    if not samples:
        return (0.0, 0.0)
    peak_neg = min(samples) / 32768.0
    peak_pos = max(samples) / 32768.0
    peak_neg = max(-1.0, peak_neg * _LEVEL_GAIN)
    peak_pos = min(1.0, peak_pos * _LEVEL_GAIN)
    return (peak_neg, peak_pos)


def _read_wav_pcm(path: Path) -> tuple[tuple[int, int, int, int, str, str], bytes]:
    """Read WAV params and PCM frames from ``path``."""
    with wave.open(str(path), "rb") as wav_file:
        params = wav_file.getparams()
        return params, wav_file.readframes(wav_file.getnframes())


def _recording_format_for_device(device: QAudioDevice) -> QAudioFormat:
    """Pick a stable int16 capture format supported by the microphone."""
    for sample_rate, channel_count in ((16000, 1), (44100, 1), (48000, 1), (44100, 2)):
        audio_format = QAudioFormat()
        audio_format.setSampleRate(sample_rate)
        audio_format.setChannelCount(channel_count)
        audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        if device.isFormatSupported(audio_format):
            return audio_format
    return device.preferredFormat()


def _save_microphone_id(device: QAudioDevice) -> None:
    """Persist selected microphone id to config-temp."""
    try:
        temp_config_path = get_temp_config_path()
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
            temp_config_path.write_text("{}", encoding="utf-8")
        h.dev.config_update_value(
            _TEMP_MICROPHONE_ID_KEY,
            _audio_device_id(device),
            get_config_path_str(),
            is_temp=True,
        )
    except (FileNotFoundError, OSError, ValueError):
        return


def _wav_params_from_audio_format(audio_format: QAudioFormat) -> tuple[int, int, int, int, str, str]:
    """Return WAV header params for normalized int16 speech capture."""
    channels = 1 if audio_format.channelCount() > 1 else max(1, audio_format.channelCount())
    return (
        channels,
        2,
        audio_format.sampleRate(),
        0,
        "NONE",
        "not compressed",
    )


def _wav_params_match_audio_format(
    wav_params: tuple[int, int, int, int, str, str],
    audio_format: QAudioFormat,
) -> bool:
    expected = _wav_params_from_audio_format(audio_format)
    nchannels, sampwidth, framerate, *_rest = wav_params
    return nchannels == expected[0] and sampwidth == expected[1] and framerate == expected[2]


def _waveform_buckets_from_pcm(pcm_data: bytes, bucket_count: int) -> list[tuple[float, float]]:
    """Downsample mono int16 PCM to normalized waveform buckets."""
    if bucket_count <= 0:
        return []
    samples = array.array("h")
    samples.frombytes(pcm_data)
    if not samples:
        return [(0.0, 0.0)] * bucket_count

    buckets: list[tuple[float, float]] = []
    sample_count = len(samples)
    for bucket_index in range(bucket_count):
        start = bucket_index * sample_count // bucket_count
        end = (bucket_index + 1) * sample_count // bucket_count
        if start >= end:
            buckets.append((0.0, 0.0))
            continue
        chunk = samples[start:end]
        peak_neg = min(chunk) / 32768.0
        peak_pos = max(chunk) / 32768.0
        buckets.append((peak_neg, peak_pos))
    return buckets


def _write_wav(path: Path, params: tuple[int, int, int, int, str, str], pcm_data: bytes) -> None:
    """Write PCM frames to a WAV file."""
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setparams(params)
        wav_file.writeframes(pcm_data)
