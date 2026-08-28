"""Ensure Habits SQLite schema includes the lookup indexes used by check-in queries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.db_indexes import ensure_sqlite_indexes

if TYPE_CHECKING:
    from pathlib import Path

_INDEX_SQL: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_process_habits_habit_date ON process_habits(_id_habit, date)",
    "CREATE INDEX IF NOT EXISTS idx_process_habits_date ON process_habits(date)",
)


def ensure_habits_indexes(db_path: Path) -> bool:
    """Create lookup indexes for `process_habits`, which every dashboard query filters on.

    Args:

    - `db_path` (`Path`): Path to `habits.db`.

    Returns:

    - `bool`: `True` when at least one index was created.

    """
    return ensure_sqlite_indexes(db_path, _INDEX_SQL, label="Habits")
