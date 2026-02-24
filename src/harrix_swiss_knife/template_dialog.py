"""Template-based form dialog system for markdown generation."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import QDate, QEvent, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QDragEnterEvent, QDropEvent, QImage, QKeyEvent, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.filtered_combobox import apply_smart_filtering


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
        self.file_label.dragEnterEvent = self._drag_enter_event  # ty: ignore[invalid-assignment]
        self.file_label.dropEvent = self._drop_event  # ty: ignore[invalid-assignment]

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
        self.list_widget.dragEnterEvent = self._drag_enter_event  # ty: ignore[invalid-assignment]
        self.list_widget.dropEvent = self._drop_event  # ty: ignore[invalid-assignment]
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
    """Widget for single image selection with drag and drop and clipboard paste.

    When save_dir is set (e.g. parent of the target markdown file), dropped or pasted
    images are copied into save_dir/img/ and the returned path is relative (img/...).
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        save_dir: Path | None = None,
    ) -> None:
        """Initialize the image drop widget.

        Args:
            parent: Parent widget.
            save_dir: If set, images are copied into save_dir/img/ and path returned as img/filename.
        """
        super().__init__(parent)
        self.image_path = ""
        self._save_dir = Path(save_dir) if save_dir else None
        self._filename_line_edit: QLineEdit | None = None
        self._setup_ui()

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        """Handle Ctrl+V when focus is on the image label."""
        if (
            obj == self.image_label
            and event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and event.key() == Qt.Key.Key_V
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self._paste_from_clipboard()
            return True
        return super().eventFilter(obj, event)

    def get_image_path(self) -> str:
        """Get the selected image path (relative to save_dir when save_dir was set)."""
        if not self.image_path:
            return ""
        if self._save_dir:
            try:
                p = Path(self.image_path).resolve()
                if str(p).startswith(str(self._save_dir.resolve())):
                    return str(p.relative_to(self._save_dir)).replace("\\", "/")
            except (ValueError, OSError):
                pass
        return self.image_path

    def keyPressEvent(self, event) -> None:
        """Handle Ctrl+V to paste image from clipboard."""
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._paste_from_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)

    def set_date_widget(self, date_edit: QDateEdit | None) -> None:
        """Add a Filename row synced with the event date (e.g. for Events template). Call after UI is built."""
        if not date_edit or not self._save_dir:
            return
        if self._filename_line_edit is not None:
            return

        self._filename_line_edit = QLineEdit()
        self._filename_line_edit.setPlaceholderText("Filename (without extension)")
        self._filename_line_edit.setText(date_edit.date().toString("yyyy-MM-dd"))
        date_edit.dateChanged.connect(lambda d, edit=self._filename_line_edit: edit.setText(d.toString("yyyy-MM-dd")))
        filerow = QHBoxLayout()
        filerow.addWidget(QLabel("Filename:"))
        filerow.addWidget(self._filename_line_edit, 1)
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.insertLayout(layout.count() - 1, filerow)

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
        self.image_label.setText("Drag and drop image here, paste (Ctrl+V), or click button")
        self.image_label.setPixmap(QPixmap())
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 5px;
                padding: 20px;
                background-color: #f9f9f9;
            }
        """)

    def _copy_to_save_dir(self, source: Path) -> Path:
        """Copy source file into save_dir/img/ with a unique name (no overwrite). Return path to the new file."""
        img_dir = self._save_dir / "img"
        img_dir.mkdir(parents=True, exist_ok=True)
        suffix = source.suffix.lower()
        base = self._get_suggested_basename(source.stem)
        dest = _unique_path(img_dir, base, suffix)
        shutil.copy2(source, dest)
        return dest

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

    def _get_suggested_basename(self, fallback: str) -> str:
        """Return suggested filename stem from internal Filename field or fallback. Sanitize for filename."""
        if self._filename_line_edit:
            text = self._filename_line_edit.text().strip()
            if text:
                safe = re.sub(r'[<>:"/\\|?*]', "_", text).strip(" .") or fallback
                return safe[:200] if len(safe) > 200 else safe
        return fallback

    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is an image."""
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".avif"}
        return Path(file_path).suffix.lower() in image_extensions

    def _paste_from_clipboard(self) -> None:
        """Set image from clipboard if an image is available. Saves to save_dir/img/ when set."""
        clipboard = QApplication.clipboard()
        qimage = clipboard.image()
        if qimage.isNull():
            return
        if self._save_dir:
            img_dir = self._save_dir / "img"
            img_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
            base = self._get_suggested_basename(f"pasted_{stamp}")
            dest = _unique_path(img_dir, base, ".png")
            if qimage.save(str(dest), "PNG"):
                self._set_image(str(dest))
        else:
            from tempfile import NamedTemporaryFile

            with NamedTemporaryFile(suffix=".png", delete=False) as f:
                tmp = Path(f.name)
            if qimage.save(str(tmp), "PNG"):
                self._set_image(str(tmp))

    def _set_image(self, file_path: str) -> None:
        """Set the image from file path. If save_dir is set, copy to save_dir/img/ first (unless already there)."""
        source = Path(file_path).resolve()
        if not source.exists():
            return
        if self._save_dir:
            try:
                img_dir = self._save_dir.resolve() / "img"
                if img_dir in source.parents or source.parent == img_dir:
                    self.image_path = str(source)
                else:
                    dest = self._copy_to_save_dir(source)
                    self.image_path = str(dest)
            except (OSError, ValueError):
                self.image_path = file_path
        else:
            self.image_path = file_path
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
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

        self.image_label = QLabel("Drag and drop image here, paste (Ctrl+V), or click button")
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
        self.image_label.installEventFilter(self)
        self.image_label.dragEnterEvent = self._drag_enter_event  # ty: ignore[invalid-assignment]
        self.image_label.dropEvent = self._drop_event  # ty: ignore[invalid-assignment]

        button_layout = QHBoxLayout()

        self.browse_button = QPushButton("Select File")
        self.browse_button.clicked.connect(self._browse_file)
        button_layout.addWidget(self.browse_button)

        self.paste_button = QPushButton("Paste")
        self.paste_button.clicked.connect(self._paste_from_clipboard)
        button_layout.addWidget(self.paste_button)

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
        self.list_widget.dragEnterEvent = self._drag_enter_event  # ty: ignore[invalid-assignment]
        self.list_widget.dropEvent = self._drop_event  # ty: ignore[invalid-assignment]
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
    - `links` (`list[tuple[str, str]]`): Optional helper links shown in the dialog header.

    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        fields: list[TemplateField],
        title: str = "Fill Template",
        links: list[tuple[str, str]] | None = None,
        image_save_dir: Path | None = None,
    ) -> None:
        """Initialize the template dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `fields` (`list[TemplateField]`): List of template fields to display.
        - `title` (`str`): Dialog title. Defaults to `"Fill Template"`.
        - `links` (`list[tuple[str, str]] | None`): Optional list of `(label, url)` helper links.
        - `image_save_dir` (`Path | None`): If set, image fields save into this dir/img/ and return relative path.

        """
        super().__init__(parent)
        self.fields = fields
        self.widgets: dict[str, QWidget] = {}
        self.field_values: dict[str, str] = {}
        self.links = links or []
        self._image_save_dir = Path(image_save_dir) if image_save_dir else None
        self._link_qurls: list[QUrl] = []
        for _, url in self.links:
            qurl = QUrl(url)
            if qurl.isValid():
                self._link_qurls.append(qurl)

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
            widget = self._create_widget_for_field(field)
            self.widgets[field.name] = widget

            # Create label with field name
            label = QLabel(f"{field.name}:")
            label.setMinimumWidth(150)

            form_layout.addRow(label, widget)

        # When template has Date and image field, show Filename row inside image widget (synced with Date)
        date_widget = self.widgets.get("Date")
        for field in self.fields:
            if field.field_type == "image" and isinstance(self.widgets.get(field.name), ImageDropWidget):
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


