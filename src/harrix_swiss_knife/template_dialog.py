"""Template-based form dialog system for markdown generation."""

from __future__ import annotations

import re
from pathlib import Path

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class FileDropWidget(QWidget):
    """Widget for single file selection with drag and drop support."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the file drop widget."""
        super().__init__(parent)
        self.file_path = ""
        self._setup_ui()

    def get_file_path(self) -> str:
        """Get the selected file path."""
        return self.file_path

    def set_file_path(self, path: str) -> None:
        """Set the file path."""
        if path and Path(path).exists():
            self._set_file(path)

    def _browse_file(self) -> None:
        """Open file dialog to select file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file", "", "All files (*)")
        if file_path:
            self._set_file(file_path)

    def _clear_file(self) -> None:
        """Clear the selected file."""
        self.file_path = ""
        self.file_label.setText("Drag and drop file here or click button")
        self.file_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 5px;
                padding: 20px;
                background-color: #f9f9f9;
            }
        """)

    def _drag_enter_event(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop_event(self, event: QDropEvent) -> None:
        """Handle drop event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                self._set_file(file_path)
            event.acceptProposedAction()

    def _set_file(self, file_path: str) -> None:
        """Set the file from file path."""
        self.file_path = file_path
        self.file_label.setText(f"File: {Path(file_path).name}")
        self.file_label.setStyleSheet("""
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 10px;
                background-color: #f0f8f0;
            }
        """)

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout()

        # File path display
        self.file_label = QLabel("Drag and drop file here or click button")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 5px;
                padding: 20px;
                background-color: #f9f9f9;
            }
        """)
        self.file_label.setMinimumHeight(60)
        self.file_label.setAcceptDrops(True)
        self.file_label.dragEnterEvent = self._drag_enter_event
        self.file_label.dropEvent = self._drop_event

        # Buttons layout
        button_layout = QHBoxLayout()

        self.browse_button = QPushButton("Select File")
        self.browse_button.clicked.connect(self._browse_file)
        button_layout.addWidget(self.browse_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._clear_file)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(self.file_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class FilesListWidget(QWidget):
    """Widget for multiple file selection with drag and drop support."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the files list widget."""
        super().__init__(parent)
        self.file_paths = []
        self._setup_ui()

    def get_file_paths(self) -> list[str]:
        """Get the list of selected file paths."""
        return self.file_paths.copy()

    def set_file_paths(self, paths: list[str]) -> None:
        """Set the list of file paths."""
        self._clear_all()
        for path in paths:
            if Path(path).exists():
                self._add_file_path(path)

    def _add_file_path(self, file_path: str) -> None:
        """Add file path to the list."""
        self.file_paths.append(file_path)
        item = QListWidgetItem(Path(file_path).name)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.list_widget.addItem(item)

    def _add_files(self) -> None:
        """Open file dialog to select multiple files."""
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select files", "", "All files (*)")
        for file_path in file_paths:
            if file_path not in self.file_paths:
                self._add_file_path(file_path)

    def _clear_all(self) -> None:
        """Clear all files from the list."""
        self.file_paths.clear()
        self.list_widget.clear()

    def _drag_enter_event(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop_event(self, event: QDropEvent) -> None:
        """Handle drop event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path not in self.file_paths:
                    self._add_file_path(file_path)
            event.acceptProposedAction()

    def _remove_selected(self) -> None:
        """Remove selected file from the list."""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path in self.file_paths:
                    self.file_paths.remove(file_path)

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout()

        # List widget for files
        self.list_widget = QListWidget()
        self.list_widget.setAcceptDrops(True)
        self.list_widget.dragEnterEvent = self._drag_enter_event
        self.list_widget.dropEvent = self._drop_event
        self.list_widget.setMinimumHeight(150)

        # Buttons layout
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Files")
        self.add_button.clicked.connect(self._add_files)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._remove_selected)
        button_layout.addWidget(self.remove_button)

        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self._clear_all)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class ImageDropWidget(QWidget):
    """Widget for single image selection with drag and drop support."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the image drop widget."""
        super().__init__(parent)
        self.image_path = ""
        self._setup_ui()

    def get_image_path(self) -> str:
        """Get the selected image path."""
        return self.image_path

    def set_image_path(self, path: str) -> None:
        """Set the image path."""
        if path and Path(path).exists():
            self._set_image(path)

    def _browse_file(self) -> None:
        """Open file dialog to select image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.avif);;All files (*)",
        )
        if file_path:
            self._set_image(file_path)

    def _clear_image(self) -> None:
        """Clear the selected image."""
        self.image_path = ""
        self.image_label.setText("Drag and drop image here or click button")
        self.image_label.setPixmap(QPixmap())
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 5px;
                padding: 20px;
                background-color: #f9f9f9;
            }
        """)

    def _drag_enter_event(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop_event(self, event: QDropEvent) -> None:
        """Handle drop event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if self._is_image_file(file_path):
                    self._set_image(file_path)
            event.acceptProposedAction()

    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is an image."""
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".avif"}
        return Path(file_path).suffix.lower() in image_extensions

    def _set_image(self, file_path: str) -> None:
        """Set the image from file path."""
        self.image_path = file_path
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # Scale image to fit label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    padding: 5px;
                    background-color: #f0f8f0;
                }
            """)
        else:
            self._clear_image()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Image preview label
        self.image_label = QLabel("Drag and drop image here or click button")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 5px;
                padding: 20px;
                background-color: #f9f9f9;
            }
        """)
        self.image_label.setMinimumHeight(100)
        self.image_label.setAcceptDrops(True)
        self.image_label.dragEnterEvent = self._drag_enter_event
        self.image_label.dropEvent = self._drop_event

        # Buttons layout
        button_layout = QHBoxLayout()

        self.browse_button = QPushButton("Select File")
        self.browse_button.clicked.connect(self._browse_file)
        button_layout.addWidget(self.browse_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._clear_image)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(self.image_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class ImagesListWidget(QWidget):
    """Widget for multiple image selection with drag and drop support."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the images list widget."""
        super().__init__(parent)
        self.image_paths = []
        self._setup_ui()

    def get_image_paths(self) -> list[str]:
        """Get the list of selected image paths."""
        return self.image_paths.copy()

    def set_image_paths(self, paths: list[str]) -> None:
        """Set the list of image paths."""
        self._clear_all()
        for path in paths:
            if Path(path).exists():
                self._add_image_path(path)

    def _add_image_path(self, file_path: str) -> None:
        """Add image path to the list."""
        self.image_paths.append(file_path)
        item = QListWidgetItem(Path(file_path).name)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.list_widget.addItem(item)

    def _add_images(self) -> None:
        """Open file dialog to select multiple images."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.avif);;All files (*)",
        )
        for file_path in file_paths:
            if file_path not in self.image_paths:
                self._add_image_path(file_path)

    def _clear_all(self) -> None:
        """Clear all images from the list."""
        self.image_paths.clear()
        self.list_widget.clear()

    def _drag_enter_event(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop_event(self, event: QDropEvent) -> None:
        """Handle drop event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if self._is_image_file(file_path) and file_path not in self.image_paths:
                    self._add_image_path(file_path)
            event.acceptProposedAction()

    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is an image."""
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".avif"}
        return Path(file_path).suffix.lower() in image_extensions

    def _remove_selected(self) -> None:
        """Remove selected image from the list."""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path in self.image_paths:
                    self.image_paths.remove(file_path)

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout()

        # List widget for images
        self.list_widget = QListWidget()
        self.list_widget.setAcceptDrops(True)
        self.list_widget.dragEnterEvent = self._drag_enter_event
        self.list_widget.dropEvent = self._drop_event
        self.list_widget.setMinimumHeight(150)

        # Buttons layout
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Images")
        self.add_button.clicked.connect(self._add_images)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._remove_selected)
        button_layout.addWidget(self.remove_button)

        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self._clear_all)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)

        self.setLayout(layout)


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
            widget = ImageDropWidget()
            if field.default_value:
                widget.set_image_path(field.default_value)
            return widget

        if field.field_type == "images":
            widget = ImagesListWidget()
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
    - `field_type` (`str`): The field type (e.g., "line", "int", "float", "date", "bool", "multiline").
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
    - bool: Checkbox (returns "true" or "false")
    - multiline: Multi-line text area
    - image: Single image selection with drag and drop support
    - images: Multiple image selection with drag and drop support
    - file: Single file selection with drag and drop support
    - files: Multiple file selection with drag and drop support

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
