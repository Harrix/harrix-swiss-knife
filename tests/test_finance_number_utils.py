"""Tests for finance number parsing helpers."""

from __future__ import annotations

from harrix_swiss_knife.apps.finance.number_utils import (
    clean_number_text,
    major_units_to_minor,
    sqlite_max_major_amount,
)


def test_clean_number_text_spaces() -> None:
    assert clean_number_text("1 234.56") == "1234.56"


def test_clean_number_text_subscripts() -> None:
    assert clean_number_text("₁₂₃₄₅₆₇₈₉") == "123456789"


def test_clean_number_text_mixed() -> None:
    assert clean_number_text("  ₁ 2 ₃  ") == "123"


def test_major_units_to_minor_keeps_one_kopeck() -> None:
    assert major_units_to_minor(0.01, 100) == 1
    assert major_units_to_minor(-0.01, 100) == -1


def test_sqlite_max_major_amount_fits_signed_64_bit_minor_units() -> None:
    for subdivision in (1, 100, 1_000):
        maximum = sqlite_max_major_amount(subdivision)
        assert major_units_to_minor(maximum, subdivision) <= 2**63 - 1
        assert maximum > 999_999.99


def test_major_units_to_minor_rounds_instead_of_truncating() -> None:
    assert int(19.99 * 100) == 1998
    assert major_units_to_minor(19.99, 100) == 1999
    assert major_units_to_minor(1.13, 100) == 113
