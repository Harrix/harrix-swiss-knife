"""Tests for the single-scroll Expense/Income category picker model."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QApplication, QListView, QMenu

from harrix_swiss_knife.apps.finance.category_icon_display import category_lucide_icon
from harrix_swiss_knife.apps.finance.category_list_model import (
    fill_category_picker_model,
    find_category_in_picker,
    iter_category_picker_rows,
    selected_category_name,
)
from harrix_swiss_knife.apps.finance.delegates.category_suggest_delegate import (
    ICON_LUCIDE_ROLE,
    ICON_ROLE,
    IS_SECTION_ROLE,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_fill_category_picker_model_sections_then_rows() -> None:
    model = QStandardItemModel()
    fill_category_picker_model(
        model,
        expense_categories=(("Food", "🍔", "Еда", "utensils"),),
        income_categories=(("Salary", "💰", "Зарплата", "wallet"),),
    )
    assert model.rowCount() == 4

    expense_header = model.item(0)
    assert expense_header is not None
    assert expense_header.text() == "Expense"
    assert expense_header.data(IS_SECTION_ROLE) is True
    assert not bool(expense_header.flags() & Qt.ItemFlag.ItemIsSelectable)

    food = model.item(1)
    assert food is not None
    assert food.text() == "Food"
    assert food.data(Qt.ItemDataRole.UserRole) == "Food"
    assert food.data(ICON_ROLE) == "🍔"
    assert food.data(ICON_LUCIDE_ROLE) == "utensils"
    assert food.data(IS_SECTION_ROLE) is False

    income_header = model.item(2)
    assert income_header is not None
    assert income_header.text() == "Income"
    assert income_header.data(IS_SECTION_ROLE) is True

    salary = model.item(3)
    assert salary is not None
    assert salary.text() == "Salary"
    assert "(Income)" not in salary.text()


def test_find_and_selected_category_skips_sections(qapp: QApplication) -> None:  # noqa: ARG001
    view = QListView()
    model = QStandardItemModel()
    fill_category_picker_model(
        model,
        expense_categories=(("Food", "🍔", "Еда", "utensils"),),
        income_categories=(("Salary", "💰", "Зарплата", "wallet"),),
    )
    view.setModel(model)
    host = SimpleNamespace(listView_categories=view)

    found = find_category_in_picker(host, "Salary")
    assert found is not None
    assert found.data(Qt.ItemDataRole.UserRole) == "Salary"

    view.setCurrentIndex(found)
    assert selected_category_name(host) == "Salary"
    assert [name for _, name, _ in iter_category_picker_rows(host)] == ["Food", "Salary"]

    view.setCurrentIndex(model.index(0, 0))
    assert selected_category_name(host) is None


def test_category_label_menu_actions_have_lucide_icons(qapp: QApplication) -> None:
    """Category picker rows expose icon roles used by the label dropdown menu."""
    assert qapp is not None
    view = QListView()
    model = QStandardItemModel()
    fill_category_picker_model(
        model,
        expense_categories=(("Food", "🍔", "Еда", "utensils"),),
        income_categories=(("Salary", "💰", "Зарплата", "wallet"),),
    )
    view.setModel(model)
    host = SimpleNamespace(listView_categories=view)
    menu = QMenu()
    for index, category_name, _local in iter_category_picker_rows(host):
        emoji = "" if index.data(ICON_ROLE) is None else str(index.data(ICON_ROLE))
        lucide = "" if index.data(ICON_LUCIDE_ROLE) is None else str(index.data(ICON_LUCIDE_ROLE))
        action = menu.addAction(category_lucide_icon(emoji, lucide_name=lucide), category_name)
        assert not action.icon().isNull(), category_name
    assert [action.text() for action in menu.actions()] == ["Food", "Salary"]
    menu.close()
