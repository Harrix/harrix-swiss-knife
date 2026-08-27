"""Tests for Food SQLite schema migration from legacy recover.sql layout."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from harrix_swiss_knife.apps.food.schema import ensure_food_schema

_LEGACY_SCHEMA = """
CREATE TABLE food_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_en TEXT,
    is_drink INTEGER NOT NULL DEFAULT 0,
    calories_per_100g REAL,
    default_portion_weight REAL,
    default_portion_calories REAL
);
CREATE TABLE food_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT NOT NULL,
    food_item_id INTEGER,
    name TEXT NOT NULL,
    name_en TEXT,
    is_drink INTEGER NOT NULL DEFAULT 0,
    calories REAL,
    weight REAL
);
"""


def test_ensure_food_schema_migrates_legacy_id_datetime(tmp_path: Path) -> None:
    """Installer-created legacy DBs gain `_id` / `date` / `portion_calories`."""
    db_path = tmp_path / "food.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(_LEGACY_SCHEMA)
        conn.execute(
            """
            INSERT INTO food_items (name, name_en, is_drink, calories_per_100g)
            VALUES ('Банан', 'Banana', 0, 89)
            """
        )
        item_id = int(conn.execute("SELECT id FROM food_items").fetchone()[0])
        conn.execute(
            """
            INSERT INTO food_log (datetime, food_item_id, name, name_en, is_drink, calories, weight)
            VALUES ('2024-06-15T08:30:00', ?, 'Банан', 'Banana', 0, 178, 200)
            """,
            (item_id,),
        )
        conn.commit()

    assert ensure_food_schema(db_path) is True
    assert ensure_food_schema(db_path) is False

    with sqlite3.connect(str(db_path)) as conn:
        log_cols = {row[1] for row in conn.execute("PRAGMA table_info(food_log)")}
        assert {"_id", "date", "portion_calories", "calories_per_100g"}.issubset(log_cols)
        assert "datetime" not in log_cols
        assert "id" not in {row[1] for row in conn.execute("PRAGMA table_info(food_items)")}
        row = conn.execute("SELECT _id, date, weight, portion_calories, name FROM food_log").fetchone()
        assert row is not None
        assert int(row[0]) == item_id
        assert row[1] == "2024-06-15"
        assert float(row[2]) == 200
        assert float(row[3]) == 178
        assert row[4] == "Банан"
        assert int(conn.execute("SELECT COUNT(*) FROM food_items").fetchone()[0]) == 1
        assert _table_exists_names(conn, "recipes")
        assert _table_exists_names(conn, "recipe_ingredients")


def test_ensure_food_schema_creates_recipes_on_current_db(tmp_path: Path) -> None:
    """Existing current-schema DBs gain empty recipes tables."""
    db_path = tmp_path / "food_current.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(
            """
            CREATE TABLE food_items (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                name_en TEXT,
                is_drink INTEGER NOT NULL DEFAULT 0,
                calories_per_100g REAL,
                default_portion_weight REAL,
                default_portion_calories REAL
            );
            CREATE TABLE food_log (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                weight REAL,
                portion_calories REAL,
                calories_per_100g REAL,
                name TEXT,
                name_en TEXT,
                is_drink INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        conn.commit()

    assert ensure_food_schema(db_path) is True
    assert ensure_food_schema(db_path) is False

    with sqlite3.connect(str(db_path)) as conn:
        assert _table_exists_names(conn, "recipes")
        assert _table_exists_names(conn, "recipe_ingredients")
        cols = {row[1] for row in conn.execute("PRAGMA table_info(recipes)")}
        assert {"_id", "name", "calories_per_100g", "total_weight"}.issubset(cols)


def _table_exists_names(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None
