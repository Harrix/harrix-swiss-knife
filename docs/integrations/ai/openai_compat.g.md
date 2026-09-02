---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `openai_compat.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_openai_chat_payload`](#-function-build_openai_chat_payload)
- [🔧 Function `openai_chat_completion`](#-function-openai_chat_completion)
- [🔧 Function `parse_openai_chat_response`](#-function-parse_openai_chat_response)

</details>

## 🔧 Function `build_openai_chat_payload`

```python
def build_openai_chat_payload(*, model: str, text: str, images: Sequence[tuple[bytes, str]] | None = None, audio: tuple[bytes, str] | None = None, allow_audio_as_image_url: bool = True) -> dict[str, Any]
```

Build OpenAI chat completions payload (for tests).

<details>
<summary>Code:</summary>

```python
def build_openai_chat_payload(
    *,
    model: str,
    text: str,
    images: Sequence[tuple[bytes, str]] | None = None,
    audio: tuple[bytes, str] | None = None,
    allow_audio_as_image_url: bool = True,
) -> dict[str, Any]:
    content_parts: list[dict[str, Any]] = [{"type": "text", "text": text}]
    for image_bytes, mime in images or []:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "auto"},
            }
        )
    if audio is not None and allow_audio_as_image_url:
        audio_bytes, mime = audio
        b64 = base64.b64encode(audio_bytes).decode("ascii")
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "auto"},
            }
        )
    message_content: str | list[dict[str, Any]] = text if len(content_parts) == 1 else content_parts
    return {
        "model": model,
        "messages": [{"role": "user", "content": message_content}],
    }
```

</details>

## 🔧 Function `openai_chat_completion`

```python
def openai_chat_completion(*, api_key: str, base_url: str, model: str, text: str, images: Sequence[tuple[bytes, str]] | None = None, audio: tuple[bytes, str] | None = None, timeout_sec: int = _DEFAULT_TIMEOUT_SEC, proxy_url: str | None = None, should_cancel: Callable[[], bool] | None = None, on_connection: Callable[[http.client.HTTPConnection], None] | None = None, allow_audio_as_image_url: bool = True, extra_headers: dict[str, str] | None = None) -> str
```

POST OpenAI-style `/chat/completions` and return assistant text.

When `allow_audio_as_image_url` is `True` (BotHub), audio is sent as an
`image_url` data URI. OpenAI chat should use Whisper separately instead.

<details>
<summary>Code:</summary>

```python
def openai_chat_completion(
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
    allow_audio_as_image_url: bool = True,
    extra_headers: dict[str, str] | None = None,
) -> str:
    content_parts: list[dict[str, Any]] = [{"type": "text", "text": text}]
    for image_bytes, mime in images or []:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        content_parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "auto"},
            }
        )
    if audio is not None and allow_audio_as_image_url:
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
    return parse_openai_chat_response(raw)
```

</details>

## 🔧 Function `parse_openai_chat_response`

```python
def parse_openai_chat_response(raw: str) -> str
```

Parse OpenAI chat completions JSON into assistant text.

<details>
<summary>Code:</summary>

```python
def parse_openai_chat_response(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        invalid_json = f"Invalid JSON response: {raw[:500]}"
        raise AiApiError(invalid_json) from exc

    if "error" in data:
        err = data["error"]
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        raise AiApiError(msg)

    choices = data.get("choices")
    if not choices:
        no_choices = "No choices in API response"
        raise AiApiError(no_choices)

    message = choices[0].get("message") or {}
    content = message.get("content")
    assistant_text = extract_openai_message_content(content)
    if not assistant_text.strip():
        empty_response = "Empty response from model"
        raise AiApiError(empty_response)
    return strip_markdown_fences(assistant_text)
```

</details>
