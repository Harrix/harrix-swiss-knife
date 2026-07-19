"""Actions for Python development and code management."""

from __future__ import annotations

import sys
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnNodeUpdate(ActionBase):
    """Update Node.js to the latest version via winget.

    This action upgrades OpenJS.NodeJS using the Windows Package Manager (winget)
    command `winget upgrade OpenJS.NodeJS`. Available only on Windows.
    """

    icon = "📥"
    title = "Update Node.js"

    @ActionBase.handle_exceptions("Node.js update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Update Node.js to the latest version via winget."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows (winget).")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("Node.js update thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Avoid interactive agreement prompts (msstore) by pinning the "winget" source
        # and disabling interactivity.
        cmd = (
            "winget upgrade -e --id OpenJS.NodeJS.LTS --source winget "
            "--accept-package-agreements --accept-source-agreements --silent --disable-interactivity"
        )
        return h.dev.run_command(cmd)

    @ActionBase.handle_exceptions("Node.js update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Node.js update completed")
        self.add_line(result)
        self.show_result()
