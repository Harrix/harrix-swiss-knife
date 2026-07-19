"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnCheckFeaturedImage(ActionBase):
    """Check for featured image files in a selected folder.

    This action prompts the user to select a folder and then checks for the presence
    of files named `featured_image` with any extension, which are commonly used
    as preview images or thumbnails for the folder contents.

    """

    icon = "✅"
    title = "Check featured_image in …"

    @ActionBase.handle_exceptions("checking featured image")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Check for featured image files in a selected folder."""
        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.check_featured_image(folder_path)[1]
        self.add_line(result)
        self.show_result()
