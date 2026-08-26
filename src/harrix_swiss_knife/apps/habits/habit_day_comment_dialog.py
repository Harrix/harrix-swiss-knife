"""Dialog for viewing and editing one habit-day comment."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.qt_emoji_icon import DELETE_BUTTON_EMOJI, apply_emoji_dialog_buttons, make_emoji_push_button


class HabitDayCommentDialog(QDialog):
    """Edit the Markdown comment attached to one habit on one date."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        habit_name: str,
        date_str: str,
        text: str = "",
    ) -> None:
        """Initialize the comment dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `habit_name` (`str`): Habit title shown in the heading.
        - `date_str` (`str`): Day in `YYYY-MM-DD` format.
        - `text` (`str`): Current comment. Defaults to `""`.

        """
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle(f"Comment — {habit_name} — {date_str}")
        self.setMinimumWidth(420)
        self.resize(480, 320)
        self._deleted = False

        root = QVBoxLayout(self)
        heading = QLabel(f"{habit_name} · {date_str}")
        heading.setStyleSheet("color: #111827; font-size: 14px; font-weight: 700;")
        root.addWidget(heading)

        self._edit = QPlainTextEdit(text)
        self._edit.setPlaceholderText("Write a comment for this day…")
        root.addWidget(self._edit, 1)

        buttons = QHBoxLayout()
        self._delete_button = make_emoji_push_button("Delete", DELETE_BUTTON_EMOJI)
        self._delete_button.setEnabled(bool(text.strip()))
        self._delete_button.clicked.connect(self._on_delete)
        buttons.addWidget(self._delete_button)
        buttons.addStretch(1)

        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(box)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        buttons.addWidget(box)
        root.addLayout(buttons)

        self._edit.setFocus()

    def comment_text(self) -> str:
        """Return the edited comment, empty when deleted or cleared."""
        if self._deleted:
            return ""
        return self._edit.toPlainText().strip()

    def _on_delete(self) -> None:
        reply = message_box.question(
            self,
            "Delete comment",
            "Delete this day's comment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._deleted = True
            self.accept()
