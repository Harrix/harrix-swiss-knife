"""Template-based form dialog system for markdown generation."""

from __future__ import annotations

import re

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class TemplateDialog(QDialog):
    """Dynamic form dialog for template-based input.

    This dialog generates input fields based on template field definitions
    and collects user input to fill the template.

    Attributes:

    - `fields` (`list[TemplateField]`): List of fields in the template.
    - `widgets` (`dict`): Dictionary mapping field names to input widgets.
    - `field_values` (`dict[str, str]`): Dictionary of collected field values.

    """

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
                    if date_obj.isValid():
                        widget.setDate(date_obj)
                    else:
                        widget.setDate(QDate.currentDate())
                except Exception:
                    widget.setDate(QDate.currentDate())
            else:
                widget.setDate(QDate.currentDate())
            return widget

        if field.field_type == "multiline":
            widget = QPlainTextEdit()
            if field.default_value:
                widget.setPlainText(field.default_value)
            else:
                widget.setPlaceholderText(f"Enter {field.name.lower()}")
            widget.setMinimumHeight(100)
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


class TemplateField:
    """Represents a single field in a template.

    Attributes:

    - `name` (`str`): The field name (e.g., "Title", "Score").
    - `field_type` (`str`): The field type (e.g., "line", "int", "float", "date", "multiline").
    - `placeholder` (`str`): The original placeholder text from the template.
    - `default_value` (`str | None`): Optional default value for the field.

    """

    def __init__(self, name: str, field_type: str, placeholder: str, default_value: str | None = None) -> None:
        """Initialize a template field.

        Args:

        - `name` (`str`): The field name.
        - `field_type` (`str`): The field type.
        - `placeholder` (`str`): The original placeholder text.
        - `default_value` (`str | None`): Optional default value. Defaults to `None`.

        """
        self.name = name
        self.field_type = field_type
        self.placeholder = placeholder
        self.default_value = default_value


class TemplateParser:
    """Parser for extracting field definitions from markdown templates.

    This class parses templates with placeholders in the format:
    {{FieldName:FieldType}}

    Supported field types:
    - line: Single-line text input
    - int: Integer number
    - float: Floating-point number
    - date: Date picker
    - multiline: Multi-line text area

    """

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
        # Pattern to match {{FieldName:FieldType}} or {{FieldName:FieldType:DefaultValue}}
        pattern = r"\{\{([^:{}]+):([^:{}]+)(?::([^{}]+))?\}\}"
        matches = re.findall(pattern, template_content)

        fields = []
        seen_names = set()

        for match in matches:
            field_type_index = 1
            default_value_index = 2

            name = match[0].strip()
            field_type = match[field_type_index].strip().lower()
            default_value = (
                match[default_value_index].strip()
                if len(match) > default_value_index and match[default_value_index]
                else None
            )

            # Skip duplicate fields
            if name in seen_names:
                continue

            seen_names.add(name)
            placeholder = f"{{{{{name}:{field_type}}}}}"
            fields.append(TemplateField(name, field_type, placeholder, default_value))

        return fields, template_content
