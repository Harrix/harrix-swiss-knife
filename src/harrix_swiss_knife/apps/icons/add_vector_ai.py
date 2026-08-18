"""BotHub fill for Add Vector Image metadata fields."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.icons.keywords_update import parse_keywords_text
from harrix_swiss_knife.apps.icons.vector_render import render_icon_to_image
from harrix_swiss_knife.integrations.bothub import (
    BothubRequestState,
    build_prompt,
    get_max_image_side,
    qimage_bytes_and_mime,
    run_bothub_request,
    show_bothub_prompt_build_error,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from PySide6.QtWidgets import QPushButton, QWidget

PROMPT_KEY = "vector_icons_add_image"
_RASTER_SIDE = 768
_FIELD_RE = re.compile(
    r"^(filename|name|category|tags)\s*:\s*(.*)$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(slots=True)
class AddVectorAiFill:
    """Parsed AI suggestions for the add-vector dialog."""

    filename: str = ""
    name: str = ""
    category: str = ""
    tags: list[str] | None = None


def parse_add_vector_ai_response(text: str) -> AddVectorAiFill:
    """Parse structured AI response into dialog fields."""
    result = AddVectorAiFill(tags=[])
    current_tags: list[str] = []
    in_tags = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = _FIELD_RE.match(line)
        if match is not None:
            key = match.group(1).casefold()
            value = match.group(2).strip()
            in_tags = key == "tags"
            if key == "filename":
                result.filename = value
            elif key == "name":
                result.name = value
            elif key == "category":
                result.category = value
            elif key == "tags" and value:
                current_tags.extend(parse_keywords_text(value))
            continue
        if in_tags:
            current_tags.extend(parse_keywords_text(line))
    result.tags = parse_keywords_text("\n".join(current_tags))
    return result


def request_add_vector_fill(
    parent: QWidget | None,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    icon_path: Path,
    existing_stems: list[str],
    category: str,
    filename: str,
    name: str,
    tags: list[str],
    fill_button: QPushButton | None,
    on_fill: Callable[[AddVectorAiFill], None],
) -> None:
    """Send raster preview + existing filename list to BotHub and fill metadata."""
    image = render_icon_to_image(icon_path, _RASTER_SIDE)
    if image is None or image.isNull():
        message_box.warning(parent, "Fill with AI", f"Could not rasterize icon:\n{icon_path}")
        return

    stems_text = "\n".join(existing_stems[:2000])
    try:
        image_data = qimage_bytes_and_mime(image, max_image_side=get_max_image_side(app_config, default=_RASTER_SIDE))
        prompt_text = build_prompt(
            app_config,
            PROMPT_KEY,
            {
                "EXISTING_FILES": stems_text,
                "CATEGORY": category,
                "FILENAME": filename,
                "NAME": name,
                "TAGS": "\n".join(tags),
            },
            prompt_display_name="vector_icons_add_image",
        )
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        return

    if fill_button is not None:
        fill_button.setEnabled(False)

    def restore_button() -> None:
        if fill_button is not None:
            fill_button.setEnabled(True)

    def on_success(response_text: str) -> None:
        restore_button()
        parsed = parse_add_vector_ai_response(response_text)
        if not parsed.filename and not parsed.name and not parsed.category and not parsed.tags:
            message_box.warning(parent, "Fill with AI", "BotHub returned no usable fields.")
            return
        on_fill(parsed)

    def on_request_error(error_message: str) -> None:
        restore_button()
        message_box.critical(parent, "BotHub Error", error_message)

    def on_request_cancelled() -> None:
        restore_button()

    started = run_bothub_request(
        parent,
        app_config,
        prompt_text,
        on_success,
        image=image_data,
        toast_message="Filling icon metadata…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_request_error,
        on_cancelled=on_request_cancelled,
    )
    if not started:
        restore_button()
