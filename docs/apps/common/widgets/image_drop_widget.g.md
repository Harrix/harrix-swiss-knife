---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_drop_widget.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ImageDropWidget`](#%EF%B8%8F-class-imagedropwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `get_image_bytes_and_mime`](#%EF%B8%8F-method-get_image_bytes_and_mime)
  - [⚙️ Method `get_image_path`](#%EF%B8%8F-method-get_image_path)
  - [⚙️ Method `has_image`](#%EF%B8%8F-method-has_image)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `set_date_widget`](#%EF%B8%8F-method-set_date_widget)
  - [⚙️ Method `set_image_path`](#%EF%B8%8F-method-set_image_path)
  - [⚙️ Method `_browse_file`](#%EF%B8%8F-method-_browse_file)
  - [⚙️ Method `_clear_image`](#%EF%B8%8F-method-_clear_image)
  - [⚙️ Method `_copy_to_save_dir`](#%EF%B8%8F-method-_copy_to_save_dir)
  - [⚙️ Method `_downscale_file_if_needed`](#%EF%B8%8F-method-_downscale_file_if_needed)
  - [⚙️ Method `_is_image_file`](#%EF%B8%8F-method-_is_image_file)
  - [⚙️ Method `_paste_from_clipboard`](#%EF%B8%8F-method-_paste_from_clipboard)
  - [⚙️ Method `_set_image`](#%EF%B8%8F-method-_set_image)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)
- [🔧 Function `unique_path_in_folder`](#-function-unique_path_in_folder)
- [🔧 Function `_downscale_qimage`](#-function-_downscale_qimage)

</details>

## 🏛️ Class `ImageDropWidget`

```python
class ImageDropWidget(QWidget)
```

Widget for single image selection with drag and drop and clipboard paste.

When save_dir is set (e.g. parent of the target markdown file), dropped or pasted
images are copied into save_dir/img/ and the returned path is relative (img/...).

<details>
<summary>Code:</summary>

```python
class ImageDropWidget(QWidget):

    image_changed = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        save_dir: Path | None = None,
        max_image_side: int | None = None,
    ) -> None:
        """Initialize the image drop widget.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `save_dir` (`Path | None`): If set, images are copied into `save_dir/img/`
        and path returned as `img/filename`.
        - `max_image_side` (`int | None`): If set, downscale images whose width or height
        exceeds this value before storing.

        """
        super().__init__(parent)
        self.image_path = ""
        self._save_dir = Path(save_dir) if save_dir else None
        self._max_image_side = max_image_side
        self._filename_line_edit: QLineEdit | None = None
        self._setup_ui()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle Ctrl+V when focus is on the image label."""
        if (
            watched == self.image_label
            and event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and event.key() == Qt.Key.Key_V
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self._paste_from_clipboard()
            return True
        return super().eventFilter(watched, event)

    def get_image_bytes_and_mime(self) -> tuple[bytes, str] | None:
        """Read the selected image file as bytes and return MIME type."""
        if not self.image_path:
            return None
        path = Path(self.image_path)
        if not path.is_file():
            return None
        mime = _MIME_BY_SUFFIX.get(path.suffix.lower(), "image/png")
        try:
            data = path.read_bytes()
        except OSError:
            return None
        return (data, mime)

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

    def has_image(self) -> bool:
        """Return True if an image is selected."""
        return bool(self.image_path) and Path(self.image_path).is_file()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
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
        self.image_changed.emit()

    def _copy_to_save_dir(self, source: Path) -> Path:
        if self._save_dir is None:
            return source
        img_dir = self._save_dir / "img"
        img_dir.mkdir(parents=True, exist_ok=True)
        suffix = source.suffix.lower()
        base = get_suggested_basename(self._filename_line_edit, source.stem)
        dest = unique_path_in_folder(img_dir, base, suffix)
        shutil.copy2(source, dest)
        return dest

    def _downscale_file_if_needed(self, path: Path) -> None:
        """Overwrite image file with a downscaled version when it exceeds max_image_side."""
        if not self._max_image_side or not path.is_file():
            return
        if path.suffix.lower() == ".svg":
            return
        qimage = QImage(str(path))
        if qimage.isNull():
            return
        scaled = _downscale_qimage(qimage, self._max_image_side)
        if scaled.width() == qimage.width() and scaled.height() == qimage.height():
            return
        scaled.save(str(path))

    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is an image."""
        return Path(file_path).suffix.lower() in _IMAGE_EXTENSIONS

    def _paste_from_clipboard(self) -> None:
        """Set image from clipboard if an image is available."""
        clipboard = QApplication.clipboard()
        qimage = clipboard.image()
        if qimage.isNull():
            return
        qimage = _downscale_qimage(qimage, self._max_image_side)
        if self._save_dir:
            img_dir = self._save_dir / "img"
            img_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
            base = get_suggested_basename(self._filename_line_edit, f"pasted_{stamp}")
            dest = unique_path_in_folder(img_dir, base, ".png")
            if qimage.save(str(dest)):
                self._set_image(str(dest))
        else:
            with NamedTemporaryFile(suffix=".png", delete=False) as f:
                tmp = Path(f.name)
            if qimage.save(str(tmp)):
                self._set_image(str(tmp))

    def _set_image(self, file_path: str) -> None:
        """Set the image from file path."""
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
        self._downscale_file_if_needed(Path(self.image_path))
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
            self.image_changed.emit()
        else:
            self._clear_image()

    def _setup_ui(self) -> None:
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
        install_url_drop_handlers(
            self.image_label,
            lambda paths: self._set_image(paths[0]),
            filter_path=self._is_image_file,
        )

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the image drop widget.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `save_dir` (`Path | None`): If set, images are copied into `save_dir/img/`
and path returned as `img/filename`.
- `max_image_side` (`int | None`): If set, downscale images whose width or height
exceeds this value before storing.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        save_dir: Path | None = None,
        max_image_side: int | None = None,
    ) -> None:
        super().__init__(parent)
        self.image_path = ""
        self._save_dir = Path(save_dir) if save_dir else None
        self._max_image_side = max_image_side
        self._filename_line_edit: QLineEdit | None = None
        self._setup_ui()
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Handle Ctrl+V when focus is on the image label.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if (
            watched == self.image_label
            and event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and event.key() == Qt.Key.Key_V
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self._paste_from_clipboard()
            return True
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `get_image_bytes_and_mime`

```python
def get_image_bytes_and_mime(self) -> tuple[bytes, str] | None
```

Read the selected image file as bytes and return MIME type.

<details>
<summary>Code:</summary>

```python
def get_image_bytes_and_mime(self) -> tuple[bytes, str] | None:
        if not self.image_path:
            return None
        path = Path(self.image_path)
        if not path.is_file():
            return None
        mime = _MIME_BY_SUFFIX.get(path.suffix.lower(), "image/png")
        try:
            data = path.read_bytes()
        except OSError:
            return None
        return (data, mime)
```

</details>

### ⚙️ Method `get_image_path`

```python
def get_image_path(self) -> str
```

Get the selected image path (relative to save_dir when save_dir was set).

<details>
<summary>Code:</summary>

```python
def get_image_path(self) -> str:
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
```

</details>

### ⚙️ Method `has_image`

```python
def has_image(self) -> bool
```

Return True if an image is selected.

<details>
<summary>Code:</summary>

```python
def has_image(self) -> bool:
        return bool(self.image_path) and Path(self.image_path).is_file()
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Handle Ctrl+V to paste image from clipboard.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._paste_from_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `set_date_widget`

```python
def set_date_widget(self, date_edit: QDateEdit | None) -> None
```

Add a Filename row synced with the event date (e.g. for Events template). Call after UI is built.

<details>
<summary>Code:</summary>

```python
def set_date_widget(self, date_edit: QDateEdit | None) -> None:
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
        self.image_changed.emit()
```

</details>

### ⚙️ Method `_copy_to_save_dir`

```python
def _copy_to_save_dir(self, source: Path) -> Path
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _copy_to_save_dir(self, source: Path) -> Path:
        if self._save_dir is None:
            return source
        img_dir = self._save_dir / "img"
        img_dir.mkdir(parents=True, exist_ok=True)
        suffix = source.suffix.lower()
        base = get_suggested_basename(self._filename_line_edit, source.stem)
        dest = unique_path_in_folder(img_dir, base, suffix)
        shutil.copy2(source, dest)
        return dest
```

</details>

### ⚙️ Method `_downscale_file_if_needed`

```python
def _downscale_file_if_needed(self, path: Path) -> None
```

Overwrite image file with a downscaled version when it exceeds max_image_side.

<details>
<summary>Code:</summary>

```python
def _downscale_file_if_needed(self, path: Path) -> None:
        if not self._max_image_side or not path.is_file():
            return
        if path.suffix.lower() == ".svg":
            return
        qimage = QImage(str(path))
        if qimage.isNull():
            return
        scaled = _downscale_qimage(qimage, self._max_image_side)
        if scaled.width() == qimage.width() and scaled.height() == qimage.height():
            return
        scaled.save(str(path))
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
        return Path(file_path).suffix.lower() in _IMAGE_EXTENSIONS
```

</details>

### ⚙️ Method `_paste_from_clipboard`

```python
def _paste_from_clipboard(self) -> None
```

Set image from clipboard if an image is available.

<details>
<summary>Code:</summary>

```python
def _paste_from_clipboard(self) -> None:
        clipboard = QApplication.clipboard()
        qimage = clipboard.image()
        if qimage.isNull():
            return
        qimage = _downscale_qimage(qimage, self._max_image_side)
        if self._save_dir:
            img_dir = self._save_dir / "img"
            img_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
            base = get_suggested_basename(self._filename_line_edit, f"pasted_{stamp}")
            dest = unique_path_in_folder(img_dir, base, ".png")
            if qimage.save(str(dest)):
                self._set_image(str(dest))
        else:
            with NamedTemporaryFile(suffix=".png", delete=False) as f:
                tmp = Path(f.name)
            if qimage.save(str(tmp)):
                self._set_image(str(tmp))
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
        self._downscale_file_if_needed(Path(self.image_path))
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
            self.image_changed.emit()
        else:
            self._clear_image()
```

</details>

### ⚙️ Method `_setup_ui`

```python
def _setup_ui(self) -> None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _setup_ui(self) -> None:
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
        install_url_drop_handlers(
            self.image_label,
            lambda paths: self._set_image(paths[0]),
            filter_path=self._is_image_file,
        )

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
```

</details>

## 🔧 Function `unique_path_in_folder`

```python
def unique_path_in_folder(folder: Path, base_name: str, suffix: str) -> Path
```

Return a path in folder that does not exist, using base_name and suffix with _1, _2 if needed.

<details>
<summary>Code:</summary>

```python
def unique_path_in_folder(folder: Path, base_name: str, suffix: str) -> Path:
    path = folder / (base_name + suffix)
    if not path.exists():
        return path
    i = 1
    while True:
        path = folder / (f"{base_name}_{i}{suffix}")
        if not path.exists():
            return path
        i += 1
```

</details>

## 🔧 Function `_downscale_qimage`

```python
def _downscale_qimage(qimage: QImage, max_side: int | None) -> QImage
```

Return image scaled down so neither side exceeds max_side.

<details>
<summary>Code:</summary>

```python
def _downscale_qimage(qimage: QImage, max_side: int | None) -> QImage:
    if qimage.isNull() or not max_side or max_side <= 0:
        return qimage
    if qimage.width() <= max_side and qimage.height() <= max_side:
        return qimage
    return qimage.scaled(
        max_side,
        max_side,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
```

</details>
