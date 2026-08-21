"""Tests for reading habits and check-in dates from a TickTick SQLite file."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from harrix_swiss_knife.apps.habits.ticktick_habits import (
    export_ticktick_habits_json,
    stamp_to_iso_date,
)


def _create_ticktick_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(path)) as conn:
        conn.executescript(
            """
            CREATE TABLE HabitModel (
                Id varchar,
                Name varchar,
                Type varchar,
                ArchivedTime datetime,
                CreatedTime datetime,
                TotalCheckIns INTEGER,
                SortOrder bigint
            );
            CREATE TABLE HabitCheckInModel (
                HabitId varchar,
                CheckinStamp varchar
            );
            INSERT INTO HabitModel VALUES
                ('h1', 'English', 'Boolean', '', '2024-08-21 18:00:00', 2, 1),
                ('h2', 'Birthdays', 'Boolean', '2026-05-31 09:58:45', '2024-08-21 18:00:00', 1, 2);
            INSERT INTO HabitCheckInModel VALUES
                ('h1', '20240822'),
                ('h1', '20240821'),
                ('h1', '20240821'),
                ('h2', '20250101');
            """
        )


def test_stamp_to_iso_date() -> None:
    assert stamp_to_iso_date("20240821") == "2024-08-21"
    assert stamp_to_iso_date(20250101) == "2025-01-01"
    assert stamp_to_iso_date("bad") is None
    assert stamp_to_iso_date("") is None


def test_export_ticktick_habits_json(tmp_path: Path) -> None:
    db_path = tmp_path / "TickTick.db"
    _create_ticktick_db(db_path)
    payload = export_ticktick_habits_json(db_path)
    assert payload["habit_count"] == 2
    assert payload["database"] == str(db_path.resolve())
    english, birthdays = payload["habits"]
    assert english["name"] == "English"
    assert english["archived"] is False
    assert english["dates"] == ["2024-08-21", "2024-08-22"]
    assert english["date_count"] == 2
    assert birthdays["name"] == "Birthdays"
    assert birthdays["archived"] is True
    assert birthdays["archived_time"] == "2026-05-31 09:58:45"
    assert birthdays["dates"] == ["2025-01-01"]


def test_export_ticktick_habits_json_ignores_non_done_status(tmp_path: Path) -> None:
    """Only Status=2 check-ins count as Done when the column exists."""
    db_path = tmp_path / "TickTick.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(
            """
            CREATE TABLE HabitModel (
                Id varchar,
                Name varchar,
                Type varchar,
                ArchivedTime datetime,
                CreatedTime datetime,
                TotalCheckIns INTEGER,
                SortOrder bigint
            );
            CREATE TABLE HabitCheckInModel (
                HabitId varchar,
                CheckinStamp varchar,
                Status INTEGER
            );
            INSERT INTO HabitModel VALUES
                ('h1', 'English', 'Boolean', '', '2024-08-21 18:00:00', 1, 1);
            INSERT INTO HabitCheckInModel VALUES
                ('h1', '20240821', 2),
                ('h1', '20240822', 0);
            """
        )
    payload = export_ticktick_habits_json(db_path)
    assert payload["habits"][0]["dates"] == ["2024-08-21"]


def test_export_ticktick_habits_json_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="TickTick database not found"):
        export_ticktick_habits_json(tmp_path / "missing.db")


def test_export_ticktick_habits_json_missing_table(tmp_path: Path) -> None:
    db_path = tmp_path / "TickTick.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("CREATE TABLE Other (Id INTEGER)")
    with pytest.raises(ValueError, match="HabitModel"):
        export_ticktick_habits_json(db_path)
