"""BotHub text correction (prompt text_fix_ru)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.integrations.bothub.config import get_connection_params
from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template
from harrix_swiss_knife.integrations.bothub_client import chat_completion

PROMPT_MISSING_MSG = "Prompt text_fix_ru is not configured in config.json."


def build_text_fix_prompt(input_text: str, config: dict[str, Any]) -> str:
    """Build full BotHub prompt for the given input text.

    Raises:

    - `ValueError`: If prompt template or API key is not configured.

    """
    return build_prompt(config, "text_fix_ru", {"TEXT": input_text}, prompt_display_name="text_fix_ru")


def fix_text_sync(input_text: str, config: dict[str, Any]) -> str:
    """Send text to BotHub synchronously and return corrected text.

    Raises:

    - `ValueError`: Configuration errors (prompt or API key).
    - `BotHubApiError`: API or network failure.

    """
    prompt_text = build_text_fix_prompt(input_text, config)
    api_key, base_url, model, proxy_url = get_connection_params(config)
    return chat_completion(
        api_key=api_key,
        base_url=base_url,
        model=model,
        text=prompt_text,
        proxy_url=proxy_url,
    )


def get_text_fix_prompt_template(config: dict[str, Any]) -> str | None:
    """Return stripped ``prompts.text_fix_ru`` template, or None if missing."""
    return get_prompt_template(config, "text_fix_ru")
