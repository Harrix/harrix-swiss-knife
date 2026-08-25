"""Tests for pinning favorite exercises to the top of lists."""

from __future__ import annotations

from harrix_swiss_knife.apps.fitness.exercise_favorites import (
    format_favorite_exercise_label,
    parse_exercise_display_name,
    prefer_favorite_names,
)


def test_prefer_favorite_names_keeps_relative_order() -> None:
    """Favorites keep their original order and sit above the rest."""
    names = ["A", "B", "C", "D"]
    assert prefer_favorite_names(names, {"C", "A"}) == ["A", "C", "B", "D"]


def test_prefer_favorite_names_empty_favorites() -> None:
    """Without favorites the input order is unchanged."""
    names = ["A", "B"]
    assert prefer_favorite_names(names, set()) == ["A", "B"]


def test_prefer_favorite_names_all_favorites() -> None:
    """When every name is a favorite, relative order is kept."""
    names = ["B", "A"]
    assert prefer_favorite_names(names, {"A", "B"}) == ["B", "A"]


def test_format_favorite_exercise_label() -> None:
    """A star is prefixed only for favorites; extra text stays a suffix."""
    assert format_favorite_exercise_label("Plank", favorite=True, extra="3/10") == "⭐ Plank 3/10"
    assert format_favorite_exercise_label("Plank", favorite=False) == "Plank"
    assert format_favorite_exercise_label("Press", favorite=False, dumbbell=True) == "🏋️ Press"
    assert format_favorite_exercise_label("Press", favorite=True, dumbbell=True, extra="2/8") == "⭐ 🏋️ Press 2/8"


def test_parse_exercise_display_name() -> None:
    """Favorite and dumbbell prefixes are stripped from table display text."""
    assert parse_exercise_display_name("⭐ 🏋️ Press") == "Press"
    assert parse_exercise_display_name("🏋️ Press") == "Press"
    assert parse_exercise_display_name("Plank") == "Plank"
