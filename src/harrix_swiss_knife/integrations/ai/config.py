"""Resolve AI provider settings from application config."""

from __future__ import annotations

from typing import Any, Literal

from harrix_swiss_knife.integrations.http_transport import resolve_proxy_url

ProviderName = Literal["bothub", "bothub.ru", "openai", "anthropic", "gemini"]

PROVIDERS: tuple[ProviderName, ...] = ("bothub", "bothub.ru", "openai", "anthropic", "gemini")
BOTHUB_ROUTERS: tuple[ProviderName, ...] = ("bothub", "bothub.ru")
_PROVIDER_ALIASES: dict[str, ProviderName] = {
    "bothub.ru": "bothub.ru",
    "bothub_ru": "bothub.ru",
    "bothub-ru": "bothub.ru",
}

_DEFAULTS: dict[ProviderName, dict[str, Any]] = {
    "bothub": {
        "base_url": "https://bothub.chat/api/v2/openai/v1",
        "model": "gpt-5.4",
        "speech_model": "gemini-3.1-flash-lite-preview",
        "api_key_config": "bothub_api_key",
        "settings_key": "bothub",
        "example_key_file": "api-keys/bothub-api-key.txt",
    },
    "bothub.ru": {
        "base_url": "https://openai.bothub.ru/v1",
        "model": "gpt-5.4",
        "speech_model": "gemini-3.1-flash-lite-preview",
        "api_key_config": "bothub_ru_api_key",
        "settings_key": "bothub_ru",
        "example_key_file": "api-keys/bothub-ru-api-key.txt",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4.1",
        "speech_model": "whisper-1",
        "api_key_config": "openai_api_key",
        "settings_key": "openai",
        "example_key_file": "api-keys/openai-api-key.txt",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com",
        "model": "claude-sonnet-4-6",
        "speech_model": "",
        "max_tokens": 8192,
        "api_key_config": "anthropic_api_key",
        "settings_key": "anthropic",
        "example_key_file": "api-keys/anthropic-api-key.txt",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "model": "gemini-2.5-flash",
        "speech_model": "gemini-2.5-flash",
        "api_key_config": "gemini_api_key",
        "settings_key": "gemini",
        "example_key_file": "api-keys/gemini-api-key.txt",
    },
}


def get_api_key(config: dict[str, Any], provider: ProviderName) -> str:
    """Return API key string for the provider (may be empty)."""
    key_name = str(_DEFAULTS[provider]["api_key_config"])
    return str(config.get(key_name, "")).strip()


def get_api_key_missing_message(provider: ProviderName) -> str:
    """User-facing setup hint for a missing API key."""
    example = _DEFAULTS[provider]["example_key_file"]
    label = {
        "bothub": "BotHub",
        "bothub.ru": "BotHub.ru",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "gemini": "Gemini",
    }[provider]
    return (
        f"{label} API key is not configured.\n\n"
        f"Copy {example.replace('.txt', '.example.txt')} to {example} "
        "and add your access token (one line)."
    )


def get_chat_provider(config: dict[str, Any]) -> ProviderName:
    """Return the configured chat/vision provider (default bothub)."""
    ai_cfg = config.get("ai") or {}
    if not isinstance(ai_cfg, dict):
        return "bothub"
    return normalize_provider(str(ai_cfg.get("provider", "bothub")))


def get_connection_params_for_provider(
    config: dict[str, Any],
    provider: ProviderName,
    *,
    for_speech: bool = False,
) -> tuple[str, str, str, str | None]:
    """Return `(api_key, base_url, model, proxy_url)` for a provider."""
    settings = get_provider_settings(config, provider)
    api_key = get_api_key(config, provider)
    base_url = str(settings.get("base_url", "")).strip()
    if for_speech:
        model = str(settings.get("speech_model") or settings.get("model") or "").strip()
    else:
        model = str(settings.get("model") or "").strip()
    proxy_url = _resolve_config_proxy_url(config)
    return api_key, base_url, model, proxy_url


def get_max_image_side(config: dict[str, Any], default: int = 1600) -> int:
    """Return max image side from `ai`, then legacy `bothub`."""
    ai_cfg = config.get("ai") or {}
    if isinstance(ai_cfg, dict) and ai_cfg.get("max_image_side") is not None:
        try:
            return int(ai_cfg["max_image_side"])
        except (TypeError, ValueError):
            pass
    bothub_cfg = config.get("bothub") or {}
    if isinstance(bothub_cfg, dict) and bothub_cfg.get("max_image_side") is not None:
        try:
            return int(bothub_cfg["max_image_side"])
        except (TypeError, ValueError):
            pass
    return default


def get_provider_settings(config: dict[str, Any], provider: ProviderName) -> dict[str, Any]:
    """Return merged defaults + config section for a provider."""
    defaults = _DEFAULTS[provider]
    settings_key = str(defaults["settings_key"])
    section = config.get(settings_key) or {}
    if not isinstance(section, dict):
        section = {}
    merged = dict(defaults)
    merged.update(section)
    return merged


def get_speech_model_for_provider(config: dict[str, Any], provider: ProviderName) -> str:
    """Return speech model ID for the provider."""
    settings = get_provider_settings(config, provider)
    return str(settings.get("speech_model") or settings.get("model") or "").strip()


def get_speech_provider(config: dict[str, Any]) -> ProviderName:
    """Return speech provider; empty `ai.speech_provider` means chat provider."""
    ai_cfg = config.get("ai") or {}
    if not isinstance(ai_cfg, dict):
        return get_chat_provider(config)
    speech = str(ai_cfg.get("speech_provider", "")).strip()
    if not speech:
        return get_chat_provider(config)
    return normalize_provider(speech)


def is_bothub_router(provider: ProviderName) -> bool:
    """Return whether `provider` is a BotHub site router (`bothub` or `bothub.ru`)."""
    return provider in BOTHUB_ROUTERS


def normalize_provider(value: str | None) -> ProviderName:
    """Normalize a provider ID; unknown values fall back to bothub."""
    name = (value or "bothub").strip().lower()
    alias = _PROVIDER_ALIASES.get(name)
    if alias is not None:
        return alias
    if name in PROVIDERS:
        return name  # type: ignore[return-value]
    return "bothub"


def other_bothub_router(provider: ProviderName) -> ProviderName:
    """Return the other BotHub site when `provider` is a BotHub router."""
    if provider == "bothub":
        return "bothub.ru"
    return "bothub"


def provider_supports_speech(provider: ProviderName) -> bool:
    """Return whether the provider can accept audio transcription requests."""
    return provider != "anthropic"


def _resolve_config_proxy_url(config: dict[str, Any]) -> str | None:
    """Resolve proxy from `ai.proxy` / `bothub.proxy` and environment (no Qt)."""
    ai_cfg = config.get("ai") or {}
    config_proxy = ""
    if isinstance(ai_cfg, dict):
        config_proxy = str(ai_cfg.get("proxy", "")).strip()
    if not config_proxy:
        bothub_cfg = config.get("bothub") or {}
        if isinstance(bothub_cfg, dict):
            config_proxy = str(bothub_cfg.get("proxy", "")).strip()
    return resolve_proxy_url(config_proxy=config_proxy or None, qt_proxy_url=None)
