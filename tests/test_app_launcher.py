"""Tests for tracker app launcher action."""

from __future__ import annotations

import inspect

from harrix_swiss_knife.actions.apps.food import OnFood
from harrix_swiss_knife.actions.apps.habits import OnHabits
from harrix_swiss_knife.apps.finance.main import MainWindow


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


def test_finance_finish_init_skips_duplicate_exchange_rates_setup() -> None:
    """Exchange rates controls are configured once in _initial_load, not again on show."""
    source = inspect.getsource(MainWindow._finish_window_initialization)
    assert "_setup_exchange_rates_controls" not in source
