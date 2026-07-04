"""Text-related actions (AI, formatting, and transformations)."""

from harrix_swiss_knife.actions.text.fix_text_with_ai import OnFixTextWithAI
from harrix_swiss_knife.actions.text.fix_text_with_ai_from_clipboard import (
    OnFixTextWithAIFromClipboard,
)
from harrix_swiss_knife.actions.text.quick_launcher import OnQuickLauncher
from harrix_swiss_knife.actions.text.speech_to_text_with_ai import OnSpeechToTextWithAI

__all__ = [
    "OnFixTextWithAI",
    "OnFixTextWithAIFromClipboard",
    "OnQuickLauncher",
    "OnSpeechToTextWithAI",
]
