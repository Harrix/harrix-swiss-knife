---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `beautify_md_folder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnBeautifyMdFolder`](#%EF%B8%8F-class-onbeautifymdfolder)
  - [⚙️ Method `beautify_markdown_common`](#%EF%B8%8F-method-beautify_markdown_common)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnBeautifyMdFolder`

```python
class OnBeautifyMdFolder(ActionBase)
```

Apply comprehensive beautification to all Markdown notes.

This action performs multiple enhancement operations on Markdown files across
all configured note directories, including:

- Adding image captions
- Generating tables of contents
- Formatting YAML frontmatter
- Formatting Markdown with the harrix-pylib formatter

It provides a one-click solution for maintaining a high-quality, consistently
formatted collection of Markdown documents.

<details>
<summary>Code:</summary>

```python
class OnBeautifyMdFolder(ActionBase):

    icon = "💎"
    title = "Beautify MD in …"
    cli_available = True
    cli_hint = "md beautify-md"

    def beautify_markdown_common(
        self: ActionBase, folder_path: str, *, is_include_summaries_and_combine: bool = False
    ) -> None:
        """Perform common beautification operations on Markdown files in a folder.

        This method applies a series of enhancement operations to all Markdown files
        in the specified folder, including file renaming (spaces to hyphens), image
        caption generation, table of contents creation, YAML formatting, and Markdown
        formatting. Optionally includes summary generation and file combination operations.

        Args:

        - `folder_path` (`str`): Path to the folder containing Markdown files to process.
        - `is_include_summaries_and_combine` (`bool`): Whether to include summary generation
          and file combination steps. Defaults to `False`.

        Returns:

        - `None`: This method performs operations and logs results but returns nothing.

        Note:

        - The method preserves the exact execution order of operations for consistency.
        - All operations are logged using `self.add_line()` for user feedback.
        - If `is_include_summaries_and_combine` is `True`, the method will first delete
          existing `*.g.md` files, generate summaries, format Markdown (including
          `*.include.g.md`), then combine files so included tables keep formatting.
        - File renaming converts spaces to hyphens in filenames for better URL compatibility.
        - After formatting, empty folders are removed via `h.file.remove_empty_folders`
          (ignored paths such as `.git` and `.venv` are skipped).

        """
        if is_include_summaries_and_combine:
            # Delete *.g.md files once for the whole tree (expects a folder, not per-file apply_func).
            self.add_line("🔵 Delete *.g.md files")
            self.add_line(h.md.delete_g_md_files_recursively(folder_path))

        def skip_generated_g_md(path: Path) -> bool:
            return path.name.endswith(".g.md") and not path.name.endswith(".include.g.md")

        # Rename files with spaces to hyphens
        self.add_line("🔵 Rename files with spaces to hyphens")
        self.add_line(h.file.apply_func(folder_path, ".md", h.file.rename_file_spaces_to_hyphens))

        # Sort sections in Markdown files (using YAML frontmatter if present)
        self.add_line("🔵 Sort sections in Markdown files (YAML-controlled)")
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                lambda filename: h.md.sort_sections(filename, is_sort_section_from_yaml=True),
                skip_file=skip_generated_g_md,
            )
        )

        # Generate image captions
        self.add_line("🔵 Generate image captions")
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                h.md.generate_image_captions,
                skip_file=skip_generated_g_md,
            )
        )

        # Generate TOC
        self.add_line("🔵 Generate TOC")
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                h.md.generate_toc_with_links,
                skip_file=skip_generated_g_md,
            )
        )

        if is_include_summaries_and_combine:
            # Generate summaries (e.g. table.include.g.md) before Markdown formatting
            # so combine below picks up already-aligned tables and other format fixes.
            self.add_line("🔵 Generate summaries")
            for path_notes_for_summaries in self.config["paths_notes_for_summaries"]:
                if (Path(path_notes_for_summaries).resolve()).is_relative_to(Path(folder_path).resolve()):
                    self.add_line(h.md.generate_summaries(path_notes_for_summaries))

        # Format YAML (skip generated *.g.md dumps so raw-markdown fences stay intact).
        # When regenerating .g.md, this must run before combine so *.include.g.md
        # (and other sources) are formatted before their content is copied in.
        self.add_line("🔵 Format YAML")
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                h.md.format_yaml,
                skip_file=skip_generated_g_md,
            )
        )

        # Format Markdown (same skip for generated dumps)
        self.add_line("🔵 Format Markdown")
        prose_wrap = getattr(self, "prose_wrap", "preserve")
        print_width = getattr(self, "print_width", 80)
        apply_prose_fixes = getattr(self, "apply_prose_fixes", True)
        end_of_line = h.dev.get_preferred_end_of_line(folder_path)
        formatter = h.md_format.MdFormatter(
            end_of_line=end_of_line,
            prose_wrap=prose_wrap,
            print_width=print_width,
            apply_prose_fixes=apply_prose_fixes,
        )
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                formatter.format_file,
                skip_file=skip_generated_g_md,
            )
        )

        if is_include_summaries_and_combine:
            # Combine after formatting so included tables keep column alignment.
            self.add_line("🔵 Combine MD files")
            self.add_line(h.md.combine_markdown_files_recursively(folder_path, is_delete_g_md_files=False))

        self.add_line("🔵 Remove empty folders")
        self.add_line(h.file.remove_empty_folders(folder_path))

    @ActionBase.handle_exceptions("beautifying markdown folder")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        prose_wrap: str = "preserve",
        print_width: int = 80,
        apply_prose_fixes: bool = True,
        **_kwargs: Any,
    ) -> None:
        """Apply comprehensive beautification to all Markdown notes."""
        self.prose_wrap = prose_wrap
        self.print_width = print_width
        self.apply_prose_fixes = apply_prose_fixes
        if noninteractive:
            if folder_path is None:
                self.handle_error(
                    ValueError("folder_path is required when noninteractive is True"),
                    "beautifying markdown folder",
                )
                return
            self.folder_path = Path(folder_path).resolve()
            self.in_thread()
            return

        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("beautifying markdown thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        if self.folder_path is None:
            return
        self.beautify_markdown_common(str(self.folder_path), is_include_summaries_and_combine=False)

    @ActionBase.handle_exceptions("beautifying markdown thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `beautify_markdown_common`

```python
def beautify_markdown_common(self: ActionBase, folder_path: str) -> None
```

Perform common beautification operations on Markdown files in a folder.

This method applies a series of enhancement operations to all Markdown files
in the specified folder, including file renaming (spaces to hyphens), image
caption generation, table of contents creation, YAML formatting, and Markdown
formatting. Optionally includes summary generation and file combination operations.

Args:

- `folder_path` (`str`): Path to the folder containing Markdown files to process.
- `is_include_summaries_and_combine` (`bool`): Whether to include summary generation
  and file combination steps. Defaults to `False`.

Returns:

- `None`: This method performs operations and logs results but returns nothing.

Note:

- The method preserves the exact execution order of operations for consistency.
- All operations are logged using `self.add_line()` for user feedback.
- If `is_include_summaries_and_combine` is `True`, the method will first delete
  existing `*.g.md` files, generate summaries, format Markdown (including
  `*.include.g.md`), then combine files so included tables keep formatting.
- File renaming converts spaces to hyphens in filenames for better URL compatibility.
- After formatting, empty folders are removed via `h.file.remove_empty_folders`
  (ignored paths such as `.git` and `.venv` are skipped).

<details>
<summary>Code:</summary>

```python
def beautify_markdown_common(
        self: ActionBase, folder_path: str, *, is_include_summaries_and_combine: bool = False
    ) -> None:
        if is_include_summaries_and_combine:
            # Delete *.g.md files once for the whole tree (expects a folder, not per-file apply_func).
            self.add_line("🔵 Delete *.g.md files")
            self.add_line(h.md.delete_g_md_files_recursively(folder_path))

        def skip_generated_g_md(path: Path) -> bool:
            return path.name.endswith(".g.md") and not path.name.endswith(".include.g.md")

        # Rename files with spaces to hyphens
        self.add_line("🔵 Rename files with spaces to hyphens")
        self.add_line(h.file.apply_func(folder_path, ".md", h.file.rename_file_spaces_to_hyphens))

        # Sort sections in Markdown files (using YAML frontmatter if present)
        self.add_line("🔵 Sort sections in Markdown files (YAML-controlled)")
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                lambda filename: h.md.sort_sections(filename, is_sort_section_from_yaml=True),
                skip_file=skip_generated_g_md,
            )
        )

        # Generate image captions
        self.add_line("🔵 Generate image captions")
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                h.md.generate_image_captions,
                skip_file=skip_generated_g_md,
            )
        )

        # Generate TOC
        self.add_line("🔵 Generate TOC")
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                h.md.generate_toc_with_links,
                skip_file=skip_generated_g_md,
            )
        )

        if is_include_summaries_and_combine:
            # Generate summaries (e.g. table.include.g.md) before Markdown formatting
            # so combine below picks up already-aligned tables and other format fixes.
            self.add_line("🔵 Generate summaries")
            for path_notes_for_summaries in self.config["paths_notes_for_summaries"]:
                if (Path(path_notes_for_summaries).resolve()).is_relative_to(Path(folder_path).resolve()):
                    self.add_line(h.md.generate_summaries(path_notes_for_summaries))

        # Format YAML (skip generated *.g.md dumps so raw-markdown fences stay intact).
        # When regenerating .g.md, this must run before combine so *.include.g.md
        # (and other sources) are formatted before their content is copied in.
        self.add_line("🔵 Format YAML")
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                h.md.format_yaml,
                skip_file=skip_generated_g_md,
            )
        )

        # Format Markdown (same skip for generated dumps)
        self.add_line("🔵 Format Markdown")
        prose_wrap = getattr(self, "prose_wrap", "preserve")
        print_width = getattr(self, "print_width", 80)
        apply_prose_fixes = getattr(self, "apply_prose_fixes", True)
        end_of_line = h.dev.get_preferred_end_of_line(folder_path)
        formatter = h.md_format.MdFormatter(
            end_of_line=end_of_line,
            prose_wrap=prose_wrap,
            print_width=print_width,
            apply_prose_fixes=apply_prose_fixes,
        )
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                formatter.format_file,
                skip_file=skip_generated_g_md,
            )
        )

        if is_include_summaries_and_combine:
            # Combine after formatting so included tables keep column alignment.
            self.add_line("🔵 Combine MD files")
            self.add_line(h.md.combine_markdown_files_recursively(folder_path, is_delete_g_md_files=False))

        self.add_line("🔵 Remove empty folders")
        self.add_line(h.file.remove_empty_folders(folder_path))
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Apply comprehensive beautification to all Markdown notes.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        prose_wrap: str = "preserve",
        print_width: int = 80,
        apply_prose_fixes: bool = True,
        **_kwargs: Any,
    ) -> None:
        self.prose_wrap = prose_wrap
        self.print_width = print_width
        self.apply_prose_fixes = apply_prose_fixes
        if noninteractive:
            if folder_path is None:
                self.handle_error(
                    ValueError("folder_path is required when noninteractive is True"),
                    "beautifying markdown folder",
                )
                return
            self.folder_path = Path(folder_path).resolve()
            self.in_thread()
            return

        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        if self.folder_path is None:
            return
        self.beautify_markdown_common(str(self.folder_path), is_include_summaries_and_combine=False)
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
