from pathlib import Path

import harrix_pylib as h
from PySide6.QtWidgets import QFileDialog, QInputDialog

config = h.dev.load_config("config/config.json")


class ActionBase:
    icon: str = ""
    title: str = ""
    is_show_output: bool = False

    def __init__(self, **kwargs): ...

    def __call__(self, *args, **kwargs):
        # Decorate the 'execute' method with 'write_in_output_txt'
        decorated_execute = h.dev.write_in_output_txt(is_show_output=self.is_show_output)(self.execute)
        # Save the 'add_line' method from the decorated function
        self.add_line = decorated_execute.add_line
        return decorated_execute(*args, **kwargs)

    def execute(self, *args, **kwargs):
        raise NotImplementedError("The execute method must be implemented in subclasses")

    def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        folder_path = QFileDialog.getExistingDirectory(None, title, default_path)
        if not folder_path:
            self.add_line("❌ Folder was not selected.")
            return None
        return Path(folder_path)

    def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        filename, _ = QFileDialog.getOpenFileName(None, title, default_path, filter_)
        if not filename:
            self.add_line("❌ No file was selected.")
            return None
        return Path(filename)

    def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        filename, _ = QFileDialog.getSaveFileName(None, title, default_path, filter_)
        if not filename:
            self.add_line("❌ No file was selected.")
            return None
        return Path(filename)

    def get_text_input(self, title: str, label: str) -> str | None:
        text, ok = QInputDialog.getText(None, title, label)
        if not (ok and text):
            self.add_line("❌ Text was not entered.")
            return None
        return text