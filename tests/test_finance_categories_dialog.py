"""Tests for the finance categories catalog dialog."""

from __future__ import annotations

from typing import Any, cast

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.categories_dialog import CategoriesDialog
from harrix_swiss_knife.apps.finance.category_add_dialog import CategoryAddDialog
from harrix_swiss_knife.apps.finance.category_edit_dialog import CategoryEditDialog


class _FakeFinanceDb:
    """Minimal stand-in for `DatabaseManager` category reads."""

    def get_all_categories(self) -> list[list[Any]]:
        return [[1, "Food", 0, "🍔", "Еда"]]


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for the dialog."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_categories_dialog_title_and_table(qapp: QApplication) -> None:  # noqa: ARG001
    """Categories dialog is titled Categories and loads catalog rows."""
    dialog = CategoriesDialog(None, cast("Any", _FakeFinanceDb()))
    assert dialog.windowTitle() == "Categories"
    assert dialog.catalog_changed is False
    model = dialog.table.model()
    assert model is not None
    assert model.rowCount() == 1
    assert model.columnCount() == 3
    assert [model.headerData(i, Qt.Orientation.Horizontal) for i in range(3)] == ["Name", "Type", "Local"]
    dialog.close()


def test_category_add_dialog_capitalizes_names(qapp: QApplication) -> None:  # noqa: ARG001
    """Add Category capitalizes Name and Local."""
    dialog = CategoryAddDialog()
    dialog._name_edit.setText("cafe")
    dialog._name_local_edit.setText("кафе")
    dialog._on_accept()
    assert dialog.get_result() == ("Cafe", 0, "", "Кафе")
    dialog.close()


def test_category_edit_dialog_capitalizes_names(qapp: QApplication) -> None:  # noqa: ARG001
    """Edit Category capitalizes Name and Local."""
    dialog = CategoryEditDialog(
        category_data={"id": 1, "name": "Food", "type": 0, "icon": "", "name_local": "Еда"},
    )
    dialog.name_edit.setText("food")
    dialog.name_local_edit.setText("еда")
    dialog._on_save()
    result = dialog.get_result()
    assert result["name"] == "Food"
    assert result["name_local"] == "Еда"
    dialog.close()
