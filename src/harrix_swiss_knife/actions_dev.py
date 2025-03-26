import harrix_pylib as h
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_exit(action_base.ActionBase):
    icon = "×"
    title = "Exit"

    def __init__(self, **kwargs):
        super().__init__()
        self.parent = kwargs.get("parent", None)

    def execute(self, *args, **kwargs):
        QApplication.quit()


class on_get_menu(action_base.ActionBase):
    icon = "☰"
    title = "Get the list of items from this menu"

    def __init__(self, **kwargs):
        super().__init__()
        self.parent = kwargs.get("parent", None)

    def execute(self, *args, **kwargs):
        result = self.parent.get_menu()
        self.add_line(result)
        self.show_text_textarea(result)


class on_npm_install_packages(action_base.ActionBase):
    icon = "📥"
    title = "Install global NPM packages"

    def execute(self, *args, **kwargs):
        self.show_toast_countdown(self.title)
        self.start_thread(self.in_thread, self.thread_after)

    def in_thread(self):
        commands = "\n".join([f"npm i -g {package}" for package in config["npm_packages"]])
        result = h.dev.run_powershell_script(commands)
        return result

    def thread_after(self, result):
        self.close_toast_countdown()
        self.show_toast("Install completed")
        self.show_text_textarea(result)
        self.add_line(result)


class on_npm_update_packages(action_base.ActionBase):
    icon = "📥"
    title = "Update NPM and global NPM packages"

    def execute(self, *args, **kwargs):
        self.show_toast_countdown(self.title)
        self.start_thread(self.in_thread, self.thread_after)

    def in_thread(self):
        commands = "npm update npm -g\nnpm update -g"
        result = h.dev.run_powershell_script(commands)
        return result

    def thread_after(self, result):
        self.close_toast_countdown()
        self.show_toast("Update completed")
        self.show_text_textarea(result)
        self.add_line(result)


class on_open_config_json(action_base.ActionBase):
    icon = "⚙️"
    title = "Open config.json"

    def execute(self, *args, **kwargs):
        commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)
