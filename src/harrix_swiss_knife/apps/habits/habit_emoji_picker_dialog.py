"""Dialog for choosing a habit emoji from presets or custom input."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.emoji_picker_dialog import EmojiPickerDialog
from harrix_swiss_knife.apps.habits.habit_emojis import HABIT_EMOJI_PRESETS, normalize_habit_emoji

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class HabitEmojiPickerDialog(EmojiPickerDialog):
    """Pick a habit emoji from a preset grid or paste a custom emoji."""

    def __init__(self, parent: QWidget | None = None, *, current_emoji: str = "") -> None:
        """Initialize the emoji picker dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `current_emoji` (`str`): Preselected emoji. Defaults to `""`.

        """
        super().__init__(
            parent,
            current_emoji=normalize_habit_emoji(current_emoji),
            presets=HABIT_EMOJI_PRESETS,
            allow_empty=False,
        )

    def selected_emoji(self) -> str:
        """Return the chosen emoji, never empty."""
        return normalize_habit_emoji(super().selected_emoji())
