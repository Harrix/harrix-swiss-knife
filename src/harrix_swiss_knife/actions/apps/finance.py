"""Actions for launching applications."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.app_launcher import AppLauncherAction


class OnFinance(AppLauncherAction):
    """Launch the finance tracking application."""

    icon = "💰"
    title = "Finance tracker"
    main_window_module = "harrix_swiss_knife.apps.finance.main"
