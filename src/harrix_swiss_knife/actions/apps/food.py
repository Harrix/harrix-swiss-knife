"""Actions for launching applications."""

from __future__ import annotations

from harrix_swiss_knife.actions.apps._launcher import AppLauncherAction
from harrix_swiss_knife.apps.food import main as food_main


class OnFood(AppLauncherAction):
    """Launch the food tracking application."""

    icon = "🍔"
    title = "Food tracker"
    main_window_class = food_main.MainWindow
