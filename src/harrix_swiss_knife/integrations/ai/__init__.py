"""Multi-provider AI chat client (BotHub, BotHub.ru, OpenAI, Open Router, Anthropic, Gemini)."""

from __future__ import annotations

from harrix_swiss_knife.integrations.ai.client import chat_completion
from harrix_swiss_knife.integrations.ai.config import (
    BOTHUB_ROUTERS,
    PROVIDERS,
    ProviderName,
    get_api_key,
    get_chat_provider,
    get_connection_params_for_provider,
    get_max_image_side,
    get_provider_settings,
    get_speech_model_for_provider,
    get_speech_provider,
    is_bothub_router,
)
from harrix_swiss_knife.integrations.ai.errors import AiApiError, RequestCancelledError
from harrix_swiss_knife.integrations.ai.text_utils import strip_markdown_fences

__all__ = [
    "BOTHUB_ROUTERS",
    "PROVIDERS",
    "AiApiError",
    "ProviderName",
    "RequestCancelledError",
    "chat_completion",
    "get_api_key",
    "get_chat_provider",
    "get_connection_params_for_provider",
    "get_max_image_side",
    "get_provider_settings",
    "get_speech_model_for_provider",
    "get_speech_provider",
    "is_bothub_router",
    "strip_markdown_fences",
]
