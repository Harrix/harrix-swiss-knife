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
    configured note directories (`paths_notes`), including:

    - Adding image captions
    - Generating tables of contents
    - Creating summaries for specified directories
    - Combining related Markdown files
    - Formatting YAML frontmatter
    - Formatting Markdown with the harrix-pylib formatter

    In the GUI it opens a checkbox list of `paths_notes` (all checked by default)
    so several folders can be processed in one run.

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
        folder_paths: list[Path] | None = None,
        noninteractive: bool = False,
        prose_wrap: str = "preserve",
        print_width: int = 80,
        apply_prose_fixes: bool = True,
        format_code_blocks: bool = True,
        **_kwargs: Any,
    ) -> None:
        """Apply comprehensive beautification to selected Markdown note folders."""
        self.prose_wrap = prose_wrap
        self.print_width = print_width
        self.apply_prose_fixes = apply_prose_fixes
        self.format_code_blocks = format_code_blocks

        selected = self._resolve_folder_paths(
            folder_path=folder_path,
            folder_paths=folder_paths,
            noninteractive=noninteractive,
        )
        if selected is None:
            return
        if not selected:
            self.add_line("❌ No note folders selected.")
            if not noninteractive:
                self.show_result()
            return

        kept: list[Path] = []
        for path in selected:
            if reject_python_project_for_md_beautify(self, path, noninteractive=noninteractive):
                continue
            kept.append(path)
        if not kept:
            return

        self.folder_paths = kept
        self.folder_path = kept[0]

        if noninteractive:
            self.in_thread()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("beautifying and regenerating thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        folders = getattr(self, "folder_paths", None) or []
        if not folders and getattr(self, "folder_path", None) is not None:
            folders = [self.folder_path]
        total = len(folders)
        for index, folder in enumerate(folders, start=1):
            self.add_line(f"🔵 Starting processing for path ({index}/{total}): {folder}")
            OnBeautifyMd.beautify_markdown_common(self, str(folder), is_include_summaries_and_combine=True)
        if total > 1:
            self.add_line(f"✅ Finished {total} note folder(s).")

    @ActionBase.handle_exceptions("beautifying and regenerating thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _configured_note_folders(self) -> list[Path]:
        """Return existing directories from `paths_notes` (resolved, unique)."""
        raw = self.config.get("paths_notes")
        if not isinstance(raw, list):
            return []
        folders: list[Path] = []
        seen: set[Path] = set()
        for entry in raw:
            path = Path(str(entry)).expanduser()
            try:
                resolved = path.resolve()
            except OSError:
                self.add_line(f"⚠️ Could not resolve path: {entry}")
                continue
            if not resolved.is_dir():
                self.add_line(f"⚠️ Skip (not a directory): {resolved}")
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            folders.append(resolved)
        return folders

    def _prompt_note_folders(self) -> list[Path] | None:
        """Show a checkbox list of `paths_notes` with every folder checked by default."""
        folders = self._configured_note_folders()
        if not folders:
            default = str(self.config.get("path_notes") or ".")
            picked = self.dialogs.get_existing_directory("Select note folder", default)
            return [picked] if picked is not None else None

        labels = [str(path) for path in folders]
        selected = self.dialogs.get_checkbox_selection(
            self.title,
            "Select note folders to beautify. All folders are checked by default.",
            labels,
            default_selected=list(labels),
        )
        if selected is None:
            return None
        return [Path(label).resolve() for label in selected]

    def _resolve_folder_paths(
        self,
        *,
        folder_path: Path | None,
        folder_paths: list[Path] | None,
        noninteractive: bool,
    ) -> list[Path] | None:
        """Return folders to process, or `None` when the user cancelled."""
        if folder_paths is not None:
            return [Path(path).resolve() for path in folder_paths]
        if folder_path is not None:
            return [Path(folder_path).resolve()]
        if noninteractive:
            folders = self._configured_note_folders()
            if not folders:
                self.add_line(
                    "❌ folder_path is required when noninteractive is True and `paths_notes` is empty.",
                )
            return folders
        return self._prompt_note_folders()
