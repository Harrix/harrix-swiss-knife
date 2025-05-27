"""Actions for Python development and code management."""

import re
import time
from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class OnExtractFunctionsAndClasses(action_base.ActionBase):
    """Extract a formatted Markdown list of functions and classes from a Python file.

    This action analyzes a selected Python file and generates a Markdown-formatted list
    of all functions and classes defined within it. The output is presented in a hierarchical
    structure that makes it easy to understand the file's organization and contents.
    """

    icon = "⬇️"
    title = "Extracts list of funcs to a MD list from one PY file"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        filename = self.get_open_filename(
            "Select an Python File",
            config["path_github"],
            "Python Files (*.py);;All Files (*)",
        )
        if not filename:
            return

        result = h.py.extract_functions_and_classes(filename)
        self.add_line(result)
        self.show_result()


class OnHarrixPylib01Prepare(action_base.ActionBase):
    """Prepare the harrix-pylib repository for publication by performing multiple optimization steps.

    This action automates several preparatory tasks for the harrix-pylib package before
    it can be published to PyPI. The process consists of four main steps:

    1. Code beautification and standardization:
       - Running isort to organize imports
       - Applying ruff format to enforce consistent code style
       - Using a custom sorting function to organize code elements (classes, methods, functions)

    2. Documentation generation:
       - Creating Markdown documentation from the codebase
       - Using the GitHub repository URL as the base for documentation links
       - Applying a standardized header to documentation files

    3. Markdown formatting:
       - Using Prettier to format all Markdown files consistently

    4. Repository access:
       - Opening the GitHub repository in the default browser for final review
    """

    icon = "👩🏻‍🍳"
    title = "01 Prepare harrix-pylib"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        folder_path = Path(config["path_github"]) / "harrix-pylib"

        # Beautify the code
        commands = f"cd {folder_path}\nisort .\nruff format"
        self.add_line(h.dev.run_powershell_script(commands))
        self.add_line(h.file.apply_func(folder_path, ".py", h.py.sort_py_code))

        # Generate Markdown documentation
        domain = f"https://github.com/{config['github_user']}/{folder_path.parts[-1]}"
        result = h.py.generate_md_docs(folder_path, config["beginning_of_md_docs"], domain)
        self.add_line(result)

        # Format Markdown files using Prettier
        commands = f"cd {folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

        # Open GitHub
        result = h.dev.run_powershell_script(f"github {folder_path} ")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnHarrixPylib02Publish(action_base.ActionBase):
    """Publish a new version of harrix-pylib to PyPI and update dependent projects.

    This action automates the process of updating, building, and publishing the harrix-pylib
    package to PyPI, then updating all projects that depend on it. The process follows
    these steps:

    1. Bump the minor version number of harrix-pylib
    2. Build the package and publish it to PyPI using the provided token
    3. Commit the version changes to the harrix-pylib repository
    4. Wait for the package to be available on PyPI (20 seconds delay)
    5. Update all dependent projects (defined in self.projects) to use the new version
    6. Commit the dependency updates to each project's repository

    The action requires a PyPI token, which can be provided in the configuration or
    entered when prompted. The entire process is executed in background threads to
    maintain UI responsiveness, with each major step running in its own thread.

    This automation significantly reduces the manual work involved in publishing library
    updates and ensuring dependent projects stay synchronized with the latest version.
    """

    icon = "👷‍♂️"
    title = "02 Publish and update harrix-pylib"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.token = config["pypi_token"]
        if not self.token:
            self.token = self.get_text_input("PyPi token", "Enter the token of the project in PyPi:")
        if not self.token:
            return

        self.start_thread(self.in_thread_01, self.thread_after_01, "Increase version, build and publish")

    def in_thread_01(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.path_library = Path(config["path_github"]) / "harrix-pylib"
        self.projects = [Path(config["path_github"]) / "harrix-swiss-knife"]

        # Increase version of harrix-pylib
        commands = f"""
            cd {self.path_library}
            uv version --bump minor """
        self.new_version = h.dev.run_powershell_script(commands).strip().split(" => ")[1].splitlines()[0]

        # Build and publish
        commands = f"""
            cd {self.path_library}
            uv sync --upgrade
            Remove-Item -Path "{self.path_library}/dist/*" -Recurse -Force
            uv build
            uv publish --token {self.token}
            git add pyproject.toml
            git add uv.lock
            git commit -m "🚀 Build version {self.new_version}" """
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    def in_thread_02(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        time.sleep(self.time_waiting_seconds)

    def in_thread_03(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Update harrix-pylib in projects
        for project_path in self.projects:
            project = Path(project_path)

            commands = f"""
                cd {project}
                uv sync --upgrade
                uv sync --upgrade """
            result = h.dev.run_powershell_script(commands)
            self.add_line(result)

            # Increase version of harrix-pylib in project
            path_toml = project / "pyproject.toml"
            content = path_toml.read_text(encoding="utf8")
            pattern = self.path_library.parts[-1] + r">=(\d+)\.(\d+)"
            new_content = re.sub(pattern, lambda _: f"{self.path_library.parts[-1]}>={self.new_version}", content)
            path_toml.write_text(new_content)

            commands = f"""
                cd {project}
                uv sync --upgrade
                git add pyproject.toml
                git add uv.lock
                git commit -m "⬆️ Update {self.path_library.parts[-1]}" """
            result = h.dev.run_powershell_script(commands)
            self.add_line(result)

    def thread_after_01(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_01(). For handling the results of thread execution."""
        self.time_waiting_seconds = 20
        message = f"Wait {self.time_waiting_seconds} seconds for the package to be published."
        self.start_thread(self.in_thread_02, self.thread_after_02, message)

    def thread_after_02(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_02(). For handling the results of thread execution."""
        self.start_thread(self.in_thread_03, self.thread_after_03, "Update harrix-pylib in projects")

    def thread_after_03(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_03(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnNewUvProject(action_base.ActionBase):
    """Create a new Python project with uv package manager using automatic naming.

    This action automatically creates a new Python project using the uv package manager
    in the configured projects directory. Unlike the dialog version, this action doesn't
    prompt for a project name or location - it automatically generates a sequential
    project name (e.g., "python_project_07") based on existing projects in the directory.

    The uv package manager (<https://github.com/astral-sh/uv>) is used to set up the project
    structure, virtual environment, and dependencies. The project is then opened in the
    configured editor specified in the application settings..
    """

    icon = "🐍"
    title = "New uv project in Projects"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        path = config["path_py_projects"]
        max_project_number = h.file.find_max_folder_number(path, config["start_pattern_py_projects"])
        name_project: str = f"python_project_{f'{(max_project_number + 1):02}'}"

        self.add_line(h.py.create_uv_new_project(name_project, path, config["editor"], config["cli_commands"]))

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnNewUvProjectDialog(action_base.ActionBase):
    """Create a new Python project with uv package manager in a specified directory.

    This action guides the user through creating a new Python project using the uv package manager.
    It prompts for a project name and destination folder, then sets up a new project with the
    appropriate structure and configuration.

    The uv package manager (<https://github.com/astral-sh/uv>) is a fast, reliable Python package
    manager and resolver. This action automates the project setup process, creating the necessary
    files and directories, initializing the virtual environment, and opening the project in the
    configured editor.
    """

    icon = "🐍"
    title = "New uv project in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.project_name = self.get_text_input(
            "Project name",
            "Enter the name of the project (English, without spaces):",
        )
        if not self.project_name:
            return

        self.folder_path = self.get_existing_directory("Select Project folder", config["path_py_projects"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.add_line(
            h.py.create_uv_new_project(
                self.project_name.replace(" ", "-"),
                self.folder_path,
                config["editor"],
                config["cli_commands"],
            ),
        )

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnSortIsortFmtDocsPythonCodeFolder(action_base.ActionBase):
    """Format, sort Python code and generate documentation in a selected folder.

    This action applies a comprehensive code formatting, organization and documentation
    workflow to all Python files in a user-selected directory. The process consists of
    five steps:

    1. Running isort to organize and standardize imports
    2. Applying ruff format to enforce consistent code style and formatting
    3. Using a custom sorting function (`h.py.sort_py_code`) to organize code elements
       such as classes, methods, and functions in a consistent order
    4. Generating markdown documentation from Python code using `h.py.generate_md_docs`
    5. Formatting generated markdown files with prettier for consistent styling
    """

    icon = "⭐"
    title = "isort, ruff format, sort, make docs in PY files"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select Project folder", config["path_github"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = f"cd {self.folder_path}\nisort .\nruff format"
        self.add_line(h.dev.run_powershell_script(commands))
        self.add_line(h.file.apply_func(self.folder_path, ".py", h.py.sort_py_code))

        domain = f"https://github.com/{config['github_user']}/{self.folder_path.parts[-1]}"
        self.add_line(h.py.generate_md_docs(self.folder_path, config["beginning_of_md_docs"], domain))

        commands = f"cd {self.folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        self.add_line(h.dev.run_powershell_script(commands))

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnSortIsortFmtPythonCodeFolder(action_base.ActionBase):
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

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select Project folder", config["path_github"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = f"cd {self.folder_path}\nisort .\nruff format"
        self.add_line(h.dev.run_powershell_script(commands))
        self.add_line(h.file.apply_func(self.folder_path, ".py", h.py.sort_py_code))

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
