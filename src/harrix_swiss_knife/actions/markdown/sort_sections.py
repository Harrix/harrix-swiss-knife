"""Actions for Python development and Markdown file management."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnSortSections(ActionBase):
    """Organize and enhance a single Markdown file by sorting sections and generating image captions.

    This action processes a user-selected Markdown file, performing two key operations
    to improve its structure and readability:

    1. Section sorting:
       - Identifies sections (headings) within the Markdown file
       - Sorts sections in a logical order based on heading level and content
       - Maintains the hierarchy and structure of nested sections
       - Preserves the content within each section while reordering

    2. Image caption generation:
       - Identifies images within the Markdown file
       - Creates or updates captions for images based on their context or filename
       - Ensures consistent formatting for image references

    Unlike the folder-based version of this action, this operates on a single file selected
    by the user. The user is prompted to select a Markdown file, with the default location
    being the notes directory specified in the configuration.
    """

    icon = "📶"
    title = "Sort sections in …"

    @ActionBase.handle_exceptions("sorting sections in markdown file")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Organize and enhance a single Markdown file by sorting sections and generating image captions."""
        self.filename = self.dialogs.get_open_filename(
            "Open Markdown file",
            self.config["path_notes"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("sorting sections thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(h.md.sort_sections(self.filename))

    @ActionBase.handle_exceptions("sorting sections thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()
