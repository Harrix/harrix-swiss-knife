---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habits_backup.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `export_hsk_habits_json`](#-function-export_hsk_habits_json)
- [🔧 Function `write_habits_backup`](#-function-write_habits_backup)

</details>

## 🔧 Function `export_hsk_habits_json`

```python
def export_hsk_habits_json(db_manager: DatabaseManager, *, database_path: str = '') -> dict[str, Any]
```

Return habit names, flags, and check-in values from the habit tracker.

Args:

- `db_manager` (`DatabaseManager`): Open habits database.
- `database_path` (`str`): Path recorded in the payload. Defaults to `""`.

Returns:

- `dict[str, Any]`: JSON-serializable object with `database` and `habits`.

<details>
<summary>Code:</summary>

```python
def export_hsk_habits_json(db_manager: DatabaseManager, *, database_path: str = "") -> dict[str, Any]:
    values_by_id: dict[int, dict[str, int]] = {}
    for row in db_manager.get_rows("SELECT _id_habit, value, date FROM process_habits ORDER BY date ASC, _id ASC"):
        if not row or row[0] is None or row[1] is None or not row[2]:
            continue
        try:
            habit_id = int(row[0])
            value = int(row[1])
        except (TypeError, ValueError):
            continue
        values_by_id.setdefault(habit_id, {})[str(row[2])] = value

    habits: list[dict[str, Any]] = []
    for row in db_manager.get_all_habits():
        fields = _habit_export_fields(row)
        if fields is None:
            continue
        habit_id, name, is_bool, archived, emoji = fields
        values = values_by_id.get(habit_id, {})
        dates = sorted(values)
        habits.append(
            {
                "id": habit_id,
                "name": name,
                "emoji": emoji,
                "is_bool": is_bool,
                "archived": archived,
                "values": values,
                "dates": dates,
                "date_count": len(dates),
            }
        )
    return {
        "database": database_path,
        "habit_count": len(habits),
        "habits": habits,
    }
```

</details>

## 🔧 Function `write_habits_backup`

```python
def write_habits_backup(dest_parent: Path, *, hsk_db_path: Path, db_manager: DatabaseManager, ticktick_db_path: Path | None = None, created_at: datetime | None = None) -> tuple[Path, str | None]
```

Write a dated folder with HSK habits, the SQLite file, and TickTick habits.

Args:

- `dest_parent` (`Path`): Folder that will contain the new backup directory.
- `hsk_db_path` (`Path`): Live habit tracker SQLite file.
- `db_manager` (`DatabaseManager`): Open habits database.
- `ticktick_db_path` (`Path | None`): TickTick SQLite file. Defaults to the desktop path.
- `created_at` (`datetime | None`): Backup timestamp. Defaults to now.

Returns:

- `tuple[Path, str | None]`: Created folder and an optional TickTick error message.

<details>
<summary>Code:</summary>

```python
def write_habits_backup(
    dest_parent: Path,
    *,
    hsk_db_path: Path,
    db_manager: DatabaseManager,
    ticktick_db_path: Path | None = None,
    created_at: datetime | None = None,
) -> tuple[Path, str | None]:
    created = created_at or datetime.now(UTC).astimezone()
    folder = dest_parent / f"habits-backup-{created.strftime('%Y-%m-%d_%H%M%S')}"
    folder.mkdir(parents=True, exist_ok=False)

    source = Path(hsk_db_path)
    hsk_payload = export_hsk_habits_json(db_manager, database_path=str(source))
    _write_json(folder / "hsk-habits.json", hsk_payload)
    _copy_sqlite_snapshot(source, folder / "hsk-habits.db")

    ticktick_payload: dict[str, Any] | None = None
    ticktick_error: str | None = None
    try:
        ticktick_payload = export_ticktick_habits_json(ticktick_db_path)
        _write_json(folder / "ticktick-habits.json", ticktick_payload)
    except (FileNotFoundError, OSError, ValueError, sqlite3.Error) as exc:
        ticktick_error = str(exc)

    _write_json(
        folder / "manifest.json",
        {
            "created": created.isoformat(timespec="seconds"),
            "hsk_database": str(source),
            "hsk_habit_count": hsk_payload["habit_count"],
            "ticktick_habit_count": None if ticktick_payload is None else ticktick_payload.get("habit_count"),
            "ticktick_error": ticktick_error,
        },
    )
    return folder, ticktick_error
```

</details>
