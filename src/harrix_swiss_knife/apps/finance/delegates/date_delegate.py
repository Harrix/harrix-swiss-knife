"""Date delegate for date column in transactions table."""

from datetime import date as date_class

from PySide6.QtCore import QAbstractItemModel, QDate, QModelIndex, QObject, Qt
from PySide6.QtWidgets import QDateEdit, QStyledItemDelegate


class DateDelegate(QStyledItemDelegate):
    """Delegate for date column in transactions table."""

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize DateDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object for the delegate.

        """
        super().__init__(parent)

    def createEditor(self, parent: QObject, _option, _index: QModelIndex) -> QDateEdit:  # noqa: N802, ANN001
        """Create a date editor for the date column.

        Args:

        - `parent` (`QObject`): Parent widget.
        - `_option`: Style option.
        - `_index` (`QModelIndex`): Model index.

        Returns:

        - `QDateEdit`: The created date editor.

        """
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDate(QDate.currentDate())
        editor.setDisplayFormat("yyyy-MM-dd")

        # Set white background for the editor
        editor.setStyleSheet("QDateEdit { background-color: white; }")

        return editor

    def setEditorData(self, editor: QDateEdit, index: QModelIndex) -> None:  # noqa: N802
        """Set the current value in the editor.

        Args:

        - `editor` (`QDateEdit`): The editor widget.
        - `index` (`QModelIndex`): Model index.

        """
        current_value = index.data()
        if current_value:
            try:
                # Parse date string to date object
                date_obj = date_class.fromisoformat(str(current_value))
                editor.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except (ValueError, TypeError):
                editor.setDate(QDate.currentDate())

    def setModelData(self, editor: QDateEdit, model: QAbstractItemModel, index: QModelIndex) -> None:  # noqa: N802
        """Set the data from the editor back to the model.

        Args:

        - `editor` (`QDateEdit`): The editor widget.
        - `model` (`QAbstractItemModel`): The data model.
        - `index` (`QModelIndex`): Model index.

        """
        selected_date: QDate = editor.date()
        date_string: str = selected_date.toString("yyyy-MM-dd")
        model.setData(index, date_string, Qt.ItemDataRole.DisplayRole)
