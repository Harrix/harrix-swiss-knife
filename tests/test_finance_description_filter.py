"""Tests for Unicode-aware transaction description filtering."""

from __future__ import annotations

from harrix_swiss_knife.apps.finance.database_manager import (
    _description_matches_filter,
    _filter_rows_by_description,
)


def test_description_matches_filter_cyrillic_case_insensitive() -> None:
    assert _description_matches_filter("Ветчина Для тостов «Клинский» нарезка", "Ветчина")
    assert _description_matches_filter("Ветчина Для тостов «Клинский» нарезка", "ветчина")
    assert _description_matches_filter("Влажный корм для кошек Schesir Тунец и ветчина 85г", "ветчина")
    assert not _description_matches_filter("Молоко 2.5%", "Ветчина")


def test_filter_rows_by_description() -> None:
    rows = [
        [1, 100, "Ветчина Для тостов «Клинский» нарезка", "Food", "RUB", "2026-01-01", "", 0, "", "₽"],
        [2, 200, "Молоко 2.5%", "Food", "RUB", "2026-01-02", "", 0, "", "₽"],
        [3, 300, "Влажный корм для кошек Schesir Тунец и ветчина 85г", "Pets", "RUB", "2026-01-03", "", 0, "", "₽"],
    ]
    filtered = _filter_rows_by_description(rows, "Ветчина")
    assert [row[0] for row in filtered] == [1, 3]
