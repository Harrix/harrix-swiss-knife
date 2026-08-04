"""Food input dialog for reviewing items before saving.

This module provides a dialog for reviewing and editing food information
in a table (default) or as text before records are saved to the database.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.food.food_table_dialog import FoodTableDialog

if TYPE_CHECKING:
    from PySide6.QtCore import QDate
    from PySide6.QtWidgets import QWidget

    from harrix_swiss_knife.apps.food.text_parser import ParsedFoodItem


_DESCRIPTION = (
    "Review and edit food items before saving. Each row is one food log entry.\n"
    "Table mode: columns Name, Weight, Calories, Mode, Drink.\n"
    "  Mode: weight (calories per 100g) or portion (calories per serving).\n"
    "  Drink: yes or no.\n"
    "Text mode: one item per line. Prefer TSV from AI "
    "(Name<Tab>Weight<Tab>Calories<Tab>Mode<Tab>Drink).\n"
    "Legacy text formats are still accepted in Text mode.\n"
    "Use Add row / Delete row in table mode. Date can be selected above."
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


class TextInputDialog(FoodTableDialog):
    """Dialog for entering food information in an editable table."""

    def __init__(
        self,
        parent: QWidget | None = None,
        default_date: QDate | None = None,
        *,
        initial_text: str | None = None,
        focus_text_on_show: bool = True,
        db_manager: Any | None = None,
    ) -> None:
        """Initialize the food input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `default_date` (`QDate | None`): Default date for food log entries.
        - `initial_text` (`str | None`): Pre-filled lines from AI. Defaults to `None`.
        - `focus_text_on_show` (`bool`): Ignored; kept for API compatibility.
        - `db_manager` (`Any | None`): Database manager for legacy text lookup.

        """
        super().__init__(
            parent,
            title="Add Food as Text",
            description=_DESCRIPTION,
            default_date=default_date,
            initial_text=initial_text,
            text_placeholder=FOOD_TEXT_PLACEHOLDER,
            db_manager=db_manager,
        )
        _ = focus_text_on_show

    def get_items(self) -> list[ParsedFoodItem]:
        """Return validated food items accepted by the user."""
        return super().get_items()
