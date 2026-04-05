"""Category combo box delegate for category column in transactions table."""

from typing import cast

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QStyleOptionViewItem, QWidget


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

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a combo box editor for the category column.

        Args:

        - `parent` (`QWidget`): Parent widget.
        - `_option` (`QStyleOptionViewItem`): Style option.
        - `_index` (`QModelIndex | QPersistentModelIndex`): Model index.

        Returns:

        - `QWidget`: The created combo box editor.

        """
        combo = QComboBox(parent)
        combo.setEditable(False)

        # Set white background for the editor
        combo.setStyleSheet("QComboBox { background-color: white; }")

        # Add categories to combo box
        for category in self.categories:
            combo.addItem(category)

        return combo

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        combo = cast("QComboBox", editor)
        current_value = index.data()
        if current_value:
            # Find the exact value in the combo box
            index_in_combo = combo.findText(current_value)
            if index_in_combo >= 0:
                combo.setCurrentIndex(index_in_combo)

    def setModelData(  # noqa: N802
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        combo = cast("QComboBox", editor)
        selected_text = combo.currentText()
        if selected_text:
            # Check if this is an income category and add suffix if needed
            # This logic should match the logic used in _save_transaction_data
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
