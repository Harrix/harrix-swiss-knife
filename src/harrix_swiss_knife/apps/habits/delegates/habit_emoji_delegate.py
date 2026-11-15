"""Table delegate that edits habit emoji and Lucide icon."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import (
    QAbstractItemModel,
    QAbstractProxyModel,
    QEvent,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
)
from PySide6.QtGui import QIcon, QMouseEvent, QStandardItemModel
from PySide6.QtWidgets import QDialog, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.habits.habit_emojis import normalize_habit_emoji
from harrix_swiss_knife.apps.habits.habit_icon_display import habit_lucide_icon, normalize_habit_lucide_name
from harrix_swiss_knife.apps.habits.habit_icon_edit_dialog import HabitIconEditDialog

# Stored on the emoji column alongside DisplayRole emoji text.
HABIT_ICON_LUCIDE_ROLE = int(Qt.ItemDataRole.UserRole) + 20


class HabitEmojiDelegate(QStyledItemDelegate):
    """Delegate that edits emoji and Lucide through `HabitIconEditDialog`."""

    def __init__(self, parent: QObject | None = None, *, app_config: dict[str, Any] | None = None) -> None:
        """Initialize HabitEmojiDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object for the delegate.
        - `app_config` (`dict[str, Any] | None`): App config for Lucide AI suggestions.

        """
        super().__init__(parent)
        self._app_config = app_config or {}

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Open the icon editor on left-click or double-click."""
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
        current_emoji = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        current_lucide = normalize_habit_lucide_name(str(index.data(HABIT_ICON_LUCIDE_ROLE) or ""))
        habit_name = str(model.data(model.index(index.row(), 0), Qt.ItemDataRole.DisplayRole) or "")
        habit_id = _habit_id_from_index(model, index)

        dialog = HabitIconEditDialog(
            parent,
            emoji=current_emoji,
            icon_lucide=current_lucide,
            habit_name=habit_name,
            habit_id=habit_id,
            app_config=self._app_config,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        emoji = normalize_habit_emoji(dialog.selected_emoji(), habit_id=habit_id)
        lucide = dialog.selected_icon_lucide()
        icon = habit_lucide_icon(lucide)
        # UserRole / DecorationRole do not auto-save; EditRole does and reads Lucide from UserRole.
        model.setData(index, lucide, HABIT_ICON_LUCIDE_ROLE)
        model.setData(index, emoji, Qt.ItemDataRole.EditRole)
        model.setData(index, icon if not icon.isNull() else QIcon(), Qt.ItemDataRole.DecorationRole)


def _habit_id_from_index(model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> int | None:
    """Return the habits table vertical-header ID for `index`, if present."""
    source: QAbstractItemModel | None = model
    source_index: QModelIndex | QPersistentModelIndex = index
    while isinstance(source, QAbstractProxyModel):
        source_index = source.mapToSource(source_index)
        source = source.sourceModel()
    if not isinstance(source, QStandardItemModel) or not source_index.isValid():
        return None
    header = source.verticalHeaderItem(source_index.row())
    if header is None:
        return None
    try:
        return int(header.text())
    except (TypeError, ValueError):
        return None
