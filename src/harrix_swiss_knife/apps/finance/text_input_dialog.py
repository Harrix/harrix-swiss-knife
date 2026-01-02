"""Text input dialog for finance entries.

This module provides a dialog for entering purchase information as text,
which will be parsed and converted to transaction records.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit, QDialog, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from PySide6.QtGui import QShowEvent


class TextInputDialog(QDialog):
    """Dialog for entering purchase information as text.

    This dialog provides a text area where users can enter purchase information
    in a simple text format, which will be parsed according to specific rules.

    Attributes:

    - `text_edit` (`QPlainTextEdit`): Text area for entering purchase information.
    - `date_edit` (`QDateEdit`): Date picker for purchase date.
    - `accepted_text` (`str | None`): The text that was accepted by the user.

    """

    text_edit: QPlainTextEdit
    date_edit: QDateEdit
    accepted_text: str | None

    def __init__(self, parent: QWidget | None = None, default_date: QDate | None = None) -> None:
        """Initialize the text input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `default_date` (`QDate | None`): Default date for purchases. Defaults to `None` (current date).

        """
        super().__init__(parent)
        self.accepted_text: str | None = None
        self._default_date: QDate | None = default_date
        self._setup_ui()

    def get_date(self) -> str | None:
        """Get the selected date.

        Returns:

        - `str | None`: The selected date in yyyy-MM-dd format, or None if dialog was cancelled.

        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self.date_edit.date().toString("yyyy-MM-dd")
        return None

    def get_text(self) -> str | None:
        """Get the entered text.

        Returns:

        - `str | None`: The entered text, or None if dialog was cancelled.

        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self.text_edit.toPlainText().strip()
        return None

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Override showEvent to set focus on text edit when dialog is shown."""
        super().showEvent(event)
        self.text_edit.setFocus()

    def _setup_ui(self) -> None:
        """Set up the user interface for the dialog."""
        self.setWindowTitle("Add Purchases as Text")
        self.setMinimumSize(600, 400)
        self.setModal(True)

        # Create main layout
        layout = QVBoxLayout(self)

        # Add description label
        description = QLabel(
            "Enter purchase information in text format. Each line represents one purchase.\n"
            "Format: Name\tCategory\tAmount\n"
            "Format examples:\n"
            "• Sugar-free Cola 'From Store'\tFood\t99 ₽\n"
            "• Milk Cocktail 'Wonder' coconut-cream 2%\tFood\t65 ₽\n"
            "• Olivier salad with chicken 'From Store'\tFood\t285 ₽\n"
            "• Cat litter filler 'Barsik'\tPet Care\t179 ₽\n"
            "• Universal wet wipes\tHousehold Goods\t29 ₽\n\n"
            "Note: Use Tab character to separate columns. Date can be selected in the date field above."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Add date picker
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_layout.addWidget(date_label)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        if self._default_date:
            self.date_edit.setDate(self._default_date)
        else:
            self.date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Add text edit
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            "Enter your purchases here...\n"
            "Example:\n"
            "Sugar-free Cola 'From Store'\tFood\t99 ₽\n"
            "Milk Cocktail 'Wonder'\tFood\t65 ₽"
        )
        layout.addWidget(self.text_edit)

        # Add buttons
        button_layout = QHBoxLayout()

        # Add spacer to push buttons to the right
        button_layout.addStretch()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # OK button
        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)
