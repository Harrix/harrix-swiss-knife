"""Base action framework for implementing executable actions with UI integration.

This module provides the ActionBase class which serves as a foundation for
implementing actions that can be executed and produce output with user interface
integrations, file operations, and threading capabilities.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any, NoReturn

import harrix_pylib as h
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QClipboard, QFont, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import toast_countdown_notification, toast_notification

config = h.dev.load_config("config/config.json")


class ActionBase:
    """Base class for actions that can be executed and produce output.

    This class provides common functionality for actions including output management,
    file operations, and user interface interactions.

    Attributes:

    - `icon` (`str`): Icon identifier for the action. Defaults to `""`.
    - `title` (`str`): Display title of the action. Defaults to `""`.
    - `file` (`Path`): Path to the output file where results are written.

    """

    icon = ""
    title = ""

    def __init__(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Initialize the action with a temporary output file.

        Args:

        - `**kwargs`: Additional keyword arguments for customization.

        """
        self.result_lines = []
        temp_path = h.dev.get_project_root() / "temp"
        if not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        self.file = Path(temp_path / "output.txt")

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the action and handle the output display.

        Args:

        - `*args`: Positional arguments passed to the execute method.
        - `**kwargs`: Keyword arguments passed to the execute method.

        Returns:

        The result returned by the execute method.

        """
        self.result_lines.clear()
        Path.open(self.file, "w").close()  # create or clear output.txt
        return self.execute(*args, **kwargs)

    def add_line(self, line: str) -> None:
        """Add a line to the output file and print it to the console.

        Args:

        - `line` (`str`): The text line to add to the output.

        """
        with Path.open(self.file, "a", encoding="utf8") as f:
            f.write(line + "\n")
        print(line)
        self.result_lines.append(line)

    def execute(self, *args: Any, **kwargs: Any) -> NoReturn:
        """Execute the action logic (must be implemented by subclasses).

        Args:

        - `*args`: Positional arguments for the execution.
        - `**kwargs`: Keyword arguments for the execution.

        Raises:

        - `NotImplementedError`: When this method is not overridden in a subclass.

        """
        msg = "The execute method must be implemented in subclasses"
        raise NotImplementedError(msg)

    def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None:
        """Open a dialog to select one item from a list of choices.

        Args:

        - `title` (`str`): The title of the selection dialog.
        - `label` (`str`): The label prompting the user for selection.
        - `choices` (`list[str]`): List of string options to choose from.

        Returns:

        - `str | None`: The selected choice, or `None` if cancelled or no selection made.

        """
        if not choices:
            self.add_line("❌ No choices provided.")
            return None

        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.resize(800, 600)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a list widget
        list_widget = QListWidget()
        for choice in choices:
            item = QListWidgetItem(choice)
            list_widget.addItem(item)

        # Set the first item as selected by default if available
        if list_widget.count() > 0:
            list_widget.setCurrentRow(0)

        # Connect double-click to accept dialog
        list_widget.itemDoubleClicked.connect(dialog.accept)

        layout.addWidget(list_widget)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.Accepted:
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.text()
            self.add_line("❌ No item was selected.")
            return None

        self.add_line("❌ Dialog was canceled.")
        return None

    def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        """Open a dialog to select an existing directory.

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
        """Open a dialog to select a file to open.

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
        """Open a dialog to specify a filename for saving.

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
        """Prompt the user for text input via a simple dialog.

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
        """Open a dialog for multi-line text entry.

        Args:

        - `title` (`str`): The title of the text area dialog.
        - `label` (`str`): The label prompting the user for input.

        Returns:

        - `str | None`: The entered multi-line text, or `None` if cancelled or empty.

        """
        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.resize(1024, 768)

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
        self.add_line("❌ Dialog was canceled.")
        return None

    def show_result(self) -> str | None:
        """Open a dialog to display result of `execute`.

        Returns:

        - `str | None`: The displayed text, or `None` if cancelled.

        """
        return self.show_text_multiline("\n".join(self.result_lines), "Result")

    def show_text_multiline(self, text: str, title: str = "Result") -> str | None:
        """Open a dialog to display text with a copy button.

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

        def click_copy_button() -> None:
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
        return None

    def show_toast(self, message: str, duration: int = 2000) -> None:
        """Display a toast notification.

        Args:

        - `message` (`str`): The text of the message.
        - `duration` (`int`): The display duration in milliseconds. Defaults to `2000`.

        """
        toast = toast_notification.ToastNotification(message=message, duration=duration)
        toast.exec()

    def start_thread(self, work_function: Callable, callback_function: Callable, message: str = "") -> None:
        """Start a worker thread with the provided work function and callback.

        This method creates a worker thread that executes the given function
        and calls the callback function with the result when completed.

        Args:

        - `work_function` (`Callable`): Function to execute in the thread that returns a result.
        - `callback_function` (`Callable`): Function to call when thread completes, receiving the result.
        - `message` (`str`): Optional message to display in a toast notification during processing.

        Returns:

        - `None`: This method does not return a value.

        Note:

        - The worker thread reference is stored in `self._current_worker` to prevent garbage collection.
        - Automatically closes any toast countdown notification before executing the callback.

        """

        class WorkerForThread(QThread):
            finished = Signal(object)

            def __init__(self, work_function: Callable, parent: QWidget | None = None) -> None:
                super().__init__(parent)
                self.work_function = work_function

            def run(self) -> None:
                result = self.work_function()
                self.finished.emit(result)

        # Create a wrapper for the callback function that first closes the toast
        def callback_wrapper(result: Any) -> None:
            if message:  # Only try to close if we opened one
                self.toast.close()
            callback_function(result)

        if message:
            self.toast = toast_countdown_notification.ToastCountdownNotification(message)
            self.toast.show()
            self.toast.start_countdown()

        worker = WorkerForThread(work_function)
        worker.finished.connect(callback_wrapper)  # Connect to our wrapper instead
        worker.start()
        # Store reference to prevent garbage collection
        self._current_worker = worker

    def text_to_clipboard(self, text: str) -> None:
        """Copy the given text to the system clipboard.

        Args:

        - `text` (`str`): The text to be copied to the clipboard.

        Returns:

        - `None`: This function does not return any value.

        Note:

        - This function uses `QGuiApplication` to interact with the system clipboard.

        """
        clipboard = QApplication.clipboard()
        clipboard.setText(text, QClipboard.Clipboard)
        self.show_toast("Copied to Clipboard")
