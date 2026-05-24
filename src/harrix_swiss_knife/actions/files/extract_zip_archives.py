"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnExtractZipArchives(ActionBase):
    """Extract all ZIP archives from a selected folder.

    This action prompts the user to select a folder and then processes all ZIP files
    within it, extracting their contents directly to the same directory where each
    archive is located. After successful extraction, the original archive files
    are deleted.

    The extraction process handles nested directory structures and preserves the
    original file organization from within the archives. Each ZIP file is processed
    independently, so if one archive fails to extract, others will still be processed.

    This provides a one-click solution for bulk extraction of ZIP archives while
    maintaining clean folder organization by removing the original archive files.
    """

    icon = "📦"
    title = "Extract ZIP archives in …"

    @ActionBase.handle_exceptions("extracting ZIP archives")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Extract all ZIP archives from a selected folder."""
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder with ZIP archives", self.config["path_3d"]
        )
        if self.folder_path is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("extracting ZIP archives thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Starting ZIP archive extraction for path: {self.folder_path}")
        self.add_line(h.file.apply_func(self.folder_path, ".zip", h.file.extract_zip_archive))

    @ActionBase.handle_exceptions("extracting ZIP archives thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
