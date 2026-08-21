"""Upgrade uv-managed Python versions."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.uv_locate import find_uv_exe, refresh_path


class OnUpgradeUvPython(ActionBase):
    """Upgrade uv-managed Python versions to the latest patch.

    Runs `uv python upgrade` for every CPython installed via uv.

    """

    icon = "📥"
    title = "Upgrade uv Python"

    @ActionBase.handle_exceptions("uv python upgrade")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Run `uv python upgrade`."""
        refresh_path()
        if find_uv_exe() is None:
            self.add_line(
                "❌ uv not found on PATH or in common install locations. Install uv first: https://docs.astral.sh/uv/"
            )
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("uv python upgrade thread")
    def in_thread(self) -> str | None:
        """Execute `uv python upgrade` in a worker thread."""
        uv = find_uv_exe()
        if uv is None:
            return "❌ uv not found"
        return h.dev.run_command([str(uv), "python", "upgrade"], is_shell=False)

    @ActionBase.handle_exceptions("uv python upgrade thread completion")
    def thread_after(self, result: Any) -> None:
        """Show toast and the upgrade log."""
        self.show_toast(f"{self.title} completed")
        self.add_line(result)
        self.show_result()
