"""Delegate for Is Drink column in food log table."""

from __future__ import annotations

from PySide6.QtCore import QAbstractItemModel, QLocale, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QCheckBox, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.common.ui_helpers import apply_white_editor_background

DRINK_EMOJI = "🥛"
_TRUTHY_IS_DRINK = frozenset({"1", "yes", "true", "да"})


def parse_is_drink_cell(value: object) -> bool:
    """Return whether a model cell value represents a drink.

    Args:

    - `value` (`object`): Raw cell value from the model.

    Returns:

    - `bool`: True if the value indicates a drink.

    """
    if value is None:
        return False
    text = str(value).strip().lower()
    if not text:
        return False
    return text in _TRUTHY_IS_DRINK or text == DRINK_EMOJI


def is_drink_to_model(*, checked: bool) -> str:
    """Convert checkbox state to food log model storage.

    Args:

    - `checked` (`bool`): Whether the drink checkbox is checked.

    Returns:

    - `str`: `"1"` when checked, empty string otherwise.

    """
    return "1" if checked else ""


class IsDrinkDelegate(QStyledItemDelegate):
    """Show drink emoji in view mode; edit with a checkbox storing 1/empty."""

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a checkbox editor for the Is Drink column."""
        editor = QCheckBox(parent)
        editor.stateChanged.connect(lambda: self.commitData.emit(editor))
        apply_white_editor_background(editor, "QCheckBox")
        return editor

    def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Map stored model value to emoji display text.

        Args:

        - `value` (`object`): Raw model value.
        - `_locale` (`QLocale | QLocale.Language`): Locale (unused).

        Returns:

        - `str`: Drink emoji or empty string.

        """
        return DRINK_EMOJI if parse_is_drink_cell(value) else ""

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Load model value into the checkbox editor."""
        checkbox = editor if isinstance(editor, QCheckBox) else None
        if checkbox is None:
            return
        checkbox.setChecked(parse_is_drink_cell(index.data(Qt.ItemDataRole.DisplayRole)))

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write checkbox state back to the model as 1 or empty."""
        checkbox = editor if isinstance(editor, QCheckBox) else None
        if checkbox is None:
            return
        model.setData(index, is_drink_to_model(checked=checkbox.isChecked()), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Position the checkbox editor inside the cell."""
        editor.setGeometry(option.rect)
