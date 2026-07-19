"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnAllFilesToParentFolder(ActionBase):
    """Move and flatten files from nested directories.

    This action prompts the user to select a folder and then moves all files
    from its nested subdirectories directly into the selected parent folder,
    effectively flattening the directory structure while preserving all files.

    """

    icon = "🗂️"
    title = "Moves and flattens files in …"

    @ActionBase.handle_exceptions("moving files to parent folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Move and flatten files from nested directories."""
        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.all_to_parent_folder(folder_path)
        self.add_line(result)
        self.show_result()
