---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `markdown.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAppendYamlTag`](#%EF%B8%8F-class-onappendyamltag)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
- [🏛️ Class `OnBeautifyMdFolder`](#%EF%B8%8F-class-onbeautifymdfolder)
  - [⚙️ Method `beautify_markdown_common`](#%EF%B8%8F-method-beautify_markdown_common)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-1)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-1)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-1)
- [🏛️ Class `OnBeautifyMdFolderAndRegenerateGMd`](#%EF%B8%8F-class-onbeautifymdfolderandregenerategmd)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-2)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-2)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-2)
- [🏛️ Class `OnCheckMdFolder`](#%EF%B8%8F-class-oncheckmdfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-3)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-3)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-3)
- [🏛️ Class `OnDecreaseHeadingLevelContent`](#%EF%B8%8F-class-ondecreaseheadinglevelcontent)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-4)
- [🏛️ Class `OnDownloadAndReplaceImagesFolder`](#%EF%B8%8F-class-ondownloadandreplaceimagesfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-5)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-4)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-4)
- [🏛️ Class `OnFixMDWithQuotes`](#%EF%B8%8F-class-onfixmdwithquotes)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-6)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-5)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-5)
- [🏛️ Class `OnGenerateShortNoteTocWithLinks`](#%EF%B8%8F-class-ongenerateshortnotetocwithlinks)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-7)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-6)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-6)
- [🏛️ Class `OnGenerateStaticSite`](#%EF%B8%8F-class-ongeneratestaticsite)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-8)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-7)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-7)
- [🏛️ Class `OnGetListMoviesBooks`](#%EF%B8%8F-class-ongetlistmoviesbooks)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-9)
- [🏛️ Class `OnGetSetVariablesFromYaml`](#%EF%B8%8F-class-ongetsetvariablesfromyaml)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-10)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-8)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-8)
- [🏛️ Class `OnIncreaseHeadingLevelContent`](#%EF%B8%8F-class-onincreaseheadinglevelcontent)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-11)
- [🏛️ Class `OnNewMarkdown`](#%EF%B8%8F-class-onnewmarkdown)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-12)
  - [⚙️ Method `_execute_from_template`](#%EF%B8%8F-method-_execute_from_template)
  - [⚙️ Method `_execute_new_article`](#%EF%B8%8F-method-_execute_new_article)
  - [⚙️ Method `_execute_new_diary`](#%EF%B8%8F-method-_execute_new_diary)
  - [⚙️ Method `_execute_new_diary_cases`](#%EF%B8%8F-method-_execute_new_diary_cases)
  - [⚙️ Method `_execute_new_diary_dream`](#%EF%B8%8F-method-_execute_new_diary_dream)
  - [⚙️ Method `_execute_new_note`](#%EF%B8%8F-method-_execute_new_note)
  - [⚙️ Method `_execute_new_note_with_images`](#%EF%B8%8F-method-_execute_new_note_with_images)
  - [⚙️ Method `_execute_new_quotes`](#%EF%B8%8F-method-_execute_new_quotes)
  - [⚙️ Method `_execute_new_quotes_format_with_author_and_book`](#%EF%B8%8F-method-_execute_new_quotes_format_with_author_and_book)
  - [⚙️ Method `_extract_authors_and_books_from_quotes_folder`](#%EF%B8%8F-method-_extract_authors_and_books_from_quotes_folder)
  - [⚙️ Method `_extract_authors_and_english_names_from_books_folder`](#%EF%B8%8F-method-_extract_authors_and_english_names_from_books_folder)
  - [⚙️ Method `_get_authors_for_book_template`](#%EF%B8%8F-method-_get_authors_for_book_template)
  - [⚙️ Method `_optimize_single_image_for_template`](#%EF%B8%8F-method-_optimize_single_image_for_template)
  - [⚙️ Method `_replace_author_field_with_combobox`](#%EF%B8%8F-method-_replace_author_field_with_combobox)
  - [⚙️ Method `_save_quotes_to_file`](#%EF%B8%8F-method-_save_quotes_to_file)
- [🏛️ Class `OnOptimizeImagesFolder`](#%EF%B8%8F-class-onoptimizeimagesfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-13)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-9)
  - [⚙️ Method `optimize_images_content_line`](#%EF%B8%8F-method-optimize_images_content_line)
  - [⚙️ Method `optimize_images_in_md_compare_sizes`](#%EF%B8%8F-method-optimize_images_in_md_compare_sizes)
  - [⚙️ Method `optimize_images_in_md_content`](#%EF%B8%8F-method-optimize_images_in_md_content)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-9)
- [🏛️ Class `OnOptimizeSelectedImages`](#%EF%B8%8F-class-onoptimizeselectedimages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-14)
  - [⚙️ Method `find_markdown_file_one_level_up`](#%EF%B8%8F-method-find_markdown_file_one_level_up)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-10)
  - [⚙️ Method `optimize_selected_images_content`](#%EF%B8%8F-method-optimize_selected_images_content)
  - [⚙️ Method `optimize_selected_images_content_line`](#%EF%B8%8F-method-optimize_selected_images_content_line)
  - [⚙️ Method `optimize_selected_images_in_md`](#%EF%B8%8F-method-optimize_selected_images_in_md)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-10)
- [🏛️ Class `OnSortSections`](#%EF%B8%8F-class-onsortsections)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-15)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-11)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-11)

</details>

## 🏛️ Class `OnAppendYamlTag`

```python
class OnAppendYamlTag(ActionBase)
```

Append a YAML tag to Markdown files in a folder.

This action processes all Markdown files in a selected folder to add or update
a YAML tag in the front matter. The user specifies the tag key and value,
and the action applies this tag to all Markdown files in the folder.

If a file doesn't have YAML front matter, it will be added. If the YAML tag
already exists, it will be updated with the new value.

<details>
<summary>Code:</summary>

```python
class OnAppendYamlTag(ActionBase):

    icon = "🏷️"
    title = "Append YAML tag in …"

    @ActionBase.handle_exceptions("appending YAML tag")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        # Get YAML tag key
        yaml_tag_key = self.get_text_input("YAML Tag Key", "Enter the YAML tag key:", "author")
        if not yaml_tag_key:
            return

        # Get YAML tag value
        yaml_tag_value = self.get_text_input("YAML Tag Value", "Enter the YAML tag value:", "")
        if yaml_tag_value is None:
            return

        self.yaml_tag_tuple = (yaml_tag_key, yaml_tag_value)
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("appending YAML tag thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        if self.folder_path is None:
            return
        self.add_line(
            h.file.apply_func(
                str(self.folder_path),
                ".md",
                lambda filename: h.md.append_yaml_tag(filename, self.yaml_tag_tuple),
            )
        )

    @ActionBase.handle_exceptions("appending YAML tag thread completion")
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
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        # Get YAML tag key
        yaml_tag_key = self.get_text_input("YAML Tag Key", "Enter the YAML tag key:", "author")
        if not yaml_tag_key:
            return

        # Get YAML tag value
        yaml_tag_value = self.get_text_input("YAML Tag Value", "Enter the YAML tag value:", "")
        if yaml_tag_value is None:
            return

        self.yaml_tag_tuple = (yaml_tag_key, yaml_tag_value)
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
        self.add_line(
            h.file.apply_func(
                str(self.folder_path),
                ".md",
                lambda filename: h.md.append_yaml_tag(filename, self.yaml_tag_tuple),
            )
        )
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
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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
    title = "Check MD in …"

    @ActionBase.handle_exceptions("checking markdown folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        # Get available rules from MarkdownChecker
        checker = h.md_check.MarkdownChecker()
        rules_dict = checker.RULES

        # Convert rules dict to list of rule descriptions for display
        rule_choices = [f"{rule_id}: {description}" for rule_id, description in rules_dict.items()]

        # Show dialog to select rules (all selected by default)
        selected_rules = self.get_checkbox_selection(
            "Select Rules for Markdown Check",
            "Choose which rules to check:",
            rule_choices,
            default_selected=rule_choices,  # All rules selected by default
        )

        if not selected_rules:
            return

        # Extract rule IDs from selected descriptions
        self.selected_rule_ids = set()
        for selected_rule in selected_rules:
            # Extract rule ID (e.g., "H001" from "H001: Description")
            rule_id = selected_rule.split(":")[0].strip()
            self.selected_rule_ids.add(rule_id)

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("markdown folder checking thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        checker = h.md_check.MarkdownChecker()
        if self.folder_path is None:
            return

        # Use selected rules for checking directory
        errors_dict = checker.check_directory(self.folder_path, select=self.selected_rule_ids)

        # Flatten the errors dictionary into a list
        all_errors = []
        for file_path, file_errors in errors_dict.items():
            for error in file_errors:
                all_errors.extend([f"{file_path}: {error}" for error in file_errors])

        if all_errors:
            self.add_line("\n".join(all_errors))
            self.add_line(f"🔢 Count errors = {len(all_errors)}")
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
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        # Get available rules from MarkdownChecker
        checker = h.md_check.MarkdownChecker()
        rules_dict = checker.RULES

        # Convert rules dict to list of rule descriptions for display
        rule_choices = [f"{rule_id}: {description}" for rule_id, description in rules_dict.items()]

        # Show dialog to select rules (all selected by default)
        selected_rules = self.get_checkbox_selection(
            "Select Rules for Markdown Check",
            "Choose which rules to check:",
            rule_choices,
            default_selected=rule_choices,  # All rules selected by default
        )

        if not selected_rules:
            return

        # Extract rule IDs from selected descriptions
        self.selected_rule_ids = set()
        for selected_rule in selected_rules:
            # Extract rule ID (e.g., "H001" from "H001: Description")
            rule_id = selected_rule.split(":")[0].strip()
            self.selected_rule_ids.add(rule_id)

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

        # Use selected rules for checking directory
        errors_dict = checker.check_directory(self.folder_path, select=self.selected_rule_ids)

        # Flatten the errors dictionary into a list
        all_errors = []
        for file_path, file_errors in errors_dict.items():
            for error in file_errors:
                all_errors.extend([f"{file_path}: {error}" for error in file_errors])

        if all_errors:
            self.add_line("\n".join(all_errors))
            self.add_line(f"🔢 Count errors = {len(all_errors)}")
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
            "Select folder with Markdown files", self.config["path_articles"]
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
            "Select folder with Markdown files", self.config["path_articles"]
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

## 🏛️ Class `OnFixMDWithQuotes`

```python
class OnFixMDWithQuotes(ActionBase)
```

Add author and title information to quote files in a folder.

This action processes quote files in a folder to add author and book information
based on the folder structure. Given a file structure like:

`C:/quotes/Name-Surname/Title-of-book.md`

The action will:

1. Extract author name from the parent folder
2. Extract book title from the filename
3. Format quotes with proper author attribution

Example transformation:

- Before: Plain text quotes separated by `---`
- After: Block quotes with attribution `-- _Name Surname, Title of book_`

<details>
<summary>Code:</summary>

````python
class OnFixMDWithQuotes(ActionBase):

    icon = "❞"
    title = "Fix MD with quotes"

    @ActionBase.handle_exceptions("fixing markdown with quotes")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.show_instructions("""Given a file like `C:/test/Name-Surname/Title-of-book.md` with content:

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
self.folder_path = self.get_existing_directory("Select folder with quotes", self.config["path_quotes"])
if not self.folder_path:
return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("fixing markdown with quotes thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        result = h.file.apply_func(self.folder_path, ".md", h.md.generate_author_book)
        self.add_line(result)

    @ActionBase.handle_exceptions("fixing markdown with quotes thread completion")
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
        self.show_instructions("""Given a file like `C:/test/Name-Surname/Title-of-book.md` with content:

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
self.folder_path = self.get_existing_directory("Select folder with quotes", self.config["path_quotes"])
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

## 🏛️ Class `OnGenerateStaticSite`

```python
class OnGenerateStaticSite(ActionBase)
```

Generate a static HTML site from Markdown files using harrix-pyssg.

This action prompts the user to select:

1. A folder containing Markdown files (md_folder)
2. An output folder for generated HTML files (html_folder)

It then uses the StaticSiteGenerator class from harrix-pyssg to convert
all Markdown files in the selected folder (and subfolders) into HTML files,
preserving the folder structure and copying associated images and assets.

<details>
<summary>Code:</summary>

```python
class OnGenerateStaticSite(ActionBase):

    icon = "🌐"
    title = "Generate static site"

    @ActionBase.handle_exceptions("generating static site")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        # Get sites from config
        paths_sites = self.config.get("paths_sites", [])

        # Build list of choices with site descriptions
        choices = []
        site_map = {}

        for idx, site in enumerate(paths_sites):
            if isinstance(site, dict) and "input" in site and "output" in site:
                display_text = f"🌐 {site['input']} → {site['output']}"
                choices.append(display_text)
                site_map[display_text] = ("site", idx)

        # Add manual selection option
        manual_choice_text = "📁 Select folders manually..."
        choices.append(manual_choice_text)
        site_map[manual_choice_text] = ("manual", None)

        # Show selection dialog (always show, even if only manual option is available)
        selected_choice = self.get_choice_from_list(
            "Select site configuration",
            "Choose a site from the list or select folders manually:",
            choices,
        )

        if not selected_choice:
            return

        choice_type, choice_data = site_map[selected_choice]

        if choice_type == "site":
            # Use configured site
            site = paths_sites[choice_data]
            self.md_folder = Path(site["input"])
            self.html_folder = Path(site["output"])
        elif choice_type == "manual":
            # Request folders manually
            self.md_folder = self.get_existing_directory(
                "Select folder with Markdown files",
                self.config.get("path_articles", self.config.get("path_notes", ".")),
            )
            if not self.md_folder:
                return

            self.html_folder = self.get_existing_directory(
                "Select output folder for HTML files",
                str(self.md_folder.parent / "build_site"),
            )
            if not self.html_folder:
                return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("generating static site thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.md_folder is None or self.html_folder is None:
            return None

        self.add_line("🔵 Starting site generation")
        self.add_line(f"📁 Markdown folder: {self.md_folder}")
        self.add_line(f"📁 HTML output folder: {self.html_folder}")
        self.add_line("")

        try:
            sg = hsg.StaticSiteGenerator(self.md_folder)
            sg.generate_site(self.html_folder)
            self.add_line("✅ Site generation completed successfully")
            self.add_line(f"📊 Generated {len(sg.articles)} articles")
        except Exception as e:
            self.add_line(f"❌ Error during site generation: {e}")
            raise

        return None

    @ActionBase.handle_exceptions("generating static site thread completion")
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
        # Get sites from config
        paths_sites = self.config.get("paths_sites", [])

        # Build list of choices with site descriptions
        choices = []
        site_map = {}

        for idx, site in enumerate(paths_sites):
            if isinstance(site, dict) and "input" in site and "output" in site:
                display_text = f"🌐 {site['input']} → {site['output']}"
                choices.append(display_text)
                site_map[display_text] = ("site", idx)

        # Add manual selection option
        manual_choice_text = "📁 Select folders manually..."
        choices.append(manual_choice_text)
        site_map[manual_choice_text] = ("manual", None)

        # Show selection dialog (always show, even if only manual option is available)
        selected_choice = self.get_choice_from_list(
            "Select site configuration",
            "Choose a site from the list or select folders manually:",
            choices,
        )

        if not selected_choice:
            return

        choice_type, choice_data = site_map[selected_choice]

        if choice_type == "site":
            # Use configured site
            site = paths_sites[choice_data]
            self.md_folder = Path(site["input"])
            self.html_folder = Path(site["output"])
        elif choice_type == "manual":
            # Request folders manually
            self.md_folder = self.get_existing_directory(
                "Select folder with Markdown files",
                self.config.get("path_articles", self.config.get("path_notes", ".")),
            )
            if not self.md_folder:
                return

            self.html_folder = self.get_existing_directory(
                "Select output folder for HTML files",
                str(self.md_folder.parent / "build_site"),
            )
            if not self.html_folder:
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
        if self.md_folder is None or self.html_folder is None:
            return None

        self.add_line("🔵 Starting site generation")
        self.add_line(f"📁 Markdown folder: {self.md_folder}")
        self.add_line(f"📁 HTML output folder: {self.html_folder}")
        self.add_line("")

        try:
            sg = hsg.StaticSiteGenerator(self.md_folder)
            sg.generate_site(self.html_folder)
            self.add_line("✅ Site generation completed successfully")
            self.add_line(f"📊 Generated {len(sg.articles)} articles")
        except Exception as e:
            self.add_line(f"❌ Error during site generation: {e}")
            raise

        return None
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

## 🏛️ Class `OnGetSetVariablesFromYaml`

```python
class OnGetSetVariablesFromYaml(ActionBase)
```

Get a sorted list of all variables from YAML frontmatter in Markdown files.

This action recursively searches through all Markdown files in a selected folder
and extracts all unique variable names from their YAML frontmatter. It:

1. Recursively searches all subfolders for `.md` files
2. Extracts YAML frontmatter from each file
3. Collects all unique variable names (keys) from the YAML
4. Returns a sorted list of all variables found

Files and folders matching common ignore patterns (like `.git`, `__pycache__`,
`node_modules`, etc.) and hidden files/folders are automatically ignored.

Example output: `['categories', 'date', 'tags']`

<details>
<summary>Code:</summary>

```python
class OnGetSetVariablesFromYaml(ActionBase):

    icon = "📋"
    title = "Get set variables from YAML in …"

    @ActionBase.handle_exceptions("getting set variables from YAML")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("getting set variables from YAML thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Processing folder: {self.folder_path}")
        variables = h.md.get_set_variables_from_yaml(self.folder_path)

        if variables:
            self.add_line(f"\n✅ Found {len(variables)} unique variable(s):\n")
            for variable in variables:
                self.add_line(f"  - {variable}")
        else:
            self.add_line("ℹ️ No variables found in YAML frontmatter.")  # noqa: RUF001

    @ActionBase.handle_exceptions("getting set variables from YAML thread completion")
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
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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

        self.add_line(f"🔵 Processing folder: {self.folder_path}")
        variables = h.md.get_set_variables_from_yaml(self.folder_path)

        if variables:
            self.add_line(f"\n✅ Found {len(variables)} unique variable(s):\n")
            for variable in variables:
                self.add_line(f"  - {variable}")
        else:
            self.add_line("ℹ️ No variables found in YAML frontmatter.")  # noqa: RUF001
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

## 🏛️ Class `OnNewMarkdown`

```python
class OnNewMarkdown(ActionBase)
```

Create new Markdown files using various templates and formats.

This action provides a unified interface for creating different types of Markdown files.
It shows a dialog with all available new Markdown commands, allowing the user to
select which type of Markdown file they want to create.

<details>
<summary>Code:</summary>

```python
class OnNewMarkdown(ActionBase):

    icon = "📝"
    title = "New Markdown"
    bold_title = True

    _COMMANDS: ClassVar[list[tuple[str, str, str]]] = [
        ("✍️", "New article", "_execute_new_article"),
        ("📖", "New diary note", "_execute_new_diary"),
        ("💤", "New dream note", "_execute_new_diary_dream"),
        ("📋", "New cases note", "_execute_new_diary_cases"),
        ("📓", "New note", "_execute_new_note"),
        ("📓", "New note with images", "_execute_new_note_with_images"),
        ("❞", "New quotes", "_execute_new_quotes"),
    ]

    @ActionBase.handle_exceptions("creating new markdown")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        templates = self.config.get("markdown_templates", {})

        choices = []
        action_map = {}

        for template_name in templates:
            icon = template_name[0] if template_name else "📝"
            choices.append((icon, template_name))
            action_map[template_name] = ("template", template_name)

        for icon, title, method_name in self._COMMANDS:
            choices.append((icon, title))
            action_map[title] = ("method", method_name)

        selected_choice = self.get_choice_from_icons(
            "New Markdown",
            "Choose a command to create new Markdown content:",
            choices,
        )

        if not selected_choice:
            return

        selected_item = action_map.get(selected_choice)
        if not selected_item:
            self.add_line(f"❌ Unknown command selected: {selected_choice}")
            self.show_result()
            return

        item_type, item_value = selected_item

        if item_type == "template":
            self._execute_from_template(template_name=item_value)
        elif item_type == "method":
            method = getattr(self, item_value)
            method()

    @ActionBase.handle_exceptions("adding markdown from template")
    def _execute_from_template(self, *, template_name: str | None = None) -> None:
        """Add Markdown content using template-based forms.

        Reads a template file with field placeholders, shows a form dialog,
        fills the template with user values, and inserts into target file or returns text.
        """
        templates = self.config.get("markdown_templates", {})

        if not templates:
            self.add_line("❌ No markdown templates configured in config.json")
            self.show_result()
            return

        selected_template = template_name
        if not selected_template:
            template_names = list(templates.keys())
            selected_template = self.get_choice_from_list(
                "Select Template",
                "Choose a template to use:",
                template_names,
            )
            if not selected_template:
                return

        template_config = templates[selected_template]
        template_file = template_config.get("template_file")

        if not template_file:
            self.add_line(f"❌ Template file not specified for '{selected_template}'")
            self.show_result()
            return

        template_path = Path(template_file)
        if not template_path.exists():
            self.add_line(f"❌ Template file not found: {template_file}")
            self.show_result()
            return

        with Path.open(template_path, encoding="utf-8") as f:
            template_content = f.read().strip()

        fields, _ = TemplateParser.parse_template(template_content)

        if not fields:
            self.add_line(f"❌ No fields found in template: {template_file}")
            self.show_result()
            return

        author_to_english: dict[str, str] = {}
        if selected_template == "📖 Book":
            authors_list, author_to_english = self._get_authors_for_book_template(template_config)
            fields = self._replace_author_field_with_combobox(fields, authors_list)

        dialog_links_config = template_config.get("dialog_links", [])
        dialog_links: list[tuple[str, str]] = []
        for item in dialog_links_config:
            if isinstance(item, dict):
                url = item.get("url", "").strip()
                if not url:
                    continue
                label = item.get("label", url).strip() or url
                dialog_links.append((label, url))
            elif isinstance(item, str):
                cleaned = item.strip()
                if cleaned:
                    dialog_links.append((cleaned, cleaned))

        path_target = template_config.get("path_target")
        path_target_path = Path(path_target.rstrip("/")) if path_target else None
        image_save_dir = path_target_path.parent if (path_target_path and path_target_path.suffix == ".md") else None

        dialog = TemplateDialog(
            fields=fields,
            title=f"Add {selected_template.capitalize()}",
            links=dialog_links,
            image_save_dir=image_save_dir,
        )

        if selected_template == "📖 Book" and author_to_english:
            author_widget = dialog.widgets.get("Author")
            author_english_widget = dialog.widgets.get("Author's name in English")
            if isinstance(author_widget, QComboBox) and isinstance(author_english_widget, QLineEdit):

                def _update_author_english(author_text: str) -> None:
                    english_name = author_to_english.get(author_text, "")
                    author_english_widget.setText(english_name)

                author_widget.currentTextChanged.connect(_update_author_english)
                if author_widget.currentText():
                    _update_author_english(author_widget.currentText())

        if dialog.exec() != dialog.DialogCode.Accepted:
            self.add_line("❌ Dialog was canceled.")
            self.show_result()
            return

        field_values = dialog.get_field_values()
        if not field_values:
            self.add_line("❌ No field values collected.")
            self.show_result()
            return

        result_markdown = TemplateParser.fill_template(template_content, field_values)

        if template_config.get("image_optimize") and image_save_dir:
            image_field_name = next((f.name for f in fields if f.field_type == "image"), None)
            image_path_value = field_values.get(image_field_name, "").strip() if image_field_name else ""
            if image_path_value:
                max_size = template_config.get("image_max_size")
                if max_size is not None:
                    try:
                        max_size = int(max_size)
                    except (ValueError, TypeError):
                        max_size = None
                try:
                    new_image_path = self._optimize_single_image_for_template(
                        image_path_value, image_save_dir, max_size
                    )
                    if new_image_path != image_path_value:
                        result_markdown = result_markdown.replace(image_path_value, new_image_path)
                except Exception as e:  # noqa: BLE001
                    self.add_line(f"⚠️ Image optimization skipped: {e}")

        path_target = template_config.get("path_target")
        insert_position = template_config.get("insert_position", "end")

        if path_target:
            current_year = datetime.now(UTC).astimezone().strftime("%Y")
            path_target_clean = path_target.rstrip("/")
            path_target_path = Path(path_target_clean)
            single_file = path_target_path.suffix == ".md"
            target_path = path_target_path if single_file else path_target_path / f"{current_year}.md"

            file_existed = target_path.exists()
            if file_existed:
                with Path.open(target_path, encoding="utf-8") as f:
                    existing_content = f.read()
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                beginning_content = self.config.get("beginning_of_md", "")
                if single_file:
                    if beginning_content:
                        existing_content = (
                            beginning_content
                            + "\n\n# Events\n\nТеатры, концерты и др.\n\n## "
                            + current_year
                            + "\n\n"
                            + result_markdown
                            + "\n"
                        )
                    else:
                        existing_content = (
                            "# Events\n\nТеатры, концерты и др.\n\n## " + current_year + "\n\n" + result_markdown + "\n"
                        )
                elif beginning_content:
                    existing_content = beginning_content + "\n\n# " + current_year + "\n"
                else:
                    existing_content = "# " + current_year + "\n"

            if not file_existed and single_file:
                new_content = existing_content
            elif insert_position == "end":
                new_content = existing_content.rstrip() + "\n\n" + result_markdown + "\n"
            elif insert_position == "start" and single_file:
                yaml_md, content_md = h.md.split_yaml_content(existing_content)
                year_heading_pattern = re.compile(r"^## " + re.escape(current_year) + r"\s*$", re.MULTILINE)
                year_match = year_heading_pattern.search(content_md)
                if year_match:
                    year_pos = year_match.end()
                    updated_content_md = (
                        content_md[:year_pos] + "\n\n" + result_markdown + "\n\n" + content_md[year_pos:].lstrip()
                    )
                    new_content = yaml_md + "\n\n" + updated_content_md if yaml_md else updated_content_md
                else:
                    toc_match = re.search(r"<details>[\s\S]*?<\/details>", content_md)
                    if toc_match:
                        insert_pos = toc_match.end()
                        updated_content_md = (
                            content_md[:insert_pos]
                            + "\n\n## "
                            + current_year
                            + "\n\n"
                            + result_markdown
                            + "\n\n"
                            + content_md[insert_pos:].lstrip()
                        )
                    else:
                        updated_content_md = (
                            "## " + current_year + "\n\n" + result_markdown + "\n\n" + content_md.lstrip()
                        )
                    new_content = yaml_md + "\n\n" + updated_content_md if yaml_md else updated_content_md
            elif insert_position == "start":
                yaml_md, content_md = h.md.split_yaml_content(existing_content)
                year_match = re.search(r"^#+ \d{4}", content_md, re.MULTILINE)

                if year_match:
                    toc_match = re.search(r"<details>[\s\S]*?<\/details>", content_md)
                    if toc_match:
                        toc_end_pos = toc_match.end()
                        updated_content_md = (
                            content_md[:toc_end_pos]
                            + "\n\n"
                            + result_markdown
                            + "\n\n"
                            + content_md[toc_end_pos:].lstrip()
                        )
                    else:
                        year_pos = year_match.end()
                        updated_content_md = (
                            content_md[:year_pos] + "\n\n" + result_markdown + "\n\n" + content_md[year_pos:].lstrip()
                        )
                    new_content = yaml_md + "\n\n" + updated_content_md if yaml_md else updated_content_md
                elif yaml_md:
                    new_content = yaml_md + "\n\n" + result_markdown + "\n\n" + content_md
                else:
                    new_content = result_markdown + "\n\n" + existing_content
            else:
                new_content = existing_content.rstrip() + "\n\n" + result_markdown + "\n"

            with Path.open(target_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            h.dev.run_command(
                f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{target_path}"'
            )
            self.add_line(f"✅ Added markdown to {target_path}")
            self.add_line("\nGenerated markdown:")
            self.add_line(result_markdown)
        else:
            self.add_line("Generated markdown:")
            self.add_line(result_markdown)

        self.show_result()

    @ActionBase.handle_exceptions("creating new article")
    def _execute_new_article(self) -> None:
        """Create new article with predefined template."""
        article_name = self.get_text_input(
            "Article title", "Enter the name of the article (English, without spaces):", "name-of-article"
        )
        if not article_name:
            return

        article_name = article_name.replace(" ", "-")

        now_local = datetime.now(UTC).astimezone()
        text = self.config["beginning_of_article"].replace(
            "[YEAR]",
            now_local.strftime("%Y"),
        )
        text = text.replace("[NAME]", article_name)
        text = text.replace(
            "[DATE]",
            now_local.strftime("%Y-%m-%d"),
        )
        text += f"\n# {article_name.capitalize().replace('-', ' ')}\n\n\n"

        result, filename = h.md.add_note(Path(self.config["path_articles"]), article_name, text, is_with_images=True)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_articles"]}" "{filename}"')
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new diary entry")
    def _execute_new_diary(self) -> None:
        """Create new diary entry for current date."""
        result, filename = h.md.add_diary_new_dairy_in_year(self.config["path_diary"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new cases entry")
    def _execute_new_diary_cases(self) -> None:
        """Create new cases entry for current month."""
        path_cases = self.config.get("path_cases")
        if not path_cases:
            self.add_line("❌ path_cases is not configured in config.json.")
            self.show_result()
            return
        result, filename = h.md.add_diary_new_cases_in_year(path_cases, self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new dream entry")
    def _execute_new_diary_dream(self) -> None:
        """Create new dream journal entry for current date."""
        result, filename = h.md.add_diary_new_dream_in_year(self.config["path_dream"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)

    @ActionBase.handle_exceptions("creating new note")
    def _execute_new_note(self, *, is_with_images: bool = False) -> None:
        """Create new general note with user-specified filename."""
        try:
            temp_config = h.dev.config_load("config/config.json", is_temp=True)
            default_path = temp_config.get(
                "path_last_note_folder", self.config.get("path_last_note_folder", self.config["path_notes"])
            )
        except (FileNotFoundError, OSError):
            default_path = self.config.get("path_last_note_folder", self.config["path_notes"])

        filename = self.get_save_filename("Save Note", default_path, "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        h.dev.config_update_value("path_last_note_folder", str(filename.parent), "config/config.json", is_temp=True)

        self.add_line(f"Folder path: {filename.parent}")
        self.add_line(f"File name without extension: {filename.stem}")

        config_folder = h.dev.get_project_root() / "config"
        template_files = self.config.get("note_beginning_templates", [])

        if not template_files:
            self.add_line("❌ No note_beginning_templates configured in config.json.")
            return

        file_contents = {}
        file_choices = []
        display_to_template = {}
        for template_file in template_files:
            if template_file.startswith("snippet:"):
                file_path_str = template_file[8:]
                file_path = h.dev.get_project_root() / file_path_str
                display_name = Path(file_path_str).name
            else:
                file_path = config_folder / template_file
                display_name = template_file

            if not file_path.exists():
                self.add_line(f"⚠️ Template file not found: {template_file}")
                continue

            try:
                with Path.open(file_path, "r", encoding="utf8") as f:
                    content = f.read()
                file_contents[template_file] = content
                lines = content.split("\n")
                max_count_lines = 10
                preview = "\n".join(lines[:max_count_lines]) + "\n..." if len(lines) > max_count_lines else content
                display_to_template[display_name] = template_file
                file_choices.append((display_name, preview))
            except Exception as e:
                self.add_line(f"❌ Error reading file {template_file}: {e}")
                continue

        if not file_choices:
            self.add_line("❌ No valid beginning template files could be read.")
            return

        selected_display_name = self.get_choice_from_list_with_descriptions(
            "Select Beginning Template", "Choose a beginning template:", file_choices
        )

        if not selected_display_name:
            return

        selected_template_file = display_to_template[selected_display_name]
        beginning_text = file_contents[selected_template_file]

        text = beginning_text + f"\n# {filename.stem}\n\n\n"
        filename_final = filename.stem.replace("-", "--").replace(" ", "-")

        result, filename = h.md.add_note(filename.parent, filename_final, text, is_with_images=is_with_images)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)

    def _execute_new_note_with_images(self) -> None:
        """Create new note with images directory."""
        self._execute_new_note(is_with_images=True)

    @ActionBase.handle_exceptions("processing quotes")
    def _execute_new_quotes(self) -> None:
        """Add new quotes with author and book title."""
        self._execute_new_quotes_format_with_author_and_book()

    def _execute_new_quotes_format_with_author_and_book(self) -> None:
        """Format quotes with specified author and book title via dialog."""
        quotes_folder = self.config.get("path_quotes", "")
        author_books_dict = self._extract_authors_and_books_from_quotes_folder(quotes_folder)
        authors_list = sorted(author_books_dict.keys())

        fields = [
            TemplateField("Author", "combobox", "{{Author:combobox}}", "", options=authors_list),
            TemplateField("Book Title", "combobox", "{{Book Title:combobox}}", "", options=[]),
            TemplateField(
                "Quotes",
                "multiline",
                "{{Quotes:multiline}}",
                (
                    "They can get a big bang out of buying a blanket.\n\n\n"
                    "I just mean that I used to think about old Spencer quite a lot"
                ),
            ),
        ]

        dialog = TemplateDialog(
            fields=fields,
            title="Enter Book, Author and Quotes",
        )

        author_widget = dialog.widgets.get("Author")
        book_widget = dialog.widgets.get("Book Title")
        if isinstance(author_widget, QComboBox) and isinstance(book_widget, QComboBox):

            def update_book_list(author_text: str) -> None:
                current_book = book_widget.currentText()
                book_widget.clear()

                if hasattr(book_widget, "smart_filter_model"):
                    delattr(book_widget, "smart_filter_model")
                if hasattr(book_widget, "smart_filter_proxy"):
                    delattr(book_widget, "smart_filter_proxy")
                if hasattr(book_widget, "smart_filter_completer"):
                    delattr(book_widget, "smart_filter_completer")
                if hasattr(book_widget, "smart_filter_items"):
                    delattr(book_widget, "smart_filter_items")

                if author_text and author_text in author_books_dict:
                    books = author_books_dict[author_text]
                    book_widget.addItems(books)
                    apply_smart_filtering(book_widget)

                    if current_book:
                        index = book_widget.findText(current_book)
                        if index >= 0:
                            book_widget.setCurrentIndex(index)
                        else:
                            book_widget.setCurrentText(current_book)
                else:
                    book_widget.setCurrentText(current_book or "")

            author_widget.currentTextChanged.connect(update_book_list)

            if author_widget.currentText():
                update_book_list(author_widget.currentText())

        if dialog.exec() != dialog.DialogCode.Accepted:
            self.add_line("❌ Dialog was canceled.")
            self.show_result()
            return

        field_values = dialog.get_field_values()
        if not field_values:
            self.add_line("❌ No field values collected.")
            self.show_result()
            return

        book_title = field_values.get("Book Title", "")
        author = field_values.get("Author", "")
        quotes_content = field_values.get("Quotes", "")

        if not book_title or not author or not quotes_content:
            self.add_line("❌ Book title, author and quotes are required.")
            self.show_result()
            return

        quotes = [q.strip() for q in quotes_content.split("\n\n") if q.strip()]

        formatted_content = ""
        for quote in quotes:
            formatted_content += f"{quote}\n\n{book_title}\n{author}\n\n\n"

        formatted_content = formatted_content.rstrip()

        result = h.md.format_quotes_as_markdown_content(formatted_content)

        quotes_without_header = result
        if quotes_without_header.startswith(f"# {book_title}"):
            lines = quotes_without_header.split("\n")
            for i_original, line in enumerate(lines):
                i = i_original
                if line.strip() == f"# {book_title}":
                    while i + 1 < len(lines) and not lines[i + 1].strip():
                        i += 1
                    quotes_without_header = "\n".join(lines[i + 1 :]).lstrip()
                    break

        success = self._save_quotes_to_file(quotes_without_header, author, book_title)
        if success:
            self.add_line("✅ Quotes saved to file successfully!")
        else:
            self.add_line("❌ Failed to save quotes to file.")

        self.show_result()

    def _extract_authors_and_books_from_quotes_folder(self, quotes_folder: str) -> dict[str, list[str]]:
        """Extract authors and their books from markdown quote files.

        If folder contains aggregated file _<FolderName>.g.md (e.g. Fiction -> _Fiction.g.md),
        only that file is scanned; otherwise all *.md in folder (and subfolders) are scanned.
        """
        author_books: dict[str, set[str]] = {}

        quotes_path = Path(quotes_folder)
        if not quotes_path.exists():
            return {}

        folder_name = quotes_path.name
        aggregated_file = quotes_path / f"_{folder_name}.g.md"
        md_files = [aggregated_file] if aggregated_file.exists() else list(quotes_path.rglob("*.md"))

        pattern = re.compile(r">\s*--\s*_([^_]+?),\s*([^_]+?)_", re.MULTILINE)

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Warning: Failed to read {md_file}: {e}")
                continue

            matches = pattern.findall(content)
            for author, book in matches:
                author_clean = author.strip()
                book_clean = book.strip()
                if author_clean and not author_clean.startswith("["):
                    if author_clean not in author_books:
                        author_books[author_clean] = set()
                    if book_clean:
                        author_books[author_clean].add(book_clean)

        return {author: sorted(books) for author, books in sorted(author_books.items())}

    def _extract_authors_and_english_names_from_books_folder(self, books_path: str) -> dict[str, str]:
        """Extract authors and their English names from books markdown files."""
        result: dict[str, str] = {}
        books_dir = Path(books_path.rstrip("/"))

        if not books_dir.exists():
            return result

        heading_pattern = re.compile(r"^#{2,3}\s+.+\(([^)]+)\):\s*[\d.]+", re.MULTILINE)
        english_pattern = re.compile(r"^\s*-\s*\*\*Author's name in English:\*\*\s*(.*)$", re.MULTILINE)

        for md_file in books_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Warning: Failed to read {md_file}: {e}")
                continue

            blocks = re.split(r"^#{2,3}\s+", content, flags=re.MULTILINE)
            for block in blocks[1:]:
                block_for_match = "## " + block
                heading_match = heading_pattern.match(block_for_match)
                if heading_match:
                    author = heading_match.group(1).strip()
                    if not author or author.startswith("["):
                        continue
                    english_match = english_pattern.search(block_for_match)
                    english_name = english_match.group(1).strip() if english_match else ""
                    if author and (author not in result or english_name):
                        result[author] = english_name

        return result

    def _get_authors_for_book_template(self, template_config: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
        """Get authors list and author-to-English-name mapping for Book template."""
        path_target = template_config.get("path_target", "")
        if not path_target:
            return [], {}

        author_to_english = self._extract_authors_and_english_names_from_books_folder(path_target)
        authors_list = sorted(author_to_english.keys())
        return authors_list, author_to_english

    def _optimize_single_image_for_template(
        self,
        image_path: str,
        image_save_dir: Path,
        max_size: int | None = None,
        image_folder: str = "img",
    ) -> str:
        """Optimize a single image and save to image_save_dir/img/. Same logic as OnOptimizeSelectedImages.

        Args:

        - `image_path` (`str`): Relative path (e.g. img/foo.png) or filename. Resolved against `image_save_dir/img/`.
        - `image_save_dir` (`Path`): Directory containing the markdown file (images go to `image_save_dir/img/`).
        - `max_size` (`int | None`): Maximum width or height in pixels. None to skip resize.
        - `image_folder` (`str`): Subfolder name for images. Defaults to `img`.

        Returns:

        - `str`: New relative path (e.g. img/foo.avif) or original path if unchanged/failed.

        """
        img_dir = image_save_dir / image_folder
        image_filename = Path(image_path) if Path(image_path).is_absolute() else (image_save_dir / image_path)
        if not image_filename.exists():
            return image_path

        ext = image_filename.suffix.lower()
        supported = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg", ".avif"]
        if ext not in supported:
            return image_path

        new_ext = ext
        if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"]:
            new_ext = ".avif"
        elif ext == ".png":
            new_ext = ".png"

        with TemporaryDirectory() as temp_folder:
            temp_folder_path = Path(temp_folder)
            temp_image = temp_folder_path / image_filename.name
            shutil.copy(image_filename, temp_image)

            commands = f'npm run optimize imagesFolder="{temp_folder}"'
            if ext == ".png":
                commands += " convertPngToAvif=compare"
            if max_size is not None:
                commands += f" maxSize={max_size}"

            h.dev.run_command(commands)

            optimized_dir = temp_folder_path / "temp"
            if ext == ".png" and (optimized_dir / f"{image_filename.stem}.avif").exists():
                new_ext = ".avif"
            optimized_image = optimized_dir / f"{image_filename.stem}{new_ext}"

            if not optimized_image.exists():
                return image_path

            img_dir.mkdir(parents=True, exist_ok=True)
            new_image_path = img_dir / f"{image_filename.stem}{new_ext}"
            if image_filename.exists():
                image_filename.unlink()
            shutil.copy(optimized_image, new_image_path)

            return f"{image_folder}/{image_filename.stem}{new_ext}".replace("\\", "/")

    def _replace_author_field_with_combobox(
        self, fields: list[TemplateField], authors_list: list[str]
    ) -> list[TemplateField]:
        """Replace Author line field with combobox in Book template fields."""
        new_fields = []
        for field in fields:
            if field.name == "Author":
                new_fields.append(TemplateField("Author", "combobox", "{{Author:combobox}}", "", options=authors_list))
            else:
                new_fields.append(field)
        return new_fields

    def _save_quotes_to_file(self, quotes_content: str, author: str, book_title: str) -> bool:
        """Save quotes to a markdown file."""
        selected_folder = self.get_folder_with_choice_option(
            "Select folder to save quotes",
            self.config.get("paths_quotes", []),
            self.config.get("path_quotes", ""),
        )

        if not selected_folder:
            return False

        author_folder_name = "-".join(part.strip() for part in author.split() if part.strip())
        author_folder = selected_folder / author_folder_name
        author_folder.mkdir(exist_ok=True)

        clean_title = book_title.replace("«", "").replace("»", "").replace('"', "").replace("'", "")
        book_filename = "-".join(part.strip() for part in clean_title.split() if part.strip())
        filename = f"{book_filename}.md"
        file_path = author_folder / filename

        header = f"# {book_title}"
        separator = "---"

        if file_path.exists():
            existing_content = file_path.read_text(encoding="utf-8")
            lines = existing_content.split("\n")
            new_lines = []
            header_found = False

            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip() == header.strip():
                    header_found = True
                    new_lines.append("")
                    new_lines.append(quotes_content)
                    new_lines.append("")
                    new_lines.append(separator)
                    new_lines.extend(lines[i + 1 :])
                    break

            if not header_found:
                if not existing_content.rstrip().endswith("---"):
                    new_lines.extend(["", separator, "", quotes_content])
                else:
                    new_lines.extend(["", quotes_content])

            content = "\n".join(new_lines)
        else:
            beginning_template = self.config["beginning_of_md"]
            content = f"{beginning_template}\n{header}\n\n{quotes_content}"

        content = content.rstrip() + "\n"
        file_path.write_text(content, encoding="utf-8")
        return True
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
        templates = self.config.get("markdown_templates", {})

        choices = []
        action_map = {}

        for template_name in templates:
            icon = template_name[0] if template_name else "📝"
            choices.append((icon, template_name))
            action_map[template_name] = ("template", template_name)

        for icon, title, method_name in self._COMMANDS:
            choices.append((icon, title))
            action_map[title] = ("method", method_name)

        selected_choice = self.get_choice_from_icons(
            "New Markdown",
            "Choose a command to create new Markdown content:",
            choices,
        )

        if not selected_choice:
            return

        selected_item = action_map.get(selected_choice)
        if not selected_item:
            self.add_line(f"❌ Unknown command selected: {selected_choice}")
            self.show_result()
            return

        item_type, item_value = selected_item

        if item_type == "template":
            self._execute_from_template(template_name=item_value)
        elif item_type == "method":
            method = getattr(self, item_value)
            method()
```

</details>

### ⚙️ Method `_execute_from_template`

```python
def _execute_from_template(self) -> None
```

Add Markdown content using template-based forms.

Reads a template file with field placeholders, shows a form dialog,
fills the template with user values, and inserts into target file or returns text.

<details>
<summary>Code:</summary>

```python
def _execute_from_template(self, *, template_name: str | None = None) -> None:
        templates = self.config.get("markdown_templates", {})

        if not templates:
            self.add_line("❌ No markdown templates configured in config.json")
            self.show_result()
            return

        selected_template = template_name
        if not selected_template:
            template_names = list(templates.keys())
            selected_template = self.get_choice_from_list(
                "Select Template",
                "Choose a template to use:",
                template_names,
            )
            if not selected_template:
                return

        template_config = templates[selected_template]
        template_file = template_config.get("template_file")

        if not template_file:
            self.add_line(f"❌ Template file not specified for '{selected_template}'")
            self.show_result()
            return

        template_path = Path(template_file)
        if not template_path.exists():
            self.add_line(f"❌ Template file not found: {template_file}")
            self.show_result()
            return

        with Path.open(template_path, encoding="utf-8") as f:
            template_content = f.read().strip()

        fields, _ = TemplateParser.parse_template(template_content)

        if not fields:
            self.add_line(f"❌ No fields found in template: {template_file}")
            self.show_result()
            return

        author_to_english: dict[str, str] = {}
        if selected_template == "📖 Book":
            authors_list, author_to_english = self._get_authors_for_book_template(template_config)
            fields = self._replace_author_field_with_combobox(fields, authors_list)

        dialog_links_config = template_config.get("dialog_links", [])
        dialog_links: list[tuple[str, str]] = []
        for item in dialog_links_config:
            if isinstance(item, dict):
                url = item.get("url", "").strip()
                if not url:
                    continue
                label = item.get("label", url).strip() or url
                dialog_links.append((label, url))
            elif isinstance(item, str):
                cleaned = item.strip()
                if cleaned:
                    dialog_links.append((cleaned, cleaned))

        path_target = template_config.get("path_target")
        path_target_path = Path(path_target.rstrip("/")) if path_target else None
        image_save_dir = path_target_path.parent if (path_target_path and path_target_path.suffix == ".md") else None

        dialog = TemplateDialog(
            fields=fields,
            title=f"Add {selected_template.capitalize()}",
            links=dialog_links,
            image_save_dir=image_save_dir,
        )

        if selected_template == "📖 Book" and author_to_english:
            author_widget = dialog.widgets.get("Author")
            author_english_widget = dialog.widgets.get("Author's name in English")
            if isinstance(author_widget, QComboBox) and isinstance(author_english_widget, QLineEdit):

                def _update_author_english(author_text: str) -> None:
                    english_name = author_to_english.get(author_text, "")
                    author_english_widget.setText(english_name)

                author_widget.currentTextChanged.connect(_update_author_english)
                if author_widget.currentText():
                    _update_author_english(author_widget.currentText())

        if dialog.exec() != dialog.DialogCode.Accepted:
            self.add_line("❌ Dialog was canceled.")
            self.show_result()
            return

        field_values = dialog.get_field_values()
        if not field_values:
            self.add_line("❌ No field values collected.")
            self.show_result()
            return

        result_markdown = TemplateParser.fill_template(template_content, field_values)

        if template_config.get("image_optimize") and image_save_dir:
            image_field_name = next((f.name for f in fields if f.field_type == "image"), None)
            image_path_value = field_values.get(image_field_name, "").strip() if image_field_name else ""
            if image_path_value:
                max_size = template_config.get("image_max_size")
                if max_size is not None:
                    try:
                        max_size = int(max_size)
                    except (ValueError, TypeError):
                        max_size = None
                try:
                    new_image_path = self._optimize_single_image_for_template(
                        image_path_value, image_save_dir, max_size
                    )
                    if new_image_path != image_path_value:
                        result_markdown = result_markdown.replace(image_path_value, new_image_path)
                except Exception as e:  # noqa: BLE001
                    self.add_line(f"⚠️ Image optimization skipped: {e}")

        path_target = template_config.get("path_target")
        insert_position = template_config.get("insert_position", "end")

        if path_target:
            current_year = datetime.now(UTC).astimezone().strftime("%Y")
            path_target_clean = path_target.rstrip("/")
            path_target_path = Path(path_target_clean)
            single_file = path_target_path.suffix == ".md"
            target_path = path_target_path if single_file else path_target_path / f"{current_year}.md"

            file_existed = target_path.exists()
            if file_existed:
                with Path.open(target_path, encoding="utf-8") as f:
                    existing_content = f.read()
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                beginning_content = self.config.get("beginning_of_md", "")
                if single_file:
                    if beginning_content:
                        existing_content = (
                            beginning_content
                            + "\n\n# Events\n\nТеатры, концерты и др.\n\n## "
                            + current_year
                            + "\n\n"
                            + result_markdown
                            + "\n"
                        )
                    else:
                        existing_content = (
                            "# Events\n\nТеатры, концерты и др.\n\n## " + current_year + "\n\n" + result_markdown + "\n"
                        )
                elif beginning_content:
                    existing_content = beginning_content + "\n\n# " + current_year + "\n"
                else:
                    existing_content = "# " + current_year + "\n"

            if not file_existed and single_file:
                new_content = existing_content
            elif insert_position == "end":
                new_content = existing_content.rstrip() + "\n\n" + result_markdown + "\n"
            elif insert_position == "start" and single_file:
                yaml_md, content_md = h.md.split_yaml_content(existing_content)
                year_heading_pattern = re.compile(r"^## " + re.escape(current_year) + r"\s*$", re.MULTILINE)
                year_match = year_heading_pattern.search(content_md)
                if year_match:
                    year_pos = year_match.end()
                    updated_content_md = (
                        content_md[:year_pos] + "\n\n" + result_markdown + "\n\n" + content_md[year_pos:].lstrip()
                    )
                    new_content = yaml_md + "\n\n" + updated_content_md if yaml_md else updated_content_md
                else:
                    toc_match = re.search(r"<details>[\s\S]*?<\/details>", content_md)
                    if toc_match:
                        insert_pos = toc_match.end()
                        updated_content_md = (
                            content_md[:insert_pos]
                            + "\n\n## "
                            + current_year
                            + "\n\n"
                            + result_markdown
                            + "\n\n"
                            + content_md[insert_pos:].lstrip()
                        )
                    else:
                        updated_content_md = (
                            "## " + current_year + "\n\n" + result_markdown + "\n\n" + content_md.lstrip()
                        )
                    new_content = yaml_md + "\n\n" + updated_content_md if yaml_md else updated_content_md
            elif insert_position == "start":
                yaml_md, content_md = h.md.split_yaml_content(existing_content)
                year_match = re.search(r"^#+ \d{4}", content_md, re.MULTILINE)

                if year_match:
                    toc_match = re.search(r"<details>[\s\S]*?<\/details>", content_md)
                    if toc_match:
                        toc_end_pos = toc_match.end()
                        updated_content_md = (
                            content_md[:toc_end_pos]
                            + "\n\n"
                            + result_markdown
                            + "\n\n"
                            + content_md[toc_end_pos:].lstrip()
                        )
                    else:
                        year_pos = year_match.end()
                        updated_content_md = (
                            content_md[:year_pos] + "\n\n" + result_markdown + "\n\n" + content_md[year_pos:].lstrip()
                        )
                    new_content = yaml_md + "\n\n" + updated_content_md if yaml_md else updated_content_md
                elif yaml_md:
                    new_content = yaml_md + "\n\n" + result_markdown + "\n\n" + content_md
                else:
                    new_content = result_markdown + "\n\n" + existing_content
            else:
                new_content = existing_content.rstrip() + "\n\n" + result_markdown + "\n"

            with Path.open(target_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            h.dev.run_command(
                f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{target_path}"'
            )
            self.add_line(f"✅ Added markdown to {target_path}")
            self.add_line("\nGenerated markdown:")
            self.add_line(result_markdown)
        else:
            self.add_line("Generated markdown:")
            self.add_line(result_markdown)

        self.show_result()
```

</details>

### ⚙️ Method `_execute_new_article`

```python
def _execute_new_article(self) -> None
```

Create new article with predefined template.

<details>
<summary>Code:</summary>

```python
def _execute_new_article(self) -> None:
        article_name = self.get_text_input(
            "Article title", "Enter the name of the article (English, without spaces):", "name-of-article"
        )
        if not article_name:
            return

        article_name = article_name.replace(" ", "-")

        now_local = datetime.now(UTC).astimezone()
        text = self.config["beginning_of_article"].replace(
            "[YEAR]",
            now_local.strftime("%Y"),
        )
        text = text.replace("[NAME]", article_name)
        text = text.replace(
            "[DATE]",
            now_local.strftime("%Y-%m-%d"),
        )
        text += f"\n# {article_name.capitalize().replace('-', ' ')}\n\n\n"

        result, filename = h.md.add_note(Path(self.config["path_articles"]), article_name, text, is_with_images=True)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_articles"]}" "{filename}"')
        self.add_line(result)
```

</details>

### ⚙️ Method `_execute_new_diary`

```python
def _execute_new_diary(self) -> None
```

Create new diary entry for current date.

<details>
<summary>Code:</summary>

```python
def _execute_new_diary(self) -> None:
        result, filename = h.md.add_diary_new_dairy_in_year(self.config["path_diary"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)
```

</details>

### ⚙️ Method `_execute_new_diary_cases`

```python
def _execute_new_diary_cases(self) -> None
```

Create new cases entry for current month.

<details>
<summary>Code:</summary>

```python
def _execute_new_diary_cases(self) -> None:
        path_cases = self.config.get("path_cases")
        if not path_cases:
            self.add_line("❌ path_cases is not configured in config.json.")
            self.show_result()
            return
        result, filename = h.md.add_diary_new_cases_in_year(path_cases, self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)
```

</details>

### ⚙️ Method `_execute_new_diary_dream`

```python
def _execute_new_diary_dream(self) -> None
```

Create new dream journal entry for current date.

<details>
<summary>Code:</summary>

```python
def _execute_new_diary_dream(self) -> None:
        result, filename = h.md.add_diary_new_dream_in_year(self.config["path_dream"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)
```

</details>

### ⚙️ Method `_execute_new_note`

```python
def _execute_new_note(self) -> None
```

Create new general note with user-specified filename.

<details>
<summary>Code:</summary>

```python
def _execute_new_note(self, *, is_with_images: bool = False) -> None:
        try:
            temp_config = h.dev.config_load("config/config.json", is_temp=True)
            default_path = temp_config.get(
                "path_last_note_folder", self.config.get("path_last_note_folder", self.config["path_notes"])
            )
        except (FileNotFoundError, OSError):
            default_path = self.config.get("path_last_note_folder", self.config["path_notes"])

        filename = self.get_save_filename("Save Note", default_path, "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        h.dev.config_update_value("path_last_note_folder", str(filename.parent), "config/config.json", is_temp=True)

        self.add_line(f"Folder path: {filename.parent}")
        self.add_line(f"File name without extension: {filename.stem}")

        config_folder = h.dev.get_project_root() / "config"
        template_files = self.config.get("note_beginning_templates", [])

        if not template_files:
            self.add_line("❌ No note_beginning_templates configured in config.json.")
            return

        file_contents = {}
        file_choices = []
        display_to_template = {}
        for template_file in template_files:
            if template_file.startswith("snippet:"):
                file_path_str = template_file[8:]
                file_path = h.dev.get_project_root() / file_path_str
                display_name = Path(file_path_str).name
            else:
                file_path = config_folder / template_file
                display_name = template_file

            if not file_path.exists():
                self.add_line(f"⚠️ Template file not found: {template_file}")
                continue

            try:
                with Path.open(file_path, "r", encoding="utf8") as f:
                    content = f.read()
                file_contents[template_file] = content
                lines = content.split("\n")
                max_count_lines = 10
                preview = "\n".join(lines[:max_count_lines]) + "\n..." if len(lines) > max_count_lines else content
                display_to_template[display_name] = template_file
                file_choices.append((display_name, preview))
            except Exception as e:
                self.add_line(f"❌ Error reading file {template_file}: {e}")
                continue

        if not file_choices:
            self.add_line("❌ No valid beginning template files could be read.")
            return

        selected_display_name = self.get_choice_from_list_with_descriptions(
            "Select Beginning Template", "Choose a beginning template:", file_choices
        )

        if not selected_display_name:
            return

        selected_template_file = display_to_template[selected_display_name]
        beginning_text = file_contents[selected_template_file]

        text = beginning_text + f"\n# {filename.stem}\n\n\n"
        filename_final = filename.stem.replace("-", "--").replace(" ", "-")

        result, filename = h.md.add_note(filename.parent, filename_final, text, is_with_images=is_with_images)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)
```

</details>

### ⚙️ Method `_execute_new_note_with_images`

```python
def _execute_new_note_with_images(self) -> None
```

Create new note with images directory.

<details>
<summary>Code:</summary>

```python
def _execute_new_note_with_images(self) -> None:
        self._execute_new_note(is_with_images=True)
```

</details>

### ⚙️ Method `_execute_new_quotes`

```python
def _execute_new_quotes(self) -> None
```

Add new quotes with author and book title.

<details>
<summary>Code:</summary>

```python
def _execute_new_quotes(self) -> None:
        self._execute_new_quotes_format_with_author_and_book()
```

</details>

### ⚙️ Method `_execute_new_quotes_format_with_author_and_book`

```python
def _execute_new_quotes_format_with_author_and_book(self) -> None
```

Format quotes with specified author and book title via dialog.

<details>
<summary>Code:</summary>

```python
def _execute_new_quotes_format_with_author_and_book(self) -> None:
        quotes_folder = self.config.get("path_quotes", "")
        author_books_dict = self._extract_authors_and_books_from_quotes_folder(quotes_folder)
        authors_list = sorted(author_books_dict.keys())

        fields = [
            TemplateField("Author", "combobox", "{{Author:combobox}}", "", options=authors_list),
            TemplateField("Book Title", "combobox", "{{Book Title:combobox}}", "", options=[]),
            TemplateField(
                "Quotes",
                "multiline",
                "{{Quotes:multiline}}",
                (
                    "They can get a big bang out of buying a blanket.\n\n\n"
                    "I just mean that I used to think about old Spencer quite a lot"
                ),
            ),
        ]

        dialog = TemplateDialog(
            fields=fields,
            title="Enter Book, Author and Quotes",
        )

        author_widget = dialog.widgets.get("Author")
        book_widget = dialog.widgets.get("Book Title")
        if isinstance(author_widget, QComboBox) and isinstance(book_widget, QComboBox):

            def update_book_list(author_text: str) -> None:
                current_book = book_widget.currentText()
                book_widget.clear()

                if hasattr(book_widget, "smart_filter_model"):
                    delattr(book_widget, "smart_filter_model")
                if hasattr(book_widget, "smart_filter_proxy"):
                    delattr(book_widget, "smart_filter_proxy")
                if hasattr(book_widget, "smart_filter_completer"):
                    delattr(book_widget, "smart_filter_completer")
                if hasattr(book_widget, "smart_filter_items"):
                    delattr(book_widget, "smart_filter_items")

                if author_text and author_text in author_books_dict:
                    books = author_books_dict[author_text]
                    book_widget.addItems(books)
                    apply_smart_filtering(book_widget)

                    if current_book:
                        index = book_widget.findText(current_book)
                        if index >= 0:
                            book_widget.setCurrentIndex(index)
                        else:
                            book_widget.setCurrentText(current_book)
                else:
                    book_widget.setCurrentText(current_book or "")

            author_widget.currentTextChanged.connect(update_book_list)

            if author_widget.currentText():
                update_book_list(author_widget.currentText())

        if dialog.exec() != dialog.DialogCode.Accepted:
            self.add_line("❌ Dialog was canceled.")
            self.show_result()
            return

        field_values = dialog.get_field_values()
        if not field_values:
            self.add_line("❌ No field values collected.")
            self.show_result()
            return

        book_title = field_values.get("Book Title", "")
        author = field_values.get("Author", "")
        quotes_content = field_values.get("Quotes", "")

        if not book_title or not author or not quotes_content:
            self.add_line("❌ Book title, author and quotes are required.")
            self.show_result()
            return

        quotes = [q.strip() for q in quotes_content.split("\n\n") if q.strip()]

        formatted_content = ""
        for quote in quotes:
            formatted_content += f"{quote}\n\n{book_title}\n{author}\n\n\n"

        formatted_content = formatted_content.rstrip()

        result = h.md.format_quotes_as_markdown_content(formatted_content)

        quotes_without_header = result
        if quotes_without_header.startswith(f"# {book_title}"):
            lines = quotes_without_header.split("\n")
            for i_original, line in enumerate(lines):
                i = i_original
                if line.strip() == f"# {book_title}":
                    while i + 1 < len(lines) and not lines[i + 1].strip():
                        i += 1
                    quotes_without_header = "\n".join(lines[i + 1 :]).lstrip()
                    break

        success = self._save_quotes_to_file(quotes_without_header, author, book_title)
        if success:
            self.add_line("✅ Quotes saved to file successfully!")
        else:
            self.add_line("❌ Failed to save quotes to file.")

        self.show_result()
```

</details>

### ⚙️ Method `_extract_authors_and_books_from_quotes_folder`

```python
def _extract_authors_and_books_from_quotes_folder(self, quotes_folder: str) -> dict[str, list[str]]
```

Extract authors and their books from markdown quote files.

If folder contains aggregated file \_<FolderName>.g.md (e.g. Fiction -> \_Fiction.g.md),
only that file is scanned; otherwise all \*.md in folder (and subfolders) are scanned.

<details>
<summary>Code:</summary>

```python
def _extract_authors_and_books_from_quotes_folder(self, quotes_folder: str) -> dict[str, list[str]]:
        author_books: dict[str, set[str]] = {}

        quotes_path = Path(quotes_folder)
        if not quotes_path.exists():
            return {}

        folder_name = quotes_path.name
        aggregated_file = quotes_path / f"_{folder_name}.g.md"
        md_files = [aggregated_file] if aggregated_file.exists() else list(quotes_path.rglob("*.md"))

        pattern = re.compile(r">\s*--\s*_([^_]+?),\s*([^_]+?)_", re.MULTILINE)

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Warning: Failed to read {md_file}: {e}")
                continue

            matches = pattern.findall(content)
            for author, book in matches:
                author_clean = author.strip()
                book_clean = book.strip()
                if author_clean and not author_clean.startswith("["):
                    if author_clean not in author_books:
                        author_books[author_clean] = set()
                    if book_clean:
                        author_books[author_clean].add(book_clean)

        return {author: sorted(books) for author, books in sorted(author_books.items())}
```

</details>

### ⚙️ Method `_extract_authors_and_english_names_from_books_folder`

```python
def _extract_authors_and_english_names_from_books_folder(self, books_path: str) -> dict[str, str]
```

Extract authors and their English names from books markdown files.

<details>
<summary>Code:</summary>

```python
def _extract_authors_and_english_names_from_books_folder(self, books_path: str) -> dict[str, str]:
        result: dict[str, str] = {}
        books_dir = Path(books_path.rstrip("/"))

        if not books_dir.exists():
            return result

        heading_pattern = re.compile(r"^#{2,3}\s+.+\(([^)]+)\):\s*[\d.]+", re.MULTILINE)
        english_pattern = re.compile(r"^\s*-\s*\*\*Author's name in English:\*\*\s*(.*)$", re.MULTILINE)

        for md_file in books_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Warning: Failed to read {md_file}: {e}")
                continue

            blocks = re.split(r"^#{2,3}\s+", content, flags=re.MULTILINE)
            for block in blocks[1:]:
                block_for_match = "## " + block
                heading_match = heading_pattern.match(block_for_match)
                if heading_match:
                    author = heading_match.group(1).strip()
                    if not author or author.startswith("["):
                        continue
                    english_match = english_pattern.search(block_for_match)
                    english_name = english_match.group(1).strip() if english_match else ""
                    if author and (author not in result or english_name):
                        result[author] = english_name

        return result
```

</details>

### ⚙️ Method `_get_authors_for_book_template`

```python
def _get_authors_for_book_template(self, template_config: dict[str, Any]) -> tuple[list[str], dict[str, str]]
```

Get authors list and author-to-English-name mapping for Book template.

<details>
<summary>Code:</summary>

```python
def _get_authors_for_book_template(self, template_config: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
        path_target = template_config.get("path_target", "")
        if not path_target:
            return [], {}

        author_to_english = self._extract_authors_and_english_names_from_books_folder(path_target)
        authors_list = sorted(author_to_english.keys())
        return authors_list, author_to_english
```

</details>

### ⚙️ Method `_optimize_single_image_for_template`

```python
def _optimize_single_image_for_template(self, image_path: str, image_save_dir: Path, max_size: int | None = None, image_folder: str = "img") -> str
```

Optimize a single image and save to image_save_dir/img/. Same logic as OnOptimizeSelectedImages.

Args:

- `image_path` (`str`): Relative path (e.g. img/foo.png) or filename. Resolved against `image_save_dir/img/`.
- `image_save_dir` (`Path`): Directory containing the markdown file (images go to `image_save_dir/img/`).
- `max_size` (`int | None`): Maximum width or height in pixels. None to skip resize.
- `image_folder` (`str`): Subfolder name for images. Defaults to `img`.

Returns:

- `str`: New relative path (e.g. img/foo.avif) or original path if unchanged/failed.

<details>
<summary>Code:</summary>

```python
def _optimize_single_image_for_template(
        self,
        image_path: str,
        image_save_dir: Path,
        max_size: int | None = None,
        image_folder: str = "img",
    ) -> str:
        img_dir = image_save_dir / image_folder
        image_filename = Path(image_path) if Path(image_path).is_absolute() else (image_save_dir / image_path)
        if not image_filename.exists():
            return image_path

        ext = image_filename.suffix.lower()
        supported = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg", ".avif"]
        if ext not in supported:
            return image_path

        new_ext = ext
        if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"]:
            new_ext = ".avif"
        elif ext == ".png":
            new_ext = ".png"

        with TemporaryDirectory() as temp_folder:
            temp_folder_path = Path(temp_folder)
            temp_image = temp_folder_path / image_filename.name
            shutil.copy(image_filename, temp_image)

            commands = f'npm run optimize imagesFolder="{temp_folder}"'
            if ext == ".png":
                commands += " convertPngToAvif=compare"
            if max_size is not None:
                commands += f" maxSize={max_size}"

            h.dev.run_command(commands)

            optimized_dir = temp_folder_path / "temp"
            if ext == ".png" and (optimized_dir / f"{image_filename.stem}.avif").exists():
                new_ext = ".avif"
            optimized_image = optimized_dir / f"{image_filename.stem}{new_ext}"

            if not optimized_image.exists():
                return image_path

            img_dir.mkdir(parents=True, exist_ok=True)
            new_image_path = img_dir / f"{image_filename.stem}{new_ext}"
            if image_filename.exists():
                image_filename.unlink()
            shutil.copy(optimized_image, new_image_path)

            return f"{image_folder}/{image_filename.stem}{new_ext}".replace("\\", "/")
```

</details>

### ⚙️ Method `_replace_author_field_with_combobox`

```python
def _replace_author_field_with_combobox(self, fields: list[TemplateField], authors_list: list[str]) -> list[TemplateField]
```

Replace Author line field with combobox in Book template fields.

<details>
<summary>Code:</summary>

```python
def _replace_author_field_with_combobox(
        self, fields: list[TemplateField], authors_list: list[str]
    ) -> list[TemplateField]:
        new_fields = []
        for field in fields:
            if field.name == "Author":
                new_fields.append(TemplateField("Author", "combobox", "{{Author:combobox}}", "", options=authors_list))
            else:
                new_fields.append(field)
        return new_fields
```

</details>

### ⚙️ Method `_save_quotes_to_file`

```python
def _save_quotes_to_file(self, quotes_content: str, author: str, book_title: str) -> bool
```

Save quotes to a markdown file.

<details>
<summary>Code:</summary>

```python
def _save_quotes_to_file(self, quotes_content: str, author: str, book_title: str) -> bool:
        selected_folder = self.get_folder_with_choice_option(
            "Select folder to save quotes",
            self.config.get("paths_quotes", []),
            self.config.get("path_quotes", ""),
        )

        if not selected_folder:
            return False

        author_folder_name = "-".join(part.strip() for part in author.split() if part.strip())
        author_folder = selected_folder / author_folder_name
        author_folder.mkdir(exist_ok=True)

        clean_title = book_title.replace("«", "").replace("»", "").replace('"', "").replace("'", "")
        book_filename = "-".join(part.strip() for part in clean_title.split() if part.strip())
        filename = f"{book_filename}.md"
        file_path = author_folder / filename

        header = f"# {book_title}"
        separator = "---"

        if file_path.exists():
            existing_content = file_path.read_text(encoding="utf-8")
            lines = existing_content.split("\n")
            new_lines = []
            header_found = False

            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip() == header.strip():
                    header_found = True
                    new_lines.append("")
                    new_lines.append(quotes_content)
                    new_lines.append("")
                    new_lines.append(separator)
                    new_lines.extend(lines[i + 1 :])
                    break

            if not header_found:
                if not existing_content.rstrip().endswith("---"):
                    new_lines.extend(["", separator, "", quotes_content])
                else:
                    new_lines.extend(["", quotes_content])

            content = "\n".join(new_lines)
        else:
            beginning_template = self.config["beginning_of_md"]
            content = f"{beginning_template}\n{header}\n\n{quotes_content}"

        content = content.rstrip() + "\n"
        file_path.write_text(content, encoding="utf-8")
        return True
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
            "Select folder with Markdown files", self.config["path_articles"]
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

                            # For PNG with size comparison, use whichever output exists
                            if (
                                is_compare_png_avif_sizes
                                and ext == ".png"
                                and (optimized_images_dir / f"{image_filename.stem}.avif").exists()
                            ):
                                new_ext = ".avif"

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
            "Select folder with Markdown files", self.config["path_articles"]
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

                            # For PNG with size comparison, use whichever output exists
                            if (
                                is_compare_png_avif_sizes
                                and ext == ".png"
                                and (optimized_images_dir / f"{image_filename.stem}.avif").exists()
                            ):
                                new_ext = ".avif"

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
        result = self.get_open_filenames_with_resize(
            "Select images to optimize",
            self.config["path_articles"],
            "Image files (*.png *.jpg *.jpeg *.gif *.webp *.mp4 *.svg *.avif);;All Files (*)",
        )
        if result[0] is None:
            return
        self.selected_images = result[0]
        resize_enabled = result[1]
        max_size_str = result[2]
        self.max_size: int | None = None
        if resize_enabled and max_size_str:
            try:
                self.max_size = int(max_size_str)
            except ValueError:
                self.max_size = 1024
        elif resize_enabled:
            self.max_size = 1024

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
                result = self.optimize_selected_images_in_md(md_file, images, self.max_size)
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
        max_size: int | None = None,
    ) -> str:
        """Optimize only selected images referenced in Markdown content.

        Args:

        - `markdown_text` (`str`): The Markdown content to process.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `selected_image_names` (`set[str]`): Set of image filenames to optimize.
        - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
        - `max_size` (`int | None`): Maximum width or height in pixels for resizing. None to skip resize.

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
                max_size,
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
        max_size: int | None = None,
    ) -> str:
        """Process a single line of Markdown to optimize only selected image references.

        Args:

        - `markdown_line` (`str`): A single line from the Markdown document.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `selected_image_names` (`set[str]`): Set of image filenames to optimize.
        - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
        - `max_size` (`int | None`): Maximum width or height in pixels for resizing. None to skip resize.

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
                            if max_size is not None:
                                commands += f" maxSize={max_size}"

                            h.dev.run_command(commands)

                            # Path to the optimized images directory
                            optimized_images_dir = temp_folder_path / "temp"

                            # For PNG with size comparison, use whichever output exists
                            if ext == ".png" and (optimized_images_dir / f"{image_filename.stem}.avif").exists():
                                new_ext = ".avif"

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

    def optimize_selected_images_in_md(
        self, md_file: Path, selected_images: list[Path], max_size: int | None = None
    ) -> str:
        """Optimize only the selected images in a Markdown file.

        Args:

        - `md_file` (`Path`): Path to the Markdown file.
        - `selected_images` (`list[Path]`): List of selected image paths to optimize.
        - `max_size` (`int | None`): Maximum width or height in pixels for resizing. None to skip resize.

        Returns:

        - `str`: Status message indicating the result of the operation.

        """
        try:
            with Path.open(md_file, encoding="utf-8") as f:
                document = f.read()

            # Get the names of selected images for filtering
            selected_image_names = {img.name for img in selected_images}

            # Process the document, optimizing only selected images
            document_new = self.optimize_selected_images_content(
                document, md_file.parent, selected_image_names, max_size=max_size
            )

            if document != document_new:
                with Path.open(md_file, "w", encoding="utf-8") as file:
                    file.write(document_new)
                return f"✅ File {md_file} updated with optimized images."
        except Exception as e:
            return f"❌ Error processing {md_file}: {e}"
        return f"ℹ️ File {md_file} was not changed (no selected images found)."  # noqa: RUF001

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
        result = self.get_open_filenames_with_resize(
            "Select images to optimize",
            self.config["path_articles"],
            "Image files (*.png *.jpg *.jpeg *.gif *.webp *.mp4 *.svg *.avif);;All Files (*)",
        )
        if result[0] is None:
            return
        self.selected_images = result[0]
        resize_enabled = result[1]
        max_size_str = result[2]
        self.max_size: int | None = None
        if resize_enabled and max_size_str:
            try:
                self.max_size = int(max_size_str)
            except ValueError:
                self.max_size = 1024
        elif resize_enabled:
            self.max_size = 1024

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
                result = self.optimize_selected_images_in_md(md_file, images, self.max_size)
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
def optimize_selected_images_content(self, markdown_text: str, path_md: Path | str, selected_image_names: set[str], image_folder: str = "img", max_size: int | None = None) -> str
```

Optimize only selected images referenced in Markdown content.

Args:

- `markdown_text` (`str`): The Markdown content to process.
- `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
- `selected_image_names` (`set[str]`): Set of image filenames to optimize.
- `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
- `max_size` (`int | None`): Maximum width or height in pixels for resizing. None to skip resize.

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
        max_size: int | None = None,
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
                max_size,
            )
            new_lines.append(processed_line)
        content_md = "\n".join(new_lines)

        return yaml_md + "\n\n" + content_md
```

</details>

### ⚙️ Method `optimize_selected_images_content_line`

```python
def optimize_selected_images_content_line(self, markdown_line: str, path_md: Path | str, selected_image_names: set[str], image_folder: str = "img", max_size: int | None = None) -> str
```

Process a single line of Markdown to optimize only selected image references.

Args:

- `markdown_line` (`str`): A single line from the Markdown document.
- `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
- `selected_image_names` (`set[str]`): Set of image filenames to optimize.
- `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
- `max_size` (`int | None`): Maximum width or height in pixels for resizing. None to skip resize.

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
        max_size: int | None = None,
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
                            if max_size is not None:
                                commands += f" maxSize={max_size}"

                            h.dev.run_command(commands)

                            # Path to the optimized images directory
                            optimized_images_dir = temp_folder_path / "temp"

                            # For PNG with size comparison, use whichever output exists
                            if ext == ".png" and (optimized_images_dir / f"{image_filename.stem}.avif").exists():
                                new_ext = ".avif"

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
def optimize_selected_images_in_md(self, md_file: Path, selected_images: list[Path], max_size: int | None = None) -> str
```

Optimize only the selected images in a Markdown file.

Args:

- `md_file` (`Path`): Path to the Markdown file.
- `selected_images` (`list[Path]`): List of selected image paths to optimize.
- `max_size` (`int | None`): Maximum width or height in pixels for resizing. None to skip resize.

Returns:

- `str`: Status message indicating the result of the operation.

<details>
<summary>Code:</summary>

```python
def optimize_selected_images_in_md(
        self, md_file: Path, selected_images: list[Path], max_size: int | None = None
    ) -> str:
        try:
            with Path.open(md_file, encoding="utf-8") as f:
                document = f.read()

            # Get the names of selected images for filtering
            selected_image_names = {img.name for img in selected_images}

            # Process the document, optimizing only selected images
            document_new = self.optimize_selected_images_content(
                document, md_file.parent, selected_image_names, max_size=max_size
            )

            if document != document_new:
                with Path.open(md_file, "w", encoding="utf-8") as file:
                    file.write(document_new)
                return f"✅ File {md_file} updated with optimized images."
        except Exception as e:
            return f"❌ Error processing {md_file}: {e}"
        return f"ℹ️ File {md_file} was not changed (no selected images found)."  # noqa: RUF001
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
