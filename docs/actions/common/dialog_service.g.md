---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dialog_service.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ActionDialogService`](#%EF%B8%8F-class-actiondialogservice)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `create_emoji_icon`](#%EF%B8%8F-method-create_emoji_icon)
  - [⚙️ Method `get_android_build_selection`](#%EF%B8%8F-method-get_android_build_selection)
  - [⚙️ Method `get_checkbox_selection`](#%EF%B8%8F-method-get_checkbox_selection)
  - [⚙️ Method `get_choice_from_described_cards`](#%EF%B8%8F-method-get_choice_from_described_cards)
  - [⚙️ Method `get_choice_from_icons`](#%EF%B8%8F-method-get_choice_from_icons)
  - [⚙️ Method `get_choice_from_list`](#%EF%B8%8F-method-get_choice_from_list)
  - [⚙️ Method `get_choice_from_list_with_descriptions`](#%EF%B8%8F-method-get_choice_from_list_with_descriptions)
  - [⚙️ Method `get_dual_checkbox_selection`](#%EF%B8%8F-method-get_dual_checkbox_selection)
  - [⚙️ Method `get_existing_directory`](#%EF%B8%8F-method-get_existing_directory)
  - [⚙️ Method `get_folder_with_choice_option (overload)`](#%EF%B8%8F-method-get_folder_with_choice_option-overload)
  - [⚙️ Method `get_folder_with_choice_option (overload 2)`](#%EF%B8%8F-method-get_folder_with_choice_option-overload-2)
  - [⚙️ Method `get_folder_with_choice_option`](#%EF%B8%8F-method-get_folder_with_choice_option)
  - [⚙️ Method `get_icon_choice`](#%EF%B8%8F-method-get_icon_choice)
  - [⚙️ Method `get_images_from_picker`](#%EF%B8%8F-method-get_images_from_picker)
  - [⚙️ Method `get_max_image_size_option`](#%EF%B8%8F-method-get_max_image_size_option)
  - [⚙️ Method `get_open_filename`](#%EF%B8%8F-method-get_open_filename)
  - [⚙️ Method `get_open_filenames`](#%EF%B8%8F-method-get_open_filenames)
  - [⚙️ Method `get_open_filenames_with_resize`](#%EF%B8%8F-method-get_open_filenames_with_resize)
  - [⚙️ Method `get_path_input`](#%EF%B8%8F-method-get_path_input)
  - [⚙️ Method `get_save_filename`](#%EF%B8%8F-method-get_save_filename)
  - [⚙️ Method `get_text_input`](#%EF%B8%8F-method-get_text_input)
  - [⚙️ Method `get_text_input_with_auto`](#%EF%B8%8F-method-get_text_input_with_auto)
  - [⚙️ Method `get_text_textarea`](#%EF%B8%8F-method-get_text_textarea)
  - [⚙️ Method `get_yes_no_question`](#%EF%B8%8F-method-get_yes_no_question)
  - [⚙️ Method `show_about_dialog`](#%EF%B8%8F-method-show_about_dialog)
  - [⚙️ Method `show_action_output_log_browser`](#%EF%B8%8F-method-show_action_output_log_browser)
  - [⚙️ Method `show_action_usage_stats_browser`](#%EF%B8%8F-method-show_action_usage_stats_browser)
  - [⚙️ Method `show_git_commit_offer`](#%EF%B8%8F-method-show_git_commit_offer)
  - [⚙️ Method `show_instructions`](#%EF%B8%8F-method-show_instructions)
  - [⚙️ Method `show_text_diff_side_by_side`](#%EF%B8%8F-method-show_text_diff_side_by_side)
  - [⚙️ Method `show_text_multiline`](#%EF%B8%8F-method-show_text_multiline)
- [🏛️ Class `AndroidBuildDialogResult`](#%EF%B8%8F-class-androidbuilddialogresult)
- [🏛️ Class `IconChoiceSelection`](#%EF%B8%8F-class-iconchoiceselection)

</details>

## 🏛️ Class `ActionDialogService`

```python
class ActionDialogService
```

Dialog builder/service for [`ActionBase`](base.g.md#%EF%B8%8F-class-actionbase)-like actions.

<details>
<summary>Code:</summary>

```python
class ActionDialogService:

    def __init__(
        self,
        *,
        default_size: QSize,
        compact_size: QSize,
        add_line: Callable[[str], None],
        show_toast: Callable[[str], None],
        create_emoji_icon: Callable[[str, int], QIcon],
    ) -> None:
        """Create service with UI callbacks injected from `ActionBase`."""
        self._default_size = default_size
        self._compact_size = compact_size
        self._add_line = add_line
        self._show_toast = show_toast
        self._create_emoji_icon = create_emoji_icon

    def create_emoji_icon(self, emoji: str, size: int = 64) -> QIcon:
        """Create icon via injected icon factory (kept for convenience)."""
        return self._create_emoji_icon(emoji, size)

    def get_android_build_selection(
        self,
        folders_list: list[str],
        default_path: str,
        *,
        build_all_checkbox_label: str,
        build_all_default: bool = False,
        release_default: bool = True,
        devices: list[tuple[str, str]],
        default_device_id: str | None = None,
    ) -> AndroidBuildDialogResult | None:
        """Pick Android project folder, build options, and one install target.

        `devices` entries are `(display_label, device_id)`. Cancel returns `None`.

        """
        select_folder = "📁 Select folder …"
        display_folders = [f"📁 {folder}" for folder in folders_list]
        full_list = [select_folder, *display_folders]

        folder_list: QListWidget | None = None
        device_list: QListWidget | None = None
        build_all_checkbox: QCheckBox | None = None
        release_checkbox: QCheckBox | None = None

        # Keep default width; avoid double width + adaptive shrink (was very wide and short).
        dialog_size = QSize(
            self._default_size.width(),
            max(self._default_size.height(), 560),
        )

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal folder_list, device_list, build_all_checkbox, release_checkbox

            columns = QHBoxLayout()

            left = QVBoxLayout()
            left.addWidget(QLabel("Folders"))
            flw = QListWidget()
            flw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            font = flw.font()
            font.setPointSize(12)
            flw.setFont(font)
            for choice in full_list:
                flw.addItem(QListWidgetItem(choice))
            # Prefer the first configured project; fall back to "Select folder …".
            if flw.count() > 1:
                flw.setCurrentRow(1)
            elif flw.count() > 0:
                flw.setCurrentRow(0)
            flw.itemDoubleClicked.connect(dialog.accept)
            left.addWidget(flw, stretch=1)

            all_cb = QCheckBox(build_all_checkbox_label)
            all_cb.setChecked(build_all_default)
            left.addWidget(all_cb)

            rel_cb = QCheckBox("Release")
            rel_cb.setChecked(release_default)
            left.addWidget(rel_cb)
            columns.addLayout(left, stretch=1)

            right = QVBoxLayout()
            right.addWidget(QLabel("Install device"))
            dlw = QListWidget()
            dlw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            dlw.setFont(font)
            dlw.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
            default_row = 0
            for index, (label, device_id) in enumerate(devices):
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, device_id)
                dlw.addItem(item)
                if default_device_id is not None and device_id == default_device_id:
                    default_row = index
            if dlw.count() > 0:
                dlw.setCurrentRow(default_row)
                dlw.itemDoubleClicked.connect(dialog.accept)
            else:
                empty = QListWidgetItem("No adb devices or AVDs found")
                empty.setFlags(Qt.ItemFlag.NoItemFlags)
                dlw.addItem(empty)
            right.addWidget(dlw, stretch=1)
            columns.addLayout(right, stretch=1)

            layout.addLayout(columns, stretch=1)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            folder_list = flw
            device_list = dlw
            build_all_checkbox = all_cb
            release_checkbox = rel_cb

        result, _dialog = self._exec_standard_dialog(
            select_folder,
            _build,
            stretch_row=0,
            adaptive=False,
            size=dialog_size,
        )
        if result != QDialog.DialogCode.Accepted:
            return None
        if folder_list is None or build_all_checkbox is None or release_checkbox is None or device_list is None:
            return None

        current_folder = folder_list.currentItem()
        if current_folder is None:
            return None

        build_all = build_all_checkbox.isChecked()
        path = self._resolve_folder_choice(
            current_folder.text(),
            select_folder,
            default_path,
            browse=not build_all,
        )
        if path is None:
            return None

        device_id: str | None = None
        current_device = device_list.currentItem()
        if current_device is not None:
            raw_id = current_device.data(Qt.ItemDataRole.UserRole)
            if isinstance(raw_id, str) and raw_id:
                device_id = raw_id

        return AndroidBuildDialogResult(
            folder=path,
            build_all=build_all,
            release=release_checkbox.isChecked(),
            device_id=device_id,
        )

    def get_checkbox_selection(
        self,
        title: str,
        label: str,
        choices: list[str],
        default_selected: list[str] | None = None,
        *,
        enable_extension_filter: bool = False,
        disabled_choices: list[str] | None = None,
        selection_presets: list[tuple[str, list[str]]] | None = None,
    ) -> list[str] | None:
        """Return checkbox-selected items, or `None` on cancel.

        `selection_presets` is a list of `(button_label, labels_to_check)` applied
        when the user clicks a preset button (other choices are unchecked).

        """
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        disabled_set = set(disabled_choices or ())

        parent = QApplication.activeWindow()
        dialog = StandardActionDialog(self._default_size, parent)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()

        label_widget = QLabel(label)
        label_widget.setWordWrap(True)
        layout.addWidget(label_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        checkboxes_container = QWidget()
        checkboxes_layout = QVBoxLayout(checkboxes_container)

        checkboxes: list[QCheckBox] = []
        for choice in choices:
            checkbox = QCheckBox(choice)
            font = checkbox.font()
            font.setPointSize(11)
            checkbox.setFont(font)

            if choice in disabled_set:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
            elif default_selected and choice in default_selected:
                checkbox.setChecked(True)

            checkboxes.append(checkbox)
            checkboxes_layout.addWidget(checkbox)

        checkboxes_layout.addStretch()

        scroll_area.setWidget(checkboxes_container)
        fit_widget_height(
            scroll_area,
            widget_content_height(checkboxes_container),
            maximum=self._default_size.height() - 200,
        )
        layout.addWidget(scroll_area)

        selection_buttons_layout = QHBoxLayout()

        select_all_button = QPushButton("✅ Select All")
        deselect_all_button = QPushButton("❌ Deselect All")
        extension_filter_button = QPushButton("🧩 Select by extension…")
        extension_filter_button.setVisible(enable_extension_filter)

        def select_all() -> None:
            for checkbox in checkboxes:
                if checkbox.isEnabled():
                    checkbox.setChecked(True)

        def deselect_all() -> None:
            for checkbox in checkboxes:
                if checkbox.isEnabled():
                    checkbox.setChecked(False)

        def apply_preset(labels: list[str]) -> None:
            wanted = set(labels)
            for checkbox in checkboxes:
                if not checkbox.isEnabled():
                    continue
                checkbox.setChecked(checkbox.text() in wanted)

        def _extension_key_for_choice(choice: str) -> str:
            return Path(choice).suffix.lower()

        def _build_extension_stats() -> tuple[list[str], dict[str, int]]:
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

            ext_dialog = StandardActionDialog(self._default_size, dialog)
            ext_dialog.setWindowTitle("Select extensions")

            ext_layout = QVBoxLayout()
            ext_label = QLabel("Choose extension states: checked = select all, unchecked = deselect all, mixed = keep.")
            ext_layout.addWidget(ext_label)

            ext_scroll_area = QScrollArea()
            ext_scroll_area.setWidgetResizable(True)
            ext_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
            fit_widget_height(
                ext_scroll_area,
                widget_content_height(ext_container),
                maximum=self._default_size.height() - 200,
            )
            ext_layout.addWidget(ext_scroll_area)

            ext_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(ext_buttons)
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
                    if checkbox.isEnabled() and _extension_key_for_choice(checkbox.text()) == ext:
                        checkbox.setChecked(target_checked)

        select_all_button.clicked.connect(select_all)
        deselect_all_button.clicked.connect(deselect_all)
        extension_filter_button.clicked.connect(select_by_extension)

        selection_buttons_layout.addWidget(select_all_button)
        selection_buttons_layout.addWidget(deselect_all_button)
        selection_buttons_layout.addWidget(extension_filter_button)
        if selection_presets:
            for preset_label, preset_labels in selection_presets:
                preset_button = QPushButton(preset_label)
                labels_snapshot = list(preset_labels)

                def _make_handler(labels: list[str]) -> object:
                    def _handler() -> None:
                        apply_preset(labels)

                    return _handler

                preset_button.clicked.connect(_make_handler(labels_snapshot))
                selection_buttons_layout.addWidget(preset_button)
        selection_buttons_layout.addStretch()

        layout.addLayout(selection_buttons_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            selected_choices = [
                checkbox.text() for checkbox in checkboxes if checkbox.isEnabled() and checkbox.isChecked()
            ]
            if not selected_choices:
                return None
            return selected_choices

        return None

    def get_choice_from_described_cards(
        self,
        title: str,
        label: str,
        choices: list[tuple[str, str, str]],
        icon_size: int = 48,
    ) -> str | None:
        """Return selected choice title from horizontal icon+hint cards, or `None` on cancel."""
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget

            lw = QListWidget()
            configure_described_choice_card_grid(lw)
            style_transparent_icon_grid(lw)

            def on_select(_choice_title: str) -> None:
                dialog.accept()

            populate_described_choice_cards(
                lw,
                choices,
                icon_size=icon_size,
                on_select=on_select,
            )
            fit_widget_height(
                lw,
                icon_grid_content_height(lw),
                maximum=self._default_size.height() - 160,
            )

            section, _, section_layout = create_command_section(title=label)
            section_layout.addWidget(lw)
            layout.addWidget(section)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item is None:
                return None
            choice_title = current_item.data(Qt.ItemDataRole.UserRole)
            if not isinstance(choice_title, str):
                return None
            return choice_title

        return None

    def get_choice_from_icons(
        self,
        title: str,
        label: str,
        choices: list[tuple[str, str]],
        icon_size: int = 64,
    ) -> str | None:
        """Return selected choice title from icon grid, or `None` on cancel."""
        selection = self.get_icon_choice(title, label, choices, icon_size=icon_size)
        return selection.title if selection is not None else None

    def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None:
        """Return selected item from list, or `None` on cancel."""
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            lw = QListWidget()
            lw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            font = lw.font()
            font.setPointSize(12)
            lw.setFont(font)

            for choice in choices:
                lw.addItem(QListWidgetItem(choice))

            if lw.count() > 0:
                lw.setCurrentRow(0)

            fit_widget_height(
                lw,
                list_content_height(lw),
                maximum=self._default_size.height() - 160,
            )

            lw.itemDoubleClicked.connect(dialog.accept)
            layout.addWidget(lw)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.text()
            return None

        return None

    def get_choice_from_list_with_descriptions(
        self,
        title: str,
        label: str,
        choices: list[tuple[str, str]],
    ) -> str | None:
        """Return selected item from list with descriptions, or `None` on cancel."""
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            lw = QListWidget()
            lw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            delegate = ChoiceWithDescriptionDelegate()
            lw.setItemDelegate(delegate)

            for choice, description in choices:
                formatted_description = description.replace("\n", "\n  ")
                item_text = f"{choice}\n  {formatted_description}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, choice)
                lw.addItem(item)

            if lw.count() > 0:
                lw.setCurrentRow(0)

            fit_widget_height(
                lw,
                list_content_height(lw),
                maximum=self._default_size.height() - 160,
            )

            lw.itemDoubleClicked.connect(dialog.accept)
            layout.addWidget(lw)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
            return None

        return None

    def get_dual_checkbox_selection(
        self,
        title: str,
        *,
        section1_title: str,
        section1_label: str,
        section1_choices: list[str],
        section1_default_selected: list[str] | None = None,
        section1_disabled_choices: list[str] | None = None,
        section2_title: str,
        section2_label: str,
        section2_choices: list[str],
        section2_default_selected: list[str] | None = None,
        section2_disabled_choices: list[str] | None = None,
    ) -> tuple[list[str], list[str]] | None:
        """Return checkbox selections for two sections, or `None` on cancel.

        Either section may be empty when the other has selections. Cancel or both
        sections empty returns `None`.

        """
        if not section1_choices and not section2_choices:
            self._add_line("❌ No choices provided.")
            return None

        parent = QApplication.activeWindow()
        dialog = StandardActionDialog(self._default_size, parent)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()

        def _build_section(
            *,
            group_title: str,
            group_label: str,
            choices: list[str],
            default_selected: list[str] | None,
            disabled_choices: list[str] | None,
        ) -> tuple[QGroupBox, list[QCheckBox]]:
            group = QGroupBox(group_title)
            group_layout = QVBoxLayout(group)

            label_widget = QLabel(group_label)
            label_widget.setWordWrap(True)
            group_layout.addWidget(label_widget)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setMinimumHeight(120)
            scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            checkboxes_container = QWidget()
            checkboxes_layout = QVBoxLayout(checkboxes_container)
            disabled_set = set(disabled_choices or ())
            default_set = set(default_selected or ())
            checkboxes: list[QCheckBox] = []
            for choice in choices:
                checkbox = QCheckBox(choice)
                font = checkbox.font()
                font.setPointSize(11)
                checkbox.setFont(font)
                if choice in disabled_set:
                    checkbox.setEnabled(False)
                    checkbox.setChecked(False)
                elif choice in default_set:
                    checkbox.setChecked(True)
                checkboxes.append(checkbox)
                checkboxes_layout.addWidget(checkbox)
            checkboxes_layout.addStretch()
            scroll_area.setWidget(checkboxes_container)
            group_layout.addWidget(scroll_area)

            selection_buttons_layout = QHBoxLayout()
            select_all_button = QPushButton("✅ Select All")
            deselect_all_button = QPushButton("❌ Deselect All")

            def select_all(boxes: list[QCheckBox] = checkboxes) -> None:
                for checkbox in boxes:
                    if checkbox.isEnabled():
                        checkbox.setChecked(True)

            def deselect_all(boxes: list[QCheckBox] = checkboxes) -> None:
                for checkbox in boxes:
                    if checkbox.isEnabled():
                        checkbox.setChecked(False)

            select_all_button.clicked.connect(select_all)
            deselect_all_button.clicked.connect(deselect_all)
            selection_buttons_layout.addWidget(select_all_button)
            selection_buttons_layout.addWidget(deselect_all_button)
            selection_buttons_layout.addStretch()
            group_layout.addLayout(selection_buttons_layout)
            return group, checkboxes

        group1, checkboxes1 = _build_section(
            group_title=section1_title,
            group_label=section1_label,
            choices=section1_choices,
            default_selected=section1_default_selected,
            disabled_choices=section1_disabled_choices,
        )
        group2, checkboxes2 = _build_section(
            group_title=section2_title,
            group_label=section2_label,
            choices=section2_choices,
            default_selected=section2_default_selected,
            disabled_choices=section2_disabled_choices,
        )
        layout.addWidget(group1, stretch=1)
        layout.addWidget(group2, stretch=1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=None)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        selected1 = [cb.text() for cb in checkboxes1 if cb.isEnabled() and cb.isChecked()]
        selected2 = [cb.text() for cb in checkboxes2 if cb.isEnabled() and cb.isChecked()]
        if not selected1 and not selected2:
            return None
        return selected1, selected2

    def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        """Return selected directory path, or `None` if cancelled."""
        folder_path = QFileDialog.getExistingDirectory(None, title, default_path)
        if not folder_path:
            return None
        return Path(folder_path)

    @overload
    def get_folder_with_choice_option(
        self,
        folders_list: list[str],
        default_path: str,
        *,
        checkbox_label: None = None,
        checkbox_default: bool = False,
    ) -> Path | None: ...

    @overload
    def get_folder_with_choice_option(
        self,
        folders_list: list[str],
        default_path: str,
        *,
        checkbox_label: str,
        checkbox_default: bool = False,
    ) -> tuple[Path, bool] | None: ...

    def get_folder_with_choice_option(
        self,
        folders_list: list[str],
        default_path: str,
        *,
        checkbox_label: str | None = None,
        checkbox_default: bool = False,
    ) -> Path | tuple[Path, bool] | None:
        """Pick folder from list or browse for directory.

        When `checkbox_label` is set, also show a checkbox and return
        `(path, checked)` on accept.

        """
        select_folder = "📁 Select folder …"
        display_folders = [f"📁 {folder}" for folder in folders_list]
        full_list = [select_folder, *display_folders]

        if checkbox_label is None:
            selected_folder = self.get_choice_from_list(select_folder, "Folders", full_list)
            if not selected_folder:
                return None
            return self._resolve_folder_choice(
                selected_folder,
                select_folder,
                default_path,
                browse=True,
            )

        selected = self._get_choice_from_list_with_checkbox(
            select_folder,
            "Folders",
            full_list,
            checkbox_label=checkbox_label,
            checkbox_default=checkbox_default,
        )
        if selected is None:
            return None
        selected_folder, checked = selected
        path = self._resolve_folder_choice(
            selected_folder,
            select_folder,
            default_path,
            browse=not checked,
        )
        if path is None:
            return None
        return path, checked

    def get_icon_choice(
        self,
        title: str,
        label: str,
        choices: list[tuple[str, str]],
        icon_size: int = 64,
        *,
        ai_screenshot_titles: Collection[str] | None = None,
    ) -> IconChoiceSelection | None:
        """Return selected icon choice, optionally via AI-screenshot card button."""
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None
        pending_action = ICON_CHOICE_ACTION_SELECT

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget, pending_action

            lw = QListWidget()
            configure_action_card_grid(lw)
            style_transparent_icon_grid(lw)

            def on_select(_choice_title: str) -> None:
                nonlocal pending_action
                pending_action = ICON_CHOICE_ACTION_SELECT
                dialog.accept()

            def on_ai_screenshot(_choice_title: str) -> None:
                nonlocal pending_action
                pending_action = ICON_CHOICE_ACTION_AI_SCREENSHOT
                dialog.accept()

            populate_icon_choice_cards(
                lw,
                choices,
                icon_size=icon_size,
                ai_screenshot_titles=ai_screenshot_titles,
                on_select=on_select,
                on_ai_screenshot=on_ai_screenshot if ai_screenshot_titles else None,
            )
            fit_widget_height(
                lw,
                icon_grid_content_height(lw),
                maximum=self._default_size.height() - 160,
            )

            section, _, section_layout = create_command_section(title=label)
            section_layout.addWidget(lw)
            layout.addWidget(section)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item is None:
                return None
            choice_title = current_item.data(Qt.ItemDataRole.UserRole)
            if not isinstance(choice_title, str):
                return None
            action = current_item.data(ICON_CHOICE_ACTION_ROLE)
            if not isinstance(action, str) or not action:
                action = pending_action
            return IconChoiceSelection(title=choice_title, action=action)

        return None

    def get_images_from_picker(
        self,
        title: str = "Select images",
        *,
        description: str = "",
        accept_button_text: str = "OK",
    ) -> list[Path] | None:
        """Show the standard ImagePicker and return selected image file paths.

        Supports adding files, capturing a screenshot, pasting from the clipboard,
        and drag-and-drop. Returns `None` if the dialog is cancelled or empty.

        """
        dialog = TextImageSourceDialog(
            None,
            title=title,
            description=description,
            show_text=False,
            show_images=True,
            images_required=True,
            image_mode=ImagePickerMode.MULTI,
            image_label="Images (drag, paste Ctrl+V, screenshot, or add files):",
            accept_button_text=accept_button_text,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        paths = [Path(path) for path in dialog.get_image_paths() if Path(path).is_file()]
        return paths or None

    def get_max_image_size_option(
        self,
        title: str = "Image size limit",
        *,
        checkbox_label: str = "Limit max image size (px)",
        default_enabled: bool = True,
        default_max_size: int = 1024,
    ) -> tuple[bool, int] | None:
        """Ask whether to limit max image width/height.

        Returns:

        - `tuple[bool, int] | None`: `(enabled, max_size)` on accept, or `None` if cancelled.
          When `enabled` is `False`, `max_size` is the spinbox value (for persistence) but
          callers should treat the limit as unset.

        """
        checkbox: QCheckBox | None = None
        spin_box: QSpinBox | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal checkbox, spin_box

            row = QHBoxLayout()
            cb = QCheckBox(checkbox_label)
            cb.setChecked(default_enabled)
            row.addWidget(cb)

            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setMaximum(100_000)
            spin.setValue(max(1, default_max_size))
            spin.setEnabled(default_enabled)
            row.addWidget(spin)
            row.addStretch()
            layout.addLayout(row)

            def toggle_spin(checked: bool) -> None:  # noqa: FBT001
                spin.setEnabled(checked)

            cb.toggled.connect(toggle_spin)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            checkbox = cb
            spin_box = spin

        result, _dialog = self._exec_compact_dialog(title, _build)
        if result != QDialog.DialogCode.Accepted or checkbox is None or spin_box is None:
            return None
        return checkbox.isChecked(), spin_box.value()

    def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """Return selected filename, or `None` if cancelled."""
        filename, _ = QFileDialog.getOpenFileName(None, title, default_path, filter_)
        if not filename:
            return None
        return Path(filename)

    def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None:
        """Return selected filenames, or `None` if cancelled."""
        dialog = DragDropFileDialog(title, default_path, filter_, self._default_size)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                return None
            return [Path(filename) for filename in filenames]
        return None

    def get_open_filenames_with_resize(
        self,
        title: str,
        default_path: str,
        filter_: str,
    ) -> tuple[list[Path] | None, bool, str | None]:
        """Return filenames plus resize options, or (`None`, `False`, `None`) if cancelled."""
        dialog = DragDropFileDialog(title, default_path, filter_, self._default_size, with_resize_option=True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                return None, False, None
            paths = [Path(f) for f in filenames]
            resize_enabled = dialog.get_resize_enabled()
            max_size = dialog.get_max_size()
            return paths, resize_enabled, max_size
        return None, False, None

    def get_path_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        """Return entered path, with an optional folder browse button."""
        line_edit: QLineEdit | None = None

        def _get_start_folder(path_text: str) -> str:
            path = Path(path_text).expanduser()
            if path.is_dir():
                return str(path)
            if path.parent.exists():
                return str(path.parent)
            return ""

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal line_edit

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            input_layout = QHBoxLayout()

            le = QLineEdit()
            le.setMinimumHeight(32)
            le.setText(default_value or "")
            input_layout.addWidget(le)

            browse_button = QPushButton("📁 Browse folder...")

            def on_browse_clicked() -> None:
                folder_path = QFileDialog.getExistingDirectory(
                    dialog,
                    "Select folder",
                    _get_start_folder(le.text().strip() or default_value or ""),
                )
                if folder_path:
                    le.setText(folder_path)

            browse_button.clicked.connect(on_browse_clicked)
            input_layout.addWidget(browse_button)

            layout.addLayout(input_layout)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            line_edit = le

        result, _dialog = self._exec_compact_dialog(title, _build)

        if result != QDialog.DialogCode.Accepted or line_edit is None:
            return None

        text = line_edit.text().strip()
        if not text:
            return None
        return text

    def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        """Return save target filename, or `None` if cancelled."""
        filename, _ = QFileDialog.getSaveFileName(None, title, default_path, filter_)
        if not filename:
            return None
        return Path(filename)

    def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        """Return entered text, or `None` on cancel/empty."""
        text, ok = QInputDialog.getText(None, title, label, text=default_value or "")
        if not (ok and text):
            return None
        return text

    def get_text_input_with_auto(
        self,
        title: str,
        label: str,
        auto_generator: Callable[[], str] | None = None,
        auto_button_text: str = "🤖 Auto",
        validator: Callable[[str], str | None] | None = None,
    ) -> str | None:
        """Return text input, optionally generated by callback, or `None` on cancel."""
        if auto_generator is None:
            return self.get_text_input(title, label)

        line_edit: QLineEdit | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal line_edit

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            input_layout = QHBoxLayout()

            le = QLineEdit()
            le.setMinimumHeight(32)
            try:
                le.setText(auto_generator())
            except Exception as e:
                self._add_line(f"❌ Error generating auto text: {e}")
            input_layout.addWidget(le)

            auto_button = make_emoji_push_button(
                auto_button_text.removeprefix("🤖 ").strip() or "Auto",
                "🤖",
            )

            def on_auto_clicked() -> None:
                try:
                    auto_text = auto_generator()
                    le.setText(auto_text)
                except Exception as e:
                    self._add_line(f"❌ Error generating auto text: {e}")

            auto_button.clicked.connect(on_auto_clicked)
            input_layout.addWidget(auto_button)

            layout.addLayout(input_layout)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)

            def try_accept() -> None:
                text = le.text().strip()
                if not text:
                    message_box.warning(dialog, title, "Name must not be empty.")
                    return
                if validator is not None:
                    error = validator(text)
                    if error:
                        message_box.warning(dialog, title, error)
                        return
                le.setText(text)
                dialog.accept()

            buttons.accepted.connect(try_accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            line_edit = le

        result, _dialog = self._exec_compact_dialog(title, _build)

        if result == QDialog.DialogCode.Accepted:
            if line_edit is None:
                return None
            return line_edit.text().strip()

        return None

    def get_text_textarea(
        self,
        title: str,
        label: str,
        default_text: str | None = None,
    ) -> str | None:
        """Return multi-line text, or `None` on cancel/empty."""
        text_edit: QPlainTextEdit | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal text_edit

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            te = QPlainTextEdit()
            te.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if default_text is not None:
                te.setPlainText(default_text)
            fit_widget_height(
                te,
                text_content_height(te),
                maximum=self._default_size.height() - 160,
            )
            layout.addWidget(te)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            text_edit = te

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if text_edit is None:
                return None
            text = text_edit.toPlainText()
            if not text.strip():
                return None
            return text
        return None

    def get_yes_no_question(self, title: str, message: str, *, default_yes: bool = False) -> bool:
        """Return `True` for Yes, `False` otherwise."""
        default_button = QMessageBox.StandardButton.Yes if default_yes else QMessageBox.StandardButton.No
        reply = message_box.question(
            None,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            default_button,
        )
        return reply == QMessageBox.StandardButton.Yes

    def show_about_dialog(
        self,
        *,
        title: str = "About",
        app_name: str = "Harrix Swiss Knife",
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
        license_text: str = "",
        github: str = "",
    ) -> str | None:
        """Show about dialog and return rendered text if accepted."""
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
            about_text += f"GitHub: [{github}]({github})\n\n"

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            logo_label = QLabel()
            logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            logo_label.setPixmap(QIcon(_ABOUT_LOGO_RESOURCE).pixmap(QSize(_ABOUT_LOGO_SIZE, _ABOUT_LOGO_SIZE)))
            logo_label.setFixedHeight(_ABOUT_LOGO_SIZE + 16)
            layout.addWidget(logo_label)

            text_browser = QTextBrowser()
            text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            text_browser.setMarkdown(about_text)
            text_browser.setOpenExternalLinks(True)

            font = QFont("JetBrains Mono", 10)
            text_browser.setFont(font)
            fit_widget_height(
                text_browser,
                text_content_height(text_browser),
                minimum=_ABOUT_TEXT_MIN_HEIGHT,
                maximum=self._default_size.height() - 160,
            )

            layout.addWidget(text_browser)

            button_layout = QHBoxLayout()
            copy_button = make_emoji_push_button("Copy to Clipboard", COPY_BUTTON_EMOJI)

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(about_text)
                self._show_toast("About information copied to Clipboard")

            copy_button.clicked.connect(click_copy_button)
            button_layout.addWidget(copy_button)

            ok_button = make_emoji_push_button("OK", OK_BUTTON_EMOJI)
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)
        return about_text if result == QDialog.DialogCode.Accepted else None

    def show_action_output_log_browser(
        self,
        entries: list[tuple[Path, str]],
        *,
        on_file_selected: Callable[[Path], None] | None = None,
    ) -> None:
        """Show a split view: log file list (left) and UTF-8 preview (right)."""
        if not entries:
            self._add_line("❌ No log files to browse.")
            return

        self._exec_standard_dialog(
            "Recent action logs",
            build_action_output_log_browser(
                entries,
                on_file_selected=on_file_selected,
                show_toast=self._show_toast,
            ),
            stretch_row=0,
        )

    def show_action_usage_stats_browser(
        self,
        rows: list[ActionUsageStatsRow],
        *,
        summary: str,
    ) -> None:
        """Show a sortable table of action invocation statistics."""
        dialog_parent = QApplication.activeWindow()
        dialog = QDialog(dialog_parent)
        dialog.setWindowTitle("Action usage stats")

        layout = QVBoxLayout()
        build_action_usage_stats_browser(rows, summary=summary)(dialog, layout)
        dialog.setLayout(layout)
        layout.setStretch(1, 1)

        # Same sizing as food/finance/habits main windows (maximize or ~1920 wide).
        apply_app_window_size_and_position(dialog)
        dialog.exec()

    def show_git_commit_offer(
        self,
        commit_message: str,
        *,
        repo_path: Path | None = None,
    ) -> int:
        """Offer to create a Git commit or copy the suggested commit message to the clipboard."""
        dialog_parent = QApplication.activeWindow()
        dialog = QDialog(dialog_parent)
        dialog.setWindowTitle("Git commit")

        layout = QVBoxLayout()

        intro = "Create a git commit with the suggested commit message?"
        if repo_path is not None:
            intro += f"\n\nRepository:\n{repo_path}"
        else:
            intro += "\n\n⚠️ Git repository not found for the changed files."

        label_widget = QLabel(intro)
        label_widget.setWordWrap(True)
        layout.addWidget(label_widget)

        message_label = QLabel("Commit message:")
        layout.addWidget(message_label)

        message_edit = QLineEdit(commit_message)
        message_edit.setReadOnly(True)
        layout.addWidget(message_edit)

        button_layout = QHBoxLayout()
        create_button = make_emoji_push_button("Create commit", "✅")
        create_button.setEnabled(repo_path is not None)
        create_button.clicked.connect(lambda: dialog.done(COMMIT_OFFER_CREATE_CODE))
        button_layout.addWidget(create_button)

        copy_button = make_emoji_push_button("Copy commit message", "📋")
        copy_button.clicked.connect(lambda: dialog.done(COMMIT_OFFER_COPY_CODE))
        button_layout.addWidget(copy_button)

        close_button = make_emoji_push_button("Close", CANCEL_BUTTON_EMOJI)
        close_button.clicked.connect(dialog.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.setMinimumWidth(min(self._default_size.width(), 640))
        dialog.adjustSize()
        result = dialog.exec()

        if result == COMMIT_OFFER_COPY_CODE:
            QGuiApplication.clipboard().setText(commit_message)
            self._show_toast("Commit message copied to Clipboard")

        return result

    def show_instructions(self, instructions: str, title: str = "Instructions") -> str | None:
        """Show instructions dialog and return text if accepted."""

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            text_browser = QTextBrowser()
            text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            text_browser.setPlainText(instructions)

            font = QFont("JetBrains Mono", 10)
            text_browser.setFont(font)
            fit_widget_height(
                text_browser,
                text_content_height(text_browser),
                maximum=self._default_size.height() - 160,
            )

            layout.addWidget(text_browser)

            button_layout = QHBoxLayout()
            copy_button = make_emoji_push_button("Copy to Clipboard", COPY_BUTTON_EMOJI)

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(instructions)
                self._show_toast("Instructions copied to Clipboard")

            copy_button.clicked.connect(click_copy_button)
            button_layout.addWidget(copy_button)

            ok_button = make_emoji_push_button("OK", OK_BUTTON_EMOJI)
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=0)
        return instructions if result == QDialog.DialogCode.Accepted else None

    def show_text_diff_side_by_side(
        self,
        before_text: str,
        after_text: str,
        title: str = "Diff (Before/After)",
        *,
        rerun_button: bool = False,
        rerun_button_label: str = RERUN_BUTTON_LABEL,
        rerun_button_emoji: str = RERUN_BUTTON_EMOJI,
        remove_paragraphs_button: bool = False,
    ) -> tuple[str | None, int]:
        """Show read-only before/after diff with inline change highlighting."""
        result_text_holder = [after_text]
        result, _dialog = self._exec_standard_dialog(
            title,
            build_text_diff_side_by_side(
                before_text,
                after_text,
                self._default_size,
                self._show_toast,
                rerun_button=rerun_button,
                rerun_button_label=rerun_button_label,
                rerun_button_emoji=rerun_button_emoji,
                remove_paragraphs_button=remove_paragraphs_button,
                result_text_holder=result_text_holder,
            ),
            stretch_row=0,
        )
        final_text = result_text_holder[0]
        if result == RERUN_DIALOG_CODE:
            return final_text, result
        return (final_text if result == QDialog.DialogCode.Accepted else None, result)

    def show_text_multiline(
        self,
        text: str,
        title: str = "Result",
        *,
        open_folder_path: Path | str | None = None,
        rerun_button: bool = False,
        rerun_button_label: str = RERUN_BUTTON_LABEL,
        rerun_button_emoji: str = RERUN_BUTTON_EMOJI,
        rewrite_button: bool = False,
        remove_paragraphs_button: bool = False,
        save_button: bool = False,
        save_default_path: str | None = None,
        save_filter: str = "Markdown Files (*.md);;All Files (*)",
    ) -> str | tuple[str | None, int] | None:
        """Show read-only multi-line text dialog and return text if accepted."""
        has_action_buttons = rerun_button or rewrite_button or remove_paragraphs_button
        folder_to_open = Path(open_folder_path) if open_folder_path is not None else None
        current_text = text

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal current_text
            text_edit = QPlainTextEdit()
            text_edit.setPlainText(current_text)
            text_edit.setReadOnly(True)
            text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            text_edit.setMinimumHeight(self._default_size.height() - 120)
            text_edit.moveCursor(QTextCursor.MoveOperation.End)

            font = QFont("JetBrains Mono")
            font.setPointSize(9)
            text_edit.setFont(font)

            layout.addWidget(text_edit)

            def _scroll_to_end() -> None:
                scrollbar = text_edit.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())

            # After showEvent resize and geometry enforce (both use singleShot(0)).
            QTimer.singleShot(0, lambda: QTimer.singleShot(0, _scroll_to_end))

            button_layout = QHBoxLayout()
            button_layout.addStretch(1)

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(text_edit.toPlainText())
                self._show_toast("Copied to Clipboard")

            add_copy_button(button_layout, click_copy_button)

            if save_button:

                def click_save_markdown() -> None:
                    path = self.get_save_filename(
                        "Save Markdown",
                        save_default_path or "",
                        save_filter,
                    )
                    if path is None:
                        return
                    if path.suffix == "":
                        path = path.with_suffix(".md")
                    markdown = text_edit.toPlainText()
                    if not markdown.endswith("\n"):
                        markdown += "\n"
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(markdown, encoding="utf-8")
                    self._add_line(f"💾 Saved Markdown: {path}")
                    self._show_toast(f"Saved: {path.name}")

                add_save_markdown_button(button_layout, click_save_markdown)

            if folder_to_open is not None:

                def click_open_folder() -> None:
                    h.file.open_file_or_folder(folder_to_open)

                add_open_folder_button(button_layout, click_open_folder)

            def on_remove_paragraphs() -> None:
                nonlocal current_text
                current_text = collapse_text_to_single_line(text_edit.toPlainText())
                text_edit.setPlainText(current_text)
                QGuiApplication.clipboard().setText(current_text)
                self._show_toast("Converted to single line")
                if remove_paragraphs_btn is not None:
                    remove_paragraphs_btn.setVisible(False)

            remove_paragraphs_btn = append_result_action_buttons(
                dialog,
                button_layout,
                rerun_button=rerun_button,
                rerun_button_label=rerun_button_label,
                rerun_button_emoji=rerun_button_emoji,
                rewrite_button=rewrite_button,
                remove_paragraphs_button=remove_paragraphs_button,
                on_remove_paragraphs=on_remove_paragraphs if remove_paragraphs_button else None,
                remove_paragraphs_source_text=current_text,
            )

            add_ok_button(dialog, button_layout)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=0, adaptive=False)
        if has_action_buttons:
            if result in (RERUN_DIALOG_CODE, REWRITE_DIALOG_CODE):
                return current_text, result
            return (current_text if result == QDialog.DialogCode.Accepted else None, result)
        return current_text if result == QDialog.DialogCode.Accepted else None

    def _apply_emoji_dialog_buttons(self, buttons: QDialogButtonBox) -> None:
        """Set emoji icons on standard QDialogButtonBox buttons."""
        apply_emoji_dialog_buttons(buttons, icon_size=DEFAULT_EMOJI_BUTTON_ICON_SIZE)

    def _exec_compact_dialog(
        self,
        title: str,
        build: Callable[[QDialog, QVBoxLayout], None],
        *,
        parent: QWidget | None = None,
    ) -> tuple[int, QDialog]:
        """Create and execute a compact dialog sized for simple input forms."""
        dialog_parent = QApplication.activeWindow() if parent is None else parent
        dialog = QDialog(dialog_parent)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()
        build(dialog, layout)

        dialog.setLayout(layout)
        dialog.setMinimumWidth(self._compact_size.width())
        dialog.adjustSize()
        dialog.resize(max(dialog.sizeHint().width(), self._compact_size.width()), dialog.sizeHint().height())
        result = dialog.exec()
        return result, dialog

    def _exec_standard_dialog(
        self,
        title: str,
        build: Callable[[QDialog, QVBoxLayout], None],
        *,
        parent: QWidget | None = None,
        stretch_row: int | None = 1,
        adaptive: bool = True,
        size: QSize | None = None,
    ) -> tuple[int, QDialog]:
        """Create, size, and execute a standard action dialog."""
        dialog_parent = QApplication.activeWindow() if parent is None else parent
        dialog_size = size if size is not None else self._default_size
        dialog = StandardActionDialog(dialog_size, dialog_parent)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()
        build(dialog, layout)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(
            dialog,
            layout,
            stretch_row=stretch_row,
            adaptive=adaptive,
            size=dialog_size,
        )
        result = dialog.exec()
        return result, dialog

    def _finalize_standard_dialog_geometry(
        self,
        dialog: QDialog,
        layout: QVBoxLayout,
        *,
        stretch_row: int | None = 1,
        adaptive: bool = True,
        size: QSize | None = None,
    ) -> None:
        """Apply dialog sizing and optional stretch row.

        When `adaptive` is `False`, keep the fixed default size (e.g. result dialogs).

        """
        target = size if size is not None else self._default_size
        if adaptive:
            size = apply_adaptive_dialog_size(dialog, layout, target=target, stretch_row=stretch_row)
        else:
            if stretch_row is not None:
                layout.setStretch(stretch_row, 1)
            size = target
            dialog.setMinimumSize(size)
            dialog.resize(size)

        if isinstance(dialog, StandardActionDialog):
            dialog.set_target_size(size)

        def _enforce() -> None:
            if adaptive:
                dialog.setMinimumWidth(size.width())
            else:
                dialog.setMinimumSize(size)
            dialog.resize(size)

        QTimer.singleShot(0, _enforce)

    def _get_choice_from_list_with_checkbox(
        self,
        title: str,
        label: str,
        choices: list[str],
        *,
        checkbox_label: str,
        checkbox_default: bool = False,
    ) -> tuple[str, bool] | None:
        """Return `(selected item, checkbox checked)` from a list dialog, or `None` on cancel."""
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None
        checkbox: QCheckBox | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget, checkbox

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            lw = QListWidget()
            lw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            font = lw.font()
            font.setPointSize(12)
            lw.setFont(font)

            for choice in choices:
                lw.addItem(QListWidgetItem(choice))

            if lw.count() > 0:
                lw.setCurrentRow(0)

            fit_widget_height(
                lw,
                list_content_height(lw),
                maximum=self._default_size.height() - 200,
            )

            lw.itemDoubleClicked.connect(dialog.accept)
            layout.addWidget(lw)

            cb = QCheckBox(checkbox_label)
            cb.setChecked(checkbox_default)
            layout.addWidget(cb)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw
            checkbox = cb

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result != QDialog.DialogCode.Accepted:
            return None
        if list_widget is None or checkbox is None:
            return None
        current_item = list_widget.currentItem()
        if current_item is None:
            return None
        return current_item.text(), checkbox.isChecked()

    def _resolve_folder_choice(
        self,
        selected_folder: str,
        select_folder: str,
        default_path: str,
        *,
        browse: bool,
    ) -> Path | None:
        """Map a folder-list selection to a `Path`, optionally opening a browse dialog."""
        if selected_folder == select_folder:
            if not browse:
                return Path(default_path)
            return self.get_existing_directory(select_folder, default_path)

        clean_folder_path = selected_folder.replace("📁 ", "", 1)
        return Path(clean_folder_path)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, default_size: QSize, compact_size: QSize, add_line: Callable[[str], None], show_toast: Callable[[str], None], create_emoji_icon: Callable[[str, int], QIcon]) -> None
