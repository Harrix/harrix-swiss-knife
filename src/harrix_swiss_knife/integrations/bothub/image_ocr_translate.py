"""BotHub image OCR + optional translate (prompt image_ocr_translate)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.apps.common.apps_config import (
    get_apps_local_language,
    get_apps_local_language_display_name,
)
from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template

PROMPT_MISSING_MSG = "Prompt image_ocr_translate is not configured in config.json."


def build_image_ocr_translate_prompt(config: dict[str, Any]) -> str:
    """Build BotHub prompt for image OCR with optional translation.

    Raises:

    - `ValueError`: If prompt template or API key is not configured.

    """
    return build_prompt(
        config,
        "image_ocr_translate",
        {
            "LOCAL_LANGUAGE": get_apps_local_language_display_name(config),
            "LOCAL_LANGUAGE_CODE": get_apps_local_language(config),
        },
        prompt_display_name="image_ocr_translate",
    )


def get_image_ocr_translate_prompt_template(config: dict[str, Any]) -> str | None:
    """Return stripped `prompts.image_ocr_translate` template, or `None` if missing."""
    return get_prompt_template(config, "image_ocr_translate")
