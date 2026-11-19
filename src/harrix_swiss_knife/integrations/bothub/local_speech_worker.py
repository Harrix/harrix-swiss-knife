"""Background worker for optional local speech-to-text."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal

from harrix_swiss_knife.integrations.ai.local_speech import transcribe_audio_local


class LocalSpeechWorker(QThread):
    """Run faster-whisper transcription off the UI thread."""

    finished_success = Signal(str)
    finished_error = Signal(str)

    def __init__(
        self,
        audio: tuple[bytes, str],
        *,
        model_size: str = "small",
        parent: QObject | None = None,
    ) -> None:
        """Store audio bytes and the Whisper model size for `run`."""
        super().__init__(parent)
        self._audio = audio
        self._model_size = model_size

    def run(self) -> None:
        """Transcribe on this thread and emit success or error."""
        if self.isInterruptionRequested():
            self.finished_error.emit("Local speech cancelled.")
            return
        try:
            text = transcribe_audio_local(self._audio, model_size=self._model_size)
        except (OSError, RuntimeError, ValueError) as exc:
            self.finished_error.emit(str(exc))
            return
        if self.isInterruptionRequested():
            self.finished_error.emit("Local speech cancelled.")
            return
        self.finished_success.emit(text)
