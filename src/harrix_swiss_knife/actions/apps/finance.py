"""Actions for launching applications."""

from __future__ import annotations

from harrix_swiss_knife.actions.apps._launcher import AppLauncherAction
from harrix_swiss_knife.apps.finance import main as finance_main


class OnFinance(AppLauncherAction):
    """Launch the finance tracking application."""

    icon = "💰"
    title = "Finance tracker"
    main_window_class = finance_main.MainWindow
