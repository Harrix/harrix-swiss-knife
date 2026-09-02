"""Dispatch chat/vision/speech requests to the configured AI provider."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.integrations.ai.anthropic import anthropic_messages
from harrix_swiss_knife.integrations.ai.config import extra_headers_for_provider
from harrix_swiss_knife.integrations.ai.errors import AiApiError, RequestCancelledError
from harrix_swiss_knife.integrations.ai.gemini import gemini_generate_content
from harrix_swiss_knife.integrations.ai.network_errors import remap_bothub_network_error
from harrix_swiss_knife.integrations.ai.openai_compat import openai_chat_completion
from harrix_swiss_knife.integrations.ai.openai_speech import openai_transcribe

if TYPE_CHECKING:
    import http.client
    from collections.abc import Callable, Sequence

    from harrix_swiss_knife.integrations.ai.config import ProviderName

_DEFAULT_TIMEOUT_SEC = 120


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
    """Send a multimodal request to the given provider and return assistant text.

    Args:

    - `provider`: `bothub`, `bothub.ru`, `openai`, `openrouter`, `anthropic`, or `gemini`.
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

    """
    image_list: list[tuple[bytes, str]] = list(images or [])
    if image is not None:
        image_list.append(image)

    try:
        return _dispatch_chat_completion(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
            text=text,
            image_list=image_list,
            audio=audio,
            timeout_sec=timeout_sec,
            proxy_url=proxy_url,
            should_cancel=should_cancel,
            on_connection=on_connection,
            max_tokens=max_tokens,
        )
    except RequestCancelledError:
        raise
    except AiApiError as exc:
        mapped = remap_bothub_network_error(str(exc), provider=provider, exc=exc)
        if mapped != str(exc):
            raise AiApiError(mapped) from exc
        raise


def _dispatch_chat_completion(
    *,
    provider: ProviderName,
    api_key: str,
    base_url: str,
    model: str,
    text: str,
    image_list: list[tuple[bytes, str]],
    audio: tuple[bytes, str] | None,
    timeout_sec: int,
    proxy_url: str | None,
    should_cancel: Callable[[], bool] | None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None,
    max_tokens: int | None,
) -> str:
    if provider == "anthropic" and audio is not None:
        msg = (
            "Anthropic does not support speech-to-text. "
            'Set ai.speech_provider to "openai", "openrouter", "gemini", "bothub", or "bothub.ru".'
        )
        raise AiApiError(msg)

    extra_headers = extra_headers_for_provider(provider)
    if provider in {"openai", "openrouter"} and audio is not None:
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
            extra_headers=extra_headers,
        )

    if provider in {"bothub", "bothub.ru", "openai", "openrouter"}:
        bothub_audio = provider in {"bothub", "bothub.ru"}
        return openai_chat_completion(
            api_key=api_key,
            base_url=base_url,
            model=model,
            text=text,
            images=image_list or None,
            audio=audio if bothub_audio else None,
            timeout_sec=timeout_sec,
            proxy_url=proxy_url,
            should_cancel=should_cancel,
            on_connection=on_connection,
            allow_audio_as_image_url=bothub_audio,
            extra_headers=extra_headers,
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
