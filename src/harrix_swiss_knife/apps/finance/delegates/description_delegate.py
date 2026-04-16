"""Description delegate for description column in transactions table."""

from typing import cast

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QLineEdit, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.common.ui_helpers import apply_white_editor_background


class DescriptionDelegate(QStyledItemDelegate):
    """Delegate for description column in transactions table."""

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize DescriptionDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object for the delegate.

        """
        super().__init__(parent)

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a line edit editor for the description column.

        Args:

        - `parent` (`QWidget`): Parent widget.
        - `_option` (`QStyleOptionViewItem`): Style option.
        - `_index` (`QModelIndex | QPersistentModelIndex`): Model index.

        Returns:

        - `QWidget`: The created line edit editor.

        """
        editor = QLineEdit(parent)

        apply_white_editor_background(editor, "QLineEdit")

        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        line_edit = cast("QLineEdit", editor)
        current_value = index.data()
        if current_value:
            line_edit.setText(str(current_value))

    def setModelData(  # noqa: N802
        self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QWidget`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex | QPersistentModelIndex`): Model index.

        """
        line_edit = cast("QLineEdit", editor)
        text = line_edit.text()
        model.setData(index, text, Qt.ItemDataRole.DisplayRole)
