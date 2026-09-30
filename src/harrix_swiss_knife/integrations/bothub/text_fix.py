"""BotHub text correction (prompt text_fix_ru)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.integrations.bothub.chat_failover import chat_completion_with_bothub_failover
from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template

PROMPT_MISSING_MSG = "Prompt text_fix_ru is not configured in config.json."
CLIPBOARD_PROMPT_MISSING_MSG = "Prompt text_fix_ru_clipboard is not configured in config.json."


def build_text_fix_from_clipboard_prompt(input_text: str, config: dict[str, Any]) -> str:
    """Build BotHub prompt for clipboard text fix (preserves original paragraph breaks).

    Raises:

    - `ValueError`: If prompt template or API key is not configured.

    """
    return build_prompt(
        config,
        "text_fix_ru_clipboard",
        {"TEXT": input_text},
        prompt_display_name="text_fix_ru_clipboard",
    )


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
    return chat_completion_with_bothub_failover(config, build_text_fix_prompt(input_text, config))


def get_text_fix_from_clipboard_prompt_template(config: dict[str, Any]) -> str | None:
    """Return stripped `prompts.text_fix_ru_clipboard` template, or `None` if missing."""
    return get_prompt_template(config, "text_fix_ru_clipboard")


def get_text_fix_prompt_template(config: dict[str, Any]) -> str | None:
    """Return stripped `prompts.text_fix_ru` template, or `None` if missing."""
    return get_prompt_template(config, "text_fix_ru")
