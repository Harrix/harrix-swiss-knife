---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `database_manager.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DatabaseManager`](#%EF%B8%8F-class-databasemanager)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `add_item`](#%EF%B8%8F-method-add_item)
  - [⚙️ Method `add_items`](#%EF%B8%8F-method-add_items)
  - [⚙️ Method `delete_item`](#%EF%B8%8F-method-delete_item)
  - [⚙️ Method `get_zone_sort`](#%EF%B8%8F-method-get_zone_sort)
  - [⚙️ Method `list_items`](#%EF%B8%8F-method-list_items)
  - [⚙️ Method `mark_used`](#%EF%B8%8F-method-mark_used)
  - [⚙️ Method `replace_zone_items`](#%EF%B8%8F-method-replace_zone_items)
  - [⚙️ Method `set_zone_sort`](#%EF%B8%8F-method-set_zone_sort)
  - [⚙️ Method `update_item`](#%EF%B8%8F-method-update_item)
- [🏛️ Class `SnippetItem`](#%EF%B8%8F-class-snippetitem)
- [🏛️ Class `ZoneSort`](#%EF%B8%8F-class-zonesort)
- [🔧 Function `utc_now_iso`](#-function-utc_now_iso)

</details>

## 🏛️ Class `DatabaseManager`

```python
class DatabaseManager(QtSqliteDatabaseManagerBase)
```

Manage the connection and operations for the snippets database.

<details>
<summary>Code:</summary>

```python
class DatabaseManager(QtSqliteDatabaseManagerBase):

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in `db_filename`."""
        super().__init__(prefix="snippets_db", db_filename=db_filename)

    def add_item(self, zone: str, value: str, hint: str = "") -> int | None:
        """Insert one item and return its `_id`."""
        created_at = utc_now_iso()
        sort_index = self._next_sort_index(zone)
        ok = self.execute_simple_query(
            "INSERT INTO items (zone, value, hint, created_at, last_used_at, sort_index) "
            "VALUES (:zone, :value, :hint, :created_at, NULL, :sort_index)",
            {
                "zone": zone,
                "value": value,
                "hint": hint,
                "created_at": created_at,
                "sort_index": sort_index,
            },
        )
        if not ok:
            return None
        rows = self.get_rows("SELECT last_insert_rowid()")
        if not rows or rows[0][0] is None:
            return None
        return int(rows[0][0])

    def add_items(self, zone: str, items: Sequence[tuple[str, str]]) -> bool:
        """Insert many `(value, hint)` pairs into `zone`."""
        if not items:
            return True
        try:
            with self.sql_transaction():
                self._insert_zone_items(zone, items)
        except (RuntimeError, OSError, ConnectionError):
            return False
        return True

    def delete_item(self, item_id: int) -> bool:
        """Delete one item by `_id`."""
        return self.execute_simple_query("DELETE FROM items WHERE _id = :id", {"id": item_id})

    def get_zone_sort(self, zone: str) -> ZoneSort:
        """Return the stored sort settings for `zone`."""
        rows = self.get_rows(
            "SELECT mode, descending FROM zone_sort WHERE zone = :zone",
            {"zone": zone},
        )
        if not rows:
            return ZoneSort(mode=DEFAULT_SORT_MODE, descending=False)
        mode_raw = str(rows[0][0] or DEFAULT_SORT_MODE)
        mode: SortMode = mode_raw if mode_raw in SORT_MODES else DEFAULT_SORT_MODE
        return ZoneSort(mode=mode, descending=bool(int(rows[0][1] or 0)))

    def list_items(self, zone: str) -> list[SnippetItem]:
        """Return all items in `zone`."""
        rows = self.get_rows(
            "SELECT _id, zone, value, hint, created_at, last_used_at, sort_index "
            "FROM items WHERE zone = :zone ORDER BY sort_index ASC, _id ASC",
            {"zone": zone},
        )
        return [_row_to_item(row) for row in rows]

    def mark_used(self, item_id: int) -> bool:
        """Set `last_used_at` to now."""
        return self.execute_simple_query(
            "UPDATE items SET last_used_at = :used_at WHERE _id = :id",
            {"used_at": utc_now_iso(), "id": item_id},
        )

    def replace_zone_items(self, zone: str, items: Sequence[tuple[str, str]]) -> bool:
        """Replace every item in `zone` with `items`, keeping new created timestamps."""
        try:
            with self.sql_transaction():
                self._replace_zone_items(zone, items)
        except (RuntimeError, OSError, ConnectionError):
            return False
        return True

    def set_zone_sort(self, zone: ZoneName | str, mode: SortMode | str, *, descending: bool) -> bool:
        """Persist sort settings for `zone`."""
        return self.execute_simple_query(
            "INSERT INTO zone_sort (zone, mode, descending) VALUES (:zone, :mode, :descending) "
            "ON CONFLICT(zone) DO UPDATE SET mode = :mode, descending = :descending",
            {"zone": zone, "mode": mode, "descending": 1 if descending else 0},
        )

    def update_item(self, item_id: int, value: str, hint: str) -> bool:
        """Update value and hint for one item."""
        return self.execute_simple_query(
            "UPDATE items SET value = :value, hint = :hint WHERE _id = :id",
            {"value": value, "hint": hint, "id": item_id},
        )

    def _insert_zone_items(self, zone: str, items: Sequence[tuple[str, str]]) -> None:
        for value, hint in items:
            if self.add_item(zone, value, hint) is None:
                msg = "Failed to insert snippet item"
                raise RuntimeError(msg)

    def _next_sort_index(self, zone: str) -> int:
        rows = self.get_rows(
            "SELECT COALESCE(MAX(sort_index), -1) FROM items WHERE zone = :zone",
            {"zone": zone},
        )
        if not rows or rows[0][0] is None:
            return 0
        return _as_int(rows[0][0]) + 1

    def _replace_zone_items(self, zone: str, items: Sequence[tuple[str, str]]) -> None:
        if not self.execute_simple_query("DELETE FROM items WHERE zone = :zone", {"zone": zone}):
            msg = "Failed to clear snippet zone"
            raise RuntimeError(msg)
        self._insert_zone_items(zone, items)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, db_filename: str) -> None
```

Open a connection to an SQLite database stored in `db_filename`.

<details>
<summary>Code:</summary>

```python
def __init__(self, db_filename: str) -> None:
        super().__init__(prefix="snippets_db", db_filename=db_filename)
```

</details>

### ⚙️ Method `add_item`

```python
def add_item(self, zone: str, value: str, hint: str = '') -> int | None
```

Insert one item and return its `_id`.

<details>
<summary>Code:</summary>

```python
def add_item(self, zone: str, value: str, hint: str = "") -> int | None:
        created_at = utc_now_iso()
        sort_index = self._next_sort_index(zone)
        ok = self.execute_simple_query(
            "INSERT INTO items (zone, value, hint, created_at, last_used_at, sort_index) "
            "VALUES (:zone, :value, :hint, :created_at, NULL, :sort_index)",
            {
                "zone": zone,
                "value": value,
                "hint": hint,
                "created_at": created_at,
                "sort_index": sort_index,
            },
        )
        if not ok:
            return None
        rows = self.get_rows("SELECT last_insert_rowid()")
        if not rows or rows[0][0] is None:
            return None
        return int(rows[0][0])
```

</details>

### ⚙️ Method `add_items`

```python
def add_items(self, zone: str, items: Sequence[tuple[str, str]]) -> bool
```

Insert many `(value, hint)` pairs into `zone`.

<details>
<summary>Code:</summary>

```python
def add_items(self, zone: str, items: Sequence[tuple[str, str]]) -> bool:
        if not items:
            return True
        try:
            with self.sql_transaction():
                self._insert_zone_items(zone, items)
        except (RuntimeError, OSError, ConnectionError):
            return False
        return True
```

</details>

### ⚙️ Method `delete_item`

```python
def delete_item(self, item_id: int) -> bool
```

Delete one item by `_id`.

<details>
<summary>Code:</summary>

```python
def delete_item(self, item_id: int) -> bool:
        return self.execute_simple_query("DELETE FROM items WHERE _id = :id", {"id": item_id})
```

</details>

### ⚙️ Method `get_zone_sort`

```python
def get_zone_sort(self, zone: str) -> ZoneSort
```

Return the stored sort settings for `zone`.

<details>
<summary>Code:</summary>

```python
def get_zone_sort(self, zone: str) -> ZoneSort:
        rows = self.get_rows(
            "SELECT mode, descending FROM zone_sort WHERE zone = :zone",
            {"zone": zone},
        )
        if not rows:
            return ZoneSort(mode=DEFAULT_SORT_MODE, descending=False)
        mode_raw = str(rows[0][0] or DEFAULT_SORT_MODE)
        mode: SortMode = mode_raw if mode_raw in SORT_MODES else DEFAULT_SORT_MODE
        return ZoneSort(mode=mode, descending=bool(int(rows[0][1] or 0)))
```

</details>

### ⚙️ Method `list_items`

```python
def list_items(self, zone: str) -> list[SnippetItem]
```

Return all items in `zone`.

<details>
<summary>Code:</summary>

```python
def list_items(self, zone: str) -> list[SnippetItem]:
        rows = self.get_rows(
            "SELECT _id, zone, value, hint, created_at, last_used_at, sort_index "
            "FROM items WHERE zone = :zone ORDER BY sort_index ASC, _id ASC",
            {"zone": zone},
        )
        return [_row_to_item(row) for row in rows]
```

</details>

### ⚙️ Method `mark_used`

```python
def mark_used(self, item_id: int) -> bool
```

Set `last_used_at` to now.

<details>
<summary>Code:</summary>

```python
def mark_used(self, item_id: int) -> bool:
        return self.execute_simple_query(
            "UPDATE items SET last_used_at = :used_at WHERE _id = :id",
            {"used_at": utc_now_iso(), "id": item_id},
        )
```

</details>

### ⚙️ Method `replace_zone_items`

```python
def replace_zone_items(self, zone: str, items: Sequence[tuple[str, str]]) -> bool
```

Replace every item in `zone` with `items`, keeping new created timestamps.

<details>
<summary>Code:</summary>

```python
def replace_zone_items(self, zone: str, items: Sequence[tuple[str, str]]) -> bool:
        try:
            with self.sql_transaction():
                self._replace_zone_items(zone, items)
        except (RuntimeError, OSError, ConnectionError):
            return False
        return True
```

</details>

### ⚙️ Method `set_zone_sort`

```python
def set_zone_sort(self, zone: ZoneName | str, mode: SortMode | str, *, descending: bool) -> bool
```

Persist sort settings for `zone`.

<details>
<summary>Code:</summary>

```python
def set_zone_sort(self, zone: ZoneName | str, mode: SortMode | str, *, descending: bool) -> bool:
        return self.execute_simple_query(
            "INSERT INTO zone_sort (zone, mode, descending) VALUES (:zone, :mode, :descending) "
            "ON CONFLICT(zone) DO UPDATE SET mode = :mode, descending = :descending",
            {"zone": zone, "mode": mode, "descending": 1 if descending else 0},
        )
```

</details>

### ⚙️ Method `update_item`

```python
def update_item(self, item_id: int, value: str, hint: str) -> bool
```

Update value and hint for one item.

<details>
<summary>Code:</summary>

```python
def update_item(self, item_id: int, value: str, hint: str) -> bool:
        return self.execute_simple_query(
            "UPDATE items SET value = :value, hint = :hint WHERE _id = :id",
            {"value": value, "hint": hint, "id": item_id},
        )
```

</details>

## 🏛️ Class `SnippetItem`

```python
class SnippetItem
```

One pasteable item stored in the snippets database.

<details>
<summary>Code:</summary>

```python
class SnippetItem:

    item_id: int
    zone: str
    value: str
    hint: str
    created_at: str
    last_used_at: str | None
    sort_index: int
```

</details>

## 🏛️ Class `ZoneSort`

```python
class ZoneSort
```

Persisted sort mode for one zone.

<details>
<summary>Code:</summary>

```python
class ZoneSort:

    mode: SortMode
    descending: bool
```

</details>

## 🔧 Function `utc_now_iso`

```python
def utc_now_iso() -> str
```

Return the current UTC timestamp in ISO-8601 form.

<details>
<summary>Code:</summary>

```python
def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
```

</details>
