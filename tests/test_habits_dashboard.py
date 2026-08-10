"""Tests for habits dashboard database helpers (streak / toggle)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.habits.database_manager import DatabaseManager

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src/harrix_swiss_knife/apps/habits/recover.sql"


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


def _local_today() -> date:
    return datetime.now(UTC).astimezone().date()


def test_toggle_habit_checkin_and_total(habits_db: DatabaseManager) -> None:
    """Toggle inserts then removes a check-in and updates totals."""
    assert habits_db.add_habit("Walk", is_bool=True)
    habit_id = int(habits_db.get_habits()[0][0])
    today = _local_today().isoformat()

    assert habits_db.toggle_habit_checkin(habit_id, today)
    assert habits_db.is_habit_done_on_date(habit_id, today)
    assert habits_db.get_habit_total_checkins(habit_id) == 1

    assert habits_db.toggle_habit_checkin(habit_id, today)
    assert not habits_db.is_habit_done_on_date(habit_id, today)
    assert habits_db.get_habit_total_checkins(habit_id) == 0


def test_habit_streak_counts_consecutive_days(habits_db: DatabaseManager) -> None:
    """Streak counts consecutive completed days ending today or yesterday."""
    assert habits_db.add_habit("Read", is_bool=True)
    habit_id = int(habits_db.get_habits()[0][0])
    today = _local_today()

    for offset in range(3):
        day = (today - timedelta(days=offset)).isoformat()
        assert habits_db.add_process_habit_record(habit_id, 1, day)

    assert habits_db.get_habit_streak(habit_id) == 3

    # Gap yesterday breaks streak when today is also missing after we clear today
    assert habits_db.toggle_habit_checkin(habit_id, today.isoformat())  # uncheck today
    # Still 2 if yesterday and day-2 are done (grace: start from yesterday)
    assert habits_db.get_habit_streak(habit_id) == 2
