---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `beautify_md_folder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnBeautifyMdFolder`](#️-class-onbeautifymdfolder)
  - [⚙️ Method `beautify_markdown_common`](#️-method-beautify_markdown_common)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `in_thread`](#️-method-in_thread)
  - [⚙️ Method `thread_after`](#️-method-thread_after)

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
        existing `*.g.md` files, then generate summaries and combine files.
        - File renaming converts spaces to hyphens in filenames for better URL compatibility.

        """
        if is_include_summaries_and_combine:
            # Delete *.g.md files
            self.add_line("🔵 Delete *.g.md files")
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.delete_g_md_files_recursively))

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
            )
        )

        # Generate image captions
        self.add_line("🔵 Generate image captions")
        self.add_line(h.file.apply_func(folder_path, ".md", h.md.generate_image_captions))

        # Generate TOC
        self.add_line("🔵 Generate TOC")
        self.add_line(h.file.apply_func(folder_path, ".md", h.md.generate_toc_with_links))

        if is_include_summaries_and_combine:
            # Generate summaries
            self.add_line("🔵 Generate summaries")
            for path_notes_for_summaries in self.config["paths_notes_for_summaries"]:
                if (Path(path_notes_for_summaries).resolve()).is_relative_to(Path(folder_path).resolve()):
                    self.add_line(h.md.generate_summaries(path_notes_for_summaries))

            # Combine MD files
            self.add_line("🔵 Combine MD files")
            self.add_line(h.md.combine_markdown_files_recursively(folder_path, is_delete_g_md_files=False))

        # Format YAML
        self.add_line("🔵 Format YAML")
        self.add_line(h.file.apply_func(folder_path, ".md", h.md.format_yaml))

        # Format Markdown
        self.add_line("🔵 Format Markdown")
        self.add_line(h.md.format_markdown_folder(folder_path))

    @ActionBase.handle_exceptions("beautifying markdown folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Apply comprehensive beautification to all Markdown notes."""
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
  existing `*.g.md` files, then generate summaries and combine files.
- File renaming converts spaces to hyphens in filenames for better URL compatibility.

<details>
<summary>Code:</summary>

```python
def beautify_markdown_common(
        self: ActionBase, folder_path: str, *, is_include_summaries_and_combine: bool = False
    ) -> None:
        if is_include_summaries_and_combine:
            # Delete *.g.md files
            self.add_line("🔵 Delete *.g.md files")
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.delete_g_md_files_recursively))

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
            )
        )

        # Generate image captions
        self.add_line("🔵 Generate image captions")
        self.add_line(h.file.apply_func(folder_path, ".md", h.md.generate_image_captions))

        # Generate TOC
        self.add_line("🔵 Generate TOC")
        self.add_line(h.file.apply_func(folder_path, ".md", h.md.generate_toc_with_links))

        if is_include_summaries_and_combine:
            # Generate summaries
            self.add_line("🔵 Generate summaries")
            for path_notes_for_summaries in self.config["paths_notes_for_summaries"]:
                if (Path(path_notes_for_summaries).resolve()).is_relative_to(Path(folder_path).resolve()):
                    self.add_line(h.md.generate_summaries(path_notes_for_summaries))

            # Combine MD files
            self.add_line("🔵 Combine MD files")
            self.add_line(h.md.combine_markdown_files_recursively(folder_path, is_delete_g_md_files=False))

        # Format YAML
        self.add_line("🔵 Format YAML")
        self.add_line(h.file.apply_func(folder_path, ".md", h.md.format_yaml))

        # Format Markdown
        self.add_line("🔵 Format Markdown")
        self.add_line(h.md.format_markdown_folder(folder_path))
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Apply comprehensive beautification to all Markdown notes.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
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
