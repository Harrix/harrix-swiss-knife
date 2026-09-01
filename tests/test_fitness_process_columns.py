"""Tests for Fitness process-table column layout on first show."""

from __future__ import annotations

import inspect

from harrix_swiss_knife.apps.fitness.main import MainWindow


def test_fitness_finish_init_hides_until_process_columns_ready() -> None:
    """First on-screen show happens after process columns are sized off-screen."""
    source = inspect.getsource(MainWindow._finish_window_initialization)
    assert "setWindowOpacity" not in source
    assert source.index("WA_DontShowOnScreen") < source.index("_show_placed_window")
    assert source.index("_adjust_process_table_columns") < source.index("_reveal_prepared_window")
