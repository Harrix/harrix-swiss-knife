"""Ensure Fitness SQLite schema includes workout tables on existing databases."""

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
