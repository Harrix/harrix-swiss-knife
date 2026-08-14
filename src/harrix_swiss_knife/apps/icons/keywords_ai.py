"""BotHub helper to expand icon keywords from a raster preview."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.icons.keywords_update import parse_keywords_text
from harrix_swiss_knife.apps.icons.vector_render import render_icon_to_image
from harrix_swiss_knife.integrations.bothub import (
    BothubRequestState,
    build_prompt,
    qimage_bytes_and_mime,
    run_bothub_request,
    show_bothub_prompt_build_error,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from PySide6.QtWidgets import QPushButton, QWidget

PROMPT_KEY = "vector_icons_keywords"
_RASTER_SIDE = 768


def request_keywords_fill(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    icon_path: Path,
    category: str,
    tags: list[str],
    fill_button: QPushButton,
    on_tags: Callable[[list[str]], None],
) -> None:
    """Send a raster preview plus category/tags to BotHub and return keywords."""
    image = render_icon_to_image(icon_path, _RASTER_SIDE)
    if image is None or image.isNull():
        message_box.warning(parent, "Process with AI", f"Could not rasterize icon:\n{icon_path}")
        return

    try:
        image_data = qimage_bytes_and_mime(image, max_image_side=_max_image_side(app_config))
        prompt_text = build_prompt(
            app_config,
            PROMPT_KEY,
            {
                "CATEGORY": category,
                "TAGS": "\n".join(tags),
            },
            prompt_display_name="vector_icons_keywords",
        )
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        return

    fill_button.setEnabled(False)

    def on_success(response_text: str) -> None:
        fill_button.setEnabled(True)
        parsed = parse_keywords_text(response_text)
        if not parsed:
            message_box.warning(parent, "Process with AI", "BotHub returned no keywords.")
            return
        on_tags(parsed)

    def on_error(error_message: str) -> None:
        fill_button.setEnabled(True)
        message_box.critical(parent, "BotHub Error", error_message)

    def on_cancelled() -> None:
        fill_button.setEnabled(True)

    started = run_bothub_request(
        parent,
        app_config,
        prompt_text,
        on_success,
        image=image_data,
        toast_message="Processing keywords…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        fill_button.setEnabled(True)


def _max_image_side(app_config: dict[str, Any]) -> int:
    bothub_cfg = app_config.get("bothub") or {}
    try:
        return int(bothub_cfg.get("max_image_side", _RASTER_SIDE))
    except (TypeError, ValueError):
        return _RASTER_SIDE
