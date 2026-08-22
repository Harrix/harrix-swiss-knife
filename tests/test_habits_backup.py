"""Tests for habit tracker plus TickTick backup."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.habits.database_manager import DatabaseManager
from harrix_swiss_knife.apps.habits.habits_backup import export_hsk_habits_json, write_habits_backup

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src/harrix_swiss_knife/apps/habits/recover.sql"


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
                ('h1', '20240821');
            """
        )


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Qt SQL drivers."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture
def habits_db(tmp_path: Path, qapp: QApplication) -> Iterator[DatabaseManager]:  # noqa: ARG001
    """Create an empty habits SQLite database for tests."""
    db_path = tmp_path / "habits.sqlite"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))
    db = DatabaseManager(str(db_path))
    yield db
    db.close()


def test_upsert_habit_checkins_inserts_and_updates(habits_db: DatabaseManager) -> None:
    """Batch upsert inserts missing days, updates existing, and drops extra rows."""
    assert habits_db.add_habit("Walk", is_bool=True, emoji="🚶")
    walk_id = int(habits_db.get_habits()[0][0])
    assert habits_db.add_process_habit_record(walk_id, 0, "2026-08-01")
    assert habits_db.add_process_habit_record(walk_id, 0, "2026-08-01")
    written = habits_db.upsert_habit_checkins(
        [
            (walk_id, "2026-08-01", 1),
            (walk_id, "2026-08-02", 0),
            (walk_id, "2026-08-03", 1),
        ]
    )
    assert written == 3
    assert habits_db.get_habit_value_on_date(walk_id, "2026-08-01") == 1
    assert habits_db.get_habit_value_on_date(walk_id, "2026-08-02") == 0
    assert habits_db.get_habit_value_on_date(walk_id, "2026-08-03") == 1
    rows = habits_db.get_rows(
        "SELECT COUNT(*) FROM process_habits WHERE _id_habit = :id AND date = :d",
        {"id": walk_id, "d": "2026-08-01"},
    )
    assert rows[0][0] == 1


def test_export_hsk_habits_json_includes_values(habits_db: DatabaseManager) -> None:
    """HSK backup lists habit metadata and the latest value per date."""
    assert habits_db.add_habit("Walk", is_bool=True, emoji="🚶")
    assert habits_db.add_habit("Pages", is_bool=False, emoji="📚")
    walk_id = int(habits_db.get_habits()[0][0])
    pages_id = int(habits_db.get_habits()[1][0])
    assert habits_db.add_process_habit_record(walk_id, 1, "2026-08-01")
    assert habits_db.add_process_habit_record(pages_id, 3, "2026-08-02")
    assert habits_db.add_process_habit_record(pages_id, 5, "2026-08-02")

    payload = export_hsk_habits_json(habits_db, database_path="habits.sqlite")
    assert payload["database"] == "habits.sqlite"
    assert payload["habit_count"] == 2
    walk, pages = payload["habits"]
    assert walk["name"] == "Walk"
    assert walk["emoji"] == "🚶"
    assert walk["is_bool"] is True
    assert walk["dates"] == ["2026-08-01"]
    assert walk["values"] == {"2026-08-01": 1}
    assert pages["name"] == "Pages"
    assert pages["is_bool"] is False
    assert pages["values"] == {"2026-08-02": 5}


def test_write_habits_backup_writes_hsk_and_ticktick(habits_db: DatabaseManager, tmp_path: Path) -> None:
    """Backup folder contains HSK JSON/DB, TickTick JSON, and a manifest."""
    assert habits_db.add_habit("Walk", is_bool=True, emoji="🚶")
    ticktick_db = tmp_path / "TickTick.db"
    _create_ticktick_db(ticktick_db)
    created = datetime(2026, 8, 21, 23, 56, tzinfo=UTC)
    folder, error = write_habits_backup(
        tmp_path,
        hsk_db_path=tmp_path / "habits.sqlite",
        db_manager=habits_db,
        ticktick_db_path=ticktick_db,
        created_at=created,
    )
    assert error is None
    assert folder.name == "habits-backup-2026-08-21_235600"
    assert (folder / "hsk-habits.db").is_file()
    hsk = json.loads((folder / "hsk-habits.json").read_text(encoding="utf-8"))
    ticktick = json.loads((folder / "ticktick-habits.json").read_text(encoding="utf-8"))
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert hsk["habit_count"] == 1
    assert ticktick["habit_count"] == 2
    assert manifest["hsk_habit_count"] == 1
    assert manifest["ticktick_habit_count"] == 2
    assert manifest["ticktick_error"] is None


def test_write_habits_backup_records_ticktick_error(habits_db: DatabaseManager, tmp_path: Path) -> None:
    """HSK backup is still written when TickTick database is missing."""
    folder, error = write_habits_backup(
        tmp_path,
        hsk_db_path=tmp_path / "habits.sqlite",
        db_manager=habits_db,
        ticktick_db_path=tmp_path / "missing.db",
        created_at=datetime(2026, 8, 21, 12, 0, tzinfo=UTC),
    )
    assert error is not None
    assert "TickTick database not found" in error
    assert (folder / "hsk-habits.json").is_file()
    assert not (folder / "ticktick-habits.json").exists()
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["ticktick_habit_count"] is None
    assert manifest["ticktick_error"] == error
