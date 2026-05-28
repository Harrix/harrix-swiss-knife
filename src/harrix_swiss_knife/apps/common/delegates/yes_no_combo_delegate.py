"""Yes/No combo box delegate for boolean columns stored as display text."""

from typing import cast

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.common.ui_helpers import apply_white_editor_background

_YES_NO_ITEMS = ("Yes", "No")


class YesNoComboDelegate(QStyledItemDelegate):
    """Delegate that edits values using a non-editable Yes/No combo box."""

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize YesNoComboDelegate.

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
        """Create a Yes/No combo box editor."""
        combo = QComboBox(parent)
        combo.addItems(list(_YES_NO_ITEMS))
        combo.setEditable(False)

        apply_white_editor_background(combo, "QComboBox")
        return combo

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Set the current Yes/No value in the editor."""
        combo = cast("QComboBox", editor)
        value = index.data()
        text = str(value) if value is not None else ""
        if text not in _YES_NO_ITEMS:
            text = "No"
        combo.setCurrentText(text)

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write Yes/No selection back to the model."""
        combo = cast("QComboBox", editor)
        model.setData(index, combo.currentText(), Qt.ItemDataRole.DisplayRole)

    def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Size the editor to the cell rectangle."""
        editor.setGeometry(option.rect)
