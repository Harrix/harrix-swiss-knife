"""Export and upsert food catalog items and recipes without touching the food log.

Uses stdlib `sqlite3` so pack/install and unit tests do not need Qt SQL.
Keys are food item `name` and recipe `name`. Table `food_log` is never read
or written.

"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class FoodCatalogUpsertStats:
    """Counts from a food catalog upsert into a target database."""

    food_items_inserted: int = 0
    food_items_updated: int = 0
    recipes_inserted: int = 0
    recipes_updated: int = 0


def create_empty_food_database(db_path: Path, recover_sql_path: Path) -> None:
    """Create a new SQLite file by executing `recover.sql` (schema plus base seed)."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql = recover_sql_path.read_text(encoding="utf-8")
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(sql)
        conn.commit()


def export_food_catalog(db_path: Path) -> dict[str, Any]:
    """Read `food_items` and recipes from `db_path` into a JSON catalog.

    Returns:

    - `dict[str, Any]`: Object with `version`, `food_items`, and `recipes`.
      Database `_id` values are omitted.

    """
    if not db_path.is_file():
        msg = f"Food database not found: {db_path}"
        raise FileNotFoundError(msg)

    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                name,
                name_en,
                is_drink,
                calories_per_100g,
                default_portion_weight,
                default_portion_calories
            FROM food_items
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()
        recipes = _export_recipes(conn)

    return {
        "version": 1,
        "food_items": [
            {
                "name": str(row["name"]),
                "name_en": str(row["name_en"]) if row["name_en"] is not None else None,
                "is_drink": bool(int(row["is_drink"] or 0)),
                "calories_per_100g": _optional_float(row["calories_per_100g"]),
                "default_portion_weight": _optional_float(row["default_portion_weight"]),
                "default_portion_calories": _optional_float(row["default_portion_calories"]),
            }
            for row in rows
        ],
        "recipes": recipes,
    }


def load_food_catalog_json(path: Path) -> dict[str, Any]:
    """Load and lightly validate a food catalog JSON file."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return normalize_food_catalog(raw)


def normalize_food_catalog(raw: Any) -> dict[str, Any]:
    """Validate catalog shape and return a normalized dict."""
    if not isinstance(raw, dict):
        msg = "food_catalog.json root must be an object"
        raise TypeError(msg)
    items_raw = raw.get("food_items")
    if items_raw is None:
        items_raw = []
    if not isinstance(items_raw, list):
        msg = "food_catalog.json must contain a 'food_items' list"
        raise TypeError(msg)

    food_items: list[dict[str, Any]] = []
    for index, item in enumerate(items_raw):
        if not isinstance(item, dict):
            msg = f"food_items[{index}] must be an object"
            raise TypeError(msg)
        name = str(item.get("name") or "").strip()
        if not name:
            msg = f"food_items[{index}] is missing non-empty 'name'"
            raise ValueError(msg)
        name_en_raw = item.get("name_en")
        name_en = str(name_en_raw).strip() if name_en_raw not in (None, "") else None
        food_items.append(
            {
                "name": name,
                "name_en": name_en,
                "is_drink": bool(item.get("is_drink")),
                "calories_per_100g": _optional_float(item.get("calories_per_100g")),
                "default_portion_weight": _optional_float(item.get("default_portion_weight")),
                "default_portion_calories": _optional_float(item.get("default_portion_calories")),
            }
        )
    recipes_raw = raw.get("recipes")
    if recipes_raw is None:
        recipes_raw = []
    if not isinstance(recipes_raw, list):
        msg = "food_catalog.json must contain a 'recipes' list when present"
        raise TypeError(msg)
    recipes: list[dict[str, Any]] = []
    for index, recipe in enumerate(recipes_raw):
        recipes.append(_normalize_recipe(recipe, index))
    return {"version": int(raw.get("version") or 1), "food_items": food_items, "recipes": recipes}


def upsert_food_catalog(db_path: Path, catalog: dict[str, Any]) -> FoodCatalogUpsertStats:
    """Insert or update food items and recipes by name; never touch `food_log`.

    Existing local-only items and recipes are left unchanged. Existing `_id`
    values are preserved so `food_log` rows stay linked.

    """
    normalized = normalize_food_catalog(catalog)
    if not db_path.is_file():
        msg = f"Food database not found: {db_path}"
        raise FileNotFoundError(msg)

    inserted = 0
    updated = 0
    recipes_inserted = 0
    recipes_updated = 0
    with sqlite3.connect(str(db_path)) as conn:
        for item in normalized["food_items"]:
            row = conn.execute("SELECT _id FROM food_items WHERE name = ?", (item["name"],)).fetchone()
            values = (
                item["name_en"],
                1 if item["is_drink"] else 0,
                item["calories_per_100g"],
                item["default_portion_weight"],
                item["default_portion_calories"],
            )
            if row is None:
                conn.execute(
                    """
                    INSERT INTO food_items (
                        name, name_en, is_drink, calories_per_100g,
                        default_portion_weight, default_portion_calories
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (item["name"], *values),
                )
                inserted += 1
            else:
                conn.execute(
                    """
                    UPDATE food_items
                    SET name_en = ?, is_drink = ?, calories_per_100g = ?,
                        default_portion_weight = ?, default_portion_calories = ?
                    WHERE _id = ?
                    """,
                    (*values, int(row[0])),
                )
                updated += 1
        recipes_inserted, recipes_updated = _upsert_recipes(conn, normalized["recipes"])
        conn.commit()

    return FoodCatalogUpsertStats(
        food_items_inserted=inserted,
        food_items_updated=updated,
        recipes_inserted=recipes_inserted,
        recipes_updated=recipes_updated,
    )


