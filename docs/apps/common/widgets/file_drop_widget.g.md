---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `file_drop_widget.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FileDropWidget`](#%EF%B8%8F-class-filedropwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_file_path`](#%EF%B8%8F-method-get_file_path)
  - [⚙️ Method `set_file_path`](#%EF%B8%8F-method-set_file_path)
  - [⚙️ Method `_browse_file`](#%EF%B8%8F-method-_browse_file)
  - [⚙️ Method `_clear_file`](#%EF%B8%8F-method-_clear_file)
  - [⚙️ Method `_set_file`](#%EF%B8%8F-method-_set_file)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)
- [🏛️ Class `FilesListWidget`](#%EF%B8%8F-class-fileslistwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `get_file_paths`](#%EF%B8%8F-method-get_file_paths)
  - [⚙️ Method `set_file_paths`](#%EF%B8%8F-method-set_file_paths)
  - [⚙️ Method `_add_file_path`](#%EF%B8%8F-method-_add_file_path)
  - [⚙️ Method `_add_files`](#%EF%B8%8F-method-_add_files)
  - [⚙️ Method `_clear_all`](#%EF%B8%8F-method-_clear_all)
  - [⚙️ Method `_on_drop_paths`](#%EF%B8%8F-method-_on_drop_paths)
  - [⚙️ Method `_remove_selected`](#%EF%B8%8F-method-_remove_selected)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui-1)

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
        super().__init__(parent)
        self.file_path = ""
        self._setup_ui()

    def get_file_path(self) -> str:
        return self.file_path

    def set_file_path(self, path: str) -> None:
        if path and Path(path).exists():
            self._set_file(path)

    def _browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file", "", "All files (*)")
        if file_path:
            self._set_file(file_path)

    def _clear_file(self) -> None:
        self.file_path = ""
        self.file_label.setText("Drag and drop file here or click button")
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)

    def _set_file(self, file_path: str) -> None:
        self.file_path = file_path
        self.file_label.setText(f"File: {Path(file_path).name}")
        self.file_label.setStyleSheet(_SELECTED_DROP_STYLE)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        self.file_label = QLabel("Drag and drop file here or click button")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)
        self.file_label.setMinimumHeight(60)
        install_url_drop_handlers(self.file_label, lambda paths: self._set_file(paths[0]))

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

_No docstring provided._

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

_No docstring provided._

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

_No docstring provided._

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

_No docstring provided._

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

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _clear_file(self) -> None:
        self.file_path = ""
        self.file_label.setText("Drag and drop file here or click button")
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)
```

</details>

### ⚙️ Method `_set_file`

```python
def _set_file(self, file_path: str) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _set_file(self, file_path: str) -> None:
        self.file_path = file_path
        self.file_label.setText(f"File: {Path(file_path).name}")
        self.file_label.setStyleSheet(_SELECTED_DROP_STYLE)
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
        self.file_label = QLabel("Drag and drop file here or click button")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)
        self.file_label.setMinimumHeight(60)
        install_url_drop_handlers(self.file_label, lambda paths: self._set_file(paths[0]))

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
        super().__init__(parent)
        self.file_paths: list[str] = []
        self._setup_ui()

    def get_file_paths(self) -> list[str]:
        return self.file_paths.copy()

    def set_file_paths(self, paths: list[str]) -> None:
        self._clear_all()
        for path in paths:
            if Path(path).exists():
                self._add_file_path(path)

    def _add_file_path(self, file_path: str) -> None:
        self.file_paths.append(file_path)
        item = QListWidgetItem(Path(file_path).name)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.list_widget.addItem(item)

    def _add_files(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select files", "", "All files (*)")
        for file_path in file_paths:
            if file_path not in self.file_paths:
                self._add_file_path(file_path)

    def _clear_all(self) -> None:
        self.file_paths.clear()
        self.list_widget.clear()

    def _on_drop_paths(self, paths: list[str]) -> None:
        for file_path in paths:
            if file_path not in self.file_paths:
                self._add_file_path(file_path)

    def _remove_selected(self) -> None:
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path in self.file_paths:
                    self.file_paths.remove(file_path)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(150)
        install_url_drop_handlers(self.list_widget, self._on_drop_paths)

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

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.file_paths: list[str] = []
        self._setup_ui()
```

</details>

### ⚙️ Method `get_file_paths`

```python
def get_file_paths(self) -> list[str]
```

_No docstring provided._

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

_No docstring provided._

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

_No docstring provided._

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

_No docstring provided._

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

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _clear_all(self) -> None:
        self.file_paths.clear()
        self.list_widget.clear()
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
            if file_path not in self.file_paths:
                self._add_file_path(file_path)
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
                if file_path in self.file_paths:
                    self.file_paths.remove(file_path)
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
        install_url_drop_handlers(self.list_widget, self._on_drop_paths)

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
