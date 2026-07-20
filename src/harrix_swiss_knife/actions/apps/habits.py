"""Actions for launching applications."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.app_launcher import AppLauncherAction


class OnHabits(AppLauncherAction):
    """Launch the habits tracking application."""

    icon = "✅"
    title = "Habit tracker"
    main_window_module = "harrix_swiss_knife.apps.habits.main"
