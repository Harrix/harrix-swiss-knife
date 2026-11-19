"""Tests for optional local speech helpers."""

from __future__ import annotations

from harrix_swiss_knife.integrations.ai.local_speech import (
    is_ai_unreachable_error,
    is_local_speech_enabled,
    local_speech_model_size,
)
from harrix_swiss_knife.integrations.ai.network_errors import BOTHUB_UNREACHABLE_MSG


def test_is_ai_unreachable_error_for_bothub_and_network() -> None:
    assert is_ai_unreachable_error(BOTHUB_UNREACHABLE_MSG)
    assert is_ai_unreachable_error("Network error: timed out")
    assert is_ai_unreachable_error("Cannot connect to host")
    assert not is_ai_unreachable_error("HTTP 400: bad request")
    assert not is_ai_unreachable_error("Empty transcription from BotHub")


def test_local_speech_config_defaults() -> None:
    assert not is_local_speech_enabled({})
    assert not is_local_speech_enabled({"ai": {}})
    assert is_local_speech_enabled({"ai": {"local_speech": {"enabled": True}}})
    assert local_speech_model_size({}) == "small"
    assert local_speech_model_size({"ai": {"local_speech": {"model": "base"}}}) == "base"
