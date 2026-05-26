"""Tests for HTTPS transport and BotHub proxy helpers."""

from __future__ import annotations

import ssl
from typing import TYPE_CHECKING
from urllib.error import URLError

from harrix_swiss_knife.integrations.http_transport import (
    format_urlerror_message,
    resolve_proxy_url,
)

if TYPE_CHECKING:
    import pytest


def test_resolve_proxy_url_prefers_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HTTPS_PROXY", "http://env:8080")
    assert resolve_proxy_url(config_proxy="http://config:3128") == "http://config:3128"


def test_resolve_proxy_url_qt_over_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HTTPS_PROXY", "http://env:8080")
    assert resolve_proxy_url(qt_proxy_url="http://qt:8080") == "http://qt:8080"


def test_resolve_proxy_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    monkeypatch.delenv("https_proxy", raising=False)
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("http_proxy", raising=False)
    monkeypatch.setenv("HTTPS_PROXY", "http://env:9090")
    assert resolve_proxy_url() == "http://env:9090"


def test_resolve_proxy_url_empty_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    monkeypatch.delenv("https_proxy", raising=False)
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("http_proxy", raising=False)

    def _no_proxies() -> dict[str, str]:
        return {}

    monkeypatch.setattr(
        "harrix_swiss_knife.integrations.http_transport.getproxies",
        _no_proxies,
    )
    assert resolve_proxy_url() is None


def test_format_urlerror_wrong_version_hint() -> None:
    exc = URLError(ssl.SSLError("[SSL: WRONG_VERSION_NUMBER] wrong version number"))
    message = format_urlerror_message(exc)
    assert "WRONG_VERSION_NUMBER" in str(exc.reason) or "wrong version number" in str(exc.reason).lower()
    assert "bothub.proxy" in message
    assert "HTTPS_PROXY" in message
    assert "no proxy was detected" in message


def test_format_urlerror_wrong_version_masks_proxy_credentials() -> None:
    exc = URLError(ssl.SSLError("[SSL: WRONG_VERSION_NUMBER] wrong version number"))
    message = format_urlerror_message(exc, proxy_url="http://user:secret@proxy.example:3128")
    assert "proxy.example:3128" in message
    assert "secret" not in message


def test_format_urlerror_cert_hint() -> None:
    exc = URLError(ssl.SSLError("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed"))
    message = format_urlerror_message(exc)
    assert "SSL_CERT_FILE" in message


def test_format_urlerror_plain() -> None:
    exc = URLError("Connection refused")
    assert format_urlerror_message(exc) == "Network error: Connection refused"
