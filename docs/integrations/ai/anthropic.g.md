---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `anthropic.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `anthropic_messages`](#-function-anthropic_messages)
- [🔧 Function `build_anthropic_payload`](#-function-build_anthropic_payload)
- [🔧 Function `parse_anthropic_response`](#-function-parse_anthropic_response)

</details>

## 🔧 Function `anthropic_messages`

```python
def anthropic_messages(*, api_key: str, base_url: str, model: str, text: str, images: Sequence[tuple[bytes, str]] | None = None, max_tokens: int = 8192, timeout_sec: int = _DEFAULT_TIMEOUT_SEC, proxy_url: str | None = None, should_cancel: Callable[[], bool] | None = None, on_connection: Callable[[http.client.HTTPConnection], None] | None = None) -> str
```

POST Anthropic `/v1/messages` and return assistant text.

<details>
<summary>Code:</summary>

```python
def anthropic_messages(
    *,
    api_key: str,
    base_url: str,
    model: str,
    text: str,
    images: Sequence[tuple[bytes, str]] | None = None,
    max_tokens: int = 8192,
    timeout_sec: int = _DEFAULT_TIMEOUT_SEC,
    proxy_url: str | None = None,
    should_cancel: Callable[[], bool] | None = None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None = None,
) -> str:
    payload = build_anthropic_payload(
        model=model,
        text=text,
        images=images,
        max_tokens=max_tokens,
    )
    url = base_url.rstrip("/") + "/v1/messages"
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "x-api-key": api_key.strip(),
        "anthropic-version": _ANTHROPIC_VERSION,
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
    return parse_anthropic_response(raw)
```

</details>

## 🔧 Function `build_anthropic_payload`

```python
def build_anthropic_payload(*, model: str, text: str, images: Sequence[tuple[bytes, str]] | None = None, max_tokens: int = 8192) -> dict[str, Any]
```

Build Anthropic Messages request body (for runtime and tests).

<details>
<summary>Code:</summary>

```python
def build_anthropic_payload(
    *,
    model: str,
    text: str,
    images: Sequence[tuple[bytes, str]] | None = None,
    max_tokens: int = 8192,
) -> dict[str, Any]:
    content: list[dict[str, Any]] = []
    for image_bytes, mime in images or []:
        media_type = mime.split(";")[0].strip() or "image/png"
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64.b64encode(image_bytes).decode("ascii"),
                },
            }
        )
    content.append({"type": "text", "text": text})
    return {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": content}],
    }
```

</details>

## 🔧 Function `parse_anthropic_response`

```python
def parse_anthropic_response(raw: str) -> str
```

Parse Anthropic Messages JSON into assistant text.

<details>
<summary>Code:</summary>

```python
def parse_anthropic_response(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        invalid_json = f"Invalid JSON response: {raw[:500]}"
        raise AiApiError(invalid_json) from exc

    if "error" in data:
        err = data["error"]
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        raise AiApiError(msg)

    content = data.get("content")
    if not isinstance(content, list) or not content:
        no_content = "No content in Anthropic response"
        raise AiApiError(no_content)

    parts = [str(part.get("text", "")) for part in content if isinstance(part, dict) and part.get("type") == "text"]
    assistant_text = "\n".join(parts).strip()
    if not assistant_text:
        empty_response = "Empty response from model"
        raise AiApiError(empty_response)
    return strip_markdown_fences(assistant_text)
```

</details>
