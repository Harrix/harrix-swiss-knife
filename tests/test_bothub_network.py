"""Tests for BotHub Qt proxy URL conversion."""

from __future__ import annotations

from PySide6.QtNetwork import QNetworkProxy

from harrix_swiss_knife.apps.common.bothub_network import qnetwork_proxy_to_url, resolve_bothub_proxy_url


def test_resolve_bothub_proxy_url_from_config() -> None:
    app_config = {"bothub": {"proxy": "http://school:3128"}}
    assert resolve_bothub_proxy_url(app_config) == "http://school:3128"


def test_resolve_bothub_proxy_url_empty_config(monkeypatch) -> None:
    monkeypatch.setenv("HTTPS_PROXY", "http://env:8080")
    app_config = {"bothub": {"proxy": ""}}
    assert resolve_bothub_proxy_url(app_config) == "http://env:8080"


def test_qnetwork_proxy_to_url_no_proxy() -> None:
    proxy = QNetworkProxy(QNetworkProxy.ProxyType.NoProxy)
    assert qnetwork_proxy_to_url(proxy) is None
