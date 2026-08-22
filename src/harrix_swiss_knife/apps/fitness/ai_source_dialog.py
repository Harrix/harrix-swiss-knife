"""Fitness-specific AI source dialog before BotHub processing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.dialogs.text_image_source_dialog import (
    SEND_TO_AI_BUTTON_STYLE,
    TextImageSourceDialog,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

SETS_TEXT_PLACEHOLDER = "Pull-ups 12, then 10, and 20 squats…"


def create_fitness_dashboard_text_dialog(parent: QWidget | None = None) -> TextImageSourceDialog:
    """Build a text-only, large-type dialog for the Fitness dashboard."""
    return TextImageSourceDialog(
        parent,
        title="Write text",
        description="Describe the sets you completed. AI will turn this into a set list.",
        placeholder=SETS_TEXT_PLACEHOLDER,
        show_text=True,
        text_required=True,
        show_images=False,
        show_skip_manual=False,
        accept_button_text="Send to AI",
        accept_button_emoji="🤖",
        accept_button_style=SEND_TO_AI_BUTTON_STYLE,
        large_ui=True,
    )
