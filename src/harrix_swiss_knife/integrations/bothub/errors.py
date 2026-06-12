"""BotHub UI error helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub.config import API_KEY_MISSING_MSG
from harrix_swiss_knife.integrations.bothub.text_fix import PROMPT_MISSING_MSG

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


def show_bothub_prompt_build_error(parent: QWidget | None, exc: ValueError) -> None:
    """Show a dialog for prompt-build failures from BotHub integrations."""
    msg = str(exc)
    if msg == API_KEY_MISSING_MSG:
        message_box.warning(parent, "BotHub API Key", msg)
    elif msg == PROMPT_MISSING_MSG:
        message_box.warning(parent, "Prompt", msg)
    else:
        message_box.warning(parent, "Prompt", msg)
