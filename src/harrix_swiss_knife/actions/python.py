"""Actions for Python development and code management."""

from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.markdown import OnBeautifyMdFolder


class OnCheckPythonFolder(ActionBase):
    """Action to check all Python files in a folder for errors with Harrix rules."""

    icon = "🚧"
    title = "Check PY in …"

    _DOCSTRING_SECTION_HEADERS_REQUIRING_BLANK_LINE: set[str] = {"Args:", "Raises:", "Returns:", "Yields:"}
    _DOCSTRING_SECTION_ERROR_CODE = "HSKPYDOC001"
    _DOCSTRING_LIST_INDENT_ERROR_CODE = "HSKPYDOC002"
    _EXCLUDED_DIR_NAMES: set[str] = {
        ".venv",
        "venv",
        ".ruff_cache",
        "__pycache__",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
    }

    @ActionBase.handle_exceptions("checking Python folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_projects"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("Python folder checking thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        checker = h.py_check.PythonChecker()
        if self.folder_path is None:
            return

        errors = h.file.check_func(self.folder_path, ".py", checker)
        folder = Path(self.folder_path)
        docstring_errors: list[str] = []
        for py_file in self._iter_python_files(folder):
            docstring_errors.extend(self._check_docstring_section_blank_line_before_list(py_file))
        if docstring_errors:
            errors = (errors or []) + docstring_errors

        if errors:
            self.add_line("\n".join(errors))
            self.add_line(f"🔢 Count errors = {len(errors)}")
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")

    @ActionBase.handle_exceptions("Python folder checking thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()

    def _check_docstring_section_blank_line_before_list(self, path: Path) -> list[str]:
        """Check blank lines and list indentation in docstrings."""
        try:
            content = self._read_text_best_effort(path)
        except (OSError, UnicodeDecodeError) as e:
            return [f"{path}:1:1: {self._DOCSTRING_SECTION_ERROR_CODE} Cannot read file: {e!s}"]

        lines = content.splitlines()
        errors: list[str] = []

        for i, line in enumerate(lines):
            header = line.strip()
            if header not in self._DOCSTRING_SECTION_HEADERS_REQUIRING_BLANK_LINE:
                continue

            header_indent = line[: len(line) - len(line.lstrip())]

            # Find next non-empty line after header
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines):
                continue

            if j == i + 1 and lines[j].lstrip().startswith("-"):
                msg = f"Missing blank line after '{header}' before list"
                errors.append(f"{path}:{i + 1}:1: {self._DOCSTRING_SECTION_ERROR_CODE} {msg}")

            # Validate indentation of list items within this section:
            # First-level list items should align with the section header indentation.
            # Nested list items are allowed when they follow a list item and are indented more.
            k = j
            allowed_indents: set[str] = {header_indent}
            prev_list_indent: str | None = None
            prev_was_list_item = False
            while k < len(lines):
                current = lines[k]
                stripped = current.strip()
                if not stripped:
                    prev_was_list_item = False
                    k += 1
                    continue
                if stripped in self._DOCSTRING_SECTION_HEADERS_REQUIRING_BLANK_LINE:
                    break
                if current.lstrip().startswith("-"):
                    item_indent = current[: len(current) - len(current.lstrip())]
                    if item_indent in allowed_indents:
                        prev_list_indent = item_indent
                        prev_was_list_item = True
                    else:
                        # Permit nested list only right after a list item, and only by increasing indentation.
                        if (
                            prev_was_list_item
                            and prev_list_indent is not None
                            and len(item_indent) > len(prev_list_indent)
                        ):
                            allowed_indents.add(item_indent)
                            prev_list_indent = item_indent
                            prev_was_list_item = True
                        else:
                            msg = f"Unexpected list indentation in '{header}' section"
                            errors.append(f"{path}:{k + 1}:1: {self._DOCSTRING_LIST_INDENT_ERROR_CODE} {msg}")
                            prev_list_indent = item_indent
                            prev_was_list_item = True
                else:
                    prev_was_list_item = False
                k += 1

        return errors

    def _iter_python_files(self, folder_path: Path) -> list[Path]:
        return [p for p in folder_path.rglob("*.py") if not any(part in self._EXCLUDED_DIR_NAMES for part in p.parts)]

    @staticmethod
    def _read_text_best_effort(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8-sig")


class OnNewUvLibrary(ActionBase):
    """Create a new Python library with uv package manager.

    This action creates a new Python library using the uv package manager in a selected directory.
    The user can choose from predefined project creation directories or browse for a custom location.
    The action prompts for a library name with auto-generation option and automatically sets up
    the library structure, virtual environment, and dependencies using uv.

    The uv package manager (<https://github.com/astral-sh/uv>) is used to set up the library
    structure with the --lib flag, which creates a packaged project with src layout and py.typed
    marker for type hints. The library is then opened in the configured editor specified in
    the application settings.

    Libraries are intended to be built and distributed, e.g., by uploading them to PyPI.
    """

    icon = "🐍"
    title = "New uv library"

    @ActionBase.handle_exceptions("creating new uv library")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_project_creation"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        # Create auto-generator function that uses the selected folder
        def generate_auto_name() -> str:
            start_pattern = self.config["start_pattern_py_projects"]
            max_number = h.file.find_max_folder_number(str(self.folder_path), start_pattern)
            return f"{start_pattern}{f'{(max_number + 1):02}'}"

        self.library_name = self.dialogs.get_text_input_with_auto(
            "Library name",
            "Enter the name of the library (English, without spaces):",
            auto_generator=generate_auto_name,
        )
        if not self.library_name:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("creating uv library thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.library_name is None or self.folder_path is None:
            return

        library_name_clean = self.library_name.replace(" ", "-")

        # Create library using uv init --lib
        commands = f"""
            cd {self.folder_path}
            uv init --lib {library_name_clean}
            cd {library_name_clean}
            {self.config["editor"]} .
        """
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    @ActionBase.handle_exceptions("creating uv library thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnNewUvProject(ActionBase):
    """Create a new Python project with uv package manager.

    This action creates a new Python project using the uv package manager in a selected directory.
    The user can choose from predefined project creation directories or browse for a custom location.
    The action prompts for a project name with auto-generation option and automatically sets up
    the project structure, virtual environment, and dependencies using uv.

    The uv package manager (<https://github.com/astral-sh/uv>) is used to set up the project
    structure, virtual environment, and dependencies. The project is then opened in the
    configured editor specified in the application settings.
    """

    icon = "🐍"
    title = "New uv project"

    @ActionBase.handle_exceptions("creating new uv project")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_project_creation"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        # Create auto-generator function that uses the selected folder
        def generate_auto_name() -> str:
            start_pattern = self.config["start_pattern_py_projects"]
            max_number = h.file.find_max_folder_number(str(self.folder_path), start_pattern)
            return f"{start_pattern}{f'{(max_number + 1):02}'}"

        self.project_name = self.dialogs.get_text_input_with_auto(
            "Project name",
            "Enter the name of the project (English, without spaces):",
            auto_generator=generate_auto_name,
        )
        if not self.project_name:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("creating uv project thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.project_name is None or self.folder_path is None:
            return

        self.add_line(
            h.py.create_uv_new_project(
                self.project_name.replace(" ", "-"),
                str(self.folder_path),
                self.config["editor"],
                self.config["cli_commands"],
            ),
        )

    @ActionBase.handle_exceptions("creating uv project thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnPublishPythonLibrary(ActionBase):
    """Publish a new version of a Python library to PyPI.

    This action automates the process of updating, building, and publishing a Python
    library package to PyPI. The process follows these steps:

    1. Select the library to publish from configured paths
    2. Bump the minor version number of the selected library
    3. Build the package and publish it to PyPI using the provided token
    4. Commit the version changes to the library repository

    The action requires a PyPI token, which can be provided in the configuration or
    entered when prompted. The entire process is executed in background threads to
    maintain UI responsiveness.

    Note: Since dependent projects now use editable installs (uv add --editable),
    they automatically receive updates without needing to update package versions.
    """

    icon = "⚡"
    title = "Publish Python library to PyPI"

    @ActionBase.handle_exceptions("publishing Python library")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        # Select library to publish
        self.library_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_libraries"], self.config["path_github"]
        )
        if not self.library_path:
            return

        # Get PyPI token
        self.token = self.config.get("pypi_token", "")
        if not self.token:
            self.token = self.dialogs.get_text_input(
                "PyPI token", "Enter the token of the project in PyPI:", f"pypi-{'Aa' * 88}"
            )
        if not self.token:
            return

        self.library_name = self.library_path.parts[-1]
        self.start_thread(self.in_thread_01, self.thread_after_01, f"Build and publish {self.library_name}")

    @ActionBase.handle_exceptions("publishing library build thread")
    def in_thread_01(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Increase version of the library
        commands = "uv version --bump minor"
        version_output = h.dev.run_command(commands, cwd=str(self.library_path)).strip()
        self.new_version = version_output.split(" => ")[1].splitlines()[0]
        self.add_line(f"New version: {self.new_version}")

        # Build and publish
        commands = f"""
            cd {self.library_path}
            uv sync --upgrade --active
            Remove-Item -Path "{self.library_path}/dist/*" -Recurse -Force -ErrorAction SilentlyContinue
            uv build
            uv publish --token {self.token}
            git add pyproject.toml
            git add uv.lock
            git commit -m "🚀 Build version {self.new_version}" """
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    @ActionBase.handle_exceptions("publishing library thread completion")
    def thread_after_01(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_01(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnSortIsortFmtDocsPythonCodeFolder(ActionBase):
    """Format, sort Python code and generate documentation in a selected folder.

    This action applies a comprehensive code formatting, organization and documentation
    workflow to all Python files in a user-selected directory. The process consists of
    five steps:

    1. Running isort to organize and standardize imports
    2. Applying ruff format to enforce consistent code style and formatting
    3. Using a custom sorting function (`h.py.sort_py_code`) to organize code elements
       such as classes, methods, and functions in a consistent order
    4. Generating Markdown documentation from Python code using `h.py.generate_md_docs`
    5. Formatting generated Markdown files with prettier for consistent styling
    """

    icon = "🌟"
    title = "isort, ruff format, sort, make docs in PY files"
    bold_title = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnGetMenu action."""
        super().__init__()
        self.parent = kwargs.get("parent")

    @ActionBase.handle_exceptions("formatting and sorting Python code with docs")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_python_projects"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def format_and_sort_python_common(self, folder_path: str, *, is_include_docs_generation: bool = True) -> None:
        """Perform common formatting and sorting operations on Python files in a folder.

        This method applies a series of code formatting and organization operations to all
        Python files in the specified folder, including import sorting with isort, code
        formatting with ruff, and custom code element sorting. Optionally includes
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
          documentation and format it with prettier.

        """
        # Run isort and ruff format
        self.add_line("🔵 Format and sort imports")
        commands = "uv run --active isort . && uv run --active ruff format"
        self.add_line(h.dev.run_command(commands, cwd=folder_path))

        # Sort Python code elements
        self.add_line("🔵 Sort Python code elements")
        self.add_line(h.file.apply_func(folder_path, ".py", h.py.sort_py_code))

        # Check if folder_path is the application root
        app_root = str(Path(__file__).parent.parent.parent.parent.resolve())
        folder_path_resolved = str(Path(folder_path).resolve())
        print(folder_path_resolved, app_root)
        if folder_path_resolved == app_root and self.parent is not None:
            self.add_line("🔵 Get the list of items from this menu")
            result = self.parent.get_menu()
            self.add_line(result)

        if is_include_docs_generation:
            # Generate Markdown documentation
            self.add_line("🔵 Generate Markdown documentation")
            domain = f"https://github.com/{self.config['github_user']}/{Path(folder_path).parts[-1]}"
            self.add_line(h.py.generate_md_docs(folder_path, self.config["beginning_of_md_docs"], domain))

            # Format markdown files with prettier
            self.add_line("🔵 Format markdown files")
            OnBeautifyMdFolder.beautify_markdown_common(self, folder_path, is_include_summaries_and_combine=False)

    @ActionBase.handle_exceptions("formatting and sorting Python with docs thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.format_and_sort_python_common(str(self.folder_path), is_include_docs_generation=True)

    @ActionBase.handle_exceptions("formatting and sorting Python with docs thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnSortIsortFmtPythonCodeFolder(OnSortIsortFmtDocsPythonCodeFolder):
    """Format and sort Python code in a selected folder using multiple tools.

    This action applies a comprehensive code formatting and organization workflow to all
    Python files in a user-selected directory. The process consists of three steps:

    1. Running isort to organize and standardize imports
    2. Applying ruff format to enforce consistent code style and formatting
    3. Using a custom sorting function (`h.py.sort_py_code`) to organize code elements
       such as classes, methods, and functions in a consistent order
    """

    icon = "🌟"
    title = "isort, ruff format, sort in PY files"
    bold_title = False

    @ActionBase.handle_exceptions("formatting and sorting Python thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.format_and_sort_python_common(str(self.folder_path), is_include_docs_generation=False)

    @ActionBase.handle_exceptions("formatting and sorting Python thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
