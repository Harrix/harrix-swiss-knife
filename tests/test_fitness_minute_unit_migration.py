"""Tests for converting minute exercise units to seconds."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from harrix_swiss_knife.apps.fitness.lightbox_logic import is_minute_exercise_unit
from harrix_swiss_knife.apps.fitness.schema import migrate_minute_exercise_units_to_seconds


def test_is_minute_exercise_unit_ignores_meters() -> None:
    assert is_minute_exercise_unit("min")
    assert is_minute_exercise_unit("min.")
    assert is_minute_exercise_unit("Minutes")
    assert not is_minute_exercise_unit("m")
    assert not is_minute_exercise_unit("sec.")
    assert not is_minute_exercise_unit("km")


def test_migrate_minute_exercise_units_to_seconds(tmp_path: Path) -> None:
    db_path = tmp_path / "fitness.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(
            """
            CREATE TABLE exercises (
                _id INTEGER PRIMARY KEY,
                name TEXT,
                unit TEXT,
                calories_per_unit REAL
            );
            CREATE TABLE process (
                _id INTEGER PRIMARY KEY,
                _id_exercises INTEGER,
                value TEXT
            );
            CREATE TABLE workout_items (
                _id INTEGER PRIMARY KEY,
                workout_id INTEGER,
                _id_exercises INTEGER,
                _id_types INTEGER,
                exercise_name TEXT,
                type_name TEXT,
                target_value TEXT
            );
            INSERT INTO exercises VALUES
                (1, 'Running', 'min.', 8.0),
                (2, 'Plank', 'sec.', 0.1),
                (3, 'Walking', 'm', 0.05),
                (4, 'Stretch', 'min', 2.5);
            INSERT INTO process VALUES
                (10, 1, '30'),
                (11, 2, '45'),
                (12, 3, '1000'),
                (13, 4, '2');
            INSERT INTO workout_items
                (_id, workout_id, _id_exercises, _id_types, exercise_name, type_name, target_value)
            VALUES
                (20, 1, 1, -1, 'Running', '', '10'),
                (21, 1, 2, -1, 'Plank', '', '60');
            """
        )
        conn.commit()

    assert migrate_minute_exercise_units_to_seconds(db_path) == 2
    assert migrate_minute_exercise_units_to_seconds(db_path) == 0

    with sqlite3.connect(str(db_path)) as conn:
        exercises = {
            row[0]: (row[1], row[2], row[3])
            for row in conn.execute("SELECT _id, name, unit, calories_per_unit FROM exercises")
        }
        assert exercises[1][0] == "Running"
        assert exercises[1][1] == "sec."
        assert exercises[1][2] == pytest.approx(8.0 / 60)
        assert exercises[2] == ("Plank", "sec.", 0.1)
        assert exercises[3] == ("Walking", "m", 0.05)
        assert exercises[4][1] == "sec."
        assert exercises[4][2] == pytest.approx(2.5 / 60)

        values = dict(conn.execute("SELECT _id, value FROM process"))
        assert values[10] == "1800"
        assert values[11] == "45"
        assert values[12] == "1000"
        assert values[13] == "120"

        targets = dict(conn.execute("SELECT _id, target_value FROM workout_items"))
        assert targets[20] == "600"
        assert targets[21] == "60"
