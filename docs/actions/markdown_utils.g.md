---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `markdown_utils.py`

## Function `beautify_markdown_common`

```python
def beautify_markdown_common(self: ActionBase, folder_path: str) -> None
```

Perform common beautification operations on Markdown files in a folder.

This method applies a series of enhancement operations to all Markdown files
in the specified folder, including image caption generation, table of contents
creation, YAML formatting, and Prettier formatting. Optionally includes
summary generation and file combination operations.

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

    # Prettier
    self.add_line("🔵 Prettier")
    commands = "prettier --parser markdown --write **/*.md --end-of-line crlf"
    result = h.dev.run_command(commands, cwd=str(folder_path))
    self.add_line(result)
```

</details>
