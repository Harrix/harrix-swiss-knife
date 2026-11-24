"""Tests for food name autocomplete items."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QApplication, QCompleter

from harrix_swiss_knife.apps.food.database_manager import FoodAutocompleteEntry, merge_food_autocomplete_entries
from harrix_swiss_knife.apps.food.food_name_autocomplete import (
    food_autocomplete_popup_icon_size,
    food_autocomplete_row_icon,
    make_food_autocomplete_item,
    setup_completer_item_tooltips,
)
from harrix_swiss_knife.apps.food.services.food_display import FOOD_ITEM_EMOJI, RECIPE_EMOJI


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


def test_completer_tooltip_helper_survives_popup_teardown(qapp: QApplication) -> None:
    """Popup teardown must not raise on late filters or a cleared `_popup`."""
    assert qapp is not None
    completer = QCompleter(["Apple", "Banana"])
    helper = setup_completer_item_tooltips(completer)
    assert helper.parent() is completer
    helper._on_popup_destroyed()
    assert helper._is_popup_alive() is False
    assert helper.eventFilter(completer, QEvent(QEvent.Type.Hide)) is False


def test_make_food_autocomplete_item_food_item_drink_has_both_icons(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(
        FoodAutocompleteEntry(name="Tea", name_en="Tea", is_food_item=True, is_drink=True),
    )
    size = food_autocomplete_popup_icon_size()
    assert item.text() == "Tea"
    assert not item.icon().isNull()
    assert item.icon().pixmap(size).width() >= size.width()


def test_make_food_autocomplete_item_food_item_has_icon(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(
        FoodAutocompleteEntry(name="Apple", name_en="Apple", is_food_item=True),
    )
    assert item.text() == "Apple"
    assert FOOD_ITEM_EMOJI not in item.text()
    assert not item.icon().isNull()


def test_make_food_autocomplete_item_log_drink_has_drink_icon(qapp: QApplication) -> None:  # noqa: ARG001
    entry = FoodAutocompleteEntry(name="Water", name_en="Water", is_drink=True)
    item = make_food_autocomplete_item(entry)
    assert not food_autocomplete_row_icon(entry).isNull()
    assert not item.icon().isNull()
    assert item.text() == "Water"


def test_make_food_autocomplete_item_plain_food_has_no_icon(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(FoodAutocompleteEntry(name="Apple", name_en="Apple"))
    assert item.icon().isNull()
    assert item.text() == "Apple"


def test_make_food_autocomplete_item_recipe_drink_has_both_icons(qapp: QApplication) -> None:  # noqa: ARG001
    entry = FoodAutocompleteEntry(name="Smoothie", name_en="Smoothie", is_recipe=True, is_drink=True)
    item = make_food_autocomplete_item(entry)
    assert not food_autocomplete_row_icon(entry).isNull()
    assert RECIPE_EMOJI not in item.text()
    assert not item.icon().isNull()


def test_make_food_autocomplete_item_recipe_has_icon(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(
        FoodAutocompleteEntry(name="Borscht", name_en="Borscht", is_recipe=True, calories_per_100g=45.0),
    )
    assert not item.icon().isNull()
    assert RECIPE_EMOJI not in item.text()
    assert item.data(Qt.ItemDataRole.EditRole) == "Borscht"


def test_merge_food_autocomplete_entries_ors_catalog_and_drink_flags() -> None:
    merged = merge_food_autocomplete_entries(
        [FoodAutocompleteEntry(name="Tea", name_en=None, is_drink=True)],
        [FoodAutocompleteEntry(name="Tea", name_en="Tea", is_food_item=True, is_drink=True)],
        [FoodAutocompleteEntry(name="Tea", name_en="Tea", is_recipe=True, calories_per_100g=5.0)],
    )
    assert len(merged) == 1
    entry = merged[0]
    assert entry.is_recipe
    assert entry.is_food_item
    assert entry.is_drink
    assert not food_autocomplete_row_icon(entry).isNull()


def test_setup_completer_item_tooltips_sets_icon_size(qapp: QApplication) -> None:  # noqa: ARG001
    completer = QCompleter()
    setup_completer_item_tooltips(completer)
    popup = completer.popup()
    assert popup is not None
    assert popup.iconSize() == food_autocomplete_popup_icon_size()
