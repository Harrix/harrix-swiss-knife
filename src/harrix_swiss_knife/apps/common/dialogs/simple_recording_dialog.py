"""Compact microphone dialog with recording, saving, and recognition controls."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtMultimedia import QAudioDevice
from PySide6.QtWidgets import QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.audio_recording import (
    RECORD_CAPTION_STOP_STYLE,
    AudioLevelWidget,
    ClickableLabel,
    FinalizeResult,
    MicrophoneRecorder,
    RecordButton,
    audio_device_id,
    load_saved_microphone_id,
)
from harrix_swiss_knife.qt_emoji_icon import SAVE_BUTTON_EMOJI, make_emoji_push_button

if TYPE_CHECKING:
    from PySide6.QtGui import QShowEvent


class SimpleRecordingDialog(QDialog):
    """Modal dialog that records audio and lets the user save or recognize it."""

    def __init__(self, parent: QWidget | None = None, *, large_ui: bool = False) -> None:
        """Initialize the simple recording dialog."""
        super().__init__(parent)
        self._large_ui = large_ui
        self._audio_path = ""
        self._auto_start_scheduled = False
        self._finalize_pending = False
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
        self._finalize_pending = False
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
        if self._finalize_pending:
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
        self._save_button.setVisible(False)
        self._recognize_button.setVisible(False)
        self._status_label.clear()
        self._status_label.setVisible(False)
        self._start_recording_with_current_device()

    def _on_recognize_clicked(self) -> None:
        if not self._audio_path:
            return
        self.release_multimedia()
        self.accept()

    def _on_recording_finalized(self, result: object) -> None:
        if not isinstance(result, FinalizeResult):
            return
        if not result.success:
            self._finalize_pending = False
            self._update_stop_button()
            self._status_label.setText(result.message or "Recording stopped")
            self._status_label.setVisible(True)
            self._level_widget.clear()
            return

        self._finalize_pending = False
        self._update_stop_button()
        self._audio_path = result.recorded_path
        if result.normalized_pcm:
            self._level_widget.show_overview(result.normalized_pcm)
        self._status_label.clear()
        self._status_label.setVisible(False)
        self._save_button.setVisible(True)
        self._save_button.setEnabled(True)
        self._recognize_button.setVisible(True)
        self._recognize_button.setEnabled(True)

    def _on_recording_started(self) -> None:
        self._status_label.clear()
        self._status_label.setVisible(False)
        self._save_button.setVisible(False)
        self._recognize_button.setVisible(False)
        self._level_widget.begin_live()
        self._update_stop_button()

    def _on_recording_stopped(self) -> None:
        self._update_stop_button()

    def _on_save_clicked(self) -> None:
        source = Path(self._audio_path)
        if not source.is_file():
            return
        suffix = source.suffix.lower()
        filters = {
            ".m4a": "M4A Audio (*.m4a);;All Files (*)",
            ".wav": "WAV Audio (*.wav);;All Files (*)",
        }
        destination, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save audio",
            source.name,
            filters.get(suffix, "Audio Files (*);;All Files (*)"),
        )
        if not destination:
            return
        destination_path = Path(destination)
        if not destination_path.suffix:
            destination_path = destination_path.with_suffix(suffix)
        try:
            if source.resolve() != destination_path.resolve():
                shutil.copy2(source, destination_path)
        except OSError as exc:
            message_box.critical(self, "Save Audio", f"Could not save audio:\n{exc}")
            return
        self._status_label.setText(f"Saved to {destination_path}")
        self._status_label.setVisible(True)

    def _on_start_failed(self, message: str) -> None:
        self._status_label.setText(message)
        self._status_label.setVisible(True)
        self._update_stop_button()

    def _on_stop_clicked(self) -> None:
        if not self._recorder.is_recording:
            return
        self._finalize_pending = True
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
                self._update_stop_button()
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
        if self._large_ui:
            self.setMinimumSize(720, 420)
        else:
            self.setMinimumSize(480, 260)
        qt_modality.set_owner_window_modal(self)

        layout = QVBoxLayout(self)

        mic_label = QLabel("Microphone:")
        layout.addWidget(mic_label)

        self._microphone_combo = QComboBox()
        self._microphone_combo.currentIndexChanged.connect(self._on_microphone_changed)
        layout.addWidget(self._microphone_combo)

        self._level_widget = AudioLevelWidget()
        self._level_widget.setStyleSheet("background-color: #1e1e1e; border: 1px solid #424242; border-radius: 6px;")
        self._level_widget.setMinimumHeight(140 if self._large_ui else 96)
        layout.addWidget(self._level_widget)

        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 16, 0, 8)
        controls.setAlignment(Qt.AlignmentFlag.AlignBottom)
        controls.addStretch()

        column = QVBoxLayout()
        column.setSpacing(12)
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

        cancel_button = make_emoji_push_button("Cancel", "❌")
        cancel_button.clicked.connect(self.reject)
        controls.addWidget(cancel_button, alignment=Qt.AlignmentFlag.AlignBottom)

        self._save_button = make_emoji_push_button("Save audio", SAVE_BUTTON_EMOJI)
        self._save_button.clicked.connect(self._on_save_clicked)
        self._save_button.setVisible(False)
        controls.addWidget(self._save_button, alignment=Qt.AlignmentFlag.AlignBottom)

        self._recognize_button = make_emoji_push_button("Recognize", "🤖")
        self._recognize_button.clicked.connect(self._on_recognize_clicked)
        self._recognize_button.setVisible(False)
        controls.addWidget(self._recognize_button, alignment=Qt.AlignmentFlag.AlignBottom)

        layout.addLayout(controls)
        if self._large_ui:
            self.setStyleSheet(
                """
                QLabel { font-size: 14pt; }
                QComboBox { min-height: 40px; font-size: 14pt; }
                QPushButton { min-height: 48px; font-size: 14pt; padding: 8px 16px; }
                """
            )
            self._stop_caption.setStyleSheet(f"{RECORD_CAPTION_STOP_STYLE} QLabel {{ font-size: 15pt; }}")
        self._update_stop_button()

    def _start_recording_with_current_device(self) -> None:
        if self._finalize_pending:
            return
        if self._recorder.is_recording:
            return

        device = self._current_input_device()
        if device is None:
            self._status_label.setText("No microphone found")
            self._status_label.setVisible(True)
            self._update_stop_button()
            return

        MicrophoneRecorder.save_device(device)
        result = self._recorder.start(device, append=False)
        if not result.success:
            self._status_label.setText(result.message or "Recording error")
            self._status_label.setVisible(True)
            self._update_stop_button()

    def _update_stop_button(self) -> None:
        recording = self._recorder.is_recording
        finalize_pending = self._finalize_pending
        show_stop = recording or finalize_pending
        self._stop_button.setVisible(show_stop)
        self._stop_caption.setVisible(show_stop)
        self._stop_button.set_recording(recording=recording or finalize_pending)
        self._stop_button.setEnabled(recording)
        self._stop_caption.setEnabled(recording)
        if not finalize_pending:
            self._microphone_combo.setEnabled(
                self._microphone_combo.count() > 0 and self._current_input_device() is not None
            )
