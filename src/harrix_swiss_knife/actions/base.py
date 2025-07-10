"""Base action framework for implementing executable actions with UI integration.

This module provides the ActionBase class which serves as a foundation for
implementing actions that can be executed and produce output with user interface
integrations, file operations, and threading capabilities.
"""

from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, Concatenate, NoReturn, ParamSpec, TypeVar

import harrix_pylib as h
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QClipboard, QFont, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import toast_countdown_notification, toast_notification

# Type variables for decorators
P = ParamSpec("P")
R = TypeVar("R")
SelfT = TypeVar("SelfT")


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
    config_path = "config/config.json"

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

    @property
    def config(self) -> dict:
        """Get current configuration (reloads every time)."""
        return h.dev.load_config(self.config_path)

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

    def get_checkbox_selection(
        self, title: str, label: str, choices: list[str], default_selected: list[str] | None = None
    ) -> list[str] | None:
        """Open a dialog to select multiple items from a list using checkboxes.

        Args:

        - `title` (`str`): The title of the selection dialog.
        - `label` (`str`): The label prompting the user for selection.
        - `choices` (`list[str]`): List of string options to choose from.
        - `default_selected` (`list[str] | None`): List of choices that should be selected by default.
          Defaults to `None`.

        Returns:

        - `list[str] | None`: The selected choices as a list, or `None` if cancelled.

        """
        if not choices:
            self.add_line("❌ No choices provided.")
            return None

        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.resize(500, 400)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create checkboxes for each choice
        checkboxes = []
        for choice in choices:
            checkbox = QCheckBox(choice)
            # Set larger font for the checkboxes
            font = checkbox.font()
            font.setPointSize(11)
            checkbox.setFont(font)

            # Set default selection if provided
            if default_selected and choice in default_selected:
                checkbox.setChecked(True)

            checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        # Add some spacing before buttons
        layout.addStretch()

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            selected_choices = [checkbox.text() for checkbox in checkboxes if checkbox.isChecked()]
            if not selected_choices:
                self.add_line("❌ No items were selected.")
                return None
            return selected_choices

        self.add_line("❌ Dialog was canceled.")
        return None

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
        dialog.resize(600, 400)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a list widget
        list_widget = QListWidget()

        # Set larger font for the list widget
        font = list_widget.font()
        font.setPointSize(12)
        list_widget.setFont(font)

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
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
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

    def get_folder_with_choice_option(
        self, title: str, folders_list: list[str], default_path: str, choice_text: str = "📚 Choice a folder …"
    ) -> Path | None:
        """Open a dialog to select a folder from a predefined list or browse for a new one.

        This method first shows a list of predefined folders with an option to browse
        for a different folder. If the user selects the browse option, a file dialog opens.

        Args:

        - `title` (`str`): The title for both the list dialog and file dialog.
        - `folders_list` (`list[str]`): List of predefined folder paths to choose from.
        - `default_path` (`str`): Default directory for the file dialog if browse option is selected.
        - `choice_text` (`str`): Text for the browse option. Defaults to `"📁 Choice a folder …"`.

        Returns:

        - `Path | None`: The selected folder as a `Path` object, or `None` if cancelled or no selection made.

        """
        # Add folder icon to each folder in the list for display
        display_folders = [f"📁 {folder}" for folder in folders_list]

        # Create the full list with the choice option at the end
        full_list = [*display_folders, choice_text]

        # Get user's choice from the list
        selected_folder = self.get_choice_from_list(title, "Folders", full_list)
        if not selected_folder:
            return None

        # If user selected the browse option, open file dialog
        if selected_folder == choice_text:
            return self.get_existing_directory(title, default_path)

        # Remove the folder icon from the selected folder path
        clean_folder_path = selected_folder.replace("📁 ", "", 1)
        return Path(clean_folder_path)

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

    def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        """Prompt the user for text input via a simple dialog.

        Args:

        - `title` (`str`): The title of the input dialog.
        - `label` (`str`): The label prompting the user for input.
        - `default_value` (`str | None`): Default value to pre-fill the input field. Defaults to `None`.

        Returns:

        - `str | None`: The entered text, or `None` if cancelled or empty.

        """
        text, ok = QInputDialog.getText(None, title, label, text=default_value or "")
        if not (ok and text):
            self.add_line("❌ Text was not entered.")
            return None
        return text

    def get_text_input_with_auto(
        self, title: str, label: str, auto_generator: Callable[[], str] | None = None, auto_button_text: str = "🤖 Auto"
    ) -> str | None:
        """Prompt the user for text input with an optional auto-generation button.

        Args:

        - `title` (`str`): The title of the input dialog.
        - `label` (`str`): The label prompting the user for input.
        - `auto_generator` (`Callable[[], str] | None`): Function that generates auto text. Defaults to `None`.
        - `auto_button_text` (`str`): Text for the auto-generation button. Defaults to `"🤖 Auto"`.

        Returns:

        - `str | None`: The entered text, or `None` if cancelled or empty.

        """
        if auto_generator is None:
            # Fallback to regular text input if no auto generator provided
            return self.get_text_input(title, label)

        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.resize(400, 150)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create input field with auto button layout
        input_layout = QHBoxLayout()

        line_edit = QLineEdit()
        input_layout.addWidget(line_edit)

        # Add auto button
        auto_button = QPushButton(auto_button_text)

        def on_auto_clicked() -> None:
            try:
                auto_text = auto_generator()
                line_edit.setText(auto_text)
            except Exception as e:
                self.add_line(f"❌ Error generating auto text: {e}")

        auto_button.clicked.connect(on_auto_clicked)
        input_layout.addWidget(auto_button)

        layout.addLayout(input_layout)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            text = line_edit.text().strip()
            if not text:
                self.add_line("❌ Text was not entered.")
                return None
            return text

        self.add_line("❌ Dialog was canceled.")
        return None

    def get_text_textarea(self, title: str, label: str, default_text: str | None = None) -> str | None:
        """Open a dialog for multi-line text entry.

        Args:

        - `title` (`str`): The title of the text area dialog.
        - `label` (`str`): The label prompting the user for input.
        - `default_text` (`str | None`): Optional default text to pre-fill the text area. Defaults to `None`.

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
        if default_text is not None:
            text_edit.setPlainText(default_text)
        layout.addWidget(text_edit)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            text = text_edit.toPlainText()
            if not text.strip():
                self.add_line("❌ Text was not entered.")
                return None
            return text
        self.add_line("❌ Dialog was canceled.")
        return None

    def handle_error(self, error: Exception, context: str) -> None:
        """Handle an error with context information.

        Args:

        - `error` (`Exception`): The exception that occurred.
        - `context` (`str`): Context information about where the error occurred.

        """
        error_message = f"❌ Error in {context}: {error!s}"
        self.add_line(error_message)

    @staticmethod
    def handle_exceptions(
        context: str = "",
    ) -> Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]:
        """Handle exceptions automatically in action methods.

        Args:

        - `context` (`str`): Optional context information for error messages. Defaults to `""`.

        Returns:

        - `Callable`: A decorator function that wraps methods with exception handling.

        """

        def decorator(func: Callable[Concatenate[SelfT, P], R]) -> Callable[Concatenate[SelfT, P], R | None]:
            @wraps(func)
            def wrapper(self: SelfT, *args: P.args, **kwargs: P.kwargs) -> R | None:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    self.handle_error(e, context or func.__name__)  # type: ignore # noqa: PGH003
                    return None

            return wrapper

        return decorator

    def show_about_dialog(
        self,
        title: str = "About",
        app_name: str = "Harrix Swiss Knife",
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
        license_text: str = "",
        github: str = "",
    ) -> str | None:
        """Open a dialog to display information about the program.

        Args:

        - `title` (`str`): The title of the about dialog. Defaults to `"About"`.
        - `app_name` (`str`): The name of the application. Defaults to `"Harrix Swiss Knife"`.
        - `version` (`str`): The version of the application. Defaults to `"1.0.0"`.
        - `description` (`str`): Description of the application. Defaults to `""`.
        - `author` (`str`): Author information. Defaults to `""`.
        - `license_text` (`str`): License information. Defaults to `""`.
        - `github` (`str`): Link to the GitHub repository. Defaults to `""`.

        Returns:

        - `str | None`: The displayed information text, or `None` if cancelled.

        """
        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.resize(600, 500)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Create a text browser widget
        text_browser = QTextBrowser()

        # Build the about text
        about_text = f"# {app_name}\n\n"

        if version:
            about_text += f"Version: {version}\n\n"

        if description:
            about_text += f"{description}\n\n"

        if author:
            about_text += f"Author: {author}\n\n"

        if license_text:
            about_text += f"License: {license_text}\n\n"

        if github:
            about_text += f"GitHub: <{github}>\n\n"

        # Use setPlainText to preserve multiline formatting
        text_browser.setPlainText(about_text)

        # Set a readable font
        font = QFont("JetBrains Mono", 10)
        text_browser.setFont(font)

        layout.addWidget(text_browser)

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Add a Copy button
        copy_button = QPushButton("Copy to Clipboard")

        def click_copy_button() -> None:
            QGuiApplication.clipboard().setText(about_text)
            self.show_toast("About information copied to Clipboard")

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

        if result == QDialog.DialogCode.Accepted:
            return about_text
        return None

    def show_instructions(self, instructions: str, title: str = "Instructions") -> str | None:
        """Open a dialog to display instructions with basic Markdown support.

        This method creates a dialog that displays instructions text.

        Args:

        - `instructions` (`str`): The instructions text.
        - `title` (`str`): The title of the instructions dialog. Defaults to `"Instructions"`.

        Returns:

        - `str | None`: The displayed instructions text, or `None` if cancelled.

        """
        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.resize(800, 600)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Create a text browser widget
        text_browser = QTextBrowser()
        # Use setPlainText to preserve multiline formatting
        text_browser.setPlainText(instructions)
        # Set a readable font
        font = QFont("JetBrains Mono", 10)
        text_browser.setFont(font)

        layout.addWidget(text_browser)

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Add a Copy button
        copy_button = QPushButton("Copy to Clipboard")

        def click_copy_button() -> None:
            QGuiApplication.clipboard().setText(instructions)
            self.show_toast("Instructions copied to Clipboard")

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

        if result == QDialog.DialogCode.Accepted:
            return instructions
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

        if result == QDialog.DialogCode.Accepted:
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
        clipboard.setText(text, QClipboard.Mode.Clipboard)
        self.show_toast("Copied to Clipboard")
