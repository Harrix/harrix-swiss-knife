"""Tests for Expense/Income category picker models."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QApplication, QListView

from harrix_swiss_knife.apps.finance.category_list_model import (
    fill_category_picker_model,
    find_category_in_picker_views,
    iter_category_picker_rows,
    selected_category_name,
)
from harrix_swiss_knife.apps.finance.delegates.category_suggest_delegate import ICON_LUCIDE_ROLE, NAME_LOCAL_ROLE


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_fill_category_picker_model_plain_rows() -> None:
    model = QStandardItemModel()
    fill_category_picker_model(
        model,
        (("Food", "🍔", "Еда", "utensils"), ("Salary", "💰", "Зарплата", "wallet")),
    )
    assert model.rowCount() == 2
    food = model.item(0)
    assert food is not None
    assert food.text() == "Food"
    assert food.data(Qt.ItemDataRole.UserRole) == "Food"
    assert food.data(NAME_LOCAL_ROLE) == "Еда"
    assert food.data(ICON_LUCIDE_ROLE) == "utensils"
    assert "(Income)" not in food.text()


def test_find_and_selected_category_across_two_views(qapp: QApplication) -> None:  # noqa: ARG001
    expense_view = QListView()
    income_view = QListView()
    expense_model = QStandardItemModel()
    income_model = QStandardItemModel()
    fill_category_picker_model(expense_model, (("Food", "🍔", "Еда", "utensils"),))
    fill_category_picker_model(income_model, (("Salary", "💰", "Зарплата", "wallet"),))
    expense_view.setModel(expense_model)
    income_view.setModel(income_model)
    host = SimpleNamespace(listView_categories=expense_view, listView_categories_income=income_view)

    found = find_category_in_picker_views(host, "Salary")
    assert found is not None
    view, index = found
    assert view is income_view
    assert index.data(Qt.ItemDataRole.UserRole) == "Salary"

    income_view.setCurrentIndex(index)
    assert selected_category_name(host) == "Salary"
    assert [name for _, name, _ in iter_category_picker_rows(host)] == ["Food", "Salary"]
