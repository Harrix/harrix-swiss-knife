"""Ensure Fitness SQLite schema includes workout tables and lookup indexes."""

from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.db_indexes import ensure_sqlite_indexes, table_exists

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

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
