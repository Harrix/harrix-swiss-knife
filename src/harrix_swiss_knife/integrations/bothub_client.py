"""BotHub OpenAI-compatible chat completions client."""

from __future__ import annotations

import base64
import http.client
import json
import re
from typing import TYPE_CHECKING, Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request

from harrix_swiss_knife.integrations.http_transport import (
    build_https_opener,
    format_urlerror_message,
    https_ssl_context,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_DEFAULT_TIMEOUT_SEC = 120


class BotHubApiError(RuntimeError):
    """Raised when BotHub API returns an error or the response cannot be parsed."""


class RequestCancelledError(BotHubApiError):
    """Raised when an in-flight BotHub request is cancelled by the user."""


def chat_completion(
    *,
    api_key: str,
    base_url: str,
    model: str,
    text: str,
    image: tuple[bytes, str] | None = None,
    audio: tuple[bytes, str] | None = None,
    timeout_sec: int = _DEFAULT_TIMEOUT_SEC,
    proxy_url: str | None = None,
    should_cancel: Callable[[], bool] | None = None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None = None,
) -> str:
    """Send a chat completion request to BotHub and return assistant text.

    Args:

    - `api_key` (`str`): BotHub access token (Bearer).
    - `base_url` (`str`): API base URL, e.g. `https://bothub.chat/api/v2/openai/v1`.
    - `model` (`str`): Model id, e.g. `gpt-5.4`.
    - `text` (`str`): User message text (prompt).
    - `image` (`tuple[bytes, str] | None`): Optional `(bytes, mime_type)` for vision.
    - `audio` (`tuple[bytes, str] | None`): Optional `(bytes, mime_type)` for speech input.
    - `timeout_sec` (`int`): HTTP timeout in seconds.
    - `proxy_url` (`str | None`): Optional HTTP proxy URL for HTTPS CONNECT.
    - `should_cancel` (`Callable[[], bool] | None`): When it returns True, abort the request.
    - `on_connection` (`Callable[[http.client.HTTPConnection], None] | None`): Receives the live connection.

    Returns:

    - `str`: Assistant message content after markdown fence stripping.

    """
    content_parts: list[dict[str, Any]] = [{"type": "text", "text": text}]
    if image is not None:
        image_bytes, mime = image
        b64 = base64.b64encode(image_bytes).decode("ascii")
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "auto"},
            }
        )
    if audio is not None:
        audio_bytes, mime = audio
        b64 = base64.b64encode(audio_bytes).decode("ascii")
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "auto"},
            }
        )

    if len(content_parts) == 1:
        message_content: str | list[dict[str, Any]] = text
    else:
        message_content = content_parts

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": message_content}],
    }

    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if should_cancel is not None or on_connection is not None:
        raw = _post_json_cancellable(
            url,
            body,
            headers,
            timeout_sec=timeout_sec,
            proxy_url=proxy_url,
            should_cancel=should_cancel,
            on_connection=on_connection,
        )
    else:
        request = Request(  # noqa: S310
            url,
            data=body,
            method="POST",
            headers=headers,
        )
        opener = build_https_opener(proxy_url)
        try:
            with opener.open(request, timeout=timeout_sec) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            http_error = f"HTTP {exc.code}: {detail}"
            raise BotHubApiError(http_error) from exc
        except URLError as exc:
            raise BotHubApiError(format_urlerror_message(exc, proxy_url=proxy_url)) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        invalid_json = f"Invalid JSON response: {raw[:500]}"
        raise BotHubApiError(invalid_json) from exc

    if "error" in data:
        err = data["error"]
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        raise BotHubApiError(msg)

    choices = data.get("choices")
    if not choices:
        no_choices = "No choices in API response"
        raise BotHubApiError(no_choices)

    message = choices[0].get("message") or {}
    content = message.get("content")
    assistant_text = _extract_message_content(content)
    if not assistant_text.strip():
        empty_response = "Empty response from model"
        raise BotHubApiError(empty_response)
    return strip_markdown_fences(assistant_text)


def strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences from model output."""
    stripped = text.strip()
    fence_match = re.match(r"^```(?:\w+)?\s*\n?(.*?)\n?```\s*$", stripped, flags=re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped


def _extract_message_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(str(part.get("text", "")))
            elif isinstance(part, str):
                parts.append(part)
        return "\n".join(parts)
    return str(content)


def _post_json_cancellable(
    url: str,
    body: bytes,
    headers: dict[str, str],
    *,
    timeout_sec: int,
    proxy_url: str | None,
    should_cancel: Callable[[], bool] | None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None,
) -> str:
    """POST JSON via http.client with optional cancellation."""
    if should_cancel and should_cancel():
        _raise_request_cancelled()

    parts = urlsplit(url)
    host = parts.hostname
    if host is None:
        msg = f"Invalid URL: {url}"
        raise BotHubApiError(msg)

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
            raise BotHubApiError(msg)
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
        network_error = f"Network error: {exc}"
        raise BotHubApiError(network_error) from exc
    finally:
        conn.close()

    if response is None:
        no_response = "No response from server"
        raise BotHubApiError(no_response)
    if response.status >= 400:  # noqa: PLR2004
        detail = raw_bytes.decode("utf-8", errors="replace")
        http_error = f"HTTP {response.status}: {detail}"
        raise BotHubApiError(http_error)

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
