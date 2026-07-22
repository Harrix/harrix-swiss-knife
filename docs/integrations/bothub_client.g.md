---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `bothub_client.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BotHubApiError`](#%EF%B8%8F-class-bothubapierror)
- [🏛️ Class `RequestCancelledError`](#%EF%B8%8F-class-requestcancellederror)
- [🔧 Function `chat_completion`](#-function-chat_completion)
- [🔧 Function `strip_markdown_fences`](#-function-strip_markdown_fences)

</details>

## 🏛️ Class `BotHubApiError`

```python
class BotHubApiError(RuntimeError)
```

Raised when BotHub API returns an error or the response cannot be parsed.

<details>
<summary>Code:</summary>

```python
class BotHubApiError(RuntimeError):
```

</details>

## 🏛️ Class `RequestCancelledError`

```python
class RequestCancelledError(BotHubApiError)
```

Raised when an in-flight BotHub request is cancelled by the user.

<details>
<summary>Code:</summary>

```python
class RequestCancelledError(BotHubApiError):
```

</details>

## 🔧 Function `chat_completion`

```python
def chat_completion() -> str
```

Send a chat completion request to BotHub and return assistant text.

Args:

- `api_key` (`str`): BotHub access token (Bearer).
- `base_url` (`str`): API base URL, e.g. `https://bothub.chat/api/v2/openai/v1`.
- `model` (`str`): Model ID, e.g. `gpt-5.4`.
- `text` (`str`): User message text (prompt).
- `images` (`Sequence[tuple[bytes, str]] | None`): Optional vision inputs `(bytes, mime_type)`.
- `image` (`tuple[bytes, str] | None`): Optional single vision input (merged into `images`).
- `audio` (`tuple[bytes, str] | None`): Optional `(bytes, mime_type)` for speech input.
- `timeout_sec` (`int`): HTTP timeout in seconds.
- `proxy_url` (`str | None`): Optional HTTP proxy URL for HTTPS CONNECT.
- `should_cancel` (`Callable[[], bool] | None`): When it returns `True`, abort the request.
- `on_connection` (`Callable[[http.client.HTTPConnection], None] | None`): Receives the live connection.

Returns:

- `str`: Assistant message content after Markdown fence stripping.

<details>
<summary>Code:</summary>

```python
def chat_completion(
    *,
    api_key: str,
    base_url: str,
    model: str,
    text: str,
    images: Sequence[tuple[bytes, str]] | None = None,
    image: tuple[bytes, str] | None = None,
    audio: tuple[bytes, str] | None = None,
    timeout_sec: int = _DEFAULT_TIMEOUT_SEC,
    proxy_url: str | None = None,
    should_cancel: Callable[[], bool] | None = None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None = None,
) -> str:
    content_parts: list[dict[str, Any]] = [{"type": "text", "text": text}]
    image_list: list[tuple[bytes, str]] = list(images or [])
    if image is not None:
        image_list.append(image)
    for image_bytes, mime in image_list:
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
```

</details>

## 🔧 Function `strip_markdown_fences`

```python
def strip_markdown_fences(text: str) -> str
```

Remove Markdown code fences from model output.

<details>
<summary>Code:</summary>

````python
def strip_markdown_fences(text: str) -> str:
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
````

</details>
