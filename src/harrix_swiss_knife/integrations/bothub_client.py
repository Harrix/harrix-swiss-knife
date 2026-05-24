"""BotHub OpenAI-compatible chat completions client."""

from __future__ import annotations

import base64
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_DEFAULT_TIMEOUT_SEC = 120


class BotHubApiError(RuntimeError):
    """Raised when BotHub API returns an error or the response cannot be parsed."""


def chat_completion(
    *,
    api_key: str,
    base_url: str,
    model: str,
    text: str,
    image: tuple[bytes, str] | None = None,
    timeout_sec: int = _DEFAULT_TIMEOUT_SEC,
) -> str:
    """Send a chat completion request to BotHub and return assistant text.

    Args:

    - `api_key` (`str`): BotHub access token (Bearer).
    - `base_url` (`str`): API base URL, e.g. `https://bothub.chat/api/v2/openai/v1`.
    - `model` (`str`): Model id, e.g. `gpt-5.4`.
    - `text` (`str`): User message text (prompt).
    - `image` (`tuple[bytes, str] | None`): Optional `(bytes, mime_type)` for vision.
    - `timeout_sec` (`int`): HTTP timeout in seconds.

    Returns:

    - `str`: Assistant message content after markdown fence stripping.

    """
    content_parts: list[dict[str, Any]] = []
    if image is not None:
        image_bytes, mime = image
        b64 = base64.b64encode(image_bytes).decode("ascii")
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "auto"},
            }
        )
    content_parts.append({"type": "text", "text": text})

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
    request = Request(  # noqa: S310
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=timeout_sec) as response:  # noqa: S310
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        http_error = f"HTTP {exc.code}: {detail}"
        raise BotHubApiError(http_error) from exc
    except URLError as exc:
        network_error = f"Network error: {exc.reason}"
        raise BotHubApiError(network_error) from exc

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
