"""Actions for Python development and Markdown file management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.integrations.http_download import DownloadCancelledError


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

        self.start_thread(self.in_thread, self.thread_after, self.title, cancellable=True)

    @ActionBase.handle_exceptions("downloading images folder thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return None
        folder = Path(self.folder_path)
        md_files = sorted(folder.rglob("*.md"))
        for md_path in md_files:
            self.raise_if_work_cancelled()
            try:
                h.md.download_and_replace_images(str(md_path))
            except DownloadCancelledError:
                raise
            except Exception as exc:
                self.add_line(f"❌ {md_path}: {exc}")
        return None

    @ActionBase.handle_exceptions("downloading images folder thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
