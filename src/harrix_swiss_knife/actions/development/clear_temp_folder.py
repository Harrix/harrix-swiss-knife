"""Actions for Python development and code management."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.paths import clear_temp_folder


class OnClearTempFolder(ActionBase):
    """Clear the project ``temp/`` folder.

    Empties ``images`` and ``optimized_images`` in place and removes all other
    files and folders under ``temp/``.
    """

    icon = "🧹"
    title = "Clear temp folder"

    @ActionBase.handle_exceptions("clearing temp folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Clear project temp directory."""
        for line in clear_temp_folder():
            self.add_line(line)
        self.show_result()
