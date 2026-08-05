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
  - [⚙️ Method `add_bin_assignment`](#%EF%B8%8F-method-add_bin_assignment)
  - [⚙️ Method `get_bin_ids_for_path`](#%EF%B8%8F-method-get_bin_ids_for_path)
  - [⚙️ Method `get_current_path_after_moves`](#%EF%B8%8F-method-get_current_path_after_moves)
  - [⚙️ Method `is_reviewed`](#%EF%B8%8F-method-is_reviewed)
  - [⚙️ Method `list_reviewed_paths`](#%EF%B8%8F-method-list_reviewed_paths)
  - [⚙️ Method `mark_deleted`](#%EF%B8%8F-method-mark_deleted)
  - [⚙️ Method `mark_reviewed`](#%EF%B8%8F-method-mark_reviewed)
  - [⚙️ Method `path_was_moved`](#%EF%B8%8F-method-path_was_moved)
  - [⚙️ Method `reviewed_count`](#%EF%B8%8F-method-reviewed_count)
  - [⚙️ Method `unmark_reviewed`](#%EF%B8%8F-method-unmark_reviewed)
- [🔧 Function `normalize_media_path`](#-function-normalize_media_path)

</details>

## 🏛️ Class `DatabaseManager`

```python
class DatabaseManager(QtSqliteDatabaseManagerBase)
```

Manage Media Sorter history (reviewed files, bin assignments, deletes).

<details>
<summary>Code:</summary>

```python
class DatabaseManager(QtSqliteDatabaseManagerBase):

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in `db_filename`."""
        super().__init__(prefix="media_sorter_db", db_filename=db_filename)

    def add_bin_assignment(
        self,
        path: str | Path,
        bin_id: str,
        dest_path: str | Path,
        mode: str,
    ) -> bool:
        """Record that `path` was copied/moved into a config bin."""
        normalized = normalize_media_path(path)
        dest = normalize_media_path(dest_path)
        mode_norm = mode.strip().lower()
        if mode_norm not in {"copy", "move"}:
            logger.error("Invalid bin assignment mode: %s", mode)
            return False
        query = """
            INSERT INTO bin_assignments (path, bin_id, dest_path, mode, assigned_at)
            VALUES (:path, :bin_id, :dest_path, :mode, :assigned_at)
            ON CONFLICT(path, bin_id) DO UPDATE SET
                dest_path = excluded.dest_path,
                mode = excluded.mode,
                assigned_at = excluded.assigned_at
        """
        return self.execute_simple_query(
            query,
            {
                "path": normalized,
                "bin_id": bin_id,
                "dest_path": dest,
                "mode": mode_norm,
                "assigned_at": _utc_now_iso(),
            },
        )

    def get_bin_ids_for_path(self, path: str | Path) -> set[str]:
        """Return bin IDs already assigned for `path`."""
        rows = self.get_rows(
            "SELECT bin_id FROM bin_assignments WHERE path = :path",
            {"path": normalize_media_path(path)},
        )
        return {str(row[0]) for row in rows if row}

    def get_current_path_after_moves(self, original_path: str | Path) -> str:
        """Follow move assignment chain until an existing file is found."""
        current = normalize_media_path(original_path)
        seen: set[str] = set()
        while current not in seen:
            seen.add(current)
            if Path(current).is_file():
                return current
            rows = self.get_rows(
                """
                SELECT dest_path FROM bin_assignments
                WHERE path = :path AND mode = 'move'
                ORDER BY assigned_at DESC
                LIMIT 1
                """,
                {"path": current},
            )
            if not rows or not rows[0] or not rows[0][0]:
                break
            current = normalize_media_path(str(rows[0][0]))
        return current

    def is_reviewed(self, path: str | Path) -> bool:
        """Return whether `path` is marked reviewed."""
        rows = self.get_rows(
            "SELECT 1 FROM reviewed_files WHERE path = :path LIMIT 1",
            {"path": normalize_media_path(path)},
        )
        return bool(rows)

    def list_reviewed_paths(self) -> set[str]:
        """Return all reviewed absolute paths."""
        rows = self.get_rows("SELECT path FROM reviewed_files")
        return {str(row[0]) for row in rows if row and row[0]}

    def mark_deleted(self, path: str | Path, size: int | None = None) -> bool:
        """Record a file moved to the OS trash and mark it reviewed."""
        normalized = normalize_media_path(path)
        size_value = size
        if size_value is None:
            try:
                size_value = Path(normalized).stat().st_size
            except OSError:
                size_value = None
        ok_delete = self.execute_simple_query(
            """
            INSERT INTO deleted_files (path, deleted_at, size)
            VALUES (:path, :deleted_at, :size)
            """,
            {"path": normalized, "deleted_at": _utc_now_iso(), "size": size_value},
        )
        ok_reviewed = self.mark_reviewed(normalized)
        return ok_delete and ok_reviewed

    def mark_reviewed(self, path: str | Path) -> bool:
        """Mark `path` as reviewed (upsert)."""
        normalized = normalize_media_path(path)
        size: int | None = None
        mtime: float | None = None
        try:
            stat = Path(normalized).stat()
            size = int(stat.st_size)
            mtime = float(stat.st_mtime)
        except OSError:
            pass
        query = """
            INSERT INTO reviewed_files (path, reviewed_at, size, mtime)
            VALUES (:path, :reviewed_at, :size, :mtime)
            ON CONFLICT(path) DO UPDATE SET
                reviewed_at = excluded.reviewed_at,
                size = COALESCE(excluded.size, reviewed_files.size),
                mtime = COALESCE(excluded.mtime, reviewed_files.mtime)
        """
        return self.execute_simple_query(
            query,
            {
                "path": normalized,
                "reviewed_at": _utc_now_iso(),
                "size": size,
                "mtime": mtime,
            },
        )

    def path_was_moved(self, path: str | Path) -> bool:
        """Return whether `path` was a source or destination of a prior move."""
        normalized = normalize_media_path(path)
        rows = self.get_rows(
            """
            SELECT 1 FROM bin_assignments
            WHERE mode = 'move' AND (path = :path OR dest_path = :path)
            LIMIT 1
            """,
            {"path": normalized},
        )
        return bool(rows)

    def reviewed_count(self) -> int:
        """Return number of reviewed files."""
        rows = self.get_rows("SELECT COUNT(*) FROM reviewed_files")
        if not rows or not rows[0]:
            return 0
        return int(rows[0][0] or 0)

    def unmark_reviewed(self, path: str | Path) -> bool:
        """Remove reviewed mark for `path`."""
        return self.execute_simple_query(
            "DELETE FROM reviewed_files WHERE path = :path",
            {"path": normalize_media_path(path)},
        )
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
        super().__init__(prefix="media_sorter_db", db_filename=db_filename)
```

</details>

### ⚙️ Method `add_bin_assignment`

```python
def add_bin_assignment(self, path: str | Path, bin_id: str, dest_path: str | Path, mode: str) -> bool
```

Record that `path` was copied/moved into a config bin.

<details>
<summary>Code:</summary>

```python
def add_bin_assignment(
        self,
        path: str | Path,
        bin_id: str,
        dest_path: str | Path,
        mode: str,
    ) -> bool:
        normalized = normalize_media_path(path)
        dest = normalize_media_path(dest_path)
        mode_norm = mode.strip().lower()
        if mode_norm not in {"copy", "move"}:
            logger.error("Invalid bin assignment mode: %s", mode)
            return False
        query = """
            INSERT INTO bin_assignments (path, bin_id, dest_path, mode, assigned_at)
            VALUES (:path, :bin_id, :dest_path, :mode, :assigned_at)
            ON CONFLICT(path, bin_id) DO UPDATE SET
                dest_path = excluded.dest_path,
                mode = excluded.mode,
                assigned_at = excluded.assigned_at
        """
        return self.execute_simple_query(
            query,
            {
                "path": normalized,
                "bin_id": bin_id,
                "dest_path": dest,
                "mode": mode_norm,
                "assigned_at": _utc_now_iso(),
            },
        )
```

</details>

### ⚙️ Method `get_bin_ids_for_path`

```python
def get_bin_ids_for_path(self, path: str | Path) -> set[str]
```

Return bin IDs already assigned for `path`.

<details>
<summary>Code:</summary>

```python
def get_bin_ids_for_path(self, path: str | Path) -> set[str]:
        rows = self.get_rows(
            "SELECT bin_id FROM bin_assignments WHERE path = :path",
            {"path": normalize_media_path(path)},
        )
        return {str(row[0]) for row in rows if row}
```

</details>

### ⚙️ Method `get_current_path_after_moves`

```python
def get_current_path_after_moves(self, original_path: str | Path) -> str
```

Follow move assignment chain until an existing file is found.

<details>
<summary>Code:</summary>

```python
def get_current_path_after_moves(self, original_path: str | Path) -> str:
        current = normalize_media_path(original_path)
        seen: set[str] = set()
        while current not in seen:
            seen.add(current)
            if Path(current).is_file():
                return current
            rows = self.get_rows(
                """
                SELECT dest_path FROM bin_assignments
                WHERE path = :path AND mode = 'move'
                ORDER BY assigned_at DESC
                LIMIT 1
                """,
                {"path": current},
            )
            if not rows or not rows[0] or not rows[0][0]:
                break
            current = normalize_media_path(str(rows[0][0]))
        return current
```

</details>

### ⚙️ Method `is_reviewed`

```python
def is_reviewed(self, path: str | Path) -> bool
```

Return whether `path` is marked reviewed.

<details>
<summary>Code:</summary>

```python
def is_reviewed(self, path: str | Path) -> bool:
        rows = self.get_rows(
            "SELECT 1 FROM reviewed_files WHERE path = :path LIMIT 1",
            {"path": normalize_media_path(path)},
        )
        return bool(rows)
```

</details>

### ⚙️ Method `list_reviewed_paths`

```python
def list_reviewed_paths(self) -> set[str]
```

Return all reviewed absolute paths.

<details>
<summary>Code:</summary>

```python
def list_reviewed_paths(self) -> set[str]:
        rows = self.get_rows("SELECT path FROM reviewed_files")
        return {str(row[0]) for row in rows if row and row[0]}
```

</details>

### ⚙️ Method `mark_deleted`

```python
def mark_deleted(self, path: str | Path, size: int | None = None) -> bool
```

Record a file moved to the OS trash and mark it reviewed.

<details>
<summary>Code:</summary>

```python
def mark_deleted(self, path: str | Path, size: int | None = None) -> bool:
        normalized = normalize_media_path(path)
        size_value = size
        if size_value is None:
            try:
                size_value = Path(normalized).stat().st_size
            except OSError:
                size_value = None
        ok_delete = self.execute_simple_query(
            """
            INSERT INTO deleted_files (path, deleted_at, size)
            VALUES (:path, :deleted_at, :size)
            """,
            {"path": normalized, "deleted_at": _utc_now_iso(), "size": size_value},
        )
        ok_reviewed = self.mark_reviewed(normalized)
        return ok_delete and ok_reviewed
```

</details>

### ⚙️ Method `mark_reviewed`

```python
def mark_reviewed(self, path: str | Path) -> bool
```

Mark `path` as reviewed (upsert).

<details>
<summary>Code:</summary>

```python
def mark_reviewed(self, path: str | Path) -> bool:
        normalized = normalize_media_path(path)
        size: int | None = None
        mtime: float | None = None
        try:
            stat = Path(normalized).stat()
            size = int(stat.st_size)
            mtime = float(stat.st_mtime)
        except OSError:
            pass
        query = """
            INSERT INTO reviewed_files (path, reviewed_at, size, mtime)
            VALUES (:path, :reviewed_at, :size, :mtime)
            ON CONFLICT(path) DO UPDATE SET
                reviewed_at = excluded.reviewed_at,
                size = COALESCE(excluded.size, reviewed_files.size),
                mtime = COALESCE(excluded.mtime, reviewed_files.mtime)
        """
        return self.execute_simple_query(
            query,
            {
                "path": normalized,
                "reviewed_at": _utc_now_iso(),
                "size": size,
                "mtime": mtime,
            },
        )
```

</details>

### ⚙️ Method `path_was_moved`

```python
def path_was_moved(self, path: str | Path) -> bool
```

Return whether `path` was a source or destination of a prior move.

<details>
<summary>Code:</summary>

```python
def path_was_moved(self, path: str | Path) -> bool:
        normalized = normalize_media_path(path)
        rows = self.get_rows(
            """
            SELECT 1 FROM bin_assignments
            WHERE mode = 'move' AND (path = :path OR dest_path = :path)
            LIMIT 1
            """,
            {"path": normalized},
        )
        return bool(rows)
```

</details>

### ⚙️ Method `reviewed_count`

```python
def reviewed_count(self) -> int
```

Return number of reviewed files.

<details>
<summary>Code:</summary>

```python
def reviewed_count(self) -> int:
        rows = self.get_rows("SELECT COUNT(*) FROM reviewed_files")
        if not rows or not rows[0]:
            return 0
        return int(rows[0][0] or 0)
```

</details>

### ⚙️ Method `unmark_reviewed`

```python
def unmark_reviewed(self, path: str | Path) -> bool
```

Remove reviewed mark for `path`.

<details>
<summary>Code:</summary>

```python
def unmark_reviewed(self, path: str | Path) -> bool:
        return self.execute_simple_query(
            "DELETE FROM reviewed_files WHERE path = :path",
            {"path": normalize_media_path(path)},
        )
```

</details>

## 🔧 Function `normalize_media_path`

```python
def normalize_media_path(path: str | Path) -> str
```

Return a stable absolute path string for DB keys.

<details>
<summary>Code:</summary>

```python
def normalize_media_path(path: str | Path) -> str:
    return str(Path(path).expanduser().resolve())
```

</details>
