"""Tests for habits emoji storage, migration, and helpers."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.habits.dashboard_widgets import HabitIconBadge
from harrix_swiss_knife.apps.habits.database_manager import DatabaseManager
from harrix_swiss_knife.apps.habits.habit_edit_dialog import HabitEditDialog
from harrix_swiss_knife.apps.habits.habit_emoji_ai import parse_habit_emoji_response
from harrix_swiss_knife.apps.habits.habit_emojis import (
    capitalize_habit_name,
    default_habit_emoji,
    normalize_habit_emoji,
)

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src/harrix_swiss_knife/apps/habits/recover.sql"

_OLD_HABITS_SCHEMA = """
CREATE TABLE "habits" (
    "_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "is_bool" INTEGER,
    "is_archived" INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY("_id" AUTOINCREMENT)
);
CREATE TABLE "process_habits" (
    "_id" INTEGER NOT NULL,
    "_id_habit" INTEGER NOT NULL,
    "value" INTEGER NOT NULL,
    "date" TEXT NOT NULL,
    PRIMARY KEY("_id" AUTOINCREMENT)
);
"""


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Qt SQL drivers."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture
def habits_db(tmp_path: Path, qapp: QApplication) -> Iterator[DatabaseManager]:  # noqa: ARG001
    """Create an empty habits SQLite database for tests."""
    db_path = tmp_path / "habits.sqlite"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))
    db = DatabaseManager(str(db_path))
    yield db
    db.close()


def test_parse_habit_emoji_response_extracts_single_emoji() -> None:
    """AI replies may wrap the emoji in fences, quotes, or extra words."""
    assert parse_habit_emoji_response("🏃") == "🏃"
    assert parse_habit_emoji_response("```\n💧\n```") == "💧"
    assert parse_habit_emoji_response('Emoji: "📚"') == "📚"
    assert parse_habit_emoji_response("no emoji here") == ""


def test_habit_edit_ai_emoji_button_requires_name(qapp: QApplication) -> None:
    """The AI emoji button stays disabled until a habit name is entered."""
    assert qapp is not None
    dialog = HabitEditDialog(app_config={})
    assert not dialog._ai_emoji_button.isEnabled()
    dialog._name_edit.setText("Walk")
    assert dialog._ai_emoji_button.isEnabled()
    dialog._name_edit.clear()
    assert not dialog._ai_emoji_button.isEnabled()

    named = HabitEditDialog(name="Read", app_config={})
    assert named._ai_emoji_button.isEnabled()


def test_default_habit_emoji_is_stable() -> None:
    """Preset emoji for a habit ID stays deterministic."""
    assert default_habit_emoji(1) == default_habit_emoji(1)
    assert normalize_habit_emoji("") == default_habit_emoji(0)
    assert normalize_habit_emoji(" 🏃 ", habit_id=1) == "🏃"


def test_capitalize_habit_name() -> None:
    """First letter is uppercased; the rest of the name is unchanged."""
    assert capitalize_habit_name("") == ""
    assert capitalize_habit_name("   ") == ""
    assert capitalize_habit_name("бегать") == "Бегать"
    assert capitalize_habit_name("бегать утром") == "Бегать утром"
    assert capitalize_habit_name("Walk") == "Walk"
    assert capitalize_habit_name("  walk") == "Walk"


def test_habit_edit_dialog_capitalizes_name(qapp: QApplication) -> None:
    """Create/edit dialog returns a habit name with the first letter capitalized."""
    assert qapp is not None
    dialog = HabitEditDialog(app_config={})
    dialog._name_edit.setText("бегать утром")
    assert dialog.habit_name() == "Бегать утром"


def test_add_habit_capitalizes_lowercase_name(habits_db: DatabaseManager) -> None:
    """Insert stores the habit name with the first letter capitalized."""
    assert habits_db.add_habit("бегать", is_bool=True)
    row = habits_db.get_habits()[0]
    assert row[1] == "Бегать"


def test_update_habit_capitalizes_lowercase_name(habits_db: DatabaseManager) -> None:
    """Update stores the habit name with the first letter capitalized."""
    assert habits_db.add_habit("Walk", is_bool=True)
    habit_id = int(habits_db.get_habits()[0][0])
    assert habits_db.update_habit(habit_id, "читать", is_bool=True)
    updated = habits_db.get_habit_by_id(habit_id)
    assert updated is not None
    assert updated[1] == "Читать"


def test_add_habit_with_emoji(habits_db: DatabaseManager) -> None:
    """Insert stores the provided emoji and returns it in getters."""
    assert habits_db.add_habit("Walk", is_bool=True, emoji="🚶")
    row = habits_db.get_habits()[0]
    assert len(row) == 5
    assert row[1] == "Walk"
    assert row[4] == "🚶"
    by_id = habits_db.get_habit_by_id(int(row[0]))
    assert by_id is not None
    assert by_id[4] == "🚶"


def test_add_habit_assigns_default_emoji_when_empty(habits_db: DatabaseManager) -> None:
    """Empty emoji is replaced with a stable preset after insert."""
    assert habits_db.add_habit("Read", is_bool=True)
    row = habits_db.get_habits()[0]
    habit_id = int(row[0])
    assert row[4] == default_habit_emoji(habit_id)


def test_update_habit_emoji(habits_db: DatabaseManager) -> None:
    """Update can change the habit emoji."""
    assert habits_db.add_habit("Meditate", is_bool=True, emoji="🧘")
    habit_id = int(habits_db.get_habits()[0][0])
    assert habits_db.update_habit(habit_id, "Meditate", is_bool=True, emoji="💤")
    updated = habits_db.get_habit_by_id(habit_id)
    assert updated is not None
    assert updated[4] == "💤"


def test_ensure_habits_schema_adds_and_backfills_emoji(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    """Migration adds emoji column and fills existing habits."""
    sql_path = tmp_path / "old_habits.sql"
    sql_path.write_text(_OLD_HABITS_SCHEMA, encoding="utf-8")
    db_path = tmp_path / "old_habits.sqlite"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(sql_path))
    db = DatabaseManager(str(db_path))
    try:
        assert db.execute_simple_query(
            "INSERT INTO habits (name, is_bool, is_archived) VALUES (:name, :is_bool, :is_archived)",
            {"name": "Old Habit", "is_bool": 1, "is_archived": 0},
        )
        assert db.ensure_habits_schema()
        cols = {str(row[1]) for row in db.get_rows("PRAGMA table_info(habits)") if len(row) > 1}
        assert "emoji" in cols
        row = db.get_habits()[0]
        habit_id = int(row[0])
        assert row[4] == default_habit_emoji(habit_id)
    finally:
        db.close()


def _render_habit_icon_badge(emoji: str) -> QImage:
    badge = HabitIconBadge(size=40)
    badge.set_habit(1, emoji)
    image = QImage(40, 40, QImage.Format.Format_ARGB32)
    image.fill(0)
    badge.render(image)
    return image


@pytest.mark.skipif(
    os.environ.get("QT_QPA_PLATFORM", "").startswith("offscreen"),
    reason="offscreen QPA does not paint emoji fonts",
)
def test_habit_icon_badge_paints_centered_emoji(qapp: QApplication) -> None:
    """List badge draws the habit emoji instead of an empty colored circle."""
    assert qapp is not None
    runner = _render_habit_icon_badge("🏃")
    syringe = _render_habit_icon_badge("💉")
    assert runner != syringe
