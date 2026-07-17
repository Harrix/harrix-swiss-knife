---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_drop_widget.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ImageDropWidget`](#️-class-imagedropwidget)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `configure_filename_row`](#️-method-configure_filename_row)
  - [⚙️ Method `eventFilter`](#️-method-eventfilter)
  - [⚙️ Method `get_image_bytes_and_mime`](#️-method-get_image_bytes_and_mime)
  - [⚙️ Method `get_image_path`](#️-method-get_image_path)
  - [⚙️ Method `has_image`](#️-method-has_image)
  - [⚙️ Method `keyPressEvent`](#️-method-keypressevent)
  - [⚙️ Method `paste_from_clipboard`](#️-method-paste_from_clipboard)
  - [⚙️ Method `paste_image_from_clipboard`](#️-method-paste_image_from_clipboard)
  - [⚙️ Method `refresh_filename_base`](#️-method-refresh_filename_base)
  - [⚙️ Method `reset_filename_row`](#️-method-reset_filename_row)
  - [⚙️ Method `set_image_path`](#️-method-set_image_path)
  - [⚙️ Method `set_on_paths_added`](#️-method-set_on_paths_added)
  - [⚙️ Method `set_save_dir`](#️-method-set_save_dir)
- [🔧 Function `is_image_file_path`](#-function-is_image_file_path)
- [🔧 Function `save_clipboard_image_to_temp_file`](#-function-save_clipboard_image_to_temp_file)
- [🔧 Function `unique_path_in_folder`](#-function-unique_path_in_folder)

</details>

## 🏛️ Class `ImageDropWidget`

```python
class ImageDropWidget(QWidget)
```

Widget for single image selection with drag and drop and clipboard paste.

When save_dir is set (e.g. parent of the target Markdown file), dropped or pasted
images are copied into save_dir/img/ and the returned path is relative (`img/…`).

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
        fallback_text_edit: QPlainTextEdit | None = None,
    ) -> None:
        """Initialize the image drop widget.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `save_dir` (`Path | None`): If set, images are copied into `save_dir/img/`
        and path returned as `img/filename`.
        - `max_image_side` (`int | None`): If set, downscale images whose width or height
        exceeds this value before storing.
        - `fallback_text_edit` (`QPlainTextEdit | None`): When clipboard has text but no image,
        paste into this editor instead (e.g. paired text field in AI source dialog).

        """
        super().__init__(parent)
        self.image_path = ""
        self._save_dir = Path(save_dir) if save_dir else None
        self._max_image_side = max_image_side
        self._fallback_text_edit = fallback_text_edit
        self._filename_line_edit: QLineEdit | None = None
        self._filename_row: ImageFilenameRow | None = None
        self._on_paths_added: Callable[[list[str]], None] | None = None
        self._setup_ui()

    def configure_filename_row(
        self,
        date_edit: QDateEdit | None,
        source_widget: QLineEdit | QComboBox | None = None,
        *,
        source_field_name: str | None = None,
        initial_base: str | None = None,
        lock_auto_sync: bool = False,
    ) -> None:
        """Add filename row synced with date and optional linked template field."""
        if not date_edit or not self._save_dir:
            return
        if self._filename_line_edit is not None:
            return

        row = ImageFilenameRow(
            multiple=False,
            date_edit=date_edit,
            source_widget=source_widget,
            source_field_name=source_field_name,
            initial_base=initial_base,
            lock_auto_sync=lock_auto_sync,
        )
        self._filename_line_edit = row.line_edit
        self._filename_row = row
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.insertWidget(layout.count() - 1, row)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle Ctrl+V when focus is on the image label."""
        if (
            watched == self.image_label
            and event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and event.key() == Qt.Key.Key_V
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self._paste_image_from_clipboard()
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
            self._paste_image_from_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)

    def paste_from_clipboard(self) -> None:
        """Paste text into fallback editor when available, otherwise paste image."""
        self._paste_smart_from_clipboard()

    def paste_image_from_clipboard(self) -> None:
        """Paste image from clipboard into the image area."""
        self._paste_image_from_clipboard()

    def refresh_filename_base(self) -> None:
        """Recompute filename base from linked template fields."""
        if self._filename_row is not None:
            self._filename_row.refresh_auto_base()

    def reset_filename_row(self) -> None:
        """Remove filename row so it can be reconfigured (e.g. when switching entries)."""
        if self._filename_line_edit is None:
            return
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            for index in range(layout.count()):
                item = layout.itemAt(index)
                widget = item.widget() if item is not None else None
                if isinstance(widget, ImageFilenameRow):
                    layout.removeWidget(widget)
                    widget.deleteLater()
                    break
        self._filename_line_edit = None
        self._filename_row = None

    def set_image_path(self, path: str) -> None:
        """Set the image path."""
        if path and Path(path).exists():
            self._set_image(path)

    def set_on_paths_added(self, callback: Callable[[list[str]], None] | None) -> None:
        """Register callback invoked with original paths when user adds an image (not on load)."""
        self._on_paths_added = callback

    def set_save_dir(self, save_dir: Path | None) -> None:
        """Update target directory for copied images."""
        self._save_dir = Path(save_dir) if save_dir else None

    def _add_user_image(self, file_path: str) -> None:
        """Notify listeners and copy the image using an updated filename base."""
        source = str(Path(file_path).resolve())
        if self._on_paths_added is not None:
            self._on_paths_added([source])
        self._set_image(file_path)

    def _browse_file(self) -> None:
        """Open file dialog to select image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.avif);;All files (*)",
        )
        if file_path:
            self._add_user_image(file_path)

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
        return is_image_file_path(file_path)

    def _paste_image_from_clipboard(self) -> None:
        """Set image from clipboard if an image is available."""
        if self._save_dir:
            clipboard = QApplication.clipboard()
            qimage = clipboard.image()
            if qimage.isNull():
                return
            qimage = _downscale_qimage(qimage, self._max_image_side)
            img_dir = self._save_dir / "img"
            img_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
            base = get_suggested_basename(self._filename_line_edit, f"pasted_{stamp}")
            dest = unique_path_in_folder(img_dir, base, ".png")
            if qimage.save(str(dest)):
                self._set_image(str(dest))
            return
        temp_path = save_clipboard_image_to_temp_file(max_image_side=self._max_image_side)
        if temp_path:
            self._set_image(temp_path)

    def _paste_smart_from_clipboard(self) -> None:
        """Paste clipboard text into fallback editor, or image when text is unavailable."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if self._fallback_text_edit is not None and text:
            self._fallback_text_edit.insertPlainText(text)
            return
        self._paste_image_from_clipboard()

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
        pixmap = load_image_pixmap(self.image_path)
        selected_style = """
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
                background-color: #f0f8f0;
            }
        """
        if pixmap is not None and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setText("")
        else:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText(Path(self.image_path).name)
        self.image_label.setStyleSheet(selected_style)
        self.image_changed.emit()

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
            lambda paths: self._add_user_image(paths[0]),
            filter_path=self._is_image_file,
        )

        button_layout = QHBoxLayout()

        self.browse_button = make_emoji_push_button("Select File", "📁")
        self.browse_button.clicked.connect(self._browse_file)
        button_layout.addWidget(self.browse_button)

        self.paste_button = make_emoji_push_button("Paste", "📋")
        self.paste_button.clicked.connect(self._paste_smart_from_clipboard)
        button_layout.addWidget(self.paste_button)

        self.clear_button = make_emoji_push_button("Clear", "🗑️")
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
- `fallback_text_edit` (`QPlainTextEdit | None`): When clipboard has text but no image,
  paste into this editor instead (e.g. paired text field in AI source dialog).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        save_dir: Path | None = None,
        max_image_side: int | None = None,
        fallback_text_edit: QPlainTextEdit | None = None,
    ) -> None:
        super().__init__(parent)
        self.image_path = ""
        self._save_dir = Path(save_dir) if save_dir else None
        self._max_image_side = max_image_side
        self._fallback_text_edit = fallback_text_edit
        self._filename_line_edit: QLineEdit | None = None
        self._filename_row: ImageFilenameRow | None = None
        self._on_paths_added: Callable[[list[str]], None] | None = None
        self._setup_ui()
```

