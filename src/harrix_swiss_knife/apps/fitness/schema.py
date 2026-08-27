"""Ensure Fitness SQLite schema includes workout tables and lookup indexes."""

from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING

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

    Without these, every `WHERE _id_exercises = ?` or `WHERE name = ?` lookup is a
    full table scan, which dominates startup once the catalog grows.

    Args:

    - `db_path` (`Path`): Path to `fitness.db`.

    Returns:

    - `bool`: `True` when at least one index was created.

    """
    if not db_path.is_file():
        return False

    created = False
    with sqlite3.connect(str(db_path)) as conn:
        existing = {
            str(row[0]) for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'") if row[0]
        }
        for statement in _INDEX_SQL:
            index_name = statement.split(" ON ", 1)[0].rsplit(" ", 1)[-1]
            if index_name in existing:
                continue
            table = statement.split(" ON ", 1)[1].split("(", 1)[0].strip()
            if not _table_exists(conn, table):
                continue
            conn.execute(statement)
            created = True
        if created:
            conn.commit()
            logger.info("Created Fitness lookup indexes in %s", db_path)
    return created


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
        if not _table_exists(conn, "process") or not _table_exists(conn, "exercises"):
            return False
        if _table_exists(conn, "workouts") and _table_exists(conn, "workout_items"):
            return False
        conn.executescript(f"{_WORKOUTS_SQL}; {_WORKOUT_ITEMS_SQL};")
        conn.commit()
        logger.info("Created Fitness workout tables in %s", db_path)
        return True


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None
