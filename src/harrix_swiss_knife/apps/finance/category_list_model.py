"""Build Transaction category picker models for Expense and Income blocks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QListView

from harrix_swiss_knife.apps.finance.delegates.category_suggest_delegate import (
    ICON_LUCIDE_ROLE,
    ICON_ROLE,
    NAME_LOCAL_ROLE,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

CategoryIconRow = tuple[str, str, str, str]


def category_picker_views(host: Any) -> tuple[QListView, QListView]:
    """Return `(expense_view, income_view)` for the transaction category column."""
    return host.listView_categories, host.listView_categories_income


def fill_category_picker_model(model: QStandardItemModel, categories: Sequence[CategoryIconRow]) -> None:
    """Replace `model` rows with plain category items (no section headers)."""
    model.clear()
    for category_name, icon, name_local, icon_lucide in categories:
        item = QStandardItem(category_name)
        item.setData(category_name, Qt.ItemDataRole.UserRole)
        item.setData(name_local, NAME_LOCAL_ROLE)
        item.setData(icon or "", ICON_ROLE)
        item.setData(icon_lucide or "", ICON_LUCIDE_ROLE)
        item.setData(category_name, Qt.ItemDataRole.ToolTipRole)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        model.appendRow(item)


def find_category_in_picker_views(
    host: Any,
    category_name: str,
) -> tuple[QListView, QModelIndex] | None:
    """Locate `category_name` in either Expense or Income list."""
    target = category_name.strip()
    if not target:
        return None
    for view in category_picker_views(host):
        model = view.model()
        if model is None:
            continue
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            value = model.data(index, Qt.ItemDataRole.UserRole)
            if value is not None and str(value) == target:
                return view, index
    return None


def iter_category_picker_rows(host: Any) -> Iterator[tuple[QModelIndex, str, str]]:
    """Yield `(index, name, name_local)` for every category in both lists."""
    for view in category_picker_views(host):
        model = view.model()
        if model is None:
            continue
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            name = model.data(index, Qt.ItemDataRole.UserRole)
            if not name:
                continue
            local = model.data(index, NAME_LOCAL_ROLE)
            yield index, str(name), "" if local is None else str(local)


def selected_category_name(host: Any) -> str | None:
    """Return the selected category name from either Expense or Income list."""
    for view in category_picker_views(host):
        index = view.currentIndex()
        if not index.isValid():
            continue
        value = index.data(Qt.ItemDataRole.UserRole)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def selected_category_index(host: Any) -> tuple[QListView, QModelIndex] | None:
    """Return the view and index of the currently selected category, if any."""
    for view in category_picker_views(host):
        index = view.currentIndex()
        if not index.isValid():
            continue
        value = index.data(Qt.ItemDataRole.UserRole)
        if value is None or not str(value).strip():
            continue
        return view, index
    return None
