"""Generate a simple list of all files in a directory structure."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase


class OnListFilesSimple(ActionBase):
    """Generate a simple list of all files in a directory structure.

    This action prompts the user to select a folder and then creates
    a simple text list of all files with their relative paths,
    similar to a flat file listing without directory tree structure.

    """

    icon = "📄"
    title = "List files in …"

    @ActionBase.handle_exceptions("generating file list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Generate a simple list of all files in a directory structure."""
        self.folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if self.folder_path is None:
            return

        self._ignore_hidden_folders = bool(kwargs.get("is_ignore_hidden_folders", False))
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("generating file list thread")
    def in_thread(self) -> None:
        """List files in a worker thread."""
        if self.folder_path is None:
            return

        result = h.file.list_files_simple(
            self.folder_path,
            is_ignore_hidden_folders=self._ignore_hidden_folders,
        )
        result = f"{self.folder_path}\n\n(no files found)" if not result.strip() else f"{self.folder_path}\n\n{result}"
        self.add_line(result)

    @ActionBase.handle_exceptions("generating file list thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result after the file list is ready."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
