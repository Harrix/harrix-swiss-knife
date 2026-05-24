"""Finance-specific AI source dialog before BotHub processing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.dialogs.ai_source_dialog import AiSourceDialog as _BaseAiSourceDialog
from harrix_swiss_knife.apps.finance.text_input_dialog import PURCHASE_TEXT_PLACEHOLDER

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

_FINANCE_AI_DESCRIPTION = (
    "Paste purchase text (optional), add a receipt image (optional), or both. "
    "At least one is required to send to AI. "
    "Use Enter Text Manually to skip AI and type tab-separated purchases yourself."
)


class AiSourceDialog(_BaseAiSourceDialog):
    """Modal dialog to collect purchase source text and/or a receipt image."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the finance AI source dialog."""
        super().__init__(
            parent,
            title="Add Purchases with AI",
            description=_FINANCE_AI_DESCRIPTION,
            placeholder=PURCHASE_TEXT_PLACEHOLDER,
        )
