---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `template_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TemplateDialog`](#%EF%B8%8F-class-templatedialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_field_values`](#%EF%B8%8F-method-get_field_values)
  - [⚙️ Method `get_selected_entry`](#%EF%B8%8F-method-get_selected_entry)

</details>

## 🏛️ Class `TemplateDialog`

```python
class TemplateDialog(QDialog)
```

Dynamic form dialog for template-based input.

This dialog generates input fields based on template field definitions
and collects user input to fill the template.

Attributes:

- `fields` (`list[TemplateField]`): List of fields in the template.
- `widgets` (`dict`): Dictionary mapping field names to input widgets.
- `field_values` (`dict[str, str]`): Dictionary of collected field values.
- `links` (`list[tuple[str, str]]`): Optional helper links shown in the dialog header.

<details>
<summary>Code:</summary>

```python
class TemplateDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        fields: list[TemplateField],
        title: str = "Fill Template",
        links: list[tuple[str, str]] | None = None,
        image_save_dir: Path | None = None,
        app_config: dict[str, Any] | None = None,
        initial_field_values: dict[str, str] | None = None,
        is_edit_mode: bool = False,
        entry_browser_groups: list[TemplateEntryBrowserGroup] | None = None,
        load_entry_values: Callable[[TemplateExistingEntry], dict[str, str] | None] | None = None,
        resolve_image_save_dir: Callable[[TemplateExistingEntry | None], Path | None] | None = None,
    ) -> None:
        """Initialize the template dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `fields` (`list[TemplateField]`): List of template fields to display.
        - `title` (`str`): Dialog title. Defaults to `Fill Template`.
        - `links` (`list[tuple[str, str]] | None`): Optional list of `(label, url)` helper links.
        - `image_save_dir` (`Path | None`): If set, image fields save into this dir/img/ and return relative path.
        - `app_config` (`dict[str, Any] | None`): Application config for BotHub text fix on multiline fields.
        - `initial_field_values` (`dict[str, str] | None`): Optional values to prefill widgets (e.g. edit mode).
        - `is_edit_mode` (`bool`): When `True`, restore filename base from existing images when present.
        - `entry_browser_groups` (`list[TemplateEntryBrowserGroup] | None`): Existing entries for left panel.
        - `load_entry_values` (`Callable | None`): Load field values when an existing entry is selected.
        - `resolve_image_save_dir` (`Callable | None`): Image save dir for add-new vs edit selection.

        """
        super().__init__(parent)
        self.fields = fields
        self.widgets: dict[str, QWidget] = {}
        self.field_values: dict[str, str] = {}
        self.links = links or []
        self._initial_field_values = initial_field_values or {}
        self._image_save_dir = Path(image_save_dir) if image_save_dir else None
        self._is_edit_mode = is_edit_mode
        self._app_config = app_config
        self._entry_browser_groups = entry_browser_groups
        self._load_entry_values = load_entry_values
        self._resolve_image_save_dir = resolve_image_save_dir
        self._entry_browser: TemplateEntryBrowserWidget | None = None
        self._selected_entry: TemplateExistingEntry | None = None
        self._bothub_state = BothubRequestState()
        self._date_field_locked: set[str] = set()
        self._multiline_ai_buttons: list[QPushButton] = []
        self._link_qurls: list[QUrl] = []
        for _, url in self.links:
            qurl = QUrl(url)
            if qurl.isValid():
                self._link_qurls.append(qurl)

        self.setWindowTitle(title)
        self.setModal(True)
        self._dialog_min_width = 1280 if entry_browser_groups else 1024
        self._dialog_min_height = 768

        self._setup_ui()
        QTimer.singleShot(0, self._apply_initial_geometry)

    def get_field_values(self) -> dict[str, str] | None:
        """Get the field values entered by the user.

        Returns:

        - `dict[str, str] | None`: Dictionary mapping field names to their values,
          or `None` if the dialog was cancelled.

        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self.field_values
        return None

    def get_selected_entry(self) -> TemplateExistingEntry | None:
        """Return selected existing entry, or `None` when Add new Entry was selected."""
        return self._selected_entry

    def _apply_dates_from_image_paths(self, image_field_name: str, source_paths: list[str]) -> None:
        """Update linked date fields from filenames of newly added images."""
        extracted = extract_dates_from_paths(source_paths)
        if not extracted:
            return
        for field in self.fields:
            if field.field_type != "date" or field.date_from_images != image_field_name:
                continue
            widget = self.widgets.get(field.name)
            if not isinstance(widget, QDateEdit):
                continue
            is_empty = self._is_date_field_empty(field, widget)
            new_date = resolve_date_from_image_batch(
                extracted,
                overwrite=field.date_from_images_overwrite,
                current_is_empty=is_empty,
            )
            if not new_date:
                continue
            date_obj = QDate.fromString(new_date, "yyyy-MM-dd")
            if not QDate.isValid(date_obj.year(), date_obj.month(), date_obj.day()):
                continue
            self._set_date_on_widget(widget, date_obj)
            if not field.date_from_images_overwrite:
                self._lock_date_field(field.name)
        self._refresh_image_filename_bases()

    def _apply_initial_geometry(self) -> None:
        """Size the dialog to use available screen height when content needs more than the minimum."""
        margin = 40
        self.setMinimumSize(self._dialog_min_width, self._dialog_min_height)

        screen = QGuiApplication.primaryScreen()
        if screen is None:
            self.resize(self._dialog_min_width, self._dialog_min_height)
            return

        available = screen.availableGeometry()
        max_width = max(self._dialog_min_width, available.width() - margin)
        max_height = max(self._dialog_min_height, available.height() - margin)
        width = min(self._dialog_min_width, max_width)

        layout = self.layout()
        if layout is not None:
            layout.activate()

        form_widget = getattr(self, "_form_widget", None)
        if form_widget is not None:
            form_widget.adjustSize()
            form_height = form_widget.sizeHint().height()
            chrome_height = self.sizeHint().height() - form_height
            if chrome_height < _MIN_CHROME_HEIGHT_HINT:
                chrome_height = _DEFAULT_CHROME_HEIGHT
            content_height = form_height + chrome_height
            height = min(max(content_height, self._dialog_min_height), max_height)
        else:
            height = min(max(self._dialog_min_height, available.height() - margin), max_height)

        self.resize(width, height)
        x = available.x() + (available.width() - width) // 2
        y = available.y() + (available.height() - height) // 2
        self.move(x, y)

    def _apply_initial_values(self) -> None:
        """Prefill widgets from `initial_field_values` when editing an existing entry."""
        for field in self.fields:
            value = self._initial_field_values.get(field.name)
            if value is None:
                continue
            widget = self.widgets.get(field.name)
            if widget is None:
                continue

            if field.field_type == "line" and isinstance(widget, QLineEdit):
                widget.setText(value)
            elif field.field_type == "int" and isinstance(widget, QSpinBox):
                with contextlib.suppress(ValueError):
                    widget.setValue(int(value))
            elif field.field_type == "float" and isinstance(widget, QDoubleSpinBox):
                with contextlib.suppress(ValueError):
                    widget.setValue(float(value.replace(",", ".")))
            elif field.field_type == "date" and isinstance(widget, QDateEdit):
                if not (value or "").strip():
                    if self._uses_empty_date_sentinel(field):
                        self._set_date_edit_to_empty(widget)
                    continue
                date_obj = QDate.fromString(value, "yyyy-MM-dd")
                if QDate.isValid(date_obj.year(), date_obj.month(), date_obj.day()):
                    self._set_date_on_widget(widget, date_obj)
                    self._lock_date_field(field.name)
            elif field.field_type == "bool" and isinstance(widget, QCheckBox):
                widget.setChecked(value.lower() in ["true", "1", "yes"])
            elif field.field_type == "multiline" and isinstance(widget, QPlainTextEdit):
                widget.setPlainText(value)
            elif field.field_type == "image" and isinstance(widget, ImagePicker):
                widget.set_image_path(value)
            elif field.field_type == "images" and isinstance(widget, ImagePicker):
                paths = [path.strip() for path in value.split(",") if path.strip()]
                widget.set_image_paths(paths)
            elif field.field_type == "file" and isinstance(widget, FileDropWidget):
                widget.set_file_path(value)
            elif field.field_type == "files" and isinstance(widget, FilesListWidget):
                paths = [path.strip() for path in value.split(",") if path.strip()]
                widget.set_file_paths(paths)
            elif field.field_type == "combobox" and isinstance(widget, QComboBox):
                index = widget.findText(value)
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    widget.setCurrentText(value)
            elif isinstance(widget, QLineEdit):
                widget.setText(value)

    def _create_coordinates_widget_for_field(self, field: TemplateField) -> tuple[QWidget, QLineEdit]:
        """Create coordinates input with clipboard paste buttons for map URLs."""
        line_edit = QLineEdit()
        if field.default_value:
            line_edit.setText(field.default_value)
        else:
            line_edit.setPlaceholderText("55.7558, 37.6173")

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(line_edit, 1)

        for label, service in (
            ("Google", "Google Maps"),
            ("Yandex", "Yandex Maps"),
            ("OSM", "OpenStreetMap"),
        ):
            button = QPushButton(f"📋 {label}")
            button.setToolTip(f"Paste {service} link from clipboard and extract coordinates")
            button.clicked.connect(lambda _checked=False, s=service: self._on_paste_map_url(line_edit, s))
            layout.addWidget(button)

        return container, line_edit

    def _create_date_widget_for_field(self, field: TemplateField) -> tuple[QWidget, QDateEdit]:
        """Create a date input with quick Today/Yesterday buttons."""
        date_edit = self._create_widget_for_field(field)
        if not isinstance(date_edit, QDateEdit):
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat("yyyy-MM-dd")
            if self._uses_empty_date_sentinel(field):
                self._set_date_edit_to_empty(date_edit)
            else:
                date_edit.setDate(QDate.currentDate())
            self._finalize_date_edit(field, date_edit)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        today_button = QPushButton("📅 Today")
        today_button.clicked.connect(lambda: date_edit.setDate(QDate.currentDate()))

        yesterday_button = QPushButton("📅 Yesterday")
        yesterday_button.clicked.connect(lambda: date_edit.setDate(QDate.currentDate().addDays(-1)))

        layout.addWidget(date_edit, 1)
        layout.addWidget(today_button)
        layout.addWidget(yesterday_button)

        return container, date_edit

    def _create_multiline_widget_for_field(self, field: TemplateField) -> tuple[QWidget, QPlainTextEdit]:
        """Create multiline input with optional Fix with AI and Speech to text buttons."""
        text_edit = self._create_widget_for_field(field)
        if not isinstance(text_edit, QPlainTextEdit):
            text_edit = QPlainTextEdit()

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(text_edit, 1)

        buttons_column = QVBoxLayout()
        buttons_column.setContentsMargins(0, 0, 0, 0)

        fix_button = QPushButton("🤖 Fix with AI")
        if self._app_config is None:
            fix_button.setEnabled(False)
            fix_button.setToolTip("BotHub is not configured for this dialog.")
        else:
            fix_button.clicked.connect(lambda: self._on_fix_multiline_clicked(text_edit))
        buttons_column.addWidget(fix_button)
        self._multiline_ai_buttons.append(fix_button)

        speech_button = QPushButton("🎙️ Speech to text")
        if self._app_config is None:
            speech_button.setEnabled(False)
            speech_button.setToolTip("BotHub is not configured for this dialog.")
        else:
            speech_button.clicked.connect(lambda: self._on_speech_multiline_clicked(text_edit))
        buttons_column.addWidget(speech_button)
        self._multiline_ai_buttons.append(speech_button)
        buttons_column.addStretch()

        layout.addLayout(buttons_column)

        return container, text_edit

    def _create_widget_for_field(self, field: TemplateField) -> QWidget:
        """Create an appropriate input widget for a field type.

        Args:

        - `field` (`TemplateField`): The field to create a widget for.

        Returns:

        - `QWidget`: The created input widget.

        """
        if field.field_type == "line":
            widget = QLineEdit()
            if field.default_value:
                widget.setText(field.default_value)
            else:
                widget.setPlaceholderText(f"Enter {field.name.lower()}")
            return widget

        if field.field_type == "int":
            widget = QSpinBox()
            widget.setRange(0, 1000)
            widget.setSingleStep(1)
            if field.default_value:
                try:
                    widget.setValue(int(field.default_value))
                except ValueError:
                    widget.setValue(0)
            else:
                widget.setValue(0)
            return widget

        if field.field_type == "float":
            widget = QDoubleSpinBox()
            widget.setRange(0.0, 100.0)
            widget.setDecimals(1)
            widget.setSingleStep(0.5)
            if field.default_value:
                try:
                    widget.setValue(float(field.default_value))
                except ValueError:
                    widget.setValue(0.0)
            else:
                widget.setValue(0.0)
            return widget

        if field.field_type == "date":
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDisplayFormat("yyyy-MM-dd")
            if field.default_value:
                try:
                    date_obj = QDate.fromString(field.default_value, "yyyy-MM-dd")
                    if QDate.isValid(date_obj.year(), date_obj.month(), date_obj.day()):
                        widget.setDate(date_obj)
                    elif self._uses_empty_date_sentinel(field):
                        self._set_date_edit_to_empty(widget)
                    else:
                        widget.setDate(QDate.currentDate())
                except Exception:
                    if self._uses_empty_date_sentinel(field):
                        self._set_date_edit_to_empty(widget)
                    else:
                        widget.setDate(QDate.currentDate())
            elif self._uses_empty_date_sentinel(field):
                self._set_date_edit_to_empty(widget)
            else:
                widget.setDate(QDate.currentDate())
            self._finalize_date_edit(field, widget)
            return widget

        if field.field_type == "bool":
            widget = QCheckBox()
            if field.default_value:
                # Parse boolean values (true, false, 1, 0, yes, no)
                is_checked = field.default_value.lower() in ["true", "1", "yes"]
                widget.setChecked(is_checked)
            else:
                widget.setChecked(False)
            return widget

        if field.field_type == "multiline":
            widget = QPlainTextEdit()
            if field.default_value:
                widget.setPlainText(field.default_value)
            else:
                widget.setPlaceholderText(f"Enter {field.name.lower()}")
            widget.setMinimumHeight(100)
            return widget

        if field.field_type == "image":
            widget = ImagePicker(mode=ImagePickerMode.SINGLE, save_dir=self._image_save_dir)
            if field.default_value:
                widget.set_image_path(field.default_value)
            return widget

        if field.field_type == "images":
            widget = ImagePicker(mode=ImagePickerMode.MULTI, save_dir=self._image_save_dir)
            if field.default_value:
                # Parse comma-separated paths
                paths = [path.strip() for path in field.default_value.split(",") if path.strip()]
                widget.set_image_paths(paths)
            return widget

        if field.field_type == "file":
            widget = FileDropWidget()
            if field.default_value:
                widget.set_file_path(field.default_value)
            return widget

        if field.field_type == "files":
            widget = FilesListWidget()
            if field.default_value:
                # Parse comma-separated paths
                paths = [path.strip() for path in field.default_value.split(",") if path.strip()]
                widget.set_file_paths(paths)
            return widget

        if field.field_type == "combobox":
            widget = QComboBox()
            widget.setEditable(True)  # Allow user to type custom value
            # Set size policy to expand like multiline fields
            size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            widget.setSizePolicy(size_policy)
            if field.options:
                widget.addItems(field.options)
                # Apply smart filtering
                apply_smart_filtering(widget)
            if field.default_value:
                # Try to set default value, if it's in options, select it, otherwise set as current text
                index = widget.findText(field.default_value)
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    widget.setCurrentText(field.default_value)
            else:
                # Set empty text if no default value
                widget.setCurrentText("")
            return widget

        if field.field_type == "coordinates":
            widget = QLineEdit()
            if field.default_value:
                widget.setText(field.default_value)
            else:
                widget.setPlaceholderText("55.7558, 37.6173")
            return widget

        # Default to line edit for unknown types
        widget = QLineEdit()
        if field.default_value:
            widget.setText(field.default_value)
        else:
            widget.setPlaceholderText(f"Enter {field.name.lower()}")
        return widget

    def _finalize_date_edit(self, field: TemplateField, date_edit: QDateEdit) -> None:
        """Configure date widget behavior for template-linked date fields."""
        date_edit.setMinimumDate(_EMPTY_DATE)
        date_edit.dateChanged.connect(lambda _date, name=field.name: self._on_date_field_edited(name))

    def _get_widget_value(self, field: TemplateField, widget: QWidget) -> str:
        """Get the value from a widget based on field type.

        Args:

        - `field` (`TemplateField`): The field definition.
        - `widget` (`QWidget`): The widget to extract value from.

        Returns:

        - `str`: The string representation of the widget's value.

        """
        if field.field_type == "line":
            return widget.text() if isinstance(widget, QLineEdit) else ""

        if field.field_type == "int":
            return str(widget.value()) if isinstance(widget, QSpinBox) else "0"

        if field.field_type == "float":
            if isinstance(widget, QDoubleSpinBox):
                value = widget.value()
                # If the value is a whole number, return it without decimal part
                if value == int(value):
                    return str(int(value))
                return str(value)
            return "0.0"

        if field.field_type == "date":
            if isinstance(widget, QDateEdit):
                if widget.date() == _EMPTY_DATE:
                    return ""
                return widget.date().toString("yyyy-MM-dd")
            return ""

        if field.field_type == "bool":
            if isinstance(widget, QCheckBox):
                return "true" if widget.isChecked() else "false"
            return "false"

        if field.field_type == "multiline":
            return widget.toPlainText() if isinstance(widget, QPlainTextEdit) else ""

        if field.field_type == "image":
            return widget.get_image_path() if isinstance(widget, ImagePicker) else ""

        if field.field_type == "images":
            if isinstance(widget, ImagePicker):
                return ",".join(widget.get_image_paths())
            return ""

        if field.field_type == "file":
            return widget.get_file_path() if isinstance(widget, FileDropWidget) else ""

        if field.field_type == "files":
            if isinstance(widget, FilesListWidget):
                return ",".join(widget.get_file_paths())
            return ""

        if field.field_type == "combobox":
            if isinstance(widget, QComboBox):
                return widget.currentText()
            return ""

        if field.field_type == "coordinates":
            return widget.text().strip() if isinstance(widget, QLineEdit) else ""

        # Default to line edit
        return widget.text() if isinstance(widget, QLineEdit) else ""

    def _is_date_field_empty(self, field: TemplateField, widget: QDateEdit) -> bool:
        if field.name in self._date_field_locked:
            return False
        return widget.date() == _EMPTY_DATE

    def _load_entry_into_form(self, entry: TemplateExistingEntry | None) -> None:
        """Switch form between add-new defaults and an existing entry."""
        self._selected_entry = entry
        self._reset_form_to_defaults()
        if entry is None:
            self._is_edit_mode = False
            self._initial_field_values = {}
        else:
            if self._load_entry_values is None:
                return
            loaded = self._load_entry_values(entry)
            if not loaded:
                return
            self._is_edit_mode = True
            self._initial_field_values = loaded
            self._apply_initial_values()

        if self._resolve_image_save_dir is not None:
            self._update_image_save_dir(self._resolve_image_save_dir(entry))
        self._wire_image_filename_rows()

    def _lock_date_field(self, field_name: str) -> None:
        self._date_field_locked.add(field_name)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.reject()

    def _on_date_field_edited(self, field_name: str) -> None:
        field = next((item for item in self.fields if item.name == field_name), None)
        if field is None or field.date_from_images_overwrite:
            return
        if self.widgets.get(field_name) is not None:
            widget = self.widgets[field_name]
            if isinstance(widget, QDateEdit) and widget.date() != _EMPTY_DATE:
                self._lock_date_field(field_name)

    def _on_entry_selection_changed(self, entry: TemplateExistingEntry | None) -> None:
        """Handle entry tree selection."""
        self._load_entry_into_form(entry)

    def _on_fix_multiline_clicked(self, text_edit: QPlainTextEdit) -> None:
        """Send multiline field text to BotHub and replace with corrected text."""
        if self._app_config is None:
            return

        input_text = text_edit.toPlainText()
        if not input_text.strip():
            message_box.warning(self, "Fix text with AI", "Text is empty.")
            return

        if self._bothub_state.worker is not None:
            return

        try:
            prompt_text = build_text_fix_prompt(input_text, self._app_config)
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        self._set_multiline_ai_buttons_enabled(False)  # noqa: FBT003

        def on_success(response_text: str) -> None:
            self._set_multiline_ai_buttons_enabled(True)  # noqa: FBT003
            if not response_text.strip():
                message_box.critical(self, "BotHub Error", "Empty response from BotHub.")
                return
            text_edit.setPlainText(response_text)

        def on_error(message: str) -> None:
            self._set_multiline_ai_buttons_enabled(True)  # noqa: FBT003
            message_box.critical(self, "BotHub Error", message)

        run_bothub_request(
            self,
            self._app_config,
            prompt_text,
            on_success,
            is_busy=lambda: self._bothub_state.worker is not None,
            state=self._bothub_state,
            on_error=on_error,
        )

    def _on_ok(self) -> None:
        """Handle OK button click and collect field values."""
        if self._entry_browser is not None:
            self._selected_entry = self._entry_browser.get_selected_entry()

        self.field_values = {}

        for field in self.fields:
            widget = self.widgets.get(field.name)
            if widget:
                value = self._get_widget_value(field, widget)
                self.field_values[field.name] = value

        self.accept()

    def _on_paste_map_url(self, line_edit: QLineEdit, service_name: str) -> None:
        """Read a map URL from the clipboard and fill coordinates."""
        url = QGuiApplication.clipboard().text().strip()
        if not url:
            message_box.warning(self, "Coordinates", "Clipboard is empty. Copy a map link first.")
            return

        coords = parse_coordinates_from_map_url(url)
        if coords is None:
            message_box.warning(
                self,
                "Coordinates",
                f"Could not extract coordinates from the clipboard URL ({service_name}).",
            )
            return

        line_edit.setText(format_coordinates(coords[0], coords[1]))

    def _on_speech_multiline_clicked(self, text_edit: QPlainTextEdit) -> None:
        """Transcribe speech and insert corrected text into the multiline field."""
        app_config = self._app_config
        if app_config is None:
            return

        if self._bothub_state.worker is not None:
            return

        dialog = AudioSourceDialog(self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        audio_path = dialog.get_audio_path()
        if not audio_path:
            return

        try:
            audio_data = audio_bytes_and_mime(audio_path)
        except ValueError as exc:
            message_box.critical(self, "Audio Error", str(exc))
            return

        self._set_multiline_ai_buttons_enabled(False)  # noqa: FBT003

        def on_transcription_error(message: str) -> None:
            self._set_multiline_ai_buttons_enabled(True)  # noqa: FBT003
            message_box.critical(self, "BotHub Error", message)

        def on_fix_success(fixed_text: str) -> None:
            self._set_multiline_ai_buttons_enabled(True)  # noqa: FBT003
            if not fixed_text.strip():
                message_box.critical(self, "BotHub Error", "Empty response from BotHub.")
                return
            text_edit.setPlainText(fixed_text)

        def on_fix_error(message: str) -> None:
            self._set_multiline_ai_buttons_enabled(True)  # noqa: FBT003
            message_box.critical(self, "BotHub Error", message)

        def on_transcription_success(transcribed_text: str) -> None:
            if not transcribed_text.strip():
                self._set_multiline_ai_buttons_enabled(True)  # noqa: FBT003
                message_box.critical(self, "BotHub Error", "Empty transcription from BotHub.")
                return

            try:
                fix_prompt = build_text_fix_prompt(transcribed_text, app_config)
            except ValueError as exc:
                self._set_multiline_ai_buttons_enabled(True)  # noqa: FBT003
                show_bothub_prompt_build_error(self, exc)
                return

            run_bothub_request(
                self,
                app_config,
                fix_prompt,
                on_fix_success,
                toast_message="Fixing text…",
                is_busy=lambda: self._bothub_state.worker is not None,
                state=self._bothub_state,
                on_error=on_fix_error,
            )

        run_bothub_request(
            self,
            app_config,
            build_transcription_prompt(),
            on_transcription_success,
            audio=audio_data,
            model=get_speech_model(app_config),
            toast_message="Recognizing speech…",
            is_busy=lambda: self._bothub_state.worker is not None,
            state=self._bothub_state,
            on_error=on_transcription_error,
        )

    def _open_all_links(self) -> None:
        """Open all helper links in the default browser."""
        for qurl in self._link_qurls:
            QDesktopServices.openUrl(qurl)

    def _refresh_image_filename_bases(self) -> None:
        """Update filename base rows after date fields change."""
        for field in self.fields:
            if field.field_type not in ("image", "images"):
                continue
            widget = self.widgets.get(field.name)
            if isinstance(widget, ImagePicker):
                widget.refresh_filename_base()

    def _reset_form_to_defaults(self) -> None:
        """Reset all field widgets to template defaults."""
        self._date_field_locked.clear()
        for field in self.fields:
            widget = self.widgets.get(field.name)
            if widget is None:
                continue

            if field.field_type == "line" and isinstance(widget, QLineEdit):
                widget.clear()
                if field.default_value:
                    widget.setText(field.default_value)
            elif field.field_type == "int" and isinstance(widget, QSpinBox):
                if field.default_value:
                    with contextlib.suppress(ValueError):
                        widget.setValue(int(field.default_value))
                        continue
                widget.setValue(0)
            elif field.field_type == "float" and isinstance(widget, QDoubleSpinBox):
                if field.default_value:
                    with contextlib.suppress(ValueError):
                        widget.setValue(float(field.default_value.replace(",", ".")))
                        continue
                widget.setValue(0.0)
            elif field.field_type == "date" and isinstance(widget, QDateEdit):
                if field.default_value:
                    date_obj = QDate.fromString(field.default_value, "yyyy-MM-dd")
                    if QDate.isValid(date_obj.year(), date_obj.month(), date_obj.day()):
                        self._set_date_on_widget(widget, date_obj)
                        continue
                if self._uses_empty_date_sentinel(field):
                    self._set_date_edit_to_empty(widget)
                else:
                    self._set_date_on_widget(widget, QDate.currentDate())
            elif field.field_type == "bool" and isinstance(widget, QCheckBox):
                widget.setChecked(field.default_value.lower() in ["true", "1", "yes"] if field.default_value else False)
            elif field.field_type == "multiline" and isinstance(widget, QPlainTextEdit):
                widget.setPlainText(field.default_value or "")
            elif field.field_type == "image" and isinstance(widget, ImagePicker):
                widget.set_image_path(field.default_value or "")
            elif field.field_type == "images" and isinstance(widget, ImagePicker):
                paths = [path.strip() for path in (field.default_value or "").split(",") if path.strip()]
                widget.set_image_paths(paths)
            elif field.field_type == "file" and isinstance(widget, FileDropWidget):
                widget.set_file_path(field.default_value or "")
            elif field.field_type == "files" and isinstance(widget, FilesListWidget):
                paths = [path.strip() for path in (field.default_value or "").split(",") if path.strip()]
                widget.set_file_paths(paths)
            elif field.field_type == "combobox" and isinstance(widget, QComboBox):
                if field.default_value:
                    index = widget.findText(field.default_value)
                    if index >= 0:
                        widget.setCurrentIndex(index)
                    else:
                        widget.setCurrentText(field.default_value)
                else:
                    widget.setCurrentIndex(0)
            elif isinstance(widget, QLineEdit):
                widget.clear()
                if field.default_value:
                    widget.setText(field.default_value)

    def _set_date_edit_to_empty(self, widget: QDateEdit) -> None:
        widget.blockSignals(True)  # noqa: FBT003
        widget.setMinimumDate(_EMPTY_DATE)
        widget.setDate(_EMPTY_DATE)
        widget.setSpecialValueText("—")
        widget.blockSignals(False)  # noqa: FBT003

    def _set_date_on_widget(self, widget: QDateEdit, date_obj: QDate) -> None:
        widget.blockSignals(True)  # noqa: FBT003
        widget.setDate(date_obj)
        widget.blockSignals(False)  # noqa: FBT003

    def _set_multiline_ai_buttons_enabled(self, enabled: bool) -> None:  # noqa: FBT001
        """Enable or disable Fix with AI / Speech to text buttons on multiline fields."""
        for button in self._multiline_ai_buttons:
            if self._app_config is not None:
                button.setEnabled(enabled)

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        main_layout = QVBoxLayout()

        if self.links:
            links_layout = QHBoxLayout()
            links_layout.setSpacing(10)
            for label, url in self.links:
                link_label = QLabel(f'<a href="{url}">{label}</a>')
                link_label.setTextFormat(Qt.TextFormat.RichText)
                link_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
                link_label.setOpenExternalLinks(True)
                links_layout.addWidget(link_label)
            if len(self._link_qurls) > 1:
                open_all_button = make_emoji_push_button("Open all", "🔗")
                open_all_button.clicked.connect(self._open_all_links)
                links_layout.addWidget(open_all_button)
            links_layout.addStretch()
            main_layout.addLayout(links_layout)

        # Create scroll area for form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create form widget
        form_widget = QWidget()
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Create widgets for each field
        for field in self.fields:
            if field.field_type == "date":
                widget, date_edit = self._create_date_widget_for_field(field)
                self.widgets[field.name] = date_edit
            elif field.field_type == "multiline":
                widget, text_edit = self._create_multiline_widget_for_field(field)
                self.widgets[field.name] = text_edit
            elif field.field_type == "coordinates":
                widget, line_edit = self._create_coordinates_widget_for_field(field)
                self.widgets[field.name] = line_edit
            else:
                widget = self._create_widget_for_field(field)
                self.widgets[field.name] = widget

            # Create label with field name
            label = QLabel(f"{field.name}:")
            label.setMinimumWidth(150)

            form_layout.addRow(label, widget)

        # When template has Date and image/images field, show Filename row inside widget (synced with Date)
        if self._entry_browser_groups is None:
            self._apply_initial_values()
            self._wire_image_filename_rows()
        else:
            self._load_entry_into_form(None)

        self._wire_date_from_images()

        self._form_widget = form_widget
        form_widget.setLayout(form_layout)
        scroll_area.setWidget(form_widget)

        if self._entry_browser_groups is not None:
            splitter = QSplitter(Qt.Orientation.Horizontal)
            self._entry_browser = TemplateEntryBrowserWidget()
            self._entry_browser.set_groups(self._entry_browser_groups)
            self._entry_browser.selection_changed.connect(self._on_entry_selection_changed)
            splitter.addWidget(self._entry_browser)
            splitter.addWidget(scroll_area)
            splitter.setSizes([300, 900])
            main_layout.addWidget(splitter, 1)
        else:
            main_layout.addWidget(scroll_area, 1)

        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = make_emoji_push_button("Cancel", CANCEL_BUTTON_EMOJI)
        cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(cancel_button)

        ok_button = make_emoji_push_button("OK", OK_BUTTON_EMOJI)
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_ok)
        ok_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        button_layout.addWidget(ok_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _update_image_save_dir(self, save_dir: Path | None) -> None:
        """Update image widgets when switching between add-new and edit targets."""
        self._image_save_dir = Path(save_dir) if save_dir else None
        for field in self.fields:
            if field.field_type not in ("image", "images"):
                continue
            widget = self.widgets.get(field.name)
            if isinstance(widget, ImagePicker):
                widget.set_save_dir(self._image_save_dir)

    def _uses_empty_date_sentinel(self, field: TemplateField) -> bool:
        return field.field_type == "date" and bool(field.date_from_images) and not field.default_value

    def _wire_date_from_images(self) -> None:
        """Connect image widgets so linked date fields update from dropped filenames."""
        for field in self.fields:
            if field.field_type not in ("image", "images"):
                continue
            widget = self.widgets.get(field.name)
            if not isinstance(widget, ImagePicker):
                continue
            image_field_name = field.name

            def handler(paths: list[str], name: str = image_field_name) -> None:
                self._apply_dates_from_image_paths(name, paths)

            widget.set_on_paths_added(handler)

    def _wire_image_filename_rows(self) -> None:
        """Attach filename base rows to image widgets after initial values are applied."""
        date_widget = self.widgets.get("Date")
        date_edit = date_widget if isinstance(date_widget, QDateEdit) else None

        for field in self.fields:
            if field.field_type not in ("image", "images"):
                continue
            widget = self.widgets.get(field.name)
            if not isinstance(widget, ImagePicker):
                continue

            widget.reset_filename_row()

            source_widget: QLineEdit | QComboBox | None = None
            source_field_name = field.field_link if field.field_type in ("image", "images") else None
            if source_field_name:
                candidate = self.widgets.get(source_field_name)
                if isinstance(candidate, (QLineEdit, QComboBox)):
                    source_widget = candidate

            initial_base: str | None = None
            lock_auto_sync = False
            if self._is_edit_mode:
                image_value = self._initial_field_values.get(field.name, "")
                paths = [path.strip() for path in image_value.split(",") if path.strip()]
                if paths:
                    inferred = infer_image_filename_base(paths)
                    if inferred:
                        initial_base = inferred
                        lock_auto_sync = True

            widget.configure_filename_row(
                date_edit,
                source_widget,
                source_field_name=source_field_name,
                initial_base=initial_base,
                lock_auto_sync=lock_auto_sync,
            )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the template dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `fields` (`list[TemplateField]`): List of template fields to display.
- `title` (`str`): Dialog title. Defaults to `Fill Template`.
- `links` (`list[tuple[str, str]] | None`): Optional list of `(label, url)` helper links.
- `image_save_dir` (`Path | None`): If set, image fields save into this dir/img/ and return relative path.
- `app_config` (`dict[str, Any] | None`): Application config for BotHub text fix on multiline fields.
- `initial_field_values` (`dict[str, str] | None`): Optional values to prefill widgets (e.g. edit mode).
- `is_edit_mode` (`bool`): When `True`, restore filename base from existing images when present.
- `entry_browser_groups` (`list[TemplateEntryBrowserGroup] | None`): Existing entries for left panel.
- `load_entry_values` (`Callable | None`): Load field values when an existing entry is selected.
- `resolve_image_save_dir` (`Callable | None`): Image save dir for add-new vs edit selection.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        fields: list[TemplateField],
        title: str = "Fill Template",
        links: list[tuple[str, str]] | None = None,
        image_save_dir: Path | None = None,
        app_config: dict[str, Any] | None = None,
        initial_field_values: dict[str, str] | None = None,
        is_edit_mode: bool = False,
        entry_browser_groups: list[TemplateEntryBrowserGroup] | None = None,
        load_entry_values: Callable[[TemplateExistingEntry], dict[str, str] | None] | None = None,
        resolve_image_save_dir: Callable[[TemplateExistingEntry | None], Path | None] | None = None,
    ) -> None:
        super().__init__(parent)
        self.fields = fields
        self.widgets: dict[str, QWidget] = {}
        self.field_values: dict[str, str] = {}
        self.links = links or []
        self._initial_field_values = initial_field_values or {}
        self._image_save_dir = Path(image_save_dir) if image_save_dir else None
        self._is_edit_mode = is_edit_mode
        self._app_config = app_config
        self._entry_browser_groups = entry_browser_groups
        self._load_entry_values = load_entry_values
        self._resolve_image_save_dir = resolve_image_save_dir
        self._entry_browser: TemplateEntryBrowserWidget | None = None
        self._selected_entry: TemplateExistingEntry | None = None
        self._bothub_state = BothubRequestState()
        self._date_field_locked: set[str] = set()
        self._multiline_ai_buttons: list[QPushButton] = []
        self._link_qurls: list[QUrl] = []
        for _, url in self.links:
            qurl = QUrl(url)
            if qurl.isValid():
                self._link_qurls.append(qurl)

        self.setWindowTitle(title)
        self.setModal(True)
        self._dialog_min_width = 1280 if entry_browser_groups else 1024
        self._dialog_min_height = 768

        self._setup_ui()
        QTimer.singleShot(0, self._apply_initial_geometry)
```

</details>

### ⚙️ Method `get_field_values`

```python
def get_field_values(self) -> dict[str, str] | None
```

Get the field values entered by the user.

Returns:

- `dict[str, str] | None`: Dictionary mapping field names to their values,
  or `None` if the dialog was cancelled.

<details>
<summary>Code:</summary>

```python
def get_field_values(self) -> dict[str, str] | None:
        if self.result() == QDialog.DialogCode.Accepted:
            return self.field_values
        return None
```

</details>

### ⚙️ Method `get_selected_entry`

```python
def get_selected_entry(self) -> TemplateExistingEntry | None
```

Return selected existing entry, or `None` when Add new Entry was selected.

<details>
<summary>Code:</summary>

```python
def get_selected_entry(self) -> TemplateExistingEntry | None:
        return self._selected_entry
```

</details>
