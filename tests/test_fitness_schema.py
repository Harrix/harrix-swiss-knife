"""Tests for Fitness workout-table schema migration."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from harrix_swiss_knife.apps.fitness.schema import ensure_fitness_schema


def test_ensure_fitness_schema_creates_workout_tables(tmp_path: Path) -> None:
    """Existing process/exercises DBs gain workouts tables."""
    db_path = tmp_path / "fitness.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(
            """
            CREATE TABLE exercises (_id INTEGER PRIMARY KEY, name TEXT);
            CREATE TABLE process (
                _id INTEGER PRIMARY KEY,
                _id_exercises INTEGER,
                _id_types INTEGER,
                value TEXT,
                date TEXT
            );
            """
        )
        conn.commit()

    assert ensure_fitness_schema(db_path) is True
    assert ensure_fitness_schema(db_path) is False

    with sqlite3.connect(str(db_path)) as conn:
        names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "workouts" in names
        assert "workout_items" in names
        cols = {row[1] for row in conn.execute("PRAGMA table_info(workouts)")}
        assert {"_id", "name", "gender", "duration_min", "created_date"}.issubset(cols)
