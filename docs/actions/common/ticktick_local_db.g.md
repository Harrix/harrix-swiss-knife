---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ticktick_local_db.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TickTickCompletion`](#%EF%B8%8F-class-ticktickcompletion)
- [🏛️ Class `TickTickDbError`](#%EF%B8%8F-class-ticktickdberror)
- [🏛️ Class `TickTickProject`](#%EF%B8%8F-class-ticktickproject)
- [🔧 Function `copy_ticktick_db`](#-function-copy_ticktick_db)
- [🔧 Function `default_ticktick_db_path`](#-function-default_ticktick_db_path)
- [🔧 Function `load_completions`](#-function-load_completions)
- [🔧 Function `load_projects`](#-function-load_projects)
- [🔧 Function `load_ticktick_snapshot`](#-function-load_ticktick_snapshot)
- [🔧 Function `open_ticktick_db`](#-function-open_ticktick_db)
- [🔧 Function `parse_ticktick_datetime`](#-function-parse_ticktick_datetime)

</details>

## 🏛️ Class `TickTickCompletion`

```python
class TickTickCompletion
```

One completed TickTick task with a completion timestamp.

<details>
<summary>Code:</summary>

```python
class TickTickCompletion:

    task_id: str
    title: str
    completed_at: datetime
    project_id: str
    project_name: str
    status: int | None = None
```

</details>

## 🏛️ Class `TickTickDbError`

```python
class TickTickDbError(RuntimeError)
```

Raised when the local TickTick database cannot be opened or queried.

<details>
<summary>Code:</summary>

```python
class TickTickDbError(RuntimeError):
```

</details>

## 🏛️ Class `TickTickProject`

```python
class TickTickProject
```

One TickTick list/project.

<details>
<summary>Code:</summary>

```python
class TickTickProject:

    id: str
    name: str
    kind: str | None = None
    closed: int | None = None
    delete_status: int = 0
```

</details>

## 🔧 Function `copy_ticktick_db`

```python
def copy_ticktick_db(src: Path, *, dest_dir: Path | None = None) -> Path
```

Copy `TickTick.db` plus `-wal`/`-shm` into a temp folder for safe reads.

Args:

- `src` (`Path`): Live TickTick database path.
- `dest_dir` (`Path | None`): Destination directory. When `None`, creates a
  new temporary directory.

Returns:

- `Path`: Path to the copied `.db` file.

Raises:

- [`TickTickDbError`](#%EF%B8%8F-class-ticktickdberror): If `src` does not exist.

<details>
<summary>Code:</summary>

```python
def copy_ticktick_db(src: Path, *, dest_dir: Path | None = None) -> Path:
    if not src.is_file():
        msg = f"TickTick database not found:\n{src}"
        raise TickTickDbError(msg)

    target_dir = Path(tempfile.mkdtemp(prefix="hsk_ticktick_")) if dest_dir is None else Path(dest_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / src.name
    shutil.copy2(src, dest)
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(src) + suffix)
        if sidecar.is_file():
            shutil.copy2(sidecar, Path(str(dest) + suffix))
    return dest
```

</details>

## 🔧 Function `default_ticktick_db_path`

```python
def default_ticktick_db_path(*, appdata: str | Path | None = None) -> Path
```

Return the default Windows TickTick desktop database path.

Args:

- `appdata` (`str | Path | None`): Override for `%APPDATA%`. When `None`,
  uses the process environment.

Returns:

- `Path`: `%APPDATA%\Tick_Tick\TickTick.db`

<details>
<summary>Code:</summary>

```python
def default_ticktick_db_path(*, appdata: str | Path | None = None) -> Path:
    root = Path(appdata) if appdata is not None else Path(os.environ.get("APPDATA", ""))
    return root / "Tick_Tick" / "TickTick.db"
