"""Actions for launching applications."""

from __future__ import annotations

from harrix_swiss_knife.actions.apps._launcher import AppLauncherAction
from harrix_swiss_knife.apps.habits import main as habits_main


class OnHabits(AppLauncherAction):
    """Launch the habits tracking application."""

    icon = "✅"
    title = "Habit tracker"
    main_window_class = habits_main.MainWindow
