"""Open the quick launcher overlay (global hotkey on Windows)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.quick_launcher.context import get_quick_launcher_context
from harrix_swiss_knife.apps.common import message_box


class OnQuickLauncher(ActionBase):
    """Show or hide the quick launcher overlay."""

    icon = "⚡"
    title = "Quick launcher…"
    bold_title = False
    cli_available = False

    @ActionBase.handle_exceptions("opening quick launcher")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Toggle the quick launcher overlay."""
        context = get_quick_launcher_context()
        if context is None:
            message_box.critical(None, "Quick launcher", "Quick launcher is not initialized.")
            return

        context.toggle()
