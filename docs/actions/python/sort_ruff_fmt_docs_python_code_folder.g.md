---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sort_ruff_fmt_docs_python_code_folder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSortRuffFmtDocsPythonCodeFolder`](#️-class-onsortrufffmtdocspythoncodefolder)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `format_and_sort_python_common`](#️-method-format_and_sort_python_common)
  - [⚙️ Method `in_thread`](#️-method-in_thread)
  - [⚙️ Method `thread_after`](#️-method-thread_after)

</details>

## 🏛️ Class `OnSortRuffFmtDocsPythonCodeFolder`

```python
class OnSortRuffFmtDocsPythonCodeFolder(ActionBase)
```

Format, sort Python code and generate documentation in a selected folder.

This action applies a comprehensive code formatting, organization and documentation
workflow to all Python files in a user-selected directory. The process consists of
five steps:

1. Running `ruff check --select I --fix` to organize and standardize imports
2. Applying ruff format to enforce consistent code style and formatting
3. Using a custom sorting function (`h.py.sort_py_code`) to organize code elements
   such as classes, methods, and functions in a consistent order
4. Generating Markdown documentation from Python code using `h.py.generate_md_docs`
5. Formatting generated Markdown files with the harrix-pylib formatter

<details>
<summary>Code:</summary>

```python
class OnSortRuffFmtDocsPythonCodeFolder(ActionBase):

    icon = "🌟"
    title = "ruff sort, ruff format, sort, make docs PY in …"
    bold_title = True
    include_docs_generation: ClassVar[bool] = True
    cli_available = True
    cli_hint = "python ruff-sort-docs"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnGetMenu action."""
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")

    @ActionBase.handle_exceptions("formatting and sorting Python code with docs")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Format, sort Python code and generate documentation in a selected folder."""
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_python_projects"], self.config["path_github"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
            self.format_and_sort_python_common(
                str(self.folder_path), is_include_docs_generation=self.include_docs_generation
            )
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def format_and_sort_python_common(self, folder_path: str, *, is_include_docs_generation: bool = True) -> None:
        """Perform common formatting and sorting operations on Python files in a folder.

        This method applies a series of code formatting and organization operations to all
        Python files in the specified folder, including import sorting and code
        formatting with Ruff, and custom code element sorting. Optionally includes
        documentation generation and Markdown formatting.

        Args:

        - `folder_path` (`str`): Path to the folder containing Python files to process.
        - `is_include_docs_generation` (`bool`): Whether to include documentation generation
        and Markdown formatting steps. Defaults to `True`.

        Returns:

        - `None`: This method performs operations and logs results but returns nothing.

        Note:

        - The method preserves the exact execution order of operations for consistency.
        - All operations are logged using `self.add_line()` for user feedback.
        - If `is_include_docs_generation` is `True`, the method will generate Markdown
        documentation and format Markdown with the harrix-pylib formatter.

        """
        # Sort imports and format with Ruff (single tool for both steps).
        self.add_line("🔵 Format and sort imports")
        commands = "uv run --active ruff check --select I --fix . && uv run --active ruff format"
        self.add_line(h.dev.run_command(commands, cwd=folder_path))

        # Sort Python code elements
        self.add_line("🔵 Sort Python code elements")
        try:
            self.add_line(h.file.apply_func(folder_path, ".py", h.py.sort_py_code))
        except Exception as e:
            # `h.py.sort_py_code` can fail on some syntax constructs; don't block the rest of the pipeline.
            self.add_line(f"⚠️ Skip sorting Python code elements due to error: {e!s}")

        # Check if folder_path is the application root
        app_root = str(Path(__file__).parent.parent.parent.parent.resolve())
        folder_path_resolved = str(Path(folder_path).resolve())
        if folder_path_resolved == app_root and self.parent is not None:
            self.add_line("🔵 Get the list of items from this menu")
            result = self.parent.get_menu()
            self.add_line(result)

        if is_include_docs_generation:
            # Generate Markdown documentation
            self.add_line("🔵 Generate Markdown documentation")
            domain = f"https://github.com/{self.config['github_user']}/{Path(folder_path).parts[-1]}"
            self.add_line(h.py.generate_md_docs(folder_path, self.config["beginning_of_md_docs"], domain))

            # Format markdown files
            self.add_line("🔵 Format markdown files")
            OnBeautifyMdFolder.beautify_markdown_common(self, folder_path, is_include_summaries_and_combine=False)

    @ActionBase.handle_exceptions("formatting and sorting Python with docs thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.format_and_sort_python_common(
            str(self.folder_path), is_include_docs_generation=self.include_docs_generation
        )

    @ActionBase.handle_exceptions("formatting and sorting Python with docs thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, **kwargs) -> None
```

Initialize the OnGetMenu action.

<details>
<summary>Code:</summary>

```python
def __init__(self, **kwargs) -> None:  # noqa: ANN003
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Format, sort Python code and generate documentation in a selected folder.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_python_projects"], self.config["path_github"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
            self.format_and_sort_python_common(
                str(self.folder_path), is_include_docs_generation=self.include_docs_generation
            )
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `format_and_sort_python_common`

```python
def format_and_sort_python_common(self, folder_path: str) -> None
```

Perform common formatting and sorting operations on Python files in a folder.

This method applies a series of code formatting and organization operations to all
Python files in the specified folder, including import sorting and code
formatting with Ruff, and custom code element sorting. Optionally includes
documentation generation and Markdown formatting.

Args:

- `folder_path` (`str`): Path to the folder containing Python files to process.
- `is_include_docs_generation` (`bool`): Whether to include documentation generation
  and Markdown formatting steps. Defaults to `True`.

Returns:

- `None`: This method performs operations and logs results but returns nothing.

Note:

- The method preserves the exact execution order of operations for consistency.
- All operations are logged using `self.add_line()` for user feedback.
- If `is_include_docs_generation` is `True`, the method will generate Markdown
  documentation and format Markdown with the harrix-pylib formatter.

<details>
<summary>Code:</summary>

```python
def format_and_sort_python_common(self, folder_path: str, *, is_include_docs_generation: bool = True) -> None:
        # Sort imports and format with Ruff (single tool for both steps).
        self.add_line("🔵 Format and sort imports")
        commands = "uv run --active ruff check --select I --fix . && uv run --active ruff format"
        self.add_line(h.dev.run_command(commands, cwd=folder_path))

        # Sort Python code elements
        self.add_line("🔵 Sort Python code elements")
        try:
            self.add_line(h.file.apply_func(folder_path, ".py", h.py.sort_py_code))
        except Exception as e:
            # `h.py.sort_py_code` can fail on some syntax constructs; don't block the rest of the pipeline.
            self.add_line(f"⚠️ Skip sorting Python code elements due to error: {e!s}")

        # Check if folder_path is the application root
        app_root = str(Path(__file__).parent.parent.parent.parent.resolve())
        folder_path_resolved = str(Path(folder_path).resolve())
        if folder_path_resolved == app_root and self.parent is not None:
            self.add_line("🔵 Get the list of items from this menu")
            result = self.parent.get_menu()
            self.add_line(result)

        if is_include_docs_generation:
            # Generate Markdown documentation
            self.add_line("🔵 Generate Markdown documentation")
            domain = f"https://github.com/{self.config['github_user']}/{Path(folder_path).parts[-1]}"
            self.add_line(h.py.generate_md_docs(folder_path, self.config["beginning_of_md_docs"], domain))

            # Format markdown files
            self.add_line("🔵 Format markdown files")
            OnBeautifyMdFolder.beautify_markdown_common(self, folder_path, is_include_summaries_and_combine=False)
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
        self.format_and_sort_python_common(
            str(self.folder_path), is_include_docs_generation=self.include_docs_generation
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