class TemplateField:
    """Represents a single field in a template.

    Attributes:

    - `name` (`str`): The field name (e.g., "Title", "Score").
    - `field_type` (`str`): The field type (e.g., "line", "int", "float", "date", "bool", "multiline", "combobox").
    - `placeholder` (`str`): The original placeholder text from the template.
    - `default_value` (`str | None`): Optional default value for the field.
    - `options` (`list[str] | None`): Optional list of options for combobox field type. Defaults to `None`.

    """

    def __init__(
        self,
        name: str,
        field_type: str,
        placeholder: str,
        default_value: str | None = None,
        options: list[str] | None = None,
    ) -> None:
        """Initialize a template field.

        Args:

        - `name` (`str`): The field name.
        - `field_type` (`str`): The field type.
        - `placeholder` (`str`): The original placeholder text.
        - `default_value` (`str | None`): Optional default value. Defaults to `None`.
        - `options` (`list[str] | None`): Optional list of options for combobox field type. Defaults to `None`.

        """
        self.name = name
        self.field_type = field_type
        self.placeholder = placeholder
        self.default_value = default_value
        self.options = options or []


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

        Multiline fields get empty lines between lines. If a multiline placeholder
        is inside a list item (e.g. ``- **Comments:** {{Comments:multiline}}``),
        continuation lines are indented with two spaces for correct markdown list.

        Args:

        - `template_content` (`str`): The template content with placeholders.
        - `field_values` (`dict[str, str]`): Dictionary mapping field names to their values.

        Returns:

        - `str`: The filled template with all placeholders replaced.

        """
        # Pattern to match {{FieldName:FieldType}} or {{FieldName:FieldType:DefaultValue}}
        placeholder_pattern = re.compile(r"\{\{([^:{}]+):([^:{}]+)(?::([^{}]+))?\}\}")
        result_parts: list[str] = []
        last_end = 0

        for match in placeholder_pattern.finditer(template_content):
            name = match.group(1).strip()
            field_type = match.group(2).strip().lower()
            value = field_values.get(name, "")

            if field_type == "multiline" and "\n" in value:
                line_start = template_content.rfind("\n", 0, match.start())
                line_start = line_start + 1 if line_start >= 0 else 0
                line_prefix = template_content[line_start : match.start()]
                value = TemplateParser._format_multiline_value(value, line_prefix)

            result_parts.append(template_content[last_end : match.start()])
            result_parts.append(value)
            last_end = match.end()

        result_parts.append(template_content[last_end:])
        return "".join(result_parts)

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

    @staticmethod
    def _format_multiline_value(value: str, line_prefix: str) -> str:
        """Format multiline value for markdown: empty line between lines.

        If placeholder is inside a list item (line starts with '- '), continuation
        lines are indented with two spaces so they remain part of the list.
        Empty/whitespace-only lines are filtered to avoid double blanks.
        Result has no trailing newline.

        Args:

        - `value` (`str`): Raw multiline string.
        - `line_prefix` (`str`): Text on the same line before the placeholder.

        Returns:

        - `str`: Formatted string (first line, then blank line, then rest with optional indent).

        """
        lines = [line.rstrip() for line in value.strip().split("\n")]
        while lines and not lines[-1]:
            lines.pop()
        if not lines:
            return ""
        if len(lines) == 1:
            return lines[0]
        first_line = lines[0]
        rest = [line for line in lines[1:] if line]
        if not rest:
            return first_line
        is_list_line = bool(re.match(r"^\s*-\s+", line_prefix))
        rest_formatted = "\n\n".join("  " + line for line in rest) if is_list_line else "\n\n".join(rest)
        result = first_line + "\n\n" + rest_formatted
        return result.rstrip("\n")


def _unique_path(folder: Path, base_name: str, suffix: str) -> Path:
    """Return a path in folder that does not exist, using base_name and suffix with _1, _2 if needed."""
    path = folder / (base_name + suffix)
    if not path.exists():
        return path
    i = 1
    while True:
        path = folder / (f"{base_name}_{i}{suffix}")
        if not path.exists():
            return path
        i += 1
