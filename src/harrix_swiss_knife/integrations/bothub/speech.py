"""BotHub speech transcription helpers."""

from __future__ import annotations

from pathlib import Path

TRANSCRIPTION_PROMPT = (
    "Transcribe the speech in this audio accurately and verbatim. "
    "Return only the transcribed text without comments or formatting."
)

MIN_AUDIO_BYTES = 512

_MIME_BY_SUFFIX: dict[str, str] = {
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".webm": "audio/webm",
}


def audio_format_from_suffix(suffix: str) -> str | None:
    """Map a file suffix to MIME type, or None if unsupported."""
    return _MIME_BY_SUFFIX.get(suffix.lower())


def audio_bytes_and_mime(path: str | Path) -> tuple[bytes, str]:
    """Read an audio file and return its bytes and MIME type.

    Raises:

    - `ValueError`: If the file extension is not supported or the file is too small.

    """
    file_path = Path(path)
    mime_type = audio_format_from_suffix(file_path.suffix)
    if mime_type is None:
        msg = f"Unsupported audio format: {file_path.suffix}"
        raise ValueError(msg)
    data = file_path.read_bytes()
    validate_audio_bytes(data, file_path.name)
    return data, mime_type


def validate_audio_bytes(data: bytes, label: str = "audio") -> None:
    """Raise ValueError when audio payload is empty or too small to be valid."""
    if len(data) < MIN_AUDIO_BYTES:
        msg = f"{label} is empty or too short ({len(data)} bytes). Record longer or choose another file."
        raise ValueError(msg)


def build_transcription_prompt() -> str:
    """Return the built-in prompt for speech-to-text requests."""
    return TRANSCRIPTION_PROMPT
