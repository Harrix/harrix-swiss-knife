"""Tests for Fitness process-table column layout on first show."""

from __future__ import annotations

import inspect

from harrix_swiss_knife.apps.fitness.main import MainWindow


def test_fitness_defers_launcher_show_until_columns_ready() -> None:
    """Launcher must not show Fitness before `_finish_window_initialization`."""
    assert MainWindow.defer_initial_show is True


def test_fitness_finish_init_shows_once_after_columns_ready() -> None:
    """The first on-screen show is the only show, after columns are pre-sized."""
    source = inspect.getsource(MainWindow._finish_window_initialization)
    hidden_source = inspect.getsource(MainWindow._apply_hidden_process_table_geometry)
    assert "setWindowOpacity" not in source
    assert "setUpdatesEnabled" not in source
    assert source.index("_apply_hidden_process_table_geometry") < source.index("_show_placed_window")
    assert hidden_source.index("WA_DontShowOnScreen") < hidden_source.index("self.show()")
    assert hidden_source.index("_adjust_process_table_columns") < hidden_source.index("self.hide()")
