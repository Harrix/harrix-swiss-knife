"""Actions for launching applications."""

from __future__ import annotations

from harrix_swiss_knife.actions.apps._launcher import AppLauncherAction


class OnFinance(AppLauncherAction):
    """Launch the finance tracking application."""

    icon = "💰"
    title = "Finance tracker"
    main_window_module = "harrix_swiss_knife.apps.finance.main"
