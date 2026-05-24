"""Image optimization and management actions."""

from __future__ import annotations

import shutil
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnClearImages(ActionBase):
    """Clear temporary image directories.

    This action removes all files from the temporary image folders
    (`images` and `optimized_images`) and recreates the empty directories,
    providing a clean workspace for new image operations.
    """

    icon = "🧹"
    title = "Clear folders images"

    @ActionBase.handle_exceptions("clearing image folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Clear temporary image directories."""
        paths = [h.dev.get_project_root() / "temp/images", h.dev.get_project_root() / "temp/optimized_images"]
        for path in paths:
            if path.exists():
                shutil.rmtree(path)
                path.mkdir(parents=True)
                result = f"Folder `{path}` is clean."
            else:
                result = f"❌ Folder `{path}` is not exist."
            self.add_line(result)
        self.show_result()
