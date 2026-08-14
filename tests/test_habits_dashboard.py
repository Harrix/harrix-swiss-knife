"""Tests for habits dashboard database helpers (streak / toggle)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.habits.dashboard_widgets import CheckCircle, HabitRow, MonthCalendarGrid, habit_day_state
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


def test_habit_day_state_mapping() -> None:
    """Map missing, zero, one, and other integers to dashboard states."""
    assert habit_day_state(None) == "absent"
    assert habit_day_state(0) == "zero"
    assert habit_day_state(1) == "one"
    assert habit_day_state(2) == "number"
    assert habit_day_state(15) == "number"
    assert habit_day_state(-3) == "number"


def test_get_habit_value_on_date_and_values_between(habits_db: DatabaseManager) -> None:
    """Distinguish no row, stored 0, stored 1, and other numeric values."""
    assert habits_db.add_habit("Push-ups", is_bool=False)
    habit_id = int(habits_db.get_habits()[0][0])
    today = _local_today()
    day_one = today.isoformat()
    day_zero = (today - timedelta(days=1)).isoformat()
    day_number = (today - timedelta(days=2)).isoformat()
    day_absent = (today - timedelta(days=3)).isoformat()

    assert habits_db.add_process_habit_record(habit_id, 1, day_one)
    assert habits_db.add_process_habit_record(habit_id, 0, day_zero)
    assert habits_db.add_process_habit_record(habit_id, 12, day_number)

    assert habits_db.get_habit_value_on_date(habit_id, day_one) == 1
    assert habits_db.get_habit_value_on_date(habit_id, day_zero) == 0
    assert habits_db.get_habit_value_on_date(habit_id, day_number) == 12
    assert habits_db.get_habit_value_on_date(habit_id, day_absent) is None

    values = habits_db.get_habit_values_between(habit_id, day_absent, day_one)
    assert values[day_one] == 1
    assert values[day_zero] == 0
    assert values[day_number] == 12
    assert day_absent not in values

    assert habits_db.is_habit_done_on_date(habit_id, day_one)
    assert not habits_db.is_habit_done_on_date(habit_id, day_zero)
    assert habits_db.is_habit_done_on_date(habit_id, day_number)
    assert not habits_db.is_habit_done_on_date(habit_id, day_absent)


def test_check_circle_four_states(qapp: QApplication) -> None:
    """CheckCircle shows absent, zero, completed, and numeric states."""
    assert qapp is not None
    circle = CheckCircle()
    assert circle.day_state() == "absent"
    assert circle.toolTip() == "No record"
    assert not circle.is_done()
    assert circle.value() is None

    circle.set_value(0)
    assert circle.day_state() == "zero"
    assert circle.toolTip() == "Not completed (0)"
    assert not circle.is_done()

    circle.set_value(1)
    assert circle.day_state() == "one"
    assert circle.toolTip() == "Completed"
    assert circle.is_done()

    circle.set_value(8)
    assert circle.day_state() == "number"
    assert circle.toolTip() == "Value: 8"
    assert circle.is_done()
    assert circle.value() == 8


def test_set_habit_checkin_four_kinds(habits_db: DatabaseManager) -> None:
    """Set no record, 0, 1, and a numeric value for a habit day."""
    assert habits_db.add_habit("Push-ups", is_bool=False)
    habit_id = int(habits_db.get_habits()[0][0])
    day = _local_today().isoformat()

    assert habits_db.set_habit_checkin(habit_id, day, None)
    assert habits_db.get_habit_value_on_date(habit_id, day) is None

    assert habits_db.set_habit_checkin(habit_id, day, 0)
    assert habits_db.get_habit_value_on_date(habit_id, day) == 0
    assert not habits_db.is_habit_done_on_date(habit_id, day)

    assert habits_db.set_habit_checkin(habit_id, day, 1)
    assert habits_db.get_habit_value_on_date(habit_id, day) == 1
    assert habits_db.is_habit_done_on_date(habit_id, day)

    assert habits_db.set_habit_checkin(habit_id, day, 15)
    assert habits_db.get_habit_value_on_date(habit_id, day) == 15
    assert habits_db.is_habit_done_on_date(habit_id, day)

    assert habits_db.set_habit_checkin(habit_id, day, None)
    assert habits_db.get_habit_value_on_date(habit_id, day) is None
    assert not habits_db.is_habit_done_on_date(habit_id, day)


def test_habit_row_day_value_set_signal(qapp: QApplication) -> None:
    """Week circles forward context-menu values, including None."""
    assert qapp is not None
    row = HabitRow()
    row.set_habit_data(7, "Walk", 0, 0, [None] * 7, selected=False, allows_number=True)
    received: list[tuple[int, int, object]] = []
    row.day_value_set.connect(lambda hid, idx, val: received.append((hid, idx, val)))

    circles = row.findChildren(CheckCircle)
    assert len(circles) == 7
    assert all(circle.allows_number() for circle in circles)
    circles[3].value_set.emit(12)
    circles[0].value_set.emit(None)
    assert received == [(7, 3, 12), (7, 0, None)]

    row.set_habit_data(7, "Walk", 0, 0, [None] * 7, selected=False, allows_number=False)
    assert all(not circle.allows_number() for circle in row.findChildren(CheckCircle))


def test_month_calendar_day_value_set_signal(qapp: QApplication) -> None:
    """Month circles forward context-menu values for the selected date."""
    assert qapp is not None
    grid = MonthCalendarGrid()
    grid.set_month(2026, 8, {"2026-08-14": 1}, allows_number=True)
    received: list[tuple[str, object]] = []
    grid.day_value_set.connect(lambda date_str, val: received.append((date_str, val)))

    matches = [circle for circle in grid.findChildren(CheckCircle) if circle.value() == 1]
    assert len(matches) == 1
    assert matches[0].allows_number()
    matches[0].value_set.emit(4)

    assert received == [("2026-08-14", 4)]