def _ensure_recipe_tables(conn: sqlite3.Connection) -> None:
    conn.execute(_RECIPES_TABLE_SQL)
    conn.execute(_RECIPE_INGREDIENTS_TABLE_SQL)


def _export_recipes(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    if not _table_exists(conn, "recipes"):
        return []
    recipe_rows = conn.execute(
        """
        SELECT _id, name, name_en, is_drink, calories_per_100g, total_weight
        FROM recipes
        ORDER BY name COLLATE NOCASE
        """
    ).fetchall()
    has_ingredients = _table_exists(conn, "recipe_ingredients")
    recipes: list[dict[str, Any]] = []
    for row in recipe_rows:
        ingredients: list[dict[str, Any]] = []
        if has_ingredients:
            ingredient_rows = conn.execute(
                """
                SELECT name, name_en, weight, calories_per_100g, portion_calories,
                       is_drink, sort_order
                FROM recipe_ingredients
                WHERE recipe_id = ?
                ORDER BY sort_order, _id
                """,
                (int(row["_id"]),),
            ).fetchall()
            ingredients = [
                {
                    "name": str(item["name"]),
                    "name_en": str(item["name_en"]) if item["name_en"] is not None else None,
                    "weight": _optional_float(item["weight"]),
                    "calories_per_100g": _optional_float(item["calories_per_100g"]),
                    "portion_calories": _optional_float(item["portion_calories"]),
                    "is_drink": bool(int(item["is_drink"] or 0)),
                    "sort_order": int(item["sort_order"] or 0),
                }
                for item in ingredient_rows
            ]
        recipes.append(
            {
                "name": str(row["name"]),
                "name_en": str(row["name_en"]) if row["name_en"] is not None else None,
                "is_drink": bool(int(row["is_drink"] or 0)),
                "calories_per_100g": _optional_float(row["calories_per_100g"]),
                "total_weight": _optional_float(row["total_weight"]),
                "ingredients": ingredients,
            }
        )
    return recipes


def _normalize_ingredient(item: Any, recipe_index: int, ingredient_index: int) -> dict[str, Any]:
    if not isinstance(item, dict):
        msg = f"recipes[{recipe_index}].ingredients[{ingredient_index}] must be an object"
        raise TypeError(msg)
    name = str(item.get("name") or "").strip()
    if not name:
        msg = f"recipes[{recipe_index}].ingredients[{ingredient_index}] is missing non-empty 'name'"
        raise ValueError(msg)
    name_en_raw = item.get("name_en")
    name_en = str(name_en_raw).strip() if name_en_raw not in (None, "") else None
    return {
        "name": name,
        "name_en": name_en,
        "weight": _optional_float(item.get("weight")),
        "calories_per_100g": _optional_float(item.get("calories_per_100g")),
        "portion_calories": _optional_float(item.get("portion_calories")),
        "is_drink": bool(item.get("is_drink")),
        "sort_order": _optional_int(item.get("sort_order"), default=ingredient_index),
    }


def _normalize_recipe(item: Any, index: int) -> dict[str, Any]:
    if not isinstance(item, dict):
        msg = f"recipes[{index}] must be an object"
        raise TypeError(msg)
    name = str(item.get("name") or "").strip()
    if not name:
        msg = f"recipes[{index}] is missing non-empty 'name'"
        raise ValueError(msg)
    name_en_raw = item.get("name_en")
    name_en = str(name_en_raw).strip() if name_en_raw not in (None, "") else None
    ingredients_raw = item.get("ingredients")
    if ingredients_raw is None:
        ingredients_raw = []
    if not isinstance(ingredients_raw, list):
        msg = f"recipes[{index}].ingredients must be a list"
        raise TypeError(msg)
    return {
        "name": name,
        "name_en": name_en,
        "is_drink": bool(item.get("is_drink")),
        "calories_per_100g": _optional_float(item.get("calories_per_100g")),
        "total_weight": _optional_float(item.get("total_weight")),
        "ingredients": [
            _normalize_ingredient(ingredient, index, ingredient_index)
            for ingredient_index, ingredient in enumerate(ingredients_raw)
        ],
    }


def _optional_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    return float(str(value))


def _optional_int(value: object, *, default: int) -> int:
    if value is None or value == "":
        return default
    return int(str(value))


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (name,),
    ).fetchone()
    return row is not None


