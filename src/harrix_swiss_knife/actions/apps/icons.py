"""Launch the Vector Icons browser application."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.app_launcher import AppLauncherAction


class OnIcons(AppLauncherAction):
    """Launch the Harrix Vector Icons browser."""

    icon = "🎨"
    title = "Vector Icons"
    main_window_module = "harrix_swiss_knife.apps.icons.main"
