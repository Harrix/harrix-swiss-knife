"""Tests for BotHub connect-timeout error remapping."""

from __future__ import annotations

from urllib.error import URLError

from harrix_swiss_knife.integrations.ai.network_errors import (
    BOTHUB_UNREACHABLE_MSG,
    exception_is_connect_timeout,
    is_bothub_host,
    remap_bothub_network_error,
)


def test_is_bothub_host_matches_chat_and_ru() -> None:
    assert is_bothub_host("https://bothub.chat/api/v2/openai/v1/chat/completions")
    assert is_bothub_host("https://openai.bothub.ru/v1/chat/completions")
    assert is_bothub_host("bothub.chat")
    assert is_bothub_host("openai.bothub.ru")
    assert not is_bothub_host("https://api.openai.com/v1/chat/completions")
    assert not is_bothub_host("")


def test_remap_winerror_10060_for_bothub_url() -> None:
    message = (
        "Network error: [WinError 10060] A connection attempt failed because the "
        "connected party did not properly respond after a period of time, or "
        "established connection failed because connected host has failed to respond"
    )
    assert remap_bothub_network_error(message, url="https://bothub.chat/api/v2/openai/v1") == BOTHUB_UNREACHABLE_MSG
    assert remap_bothub_network_error(message, url="https://openai.bothub.ru/v1") == BOTHUB_UNREACHABLE_MSG
    assert remap_bothub_network_error(message, provider="bothub") == BOTHUB_UNREACHABLE_MSG
    assert remap_bothub_network_error(message, provider="bothub.ru") == BOTHUB_UNREACHABLE_MSG


def test_remap_keeps_raw_error_for_other_providers() -> None:
    message = "Network error: [WinError 10060] A connection attempt failed"
    assert remap_bothub_network_error(message, provider="openai") == message
    assert remap_bothub_network_error(message, url="https://api.openai.com/v1") == message


def test_remap_keeps_http_errors() -> None:
    message = "HTTP 401: invalid api key"
    assert remap_bothub_network_error(message, provider="bothub") == message


def test_exception_is_connect_timeout_from_urlerror() -> None:
    inner = OSError(10060, "A connection attempt failed")
    inner.winerror = 10060
    wrapped = URLError(inner)
    assert exception_is_connect_timeout(wrapped)
    assert exception_is_connect_timeout(TimeoutError("timed out"))
    assert not exception_is_connect_timeout(OSError(111, "Connection refused"))
