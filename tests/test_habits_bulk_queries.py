"""Tests for the bulk habits queries that replaced per-habit dashboard lookups."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.habits.database_manager import DatabaseManager

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps" / "habits" / "recover.sql"


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture
def habits_db(tmp_path: Path, qapp: QApplication) -> Iterator[DatabaseManager]:  # noqa: ARG001
    db_path = tmp_path / "habits.db"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))

    db = DatabaseManager(str(db_path))
    db.execute_simple_query("DELETE FROM process_habits")
    db.execute_simple_query("DELETE FROM habits")
    db.ensure_habits_schema()
    yield db
    db.close()


def _add_habit(db: DatabaseManager, name: str) -> int:
    assert db.add_habit(name, is_bool=True)
    rows = db.get_rows("SELECT _id FROM habits WHERE name = :name", {"name": name})
    assert rows
    return int(rows[0][0])


def _today() -> datetime:
    return datetime.now(UTC).astimezone()


def test_stats_map_matches_per_habit_queries(habits_db: DatabaseManager) -> None:
    """The bulk stats map must equal the per-habit total and streak queries."""
    today = _today().date()
    streaky = _add_habit(habits_db, "Streaky")
    gapped = _add_habit(habits_db, "Gapped")
    empty = _add_habit(habits_db, "Empty")

    for offset in range(3):
        assert habits_db.set_habit_checkin(streaky, (today - timedelta(days=offset)).isoformat(), 1)
    # A gap right before yesterday must reset the streak to zero.
    for offset in (5, 6):
        assert habits_db.set_habit_checkin(gapped, (today - timedelta(days=offset)).isoformat(), 1)

    stats = habits_db.get_habit_stats_map()

    assert stats[streaky].total_checkins == habits_db.get_habit_total_checkins(streaky)
    assert stats[streaky].streak == habits_db.get_habit_streak(streaky)
    assert stats[streaky].streak == 3
    assert stats[gapped].total_checkins == 2
    assert stats[gapped].streak == 0
    assert empty not in stats


def test_stats_map_ignores_zero_values(habits_db: DatabaseManager) -> None:
    """Only rows with value greater than zero count as check-ins."""
    today = _today().date()
    habit_id = _add_habit(habits_db, "Zeroed")
    assert habits_db.set_habit_checkin(habit_id, today.isoformat(), 0)

    assert habits_db.get_habit_stats_map().get(habit_id) is None
    assert habits_db.get_habit_total_checkins(habit_id) == 0


def test_values_between_map_matches_per_habit_queries(habits_db: DatabaseManager) -> None:
    """The bulk week map must equal `get_habit_values_between` for every habit."""
    today = _today().date()
    first = _add_habit(habits_db, "First")
    second = _add_habit(habits_db, "Second")

    assert habits_db.set_habit_checkin(first, today.isoformat(), 1)
    assert habits_db.set_habit_checkin(first, (today - timedelta(days=2)).isoformat(), 4)
    assert habits_db.set_habit_checkin(second, (today - timedelta(days=1)).isoformat(), 7)

    date_from = (today - timedelta(days=6)).isoformat()
    date_to = today.isoformat()
    bulk = habits_db.get_habit_values_between_map([first, second], date_from, date_to)

    assert bulk[first] == habits_db.get_habit_values_between(first, date_from, date_to)
    assert bulk[second] == habits_db.get_habit_values_between(second, date_from, date_to)
    assert bulk[first][(today - timedelta(days=2)).isoformat()] == 4


def test_values_between_map_excludes_dates_outside_range(habits_db: DatabaseManager) -> None:
    """Dates outside the requested range must not appear in the map."""
    today = _today().date()
    habit_id = _add_habit(habits_db, "Ranged")
    inside = (today - timedelta(days=1)).isoformat()
    outside = (today - timedelta(days=30)).isoformat()
    assert habits_db.set_habit_checkin(habit_id, inside, 1)
    assert habits_db.set_habit_checkin(habit_id, outside, 1)

    bulk = habits_db.get_habit_values_between_map(
        [habit_id], (today - timedelta(days=6)).isoformat(), today.isoformat()
    )

    assert inside in bulk[habit_id]
    assert outside not in bulk[habit_id]


def test_values_between_map_handles_empty_habit_list(habits_db: DatabaseManager) -> None:
    """An empty habit list must not build a query with an empty IN clause."""
    assert habits_db.get_habit_values_between_map([], "2024-01-01", "2024-01-07") == {}


def test_values_between_map_includes_requested_habits_without_rows(habits_db: DatabaseManager) -> None:
    """Habits with no check-ins must still be present with an empty mapping."""
    habit_id = _add_habit(habits_db, "Silent")

    bulk = habits_db.get_habit_values_between_map([habit_id], "2024-01-01", "2024-01-07")

    assert bulk == {habit_id: {}}
