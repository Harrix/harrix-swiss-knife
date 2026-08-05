"""Launch the Media Sorter application."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.app_launcher import AppLauncherAction


class OnMediaSorter(AppLauncherAction):
    """Launch the media sorting application."""

    icon = "🖼️"
    title = "Media Sorter"
    main_window_module = "harrix_swiss_knife.apps.media_sorter.main"
