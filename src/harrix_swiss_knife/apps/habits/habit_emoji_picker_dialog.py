"""Dialog for choosing a habit emoji from presets or custom input."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.habits.habit_emojis import HABIT_EMOJI_PRESETS, normalize_habit_emoji
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons


class HabitEmojiPickerDialog(QDialog):
    """Pick a habit emoji from a preset grid or paste a custom emoji."""

    def __init__(self, parent: QWidget | None = None, *, current_emoji: str = "") -> None:
        """Initialize the emoji picker dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `current_emoji` (`str`): Preselected emoji. Defaults to `""`.

        """
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle("Choose emoji")
        self.resize(420, 360)
        self._selected = normalize_habit_emoji(current_emoji)

        root = QVBoxLayout(self)
        root.setSpacing(10)

        preview_row = QHBoxLayout()
        preview_label = QLabel("Selected:")
        self._preview = QLabel(self._selected)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setFixedSize(48, 48)
        self._preview.setStyleSheet(
            "QLabel { font-size: 28px; border: 1px solid #D1D5DB; border-radius: 8px; background: #F9FAFB; }"
        )
        preview_row.addWidget(preview_label)
        preview_row.addWidget(self._preview)
        preview_row.addStretch(1)
        root.addLayout(preview_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setSpacing(6)
        columns = 8
        for index, emoji in enumerate(HABIT_EMOJI_PRESETS):
            button = QPushButton(emoji)
            button.setFixedSize(40, 40)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(
                """
                QPushButton {
                    font-size: 20px;
                    border: 1px solid #E5E7EB;
                    border-radius: 8px;
                    background: #FFFFFF;
                }
                QPushButton:hover { background: #EFF6FF; border-color: #93C5FD; }
                """
            )
            button.clicked.connect(lambda _checked=False, value=emoji: self._select_emoji(value))
            grid.addWidget(button, index // columns, index % columns)
        scroll.setWidget(grid_host)
        root.addWidget(scroll, 1)

        custom_row = QHBoxLayout()
        custom_row.addWidget(QLabel("Or paste emoji:"))
        self._custom_edit = QLineEdit(self._selected)
        self._custom_edit.setMaxLength(16)
        self._custom_edit.setPlaceholderText("Emoji")
        self._custom_edit.textChanged.connect(self._on_custom_changed)
        custom_row.addWidget(self._custom_edit, 1)
        root.addLayout(custom_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def selected_emoji(self) -> str:
        """Return the chosen emoji."""
        return normalize_habit_emoji(self._selected)

    def _on_custom_changed(self, text: str) -> None:
        value = text.strip()
        if value:
            self._selected = value
            self._preview.setText(value)

    def _select_emoji(self, emoji: str) -> None:
        self._selected = emoji
        self._preview.setText(emoji)
        self._custom_edit.blockSignals(True)  # noqa: FBT003
        self._custom_edit.setText(emoji)
        self._custom_edit.blockSignals(False)  # noqa: FBT003
