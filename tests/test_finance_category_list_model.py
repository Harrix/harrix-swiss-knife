"""Tests for Expense/Income sections in the category picker model."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel

from harrix_swiss_knife.apps.finance.category_list_model import populate_category_picker_model
from harrix_swiss_knife.apps.finance.delegates.category_suggest_delegate import (
    ICON_LUCIDE_ROLE,
    IS_SECTION_ROLE,
)
from harrix_swiss_knife.apps.finance.transaction_filter_chrome import EXPENSE_LUCIDE_ICON, INCOME_LUCIDE_ICON


def test_populate_category_picker_model_sections() -> None:
    model = QStandardItemModel()
    populate_category_picker_model(
        model,
        expense_categories=(("Food", "🍔", "Еда", "utensils"),),
        income_categories=(("Salary", "💰", "Зарплата", "wallet"),),
    )
    assert model.rowCount() == 4

    expense_header = model.item(0)
    assert expense_header is not None
    assert expense_header.text() == "Expense"
    assert expense_header.data(IS_SECTION_ROLE) is True
    assert expense_header.data(Qt.ItemDataRole.UserRole) == ""
    assert expense_header.data(ICON_LUCIDE_ROLE) == EXPENSE_LUCIDE_ICON
    assert not bool(expense_header.flags() & Qt.ItemFlag.ItemIsSelectable)

    food = model.item(1)
    assert food is not None
    assert food.text() == "Food"
    assert food.data(Qt.ItemDataRole.UserRole) == "Food"
    assert food.data(IS_SECTION_ROLE) is False

    income_header = model.item(2)
    assert income_header is not None
    assert income_header.text() == "Income"
    assert income_header.data(IS_SECTION_ROLE) is True
    assert income_header.data(ICON_LUCIDE_ROLE) == INCOME_LUCIDE_ICON

    salary = model.item(3)
    assert salary is not None
    assert salary.text() == "Salary"
    assert salary.data(Qt.ItemDataRole.UserRole) == "Salary"
    assert "(Income)" not in salary.text()
