"""Delegate for Is Drink column in food log table."""

from __future__ import annotations

from PySide6.QtCore import QAbstractItemModel, QLocale, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QCheckBox, QStyledItemDelegate, QStyleOptionViewItem, QWidget

DRINK_EMOJI = "🥤"
_TRUTHY_IS_DRINK = frozenset({"1", "yes", "true", "да"})


class IsDrinkDelegate(QStyledItemDelegate):
    """Show drink emoji in view mode; edit with a checkbox storing 1/empty."""

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a checkbox editor for the Is Drink column."""
        editor = QCheckBox(parent)
        editor.setText("")
        editor.stateChanged.connect(lambda: self.commitData.emit(editor))
        self._apply_editor_row_background(editor, option)
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
        checkbox = editor if isinstance(editor, QCheckBox) else None
        if checkbox is None:
            editor.setGeometry(option.rect)
            return
        size = checkbox.sizeHint()
        x = option.rect.x() + (option.rect.width() - size.width()) // 2
        y = option.rect.y() + (option.rect.height() - size.height()) // 2
        editor.setGeometry(x, y, size.width(), size.height())

    @staticmethod
    def _apply_editor_row_background(editor: QCheckBox, option: QStyleOptionViewItem) -> None:
        """Match the editor background to the table row without overriding native checkbox style."""
        brush = option.backgroundBrush
        if brush.style() != Qt.BrushStyle.NoBrush and brush.color().isValid():
            bg = brush.color()
        else:
            bg = QColor(255, 255, 255)
        palette = editor.palette()
        palette.setColor(QPalette.ColorRole.Window, bg)
        palette.setColor(QPalette.ColorRole.Base, bg)
        editor.setPalette(palette)
        editor.setAutoFillBackground(True)


def is_drink_to_model(*, checked: bool) -> str:
    """Convert checkbox state to food log model storage.

    Args:

    - `checked` (`bool`): Whether the drink checkbox is checked.

    Returns:

    - `str`: `"1"` when checked, empty string otherwise.

    """
    return "1" if checked else ""


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
