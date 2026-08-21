---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ticktick_habits.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `default_ticktick_db_path`](#-function-default_ticktick_db_path)
- [🔧 Function `export_ticktick_habits_json`](#-function-export_ticktick_habits_json)
- [🔧 Function `stamp_to_iso_date`](#-function-stamp_to_iso_date)

</details>

## 🔧 Function `default_ticktick_db_path`

```python
def default_ticktick_db_path() -> Path
```

Return the usual Windows TickTick desktop SQLite path.

Returns:

- `Path`: `%APPDATA%/Tick_Tick/TickTick.db`, or the home-based equivalent.

<details>
<summary>Code:</summary>

```python
def default_ticktick_db_path() -> Path:
    appdata = Path.home() / "AppData" / "Roaming"
    return appdata / TICKTICK_DB_RELATIVE
```

</details>

## 🔧 Function `export_ticktick_habits_json`

```python
def export_ticktick_habits_json(db_path: Path | None = None) -> dict[str, Any]
```

Return habit names and achieved dates from a TickTick SQLite file.

Args:

- `db_path` (`Path | None`): `TickTick.db`. Defaults to the desktop AppData path.

Returns:

- `dict[str, Any]`: JSON-serializable object with `database` and `habits`.

Raises:

- `FileNotFoundError`: When the database file is missing.
- `ValueError`: When habit tables are missing or unreadable.

<details>
<summary>Code:</summary>

```python
def export_ticktick_habits_json(db_path: Path | None = None) -> dict[str, Any]:
    source = Path(db_path) if db_path is not None else default_ticktick_db_path()
    source = source.expanduser().resolve()
    if not source.is_file():
        msg = f"TickTick database not found: {source}"
        raise FileNotFoundError(msg)

    with tempfile.TemporaryDirectory(prefix="hsk-ticktick-") as tmp_dir:
        snapshot = _copy_ticktick_db_snapshot(source, Path(tmp_dir))
        connection = sqlite3.connect(str(snapshot))
        connection.row_factory = sqlite3.Row
        try:
            habits = _load_habits(connection)
            dates_by_id = _load_check_in_dates(connection)
        finally:
            connection.close()

    payload_habits = []
    for habit in habits:
        dates = dates_by_id.get(str(habit["id"]), [])
        payload_habits.append(
            {
                "id": habit["id"],
                "name": habit["name"],
                "type": habit["type"],
                "archived": habit["archived"],
                "archived_time": habit["archived_time"],
                "created_time": habit["created_time"],
                "total_check_ins": habit["total_check_ins"],
                "dates": dates,
                "date_count": len(dates),
            }
        )
    return {
        "database": str(source),
        "habit_count": len(payload_habits),
        "habits": payload_habits,
    }
```

</details>

## 🔧 Function `stamp_to_iso_date`

```python
def stamp_to_iso_date(stamp: object) -> str | None
```

Convert a TickTick `YYYYMMDD` stamp to `YYYY-MM-DD`.

Args:

- `stamp` (`object`): Check-in stamp from `HabitCheckInModel`.

Returns:

- `str | None`: ISO date, or `None` when the stamp is not eight digits.

<details>
<summary>Code:</summary>

```python
def stamp_to_iso_date(stamp: object) -> str | None:
    text = str(stamp or "").strip()
    if len(text) == _STAMP_LENGTH and text.isdigit():
        return f"{text[0:4]}-{text[4:6]}-{text[6:8]}"
    return None
```

</details>