```

Create service with UI callbacks injected from [`ActionBase`](base.g.md#%EF%B8%8F-class-actionbase).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        *,
        default_size: QSize,
        compact_size: QSize,
        add_line: Callable[[str], None],
        show_toast: Callable[[str], None],
        create_emoji_icon: Callable[[str, int], QIcon],
    ) -> None:
        self._default_size = default_size
        self._compact_size = compact_size
        self._add_line = add_line
        self._show_toast = show_toast
        self._create_emoji_icon = create_emoji_icon
```

</details>

### ⚙️ Method `create_emoji_icon`

```python
def create_emoji_icon(self, emoji: str, size: int = 64) -> QIcon
```

Create icon via injected icon factory (kept for convenience).

<details>
<summary>Code:</summary>

```python
def create_emoji_icon(self, emoji: str, size: int = 64) -> QIcon:
        return self._create_emoji_icon(emoji, size)
```

</details>

### ⚙️ Method `get_android_build_selection`

```python
def get_android_build_selection(self, folders_list: list[str], default_path: str, *, build_all_checkbox_label: str, build_all_default: bool = False, release_default: bool = True, devices: list[tuple[str, str]], default_device_id: str | None = None) -> AndroidBuildDialogResult | None
```

Pick Android project folder, build options, and one install target.

