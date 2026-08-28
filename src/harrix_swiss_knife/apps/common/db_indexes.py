"""Create SQLite lookup indexes for tracker databases before the app opens them."""

from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_sqlite_indexes(db_path: Path, statements: Sequence[str], *, label: str) -> bool:
    """Run `CREATE INDEX IF NOT EXISTS` statements, skipping ones whose table is absent.

    Without these indexes every `WHERE column = ?` lookup is a full table scan, which
    dominates once a tracker table grows to tens of thousands of rows.

    Each statement must be of the form `CREATE INDEX IF NOT EXISTS name ON table(...)`
    so the index and table names can be read back from the statement itself.

    Args:

    - `db_path` (`Path`): Path to the SQLite file.
    - `statements` (`Sequence[str]`): Index statements to apply.
    - `label` (`str`): App name used in the log message.

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
        for statement in statements:
            index_name = statement.split(" ON ", 1)[0].rsplit(" ", 1)[-1]
            if index_name in existing:
                continue
            table = statement.split(" ON ", 1)[1].split("(", 1)[0].strip()
            if not table_exists(conn, table):
                continue
            conn.execute(statement)
            created = True
        if created:
            conn.commit()
            logger.info("Created %s lookup indexes in %s", label, db_path)
    return created


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    """Return whether `table` exists in the database behind `conn`.

    Args:

    - `conn` (`sqlite3.Connection`): Open connection.
    - `table` (`str`): Table name to check.

    Returns:

    - `bool`: `True` when the table exists.

    """
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None
