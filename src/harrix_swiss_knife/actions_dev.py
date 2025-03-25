import harrix_pylib as h
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import action_base, toast_countdown_notification

config = h.dev.load_config("config/config.json")


class on_exit(action_base.ActionBase):
    icon: str = "×"
    title: str = "Exit"

    def __init__(self, **kwargs):
        super().__init__()
        self.parent = kwargs.get("parent", None)

    def execute(self, *args, **kwargs):
        QApplication.quit()


class on_get_menu(action_base.ActionBase):
    icon: str = "☰"
    title: str = "Get the list of items from this menu"

    def __init__(self, **kwargs):
        super().__init__()
        self.parent = kwargs.get("parent", None)

    def execute(self, *args, **kwargs):
        result = self.parent.get_menu()
        self.add_line(result)
        self.show_text_textarea(result)


class on_npm_install_packages(action_base.ActionBase):
    icon: str = "📥"
    title: str = "Install global NPM packages"

    def execute(self, *args, **kwargs):
        self.toast = toast_countdown_notification.ToastCountdownNotification(on_npm_update_packages.title)
        self.toast.show()
        self.toast.start_countdown()

        class Worker(QThread):
            finished = Signal(str)

            def __init__(self, parent=None):
                super().__init__(parent)

            def run(self):
                commands = "\n".join([f"npm i -g {package}" for package in config["npm_packages"]])
                result = h.dev.run_powershell_script(commands)
                self.finished.emit(result)

        self.worker = Worker()
        self.worker.finished.connect(self.on_update_finished)
        self.worker.start()

    @Slot(str)
    def on_update_finished(self, result: str):
        self.toast.close()

        self.show_toast("Install completed", duration=2000)

        self.show_text_textarea(result)
        self.add_line(result)


class on_npm_update_packages(action_base.ActionBase):
    icon: str = "📥"
    title: str = "Update NPM and global NPM packages"

    def execute(self, *args, **kwargs):
        self.toast = toast_countdown_notification.ToastCountdownNotification(on_npm_update_packages.title)
        self.toast.show()
        self.toast.start_countdown()

        class Worker(QThread):
            finished = Signal(str)

            def __init__(self, parent=None):
                super().__init__(parent)

            def run(self):
                commands = "npm update npm -g\nnpm update -g"
                result = h.dev.run_powershell_script(commands)
                self.finished.emit(result)

        self.worker = Worker()
        self.worker.finished.connect(self.on_update_finished)
        self.worker.start()

    @Slot(str)
    def on_update_finished(self, result: str):
        self.toast.close()

        self.show_toast("Update completed", duration=2000)

        self.show_text_textarea(result)
        self.add_line(result)


class on_open_config_json(action_base.ActionBase):
    icon: str = "⚙️"
    title: str = "Open config.json"

    def execute(self, *args, **kwargs):
        commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)
