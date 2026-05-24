"""Food-specific AI source dialog before BotHub processing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.dialogs.ai_source_dialog import AiSourceDialog as _BaseAiSourceDialog
from harrix_swiss_knife.apps.food.text_input_dialog import FOOD_TEXT_PLACEHOLDER

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

_FOOD_AI_DESCRIPTION = (
    "Paste food text (optional), add a nutrition label or meal photo (optional), or both. "
    "At least one is required to send to AI. "
    "Use Enter Text Manually to skip AI and enter food lines yourself."
)


class AiSourceDialog(_BaseAiSourceDialog):
    """Modal dialog to collect food source text and/or an image."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the food AI source dialog."""
        super().__init__(
            parent,
            title="Add Food with AI",
            description=_FOOD_AI_DESCRIPTION,
            placeholder=FOOD_TEXT_PLACEHOLDER,
        )
