"""Tests for food_log English name translation parsers."""

# ruff: noqa: RUF001

from __future__ import annotations

from harrix_swiss_knife.apps.food.food_translate_parser import (
    filter_food_translate_for_names,
    parse_food_translate_response,
)


def test_parse_food_translate_response_tsv() -> None:
    text = "Яблоко\tApple\nБанан\tBanana\n"
    assert parse_food_translate_response(text) == {"Яблоко": "Apple", "Банан": "Banana"}


def test_filter_food_translate_for_names_keeps_requested_only() -> None:
    translations = {
        "Яблоко": "Apple",
        "Банан": "Banana",
        "Extra": "Should drop",
    }
    filtered = filter_food_translate_for_names(translations, ["Яблоко", "Банан"])
    assert filtered == {"Яблоко": "Apple", "Банан": "Banana"}


def test_filter_food_translate_for_names_drops_blank_english() -> None:
    translations = {"Яблоко": "  ", "Банан": "Banana"}
    filtered = filter_food_translate_for_names(translations, ["Яблоко", "Банан"])
    assert filtered == {"Банан": "Banana"}
