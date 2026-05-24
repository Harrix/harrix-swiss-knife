"""Actions for Python development and Markdown file management."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnDownloadAndReplaceImagesFolder(ActionBase):
    """Download remote images and replace URLs with local references in multiple Markdown files.

    This action processes all Markdown files in a selected folder to find image URLs,
    downloads the images to local directories, and updates the Markdown files to reference
    these local copies instead of the remote URLs, improving document portability and
    reducing external dependencies across an entire collection of documents.
    """

    icon = "📥"
    title = "Download images in …"

    @ActionBase.handle_exceptions("downloading images in folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Download remote images and replace URLs with local references in multiple Markdown files."""
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("downloading images folder thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.download_and_replace_images))

    @ActionBase.handle_exceptions("downloading images folder thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
