"""Low-level HTTP helpers for AI providers."""

from __future__ import annotations

import http.client
from typing import TYPE_CHECKING
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request

from harrix_swiss_knife.integrations.ai.errors import AiApiError, RequestCancelledError
from harrix_swiss_knife.integrations.ai.network_errors import remap_bothub_network_error
from harrix_swiss_knife.integrations.http_transport import (
    build_https_opener,
    format_urlerror_message,
    https_ssl_context,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def post_bytes(
    url: str,
    body: bytes,
    headers: dict[str, str],
    *,
    timeout_sec: int,
    proxy_url: str | None = None,
    should_cancel: Callable[[], bool] | None = None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None = None,
) -> str:
    """POST raw body and return response text; raise AiApiError on failure."""
    if should_cancel is not None or on_connection is not None:
        return _post_cancellable(
            url,
            body,
            headers,
            timeout_sec=timeout_sec,
            proxy_url=proxy_url,
            should_cancel=should_cancel,
            on_connection=on_connection,
        )

    request = Request(  # noqa: S310
        url,
        data=body,
        method="POST",
        headers=headers,
    )
    opener = build_https_opener(proxy_url)
    try:
        with opener.open(request, timeout=timeout_sec) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        http_error = f"HTTP {exc.code}: {detail}"
        raise AiApiError(http_error) from exc
    except URLError as exc:
        message = remap_bothub_network_error(
            format_urlerror_message(exc, proxy_url=proxy_url),
            url=url,
            exc=exc,
        )
        raise AiApiError(message) from exc


def _post_cancellable(
    url: str,
    body: bytes,
    headers: dict[str, str],
    *,
    timeout_sec: int,
    proxy_url: str | None,
    should_cancel: Callable[[], bool] | None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None,
) -> str:
    if should_cancel and should_cancel():
        _raise_request_cancelled()

    parts = urlsplit(url)
    host = parts.hostname
    if host is None:
        msg = f"Invalid URL: {url}"
        raise AiApiError(msg)

    default_port = 443 if parts.scheme == "https" else 80
    port = parts.port or default_port
    path = parts.path or "/"
    if parts.query:
        path = f"{path}?{parts.query}"

    conn: http.client.HTTPConnection
    if proxy_url:
        proxy_parts = urlsplit(proxy_url)
        proxy_host = proxy_parts.hostname
        if proxy_host is None:
            msg = f"Invalid proxy URL: {proxy_url}"
            raise AiApiError(msg)
        proxy_port = proxy_parts.port or 80
        conn = http.client.HTTPConnection(proxy_host, proxy_port, timeout=timeout_sec)
        conn.set_tunnel(host, port)
    elif parts.scheme == "https":
        conn = http.client.HTTPSConnection(
            host,
            port,
            timeout=timeout_sec,
            context=https_ssl_context(),
        )
    else:
        conn = http.client.HTTPConnection(host, port, timeout=timeout_sec)

    if on_connection is not None:
        on_connection(conn)

    response: http.client.HTTPResponse | None = None
    raw_bytes = b""
    try:
        conn.request("POST", path, body, headers)
        if should_cancel and should_cancel():
            _raise_request_cancelled()
        response = conn.getresponse()
        raw_bytes = _read_response_bytes(conn, response, should_cancel=should_cancel)
    except RequestCancelledError:
        raise
    except (TimeoutError, OSError) as exc:
        if should_cancel and should_cancel():
            raise RequestCancelledError from exc
        network_error = remap_bothub_network_error(
            f"Network error: {exc}",
            url=url,
            exc=exc,
        )
        raise AiApiError(network_error) from exc
    finally:
        conn.close()

    if response is None:
        no_response = "No response from server"
        raise AiApiError(no_response)
    if response.status >= 400:  # noqa: PLR2004
        detail = raw_bytes.decode("utf-8", errors="replace")
        http_error = f"HTTP {response.status}: {detail}"
        raise AiApiError(http_error)

    return raw_bytes.decode("utf-8")


def _raise_request_cancelled() -> None:
    raise RequestCancelledError


def _read_response_bytes(
    conn: http.client.HTTPConnection,
    response: http.client.HTTPResponse,
    *,
    should_cancel: Callable[[], bool] | None,
) -> bytes:
    chunks: list[bytes] = []
    while True:
        if should_cancel and should_cancel():
            conn.close()
            _raise_request_cancelled()
        chunk = response.read(8192)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)
