"""Tests for tracker app launcher action."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication, QWidget

from harrix_swiss_knife.actions.apps.food import OnFood
from harrix_swiss_knife.actions.apps.habits import OnHabits
from harrix_swiss_knife.apps.finance.main import MainWindow

if TYPE_CHECKING:
    import pytest


def test_app_launcher_clears_main_window_on_destroyed_callback() -> None:
    """Launcher should drop cached window reference when Qt emits destroyed."""
    action = OnHabits()
    action.main_window = object()
    action._clear_main_window_ref()
    assert action.main_window is None


def test_app_launcher_skips_concurrent_window_creation() -> None:
    """Second execute() while __init__ is running must not spawn another window."""
    action = OnHabits()
    action._is_creating_window = True
    action.execute()
    assert action.main_window is None


def test_habits_launcher_destroys_on_close() -> None:
    """Habits launched from tray should destroy on close like other tracker apps."""
    assert OnHabits.hide_on_close is False
    assert OnFood.hide_on_close is False


def test_app_launcher_shows_loading_toast_while_creating_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Creating a window shows a countdown toast that is closed afterwards."""
    app = QApplication.instance()
    if app is None:
        QApplication([])

    class DummyWindow(QWidget):
        def __init__(self, *, hide_on_close: bool = False) -> None:
            super().__init__()
            del hide_on_close

    started: list[str] = []
    stopped: list[object] = []

    def fake_start(title: str) -> object:
        started.append(title)
        return object()

    def fake_stop(toast: object | None) -> None:
        stopped.append(toast)

    monkeypatch.setattr(OnHabits, "get_main_window_class", classmethod(lambda _cls: DummyWindow))
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.app_launcher.start_app_loading_toast",
        fake_start,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.common.app_launcher.stop_app_loading_toast",
        fake_stop,
    )

    action = OnHabits()
    action.execute()
    assert started == ["Habit tracker"]
    assert len(stopped) == 1
    assert action.main_window is not None
    action.main_window.close()


def test_finance_finish_init_skips_duplicate_exchange_rates_setup() -> None:
    """Exchange rates controls are configured once in _initial_load, not again on show."""
    source = inspect.getsource(MainWindow._finish_window_initialization)
    assert "_setup_exchange_rates_controls" not in source
