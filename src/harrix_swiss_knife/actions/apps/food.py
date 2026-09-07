"""Launch the Food tracker application."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.app_launcher import AppLauncherAction


class OnFood(AppLauncherAction):
    """Launch the food tracking application."""

    icon = "🍔"
    icon_svg = "food__hamburger.svg"
    title = "Food tracker"
    main_window_module = "harrix_swiss_knife.apps.food.main"