```

</details>

## 🔧 Function `load_completions`

```python
def load_completions(conn: sqlite3.Connection, *, project_id: str | None = None) -> list[TickTickCompletion]
```

Load completed tasks that have a non-empty `completedTime`.

Soft-deleted tasks (`deleted != 0`) are excluded. Any status with a
completion timestamp is kept (mostly `status = 2`).

<details>
<summary>Code:</summary>

```python
def load_completions(
    conn: sqlite3.Connection,
    *,
    project_id: str | None = None,
) -> list[TickTickCompletion]:
    base_query = """
        SELECT
            t.id,
            t.title,
            t.completedTime,
            t.projectId,
            COALESCE(p.name, ''),
            t.status
        FROM TaskModel AS t
        LEFT JOIN ProjectModel AS p ON t.projectId = p.id
        WHERE t.completedTime IS NOT NULL
          AND TRIM(t.completedTime) != ''
          AND COALESCE(t.deleted, 0) = 0
    """
    if project_id:
        query = base_query + " AND t.projectId = ? ORDER BY t.completedTime ASC"
        rows = conn.execute(query, (project_id,))
    else:
        query = base_query + " ORDER BY t.completedTime ASC"
        rows = conn.execute(query)

    completions: list[TickTickCompletion] = []
    for row in rows:
        completed_at = parse_ticktick_datetime(str(row[2]))
        if completed_at is None:
            continue
        task_id = str(row[0] or "")
        title = str(row[1] or "").strip() or "(untitled)"
        proj_id = str(row[3] or "")
        proj_name = str(row[4] or "").strip() or proj_id or "—"
        status = int(row[5]) if row[5] is not None else None
        completions.append(
            TickTickCompletion(
                task_id=task_id,
                title=title,
                completed_at=completed_at,
                project_id=proj_id,
                project_name=proj_name,
                status=status,
            ),
        )
    return completions
```

</details>

## 🔧 Function `load_projects`

```python
def load_projects(conn: sqlite3.Connection) -> list[TickTickProject]
```

Return TickTick lists ordered for a filter combo (active first).

<details>
<summary>Code:</summary>

```python
def load_projects(conn: sqlite3.Connection) -> list[TickTickProject]:
    rows = conn.execute(
        """
        SELECT id, name, kind, closed, COALESCE(delete_status, 0) AS delete_status
        FROM ProjectModel
        WHERE COALESCE(delete_status, 0) = 0
        ORDER BY
            CASE WHEN closed IS NULL OR closed = 0 THEN 0 ELSE 1 END,
            sortOrder ASC,
            name COLLATE NOCASE ASC
        """,
    ).fetchall()
    projects: list[TickTickProject] = []
    for row in rows:
        project_id = str(row[0] or "")
        name = str(row[1] or "").strip() or project_id
        if not project_id:
            continue
        projects.append(
            TickTickProject(
                id=project_id,
                name=name,
                kind=str(row[2]) if row[2] is not None else None,
                closed=int(row[3]) if row[3] is not None else None,
                delete_status=int(row[4] or 0),
            ),
        )
    return projects
```

</details>

## 🔧 Function `load_ticktick_snapshot`

```python
def load_ticktick_snapshot(src: Path | None = None) -> tuple[list[TickTickProject], list[TickTickCompletion], Path]
```

Copy the live DB and return projects plus all completions.

Returns:

- `(projects, completions, source_path)` where `source_path` is the live DB.

<details>
<summary>Code:</summary>

```python
def load_ticktick_snapshot(
    src: Path | None = None,
) -> tuple[list[TickTickProject], list[TickTickCompletion], Path]:
    db_src = Path(src) if src is not None else default_ticktick_db_path()
    copied = copy_ticktick_db(db_src)
    try:
        with open_ticktick_db(copied) as conn:
            projects = load_projects(conn)
            completions = load_completions(conn)
    finally:
        _cleanup_copied_db(copied)
    return projects, completions, db_src
```

</details>

## 🔧 Function `open_ticktick_db`

```python
def open_ticktick_db(db_path: Path) -> sqlite3.Connection
```

Open a copied TickTick database in read-only URI mode.

<details>
<summary>Code:</summary>

```python
def open_ticktick_db(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path.as_posix()}?mode=ro"
    try:
        return sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        msg = f"Failed to open TickTick database:\n{db_path}\n{exc}"
        raise TickTickDbError(msg) from exc
```

</details>

## 🔧 Function `parse_ticktick_datetime`

```python
def parse_ticktick_datetime(value: str) -> datetime | None
```

Parse TickTick `completedTime` strings into naive local datetimes.

<details>
<summary>Code:</summary>

```python
def parse_ticktick_datetime(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(text, fmt)  # noqa: DTZ007 — TickTick stores local naive stamps
        except ValueError:
            continue
    iso_text = f"{text[:-1]}+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(iso_text)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return parsed.astimezone().replace(tzinfo=None)
    return parsed
```

</details>
