"""Actions for Python development and code management."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.python.sort_ruff_fmt_docs_python_code_folder import (
    OnSortRuffFmtDocsPythonCodeFolder,
)


class OnSortRuffFmtPythonCodeFolder(OnSortRuffFmtDocsPythonCodeFolder):
    """Format and sort Python code in a selected folder using multiple tools.

    This action applies a comprehensive code formatting and organization workflow to all
    Python files in a user-selected directory. The process consists of three steps:

    1. Running `ruff check --select I --fix` to organize and standardize imports
    2. Applying ruff format to enforce consistent code style and formatting
    3. Using a custom sorting function (`h.py.sort_py_code`) to organize code elements
       such as classes, methods, and functions in a consistent order
    """

    icon = "🌟"
    title = "ruff sort, ruff format, sort PY in …"
    bold_title = False
    include_docs_generation = False
    cli_available = True
    cli_hint = "python ruff-sort"

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