def _upsert_recipes(conn: sqlite3.Connection, recipes: list[dict[str, Any]]) -> tuple[int, int]:
    _ensure_recipe_tables(conn)
    inserted = 0
    updated = 0
    for recipe in recipes:
        row = conn.execute("SELECT _id FROM recipes WHERE name = ?", (recipe["name"],)).fetchone()
        values = (
            recipe["name_en"],
            1 if recipe["is_drink"] else 0,
            recipe["calories_per_100g"],
            recipe["total_weight"],
        )
        if row is None:
            cursor = conn.execute(
                """
                INSERT INTO recipes (name, name_en, is_drink, calories_per_100g, total_weight)
                VALUES (?, ?, ?, ?, ?)
                """,
                (recipe["name"], *values),
            )
            recipe_id = int(cursor.lastrowid or 0)
            inserted += 1
        else:
            recipe_id = int(row[0])
            conn.execute(
                """
                UPDATE recipes
                SET name_en = ?, is_drink = ?, calories_per_100g = ?, total_weight = ?
                WHERE _id = ?
                """,
                (*values, recipe_id),
            )
            conn.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
            updated += 1
        for ingredient in recipe["ingredients"]:
            conn.execute(
                """
                INSERT INTO recipe_ingredients (
                    recipe_id, name, name_en, weight, calories_per_100g,
                    portion_calories, is_drink, sort_order
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    recipe_id,
                    ingredient["name"],
                    ingredient["name_en"],
                    ingredient["weight"],
                    ingredient["calories_per_100g"],
                    ingredient["portion_calories"],
                    1 if ingredient["is_drink"] else 0,
                    ingredient["sort_order"],
                ),
            )
    return inserted, updated


_RECIPES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS recipes (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_en TEXT,
    is_drink INTEGER NOT NULL DEFAULT 0 CHECK (is_drink IN (0, 1)),
    calories_per_100g REAL,
    total_weight REAL
)
"""

_RECIPE_INGREDIENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS recipe_ingredients (
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
)
"""
