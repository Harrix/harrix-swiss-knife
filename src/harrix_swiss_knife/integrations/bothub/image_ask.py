"""BotHub screenshot Ask AI (prompt image_ask)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template

PROMPT_MISSING_MSG = "Prompt image_ask is not configured in config.json."
_EMPTY_NOTE = "(none — answer based only on the screenshot)"


def build_image_ask_prompt(config: dict[str, Any], note: str = "") -> str:
    """Build BotHub prompt that answers a question about a screenshot.

    Raises:

    - `ValueError`: If prompt template or API key is not configured.

    """
    note_text = note.strip() or _EMPTY_NOTE
    return build_prompt(
        config,
        "image_ask",
        {"NOTE": note_text},
        prompt_display_name="image_ask",
    )


def get_image_ask_prompt_template(config: dict[str, Any]) -> str | None:
    """Return stripped `prompts.image_ask` template, or `None` if missing."""
    return get_prompt_template(config, "image_ask")
