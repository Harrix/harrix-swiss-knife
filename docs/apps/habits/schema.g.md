---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `schema.py`

## 🔧 Function `ensure_habits_indexes`

```python
def ensure_habits_indexes(db_path: Path) -> bool
```

Create lookup indexes for `process_habits`, which every dashboard query filters on.

Args:

- `db_path` (`Path`): Path to `habits.db`.

Returns:

- `bool`: `True` when at least one index was created.

<details>
<summary>Code:</summary>

```python
def ensure_habits_indexes(db_path: Path) -> bool:
    return ensure_sqlite_indexes(db_path, _INDEX_SQL, label="Habits")
```

</details>
