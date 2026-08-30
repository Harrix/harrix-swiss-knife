"""Tests for food catalog export/upsert (no Qt required)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from harrix_swiss_knife.apps.food.catalog_sync import export_food_catalog, upsert_food_catalog

_SCHEMA_ONLY_SQL = """
CREATE TABLE food_items (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_en TEXT,
    is_drink INTEGER NOT NULL DEFAULT 0 CHECK (is_drink IN (0, 1)),
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
    is_drink INTEGER NOT NULL DEFAULT 0 CHECK (is_drink IN (0, 1))
);
"""


def _create_schema_only_db(db_path: Path) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(_SCHEMA_ONLY_SQL)
        conn.commit()
    return db_path


def _seed_source_db(db_path: Path) -> int:
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO food_items (
                name, name_en, is_drink, calories_per_100g,
                default_portion_weight, default_portion_calories
            )
            VALUES ('Банан', 'Banana', 0, 89, NULL, NULL)
            """
        )
        item_id = int(conn.execute("SELECT _id FROM food_items WHERE name = 'Банан'").fetchone()[0])
        conn.execute(
            """
            INSERT INTO food_log (date, name, calories_per_100g, weight, is_drink)
            VALUES ('2024-01-01', 'Банан', 89, 100, 0)
            """,
        )
        conn.commit()
    return item_id


def test_export_omits_ids_and_food_log(tmp_path: Path) -> None:
    """Catalog export has food items and empty recipes when recipe tables are missing."""
    db_path = _create_schema_only_db(tmp_path / "food.db")
    _seed_source_db(db_path)
    catalog = export_food_catalog(db_path)
    assert catalog["version"] == 1
    assert catalog["food_items"] == [
        {
            "name": "Банан",
            "name_en": "Banana",
            "is_drink": False,
            "calories_per_100g": 89.0,
            "default_portion_weight": None,
            "default_portion_calories": None,
        },
    ]
    assert catalog["recipes"] == []
    assert "food_log" not in catalog
    assert "id" not in catalog["food_items"][0]


def test_upsert_updates_existing_preserves_ids_and_log(tmp_path: Path) -> None:
    """Matching names update fields; food_log and IDs stay intact."""
    db_path = _create_schema_only_db(tmp_path / "food.db")
    item_id = _seed_source_db(db_path)
    catalog = {
        "version": 1,
        "food_items": [
            {
                "name": "Банан",
                "name_en": "Banana ripe",
                "is_drink": False,
                "calories_per_100g": 95,
                "default_portion_weight": 120,
                "default_portion_calories": None,
            },
            {
                "name": "Американо",
                "name_en": "Americano",
                "is_drink": True,
                "calories_per_100g": 2,
                "default_portion_weight": 200,
                "default_portion_calories": None,
            },
        ],
    }
    stats = upsert_food_catalog(db_path, catalog)
    assert stats.food_items_updated == 1
    assert stats.food_items_inserted == 1

    with sqlite3.connect(str(db_path)) as conn:
        banana = conn.execute(
            """
            SELECT _id, name_en, calories_per_100g, default_portion_weight
            FROM food_items WHERE name = 'Банан'
            """
        ).fetchone()
        assert banana is not None
        assert int(banana[0]) == item_id
        assert banana[1] == "Banana ripe"
        assert float(banana[2]) == 95
        assert float(banana[3]) == 120
        assert int(conn.execute("SELECT COUNT(*) FROM food_log").fetchone()[0]) == 1
        assert conn.execute("SELECT name FROM food_log").fetchone()[0] == "Банан"
        assert int(conn.execute("SELECT is_drink FROM food_items WHERE name = 'Американо'").fetchone()[0]) == 1


_RECIPES_SCHEMA_SQL = """
CREATE TABLE recipes (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_en TEXT,
    is_drink INTEGER NOT NULL DEFAULT 0 CHECK (is_drink IN (0, 1)),
    calories_per_100g REAL,
    total_weight REAL
);
CREATE TABLE recipe_ingredients (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    name_en TEXT,
    weight REAL,
    calories_per_100g REAL,
    portion_calories REAL,
    is_drink INTEGER NOT NULL DEFAULT 0 CHECK (is_drink IN (0, 1)),
    sort_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (recipe_id) REFERENCES recipes(_id) ON DELETE CASCADE
);
"""


