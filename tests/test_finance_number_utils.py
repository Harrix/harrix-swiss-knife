"""Tests for finance number parsing helpers."""

from __future__ import annotations

from harrix_swiss_knife.apps.finance.number_utils import clean_number_text


def test_clean_number_text_spaces() -> None:
    assert clean_number_text("1 234.56") == "1234.56"


def test_clean_number_text_subscripts() -> None:
    assert clean_number_text("₁₂₃₄₅₆₇₈₉") == "123456789"


def test_clean_number_text_mixed() -> None:
    assert clean_number_text("  ₁ 2 ₃  ") == "123"
