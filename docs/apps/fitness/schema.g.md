---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `schema.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `ensure_fitness_indexes`](#-function-ensure_fitness_indexes)
- [🔧 Function `ensure_fitness_schema`](#-function-ensure_fitness_schema)

</details>

## 🔧 Function `ensure_fitness_indexes`

```python
def ensure_fitness_indexes(db_path: Path) -> bool
```

Create lookup indexes used by per-exercise queries.

Without these, every `WHERE _id_exercises = ?` or `WHERE name = ?` lookup is a
full table scan, which dominates startup once the catalog grows.

Args:

- `db_path` (`Path`): Path to `fitness.db`.

Returns:

- `bool`: `True` when at least one index was created.

<details>
<summary>Code:</summary>

```python
def ensure_fitness_indexes(db_path: Path) -> bool:
    if not db_path.is_file():
        return False

    created = False
    with sqlite3.connect(str(db_path)) as conn:
        existing = {
            str(row[0]) for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'") if row[0]
        }
        for statement in _INDEX_SQL:
            index_name = statement.split(" ON ", 1)[0].rsplit(" ", 1)[-1]
            if index_name in existing:
                continue
            table = statement.split(" ON ", 1)[1].split("(", 1)[0].strip()
            if not _table_exists(conn, table):
                continue
            conn.execute(statement)
            created = True
        if created:
            conn.commit()
            logger.info("Created Fitness lookup indexes in %s", db_path)
    return created
```

</details>

## 🔧 Function `ensure_fitness_schema`

```python
def ensure_fitness_schema(db_path: Path) -> bool
```

Create `workouts` / `workout_items` when they are missing.

Args:

- `db_path` (`Path`): Path to `fitness.db`.

Returns:

- `bool`: `True` when tables were created, `False` when unchanged or skipped.

<details>
<summary>Code:</summary>

```python
def ensure_fitness_schema(db_path: Path) -> bool:
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
```

</details>
