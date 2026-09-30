"""BotHub deep text rewrite (prompt text_rewrite_ru)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.integrations.bothub.chat_failover import chat_completion_with_bothub_failover
from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template

PROMPT_MISSING_MSG = "Prompt text_rewrite_ru is not configured in config.json."


def build_text_rewrite_prompt(input_text: str, config: dict[str, Any]) -> str:
    """Build full BotHub prompt for deep text rewrite.

    Raises:

    - `ValueError`: If prompt template or API key is not configured.

    """
    return build_prompt(config, "text_rewrite_ru", {"TEXT": input_text}, prompt_display_name="text_rewrite_ru")


def get_text_rewrite_prompt_template(config: dict[str, Any]) -> str | None:
    """Return stripped `prompts.text_rewrite_ru` template, or `None` if missing."""
    return get_prompt_template(config, "text_rewrite_ru")


def rewrite_text_sync(input_text: str, config: dict[str, Any]) -> str:
    """Send text to BotHub synchronously and return rewritten text.

    Raises:

    - `ValueError`: Configuration errors (prompt or API key).
    - `BotHubApiError`: API or network failure.

    """
    return chat_completion_with_bothub_failover(config, build_text_rewrite_prompt(input_text, config))
