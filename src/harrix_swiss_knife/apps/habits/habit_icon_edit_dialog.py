"""Dialog for editing habit emoji and Lucide icon together."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common.lucide_picker_dialog import LucideChoiceRow
from harrix_swiss_knife.apps.habits.habit_emoji_picker_dialog import HabitEmojiPickerDialog
from harrix_swiss_knife.apps.habits.habit_emojis import HABIT_EMOJI_PRESETS, normalize_habit_emoji
from harrix_swiss_knife.apps.habits.habit_icon_display import (
    HABIT_LUCIDE_PRESETS,
    normalize_habit_lucide_name,
)
from harrix_swiss_knife.integrations.bothub import BothubRequestState
from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_dialog_buttons


class HabitIconEditDialog(QDialog):
    """Choose emoji and optional Lucide icon for a habit."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        emoji: str = "",
        icon_lucide: str = "",
        habit_name: str = "",
        habit_id: int | None = None,
        app_config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the icon editor.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `emoji` (`str`): Current emoji.
        - `icon_lucide` (`str`): Current Lucide id.
        - `habit_name` (`str`): Habit name used as AI suggest query.
        - `habit_id` (`int | None`): Habit id for emoji fallback.
        - `app_config` (`dict[str, Any] | None`): App config for Lucide AI.

        """
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle("Edit Habit Icon")
        self.setMinimumWidth(440)
        self._habit_id = habit_id
        self._habit_name = habit_name.strip()
        self._emoji = normalize_habit_emoji(emoji, habit_id=habit_id)
        self._app_config = app_config if app_config is not None else h.dev.config_load(get_config_path_str())
        self._bothub_state = BothubRequestState()

        root = QVBoxLayout(self)
        form = QFormLayout()

        emoji_row = QHBoxLayout()
        self._emoji_preview = QPushButton(self._emoji)
        self._emoji_preview.setFixedSize(44, 44)
        self._emoji_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self._emoji_preview.setStyleSheet("QPushButton { font-size: 22px; }")
        self._emoji_preview.setToolTip("Choose emoji")
        self._emoji_preview.clicked.connect(self._choose_emoji)
        choose_button = QPushButton("Choose…")
        choose_button.clicked.connect(self._choose_emoji)
        emoji_row.addWidget(self._emoji_preview)
        emoji_row.addWidget(choose_button)
        emoji_row.addStretch(1)
        form.addRow("Emoji:", emoji_row)

        self._lucide_row = LucideChoiceRow(
            self,
            current_name=normalize_habit_lucide_name(icon_lucide),
            presets=HABIT_LUCIDE_PRESETS,
            allow_empty=True,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            suggest_query_provider=lambda: self._habit_name,
        )
        form.addRow("Lucide:", self._lucide_row)
        root.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_lucide_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def selected_emoji(self) -> str:
        """Return the selected emoji."""
        return normalize_habit_emoji(self._emoji, habit_id=self._habit_id)

    def selected_icon_lucide(self) -> str:
        """Return the selected Lucide id (empty when cleared)."""
        return normalize_habit_lucide_name(self._lucide_row.lucide_name())

    def _choose_emoji(self) -> None:
        dialog = HabitEmojiPickerDialog(self, current_emoji=self._emoji)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._emoji = dialog.selected_emoji() or (HABIT_EMOJI_PRESETS[0] if HABIT_EMOJI_PRESETS else "✅")
        self._emoji_preview.setText(self._emoji)
