"""Actions for launching applications."""

from __future__ import annotations

from harrix_swiss_knife.actions.apps._launcher import AppLauncherAction


class OnFood(AppLauncherAction):
    """Launch the food tracking application."""

    icon = "🍔"
    title = "Food tracker"
    main_window_module = "harrix_swiss_knife.apps.food.main"
