---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `catalog_sync.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CatalogUpsertStats`](#%EF%B8%8F-class-catalogupsertstats)
- [🔧 Function `create_empty_fitness_database`](#-function-create_empty_fitness_database)
- [🔧 Function `export_fitness_catalog`](#-function-export_fitness_catalog)
- [🔧 Function `load_fitness_catalog_json`](#-function-load_fitness_catalog_json)
- [🔧 Function `normalize_fitness_catalog`](#-function-normalize_fitness_catalog)
- [🔧 Function `upsert_fitness_catalog`](#-function-upsert_fitness_catalog)

</details>

## 🏛️ Class `CatalogUpsertStats`

```python
class CatalogUpsertStats
```

Counts from a catalog upsert into a target database.

<details>
<summary>Code:</summary>

```python
class CatalogUpsertStats:

    exercises_inserted: int = 0
    exercises_updated: int = 0
    types_inserted: int = 0
    types_updated: int = 0
```

</details>

## 🔧 Function `create_empty_fitness_database`

```python
def create_empty_fitness_database(db_path: Path, recover_sql_path: Path) -> None
```

Create a new SQLite file by executing `recover.sql` (schema plus base seed).

<details>
<summary>Code:</summary>

```python
def create_empty_fitness_database(db_path: Path, recover_sql_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql = recover_sql_path.read_text(encoding="utf-8")
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(sql)
        conn.commit()
```

</details>

## 🔧 Function `export_fitness_catalog`

```python
def export_fitness_catalog(db_path: Path) -> dict[str, Any]
```

Read `exercises` and `types` from `db_path` into a JSON-serializable catalog.

Returns:

- `dict[str, Any]`: Object with `version` and `exercises` list. Each exercise has
  `name`, `unit`, `is_type_required`, `calories_per_unit`, `name_local`, and `types`
  (each type: `type`, `calories_modifier`, `name_local`). Database `_id` values are
  omitted.

<details>
<summary>Code:</summary>

```python
def export_fitness_catalog(db_path: Path) -> dict[str, Any]:
    if not db_path.is_file():
        msg = f"Fitness database not found: {db_path}"
        raise FileNotFoundError(msg)

    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        exercise_rows = conn.execute(
            """
            SELECT _id, name, unit, is_type_required, calories_per_unit,
                   IFNULL(name_local, '') AS name_local
            FROM exercises
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()

        exercises: list[dict[str, Any]] = []
        for row in exercise_rows:
            type_rows = conn.execute(
                """
                SELECT type, calories_modifier, IFNULL(name_local, '') AS name_local
                FROM types
                WHERE _id_exercises = ?
                ORDER BY type COLLATE NOCASE
                """,
                (int(row["_id"]),),
            ).fetchall()
            exercises.append(
                {
                    "name": str(row["name"]),
                    "unit": str(row["unit"] or ""),
                    "is_type_required": bool(int(row["is_type_required"] or 0)),
                    "calories_per_unit": float(row["calories_per_unit"] or 0.0),
                    "name_local": str(row["name_local"] or ""),
                    "types": [
                        {
                            "type": str(t["type"]),
                            "calories_modifier": float(t["calories_modifier"] or 1.0),
                            "name_local": str(t["name_local"] or ""),
                        }
                        for t in type_rows
                    ],
                }
            )

    return {"version": 1, "exercises": exercises}
```

</details>

## 🔧 Function `load_fitness_catalog_json`

```python
def load_fitness_catalog_json(path: Path) -> dict[str, Any]
```

Load and lightly validate a fitness catalog JSON file.

<details>
<summary>Code:</summary>

```python
def load_fitness_catalog_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return normalize_fitness_catalog(raw)
```

</details>

## 🔧 Function `normalize_fitness_catalog`

```python
def normalize_fitness_catalog(raw: Any) -> dict[str, Any]
```

Validate catalog shape and return a normalized dict.

<details>
<summary>Code:</summary>

```python
def normalize_fitness_catalog(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        msg = "fitness_catalog.json root must be an object"
        raise TypeError(msg)
    exercises_raw = raw.get("exercises")
    if not isinstance(exercises_raw, list):
        msg = "fitness_catalog.json must contain an 'exercises' list"
        raise TypeError(msg)

    exercises: list[dict[str, Any]] = []
    for index, item in enumerate(exercises_raw):
        if not isinstance(item, dict):
            msg = f"exercises[{index}] must be an object"
            raise TypeError(msg)
        name = str(item.get("name") or "").strip()
        if not name:
            msg = f"exercises[{index}] is missing non-empty 'name'"
            raise ValueError(msg)
        types_raw = item.get("types") or []
        if not isinstance(types_raw, list):
            msg = f"exercises[{index}].types must be a list"
            raise TypeError(msg)
        types: list[dict[str, Any]] = []
        for t_index, t_item in enumerate(types_raw):
            if not isinstance(t_item, dict):
                msg = f"exercises[{index}].types[{t_index}] must be an object"
                raise TypeError(msg)
            type_name = str(t_item.get("type") or "").strip()
            if not type_name:
                msg = f"exercises[{index}].types[{t_index}] is missing non-empty 'type'"
                raise ValueError(msg)
            types.append(
                {
                    "type": type_name,
                    "calories_modifier": float(t_item.get("calories_modifier") or 1.0),
                    "name_local": str(t_item.get("name_local") or ""),
                }
            )
        exercises.append(
            {
                "name": name,
                "unit": str(item.get("unit") or ""),
                "is_type_required": bool(item.get("is_type_required")),
                "calories_per_unit": float(item.get("calories_per_unit") or 0.0),
                "name_local": str(item.get("name_local") or ""),
                "types": types,
            }
        )
    return {"version": int(raw.get("version") or 1), "exercises": exercises}
```

</details>

## 🔧 Function `upsert_fitness_catalog`

```python
def upsert_fitness_catalog(db_path: Path, catalog: dict[str, Any]) -> CatalogUpsertStats
```

Insert or update exercises and types by English name; never touch process/weight.

Existing local-only exercises and types are left unchanged. Existing `_id` values
are preserved so `process` rows stay linked.

<details>
<summary>Code:</summary>

```python
def upsert_fitness_catalog(db_path: Path, catalog: dict[str, Any]) -> CatalogUpsertStats:
    normalized = normalize_fitness_catalog(catalog)
    if not db_path.is_file():
        msg = f"Fitness database not found: {db_path}"
        raise FileNotFoundError(msg)

    exercises_inserted = 0
    exercises_updated = 0
    types_inserted = 0
    types_updated = 0

    with sqlite3.connect(str(db_path)) as conn:
        _ensure_name_local_columns(conn)
        for exercise in normalized["exercises"]:
            name = exercise["name"]
            row = conn.execute("SELECT _id FROM exercises WHERE name = ?", (name,)).fetchone()
            if row is None:
                cur = conn.execute(
                    """
                    INSERT INTO exercises (name, unit, is_type_required, calories_per_unit, name_local)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        exercise["unit"],
                        1 if exercise["is_type_required"] else 0,
                        exercise["calories_per_unit"],
                        exercise["name_local"] or None,
                    ),
                )
                if cur.lastrowid is None:
                    msg = f"INSERT into exercises did not return lastrowid for {name!r}"
                    raise RuntimeError(msg)
                exercise_id = int(cur.lastrowid)
                exercises_inserted += 1
            else:
                exercise_id = int(row[0])
                conn.execute(
                    """
                    UPDATE exercises
                    SET unit = ?, is_type_required = ?, calories_per_unit = ?, name_local = ?
                    WHERE _id = ?
                    """,
                    (
                        exercise["unit"],
                        1 if exercise["is_type_required"] else 0,
                        exercise["calories_per_unit"],
                        exercise["name_local"] or None,
                        exercise_id,
                    ),
                )
                exercises_updated += 1

            for type_item in exercise["types"]:
                type_name = type_item["type"]
                t_row = conn.execute(
                    "SELECT _id FROM types WHERE _id_exercises = ? AND type = ?",
                    (exercise_id, type_name),
                ).fetchone()
                if t_row is None:
                    conn.execute(
                        """
                        INSERT INTO types (_id_exercises, type, calories_modifier, name_local)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            exercise_id,
                            type_name,
                            type_item["calories_modifier"],
                            type_item["name_local"] or None,
                        ),
                    )
                    types_inserted += 1
                else:
                    conn.execute(
                        """
                        UPDATE types
                        SET calories_modifier = ?, name_local = ?
                        WHERE _id = ?
                        """,
                        (
                            type_item["calories_modifier"],
                            type_item["name_local"] or None,
                            int(t_row[0]),
                        ),
                    )
                    types_updated += 1
        conn.commit()

    return CatalogUpsertStats(
        exercises_inserted=exercises_inserted,
        exercises_updated=exercises_updated,
        types_inserted=types_inserted,
        types_updated=types_updated,
    )
```

</details>
