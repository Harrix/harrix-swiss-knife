"""Launch the Beat Saber tracker application."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.app_launcher import AppLauncherAction


class OnBeatSaber(AppLauncherAction):
    """Launch the Beat Saber progress tracker."""

    icon = "🎮"
    title = "Beat Saber tracker"
    description = "Official song progress, PC vs Quest compare, sync and save backups."
    main_window_module = "harrix_swiss_knife.apps.beat_saber.main"
