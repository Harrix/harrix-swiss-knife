---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `base.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ActionBase`](#%EF%B8%8F-class-actionbase)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `__call__`](#%EF%B8%8F-method-__call__)
  - [⚙️ Method `add_line`](#%EF%B8%8F-method-add_line)
  - [⚙️ Method `config`](#%EF%B8%8F-method-config)
  - [⚙️ Method `create_emoji_icon`](#%EF%B8%8F-method-create_emoji_icon)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `get_checkbox_selection`](#%EF%B8%8F-method-get_checkbox_selection)
  - [⚙️ Method `get_choice_from_icons`](#%EF%B8%8F-method-get_choice_from_icons)
  - [⚙️ Method `get_choice_from_list`](#%EF%B8%8F-method-get_choice_from_list)
  - [⚙️ Method `get_choice_from_list_with_descriptions`](#%EF%B8%8F-method-get_choice_from_list_with_descriptions)
  - [⚙️ Method `get_existing_directory`](#%EF%B8%8F-method-get_existing_directory)
  - [⚙️ Method `get_folder_with_choice_option`](#%EF%B8%8F-method-get_folder_with_choice_option)
  - [⚙️ Method `get_open_filename`](#%EF%B8%8F-method-get_open_filename)
  - [⚙️ Method `get_open_filenames`](#%EF%B8%8F-method-get_open_filenames)
  - [⚙️ Method `get_open_filenames_with_resize`](#%EF%B8%8F-method-get_open_filenames_with_resize)
  - [⚙️ Method `get_save_filename`](#%EF%B8%8F-method-get_save_filename)
  - [⚙️ Method `get_text_input`](#%EF%B8%8F-method-get_text_input)
  - [⚙️ Method `get_text_input_with_auto`](#%EF%B8%8F-method-get_text_input_with_auto)
  - [⚙️ Method `get_text_textarea`](#%EF%B8%8F-method-get_text_textarea)
  - [⚙️ Method `get_yes_no_question`](#%EF%B8%8F-method-get_yes_no_question)
  - [⚙️ Method `handle_error`](#%EF%B8%8F-method-handle_error)
  - [⚙️ Method `handle_exceptions`](#%EF%B8%8F-method-handle_exceptions)
  - [⚙️ Method `show_about_dialog`](#%EF%B8%8F-method-show_about_dialog)
  - [⚙️ Method `show_instructions`](#%EF%B8%8F-method-show_instructions)
  - [⚙️ Method `show_result`](#%EF%B8%8F-method-show_result)
  - [⚙️ Method `show_text_multiline`](#%EF%B8%8F-method-show_text_multiline)
  - [⚙️ Method `show_toast`](#%EF%B8%8F-method-show_toast)
  - [⚙️ Method `start_thread`](#%EF%B8%8F-method-start_thread)
  - [⚙️ Method `text_to_clipboard`](#%EF%B8%8F-method-text_to_clipboard)
  - [⚙️ Method `_finalize_standard_dialog_geometry`](#%EF%B8%8F-method-_finalize_standard_dialog_geometry)
  - [⚙️ Method `_write_output_path`](#%EF%B8%8F-method-_write_output_path)
- [🏛️ Class `ChoiceWithDescriptionDelegate`](#%EF%B8%8F-class-choicewithdescriptiondelegate)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🏛️ Class `DragDropFileDialog`](#%EF%B8%8F-class-dragdropfiledialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `add_files`](#%EF%B8%8F-method-add_files)
  - [⚙️ Method `clear_files`](#%EF%B8%8F-method-clear_files)
  - [⚙️ Method `dragEnterEvent`](#%EF%B8%8F-method-dragenterevent)
  - [⚙️ Method `dragLeaveEvent`](#%EF%B8%8F-method-dragleaveevent)
  - [⚙️ Method `dropEvent`](#%EF%B8%8F-method-dropevent)
  - [⚙️ Method `get_max_size`](#%EF%B8%8F-method-get_max_size)
  - [⚙️ Method `get_resize_enabled`](#%EF%B8%8F-method-get_resize_enabled)
  - [⚙️ Method `get_selected_files`](#%EF%B8%8F-method-get_selected_files)
  - [⚙️ Method `select_files`](#%EF%B8%8F-method-select_files)
  - [⚙️ Method `setup_ui`](#%EF%B8%8F-method-setup_ui)
- [🏛️ Class `_StandardActionDialog`](#%EF%B8%8F-class-_standardactiondialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)

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
- `title` (`str`): Display title of the action. Defaults to `""`.
- `file` (`Path`): Path to the output file where results are written.

<details>
<summary>Code:</summary>

```python
class ActionBase(ABC):

    icon = ""
    title = ""
    config_path = get_config_path_str()
    temp_config_path = get_temp_config_path_str()
    DEFAULT_ACTION_DIALOG_SIZE: ClassVar[QSize] = QSize(1024, 768)

    def __init__(self, **kwargs: Any) -> None:  # noqa: ARG002
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
        """Open a dialog to select multiple items from a list using checkboxes.

        Args:

        - `title` (`str`): The title of the selection dialog.
        - `label` (`str`): The label prompting the user for selection.
        - `choices` (`list[str]`): List of string options to choose from.
        - `default_selected` (`list[str] | None`): List of choices that should be selected by default.
          Defaults to `None`.
        - `enable_extension_filter` (`bool`): When True, adds a button to uncheck items by file extension.
          Defaults to `False`.

        Returns:

        - `list[str] | None`: The selected choices as a list, or `None` if cancelled.

        """
        if not choices:
            self.add_line("❌ No choices provided.")
            return None

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 200)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create a container widget for checkboxes
        checkboxes_container = QWidget()
        checkboxes_layout = QVBoxLayout(checkboxes_container)

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
            checkboxes_layout.addWidget(checkbox)

        # Add stretch to push checkboxes to the top
        checkboxes_layout.addStretch()

        # Set the container as the scroll area's widget
        scroll_area.setWidget(checkboxes_container)
        layout.addWidget(scroll_area)

        # Add Select All / Deselect All buttons
        selection_buttons_layout = QHBoxLayout()

        select_all_button = QPushButton("✅ Select All")
        deselect_all_button = QPushButton("❌ Deselect All")
        extension_filter_button = QPushButton("🧩 Select by extension…")
        extension_filter_button.setVisible(enable_extension_filter)

        def select_all() -> None:
            for checkbox in checkboxes:
                checkbox.setChecked(True)

        def deselect_all() -> None:
            for checkbox in checkboxes:
                checkbox.setChecked(False)

        def _extension_key_for_choice(choice: str) -> str:
            """Return lowercase suffix ('.py') or '' for no extension."""
            return Path(choice).suffix.lower()

        def _build_extension_stats() -> tuple[list[str], dict[str, int]]:
            """Build sorted extension list and counts."""
            counts: dict[str, int] = {}
            for choice in choices:
                ext = _extension_key_for_choice(choice)
                counts[ext] = counts.get(ext, 0) + 1

            sorted_exts = sorted(counts.keys(), key=lambda ext: (-(counts[ext]), ext))
            return sorted_exts, counts

        def select_by_extension() -> None:
            sorted_exts, counts = _build_extension_stats()
            if not sorted_exts:
                return

            ext_dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, dialog)
            ext_dialog.setWindowTitle("Select extensions")

            ext_layout = QVBoxLayout()
            ext_label = QLabel("Choose extension states: checked = select all, unchecked = deselect all, mixed = keep.")
            ext_layout.addWidget(ext_label)

            ext_scroll_area = QScrollArea()
            ext_scroll_area.setWidgetResizable(True)
            ext_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            ext_scroll_area.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 200)
            ext_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            ext_container = QWidget()
            ext_container_layout = QVBoxLayout(ext_container)

            ext_checkboxes: dict[str, QCheckBox] = {}
            for ext in sorted_exts:
                total = counts[ext]
                checked_count = sum(
                    1
                    for checkbox in checkboxes
                    if _extension_key_for_choice(checkbox.text()) == ext and checkbox.isChecked()
                )
                if checked_count == 0:
                    state = Qt.CheckState.Unchecked
                elif checked_count == total:
                    state = Qt.CheckState.Checked
                else:
                    state = Qt.CheckState.PartiallyChecked

                ext_name = ext or "(no extension)"
                ext_checkbox = QCheckBox(f"{ext_name} ({total})")
                ext_checkbox.setTristate(True)
                ext_checkbox.setCheckState(state)
                ext_checkboxes[ext] = ext_checkbox
                ext_container_layout.addWidget(ext_checkbox)

            ext_container_layout.addStretch()
            ext_scroll_area.setWidget(ext_container)
            ext_layout.addWidget(ext_scroll_area)

            ext_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            ext_buttons.accepted.connect(ext_dialog.accept)
            ext_buttons.rejected.connect(ext_dialog.reject)
            ext_layout.addWidget(ext_buttons)
            ext_dialog.setLayout(ext_layout)
            self._finalize_standard_dialog_geometry(ext_dialog, ext_layout, stretch_row=1)

            if ext_dialog.exec() != QDialog.DialogCode.Accepted:
                return

            for ext, ext_checkbox in ext_checkboxes.items():
                state = ext_checkbox.checkState()
                if state == Qt.CheckState.PartiallyChecked:
                    continue
                target_checked = state == Qt.CheckState.Checked
                for checkbox in checkboxes:
                    if _extension_key_for_choice(checkbox.text()) == ext:
                        checkbox.setChecked(target_checked)

        select_all_button.clicked.connect(select_all)
        deselect_all_button.clicked.connect(deselect_all)
        extension_filter_button.clicked.connect(select_by_extension)

        selection_buttons_layout.addWidget(select_all_button)
        selection_buttons_layout.addWidget(deselect_all_button)
        selection_buttons_layout.addWidget(extension_filter_button)
        selection_buttons_layout.addStretch()

        layout.addLayout(selection_buttons_layout)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

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

    def get_choice_from_icons(
        self, title: str, label: str, choices: list[tuple[str, str]], icon_size: int = 64
    ) -> str | None:
        """Open a dialog to select one item from a list of choices displayed as icons.

        Args:

        - `title` (`str`): The title of the selection dialog.
        - `label` (`str`): The label prompting the user for selection.
        - `choices` (`list[tuple[str, str]]`): List of tuples containing (icon_emoji, title) pairs.
        - `icon_size` (`int`): Size of icons in pixels. Defaults to `64`.

        Returns:

        - `str | None`: The selected title, or `None` if cancelled or no selection made.

        """
        if not choices:
            self.add_line("❌ No choices provided.")
            return None

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a list widget in icon mode
        list_widget = QListWidget()
        list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        list_widget.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)
        list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        list_widget.setMovement(QListWidget.Movement.Static)
        list_widget.setSpacing(16)
        list_widget.setIconSize(QSize(icon_size, icon_size))
        list_widget.setWordWrap(True)
        list_widget.setUniformItemSizes(False)
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Create items with icons
        for icon_emoji, choice_title in choices:
            item = QListWidgetItem(choice_title, list_widget)
            item.setData(Qt.ItemDataRole.UserRole, choice_title)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

            # Create icon from emoji
            icon = self.create_emoji_icon(icon_emoji, icon_size)
            item.setIcon(icon)

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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
            self.add_line("❌ No item was selected.")
            return None

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

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a list widget
        list_widget = QListWidget()
        list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        list_widget.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)

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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

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

    def get_choice_from_list_with_descriptions(
        self, title: str, label: str, choices: list[tuple[str, str]]
    ) -> str | None:
        """Open a dialog to select one item from a list of choices with descriptions.

        Args:

        - `title` (`str`): The title of the selection dialog.
        - `label` (`str`): The label prompting the user for selection.
        - `choices` (`list[tuple[str, str]]`): List of tuples containing (choice, description) pairs.

        Returns:

        - `str | None`: The selected choice, or `None` if cancelled or no selection made.

        """
        if not choices:
            self.add_line("❌ No choices provided.")
            return None

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a list widget
        list_widget = QListWidget()
        list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        list_widget.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)

        # Set up the custom delegate for better text formatting
        delegate = ChoiceWithDescriptionDelegate()
        list_widget.setItemDelegate(delegate)

        for choice, description in choices:
            # Create a custom item with choice and description
            # Format description with proper line breaks and indentation
            formatted_description = description.replace("\n", "\n  ")
            item_text = f"{choice}\n  {formatted_description}"
            item = QListWidgetItem(item_text)

            # Store the original choice text as data for easy retrieval
            item.setData(Qt.ItemDataRole.UserRole, choice)
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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            current_item = list_widget.currentItem()
            if current_item:
                # Get the original choice from the item data
                return current_item.data(Qt.ItemDataRole.UserRole)
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

    def get_folder_with_choice_option(self, folders_list: list[str], default_path: str) -> Path | None:
        """Open a dialog to select a folder from a predefined list or browse for a new one.

        This method first shows the browse option ("Select folder"), then a list of predefined folders.
        If the user selects the browse option, a file dialog opens.

        Args:

        - `folders_list` (`list[str]`): List of predefined folder paths to choose from.
        - `default_path` (`str`): Default directory for the file dialog if browse option is selected.

        Returns:

        - `Path | None`: The selected folder as a `Path` object, or `None` if cancelled or no selection made.

        """
        select_folder = "📁 Select folder …"
        # Add folder icon to each folder in the list for display
        display_folders = [f"📁 {folder}" for folder in folders_list]

        # Create the full list with the browse option first
        full_list = [select_folder, *display_folders]

        # Get user's choice from the list
        selected_folder = self.get_choice_from_list(select_folder, "Folders", full_list)
        if not selected_folder:
            return None

        # If user selected the browse option, open file dialog
        if selected_folder == select_folder:
            return self.get_existing_directory(select_folder, default_path)

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

    def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None:
        """Open a dialog to select multiple files to open with drag-and-drop support.

        Args:

        - `title` (`str`): The title of the dialog window.
        - `default_path` (`str`): The initial directory displayed in the dialog.
        - `filter_` (`str`): Filter for the types of files to display.

        Returns:

        - `list[Path] | None`: The selected files as a list of `Path` objects, or `None` if no files are selected.

        """
        dialog = DragDropFileDialog(title, default_path, filter_)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                self.add_line("❌ No files were selected.")
                return None
            return [Path(filename) for filename in filenames]
        self.add_line("❌ No files were selected.")
        return None

    def get_open_filenames_with_resize(
        self, title: str, default_path: str, filter_: str
    ) -> tuple[list[Path] | None, bool, str | None]:
        """Open a dialog to select multiple files with optional resize (max size in pixels).

        Same as get_open_filenames but adds an optional checkbox "Resize images" and a text
        field for max size in pixels. When checkbox is unchecked, no resize is applied.

        Returns:

        - `tuple[list[Path] | None, bool, str | None]`: (selected files or None if cancelled,
          resize enabled, max size string or None).

        """
        dialog = DragDropFileDialog(title, default_path, filter_, with_resize_option=True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                self.add_line("❌ No files were selected.")
                return None, False, None
            paths = [Path(f) for f in filenames]
            resize_enabled = dialog.get_resize_enabled()
            max_size = dialog.get_max_size()
            return paths, resize_enabled, max_size
        self.add_line("❌ No files were selected.")
        return None, False, None

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

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create input field with auto button layout
        input_layout = QHBoxLayout()

        line_edit = QLineEdit()
        line_edit.setMinimumHeight(32)
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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

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
        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a multi-line text field
        text_edit = QPlainTextEdit()
        text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        text_edit.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)
        if default_text is not None:
            text_edit.setPlainText(default_text)
        layout.addWidget(text_edit)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

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

    def get_yes_no_question(self, title: str, message: str) -> bool:
        """Open a yes/no question dialog.

        Args:

        - `title` (`str`): The title of the dialog window.
        - `message` (`str`): The message to display to the user.

        Returns:

        - `bool`: True if user clicked Yes, False if user clicked No or closed the dialog.

        """
        reply = message_box.question(
            None,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

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
        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Create a text browser widget
        text_browser = QTextBrowser()
        text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        text_browser.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)

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

        # Use setMarkdown to render headings, links, etc.
        text_browser.setMarkdown(about_text)
        text_browser.setOpenExternalLinks(True)

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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=0)

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
        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Create a text browser widget
        text_browser = QTextBrowser()
        text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        text_browser.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)
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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=0)

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
        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Create a multi-line text field
        text_edit = QPlainTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)  # Make it read-only since we're just displaying text
        text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        text_edit.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 120)

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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=0)

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

    def _finalize_standard_dialog_geometry(
        self,
        dialog: QDialog,
        layout: QVBoxLayout,
        *,
        stretch_row: int | None = 1,
    ) -> None:
        """Apply default 1024x768 sizing and optional stretch (same as Select file combination)."""
        target = self.DEFAULT_ACTION_DIALOG_SIZE
        if stretch_row is not None:
            layout.setStretch(stretch_row, 1)
        dialog.setMinimumSize(target)
        dialog.resize(target)

        def _enforce() -> None:
            dialog.setMinimumSize(target)
            dialog.resize(target)

        QTimer.singleShot(0, _enforce)

    def _write_output_path(self) -> Path:
        """Path for ``add_line`` on this thread (worker threads keep their run's file)."""
        override = getattr(_output_path_local, "file", None)
        return override if override is not None else self.file
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
def __init__(self, **kwargs: Any) -> None:  # noqa: ARG002
        self.result_lines = []
        self._output_bus: ActionOutputBus | None = kwargs.get("output_bus")
        self._action_output_dir = get_action_output_dir()
        self._action_output_dir.mkdir(parents=True, exist_ok=True)
        # Real path assigned at the start of each ``__call__`` (unique per run).
        self.file = self._action_output_dir / "pending.txt"
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
        print(line)
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
        return h.dev.config_load(self.config_path)
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
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        font = QFont()
        font.setPointSize(int(size * 0.8))
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()

        return QIcon(pixmap)
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

Open a dialog to select multiple items from a list using checkboxes.

Args:

- `title` (`str`): The title of the selection dialog.
- `label` (`str`): The label prompting the user for selection.
- `choices` (`list[str]`): List of string options to choose from.
- `default_selected` (`list[str] | None`): List of choices that should be selected by default.
  Defaults to `None`.
- `enable_extension_filter` (`bool`): When True, adds a button to uncheck items by file extension.
  Defaults to `False`.

Returns:

- `list[str] | None`: The selected choices as a list, or `None` if cancelled.

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
    ) -> list[str] | None:
        if not choices:
            self.add_line("❌ No choices provided.")
            return None

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 200)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create a container widget for checkboxes
        checkboxes_container = QWidget()
        checkboxes_layout = QVBoxLayout(checkboxes_container)

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
            checkboxes_layout.addWidget(checkbox)

        # Add stretch to push checkboxes to the top
        checkboxes_layout.addStretch()

        # Set the container as the scroll area's widget
        scroll_area.setWidget(checkboxes_container)
        layout.addWidget(scroll_area)

        # Add Select All / Deselect All buttons
        selection_buttons_layout = QHBoxLayout()

        select_all_button = QPushButton("✅ Select All")
        deselect_all_button = QPushButton("❌ Deselect All")
        extension_filter_button = QPushButton("🧩 Select by extension…")
        extension_filter_button.setVisible(enable_extension_filter)

        def select_all() -> None:
            for checkbox in checkboxes:
                checkbox.setChecked(True)

        def deselect_all() -> None:
            for checkbox in checkboxes:
                checkbox.setChecked(False)

        def _extension_key_for_choice(choice: str) -> str:
            """Return lowercase suffix ('.py') or '' for no extension."""
            return Path(choice).suffix.lower()

        def _build_extension_stats() -> tuple[list[str], dict[str, int]]:
            """Build sorted extension list and counts."""
            counts: dict[str, int] = {}
            for choice in choices:
                ext = _extension_key_for_choice(choice)
                counts[ext] = counts.get(ext, 0) + 1

            sorted_exts = sorted(counts.keys(), key=lambda ext: (-(counts[ext]), ext))
            return sorted_exts, counts

        def select_by_extension() -> None:
            sorted_exts, counts = _build_extension_stats()
            if not sorted_exts:
                return

            ext_dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, dialog)
            ext_dialog.setWindowTitle("Select extensions")

            ext_layout = QVBoxLayout()
            ext_label = QLabel("Choose extension states: checked = select all, unchecked = deselect all, mixed = keep.")
            ext_layout.addWidget(ext_label)

            ext_scroll_area = QScrollArea()
            ext_scroll_area.setWidgetResizable(True)
            ext_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            ext_scroll_area.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 200)
            ext_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            ext_container = QWidget()
            ext_container_layout = QVBoxLayout(ext_container)

            ext_checkboxes: dict[str, QCheckBox] = {}
            for ext in sorted_exts:
                total = counts[ext]
                checked_count = sum(
                    1
                    for checkbox in checkboxes
                    if _extension_key_for_choice(checkbox.text()) == ext and checkbox.isChecked()
                )
                if checked_count == 0:
                    state = Qt.CheckState.Unchecked
                elif checked_count == total:
                    state = Qt.CheckState.Checked
                else:
                    state = Qt.CheckState.PartiallyChecked

                ext_name = ext or "(no extension)"
                ext_checkbox = QCheckBox(f"{ext_name} ({total})")
                ext_checkbox.setTristate(True)
                ext_checkbox.setCheckState(state)
                ext_checkboxes[ext] = ext_checkbox
                ext_container_layout.addWidget(ext_checkbox)

            ext_container_layout.addStretch()
            ext_scroll_area.setWidget(ext_container)
            ext_layout.addWidget(ext_scroll_area)

            ext_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            ext_buttons.accepted.connect(ext_dialog.accept)
            ext_buttons.rejected.connect(ext_dialog.reject)
            ext_layout.addWidget(ext_buttons)
            ext_dialog.setLayout(ext_layout)
            self._finalize_standard_dialog_geometry(ext_dialog, ext_layout, stretch_row=1)

            if ext_dialog.exec() != QDialog.DialogCode.Accepted:
                return

            for ext, ext_checkbox in ext_checkboxes.items():
                state = ext_checkbox.checkState()
                if state == Qt.CheckState.PartiallyChecked:
                    continue
                target_checked = state == Qt.CheckState.Checked
                for checkbox in checkboxes:
                    if _extension_key_for_choice(checkbox.text()) == ext:
                        checkbox.setChecked(target_checked)

        select_all_button.clicked.connect(select_all)
        deselect_all_button.clicked.connect(deselect_all)
        extension_filter_button.clicked.connect(select_by_extension)

        selection_buttons_layout.addWidget(select_all_button)
        selection_buttons_layout.addWidget(deselect_all_button)
        selection_buttons_layout.addWidget(extension_filter_button)
        selection_buttons_layout.addStretch()

        layout.addLayout(selection_buttons_layout)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

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
```

</details>

### ⚙️ Method `get_choice_from_icons`

```python
def get_choice_from_icons(self, title: str, label: str, choices: list[tuple[str, str]], icon_size: int = 64) -> str | None
```

Open a dialog to select one item from a list of choices displayed as icons.

Args:

- `title` (`str`): The title of the selection dialog.
- `label` (`str`): The label prompting the user for selection.
- `choices` (`list[tuple[str, str]]`): List of tuples containing (icon_emoji, title) pairs.
- `icon_size` (`int`): Size of icons in pixels. Defaults to `64`.

Returns:

- `str | None`: The selected title, or `None` if cancelled or no selection made.

<details>
<summary>Code:</summary>

```python
def get_choice_from_icons(
        self, title: str, label: str, choices: list[tuple[str, str]], icon_size: int = 64
    ) -> str | None:
        if not choices:
            self.add_line("❌ No choices provided.")
            return None

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a list widget in icon mode
        list_widget = QListWidget()
        list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        list_widget.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)
        list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        list_widget.setMovement(QListWidget.Movement.Static)
        list_widget.setSpacing(16)
        list_widget.setIconSize(QSize(icon_size, icon_size))
        list_widget.setWordWrap(True)
        list_widget.setUniformItemSizes(False)
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Create items with icons
        for icon_emoji, choice_title in choices:
            item = QListWidgetItem(choice_title, list_widget)
            item.setData(Qt.ItemDataRole.UserRole, choice_title)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

            # Create icon from emoji
            icon = self.create_emoji_icon(icon_emoji, icon_size)
            item.setIcon(icon)

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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
            self.add_line("❌ No item was selected.")
            return None

        self.add_line("❌ Dialog was canceled.")
        return None
```

</details>

### ⚙️ Method `get_choice_from_list`

```python
def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None
```

Open a dialog to select one item from a list of choices.

Args:

- `title` (`str`): The title of the selection dialog.
- `label` (`str`): The label prompting the user for selection.
- `choices` (`list[str]`): List of string options to choose from.

Returns:

- `str | None`: The selected choice, or `None` if cancelled or no selection made.

<details>
<summary>Code:</summary>

```python
def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None:
        if not choices:
            self.add_line("❌ No choices provided.")
            return None

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a list widget
        list_widget = QListWidget()
        list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        list_widget.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)

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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

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
```

</details>

### ⚙️ Method `get_choice_from_list_with_descriptions`

```python
def get_choice_from_list_with_descriptions(self, title: str, label: str, choices: list[tuple[str, str]]) -> str | None
```

Open a dialog to select one item from a list of choices with descriptions.

Args:

- `title` (`str`): The title of the selection dialog.
- `label` (`str`): The label prompting the user for selection.
- `choices` (`list[tuple[str, str]]`): List of tuples containing (choice, description) pairs.

Returns:

- `str | None`: The selected choice, or `None` if cancelled or no selection made.

<details>
<summary>Code:</summary>

```python
def get_choice_from_list_with_descriptions(
        self, title: str, label: str, choices: list[tuple[str, str]]
    ) -> str | None:
        if not choices:
            self.add_line("❌ No choices provided.")
            return None

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a list widget
        list_widget = QListWidget()
        list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        list_widget.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)

        # Set up the custom delegate for better text formatting
        delegate = ChoiceWithDescriptionDelegate()
        list_widget.setItemDelegate(delegate)

        for choice, description in choices:
            # Create a custom item with choice and description
            # Format description with proper line breaks and indentation
            formatted_description = description.replace("\n", "\n  ")
            item_text = f"{choice}\n  {formatted_description}"
            item = QListWidgetItem(item_text)

            # Store the original choice text as data for easy retrieval
            item.setData(Qt.ItemDataRole.UserRole, choice)
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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            current_item = list_widget.currentItem()
            if current_item:
                # Get the original choice from the item data
                return current_item.data(Qt.ItemDataRole.UserRole)
            self.add_line("❌ No item was selected.")
            return None

        self.add_line("❌ Dialog was canceled.")
        return None
```

</details>

### ⚙️ Method `get_existing_directory`

```python
def get_existing_directory(self, title: str, default_path: str) -> Path | None
```

Open a dialog to select an existing directory.

Args:

- `title` (`str`): The title of the dialog window.
- `default_path` (`str`): The initial directory displayed in the dialog.

Returns:

- `Path | None`: The selected directory as a `Path` object, or `None` if no directory is selected.

<details>
<summary>Code:</summary>

```python
def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        folder_path = QFileDialog.getExistingDirectory(None, title, default_path)
        if not folder_path:
            self.add_line("❌ Folder was not selected.")
            return None
        return Path(folder_path)
```

</details>

### ⚙️ Method `get_folder_with_choice_option`

```python
def get_folder_with_choice_option(self, folders_list: list[str], default_path: str) -> Path | None
```

Open a dialog to select a folder from a predefined list or browse for a new one.

This method first shows the browse option ("Select folder"), then a list of predefined folders.
If the user selects the browse option, a file dialog opens.

Args:

- `folders_list` (`list[str]`): List of predefined folder paths to choose from.
- `default_path` (`str`): Default directory for the file dialog if browse option is selected.

Returns:

- `Path | None`: The selected folder as a `Path` object, or `None` if cancelled or no selection made.

<details>
<summary>Code:</summary>

```python
def get_folder_with_choice_option(self, folders_list: list[str], default_path: str) -> Path | None:
        select_folder = "📁 Select folder …"
        # Add folder icon to each folder in the list for display
        display_folders = [f"📁 {folder}" for folder in folders_list]

        # Create the full list with the browse option first
        full_list = [select_folder, *display_folders]

        # Get user's choice from the list
        selected_folder = self.get_choice_from_list(select_folder, "Folders", full_list)
        if not selected_folder:
            return None

        # If user selected the browse option, open file dialog
        if selected_folder == select_folder:
            return self.get_existing_directory(select_folder, default_path)

        # Remove the folder icon from the selected folder path
        clean_folder_path = selected_folder.replace("📁 ", "", 1)
        return Path(clean_folder_path)
```

</details>

### ⚙️ Method `get_open_filename`

```python
def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None
```

Open a dialog to select a file to open.

Args:

- `title` (`str`): The title of the dialog window.
- `default_path` (`str`): The initial directory displayed in the dialog.
- `filter_` (`str`): Filter for the types of files to display.

Returns:

- `Path | None`: The selected file as a `Path` object, or `None` if no file is selected.

<details>
<summary>Code:</summary>

```python
def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        filename, _ = QFileDialog.getOpenFileName(None, title, default_path, filter_)
        if not filename:
            self.add_line("❌ No file was selected.")
            return None
        return Path(filename)
```

</details>

### ⚙️ Method `get_open_filenames`

```python
def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None
```

Open a dialog to select multiple files to open with drag-and-drop support.

Args:

- `title` (`str`): The title of the dialog window.
- `default_path` (`str`): The initial directory displayed in the dialog.
- `filter_` (`str`): Filter for the types of files to display.

Returns:

- `list[Path] | None`: The selected files as a list of `Path` objects, or `None` if no files are selected.

<details>
<summary>Code:</summary>

```python
def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None:
        dialog = DragDropFileDialog(title, default_path, filter_)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                self.add_line("❌ No files were selected.")
                return None
            return [Path(filename) for filename in filenames]
        self.add_line("❌ No files were selected.")
        return None
```

</details>

### ⚙️ Method `get_open_filenames_with_resize`

```python
def get_open_filenames_with_resize(self, title: str, default_path: str, filter_: str) -> tuple[list[Path] | None, bool, str | None]
```

Open a dialog to select multiple files with optional resize (max size in pixels).

Same as get_open_filenames but adds an optional checkbox "Resize images" and a text
field for max size in pixels. When checkbox is unchecked, no resize is applied.

Returns:

- `tuple[list[Path] | None, bool, str | None]`: (selected files or None if cancelled,
  resize enabled, max size string or None).

<details>
<summary>Code:</summary>

```python
def get_open_filenames_with_resize(
        self, title: str, default_path: str, filter_: str
    ) -> tuple[list[Path] | None, bool, str | None]:
        dialog = DragDropFileDialog(title, default_path, filter_, with_resize_option=True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                self.add_line("❌ No files were selected.")
                return None, False, None
            paths = [Path(f) for f in filenames]
            resize_enabled = dialog.get_resize_enabled()
            max_size = dialog.get_max_size()
            return paths, resize_enabled, max_size
        self.add_line("❌ No files were selected.")
        return None, False, None
```

</details>

### ⚙️ Method `get_save_filename`

```python
def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None
```

Open a dialog to specify a filename for saving.

Args:

- `title` (`str`): The title of the dialog window.
- `default_path` (`str`): The initial directory displayed in the dialog.
- `filter_` (`str`): Filter for the types of files to display.

Returns:

- `Path | None`: The specified file path as a `Path` object, or `None` if no file name is chosen.

<details>
<summary>Code:</summary>

```python
def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        filename, _ = QFileDialog.getSaveFileName(None, title, default_path, filter_)
        if not filename:
            self.add_line("❌ No file was selected.")
            return None
        return Path(filename)
```

</details>

### ⚙️ Method `get_text_input`

```python
def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None
```

Prompt the user for text input via a simple dialog.

Args:

- `title` (`str`): The title of the input dialog.
- `label` (`str`): The label prompting the user for input.
- `default_value` (`str | None`): Default value to pre-fill the input field. Defaults to `None`.

Returns:

- `str | None`: The entered text, or `None` if cancelled or empty.

<details>
<summary>Code:</summary>

```python
def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        text, ok = QInputDialog.getText(None, title, label, text=default_value or "")
        if not (ok and text):
            self.add_line("❌ Text was not entered.")
            return None
        return text
```

</details>

### ⚙️ Method `get_text_input_with_auto`

```python
def get_text_input_with_auto(self, title: str, label: str, auto_generator: Callable[[], str] | None = None, auto_button_text: str = "🤖 Auto") -> str | None
```

Prompt the user for text input with an optional auto-generation button.

Args:

- `title` (`str`): The title of the input dialog.
- `label` (`str`): The label prompting the user for input.
- `auto_generator` (`Callable[[], str] | None`): Function that generates auto text. Defaults to `None`.
- `auto_button_text` (`str`): Text for the auto-generation button. Defaults to `"🤖 Auto"`.

Returns:

- `str | None`: The entered text, or `None` if cancelled or empty.

<details>
<summary>Code:</summary>

```python
def get_text_input_with_auto(
        self, title: str, label: str, auto_generator: Callable[[], str] | None = None, auto_button_text: str = "🤖 Auto"
    ) -> str | None:
        if auto_generator is None:
            # Fallback to regular text input if no auto generator provided
            return self.get_text_input(title, label)

        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create input field with auto button layout
        input_layout = QHBoxLayout()

        line_edit = QLineEdit()
        line_edit.setMinimumHeight(32)
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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

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
```

</details>

### ⚙️ Method `get_text_textarea`

```python
def get_text_textarea(self, title: str, label: str, default_text: str | None = None) -> str | None
```

Open a dialog for multi-line text entry.

Args:

- `title` (`str`): The title of the text area dialog.
- `label` (`str`): The label prompting the user for input.
- `default_text` (`str | None`): Optional default text to pre-fill the text area. Defaults to `None`.

Returns:

- `str | None`: The entered multi-line text, or `None` if cancelled or empty.

<details>
<summary>Code:</summary>

```python
def get_text_textarea(self, title: str, label: str, default_text: str | None = None) -> str | None:
        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Add a label
        label_widget = QLabel(label)
        layout.addWidget(label_widget)

        # Create a multi-line text field
        text_edit = QPlainTextEdit()
        text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        text_edit.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)
        if default_text is not None:
            text_edit.setPlainText(default_text)
        layout.addWidget(text_edit)

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

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
```

</details>

### ⚙️ Method `get_yes_no_question`

```python
def get_yes_no_question(self, title: str, message: str) -> bool
```

Open a yes/no question dialog.

Args:

- `title` (`str`): The title of the dialog window.
- `message` (`str`): The message to display to the user.

Returns:

- `bool`: True if user clicked Yes, False if user clicked No or closed the dialog.

<details>
<summary>Code:</summary>

```python
def get_yes_no_question(self, title: str, message: str) -> bool:
        reply = message_box.question(
            None,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes
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

### ⚙️ Method `show_about_dialog`

```python
def show_about_dialog(self, title: str = "About", app_name: str = "Harrix Swiss Knife", version: str = "1.0.0", description: str = "", author: str = "", license_text: str = "", github: str = "") -> str | None
```

Open a dialog to display information about the program.

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
        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Create a text browser widget
        text_browser = QTextBrowser()
        text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        text_browser.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)

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

        # Use setMarkdown to render headings, links, etc.
        text_browser.setMarkdown(about_text)
        text_browser.setOpenExternalLinks(True)

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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=0)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            return about_text
        return None
```

</details>

### ⚙️ Method `show_instructions`

```python
def show_instructions(self, instructions: str, title: str = "Instructions") -> str | None
```

Open a dialog to display instructions with basic Markdown support.

This method creates a dialog that displays instructions text.

Args:

- `instructions` (`str`): The instructions text.
- `title` (`str`): The title of the instructions dialog. Defaults to `"Instructions"`.

Returns:

- `str | None`: The displayed instructions text, or `None` if cancelled.

<details>
<summary>Code:</summary>

```python
def show_instructions(self, instructions: str, title: str = "Instructions") -> str | None:
        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Create a text browser widget
        text_browser = QTextBrowser()
        text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        text_browser.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 160)
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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=0)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            return instructions
        return None
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
        return self.show_text_multiline("\n".join(self.result_lines), "Result")
```

</details>

### ⚙️ Method `show_text_multiline`

```python
def show_text_multiline(self, text: str, title: str = "Result") -> str | None
```

Open a dialog to display text with a copy button.

Args:

- `text` (`str`): The text to display in the textarea.
- `title` (`str`): The title of the text area dialog.

Returns:

- `str | None`: The displayed text, or `None` if cancelled.

<details>
<summary>Code:</summary>

```python
def show_text_multiline(self, text: str, title: str = "Result") -> str | None:
        parent = QApplication.activeWindow()
        dialog = _StandardActionDialog(self.DEFAULT_ACTION_DIALOG_SIZE, parent)
        dialog.setWindowTitle(title)

        # Create the main layout for the dialog
        layout = QVBoxLayout()

        # Create a multi-line text field
        text_edit = QPlainTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)  # Make it read-only since we're just displaying text
        text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        text_edit.setMinimumHeight(self.DEFAULT_ACTION_DIALOG_SIZE.height() - 120)

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
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=0)

        # Show the dialog and wait for a response
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            return text
        return None
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
        toast = toast_notification.ToastNotification(message=message, duration=duration)
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

Returns:

- `None`: This method does not return a value.

Note:

- The worker thread reference is stored in `self._current_worker` to prevent garbage collection.
- Automatically closes any toast countdown notification before executing the callback.

<details>
<summary>Code:</summary>

```python
def start_thread(self, work_function: Callable, callback_function: Callable, message: str = "") -> None:

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

### ⚙️ Method `_finalize_standard_dialog_geometry`

```python
def _finalize_standard_dialog_geometry(self, dialog: QDialog, layout: QVBoxLayout) -> None
```

Apply default 1024x768 sizing and optional stretch (same as Select file combination).

<details>
<summary>Code:</summary>

```python
def _finalize_standard_dialog_geometry(
        self,
        dialog: QDialog,
        layout: QVBoxLayout,
        *,
        stretch_row: int | None = 1,
    ) -> None:
        target = self.DEFAULT_ACTION_DIALOG_SIZE
        if stretch_row is not None:
            layout.setStretch(stretch_row, 1)
        dialog.setMinimumSize(target)
        dialog.resize(target)

        def _enforce() -> None:
            dialog.setMinimumSize(target)
            dialog.resize(target)

        QTimer.singleShot(0, _enforce)
```

</details>

### ⚙️ Method `_write_output_path`

```python
def _write_output_path(self) -> Path
```

Path for `add_line` on this thread (worker threads keep their run's file).

<details>
<summary>Code:</summary>

```python
def _write_output_path(self) -> Path:
        override = getattr(_output_path_local, "file", None)
        return override if override is not None else self.file
```

</details>

## 🏛️ Class `ChoiceWithDescriptionDelegate`

```python
class ChoiceWithDescriptionDelegate(QStyledItemDelegate)
```

Custom delegate for displaying choices with descriptions in different font sizes.

<details>
<summary>Code:</summary>

```python
class ChoiceWithDescriptionDelegate(QStyledItemDelegate):

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint the item with custom formatting using QTextDocument."""
        painter.save()

        # Get the item text
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            painter.restore()
            return

        # Split text into choice and description
        lines = text.split("\n")
        min_count_lines = 2
        if len(lines) < min_count_lines:
            # Fallback to default painting
            super().paint(painter, option, index)
            painter.restore()
            return

        choice = lines[0]
        description = "\n".join(lines[1:]).strip()

        # Check if item is selected
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        # Set background color based on selection state
        if is_selected:
            painter.fillRect(option.rect, option.palette.highlight())
            text_color = option.palette.highlightedText().color()
        elif is_hovered:
            painter.fillRect(option.rect, option.palette.alternateBase())
            text_color = option.palette.text().color()
        else:
            text_color = option.palette.text().color()

        # Escape HTML and preserve line breaks
        escaped_choice = escape(choice)
        escaped_description = escape(description).replace("\n", "<br>")

        # Create HTML content with different font sizes and proper colors, avoiding line too long
        html_content = (
            f'<div style="font-family: Arial, sans-serif; color: {text_color.name()};">'
            f'<div style="font-size: 12pt; font-weight: bold; margin-bottom: 2px;">'
            f"{escaped_choice}"
            f"</div>"
            f'<div style="font-size: 9pt; font-style: italic; color: {text_color.name()}; '
            f'opacity: 0.7; margin-left: 10px; white-space: pre-wrap;">'
            f"{escaped_description}"
            f"</div>"
            f"</div>"
        )

        # Create QTextDocument for rich text rendering
        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.setTextWidth(option.rect.width())

        # Draw the document
        painter.translate(option.rect.topLeft())
        doc.drawContents(painter)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:  # noqa: N802
        """Calculate the size hint for the item."""
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            return super().sizeHint(option, index)

        lines = text.split("\n")
        max_count_parts = 2
        if len(lines) < max_count_parts:
            return super().sizeHint(option, index)

        choice = lines[0]
        description = "\n".join(lines[1:]).strip()

        # Escape HTML and preserve line breaks
        escaped_choice = escape(choice)
        escaped_description = escape(description).replace("\n", "<br>")

        html_content = f"""
        <div style="font-family: Arial, sans-serif;">
            <div style="font-size: 12pt; font-weight: bold; margin-bottom: 2px;">
                {escaped_choice}
            </div>
            <div style="font-size: 9pt; font-style: italic; color: #666666; margin-left: 10px; white-space: pre-wrap;">
                {escaped_description}
            </div>
        </div>
        """

        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.setTextWidth(option.rect.width())

        doc_size = doc.size()
        return QSize(int(doc_size.width()), int(doc_size.height()) + 5)  # Add some padding
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint the item with custom formatting using QTextDocument.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        painter.save()

        # Get the item text
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            painter.restore()
            return

        # Split text into choice and description
        lines = text.split("\n")
        min_count_lines = 2
        if len(lines) < min_count_lines:
            # Fallback to default painting
            super().paint(painter, option, index)
            painter.restore()
            return

        choice = lines[0]
        description = "\n".join(lines[1:]).strip()

        # Check if item is selected
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        # Set background color based on selection state
        if is_selected:
            painter.fillRect(option.rect, option.palette.highlight())
            text_color = option.palette.highlightedText().color()
        elif is_hovered:
            painter.fillRect(option.rect, option.palette.alternateBase())
            text_color = option.palette.text().color()
        else:
            text_color = option.palette.text().color()

        # Escape HTML and preserve line breaks
        escaped_choice = escape(choice)
        escaped_description = escape(description).replace("\n", "<br>")

        # Create HTML content with different font sizes and proper colors, avoiding line too long
        html_content = (
            f'<div style="font-family: Arial, sans-serif; color: {text_color.name()};">'
            f'<div style="font-size: 12pt; font-weight: bold; margin-bottom: 2px;">'
            f"{escaped_choice}"
            f"</div>"
            f'<div style="font-size: 9pt; font-style: italic; color: {text_color.name()}; '
            f'opacity: 0.7; margin-left: 10px; white-space: pre-wrap;">'
            f"{escaped_description}"
            f"</div>"
            f"</div>"
        )

        # Create QTextDocument for rich text rendering
        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.setTextWidth(option.rect.width())

        # Draw the document
        painter.translate(option.rect.topLeft())
        doc.drawContents(painter)

        painter.restore()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize
```

Calculate the size hint for the item.

<details>
<summary>Code:</summary>

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:  # noqa: N802
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            return super().sizeHint(option, index)

        lines = text.split("\n")
        max_count_parts = 2
        if len(lines) < max_count_parts:
            return super().sizeHint(option, index)

        choice = lines[0]
        description = "\n".join(lines[1:]).strip()

        # Escape HTML and preserve line breaks
        escaped_choice = escape(choice)
        escaped_description = escape(description).replace("\n", "<br>")

        html_content = f"""
        <div style="font-family: Arial, sans-serif;">
            <div style="font-size: 12pt; font-weight: bold; margin-bottom: 2px;">
                {escaped_choice}
            </div>
            <div style="font-size: 9pt; font-style: italic; color: #666666; margin-left: 10px; white-space: pre-wrap;">
                {escaped_description}
            </div>
        </div>
        """

        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.setTextWidth(option.rect.width())

        doc_size = doc.size()
        return QSize(int(doc_size.width()), int(doc_size.height()) + 5)  # Add some padding
```

</details>

## 🏛️ Class `DragDropFileDialog`

```python
class DragDropFileDialog(QDialog)
```

Custom dialog with drag-and-drop support for file selection.

<details>
<summary>Code:</summary>

```python
class DragDropFileDialog(QDialog):

    def __init__(
        self,
        title: str,
        default_path: str,
        filter_: str,
        parent: QWidget | None = None,
        *,
        with_resize_option: bool = False,
    ) -> None:
        """Initialize DragDropFileDialog.

        Args:

        - `title` (`str`): The window title for the dialog.
        - `default_path` (`str`): The default path to open in the file dialog.
        - `filter_` (`str`): The file filter string (e.g., "Text Files (*.txt)").
        - `parent` (`QWidget | None`): The parent widget. Defaults to `None`.
        - `with_resize_option` (`bool`): If True, show optional resize checkbox and max size input. Defaults to `False`.

        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setAcceptDrops(True)
        self.setMinimumSize(ActionBase.DEFAULT_ACTION_DIALOG_SIZE)
        self.resize(ActionBase.DEFAULT_ACTION_DIALOG_SIZE)

        self.default_path = default_path
        self.filter_ = filter_
        self.selected_files = []
        self.with_resize_option = with_resize_option

        self.setup_ui()

    def add_files(self, file_paths: list[str]) -> None:
        """Add files to the selection."""
        for file_path in file_paths:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_list.addItem(file_path)

    def clear_files(self) -> None:
        """Clear all selected files."""
        self.selected_files.clear()
        self.files_list.clear()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("""
                QLabel {
                    border: 2px dashed #007acc;
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    background-color: #e6f3ff;
                    color: #007acc;
                    font-size: 12px;
                }
            """)
        else:
            event.ignore()

    def dragLeaveEvent(self, _event: QDragLeaveEvent) -> None:  # noqa: N802
        """Handle drag leave event."""
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background-color: #f9f9f9;
                color: #666;
                font-size: 12px;
            }
        """)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        """Handle drop event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            files = []
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    files.append(file_path)

            self.add_files(files)
            event.acceptProposedAction()
        else:
            event.ignore()

    def get_max_size(self) -> str | None:
        """Return max size string for resize, or None if resize disabled or empty.
        Only valid when with_resize_option is True.
        """
        if not self.get_resize_enabled() or not hasattr(self, "max_size_edit"):
            return None
        text = self.max_size_edit.text().strip()
        return text or None

    def get_resize_enabled(self) -> bool:
        """Return True if resize option is enabled (checkbox checked). Only valid when with_resize_option is True."""
        if not self.with_resize_option or not hasattr(self, "resize_checkbox"):
            return False
        return self.resize_checkbox.isChecked()

    def get_selected_files(self) -> list[str]:
        """Get list of selected file paths."""
        return self.selected_files

    def select_files(self) -> None:
        """Open standard file dialog to select files."""
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.default_path, self.filter_)
        if filenames:
            self.add_files(filenames)

    def setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel("Select files for processing")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Drag and drop area
        self.drop_area = QLabel("Drag files here or click 'Select Files' button")
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background-color: #f9f9f9;
                color: #666;
                font-size: 12px;
            }
            QLabel:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
            }
        """)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setMinimumHeight(150)
        layout.addWidget(self.drop_area)

        # Selected files list
        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(100)
        layout.addWidget(self.files_list)

        # Optional resize option (max size in pixels)
        if self.with_resize_option:
            resize_layout = QHBoxLayout()
            self.resize_checkbox = QCheckBox("Resize images (max size, px)")
            self.resize_checkbox.setChecked(False)
            resize_layout.addWidget(self.resize_checkbox)
            self.max_size_edit = QLineEdit()
            self.max_size_edit.setPlaceholderText("1024")
            self.max_size_edit.setText("1024")
            self.max_size_edit.setEnabled(False)

            def toggle_max_size_edit(checked: bool) -> None:  # noqa: FBT001 (Qt slot receives one positional bool)
                self.max_size_edit.setEnabled(checked)

            self.resize_checkbox.toggled.connect(toggle_max_size_edit)
            resize_layout.addWidget(self.max_size_edit)
            resize_layout.addStretch()
            layout.addLayout(resize_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        self.select_files_btn = QPushButton("Select Files")
        self.select_files_btn.clicked.connect(self.select_files)
        buttons_layout.addWidget(self.select_files_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_files)
        buttons_layout.addWidget(self.clear_btn)

        buttons_layout.addStretch()

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        buttons_layout.addWidget(self.button_box)

        layout.addLayout(buttons_layout)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, default_path: str, filter_: str, parent: QWidget | None = None) -> None
```

Initialize DragDropFileDialog.

Args:

- `title` (`str`): The window title for the dialog.
- `default_path` (`str`): The default path to open in the file dialog.
- `filter_` (`str`): The file filter string (e.g., "Text Files (\*.txt)").
- `parent` (`QWidget | None`): The parent widget. Defaults to `None`.
- `with_resize_option` (`bool`): If True, show optional resize checkbox and max size input. Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        default_path: str,
        filter_: str,
        parent: QWidget | None = None,
        *,
        with_resize_option: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setAcceptDrops(True)
        self.setMinimumSize(ActionBase.DEFAULT_ACTION_DIALOG_SIZE)
        self.resize(ActionBase.DEFAULT_ACTION_DIALOG_SIZE)

        self.default_path = default_path
        self.filter_ = filter_
        self.selected_files = []
        self.with_resize_option = with_resize_option

        self.setup_ui()
```

</details>

### ⚙️ Method `add_files`

```python
def add_files(self, file_paths: list[str]) -> None
```

Add files to the selection.

<details>
<summary>Code:</summary>

```python
def add_files(self, file_paths: list[str]) -> None:
        for file_path in file_paths:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_list.addItem(file_path)
```

</details>

### ⚙️ Method `clear_files`

```python
def clear_files(self) -> None
```

Clear all selected files.

<details>
<summary>Code:</summary>

```python
def clear_files(self) -> None:
        self.selected_files.clear()
        self.files_list.clear()
```

</details>

### ⚙️ Method `dragEnterEvent`

```python
def dragEnterEvent(self, event: QDragEnterEvent) -> None
```

Handle drag enter event.

<details>
<summary>Code:</summary>

```python
def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("""
                QLabel {
                    border: 2px dashed #007acc;
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    background-color: #e6f3ff;
                    color: #007acc;
                    font-size: 12px;
                }
            """)
        else:
            event.ignore()
```

</details>

### ⚙️ Method `dragLeaveEvent`

```python
def dragLeaveEvent(self, _event: QDragLeaveEvent) -> None
```

Handle drag leave event.

<details>
<summary>Code:</summary>

```python
def dragLeaveEvent(self, _event: QDragLeaveEvent) -> None:  # noqa: N802
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background-color: #f9f9f9;
                color: #666;
                font-size: 12px;
            }
        """)
```

</details>

### ⚙️ Method `dropEvent`

```python
def dropEvent(self, event: QDropEvent) -> None
```

Handle drop event.

<details>
<summary>Code:</summary>

```python
def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            files = []
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    files.append(file_path)

            self.add_files(files)
            event.acceptProposedAction()
        else:
            event.ignore()
```

</details>

### ⚙️ Method `get_max_size`

```python
def get_max_size(self) -> str | None
```

Return max size string for resize, or None if resize disabled or empty.
Only valid when with_resize_option is True.

<details>
<summary>Code:</summary>

```python
def get_max_size(self) -> str | None:
        if not self.get_resize_enabled() or not hasattr(self, "max_size_edit"):
            return None
        text = self.max_size_edit.text().strip()
        return text or None
```

</details>

### ⚙️ Method `get_resize_enabled`

```python
def get_resize_enabled(self) -> bool
```

Return True if resize option is enabled (checkbox checked). Only valid when with_resize_option is True.

<details>
<summary>Code:</summary>

```python
def get_resize_enabled(self) -> bool:
        if not self.with_resize_option or not hasattr(self, "resize_checkbox"):
            return False
        return self.resize_checkbox.isChecked()
```

</details>

### ⚙️ Method `get_selected_files`

```python
def get_selected_files(self) -> list[str]
```

Get list of selected file paths.

<details>
<summary>Code:</summary>

```python
def get_selected_files(self) -> list[str]:
        return self.selected_files
```

</details>

### ⚙️ Method `select_files`

```python
def select_files(self) -> None
```

Open standard file dialog to select files.

<details>
<summary>Code:</summary>

```python
def select_files(self) -> None:
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.default_path, self.filter_)
        if filenames:
            self.add_files(filenames)
```

</details>

### ⚙️ Method `setup_ui`

```python
def setup_ui(self) -> None
```

Set up the user interface.

<details>
<summary>Code:</summary>

```python
def setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel("Select files for processing")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Drag and drop area
        self.drop_area = QLabel("Drag files here or click 'Select Files' button")
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background-color: #f9f9f9;
                color: #666;
                font-size: 12px;
            }
            QLabel:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
            }
        """)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setMinimumHeight(150)
        layout.addWidget(self.drop_area)

        # Selected files list
        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(100)
        layout.addWidget(self.files_list)

        # Optional resize option (max size in pixels)
        if self.with_resize_option:
            resize_layout = QHBoxLayout()
            self.resize_checkbox = QCheckBox("Resize images (max size, px)")
            self.resize_checkbox.setChecked(False)
            resize_layout.addWidget(self.resize_checkbox)
            self.max_size_edit = QLineEdit()
            self.max_size_edit.setPlaceholderText("1024")
            self.max_size_edit.setText("1024")
            self.max_size_edit.setEnabled(False)

            def toggle_max_size_edit(checked: bool) -> None:  # noqa: FBT001 (Qt slot receives one positional bool)
                self.max_size_edit.setEnabled(checked)

            self.resize_checkbox.toggled.connect(toggle_max_size_edit)
            resize_layout.addWidget(self.max_size_edit)
            resize_layout.addStretch()
            layout.addLayout(resize_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        self.select_files_btn = QPushButton("Select Files")
        self.select_files_btn.clicked.connect(self.select_files)
        buttons_layout.addWidget(self.select_files_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_files)
        buttons_layout.addWidget(self.clear_btn)

        buttons_layout.addStretch()

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        buttons_layout.addWidget(self.button_box)

        layout.addLayout(buttons_layout)
```

</details>

## 🏛️ Class `_StandardActionDialog`

```python
class _StandardActionDialog(QDialog)
```

QDialog that reapplies target size when shown (Windows may ignore initial `resize()`).

<details>
<summary>Code:</summary>

```python
class _StandardActionDialog(QDialog):

    def __init__(self, target_size: QSize, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._target_size = target_size

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self.setMinimumSize(self._target_size)
        self.resize(self._target_size)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, target_size: QSize, parent: QWidget | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, target_size: QSize, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._target_size = target_size
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self.setMinimumSize(self._target_size)
        self.resize(self._target_size)
```

</details>
