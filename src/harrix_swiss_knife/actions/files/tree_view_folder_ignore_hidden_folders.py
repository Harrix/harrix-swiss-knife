"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.files.tree_view_folder import OnTreeViewFolder


class OnTreeViewFolderIgnoreHiddenFolders(OnTreeViewFolder):
    """Generate a tree view excluding hidden folders.

    This action extends `OnTreeViewFolder` by automatically setting the
    `is_ignore_hidden_folders` flag to `True`, creating a cleaner tree view
    that omits hidden directories (those starting with a dot).
    """

    icon = "├"
    title = "Tree view in … (ignore hidden folders)"

    @ActionBase.handle_exceptions("generating tree view ignoring hidden folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Generate a tree view excluding hidden folders."""
        super().execute(*args, is_ignore_hidden_folders=True, **kwargs)
