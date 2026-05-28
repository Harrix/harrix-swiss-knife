"""Category combo box delegate for category column in transactions table."""

from PySide6.QtCore import QObject

from harrix_swiss_knife.apps.common.delegates import ComboBoxDelegate


class CategoryComboBoxDelegate(ComboBoxDelegate):
    """Delegate for category column in transactions table with dropdown list."""

    def __init__(self, parent: QObject | None = None, categories: list[str] | None = None) -> None:
        """Initialize CategoryComboBoxDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object.
        - `categories` (`list[str] | None`): List of category names for the combo box.

        """
        super().__init__(parent, items=categories)

    @property
    def categories(self) -> list[str]:
        """Category names shown in the combo box."""
        return self.items

    @categories.setter
    def categories(self, value: list[str] | None) -> None:
        self.items = list(value or [])