</details>

### ⚙️ Method `configure_filename_row`

```python
def configure_filename_row(self, date_edit: QDateEdit | None, source_widget: QLineEdit | QComboBox | None = None) -> None
```

Add filename row synced with date and optional linked template field.

<details>
<summary>Code:</summary>

```python
def configure_filename_row(
        self,
        date_edit: QDateEdit | None,
        source_widget: QLineEdit | QComboBox | None = None,
        *,
        source_field_name: str | None = None,
        initial_base: str | None = None,
        lock_auto_sync: bool = False,
    ) -> None:
        if not date_edit or not self._save_dir:
            return
        if self._filename_line_edit is not None:
            return

        row = ImageFilenameRow(
            multiple=False,
            date_edit=date_edit,
            source_widget=source_widget,
            source_field_name=source_field_name,
            initial_base=initial_base,
            lock_auto_sync=lock_auto_sync,
        )
        self._filename_line_edit = row.line_edit
        self._filename_row = row
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.insertWidget(layout.count() - 1, row)
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
            self._paste_image_from_clipboard()
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
            self._paste_image_from_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `paste_from_clipboard`

```python
def paste_from_clipboard(self) -> None
```

Paste text into fallback editor when available, otherwise paste image.

<details>
<summary>Code:</summary>

```python
def paste_from_clipboard(self) -> None:
        self._paste_smart_from_clipboard()
