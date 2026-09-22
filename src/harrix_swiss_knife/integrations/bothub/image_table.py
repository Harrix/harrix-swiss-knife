"""BotHub image table extraction (prompt image_table_to_excel)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.integrations.ai.config import get_ai_prompts, get_ai_section, get_chat_provider
from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template

PROMPT_KEY = "image_table_to_excel"
DEFAULT_IMAGE_TABLE_MODEL = "gpt-5.6"
IMAGE_TABLE_MODEL_KEY = "image_table_model"

_DEFAULT_PROMPT = """You extract tables from a screenshot or photo.

Return JSON only. No markdown fences, comments, or extra text.

Build one rectangular HTML table. Every row covers the same `column_count`.

Schema:

{
  "title": "Caption above the table, or empty string",
  "column_count": 4,
  "rows": [
    {
      "cells": [
        {
          "text": "cell text exactly as shown",
          "bold": true,
          "fill": "#5B8DB8",
          "color": "#FFFFFF",
          "align": "left",
          "colspan": 1,
          "rowspan": 1
        }
      ]
    }
  ]
}

Grid rules:

- Choose `column_count` first so the whole screenshot fits one rectangle, including side panels.
- Emit a cell only at the top-left of its merged range.
  Never output a cell in a slot already covered by an earlier rowspan or colspan.
- New cells in a row plus already-occupied slots must add up to `column_count`.
- A sidebar or right-hand panel beside several stacked blocks is one cell:
  put it on the first of those rows, in the last columns, with rowspan equal to every row it covers.
- Nested sections (a header bar, then a 2-column block, then a 3-column block)
  still share the same `column_count`. Narrower blocks use colspan on the left.
  They must not push extra cells past the sidebar.
- A section header that sits only over the left stack uses colspan = left width;
  the sidebar continues in the remaining columns.
- fill and color are #RRGGBB from the screenshot (header bars, zebra rows, white cells).
- bold is true for header cells and other visually bold text.
- align is left, center, or right.
- Keep the original language. The word false, emails, phones, and codes stay as text, not booleans.
- If several disconnected tables are visible, return {"tables": [ { ... }, { ... } ] }.
- If there is no table, return {"title": "", "rows": []}.
"""


def build_image_table_prompt(config: dict[str, Any]) -> str:
    """Build BotHub prompt for extracting a styled table from an image.

    Raises:

    - `ValueError`: If the API key is not configured.

    """
    if get_prompt_template(config, PROMPT_KEY):
        return build_prompt(config, PROMPT_KEY, {}, prompt_display_name=PROMPT_KEY)
    ai_cfg = get_ai_section(config)
    return build_prompt(
        {**config, "ai": {**ai_cfg, "prompts": {**get_ai_prompts(config), PROMPT_KEY: _DEFAULT_PROMPT}}},
        PROMPT_KEY,
        {},
        prompt_display_name=PROMPT_KEY,
    )


def get_image_table_model(config: dict[str, Any]) -> str:
    """Return the chat model for table extraction (`ai.image_table_model`, else GPT-5.6)."""
    ai_cfg = get_ai_section(config)
    model = DEFAULT_IMAGE_TABLE_MODEL
    raw = str(ai_cfg.get(IMAGE_TABLE_MODEL_KEY) or "").strip()
    if raw:
        model = raw
    if get_chat_provider(config) == "openrouter" and "/" not in model:
        return f"openai/{model}"
    return model


def get_image_table_prompt_template(config: dict[str, Any]) -> str:
    """Return stripped `prompts.image_table_to_excel` template, or the built-in default."""
    return get_prompt_template(config, PROMPT_KEY) or _DEFAULT_PROMPT.strip()
