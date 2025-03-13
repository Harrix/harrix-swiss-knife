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
        self.add_line(self.parent.get_menu())


class on_npm_install_packages(action_base.ActionBase):
    icon: str = "📥"
    title: str = "Install global NPM packages"
    is_show_output = True

    def execute(self, *args, **kwargs):
        @self.run_in_thread
        def func_in_thread():
            commands = "\n".join([f"npm i -g {package}" for package in config["npm_packages"]])
            result = h.dev.run_powershell_script(commands)
            print("111")
            return result

        def on_update_complete(result):
            self.add_line(result)
            print("222")

        thread_signal = func_in_thread()
        self.on_thread_done(thread_signal, on_update_complete)


class on_npm_update_packages(action_base.ActionBase):
    icon: str = "📥"
    title: str = "Update NPM and global NPM packages"
    is_show_output = True

    def execute(self, *args, **kwargs):
        @self.run_in_thread
        def func_in_thread():
            commands = "npm update npm -g\nnpm update -g"
            result = h.dev.run_powershell_script(commands)
            return result

        def on_update_complete(result):
            self.add_line(result)

        thread_signal = func_in_thread()
        self.on_thread_done(thread_signal, on_update_complete)

class on_open_config_json(action_base.ActionBase):
    icon: str = "⚙️"
    title: str = "Open config.json"

    def execute(self, *args, **kwargs):
        @self.run_in_thread
        def func_in_thread():
            commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
            result = h.dev.run_powershell_script(commands)
            print("111")
            return result

        def on_update_complete(result):
            self.add_line(result)
            print("222")

        thread_signal = func_in_thread()
        self.on_thread_done(thread_signal, on_update_complete)
