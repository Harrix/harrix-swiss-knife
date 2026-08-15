---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `client.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `chat_completion`](#-function-chat_completion)
- [🔧 Function `chat_completion_from_config`](#-function-chat_completion_from_config)

</details>

## 🔧 Function `chat_completion`

```python
def chat_completion(*, provider: ProviderName, api_key: str, base_url: str, model: str, text: str, images: Sequence[tuple[bytes, str]] | None = None, image: tuple[bytes, str] | None = None, audio: tuple[bytes, str] | None = None, timeout_sec: int = _DEFAULT_TIMEOUT_SEC, proxy_url: str | None = None, should_cancel: Callable[[], bool] | None = None, on_connection: Callable[[http.client.HTTPConnection], None] | None = None, max_tokens: int | None = None) -> str
```

Send a multimodal request to the given provider and return assistant text.

Args:

- `provider`: `bothub`, `openai`, `anthropic`, or `gemini`.
- `api_key`: Provider access token.
- `base_url`: API base URL.
- `model`: Model ID (or Whisper model for OpenAI speech).
- `text`: User prompt text.
- `images` / `image`: Optional vision inputs `(bytes, mime_type)`.
- `audio`: Optional speech input `(bytes, mime_type)`.
- `timeout_sec`: HTTP timeout in seconds.
- `proxy_url`: Optional HTTP proxy URL for HTTPS CONNECT.
- `should_cancel` / `on_connection`: Cancellation hooks for Qt workers.
- `max_tokens`: Anthropic `max_tokens` override.

Returns:

- `str`: Assistant / transcript text after Markdown fence stripping.

<details>
<summary>Code:</summary>

```python
def chat_completion(
    *,
    provider: ProviderName,
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
    max_tokens: int | None = None,
) -> str:
    image_list: list[tuple[bytes, str]] = list(images or [])
    if image is not None:
        image_list.append(image)

    if provider == "anthropic" and audio is not None:
        msg = 'Anthropic does not support speech-to-text. Set ai.speech_provider to "openai", "gemini", or "bothub".'
        raise AiApiError(msg)

    if provider == "openai" and audio is not None:
        return openai_transcribe(
            api_key=api_key,
            base_url=base_url,
            model=model,
            audio=audio,
            prompt=text,
            timeout_sec=timeout_sec,
            proxy_url=proxy_url,
            should_cancel=should_cancel,
            on_connection=on_connection,
        )

    if provider in {"bothub", "openai"}:
        return openai_chat_completion(
            api_key=api_key,
            base_url=base_url,
            model=model,
            text=text,
            images=image_list or None,
            audio=audio if provider == "bothub" else None,
            timeout_sec=timeout_sec,
            proxy_url=proxy_url,
            should_cancel=should_cancel,
            on_connection=on_connection,
            allow_audio_as_image_url=provider == "bothub",
        )

    if provider == "anthropic":
        resolved_max_tokens = max_tokens if max_tokens is not None else 8192
        return anthropic_messages(
            api_key=api_key,
            base_url=base_url,
            model=model,
            text=text,
            images=image_list or None,
            max_tokens=resolved_max_tokens,
            timeout_sec=timeout_sec,
            proxy_url=proxy_url,
            should_cancel=should_cancel,
            on_connection=on_connection,
        )

    if provider == "gemini":
        return gemini_generate_content(
            api_key=api_key,
            base_url=base_url,
            model=model,
            text=text,
            images=image_list or None,
            audio=audio,
            timeout_sec=timeout_sec,
            proxy_url=proxy_url,
            should_cancel=should_cancel,
            on_connection=on_connection,
        )

    msg = f"Unsupported AI provider: {provider}"
    raise AiApiError(msg)
```

</details>

## 🔧 Function `chat_completion_from_config`

```python
def chat_completion_from_config(config: dict, *, text: str, images: Sequence[tuple[bytes, str]] | None = None, image: tuple[bytes, str] | None = None, audio: tuple[bytes, str] | None = None, model: str | None = None, for_speech: bool | None = None, timeout_sec: int = _DEFAULT_TIMEOUT_SEC, proxy_url: str | None = None, should_cancel: Callable[[], bool] | None = None, on_connection: Callable[[http.client.HTTPConnection], None] | None = None) -> str
```

Resolve provider from config and run `chat_completion`.

<details>
<summary>Code:</summary>

```python
def chat_completion_from_config(
    config: dict,
    *,
    text: str,
    images: Sequence[tuple[bytes, str]] | None = None,
    image: tuple[bytes, str] | None = None,
    audio: tuple[bytes, str] | None = None,
    model: str | None = None,
    for_speech: bool | None = None,
    timeout_sec: int = _DEFAULT_TIMEOUT_SEC,
    proxy_url: str | None = None,
    should_cancel: Callable[[], bool] | None = None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None = None,
) -> str:
    use_speech = for_speech if for_speech is not None else audio is not None
    provider = get_speech_provider(config) if use_speech else get_chat_provider(config)
    api_key, base_url, default_model, resolved_proxy = get_connection_params_for_provider(
        config,
        provider,
        for_speech=use_speech,
    )
    settings = get_provider_settings(config, provider)
    max_tokens = settings.get("max_tokens")
    max_tokens_int = int(max_tokens) if max_tokens is not None else None
    return chat_completion(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model if model is not None else default_model,
        text=text,
        images=images,
        image=image,
        audio=audio,
        timeout_sec=timeout_sec,
        proxy_url=proxy_url if proxy_url is not None else resolved_proxy,
        should_cancel=should_cancel,
        on_connection=on_connection,
        max_tokens=max_tokens_int,
    )
```

</details>
