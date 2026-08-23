"""Ensure Food SQLite schema matches the columns used by the Food app."""

from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

_CURRENT_FOOD_ITEMS_SQL = """
CREATE TABLE food_items (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_en TEXT,
    is_drink INTEGER NOT NULL DEFAULT 0 CHECK (is_drink IN (0, 1)),
    calories_per_100g REAL,
    default_portion_weight REAL,
    default_portion_calories REAL
)
"""

_CURRENT_FOOD_LOG_SQL = """
CREATE TABLE food_log (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    weight REAL,
    portion_calories REAL,
    calories_per_100g REAL,
    name TEXT,
    name_en TEXT,
    is_drink INTEGER NOT NULL DEFAULT 0 CHECK (is_drink IN (0, 1))
)
"""


def ensure_food_schema(db_path: Path) -> bool:
    """Migrate a legacy Food database to the current schema when needed.

    Legacy `recover.sql` used `id` / `datetime` / `calories` / `food_item_id`. The app
    expects `_id` / `date` / `portion_calories` / `calories_per_100g` on denormalized
    `food_log` rows. Fresh installs after updating `recover.sql` already match and are
    left untouched.

    Args:

    - `db_path` (`Path`): Path to `food.db`.

    Returns:

    - `bool`: `True` when a migration ran, `False` when the schema was already current.

    """
    if not db_path.is_file():
        return False

    with sqlite3.connect(str(db_path)) as conn:
        if not _table_exists(conn, "food_log") or not _table_exists(conn, "food_items"):
            return False
        if _is_current_schema(conn):
            return False

        logger.info("Migrating legacy Food schema in %s", db_path)
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("ALTER TABLE food_items RENAME TO food_items_legacy")
        conn.execute("ALTER TABLE food_log RENAME TO food_log_legacy")
        conn.executescript(f"{_CURRENT_FOOD_ITEMS_SQL}; {_CURRENT_FOOD_LOG_SQL};")

        item_cols = _column_names(conn, "food_items_legacy")
        id_col = "_id" if "_id" in item_cols else "id"
        conn.execute(
            f"""
            INSERT INTO food_items (
                _id, name, name_en, is_drink, calories_per_100g,
                default_portion_weight, default_portion_calories
            )
            SELECT
                {id_col},
                name,
                name_en,
                COALESCE(is_drink, 0),
                calories_per_100g,
                default_portion_weight,
                default_portion_calories
            FROM food_items_legacy
            """
        )

        log_cols = _column_names(conn, "food_log_legacy")
        log_id = "_id" if "_id" in log_cols else "id"
        date_expr = _legacy_date_expression(log_cols)
        weight_expr = "weight" if "weight" in log_cols else "NULL"
        portion_expr = _legacy_portion_calories_expression(log_cols)
        per_100_expr = "calories_per_100g" if "calories_per_100g" in log_cols else "NULL"
        name_expr = "name" if "name" in log_cols else "NULL"
        name_en_expr = "name_en" if "name_en" in log_cols else "NULL"
        is_drink_expr = "COALESCE(is_drink, 0)" if "is_drink" in log_cols else "0"

        conn.execute(
            f"""
            INSERT INTO food_log (
                _id, date, weight, portion_calories, calories_per_100g, name, name_en, is_drink
            )
            SELECT
                {log_id},
                {date_expr},
                {weight_expr},
                {portion_expr},
                {per_100_expr},
                {name_expr},
                {name_en_expr},
                {is_drink_expr}
            FROM food_log_legacy
            """
        )

        conn.execute("DROP TABLE food_log_legacy")
        conn.execute("DROP TABLE food_items_legacy")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
        logger.info("Food schema migration finished for %s", db_path)
        return True


def _column_names(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {str(row[1]) for row in rows}


def _is_current_schema(conn: sqlite3.Connection) -> bool:
    items = _column_names(conn, "food_items")
    log = _column_names(conn, "food_log")
    required_items = {"_id", "name", "is_drink", "calories_per_100g"}
    required_log = {"_id", "date", "portion_calories", "calories_per_100g", "name", "is_drink"}
    return required_items.issubset(items) and required_log.issubset(log)


def _legacy_date_expression(columns: set[str]) -> str:
    if "date" in columns:
        return "date"
    if "datetime" in columns:
        return "CASE WHEN length(datetime) >= 10 THEN substr(datetime, 1, 10) ELSE datetime END"
    return "NULL"


def _legacy_portion_calories_expression(columns: set[str]) -> str:
    if "portion_calories" in columns:
        return "portion_calories"
    if "calories" in columns:
        return "calories"
    return "NULL"


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None
