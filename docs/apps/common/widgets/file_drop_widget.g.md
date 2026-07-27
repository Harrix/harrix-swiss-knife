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
- [🏛️ Class `FilesListWidget`](#%EF%B8%8F-class-fileslistwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `get_file_paths`](#%EF%B8%8F-method-get_file_paths)
  - [⚙️ Method `set_file_paths`](#%EF%B8%8F-method-set_file_paths)

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
        """Initialize single-file drop widget."""
        super().__init__(parent)
        self.file_path = ""
        self._setup_ui()

    def get_file_path(self) -> str:
        """Return selected file path."""
        return self.file_path

    def set_file_path(self, path: str) -> None:
        """Set file path when the file exists."""
        if path and Path(path).exists():
            self._set_file(path)

    def _browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file", "", "All files (*)")
        if file_path:
            self._set_file(file_path)

    def _clear_file(self) -> None:
        self.file_path = ""
        self.file_label.setText("Drag and drop file here, or right-click")
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)

    def _set_file(self, file_path: str) -> None:
        self.file_path = file_path
        self.file_label.setText(f"File: {Path(file_path).name}")
        self.file_label.setStyleSheet(_SELECTED_DROP_STYLE)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        self.file_label = QLabel("Drag and drop file here, or right-click")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)
        self.file_label.setMinimumHeight(60)
        self.file_label.setToolTip("Right-click for Select File / Clear")
        install_url_drop_handlers(self.file_label, lambda paths: self._set_file(paths[0]))
        self.file_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_label.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.file_label)
        self.setLayout(layout)

    def _show_context_menu(self, pos) -> None:  # noqa: ANN001
        menu = QMenu(self)
        select_action = menu.addAction("📁 Select File")
        select_action.triggered.connect(self._browse_file)
        if self.file_path:
            clear_action = menu.addAction("🗑️ Clear")
            clear_action.triggered.connect(self._clear_file)
        menu.exec(self.file_label.mapToGlobal(pos))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize single-file drop widget.

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

Return selected file path.

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

Set file path when the file exists.

<details>
<summary>Code:</summary>

```python
def set_file_path(self, path: str) -> None:
        if path and Path(path).exists():
            self._set_file(path)
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
        """Initialize multi-file drop widget."""
        super().__init__(parent)
        self.file_paths: list[str] = []
        self._setup_ui()

    def get_file_paths(self) -> list[str]:
        """Return copy of selected file paths."""
        return self.file_paths.copy()

    def set_file_paths(self, paths: list[str]) -> None:
        """Replace selected files with existing paths from `paths`."""
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
        self.list_widget.setToolTip("Drag and drop files, or right-click for actions")
        install_url_drop_handlers(self.list_widget, self._on_drop_paths)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def _show_context_menu(self, pos) -> None:  # noqa: ANN001
        menu = QMenu(self)
        add_action = menu.addAction("➕ Add Files")  # noqa: RUF001
        add_action.triggered.connect(self._add_files)
        if self.list_widget.currentRow() >= 0:
            remove_action = menu.addAction("➖ Remove Selected")  # noqa: RUF001
            remove_action.triggered.connect(self._remove_selected)
        if self.file_paths:
            clear_action = menu.addAction("🗑️ Clear All")
            clear_action.triggered.connect(self._clear_all)
        menu.exec(self.list_widget.mapToGlobal(pos))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize multi-file drop widget.

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

Return copy of selected file paths.

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

Replace selected files with existing paths from `paths`.

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
