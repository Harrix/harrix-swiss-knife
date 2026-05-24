"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.files.list_files_simple import OnListFilesSimple


class OnListFilesSimpleIgnoreHiddenFolders(ActionBase):
    """Generate a simple file list excluding hidden folders.

    This action extends OnListFilesSimple by automatically setting the
    is_ignore_hidden_folders flag to true, creating a cleaner file list
    that omits hidden directories and files (those starting with a dot
    or matching common ignore patterns like .git, __pycache__, etc.).
    """

    icon = "📄"
    title = "List files simple (ignore hidden folders)"

    @ActionBase.handle_exceptions("generating file list ignoring hidden folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Generate a simple file list excluding hidden folders."""
        OnListFilesSimple().execute(is_ignore_hidden_folders=True)
