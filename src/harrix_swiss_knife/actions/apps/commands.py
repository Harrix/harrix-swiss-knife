"""Open the Commands app (tray command cards)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.tray_icon import show_command_window


class OnCommands(ActionBase):
    """Show the Commands window with the tray command list and Fluent cards."""

    icon = "🗂️"
    title = "Commands"
    description = "Browse and run Harrix Swiss Knife commands as cards."
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("opening commands")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Show or raise the command-cards window."""
        if show_command_window():
            return
        message_box.critical(None, "Commands", "Tray icon is not initialized.")
