---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `openai_speech.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `openai_transcribe`](#-function-openai_transcribe)
- [🔧 Function `parse_whisper_response`](#-function-parse_whisper_response)

</details>

## 🔧 Function `openai_transcribe`

```python
def openai_transcribe(*, api_key: str, base_url: str, model: str, audio: tuple[bytes, str], prompt: str | None = None, timeout_sec: int = _DEFAULT_TIMEOUT_SEC, proxy_url: str | None = None, should_cancel: Callable[[], bool] | None = None, on_connection: Callable[[http.client.HTTPConnection], None] | None = None, extra_headers: dict[str, str] | None = None) -> str
```

POST OpenAI `/audio/transcriptions` (multipart) and return transcript text.

<details>
<summary>Code:</summary>

```python
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
    extra_headers: dict[str, str] | None = None,
) -> str:
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
    if extra_headers:
        headers.update(extra_headers)
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
```

</details>

## 🔧 Function `parse_whisper_response`

```python
def parse_whisper_response(raw: str) -> str
```

Parse Whisper JSON transcription response.

<details>
<summary>Code:</summary>

```python
def parse_whisper_response(raw: str) -> str:
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
```

</details>
