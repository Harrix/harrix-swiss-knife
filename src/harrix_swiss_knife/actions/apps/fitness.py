"""Actions for launching applications."""

from __future__ import annotations

from harrix_swiss_knife.actions.apps._launcher import AppLauncherAction
from harrix_swiss_knife.apps.fitness import main as fitness_main


class OnFitness(AppLauncherAction):
    """Launch the fitness tracking application."""

    icon = "🏃🏻"
    title = "Fitness tracker"
    main_window_class = fitness_main.MainWindow
