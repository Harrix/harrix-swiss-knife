"""BotHub OpenAI-compatible chat completions client.

Backward-compatible facade over `harrix_swiss_knife.integrations.ai`.
New code should prefer `integrations.ai.chat_completion` with an explicit provider.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.integrations.ai.client import chat_completion as ai_chat_completion
from harrix_swiss_knife.integrations.ai.errors import AiApiError, RequestCancelledError
from harrix_swiss_knife.integrations.ai.text_utils import strip_markdown_fences

if TYPE_CHECKING:
    import http.client
    from collections.abc import Callable, Sequence

    from harrix_swiss_knife.integrations.ai.config import ProviderName

_DEFAULT_TIMEOUT_SEC = 120

# Re-export names expected by existing call sites.
BotHubApiError = AiApiError


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
    """Send a chat completion request and return assistant text.

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

    """
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


__all__ = [
    "BotHubApiError",
    "RequestCancelledError",
    "chat_completion",
    "strip_markdown_fences",
]
