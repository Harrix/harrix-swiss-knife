from pathlib import Path

import harrix_pylib as h
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QInputDialog, QLabel, QPlainTextEdit, QVBoxLayout

config = h.dev.load_config("config/config.json")


class ActionBase:
    """
    A base class for actions that can be executed and optionally have outputs written to a text file.

    Attributes:

    - `icon` (`str`): Path to the icon representing this action. Defaults to an empty string `""`.
    - `title` (`str`): The title of the action. Defaults to an empty string `""`.
    - `is_show_output` (`bool`): Flag to determine if output should be shown. Defaults to `False`.

    Note:

    - The `__call__` method decorates the `execute` method with `write_in_output_txt` for output handling.
    - Subclasses must implement the `execute` method to define specific behaviors.
    """

    icon: str = ""
    title: str = ""
    is_show_output: bool = False

    def __init__(self, **kwargs): ...

    def __call__(self, *args, **kwargs):
        """
        Calls the decorated `execute` method, setting up output handling if required.

        Args:

        - `*args`: Variable length argument list.
        - `**kwargs`: Arbitrary keyword arguments.

        Returns:

        - The result of the decorated `execute` method.
        """
        # Decorate the 'execute' method with 'write_in_output_txt'
        decorated_execute = h.dev.write_in_output_txt(is_show_output=self.is_show_output)(self.execute)
        # Save the 'add_line' method from the decorated function
        self.add_line = decorated_execute.add_line
        return decorated_execute(*args, **kwargs)

    def execute(self, *args, **kwargs):
        """
        Abstract method intended to be overridden by subclasses with specific action logic.

        Args:

        - `*args`: Variable length argument list.
        - `**kwargs`: Arbitrary keyword arguments.

        Raises:

        - `NotImplementedError`: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("The execute method must be implemented in subclasses")

    def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        """
        Opens a dialog to select an existing directory.

        Args:

        - `title` (`str`): The title of the dialog window.
        - `default_path` (`str`): The initial directory displayed in the dialog.

        Returns:

        - `Path | None`: The selected directory as a `Path` object, or `None` if no directory is selected.
        """
        folder_path = QFileDialog.getExistingDirectory(None, title, default_path)
        if not folder_path:
            self.add_line("❌ Folder was not selected.")
            return None
        return Path(folder_path)

    def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """
        Opens a dialog to select a file to open.

        Args:

        - `title` (`str`): The title of the dialog window.
        - `default_path` (`str`): The initial directory displayed in the dialog.
        - `filter_` (`str`): Filter for the types of files to display.

        Returns:

        - `Path | None`: The selected file as a `Path` object, or `None` if no file is selected.
        """
        filename, _ = QFileDialog.getOpenFileName(None, title, default_path, filter_)
        if not filename:
            self.add_line("❌ No file was selected.")
            return None
        return Path(filename)

    def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """
        Opens a dialog to specify a filename for saving.

        Args:

        - `title` (`str`): The title of the dialog window.
        - `default_path` (`str`): The initial directory displayed in the dialog.
        - `filter_` (`str`): Filter for the types of files to display.

        Returns:

        - `Path | None`: The specified file path as a `Path` object, or `None` if no file name is chosen.
        """
        filename, _ = QFileDialog.getSaveFileName(None, title, default_path, filter_)
        if not filename:
            self.add_line("❌ No file was selected.")
            return None
        return Path(filename)

    def get_text_input(self, title: str, label: str) -> str | None:
        """
        Prompts the user for text input via a simple dialog.

        Args:

        - `title` (`str`): The title of the input dialog.
        - `label` (`str`): The label prompting the user for input.

        Returns:

        - `str | None`: The entered text, or `None` if cancelled or empty.
        """
        text, ok = QInputDialog.getText(None, title, label)
        if not (ok and text):
            self.add_line("❌ Text was not entered.")
            return None
        return text

    def get_text_textarea(self, title: str, label: str) -> str | None:
        """
        Opens a dialog for multi-line text entry.

        Args:

        - `title` (`str`): The title of the text area dialog.
        - `label` (`str`): The label prompting the user for input.

        Returns:

        - `str | None`: The entered multi-line text, or `None` if cancelled or empty.
        """
        dialog = QDialog()
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a multi-line text field
        text_edit = QPlainTextEdit()
        layout.addWidget(text_edit)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.Accepted:
            text = text_edit.toPlainText()
            if not text.strip():
                self.add_line("❌ Text was not entered.")
                return None
            return text
        else:
            self.add_line("❌ Dialog was canceled.")
            return None
