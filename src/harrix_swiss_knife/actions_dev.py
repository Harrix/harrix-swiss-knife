from typing import Any
import harrix_pylib as h
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class OnExit(action_base.ActionBase):
    icon = "×"
    title = "Exit"

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.parent = kwargs.get("parent")

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        QApplication.quit()


class OnGetMenu(action_base.ActionBase):
    icon = "☰"
    title = "Get the list of items from this menu"

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.parent = kwargs.get("parent")

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        result = self.parent.get_menu()
        self.add_line(result)
        self.show_result()


class OnNpmInstallPackages(action_base.ActionBase):
    icon = "📥"
    title = "Install global NPM packages"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        commands = "\n".join([f"npm i -g {package}" for package in config["npm_packages"]])
        return h.dev.run_powershell_script(commands)

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast("Install completed")
        self.add_line(result)
        self.show_result()


class OnNpmUpdatePackages(action_base.ActionBase):
    icon = "📥"
    title = "Update NPM and global NPM packages"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        commands = "npm update npm -g\nnpm update -g"
        return h.dev.run_powershell_script(commands)

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast("Update completed")
        self.add_line(result)
        self.show_result()


class OnOpenConfigJson(action_base.ActionBase):
    icon = "⚙️"
    title = "Open config.json"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)
