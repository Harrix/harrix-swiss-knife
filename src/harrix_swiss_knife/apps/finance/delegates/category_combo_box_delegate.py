"""Category combo box delegate for category column in transactions table."""

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt
from PySide6.QtWidgets import QComboBox, QStyledItemDelegate


class CategoryComboBoxDelegate(QStyledItemDelegate):
    """Delegate for category column in transactions table with dropdown list."""

    def __init__(self, parent: QObject | None = None, categories: list[str] | None = None) -> None:
        """Initialize CategoryComboBoxDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object.
        - `categories` (`list[str] | None`): List of category names for the combo box.

        """
        super().__init__(parent)
        self.categories = categories or []

    def createEditor(self, parent: QObject, _option: object, _index: QModelIndex) -> QComboBox:  # noqa: N802
        """Create a combo box editor for the category column.

        Args:

        - `parent` (`QObject`): Parent widget.
        - `_option` (`object`): Style option.
        - `_index` (`QModelIndex`): Model index.

        Returns:

        - `QComboBox`: The created combo box editor.

        """
        combo = QComboBox(parent)
        combo.setEditable(False)

        # Set white background for the editor
        combo.setStyleSheet("QComboBox { background-color: white; }")

        # Add categories to combo box
        for category in self.categories:
            combo.addItem(category)

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
            # Check if this is an income category and add suffix if needed
            # This logic should match the logic used in _save_transaction_data
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)

