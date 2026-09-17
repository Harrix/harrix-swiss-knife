"""Tests for the Recipes editor list and delete placement."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QLocale, QPoint, Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QApplication, QMenu, QWidget

from harrix_swiss_knife.apps.common.table_context_menu import LABEL_DELETE
from harrix_swiss_knife.apps.food.database_manager import DatabaseManager
from harrix_swiss_knife.apps.food.delegates import IsDrinkDelegate, is_drink_to_model
from harrix_swiss_knife.apps.food.recipe_calories import RecipeIngredientInput
from harrix_swiss_knife.apps.food.recipes_dialog import RecipesDialog
from harrix_swiss_knife.apps.food.recipes_widget import RecipesWidget
from harrix_swiss_knife.apps.food.services.food_display import DRINK_EMOJI


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for the widget."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_recipes_dialog_embeds_widget(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    recover_sql = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps" / "food" / "recover.sql"
    db_path = tmp_path / "food.db"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(recover_sql))
    db = DatabaseManager(str(db_path))
    dialog = RecipesDialog(None, db)
    assert dialog.windowTitle() == "Recipes"
    assert isinstance(dialog.recipes_widget, RecipesWidget)
    dialog.close()
    db.close()


def test_recipes_dialog_matches_parent_geometry(qapp: QApplication, tmp_path: Path) -> None:
    recover_sql = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps" / "food" / "recover.sql"
    db_path = tmp_path / "food.db"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(recover_sql))
    db = DatabaseManager(str(db_path))
    parent = QWidget()
    parent.resize(1100, 640)
    parent.move(80, 60)
    parent.show()
    qapp.processEvents()
    dialog = RecipesDialog(parent, db)
    assert dialog.size() == parent.size()
    assert dialog.pos() == parent.mapToGlobal(QPoint(0, 0))
    dialog.close()
    parent.close()
    db.close()


def test_recipes_widget_has_no_bottom_delete_button(qapp: QApplication) -> None:  # noqa: ARG001
    widget = RecipesWidget()
    assert not hasattr(widget, "button_delete")
    assert widget.button_new is not None
    assert widget.list_recipes.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu
    widget.close()


def test_recipe_id_and_name_from_index(qapp: QApplication) -> None:  # noqa: ARG001
    widget = RecipesWidget()
    item = QStandardItem("Borscht")
    item.setData(42, Qt.ItemDataRole.UserRole)
    widget._recipes_model.appendRow(item)
    index = widget._recipes_model.index(0, 0)
    assert widget._recipe_id_and_name_from_index(index) == (42, "Borscht")
    widget.close()


def test_recipe_context_menu_has_delete(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: ARG001
    widget = RecipesWidget()
    item = QStandardItem("Soup")
    item.setData(7, Qt.ItemDataRole.UserRole)
    widget._recipes_model.appendRow(item)
    shown: list[str] = []

    def _capture_popup(self: QMenu, _pos: object) -> None:
        shown.extend(action.text() for action in self.actions() if not action.isSeparator())

    monkeypatch.setattr(QMenu, "popup", _capture_popup)
    widget._show_recipe_context_menu(widget.list_recipes.visualRect(widget._recipes_model.index(0, 0)).center())
    # apply_leading_chrome_icons moves the emoji into the action icon.
    assert shown == ["Delete"]
    assert LABEL_DELETE.endswith("Delete")
    widget.close()


def test_ingredient_drink_column_matches_food_log(qapp: QApplication) -> None:  # noqa: ARG001
    widget = RecipesWidget()
    widget._ingredients = [
        RecipeIngredientInput(name="Water", weight=200, portion_calories=0, is_drink=True),
        RecipeIngredientInput(name="Rice", weight=100, calories_per_100g=130, is_drink=False),
    ]
    widget._refresh_ingredients_table()

    delegate = widget.table_ingredients.itemDelegateForColumn(5)
    assert isinstance(delegate, IsDrinkDelegate)
    assert delegate.displayText("1", QLocale()) == DRINK_EMOJI
    assert delegate.displayText("", QLocale()) == ""

    drink_item = widget.table_ingredients.item(0, 5)
    food_item = widget.table_ingredients.item(1, 5)
    assert drink_item is not None
    assert food_item is not None
    assert drink_item.text() == is_drink_to_model(checked=True)
    assert food_item.text() == is_drink_to_model(checked=False)
    assert drink_item.flags() & Qt.ItemFlag.ItemIsEditable
    assert not (widget.table_ingredients.item(0, 0).flags() & Qt.ItemFlag.ItemIsEditable)

    drink_item.setText(is_drink_to_model(checked=False))
    assert widget._ingredients[0].is_drink is False
    widget.close()
