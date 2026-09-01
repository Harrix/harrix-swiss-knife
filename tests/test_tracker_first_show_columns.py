"""Tests for tracker tables that are sized before the window is first shown."""

from __future__ import annotations

import inspect

import pytest

from harrix_swiss_knife.apps.common.qt_main_window import AppWindowMixin
from harrix_swiss_knife.apps.finance.main import MainWindow as FinanceMainWindow
from harrix_swiss_knife.apps.fitness.main import MainWindow as FitnessMainWindow
from harrix_swiss_knife.apps.food.main import MainWindow as FoodMainWindow

_WINDOWS = [FinanceMainWindow, FitnessMainWindow, FoodMainWindow]


@pytest.mark.parametrize("window_class", _WINDOWS)
def test_tracker_defers_launcher_show_until_columns_ready(window_class: type) -> None:
    """The launcher must not show the window before `_finish_window_initialization`."""
    assert window_class.defer_initial_show is True


@pytest.mark.parametrize("window_class", _WINDOWS)
def test_tracker_sizes_columns_before_first_show(window_class: type) -> None:
    """Off-screen layout runs first, so the only on-screen show is already correct."""
    source = inspect.getsource(window_class._finish_window_initialization)
    assert "setWindowOpacity" not in source
    assert "setUpdatesEnabled" not in source
    assert source.index("_prepare_layout_before_first_show") < source.index("_show_placed_window")


def test_prepare_layout_uses_offscreen_show_pass() -> None:
    """The shared helper lays out via `WA_DontShowOnScreen`, not a visible show."""
    source = inspect.getsource(AppWindowMixin._prepare_layout_before_first_show)
    assert source.index("WA_DontShowOnScreen") < source.index("widget.show()")
    assert source.index("step()") < source.index("widget.hide()")
