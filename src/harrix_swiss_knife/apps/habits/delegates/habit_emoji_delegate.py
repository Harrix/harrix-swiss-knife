"""Table delegate that opens the habit emoji picker."""

from __future__ import annotations

from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QObject, QPersistentModelIndex, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QDialog, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.habits.habit_emoji_picker_dialog import HabitEmojiPickerDialog
from harrix_swiss_knife.apps.habits.habit_emojis import normalize_habit_emoji


class HabitEmojiDelegate(QStyledItemDelegate):
    """Delegate that edits emoji values through `HabitEmojiPickerDialog`."""

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize HabitEmojiDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object for the delegate.

        """
        super().__init__(parent)

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Open the picker on left-click or double-click."""
        if event.type() not in {QEvent.Type.MouseButtonDblClick, QEvent.Type.MouseButtonRelease}:
            return super().editorEvent(event, model, option, index)
        if not isinstance(event, QMouseEvent) or event.button() != Qt.MouseButton.LeftButton:
            return super().editorEvent(event, model, option, index)
        parent = option.widget
        self._pick_and_apply(parent.window() if parent is not None else None, model, index)
        return True

    def _pick_and_apply(
        self,
        parent: QWidget | None,
        model: QAbstractItemModel | None,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        if model is None or not index.isValid():
            return
        current = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        dialog = HabitEmojiPickerDialog(parent, current_emoji=current)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        model.setData(index, normalize_habit_emoji(dialog.selected_emoji()), Qt.ItemDataRole.EditRole)
