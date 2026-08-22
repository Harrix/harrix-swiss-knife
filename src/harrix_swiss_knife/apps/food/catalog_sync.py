"""Export and upsert food catalog items without touching the food log.

Uses stdlib `sqlite3` so pack/install and unit tests do not need Qt SQL.
Keys are food item `name`. Table `food_log` is never read or written.

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


def create_empty_food_database(db_path: Path, recover_sql_path: Path) -> None:
    """Create a new SQLite file by executing `recover.sql` (schema plus base seed)."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql = recover_sql_path.read_text(encoding="utf-8")
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(sql)
        conn.commit()


def export_food_catalog(db_path: Path) -> dict[str, Any]:
    """Read `food_items` from `db_path` into a JSON-serializable catalog.

    Returns:

    - `dict[str, Any]`: Object with `version` and `food_items`. Database `id`
      values are omitted.

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
    return {"version": int(raw.get("version") or 1), "food_items": food_items}


def upsert_food_catalog(db_path: Path, catalog: dict[str, Any]) -> FoodCatalogUpsertStats:
    """Insert or update food items by name; never touch `food_log`.

    Existing local-only items are left unchanged. Existing `id` values are
    preserved so `food_log` rows stay linked.

    """
    normalized = normalize_food_catalog(catalog)
    if not db_path.is_file():
        msg = f"Food database not found: {db_path}"
        raise FileNotFoundError(msg)

    inserted = 0
    updated = 0
    with sqlite3.connect(str(db_path)) as conn:
        for item in normalized["food_items"]:
            row = conn.execute("SELECT id FROM food_items WHERE name = ?", (item["name"],)).fetchone()
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
                    WHERE id = ?
                    """,
                    (*values, int(row[0])),
                )
                updated += 1
        conn.commit()

    return FoodCatalogUpsertStats(food_items_inserted=inserted, food_items_updated=updated)


def _optional_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    return float(str(value))
