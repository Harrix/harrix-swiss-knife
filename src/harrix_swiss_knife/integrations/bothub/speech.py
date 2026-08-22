"""BotHub speech transcription helpers."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.paths import get_project_root

TRANSCRIPTION_PROMPT_PATH = Path("config") / "prompts" / "speech-transcription.md"

TRANSCRIPTION_PROMPT = (
    "Transcribe the speech in this audio accurately and verbatim. "
    "The speech is usually Russian, with occasional English words mixed in, especially IT terms. "
    "Write those English words as English, not as Russian transliteration. "
    "For example: API, Docker, commit, pull request, backend. "
    "Return only the transcribed text without comments or formatting."
)

MIN_AUDIO_BYTES = 512

_MIME_BY_SUFFIX: dict[str, str] = {
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/m4a",
    ".ogg": "audio/ogg",
    ".webm": "audio/webm",
}


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


def audio_format_from_suffix(suffix: str) -> str | None:
    """Map a file suffix to MIME type, or `None` if unsupported."""
    return _MIME_BY_SUFFIX.get(suffix.lower())


def build_transcription_prompt() -> str:
    """Return the speech-to-text prompt from `config/prompts`, or the built-in fallback."""
    path = get_project_root() / TRANSCRIPTION_PROMPT_PATH
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        text = ""
    return text or TRANSCRIPTION_PROMPT


def validate_audio_bytes(data: bytes, label: str = "audio") -> None:
    """Raise ValueError when audio payload is empty or too small to be valid."""
    if len(data) < MIN_AUDIO_BYTES:
        msg = f"{label} is empty or too short ({len(data)} bytes). Record longer or choose another file."
        raise ValueError(msg)
