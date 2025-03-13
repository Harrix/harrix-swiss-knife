from pathlib import Path

import harrix_pylib as h
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QInputDialog, QLabel, QPlainTextEdit, QVBoxLayout

from PySide6.QtCore import QObject, Signal, QThreadPool, QRunnable
import functools

config = h.dev.load_config("config/config.json")

# Signals for thread communication
class WorkerSignals(QObject):
    result_ready = Signal(object)

# Class for executing task in a separate thread
class ThreadWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result_ready.emit(result)
        except Exception as e:
            print(f"Error in thread: {e}")

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

    def __init__(self, **kwargs):
        # Initialize attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._thread_results = {}
        self._worker_signals = {}

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

    def run_in_thread(self, func):
        """
        Decorator for functions that should be executed in a separate thread

        Usage:
        @run_in_thread
        def my_long_running_function(param1, param2):
            # Executes in a separate thread
            return result

        signal = my_long_running_function(1, 2)  # Returns signal object
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Unique identifier for this call
            call_id = id(func)

            # Create signals if not already created
            if call_id not in self._worker_signals:
                self._worker_signals[call_id] = WorkerSignals()

            # Function to execute in thread
            def thread_func():
                result = func(*args, **kwargs)
                self._thread_results[call_id] = result
                self._worker_signals[call_id].result_ready.emit(result)
                return result

            # Start in thread
            worker = ThreadWorker(thread_func)
            QThreadPool.globalInstance().start(worker)

            # Return object that can be used to get the result
            return self._worker_signals[call_id]

        return wrapper

    def on_thread_done(self, signal, callback):
        """
        Connect callback to thread completion signal

        Usage:
        signal = self.run_in_thread(my_func)(arg1, arg2)
        self.on_thread_done(signal, lambda result: self.update_ui(result))
        """
        signal.result_ready.connect(callback)

    def __call__(self, *args, **kwargs):
        # Apply the write_in_output_txt decorator to the execute method
        decorated_execute = h.dev.write_in_output_txt(is_show_output=self.is_show_output)(self.execute)

        # Save the add_line method from the decorated function
        self.add_line = decorated_execute.add_line

        # Create a wrapper for decorated_execute that adds threading functionality
        @functools.wraps(decorated_execute)
        def thread_aware_execute(*exec_args, **exec_kwargs):
            # Temporarily store the original execute method
            original_execute = self.execute

            # Call the decorated_execute with arguments
            result = decorated_execute(*exec_args, **exec_kwargs)

            # Restore the execute method
            self.execute = original_execute

            return result

        # Replace the execute method with thread_aware_execute
        self.execute = thread_aware_execute

        # Call thread_aware_execute
        return thread_aware_execute(*args, **kwargs)

    def run_code_in_thread(self, func_in_thread, on_update_complete):
        thread_signal = func_in_thread()
        self.on_thread_done(thread_signal, on_update_complete)

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
