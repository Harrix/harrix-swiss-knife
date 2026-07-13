"""Tests for main window view mode settings."""

from harrix_swiss_knife.main_window_settings import MAIN_WINDOW_ICON_GRID_KEY, load_main_window_icon_grid


def test_load_main_window_icon_grid_defaults_to_true() -> None:
    assert load_main_window_icon_grid() is True


def test_main_window_icon_grid_key() -> None:
    assert MAIN_WINDOW_ICON_GRID_KEY == "main_window_icon_grid"
