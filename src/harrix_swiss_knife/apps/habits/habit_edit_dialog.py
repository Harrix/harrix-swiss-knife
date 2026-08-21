"""Dialog for creating or editing a habit."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.habits.habit_emoji_ai import request_habit_emoji_suggestion
from harrix_swiss_knife.apps.habits.habit_emoji_picker_dialog import HabitEmojiPickerDialog
from harrix_swiss_knife.apps.habits.habit_emojis import HABIT_EMOJI_PRESETS, normalize_habit_emoji
from harrix_swiss_knife.integrations.bothub import BothubRequestState
from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons, make_emoji_push_button


class HabitEditDialog(QDialog):
    """Create or edit habit name, boolean flag, and emoji."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Add Habit",
        name: str = "",
        is_bool: bool = True,
        emoji: str = "",
        habit_id: int | None = None,
        app_config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the habit edit dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `title` (`str`): Window title. Defaults to `"Add Habit"`.
        - `name` (`str`): Initial habit name. Defaults to `""`.
        - `is_bool` (`bool`): Initial boolean habit flag. Defaults to `True`.
        - `emoji` (`str`): Initial emoji. Defaults to `""`.
        - `habit_id` (`int | None`): Habit ID used for emoji fallback. Defaults to `None`.
        - `app_config` (`dict[str, Any] | None`): App config for AI emoji suggestions.
          Defaults to `None` (load `config.json`).

        """
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle(title)
        self._habit_id = habit_id
        self._emoji = normalize_habit_emoji(emoji, habit_id=habit_id)
        self._app_config = app_config if app_config is not None else h.dev.config_load(get_config_path_str())
        self._bothub_state = BothubRequestState()
        self._ai_request_in_progress = False

        root = QVBoxLayout(self)
        form = QFormLayout()

        self._name_edit = QLineEdit(name)
        self._name_edit.setPlaceholderText("Habit name")
        self._name_edit.textChanged.connect(self._update_ai_emoji_button)
        form.addRow("Name:", self._name_edit)

        self._is_bool_checkbox = QCheckBox("Boolean (done / not done)")
        self._is_bool_checkbox.setChecked(is_bool)
        form.addRow("", self._is_bool_checkbox)

        emoji_row = QHBoxLayout()
        self._emoji_preview = QPushButton(self._emoji)
        self._emoji_preview.setFixedSize(44, 44)
        self._emoji_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self._emoji_preview.setStyleSheet("QPushButton { font-size: 22px; }")
        self._emoji_preview.setToolTip("Choose emoji")
        self._emoji_preview.clicked.connect(self._choose_emoji)
        choose_button = QPushButton("Choose…")
        choose_button.clicked.connect(self._choose_emoji)
        self._ai_emoji_button = make_emoji_push_button("", "🤖")
        self._ai_emoji_button.setToolTip("Suggest emoji with AI")
        self._ai_emoji_button.setFixedWidth(36)
        self._ai_emoji_button.clicked.connect(self._suggest_emoji_with_ai)
        emoji_row.addWidget(self._emoji_preview)
        emoji_row.addWidget(choose_button)
        emoji_row.addWidget(self._ai_emoji_button)
        emoji_row.addStretch(1)
        form.addRow("Emoji:", emoji_row)

        root.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        self._update_ai_emoji_button()

    def accept(self) -> None:
        """Validate required fields before accepting."""
        if not self._name_edit.text().strip():
            message_box.warning(self, "Validation Error", "Habit name cannot be empty")
            return
        super().accept()

    def habit_emoji(self) -> str:
        """Return the selected emoji."""
        return normalize_habit_emoji(self._emoji, habit_id=self._habit_id)

    def habit_is_bool(self) -> bool:
        """Return whether the habit is boolean."""
        return self._is_bool_checkbox.isChecked()

    def habit_name(self) -> str:
        """Return the trimmed habit name."""
        return self._name_edit.text().strip()

    def _apply_suggested_emoji(self, emoji: str) -> None:
        self._emoji = normalize_habit_emoji(emoji, habit_id=self._habit_id)
        self._emoji_preview.setText(self._emoji)

    def _choose_emoji(self) -> None:
        dialog = HabitEmojiPickerDialog(self, current_emoji=self._emoji)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._emoji = dialog.selected_emoji() or (HABIT_EMOJI_PRESETS[0] if HABIT_EMOJI_PRESETS else "✅")
        self._emoji_preview.setText(self._emoji)

    def _on_ai_emoji_finished(self) -> None:
        self._ai_request_in_progress = False
        self._update_ai_emoji_button()

    def _suggest_emoji_with_ai(self) -> None:
        if not self.habit_name() or self._ai_request_in_progress:
            return
        self._ai_request_in_progress = True
        self._update_ai_emoji_button()
        request_habit_emoji_suggestion(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            habit_name=self.habit_name(),
            suggest_button=self._ai_emoji_button,
            on_emoji=self._apply_suggested_emoji,
            on_finished=self._on_ai_emoji_finished,
        )

    def _update_ai_emoji_button(self) -> None:
        self._ai_emoji_button.setEnabled(bool(self._name_edit.text().strip()) and not self._ai_request_in_progress)
