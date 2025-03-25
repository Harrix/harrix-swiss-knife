from pathlib import Path

import harrix_pylib as h
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)


from harrix_swiss_knife import toast_notification

config = h.dev.load_config("config/config.json")


class ActionBase:
    """
    Base class for actions that can be executed and produce output.

    This class provides common functionality for actions including output management,
    file operations, and user interface interactions.

    Attributes:

    - `icon` (`str`): Icon identifier for the action. Defaults to `""`.
    - `title` (`str`): Display title of the action. Defaults to `""`.
    - `is_show_output` (`bool`): Whether to automatically display output after execution. Defaults to `False`.
    - `file` (`Path`): Path to the output file where results are written.
    """

    icon: str = ""
    title: str = ""
    is_show_output: bool = False

    def __init__(self, **kwargs):
        """
        Initialize the action with a temporary output file.

        Args:

        - `**kwargs`: Additional keyword arguments for customization.
        """
        temp_path = h.dev.get_project_root() / "temp"
        if not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        self.file = Path(temp_path / "output.txt")

    def __call__(self, *args, **kwargs):
        """
        Execute the action and handle the output display.

        Args:

        - `*args`: Positional arguments passed to the execute method.
        - `**kwargs`: Keyword arguments passed to the execute method.

        Returns:

        The result returned by the execute method.
        """
        open(self.file, "w").close()  # create or clear
        result = self.execute(*args, **kwargs)

        if self.is_show_output:
            h.file.open_file_or_folder(self.file)
        return result

    def add_line(self, line):
        """
        Add a line to the output file and print it to the console.

        Args:

        - `line` (`str`): The text line to add to the output.
        """
        with open(self.file, "a", encoding="utf8") as f:
            f.write(line + "\n")
        print(line)

    def execute(self, *args, **kwargs):
        """
        Execute the action logic (must be implemented by subclasses).

        Args:

        - `*args`: Positional arguments for the execution.
        - `**kwargs`: Keyword arguments for the execution.

        Raises:

        - `NotImplementedError`: When this method is not overridden in a subclass.
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

    def show_text_textarea(self, text: str, title: str = "Result") -> str | None:
        """
        Opens a dialog to display text with a copy button.

        Args:
        - `text` (`str`): The text to display in the textarea.
        - `title` (`str`): The title of the text area dialog.

        Returns:
        - `str | None`: The displayed text, or `None` if cancelled.
        """
        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.resize(1024, 768)  # Set a reasonable default size

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Create a multi-line text field
        text_edit = QPlainTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)  # Make it read-only since we're just displaying text

        # Set JetBrains Mono font
        font = QFont("JetBrains Mono")
        font.setPointSize(9)
        text_edit.setFont(font)

        layout.addWidget(text_edit)

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Add a Copy button
        copy_button = QPushButton("Copy to Clipboard")

        def click_copy_button():
            QGuiApplication.clipboard().setText(text_edit.toPlainText())
            self.show_toast("Copied to Clipboard")

        copy_button.clicked.connect(click_copy_button)
        button_layout.addWidget(copy_button)

        # Add OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)

        # Add the button layout to the main layout
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.Accepted:
            return text
        else:
            return None

    def show_toast(self, message: str, duration: int = 1000):
        """
        Displays a toast notification.

        Args:

        - `message` (`str`): The text of the message.
        - `duration` (`int`): The display duration in milliseconds. Defaults to `1000`.
        """
        toast = toast_notification.ToastNotification(message=message, duration=duration)
        toast.exec()

    def text_to_clipboard(self, text: str):
        """
        Copies the given text to the system clipboard.

        Args:

        - `text` (`str`): The text to be copied to the clipboard.

        Returns:

        - `None`: This function does not return any value.

        Note:

        - This function uses `QGuiApplication` to interact with the system clipboard.
        """
        QGuiApplication.clipboard().setText(text)
        self.show_toast("Copied to Clipboard")