`devices` entries are `(display_label, device_id)`. Cancel returns `None`.

<details>
<summary>Code:</summary>

```python
def get_android_build_selection(
        self,
        folders_list: list[str],
        default_path: str,
        *,
        build_all_checkbox_label: str,
        build_all_default: bool = False,
        release_default: bool = True,
        devices: list[tuple[str, str]],
        default_device_id: str | None = None,
    ) -> AndroidBuildDialogResult | None:
        select_folder = "📁 Select folder …"
        display_folders = [f"📁 {folder}" for folder in folders_list]
        full_list = [select_folder, *display_folders]

        folder_list: QListWidget | None = None
        device_list: QListWidget | None = None
        build_all_checkbox: QCheckBox | None = None
        release_checkbox: QCheckBox | None = None

        # Keep default width; avoid double width + adaptive shrink (was very wide and short).
        dialog_size = QSize(
            self._default_size.width(),
            max(self._default_size.height(), 560),
        )

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal folder_list, device_list, build_all_checkbox, release_checkbox

            columns = QHBoxLayout()

            left = QVBoxLayout()
            left.addWidget(QLabel("Folders"))
            flw = QListWidget()
            flw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            font = flw.font()
            font.setPointSize(12)
            flw.setFont(font)
            for choice in full_list:
                flw.addItem(QListWidgetItem(choice))
            # Prefer the first configured project; fall back to "Select folder …".
            if flw.count() > 1:
                flw.setCurrentRow(1)
            elif flw.count() > 0:
                flw.setCurrentRow(0)
            flw.itemDoubleClicked.connect(dialog.accept)
            left.addWidget(flw, stretch=1)

            all_cb = QCheckBox(build_all_checkbox_label)
            all_cb.setChecked(build_all_default)
            left.addWidget(all_cb)

            rel_cb = QCheckBox("Release")
            rel_cb.setChecked(release_default)
            left.addWidget(rel_cb)
            columns.addLayout(left, stretch=1)

            right = QVBoxLayout()
            right.addWidget(QLabel("Install device"))
            dlw = QListWidget()
            dlw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            dlw.setFont(font)
            dlw.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
            default_row = 0
            for index, (label, device_id) in enumerate(devices):
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, device_id)
                dlw.addItem(item)
                if default_device_id is not None and device_id == default_device_id:
                    default_row = index
            if dlw.count() > 0:
                dlw.setCurrentRow(default_row)
                dlw.itemDoubleClicked.connect(dialog.accept)
            else:
                empty = QListWidgetItem("No adb devices or AVDs found")
                empty.setFlags(Qt.ItemFlag.NoItemFlags)
                dlw.addItem(empty)
            right.addWidget(dlw, stretch=1)
            columns.addLayout(right, stretch=1)

            layout.addLayout(columns, stretch=1)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            folder_list = flw
            device_list = dlw
            build_all_checkbox = all_cb
            release_checkbox = rel_cb

        result, _dialog = self._exec_standard_dialog(
            select_folder,
            _build,
            stretch_row=0,
            adaptive=False,
            size=dialog_size,
        )
        if result != QDialog.DialogCode.Accepted:
            return None
        if folder_list is None or build_all_checkbox is None or release_checkbox is None or device_list is None:
            return None

        current_folder = folder_list.currentItem()
        if current_folder is None:
            return None

        build_all = build_all_checkbox.isChecked()
        path = self._resolve_folder_choice(
            current_folder.text(),
            select_folder,
            default_path,
            browse=not build_all,
        )
        if path is None:
            return None

        device_id: str | None = None
        current_device = device_list.currentItem()
        if current_device is not None:
            raw_id = current_device.data(Qt.ItemDataRole.UserRole)
            if isinstance(raw_id, str) and raw_id:
                device_id = raw_id

        return AndroidBuildDialogResult(
            folder=path,
            build_all=build_all,
            release=release_checkbox.isChecked(),
            device_id=device_id,
        )
```

