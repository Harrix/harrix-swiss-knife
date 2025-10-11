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
  - [⚙️ Method `_create_widget_for_field`](#%EF%B8%8F-method-_create_widget_for_field)
  - [⚙️ Method `_get_widget_value`](#%EF%B8%8F-method-_get_widget_value)
  - [⚙️ Method `_on_cancel`](#%EF%B8%8F-method-_on_cancel)
  - [⚙️ Method `_on_ok`](#%EF%B8%8F-method-_on_ok)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)
- [🏛️ Class `TemplateField`](#%EF%B8%8F-class-templatefield)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
- [🏛️ Class `TemplateParser`](#%EF%B8%8F-class-templateparser)
  - [⚙️ Method `fill_template`](#%EF%B8%8F-method-fill_template)
  - [⚙️ Method `parse_template`](#%EF%B8%8F-method-parse_template)

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
    ) -> None:
        """Initialize the template dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `fields` (`list[TemplateField]`): List of template fields to display.
        - `title` (`str`): Dialog title. Defaults to `"Fill Template"`.

        """
        super().__init__(parent)
        self.fields = fields
        self.widgets: dict[str, QWidget] = {}
        self.field_values: dict[str, str] = {}

        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(600, 400)

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

    def _create_widget_for_field(self, field: TemplateField) -> QWidget:
        """Create an appropriate input widget for a field type.

        Args:

        - `field` (`TemplateField`): The field to create a widget for.

        Returns:

        - `QWidget`: The created input widget.

        """
        if field.field_type == "line":
            widget = QLineEdit()
            widget.setPlaceholderText(f"Enter {field.name.lower()}")
            return widget

        if field.field_type == "float":
            widget = QDoubleSpinBox()
            widget.setRange(0.0, 100.0)
            widget.setDecimals(1)
            widget.setSingleStep(0.5)
            widget.setValue(0.0)
            return widget

        if field.field_type == "date":
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDate(QDate.currentDate())
            widget.setDisplayFormat("yyyy-MM-dd")
            return widget

        if field.field_type == "multiline":
            widget = QPlainTextEdit()
            widget.setPlaceholderText(f"Enter {field.name.lower()}")
            widget.setMinimumHeight(100)
            return widget

        # Default to line edit for unknown types
        widget = QLineEdit()
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

        if field.field_type == "float":
            return str(widget.value()) if isinstance(widget, QDoubleSpinBox) else "0.0"

        if field.field_type == "date":
            if isinstance(widget, QDateEdit):
                return widget.date().toString("yyyy-MM-dd")
            return ""

        if field.field_type == "multiline":
            return widget.toPlainText() if isinstance(widget, QPlainTextEdit) else ""

        # Default to line edit
        return widget.text() if isinstance(widget, QLineEdit) else ""

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.reject()

    def _on_ok(self) -> None:
        """Handle OK button click and collect field values."""
        self.field_values = {}

        for field in self.fields:
            widget = self.widgets.get(field.name)
            if widget:
                value = self._get_widget_value(field, widget)
                self.field_values[field.name] = value

        self.accept()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        main_layout = QVBoxLayout()

        # Add title label
        title_label = QLabel("Fill in the template fields:")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        main_layout.addWidget(title_label)

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
            widget = self._create_widget_for_field(field)
            self.widgets[field.name] = widget

            # Create label with field name
            label = QLabel(f"{field.name}:")
            label.setMinimumWidth(150)

            form_layout.addRow(label, widget)

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

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        fields: list[TemplateField],
        title: str = "Fill Template",
    ) -> None:
        super().__init__(parent)
        self.fields = fields
        self.widgets: dict[str, QWidget] = {}
        self.field_values: dict[str, str] = {}

        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(600, 400)

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
            widget.setPlaceholderText(f"Enter {field.name.lower()}")
            return widget

        if field.field_type == "float":
            widget = QDoubleSpinBox()
            widget.setRange(0.0, 100.0)
            widget.setDecimals(1)
            widget.setSingleStep(0.5)
            widget.setValue(0.0)
            return widget

        if field.field_type == "date":
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDate(QDate.currentDate())
            widget.setDisplayFormat("yyyy-MM-dd")
            return widget

        if field.field_type == "multiline":
            widget = QPlainTextEdit()
            widget.setPlaceholderText(f"Enter {field.name.lower()}")
            widget.setMinimumHeight(100)
            return widget

        # Default to line edit for unknown types
        widget = QLineEdit()
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

        if field.field_type == "float":
            return str(widget.value()) if isinstance(widget, QDoubleSpinBox) else "0.0"

        if field.field_type == "date":
            if isinstance(widget, QDateEdit):
                return widget.date().toString("yyyy-MM-dd")
            return ""

        if field.field_type == "multiline":
            return widget.toPlainText() if isinstance(widget, QPlainTextEdit) else ""

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
            widget = self._create_widget_for_field(field)
            self.widgets[field.name] = widget

            # Create label with field name
            label = QLabel(f"{field.name}:")
            label.setMinimumWidth(150)

            form_layout.addRow(label, widget)

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

## 🏛️ Class `TemplateField`

```python
class TemplateField
```

Represents a single field in a template.

Attributes:

- `name` (`str`): The field name (e.g., "Title", "Score").
- `field_type` (`str`): The field type (e.g., "line", "float", "date", "multiline").
- `placeholder` (`str`): The original placeholder text from the template.

<details>
<summary>Code:</summary>

```python
class TemplateField:

    def __init__(self, name: str, field_type: str, placeholder: str) -> None:
        """Initialize a template field.

        Args:

        - `name` (`str`): The field name.
        - `field_type` (`str`): The field type.
        - `placeholder` (`str`): The original placeholder text.

        """
        self.name = name
        self.field_type = field_type
        self.placeholder = placeholder
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, name: str, field_type: str, placeholder: str) -> None
```

Initialize a template field.

Args:

- `name` (`str`): The field name.
- `field_type` (`str`): The field type.
- `placeholder` (`str`): The original placeholder text.

<details>
<summary>Code:</summary>

```python
def __init__(self, name: str, field_type: str, placeholder: str) -> None:
        self.name = name
        self.field_type = field_type
        self.placeholder = placeholder
```

</details>

## 🏛️ Class `TemplateParser`

```python
class TemplateParser
```

Parser for extracting field definitions from markdown templates.

This class parses templates with placeholders in the format:
{{FieldName:FieldType}}

Supported field types:

- line: Single-line text input
- float: Floating-point number
- date: Date picker
- multiline: Multi-line text area

<details>
<summary>Code:</summary>

```python
class TemplateParser:

    @staticmethod
    def fill_template(template_content: str, field_values: dict[str, str]) -> str:
        """Fill a template with provided field values.

        Args:

        - `template_content` (`str`): The template content with placeholders.
        - `field_values` (`dict[str, str]`): Dictionary mapping field names to their values.

        Returns:

        - `str`: The filled template with all placeholders replaced.

        """
        result = template_content

        for field_name, value in field_values.items():
            # Match both the exact pattern and case variations
            pattern = r"\{\{" + re.escape(field_name) + r":[^}]+\}\}"
            result = re.sub(pattern, value, result)

        return result

    @staticmethod
    def parse_template(template_content: str) -> tuple[list[TemplateField], str]:
        """Parse a template to extract field definitions.

        Args:

        - `template_content` (`str`): The template content with placeholders.

        Returns:

        - `tuple[list[TemplateField], str]`: A tuple containing:
          - List of TemplateField objects found in the template
          - The original template content

        """
        # Pattern to match {{FieldName:FieldType}}
        pattern = r"\{\{([^:{}]+):([^:{}]+)\}\}"
        matches = re.findall(pattern, template_content)

        fields = []
        seen_names = set()

        for name, field_type in matches:
            name = name.strip()
            field_type = field_type.strip().lower()

            # Skip duplicate fields
            if name in seen_names:
                continue

            seen_names.add(name)
            placeholder = f"{{{{{name}:{field_type}}}}}"
            fields.append(TemplateField(name, field_type, placeholder))

        return fields, template_content
```

</details>

### ⚙️ Method `fill_template`

```python
def fill_template(template_content: str, field_values: dict[str, str]) -> str
```

Fill a template with provided field values.

Args:

- `template_content` (`str`): The template content with placeholders.
- `field_values` (`dict[str, str]`): Dictionary mapping field names to their values.

Returns:

- `str`: The filled template with all placeholders replaced.

<details>
<summary>Code:</summary>

```python
def fill_template(template_content: str, field_values: dict[str, str]) -> str:
        result = template_content

        for field_name, value in field_values.items():
            # Match both the exact pattern and case variations
            pattern = r"\{\{" + re.escape(field_name) + r":[^}]+\}\}"
            result = re.sub(pattern, value, result)

        return result
```

</details>

### ⚙️ Method `parse_template`

```python
def parse_template(template_content: str) -> tuple[list[TemplateField], str]
```

Parse a template to extract field definitions.

Args:

- `template_content` (`str`): The template content with placeholders.

Returns:

- `tuple[list[TemplateField], str]`: A tuple containing:
  - List of TemplateField objects found in the template
  - The original template content

<details>
<summary>Code:</summary>

```python
def parse_template(template_content: str) -> tuple[list[TemplateField], str]:
        # Pattern to match {{FieldName:FieldType}}
        pattern = r"\{\{([^:{}]+):([^:{}]+)\}\}"
        matches = re.findall(pattern, template_content)

        fields = []
        seen_names = set()

        for name, field_type in matches:
            name = name.strip()
            field_type = field_type.strip().lower()

            # Skip duplicate fields
            if name in seen_names:
                continue

            seen_names.add(name)
            placeholder = f"{{{{{name}:{field_type}}}}}"
            fields.append(TemplateField(name, field_type, placeholder))

        return fields, template_content
```

</details>
