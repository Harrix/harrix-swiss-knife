"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnRenameFb2EpubPdfFiles(ActionBase):
    """Rename FB2, Epub, PDF files based on metadata from file content.

    This action prompts the user to select a folder and then processes all FB2, Epub, PDF files
    within it, extracting author, title, and year information from the metadata.
    Files are renamed according to the pattern: `Author - Title - Year.ext` (year is optional).

    If metadata extraction fails, the action attempts to transliterate the filename
    from English to Russian, assuming it might be a transliterated Russian title.
    If transliteration doesn't improve the filename, it remains unchanged.

    This provides a one-click solution for organizing and standardizing FB2, Epub, PDF book collections
    with proper naming conventions based on actual book metadata.

    """

    icon = "📚"
    title = "Rename FB2, Epub, PDF files in …"

    @ActionBase.handle_exceptions("renaming FB2, Epub, PDF files")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Rename FB2, Epub, PDF files based on metadata from file content."""
        if not self.show_rename_preview(
            """Recursively renames FB2, Epub, and PDF files based on metadata (author, title, year).
If metadata extraction fails, the filename may be transliterated from English to Russian.
Files that cannot be improved are left unchanged.

Pattern: Author - Title - Year.ext (year is optional)

Example:

  war_and_peace.fb2
→ Tolstoy Leo - War and Peace - 1869.fb2"""
        ):
            return

        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder with FB2, Epub, PDF files", self.config["path_books"]
        )
        if self.folder_path is None:
            return

        # Define available operations
        operations = [
            "📖 Rename FB2 files by metadata",
            "📖 Rename Epub files by metadata",
            "📖 Rename PDF files by metadata",
        ]

        # Get user selection for operations
        selected_operations = self.dialogs.get_checkbox_selection(
            "Select Operations",
            "Choose which operations to perform:",
            operations,
            default_selected=operations,  # All selected by default
        )

        if selected_operations is None:
            return

        self.selected_operations = selected_operations
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("renaming FB2, Epub, PDF files thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        # Execute selected operations
        if "📖 Rename FB2 files by metadata" in self.selected_operations:
            self.add_line(f"🔵 Starting FB2 file processing for path: {self.folder_path}")
            self.add_line(h.file.apply_func(self.folder_path, ".fb2", h.file.rename_fb2_file))

        if "📖 Rename Epub files by metadata" in self.selected_operations:
            self.add_line(f"🔵 Starting Epub file processing for path: {self.folder_path}")
            self.add_line(h.file.apply_func(self.folder_path, ".epub", h.file.rename_epub_file))

        if "📖 Rename PDF files by metadata" in self.selected_operations:
            self.add_line(f"🔵 Starting PDF file processing for path: {self.folder_path}")
            self.add_line(h.file.apply_func(self.folder_path, ".pdf", h.file.rename_pdf_file))

    @ActionBase.handle_exceptions("renaming FB2, Epub, PDF files thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
