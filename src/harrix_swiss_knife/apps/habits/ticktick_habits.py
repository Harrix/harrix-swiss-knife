"""Read habit names and check-in dates from a local TickTick desktop database."""

from __future__ import annotations

import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

TICKTICK_DB_RELATIVE = Path("Tick_Tick") / "TickTick.db"
_STAMP_LENGTH = 8
# TickTick task/habit Status: Normal=0, Completed=2 (same as Open API tasks).
_TICKTICK_DONE_STATUS = 2


def default_ticktick_db_path() -> Path:
    """Return the usual Windows TickTick desktop SQLite path.

    Returns:

    - `Path`: `%APPDATA%/Tick_Tick/TickTick.db`, or the home-based equivalent.

    """
    appdata = Path.home() / "AppData" / "Roaming"
    return appdata / TICKTICK_DB_RELATIVE


def export_ticktick_habits_json(db_path: Path | None = None) -> dict[str, Any]:
    """Return habit names and achieved dates from a TickTick SQLite file.

    Only check-ins with Status completed (`2`) count as Done. Rows without a
    `Status` column are treated as Done (legacy test snapshots).

    Args:

    - `db_path` (`Path | None`): `TickTick.db`. Defaults to the desktop AppData path.

    Returns:

    - `dict[str, Any]`: JSON-serializable object with `database` and `habits`.

    Raises:

    - `FileNotFoundError`: When the database file is missing.
    - `ValueError`: When habit tables are missing or unreadable.

    """
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


def stamp_to_iso_date(stamp: object) -> str | None:
    """Convert a TickTick `YYYYMMDD` stamp to `YYYY-MM-DD`.

    Args:

    - `stamp` (`object`): Check-in stamp from `HabitCheckInModel`.

    Returns:

    - `str | None`: ISO date, or `None` when the stamp is not eight digits.

    """
    text = str(stamp or "").strip()
    if len(text) == _STAMP_LENGTH and text.isdigit():
        return f"{text[0:4]}-{text[4:6]}-{text[6:8]}"
    return None


def _copy_ticktick_db_snapshot(source: Path, tmp_dir: Path) -> Path:
    """Copy `TickTick.db` plus WAL/SHM so an open TickTick app is not required.

    Args:

    - `source` (`Path`): Live TickTick SQLite file.
    - `tmp_dir` (`Path`): Empty folder for the snapshot.

    Returns:

    - `Path`: Copied `TickTick.db` inside `tmp_dir`.

    """
    snapshot = tmp_dir / "TickTick.db"
    shutil.copy2(source, snapshot)
    for suffix in ("-wal", "-shm"):
        sidecar = source.with_name(source.name + suffix)
        if sidecar.is_file():
            shutil.copy2(sidecar, tmp_dir / f"TickTick.db{suffix}")
    return snapshot


def _load_check_in_dates(connection: sqlite3.Connection) -> dict[str, list[str]]:
    """Return Done ISO dates grouped by habit ID, sorted and unique."""
    _require_table(connection, "HabitCheckInModel")
    columns = _table_columns(connection, "HabitCheckInModel")
    has_status = "Status" in columns
    if has_status:
        rows = connection.execute(
            """
            SELECT HabitId, CheckinStamp
            FROM HabitCheckInModel
            WHERE CheckinStamp IS NOT NULL
              AND TRIM(CAST(CheckinStamp AS TEXT)) != ''
              AND Status = ?
            """,
            (_TICKTICK_DONE_STATUS,),
        )
    else:
        rows = connection.execute(
            """
            SELECT HabitId, CheckinStamp
            FROM HabitCheckInModel
            WHERE CheckinStamp IS NOT NULL AND TRIM(CAST(CheckinStamp AS TEXT)) != ''
            """
        )
    grouped: dict[str, set[str]] = {}
    for row in rows:
        iso = stamp_to_iso_date(row["CheckinStamp"])
        if iso is None:
            continue
        grouped.setdefault(str(row["HabitId"]), set()).add(iso)
    return {habit_id: sorted(dates) for habit_id, dates in grouped.items()}


def _load_habits(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return habit metadata ordered like the TickTick list."""
    _require_table(connection, "HabitModel")
    rows = connection.execute(
        """
        SELECT Id, Name, Type, ArchivedTime, CreatedTime, TotalCheckIns, SortOrder
        FROM HabitModel
        ORDER BY SortOrder ASC, Name COLLATE NOCASE ASC
        """
    )
    habits: list[dict[str, Any]] = []
    for row in rows:
        archived_time = str(row["ArchivedTime"] or "").strip() or None
        total = row["TotalCheckIns"]
        habits.append(
            {
                "id": str(row["Id"] or ""),
                "name": str(row["Name"] or ""),
                "type": str(row["Type"] or ""),
                "archived": archived_time is not None,
                "archived_time": archived_time,
                "created_time": str(row["CreatedTime"] or "").strip() or None,
                "total_check_ins": int(total) if total is not None else 0,
            }
        )
    return habits


def _require_table(connection: sqlite3.Connection, table_name: str) -> None:
    """Raise when `table_name` is not in the SQLite file."""
    found = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    if found is None:
        msg = f"TickTick database has no {table_name} table."
        raise ValueError(msg)


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    """Return column names for `table_name`."""
    return {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table_name})")}
