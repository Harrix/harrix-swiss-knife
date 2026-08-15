"""OpenAI Whisper speech transcriptions."""

from __future__ import annotations

import json
import mimetypes
from typing import TYPE_CHECKING
from uuid import uuid4

from harrix_swiss_knife.integrations.ai.errors import AiApiError
from harrix_swiss_knife.integrations.ai.http import post_bytes

if TYPE_CHECKING:
    import http.client
    from collections.abc import Callable

_DEFAULT_TIMEOUT_SEC = 120


def openai_transcribe(
    *,
    api_key: str,
    base_url: str,
    model: str,
    audio: tuple[bytes, str],
    prompt: str | None = None,
    timeout_sec: int = _DEFAULT_TIMEOUT_SEC,
    proxy_url: str | None = None,
    should_cancel: Callable[[], bool] | None = None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None = None,
) -> str:
    """POST OpenAI `/audio/transcriptions` (multipart) and return transcript text."""
    audio_bytes, mime = audio
    filename = _filename_for_mime(mime)
    boundary = f"----hsk{uuid4().hex}"
    body = _multipart_body(
        boundary=boundary,
        fields={
            "model": model,
            **({"prompt": prompt} if prompt and prompt.strip() else {}),
        },
        file_field="file",
        filename=filename,
        file_mime=mime or "application/octet-stream",
        file_bytes=audio_bytes,
    )
    url = base_url.rstrip("/") + "/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
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
    return parse_whisper_response(raw)


def parse_whisper_response(raw: str) -> str:
    """Parse Whisper JSON transcription response."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        invalid_json = f"Invalid JSON response: {raw[:500]}"
        raise AiApiError(invalid_json) from exc

    if "error" in data:
        err = data["error"]
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        raise AiApiError(msg)

    text = str(data.get("text", "")).strip()
    if not text:
        empty_response = "Empty transcription from model"
        raise AiApiError(empty_response)
    return text


def _filename_for_mime(mime: str) -> str:
    ext = mimetypes.guess_extension(mime.split(";", maxsplit=1)[0].strip()) if mime else None
    if not ext:
        if "wav" in mime:
            ext = ".wav"
        elif "mpeg" in mime or "mp3" in mime:
            ext = ".mp3"
        elif "mp4" in mime or "m4a" in mime:
            ext = ".m4a"
        elif "ogg" in mime:
            ext = ".ogg"
        elif "webm" in mime:
            ext = ".webm"
        else:
            ext = ".bin"
    return f"audio{ext}"


def _multipart_body(
    *,
    boundary: str,
    fields: dict[str, str],
    file_field: str,
    filename: str,
    file_mime: str,
    file_bytes: bytes,
) -> bytes:
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        chunks.append(value.encode("utf-8"))
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}\r\n".encode())
    chunks.append(
        (
            f'Content-Disposition: form-data; name="{file_field}"; '
            f'filename="{filename}"\r\n'
            f"Content-Type: {file_mime}\r\n\r\n"
        ).encode()
    )
    chunks.append(file_bytes)
    chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks)
