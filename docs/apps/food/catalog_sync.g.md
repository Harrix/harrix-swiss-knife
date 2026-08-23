---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `catalog_sync.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FoodCatalogUpsertStats`](#%EF%B8%8F-class-foodcatalogupsertstats)
- [🔧 Function `create_empty_food_database`](#-function-create_empty_food_database)
- [🔧 Function `export_food_catalog`](#-function-export_food_catalog)
- [🔧 Function `load_food_catalog_json`](#-function-load_food_catalog_json)
- [🔧 Function `normalize_food_catalog`](#-function-normalize_food_catalog)
- [🔧 Function `upsert_food_catalog`](#-function-upsert_food_catalog)

</details>

## 🏛️ Class `FoodCatalogUpsertStats`

```python
class FoodCatalogUpsertStats
```

Counts from a food catalog upsert into a target database.

<details>
<summary>Code:</summary>

```python
class FoodCatalogUpsertStats:

    food_items_inserted: int = 0
    food_items_updated: int = 0
```

</details>

## 🔧 Function `create_empty_food_database`

```python
def create_empty_food_database(db_path: Path, recover_sql_path: Path) -> None
```

Create a new SQLite file by executing `recover.sql` (schema plus base seed).

<details>
<summary>Code:</summary>

```python
def create_empty_food_database(db_path: Path, recover_sql_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql = recover_sql_path.read_text(encoding="utf-8")
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(sql)
        conn.commit()
```

</details>

## 🔧 Function `export_food_catalog`

```python
def export_food_catalog(db_path: Path) -> dict[str, Any]
```

Read `food_items` from `db_path` into a JSON-serializable catalog.

Returns:

- `dict[str, Any]`: Object with `version` and `food_items`. Database `_id`
  values are omitted.

<details>
<summary>Code:</summary>

```python
def export_food_catalog(db_path: Path) -> dict[str, Any]:
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
```

</details>

## 🔧 Function `load_food_catalog_json`

```python
def load_food_catalog_json(path: Path) -> dict[str, Any]
```

Load and lightly validate a food catalog JSON file.

<details>
<summary>Code:</summary>

```python
def load_food_catalog_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return normalize_food_catalog(raw)
```

</details>

## 🔧 Function `normalize_food_catalog`

```python
def normalize_food_catalog(raw: Any) -> dict[str, Any]
```

Validate catalog shape and return a normalized dict.

<details>
<summary>Code:</summary>

```python
def normalize_food_catalog(raw: Any) -> dict[str, Any]:
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
```

</details>

## 🔧 Function `upsert_food_catalog`

```python
def upsert_food_catalog(db_path: Path, catalog: dict[str, Any]) -> FoodCatalogUpsertStats
```

Insert or update food items by name; never touch `food_log`.

Existing local-only items are left unchanged. Existing `_id` values are
preserved so `food_log` rows stay linked.

<details>
<summary>Code:</summary>

```python
def upsert_food_catalog(db_path: Path, catalog: dict[str, Any]) -> FoodCatalogUpsertStats:
    normalized = normalize_food_catalog(catalog)
    if not db_path.is_file():
        msg = f"Food database not found: {db_path}"
        raise FileNotFoundError(msg)

    inserted = 0
    updated = 0
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
        conn.commit()

    return FoodCatalogUpsertStats(food_items_inserted=inserted, food_items_updated=updated)
```

</details>
