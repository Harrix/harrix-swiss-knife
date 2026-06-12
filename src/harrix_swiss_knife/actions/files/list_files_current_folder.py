"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnListFilesCurrentFolder(ActionBase):
    """Generate a simple list of files from the current directory only.

    This action prompts the user to select a folder and then creates
    a simple text list of all files in the selected directory only,
    without entering any subdirectories. This provides a flat view
    of files at the current level.
    """

    icon = "📄"
    title = "List files current folder in …"

    @ActionBase.handle_exceptions("generating current folder file list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Generate a simple list of files from the current directory only."""
        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.list_files_simple(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False), is_only_files=True
        )
        self.add_line(result)
        self.show_result()
