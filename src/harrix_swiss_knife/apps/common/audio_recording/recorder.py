"""Microphone capture session with finalize to WAV/M4A."""

from __future__ import annotations

import uuid
import wave
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtMultimedia import QAudioDevice, QAudioFormat, QAudioSource, QMediaDevices

from harrix_swiss_knife.apps.common.audio_compress import FfmpegNotFoundError, wav_to_m4a
from harrix_swiss_knife.apps.common.audio_recording.pcm_utils import (
    audio_device_id,
    format_file_size,
    load_saved_microphone_id,
    normalize_pcm_to_int16_mono,
    pcm_chunk_envelope,
    read_wav_pcm,
    recording_duration_from_pcm,
    recording_format_for_device,
    save_microphone_id,
    trim_edge_silence_int16_mono,
    wav_params_from_audio_format,
    wav_params_match_audio_format,
    write_wav,
)
from harrix_swiss_knife.integrations.bothub.speech import MIN_AUDIO_BYTES
from harrix_swiss_knife.paths import get_project_root


@dataclass
class FinalizeResult:
    """Result of stopping and writing a recording."""

    success: bool
    recorded_path: str = ""
    recording_wav_path: str = ""
    normalized_pcm: bytes = b""
    message: str = ""
    ffmpeg_warning: str = ""


