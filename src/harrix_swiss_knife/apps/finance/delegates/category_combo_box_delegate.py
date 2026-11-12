"""Category combo box delegate for category column in transactions table."""

from __future__ import annotations

from typing import cast

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, QPersistentModelIndex, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.common.delegates import ComboBoxDelegate
from harrix_swiss_knife.apps.common.ui_helpers import apply_white_editor_background
from harrix_swiss_knife.apps.finance.category_icon_display import category_lucide_icon

_CATEGORY_ENTRY_EMOJI_INDEX = 1
_CATEGORY_ENTRY_LUCIDE_INDEX = 2


class CategoryComboBoxDelegate(ComboBoxDelegate):
    """Delegate for category column in transactions table with dropdown list."""

    def __init__(
        self,
        parent: QObject | None = None,
        categories: list[tuple[str, str, str]] | list[tuple[str, str]] | list[str] | None = None,
    ) -> None:
        """Initialize CategoryComboBoxDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object.
        - `categories`: Display labels with optional `(label, emoji, lucide)`.

        """
        super().__init__(parent, items=[])
        self._category_emojis: list[str] = []
        self._category_lucides: list[str] = []
        self.categories = categories

    @property
    def categories(self) -> list[str]:
        """Category labels shown in the combo box."""
        return self.items

    @categories.setter
    def categories(self, value: list[tuple[str, str, str]] | list[tuple[str, str]] | list[str] | None) -> None:
        labels: list[str] = []
        emojis: list[str] = []
        lucides: list[str] = []
        for entry in value or []:
            if isinstance(entry, tuple):
                labels.append(str(entry[0]))
                emojis.append(str(entry[1] or "") if len(entry) > _CATEGORY_ENTRY_EMOJI_INDEX else "")
                lucides.append(
                    str(entry[_CATEGORY_ENTRY_LUCIDE_INDEX] or "") if len(entry) > _CATEGORY_ENTRY_LUCIDE_INDEX else ""
                )
            else:
                labels.append(str(entry))
                emojis.append("")
                lucides.append("")
        self.items = labels
        self._category_emojis = emojis
        self._category_lucides = lucides

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a combo box with Lucide icons for each category."""
        combo = QComboBox(parent)
        combo.setEditable(self.editable)
        apply_white_editor_background(combo, "QComboBox")
        for index, label in enumerate(self.items):
            emoji = self._category_emojis[index] if index < len(self._category_emojis) else ""
            lucide = self._category_lucides[index] if index < len(self._category_lucides) else ""
            icon = category_lucide_icon(emoji, lucide_name=lucide)
            if not icon.isNull():
                combo.addItem(icon, label)
            else:
                combo.addItem(label)
        return combo

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write the selected label and matching Lucide icon back to the model."""
        super().setModelData(editor, model, index)
        combo = cast("QComboBox", editor)
        selected = combo.currentText().strip() if self.strip_values else combo.currentText()
        emoji = ""
        lucide = ""
        try:
            item_index = self.items.index(selected)
        except ValueError:
            item_index = -1
        if 0 <= item_index < len(self._category_emojis):
            emoji = self._category_emojis[item_index]
        if 0 <= item_index < len(self._category_lucides):
            lucide = self._category_lucides[item_index]
        icon = category_lucide_icon(emoji, lucide_name=lucide) if (emoji or lucide) else QIcon()
        model.setData(index, icon, Qt.ItemDataRole.DecorationRole)
