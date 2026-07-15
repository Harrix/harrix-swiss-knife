---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `base.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ActionBase`](#️-class-actionbase)
  - [⚙️ Method `__call__`](#️-method-__call__)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `add_line`](#️-method-add_line)
  - [⚙️ Method `config`](#️-method-config)
  - [⚙️ Method `create_emoji_icon`](#️-method-create_emoji_icon)
  - [⚙️ Method `display_title`](#️-method-display_title)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `get_checkbox_selection`](#️-method-get_checkbox_selection)
  - [⚙️ Method `get_choice_from_icons`](#️-method-get_choice_from_icons)
  - [⚙️ Method `get_choice_from_list`](#️-method-get_choice_from_list)
  - [⚙️ Method `get_choice_from_list_with_descriptions`](#️-method-get_choice_from_list_with_descriptions)
  - [⚙️ Method `get_existing_directory`](#️-method-get_existing_directory)
  - [⚙️ Method `get_folder_with_choice_option`](#️-method-get_folder_with_choice_option)
  - [⚙️ Method `get_open_filename`](#️-method-get_open_filename)
  - [⚙️ Method `get_open_filenames`](#️-method-get_open_filenames)
  - [⚙️ Method `get_open_filenames_with_resize`](#️-method-get_open_filenames_with_resize)
  - [⚙️ Method `get_save_filename`](#️-method-get_save_filename)
  - [⚙️ Method `get_text_input`](#️-method-get_text_input)
  - [⚙️ Method `get_text_input_with_auto`](#️-method-get_text_input_with_auto)
  - [⚙️ Method `get_text_textarea`](#️-method-get_text_textarea)
  - [⚙️ Method `get_yes_no_question`](#️-method-get_yes_no_question)
  - [⚙️ Method `handle_error`](#️-method-handle_error)
  - [⚙️ Method `handle_exceptions`](#️-method-handle_exceptions)
  - [⚙️ Method `is_work_cancelled`](#️-method-is_work_cancelled)
  - [⚙️ Method `raise_if_work_cancelled`](#️-method-raise_if_work_cancelled)
  - [⚙️ Method `resolve_config_value`](#️-method-resolve_config_value)
  - [⚙️ Method `show_about_dialog`](#️-method-show_about_dialog)
  - [⚙️ Method `show_instructions`](#️-method-show_instructions)
  - [⚙️ Method `show_rename_preview`](#️-method-show_rename_preview)
  - [⚙️ Method `show_result`](#️-method-show_result)
  - [⚙️ Method `show_text_multiline`](#️-method-show_text_multiline)
  - [⚙️ Method `show_toast`](#️-method-show_toast)
  - [⚙️ Method `start_thread`](#️-method-start_thread)
  - [⚙️ Method `text_to_clipboard`](#️-method-text_to_clipboard)
  - [⚙️ Method `thread_after_show_result`](#️-method-thread_after_show_result)

</details>

## 🏛️ Class `ActionBase`

```python
class ActionBase(ABC)
```

Base class for actions that can be executed and produce output.

This class provides common functionality for actions including output management,
file operations, and user interface interactions.

Attributes:

- `icon` (`str`): Icon identifier for the action. Defaults to `""`.
- `title` (`str`): Action title. May include Markdown inline code (`` `name` ``)
  for README generation; Qt UI shows it without backticks via `display_title`.
  Defaults to `""`.
- `cli_available` (`bool`): Whether the action is available via `hsk`. Defaults to `False`.
- `cli_hint` (`str`): Short CLI example for menu tooltip. Defaults to `""`.
- `file` (`Path`): Path to the output file where results are written.

<details>
<summary>Code:</summary>

```python
class ActionBase(ABC):

    icon = ""
    title = ""
    cli_available: ClassVar[bool] = False
    cli_hint: ClassVar[str] = ""
    config_path = get_config_path_str()
    temp_config_path = get_temp_config_path_str()
    DEFAULT_ACTION_DIALOG_SIZE: ClassVar[QSize] = QSize(1024, 768)
    DEFAULT_COMPACT_ACTION_DIALOG_SIZE: ClassVar[QSize] = QSize(520, 170)

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
        self._run_started = perf_counter()
        if self._output_bus is not None:
            self._output_bus.set_active_output(self.file)
        Path.open(self.file, "w", encoding="utf8").close()
        _output_path_local.file = self.file
        try:
            return self.execute(*args, **kwargs)
        finally:
            if getattr(_output_path_local, "file", None) is self.file:
                delattr(_output_path_local, "file")

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the action with a temporary output file.

        Args:

        - `**kwargs`: Additional keyword arguments for customization.

        """
        self.result_lines = []
        self._output_bus: ActionOutputBus | None = kwargs.get("output_bus")
        self._action_output_dir = get_action_output_dir()
        self._action_output_dir.mkdir(parents=True, exist_ok=True)
        self._run_started: float | None = None
        # Real path assigned at the start of each ``__call__`` (unique per run).
        self.file = self._action_output_dir / "pending.txt"
        self.dialogs = ActionDialogService(
            default_size=self.DEFAULT_ACTION_DIALOG_SIZE,
            compact_size=self.DEFAULT_COMPACT_ACTION_DIALOG_SIZE,
            add_line=self.add_line,
            show_toast=self.show_toast,
            create_emoji_icon=self.create_emoji_icon,
        )

    def add_line(self, line: str) -> None:
        """Add a line to the output file and print it to the console.

        Args:

        - `line` (`str`): The text line to add to the output.

        """
        with Path.open(self._write_output_path(), "a", encoding="utf8") as f:
            f.write(line + "\n")
        if self._output_bus is not None:
            self._output_bus.append_line(self._write_output_path(), line)
        try:
            print(line)
        except UnicodeEncodeError:
            # Some environments (e.g., spawned CLI on Windows) may expose a non-UTF console
            # encoding (cp1252/cp866). Never fail the action because of output encoding.
            safe = line.encode("utf-8", errors="backslashreplace").decode("utf-8")
            try:
                print(safe)
            except Exception:
                # Last resort: write bytes directly if possible.
                buf = getattr(sys.stdout, "buffer", None)
                if buf is not None:
                    buf.write((safe + "\n").encode("utf-8", errors="backslashreplace"))
                    buf.flush()
        self.result_lines.append(line)

    @property
    def config(self) -> dict:
        """Get current configuration (reloads every time)."""
        return _ActionConfig(h.dev.config_load(self.config_path), self)

    def create_emoji_icon(self, emoji: str, size: int = 64) -> QIcon:
        """Create an icon with the given emoji.

        Args:

        - `emoji` (`str`): The emoji to be used in the icon.
        - `size` (`int`): The size of the icon in pixels. Defaults to `64`.

        Returns:

        - `QIcon`: A QIcon object containing the emoji as an icon.

        """
        return create_emoji_icon(emoji, size)

    @property
    def display_title(self) -> str:
        """Action title without Markdown inline-code backticks for Qt UI."""
        return strip_md_inline_code_markers(self.title)

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
        disabled_choices: list[str] | None = None,
    ) -> list[str] | None:
        """Dialog wrapper. Prefer `self.dialogs.get_checkbox_selection()`."""
        return self.dialogs.get_checkbox_selection(
            strip_md_inline_code_markers(title),
            label,
            choices,
            default_selected=default_selected,
            enable_extension_filter=enable_extension_filter,
            disabled_choices=disabled_choices,
        )

    def get_choice_from_icons(
        self, title: str, label: str, choices: list[tuple[str, str]], icon_size: int = 64
    ) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_choice_from_icons()`."""
        return self.dialogs.get_choice_from_icons(strip_md_inline_code_markers(title), label, choices, icon_size)

    def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_choice_from_list()`."""
        return self.dialogs.get_choice_from_list(strip_md_inline_code_markers(title), label, choices)

    def get_choice_from_list_with_descriptions(
        self, title: str, label: str, choices: list[tuple[str, str]]
    ) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_choice_from_list_with_descriptions()`."""
        return self.dialogs.get_choice_from_list_with_descriptions(
            strip_md_inline_code_markers(title),
            label,
            choices,
        )

    def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        """Dialog wrapper. Prefer `self.dialogs.get_existing_directory()`."""
        return self.dialogs.get_existing_directory(strip_md_inline_code_markers(title), default_path)

    def get_folder_with_choice_option(self, folders_list: list[str], default_path: str) -> Path | None:
        """Dialog wrapper. Prefer `self.dialogs.get_folder_with_choice_option()`."""
        return self.dialogs.get_folder_with_choice_option(folders_list, default_path)

    def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """Dialog wrapper. Prefer `self.dialogs.get_open_filename()`."""
        return self.dialogs.get_open_filename(strip_md_inline_code_markers(title), default_path, filter_)

    def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None:
        """Dialog wrapper. Prefer `self.dialogs.get_open_filenames()`."""
        return self.dialogs.get_open_filenames(strip_md_inline_code_markers(title), default_path, filter_)

    def get_open_filenames_with_resize(
        self, title: str, default_path: str, filter_: str
    ) -> tuple[list[Path] | None, bool, str | None]:
        """Dialog wrapper. Prefer `self.dialogs.get_open_filenames_with_resize()`."""
        return self.dialogs.get_open_filenames_with_resize(
            strip_md_inline_code_markers(title),
            default_path,
            filter_,
        )

    def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """Dialog wrapper. Prefer `self.dialogs.get_save_filename()`."""
        return self.dialogs.get_save_filename(strip_md_inline_code_markers(title), default_path, filter_)

    def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_text_input()`."""
        return self.dialogs.get_text_input(strip_md_inline_code_markers(title), label, default_value)

    def get_text_input_with_auto(
        self,
        title: str,
        label: str,
        auto_generator: Callable[[], str] | None = None,
        auto_button_text: str = "🤖 Auto",
        validator: Callable[[str], str | None] | None = None,
    ) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_text_input_with_auto()`."""
        return self.dialogs.get_text_input_with_auto(
            strip_md_inline_code_markers(title),
            label,
            auto_generator,
            auto_button_text,
            validator,
        )

    def get_text_textarea(
        self,
        title: str,
        label: str,
        default_text: str | None = None,
        **kwargs: Any,
    ) -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.get_text_textarea()`."""
        return self.dialogs.get_text_textarea(strip_md_inline_code_markers(title), label, default_text, **kwargs)

    def get_yes_no_question(self, title: str, message: str, *, default_yes: bool = False) -> bool:
        """Dialog wrapper. Prefer `self.dialogs.get_yes_no_question()`."""
        return self.dialogs.get_yes_no_question(
            strip_md_inline_code_markers(title),
            strip_md_inline_code_markers(message),
            default_yes=default_yes,
        )

    def handle_error(self, error: Exception, context: str) -> None:
        """Handle an error with context information.

        Args:

        - `error` (`Exception`): The exception that occurred.
        - `context` (`str`): Context information about where the error occurred.

        """
        error_message = f"❌ Error in {context}: {error!s}"
        logging.getLogger(__name__).error(
            "Action error in %s: %s",
            context,
            error,
            exc_info=(type(error), error, error.__traceback__),
        )
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

    def is_work_cancelled(self) -> bool:
        """Return True when the current background worker was cancelled."""
        worker = getattr(self, "_current_worker", None)
        return bool(worker is not None and getattr(worker, "should_stop", False))

    def raise_if_work_cancelled(self) -> None:
        """Raise DownloadCancelledError when the current worker was cancelled."""
        if self.is_work_cancelled():
            raise DownloadCancelledError

    def resolve_config_value(self, key: Any, value: Any) -> Any:
        """Return a config value, prompting to fix missing top-level path values."""
        if not self._config_value_needs_existing_path(key, value):
            return value

        return self._get_existing_config_path_from_user(str(key), value)

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
            title=strip_md_inline_code_markers(title),
            app_name=app_name,
            version=version,
            description=description,
            author=author,
            license_text=license_text,
            github=github,
        )

    def show_instructions(self, instructions: str, title: str = "Instructions") -> str | None:
        """Dialog wrapper. Prefer `self.dialogs.show_instructions()`."""
        return self.dialogs.show_instructions(instructions, strip_md_inline_code_markers(title))

    def show_rename_preview(self, instructions: str, *, title: str | None = None) -> bool:
        """Show rename explanation with an example; return False if the user closed the dialog."""
        return self.show_instructions(instructions, title=title or self.display_title) is not None

    def show_result(self) -> str | None:
        """Open a dialog to display result of `execute`.

        Returns:

        - `str | None`: The displayed text, or `None` if cancelled.

        """
        if not self.result_lines:
            return None

        text = "\n".join(self.result_lines).strip()
        if not text:
            return None

        title = "Result"
        if self._run_started is not None:
            elapsed_s = max(0, int(perf_counter() - self._run_started))
            minutes = elapsed_s // 60
            seconds = elapsed_s % 60
            title = f"Result — {minutes:02d}:{seconds:02d}"
        result = self.dialogs.show_text_multiline(text, title)
        if isinstance(result, tuple):
            return result[0]
        return result

    def show_text_multiline(
        self,
        text: str,
        title: str = "Result",
        **kwargs: Any,
    ) -> str | None | tuple[str | None, int]:
        """Dialog wrapper. Prefer `self.dialogs.show_text_multiline()`."""
        return self.dialogs.show_text_multiline(text, strip_md_inline_code_markers(title), **kwargs)

    def show_toast(self, message: str, duration: int = 2000) -> None:
        """Display a toast notification.

        Args:

        - `message` (`str`): The text of the message.
        - `duration` (`int`): The display duration in milliseconds. Defaults to `2000`.

        """
        toast = toast_notification.ToastNotification(
            message=strip_md_inline_code_markers(message),
            duration=duration,
        )
        toast.exec()

    def start_thread(
        self,
        work_function: Callable,
        callback_function: Callable,
        message: str = "",
        *,
        cancellable: bool = False,
    ) -> None:
        """Start a worker thread with the provided work function and callback.

        This method creates a worker thread that executes the given function
        and calls the callback function with the result when completed.

        Args:

        - `work_function` (`Callable`): Function to execute in the thread that returns a result.
        - `callback_function` (`Callable`): Function to call when thread completes, receiving the result.
        - `message` (`str`): Optional message to display in a toast notification during processing.
        - `cancellable` (`bool`): When True, show cancellable HTTP toast with close control and Esc.

        Returns:

        - `None`: This method does not return a value.

        Note:

        - The worker thread reference is stored in `self._current_worker` to prevent garbage collection.
        - Automatically closes any toast countdown notification before executing the callback.

        """
        output_path = self._write_output_path()
        ui_message = strip_md_inline_code_markers(message) if message else ""

        # Create a wrapper for the callback function that first closes the toast
        def callback_wrapper(result: Any) -> None:
            if ui_message:
                self._close_progress_toast()
            if isinstance(result, _WorkerCancelled):
                print("❌ Request cancelled by user.")
                return
            if isinstance(result, _WorkerFailure):
                self.handle_error(result.error, result.context)
                return
            # Callback runs on the main thread; another action may have changed ``self.file``.
            _output_path_local.file = output_path
            try:
                callback_function(result)
            finally:
                if getattr(_output_path_local, "file", None) is output_path:
                    delattr(_output_path_local, "file")

        if ui_message:
            if cancellable:
                self.toast = toast_cancellable_http_notification.ToastCancellableHttpNotification(ui_message)
            else:
                self.toast = toast_countdown_notification.ToastCountdownNotification(ui_message)
            self.toast.start_countdown()

        worker = _WorkerForThread(work_function, output_path)
        if cancellable and ui_message:
            self.toast.cancel_requested.connect(worker.cancel)
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

    def thread_after_show_result(self, result: Any, toast: str | None = None) -> None:  # noqa: ARG002
        """Default thread completion handler: optional toast and show_result."""
        if toast:
            self.show_toast(toast)
        self.show_result()

    def _close_progress_toast(self) -> None:
        """Close countdown or cancellable progress toast after worker completion."""
        toast = getattr(self, "toast", None)
        if toast is None:
            return
        if isinstance(toast, toast_cancellable_http_notification.ToastCancellableHttpNotification):
            toast.mark_completed()
        toast.close()

    def _config_value_needs_existing_path(self, key: Any, value: Any) -> bool:
        """Check whether a top-level config value is an existing path setting."""
        if not isinstance(key, str) or not key.startswith("path_"):
            return False
        if not isinstance(value, str):
            return False

        path_value = value.strip()
        return not path_value or not Path(path_value).expanduser().exists()

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

    def _get_existing_config_path_from_user(self, key: str, current_path: str) -> str:
        """Ask user for an existing replacement path and save it to config."""
        while True:
            new_path = self.dialogs.get_path_input(
                "Update config path",
                f'Path from config key "{key}" does not exist.\nEnter an existing path:',
                current_path,
            )
            if new_path is None:
                self.add_line(f'❌ Config path "{key}" does not exist: {current_path}')
                return current_path

            normalized_path = new_path.strip().strip("\"'")
            if not normalized_path:
                self.add_line(f'❌ Empty path is not allowed for "{key}".')
                continue

            if Path(normalized_path).expanduser().exists():
                self._save_config_value(key, normalized_path)
                self.add_line(f'Config path "{key}" updated: {normalized_path}')
                return h.dev.config_load(self.config_path).get(key, normalized_path)

            self.add_line(f"❌ Path does not exist: {normalized_path}")

    def _save_config_value(self, key: str, value: str) -> None:
        """Save a single top-level config value to config file."""
        config_path = Path(self.config_path)
        with Path.open(config_path, encoding="utf8") as f:
            config = json.load(f)

        config[key] = value

        with Path.open(config_path, "w", encoding="utf8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            f.write("\n")

    def _write_output_path(self) -> Path:
        """Path for ``add_line`` on this thread (worker threads keep their run's file)."""
        override = getattr(_output_path_local, "file", None)
        return override if override is not None else self.file
```

</details>

### ⚙️ Method `__call__`

```python
def __call__(self, *args: Any, **kwargs: Any) -> Any
```

Execute the action and handle the output display.

Args:

- `*args`: Positional arguments passed to the execute method.
- `**kwargs`: Keyword arguments passed to the execute method.

Returns:

The result returned by the execute method.

<details>
<summary>Code:</summary>

```python
def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.result_lines.clear()
        self.file = new_action_output_file_path(self._action_output_dir, type(self).__name__)
        self._run_started = perf_counter()
        if self._output_bus is not None:
            self._output_bus.set_active_output(self.file)
        Path.open(self.file, "w", encoding="utf8").close()
        _output_path_local.file = self.file
        try:
            return self.execute(*args, **kwargs)
        finally:
            if getattr(_output_path_local, "file", None) is self.file:
                delattr(_output_path_local, "file")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, **kwargs: Any) -> None
```

Initialize the action with a temporary output file.

Args:

- `**kwargs`: Additional keyword arguments for customization.

<details>
<summary>Code:</summary>

```python
def __init__(self, **kwargs: Any) -> None:
        self.result_lines = []
        self._output_bus: ActionOutputBus | None = kwargs.get("output_bus")
        self._action_output_dir = get_action_output_dir()
        self._action_output_dir.mkdir(parents=True, exist_ok=True)
        self._run_started: float | None = None
        # Real path assigned at the start of each ``__call__`` (unique per run).
        self.file = self._action_output_dir / "pending.txt"
        self.dialogs = ActionDialogService(
            default_size=self.DEFAULT_ACTION_DIALOG_SIZE,
            compact_size=self.DEFAULT_COMPACT_ACTION_DIALOG_SIZE,
            add_line=self.add_line,
            show_toast=self.show_toast,
            create_emoji_icon=self.create_emoji_icon,
        )
```

</details>

### ⚙️ Method `add_line`

```python
def add_line(self, line: str) -> None
```

Add a line to the output file and print it to the console.

Args:

- `line` (`str`): The text line to add to the output.

<details>
<summary>Code:</summary>

```python
def add_line(self, line: str) -> None:
        with Path.open(self._write_output_path(), "a", encoding="utf8") as f:
            f.write(line + "\n")
        if self._output_bus is not None:
            self._output_bus.append_line(self._write_output_path(), line)
        try:
            print(line)
        except UnicodeEncodeError:
            # Some environments (e.g., spawned CLI on Windows) may expose a non-UTF console
            # encoding (cp1252/cp866). Never fail the action because of output encoding.
            safe = line.encode("utf-8", errors="backslashreplace").decode("utf-8")
            try:
                print(safe)
            except Exception:
                # Last resort: write bytes directly if possible.
                buf = getattr(sys.stdout, "buffer", None)
                if buf is not None:
                    buf.write((safe + "\n").encode("utf-8", errors="backslashreplace"))
                    buf.flush()
        self.result_lines.append(line)
```

</details>

### ⚙️ Method `config`

```python
def config(self) -> dict
```

Get current configuration (reloads every time).

<details>
<summary>Code:</summary>

```python
def config(self) -> dict:
        return _ActionConfig(h.dev.config_load(self.config_path), self)
```

</details>

### ⚙️ Method `create_emoji_icon`

```python
def create_emoji_icon(self, emoji: str, size: int = 64) -> QIcon
```

Create an icon with the given emoji.

Args:

- `emoji` (`str`): The emoji to be used in the icon.
- `size` (`int`): The size of the icon in pixels. Defaults to `64`.

Returns:

- `QIcon`: A QIcon object containing the emoji as an icon.

<details>
<summary>Code:</summary>

```python
def create_emoji_icon(self, emoji: str, size: int = 64) -> QIcon:
        return create_emoji_icon(emoji, size)
```

</details>

### ⚙️ Method `display_title`

```python
def display_title(self) -> str
```

Action title without Markdown inline-code backticks for Qt UI.

<details>
<summary>Code:</summary>

```python
def display_title(self) -> str:
        return strip_md_inline_code_markers(self.title)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> Any
```

Execute the action logic (subclasses must implement).

Args:

- `*args`: Positional arguments for the execution.
- `**kwargs`: Keyword arguments for the execution.

Returns:

Optional value propagated from `__call__`; most actions return `None`.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> Any:
        ...
```

</details>

### ⚙️ Method `get_checkbox_selection`

```python
def get_checkbox_selection(self, title: str, label: str, choices: list[str], default_selected: list[str] | None = None) -> list[str] | None
```

Dialog wrapper. Prefer `self.dialogs.get_checkbox_selection()`.

<details>
<summary>Code:</summary>

```python
def get_checkbox_selection(
        self,
        title: str,
        label: str,
        choices: list[str],
        default_selected: list[str] | None = None,
        *,
        enable_extension_filter: bool = False,
        disabled_choices: list[str] | None = None,
    ) -> list[str] | None:
        return self.dialogs.get_checkbox_selection(
            strip_md_inline_code_markers(title),
            label,
            choices,
            default_selected=default_selected,
            enable_extension_filter=enable_extension_filter,
            disabled_choices=disabled_choices,
        )
```

</details>

### ⚙️ Method `get_choice_from_icons`

```python
def get_choice_from_icons(self, title: str, label: str, choices: list[tuple[str, str]], icon_size: int = 64) -> str | None
```

Dialog wrapper. Prefer `self.dialogs.get_choice_from_icons()`.

<details>
<summary>Code:</summary>

```python
def get_choice_from_icons(
        self, title: str, label: str, choices: list[tuple[str, str]], icon_size: int = 64
    ) -> str | None:
        return self.dialogs.get_choice_from_icons(strip_md_inline_code_markers(title), label, choices, icon_size)
```

</details>

### ⚙️ Method `get_choice_from_list`

```python
def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None
```

Dialog wrapper. Prefer `self.dialogs.get_choice_from_list()`.

<details>
<summary>Code:</summary>

```python
def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None:
        return self.dialogs.get_choice_from_list(strip_md_inline_code_markers(title), label, choices)
```

</details>

### ⚙️ Method `get_choice_from_list_with_descriptions`

```python
def get_choice_from_list_with_descriptions(self, title: str, label: str, choices: list[tuple[str, str]]) -> str | None
```

Dialog wrapper. Prefer `self.dialogs.get_choice_from_list_with_descriptions()`.

<details>
<summary>Code:</summary>

```python
def get_choice_from_list_with_descriptions(
        self, title: str, label: str, choices: list[tuple[str, str]]
    ) -> str | None:
        return self.dialogs.get_choice_from_list_with_descriptions(
            strip_md_inline_code_markers(title),
            label,
            choices,
        )
```

</details>

### ⚙️ Method `get_existing_directory`

```python
def get_existing_directory(self, title: str, default_path: str) -> Path | None
```

Dialog wrapper. Prefer `self.dialogs.get_existing_directory()`.

<details>
<summary>Code:</summary>

```python
def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        return self.dialogs.get_existing_directory(strip_md_inline_code_markers(title), default_path)
```

</details>

### ⚙️ Method `get_folder_with_choice_option`

```python
def get_folder_with_choice_option(self, folders_list: list[str], default_path: str) -> Path | None
```

Dialog wrapper. Prefer `self.dialogs.get_folder_with_choice_option()`.

<details>
<summary>Code:</summary>

```python
def get_folder_with_choice_option(self, folders_list: list[str], default_path: str) -> Path | None:
        return self.dialogs.get_folder_with_choice_option(folders_list, default_path)
```

</details>

### ⚙️ Method `get_open_filename`

```python
def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None
```

Dialog wrapper. Prefer `self.dialogs.get_open_filename()`.

<details>
<summary>Code:</summary>

```python
def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        return self.dialogs.get_open_filename(strip_md_inline_code_markers(title), default_path, filter_)
```

</details>

### ⚙️ Method `get_open_filenames`

```python
def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None
```

Dialog wrapper. Prefer `self.dialogs.get_open_filenames()`.

<details>
<summary>Code:</summary>

```python
def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None:
        return self.dialogs.get_open_filenames(strip_md_inline_code_markers(title), default_path, filter_)
```

</details>

### ⚙️ Method `get_open_filenames_with_resize`

```python
def get_open_filenames_with_resize(self, title: str, default_path: str, filter_: str) -> tuple[list[Path] | None, bool, str | None]
```

Dialog wrapper. Prefer `self.dialogs.get_open_filenames_with_resize()`.

<details>
<summary>Code:</summary>

```python
def get_open_filenames_with_resize(
        self, title: str, default_path: str, filter_: str
    ) -> tuple[list[Path] | None, bool, str | None]:
        return self.dialogs.get_open_filenames_with_resize(
            strip_md_inline_code_markers(title),
            default_path,
            filter_,
        )
```

</details>

### ⚙️ Method `get_save_filename`

```python
def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None
```

Dialog wrapper. Prefer `self.dialogs.get_save_filename()`.

<details>
<summary>Code:</summary>

```python
def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        return self.dialogs.get_save_filename(strip_md_inline_code_markers(title), default_path, filter_)
```

</details>

### ⚙️ Method `get_text_input`

```python
def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None
```

Dialog wrapper. Prefer `self.dialogs.get_text_input()`.

<details>
<summary>Code:</summary>

```python
def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        return self.dialogs.get_text_input(strip_md_inline_code_markers(title), label, default_value)
```

</details>

### ⚙️ Method `get_text_input_with_auto`

```python
def get_text_input_with_auto(self, title: str, label: str, auto_generator: Callable[[], str] | None = None, auto_button_text: str = "🤖 Auto", validator: Callable[[str], str | None] | None = None) -> str | None
```

Dialog wrapper. Prefer `self.dialogs.get_text_input_with_auto()`.

<details>
<summary>Code:</summary>

```python
def get_text_input_with_auto(
        self,
        title: str,
        label: str,
        auto_generator: Callable[[], str] | None = None,
        auto_button_text: str = "🤖 Auto",
        validator: Callable[[str], str | None] | None = None,
    ) -> str | None:
        return self.dialogs.get_text_input_with_auto(
            strip_md_inline_code_markers(title),
            label,
            auto_generator,
            auto_button_text,
            validator,
        )
```

</details>

### ⚙️ Method `get_text_textarea`

```python
def get_text_textarea(self, title: str, label: str, default_text: str | None = None, **kwargs: Any) -> str | None
```

Dialog wrapper. Prefer `self.dialogs.get_text_textarea()`.

<details>
<summary>Code:</summary>

```python
def get_text_textarea(
        self,
        title: str,
        label: str,
        default_text: str | None = None,
        **kwargs: Any,
    ) -> str | None:
        return self.dialogs.get_text_textarea(strip_md_inline_code_markers(title), label, default_text, **kwargs)
```

</details>

### ⚙️ Method `get_yes_no_question`

```python
def get_yes_no_question(self, title: str, message: str) -> bool
```

Dialog wrapper. Prefer `self.dialogs.get_yes_no_question()`.

<details>
<summary>Code:</summary>

```python
def get_yes_no_question(self, title: str, message: str, *, default_yes: bool = False) -> bool:
        return self.dialogs.get_yes_no_question(
            strip_md_inline_code_markers(title),
            strip_md_inline_code_markers(message),
            default_yes=default_yes,
        )
```

</details>

### ⚙️ Method `handle_error`

```python
def handle_error(self, error: Exception, context: str) -> None
```

Handle an error with context information.

Args:

- `error` (`Exception`): The exception that occurred.
- `context` (`str`): Context information about where the error occurred.

<details>
<summary>Code:</summary>

```python
def handle_error(self, error: Exception, context: str) -> None:
        error_message = f"❌ Error in {context}: {error!s}"
        logging.getLogger(__name__).error(
            "Action error in %s: %s",
            context,
            error,
            exc_info=(type(error), error, error.__traceback__),
        )
        self.add_line(error_message)
```

</details>

### ⚙️ Method `handle_exceptions`

```python
def handle_exceptions(context: str = "") -> Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]
```

Handle exceptions automatically in action methods.

Args:

- `context` (`str`): Optional context information for error messages. Defaults to `""`.

Returns:

- `Callable`: A decorator function that wraps methods with exception handling.

<details>
<summary>Code:</summary>

```python
def handle_exceptions(
        context: str = "",
    ) -> Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]:

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
```

</details>

### ⚙️ Method `is_work_cancelled`

```python
def is_work_cancelled(self) -> bool
```

Return True when the current background worker was cancelled.

<details>
<summary>Code:</summary>

```python
def is_work_cancelled(self) -> bool:
        worker = getattr(self, "_current_worker", None)
        return bool(worker is not None and getattr(worker, "should_stop", False))
```

</details>

### ⚙️ Method `raise_if_work_cancelled`

```python
def raise_if_work_cancelled(self) -> None
```

Raise DownloadCancelledError when the current worker was cancelled.

<details>
<summary>Code:</summary>

```python
def raise_if_work_cancelled(self) -> None:
        if self.is_work_cancelled():
            raise DownloadCancelledError
```

</details>

### ⚙️ Method `resolve_config_value`

```python
def resolve_config_value(self, key: Any, value: Any) -> Any
```

Return a config value, prompting to fix missing top-level path values.

<details>
<summary>Code:</summary>

```python
def resolve_config_value(self, key: Any, value: Any) -> Any:
        if not self._config_value_needs_existing_path(key, value):
            return value

        return self._get_existing_config_path_from_user(str(key), value)
```

</details>

### ⚙️ Method `show_about_dialog`

```python
def show_about_dialog(self, title: str = "About", app_name: str = "Harrix Swiss Knife", version: str = "1.0.0", description: str = "", author: str = "", license_text: str = "", github: str = "") -> str | None
```

Dialog wrapper. Prefer `self.dialogs.show_about_dialog()`.

<details>
<summary>Code:</summary>

```python
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
        return self.dialogs.show_about_dialog(
            title=strip_md_inline_code_markers(title),
            app_name=app_name,
            version=version,
            description=description,
            author=author,
            license_text=license_text,
            github=github,
        )
```

</details>

### ⚙️ Method `show_instructions`

```python
def show_instructions(self, instructions: str, title: str = "Instructions") -> str | None
```

Dialog wrapper. Prefer `self.dialogs.show_instructions()`.

<details>
<summary>Code:</summary>

```python
def show_instructions(self, instructions: str, title: str = "Instructions") -> str | None:
        return self.dialogs.show_instructions(instructions, strip_md_inline_code_markers(title))
```

</details>

### ⚙️ Method `show_rename_preview`

```python
def show_rename_preview(self, instructions: str) -> bool
```

Show rename explanation with an example; return False if the user closed the dialog.

<details>
<summary>Code:</summary>

```python
def show_rename_preview(self, instructions: str, *, title: str | None = None) -> bool:
        return self.show_instructions(instructions, title=title or self.display_title) is not None
```

</details>

### ⚙️ Method `show_result`

```python
def show_result(self) -> str | None
```

Open a dialog to display result of `execute`.

Returns:

- `str | None`: The displayed text, or `None` if cancelled.

<details>
<summary>Code:</summary>

```python
def show_result(self) -> str | None:
        if not self.result_lines:
            return None

        text = "\n".join(self.result_lines).strip()
        if not text:
            return None

        title = "Result"
        if self._run_started is not None:
            elapsed_s = max(0, int(perf_counter() - self._run_started))
            minutes = elapsed_s // 60
            seconds = elapsed_s % 60
            title = f"Result — {minutes:02d}:{seconds:02d}"
        result = self.dialogs.show_text_multiline(text, title)
        if isinstance(result, tuple):
            return result[0]
        return result
```

</details>

### ⚙️ Method `show_text_multiline`

```python
def show_text_multiline(self, text: str, title: str = "Result", **kwargs: Any) -> str | None | tuple[str | None, int]
```

Dialog wrapper. Prefer `self.dialogs.show_text_multiline()`.

<details>
<summary>Code:</summary>

```python
def show_text_multiline(
        self,
        text: str,
        title: str = "Result",
        **kwargs: Any,
    ) -> str | None | tuple[str | None, int]:
        return self.dialogs.show_text_multiline(text, strip_md_inline_code_markers(title), **kwargs)
```

</details>

### ⚙️ Method `show_toast`

```python
def show_toast(self, message: str, duration: int = 2000) -> None
```

Display a toast notification.

Args:

- `message` (`str`): The text of the message.
- `duration` (`int`): The display duration in milliseconds. Defaults to `2000`.

<details>
<summary>Code:</summary>

```python
def show_toast(self, message: str, duration: int = 2000) -> None:
        toast = toast_notification.ToastNotification(
            message=strip_md_inline_code_markers(message),
            duration=duration,
        )
        toast.exec()
```

</details>

### ⚙️ Method `start_thread`

```python
def start_thread(self, work_function: Callable, callback_function: Callable, message: str = "") -> None
```

Start a worker thread with the provided work function and callback.

This method creates a worker thread that executes the given function
and calls the callback function with the result when completed.

Args:

- `work_function` (`Callable`): Function to execute in the thread that returns a result.
- `callback_function` (`Callable`): Function to call when thread completes, receiving the result.
- `message` (`str`): Optional message to display in a toast notification during processing.
- `cancellable` (`bool`): When True, show cancellable HTTP toast with close control and Esc.

Returns:

- `None`: This method does not return a value.

Note:

- The worker thread reference is stored in `self._current_worker` to prevent garbage collection.
- Automatically closes any toast countdown notification before executing the callback.

<details>
<summary>Code:</summary>

```python
def start_thread(
        self,
        work_function: Callable,
        callback_function: Callable,
        message: str = "",
        *,
        cancellable: bool = False,
    ) -> None:
        output_path = self._write_output_path()
        ui_message = strip_md_inline_code_markers(message) if message else ""

        # Create a wrapper for the callback function that first closes the toast
        def callback_wrapper(result: Any) -> None:
            if ui_message:
                self._close_progress_toast()
            if isinstance(result, _WorkerCancelled):
                print("❌ Request cancelled by user.")
                return
            if isinstance(result, _WorkerFailure):
                self.handle_error(result.error, result.context)
                return
            # Callback runs on the main thread; another action may have changed ``self.file``.
            _output_path_local.file = output_path
            try:
                callback_function(result)
            finally:
                if getattr(_output_path_local, "file", None) is output_path:
                    delattr(_output_path_local, "file")

        if ui_message:
            if cancellable:
                self.toast = toast_cancellable_http_notification.ToastCancellableHttpNotification(ui_message)
            else:
                self.toast = toast_countdown_notification.ToastCountdownNotification(ui_message)
            self.toast.start_countdown()

        worker = _WorkerForThread(work_function, output_path)
        if cancellable and ui_message:
            self.toast.cancel_requested.connect(worker.cancel)
        worker.finished.connect(callback_wrapper)  # Connect to our wrapper instead
        worker.start()
        # Store reference to prevent garbage collection
        self._current_worker = worker
```

</details>

### ⚙️ Method `text_to_clipboard`

```python
def text_to_clipboard(self, text: str) -> None
```

Copy the given text to the system clipboard.

Args:

- `text` (`str`): The text to be copied to the clipboard.

Returns:

- `None`: This function does not return any value.

Note:

- This function uses `QGuiApplication` to interact with the system clipboard.

<details>
<summary>Code:</summary>

```python
def text_to_clipboard(self, text: str) -> None:
        clipboard = QApplication.clipboard()
        clipboard.setText(text, QClipboard.Mode.Clipboard)
        self.show_toast("Copied to Clipboard")
```

</details>

### ⚙️ Method `thread_after_show_result`

```python
def thread_after_show_result(self, result: Any, toast: str | None = None) -> None
```

Default thread completion handler: optional toast and show_result.

<details>
<summary>Code:</summary>

```python
def thread_after_show_result(self, result: Any, toast: str | None = None) -> None:  # noqa: ARG002
        if toast:
            self.show_toast(toast)
        self.show_result()
```

</details>
