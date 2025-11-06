"""Currency combo box delegate for currency column in transactions table."""

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt
from PySide6.QtWidgets import QComboBox, QStyledItemDelegate


class CurrencyComboBoxDelegate(QStyledItemDelegate):
    """Delegate for currency column in transactions table with dropdown list."""

    def __init__(self, parent: QObject, currencies: list[str] | None = None) -> None:
        """Initialize CurrencyComboBoxDelegate.

        Args:

        - `parent` (`QObject`): Parent widget.
        - `currencies` (`list[str] | None`): List of currency codes. Defaults to empty list if None.

        """
        super().__init__(parent)
        self.currencies = currencies or []

    def createEditor(self, parent: QObject, _option, _index: QModelIndex) -> QComboBox:  # noqa: N802, ANN001
        """Create a combo box editor for the currency column.

        Args:

        - `parent` (`QObject`): Parent widget.
        - `_option`: Style option.
        - `_index` (`QModelIndex`): Model index.

        Returns:

        - `QComboBox`: The created combo box editor.

        """
        combo = QComboBox(parent)
        combo.setEditable(False)

        # Set white background for the editor
        combo.setStyleSheet("QComboBox { background-color: white; }")

        # Add currencies to combo box
        for currency in self.currencies:
            combo.addItem(currency)

        return combo

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QComboBox`): The editor widget.
        - `index` (`QModelIndex`): Model index.

        """
        current_value = index.data()
        if current_value:
            # Find the exact value in the combo box
            index_in_combo = editor.findText(current_value)
            if index_in_combo >= 0:
                editor.setCurrentIndex(index_in_combo)

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QComboBox`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex`): Model index.

        """
        selected_text = editor.currentText()
        if selected_text:
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)

