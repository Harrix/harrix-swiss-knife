"""Description delegate for description column in transactions table."""

from typing import cast

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt
from PySide6.QtWidgets import QLineEdit, QStyledItemDelegate, QWidget


class DescriptionDelegate(QStyledItemDelegate):
    """Delegate for description column in transactions table."""

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize DescriptionDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object for the delegate.

        """
        super().__init__(parent)

    def createEditor(self, parent: QObject, _option: object, _index: QModelIndex) -> QLineEdit:  # noqa: N802
        """Create a line edit editor for the description column.

        Args:

        - `parent` (`QObject`): Parent widget.
        - `_option` (`object`): Style option.
        - `_index` (`QModelIndex`): Model index.

        Returns:

        - `QLineEdit`: The created line edit editor.

        """
        editor = QLineEdit(cast("QWidget", parent))

        # Set white background for the editor
        editor.setStyleSheet("QLineEdit { background-color: white; }")

        return editor

    def setEditorData(self, editor: QLineEdit, index: QModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QLineEdit`): The editor widget.
        - `index` (`QModelIndex`): Model index.

        """
        current_value = index.data()
        if current_value:
            editor.setText(str(current_value))

    def setModelData(self, editor: QLineEdit, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QLineEdit`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex`): Model index.

        """
        text = editor.text()
        model.setData(index, text, Qt.ItemDataRole.DisplayRole)
