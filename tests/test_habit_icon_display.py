"""Tests for habit emoji → Lucide mapping and colored icons."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.habits.habit_icon_display import (
    HABIT_EMOJI_TO_LUCIDE,
    HABIT_LUCIDE_COLORS,
    habit_lucide_color,
    habit_lucide_icon,
    lucide_name_for_habit_emoji,
    normalize_habit_lucide_name,
    resolve_habit_display_lucide,
)
from harrix_swiss_knife.qt_lucide_icon import LUCIDE_COLOR_ORANGE


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Lucide icon painting."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_popular_habit_emojis_map_to_lucide() -> None:
    assert lucide_name_for_habit_emoji("🚶") == "footprints"
    assert lucide_name_for_habit_emoji("📚") == "library"
    assert lucide_name_for_habit_emoji("☕") == "coffee"
    assert lucide_name_for_habit_emoji("") is None


def test_habit_lucide_map_covers_presets() -> None:
    assert "🚶" in HABIT_EMOJI_TO_LUCIDE
    assert HABIT_EMOJI_TO_LUCIDE["🔥"] == "flame"


def test_resolve_habit_display_lucide_requires_explicit_id() -> None:
    """Empty Lucide means show emoji — do not auto-map at paint time."""
    assert resolve_habit_display_lucide(lucide_name="") is None
    assert resolve_habit_display_lucide(lucide_name="footprints") == "footprints"
    assert resolve_habit_display_lucide(lucide_name="not-a-real-icon") is None


def test_normalize_habit_lucide_name_rejects_unknown() -> None:
    assert normalize_habit_lucide_name("footprints") == "footprints"
    assert normalize_habit_lucide_name("nope") == ""
    assert normalize_habit_lucide_name(None) == ""


def test_habit_lucide_color_is_semantic_or_stable() -> None:
    assert habit_lucide_color("footprints") == LUCIDE_COLOR_ORANGE
    assert habit_lucide_color("flame") == HABIT_LUCIDE_COLORS["flame"]
    assert habit_lucide_color("custom-habit-a") == habit_lucide_color("custom-habit-a")
    assert habit_lucide_color("custom-habit-a") != habit_lucide_color("custom-habit-b")


def test_habit_lucide_icon_paints_known_id(qapp: QApplication) -> None:  # noqa: ARG001
    icon = habit_lucide_icon("footprints")
    assert not icon.isNull()
    assert habit_lucide_icon("").isNull()
