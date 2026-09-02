"""Tests for syncing a sport habit from Fitness process records."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu

from harrix_swiss_knife.apps.common.apps_config import (
    DEFAULT_HABITS_SPORT_LOOKBACK_DAYS,
    HABITS_SPORT_HABIT_NAME_KEY,
    HABITS_SPORT_LOOKBACK_DAYS_KEY,
    get_habits_sport_habit_name,
    get_habits_sport_lookback_days,
    set_habits_sport_habit_name,
)
from harrix_swiss_knife.apps.habits.dashboard import HabitDashboardWidget
from harrix_swiss_knife.apps.habits.database_manager import DatabaseManager
from harrix_swiss_knife.apps.habits.sport_habit_sync import (
    build_sport_checkins,
    find_sport_habit,
    habit_names_match,
    iter_iso_dates,
    load_dates_with_non_steps_exercises,
    lookback_date_range,
    resolve_fitness_db_path,
    sync_sport_habit_from_fitness,
)

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src/harrix_swiss_knife/apps/habits/recover.sql"


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture
def habits_db(tmp_path: Path, qapp: QApplication) -> Iterator[DatabaseManager]:  # noqa: ARG001
    db_path = tmp_path / "habits.sqlite"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))
    db = DatabaseManager(str(db_path))
    yield db
    db.close()


def _write_fitness_db(path: Path, rows: list[tuple[str, str]]) -> None:
    connection = sqlite3.connect(str(path))
    try:
        connection.execute("CREATE TABLE exercises (_id INTEGER PRIMARY KEY, name TEXT)")
        connection.execute("CREATE TABLE process (_id INTEGER PRIMARY KEY, _id_exercises INTEGER, date TEXT)")
        names = sorted({name for name, _date in rows})
        for index, name in enumerate(names, start=1):
            connection.execute("INSERT INTO exercises (_id, name) VALUES (?, ?)", (index, name))
        name_ids = {name: index for index, name in enumerate(names, start=1)}
        for name, day in rows:
            connection.execute(
                "INSERT INTO process (_id_exercises, date) VALUES (?, ?)",
                (name_ids[name], day),
            )
        connection.commit()
    finally:
        connection.close()


def test_habit_names_match_ignores_case_and_spaces() -> None:
    assert habit_names_match("Sport", "sport")
    assert habit_names_match("  Sport  ", "SPORT")
    assert not habit_names_match("", "Sport")
    assert not habit_names_match("Sport", "Walk")


def test_find_sport_habit_is_case_insensitive() -> None:
    habits = [[1, "Walk"], [2, "Sport"]]
    assert find_sport_habit(habits, "sport") == (2, "Sport")
    assert find_sport_habit(habits, "") is None
    assert find_sport_habit(habits, "Missing") is None


def test_lookback_and_iter_dates() -> None:
    assert lookback_date_range(date(2026, 9, 10), 31) == ("2026-08-11", "2026-09-10")
    assert iter_iso_dates("2026-09-01", "2026-09-03") == ["2026-09-01", "2026-09-02", "2026-09-03"]
    assert iter_iso_dates("2026-09-03", "2026-09-01") == []


def test_build_sport_checkins_marks_only_non_steps_days() -> None:
    rows = build_sport_checkins(7, "2026-09-01", "2026-09-03", {"2026-09-02"})
    assert rows == [(7, "2026-09-01", 0), (7, "2026-09-02", 1), (7, "2026-09-03", 0)]


def test_load_dates_with_non_steps_exercises(tmp_path: Path) -> None:
    path = tmp_path / "fitness.db"
    _write_fitness_db(
        path,
        [
            ("Steps", "2026-09-01"),
            ("Pull-up", "2026-09-02"),
            ("STEPS", "2026-09-03"),
        ],
    )
    dates = load_dates_with_non_steps_exercises(path, "2026-09-01", "2026-09-03")
    assert dates == {"2026-09-02"}
    assert load_dates_with_non_steps_exercises(tmp_path / "missing.db", "2026-09-01", "2026-09-03") is None


def test_sync_sport_habit_from_fitness_writes_done_and_not_done(
    habits_db: DatabaseManager,
    tmp_path: Path,
) -> None:
    assert habits_db.add_habit("Sport", is_bool=True)
    habit_id = int(habits_db.get_all_habits()[0][0])
    fitness = tmp_path / "fitness.db"
    _write_fitness_db(
        fitness,
        [
            ("Steps", "2026-09-01"),
            ("Squat", "2026-09-02"),
        ],
    )
    config: dict[str, Any] = {
        HABITS_SPORT_HABIT_NAME_KEY: "sport",
        HABITS_SPORT_LOOKBACK_DAYS_KEY: 3,
        "sqlite_fitness": str(fitness),
    }
    changed = sync_sport_habit_from_fitness(habits_db, config, today=date(2026, 9, 3))
    assert changed == 3
    values = habits_db.get_habit_values_between(habit_id, "2026-09-01", "2026-09-03")
    assert values == {"2026-09-01": 0, "2026-09-02": 1, "2026-09-03": 0}
    assert sync_sport_habit_from_fitness(habits_db, config, today=date(2026, 9, 3)) == 0


def test_sync_sport_habit_from_fitness_does_nothing_without_habit(
    habits_db: DatabaseManager,
    tmp_path: Path,
) -> None:
    fitness = tmp_path / "fitness.db"
    _write_fitness_db(fitness, [("Squat", "2026-09-02")])
    assert (
        sync_sport_habit_from_fitness(
            habits_db,
            {HABITS_SPORT_HABIT_NAME_KEY: "Sport", "sqlite_fitness": str(fitness)},
            today=date(2026, 9, 3),
        )
        == 0
    )
    assert habits_db.add_habit("Walk", is_bool=True)
    assert (
        sync_sport_habit_from_fitness(
            habits_db,
            {HABITS_SPORT_HABIT_NAME_KEY: "Sport", "sqlite_fitness": str(fitness)},
            today=date(2026, 9, 3),
        )
        == 0
    )
    assert (
        sync_sport_habit_from_fitness(
            habits_db,
            {HABITS_SPORT_HABIT_NAME_KEY: ""},
            today=date(2026, 9, 3),
        )
        == 0
    )


def test_resolve_fitness_db_path(tmp_path: Path) -> None:
    missing = tmp_path / "missing.db"
    present = tmp_path / "fitness.db"
    present.write_bytes(b"")
    assert resolve_fitness_db_path({}) is None
    assert resolve_fitness_db_path({"sqlite_fitness": str(missing)}) is None
    assert resolve_fitness_db_path({"sqlite_fitness": str(present)}) == present


def test_habits_sport_config_helpers(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps({}), encoding="utf-8")
    assert get_habits_sport_habit_name({HABITS_SPORT_HABIT_NAME_KEY: ""}, config_path=str(path)) == ""
    assert get_habits_sport_habit_name(config_path=str(path)) == ""
    assert get_habits_sport_lookback_days({}) == DEFAULT_HABITS_SPORT_LOOKBACK_DAYS
    assert get_habits_sport_lookback_days({HABITS_SPORT_LOOKBACK_DAYS_KEY: 0}) == 1
    assert get_habits_sport_lookback_days({HABITS_SPORT_LOOKBACK_DAYS_KEY: 400}) == 366
    path.write_text(
        json.dumps({"editor": "cursor", HABITS_SPORT_HABIT_NAME_KEY: "Old"}),
        encoding="utf-8",
    )
    live: dict[str, Any] = {}
    set_habits_sport_habit_name("Sport", config=live, config_path=str(path))
    written = json.loads(path.read_text(encoding="utf-8"))
    assert HABITS_SPORT_HABIT_NAME_KEY not in written
    assert written["editor"] == "cursor"
    temp = json.loads((tmp_path / "config-temp.json").read_text(encoding="utf-8"))
    assert temp[HABITS_SPORT_HABIT_NAME_KEY] == "Sport"
    assert live[HABITS_SPORT_HABIT_NAME_KEY] == "Sport"
    assert get_habits_sport_habit_name(live) == "Sport"
    assert get_habits_sport_habit_name(config_path=str(path)) == "Sport"


def test_habits_sport_habit_name_falls_back_to_main_config(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps({HABITS_SPORT_HABIT_NAME_KEY: "Walk"}), encoding="utf-8")
    assert get_habits_sport_habit_name(config_path=str(path)) == "Walk"


def test_dashboard_context_menu_hides_assign_for_sport_habit(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert qapp is not None
    labels: list[str] = []

    def fake_add(menu: QMenu, text: str, _emoji: str) -> QAction:
        labels.append(text)
        action = QAction(text, menu)
        menu.addAction(action)
        return action

    monkeypatch.setattr("harrix_swiss_knife.apps.habits.dashboard.add_emoji_action", fake_add)
    monkeypatch.setattr(QMenu, "exec_", lambda *_args, **_kwargs: None)

    assigned = HabitDashboardWidget(app_config={HABITS_SPORT_HABIT_NAME_KEY: "Sport"})
    assigned._habits_cache = [[1, "Sport", 1, 0, ""]]
    assigned._on_habit_row_context_menu(1, QPoint(0, 0))
    assert "Assign as sport habit" not in labels

    labels.clear()
    other = HabitDashboardWidget(app_config={HABITS_SPORT_HABIT_NAME_KEY: "Walk"})
    other._habits_cache = [[2, "Sport", 1, 0, ""]]
    other._on_habit_row_context_menu(2, QPoint(0, 0))
    assert "Assign as sport habit" in labels
    assigned.close()
    other.close()


def test_dashboard_context_menu_assigns_sport_habit(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert qapp is not None
    captured: list[QAction] = []

    def fake_add(menu: QMenu, text: str, _emoji: str) -> QAction:
        action = QAction(text, menu)
        menu.addAction(action)
        captured.append(action)
        return action

    monkeypatch.setattr("harrix_swiss_knife.apps.habits.dashboard.add_emoji_action", fake_add)
    dashboard = HabitDashboardWidget(app_config={HABITS_SPORT_HABIT_NAME_KEY: ""})
    dashboard._habits_cache = [[3, "Sport", 1, 0, ""]]
    names: list[str] = []
    dashboard.sport_habit_assign_requested.connect(names.append)
    monkeypatch.setattr(QMenu, "exec_", lambda *_args, **_kwargs: captured[-1])
    dashboard._on_habit_row_context_menu(3, QPoint(0, 0))
    assert names == ["Sport"]
    dashboard.close()
