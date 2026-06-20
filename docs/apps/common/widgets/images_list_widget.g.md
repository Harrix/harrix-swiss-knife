---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `images_list_widget.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ImagesListWidget`](#️-class-imageslistwidget)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `get_image_paths`](#️-method-get_image_paths)
  - [⚙️ Method `set_date_widget`](#️-method-set_date_widget)
  - [⚙️ Method `set_image_paths`](#️-method-set_image_paths)
  - [⚙️ Method `_add_image_path`](#️-method-_add_image_path)
  - [⚙️ Method `_add_images`](#️-method-_add_images)
  - [⚙️ Method `_clear_all`](#️-method-_clear_all)
  - [⚙️ Method `_is_image_file`](#️-method-_is_image_file)
  - [⚙️ Method `_on_drop_paths`](#️-method-_on_drop_paths)
  - [⚙️ Method `_remove_selected`](#️-method-_remove_selected)
  - [⚙️ Method `_setup_ui`](#️-method-_setup_ui)

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

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        save_dir: Path | None = None,
    ) -> None:
        """Initialize multi-image drop widget."""
        super().__init__(parent)
        self.image_paths: list[str] = []
        self._save_dir = Path(save_dir) if save_dir else None
        self._filename_line_edit: QLineEdit | None = None
        self._setup_ui()

    def get_image_paths(self) -> list[str]:
        """Return image paths, relative to ``save_dir`` when configured."""
        if not self._save_dir:
            return self.image_paths.copy()
        result = []
        for path in self.image_paths:
            if not path:
                continue
            try:
                resolved = Path(path).resolve()
                save_resolved = self._save_dir.resolve()
                if str(resolved).startswith(str(save_resolved)):
                    result.append(str(resolved.relative_to(save_resolved)).replace("\\", "/"))
                else:
                    result.append(path)
            except (ValueError, OSError):
                result.append(path)
        return result

    def set_date_widget(self, date_edit: QDateEdit | None) -> None:
        """Add filename base row synced with the event date widget."""
        if not date_edit or not self._save_dir or self._filename_line_edit is not None:
            return
        self._filename_line_edit = QLineEdit()
        self._filename_line_edit.setPlaceholderText("Base name (e.g. date); images will be named base_01, base_02, ...")
        self._filename_line_edit.setText(date_edit.date().toString("yyyy-MM-dd"))
        date_edit.dateChanged.connect(lambda d, edit=self._filename_line_edit: edit.setText(d.toString("yyyy-MM-dd")))
        filerow = QHBoxLayout()
        filerow.addWidget(QLabel("Filename base:"))
        filerow.addWidget(self._filename_line_edit, 1)
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.insertLayout(layout.count() - 1, filerow)

    def set_image_paths(self, paths: list[str]) -> None:
        """Replace selected images with existing paths from ``paths``."""
        self._clear_all()
        for path in paths:
            if Path(path).exists():
                self._add_image_path(path)

    def _add_image_path(self, file_path: str) -> None:
        source = Path(file_path).resolve()
        if not source.exists():
            return
        path_to_store = file_path
        if self._save_dir:
            try:
                img_dir = self._save_dir.resolve() / "img"
                img_dir.mkdir(parents=True, exist_ok=True)
                if img_dir in source.parents or source.parent == img_dir:
                    path_to_store = str(source)
                else:
                    suffix = source.suffix.lower()
                    base = get_suggested_basename(self._filename_line_edit, source.stem)
                    dest = unique_path_numbered(img_dir, base, suffix)
                    shutil.copy2(source, dest)
                    path_to_store = str(dest)
            except (OSError, ValueError):
                pass
        self.image_paths.append(path_to_store)
        item = QListWidgetItem(Path(path_to_store).name)
        item.setData(Qt.ItemDataRole.UserRole, path_to_store)
        self.list_widget.addItem(item)

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

    def _clear_all(self) -> None:
        self.image_paths.clear()
        self.list_widget.clear()

    def _is_image_file(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in _IMAGE_EXTENSIONS

    def _on_drop_paths(self, paths: list[str]) -> None:
        for file_path in paths:
            if self._is_image_file(file_path) and file_path not in self.image_paths:
                self._add_image_path(file_path)

    def _remove_selected(self) -> None:
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path in self.image_paths:
                    self.image_paths.remove(file_path)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(150)
        install_url_drop_handlers(self.list_widget, self._on_drop_paths, filter_path=self._is_image_file)

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

Initialize multi-image drop widget.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        save_dir: Path | None = None,
    ) -> None:
        super().__init__(parent)
        self.image_paths: list[str] = []
        self._save_dir = Path(save_dir) if save_dir else None
        self._filename_line_edit: QLineEdit | None = None
        self._setup_ui()
```

</details>

### ⚙️ Method `get_image_paths`

```python
def get_image_paths(self) -> list[str]
```

Return image paths, relative to `save_dir` when configured.

<details>
<summary>Code:</summary>

```python
def get_image_paths(self) -> list[str]:
        if not self._save_dir:
            return self.image_paths.copy()
        result = []
        for path in self.image_paths:
            if not path:
                continue
            try:
                resolved = Path(path).resolve()
                save_resolved = self._save_dir.resolve()
                if str(resolved).startswith(str(save_resolved)):
                    result.append(str(resolved.relative_to(save_resolved)).replace("\\", "/"))
                else:
                    result.append(path)
            except (ValueError, OSError):
                result.append(path)
        return result
```

</details>

### ⚙️ Method `set_date_widget`

```python
def set_date_widget(self, date_edit: QDateEdit | None) -> None
```

Add filename base row synced with the event date widget.

<details>
<summary>Code:</summary>

```python
def set_date_widget(self, date_edit: QDateEdit | None) -> None:
        if not date_edit or not self._save_dir or self._filename_line_edit is not None:
            return
        self._filename_line_edit = QLineEdit()
        self._filename_line_edit.setPlaceholderText("Base name (e.g. date); images will be named base_01, base_02, ...")
        self._filename_line_edit.setText(date_edit.date().toString("yyyy-MM-dd"))
        date_edit.dateChanged.connect(lambda d, edit=self._filename_line_edit: edit.setText(d.toString("yyyy-MM-dd")))
        filerow = QHBoxLayout()
        filerow.addWidget(QLabel("Filename base:"))
        filerow.addWidget(self._filename_line_edit, 1)
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.insertLayout(layout.count() - 1, filerow)
```

</details>

### ⚙️ Method `set_image_paths`

```python
def set_image_paths(self, paths: list[str]) -> None
```

Replace selected images with existing paths from `paths`.

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

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _add_image_path(self, file_path: str) -> None:
        source = Path(file_path).resolve()
        if not source.exists():
            return
        path_to_store = file_path
        if self._save_dir:
            try:
                img_dir = self._save_dir.resolve() / "img"
                img_dir.mkdir(parents=True, exist_ok=True)
                if img_dir in source.parents or source.parent == img_dir:
                    path_to_store = str(source)
                else:
                    suffix = source.suffix.lower()
                    base = get_suggested_basename(self._filename_line_edit, source.stem)
                    dest = unique_path_numbered(img_dir, base, suffix)
                    shutil.copy2(source, dest)
                    path_to_store = str(dest)
            except (OSError, ValueError):
                pass
        self.image_paths.append(path_to_store)
        item = QListWidgetItem(Path(path_to_store).name)
        item.setData(Qt.ItemDataRole.UserRole, path_to_store)
        self.list_widget.addItem(item)
```

</details>

### ⚙️ Method `_add_images`

```python
def _add_images(self) -> None
```

_No docstring provided._

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

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _clear_all(self) -> None:
        self.image_paths.clear()
        self.list_widget.clear()
```

</details>

### ⚙️ Method `_is_image_file`

```python
def _is_image_file(self, file_path: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_image_file(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in _IMAGE_EXTENSIONS
```

</details>

### ⚙️ Method `_on_drop_paths`

```python
def _on_drop_paths(self, paths: list[str]) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _on_drop_paths(self, paths: list[str]) -> None:
        for file_path in paths:
            if self._is_image_file(file_path) and file_path not in self.image_paths:
                self._add_image_path(file_path)
```

</details>

### ⚙️ Method `_remove_selected`

```python
def _remove_selected(self) -> None
```

_No docstring provided._

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

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(150)
        install_url_drop_handlers(self.list_widget, self._on_drop_paths, filter_path=self._is_image_file)

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
