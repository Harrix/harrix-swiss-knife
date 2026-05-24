"""Actions for Python development and Markdown file management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.markdown.beautify_md_folder import OnBeautifyMdFolder


class OnBeautifyMdFolderAndRegenerateGMd(ActionBase):
    """Apply comprehensive beautification to all Markdown notes.

    This action performs multiple enhancement operations on Markdown files across
    all configured note directories, including:

    - Adding image captions
    - Generating tables of contents
    - Creating summaries for specified directories
    - Combining related Markdown files
    - Formatting YAML frontmatter
    - Running Prettier for consistent formatting

    It provides a one-click solution for maintaining a high-quality, consistently
    formatted collection of Markdown documents.
    """

    icon = "💎"
    title = "Beautify MD and regenerate .g.md in …"
    bold_title = True
    cli_available = True
    cli_hint = "markdown beautify-regenerate-g-md"

    @ActionBase.handle_exceptions("beautifying markdown folder and regenerating g.md")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Apply comprehensive beautification to all Markdown notes."""
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                "beautifying markdown folder and regenerating g.md",
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_notes"], self.config["path_notes"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.in_thread()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("beautifying and regenerating thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        if self.folder_path is None:
            return
        OnBeautifyMdFolder.beautify_markdown_common(self, str(self.folder_path), is_include_summaries_and_combine=True)

    @ActionBase.handle_exceptions("beautifying and regenerating thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
