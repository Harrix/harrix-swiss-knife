"""Text input dialog for food entries.

This module provides a dialog for entering food information as text,
which will be parsed and converted to food log records.
"""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


class TextInputDialog(QDialog):
    """Dialog for entering food information as text.

    This dialog provides a text area where users can enter food information
    in a simple text format, which will be parsed according to specific rules.

    Attributes:

    - `text_edit` (`QPlainTextEdit`): Text area for entering food information.
    - `accepted_text` (`str | None`): The text that was accepted by the user.

    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the text input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.

        """
        super().__init__(parent)
        self.accepted_text: str | None = None
        self._setup_ui()

    def get_text(self) -> str | None:
        """Get the entered text.

        Returns:

        - `str | None`: The entered text, or None if dialog was cancelled.

        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self.text_edit.toPlainText().strip()
        return None

    def _setup_ui(self) -> None:
        """Set up the user interface for the dialog."""
        self.setWindowTitle("Add Food as Text")
        self.setMinimumSize(600, 400)
        self.setModal(True)

        # Create main layout
        layout = QVBoxLayout(self)

        # Add description label
        description = QLabel(
            "Enter food information in text format. Each line represents one food item.\n"
            "Format examples:\n"
            "• 100 200 Apple (weight: 100g, calories per 100g: 200)\n"
            "• 150 Coffee (weight: 150g, calories from database)\n"
            "• Coffee 100 portion (100 calories per portion)\n"
            "• Apple 2025-01-15 (with specific date)\n"
            "• Water (default weight and calories from database)"
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Add text edit
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            "Enter your food items here...\nExample:\n100 200 Apple\n150 Coffee\nCoffee 100 portion\nWater 250"
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
