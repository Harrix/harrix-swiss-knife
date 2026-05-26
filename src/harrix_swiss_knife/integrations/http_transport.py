"""HTTPS transport helpers (SSL context, proxy, urllib opener)."""

from __future__ import annotations

import os
import ssl
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlsplit, urlunsplit
from urllib.request import BaseHandler, HTTPSHandler, OpenerDirector, ProxyHandler, build_opener, getproxies

if TYPE_CHECKING:
    from urllib.error import URLError

import certifi

_WRONG_VERSION_HINT = (
    "\n\nHint: this often happens on school/corporate Wi-Fi when HTTPS is intercepted "
    "or a proxy is required. Set bothub.proxy in config.json, HTTPS_PROXY, "
    "or use another network/VPN."
)
_CERT_VERIFY_HINT = "\n\nHint: set SSL_CERT_FILE to a PEM bundle that includes your network root CA."


def build_https_opener(proxy_url: str | None = None) -> OpenerDirector:
    """Return urllib opener with certifi SSL and optional HTTP(S) proxy."""
    ctx = https_ssl_context()
    handlers: list[BaseHandler] = [HTTPSHandler(context=ctx)]
    if proxy_url:
        proxy_map = {"http": proxy_url, "https": proxy_url}
        handlers.insert(0, ProxyHandler(proxy_map))
    return build_opener(*handlers)


def format_urlerror_message(exc: URLError, *, proxy_url: str | None = None) -> str:
    """Format URLError with optional hints for common school/corporate network issues."""
    reason_str = str(exc.reason)
    message = f"Network error: {reason_str}"
    upper = reason_str.upper()
    if "WRONG_VERSION_NUMBER" in upper or "wrong version number" in reason_str.lower():
        message += _WRONG_VERSION_HINT
        message += _proxy_diagnostic(proxy_url)
    elif "CERTIFICATE_VERIFY_FAILED" in upper:
        message += _CERT_VERIFY_HINT
    return message


def https_ssl_context() -> ssl.SSLContext:
    """Build SSL context with certifi CA bundle and optional SSL_CERT_FILE."""
    ctx = ssl.create_default_context(cafile=certifi.where())
    ssl_cert_file = os.environ.get("SSL_CERT_FILE")
    if ssl_cert_file and Path(ssl_cert_file).is_file():
        ctx.load_verify_locations(cafile=ssl_cert_file)
    return ctx


def resolve_proxy_url(
    *,
    config_proxy: str | None = None,
    qt_proxy_url: str | None = None,
) -> str | None:
    """Resolve proxy URL: config, Qt system proxy, env, then urllib getproxies."""
    if config_proxy and config_proxy.strip():
        return config_proxy.strip()
    if qt_proxy_url and qt_proxy_url.strip():
        return qt_proxy_url.strip()
    for key in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    proxies = getproxies()
    return proxies.get("https") or proxies.get("http")


def _proxy_diagnostic(proxy_url: str | None) -> str:
    """Return a short proxy diagnostic without exposing credentials."""
    if not proxy_url:
        return "\n\nProxy diagnostic: no proxy was detected for this request."

    parts = urlsplit(proxy_url)
    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    netloc = f"{host}{port}" if host else parts.netloc
    masked = urlunsplit((parts.scheme, netloc, "", "", ""))
    return f"\n\nProxy diagnostic: using proxy {masked}."
