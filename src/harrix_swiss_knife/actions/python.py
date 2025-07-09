"""Actions for Python development and code management."""

from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions import markdown_utils
from harrix_swiss_knife.actions.base import ActionBase


class OnCheckPythonFolder(ActionBase):
    """Action to check all Python files in a folder for errors with Harrix rules."""

    icon = "🚧"
    title = "Check PY in …"

    @ActionBase.handle_exceptions("checking Python folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with PY files", self.config["paths_python_projects"], self.config["path_github"]
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
        self.folder_path = self.get_folder_with_choice_option(
            "Select Project folder", self.config["paths_python_project_creation"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        # Create auto-generator function that uses the selected folder
        def generate_auto_name() -> str:
            start_pattern = self.config["start_pattern_py_projects"]
            max_number = h.file.find_max_folder_number(str(self.folder_path), start_pattern)
            return f"{start_pattern}{f'{(max_number + 1):02}'}"

        self.project_name = self.get_text_input_with_auto(
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

    icon = "👷‍♂️"
    title = "Publish Python library to PyPI"

    @ActionBase.handle_exceptions("publishing Python library")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        # Select library to publish
        self.library_path = self.get_folder_with_choice_option(
            "Select Python library to publish", self.config["paths_python_libraries"], self.config["path_github"]
        )
        if not self.library_path:
            return

        # Get PyPI token
        self.token = self.config.get("pypi_token", "")
        if not self.token:
            self.token = self.get_text_input(
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
            uv sync --upgrade
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

    icon = "⭐"
    title = "isort, ruff format, sort, make docs in PY files"
    bold_title = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnGetMenu action."""
        super().__init__()
        self.parent = kwargs.get("parent")

    @ActionBase.handle_exceptions("formatting and sorting Python code with docs")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select Project folder", self.config["paths_python_projects"], self.config["path_github"]
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

        if is_include_docs_generation:
            # Generate markdown documentation
            self.add_line("🔵 Generate markdown documentation")
            domain = f"https://github.com/{self.config['github_user']}/{Path(folder_path).parts[-1]}"
            self.add_line(h.py.generate_md_docs(folder_path, self.config["beginning_of_md_docs"], domain))

            # Format markdown files with prettier
            self.add_line("🔵 Format markdown files")
            markdown_utils.beautify_markdown_common(self, folder_path, is_include_summaries_and_combine=False)

        # Check if folder_path is the application root
        app_root = str(Path(__file__).parent.parent.parent.parent.resolve())
        folder_path_resolved = str(Path(folder_path).resolve())
        print(folder_path_resolved, app_root)
        if folder_path_resolved == app_root and self.parent is not None:
            self.add_line("🔵 Get the list of items from this menu")
            result = self.parent.get_menu()
            self.add_line(result)

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
