"""Text input dialog for finance entries.

This module provides a dialog for entering purchase information as text,
which will be parsed and converted to transaction records. The underlying
implementation is the shared `apps.common.dialogs.TextInputDialog`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.dialogs import TextInputDialog as _BaseTextInputDialog

if TYPE_CHECKING:
    from PySide6.QtCore import QDate
    from PySide6.QtWidgets import QWidget


_DESCRIPTION = (
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

_PLACEHOLDER = (
    "Enter your purchases here...\n"
    "Example:\n"
    "Sugar-free Cola 'From Store'\tFood\t99 ₽\n"
    "Milk Cocktail 'Wonder'\tFood\t65 ₽"
)


class TextInputDialog(_BaseTextInputDialog):
    """Dialog for entering purchase information as text."""

    def __init__(self, parent: QWidget | None = None, default_date: QDate | None = None) -> None:
        """Initialize the finance text input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `default_date` (`QDate | None`): Default date for purchases. Defaults to `None` (current date).

        """
        super().__init__(
            parent,
            title="Add Purchases as Text",
            description=_DESCRIPTION,
            placeholder=_PLACEHOLDER,
            show_date=True,
            default_date=default_date,
            focus_text_on_show=True,
        )
