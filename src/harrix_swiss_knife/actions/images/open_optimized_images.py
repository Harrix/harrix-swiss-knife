"""Image optimization and management actions."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnOpenOptimizedImages(ActionBase):
    """Open the optimized images temporary folder.

    This action opens the temporary directory containing optimized images
    (`optimized_images`) in the system's file explorer, allowing quick access
    to view or use the processed image files.

    """

    icon = "📂"
    title = "Open the folder optimized_images"

    @ActionBase.handle_exceptions("opening optimized images folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the optimized images temporary folder."""
        path = h.dev.get_project_root() / "temp/optimized_images"
        if not path.exists():
            path.mkdir(parents=True)
            result = f"Folder `{path}` is created and opened."
        else:
            result = f"Folder `{path}` is opened."
        h.file.open_file_or_folder(path)
        self.add_line(result)
