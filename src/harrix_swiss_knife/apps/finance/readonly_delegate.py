"""Read-only delegate for displaying non-editable data in tables."""

from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget


class ReadOnlyDelegate(QStyledItemDelegate):
    """Delegate for read-only columns that display data but don't allow editing.

    This delegate provides display formatting for read-only columns while
    preventing any editing functionality.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the read-only delegate.

        Args:

        - `parent` (`QWidget | None`): The parent widget. Defaults to `None`.

        """
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> None:  # noqa: N802
        """Prevent creation of any editor for read-only columns.

        Args:

        - `parent` (`QWidget`): The parent widget for the editor.
        - `option` (`QStyleOptionViewItem`): The style options for the item.
        - `index` (`QModelIndex`): The model index of the item being edited.

        Returns:

        - `None`: Always returns None to prevent editing.

        """
        # Return None to prevent any editing
        return

    def editorEvent(self, event, model, option, index):  # noqa: N802
        """Prevent editor events for read-only columns.

        Args:

        - `event`: The event being processed.
        - `model`: The model containing the data.
        - `option`: The style options for the item.
        - `index`: The model index of the item.

        Returns:

        - `bool`: Always returns False to prevent editing.

        """
        # Return False to prevent any editor events
        return False
