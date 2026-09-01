"""Tests for the bulk goal-info path of `ExerciseProgressCalculator`."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

from harrix_swiss_knife.apps.fitness.progress_calculator import ExerciseProgressCalculator

if TYPE_CHECKING:
    from pathlib import Path

    from harrix_swiss_knife.apps.fitness.database_manager import DatabaseManager

_SCHEMA = """
CREATE TABLE exercises (_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, unit TEXT);
CREATE TABLE types (_id INTEGER PRIMARY KEY AUTOINCREMENT, _id_exercises INTEGER NOT NULL, type TEXT NOT NULL);
CREATE TABLE process (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    _id_exercises INTEGER NOT NULL,
    _id_types INTEGER NOT NULL,
    value TEXT NOT NULL,
    date TEXT NOT NULL
);
"""


class _SqliteDatabaseManager:
    """Minimal stand-in for `DatabaseManager` backed by plain sqlite3."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get_exercise_chart_data(
        self,
        exercise_name: str,
        exercise_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[tuple[str, str]]:
        conditions = ["e.name = :exercise"]
        params: dict[str, Any] = {"exercise": exercise_name}
        if date_from and date_to:
            conditions.append("p.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to
        if exercise_type and exercise_type != "All types":
            conditions.append("t.type = :type")
            params["type"] = exercise_type
        rows = self.connection.execute(
            f"""
            SELECT p.date, p.value
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            WHERE {" AND ".join(conditions)}
            ORDER BY p.date ASC
            """,
            params,
        ).fetchall()
        return [(row[0], row[1]) for row in rows]

    def get_exercise_total_today(self, exercise_id: int) -> float:
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        row = self.connection.execute(
            "SELECT SUM(CAST(value AS REAL)) FROM process WHERE _id_exercises = :ex_id AND date = :today",
            {"ex_id": exercise_id, "today": today},
        ).fetchone()
        return float(row[0]) if row and row[0] is not None else 0.0

    def get_id(self, table: str, name_column: str, name_value: str) -> int | None:
        row = self.connection.execute(
            f"SELECT _id FROM {table} WHERE {name_column} = ?",
            (name_value,),
        ).fetchone()
        return int(row[0]) if row else None

    def get_monthly_totals_by_exercise(self, date_from: str, date_to: str) -> list[tuple[str, str, float]]:
        rows = self.connection.execute(
            """
            SELECT e.name, SUBSTR(p.date, 1, 7) AS month_key, SUM(CAST(p.value AS REAL))
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            WHERE p.date BETWEEN :date_from AND :date_to
            GROUP BY e.name, month_key
            """,
            {"date_from": date_from, "date_to": date_to},
        ).fetchall()
        return [(str(row[0]), str(row[1]), float(row[2] or 0.0)) for row in rows]

    def get_totals_by_exercise_for_date(self, date: str) -> dict[str, float]:
        rows = self.connection.execute(
            """
            SELECT e.name, SUM(CAST(value AS REAL))
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            WHERE p.date = :date
            GROUP BY e.name
            """,
            {"date": date},
        ).fetchall()
        return {str(row[0]): float(row[1] or 0.0) for row in rows}


def _build_db(tmp_path: Path) -> _SqliteDatabaseManager:
    connection = sqlite3.connect(tmp_path / "fitness.db")
    connection.executescript(_SCHEMA)

    today = datetime.now(UTC).astimezone()
    exercises = ["Push ups", "Running", "Untouched", "Only today"]
    for name in exercises:
        connection.execute("INSERT INTO exercises (name, unit) VALUES (?, 'times')", (name,))
        exercise_id = connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        connection.execute("INSERT INTO types (_id_exercises, type) VALUES (?, 'Default')", (exercise_id,))

    def add(name: str, date: str, value: str) -> None:
        exercise_id = connection.execute("SELECT _id FROM exercises WHERE name = ?", (name,)).fetchone()[0]
        type_id = connection.execute(
            "SELECT _id FROM types WHERE _id_exercises = ?",
            (exercise_id,),
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO process (_id_exercises, _id_types, value, date) VALUES (?, ?, ?, ?)",
            (exercise_id, type_id, value, date),
        )

    today_str = today.strftime("%Y-%m-%d")
    month_start = today.strftime("%Y-%m-01")
    # A strong previous month sets the goal, the current month is behind it.
    previous_month = today.month - 1 or 12
    previous_year = today.year if today.month > 1 else today.year - 1
    previous_str = f"{previous_year:04d}-{previous_month:02d}-05"

    add("Push ups", previous_str, "500")
    if month_start != today_str:
        add("Push ups", month_start, "40")
    add("Push ups", today_str, "10")

    add("Running", previous_str, "20")
    add("Running", month_start, "900")
    add("Running", today_str, "5")

    add("Only today", today_str, "7")

    connection.commit()
    return _SqliteDatabaseManager(connection)


def _build_calculator(tmp_path: Path) -> tuple[ExerciseProgressCalculator, _SqliteDatabaseManager]:
    db_manager = _build_db(tmp_path)
    return ExerciseProgressCalculator(cast("DatabaseManager", db_manager)), db_manager


def test_goal_info_map_matches_per_exercise_calls(tmp_path: Path) -> None:
    calculator, db_manager = _build_calculator(tmp_path)
    months_count = 12

    bulk = calculator.get_today_goal_info_map(months_count)
    names = [row[0] for row in db_manager.connection.execute("SELECT name FROM exercises")]

    expected = {name: calculator.get_today_goal_info(name, months_count) for name in names}
    expected = {name: label for name, label in expected.items() if label}

    assert bulk == expected


def test_goal_info_map_skips_exercises_without_records(tmp_path: Path) -> None:
    calculator, _db_manager = _build_calculator(tmp_path)

    bulk = calculator.get_today_goal_info_map(12)

    assert "Untouched" not in bulk
    assert bulk["Push ups"].startswith("(+")


def test_goal_info_map_returns_empty_for_non_positive_months(tmp_path: Path) -> None:
    calculator, _db_manager = _build_calculator(tmp_path)

    assert calculator.get_today_goal_info_map(0) == {}
