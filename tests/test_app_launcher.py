"""Tests for tracker app launcher action."""

from __future__ import annotations

from harrix_swiss_knife.actions.apps.habits import OnHabits


def test_app_launcher_clears_main_window_on_destroyed_callback() -> None:
    """Launcher should drop cached window reference when Qt emits destroyed."""
    action = OnHabits()
    action.main_window = object()
    action._clear_main_window_ref()
    assert action.main_window is None
