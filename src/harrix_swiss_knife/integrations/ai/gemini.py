"""Google Gemini generateContent client."""

from __future__ import annotations

import base64
import json
from typing import TYPE_CHECKING, Any
from urllib.parse import quote, urlencode

from harrix_swiss_knife.integrations.ai.errors import AiApiError
from harrix_swiss_knife.integrations.ai.http import post_bytes
from harrix_swiss_knife.integrations.ai.text_utils import strip_markdown_fences

if TYPE_CHECKING:
    import http.client
    from collections.abc import Callable, Sequence

_DEFAULT_TIMEOUT_SEC = 120


def build_gemini_payload(
    *,
    text: str,
    images: Sequence[tuple[bytes, str]] | None = None,
    audio: tuple[bytes, str] | None = None,
) -> dict[str, Any]:
    """Build Gemini generateContent request body (for runtime and tests)."""
    parts: list[dict[str, Any]] = [{"text": text}]
    for image_bytes, mime in images or []:
        parts.append(
            {
                "inline_data": {
                    "mime_type": mime.split(";")[0].strip() or "image/png",
                    "data": base64.b64encode(image_bytes).decode("ascii"),
                }
            }
        )
    if audio is not None:
        audio_bytes, mime = audio
        parts.append(
            {
                "inline_data": {
                    "mime_type": mime.split(";")[0].strip() or "audio/wav",
                    "data": base64.b64encode(audio_bytes).decode("ascii"),
                }
            }
        )
    return {"contents": [{"role": "user", "parts": parts}]}


def gemini_generate_content(
    *,
    api_key: str,
    base_url: str,
    model: str,
    text: str,
    images: Sequence[tuple[bytes, str]] | None = None,
    audio: tuple[bytes, str] | None = None,
    timeout_sec: int = _DEFAULT_TIMEOUT_SEC,
    proxy_url: str | None = None,
    should_cancel: Callable[[], bool] | None = None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None = None,
) -> str:
    """POST Gemini `models/{model}:generateContent` and return text."""
    payload = build_gemini_payload(text=text, images=images, audio=audio)
    model_id = model.strip().removeprefix("models/")
    query = urlencode({"key": api_key.strip()})
    url = f"{base_url.rstrip('/')}/models/{quote(model_id, safe='')}:generateContent?{query}"
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    raw = post_bytes(
        url,
        body,
        headers,
        timeout_sec=timeout_sec,
        proxy_url=proxy_url,
        should_cancel=should_cancel,
        on_connection=on_connection,
    )
    return parse_gemini_response(raw)


def parse_gemini_response(raw: str) -> str:
    """Parse Gemini generateContent JSON into assistant text."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        invalid_json = f"Invalid JSON response: {raw[:500]}"
        raise AiApiError(invalid_json) from exc

    if "error" in data:
        err = data["error"]
        msg = str(err.get("message") or err) if isinstance(err, dict) else str(err)
        raise AiApiError(msg)

    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        no_candidates = "No candidates in Gemini response"
        raise AiApiError(no_candidates)

    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    texts = [str(part.get("text", "")) for part in parts if isinstance(part, dict) and "text" in part]
    assistant_text = "\n".join(texts).strip()
    if not assistant_text:
        empty_response = "Empty response from model"
        raise AiApiError(empty_response)
    return strip_markdown_fences(assistant_text)
