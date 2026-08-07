"""Beautify all Markdown notes and regenerate `.g.md` summaries and combined files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.python_project import reject_python_project_for_md_beautify
from harrix_swiss_knife.actions.markdown.beautify_md import OnBeautifyMd


class OnBeautifyMdAndRegenerateGMd(ActionBase):
    """Beautify all Markdown notes and regenerate `.g.md` summaries and combined files.

    This action performs multiple enhancement operations on Markdown files across
    all configured note directories, including:

    - Adding image captions
    - Generating tables of contents
    - Creating summaries for specified directories
    - Combining related Markdown files
    - Formatting YAML frontmatter
    - Formatting Markdown with the harrix-pylib formatter

    It provides a one-click solution for maintaining a high-quality, consistently
    formatted collection of Markdown documents.

    """

    icon = "💎"
    title = "Beautify MD and regenerate `.g.md` in …"
    bold_title = True
    cli_available = True
    cli_hint = "md beautify-regenerate-g-md"

    @ActionBase.handle_exceptions("beautifying markdown folder and regenerating g.md")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        prose_wrap: str = "preserve",
        print_width: int = 80,
        apply_prose_fixes: bool = True,
        format_code_blocks: bool = True,
        **_kwargs: Any,
    ) -> None:
        """Apply comprehensive beautification to all Markdown notes."""
        self.prose_wrap = prose_wrap
        self.print_width = print_width
        self.apply_prose_fixes = apply_prose_fixes
        self.format_code_blocks = format_code_blocks
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

        if reject_python_project_for_md_beautify(self, self.folder_path, noninteractive=noninteractive):
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
        OnBeautifyMd.beautify_markdown_common(self, str(self.folder_path), is_include_summaries_and_combine=True)

    @ActionBase.handle_exceptions("beautifying and regenerating thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
