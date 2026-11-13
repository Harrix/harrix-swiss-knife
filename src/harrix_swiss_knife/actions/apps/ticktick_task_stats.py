"""Show TickTick task completion stats from the local desktop database."""

from __future__ import annotations

from typing import Any, ClassVar

from harrix_swiss_knife.actions.common.base import ActionBase


class OnShowTickTickTaskStats(ActionBase):
    """Open a GitHub-like calendar of completed TickTick tasks from the local DB."""

    icon = "📅"
    title = "TickTick task stats"
    description = "Show a contribution calendar of completed TickTick tasks from the local database"
    cli_available: ClassVar[bool] = False

    @ActionBase.handle_exceptions("show TickTick task stats")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the TickTick task-stats dialog."""
        self.dialogs.show_ticktick_task_stats()
