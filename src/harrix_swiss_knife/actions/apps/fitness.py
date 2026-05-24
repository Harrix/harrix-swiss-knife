"""Actions for launching applications."""

from __future__ import annotations

from typing import Any

from shiboken6 import isValid

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.apps.fitness import main as fitness_main


class OnFitness(ActionBase):
    """Launch the fitness tracking application.

    This action opens the fitness tracker application in a new window or brings
    the existing window to the foreground if it's already open. The fitness tracker
    allows users to record, monitor, and analyze their physical activities and
    exercise routines.
    """

    icon = "🏃🏻"
    title = "Fitness tracker"
    show_in_compact_mode = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnFitness action."""
        super().__init__()
        self.parent = kwargs.get("parent")
        self.main_window = None

    @ActionBase.handle_exceptions("launching fitness tracker")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Launch the fitness tracking application."""
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = fitness_main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
