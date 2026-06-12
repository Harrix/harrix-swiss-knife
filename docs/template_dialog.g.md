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
  - [⚙️ Method `_create_date_widget_for_field`](#%EF%B8%8F-method-_create_date_widget_for_field)
  - [⚙️ Method `_create_multiline_widget_for_field`](#%EF%B8%8F-method-_create_multiline_widget_for_field)
  - [⚙️ Method `_create_widget_for_field`](#%EF%B8%8F-method-_create_widget_for_field)
  - [⚙️ Method `_get_widget_value`](#%EF%B8%8F-method-_get_widget_value)
  - [⚙️ Method `_on_cancel`](#%EF%B8%8F-method-_on_cancel)
  - [⚙️ Method `_on_fix_multiline_clicked`](#%EF%B8%8F-method-_on_fix_multiline_clicked)
  - [⚙️ Method `_on_ok`](#%EF%B8%8F-method-_on_ok)
  - [⚙️ Method `_open_all_links`](#%EF%B8%8F-method-_open_all_links)
  - [⚙️ Method `_set_fix_buttons_enabled`](#%EF%B8%8F-method-_set_fix_buttons_enabled)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)

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
    ) -> None:
        """Initialize the template dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `fields` (`list[TemplateField]`): List of template fields to display.
        - `title` (`str`): Dialog title. Defaults to `"Fill Template"`.
        - `links` (`list[tuple[str, str]] | None`): Optional list of `(label, url)` helper links.
        - `image_save_dir` (`Path | None`): If set, image fields save into this dir/img/ and return relative path.
        - `app_config` (`dict[str, Any] | None`): Application config for BotHub text fix on multiline fields.

        """
        super().__init__(parent)
        self.fields = fields
        self.widgets: dict[str, QWidget] = {}
        self.field_values: dict[str, str] = {}
        self.links = links or []
        self._image_save_dir = Path(image_save_dir) if image_save_dir else None
        self._app_config = app_config
        self._bothub_state = BothubRequestState()
        self._fix_ai_buttons: list[QPushButton] = []
        self._link_qurls: list[QUrl] = []
        for _, url in self.links:
            qurl = QUrl(url)
            if qurl.isValid():
                self._link_qurls.append(qurl)

        self.setWindowTitle(title)
        self.setModal(True)
        target = QSize(1024, 768)
        self.setMinimumSize(target)
        self.resize(target)

        def _enforce() -> None:
            self.setMinimumSize(target)
            self.resize(target)

        QTimer.singleShot(0, _enforce)

        self._setup_ui()

    def get_field_values(self) -> dict[str, str] | None:
        """Get the field values entered by the user.

        Returns:

        - `dict[str, str] | None`: Dictionary mapping field names to their values,
          or `None` if the dialog was cancelled.

        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self.field_values
        return None

    def _create_date_widget_for_field(self, field: TemplateField) -> tuple[QWidget, QDateEdit]:
        """Create a date input with quick Today/Yesterday buttons."""
        date_edit = self._create_widget_for_field(field)
        if not isinstance(date_edit, QDateEdit):
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat("yyyy-MM-dd")
            date_edit.setDate(QDate.currentDate())

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
        """Create multiline input with optional Fix with AI button."""
        text_edit = self._create_widget_for_field(field)
        if not isinstance(text_edit, QPlainTextEdit):
            text_edit = QPlainTextEdit()

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(text_edit, 1)

        fix_button = QPushButton("🤖 Fix with AI")
        if self._app_config is None:
            fix_button.setEnabled(False)
            fix_button.setToolTip("BotHub is not configured for this dialog.")
        else:
            fix_button.clicked.connect(lambda: self._on_fix_multiline_clicked(text_edit))
        self._fix_ai_buttons.append(fix_button)
        layout.addWidget(fix_button)

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
                    # Try to parse the date string
                    date_obj = QDate.fromString(field.default_value, "yyyy-MM-dd")
                    if QDate.isValid(date_obj):
                        widget.setDate(date_obj)
                    else:
                        widget.setDate(QDate.currentDate())
                except Exception:
                    widget.setDate(QDate.currentDate())
            else:
                widget.setDate(QDate.currentDate())
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
            widget = ImageDropWidget(save_dir=self._image_save_dir)
            if field.default_value:
                widget.set_image_path(field.default_value)
            return widget

        if field.field_type == "images":
            widget = ImagesListWidget(save_dir=self._image_save_dir)
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

        # Default to line edit for unknown types
        widget = QLineEdit()
        if field.default_value:
            widget.setText(field.default_value)
        else:
            widget.setPlaceholderText(f"Enter {field.name.lower()}")
        return widget

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
                return widget.date().toString("yyyy-MM-dd")
            return ""

        if field.field_type == "bool":
            if isinstance(widget, QCheckBox):
                return "true" if widget.isChecked() else "false"
            return "false"

        if field.field_type == "multiline":
            return widget.toPlainText() if isinstance(widget, QPlainTextEdit) else ""

        if field.field_type == "image":
            return widget.get_image_path() if isinstance(widget, ImageDropWidget) else ""

        if field.field_type == "images":
            if isinstance(widget, ImagesListWidget):
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

        # Default to line edit
        return widget.text() if isinstance(widget, QLineEdit) else ""

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.reject()

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

        self._set_fix_buttons_enabled(False)  # noqa: FBT003

        def on_success(response_text: str) -> None:
            self._set_fix_buttons_enabled(True)  # noqa: FBT003
            if not response_text.strip():
                message_box.critical(self, "BotHub Error", "Empty response from BotHub.")
                return
            text_edit.setPlainText(response_text)

        def on_error(message: str) -> None:
            self._set_fix_buttons_enabled(True)  # noqa: FBT003
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
        self.field_values = {}

        for field in self.fields:
            widget = self.widgets.get(field.name)
            if widget:
                value = self._get_widget_value(field, widget)
                self.field_values[field.name] = value

        self.accept()

    def _open_all_links(self) -> None:
        """Open all helper links in the default browser."""
        for qurl in self._link_qurls:
            QDesktopServices.openUrl(qurl)

    def _set_fix_buttons_enabled(self, enabled: bool) -> None:  # noqa: FBT001
        """Enable or disable all Fix with AI buttons on multiline fields."""
        for button in self._fix_ai_buttons:
            if self._app_config is not None:
                button.setEnabled(enabled)

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        main_layout = QVBoxLayout()

        # Add title label
        title_label = QLabel("Fill in the template fields:")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        main_layout.addWidget(title_label)

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
                open_all_button = QPushButton("Open all")
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
            else:
                widget = self._create_widget_for_field(field)
                self.widgets[field.name] = widget

            # Create label with field name
            label = QLabel(f"{field.name}:")
            label.setMinimumWidth(150)

            form_layout.addRow(label, widget)

        # When template has Date and image/images field, show Filename row inside widget (synced with Date)
        date_widget = self.widgets.get("Date")
        for field in self.fields:
            if field.field_type == "image" and isinstance(self.widgets.get(field.name), ImageDropWidget):
                self.widgets[field.name].set_date_widget(date_widget if isinstance(date_widget, QDateEdit) else None)
            if field.field_type == "images" and isinstance(self.widgets.get(field.name), ImagesListWidget):
                self.widgets[field.name].set_date_widget(date_widget if isinstance(date_widget, QDateEdit) else None)

        form_widget.setLayout(form_layout)
        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)

        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(cancel_button)

        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_ok)
        ok_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        button_layout.addWidget(ok_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
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
- `title` (`str`): Dialog title. Defaults to `"Fill Template"`.
- `links` (`list[tuple[str, str]] | None`): Optional list of `(label, url)` helper links.
- `image_save_dir` (`Path | None`): If set, image fields save into this dir/img/ and return relative path.
- `app_config` (`dict[str, Any] | None`): Application config for BotHub text fix on multiline fields.

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
    ) -> None:
        super().__init__(parent)
        self.fields = fields
        self.widgets: dict[str, QWidget] = {}
        self.field_values: dict[str, str] = {}
        self.links = links or []
        self._image_save_dir = Path(image_save_dir) if image_save_dir else None
        self._app_config = app_config
        self._bothub_state = BothubRequestState()
        self._fix_ai_buttons: list[QPushButton] = []
        self._link_qurls: list[QUrl] = []
        for _, url in self.links:
            qurl = QUrl(url)
            if qurl.isValid():
                self._link_qurls.append(qurl)

        self.setWindowTitle(title)
        self.setModal(True)
        target = QSize(1024, 768)
        self.setMinimumSize(target)
        self.resize(target)

        def _enforce() -> None:
            self.setMinimumSize(target)
            self.resize(target)

        QTimer.singleShot(0, _enforce)

        self._setup_ui()
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

### ⚙️ Method `_create_date_widget_for_field`

```python
def _create_date_widget_for_field(self, field: TemplateField) -> tuple[QWidget, QDateEdit]
```

Create a date input with quick Today/Yesterday buttons.

<details>
<summary>Code:</summary>

```python
def _create_date_widget_for_field(self, field: TemplateField) -> tuple[QWidget, QDateEdit]:
        date_edit = self._create_widget_for_field(field)
        if not isinstance(date_edit, QDateEdit):
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat("yyyy-MM-dd")
            date_edit.setDate(QDate.currentDate())

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
```

</details>

### ⚙️ Method `_create_multiline_widget_for_field`

```python
def _create_multiline_widget_for_field(self, field: TemplateField) -> tuple[QWidget, QPlainTextEdit]
```

Create multiline input with optional Fix with AI button.

<details>
<summary>Code:</summary>

```python
def _create_multiline_widget_for_field(self, field: TemplateField) -> tuple[QWidget, QPlainTextEdit]:
        text_edit = self._create_widget_for_field(field)
        if not isinstance(text_edit, QPlainTextEdit):
            text_edit = QPlainTextEdit()

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(text_edit, 1)

        fix_button = QPushButton("🤖 Fix with AI")
        if self._app_config is None:
            fix_button.setEnabled(False)
            fix_button.setToolTip("BotHub is not configured for this dialog.")
        else:
            fix_button.clicked.connect(lambda: self._on_fix_multiline_clicked(text_edit))
        self._fix_ai_buttons.append(fix_button)
        layout.addWidget(fix_button)

        return container, text_edit
```

</details>

### ⚙️ Method `_create_widget_for_field`

```python
def _create_widget_for_field(self, field: TemplateField) -> QWidget
```

Create an appropriate input widget for a field type.

Args:

- `field` (`TemplateField`): The field to create a widget for.

Returns:

- `QWidget`: The created input widget.

<details>
<summary>Code:</summary>

```python
def _create_widget_for_field(self, field: TemplateField) -> QWidget:
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
                    # Try to parse the date string
                    date_obj = QDate.fromString(field.default_value, "yyyy-MM-dd")
                    if QDate.isValid(date_obj):
                        widget.setDate(date_obj)
                    else:
                        widget.setDate(QDate.currentDate())
                except Exception:
                    widget.setDate(QDate.currentDate())
            else:
                widget.setDate(QDate.currentDate())
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
            widget = ImageDropWidget(save_dir=self._image_save_dir)
            if field.default_value:
                widget.set_image_path(field.default_value)
            return widget

        if field.field_type == "images":
            widget = ImagesListWidget(save_dir=self._image_save_dir)
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

        # Default to line edit for unknown types
        widget = QLineEdit()
        if field.default_value:
            widget.setText(field.default_value)
        else:
            widget.setPlaceholderText(f"Enter {field.name.lower()}")
        return widget
```

</details>

### ⚙️ Method `_get_widget_value`

```python
def _get_widget_value(self, field: TemplateField, widget: QWidget) -> str
```

Get the value from a widget based on field type.

Args:

- `field` (`TemplateField`): The field definition.
- `widget` (`QWidget`): The widget to extract value from.

Returns:

- `str`: The string representation of the widget's value.

<details>
<summary>Code:</summary>

```python
def _get_widget_value(self, field: TemplateField, widget: QWidget) -> str:
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
                return widget.date().toString("yyyy-MM-dd")
            return ""

        if field.field_type == "bool":
            if isinstance(widget, QCheckBox):
                return "true" if widget.isChecked() else "false"
            return "false"

        if field.field_type == "multiline":
            return widget.toPlainText() if isinstance(widget, QPlainTextEdit) else ""

        if field.field_type == "image":
            return widget.get_image_path() if isinstance(widget, ImageDropWidget) else ""

        if field.field_type == "images":
            if isinstance(widget, ImagesListWidget):
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

        # Default to line edit
        return widget.text() if isinstance(widget, QLineEdit) else ""
```

</details>

### ⚙️ Method `_on_cancel`

```python
def _on_cancel(self) -> None
```

Handle cancel button click.

<details>
<summary>Code:</summary>

```python
def _on_cancel(self) -> None:
        self.reject()
```

</details>

### ⚙️ Method `_on_fix_multiline_clicked`

```python
def _on_fix_multiline_clicked(self, text_edit: QPlainTextEdit) -> None
```

Send multiline field text to BotHub and replace with corrected text.

<details>
<summary>Code:</summary>

```python
def _on_fix_multiline_clicked(self, text_edit: QPlainTextEdit) -> None:
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

        self._set_fix_buttons_enabled(False)  # noqa: FBT003

        def on_success(response_text: str) -> None:
            self._set_fix_buttons_enabled(True)  # noqa: FBT003
            if not response_text.strip():
                message_box.critical(self, "BotHub Error", "Empty response from BotHub.")
                return
            text_edit.setPlainText(response_text)

        def on_error(message: str) -> None:
            self._set_fix_buttons_enabled(True)  # noqa: FBT003
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
```

</details>

### ⚙️ Method `_on_ok`

```python
def _on_ok(self) -> None
```

Handle OK button click and collect field values.

<details>
<summary>Code:</summary>

```python
def _on_ok(self) -> None:
        self.field_values = {}

        for field in self.fields:
            widget = self.widgets.get(field.name)
            if widget:
                value = self._get_widget_value(field, widget)
                self.field_values[field.name] = value

        self.accept()
```

</details>

### ⚙️ Method `_open_all_links`

```python
def _open_all_links(self) -> None
```

Open all helper links in the default browser.

<details>
<summary>Code:</summary>

```python
def _open_all_links(self) -> None:
        for qurl in self._link_qurls:
            QDesktopServices.openUrl(qurl)
```

</details>

### ⚙️ Method `_set_fix_buttons_enabled`

```python
def _set_fix_buttons_enabled(self, enabled: bool) -> None
```

Enable or disable all Fix with AI buttons on multiline fields.

<details>
<summary>Code:</summary>

```python
def _set_fix_buttons_enabled(self, enabled: bool) -> None:  # noqa: FBT001
        for button in self._fix_ai_buttons:
            if self._app_config is not None:
                button.setEnabled(enabled)
```

</details>

### ⚙️ Method `_setup_ui`

```python
def _setup_ui(self) -> None
```

Set up the user interface.

<details>
<summary>Code:</summary>

```python
def _setup_ui(self) -> None:
        main_layout = QVBoxLayout()

        # Add title label
        title_label = QLabel("Fill in the template fields:")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        main_layout.addWidget(title_label)

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
                open_all_button = QPushButton("Open all")
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
            else:
                widget = self._create_widget_for_field(field)
                self.widgets[field.name] = widget

            # Create label with field name
            label = QLabel(f"{field.name}:")
            label.setMinimumWidth(150)

            form_layout.addRow(label, widget)

        # When template has Date and image/images field, show Filename row inside widget (synced with Date)
        date_widget = self.widgets.get("Date")
        for field in self.fields:
            if field.field_type == "image" and isinstance(self.widgets.get(field.name), ImageDropWidget):
                self.widgets[field.name].set_date_widget(date_widget if isinstance(date_widget, QDateEdit) else None)
            if field.field_type == "images" and isinstance(self.widgets.get(field.name), ImagesListWidget):
                self.widgets[field.name].set_date_widget(date_widget if isinstance(date_widget, QDateEdit) else None)

        form_widget.setLayout(form_layout)
        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)

        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(cancel_button)

        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_ok)
        ok_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        button_layout.addWidget(ok_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
```

</details>
