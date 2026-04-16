"""Text input dialog for food entries.

This module provides a dialog for entering food information as text,
which will be parsed and converted to food log records. The underlying
implementation is the shared `apps.common.dialogs.TextInputDialog`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.dialogs import TextInputDialog as _BaseTextInputDialog

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


_DESCRIPTION = (
    "Enter food information in text format. Each line represents one food item.\n"
    "Format examples:\n"
    "• 100 200 Apple (weight: 100g, calories per 100g: 200)\n"
    "• 150 Coffee (weight: 150g, calories from database)\n"
    "• Coffee 100 portion (100 calories per portion)\n"
    "• Apple 2025-01-15 (with specific date)\n"
    "• Water (default weight and calories from database)"
)

_PLACEHOLDER = "Enter your food items here...\nExample:\n100 200 Apple\n150 Coffee\nCoffee 100 portion\nWater 250"


class TextInputDialog(_BaseTextInputDialog):
    """Dialog for entering food information as text."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the food text input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.

        """
        super().__init__(
            parent,
            title="Add Food as Text",
            description=_DESCRIPTION,
            placeholder=_PLACEHOLDER,
        )
