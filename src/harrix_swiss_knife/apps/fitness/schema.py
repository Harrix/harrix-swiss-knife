"""Ensure Fitness SQLite schema includes workout tables and lookup indexes."""

from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.db_indexes import ensure_sqlite_indexes, table_exists
from harrix_swiss_knife.apps.fitness.lightbox_logic import is_minute_exercise_unit

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

_SECONDS_UNIT = "sec."
_SECONDS_PER_MINUTE = 60

_WORKOUTS_SQL = """
CREATE TABLE IF NOT EXISTS workouts (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gender TEXT NOT NULL,
    duration_min INTEGER NOT NULL,
    created_date TEXT NOT NULL,
    notes TEXT
)
"""

_WORKOUT_ITEMS_SQL = """
CREATE TABLE IF NOT EXISTS workout_items (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    _id_exercises INTEGER NOT NULL,
    _id_types INTEGER NOT NULL,
    exercise_name TEXT NOT NULL,
    type_name TEXT,
    target_value TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_done INTEGER NOT NULL DEFAULT 0 CHECK (is_done IN (0, 1)),
    process_id INTEGER,
    FOREIGN KEY (workout_id) REFERENCES workouts(_id)
)
"""


_INDEX_SQL: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_process_exercise ON process(_id_exercises)",
    "CREATE INDEX IF NOT EXISTS idx_process_exercise_date ON process(_id_exercises, date)",
    "CREATE INDEX IF NOT EXISTS idx_process_date ON process(date)",
    "CREATE INDEX IF NOT EXISTS idx_process_type ON process(_id_types)",
    "CREATE INDEX IF NOT EXISTS idx_types_exercise ON types(_id_exercises)",
    "CREATE INDEX IF NOT EXISTS idx_exercises_name ON exercises(name)",
    "CREATE INDEX IF NOT EXISTS idx_weight_date ON weight(date)",
    "CREATE INDEX IF NOT EXISTS idx_workout_items_workout ON workout_items(workout_id)",
)


def ensure_fitness_indexes(db_path: Path) -> bool:
    """Create lookup indexes used by per-exercise queries.

    Args:

    - `db_path` (`Path`): Path to `fitness.db`.

    Returns:

    - `bool`: `True` when at least one index was created.

    """
    return ensure_sqlite_indexes(db_path, _INDEX_SQL, label="Fitness")


def ensure_fitness_schema(db_path: Path) -> bool:
    """Create `workouts` / `workout_items` when they are missing.

    Args:

    - `db_path` (`Path`): Path to `fitness.db`.

    Returns:

    - `bool`: `True` when tables were created, `False` when unchanged or skipped.

    """
    if not db_path.is_file():
        return False

    with sqlite3.connect(str(db_path)) as conn:
        if not table_exists(conn, "process") or not table_exists(conn, "exercises"):
            return False
        if table_exists(conn, "workouts") and table_exists(conn, "workout_items"):
            return False
        conn.executescript(f"{_WORKOUTS_SQL}; {_WORKOUT_ITEMS_SQL};")
        conn.commit()
        logger.info("Created Fitness workout tables in %s", db_path)
        return True


def migrate_minute_exercise_units_to_seconds(db_path: Path) -> int:
    """Convert exercise units stored in minutes to seconds (idempotent).

    For every exercise whose unit is minutes (`min`, `min.`, …):

    - set unit to `sec.`
    - divide `calories_per_unit` by 60
    - multiply `process.value` and `workout_items.target_value` by 60

    Safe to run on every app open: already-converted exercises are skipped.
    Distance unit `m` (meters) is not treated as minutes.

    Args:

    - `db_path` (`Path`): Path to `fitness.db`.

    Returns:

    - `int`: Number of exercises converted.

    """
    if not db_path.is_file():
        return 0

    with sqlite3.connect(str(db_path)) as conn:
        if not table_exists(conn, "exercises") or not table_exists(conn, "process"):
            return 0

        exercise_rows = conn.execute("SELECT _id, unit, calories_per_unit FROM exercises").fetchall()
        minute_exercises: list[tuple[int, float]] = []
        for exercise_id, unit, calories_per_unit in exercise_rows:
            if not is_minute_exercise_unit(str(unit or "")):
                continue
            try:
                calories = float(calories_per_unit or 0)
            except (TypeError, ValueError):
                calories = 0.0
            minute_exercises.append((int(exercise_id), calories))

        if not minute_exercises:
            return 0

        exercise_ids = [exercise_id for exercise_id, _calories in minute_exercises]
        placeholders = ",".join("?" * len(exercise_ids))

        for exercise_id, calories in minute_exercises:
            conn.execute(
                "UPDATE exercises SET unit = ?, calories_per_unit = ? WHERE _id = ?",
                (_SECONDS_UNIT, calories / _SECONDS_PER_MINUTE, exercise_id),
            )

        process_rows = conn.execute(
            f"SELECT _id, value FROM process WHERE _id_exercises IN ({placeholders})",
            exercise_ids,
        ).fetchall()
        for process_id, value in process_rows:
            scaled = _scale_minutes_value_to_seconds(value)
            if scaled is None:
                continue
            conn.execute("UPDATE process SET value = ? WHERE _id = ?", (scaled, process_id))

        if table_exists(conn, "workout_items"):
            item_rows = conn.execute(
                f"SELECT _id, target_value FROM workout_items WHERE _id_exercises IN ({placeholders})",
                exercise_ids,
            ).fetchall()
            for item_id, target_value in item_rows:
                scaled = _scale_minutes_value_to_seconds(target_value)
                if scaled is None:
                    continue
                conn.execute(
                    "UPDATE workout_items SET target_value = ? WHERE _id = ?",
                    (scaled, item_id),
                )

        conn.commit()
        logger.info(
            "Converted %s minute-unit exercise(s) to seconds in %s",
            len(minute_exercises),
            db_path,
        )
        return len(minute_exercises)


def _scale_minutes_value_to_seconds(raw: object) -> str | None:
    """Multiply a stored minute quantity by 60; return `None` when not numeric."""
    text = str(raw or "").strip()
    if not text:
        return None
    try:
        amount = float(text.replace(",", "."))
    except ValueError:
        return None
    scaled = amount * _SECONDS_PER_MINUTE
    if scaled == int(scaled):
        return str(int(scaled))
    return str(scaled)
