"""BotHub image table extraction (prompt image_table_to_excel)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template

PROMPT_KEY = "image_table_to_excel"

_DEFAULT_PROMPT = """You extract tables from a screenshot or photo of a table.

Return JSON only. No markdown fences, comments, or extra text.

Schema:

{
  "title": "Caption above the table, or empty string",
  "columns": [{"width": 24}],
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

Rules:

- Reproduce every visible header and data cell. Keep the original language.
- Use HTML-style cells: include a cell only at the top-left of a merged range; set colspan/rowspan.
- fill and color are #RRGGBB from the screenshot (header bars, zebra rows, white cells).
- bold is true for header cells and other visually bold text.
- align is left, center, or right.
- columns.width is optional Excel character width; omit the array if unsure.
- The word false, emails, phones, and codes stay as text, not booleans.
- If several tables are visible, return {"tables": [ { ... }, { ... } ] } using the same per-table schema.
- If there is no table, return {"title": "", "rows": []}.
"""


def build_image_table_prompt(config: dict[str, Any]) -> str:
    """Build BotHub prompt for extracting a styled table from an image.

    Raises:

    - `ValueError`: If the API key is not configured.

    """
    if get_prompt_template(config, PROMPT_KEY):
        return build_prompt(config, PROMPT_KEY, {}, prompt_display_name=PROMPT_KEY)
    return build_prompt(
        {**config, "prompts": {**(config.get("prompts") or {}), PROMPT_KEY: _DEFAULT_PROMPT}},
        PROMPT_KEY,
        {},
        prompt_display_name=PROMPT_KEY,
    )


def get_image_table_prompt_template(config: dict[str, Any]) -> str:
    """Return stripped `prompts.image_table_to_excel` template, or the built-in default."""
    return get_prompt_template(config, PROMPT_KEY) or _DEFAULT_PROMPT.strip()
