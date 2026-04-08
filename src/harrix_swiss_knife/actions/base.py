"""Base action framework for implementing executable actions with UI integration.

This module provides the ActionBase class which serves as a foundation for
implementing actions that can be executed and produce output with user interface
integrations, file operations, and threading capabilities.
"""

import threading
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Concatenate, ParamSpec, TypeVar

import harrix_pylib as h
from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import (
    QClipboard,
    QFont,
    QIcon,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import toast_countdown_notification, toast_notification
from harrix_swiss_knife.actions.dialog_service import ActionDialogService
from harrix_swiss_knife.paths import (
    get_action_output_dir,
    get_config_path_str,
    get_temp_config_path_str,
    new_action_output_file_path,
)

_output_path_local = threading.local()

# NOTE: Avoid importing app modules at runtime from here (ruff TC001/TC003).
if TYPE_CHECKING:
    from harrix_swiss_knife.action_output_bus import ActionOutputBus

# Type variables for decorators
P = ParamSpec("P")
R = TypeVar("R")
SelfT = TypeVar("SelfT")


class ActionBase(ABC):
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
    config_path = get_config_path_str()
    temp_config_path = get_temp_config_path_str()
    DEFAULT_ACTION_DIALOG_SIZE: ClassVar[QSize] = QSize(1024, 768)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the action with a temporary output file.

        Args:

        - `**kwargs`: Additional keyword arguments for customization.

        """
        self.result_lines = []
        self._output_bus: ActionOutputBus | None = kwargs.get("output_bus")
        self._action_output_dir = get_action_output_dir()
        self._action_output_dir.mkdir(parents=True, exist_ok=True)
        # Real path assigned at the start of each ``__call__`` (unique per run).
        self.file = self._action_output_dir / "pending.txt"
        self.dialogs = ActionDialogService(
            default_size=self.DEFAULT_ACTION_DIALOG_SIZE,
            add_line=self.add_line,
            show_toast=self.show_toast,
            create_emoji_icon=self.create_emoji_icon,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the action and handle the output display.

        Args:

        - `*args`: Positional arguments passed to the execute method.
        - `**kwargs`: Keyword arguments passed to the execute method.

        Returns:

        The result returned by the execute method.

        """
        self.result_lines.clear()
        self.file = new_action_output_file_path(self._action_output_dir, type(self).__name__)
        if self._output_bus is not None:
            self._output_bus.set_active_output(self.file)
        Path.open(self.file, "w", encoding="utf8").close()
        _output_path_local.file = self.file
        try:
            return self.execute(*args, **kwargs)
        finally:
            if getattr(_output_path_local, "file", None) is self.file:
                delattr(_output_path_local, "file")

    def add_line(self, line: str) -> None:
        """Add a line to the output file and print it to the console.

        Args:

        - `line` (`str`): The text line to add to the output.

        """
        with Path.open(self._write_output_path(), "a", encoding="utf8") as f:
            f.write(line + "\n")
        if self._output_bus is not None:
            self._output_bus.append_line(self._write_output_path(), line)
        print(line)
        self.result_lines.append(line)

    @property
    def config(self) -> dict:
        """Get current configuration (reloads every time)."""
        return h.dev.config_load(self.config_path)

    def create_emoji_icon(self, emoji: str, size: int = 64) -> QIcon:
        """Create an icon with the given emoji.

        Args:

        - `emoji` (`str`): The emoji to be used in the icon.
        - `size` (`int`): The size of the icon in pixels. Defaults to `64`.

        Returns:

        - `QIcon`: A QIcon object containing the emoji as an icon.

        """
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        font = QFont()
        font.setPointSize(int(size * 0.8))
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()

        return QIcon(pixmap)

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the action logic (subclasses must implement).

        Args:

        - `*args`: Positional arguments for the execution.
        - `**kwargs`: Keyword arguments for the execution.

        Returns:

        Optional value propagated from ``__call__``; most actions return ``None``.

        """
        ...

    def get_checkbox_selection(
        self,
        title: str,
        label: str,
        choices: list[str],
        default_selected: list[str] | None = None,
        *,
        enable_extension_filter: bool = False,
    ) -> list[str] | None:
        """Dialog wrapper. Prefer `self.dialogs.get_checkbox_selection()`."""
        return self.dialogs.get_checkbox_selection(
            title,
            label,
            choices,
            default_selected=default_selected,
            enable_extension_filter=enable_extension_filter,
        )

    def get_choice_from_icons(
        self, title: str, label: str, choices: list[tuple[str, str]], icon_size: int = 64
    ) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_choice_from_icons()`."""
        return self.dialogs.get_choice_from_icons(title, label, choices, icon_size)

    def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_choice_from_list()`."""
        return self.dialogs.get_choice_from_list(title, label, choices)

    def get_choice_from_list_with_descriptions(
        self, title: str, label: str, choices: list[tuple[str, str]]
    ) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_choice_from_list_with_descriptions()`."""
        return self.dialogs.get_choice_from_list_with_descriptions(title, label, choices)

    def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        """Dialog wrapper. Prefer `self.dialogs.get_existing_directory()`."""
        return self.dialogs.get_existing_directory(title, default_path)

    def get_folder_with_choice_option(self, folders_list: list[str], default_path: str) -> Path | None:
        """Dialog wrapper. Prefer `self.dialogs.get_folder_with_choice_option()`."""
        return self.dialogs.get_folder_with_choice_option(folders_list, default_path)

    def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """Dialog wrapper. Prefer `self.dialogs.get_open_filename()`."""
        return self.dialogs.get_open_filename(title, default_path, filter_)

    def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None:
        """Dialog wrapper. Prefer `self.dialogs.get_open_filenames()`."""
        return self.dialogs.get_open_filenames(title, default_path, filter_)

    def get_open_filenames_with_resize(
        self, title: str, default_path: str, filter_: str
    ) -> tuple[list[Path] | None, bool, str | None]:
        """Dialog wrapper. Prefer `self.dialogs.get_open_filenames_with_resize()`."""
        return self.dialogs.get_open_filenames_with_resize(title, default_path, filter_)

    def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """Dialog wrapper. Prefer `self.dialogs.get_save_filename()`."""
        return self.dialogs.get_save_filename(title, default_path, filter_)

    def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_text_input()`."""
        return self.dialogs.get_text_input(title, label, default_value)

    def get_text_input_with_auto(
        self, title: str, label: str, auto_generator: Callable[[], str] | None = None, auto_button_text: str = "🤖 Auto"
    ) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_text_input_with_auto()`."""
        return self.dialogs.get_text_input_with_auto(title, label, auto_generator, auto_button_text)

    def get_text_textarea(self, title: str, label: str, default_text: str | None = None) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_text_textarea()`."""
        return self.dialogs.get_text_textarea(title, label, default_text)

    def get_yes_no_question(self, title: str, message: str) -> bool:
        """Dialog wrapper. Prefer `self.dialogs.get_yes_no_question()`."""
        return self.dialogs.get_yes_no_question(title, message)

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
                    self.handle_error(e, context or func.__name__)
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
        """Dialog wrapper. Prefer `self.dialogs.show_about_dialog()`."""
        return self.dialogs.show_about_dialog(
            title=title,
            app_name=app_name,
            version=version,
            description=description,
            author=author,
            license_text=license_text,
            github=github,
        )

    def show_instructions(self, instructions: str, title: str = "Instructions") -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.show_instructions()`."""
        return self.dialogs.show_instructions(instructions, title)

    def show_result(self) -> str | None:
        """Open a dialog to display result of `execute`.

        Returns:

        - `str | None`: The displayed text, or `None` if cancelled.

        """
        return self.dialogs.show_text_multiline("\n".join(self.result_lines), "Result")

    def show_text_multiline(self, text: str, title: str = "Result") -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.show_text_multiline()`."""
        return self.dialogs.show_text_multiline(text, title)

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

            def __init__(
                self,
                work_function: Callable,
                output_path: Path,
                parent: QWidget | None = None,
            ) -> None:
                super().__init__(parent)
                self.work_function = work_function
                self._output_path = output_path

            def run(self) -> None:
                _output_path_local.file = self._output_path
                try:
                    result = self.work_function()
                    self.finished.emit(result)
                finally:
                    if getattr(_output_path_local, "file", None) is self._output_path:
                        delattr(_output_path_local, "file")

        output_path = self._write_output_path()

        # Create a wrapper for the callback function that first closes the toast
        def callback_wrapper(result: Any) -> None:
            if message:  # Only try to close if we opened one
                self.toast.close()
            # Callback runs on the main thread; another action may have changed ``self.file``.
            _output_path_local.file = output_path
            try:
                callback_function(result)
            finally:
                if getattr(_output_path_local, "file", None) is output_path:
                    delattr(_output_path_local, "file")

        if message:
            self.toast = toast_countdown_notification.ToastCountdownNotification(message)
            self.toast.show()
            self.toast.start_countdown()

        worker = WorkerForThread(work_function, output_path)
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

    def _exec_standard_dialog(
        self,
        title: str,
        build: Callable[[QDialog, QVBoxLayout], None],
        *,
        parent: QWidget | None = None,
        stretch_row: int | None = 1,
    ) -> tuple[int, QDialog]:
        return self.dialogs._exec_standard_dialog(  # noqa: SLF001
            title,
            build,
            parent=parent,
            stretch_row=stretch_row,
        )

    def _finalize_standard_dialog_geometry(
        self,
        dialog: QDialog,
        layout: QVBoxLayout,
        *,
        stretch_row: int | None = 1,
    ) -> None:
        self.dialogs._finalize_standard_dialog_geometry(  # noqa: SLF001
            dialog,
            layout,
            stretch_row=stretch_row,
        )

    def _write_output_path(self) -> Path:
        """Path for ``add_line`` on this thread (worker threads keep their run's file)."""
        override = getattr(_output_path_local, "file", None)
        return override if override is not None else self.file
