"""Actions for launching applications."""

from typing import Any

from shiboken6 import isValid

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.finance import main as finance_main
from harrix_swiss_knife.fitness import main as fitness_main
from harrix_swiss_knife.food import main as food_main


class OnFinance(ActionBase):
    """Launch the finance tracking application.

    This action opens the finance tracker application in a new window or brings
    the existing window to the foreground if it's already open. The finance tracker
    allows users to record, monitor, and analyze their finance.
    """

    icon = "💰"
    title = "Finance tracker"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnFinance action."""
        super().__init__()
        self.parent = kwargs.get("parent")
        self.main_window = None

    @ActionBase.handle_exceptions("launching finance tracker")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = finance_main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()


class OnFitness(ActionBase):
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

    @ActionBase.handle_exceptions("launching fitness tracker")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = fitness_main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()


class OnFood(ActionBase):
    """Launch the food tracking application.

    This action opens the food tracker application in a new window or brings
    the existing window to the foreground if it's already open. The food tracker
    allows users to record, monitor, and analyze their food intake and nutrition.
    """

    icon = "🍔"
    title = "Food tracker"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnFood action."""
        super().__init__()
        self.parent = kwargs.get("parent")
        self.main_window = None

    @ActionBase.handle_exceptions("launching food tracker")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        if self.main_window is None or not isValid(self.main_window):
            self.main_window = food_main.MainWindow()

        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
