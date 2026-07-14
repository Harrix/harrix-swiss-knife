"""Actions for launching applications."""

from __future__ import annotations

from harrix_swiss_knife.actions.apps._launcher import AppLauncherAction


class OnFitness(AppLauncherAction):
    """Launch the fitness tracking application."""

    icon = "🏃🏻"
    title = "Fitness tracker"
    main_window_module = "harrix_swiss_knife.apps.fitness.main"
