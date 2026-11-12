"""Build the Transaction category picker model with Expense/Income sections."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from harrix_swiss_knife.apps.finance.delegates.category_suggest_delegate import (
    ICON_LUCIDE_ROLE,
    ICON_ROLE,
    IS_SECTION_ROLE,
    NAME_LOCAL_ROLE,
)
from harrix_swiss_knife.apps.finance.transaction_filter_chrome import EXPENSE_LUCIDE_ICON, INCOME_LUCIDE_ICON

if TYPE_CHECKING:
    from collections.abc import Sequence

CategoryIconRow = tuple[str, str, str, str]


def populate_category_picker_model(
    model: QStandardItemModel,
    *,
    expense_categories: Sequence[CategoryIconRow],
    income_categories: Sequence[CategoryIconRow],
) -> None:
    """Fill `model` with Expense and Income section blocks."""
    model.clear()
    _append_section(model, "Expense", EXPENSE_LUCIDE_ICON)
    for category_name, icon, name_local, icon_lucide in expense_categories:
        _append_category(model, category_name, icon, name_local, icon_lucide)
    _append_section(model, "Income", INCOME_LUCIDE_ICON)
    for category_name, icon, name_local, icon_lucide in income_categories:
        _append_category(model, category_name, icon, name_local, icon_lucide)


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


def _append_section(model: QStandardItemModel, title: str, lucide_name: str) -> None:
    item = QStandardItem(title)
    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    item.setData("", Qt.ItemDataRole.UserRole)
    item.setData(True, IS_SECTION_ROLE)
    item.setData(lucide_name, ICON_LUCIDE_ROLE)
    item.setData(title, Qt.ItemDataRole.ToolTipRole)
    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    model.appendRow(item)
