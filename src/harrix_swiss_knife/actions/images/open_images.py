"""Image optimization and management actions."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnOpenImages(ActionBase):
    """Open the source images temporary folder.

    This action opens the temporary directory containing original images
    (`images`) in the system's file explorer, allowing quick access
    to view or manage the source image files.

    """

    icon = "📂"
    title = "Open the folder images"

    @ActionBase.handle_exceptions("opening images folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the source images temporary folder."""
        path = h.dev.get_project_root() / "temp/images"
        if not path.exists():
            path.mkdir(parents=True)
            result = f"Folder `{path}` is created and opened."
        else:
            result = f"Folder `{path}` is opened."
        h.file.open_file_or_folder(path)
        self.add_line(result)
