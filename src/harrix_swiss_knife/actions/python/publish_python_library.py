"""Actions for Python development and code management."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


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
    title = "Publish Python library to PyPI in …"

    @ActionBase.handle_exceptions("publishing Python library")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Publish a new version of a Python library to PyPI."""
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
