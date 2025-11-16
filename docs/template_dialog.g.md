---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `template_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FileDropWidget`](#%EF%B8%8F-class-filedropwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_file_path`](#%EF%B8%8F-method-get_file_path)
  - [⚙️ Method `set_file_path`](#%EF%B8%8F-method-set_file_path)
  - [⚙️ Method `_browse_file`](#%EF%B8%8F-method-_browse_file)
  - [⚙️ Method `_clear_file`](#%EF%B8%8F-method-_clear_file)
  - [⚙️ Method `_drag_enter_event`](#%EF%B8%8F-method-_drag_enter_event)
  - [⚙️ Method `_drop_event`](#%EF%B8%8F-method-_drop_event)
  - [⚙️ Method `_set_file`](#%EF%B8%8F-method-_set_file)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)
- [🏛️ Class `FilesListWidget`](#%EF%B8%8F-class-fileslistwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `get_file_paths`](#%EF%B8%8F-method-get_file_paths)
  - [⚙️ Method `set_file_paths`](#%EF%B8%8F-method-set_file_paths)
  - [⚙️ Method `_add_file_path`](#%EF%B8%8F-method-_add_file_path)
  - [⚙️ Method `_add_files`](#%EF%B8%8F-method-_add_files)
  - [⚙️ Method `_clear_all`](#%EF%B8%8F-method-_clear_all)
  - [⚙️ Method `_drag_enter_event`](#%EF%B8%8F-method-_drag_enter_event-1)
  - [⚙️ Method `_drop_event`](#%EF%B8%8F-method-_drop_event-1)
  - [⚙️ Method `_remove_selected`](#%EF%B8%8F-method-_remove_selected)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui-1)
- [🏛️ Class `ImageDropWidget`](#%EF%B8%8F-class-imagedropwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `get_image_path`](#%EF%B8%8F-method-get_image_path)
  - [⚙️ Method `set_image_path`](#%EF%B8%8F-method-set_image_path)
  - [⚙️ Method `_browse_file`](#%EF%B8%8F-method-_browse_file-1)
  - [⚙️ Method `_clear_image`](#%EF%B8%8F-method-_clear_image)
  - [⚙️ Method `_drag_enter_event`](#%EF%B8%8F-method-_drag_enter_event-2)
  - [⚙️ Method `_drop_event`](#%EF%B8%8F-method-_drop_event-2)
  - [⚙️ Method `_is_image_file`](#%EF%B8%8F-method-_is_image_file)
  - [⚙️ Method `_set_image`](#%EF%B8%8F-method-_set_image)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui-2)
- [🏛️ Class `ImagesListWidget`](#%EF%B8%8F-class-imageslistwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `get_image_paths`](#%EF%B8%8F-method-get_image_paths)
  - [⚙️ Method `set_image_paths`](#%EF%B8%8F-method-set_image_paths)
  - [⚙️ Method `_add_image_path`](#%EF%B8%8F-method-_add_image_path)
  - [⚙️ Method `_add_images`](#%EF%B8%8F-method-_add_images)
  - [⚙️ Method `_clear_all`](#%EF%B8%8F-method-_clear_all-1)
  - [⚙️ Method `_drag_enter_event`](#%EF%B8%8F-method-_drag_enter_event-3)
  - [⚙️ Method `_drop_event`](#%EF%B8%8F-method-_drop_event-3)
  - [⚙️ Method `_is_image_file`](#%EF%B8%8F-method-_is_image_file-1)
  - [⚙️ Method `_remove_selected`](#%EF%B8%8F-method-_remove_selected-1)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui-3)
- [🏛️ Class `TemplateDialog`](#%EF%B8%8F-class-templatedialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `get_field_values`](#%EF%B8%8F-method-get_field_values)
  - [⚙️ Method `_create_widget_for_field`](#%EF%B8%8F-method-_create_widget_for_field)
  - [⚙️ Method `_get_widget_value`](#%EF%B8%8F-method-_get_widget_value)
  - [⚙️ Method `_on_cancel`](#%EF%B8%8F-method-_on_cancel)
  - [⚙️ Method `_on_ok`](#%EF%B8%8F-method-_on_ok)
  - [⚙️ Method `_open_all_links`](#%EF%B8%8F-method-_open_all_links)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui-4)
- [🏛️ Class `TemplateField`](#%EF%B8%8F-class-templatefield)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
- [🏛️ Class `TemplateParser`](#%EF%B8%8F-class-templateparser)
  - [⚙️ Method `fill_template`](#%EF%B8%8F-method-fill_template)
  - [⚙️ Method `parse_template`](#%EF%B8%8F-method-parse_template)

</details>

## 🏛️ Class `FileDropWidget`

```python
class FileDropWidget(QWidget)
```

Widget for single file selection with drag and drop support.

<details>
<summary>Code:</summary>

```python
class FileDropWidget(QWidget):

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the file drop widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.file_path = ""
        self._setup_ui()
```

</details>

### ⚙️ Method `get_file_path`

```python
def get_file_path(self) -> str
```

Get the selected file path.

<details>
<summary>Code:</summary>

```python
def get_file_path(self) -> str:
        return self.file_path
```

</details>

### ⚙️ Method `set_file_path`

```python
def set_file_path(self, path: str) -> None
```

Set the file path.

<details>
<summary>Code:</summary>

```python
def set_file_path(self, path: str) -> None:
        if path and Path(path).exists():
            self._set_file(path)
```

</details>

### ⚙️ Method `_browse_file`

```python
def _browse_file(self) -> None
```

Open file dialog to select file.

<details>
<summary>Code:</summary>

```python
def _browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file", "", "All files (*)")
        if file_path:
            self._set_file(file_path)
```

</details>

### ⚙️ Method `_clear_file`

```python
def _clear_file(self) -> None
```

Clear the selected file.

<details>
<summary>Code:</summary>

```python
def _clear_file(self) -> None:
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
```

</details>

### ⚙️ Method `_drag_enter_event`

```python
def _drag_enter_event(self, event: QDragEnterEvent) -> None
```

Handle drag enter event.

<details>
<summary>Code:</summary>

```python
def _drag_enter_event(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
```

</details>

### ⚙️ Method `_drop_event`

```python
def _drop_event(self, event: QDropEvent) -> None
```

Handle drop event.

<details>
<summary>Code:</summary>

```python
def _drop_event(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                self._set_file(file_path)
            event.acceptProposedAction()
```

</details>

### ⚙️ Method `_set_file`

```python
def _set_file(self, file_path: str) -> None
```

Set the file from file path.

<details>
<summary>Code:</summary>

```python
def _set_file(self, file_path: str) -> None:
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
```

</details>

## 🏛️ Class `FilesListWidget`

```python
class FilesListWidget(QWidget)
```

Widget for multiple file selection with drag and drop support.

<details>
<summary>Code:</summary>

```python
class FilesListWidget(QWidget):

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the files list widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.file_paths = []
        self._setup_ui()
```

</details>

### ⚙️ Method `get_file_paths`

```python
def get_file_paths(self) -> list[str]
```

Get the list of selected file paths.

<details>
<summary>Code:</summary>

```python
def get_file_paths(self) -> list[str]:
        return self.file_paths.copy()
```

</details>

### ⚙️ Method `set_file_paths`

```python
def set_file_paths(self, paths: list[str]) -> None
```

Set the list of file paths.

<details>
<summary>Code:</summary>

```python
def set_file_paths(self, paths: list[str]) -> None:
        self._clear_all()
        for path in paths:
            if Path(path).exists():
                self._add_file_path(path)
```

</details>

### ⚙️ Method `_add_file_path`

```python
def _add_file_path(self, file_path: str) -> None
```

Add file path to the list.

<details>
<summary>Code:</summary>

```python
def _add_file_path(self, file_path: str) -> None:
        self.file_paths.append(file_path)
        item = QListWidgetItem(Path(file_path).name)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.list_widget.addItem(item)
```

</details>

### ⚙️ Method `_add_files`

```python
def _add_files(self) -> None
```

Open file dialog to select multiple files.

<details>
<summary>Code:</summary>

```python
def _add_files(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select files", "", "All files (*)")
        for file_path in file_paths:
            if file_path not in self.file_paths:
                self._add_file_path(file_path)
```

</details>

### ⚙️ Method `_clear_all`

```python
def _clear_all(self) -> None
```

Clear all files from the list.

<details>
<summary>Code:</summary>

```python
def _clear_all(self) -> None:
        self.file_paths.clear()
        self.list_widget.clear()
```

</details>

### ⚙️ Method `_drag_enter_event`

```python
def _drag_enter_event(self, event: QDragEnterEvent) -> None
```

Handle drag enter event.

<details>
<summary>Code:</summary>

```python
def _drag_enter_event(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
```

</details>

### ⚙️ Method `_drop_event`

```python
def _drop_event(self, event: QDropEvent) -> None
```

Handle drop event.

<details>
<summary>Code:</summary>

```python
def _drop_event(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path not in self.file_paths:
                    self._add_file_path(file_path)
            event.acceptProposedAction()
```

</details>

### ⚙️ Method `_remove_selected`

```python
def _remove_selected(self) -> None
```

Remove selected file from the list.

<details>
<summary>Code:</summary>

```python
def _remove_selected(self) -> None:
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path in self.file_paths:
                    self.file_paths.remove(file_path)
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
```

</details>

## 🏛️ Class `ImageDropWidget`

```python
class ImageDropWidget(QWidget)
```

Widget for single image selection with drag and drop support.

<details>
<summary>Code:</summary>

```python
class ImageDropWidget(QWidget):

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
        self.image_label.dragEnterEvent = self._drag_enter_event  # ty: ignore[invalid-assignment]
        self.image_label.dropEvent = self._drop_event  # ty: ignore[invalid-assignment]

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the image drop widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.image_path = ""
        self._setup_ui()
```

</details>

### ⚙️ Method `get_image_path`

```python
def get_image_path(self) -> str
```

Get the selected image path.

<details>
<summary>Code:</summary>

```python
def get_image_path(self) -> str:
        return self.image_path
```

</details>

### ⚙️ Method `set_image_path`

```python
def set_image_path(self, path: str) -> None
```

Set the image path.

<details>
<summary>Code:</summary>

```python
def set_image_path(self, path: str) -> None:
        if path and Path(path).exists():
            self._set_image(path)
```

</details>

### ⚙️ Method `_browse_file`

```python
def _browse_file(self) -> None
```

Open file dialog to select image.

<details>
<summary>Code:</summary>

```python
def _browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.avif);;All files (*)",
        )
        if file_path:
            self._set_image(file_path)
```

</details>

### ⚙️ Method `_clear_image`

```python
def _clear_image(self) -> None
```

Clear the selected image.

<details>
<summary>Code:</summary>

```python
def _clear_image(self) -> None:
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
```

</details>

### ⚙️ Method `_drag_enter_event`

```python
def _drag_enter_event(self, event: QDragEnterEvent) -> None
```

Handle drag enter event.

<details>
<summary>Code:</summary>

```python
def _drag_enter_event(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
```

</details>

### ⚙️ Method `_drop_event`

```python
def _drop_event(self, event: QDropEvent) -> None
```

Handle drop event.

<details>
<summary>Code:</summary>

```python
def _drop_event(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if self._is_image_file(file_path):
                    self._set_image(file_path)
            event.acceptProposedAction()
```

</details>

### ⚙️ Method `_is_image_file`

```python
def _is_image_file(self, file_path: str) -> bool
```

Check if file is an image.

<details>
<summary>Code:</summary>

```python
def _is_image_file(self, file_path: str) -> bool:
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".avif"}
        return Path(file_path).suffix.lower() in image_extensions
```

</details>

### ⚙️ Method `_set_image`

```python
def _set_image(self, file_path: str) -> None
```

Set the image from file path.

<details>
<summary>Code:</summary>

```python
def _set_image(self, file_path: str) -> None:
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
        self.image_label.dragEnterEvent = self._drag_enter_event  # ty: ignore[invalid-assignment]
        self.image_label.dropEvent = self._drop_event  # ty: ignore[invalid-assignment]

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
```

</details>

## 🏛️ Class `ImagesListWidget`

```python
class ImagesListWidget(QWidget)
```

Widget for multiple image selection with drag and drop support.

<details>
<summary>Code:</summary>

```python
class ImagesListWidget(QWidget):

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the images list widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.image_paths = []
        self._setup_ui()
```

</details>

### ⚙️ Method `get_image_paths`

```python
def get_image_paths(self) -> list[str]
```

Get the list of selected image paths.

<details>
<summary>Code:</summary>

```python
def get_image_paths(self) -> list[str]:
        return self.image_paths.copy()
```

</details>

### ⚙️ Method `set_image_paths`

```python
def set_image_paths(self, paths: list[str]) -> None
```

Set the list of image paths.

<details>
<summary>Code:</summary>

```python
def set_image_paths(self, paths: list[str]) -> None:
        self._clear_all()
        for path in paths:
            if Path(path).exists():
                self._add_image_path(path)
```

</details>

### ⚙️ Method `_add_image_path`

```python
def _add_image_path(self, file_path: str) -> None
```

Add image path to the list.

<details>
<summary>Code:</summary>

```python
def _add_image_path(self, file_path: str) -> None:
        self.image_paths.append(file_path)
        item = QListWidgetItem(Path(file_path).name)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.list_widget.addItem(item)
```

</details>

### ⚙️ Method `_add_images`

```python
def _add_images(self) -> None
```

Open file dialog to select multiple images.

<details>
<summary>Code:</summary>

```python
def _add_images(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.avif);;All files (*)",
        )
        for file_path in file_paths:
            if file_path not in self.image_paths:
                self._add_image_path(file_path)
```

</details>

### ⚙️ Method `_clear_all`

```python
def _clear_all(self) -> None
```

Clear all images from the list.

<details>
<summary>Code:</summary>

```python
def _clear_all(self) -> None:
        self.image_paths.clear()
        self.list_widget.clear()
```

</details>

### ⚙️ Method `_drag_enter_event`

```python
def _drag_enter_event(self, event: QDragEnterEvent) -> None
```

Handle drag enter event.

<details>
<summary>Code:</summary>

```python
def _drag_enter_event(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
```

</details>

### ⚙️ Method `_drop_event`

```python
def _drop_event(self, event: QDropEvent) -> None
```

Handle drop event.

<details>
<summary>Code:</summary>

```python
def _drop_event(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if self._is_image_file(file_path) and file_path not in self.image_paths:
                    self._add_image_path(file_path)
            event.acceptProposedAction()
```

</details>

### ⚙️ Method `_is_image_file`

```python
def _is_image_file(self, file_path: str) -> bool
```

Check if file is an image.

<details>
<summary>Code:</summary>

```python
def _is_image_file(self, file_path: str) -> bool:
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".avif"}
        return Path(file_path).suffix.lower() in image_extensions
```

</details>

### ⚙️ Method `_remove_selected`

```python
def _remove_selected(self) -> None
```

Remove selected image from the list.

<details>
<summary>Code:</summary>

```python
def _remove_selected(self) -> None:
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path in self.image_paths:
                    self.image_paths.remove(file_path)
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
```

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
    ) -> None:
        """Initialize the template dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `fields` (`list[TemplateField]`): List of template fields to display.
        - `title` (`str`): Dialog title. Defaults to `"Fill Template"`.
        - `links` (`list[tuple[str, str]] | None`): Optional list of `(label, url)` helper links.

        """
        super().__init__(parent)
        self.fields = fields
        self.widgets: dict[str, QWidget] = {}
        self.field_values: dict[str, str] = {}
        self.links = links or []
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
    ) -> None:
        super().__init__(parent)
        self.fields = fields
        self.widgets: dict[str, QWidget] = {}
        self.field_values: dict[str, str] = {}
        self.links = links or []
        self._link_qurls: list[QUrl] = []
        for _, url in self.links:
            qurl = QUrl(url)
            if qurl.isValid():
                self._link_qurls.append(qurl)

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
- `field_type` (`str`): The field type (e.g., "line", "int", "float", "date", "bool", "multiline", "combobox").
- `placeholder` (`str`): The original placeholder text from the template.
- `default_value` (`str | None`): Optional default value for the field.
- `options` (`list[str] | None`): Optional list of options for combobox field type. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
class TemplateField:

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, name: str, field_type: str, placeholder: str, default_value: str | None = None, options: list[str] | None = None) -> None
```

Initialize a template field.

Args:

- `name` (`str`): The field name.
- `field_type` (`str`): The field type.
- `placeholder` (`str`): The original placeholder text.
- `default_value` (`str | None`): Optional default value. Defaults to `None`.
- `options` (`list[str] | None`): Optional list of options for combobox field type. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        name: str,
        field_type: str,
        placeholder: str,
        default_value: str | None = None,
        options: list[str] | None = None,
    ) -> None:
        self.name = name
        self.field_type = field_type
        self.placeholder = placeholder
        self.default_value = default_value
        self.options = options or []
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
- int: Integer number
- float: Floating-point number
- date: Date picker
- bool: Checkbox (returns "true" or "false")
- multiline: Multi-line text area
- image: Single image selection with drag and drop support
- images: Multiple image selection with drag and drop support
- file: Single file selection with drag and drop support
- files: Multiple file selection with drag and drop support

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
```

</details>
