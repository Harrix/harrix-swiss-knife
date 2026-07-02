"""BotHub speech transcription helpers."""

from __future__ import annotations

from pathlib import Path

TRANSCRIPTION_PROMPT = (
    "Transcribe the speech in this audio accurately and verbatim. "
    "Return only the transcribed text without comments or formatting."
)

_FORMAT_BY_SUFFIX: dict[str, str] = {
    ".wav": "wav",
    ".mp3": "mp3",
    ".m4a": "mp3",
    ".ogg": "mp3",
    ".webm": "mp3",
}


def audio_format_from_suffix(suffix: str) -> str | None:
    """Map a file suffix to BotHub input_audio format, or None if unsupported."""
    return _FORMAT_BY_SUFFIX.get(suffix.lower())


def audio_bytes_and_format(path: str | Path) -> tuple[bytes, str]:
    """Read an audio file and return its bytes and BotHub input_audio format.

    Raises:

    - `ValueError`: If the file extension is not supported.

    """
    file_path = Path(path)
    audio_format = audio_format_from_suffix(file_path.suffix)
    if audio_format is None:
        msg = f"Unsupported audio format: {file_path.suffix}"
        raise ValueError(msg)
    return file_path.read_bytes(), audio_format


def build_transcription_prompt() -> str:
    """Return the built-in prompt for speech-to-text requests."""
    return TRANSCRIPTION_PROMPT
