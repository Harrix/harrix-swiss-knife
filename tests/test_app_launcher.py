"""Tests for tracker app launcher action."""

from __future__ import annotations

from harrix_swiss_knife.actions.apps.food import OnFood
from harrix_swiss_knife.actions.apps.habits import OnHabits


def test_app_launcher_clears_main_window_on_destroyed_callback() -> None:
    """Launcher should drop cached window reference when Qt emits destroyed."""
    action = OnHabits()
    action.main_window = object()
    action._clear_main_window_ref()
    assert action.main_window is None


def test_habits_launcher_hides_instead_of_destroying() -> None:
    """Habits launched from tray should hide on close to keep matplotlib canvas alive."""
    assert OnHabits.hide_on_close is True
    assert OnFood.hide_on_close is False


def test_finance_finish_init_skips_duplicate_exchange_rates_setup() -> None:
    """Exchange rates controls are configured once in _initial_load, not again on show."""
    import inspect

    from harrix_swiss_knife.apps.finance.main import MainWindow

    source = inspect.getsource(MainWindow._finish_window_initialization)
    assert "_setup_exchange_rates_controls" not in source
