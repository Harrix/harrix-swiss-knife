"""Tests for BotHub audio transcription helpers."""

from __future__ import annotations

import base64
import json
from typing import Self
from unittest.mock import MagicMock

import pytest

from harrix_swiss_knife.integrations.bothub.config import get_speech_model
from harrix_swiss_knife.integrations.bothub.speech import (
    MIN_AUDIO_BYTES,
    audio_bytes_and_mime,
    audio_format_from_suffix,
    build_transcription_prompt,
    validate_audio_bytes,
)
from harrix_swiss_knife.integrations.bothub_client import chat_completion


def test_audio_format_from_suffix() -> None:
    assert audio_format_from_suffix(".wav") == "audio/wav"
    assert audio_format_from_suffix(".WAV") == "audio/wav"
    assert audio_format_from_suffix(".mp3") == "audio/mpeg"
    assert audio_format_from_suffix(".m4a") == "audio/mp4"
    assert audio_format_from_suffix(".txt") is None


def test_audio_bytes_and_mime(tmp_path: object) -> None:
    audio_file = tmp_path / "sample.wav"  # type: ignore[operator]
    audio_file.write_bytes(b"RIFF" + b"x" * MIN_AUDIO_BYTES)
    data, mime = audio_bytes_and_mime(audio_file)
    assert len(data) >= MIN_AUDIO_BYTES
    assert mime == "audio/wav"


def test_validate_audio_bytes_rejects_small_payload() -> None:
    with pytest.raises(ValueError, match="too short"):
        validate_audio_bytes(b"tiny")


def test_build_transcription_prompt_is_non_empty() -> None:
    assert build_transcription_prompt().strip()


def test_get_speech_model_from_config() -> None:
    config = {"bothub": {"speech_model": "gemini-3.1-flash-lite-preview"}}
    assert get_speech_model(config) == "gemini-3.1-flash-lite-preview"


def test_chat_completion_payload_sends_audio_as_data_uri(monkeypatch: pytest.MonkeyPatch) -> None:
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
        audio=(audio_bytes, "audio/wav"),
    )

    assert result == "hello"
    payload = json.loads(captured["body"].decode("utf-8"))
    content = payload["messages"][0]["content"]
    assert isinstance(content, list)
    assert content[0] == {"type": "text", "text": "Transcribe this"}
    audio_part = content[1]
    assert audio_part["type"] == "image_url"
    expected_url = f"data:audio/wav;base64,{base64.b64encode(audio_bytes).decode('ascii')}"
    assert audio_part["image_url"]["url"] == expected_url