class MicrophoneRecorder(QObject):
    """Capture microphone PCM, emit live envelopes, and finalize to an audio file."""

    envelope_ready = Signal(float, float)
    recording_started = Signal()
    recording_stopped = Signal()
    finalized = Signal(object)
    start_failed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize microphone recorder."""
        super().__init__(parent)
        self._state = _RecorderState()
        self._audio_source: QAudioSource | None = None
        self._audio_io = None

    def can_continue(self) -> bool:
        """Return whether continue-from-WAV is available."""
        return (
            bool(self._state.recording_wav_path)
            and Path(self._state.recording_wav_path).is_file()
            and bool(self._state.recorded_path)
        )

    def clear(self) -> None:
        """Clear finalized recording paths (does not stop an active capture)."""
        self._state.recorded_path = ""
        self._state.recording_wav_path = ""

    def duration_seconds(self) -> float:
        """Return duration of buffered PCM in seconds."""
        if self._state.wav_params is None:
            return 0.0
        sample_rate = self._state.wav_params[2]
        if sample_rate <= 0:
            return 0.0
        pcm_data = b"".join(self._state.pcm_chunks)
        return recording_duration_from_pcm(pcm_data, sample_rate)

    @property
    def is_recording(self) -> bool:
        """Return whether capture is active."""
        return self._state.is_recording

    @staticmethod
    def list_input_devices() -> list[QAudioDevice]:
        """Return available microphone devices."""
        return list(QMediaDevices.audioInputs())

    @property
    def recorded_path(self) -> str:
        """Return path to the last finalized recording (WAV or M4A)."""
        return self._state.recorded_path

    @property
    def recording_wav_path(self) -> str:
        """Return path to the WAV used for continue-recording."""
        return self._state.recording_wav_path

    def release(self) -> None:
        """Abort capture without finalizing and free multimedia handles."""
        if self._state.is_recording:
            if self._audio_source is not None:
                self._audio_source.stop()
            self._state.is_recording = False
            self._state.pcm_chunks = []
        self._cleanup_handles()

    @staticmethod
    def resolve_input_device(preferred_id: str = "") -> QAudioDevice | None:
        """Pick saved, preferred, or default microphone device."""
        devices = MicrophoneRecorder.list_input_devices()
        if not devices:
            return None

        saved_id = preferred_id or load_saved_microphone_id()
        if saved_id:
            for device in devices:
                if audio_device_id(device) == saved_id:
                    return device

        default_device = QMediaDevices.defaultAudioInput()
        for device in devices:
            if audio_device_id(device) == audio_device_id(default_device):
                return device
        return devices[0]

    @staticmethod
    def save_device(device: QAudioDevice) -> None:
        """Persist selected microphone ID."""
        save_microphone_id(device)

    def start(self, device: QAudioDevice, *, append: bool = False) -> StartResult:
        """Start microphone capture. Returns whether start succeeded."""
        if self._state.is_recording:
            return StartResult(success=False, message="Already recording")

        self._state.audio_format = recording_format_for_device(device)
        new_params = wav_params_from_audio_format(self._state.audio_format)

        if append:
            if not self._state.recording_wav_path:
                append = False
            else:
                recorded_path = Path(self._state.recording_wav_path)
            if append and not recorded_path.exists():
                append = False
            if append:
                try:
                    existing_params, existing_pcm = read_wav_pcm(recorded_path)
                except (OSError, wave.Error) as exc:
                    message = f"Cannot continue recording: {exc}"
                    self.start_failed.emit(message)
                    return StartResult(success=False, message=message)
                if not wav_params_match_audio_format(existing_params, self._state.audio_format):
                    message = "Cannot continue: microphone format changed. Start over."
                    self.start_failed.emit(message)
                    return StartResult(success=False, message=message)
                self._state.recording_path = recorded_path
                self._state.wav_params = existing_params
                self._state.pcm_chunks = [existing_pcm] if existing_pcm else []

        if not append:
            self._state.recording_path = self._new_recording_path()
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self._state.wav_params = new_params
            self._state.pcm_chunks = []

        try:
            self._audio_source = QAudioSource(device, self._state.audio_format, self)
            self._audio_io = self._audio_source.start()
            self._audio_io.readyRead.connect(self._on_audio_ready)
        except OSError as exc:
            self._cleanup_handles()
            message = f"Recording error: {exc}"
            self.start_failed.emit(message)
            return StartResult(success=False, message=message)

        self._state.is_recording = True
        self.recording_started.emit()
        return StartResult(success=True)

    def stop(self) -> None:
        """Stop capture and schedule finalize."""
        if not self._state.is_recording:
            return
        if self._audio_source is not None:
            self._audio_source.stop()
        self._cleanup_handles()
        self._state.is_recording = False
        self.recording_stopped.emit()
        QTimer.singleShot(100, self._finalize)

    def _cleanup_handles(self) -> None:
        if self._audio_io is not None:
            with suppress(RuntimeError, TypeError):
                self._audio_io.readyRead.disconnect(self._on_audio_ready)
            self._audio_io = None
        if self._audio_source is not None:
            source = self._audio_source
            self._audio_source = None
            source.stop()
            source.setParent(None)
            source.deleteLater()

    def _finalize(self) -> None:
        output = self._state.recording_path
        pcm_data = b"".join(self._state.pcm_chunks)
        self._state.pcm_chunks = []

        if not output or not pcm_data or self._state.wav_params is None:
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self.finalized.emit(FinalizeResult(success=False, message="Recording stopped"))
            return

        try:
            wav_params = wav_params_from_audio_format(self._state.audio_format)
            normalized_pcm = normalize_pcm_to_int16_mono(pcm_data, self._state.audio_format)
            normalized_pcm = trim_edge_silence_int16_mono(normalized_pcm, wav_params[2])
            write_wav(output, wav_params, normalized_pcm)
        except OSError as exc:
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self.finalized.emit(FinalizeResult(success=False, message=f"Recording error: {exc}"))
            return

        size = output.stat().st_size
        if size < MIN_AUDIO_BYTES:
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self.finalized.emit(
                FinalizeResult(
                    success=False,
                    message=f"Recording too short ({format_file_size(size)}). Try again.",
                )
            )
            return

        final_path = output
        ffmpeg_warning = ""
        try:
            final_path = wav_to_m4a(output, project_root=get_project_root())
            self._state.recording_wav_path = str(output)
        except FfmpegNotFoundError:
            ffmpeg_warning = " (ffmpeg not found — saved as WAV, file is large)"
            self._state.recording_wav_path = str(output)
        except RuntimeError as exc:
            self._state.recorded_path = ""
            self._state.recording_wav_path = ""
            self.finalized.emit(FinalizeResult(success=False, message=f"Recording error: {exc}"))
            return

        self._state.recorded_path = str(final_path)
        self.finalized.emit(
            FinalizeResult(
                success=True,
                recorded_path=str(final_path),
                recording_wav_path=self._state.recording_wav_path,
                normalized_pcm=normalized_pcm,
                message="Ready for recognition:",
                ffmpeg_warning=ffmpeg_warning,
            )
        )

    @staticmethod
    def _new_recording_path() -> Path:
        temp_dir = get_project_root() / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir / f"hsk-speech-{uuid.uuid4().hex}.wav"

    def _on_audio_ready(self) -> None:
        if self._audio_io is None:
            return
        data = bytes(self._audio_io.readAll().data())
        if not data:
            return
        self._state.pcm_chunks.append(data)
        peak_neg, peak_pos = pcm_chunk_envelope(data, self._state.audio_format)
        self.envelope_ready.emit(peak_neg, peak_pos)


@dataclass
class StartResult:
    """Result of attempting to start capture."""

    success: bool
    message: str = ""


@dataclass
class _RecorderState:
    recorded_path: str = ""
    recording_wav_path: str = ""
    is_recording: bool = False
    audio_format: QAudioFormat = field(default_factory=QAudioFormat)
    recording_path: Path = field(default_factory=Path)
    pcm_chunks: list[bytes] = field(default_factory=list)
    wav_params: tuple[int, int, int, int, str, str] | None = None
