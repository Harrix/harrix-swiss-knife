"""Tests for food name autocomplete items."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCompleter

from harrix_swiss_knife.apps.food.database_manager import FoodAutocompleteEntry
from harrix_swiss_knife.apps.food.food_name_autocomplete import (
    FOOD_AUTOCOMPLETE_ICON_SIZE,
    make_food_autocomplete_item,
    setup_completer_item_tooltips,
)
from harrix_swiss_knife.apps.food.services.food_display import RECIPE_EMOJI


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists so emoji icons can be rasterized."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_make_food_autocomplete_item_recipe_has_icon(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(
        FoodAutocompleteEntry(name="Borscht", name_en="Borscht", is_recipe=True, calories_per_100g=45.0),
    )
    assert not item.icon().isNull()
    assert RECIPE_EMOJI not in item.text()
    assert item.data(Qt.ItemDataRole.EditRole) == "Borscht"


def test_make_food_autocomplete_item_plain_food_has_no_icon(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(FoodAutocompleteEntry(name="Apple", name_en="Apple"))
    assert item.icon().isNull()
    assert item.text() == "Apple"


def test_setup_completer_item_tooltips_sets_icon_size(qapp: QApplication) -> None:  # noqa: ARG001
    completer = QCompleter()
    setup_completer_item_tooltips(completer)
    popup = completer.popup()
    assert popup is not None
    assert popup.iconSize().width() == FOOD_AUTOCOMPLETE_ICON_SIZE
    assert popup.iconSize().height() == FOOD_AUTOCOMPLETE_ICON_SIZE
