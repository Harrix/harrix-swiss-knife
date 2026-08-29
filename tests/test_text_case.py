"""Tests for shared first-letter capitalization."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.text_case import capitalize_first_letter


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


def test_capitalize_first_letter_empty_or_symbols() -> None:
    assert capitalize_first_letter("") == ""
    assert capitalize_first_letter("   ") == ""
    assert capitalize_first_letter("123") == "123"
    assert capitalize_first_letter("🍎") == "🍎"
