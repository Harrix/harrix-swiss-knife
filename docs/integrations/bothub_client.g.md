---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `bothub_client.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `BotHubApiError`](#-constant-bothubapierror)
- [🔧 Function `chat_completion`](#-function-chat_completion)

</details>

## 📎 Constant `BotHubApiError`

```python
BotHubApiError = AiApiError
```

_No docstring provided._

## 🔧 Function `chat_completion`

```python
def chat_completion(*, api_key: str, base_url: str, model: str, text: str, images: Sequence[tuple[bytes, str]] | None = None, image: tuple[bytes, str] | None = None, audio: tuple[bytes, str] | None = None, timeout_sec: int = _DEFAULT_TIMEOUT_SEC, proxy_url: str | None = None, should_cancel: Callable[[], bool] | None = None, on_connection: Callable[[http.client.HTTPConnection], None] | None = None, provider: ProviderName = 'bothub', max_tokens: int | None = None) -> str
```

Send a chat completion request and return assistant text.

Defaults to the BotHub OpenAI-compatible transport. Pass `provider` to use
OpenAI, Anthropic, or Gemini.

Args:

- `api_key` (`str`): Provider access token.
- `base_url` (`str`): API base URL.
- `model` (`str`): Model ID.
- `text` (`str`): User message text (prompt).
- `images` (`Sequence[tuple[bytes, str]] | None`): Optional vision inputs.
- `image` (`tuple[bytes, str] | None`): Optional single vision input.
- `audio` (`tuple[bytes, str] | None`): Optional speech input.
- `timeout_sec` (`int`): HTTP timeout in seconds.
- `proxy_url` (`str | None`): Optional HTTP proxy URL for HTTPS CONNECT.
- `should_cancel` (`Callable[[], bool] | None`): When it returns `True`, abort.
- `on_connection` (`Callable[[http.client.HTTPConnection], None] | None`): Live connection hook.
- `provider`: Active AI provider ID.
- `max_tokens`: Anthropic max tokens override.

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
    provider: ProviderName = "bothub",
    max_tokens: int | None = None,
) -> str:
    return ai_chat_completion(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
        text=text,
        images=images,
        image=image,
        audio=audio,
        timeout_sec=timeout_sec,
        proxy_url=proxy_url,
        should_cancel=should_cancel,
        on_connection=on_connection,
        max_tokens=max_tokens,
    )
```

</details>
