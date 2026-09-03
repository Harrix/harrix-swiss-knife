"""Tests for the food items catalog dialog."""

from __future__ import annotations

from typing import Any, cast

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.food.food_item_dialog import FoodItemDialog
from harrix_swiss_knife.apps.food.food_items_dialog import FoodItemsDialog


class _FakeFoodDb:
    """Minimal stand-in for `DatabaseManager` food-item reads."""

    def get_all_food_items(self) -> list[list[Any]]:
        return [[1, "Apple", "Apple", 0, 52.0, 100.0, None]]


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


def test_food_items_dialog_title_and_table(qapp: QApplication) -> None:  # noqa: ARG001
    """Food Items dialog loads catalog rows into the table."""
    dialog = FoodItemsDialog(None, cast("Any", _FakeFoodDb()))
    assert dialog.windowTitle() == "Food Items"
    assert dialog.catalog_changed is False
    model = dialog.table.model()
    assert model is not None
    assert model.rowCount() == 1
    assert model.columnCount() == 6
    assert [model.headerData(i, Qt.Orientation.Horizontal) for i in range(6)] == [
        "Name",
        "Name EN",
        "Drink",
        "kcal/100g",
        "Portion g",
        "Portion kcal",
    ]
    assert model.index(0, 0).data() == "Apple"
    dialog.close()


def test_food_item_dialog_capitalizes_names(qapp: QApplication) -> None:  # noqa: ARG001
    """Create Food Item capitalizes Name and English Name."""
    dialog = FoodItemDialog(is_create=True)
    dialog.name_edit.setText("яблоко")
    dialog.name_en_edit.setText("apple")
    dialog.calories_per_100g_spinbox.setValue(52)
    assert dialog.get_edited_data()["name"] == "Яблоко"
    assert dialog.get_edited_data()["name_en"] == "Apple"
    dialog.close()
