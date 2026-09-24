"""Tests for shared first-letter capitalization."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.text_case import capitalize_first_letter, edited_source_text_differs


def test_capitalize_first_letter_plain() -> None:
    assert capitalize_first_letter("яблоко") == "Яблоко"
    assert capitalize_first_letter("  apple ") == "Apple"
    assert capitalize_first_letter("Apple") == "Apple"


def test_capitalize_first_letter_leading_quotes() -> None:
    assert capitalize_first_letter('"яблоко"') == '"Яблоко"'
    assert capitalize_first_letter("«яблоко»") == "«Яблоко»"
    assert capitalize_first_letter("'apple") == "'Apple"


def test_capitalize_first_letter_leading_emoji() -> None:
    assert capitalize_first_letter("🍎 яблоко") == "🍎 Яблоко"
    assert capitalize_first_letter('🍎 "яблоко"') == '🍎 "Яблоко"'
    assert capitalize_first_letter("☕ coffee") == "☕ Coffee"


def test_edited_source_text_differs_ignores_case_and_outer_space() -> None:
    assert not edited_source_text_differs("Молоко", "молоко")
    assert not edited_source_text_differs("  Milk  ", "Milk")
    assert edited_source_text_differs("Молоко", "Кефир")
    assert edited_source_text_differs("Milk", "Milk 2%")


def test_capitalize_first_letter_empty_or_symbols() -> None:
    assert capitalize_first_letter("") == ""
    assert capitalize_first_letter("   ") == ""
    assert capitalize_first_letter("123") == "123"
    assert capitalize_first_letter("🍎") == "🍎"
