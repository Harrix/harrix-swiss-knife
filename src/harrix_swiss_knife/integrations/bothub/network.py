"""BotHub network settings (proxy resolution via config and Qt)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QNetworkProxy, QNetworkProxyFactory, QNetworkProxyQuery

from harrix_swiss_knife.integrations.http_transport import resolve_proxy_url

if TYPE_CHECKING:
    from collections.abc import Iterable


def qnetwork_proxy_to_url(
    proxy: QNetworkProxy | None = None,
    *,
    system_proxies: Iterable[QNetworkProxy] | None = None,
) -> str | None:
    """Resolve Qt proxy to HTTP proxy URL for urllib.

    Priority:
    - Explicit `proxy` if provided (used mostly for tests).
    - System proxy configuration via `QNetworkProxyFactory.systemProxyForQuery` (PAC/WPAD).
    - `QNetworkProxy.applicationProxy` fallback.
    """
    if proxy is not None:
        return _proxy_to_url(proxy)

    if system_proxies is None:
        query = QNetworkProxyQuery(QUrl("https://bothub.chat/"))
        system_proxies = QNetworkProxyFactory.systemProxyForQuery(query)

    for p in system_proxies:
        url = _proxy_to_url(p)
        if url:
            return url

    return _proxy_to_url(QNetworkProxy.applicationProxy())


def resolve_bothub_proxy_url(app_config: dict[str, Any]) -> str | None:
    """Resolve BotHub HTTP proxy from config, Qt, environment, and system settings."""
    bothub_cfg = app_config.get("bothub") or {}
    config_proxy = str(bothub_cfg.get("proxy", "")).strip() or None
    qt_proxy_url = qnetwork_proxy_to_url()
    return resolve_proxy_url(config_proxy=config_proxy, qt_proxy_url=qt_proxy_url)


def _proxy_to_url(proxy: QNetworkProxy) -> str | None:
    """Convert Qt proxy to an HTTP proxy URL for urllib.

    Only HTTP proxies are returned; SOCKS proxies are not supported by stdlib urllib.
    """
    if proxy.type() == QNetworkProxy.ProxyType.NoProxy:
        return None
    host = proxy.hostName().strip()
    if not host:
        return None
    if proxy.type() != QNetworkProxy.ProxyType.HttpProxy:
        return None
    port = proxy.port()
    user = proxy.user().strip()
    password = proxy.password()
    if user:
        auth = f"{quote(user, safe='')}:{quote(password, safe='')}@" if password else f"{quote(user, safe='')}@"
        return f"http://{auth}{host}:{port}"
    return f"http://{host}:{port}"
