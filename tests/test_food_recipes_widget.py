"""Tests for the Recipes tab list and delete placement."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QApplication, QMenu

from harrix_swiss_knife.apps.common.table_context_menu import LABEL_DELETE
from harrix_swiss_knife.apps.food.recipes_widget import RecipesWidget


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
    # apply_leading_emoji_icons moves the emoji into the action icon.
    assert shown == ["Delete"]
    assert LABEL_DELETE.endswith("Delete")
    widget.close()
