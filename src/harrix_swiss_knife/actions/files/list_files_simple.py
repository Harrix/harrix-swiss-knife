"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnListFilesSimple(ActionBase):
    """Generate a simple list of all files in a directory structure.

    This action prompts the user to select a folder and then creates
    a simple text list of all files with their relative paths,
    similar to a flat file listing without directory tree structure.
    """

    icon = "📄"
    title = "List files simple"

    @ActionBase.handle_exceptions("generating file list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Generate a simple list of all files in a directory structure."""
        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.list_files_simple(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False)
        )
        self.add_line(result)
        self.show_result()
