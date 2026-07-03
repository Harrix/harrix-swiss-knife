"""Image optimization and management actions."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.paths import clear_directory_contents


class OnClearImages(ActionBase):
    """Clear temporary image directories.

    This action removes all files from the temporary image folders
    (`images` and `optimized_images`) while keeping the directories,
    providing a clean workspace for new image operations.
    """

    icon = "🧹"
    title = "Clear folders images"

    @ActionBase.handle_exceptions("clearing image folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Clear temporary image directories."""
        paths = [h.dev.get_project_root() / "temp/images", h.dev.get_project_root() / "temp/optimized_images"]
        for path in paths:
            if path.exists() and path.is_dir():
                clear_directory_contents(path)
                result = f"Folder `{path}` is clean."
            elif not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                result = f"Created empty folder `{path}`."
            else:
                result = f"❌ `{path}` exists but is not a directory."
            self.add_line(result)
        self.show_result()
