---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `markdown.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnBeautifyMdFolder`](#%EF%B8%8F-class-onbeautifymdfolder)
  - [⚙️ Method `beautify_markdown_common`](#%EF%B8%8F-method-beautify_markdown_common)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
- [🏛️ Class `OnBeautifyMdFolderAndRegenerateGMd`](#%EF%B8%8F-class-onbeautifymdfolderandregenerategmd)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-1)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-1)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-1)
- [🏛️ Class `OnCheckMdFolder`](#%EF%B8%8F-class-oncheckmdfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-2)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-2)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-2)
- [🏛️ Class `OnDecreaseHeadingLevelContent`](#%EF%B8%8F-class-ondecreaseheadinglevelcontent)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-3)
- [🏛️ Class `OnDownloadAndReplaceImagesFolder`](#%EF%B8%8F-class-ondownloadandreplaceimagesfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-4)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-3)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-3)
- [🏛️ Class `OnGenerateShortNoteTocWithLinks`](#%EF%B8%8F-class-ongenerateshortnotetocwithlinks)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-5)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-4)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-4)
- [🏛️ Class `OnGetListMoviesBooks`](#%EF%B8%8F-class-ongetlistmoviesbooks)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-6)
- [🏛️ Class `OnIncreaseHeadingLevelContent`](#%EF%B8%8F-class-onincreaseheadinglevelcontent)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-7)
- [🏛️ Class `OnNewArticle`](#%EF%B8%8F-class-onnewarticle)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-8)
- [🏛️ Class `OnNewDiary`](#%EF%B8%8F-class-onnewdiary)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-9)
- [🏛️ Class `OnNewDiaryDream`](#%EF%B8%8F-class-onnewdiarydream)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-10)
- [🏛️ Class `OnNewNoteDialog`](#%EF%B8%8F-class-onnewnotedialog)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-11)
- [🏛️ Class `OnNewNoteDialogWithImages`](#%EF%B8%8F-class-onnewnotedialogwithimages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-12)
- [🏛️ Class `OnOptimizeImagesFolder`](#%EF%B8%8F-class-onoptimizeimagesfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-13)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-5)
  - [⚙️ Method `optimize_images_content_line`](#%EF%B8%8F-method-optimize_images_content_line)
  - [⚙️ Method `optimize_images_in_md_compare_sizes`](#%EF%B8%8F-method-optimize_images_in_md_compare_sizes)
  - [⚙️ Method `optimize_images_in_md_content`](#%EF%B8%8F-method-optimize_images_in_md_content)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-5)
- [🏛️ Class `OnOptimizeSelectedImages`](#%EF%B8%8F-class-onoptimizeselectedimages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-14)
  - [⚙️ Method `find_markdown_file_one_level_up`](#%EF%B8%8F-method-find_markdown_file_one_level_up)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-6)
  - [⚙️ Method `optimize_selected_images_content`](#%EF%B8%8F-method-optimize_selected_images_content)
  - [⚙️ Method `optimize_selected_images_content_line`](#%EF%B8%8F-method-optimize_selected_images_content_line)
  - [⚙️ Method `optimize_selected_images_in_md`](#%EF%B8%8F-method-optimize_selected_images_in_md)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-6)
- [🏛️ Class `OnQuotesFormatAsMarkdownContent`](#%EF%B8%8F-class-onquotesformatasmarkdowncontent)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-15)
- [🏛️ Class `OnQuotesGenerateAuthorAndBook`](#%EF%B8%8F-class-onquotesgenerateauthorandbook)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-16)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-7)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-7)
- [🏛️ Class `OnSortSections`](#%EF%B8%8F-class-onsortsections)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-17)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-8)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-8)

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
- Running Prettier for consistent formatting

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
        caption generation, table of contents creation, YAML formatting, and Prettier
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

        # Prettier
        self.add_line("🔵 Prettier")
        commands = "prettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_command(commands, cwd=str(folder_path))
        self.add_line(result)

    @ActionBase.handle_exceptions("beautifying markdown folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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
caption generation, table of contents creation, YAML formatting, and Prettier
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

        # Prettier
        self.add_line("🔵 Prettier")
        commands = "prettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_command(commands, cwd=str(folder_path))
        self.add_line(result)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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

## 🏛️ Class `OnBeautifyMdFolderAndRegenerateGMd`

```python
class OnBeautifyMdFolderAndRegenerateGMd(ActionBase)
```

Apply comprehensive beautification to all Markdown notes.

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

<details>
<summary>Code:</summary>

```python
class OnBeautifyMdFolderAndRegenerateGMd(ActionBase):

    icon = "💎"
    title = "Beautify MD and regenerate .g.md in …"
    bold_title = True

    @ActionBase.handle_exceptions("beautifying markdown folder and regenerating g.md")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
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
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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
        OnBeautifyMdFolder.beautify_markdown_common(self, str(self.folder_path), is_include_summaries_and_combine=True)
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

## 🏛️ Class `OnCheckMdFolder`

```python
class OnCheckMdFolder(ActionBase)
```

Action to check all Markdown files in a folder for errors with Harrix rules.

<details>
<summary>Code:</summary>

```python
class OnCheckMdFolder(ActionBase):

    icon = "🚧"
    title = "Check in …"

    @ActionBase.handle_exceptions("checking markdown folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("markdown folder checking thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        checker = h.md_check.MarkdownChecker()
        if self.folder_path is None:
            return
        errors = h.file.check_func(self.folder_path, ".md", checker)
        if errors:
            self.add_line("\n".join(errors))
            self.add_line(f"🔢 Count errors = {len(errors)}")
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")

    @ActionBase.handle_exceptions("markdown folder checking thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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
        checker = h.md_check.MarkdownChecker()
        if self.folder_path is None:
            return
        errors = h.file.check_func(self.folder_path, ".md", checker)
        if errors:
            self.add_line("\n".join(errors))
            self.add_line(f"🔢 Count errors = {len(errors)}")
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")
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
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>

## 🏛️ Class `OnDecreaseHeadingLevelContent`

```python
class OnDecreaseHeadingLevelContent(ActionBase)
```

Decrease the heading level of all headings in Markdown content.

This action takes Markdown content and decreases the level of all headings
by removing one '#' character from each heading, making them one level
shallower in the document hierarchy.

<details>
<summary>Code:</summary>

```python
class OnDecreaseHeadingLevelContent(ActionBase):

    icon = "👈"
    title = "Heading level: Decrease"

    @ActionBase.handle_exceptions("decreasing heading level")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        content = self.get_text_textarea(
            "Markdown content", "Input Markdown content", "# Title\n\nText\n\n## Subtitle\n\nText"
        )
        if not content:
            return

        new_content = h.md.decrease_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        content = self.get_text_textarea(
            "Markdown content", "Input Markdown content", "# Title\n\nText\n\n## Subtitle\n\nText"
        )
        if not content:
            return

        new_content = h.md.decrease_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()
```

</details>

## 🏛️ Class `OnDownloadAndReplaceImagesFolder`

```python
class OnDownloadAndReplaceImagesFolder(ActionBase)
```

Download remote images and replace URLs with local references in multiple Markdown files.

This action processes all Markdown files in a selected folder to find image URLs,
downloads the images to local directories, and updates the Markdown files to reference
these local copies instead of the remote URLs, improving document portability and
reducing external dependencies across an entire collection of documents.

<details>
<summary>Code:</summary>

```python
class OnDownloadAndReplaceImagesFolder(ActionBase):

    icon = "📥"
    title = "Download images in …"

    @ActionBase.handle_exceptions("downloading images in folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("downloading images folder thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.download_and_replace_images))

    @ActionBase.handle_exceptions("downloading images folder thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
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
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.download_and_replace_images))
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
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>

## 🏛️ Class `OnGenerateShortNoteTocWithLinks`

```python
class OnGenerateShortNoteTocWithLinks(ActionBase)
```

Generate a condensed version of a document with only its table of contents.

This action creates a shortened version of a selected Markdown file that
includes only the document's title and table of contents with working links.
Useful for creating quick reference documents or previews of longer content.

<details>
<summary>Code:</summary>

```python
class OnGenerateShortNoteTocWithLinks(ActionBase):

    icon = "📑"
    title = "Generate a short version with only TOC"

    @ActionBase.handle_exceptions("generating short note with TOC")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.filename = self.get_open_filename(
            "Open Markdown file",
            self.config["path_articles"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("generating short note TOC thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(h.md.generate_short_note_toc_with_links(self.filename))

    @ActionBase.handle_exceptions("generating short note TOC thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.filename = self.get_open_filename(
            "Open Markdown file",
            self.config["path_articles"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
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
        if self.filename is None:
            return
        self.add_line(h.md.generate_short_note_toc_with_links(self.filename))
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
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()
```

</details>

## 🏛️ Class `OnGetListMoviesBooks`

```python
class OnGetListMoviesBooks(ActionBase)
```

Extract and format a list of movies or books from Markdown content.

This action takes Markdown content with level-3 headings (`### Title`)
and converts them into a bulleted list, counting the total number of items.
Useful for creating web-friendly lists from structured Markdown content.

<details>
<summary>Code:</summary>

```python
class OnGetListMoviesBooks(ActionBase):

    icon = "🎬"
    title = "Get a list of movies, books for web"

    @ActionBase.handle_exceptions("extracting movies/books list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        default_text = """### Song of the Sea: 8.5

- **Original or English title:** Song of the Sea
- **Date watching:** 2019-10-28
- **Kinopoisk:** <https://www.kinopoisk.ru/film/714248/>
- **IMDb:** <https://www.imdb.com/title/tt1865505/>
- **Comments:** A beautiful cartoon that needs to be shown to children.

### Red Turtle: 9

- **Original or English title:** La tortue rouge
- **Date watching:** 2019-10-12
- **Kinopoisk:** <https://www.kinopoisk.ru/film/879827/>
- **IMDb:** <https://www.imdb.com/title/tt3666024/>
- **Comments:** Beautiful meditative cartoon."""

        content = self.get_text_textarea("Markdown content", "Input Markdown content", default_text)
        if not content:
            return

        result = ""
        count = 0
        start_element = "### " if "### " in content else "## "
        for line in content.splitlines():
            if line.startswith(start_element):
                result += f"- {line[4:].strip()}\n"
                count += 1

        result += f"\nCount: {count}"
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        default_text = """### Song of the Sea: 8.5

- **Original or English title:** Song of the Sea
- **Date watching:** 2019-10-28
- **Kinopoisk:** <https://www.kinopoisk.ru/film/714248/>
- **IMDb:** <https://www.imdb.com/title/tt1865505/>
- **Comments:** A beautiful cartoon that needs to be shown to children.

### Red Turtle: 9

- **Original or English title:** La tortue rouge
- **Date watching:** 2019-10-12
- **Kinopoisk:** <https://www.kinopoisk.ru/film/879827/>
- **IMDb:** <https://www.imdb.com/title/tt3666024/>
- **Comments:** Beautiful meditative cartoon."""

        content = self.get_text_textarea("Markdown content", "Input Markdown content", default_text)
        if not content:
            return

        result = ""
        count = 0
        start_element = "### " if "### " in content else "## "
        for line in content.splitlines():
            if line.startswith(start_element):
                result += f"- {line[4:].strip()}\n"
                count += 1

        result += f"\nCount: {count}"
        self.add_line(result)
        self.show_result()
```

</details>

## 🏛️ Class `OnIncreaseHeadingLevelContent`

```python
class OnIncreaseHeadingLevelContent(ActionBase)
```

Increase the heading level of all headings in Markdown content.

This action takes Markdown content and increases the level of all headings
by adding an additional '#' character to each heading, making them one level
deeper in the document hierarchy.

<details>
<summary>Code:</summary>

```python
class OnIncreaseHeadingLevelContent(ActionBase):

    icon = "👉"
    title = "Heading level: Increase"

    @ActionBase.handle_exceptions("increasing heading level")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        content = self.get_text_textarea(
            "Markdown content", "Input Markdown content", "# Title\n\nText\n\n## Subtitle\n\nText"
        )
        if not content:
            return

        new_content = h.md.increase_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        content = self.get_text_textarea(
            "Markdown content", "Input Markdown content", "# Title\n\nText\n\n## Subtitle\n\nText"
        )
        if not content:
            return

        new_content = h.md.increase_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()
```

</details>

## 🏛️ Class `OnNewArticle`

```python
class OnNewArticle(ActionBase)
```

Create a new article with predefined template.

This action prompts the user for an article title, creates a new Markdown file
in the configured articles directory, and opens it in the configured editor.

<details>
<summary>Code:</summary>

```python
class OnNewArticle(ActionBase):

    icon = "✍️"
    title = "New article"

    @ActionBase.handle_exceptions("creating new article")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        article_name = self.get_text_input(
            "Article title", "Enter the name of the article (English, without spaces):", "name-of-article"
        )
        if not article_name:
            return

        article_name = article_name.replace(" ", "-")

        text = self.config["beginning_of_article"].replace(
            "[YEAR]",
            datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime("%Y"),
        )
        text = text.replace("[NAME]", article_name)
        text = text.replace(
            "[DATE]",
            datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime(
                "%Y-%m-%d"
            ),
        )
        text += f"\n# {article_name.capitalize().replace('-', ' ')}\n\n\n"

        result, filename = h.md.add_note(Path(self.config["path_articles"]), article_name, text, is_with_images=True)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_articles"]}" "{filename}"')
        self.add_line(result)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        article_name = self.get_text_input(
            "Article title", "Enter the name of the article (English, without spaces):", "name-of-article"
        )
        if not article_name:
            return

        article_name = article_name.replace(" ", "-")

        text = self.config["beginning_of_article"].replace(
            "[YEAR]",
            datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime("%Y"),
        )
        text = text.replace("[NAME]", article_name)
        text = text.replace(
            "[DATE]",
            datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime(
                "%Y-%m-%d"
            ),
        )
        text += f"\n# {article_name.capitalize().replace('-', ' ')}\n\n\n"

        result, filename = h.md.add_note(Path(self.config["path_articles"]), article_name, text, is_with_images=True)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_articles"]}" "{filename}"')
        self.add_line(result)
```

</details>

## 🏛️ Class `OnNewDiary`

```python
class OnNewDiary(ActionBase)
```

Create a new diary entry for the current date.

This action creates a new diary Markdown file in the configured diary directory
using the current date, adds the configured template content, and opens it
in the configured editor.

<details>
<summary>Code:</summary>

```python
class OnNewDiary(ActionBase):

    icon = "📖"
    title = "New diary note"

    @ActionBase.handle_exceptions("creating new diary entry")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        result, filename = h.md.add_diary_new_dairy_in_year(self.config["path_diary"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        result, filename = h.md.add_diary_new_dairy_in_year(self.config["path_diary"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)
```

</details>

## 🏛️ Class `OnNewDiaryDream`

```python
class OnNewDiaryDream(ActionBase)
```

Create a new dream journal entry for the current date.

This action creates a new dream journal Markdown file in the configured dream directory
using the current date, adds the configured template content, and opens it
in the configured editor.

<details>
<summary>Code:</summary>

```python
class OnNewDiaryDream(ActionBase):

    icon = "💤"
    title = "New dream note"

    @ActionBase.handle_exceptions("creating new dream entry")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        result, filename = h.md.add_diary_new_dream_in_year(self.config["path_dream"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        result, filename = h.md.add_diary_new_dream_in_year(self.config["path_dream"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)
```

</details>

## 🏛️ Class `OnNewNoteDialog`

```python
class OnNewNoteDialog(ActionBase)
```

Create a new general note with a user-specified filename.

This action prompts the user to save a new Markdown file in the configured notes directory,
adds template content with the filename as the title, and opens it in the configured editor.
Supports optional image directory creation.

<details>
<summary>Code:</summary>

```python
class OnNewNoteDialog(ActionBase):

    icon = "📓"
    title = "New note"

    @ActionBase.handle_exceptions("creating new note")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        filename = self.get_save_filename("Save Note", self.config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        self.add_line(f"Folder path: {filename.parent}")
        self.add_line(f"File name without extension: {filename.stem}")

        is_with_images = kwargs.get("is_with_images", False)

        text = self.config["beginning_of_md"] + f"\n# {filename.stem}\n\n\n"

        filename_final = filename.stem.replace("-", "--").replace(" ", "-")

        result, filename = h.md.add_note(filename.parent, filename_final, text, is_with_images=is_with_images)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        filename = self.get_save_filename("Save Note", self.config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        self.add_line(f"Folder path: {filename.parent}")
        self.add_line(f"File name without extension: {filename.stem}")

        is_with_images = kwargs.get("is_with_images", False)

        text = self.config["beginning_of_md"] + f"\n# {filename.stem}\n\n\n"

        filename_final = filename.stem.replace("-", "--").replace(" ", "-")

        result, filename = h.md.add_note(filename.parent, filename_final, text, is_with_images=is_with_images)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)
```

</details>

## 🏛️ Class `OnNewNoteDialogWithImages`

```python
class OnNewNoteDialogWithImages(OnNewNoteDialog)
```

Create a new general note with image support.

This action extends the OnNewNoteDialog action by automatically creating
an associated images directory for the new note.

<details>
<summary>Code:</summary>

```python
class OnNewNoteDialogWithImages(OnNewNoteDialog):

    icon = "📓"
    title = "New note with images"

    @ActionBase.handle_exceptions("creating new note with images")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        super().execute(is_with_images=True)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        super().execute(is_with_images=True)
```

</details>

## 🏛️ Class `OnOptimizeImagesFolder`

```python
class OnOptimizeImagesFolder(ActionBase)
```

Optimize images in Markdown files with PNG/AVIF size comparison.

<details>
<summary>Code:</summary>

```python
class OnOptimizeImagesFolder(ActionBase):

    icon = "🖼️"
    title = "Optimize images in MD in …"

    @ActionBase.handle_exceptions("optimizing images with size comparison")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("optimizing images with size comparison thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", self.optimize_images_in_md_compare_sizes))

    def optimize_images_content_line(
        self,
        markdown_line: str,
        path_md: Path | str,
        image_folder: str = "img",
        *,
        is_convert_png_to_avif: bool = False,
        is_compare_png_avif_sizes: bool = False,
    ) -> str:
        """Process a single line of Markdown to optimize any image reference it contains.

        Args:
        - `markdown_line` (`str`): A single line from the Markdown document.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
        - `is_convert_png_to_avif` (`bool`): Flag for converting PNG to AVIF. Defaults to `False`.
        - `is_compare_png_avif_sizes` (`bool`): Flag for comparing PNG and AVIF sizes and keeping smaller.
          Defaults to `False`.

        Returns:
        - `str`: The processed Markdown line, with image references updated if needed.

        """
        result_line = markdown_line
        should_process = True

        # Regular expression to match Markdown image with remote URL (http or https)
        pattern = r"^\!\[(.*?)\]\((http.*?)\)$"
        match = re.search(pattern, markdown_line.strip())

        # If the line contains a remote image, don't process it
        if match:
            should_process = False

        # Regular expression to match Markdown image with local path
        local_pattern = r"^\!\[(.*?)\]\((.*?)\)$"
        local_match = re.search(local_pattern, markdown_line.strip())

        if should_process and local_match:
            alt_text = local_match.group(1)
            image_path = local_match.group(2)

            # Check if this is a local image (not a remote URL)
            if not image_path.startswith("http"):
                # Convert path_md to Path object if it's a string
                if isinstance(path_md, str):
                    path_md = Path(path_md)

                # Get the directory containing the Markdown file
                md_dir = path_md.parent if path_md.is_file() else path_md

                # Determine the complete path to the image
                image_filename = Path(image_path) if Path(image_path).is_absolute() else md_dir / image_path

                # Check if the image exists and has a supported extension
                if image_filename.exists():
                    # Get the extension
                    ext = image_filename.suffix.lower()
                    supported_extensions = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg", ".avif"]

                    if ext in supported_extensions:
                        # Determine the new extension based on the current one
                        new_ext = ext
                        if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"]:
                            new_ext = ".avif"
                        elif ext == ".png":
                            if is_compare_png_avif_sizes:
                                # Will be determined by the optimization script
                                pass
                            elif is_convert_png_to_avif:
                                new_ext = ".avif"
                            # Otherwise keep .png
                        # For .svg and .avif, keep the original extension

                        # Create temporary directory for optimization
                        with TemporaryDirectory() as temp_folder:
                            temp_folder_path = Path(temp_folder)
                            temp_image_filename = temp_folder_path / image_filename.name
                            shutil.copy(image_filename, temp_image_filename)

                            # Run the optimization command
                            commands = f'npm run optimize imagesFolder="{temp_folder}"'
                            if is_compare_png_avif_sizes and ext == ".png":
                                commands += " convertPngToAvif=compare"
                            elif is_convert_png_to_avif and ext == ".png":
                                commands += " convertPngToAvif=true"

                            h.dev.run_command(commands)

                            # Path to the optimized images directory
                            optimized_images_dir = temp_folder_path / "temp"

                            # For PNG with size comparison, check results file
                            if is_compare_png_avif_sizes and ext == ".png":
                                results_file = optimized_images_dir / "optimization_results.json"
                                if results_file.exists():
                                    with Path.open(results_file) as f:
                                        results = json.load(f)

                                    stem = image_filename.stem
                                    if stem in results:
                                        new_ext = results[stem]

                            # Path to the optimized image
                            optimized_image = optimized_images_dir / f"{image_filename.stem}{new_ext}"

                            # Check if the optimization was successful
                            if optimized_image.exists():
                                # Determine the target path for the new image
                                if Path(image_path).is_absolute():
                                    # If it was an absolute path, maintain that structure
                                    new_image_path = image_filename.with_suffix(new_ext)
                                    new_image_rel_path = str(new_image_path)
                                else:
                                    # For relative paths, ensure the image goes to the image_folder
                                    img_folder_path = md_dir / image_folder
                                    img_folder_path.mkdir(exist_ok=True)

                                    # Create the new image path
                                    new_image_path = img_folder_path / f"{image_filename.stem}{new_ext}"
                                    new_image_rel_path = f"{image_folder}/{image_filename.stem}{new_ext}"

                                # Remove the original image if we're replacing it
                                if image_filename.exists():
                                    image_filename.unlink()

                                # Copy the optimized image to the target location
                                shutil.copy(optimized_image, new_image_path)

                                # Create the new Markdown line with updated path
                                result_line = f"![{alt_text}]({new_image_rel_path})"

        return result_line

    def optimize_images_in_md_compare_sizes(self, filename: Path | str) -> str:
        """Optimize images in a Markdown file with PNG/AVIF size comparison.

        This function reads a Markdown file, processes any local images referenced in it,
        optimizes them, and for PNG images compares optimized PNG vs AVIF sizes to keep the smaller one.

        Args:
        - `filename` (`Path | str`): Path to the Markdown file to process.

        Returns:
        - `str`: A status message indicating whether the file was modified.

        """
        filename = Path(filename)
        with Path.open(filename, encoding="utf-8") as f:
            document = f.read()

        document_new = self.optimize_images_in_md_content(
            document, filename.parent, is_convert_png_to_avif=False, is_compare_png_avif_sizes=True
        )

        if document != document_new:
            with Path.open(filename, "w", encoding="utf-8") as file:
                file.write(document_new)
            return f"✅ File {filename} applied."
        return "File is not changed."

    def optimize_images_in_md_content(
        self,
        markdown_text: str,
        path_md: Path | str,
        image_folder: str = "img",
        *,
        is_convert_png_to_avif: bool = False,
        is_compare_png_avif_sizes: bool = False,
    ) -> str:
        """Optimize images referenced in Markdown content by converting them to more efficient formats.

        This function processes Markdown content to find local image references, optimizes those images,
        and updates the Markdown content to reference the optimized versions. Remote images (URLs)
        are left unchanged.

        Args:
        - `markdown_text` (`str`): The Markdown content to process.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
        - `is_convert_png_to_avif` (`bool`): Flag for converting PNG to AVIF. Defaults to `False`.
        - `is_compare_png_avif_sizes` (`bool`): Flag for comparing PNG and AVIF sizes and keeping smaller.
          Defaults to `False`.

        Returns:
        - `str`: The updated Markdown content with references to optimized images.

        Notes:
        - Images with extensions .jpg, .jpeg, .webp, .gif, and .mp4 will be converted to .avif
        - PNG files behavior depends on flags:
          - If `is_compare_png_avif_sizes` is True: compares optimized PNG vs AVIF and keeps smaller
          - If `is_convert_png_to_avif` is True: converts PNG to AVIF
          - Otherwise: optimizes PNG and keeps as PNG
        - SVG files keep their original format but may still be optimized
        - The optimization process uses an external npm script
        - Code blocks in the Markdown are preserved without changes

        """
        yaml_md, content_md = h.md.split_yaml_content(markdown_text)

        new_lines = []
        lines = content_md.split("\n")
        for line_content, is_code_block in h.md.identify_code_blocks(lines):
            if is_code_block:
                new_lines.append(line_content)
                continue

            processed_line = self.optimize_images_content_line(
                line_content,
                path_md,
                image_folder,
                is_convert_png_to_avif=is_convert_png_to_avif,
                is_compare_png_avif_sizes=is_compare_png_avif_sizes,
            )
            new_lines.append(processed_line)
        content_md = "\n".join(new_lines)

        return yaml_md + "\n\n" + content_md

    @ActionBase.handle_exceptions("optimizing images with size comparison thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
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
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", self.optimize_images_in_md_compare_sizes))
```

</details>

### ⚙️ Method `optimize_images_content_line`

```python
def optimize_images_content_line(self, markdown_line: str, path_md: Path | str, image_folder: str = "img") -> str
```

Process a single line of Markdown to optimize any image reference it contains.

Args:

- `markdown_line` (`str`): A single line from the Markdown document.
- `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
- `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
- `is_convert_png_to_avif` (`bool`): Flag for converting PNG to AVIF. Defaults to `False`.
- `is_compare_png_avif_sizes` (`bool`): Flag for comparing PNG and AVIF sizes and keeping smaller.
  Defaults to `False`.

Returns:

- `str`: The processed Markdown line, with image references updated if needed.

<details>
<summary>Code:</summary>

```python
def optimize_images_content_line(
        self,
        markdown_line: str,
        path_md: Path | str,
        image_folder: str = "img",
        *,
        is_convert_png_to_avif: bool = False,
        is_compare_png_avif_sizes: bool = False,
    ) -> str:
        result_line = markdown_line
        should_process = True

        # Regular expression to match Markdown image with remote URL (http or https)
        pattern = r"^\!\[(.*?)\]\((http.*?)\)$"
        match = re.search(pattern, markdown_line.strip())

        # If the line contains a remote image, don't process it
        if match:
            should_process = False

        # Regular expression to match Markdown image with local path
        local_pattern = r"^\!\[(.*?)\]\((.*?)\)$"
        local_match = re.search(local_pattern, markdown_line.strip())

        if should_process and local_match:
            alt_text = local_match.group(1)
            image_path = local_match.group(2)

            # Check if this is a local image (not a remote URL)
            if not image_path.startswith("http"):
                # Convert path_md to Path object if it's a string
                if isinstance(path_md, str):
                    path_md = Path(path_md)

                # Get the directory containing the Markdown file
                md_dir = path_md.parent if path_md.is_file() else path_md

                # Determine the complete path to the image
                image_filename = Path(image_path) if Path(image_path).is_absolute() else md_dir / image_path

                # Check if the image exists and has a supported extension
                if image_filename.exists():
                    # Get the extension
                    ext = image_filename.suffix.lower()
                    supported_extensions = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg", ".avif"]

                    if ext in supported_extensions:
                        # Determine the new extension based on the current one
                        new_ext = ext
                        if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"]:
                            new_ext = ".avif"
                        elif ext == ".png":
                            if is_compare_png_avif_sizes:
                                # Will be determined by the optimization script
                                pass
                            elif is_convert_png_to_avif:
                                new_ext = ".avif"
                            # Otherwise keep .png
                        # For .svg and .avif, keep the original extension

                        # Create temporary directory for optimization
                        with TemporaryDirectory() as temp_folder:
                            temp_folder_path = Path(temp_folder)
                            temp_image_filename = temp_folder_path / image_filename.name
                            shutil.copy(image_filename, temp_image_filename)

                            # Run the optimization command
                            commands = f'npm run optimize imagesFolder="{temp_folder}"'
                            if is_compare_png_avif_sizes and ext == ".png":
                                commands += " convertPngToAvif=compare"
                            elif is_convert_png_to_avif and ext == ".png":
                                commands += " convertPngToAvif=true"

                            h.dev.run_command(commands)

                            # Path to the optimized images directory
                            optimized_images_dir = temp_folder_path / "temp"

                            # For PNG with size comparison, check results file
                            if is_compare_png_avif_sizes and ext == ".png":
                                results_file = optimized_images_dir / "optimization_results.json"
                                if results_file.exists():
                                    with Path.open(results_file) as f:
                                        results = json.load(f)

                                    stem = image_filename.stem
                                    if stem in results:
                                        new_ext = results[stem]

                            # Path to the optimized image
                            optimized_image = optimized_images_dir / f"{image_filename.stem}{new_ext}"

                            # Check if the optimization was successful
                            if optimized_image.exists():
                                # Determine the target path for the new image
                                if Path(image_path).is_absolute():
                                    # If it was an absolute path, maintain that structure
                                    new_image_path = image_filename.with_suffix(new_ext)
                                    new_image_rel_path = str(new_image_path)
                                else:
                                    # For relative paths, ensure the image goes to the image_folder
                                    img_folder_path = md_dir / image_folder
                                    img_folder_path.mkdir(exist_ok=True)

                                    # Create the new image path
                                    new_image_path = img_folder_path / f"{image_filename.stem}{new_ext}"
                                    new_image_rel_path = f"{image_folder}/{image_filename.stem}{new_ext}"

                                # Remove the original image if we're replacing it
                                if image_filename.exists():
                                    image_filename.unlink()

                                # Copy the optimized image to the target location
                                shutil.copy(optimized_image, new_image_path)

                                # Create the new Markdown line with updated path
                                result_line = f"![{alt_text}]({new_image_rel_path})"

        return result_line
```

</details>

### ⚙️ Method `optimize_images_in_md_compare_sizes`

```python
def optimize_images_in_md_compare_sizes(self, filename: Path | str) -> str
```

Optimize images in a Markdown file with PNG/AVIF size comparison.

This function reads a Markdown file, processes any local images referenced in it,
optimizes them, and for PNG images compares optimized PNG vs AVIF sizes to keep the smaller one.

Args:

- `filename` (`Path | str`): Path to the Markdown file to process.

Returns:

- `str`: A status message indicating whether the file was modified.

<details>
<summary>Code:</summary>

```python
def optimize_images_in_md_compare_sizes(self, filename: Path | str) -> str:
        filename = Path(filename)
        with Path.open(filename, encoding="utf-8") as f:
            document = f.read()

        document_new = self.optimize_images_in_md_content(
            document, filename.parent, is_convert_png_to_avif=False, is_compare_png_avif_sizes=True
        )

        if document != document_new:
            with Path.open(filename, "w", encoding="utf-8") as file:
                file.write(document_new)
            return f"✅ File {filename} applied."
        return "File is not changed."
```

</details>

### ⚙️ Method `optimize_images_in_md_content`

```python
def optimize_images_in_md_content(self, markdown_text: str, path_md: Path | str, image_folder: str = "img") -> str
```

Optimize images referenced in Markdown content by converting them to more efficient formats.

This function processes Markdown content to find local image references, optimizes those images,
and updates the Markdown content to reference the optimized versions. Remote images (URLs)
are left unchanged.

Args:

- `markdown_text` (`str`): The Markdown content to process.
- `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
- `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
- `is_convert_png_to_avif` (`bool`): Flag for converting PNG to AVIF. Defaults to `False`.
- `is_compare_png_avif_sizes` (`bool`): Flag for comparing PNG and AVIF sizes and keeping smaller.
  Defaults to `False`.

Returns:

- `str`: The updated Markdown content with references to optimized images.

Notes:

- Images with extensions .jpg, .jpeg, .webp, .gif, and .mp4 will be converted to .avif
- PNG files behavior depends on flags:
  - If `is_compare_png_avif_sizes` is True: compares optimized PNG vs AVIF and keeps smaller
  - If `is_convert_png_to_avif` is True: converts PNG to AVIF
  - Otherwise: optimizes PNG and keeps as PNG
- SVG files keep their original format but may still be optimized
- The optimization process uses an external npm script
- Code blocks in the Markdown are preserved without changes

<details>
<summary>Code:</summary>

```python
def optimize_images_in_md_content(
        self,
        markdown_text: str,
        path_md: Path | str,
        image_folder: str = "img",
        *,
        is_convert_png_to_avif: bool = False,
        is_compare_png_avif_sizes: bool = False,
    ) -> str:
        yaml_md, content_md = h.md.split_yaml_content(markdown_text)

        new_lines = []
        lines = content_md.split("\n")
        for line_content, is_code_block in h.md.identify_code_blocks(lines):
            if is_code_block:
                new_lines.append(line_content)
                continue

            processed_line = self.optimize_images_content_line(
                line_content,
                path_md,
                image_folder,
                is_convert_png_to_avif=is_convert_png_to_avif,
                is_compare_png_avif_sizes=is_compare_png_avif_sizes,
            )
            new_lines.append(processed_line)
        content_md = "\n".join(new_lines)

        return yaml_md + "\n\n" + content_md
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
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>

## 🏛️ Class `OnOptimizeSelectedImages`

```python
class OnOptimizeSelectedImages(ActionBase)
```

Optimize specific selected images in their corresponding Markdown file.

This action allows users to select specific image files and optimizes only those
images within their corresponding Markdown file. The action:

1. Opens a file dialog to select multiple image files
2. Finds the Markdown file one level up from the selected images
3. Optimizes only the selected images within that Markdown file
4. Updates the Markdown file with references to the optimized images

This is useful when you want to optimize specific images without processing
all images in a folder or when working with images in a specific location.

<details>
<summary>Code:</summary>

```python
class OnOptimizeSelectedImages(ActionBase):

    icon = "🖼️"
    title = "Optimize selected images in MD"
    bold_title = True

    @ActionBase.handle_exceptions("optimizing selected images")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.selected_images = self.get_open_filenames(
            "Select images to optimize",
            self.config["path_articles"],
            "Image files (*.png *.jpg *.jpeg *.gif *.webp *.mp4 *.svg *.avif);;All Files (*)",
        )
        if not self.selected_images:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def find_markdown_file_one_level_up(self, image_dir: Path) -> Path | None:
        """Find a Markdown file one level up from the given directory.

        Args:
        - `image_dir` (`Path`): Directory containing the images.

        Returns:
        - `Path | None`: Path to the Markdown file if found, None otherwise.

        """
        parent_dir = image_dir.parent
        md_files = list(parent_dir.glob("*.md"))

        if md_files:
            # Return the first .md file found
            return md_files[0]
        return None

    @ActionBase.handle_exceptions("optimizing selected images thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if not self.selected_images:
            return

        # Group images by their parent directory to find corresponding MD files
        images_by_dir = {}
        for image_path in self.selected_images:
            parent_dir = image_path.parent
            if parent_dir not in images_by_dir:
                images_by_dir[parent_dir] = []
            images_by_dir[parent_dir].append(image_path)

        processed_files = []
        for parent_dir, images in images_by_dir.items():
            # Look for Markdown file one level up
            md_file = self.find_markdown_file_one_level_up(parent_dir)
            if md_file:
                self.add_line(f"🔵 Found MD file: {md_file}")
                self.add_line(f"🔵 Processing {len(images)} images in {parent_dir}")

                # Optimize only the selected images in this MD file
                result = self.optimize_selected_images_in_md(md_file, images)
                processed_files.append((md_file, result))
            else:
                self.add_line(f"❌ No Markdown file found one level up from {parent_dir}")

        if processed_files:
            self.add_line(f"✅ Processed {len(processed_files)} Markdown file(s)")
        else:
            self.add_line("❌ No Markdown files were processed")

    def optimize_selected_images_content(
        self,
        markdown_text: str,
        path_md: Path | str,
        selected_image_names: set[str],
        image_folder: str = "img",
    ) -> str:
        """Optimize only selected images referenced in Markdown content.

        Args:
        - `markdown_text` (`str`): The Markdown content to process.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `selected_image_names` (`set[str]`): Set of image filenames to optimize.
        - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.

        Returns:
        - `str`: The updated Markdown content with references to optimized images.

        """
        yaml_md, content_md = h.md.split_yaml_content(markdown_text)

        new_lines = []
        lines = content_md.split("\n")
        for line_content, is_code_block in h.md.identify_code_blocks(lines):
            if is_code_block:
                new_lines.append(line_content)
                continue

            processed_line = self.optimize_selected_images_content_line(
                line_content,
                path_md,
                selected_image_names,
                image_folder,
            )
            new_lines.append(processed_line)
        content_md = "\n".join(new_lines)

        return yaml_md + "\n\n" + content_md

    def optimize_selected_images_content_line(
        self,
        markdown_line: str,
        path_md: Path | str,
        selected_image_names: set[str],
        image_folder: str = "img",
    ) -> str:
        """Process a single line of Markdown to optimize only selected image references.

        Args:
        - `markdown_line` (`str`): A single line from the Markdown document.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `selected_image_names` (`set[str]`): Set of image filenames to optimize.
        - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.

        Returns:
        - `str`: The processed Markdown line, with image references updated if needed.

        """
        result_line = markdown_line
        should_process = True

        # Regular expression to match Markdown image with remote URL (http or https)
        pattern = r"^\!\[(.*?)\]\((http.*?)\)$"
        match = re.search(pattern, markdown_line.strip())

        # If the line contains a remote image, don't process it
        if match:
            should_process = False

        # Regular expression to match Markdown image with local path
        local_pattern = r"^\!\[(.*?)\]\((.*?)\)$"
        local_match = re.search(local_pattern, markdown_line.strip())

        if should_process and local_match:
            alt_text = local_match.group(1)
            image_path = local_match.group(2)

            # Check if this is a local image (not a remote URL)
            if not image_path.startswith("http"):
                # Convert path_md to Path object if it's a string
                if isinstance(path_md, str):
                    path_md = Path(path_md)

                # Get the directory containing the Markdown file
                md_dir = path_md.parent if path_md.is_file() else path_md

                # Determine the complete path to the image
                image_filename = Path(image_path) if Path(image_path).is_absolute() else md_dir / image_path

                # Check if the image exists and is in our selected images
                if image_filename.exists() and image_filename.name in selected_image_names:
                    # Get the extension
                    ext = image_filename.suffix.lower()
                    supported_extensions = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg", ".avif"]

                    if ext in supported_extensions:
                        # Determine the new extension based on the current one
                        new_ext = ext
                        if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"]:
                            new_ext = ".avif"
                        elif ext == ".png":
                            # For PNG, compare sizes and keep smaller
                            new_ext = ".png"  # Will be determined by optimization

                        # Create temporary directory for optimization
                        with TemporaryDirectory() as temp_folder:
                            temp_folder_path = Path(temp_folder)
                            temp_image_filename = temp_folder_path / image_filename.name
                            shutil.copy(image_filename, temp_image_filename)

                            # Run the optimization command
                            commands = f'npm run optimize imagesFolder="{temp_folder}"'
                            if ext == ".png":
                                commands += " convertPngToAvif=compare"

                            h.dev.run_command(commands)

                            # Path to the optimized images directory
                            optimized_images_dir = temp_folder_path / "temp"

                            # For PNG with size comparison, check results file
                            if ext == ".png":
                                results_file = optimized_images_dir / "optimization_results.json"
                                if results_file.exists():
                                    with Path.open(results_file) as f:
                                        results = json.load(f)

                                    stem = image_filename.stem
                                    if stem in results:
                                        new_ext = results[stem]

                            # Path to the optimized image
                            optimized_image = optimized_images_dir / f"{image_filename.stem}{new_ext}"

                            # Check if the optimization was successful
                            if optimized_image.exists():
                                # Determine the target path for the new image
                                if Path(image_path).is_absolute():
                                    # If it was an absolute path, maintain that structure
                                    new_image_path = image_filename.with_suffix(new_ext)
                                    new_image_rel_path = str(new_image_path)
                                else:
                                    # For relative paths, ensure the image goes to the image_folder
                                    img_folder_path = md_dir / image_folder
                                    img_folder_path.mkdir(exist_ok=True)

                                    # Create the new image path
                                    new_image_path = img_folder_path / f"{image_filename.stem}{new_ext}"
                                    new_image_rel_path = f"{image_folder}/{image_filename.stem}{new_ext}"

                                # Remove the original image if we're replacing it
                                if image_filename.exists():
                                    image_filename.unlink()

                                # Copy the optimized image to the target location
                                shutil.copy(optimized_image, new_image_path)

                                # Create the new Markdown line with updated path
                                result_line = f"![{alt_text}]({new_image_rel_path})"

        return result_line

    def optimize_selected_images_in_md(self, md_file: Path, selected_images: list[Path]) -> str:
        """Optimize only the selected images in a Markdown file.

        Args:
        - `md_file` (`Path`): Path to the Markdown file.
        - `selected_images` (`list[Path]`): List of selected image paths to optimize.

        Returns:
        - `str`: Status message indicating the result of the operation.

        """
        try:
            with Path.open(md_file, encoding="utf-8") as f:
                document = f.read()

            # Get the names of selected images for filtering
            selected_image_names = {img.name for img in selected_images}

            # Process the document, optimizing only selected images
            document_new = self.optimize_selected_images_content(document, md_file.parent, selected_image_names)

            if document != document_new:
                with Path.open(md_file, "w", encoding="utf-8") as file:
                    file.write(document_new)
                return f"✅ File {md_file} updated with optimized images."
            return f"ℹ️ File {md_file} was not changed (no selected images found)."  # noqa: RUF001

        except Exception as e:
            return f"❌ Error processing {md_file}: {e}"

    @ActionBase.handle_exceptions("optimizing selected images thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.selected_images = self.get_open_filenames(
            "Select images to optimize",
            self.config["path_articles"],
            "Image files (*.png *.jpg *.jpeg *.gif *.webp *.mp4 *.svg *.avif);;All Files (*)",
        )
        if not self.selected_images:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `find_markdown_file_one_level_up`

```python
def find_markdown_file_one_level_up(self, image_dir: Path) -> Path | None
```

Find a Markdown file one level up from the given directory.

Args:

- `image_dir` (`Path`): Directory containing the images.

Returns:

- `Path | None`: Path to the Markdown file if found, None otherwise.

<details>
<summary>Code:</summary>

```python
def find_markdown_file_one_level_up(self, image_dir: Path) -> Path | None:
        parent_dir = image_dir.parent
        md_files = list(parent_dir.glob("*.md"))

        if md_files:
            # Return the first .md file found
            return md_files[0]
        return None
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
        if not self.selected_images:
            return

        # Group images by their parent directory to find corresponding MD files
        images_by_dir = {}
        for image_path in self.selected_images:
            parent_dir = image_path.parent
            if parent_dir not in images_by_dir:
                images_by_dir[parent_dir] = []
            images_by_dir[parent_dir].append(image_path)

        processed_files = []
        for parent_dir, images in images_by_dir.items():
            # Look for Markdown file one level up
            md_file = self.find_markdown_file_one_level_up(parent_dir)
            if md_file:
                self.add_line(f"🔵 Found MD file: {md_file}")
                self.add_line(f"🔵 Processing {len(images)} images in {parent_dir}")

                # Optimize only the selected images in this MD file
                result = self.optimize_selected_images_in_md(md_file, images)
                processed_files.append((md_file, result))
            else:
                self.add_line(f"❌ No Markdown file found one level up from {parent_dir}")

        if processed_files:
            self.add_line(f"✅ Processed {len(processed_files)} Markdown file(s)")
        else:
            self.add_line("❌ No Markdown files were processed")
```

</details>

### ⚙️ Method `optimize_selected_images_content`

```python
def optimize_selected_images_content(self, markdown_text: str, path_md: Path | str, selected_image_names: set[str], image_folder: str = "img") -> str
```

Optimize only selected images referenced in Markdown content.

Args:

- `markdown_text` (`str`): The Markdown content to process.
- `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
- `selected_image_names` (`set[str]`): Set of image filenames to optimize.
- `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.

Returns:

- `str`: The updated Markdown content with references to optimized images.

<details>
<summary>Code:</summary>

```python
def optimize_selected_images_content(
        self,
        markdown_text: str,
        path_md: Path | str,
        selected_image_names: set[str],
        image_folder: str = "img",
    ) -> str:
        yaml_md, content_md = h.md.split_yaml_content(markdown_text)

        new_lines = []
        lines = content_md.split("\n")
        for line_content, is_code_block in h.md.identify_code_blocks(lines):
            if is_code_block:
                new_lines.append(line_content)
                continue

            processed_line = self.optimize_selected_images_content_line(
                line_content,
                path_md,
                selected_image_names,
                image_folder,
            )
            new_lines.append(processed_line)
        content_md = "\n".join(new_lines)

        return yaml_md + "\n\n" + content_md
```

</details>

### ⚙️ Method `optimize_selected_images_content_line`

```python
def optimize_selected_images_content_line(self, markdown_line: str, path_md: Path | str, selected_image_names: set[str], image_folder: str = "img") -> str
```

Process a single line of Markdown to optimize only selected image references.

Args:

- `markdown_line` (`str`): A single line from the Markdown document.
- `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
- `selected_image_names` (`set[str]`): Set of image filenames to optimize.
- `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.

Returns:

- `str`: The processed Markdown line, with image references updated if needed.

<details>
<summary>Code:</summary>

```python
def optimize_selected_images_content_line(
        self,
        markdown_line: str,
        path_md: Path | str,
        selected_image_names: set[str],
        image_folder: str = "img",
    ) -> str:
        result_line = markdown_line
        should_process = True

        # Regular expression to match Markdown image with remote URL (http or https)
        pattern = r"^\!\[(.*?)\]\((http.*?)\)$"
        match = re.search(pattern, markdown_line.strip())

        # If the line contains a remote image, don't process it
        if match:
            should_process = False

        # Regular expression to match Markdown image with local path
        local_pattern = r"^\!\[(.*?)\]\((.*?)\)$"
        local_match = re.search(local_pattern, markdown_line.strip())

        if should_process and local_match:
            alt_text = local_match.group(1)
            image_path = local_match.group(2)

            # Check if this is a local image (not a remote URL)
            if not image_path.startswith("http"):
                # Convert path_md to Path object if it's a string
                if isinstance(path_md, str):
                    path_md = Path(path_md)

                # Get the directory containing the Markdown file
                md_dir = path_md.parent if path_md.is_file() else path_md

                # Determine the complete path to the image
                image_filename = Path(image_path) if Path(image_path).is_absolute() else md_dir / image_path

                # Check if the image exists and is in our selected images
                if image_filename.exists() and image_filename.name in selected_image_names:
                    # Get the extension
                    ext = image_filename.suffix.lower()
                    supported_extensions = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg", ".avif"]

                    if ext in supported_extensions:
                        # Determine the new extension based on the current one
                        new_ext = ext
                        if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"]:
                            new_ext = ".avif"
                        elif ext == ".png":
                            # For PNG, compare sizes and keep smaller
                            new_ext = ".png"  # Will be determined by optimization

                        # Create temporary directory for optimization
                        with TemporaryDirectory() as temp_folder:
                            temp_folder_path = Path(temp_folder)
                            temp_image_filename = temp_folder_path / image_filename.name
                            shutil.copy(image_filename, temp_image_filename)

                            # Run the optimization command
                            commands = f'npm run optimize imagesFolder="{temp_folder}"'
                            if ext == ".png":
                                commands += " convertPngToAvif=compare"

                            h.dev.run_command(commands)

                            # Path to the optimized images directory
                            optimized_images_dir = temp_folder_path / "temp"

                            # For PNG with size comparison, check results file
                            if ext == ".png":
                                results_file = optimized_images_dir / "optimization_results.json"
                                if results_file.exists():
                                    with Path.open(results_file) as f:
                                        results = json.load(f)

                                    stem = image_filename.stem
                                    if stem in results:
                                        new_ext = results[stem]

                            # Path to the optimized image
                            optimized_image = optimized_images_dir / f"{image_filename.stem}{new_ext}"

                            # Check if the optimization was successful
                            if optimized_image.exists():
                                # Determine the target path for the new image
                                if Path(image_path).is_absolute():
                                    # If it was an absolute path, maintain that structure
                                    new_image_path = image_filename.with_suffix(new_ext)
                                    new_image_rel_path = str(new_image_path)
                                else:
                                    # For relative paths, ensure the image goes to the image_folder
                                    img_folder_path = md_dir / image_folder
                                    img_folder_path.mkdir(exist_ok=True)

                                    # Create the new image path
                                    new_image_path = img_folder_path / f"{image_filename.stem}{new_ext}"
                                    new_image_rel_path = f"{image_folder}/{image_filename.stem}{new_ext}"

                                # Remove the original image if we're replacing it
                                if image_filename.exists():
                                    image_filename.unlink()

                                # Copy the optimized image to the target location
                                shutil.copy(optimized_image, new_image_path)

                                # Create the new Markdown line with updated path
                                result_line = f"![{alt_text}]({new_image_rel_path})"

        return result_line
```

</details>

### ⚙️ Method `optimize_selected_images_in_md`

```python
def optimize_selected_images_in_md(self, md_file: Path, selected_images: list[Path]) -> str
```

Optimize only the selected images in a Markdown file.

Args:

- `md_file` (`Path`): Path to the Markdown file.
- `selected_images` (`list[Path]`): List of selected image paths to optimize.

Returns:

- `str`: Status message indicating the result of the operation.

<details>
<summary>Code:</summary>

```python
def optimize_selected_images_in_md(self, md_file: Path, selected_images: list[Path]) -> str:
        try:
            with Path.open(md_file, encoding="utf-8") as f:
                document = f.read()

            # Get the names of selected images for filtering
            selected_image_names = {img.name for img in selected_images}

            # Process the document, optimizing only selected images
            document_new = self.optimize_selected_images_content(document, md_file.parent, selected_image_names)

            if document != document_new:
                with Path.open(md_file, "w", encoding="utf-8") as file:
                    file.write(document_new)
                return f"✅ File {md_file} updated with optimized images."
            return f"ℹ️ File {md_file} was not changed (no selected images found)."  # noqa: RUF001

        except Exception as e:
            return f"❌ Error processing {md_file}: {e}"
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

## 🏛️ Class `OnQuotesFormatAsMarkdownContent`

```python
class OnQuotesFormatAsMarkdownContent(ActionBase)
```

Format plain text quotes into properly structured Markdown.

<details>
<summary>Code:</summary>

```python
class OnQuotesFormatAsMarkdownContent(ActionBase):

    icon = "❞"
    title = "Quotes. Format quotes as Markdown content"

    @ActionBase.handle_exceptions("formatting quotes as markdown")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        default_text = """They can get a big bang out of buying a blanket.

The Catcher in the Rye
J.D. Salinger


I just mean that I used to think about old Spencer quite a lot

The Catcher in the Rye
J.D. Salinger"""
        content = self.get_text_textarea("Quotes", "Input quotes", default_text)
        if not content:
            return

        result = h.md.format_quotes_as_markdown_content(content)

        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        default_text = """They can get a big bang out of buying a blanket.

The Catcher in the Rye
J.D. Salinger


I just mean that I used to think about old Spencer quite a lot

The Catcher in the Rye
J.D. Salinger"""
        content = self.get_text_textarea("Quotes", "Input quotes", default_text)
        if not content:
            return

        result = h.md.format_quotes_as_markdown_content(content)

        self.add_line(result)
        self.show_result()
```

</details>

## 🏛️ Class `OnQuotesGenerateAuthorAndBook`

```python
class OnQuotesGenerateAuthorAndBook(ActionBase)
```

Process quote files to add author and book information.

This action traverses a folder of quote Markdown files and processes each file
to generate or update author and book information based on the content structure.
Useful for maintaining a consistent format in a collection of literary quotes.

<details>
<summary>Code:</summary>

````python
class OnQuotesGenerateAuthorAndBook(ActionBase):

    icon = "❞"
    title = "Quotes. Add author and title"

    @ActionBase.handle_exceptions("generating author and book information")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.show_instructions("""Given a file like `C:/test/Name_Surname/Title_of_book.md` with content:

```markdown
# Title of book

Line 1.

Line 2.

---

Line 3.

Line 4.

-- Modified title of book

````

After processing:

```markdown
# Title of book

> Line 1.
>
> Line 2.
>
> -- _Name Surname, Title of book_

---

> Line 3.
>
> Line 4.
>
> -- _Name Surname, Modified title of book_
```

""")
self.folder_path = self.get_existing_directory("Select a folder with quotes", self.config["path_quotes"])
if not self.folder_path:
return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("generating author book thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        result = h.file.apply_func(self.folder_path, ".md", h.md.generate_author_book)
        self.add_line(result)

    @ActionBase.handle_exceptions("generating author book thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()

````

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
````

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

````python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.show_instructions("""Given a file like `C:/test/Name_Surname/Title_of_book.md` with content:

```markdown
# Title of book

Line 1.

Line 2.

---

Line 3.

Line 4.

-- Modified title of book

````

After processing:

```markdown
# Title of book

> Line 1.
>
> Line 2.
>
> -- _Name Surname, Title of book_

---

> Line 3.
>
> Line 4.
>
> -- _Name Surname, Modified title of book_
```

""")
self.folder_path = self.get_existing_directory("Select a folder with quotes", self.config["path_quotes"])
if not self.folder_path:
return

        self.start_thread(self.in_thread, self.thread_after, self.title)

````

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
````

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        if self.folder_path is None:
            return
        result = h.file.apply_func(self.folder_path, ".md", h.md.generate_author_book)
        self.add_line(result)
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
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>

## 🏛️ Class `OnSortSections`

```python
class OnSortSections(ActionBase)
```

Organize and enhance a single Markdown file by sorting sections and generating image captions.

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

<details>
<summary>Code:</summary>

```python
class OnSortSections(ActionBase):

    icon = "📶"
    title = "Sort sections in one MD"

    @ActionBase.handle_exceptions("sorting sections in markdown file")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.filename = self.get_open_filename(
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
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.filename = self.get_open_filename(
            "Open Markdown file",
            self.config["path_notes"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
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
        if self.filename is None:
            return
        self.add_line(h.md.sort_sections(self.filename))
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
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()
```

</details>
