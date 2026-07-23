"""Actions for Python development and code management."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.markdown import OnBeautifyMdFolder
from harrix_swiss_knife.menu_list_markdown import update_readme_list_of_commands


class OnSortRuffFmtDocsPythonCodeFolder(ActionBase):
    """Format, sort Python code and generate documentation in a selected folder.

    This action applies a comprehensive code formatting, organization and documentation
    workflow to all Python files in a user-selected directory. The process consists of:

    1. Running `ruff check --select I --fix` to organize and standardize imports
    2. Applying ruff format to enforce consistent code style and formatting
    3. Using a custom sorting function (`h.py.sort_py_code`) to organize code elements
       such as classes, methods, and functions in a consistent order
    4. Formatting Markdown inside Python docstrings (`h.py.PyDocstringFormatter`)
    5. Re-running ruff format after docstring updates
    6. Generating Markdown documentation from Python code using `h.py.generate_md_docs`
    7. Formatting generated Markdown files with the harrix-pylib formatter

    """

    icon = "🌟"
    title = "ruff sort, ruff format, sort, make docs PY in …"
    bold_title = True
    include_docs_generation: ClassVar[bool] = True
    cli_available = True
    cli_hint = "py ruff-sort-docs"

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
        apply_prose_fixes: bool = True,
        **_kwargs: Any,
    ) -> None:
        """Format, sort Python code and generate documentation in a selected folder."""
        self.apply_prose_fixes = apply_prose_fixes
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

        if not self._folder_has_python_files(self.folder_path):
            self.add_line(f"❌ {self.folder_path} is not a Python project (no .py files found)")
            if not noninteractive:
                self.show_result()
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
        - Docstring Markdown formatting runs even when docs generation is disabled.
        - If `is_include_docs_generation` is `True`, the method will generate Markdown
          documentation and format Markdown with the harrix-pylib formatter.
        - After formatting, empty folders are removed via `h.file.remove_empty_folders`
          (ignored paths such as `.git` and `.venv` are skipped).

        """
        # Sort imports and format with Ruff (single tool for both steps).
        self.add_line("🔵 Format and sort imports")
        commands = "uv run --active ruff check --select I --fix . && uv run --active ruff format"
        self.add_line(h.dev.run_command(commands, cwd=folder_path))

        # Sort Python code elements (skip per-file ruff: pipeline already runs ruff format).
        self.add_line("🔵 Sort Python code elements")
        try:
            self.add_line(
                h.file.apply_func(
                    folder_path,
                    ".py",
                    lambda filename: h.py.sort_py_code(filename, is_use_ruff_format=False),
                )
            )
        except Exception as e:
            # `h.py.sort_py_code` can fail on some syntax constructs; don't block the rest of the pipeline.
            self.add_line(f"⚠️ Skip sorting Python code elements due to error: {e!s}")

        # Format Markdown inside Python docstrings (adapted MdFormatter + D301-safe r""").
        self.add_line("🔵 Format Markdown in Python docstrings")
        apply_prose_fixes = getattr(self, "apply_prose_fixes", True)
        try:
            self.add_line(h.py.PyDocstringFormatter(apply_prose_fixes=apply_prose_fixes).format_folder(folder_path))
        except Exception as e:
            self.add_line(f"⚠️ Skip docstring Markdown formatting due to error: {e!s}")

        self.add_line("🔵 Format with Ruff after docstring updates")
        self.add_line(h.dev.run_command("uv run --active ruff format", cwd=folder_path))

        if Path(folder_path).resolve() == h.dev.get_project_root().resolve():
            self.add_line("🔵 Update README List of commands")
            self.add_line(update_readme_list_of_commands())

        if is_include_docs_generation:
            # Generate Markdown documentation
            self.add_line("🔵 Generate Markdown documentation")
            domain = f"https://github.com/{self.config['github_user']}/{Path(folder_path).parts[-1]}"
            self.add_line(h.py.generate_md_docs(folder_path, self.config["beginning_of_md_docs"], domain))

            # Format markdown files
            self.add_line("🔵 Format markdown files")
            OnBeautifyMdFolder.beautify_markdown_common(self, folder_path, is_include_summaries_and_combine=False)

        self.add_line("🔵 Remove empty folders")
        self.add_line(h.file.remove_empty_folders(folder_path))

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

    @staticmethod
    def _folder_has_python_files(folder_path: Path) -> bool:
        """Return whether `folder_path` contains any non-ignored `.py` files."""
        folder_resolved = folder_path.resolve()
        return any(
            not h.file.should_ignore_path(py_file.resolve().relative_to(folder_resolved))
            for py_file in folder_path.rglob("*.py")
        )
