"""Actions for Python development and code management."""

import tomllib  # noqa: I001
from pathlib import Path
from typing import Any

import harrix_pylib as h
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.base import ActionBase


class AboutDialog(ActionBase):
    """Show the about dialog with program information.

    This action displays a dialog window containing information about the application,
    including version, description, author, and license information.
    """

    icon = "ℹ️"  # noqa: RUF001
    title = "About"

    def _get_version_from_pyproject(self) -> str:
        """Get version from pyproject.toml file.

        Returns:
            str: Version string from pyproject.toml, or "Unknown" if not found.

        """
        try:
            pyproject_path = h.dev.get_project_root() / "pyproject.toml"
            with Path.open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "Unknown")
        except Exception as e:
            self.add_line(f"⚠️ Warning: Could not read version from pyproject.toml: {e}")
            return "Unknown"

    @ActionBase.handle_exceptions("about dialog")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        version = self._get_version_from_pyproject()

        about_info = self.show_about_dialog(
            title="About",
            app_name="harrix-swiss-knife",
            version=version,
            description=(
                "A multifunctional tool for developers.\n"
                "Includes a rich set of utilities for working with files, images,\n"
                "Python code, and more."
            ),
            author="Anton Sergienko (Harrix)",
            license_text="MIT License",
            github="https://github.com/harrix/harrix-swiss-knife",
        )

        if about_info:
            self.add_line("✅ The About window has been shown")
        else:
            self.add_line("❌ The About window has been canceled")


class OnExit(ActionBase):
    """Exit the application.

    This action terminates the current Qt application instance,
    closing all windows and ending the program execution.
    """

    icon = "×"  # noqa: RUF001
    title = "Exit"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnExit action."""
        super().__init__()
        self.parent = kwargs.get("parent")

    @ActionBase.handle_exceptions("application exit")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        QApplication.quit()


class OnNpmManagePackages(ActionBase):
    """Install or update configured NPM packages globally.

    This action manages NPM packages specified in the `config["npm_packages"]` list:
    1. Updates NPM itself to the latest version
    2. Installs/updates all configured packages (npm install will update if already exists)
    3. Runs global update to ensure all packages are at latest versions

    This ensures all configured packages are present and up-to-date in the system.
    """

    icon = "📦"
    title = "Install/Update global NPM packages"

    @ActionBase.handle_exceptions("NPM package management")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("NPM operations thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Update NPM itself first
        self.add_line("Updating NPM...")
        result = h.dev.run_command("npm update npm -g")
        self.add_line(result)

        # Install/update all configured packages
        self.add_line("Installing/updating configured packages...")
        install_commands = "\n".join([f"npm i -g {package}" for package in self.config["npm_packages"]])
        result = h.dev.run_command(install_commands)
        self.add_line(result)

        # Run global update to ensure everything is up-to-date
        self.add_line("Running global update...")
        result = h.dev.run_command("npm update -g")
        self.add_line(result)

        return "NPM packages management completed"

    @ActionBase.handle_exceptions("NPM thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("NPM packages management completed")
        self.add_line(result)
        self.show_result()


class OnOpenConfigJson(ActionBase):
    """Open the application's configuration file.

    This action opens the `config.json` file in the configured editor,
    allowing direct viewing and editing of the application's settings
    and configuration parameters.
    """

    icon = "⚙️"
    title = "Open config.json"

    @ActionBase.handle_exceptions("config file opening")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        commands = f"{self.config['editor']} {h.dev.get_project_root() / self.config_path}"
        result = h.dev.run_command(commands)
        self.add_line(result)


class OnUvUpdate(ActionBase):
    """Update uv package manager to its latest version.

    This action updates the uv Python package manager to its latest version
    using the 'uv self update' command, ensuring the development environment
    has the most current version of this package management tool.
    """

    icon = "📥"
    title = "Update uv"

    @ActionBase.handle_exceptions("uv update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("uv update thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "uv self update"
        return h.dev.run_command(commands)

    @ActionBase.handle_exceptions("uv update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Update completed")
        self.add_line(result)
        self.show_result()
