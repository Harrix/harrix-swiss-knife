"""Tag delegate for the tag column in the transactions table."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtWidgets import (
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.ui_helpers import apply_white_editor_background
from harrix_swiss_knife.apps.finance.tags import format_tag_text, parse_tag_text

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtCore import QObject

_EDITOR_HEIGHT = 200
_EDITOR_MIN_WIDTH = 220


class TagDelegate(QStyledItemDelegate):
    """Edit a transaction tag cell as a check list of several tags."""

    def __init__(
        self,
        parent: QObject | None = None,
        tags: list[str] | None = None,
        *,
        tags_provider: Callable[[], list[str]] | None = None,
    ) -> None:
        """Initialize the tag delegate.

        Args:

        - `parent` (`QObject | None`): Parent object, usually the transactions view.
        - `tags` (`list[str] | None`): Fallback names when `tags_provider` is omitted.
        - `tags_provider` (`Callable[[], list[str]] | None`): Called each time the
          editor opens so newly saved tags appear without rebuilding the delegate.

        """
        super().__init__(parent)
        self._tags = list(tags or [])
        self._tags_provider = tags_provider

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Open a check list of known tags with the current cell values checked."""
        raw = index.data()
        selected = parse_tag_text(str(raw) if raw is not None else "")
        return _TagCheckListEditor(self._known_tags(), selected, parent)

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:  # noqa: N802
        """Check the tags currently stored in the cell."""
        checklist = cast("_TagCheckListEditor", editor)
        raw = index.data()
        selected = {name.casefold() for name in parse_tag_text(str(raw) if raw is not None else "")}
        tag_list = checklist.findChild(QListWidget)
        if tag_list is None:
            return
        for row in range(tag_list.count()):
            item = tag_list.item(row)
            if item is None:
                continue
            item.setCheckState(Qt.CheckState.Checked if item.text().casefold() in selected else Qt.CheckState.Unchecked)

    def setModelData(  # noqa: N802
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Write the checked tags back as one comma-separated cell value."""
        checklist = cast("_TagCheckListEditor", editor)
        model.setData(index, checklist.tags_text(), Qt.ItemDataRole.DisplayRole)

    @property
    def tags(self) -> list[str]:
        """Tag names shown when no provider is set."""
        return list(self._tags)

    @tags.setter
    def tags(self, value: list[str] | None) -> None:
        self._tags = list(value or [])

    def updateEditorGeometry(  # noqa: N802
        self,
        editor: QWidget,
        option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Give the check list enough height to show several tags."""
        rect = option.rect
        height = _EDITOR_HEIGHT
        width = max(rect.width(), _EDITOR_MIN_WIDTH)
        parent = editor.parentWidget()
        if parent is not None:
            bounds = parent.rect()
            width = min(width, bounds.width())
            height = min(height, bounds.height())
            if rect.top() + height > bounds.bottom() + 1:
                rect.moveTop(max(bounds.top(), bounds.bottom() + 1 - height))
            if rect.left() + width > bounds.right() + 1:
                rect.moveLeft(max(bounds.left(), bounds.right() + 1 - width))
        rect.setWidth(width)
        rect.setHeight(height)
        editor.setGeometry(rect)

    def _known_tags(self) -> list[str]:
        """Return the tag names the editor should offer."""
        if self._tags_provider is not None:
            return list(self._tags_provider())
        return list(self._tags)


class _TagCheckListEditor(QWidget):
    """Check list of known tags plus a field for a new name."""

    def __init__(
        self,
        known_tags: list[str],
        selected: list[str],
        parent: QWidget | None = None,
    ) -> None:
        """Build the check list and the field used to type one more tag."""
        super().__init__(parent)
        self.setAutoFillBackground(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        self._list = QListWidget(self)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        names = list(known_tags)
        selected_keys = {name.casefold() for name in selected}
        known_keys = {name.casefold() for name in names}
        for name in selected:
            if name.casefold() not in known_keys:
                names.append(name)
                known_keys.add(name.casefold())
        for name in names:
            item = QListWidgetItem(name, self._list)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if name.casefold() in selected_keys else Qt.CheckState.Unchecked)
        layout.addWidget(self._list, stretch=1)

        self._new_tag = QLineEdit(self)
        self._new_tag.setPlaceholderText("Add tag")
        layout.addWidget(self._new_tag)
        apply_white_editor_background(self, "QWidget")
        self._list.setStyleSheet("QListWidget { background-color: white; border: none; }")
        self._new_tag.setStyleSheet("QLineEdit { background-color: white; }")
        self.setFocusProxy(self._list)

    def tags_text(self) -> str:
        """Return the checked names plus any tag still typed in the add field."""
        names: list[str] = []
        for index in range(self._list.count()):
            item = self._list.item(index)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                names.append(item.text())
        names.extend(parse_tag_text(self._new_tag.text()))
        return format_tag_text(names)
