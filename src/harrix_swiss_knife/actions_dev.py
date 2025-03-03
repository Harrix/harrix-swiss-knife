import harrix_pylib as h
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import action_base_in_thread

config = h.dev.load_config("config/config.json")


class on_exit(action_base_in_thread.ActionBaseInThread):
    icon: str = "×"
    title: str = "Exit"

    def __init__(self, **kwargs):
        self.parent = kwargs.get("parent", None)

    def execute(self, *args, **kwargs):
        QApplication.quit()


class on_get_menu(action_base_in_thread.ActionBaseInThread):
    icon: str = "☰"
    title: str = "Get the list of items from this menu"

    def __init__(self, **kwargs):
        self.parent = kwargs.get("parent", None)

    def execute(self, *args, **kwargs):
        self.add_line(self.parent.get_menu())


class on_npm_install_packages(action_base_in_thread.ActionBaseInThread):
    icon: str = "📥"
    title: str = "Install global NPM packages"
    is_show_output = True

    def execute(self, *args, **kwargs):
        commands = "\n".join([f"npm i -g {package}" for package in config["npm_packages"]])
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)


class on_npm_update_packages(action_base_in_thread.ActionBaseInThread):
    icon: str = "📥"
    title: str = "Update NPM and global NPM packages"
    is_show_output = True

    def execute(self, *args, **kwargs):
        commands = "npm update npm -g\nnpm update -g"
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)


class on_open_config_json(action_base_in_thread.ActionBaseInThread):
    icon: str = "⚙️"
    title: str = "Open config.json"

    def execute(self, *args, **kwargs):
        commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)
