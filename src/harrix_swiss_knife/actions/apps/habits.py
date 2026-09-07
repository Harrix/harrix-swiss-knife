"""Launch the Habits tracker application."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.app_launcher import AppLauncherAction


class OnHabits(AppLauncherAction):
    """Launch the habits tracking application."""

    icon = "✅"
    icon_svg = "symbol__ok.svg"
    title = "Habit tracker"
    main_window_module = "harrix_swiss_knife.apps.habits.main"
