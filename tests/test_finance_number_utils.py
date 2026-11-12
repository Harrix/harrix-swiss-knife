"""Tests for finance amount formatting."""

from __future__ import annotations

from harrix_swiss_knife.apps.finance.number_utils import format_amount


def test_format_amount_uses_subscript_decimals() -> None:
    assert format_amount("1234.56") == "1 234.₅₆"
    assert format_amount("-19.99") == "-19.₉₉"
    assert format_amount("100.00") == "100.₀₀"


def test_format_amount_preserves_rate_decimals() -> None:
    assert format_amount("92.1234") == "92.₁₂₃₄"


def test_format_amount_can_omit_whole_decimals() -> None:
    assert format_amount("100.00", always_decimals=False) == "100"
