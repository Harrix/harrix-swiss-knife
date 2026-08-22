"""Food-specific AI source dialog before BotHub processing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.dialogs.text_image_source_dialog import (
    SEND_TO_AI_BUTTON_STYLE,
    TextImageSourceDialog,
)
from harrix_swiss_knife.apps.common.widgets.image_picker import ImagePickerMode
from harrix_swiss_knife.apps.food.text_input_dialog import FOOD_TEXT_PLACEHOLDER

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

_FOOD_AI_DESCRIPTION = (
    "Paste food text (optional), add nutrition label or meal photos (optional), or both. "
    "At least one is required to send to AI. "
    "Use Enter Text Manually to skip AI and enter food lines yourself."
)


class AiSourceDialog(TextImageSourceDialog):
    """Modal dialog to collect food source text and/or images."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        max_image_side: int | None = None,
        initial_image_path: str | None = None,
        initial_image_paths: list[str] | None = None,
    ) -> None:
        """Initialize the food AI source dialog."""
        super().__init__(
            parent,
            title="Add Food with AI",
            description=_FOOD_AI_DESCRIPTION,
            placeholder=FOOD_TEXT_PLACEHOLDER,
            image_mode=ImagePickerMode.MULTI,
            show_skip_manual=True,
            accept_button_text="Send to AI",
            accept_button_emoji="🤖",
            accept_button_style=SEND_TO_AI_BUTTON_STYLE,
            max_image_side=max_image_side,
            initial_image_path=initial_image_path,
            initial_image_paths=initial_image_paths,
        )


def create_food_dashboard_photo_dialog(
    parent: QWidget | None = None,
    *,
    max_image_side: int | None = None,
) -> TextImageSourceDialog:
    """Build a photo-only, large-type dialog for the Food dashboard."""
    return TextImageSourceDialog(
        parent,
        title="Add photo",
        description="Add a meal photo or nutrition label.",
        show_text=False,
        show_images=True,
        images_required=True,
        image_mode=ImagePickerMode.MULTI,
        image_label="Photo (drag, paste Ctrl+V, or select files):",
        show_skip_manual=False,
        accept_button_text="Send to AI",
        accept_button_emoji="🤖",
        accept_button_style=SEND_TO_AI_BUTTON_STYLE,
        max_image_side=max_image_side,
        large_ui=True,
    )


def create_food_dashboard_text_dialog(parent: QWidget | None = None) -> TextImageSourceDialog:
    """Build a text-only, large-type dialog for the Food dashboard."""
    return TextImageSourceDialog(
        parent,
        title="Write text",
        description="Describe what you ate. AI will turn this into a food log.",
        placeholder="Oatmeal with banana and coffee…",
        show_text=True,
        text_required=True,
        show_images=False,
        show_skip_manual=False,
        accept_button_text="Send to AI",
        accept_button_emoji="🤖",
        accept_button_style=SEND_TO_AI_BUTTON_STYLE,
        large_ui=True,
    )
