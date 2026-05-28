"""Currency combo box delegate for currency column in transactions table."""

from PySide6.QtCore import QObject

from harrix_swiss_knife.apps.common.delegates import ComboBoxDelegate


class CurrencyComboBoxDelegate(ComboBoxDelegate):
    """Delegate for currency column in transactions table with dropdown list."""

    def __init__(self, parent: QObject | None = None, currencies: list[str] | None = None) -> None:
        """Initialize CurrencyComboBoxDelegate.

        Args:

        - `parent` (`QObject | None`): Parent widget.
        - `currencies` (`list[str] | None`): List of currency codes.

        """
        super().__init__(parent, items=currencies)

    @property
    def currencies(self) -> list[str]:
        """Currency codes shown in the combo box."""
        return self.items

    @currencies.setter
    def currencies(self, value: list[str] | None) -> None:
        self.items = list(value or [])
