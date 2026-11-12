"""Build the Transaction category picker as one scrollable Expense→Income list."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from harrix_swiss_knife.apps.finance.delegates.category_suggest_delegate import (
    ICON_LUCIDE_ROLE,
    ICON_ROLE,
    IS_SECTION_ROLE,
    NAME_LOCAL_ROLE,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

CategoryIconRow = tuple[str, str, str, str]


def fill_category_picker_model(
    model: QStandardItemModel,
    *,
    expense_categories: Sequence[CategoryIconRow],
    income_categories: Sequence[CategoryIconRow],
) -> None:
    """Fill one model: Expense section, expense rows, Income section, income rows."""
    model.clear()
    _append_section(model, "Expense")
    for category_name, icon, name_local, icon_lucide in expense_categories:
        _append_category(model, category_name, icon, name_local, icon_lucide)
    _append_section(model, "Income")
    for category_name, icon, name_local, icon_lucide in income_categories:
        _append_category(model, category_name, icon, name_local, icon_lucide)


def find_category_in_picker(
    host: Any,
    category_name: str,
) -> QModelIndex | None:
    """Locate `category_name` in the category picker list."""
    target = category_name.strip()
    if not target:
        return None
    model = host.listView_categories.model()
    if model is None:
        return None
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if bool(index.data(IS_SECTION_ROLE)):
            continue
        value = model.data(index, Qt.ItemDataRole.UserRole)
        if value is not None and str(value) == target:
            return index
    return None


def iter_category_picker_rows(host: Any) -> Iterator[tuple[QModelIndex, str, str]]:
    """Yield `(index, name, name_local)` for every real category row."""
    model = host.listView_categories.model()
    if model is None:
        return
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        if bool(index.data(IS_SECTION_ROLE)):
            continue
        name = model.data(index, Qt.ItemDataRole.UserRole)
        if not name:
            continue
        local = model.data(index, NAME_LOCAL_ROLE)
        yield index, str(name), "" if local is None else str(local)


def selected_category_name(host: Any) -> str | None:
    """Return the selected category name, ignoring section headers."""
    index = host.listView_categories.currentIndex()
    if not index.isValid() or bool(index.data(IS_SECTION_ROLE)):
        return None
    value = index.data(Qt.ItemDataRole.UserRole)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _append_category(
    model: QStandardItemModel,
    category_name: str,
    icon: str,
    name_local: str,
    icon_lucide: str,
) -> None:
    item = QStandardItem(category_name)
    item.setData(category_name, Qt.ItemDataRole.UserRole)
    item.setData(name_local, NAME_LOCAL_ROLE)
    item.setData(icon or "", ICON_ROLE)
    item.setData(icon_lucide or "", ICON_LUCIDE_ROLE)
    item.setData(False, IS_SECTION_ROLE)
    item.setData(category_name, Qt.ItemDataRole.ToolTipRole)
    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    model.appendRow(item)


def _append_section(model: QStandardItemModel, title: str) -> None:
    item = QStandardItem(title)
    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    item.setData("", Qt.ItemDataRole.UserRole)
    item.setData(True, IS_SECTION_ROLE)
    item.setData(title, Qt.ItemDataRole.ToolTipRole)
    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    model.appendRow(item)
