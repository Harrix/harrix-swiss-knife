"""Tests for food kcal lookup TSV parsing."""

from __future__ import annotations

from harrix_swiss_knife.apps.food.kcal_lookup_parser import (
    KcalLookupResult,
    calories_from_kcal_lookup,
    normalize_kcal_lookup_mode,
    parse_kcal_lookup_response,
)


def test_parse_packaged_snack_weight_mode() -> None:
    result = parse_kcal_lookup_response("430\tweight\tno\t17")
    assert result is not None
    assert result.is_weight_mode is True
    assert result.calories == 430.0
    assert result.weight_g == 17


def test_parse_portion_mislabel_corrected_to_weight() -> None:
    """430 kcal for 17 g as portion implies >900 kcal/100g — treat as per 100g."""
    result = parse_kcal_lookup_response("430\tportion\tno\t17")
    assert result is not None
    assert result.is_weight_mode is True
    assert result.calories == 430.0
    assert result.weight_g == 17


def test_parse_drink_portion_unchanged() -> None:
    result = parse_kcal_lookup_response("85\tportion\tyes\t180")
    assert result is not None
    assert result.is_weight_mode is False
    assert result.calories == 85.0


def test_normalize_skips_weight_mode() -> None:
    original = KcalLookupResult(calories=165.0, is_weight_mode=True, is_drink=False, weight_g=0)
    assert normalize_kcal_lookup_mode(original) is original


def test_calories_from_lookup_weight_mode_clears_portion() -> None:
    result = KcalLookupResult(calories=165.0, is_weight_mode=True, is_drink=False, weight_g=200)
    assert calories_from_kcal_lookup(result) == (165.0, None)


def test_calories_from_lookup_portion_mode_clears_per_100g() -> None:
    result = KcalLookupResult(calories=85.0, is_weight_mode=False, is_drink=True, weight_g=180)
    assert calories_from_kcal_lookup(result) == (None, 85.0)
