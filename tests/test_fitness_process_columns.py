"""Tests for Fitness process-table column layout on first show."""

from __future__ import annotations

import inspect

from harrix_swiss_knife.apps.fitness.main import MainWindow


def test_fitness_finish_init_hides_until_process_columns_ready() -> None:
    """The window stays at opacity 0 until process columns are sized."""
    source = inspect.getsource(MainWindow._finish_window_initialization)
    assert source.index("setWindowOpacity(0)") < source.index("_show_placed_window")
    assert source.index("_wait_until_process_table_ready") < source.index("_adjust_process_table_columns")
    assert source.index("_adjust_process_table_columns") < source.rindex("setWindowOpacity(1)")
