"""BotHub connection settings from application config."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub.network import resolve_bothub_proxy_url

API_KEY_MISSING_MSG = (
    "BotHub API key is not configured.\n\n"
    "Copy api-keys/bothub-api-key.example.txt to api-keys/bothub-api-key.txt "
    "and add your access token (one line)."
)


def get_connection_params(config: dict[str, Any]) -> tuple[str, str, str, str | None]:
    """Return (api_key, base_url, model, proxy_url) for BotHub chat completion."""
    api_key = str(config.get("bothub_api_key", "")).strip()
    bothub_cfg = config.get("bothub") or {}
    base_url = str(bothub_cfg.get("base_url", "https://bothub.chat/api/v2/openai/v1")).strip()
    model = str(bothub_cfg.get("model", "gpt-5.4")).strip()
    proxy_url = resolve_bothub_proxy_url(config)
    return api_key, base_url, model, proxy_url


def validate_api_key(
    config: dict[str, Any],
    *,
    parent: object | None = None,
    show_message: bool = True,
) -> str | None:
    """Return API key if configured; optionally show warning dialog and return None."""
    api_key = str(config.get("bothub_api_key", "")).strip()
    if api_key and not api_key.startswith("paste-your-"):
        return api_key
    if show_message:
        message_box.warning(parent, "BotHub API Key", API_KEY_MISSING_MSG)
    return None
