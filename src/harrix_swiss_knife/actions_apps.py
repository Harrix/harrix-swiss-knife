"""Actions for launching applications."""

from typing import Any

from shiboken6 import isValid

from harrix_swiss_knife import action_base
from harrix_swiss_knife.fitness import main


class OnFitness(action_base.ActionBase):
    """Launch the fitness tracking application.

    This action opens the fitness tracker application in a new window or brings
    the existing window to the foreground if it's already open. The fitness tracker
    allows users to record, monitor, and analyze their physical activities and
    exercise routines.
    """

    icon = "🏃🏻"
    title = "Fitness tracker"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnFitness action."""
        super().__init__()
        self.parent = kwargs.get("parent")
        self.main_window = None

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