def _create_recipes_schema(db_path: Path) -> None:
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(_RECIPES_SCHEMA_SQL)
        conn.commit()


def _seed_recipe(db_path: Path) -> int:
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.execute(
            """
            INSERT INTO recipes (name, name_en, is_drink, calories_per_100g, total_weight)
            VALUES ('Овсянка', 'Oatmeal', 0, 88, 250)
            """
        )
        recipe_id = int(cursor.lastrowid or 0)
        conn.execute(
            """
            INSERT INTO recipe_ingredients (
                recipe_id, name, name_en, weight, calories_per_100g,
                portion_calories, is_drink, sort_order
            )
            VALUES (?, 'Овсянка', 'Oats', 50, 350, 175, 0, 0)
            """,
            (recipe_id,),
        )
        conn.commit()
    return recipe_id


def test_export_recipes_omits_ids(tmp_path: Path) -> None:
    """Catalog export includes recipes and ingredients without database IDs."""
    db_path = _create_schema_only_db(tmp_path / "food.db")
    _create_recipes_schema(db_path)
    _seed_recipe(db_path)
    catalog = export_food_catalog(db_path)
    assert catalog["recipes"] == [
        {
            "name": "Овсянка",
            "name_en": "Oatmeal",
            "is_drink": False,
            "calories_per_100g": 88.0,
            "total_weight": 250.0,
            "ingredients": [
                {
                    "name": "Овсянка",
                    "name_en": "Oats",
                    "weight": 50.0,
                    "calories_per_100g": 350.0,
                    "portion_calories": 175.0,
                    "is_drink": False,
                    "sort_order": 0,
                },
            ],
        },
    ]
    assert "_id" not in catalog["recipes"][0]


def test_export_without_recipe_tables_returns_empty_list(tmp_path: Path) -> None:
    """Older food databases without recipe tables export `recipes` as []."""
    db_path = _create_schema_only_db(tmp_path / "food.db")
    catalog = export_food_catalog(db_path)
    assert catalog["recipes"] == []


def test_upsert_recipes_preserves_ids_and_food_log(tmp_path: Path) -> None:
    """Matching recipe names update fields and replace ingredients; food_log stays."""
    db_path = _create_schema_only_db(tmp_path / "food.db")
    _create_recipes_schema(db_path)
    _seed_source_db(db_path)
    recipe_id = _seed_recipe(db_path)
    catalog = {
        "version": 1,
        "food_items": [],
        "recipes": [
            {
                "name": "Овсянка",
                "name_en": "Overnight oats",
                "is_drink": False,
                "calories_per_100g": 90,
                "total_weight": 300,
                "ingredients": [
                    {
                        "name": "Молоко",
                        "name_en": "Milk",
                        "weight": 200,
                        "calories_per_100g": 60,
                        "portion_calories": 120,
                        "is_drink": True,
                        "sort_order": 0,
                    },
                ],
            },
            {
                "name": "Смузи",
                "name_en": "Smoothie",
                "is_drink": True,
                "calories_per_100g": 40,
                "total_weight": 400,
                "ingredients": [],
            },
        ],
    }
    stats = upsert_food_catalog(db_path, catalog)
    assert stats.recipes_updated == 1
    assert stats.recipes_inserted == 1

    with sqlite3.connect(str(db_path)) as conn:
        oatmeal = conn.execute(
            "SELECT _id, name_en, calories_per_100g, total_weight FROM recipes WHERE name = 'Овсянка'"
        ).fetchone()
        assert oatmeal is not None
        assert int(oatmeal[0]) == recipe_id
        assert oatmeal[1] == "Overnight oats"
        assert float(oatmeal[2]) == 90
        assert float(oatmeal[3]) == 300
        ingredients = conn.execute(
            "SELECT name, is_drink FROM recipe_ingredients WHERE recipe_id = ? ORDER BY sort_order",
            (recipe_id,),
        ).fetchall()
        assert [(row[0], int(row[1])) for row in ingredients] == [("Молоко", 1)]
        assert int(conn.execute("SELECT COUNT(*) FROM food_log").fetchone()[0]) == 1
        assert conn.execute("SELECT name FROM recipes WHERE name = 'Смузи'").fetchone() is not None
