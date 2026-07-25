"""Helpers for filling New Markdown template fields via BotHub."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from harrix_swiss_knife.integrations.bothub_client import strip_markdown_fences

if TYPE_CHECKING:
    from harrix_swiss_knife.template_parser import TemplateField

_EXCLUDED_FIELD_TYPES = frozenset({"image", "images", "file", "files", "bool"})
_REVIEW_FIELD_NAME = "Review"


def format_fields_for_prompt(fields: list[TemplateField]) -> str:
    """Format candidate fields as a bullet list for the BotHub prompt."""
    return "\n".join(f"- {field.name} ({field.field_type})" for field in fields)


def is_ai_fill_candidate(field: TemplateField, value: str) -> bool:
    """Return whether a field should be sent to / filled by AI.

    Excludes `Review`, media, and bool fields. Includes empty values, numeric zeros,
    and int/float values that still equal the template default.

    """
    if field.name == _REVIEW_FIELD_NAME:
        return False
    if field.field_type in _EXCLUDED_FIELD_TYPES:
        return False

    stripped = (value or "").strip()
    if not stripped:
        return True

    if field.field_type in {"int", "float"}:
        try:
            number = float(stripped.replace(",", "."))
        except ValueError:
            return False
        if number == 0:
            return True
        if field.default_value is None:
            return False
        try:
            default_number = float(str(field.default_value).replace(",", "."))
        except ValueError:
            return False
        return number == default_number

    return False


def parse_template_fields_response(text: str) -> dict[str, str]:
    """Parse a JSON object of field name → string value from BotHub output.

    Ignores `Review`. Raises `ValueError` on empty/invalid JSON, `TypeError` if
    the root value is not an object.

    """
    cleaned = strip_markdown_fences(text)
    if not cleaned.strip():
        msg = "Empty response from BotHub."
        raise ValueError(msg)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        msg = f"Invalid JSON from BotHub: {exc}"
        raise ValueError(msg) from exc
    if not isinstance(data, dict):
        msg = "BotHub response must be a JSON object."
        raise TypeError(msg)

    result: dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(key, str):
            continue
        if key == _REVIEW_FIELD_NAME:
            continue
        if value is None:
            continue
        result[key] = value if isinstance(value, str) else str(value)
    return result
