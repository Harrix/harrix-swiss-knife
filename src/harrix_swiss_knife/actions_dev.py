import harrix_pylib as h
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_exit(action_base.ActionBase):
    icon: str = "×"
    title: str = "Exit"

    def __init__(self, **kwargs):
        self.parent = kwargs.get("parent", None)

    def execute(self, *args, **kwargs):
        QApplication.quit()


class on_get_menu(action_base.ActionBase):
    icon: str = "☰"
    title: str = "Get the list of items from this menu"

    def __init__(self, **kwargs):
        self.parent = kwargs.get("parent", None)

    def execute(self, *args, **kwargs):
        result = self.parent.get_menu()
        self.add_line(result)
        self.show_text_textarea(result)


class on_npm_install_packages(action_base.ActionBase):
    icon: str = "📥"
    title: str = "Install global NPM packages"
    is_show_output = True

    def execute(self, *args, **kwargs):
        commands = "\n".join([f"npm i -g {package}" for package in config["npm_packages"]])
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)


class on_npm_update_packages(action_base.ActionBase):
    icon: str = "📥"
    title: str = "Update NPM and global NPM packages"

    def execute(self, *args, **kwargs):
        self.show_toast("❗The process is not fast", duration=5000)
        commands = "npm update npm -g\nnpm update -g"
        result = h.dev.run_powershell_script(commands)
        self.show_toast("Update completed")
        self.show_text_textarea(result)


class on_open_config_json(action_base.ActionBase):
    icon: str = "⚙️"
    title: str = "Open config.json"

    def execute(self, *args, **kwargs):
        commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)
