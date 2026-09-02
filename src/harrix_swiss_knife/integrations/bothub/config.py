"""AI / BotHub connection settings from application config."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.ai.config import (
    get_api_key,
    get_api_key_missing_message,
    get_chat_provider,
    get_connection_params_for_provider,
    get_max_image_side,
    get_speech_model_for_provider,
    get_speech_provider,
    provider_supports_speech,
)
from harrix_swiss_knife.integrations.bothub.network import resolve_bothub_proxy_url

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from harrix_swiss_knife.integrations.ai.config import ProviderName

API_KEY_MISSING_MSG = (
    "AI API key is not configured.\n\nSet ai.provider in config.json and add the matching key file under api-keys/."
)


def get_active_provider(config: dict[str, Any], *, for_speech: bool = False) -> ProviderName:
    """Return chat or speech provider ID from config."""
    return get_speech_provider(config) if for_speech else get_chat_provider(config)


def get_connection_params(
    config: dict[str, Any],
    *,
    for_speech: bool = False,
) -> tuple[str, str, str, str | None]:
    """Return `(api_key, base_url, model, proxy_url)` for the active provider."""
    provider = get_active_provider(config, for_speech=for_speech)
    api_key, base_url, model, _ = get_connection_params_for_provider(
        config,
        provider,
        for_speech=for_speech,
    )
    return api_key, base_url, model, resolve_bothub_proxy_url(config)


def get_proxy_url(config: dict[str, Any]) -> str | None:
    """Resolve HTTP proxy for AI requests."""
    return resolve_bothub_proxy_url(config)


def get_speech_model(config: dict[str, Any]) -> str:
    """Return speech recognition model ID from the speech provider settings."""
    provider = get_speech_provider(config)
    return get_speech_model_for_provider(config, provider)


def validate_api_key(
    config: dict[str, Any],
    *,
    parent: QWidget | None = None,
    show_message: bool = True,
    for_speech: bool = False,
) -> str | None:
    """Return API key if configured; optionally show warning dialog and return `None`."""
    provider = get_active_provider(config, for_speech=for_speech)
    if for_speech and not provider_supports_speech(provider):
        if show_message:
            message_box.warning(
                parent,
                "AI Speech",
                (
                    "Anthropic does not support speech-to-text.\n\n"
                    'Set ai.speech_provider to "openai", "openrouter", "gemini", "bothub", or "bothub.ru".'
                ),
            )
        return None

    api_key = get_api_key(config, provider)
    if api_key and not api_key.startswith("paste-your-"):
        return api_key
    if show_message:
        message_box.warning(parent, "AI API Key", get_api_key_missing_message(provider))
    return None


# Re-export for call sites that need image sizing without importing ai.config.
__all__ = [
    "API_KEY_MISSING_MSG",
    "get_active_provider",
    "get_connection_params",
    "get_max_image_side",
    "get_proxy_url",
    "get_speech_model",
    "validate_api_key",
]
