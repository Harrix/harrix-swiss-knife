"""BotHub translation of recognized text into the local language."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.apps.common.apps_config import (
    get_apps_local_language,
    get_apps_local_language_display_name,
)
from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template

PROMPT_MISSING_MSG = "Prompt text_translate_to_local is not configured in config.json."


def build_text_translate_prompt(text: str, config: dict[str, Any]) -> str:
    """Build BotHub prompt to translate `text` into the local language.

    Raises:

    - `ValueError`: If prompt template or API key is not configured.

    """
    return build_prompt(
        config,
        "text_translate_to_local",
        {
            "TEXT": text,
            "LOCAL_LANGUAGE": get_apps_local_language_display_name(config),
            "LOCAL_LANGUAGE_CODE": get_apps_local_language(config),
        },
        prompt_display_name="text_translate_to_local",
    )


def get_text_translate_prompt_template(config: dict[str, Any]) -> str | None:
    """Return stripped `prompts.text_translate_to_local` template, or `None` if missing."""
    return get_prompt_template(config, "text_translate_to_local")
