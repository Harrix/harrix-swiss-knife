"""Helpers for filling New Markdown template fields via BotHub."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub import (
    BothubRequestState,
    build_prompt,
    qimage_bytes_and_mime,
    run_bothub_request_blocking,
    show_bothub_prompt_build_error,
)
from harrix_swiss_knife.integrations.bothub_client import strip_markdown_fences
from harrix_swiss_knife.screenshot import capture_region

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from harrix_swiss_knife.template_parser import TemplateField

_EXCLUDED_FIELD_TYPES = frozenset({"image", "images", "file", "files", "bool"})
_REVIEW_FIELD_NAME = "Review"


def collect_ai_fill_candidates_from_fields(fields: list[TemplateField]) -> list[TemplateField]:
    """Return fields that would be AI-filled when the form is still at defaults."""
    candidates: list[TemplateField] = []
    for field in fields:
        if field.field_type in {"int", "float"} and field.default_value is not None:
            value = str(field.default_value)
        else:
            value = ""
        if is_ai_fill_candidate(field, value):
            candidates.append(field)
    return candidates


def fill_template_fields_from_screenshot_ai(
    parent: QWidget | None,
    app_config: dict[str, Any],
    fields: list[TemplateField],
) -> dict[str, str] | None:
    """Capture a region, send it to BotHub, and return parsed field values.

    Returns:

    - `dict[str, str]`: Field values from BotHub on success.
    - `None`: Screenshot cancelled, request cancelled, or a handled error.

    """
    candidates = collect_ai_fill_candidates_from_fields(fields)
    if not candidates:
        message_box.warning(
            parent,
            "Fill with AI",
            "No empty fields to fill for this template.",
        )
        return None

    image = capture_region(show_preview=False, show_shutter_button=True)
    if image is None or image.isNull():
        return None

    bothub_cfg = app_config.get("bothub") or {}
    max_image_side = int(bothub_cfg.get("max_image_side", 1600))
    try:
        image_data = qimage_bytes_and_mime(image, max_image_side=max_image_side)
    except ValueError as exc:
        message_box.critical(parent, "Fill with AI", str(exc))
        return None

    try:
        prompt_text = build_prompt(
            app_config,
            "markdown_template_fields_from_source",
            {
                "FIELDS": format_fields_for_prompt(candidates),
                "RAW_DATA": "",
            },
        )
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        return None

    response_text = run_bothub_request_blocking(
        parent,
        app_config,
        prompt_text,
        images=[image_data],
        state=BothubRequestState(),
    )
    if response_text is None:
        return None

    try:
        values = parse_template_fields_response(response_text)
    except (TypeError, ValueError) as exc:
        message_box.critical(parent, "BotHub Error", f"Could not parse AI response:\n{exc}")
        return None

    if not values:
        message_box.warning(parent, "Fill with AI", "AI returned no field values.")
        return None

    return values


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
