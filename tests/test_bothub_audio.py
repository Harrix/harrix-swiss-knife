"""Tests for BotHub audio transcription helpers."""

from __future__ import annotations

import base64
import json
from typing import TYPE_CHECKING, Self
from unittest.mock import MagicMock

from harrix_swiss_knife.integrations.bothub.config import get_speech_model
from harrix_swiss_knife.integrations.bothub.speech import (
    audio_bytes_and_format,
    audio_format_from_suffix,
    build_transcription_prompt,
)
from harrix_swiss_knife.integrations.bothub_client import chat_completion

if TYPE_CHECKING:
    import pytest


def test_audio_format_from_suffix() -> None:
    assert audio_format_from_suffix(".wav") == "wav"
    assert audio_format_from_suffix(".WAV") == "wav"
    assert audio_format_from_suffix(".mp3") == "mp3"
    assert audio_format_from_suffix(".m4a") == "mp3"
    assert audio_format_from_suffix(".txt") is None


def test_audio_bytes_and_format(tmp_path: object) -> None:
    audio_file = tmp_path / "sample.wav"  # type: ignore[operator]
    audio_file.write_bytes(b"RIFF")
    data, fmt = audio_bytes_and_format(audio_file)
    assert data == b"RIFF"
    assert fmt == "wav"


def test_build_transcription_prompt_is_non_empty() -> None:
    assert build_transcription_prompt().strip()


def test_get_speech_model_from_config() -> None:
    config = {"bothub": {"speech_model": "gemini-3.1-flash-lite-preview"}}
    assert get_speech_model(config) == "gemini-3.1-flash-lite-preview"


def test_chat_completion_payload_includes_input_audio(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, bytes] = {}

    class _FakeResponse:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "choices": [
                        {"message": {"content": "hello"}},
                    ],
                },
            ).encode("utf-8")

    def _fake_open(request, timeout: int = 0) -> _FakeResponse:  # noqa: ARG001
        captured["body"] = request.data
        return _FakeResponse()

    fake_opener = MagicMock()
    fake_opener.open = _fake_open
    monkeypatch.setattr(
        "harrix_swiss_knife.integrations.bothub_client.build_https_opener",
        lambda _proxy_url: fake_opener,
    )

    audio_bytes = b"test-audio"
    result = chat_completion(
        api_key="test-key",
        base_url="https://bothub.chat/api/v2/openai/v1",
        model="gemini-3.1-flash-lite-preview",
        text="Transcribe this",
        audio=(audio_bytes, "wav"),
    )

    assert result == "hello"
    payload = json.loads(captured["body"].decode("utf-8"))
    content = payload["messages"][0]["content"]
    assert isinstance(content, list)
    audio_part = next(part for part in content if part.get("type") == "input_audio")
    assert audio_part["input_audio"]["format"] == "wav"
    assert audio_part["input_audio"]["data"] == base64.b64encode(audio_bytes).decode("ascii")
    text_part = next(part for part in content if part.get("type") == "text")
    assert text_part["text"] == "Transcribe this"
