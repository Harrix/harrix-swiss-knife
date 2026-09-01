"""Tests for food name autocomplete items."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCompleter

from harrix_swiss_knife.apps.food.database_manager import FoodAutocompleteEntry, merge_food_autocomplete_entries
from harrix_swiss_knife.apps.food.food_name_autocomplete import (
    FOOD_AUTOCOMPLETE_ICON_GAP,
    FOOD_AUTOCOMPLETE_ICON_SIZE,
    food_autocomplete_icon_emojis,
    food_autocomplete_popup_icon_size,
    make_food_autocomplete_item,
    setup_completer_item_tooltips,
)
from harrix_swiss_knife.apps.food.services.food_display import DRINK_EMOJI, FOOD_ITEM_EMOJI, RECIPE_EMOJI
from harrix_swiss_knife.qt_emoji_icon import create_emoji_row_icon


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


def test_make_food_autocomplete_item_food_item_has_icon(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(
        FoodAutocompleteEntry(name="Apple", name_en="Apple", is_food_item=True),
    )
    expected = create_emoji_row_icon([FOOD_ITEM_EMOJI], FOOD_AUTOCOMPLETE_ICON_SIZE)
    assert item.text() == "Apple"
    assert FOOD_ITEM_EMOJI not in item.text()
    assert (
        item.icon().pixmap(FOOD_AUTOCOMPLETE_ICON_SIZE, FOOD_AUTOCOMPLETE_ICON_SIZE).toImage()
        == expected.pixmap(FOOD_AUTOCOMPLETE_ICON_SIZE, FOOD_AUTOCOMPLETE_ICON_SIZE).toImage()
    )


def test_make_food_autocomplete_item_food_item_drink_has_both_icons(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(
        FoodAutocompleteEntry(name="Tea", name_en="Tea", is_food_item=True, is_drink=True),
    )
    expected = create_emoji_row_icon(
        [FOOD_ITEM_EMOJI, DRINK_EMOJI],
        FOOD_AUTOCOMPLETE_ICON_SIZE,
        gap=FOOD_AUTOCOMPLETE_ICON_GAP,
    )
    size = food_autocomplete_popup_icon_size()
    assert item.text() == "Tea"
    assert DRINK_EMOJI not in item.text()
    assert item.icon().pixmap(size).toImage() == expected.pixmap(size).toImage()


def test_make_food_autocomplete_item_recipe_drink_has_both_icons(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(
        FoodAutocompleteEntry(name="Smoothie", name_en="Smoothie", is_recipe=True, is_drink=True),
    )
    assert food_autocomplete_icon_emojis(
        FoodAutocompleteEntry(name="Smoothie", name_en="Smoothie", is_recipe=True, is_drink=True),
    ) == [RECIPE_EMOJI, DRINK_EMOJI]
    assert RECIPE_EMOJI not in item.text()
    assert DRINK_EMOJI not in item.text()
    assert not item.icon().isNull()


def test_make_food_autocomplete_item_plain_food_has_no_icon(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(FoodAutocompleteEntry(name="Apple", name_en="Apple"))
    assert item.icon().isNull()
    assert item.text() == "Apple"


def test_make_food_autocomplete_item_log_drink_has_drink_icon(qapp: QApplication) -> None:  # noqa: ARG001
    item = make_food_autocomplete_item(
        FoodAutocompleteEntry(name="Water", name_en="Water", is_drink=True),
    )
    assert food_autocomplete_icon_emojis(
        FoodAutocompleteEntry(name="Water", name_en="Water", is_drink=True),
    ) == [DRINK_EMOJI]
    assert not item.icon().isNull()
    assert item.text() == "Water"


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
    assert food_autocomplete_icon_emojis(entry) == [RECIPE_EMOJI, DRINK_EMOJI]


def test_setup_completer_item_tooltips_sets_icon_size(qapp: QApplication) -> None:  # noqa: ARG001
    completer = QCompleter()
    setup_completer_item_tooltips(completer)
    popup = completer.popup()
    assert popup is not None
    assert popup.iconSize() == food_autocomplete_popup_icon_size()
