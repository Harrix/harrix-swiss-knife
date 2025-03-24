import harrix_pylib as h
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import action_base
from harrix_swiss_knife import toast_countdown_notification

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


from PySide6.QtCore import Signal, QThread

# class on_npm_update_packages(action_base.ActionBase):
#     icon: str = "📥"
#     title: str = "Update NPM and global NPM packages"

#     def execute(self, *args, **kwargs):
#         self.show_toast("❗The process is not fast", duration=5000)
#         commands = "npm update npm -g\nnpm update -g"
#         result = h.dev.run_powershell_script(commands)
#         self.show_toast("Update completed")
#         self.show_text_textarea(result)


from PySide6.QtCore import Slot

class on_npm_update_packages(action_base.ActionBase):
    icon: str = "📥"
    title: str = "Update NPM and global NPM packages"

    def execute(self, *args, **kwargs):
        # Создаём "тост" со счётчиком
        self.toast = toast_countdown_notification.ToastCountdownNotification("Обновление NPM и глобальных пакетов...")
        self.toast.show()
        self.toast.start_countdown()

        # Готовим команды
        commands = "npm update npm -g\nnpm update -g"

        # Создаём поток-воркер
        class Worker(QThread):
            finished = Signal(str)  # Сигнал, который вернёт результат скрипта

            def __init__(self, commands: str, parent=None):
                super().__init__(parent)
                self.commands = commands

            def run(self):
                # Здесь выполняется длительная операция
                result = h.dev.run_powershell_script(self.commands)
                # По окончании шлём сигнал с результатом
                self.finished.emit(result)

        self.worker = Worker(commands)
        # По завершении потока вызываем наш метод
        self.worker.finished.connect(self.on_update_finished)
        # Стартуем поток
        self.worker.start()

    @Slot(str)
    def on_update_finished(self, result: str):
        """Вызывается, когда поток завершит обновление NPM."""
        # Закрываем "тост"-секундомер
        self.toast.close()

        # Показываем стандартный тост (на 1 секунду) с сообщением
        self.show_toast("Update completed", duration=2000)

        # Показываем результат в текстовом поле
        self.show_text_textarea(result)
        self.add_line(result)


class on_open_config_json(action_base.ActionBase):
    icon: str = "⚙️"
    title: str = "Open config.json"

    def execute(self, *args, **kwargs):
        commands = f"{config['editor']} {h.dev.get_project_root() / 'config/config.json'}"
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)
