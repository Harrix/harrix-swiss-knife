"""Text input dialog for food entries.

This module provides a dialog for entering food information as text,
which will be parsed and converted to food log records. The underlying
implementation is the shared `apps.common.dialogs.TextInputDialog`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.dialogs import TextInputDialog as _BaseTextInputDialog

if TYPE_CHECKING:
    from PySide6.QtCore import QDate
    from PySide6.QtWidgets import QWidget


_DESCRIPTION = (
    "Enter food information in text format. Each line represents one food item.\n"
    "TSV format (from AI): Name\tWeight\tCalories\tMode\tDrink\n"
    "  Mode: weight (calories per 100g) or portion (calories per serving)\n"
    "  Drink: yes or no\n"
    "Legacy format examples:\n"
    "• 100 200 Apple (weight: 100g, calories per 100g: 200)\n"
    "• 150 Coffee (weight: 150g, calories from database)\n"
    "• Coffee 100 portion (100 calories per portion)\n"
    "• Apple 2025-01-15 (with specific date in line)\n"
    "• Water (default weight and calories from database)\n\n"
    "Note: Use Tab character for TSV columns. Date can be selected in the date field above."
)

FOOD_TEXT_PLACEHOLDER = (
    "Enter your food items here...\n"
    "TSV example:\n"
    "Oatmeal\t150\t350\tweight\tno\n"
    "Coffee\t250\t85\tportion\tyes\n\n"
    "Legacy example:\n"
    "100 200 Apple\n"
    "150 Coffee\n"
    "Coffee 100 portion"
)


class TextInputDialog(_BaseTextInputDialog):
    """Dialog for entering food information as text."""

    def __init__(
        self,
        parent: QWidget | None = None,
        default_date: QDate | None = None,
        *,
        initial_text: str | None = None,
        focus_text_on_show: bool = True,
    ) -> None:
        """Initialize the food text input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `default_date` (`QDate | None`): Default date for food log entries.
        - `initial_text` (`str | None`): Pre-filled text. Defaults to `None`.
        - `focus_text_on_show` (`bool`): Focus text area on show. Defaults to `True`.

        """
        super().__init__(
            parent,
            title="Add Food as Text",
            description=_DESCRIPTION,
            placeholder=FOOD_TEXT_PLACEHOLDER,
            show_date=True,
            default_date=default_date,
            initial_text=initial_text,
            focus_text_on_show=focus_text_on_show,
        )
