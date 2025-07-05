"""Actions for Python development and code management."""

from typing import Any

import harrix_pylib as h
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import action_base


class OnExit(action_base.ActionBase):
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

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        QApplication.quit()


class OnGetMenu(action_base.ActionBase):
    """Display a list of all available menu items.

    This action retrieves and displays a complete list of all menu items
    from the parent menu, providing a convenient overview of all available
    actions in the current context.
    """

    icon = "☰"
    title = "Get the list of items from this menu"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnGetMenu action."""
        super().__init__()
        self.parent = kwargs.get("parent")

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        if self.parent is not None:
            result = self.parent.get_menu()
            self.add_line(result)
        else:
            self.add_line("❌ No parent menu available.")
        self.show_result()


class OnNpmManagePackages(action_base.ActionBase):
    """Install or update configured NPM packages globally.

    This action manages NPM packages specified in the `config["npm_packages"]` list:
    1. Updates NPM itself to the latest version
    2. Installs/updates all configured packages (npm install will update if already exists)
    3. Runs global update to ensure all packages are at latest versions

    This ensures all configured packages are present and up-to-date in the system.
    """

    icon = "📦"
    title = "Install/Update global NPM packages"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

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

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("NPM packages management completed")
        self.add_line(result)
        self.show_result()


class OnOpenConfigJson(action_base.ActionBase):
    """Open the application's configuration file.

    This action opens the `config.json` file in the configured editor,
    allowing direct viewing and editing of the application's settings
    and configuration parameters.
    """

    icon = "⚙️"
    title = "Open config.json"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        commands = f"{self.config['editor']} {h.dev.get_project_root() / self.config_path}"
        result = h.dev.run_command(commands)
        self.add_line(result)


class OnUvUpdate(action_base.ActionBase):
    """Update uv package manager to its latest version.

    This action updates the uv Python package manager to its latest version
    using the 'uv self update' command, ensuring the development environment
    has the most current version of this package management tool.
    """

    icon = "📥"
    title = "Update uv"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "uv self update"
        return h.dev.run_command(commands)

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Update completed")
        self.add_line(result)
        self.show_result()
