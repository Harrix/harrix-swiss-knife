"""Tests for multi-provider AI config and payload builders."""

from __future__ import annotations

import base64
import json

import pytest

from harrix_swiss_knife.integrations.ai.anthropic import (
    build_anthropic_payload,
    parse_anthropic_response,
)
from harrix_swiss_knife.integrations.ai.config import (
    get_api_key,
    get_chat_provider,
    get_connection_params_for_provider,
    get_max_image_side,
    get_speech_model_for_provider,
    get_speech_provider,
    normalize_provider,
    provider_supports_speech,
)
from harrix_swiss_knife.integrations.ai.errors import AiApiError
from harrix_swiss_knife.integrations.ai.gemini import build_gemini_payload, parse_gemini_response
from harrix_swiss_knife.integrations.ai.openai_compat import build_openai_chat_payload
from harrix_swiss_knife.integrations.ai.openai_speech import parse_whisper_response
from harrix_swiss_knife.integrations.bothub.config import get_connection_params, get_speech_model


def test_normalize_provider_unknown_falls_back_to_bothub() -> None:
    assert normalize_provider("unknown") == "bothub"
    assert normalize_provider("") == "bothub"
    assert normalize_provider("OpenAI") == "openai"


def test_get_chat_provider_defaults_to_bothub() -> None:
    assert get_chat_provider({}) == "bothub"
    assert get_chat_provider({"ai": {"provider": "gemini"}}) == "gemini"


def test_get_speech_provider_falls_back_to_chat() -> None:
    config = {"ai": {"provider": "anthropic", "speech_provider": ""}}
    assert get_speech_provider(config) == "anthropic"
    config["ai"]["speech_provider"] = "openai"
    assert get_speech_provider(config) == "openai"


def test_provider_supports_speech() -> None:
    assert provider_supports_speech("bothub")
    assert provider_supports_speech("openai")
    assert provider_supports_speech("gemini")
    assert not provider_supports_speech("anthropic")


def test_get_api_key_and_connection_params(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("https_proxy", raising=False)
    monkeypatch.delenv("http_proxy", raising=False)

    config = {
        "ai": {"provider": "openai", "proxy": ""},
        "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-4.1", "speech_model": "whisper-1"},
        "openai_api_key": "sk-test",
        "bothub": {"proxy": ""},
    }
    assert get_api_key(config, "openai") == "sk-test"
    api_key, base_url, model, _proxy = get_connection_params_for_provider(config, "openai")
    assert api_key == "sk-test"
    assert base_url == "https://api.openai.com/v1"
    assert model == "gpt-4.1"
    assert get_speech_model_for_provider(config, "openai") == "whisper-1"


def test_get_connection_params_uses_active_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("https_proxy", raising=False)
    monkeypatch.delenv("http_proxy", raising=False)

    config = {
        "ai": {"provider": "gemini"},
        "gemini": {
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "model": "gemini-2.5-flash",
            "speech_model": "gemini-2.5-flash",
        },
        "gemini_api_key": "gem-key",
        "bothub_api_key": "bothub-key",
        "bothub": {"proxy": ""},
    }
    api_key, base_url, model, _ = get_connection_params(config)
    assert api_key == "gem-key"
    assert "generativelanguage" in base_url
    assert model == "gemini-2.5-flash"
    assert get_speech_model(config) == "gemini-2.5-flash"


def test_get_max_image_side_prefers_ai() -> None:
    assert get_max_image_side({"ai": {"max_image_side": 800}, "bothub": {"max_image_side": 1600}}) == 800
    assert get_max_image_side({"bothub": {"max_image_side": 1200}}) == 1200
    assert get_max_image_side({}) == 1600


def test_build_openai_chat_payload_text_only() -> None:
    payload = build_openai_chat_payload(model="gpt-4.1", text="hello")
    assert payload["model"] == "gpt-4.1"
    assert payload["messages"][0]["content"] == "hello"


def test_build_openai_chat_payload_with_image_and_audio() -> None:
    payload = build_openai_chat_payload(
        model="gpt-5.4",
        text="ocr",
        images=[(b"img", "image/png")],
        audio=(b"wav", "audio/wav"),
        allow_audio_as_image_url=True,
    )
    content = payload["messages"][0]["content"]
    assert isinstance(content, list)
    assert content[0]["type"] == "text"
    assert content[1]["type"] == "image_url"
    assert content[2]["type"] == "image_url"
    assert "data:image/png;base64," in content[1]["image_url"]["url"]
    assert "data:audio/wav;base64," in content[2]["image_url"]["url"]


def test_build_openai_chat_payload_openai_skips_audio_as_image() -> None:
    payload = build_openai_chat_payload(
        model="gpt-4.1",
        text="hi",
        audio=(b"wav", "audio/wav"),
        allow_audio_as_image_url=False,
    )
    assert payload["messages"][0]["content"] == "hi"


def test_build_anthropic_payload() -> None:
    payload = build_anthropic_payload(
        model="claude-sonnet-4-6",
        text="describe",
        images=[(b"png-bytes", "image/png")],
        max_tokens=4096,
    )
    assert payload["model"] == "claude-sonnet-4-6"
    assert payload["max_tokens"] == 4096
    content = payload["messages"][0]["content"]
    assert content[0]["type"] == "image"
    assert content[0]["source"]["data"] == base64.b64encode(b"png-bytes").decode("ascii")
    assert content[1] == {"type": "text", "text": "describe"}


def test_parse_anthropic_response() -> None:
    raw = json.dumps({"content": [{"type": "text", "text": "Hello"}]})
    assert parse_anthropic_response(raw) == "Hello"


def test_build_gemini_payload_with_audio() -> None:
    payload = build_gemini_payload(text="transcribe", audio=(b"aud", "audio/wav"))
    parts = payload["contents"][0]["parts"]
    assert parts[0] == {"text": "transcribe"}
    assert parts[1]["inline_data"]["mime_type"] == "audio/wav"
    assert parts[1]["inline_data"]["data"] == base64.b64encode(b"aud").decode("ascii")


def test_parse_gemini_response() -> None:
    raw = json.dumps({"candidates": [{"content": {"parts": [{"text": "ok"}]}}]})
    assert parse_gemini_response(raw) == "ok"


def test_parse_whisper_response() -> None:
    assert parse_whisper_response(json.dumps({"text": " spoken "})) == "spoken"
    with pytest.raises(AiApiError, match="Empty transcription"):
        parse_whisper_response(json.dumps({"text": ""}))
