"""Text-related actions (AI, formatting, and transformations)."""

from harrix_swiss_knife.actions.text.fix_text_with_ai import OnFixTextWithAI
from harrix_swiss_knife.actions.text.fix_text_with_ai_from_clipboard import (
    OnFixTextWithAIFromClipboard,
)

__all__ = [
    "OnFixTextWithAI",
    "OnFixTextWithAIFromClipboard",
]
