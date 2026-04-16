"""Tag delegate for tag column in transactions table."""

from typing import cast

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.common.ui_helpers import apply_white_editor_background


class TagDelegate(QStyledItemDelegate):
    """Delegate for tag column in transactions table."""

    def __init__(self, parent: QObject | None = None, tags: list[str] | None = None) -> None:
        """Initialize the tag delegate."""
        super().__init__(parent)
        self.tags = tags or []

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a combo box editor for the tag column.

        Args:

        - `parent` (`QWidget`): Parent widget.
        - `_` (`QStyleOptionViewItem`): Style option (unused).
        - `_index` (`QModelIndex | QPersistentModelIndex`): Model index (unused).

        Returns:

        - `QWidget`: The created combo box editor.

        """
        combo: QComboBox = QComboBox(parent)
        combo.setEditable(True)

        apply_white_editor_background(combo, "QComboBox")

        # Add tags to combo box
        for tag in self.tags:
            combo.addItem(tag)

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
            index_in_combo: int = combo.findText(current_value)
            if index_in_combo >= 0:
                combo.setCurrentIndex(index_in_combo)
            else:
                # If not found, set as current text
                combo.setCurrentText(current_value)

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
        selected_text: str = combo.currentText()
        if selected_text:
            model.setData(index, selected_text, Qt.ItemDataRole.DisplayRole)
