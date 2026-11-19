"""Optional on-device speech-to-text via faster-whisper (cloud first)."""

from __future__ import annotations

import importlib
import tempfile
from pathlib import Path
from typing import Any

from harrix_swiss_knife.integrations.ai.config import get_ai_section
from harrix_swiss_knife.integrations.ai.network_errors import (
    BOTHUB_UNREACHABLE_MSG,
    is_connect_timeout_message,
)

LOCAL_SPEECH_FIX_SKIPPED_NOTE = "(AI text fix skipped: cloud unreachable.)"
_MIME_SUFFIX: dict[str, str] = {
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/mp4": ".m4a",
    "audio/m4a": ".m4a",
    "audio/ogg": ".ogg",
    "audio/webm": ".webm",
}
_UNREACHABLE_MARKERS = (
    "cannot connect",
    "network error",
    "unreachable",
    "failed to connect",
    "name or service not known",
    "nodename nor servname",
    "temporary failure in name resolution",
)


def is_ai_unreachable_error(message: str) -> bool:
    """Return whether `message` means the AI host could not be reached."""
    text = (message or "").strip()
    if not text:
        return False
    if BOTHUB_UNREACHABLE_MSG in text:
        return True
    if is_connect_timeout_message(text):
        return True
    lower = text.lower()
    return any(marker in lower for marker in _UNREACHABLE_MARKERS)


def is_local_speech_enabled(config: dict[str, Any]) -> bool:
    """Return whether optional local speech fallback is enabled in config."""
    section = _local_speech_section(config)
    return bool(section.get("enabled"))


def local_speech_model_size(config: dict[str, Any]) -> str:
    """Return Whisper model size for local speech (`small` by default)."""
    section = _local_speech_section(config)
    model = str(section.get("model") or "small").strip()
    return model or "small"


def transcribe_audio_local(
    audio: tuple[bytes, str],
    *,
    model_size: str = "small",
) -> str:
    """Transcribe `audio` with faster-whisper.

    Raises:

    - `RuntimeError`: When faster-whisper is missing or transcription fails.
    - `ValueError`: When the transcript is empty.

    """
    data, mime = audio
    if not data:
        msg = "Empty audio for local speech recognition"
        raise ValueError(msg)

    try:
        whisper = importlib.import_module("faster_whisper")
    except ImportError as exc:
        msg = "Local speech requires the optional package faster-whisper. Install with: uv sync --extra local-speech"
        raise RuntimeError(msg) from exc

    suffix = _suffix_for_mime(mime)
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(data)
        temp_path = Path(handle.name)

    try:
        model = whisper.WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, _info = model.transcribe(str(temp_path), beam_size=1)
        text = " ".join(segment.text.strip() for segment in segments if segment.text.strip()).strip()
    except Exception as exc:
        msg = f"Local speech recognition failed: {exc}"
        raise RuntimeError(msg) from exc
    finally:
        temp_path.unlink(missing_ok=True)

    if not text:
        msg = "Empty transcription from local speech model"
        raise ValueError(msg)
    return text


def _local_speech_section(config: dict[str, Any]) -> dict[str, Any]:
    ai_cfg = get_ai_section(config)
    section = ai_cfg.get("local_speech")
    return section if isinstance(section, dict) else {}


def _suffix_for_mime(mime: str) -> str:
    key = (mime or "").split(";")[0].strip().lower()
    return _MIME_SUFFIX.get(key, ".wav")