```

</details>

### ⚙️ Method `paste_image_from_clipboard`

```python
def paste_image_from_clipboard(self) -> None
```

Paste image from clipboard into the image area.

<details>
<summary>Code:</summary>

```python
def paste_image_from_clipboard(self) -> None:
        self._paste_image_from_clipboard()
```

</details>

### ⚙️ Method `refresh_filename_base`

```python
def refresh_filename_base(self) -> None
```

Recompute filename base from linked template fields.

<details>
<summary>Code:</summary>

```python
def refresh_filename_base(self) -> None:
        if self._filename_row is not None:
            self._filename_row.refresh_auto_base()
```

</details>

### ⚙️ Method `reset_filename_row`

```python
def reset_filename_row(self) -> None
```

Remove filename row so it can be reconfigured (e.g. when switching entries).

<details>
<summary>Code:</summary>

```python
def reset_filename_row(self) -> None:
        if self._filename_line_edit is None:
            return
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            for index in range(layout.count()):
                item = layout.itemAt(index)
                widget = item.widget() if item is not None else None
                if isinstance(widget, ImageFilenameRow):
                    layout.removeWidget(widget)
                    widget.deleteLater()
                    break
        self._filename_line_edit = None
        self._filename_row = None
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

### ⚙️ Method `set_on_paths_added`

```python
def set_on_paths_added(self, callback: Callable[[list[str]], None] | None) -> None
```

Register callback invoked with original paths when user adds an image (not on load).

<details>
<summary>Code:</summary>

```python
def set_on_paths_added(self, callback: Callable[[list[str]], None] | None) -> None:
        self._on_paths_added = callback
```

</details>

### ⚙️ Method `set_save_dir`

```python
def set_save_dir(self, save_dir: Path | None) -> None
```

Update target directory for copied images.

<details>
<summary>Code:</summary>

```python
def set_save_dir(self, save_dir: Path | None) -> None:
        self._save_dir = Path(save_dir) if save_dir else None
```

</details>

## 🔧 Function `is_image_file_path`

```python
def is_image_file_path(file_path: str) -> bool
```

Return True if path has a supported image extension.

<details>
<summary>Code:</summary>

```python
def is_image_file_path(file_path: str) -> bool:
    return Path(file_path).suffix.lower() in _IMAGE_EXTENSIONS
```

</details>

## 🔧 Function `save_clipboard_image_to_temp_file`

```python
def save_clipboard_image_to_temp_file() -> str | None
```

Save clipboard image to a temporary PNG file and return its path.

<details>
<summary>Code:</summary>

```python
def save_clipboard_image_to_temp_file(*, max_image_side: int | None = None) -> str | None:
    qimage = QApplication.clipboard().image()
    if qimage.isNull():
        return None
    qimage = _downscale_qimage(qimage, max_image_side)
    with NamedTemporaryFile(suffix=".png", delete=False) as f:
        tmp = Path(f.name)
    if qimage.save(str(tmp)):
        return str(tmp)
    return None
```

</details>

## 🔧 Function `unique_path_in_folder`

```python
def unique_path_in_folder(folder: Path, base_name: str, suffix: str) -> Path
```

Return a path in folder that does not exist, using base_name and suffix with \_1, \_2 if needed.

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
