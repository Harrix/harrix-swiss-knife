"""Upgrade uv-managed Python versions."""

from __future__ import annotations

import shutil
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase


class OnUpgradeUvPython(ActionBase):
    """Upgrade uv-managed Python versions to the latest patch.

    Runs `uv python upgrade` for every CPython installed via uv.

    """

    icon = "📥"
    title = "Upgrade uv Python"

    @ActionBase.handle_exceptions("uv python upgrade")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Run `uv python upgrade`."""
        if shutil.which("uv") is None:
            self.add_line("❌ uv not found on PATH. Install uv first: https://docs.astral.sh/uv/")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("uv python upgrade thread")
    def in_thread(self) -> str | None:
        """Execute `uv python upgrade` in a worker thread."""
        return h.dev.run_command(["uv", "python", "upgrade"])

    @ActionBase.handle_exceptions("uv python upgrade thread completion")
    def thread_after(self, result: Any) -> None:
        """Show toast and the upgrade log."""
        self.show_toast(f"{self.title} completed")
        self.add_line(result)
        self.show_result()
