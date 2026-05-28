"""Tag delegate for tag column in transactions table."""

from PySide6.QtCore import QObject

from harrix_swiss_knife.apps.common.delegates import ComboBoxDelegate


class TagDelegate(ComboBoxDelegate):
    """Delegate for tag column with editable combo and clearable empty option."""

    def __init__(self, parent: QObject | None = None, tags: list[str] | None = None) -> None:
        """Initialize the tag delegate."""
        super().__init__(
            parent,
            items=tags,
            editable=True,
            leading_empty_item=True,
            strip_values=True,
            write_empty_value=True,
        )

    @property
    def tags(self) -> list[str]:
        """Tag names shown in the combo box."""
        return self.items

    @tags.setter
    def tags(self, value: list[str] | None) -> None:
        self.items = list(value or [])
