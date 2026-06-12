"""Actions for launching applications."""

from __future__ import annotations

from typing import Any

from shiboken6 import isValid

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.apps.habits import main as habits_main


class OnHabits(ActionBase):
    """Launch the habits tracking application.

    This action opens the habit tracker application in a new window or brings
    the existing window to the foreground if it's already open. The habit tracker
    allows users to record and monitor daily habits.
    """

    icon = "✅"
    title = "Habit tracker"
    show_in_compact_mode = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnHabits action."""
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")
        self.main_window = None

    @ActionBase.handle_exceptions("launching habit tracker")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Launch the habits tracking application."""
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = habits_main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
