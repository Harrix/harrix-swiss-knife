"""Tests for food list display string helpers."""

from __future__ import annotations

import pytest

from harrix_swiss_knife.apps.food.services.food_display import (
    DRINK_EMOJI,
    FOOD_ITEM_EMOJI,
    RECIPE_EMOJI,
    extract_food_name_from_display,
    format_food_name_with_calories,
    partition_food_item_indexes_by_filter,
)


def test_extract_food_name_from_display_empty() -> None:
    assert extract_food_name_from_display("") == ""


@pytest.mark.parametrize(
    ("display", "expected"),
    [
        ("Apple", "Apple"),
        ("Oatmeal (120 kcal/portion)", "Oatmeal"),
        ("Rice (45.5 kcal/100g)", "Rice"),
        (f"{DRINK_EMOJI} Tea (5 kcal/portion)", "Tea"),
        (f"{DRINK_EMOJI} Water", "Water"),
        (f"{RECIPE_EMOJI} Borscht (45 kcal/100g)", "Borscht"),
        (f"{RECIPE_EMOJI} {DRINK_EMOJI} Smoothie (60 kcal/100g)", "Smoothie"),
        (f"{FOOD_ITEM_EMOJI} Apple", "Apple"),
        (f"{FOOD_ITEM_EMOJI} {DRINK_EMOJI} Tea", "Tea"),
        (
            "Name with (120 kcal/portion) extra",
            "Name with (120 kcal/portion) extra",
        ),
    ],
)
def test_extract_food_name_from_display_suffix(display: str, expected: str) -> None:
    assert extract_food_name_from_display(display) == expected


def test_format_food_name_with_calories_empty_name() -> None:
    assert format_food_name_with_calories("", 100.0, None) == ""


def test_format_food_name_with_calories_portion_preferred() -> None:
    assert format_food_name_with_calories("Egg", 140.0, 70.0) == "Egg (70 kcal/portion)"


def test_format_food_name_with_calories_100g_when_no_portion() -> None:
    assert format_food_name_with_calories("Rice", 130.5, None) == "Rice (130 kcal/100g)"


def test_format_food_name_with_calories_no_values() -> None:
    assert format_food_name_with_calories("Plain", None, None) == "Plain"


def test_format_food_name_with_calories_fractional_calories() -> None:
    assert format_food_name_with_calories("X", 12.3, None) == "X (12 kcal/100g)"


def test_format_food_name_with_calories_drink_prefix() -> None:
    assert format_food_name_with_calories("Tea", None, 5.0, is_drink=True) == f"{DRINK_EMOJI} Tea (5 kcal/portion)"
    assert format_food_name_with_calories("Water", None, None, is_drink=True) == f"{DRINK_EMOJI} Water"
    assert format_food_name_with_calories("Egg", 140.0, 70.0, is_drink=False) == "Egg (70 kcal/portion)"


def test_format_food_name_with_calories_recipe_prefix() -> None:
    assert (
        format_food_name_with_calories("Borscht", 45.0, None, is_recipe=True)
        == f"{RECIPE_EMOJI} Borscht (45 kcal/100g)"
    )
    assert (
        format_food_name_with_calories("Smoothie", 60.0, None, is_drink=True, is_recipe=True)
        == f"{RECIPE_EMOJI} {DRINK_EMOJI} Smoothie (60 kcal/100g)"
    )


def test_partition_food_item_indexes_by_filter_keeps_matches_first() -> None:
    texts = ["Banana", "Apricot", "Berry", "Apple"]
    matched, unmatched = partition_food_item_indexes_by_filter(texts, "ap")
    assert matched == [3, 1]  # Apple, Apricot
    assert unmatched == [0, 2]  # Banana, Berry


def test_partition_food_item_indexes_by_filter_sorts_dimmed_alphabetically() -> None:
    texts = ["Zucchini", "Milk", "Apple", "Yogurt"]
    matched, unmatched = partition_food_item_indexes_by_filter(texts, "milk")
    assert matched == [1]
    assert unmatched == [2, 3, 0]  # Apple, Yogurt, Zucchini


def test_partition_food_item_indexes_by_filter_empty_query_matches_all() -> None:
    texts = ["Banana", "Apple"]
    matched, unmatched = partition_food_item_indexes_by_filter(texts, "  ")
    assert matched == [1, 0]  # Apple, Banana
    assert unmatched == []
