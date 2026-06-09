"""Purchase input dialog for finance entries.

This module provides a dialog for reviewing and editing purchase information
in a table before records are saved to the database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.finance.purchase_table_dialog import PurchaseTableDialog

if TYPE_CHECKING:
    from PySide6.QtCore import QDate
    from PySide6.QtWidgets import QWidget

    from harrix_swiss_knife.apps.finance.text_parser import ParsedPurchaseItem


_DESCRIPTION = (
    "Review and edit purchases before saving. Each row is one purchase.\n"
    "Columns: Name, Category, Amount (for example: 99 ₽).\n"
    "Use Add row / Delete row to manage entries. Date can be selected above."
)

PURCHASE_TEXT_PLACEHOLDER = (
    "Enter your purchases here...\n"
    "Example:\n"
    "Sugar-free Cola 'From Store'\tFood\t99 ₽\n"
    "Milk Cocktail 'Wonder'\tFood\t65 ₽"
)


class TextInputDialog(PurchaseTableDialog):
    """Dialog for entering purchase information in an editable table."""

    def __init__(
        self,
        parent: QWidget | None = None,
        default_date: QDate | None = None,
        *,
        initial_text: str | None = None,
        focus_text_on_show: bool = True,
        currency_symbol: str = "",
    ) -> None:
        """Initialize the finance purchase input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `default_date` (`QDate | None`): Default date for purchases. Defaults to `None` (current date).
        - `initial_text` (`str | None`): Pre-filled purchase lines from AI. Defaults to `None`.
        - `focus_text_on_show` (`bool`): Ignored; kept for API compatibility.
        - `currency_symbol` (`str`): Default currency symbol for the total label.

        """
        super().__init__(
            parent,
            title="Add Purchases as Text",
            description=_DESCRIPTION,
            default_date=default_date,
            initial_text=initial_text,
            currency_symbol=currency_symbol,
        )
        _ = focus_text_on_show

    def get_items(self) -> list[ParsedPurchaseItem]:
        """Return validated purchase items accepted by the user."""
        return super().get_items()
