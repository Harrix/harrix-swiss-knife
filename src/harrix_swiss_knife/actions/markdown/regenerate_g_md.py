"""Delete and regenerate `.g.md` files, then beautify only those generated files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.python_project import reject_python_project_for_md_beautify


class OnRegenerateGMd(ActionBase):
    """Delete `.g.md` dumps, regenerate them, and beautify only `.g.md` files.

    Source Markdown notes (`.md` that are not `.g.md`) are left unchanged.
    Summaries (`*.include.g.md`) and combined dumps (`_<Folder>.g.md`) are rebuilt,
    then YAML and MdFormatter run only on `*.g.md`.

    """

    icon = "📜"
    title = "Regenerate `.g.md` in …"
    cli_available = True
    cli_hint = "md regenerate-g-md"

    @ActionBase.handle_exceptions("regenerating g.md in folder")
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
        """Delete `.g.md`, regenerate, and beautify only generated Markdown."""
        self.prose_wrap = prose_wrap
        self.print_width = print_width
        self.apply_prose_fixes = apply_prose_fixes
        self.format_code_blocks = format_code_blocks
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                "regenerating g.md in folder",
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

    @ActionBase.handle_exceptions("regenerating g.md thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        if self.folder_path is None:
            return
        self.regenerate_g_md_common(str(self.folder_path))

    def regenerate_g_md_common(self: ActionBase, folder_path: str) -> None:
        """Delete `.g.md`, regenerate summaries and combined dumps, beautify only `.g.md`.

        Args:

        - `folder_path` (`str`): Folder to process recursively.

        """
        self.add_line("🔵 Delete *.g.md files")
        self.add_line(h.md.delete_g_md_files_recursively(folder_path))

        self.add_line("🔵 Generate summaries")
        for path_notes_for_summaries in self.config.get("paths_notes_for_summaries") or []:
            if (Path(path_notes_for_summaries).resolve()).is_relative_to(Path(folder_path).resolve()):
                self.add_line(h.md.generate_summaries(path_notes_for_summaries))

        OnRegenerateGMd._format_g_md_files(self, folder_path)

        self.add_line("🔵 Combine MD files")
        self.add_line(h.md.combine_markdown_files_recursively(folder_path, is_delete_g_md_files=False))

        OnRegenerateGMd._format_g_md_files(self, folder_path)

    @ActionBase.handle_exceptions("regenerating g.md thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    @staticmethod
    def _format_g_md_files(action: ActionBase, folder_path: str) -> None:
        """Apply YAML and MdFormatter only to `*.g.md` files."""

        def skip_non_g_md(path: Path) -> bool:
            return not path.name.endswith(".g.md")

        action.add_line("🔵 Format YAML in *.g.md")
        action.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                h.md.format_yaml,
                skip_file=skip_non_g_md,
            )
        )

        action.add_line("🔵 Format Markdown in *.g.md")
        prose_wrap = getattr(action, "prose_wrap", "preserve")
        print_width = getattr(action, "print_width", 80)
        apply_prose_fixes = getattr(action, "apply_prose_fixes", True)
        format_code_blocks = getattr(action, "format_code_blocks", True)
        end_of_line = h.dev.get_preferred_end_of_line(folder_path)
        formatter = h.md_format.MdFormatter(
            end_of_line=end_of_line,
            prose_wrap=prose_wrap,
            print_width=print_width,
            apply_prose_fixes=apply_prose_fixes,
            format_code_blocks=format_code_blocks,
        )
        action.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                formatter.format_file,
                skip_file=skip_non_g_md,
            )
        )
