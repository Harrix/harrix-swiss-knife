---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `schema.py`

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
