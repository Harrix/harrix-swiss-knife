"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnTreeViewFolder(ActionBase):
    """Generate a text-based tree view of a folder structure.

    This action prompts the user to select a folder and then creates
    a hierarchical text representation of its directory structure,
    similar to the output of the `tree` command in command-line interfaces.

    """

    icon = "├"
    title = "Tree view in …"

    @ActionBase.handle_exceptions("generating tree view")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Generate a text-based tree view of a folder structure."""
        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.tree_view_folder(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False)
        )
        self.add_line(result)
        self.show_result()
