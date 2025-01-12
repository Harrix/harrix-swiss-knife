import harrix_pylib as h
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_dev_exit(action_base.ActionBase):
    icon: str = "×"
    title: str = "Exit"

    def __init__(self, **kwargs):
        self.parent = kwargs.get("parent", None)

    def execute(self, *args, **kwargs):
        QApplication.quit()


class on_dev_get_menu(action_base.ActionBase):
    icon: str = "☰"
    title: str = "Get the list of items from this menu"

    def __init__(self, **kwargs):
        self.parent = kwargs.get("parent", None)

    def execute(self, *args, **kwargs):
        self.add_line(self.parent.get_menu())


class on_dev_open_config_json(action_base.ActionBase):
    icon: str = "⚙️"
    title: str = "Open config.json"

    def execute(self, *args, **kwargs):
        commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)