</details>

### ⚙️ Method `get_checkbox_selection`

```python
def get_checkbox_selection(self, title: str, label: str, choices: list[str], default_selected: list[str] | None = None, *, enable_extension_filter: bool = False, disabled_choices: list[str] | None = None, selection_presets: list[tuple[str, list[str]]] | None = None) -> list[str] | None
```

Return checkbox-selected items, or `None` on cancel.

`selection_presets` is a list of `(button_label, labels_to_check)` applied
when the user clicks a preset button (other choices are unchecked).

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
        selection_presets: list[tuple[str, list[str]]] | None = None,
    ) -> list[str] | None:
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        disabled_set = set(disabled_choices or ())

        parent = QApplication.activeWindow()
        dialog = StandardActionDialog(self._default_size, parent)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()

        label_widget = QLabel(label)
        label_widget.setWordWrap(True)
        layout.addWidget(label_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        checkboxes_container = QWidget()
        checkboxes_layout = QVBoxLayout(checkboxes_container)

        checkboxes: list[QCheckBox] = []
        for choice in choices:
            checkbox = QCheckBox(choice)
            font = checkbox.font()
            font.setPointSize(11)
            checkbox.setFont(font)

            if choice in disabled_set:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
            elif default_selected and choice in default_selected:
                checkbox.setChecked(True)

            checkboxes.append(checkbox)
            checkboxes_layout.addWidget(checkbox)

        checkboxes_layout.addStretch()

        scroll_area.setWidget(checkboxes_container)
        fit_widget_height(
            scroll_area,
            widget_content_height(checkboxes_container),
            maximum=self._default_size.height() - 200,
        )
        layout.addWidget(scroll_area)

        selection_buttons_layout = QHBoxLayout()

        select_all_button = QPushButton("✅ Select All")
        deselect_all_button = QPushButton("❌ Deselect All")
        extension_filter_button = QPushButton("🧩 Select by extension…")
        extension_filter_button.setVisible(enable_extension_filter)

        def select_all() -> None:
            for checkbox in checkboxes:
                if checkbox.isEnabled():
                    checkbox.setChecked(True)

        def deselect_all() -> None:
            for checkbox in checkboxes:
                if checkbox.isEnabled():
                    checkbox.setChecked(False)

        def apply_preset(labels: list[str]) -> None:
            wanted = set(labels)
            for checkbox in checkboxes:
                if not checkbox.isEnabled():
                    continue
                checkbox.setChecked(checkbox.text() in wanted)

        def _extension_key_for_choice(choice: str) -> str:
            return Path(choice).suffix.lower()

        def _build_extension_stats() -> tuple[list[str], dict[str, int]]:
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

            ext_dialog = StandardActionDialog(self._default_size, dialog)
            ext_dialog.setWindowTitle("Select extensions")

            ext_layout = QVBoxLayout()
            ext_label = QLabel("Choose extension states: checked = select all, unchecked = deselect all, mixed = keep.")
            ext_layout.addWidget(ext_label)

            ext_scroll_area = QScrollArea()
            ext_scroll_area.setWidgetResizable(True)
            ext_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
            fit_widget_height(
                ext_scroll_area,
                widget_content_height(ext_container),
                maximum=self._default_size.height() - 200,
            )
            ext_layout.addWidget(ext_scroll_area)

            ext_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(ext_buttons)
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
                    if checkbox.isEnabled() and _extension_key_for_choice(checkbox.text()) == ext:
                        checkbox.setChecked(target_checked)

        select_all_button.clicked.connect(select_all)
        deselect_all_button.clicked.connect(deselect_all)
        extension_filter_button.clicked.connect(select_by_extension)

        selection_buttons_layout.addWidget(select_all_button)
        selection_buttons_layout.addWidget(deselect_all_button)
        selection_buttons_layout.addWidget(extension_filter_button)
        if selection_presets:
            for preset_label, preset_labels in selection_presets:
                preset_button = QPushButton(preset_label)
                labels_snapshot = list(preset_labels)

                def _make_handler(labels: list[str]) -> object:
                    def _handler() -> None:
                        apply_preset(labels)

                    return _handler

                preset_button.clicked.connect(_make_handler(labels_snapshot))
                selection_buttons_layout.addWidget(preset_button)
        selection_buttons_layout.addStretch()

        layout.addLayout(selection_buttons_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=1)

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            selected_choices = [
                checkbox.text() for checkbox in checkboxes if checkbox.isEnabled() and checkbox.isChecked()
            ]
            if not selected_choices:
                return None
            return selected_choices

        return None
```

</details>

### ⚙️ Method `get_choice_from_described_cards`

```python
def get_choice_from_described_cards(self, title: str, label: str, choices: list[tuple[str, str, str]], icon_size: int = 48) -> str | None
```

Return selected choice title from horizontal icon+hint cards, or `None` on cancel.

<details>
<summary>Code:</summary>

```python
def get_choice_from_described_cards(
        self,
        title: str,
        label: str,
        choices: list[tuple[str, str, str]],
        icon_size: int = 48,
    ) -> str | None:
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget

            lw = QListWidget()
            configure_described_choice_card_grid(lw)
            style_transparent_icon_grid(lw)

            def on_select(_choice_title: str) -> None:
                dialog.accept()

            populate_described_choice_cards(
                lw,
                choices,
                icon_size=icon_size,
                on_select=on_select,
            )
            fit_widget_height(
                lw,
                icon_grid_content_height(lw),
                maximum=self._default_size.height() - 160,
            )

            section, _, section_layout = create_command_section(title=label)
            section_layout.addWidget(lw)
            layout.addWidget(section)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item is None:
                return None
            choice_title = current_item.data(Qt.ItemDataRole.UserRole)
            if not isinstance(choice_title, str):
                return None
            return choice_title

        return None
```

</details>

### ⚙️ Method `get_choice_from_icons`

```python
def get_choice_from_icons(self, title: str, label: str, choices: list[tuple[str, str]], icon_size: int = 64) -> str | None
```

Return selected choice title from icon grid, or `None` on cancel.

<details>
<summary>Code:</summary>

```python
def get_choice_from_icons(
        self,
        title: str,
        label: str,
        choices: list[tuple[str, str]],
        icon_size: int = 64,
    ) -> str | None:
        selection = self.get_icon_choice(title, label, choices, icon_size=icon_size)
        return selection.title if selection is not None else None
```

</details>

### ⚙️ Method `get_choice_from_list`

```python
def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None
```

Return selected item from list, or `None` on cancel.

<details>
<summary>Code:</summary>

```python
def get_choice_from_list(self, title: str, label: str, choices: list[str]) -> str | None:
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            lw = QListWidget()
            lw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            font = lw.font()
            font.setPointSize(12)
            lw.setFont(font)

            for choice in choices:
                lw.addItem(QListWidgetItem(choice))

            if lw.count() > 0:
                lw.setCurrentRow(0)

            fit_widget_height(
                lw,
                list_content_height(lw),
                maximum=self._default_size.height() - 160,
            )

            lw.itemDoubleClicked.connect(dialog.accept)
            layout.addWidget(lw)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.text()
            return None

        return None
```

</details>

### ⚙️ Method `get_choice_from_list_with_descriptions`

```python
def get_choice_from_list_with_descriptions(self, title: str, label: str, choices: list[tuple[str, str]]) -> str | None
```

Return selected item from list with descriptions, or `None` on cancel.

<details>
<summary>Code:</summary>

```python
def get_choice_from_list_with_descriptions(
        self,
        title: str,
        label: str,
        choices: list[tuple[str, str]],
    ) -> str | None:
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            lw = QListWidget()
            lw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            delegate = ChoiceWithDescriptionDelegate()
            lw.setItemDelegate(delegate)

            for choice, description in choices:
                formatted_description = description.replace("\n", "\n  ")
                item_text = f"{choice}\n  {formatted_description}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, choice)
                lw.addItem(item)

            if lw.count() > 0:
                lw.setCurrentRow(0)

            fit_widget_height(
                lw,
                list_content_height(lw),
                maximum=self._default_size.height() - 160,
            )

            lw.itemDoubleClicked.connect(dialog.accept)
            layout.addWidget(lw)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
            return None

        return None
```

</details>

### ⚙️ Method `get_dual_checkbox_selection`

```python
def get_dual_checkbox_selection(self, title: str, *, section1_title: str, section1_label: str, section1_choices: list[str], section1_default_selected: list[str] | None = None, section1_disabled_choices: list[str] | None = None, section2_title: str, section2_label: str, section2_choices: list[str], section2_default_selected: list[str] | None = None, section2_disabled_choices: list[str] | None = None) -> tuple[list[str], list[str]] | None
```

Return checkbox selections for two sections, or `None` on cancel.

Either section may be empty when the other has selections. Cancel or both
sections empty returns `None`.

<details>
<summary>Code:</summary>

```python
def get_dual_checkbox_selection(
        self,
        title: str,
        *,
        section1_title: str,
        section1_label: str,
        section1_choices: list[str],
        section1_default_selected: list[str] | None = None,
        section1_disabled_choices: list[str] | None = None,
        section2_title: str,
        section2_label: str,
        section2_choices: list[str],
        section2_default_selected: list[str] | None = None,
        section2_disabled_choices: list[str] | None = None,
    ) -> tuple[list[str], list[str]] | None:
        if not section1_choices and not section2_choices:
            self._add_line("❌ No choices provided.")
            return None

        parent = QApplication.activeWindow()
        dialog = StandardActionDialog(self._default_size, parent)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()

        def _build_section(
            *,
            group_title: str,
            group_label: str,
            choices: list[str],
            default_selected: list[str] | None,
            disabled_choices: list[str] | None,
        ) -> tuple[QGroupBox, list[QCheckBox]]:
            group = QGroupBox(group_title)
            group_layout = QVBoxLayout(group)

            label_widget = QLabel(group_label)
            label_widget.setWordWrap(True)
            group_layout.addWidget(label_widget)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setMinimumHeight(120)
            scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            checkboxes_container = QWidget()
            checkboxes_layout = QVBoxLayout(checkboxes_container)
            disabled_set = set(disabled_choices or ())
            default_set = set(default_selected or ())
            checkboxes: list[QCheckBox] = []
            for choice in choices:
                checkbox = QCheckBox(choice)
                font = checkbox.font()
                font.setPointSize(11)
                checkbox.setFont(font)
                if choice in disabled_set:
                    checkbox.setEnabled(False)
                    checkbox.setChecked(False)
                elif choice in default_set:
                    checkbox.setChecked(True)
                checkboxes.append(checkbox)
                checkboxes_layout.addWidget(checkbox)
            checkboxes_layout.addStretch()
            scroll_area.setWidget(checkboxes_container)
            group_layout.addWidget(scroll_area)

            selection_buttons_layout = QHBoxLayout()
            select_all_button = QPushButton("✅ Select All")
            deselect_all_button = QPushButton("❌ Deselect All")

            def select_all(boxes: list[QCheckBox] = checkboxes) -> None:
                for checkbox in boxes:
                    if checkbox.isEnabled():
                        checkbox.setChecked(True)

            def deselect_all(boxes: list[QCheckBox] = checkboxes) -> None:
                for checkbox in boxes:
                    if checkbox.isEnabled():
                        checkbox.setChecked(False)

            select_all_button.clicked.connect(select_all)
            deselect_all_button.clicked.connect(deselect_all)
            selection_buttons_layout.addWidget(select_all_button)
            selection_buttons_layout.addWidget(deselect_all_button)
            selection_buttons_layout.addStretch()
            group_layout.addLayout(selection_buttons_layout)
            return group, checkboxes

        group1, checkboxes1 = _build_section(
            group_title=section1_title,
            group_label=section1_label,
            choices=section1_choices,
            default_selected=section1_default_selected,
            disabled_choices=section1_disabled_choices,
        )
        group2, checkboxes2 = _build_section(
            group_title=section2_title,
            group_label=section2_label,
            choices=section2_choices,
            default_selected=section2_default_selected,
            disabled_choices=section2_disabled_choices,
        )
        layout.addWidget(group1, stretch=1)
        layout.addWidget(group2, stretch=1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        self._finalize_standard_dialog_geometry(dialog, layout, stretch_row=None)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        selected1 = [cb.text() for cb in checkboxes1 if cb.isEnabled() and cb.isChecked()]
        selected2 = [cb.text() for cb in checkboxes2 if cb.isEnabled() and cb.isChecked()]
        if not selected1 and not selected2:
            return None
        return selected1, selected2
```

</details>

### ⚙️ Method `get_existing_directory`

```python
def get_existing_directory(self, title: str, default_path: str) -> Path | None
```

Return selected directory path, or `None` if cancelled.

<details>
<summary>Code:</summary>

```python
def get_existing_directory(self, title: str, default_path: str) -> Path | None:
        folder_path = QFileDialog.getExistingDirectory(None, title, default_path)
        if not folder_path:
            return None
        return Path(folder_path)
```

</details>

### ⚙️ Method `get_folder_with_choice_option (overload)`

```python
def get_folder_with_choice_option(self, folders_list: list[str], default_path: str, *, checkbox_label: None = None, checkbox_default: bool = False) -> Path | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def get_folder_with_choice_option(
        self,
        folders_list: list[str],
        default_path: str,
        *,
        checkbox_label: None = None,
        checkbox_default: bool = False,
    ) -> Path | None: ...
```

</details>

### ⚙️ Method `get_folder_with_choice_option (overload 2)`

```python
def get_folder_with_choice_option(self, folders_list: list[str], default_path: str, *, checkbox_label: str, checkbox_default: bool = False) -> tuple[Path, bool] | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def get_folder_with_choice_option(
        self,
        folders_list: list[str],
        default_path: str,
        *,
        checkbox_label: str,
        checkbox_default: bool = False,
    ) -> tuple[Path, bool] | None: ...
```

</details>

### ⚙️ Method `get_folder_with_choice_option`

```python
def get_folder_with_choice_option(self, folders_list: list[str], default_path: str, *, checkbox_label: str | None = None, checkbox_default: bool = False) -> Path | tuple[Path, bool] | None
```

Pick folder from list or browse for directory.

When `checkbox_label` is set, also show a checkbox and return
`(path, checked)` on accept.

<details>
<summary>Code:</summary>

```python
def get_folder_with_choice_option(
        self,
        folders_list: list[str],
        default_path: str,
        *,
        checkbox_label: str | None = None,
        checkbox_default: bool = False,
    ) -> Path | tuple[Path, bool] | None:
        select_folder = "📁 Select folder …"
        display_folders = [f"📁 {folder}" for folder in folders_list]
        full_list = [select_folder, *display_folders]

        if checkbox_label is None:
            selected_folder = self.get_choice_from_list(select_folder, "Folders", full_list)
            if not selected_folder:
                return None
            return self._resolve_folder_choice(
                selected_folder,
                select_folder,
                default_path,
                browse=True,
            )

        selected = self._get_choice_from_list_with_checkbox(
            select_folder,
            "Folders",
            full_list,
            checkbox_label=checkbox_label,
            checkbox_default=checkbox_default,
        )
        if selected is None:
            return None
        selected_folder, checked = selected
        path = self._resolve_folder_choice(
            selected_folder,
            select_folder,
            default_path,
            browse=not checked,
        )
        if path is None:
            return None
        return path, checked
```

</details>

### ⚙️ Method `get_icon_choice`

```python
def get_icon_choice(self, title: str, label: str, choices: list[tuple[str, str]], icon_size: int = 64, *, ai_screenshot_titles: Collection[str] | None = None) -> IconChoiceSelection | None
```

Return selected icon choice, optionally via AI-screenshot card button.

<details>
<summary>Code:</summary>

```python
def get_icon_choice(
        self,
        title: str,
        label: str,
        choices: list[tuple[str, str]],
        icon_size: int = 64,
        *,
        ai_screenshot_titles: Collection[str] | None = None,
    ) -> IconChoiceSelection | None:
        if not choices:
            self._add_line("❌ No choices provided.")
            return None

        list_widget: QListWidget | None = None
        pending_action = ICON_CHOICE_ACTION_SELECT

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal list_widget, pending_action

            lw = QListWidget()
            configure_action_card_grid(lw)
            style_transparent_icon_grid(lw)

            def on_select(_choice_title: str) -> None:
                nonlocal pending_action
                pending_action = ICON_CHOICE_ACTION_SELECT
                dialog.accept()

            def on_ai_screenshot(_choice_title: str) -> None:
                nonlocal pending_action
                pending_action = ICON_CHOICE_ACTION_AI_SCREENSHOT
                dialog.accept()

            populate_icon_choice_cards(
                lw,
                choices,
                icon_size=icon_size,
                ai_screenshot_titles=ai_screenshot_titles,
                on_select=on_select,
                on_ai_screenshot=on_ai_screenshot if ai_screenshot_titles else None,
            )
            fit_widget_height(
                lw,
                icon_grid_content_height(lw),
                maximum=self._default_size.height() - 160,
            )

            section, _, section_layout = create_command_section(title=label)
            section_layout.addWidget(lw)
            layout.addWidget(section)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            list_widget = lw

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if list_widget is None:
                return None
            current_item = list_widget.currentItem()
            if current_item is None:
                return None
            choice_title = current_item.data(Qt.ItemDataRole.UserRole)
            if not isinstance(choice_title, str):
                return None
            action = current_item.data(ICON_CHOICE_ACTION_ROLE)
            if not isinstance(action, str) or not action:
                action = pending_action
            return IconChoiceSelection(title=choice_title, action=action)

        return None
```

</details>

### ⚙️ Method `get_images_from_picker`

```python
def get_images_from_picker(self, title: str = 'Select images', *, description: str = '', accept_button_text: str = 'OK') -> list[Path] | None
```

Show the standard ImagePicker and return selected image file paths.

Supports adding files, capturing a screenshot, pasting from the clipboard,
and drag-and-drop. Returns `None` if the dialog is cancelled or empty.

<details>
<summary>Code:</summary>

```python
def get_images_from_picker(
        self,
        title: str = "Select images",
        *,
        description: str = "",
        accept_button_text: str = "OK",
    ) -> list[Path] | None:
        dialog = TextImageSourceDialog(
            None,
            title=title,
            description=description,
            show_text=False,
            show_images=True,
            images_required=True,
            image_mode=ImagePickerMode.MULTI,
            image_label="Images (drag, paste Ctrl+V, screenshot, or add files):",
            accept_button_text=accept_button_text,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        paths = [Path(path) for path in dialog.get_image_paths() if Path(path).is_file()]
        return paths or None
```

</details>

### ⚙️ Method `get_max_image_size_option`

```python
def get_max_image_size_option(self, title: str = 'Image size limit', *, checkbox_label: str = 'Limit max image size (px)', default_enabled: bool = True, default_max_size: int = 1024) -> tuple[bool, int] | None
```

Ask whether to limit max image width/height.

Returns:

- `tuple[bool, int] | None`: `(enabled, max_size)` on accept, or `None` if cancelled.
  When `enabled` is `False`, `max_size` is the spinbox value (for persistence) but
  callers should treat the limit as unset.

<details>
<summary>Code:</summary>

```python
def get_max_image_size_option(
        self,
        title: str = "Image size limit",
        *,
        checkbox_label: str = "Limit max image size (px)",
        default_enabled: bool = True,
        default_max_size: int = 1024,
    ) -> tuple[bool, int] | None:
        checkbox: QCheckBox | None = None
        spin_box: QSpinBox | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal checkbox, spin_box

            row = QHBoxLayout()
            cb = QCheckBox(checkbox_label)
            cb.setChecked(default_enabled)
            row.addWidget(cb)

            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setMaximum(100_000)
            spin.setValue(max(1, default_max_size))
            spin.setEnabled(default_enabled)
            row.addWidget(spin)
            row.addStretch()
            layout.addLayout(row)

            def toggle_spin(checked: bool) -> None:  # noqa: FBT001
                spin.setEnabled(checked)

            cb.toggled.connect(toggle_spin)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            checkbox = cb
            spin_box = spin

        result, _dialog = self._exec_compact_dialog(title, _build)
        if result != QDialog.DialogCode.Accepted or checkbox is None or spin_box is None:
            return None
        return checkbox.isChecked(), spin_box.value()
```

</details>

### ⚙️ Method `get_open_filename`

```python
def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None
```

Return selected filename, or `None` if cancelled.

<details>
<summary>Code:</summary>

```python
def get_open_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        filename, _ = QFileDialog.getOpenFileName(None, title, default_path, filter_)
        if not filename:
            return None
        return Path(filename)
```

</details>

### ⚙️ Method `get_open_filenames`

```python
def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None
```

Return selected filenames, or `None` if cancelled.

<details>
<summary>Code:</summary>

```python
def get_open_filenames(self, title: str, default_path: str, filter_: str) -> list[Path] | None:
        dialog = DragDropFileDialog(title, default_path, filter_, self._default_size)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                return None
            return [Path(filename) for filename in filenames]
        return None
```

</details>

### ⚙️ Method `get_open_filenames_with_resize`

```python
def get_open_filenames_with_resize(self, title: str, default_path: str, filter_: str) -> tuple[list[Path] | None, bool, str | None]
```

Return filenames plus resize options, or (`None`, `False`, `None`) if cancelled.

<details>
<summary>Code:</summary>

```python
def get_open_filenames_with_resize(
        self,
        title: str,
        default_path: str,
        filter_: str,
    ) -> tuple[list[Path] | None, bool, str | None]:
        dialog = DragDropFileDialog(title, default_path, filter_, self._default_size, with_resize_option=True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filenames = dialog.get_selected_files()
            if not filenames:
                return None, False, None
            paths = [Path(f) for f in filenames]
            resize_enabled = dialog.get_resize_enabled()
            max_size = dialog.get_max_size()
            return paths, resize_enabled, max_size
        return None, False, None
```

</details>

### ⚙️ Method `get_path_input`

```python
def get_path_input(self, title: str, label: str, default_value: str | None = None) -> str | None
```

Return entered path, with an optional folder browse button.

<details>
<summary>Code:</summary>

```python
def get_path_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        line_edit: QLineEdit | None = None

        def _get_start_folder(path_text: str) -> str:
            path = Path(path_text).expanduser()
            if path.is_dir():
                return str(path)
            if path.parent.exists():
                return str(path.parent)
            return ""

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal line_edit

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            input_layout = QHBoxLayout()

            le = QLineEdit()
            le.setMinimumHeight(32)
            le.setText(default_value or "")
            input_layout.addWidget(le)

            browse_button = QPushButton("📁 Browse folder...")

            def on_browse_clicked() -> None:
                folder_path = QFileDialog.getExistingDirectory(
                    dialog,
                    "Select folder",
                    _get_start_folder(le.text().strip() or default_value or ""),
                )
                if folder_path:
                    le.setText(folder_path)

            browse_button.clicked.connect(on_browse_clicked)
            input_layout.addWidget(browse_button)

            layout.addLayout(input_layout)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            line_edit = le

        result, _dialog = self._exec_compact_dialog(title, _build)

        if result != QDialog.DialogCode.Accepted or line_edit is None:
            return None

        text = line_edit.text().strip()
        if not text:
            return None
        return text
```

</details>

### ⚙️ Method `get_save_filename`

```python
def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None
```

Return save target filename, or `None` if cancelled.

<details>
<summary>Code:</summary>

```python
def get_save_filename(self, title: str, default_path: str, filter_: str) -> Path | None:
        filename, _ = QFileDialog.getSaveFileName(None, title, default_path, filter_)
        if not filename:
            return None
        return Path(filename)
```

</details>

### ⚙️ Method `get_text_input`

```python
def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None
```

Return entered text, or `None` on cancel/empty.

<details>
<summary>Code:</summary>

```python
def get_text_input(self, title: str, label: str, default_value: str | None = None) -> str | None:
        text, ok = QInputDialog.getText(None, title, label, text=default_value or "")
        if not (ok and text):
            return None
        return text
```

</details>

### ⚙️ Method `get_text_input_with_auto`

```python
def get_text_input_with_auto(self, title: str, label: str, auto_generator: Callable[[], str] | None = None, auto_button_text: str = '🤖 Auto', validator: Callable[[str], str | None] | None = None) -> str | None
```

Return text input, optionally generated by callback, or `None` on cancel.

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
        if auto_generator is None:
            return self.get_text_input(title, label)

        line_edit: QLineEdit | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal line_edit

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            input_layout = QHBoxLayout()

            le = QLineEdit()
            le.setMinimumHeight(32)
            try:
                le.setText(auto_generator())
            except Exception as e:
                self._add_line(f"❌ Error generating auto text: {e}")
            input_layout.addWidget(le)

            auto_button = make_emoji_push_button(
                auto_button_text.removeprefix("🤖 ").strip() or "Auto",
                "🤖",
            )

            def on_auto_clicked() -> None:
                try:
                    auto_text = auto_generator()
                    le.setText(auto_text)
                except Exception as e:
                    self._add_line(f"❌ Error generating auto text: {e}")

            auto_button.clicked.connect(on_auto_clicked)
            input_layout.addWidget(auto_button)

            layout.addLayout(input_layout)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)

            def try_accept() -> None:
                text = le.text().strip()
                if not text:
                    message_box.warning(dialog, title, "Name must not be empty.")
                    return
                if validator is not None:
                    error = validator(text)
                    if error:
                        message_box.warning(dialog, title, error)
                        return
                le.setText(text)
                dialog.accept()

            buttons.accepted.connect(try_accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            line_edit = le

        result, _dialog = self._exec_compact_dialog(title, _build)

        if result == QDialog.DialogCode.Accepted:
            if line_edit is None:
                return None
            return line_edit.text().strip()

        return None
```

</details>

### ⚙️ Method `get_text_textarea`

```python
def get_text_textarea(self, title: str, label: str, default_text: str | None = None) -> str | None
```

Return multi-line text, or `None` on cancel/empty.

<details>
<summary>Code:</summary>

```python
def get_text_textarea(
        self,
        title: str,
        label: str,
        default_text: str | None = None,
    ) -> str | None:
        text_edit: QPlainTextEdit | None = None

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal text_edit

            label_widget = QLabel(label)
            layout.addWidget(label_widget)

            te = QPlainTextEdit()
            te.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            if default_text is not None:
                te.setPlainText(default_text)
            fit_widget_height(
                te,
                text_content_height(te),
                maximum=self._default_size.height() - 160,
            )
            layout.addWidget(te)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self._apply_emoji_dialog_buttons(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            text_edit = te

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)

        if result == QDialog.DialogCode.Accepted:
            if text_edit is None:
                return None
            text = text_edit.toPlainText()
            if not text.strip():
                return None
            return text
        return None
```

</details>

### ⚙️ Method `get_yes_no_question`

```python
def get_yes_no_question(self, title: str, message: str, *, default_yes: bool = False) -> bool
```

Return `True` for Yes, `False` otherwise.

<details>
<summary>Code:</summary>

```python
def get_yes_no_question(self, title: str, message: str, *, default_yes: bool = False) -> bool:
        default_button = QMessageBox.StandardButton.Yes if default_yes else QMessageBox.StandardButton.No
        reply = message_box.question(
            None,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            default_button,
        )
        return reply == QMessageBox.StandardButton.Yes
```

</details>

### ⚙️ Method `show_about_dialog`

```python
def show_about_dialog(self, *, title: str = 'About', app_name: str = 'Harrix Swiss Knife', version: str = '1.0.0', description: str = '', author: str = '', license_text: str = '', github: str = '') -> str | None
```

Show about dialog and return rendered text if accepted.

<details>
<summary>Code:</summary>

```python
def show_about_dialog(
        self,
        *,
        title: str = "About",
        app_name: str = "Harrix Swiss Knife",
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
        license_text: str = "",
        github: str = "",
    ) -> str | None:
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
            about_text += f"GitHub: [{github}]({github})\n\n"

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            logo_label = QLabel()
            logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            logo_label.setPixmap(QIcon(_ABOUT_LOGO_RESOURCE).pixmap(QSize(_ABOUT_LOGO_SIZE, _ABOUT_LOGO_SIZE)))
            logo_label.setFixedHeight(_ABOUT_LOGO_SIZE + 16)
            layout.addWidget(logo_label)

            text_browser = QTextBrowser()
            text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            text_browser.setMarkdown(about_text)
            text_browser.setOpenExternalLinks(True)

            font = QFont("JetBrains Mono", 10)
            text_browser.setFont(font)
            fit_widget_height(
                text_browser,
                text_content_height(text_browser),
                minimum=_ABOUT_TEXT_MIN_HEIGHT,
                maximum=self._default_size.height() - 160,
            )

            layout.addWidget(text_browser)

            button_layout = QHBoxLayout()
            copy_button = make_emoji_push_button("Copy to Clipboard", COPY_BUTTON_EMOJI)

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(about_text)
                self._show_toast("About information copied to Clipboard")

            copy_button.clicked.connect(click_copy_button)
            button_layout.addWidget(copy_button)

            ok_button = make_emoji_push_button("OK", OK_BUTTON_EMOJI)
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=1)
        return about_text if result == QDialog.DialogCode.Accepted else None
```

</details>

### ⚙️ Method `show_action_output_log_browser`

```python
def show_action_output_log_browser(self, entries: list[tuple[Path, str]], *, on_file_selected: Callable[[Path], None] | None = None) -> None
```

Show a split view: log file list (left) and UTF-8 preview (right).

<details>
<summary>Code:</summary>

```python
def show_action_output_log_browser(
        self,
        entries: list[tuple[Path, str]],
        *,
        on_file_selected: Callable[[Path], None] | None = None,
    ) -> None:
        if not entries:
            self._add_line("❌ No log files to browse.")
            return

        self._exec_standard_dialog(
            "Recent action logs",
            build_action_output_log_browser(
                entries,
                on_file_selected=on_file_selected,
                show_toast=self._show_toast,
            ),
            stretch_row=0,
        )
```

</details>

### ⚙️ Method `show_action_usage_stats_browser`

```python
def show_action_usage_stats_browser(self, rows: list[ActionUsageStatsRow], *, summary: str) -> None
```

Show a sortable table of action invocation statistics.

<details>
<summary>Code:</summary>

```python
def show_action_usage_stats_browser(
        self,
        rows: list[ActionUsageStatsRow],
        *,
        summary: str,
    ) -> None:
        dialog_parent = QApplication.activeWindow()
        dialog = QDialog(dialog_parent)
        dialog.setWindowTitle("Action usage stats")

        layout = QVBoxLayout()
        build_action_usage_stats_browser(rows, summary=summary)(dialog, layout)
        dialog.setLayout(layout)
        layout.setStretch(1, 1)

        # Same sizing as food/finance/habits main windows (maximize or ~1920 wide).
        apply_app_window_size_and_position(dialog)
        dialog.exec()
```

</details>

### ⚙️ Method `show_git_commit_offer`

```python
def show_git_commit_offer(self, commit_message: str, *, repo_path: Path | None = None) -> int
```

Offer to create a Git commit or copy the suggested commit message to the clipboard.

<details>
<summary>Code:</summary>

```python
def show_git_commit_offer(
        self,
        commit_message: str,
        *,
        repo_path: Path | None = None,
    ) -> int:
        dialog_parent = QApplication.activeWindow()
        dialog = QDialog(dialog_parent)
        dialog.setWindowTitle("Git commit")

        layout = QVBoxLayout()

        intro = "Create a git commit with the suggested commit message?"
        if repo_path is not None:
            intro += f"\n\nRepository:\n{repo_path}"
        else:
            intro += "\n\n⚠️ Git repository not found for the changed files."

        label_widget = QLabel(intro)
        label_widget.setWordWrap(True)
        layout.addWidget(label_widget)

        message_label = QLabel("Commit message:")
        layout.addWidget(message_label)

        message_edit = QLineEdit(commit_message)
        message_edit.setReadOnly(True)
        layout.addWidget(message_edit)

        button_layout = QHBoxLayout()
        create_button = make_emoji_push_button("Create commit", "✅")
        create_button.setEnabled(repo_path is not None)
        create_button.clicked.connect(lambda: dialog.done(COMMIT_OFFER_CREATE_CODE))
        button_layout.addWidget(create_button)

        copy_button = make_emoji_push_button("Copy commit message", "📋")
        copy_button.clicked.connect(lambda: dialog.done(COMMIT_OFFER_COPY_CODE))
        button_layout.addWidget(copy_button)

        close_button = make_emoji_push_button("Close", CANCEL_BUTTON_EMOJI)
        close_button.clicked.connect(dialog.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.setMinimumWidth(min(self._default_size.width(), 640))
        dialog.adjustSize()
        result = dialog.exec()

        if result == COMMIT_OFFER_COPY_CODE:
            QGuiApplication.clipboard().setText(commit_message)
            self._show_toast("Commit message copied to Clipboard")

        return result
```

</details>

### ⚙️ Method `show_instructions`

```python
def show_instructions(self, instructions: str, title: str = 'Instructions') -> str | None
```

Show instructions dialog and return text if accepted.

<details>
<summary>Code:</summary>

```python
def show_instructions(self, instructions: str, title: str = "Instructions") -> str | None:

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            text_browser = QTextBrowser()
            text_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            text_browser.setPlainText(instructions)

            font = QFont("JetBrains Mono", 10)
            text_browser.setFont(font)
            fit_widget_height(
                text_browser,
                text_content_height(text_browser),
                maximum=self._default_size.height() - 160,
            )

            layout.addWidget(text_browser)

            button_layout = QHBoxLayout()
            copy_button = make_emoji_push_button("Copy to Clipboard", COPY_BUTTON_EMOJI)

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(instructions)
                self._show_toast("Instructions copied to Clipboard")

            copy_button.clicked.connect(click_copy_button)
            button_layout.addWidget(copy_button)

            ok_button = make_emoji_push_button("OK", OK_BUTTON_EMOJI)
            ok_button.clicked.connect(dialog.accept)
            button_layout.addWidget(ok_button)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=0)
        return instructions if result == QDialog.DialogCode.Accepted else None
```

</details>

### ⚙️ Method `show_text_diff_side_by_side`

```python
def show_text_diff_side_by_side(self, before_text: str, after_text: str, title: str = 'Diff (Before/After)', *, rerun_button: bool = False, rerun_button_label: str = RERUN_BUTTON_LABEL, rerun_button_emoji: str = RERUN_BUTTON_EMOJI, remove_paragraphs_button: bool = False) -> tuple[str | None, int]
```

Show read-only before/after diff with inline change highlighting.

<details>
<summary>Code:</summary>

```python
def show_text_diff_side_by_side(
        self,
        before_text: str,
        after_text: str,
        title: str = "Diff (Before/After)",
        *,
        rerun_button: bool = False,
        rerun_button_label: str = RERUN_BUTTON_LABEL,
        rerun_button_emoji: str = RERUN_BUTTON_EMOJI,
        remove_paragraphs_button: bool = False,
    ) -> tuple[str | None, int]:
        result_text_holder = [after_text]
        result, _dialog = self._exec_standard_dialog(
            title,
            build_text_diff_side_by_side(
                before_text,
                after_text,
                self._default_size,
                self._show_toast,
                rerun_button=rerun_button,
                rerun_button_label=rerun_button_label,
                rerun_button_emoji=rerun_button_emoji,
                remove_paragraphs_button=remove_paragraphs_button,
                result_text_holder=result_text_holder,
            ),
            stretch_row=0,
        )
        final_text = result_text_holder[0]
        if result == RERUN_DIALOG_CODE:
            return final_text, result
        return (final_text if result == QDialog.DialogCode.Accepted else None, result)
```

</details>

### ⚙️ Method `show_text_multiline`

```python
def show_text_multiline(self, text: str, title: str = 'Result', *, open_folder_path: Path | str | None = None, rerun_button: bool = False, rerun_button_label: str = RERUN_BUTTON_LABEL, rerun_button_emoji: str = RERUN_BUTTON_EMOJI, rewrite_button: bool = False, remove_paragraphs_button: bool = False, save_button: bool = False, save_default_path: str | None = None, save_filter: str = 'Markdown Files (*.md);;All Files (*)') -> str | tuple[str | None, int] | None
```

Show read-only multi-line text dialog and return text if accepted.

<details>
<summary>Code:</summary>

```python
def show_text_multiline(
        self,
        text: str,
        title: str = "Result",
        *,
        open_folder_path: Path | str | None = None,
        rerun_button: bool = False,
        rerun_button_label: str = RERUN_BUTTON_LABEL,
        rerun_button_emoji: str = RERUN_BUTTON_EMOJI,
        rewrite_button: bool = False,
        remove_paragraphs_button: bool = False,
        save_button: bool = False,
        save_default_path: str | None = None,
        save_filter: str = "Markdown Files (*.md);;All Files (*)",
    ) -> str | tuple[str | None, int] | None:
        has_action_buttons = rerun_button or rewrite_button or remove_paragraphs_button
        folder_to_open = Path(open_folder_path) if open_folder_path is not None else None
        current_text = text

        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            nonlocal current_text
            text_edit = QPlainTextEdit()
            text_edit.setPlainText(current_text)
            text_edit.setReadOnly(True)
            text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            text_edit.setMinimumHeight(self._default_size.height() - 120)
            text_edit.moveCursor(QTextCursor.MoveOperation.End)

            font = QFont("JetBrains Mono")
            font.setPointSize(9)
            text_edit.setFont(font)

            layout.addWidget(text_edit)

            def _scroll_to_end() -> None:
                scrollbar = text_edit.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())

            # After showEvent resize and geometry enforce (both use singleShot(0)).
            QTimer.singleShot(0, lambda: QTimer.singleShot(0, _scroll_to_end))

            button_layout = QHBoxLayout()
            button_layout.addStretch(1)

            def click_copy_button() -> None:
                QGuiApplication.clipboard().setText(text_edit.toPlainText())
                self._show_toast("Copied to Clipboard")

            add_copy_button(button_layout, click_copy_button)

            if save_button:

                def click_save_markdown() -> None:
                    path = self.get_save_filename(
                        "Save Markdown",
                        save_default_path or "",
                        save_filter,
                    )
                    if path is None:
                        return
                    if path.suffix == "":
                        path = path.with_suffix(".md")
                    markdown = text_edit.toPlainText()
                    if not markdown.endswith("\n"):
                        markdown += "\n"
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(markdown, encoding="utf-8")
                    self._add_line(f"💾 Saved Markdown: {path}")
                    self._show_toast(f"Saved: {path.name}")

                add_save_markdown_button(button_layout, click_save_markdown)

            if folder_to_open is not None:

                def click_open_folder() -> None:
                    h.file.open_file_or_folder(folder_to_open)

                add_open_folder_button(button_layout, click_open_folder)

            def on_remove_paragraphs() -> None:
                nonlocal current_text
                current_text = collapse_text_to_single_line(text_edit.toPlainText())
                text_edit.setPlainText(current_text)
                QGuiApplication.clipboard().setText(current_text)
                self._show_toast("Converted to single line")
                if remove_paragraphs_btn is not None:
                    remove_paragraphs_btn.setVisible(False)

            remove_paragraphs_btn = append_result_action_buttons(
                dialog,
                button_layout,
                rerun_button=rerun_button,
                rerun_button_label=rerun_button_label,
                rerun_button_emoji=rerun_button_emoji,
                rewrite_button=rewrite_button,
                remove_paragraphs_button=remove_paragraphs_button,
                on_remove_paragraphs=on_remove_paragraphs if remove_paragraphs_button else None,
                remove_paragraphs_source_text=current_text,
            )

            add_ok_button(dialog, button_layout)

            layout.addLayout(button_layout)

        result, _dialog = self._exec_standard_dialog(title, _build, stretch_row=0, adaptive=False)
        if has_action_buttons:
            if result in (RERUN_DIALOG_CODE, REWRITE_DIALOG_CODE):
                return current_text, result
            return (current_text if result == QDialog.DialogCode.Accepted else None, result)
        return current_text if result == QDialog.DialogCode.Accepted else None
```

</details>

## 🏛️ Class `AndroidBuildDialogResult`

```python
class AndroidBuildDialogResult
```

Tray selection for Android APK build: folder, options, and install target.

<details>
<summary>Code:</summary>

```python
class AndroidBuildDialogResult:

    folder: Path
    build_all: bool
    release: bool
    device_id: str | None
```

</details>

## 🏛️ Class `IconChoiceSelection`

```python
class IconChoiceSelection
```

Result of an icon-grid picker, including optional secondary card actions.

<details>
<summary>Code:</summary>

```python
class IconChoiceSelection:

    title: str
    action: str = ICON_CHOICE_ACTION_SELECT
```

</details>
