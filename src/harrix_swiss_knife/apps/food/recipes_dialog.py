"""Modal dialog hosting the Recipes editor (list + ingredients)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QWidget

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.food.recipes_widget import RecipesWidget
from harrix_swiss_knife.qt_lucide_icon import CANCEL_BUTTON_ICON, make_lucide_push_button

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.food.database_manager import DatabaseManager


class RecipesDialog(QDialog):
    """Show and edit recipes with the same UI formerly on the Recipes tab."""

    def __init__(
        self,
        parent: QWidget | None,
        db_manager: DatabaseManager,
        *,
        select_recipe_id: int | None = None,
    ) -> None:
        """Build the dialog, attach `db_manager`, and optionally select a recipe."""
        super().__init__(parent)
        self.setWindowTitle("Recipes")
        qt_modality.set_owner_window_modal(self)
        self.resize(1200, 720)

        self._widget = RecipesWidget(self)
        self._widget.set_database_manager(db_manager)
        if select_recipe_id is not None:
            self._widget.select_recipe_by_id(select_recipe_id)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self._widget, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close_button = make_lucide_push_button("Close", CANCEL_BUTTON_ICON)
        close_button.clicked.connect(self.accept)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    @property
    def recipes_widget(self) -> RecipesWidget:
        """Embedded recipes editor."""
        return self._widget
