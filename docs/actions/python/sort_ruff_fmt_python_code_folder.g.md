---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sort_ruff_fmt_python_code_folder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSortRuffFmtPythonCodeFolder`](#️-class-onsortrufffmtpythoncodefolder)
  - [⚙️ Method `in_thread`](#️-method-in_thread)
  - [⚙️ Method `thread_after`](#️-method-thread_after)

</details>

## 🏛️ Class `OnSortRuffFmtPythonCodeFolder`

```python
class OnSortRuffFmtPythonCodeFolder(OnSortRuffFmtDocsPythonCodeFolder)
```

Format and sort Python code in a selected folder using multiple tools.

This action applies a comprehensive code formatting and organization workflow to all
Python files in a user-selected directory. The process consists of three steps:

1. Running `ruff check --select I --fix` to organize and standardize imports
2. Applying ruff format to enforce consistent code style and formatting
3. Using a custom sorting function (`h.py.sort_py_code`) to organize code elements
   such as classes, methods, and functions in a consistent order

<details>
<summary>Code:</summary>

```python
class OnSortRuffFmtPythonCodeFolder(OnSortRuffFmtDocsPythonCodeFolder):

    icon = "🌟"
    title = "ruff sort, ruff format, sort PY in …"
    bold_title = False
    include_docs_generation = False
    cli_available = True
    cli_hint = "py ruff-sort"

    @ActionBase.handle_exceptions("formatting and sorting Python thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.format_and_sort_python_common(
            str(self.folder_path), is_include_docs_generation=self.include_docs_generation
        )

    @ActionBase.handle_exceptions("formatting and sorting Python thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
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
