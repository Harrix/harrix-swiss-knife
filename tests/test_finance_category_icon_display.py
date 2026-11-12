"""Tests for finance category emoji → Lucide display mapping."""

from __future__ import annotations

from harrix_swiss_knife.apps.finance.category_icon_display import (
    category_display_label,
    lucide_name_for_category_icon,
    strip_category_display_value,
)


def test_seed_emojis_map_to_lucide() -> None:
    assert lucide_name_for_category_icon("🍔") == "utensils"
    assert lucide_name_for_category_icon("☕") == "coffee"
    assert lucide_name_for_category_icon("💰") == "wallet"
    assert lucide_name_for_category_icon("🔄") == "refresh-cw"
    assert lucide_name_for_category_icon("") is None


def test_unknown_emoji_falls_back_to_tags() -> None:
    assert lucide_name_for_category_icon("🛸") == "tags"


def test_category_display_label_plain() -> None:
    assert category_display_label("Food") == "Food"
    assert category_display_label("Salary", income=True) == "Salary (Income)"
    assert category_display_label("Food", name_local="Еда") == "Food (Еда)"


def test_strip_category_display_value() -> None:
    assert strip_category_display_value("Food") == "Food"
    assert strip_category_display_value("Food (Income)") == "Food"
    assert strip_category_display_value("🍔 Food") == "Food"
    assert strip_category_display_value("💰 Salary (Income)") == "Salary"
