"""Tests for tracker presentation-mode temp databases and title helpers."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QWidget

from harrix_swiss_knife import cli_menu
from harrix_swiss_knife.apps.common.presentation_mode import (
    OPEN_IN_PRESENTATION_MENU_LABEL,
    PRESENTATION_TITLE_SUFFIX,
    apply_presentation_window_title,
    create_presentation_database,
    presentation_ticktick_db_path,
    strip_presentation_title_suffix,
)
from harrix_swiss_knife.cli_menu import (
    OPEN_ALL_TRACKERS_MENU_LABEL,
    OPEN_ALL_TRACKERS_PRESENTATION_MENU_LABEL,
    show_tracker_launcher_context_menu,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_strip_and_apply_presentation_window_title(qapp: QApplication) -> None:
    assert qapp is not None
    assert strip_presentation_title_suffix(f"Finance Tracker{PRESENTATION_TITLE_SUFFIX}") == "Finance Tracker"
    assert strip_presentation_title_suffix("Finance Tracker") == "Finance Tracker"

    window = QWidget()
    window.setWindowTitle("Finance Tracker")
    apply_presentation_window_title(window, enabled=True)
    assert window.windowTitle() == f"Finance Tracker{PRESENTATION_TITLE_SUFFIX}"
    apply_presentation_window_title(window, enabled=True)
    assert window.windowTitle() == f"Finance Tracker{PRESENTATION_TITLE_SUFFIX}"
    apply_presentation_window_title(window, enabled=False)
    assert window.windowTitle() == "Finance Tracker"
    window.close()


def test_create_presentation_databases_include_today(tmp_path: Path) -> None:
    del tmp_path  # seeders use their own temp dirs
    today = datetime.now(UTC).astimezone().date().isoformat()

    finance_db = create_presentation_database("finance")
    assert finance_db.is_file()
    assert "hsk_presentation_finance_" in str(finance_db)
    with sqlite3.connect(str(finance_db)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM transactions WHERE date = ?", (today,)).fetchone()[0] > 0
        assert conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] >= 80
        oldest = conn.execute("SELECT MIN(date) FROM transactions").fetchone()[0]
        assert oldest is not None
        oldest_day = datetime.fromisoformat(str(oldest)).date()
        today_day = datetime.now(UTC).astimezone().date()
        assert (today_day - oldest_day).days >= 50

    fitness_db = create_presentation_database("fitness")
    assert fitness_db.is_file()
    with sqlite3.connect(str(fitness_db)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM process WHERE date = ?", (today,)).fetchone()[0] > 0
        assert conn.execute("SELECT COUNT(*) FROM weight WHERE date = ?", (today,)).fetchone()[0] > 0

    food_db = create_presentation_database("food")
    assert food_db.is_file()
    with sqlite3.connect(str(food_db)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM food_log WHERE date = ?", (today,)).fetchone()[0] > 0
        cols = {row[1] for row in conn.execute("PRAGMA table_info(food_day_nutrition_analysis)").fetchall()}
        assert "fiber_g" in cols
        assert "norm_fiber_g" in cols

    habits_db = create_presentation_database("habits")
    assert habits_db.is_file()
    with sqlite3.connect(str(habits_db)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM habits").fetchone()[0] >= 4
        assert conn.execute("SELECT COUNT(*) FROM process_habits WHERE date = ?", (today,)).fetchone()[0] > 0
    ticktick_db = presentation_ticktick_db_path(habits_db)
    assert ticktick_db.is_file()
    with sqlite3.connect(str(ticktick_db)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM TaskModel").fetchone()[0] >= 1
        assert conn.execute("SELECT COUNT(*) FROM ProjectModel").fetchone()[0] >= 1


def test_tracker_context_menu_has_presentation_action(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    assert qapp is not None
    host = QMenu()
    tracker = QAction("Finance tracker", host)
    host.addAction(tracker)
    shown: list[object] = []

    def _capture_exec(self: object, *_args: object, **_kwargs: object) -> None:
        shown.append(self)

    monkeypatch.setattr(cli_menu.FluentMenu, "exec", _capture_exec)
    show_tracker_launcher_context_menu(
        parent=None,
        global_pos=host.mapToGlobal(host.rect().center()),
        host_menu=host,
        tracker_action=tracker,
    )
    assert len(shown) == 1
    menu = shown[0]
    assert isinstance(menu, cli_menu.FluentMenu)
    actions = [action for action in menu.actions() if not action.isSeparator()]
    labels = [action.text() for action in actions]
    assert labels == [
        OPEN_IN_PRESENTATION_MENU_LABEL,
        OPEN_ALL_TRACKERS_MENU_LABEL,
        OPEN_ALL_TRACKERS_PRESENTATION_MENU_LABEL,
    ]
    assert all(not action.icon().isNull() for action in actions)
