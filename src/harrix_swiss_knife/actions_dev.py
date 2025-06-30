"""Actions for Python development and code management."""

from typing import Any

import harrix_pylib as h
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


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
        result = self.parent.get_menu()
        self.add_line(result)
        self.show_result()


class OnNpmInstallPackages(action_base.ActionBase):
    """Install configured NPM packages globally.

    This action installs all NPM packages specified in the `config["npm_packages"]`
    list as global packages, making them available system-wide for command-line
    use and other applications.
    """

    icon = "📥"
    title = "Install global NPM packages"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "\n".join([f"npm i -g {package}" for package in config["npm_packages"]])
        return h.dev.run_powershell_script(commands)

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Install completed")
        self.add_line(result)
        self.show_result()


class OnNpmUpdatePackages(action_base.ActionBase):
    """Update NPM itself and all globally installed packages.

    This action first updates the npm package manager to its latest version,
    then updates all globally installed npm packages to their latest versions,
    ensuring the development environment has the most current tools available.
    """

    icon = "📥"
    title = "Update NPM and global NPM packages"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = "npm update npm -g\nnpm update -g"
        return h.dev.run_powershell_script(commands)

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Update completed")
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
        commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
        result = h.dev.run_powershell_script(commands)
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
        return h.dev.run_powershell_script(commands)

    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Update completed")
        self.add_line(result)
        self.show_result()
