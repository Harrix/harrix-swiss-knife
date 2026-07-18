"""BotHub image OCR (prompt image_ocr_to_markdown)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template

PROMPT_MISSING_MSG = "Prompt image_ocr_to_markdown is not configured in config.json."


def build_image_ocr_prompt(config: dict[str, Any]) -> str:
    """Build BotHub prompt for image OCR.

    Raises:

    - `ValueError`: If prompt template or API key is not configured.

    """
    return build_prompt(
        config,
        "image_ocr_to_markdown",
        {},
        prompt_display_name="image_ocr_to_markdown",
    )


def get_image_ocr_prompt_template(config: dict[str, Any]) -> str | None:
    """Return stripped `prompts.image_ocr_to_markdown` template, or None if missing."""
    return get_prompt_template(config, "image_ocr_to_markdown")
