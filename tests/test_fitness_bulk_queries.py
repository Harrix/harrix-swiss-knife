"""Tests for the bulk fitness queries behind goal recommendations and statistics."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.fitness.database_manager import DatabaseManager
from harrix_swiss_knife.apps.fitness.progress_calculator import ExerciseProgressCalculator

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps" / "fitness" / "recover.sql"

MONTHS_COUNT = 3


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
def fitness_db(tmp_path: Path, qapp: QApplication) -> Iterator[DatabaseManager]:  # noqa: ARG001
    db_path = tmp_path / "fitness.db"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))

    db = DatabaseManager(str(db_path))
    db.execute_simple_query("DELETE FROM process")
    yield db
    db.close()


def _exercise_names(db: DatabaseManager, count: int) -> list[str]:
    rows = db.get_rows("SELECT name FROM exercises ORDER BY _id LIMIT :limit", {"limit": count})
    assert len(rows) == count
    return [str(row[0]) for row in rows]


def _today_iso() -> str:
    return datetime.now(UTC).astimezone().strftime("%Y-%m-%d")


def test_chart_data_for_all_exercises_matches_single_queries(fitness_db: DatabaseManager) -> None:
    """The bulk chart query must return the same rows as the per-exercise query."""
    first, second = _exercise_names(fitness_db, 2)
    today = _today_iso()
    month_start = f"{today[:7]}-01"

    assert fitness_db.add_process_record(_exercise_id(fitness_db, first), -1, "10", today)
    assert fitness_db.add_process_record(_exercise_id(fitness_db, first), -1, "5", today)
    assert fitness_db.add_process_record(_exercise_id(fitness_db, second), -1, "7", today)

    bulk = fitness_db.get_chart_data_for_all_exercises(month_start, today)

    assert bulk[first] == fitness_db.get_exercise_chart_data(first, None, month_start, today)
    assert bulk[second] == fitness_db.get_exercise_chart_data(second, None, month_start, today)


def test_chart_data_for_all_exercises_omits_exercises_without_rows(fitness_db: DatabaseManager) -> None:
    """Exercises with no process rows in the window must be absent from the result."""
    name = _exercise_names(fitness_db, 1)[0]
    today = _today_iso()

    bulk = fitness_db.get_chart_data_for_all_exercises(f"{today[:7]}-01", today)

    assert name not in bulk


def test_monthly_data_for_exercises_matches_single_exercise_path(fitness_db: DatabaseManager) -> None:
    """Bulk monthly data must equal the per-exercise implementation exactly."""
    first, second = _exercise_names(fitness_db, 2)
    today = _today_iso()
    assert fitness_db.add_process_record(_exercise_id(fitness_db, first), -1, "12", today)
    assert fitness_db.add_process_record(_exercise_id(fitness_db, second), -1, "3", today)

    calculator = ExerciseProgressCalculator(fitness_db)
    bulk = calculator.get_monthly_data_for_exercises([first, second], MONTHS_COUNT)

    assert bulk[first] == calculator.get_monthly_data_for_exercise(first, MONTHS_COUNT)
    assert bulk[second] == calculator.get_monthly_data_for_exercise(second, MONTHS_COUNT)
    assert len(bulk[first]) == MONTHS_COUNT


def test_monthly_data_for_exercises_accumulates_within_month(fitness_db: DatabaseManager) -> None:
    """Values on the same day must accumulate into a rising cumulative series."""
    name = _exercise_names(fitness_db, 1)[0]
    today = _today_iso()
    assert fitness_db.add_process_record(_exercise_id(fitness_db, name), -1, "10", today)
    assert fitness_db.add_process_record(_exercise_id(fitness_db, name), -1, "15", today)

    calculator = ExerciseProgressCalculator(fitness_db)
    current_month = calculator.get_monthly_data_for_exercises([name], MONTHS_COUNT)[name][0]

    assert current_month
    assert current_month[-1][1] == pytest.approx(25.0)


def test_monthly_data_for_exercises_handles_empty_inputs(fitness_db: DatabaseManager) -> None:
    """No exercise names means no work and no result rows."""
    calculator = ExerciseProgressCalculator(fitness_db)

    assert calculator.get_monthly_data_for_exercises([], MONTHS_COUNT) == {}


def test_exercise_units_matches_single_lookups(fitness_db: DatabaseManager) -> None:
    """The unit map must agree with `get_exercise_unit` for every exercise."""
    units = fitness_db.get_exercise_units()
    assert units

    for name in _exercise_names(fitness_db, 10):
        assert units[name] == fitness_db.get_exercise_unit(name)


def test_exercise_units_defaults_missing_unit_to_times(fitness_db: DatabaseManager) -> None:
    """An empty stored unit must read back as the `times` default."""
    name = _exercise_names(fitness_db, 1)[0]
    assert fitness_db.execute_simple_query(
        "UPDATE exercises SET unit = '' WHERE name = :name",
        {"name": name},
    )

    assert fitness_db.get_exercise_units()[name] == "times"
    assert fitness_db.get_exercise_unit(name) == "times"


def test_statistics_limit_matches_python_top_n(fitness_db: DatabaseManager) -> None:
    """SQL top-N per exercise/type must match sorting the full set in Python."""
    name = _exercise_names(fitness_db, 1)[0]
    ex_id = _exercise_id(fitness_db, name)
    dates = ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01", "2024-05-01", "2024-06-01"]
    values = [10, 30, 20, 50, 40, 25]
    for date_str, value in zip(dates, values, strict=True):
        assert fitness_db.add_process_record(ex_id, -1, str(value), date_str)

    limit = 3
    sql_rows = fitness_db.get_filtered_statistics_data(name, limit=limit)

    all_rows = fitness_db.get_filtered_statistics_data(name)
    grouped: dict[str, list[tuple[str, str, float, str]]] = {}
    for row in all_rows:
        key = f"{row[0]} {row[1]}".strip()
        grouped.setdefault(key, []).append(row)
    expected: list[tuple[str, str, float, str]] = []
    for rows in grouped.values():
        rows.sort(key=lambda item: (item[2], item[3]), reverse=True)
        expected.extend(rows[:limit])

    assert len(sql_rows) == limit
    assert {(row[0], row[1], row[2], row[3]) for row in sql_rows} == {
        (row[0], row[1], row[2], row[3]) for row in expected
    }
    assert sql_rows[0][2] == 50.0


def _exercise_id(db: DatabaseManager, name: str) -> int:
    rows = db.get_rows("SELECT _id FROM exercises WHERE name = :name", {"name": name})
    assert rows
    return int(rows[0][0])
