---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dialog_widgets.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ChoiceWithDescriptionDelegate`](#️-class-choicewithdescriptiondelegate)
  - [⚙️ Method `paint`](#️-method-paint)
  - [⚙️ Method `sizeHint`](#️-method-sizehint)
- [🏛️ Class `DragDropFileDialog`](#️-class-dragdropfiledialog)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `add_files`](#️-method-add_files)
  - [⚙️ Method `clear_files`](#️-method-clear_files)
  - [⚙️ Method `get_max_size`](#️-method-get_max_size)
  - [⚙️ Method `get_resize_enabled`](#️-method-get_resize_enabled)
  - [⚙️ Method `get_selected_files`](#️-method-get_selected_files)
  - [⚙️ Method `select_files`](#️-method-select_files)
  - [⚙️ Method `setup_ui`](#️-method-setup_ui)
- [🏛️ Class `StandardActionDialog`](#️-class-standardactiondialog)
  - [⚙️ Method `__init__`](#️-method-__init__-1)
  - [⚙️ Method `showEvent`](#️-method-showevent)

</details>

## 🏛️ Class `ChoiceWithDescriptionDelegate`

```python
class ChoiceWithDescriptionDelegate(QStyledItemDelegate)
```

Custom delegate for displaying choices with descriptions in different font sizes.

<details>
<summary>Code:</summary>

```python
class ChoiceWithDescriptionDelegate(QStyledItemDelegate):

    MIN_LINES_FOR_DESCRIPTION = 2

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Render choice title + description with rich text."""
        painter.save()

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            painter.restore()
            return

        lines = text.split("\n")
        if len(lines) < self.MIN_LINES_FOR_DESCRIPTION:
            super().paint(painter, option, index)
            painter.restore()
            return

        choice = lines[0]
        description = "\n".join(lines[1:]).strip()

        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        if is_selected:
            painter.fillRect(option.rect, option.palette.highlight())
            text_color = option.palette.highlightedText().color()
        elif is_hovered:
            painter.fillRect(option.rect, option.palette.alternateBase())
            text_color = option.palette.text().color()
        else:
            text_color = option.palette.text().color()

        # Escape HTML and preserve line breaks
        escaped_choice = escape(choice)
        escaped_description = escape(description).replace("\n", "<br>")

        html_content = (
            f'<div style="font-family: Arial, sans-serif; color: {text_color.name()};">'
            f'<div style="font-size: 12pt; font-weight: bold; margin-bottom: 2px;">'
            f"{escaped_choice}"
            f"</div>"
            f'<div style="font-size: 9pt; font-style: italic; color: {text_color.name()}; '
            f'opacity: 0.7; margin-left: 10px; white-space: pre-wrap;">'
            f"{escaped_description}"
            f"</div>"
            f"</div>"
        )

        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.setTextWidth(option.rect.width())

        painter.translate(option.rect.topLeft())
        doc.drawContents(painter)

        painter.restore()

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Return size hint for rich-text item."""
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            return super().sizeHint(option, index)

        lines = text.split("\n")
        if len(lines) < self.MIN_LINES_FOR_DESCRIPTION:
            return super().sizeHint(option, index)

        choice = lines[0]
        description = "\n".join(lines[1:]).strip()

        escaped_choice = escape(choice)
        escaped_description = escape(description).replace("\n", "<br>")

        html_content = f"""
        <div style="font-family: Arial, sans-serif;">
            <div style="font-size: 12pt; font-weight: bold; margin-bottom: 2px;">
                {escaped_choice}
            </div>
            <div style="font-size: 9pt; font-style: italic; color: #666666; margin-left: 10px; white-space: pre-wrap;">
                {escaped_description}
            </div>
        </div>
        """

        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.setTextWidth(option.rect.width())

        doc_size = doc.size()
        return QSize(int(doc_size.width()), int(doc_size.height()) + 5)
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Render choice title + description with rich text.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        painter.save()

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            painter.restore()
            return

        lines = text.split("\n")
        if len(lines) < self.MIN_LINES_FOR_DESCRIPTION:
            super().paint(painter, option, index)
            painter.restore()
            return

        choice = lines[0]
        description = "\n".join(lines[1:]).strip()

        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        if is_selected:
            painter.fillRect(option.rect, option.palette.highlight())
            text_color = option.palette.highlightedText().color()
        elif is_hovered:
            painter.fillRect(option.rect, option.palette.alternateBase())
            text_color = option.palette.text().color()
        else:
            text_color = option.palette.text().color()

        # Escape HTML and preserve line breaks
        escaped_choice = escape(choice)
        escaped_description = escape(description).replace("\n", "<br>")

        html_content = (
            f'<div style="font-family: Arial, sans-serif; color: {text_color.name()};">'
            f'<div style="font-size: 12pt; font-weight: bold; margin-bottom: 2px;">'
            f"{escaped_choice}"
            f"</div>"
            f'<div style="font-size: 9pt; font-style: italic; color: {text_color.name()}; '
            f'opacity: 0.7; margin-left: 10px; white-space: pre-wrap;">'
            f"{escaped_description}"
            f"</div>"
            f"</div>"
        )

        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.setTextWidth(option.rect.width())

        painter.translate(option.rect.topLeft())
        doc.drawContents(painter)

        painter.restore()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize
```

Return size hint for rich-text item.

<details>
<summary>Code:</summary>

```python
def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            return super().sizeHint(option, index)

        lines = text.split("\n")
        if len(lines) < self.MIN_LINES_FOR_DESCRIPTION:
            return super().sizeHint(option, index)

        choice = lines[0]
        description = "\n".join(lines[1:]).strip()

        escaped_choice = escape(choice)
        escaped_description = escape(description).replace("\n", "<br>")

        html_content = f"""
        <div style="font-family: Arial, sans-serif;">
            <div style="font-size: 12pt; font-weight: bold; margin-bottom: 2px;">
                {escaped_choice}
            </div>
            <div style="font-size: 9pt; font-style: italic; color: #666666; margin-left: 10px; white-space: pre-wrap;">
                {escaped_description}
            </div>
        </div>
        """

        doc = QTextDocument()
        doc.setHtml(html_content)
        doc.setTextWidth(option.rect.width())

        doc_size = doc.size()
        return QSize(int(doc_size.width()), int(doc_size.height()) + 5)
```

</details>

## 🏛️ Class `DragDropFileDialog`

```python
class DragDropFileDialog(QDialog)
```

Custom dialog with drag-and-drop support for file selection.

<details>
<summary>Code:</summary>

```python
class DragDropFileDialog(QDialog):

    def __init__(
        self,
        title: str,
        default_path: str,
        filter_: str,
        target_size: QSize,
        parent: QWidget | None = None,
        *,
        with_resize_option: bool = False,
    ) -> None:
        """Create file-selection dialog with optional resize controls."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setAcceptDrops(True)
        self.setMinimumSize(target_size)
        self.resize(target_size)

        self.default_path = default_path
        self.filter_ = filter_
        self.selected_files: list[str] = []
        self.with_resize_option = with_resize_option

        self.setup_ui()

    def add_files(self, file_paths: list[str]) -> None:
        """Add files to selection list (deduplicated)."""
        for file_path in file_paths:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_list.addItem(file_path)

    def clear_files(self) -> None:
        """Clear selected files list."""
        self.selected_files.clear()
        self.files_list.clear()

    def get_max_size(self) -> str | None:
        """Return max size string, or None if resize disabled/empty."""
        if not self.get_resize_enabled() or not hasattr(self, "max_size_edit"):
            return None
        text = self.max_size_edit.text().strip()
        return text or None

    def get_resize_enabled(self) -> bool:
        """Return True when resize checkbox enabled and checked."""
        if not self.with_resize_option or not hasattr(self, "resize_checkbox"):
            return False
        return self.resize_checkbox.isChecked()

    def get_selected_files(self) -> list[str]:
        """Return selected file paths."""
        return self.selected_files

    def select_files(self) -> None:
        """Open native file dialog and add selected files."""
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.default_path, self.filter_)
        if filenames:
            self.add_files(filenames)

    def setup_ui(self) -> None:
        """Build widget layout for drag-drop file selection."""
        layout = QVBoxLayout(self)

        title_label = QLabel("Select files for processing")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        self.drop_area = QLabel("Drag files here or click 'Select Files' button")
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background-color: #f9f9f9;
                color: #666;
                font-size: 12px;
            }
            QLabel:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
            }
        """)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setMinimumHeight(150)
        layout.addWidget(self.drop_area)

        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(100)
        layout.addWidget(self.files_list)

        if self.with_resize_option:
            resize_layout = QHBoxLayout()
            self.resize_checkbox = QCheckBox("Resize images (max size, px)")
            self.resize_checkbox.setChecked(False)
            resize_layout.addWidget(self.resize_checkbox)
            self.max_size_edit = QLineEdit()
            self.max_size_edit.setPlaceholderText("1024")
            self.max_size_edit.setText("1024")
            self.max_size_edit.setEnabled(False)

            def toggle_max_size_edit(checked: bool) -> None:  # noqa: FBT001
                self.max_size_edit.setEnabled(checked)

            self.resize_checkbox.toggled.connect(toggle_max_size_edit)
            resize_layout.addWidget(self.max_size_edit)
            resize_layout.addStretch()
            layout.addLayout(resize_layout)

        buttons_layout = QHBoxLayout()

        self.select_files_btn = QPushButton("Select Files")
        self.select_files_btn.clicked.connect(self.select_files)
        buttons_layout.addWidget(self.select_files_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_files)
        buttons_layout.addWidget(self.clear_btn)

        buttons_layout.addStretch()

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        buttons_layout.addWidget(self.button_box)

        layout.addLayout(buttons_layout)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, default_path: str, filter_: str, target_size: QSize, parent: QWidget | None = None) -> None
```

Create file-selection dialog with optional resize controls.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        default_path: str,
        filter_: str,
        target_size: QSize,
        parent: QWidget | None = None,
        *,
        with_resize_option: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setAcceptDrops(True)
        self.setMinimumSize(target_size)
        self.resize(target_size)

        self.default_path = default_path
        self.filter_ = filter_
        self.selected_files: list[str] = []
        self.with_resize_option = with_resize_option

        self.setup_ui()
```

</details>

### ⚙️ Method `add_files`

```python
def add_files(self, file_paths: list[str]) -> None
```

Add files to selection list (deduplicated).

<details>
<summary>Code:</summary>

```python
def add_files(self, file_paths: list[str]) -> None:
        for file_path in file_paths:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_list.addItem(file_path)
```

</details>

### ⚙️ Method `clear_files`

```python
def clear_files(self) -> None
```

Clear selected files list.

<details>
<summary>Code:</summary>

```python
def clear_files(self) -> None:
        self.selected_files.clear()
        self.files_list.clear()
```

</details>

### ⚙️ Method `get_max_size`

```python
def get_max_size(self) -> str | None
```

Return max size string, or None if resize disabled/empty.

<details>
<summary>Code:</summary>

```python
def get_max_size(self) -> str | None:
        if not self.get_resize_enabled() or not hasattr(self, "max_size_edit"):
            return None
        text = self.max_size_edit.text().strip()
        return text or None
```

</details>

### ⚙️ Method `get_resize_enabled`

```python
def get_resize_enabled(self) -> bool
```

Return True when resize checkbox enabled and checked.

<details>
<summary>Code:</summary>

```python
def get_resize_enabled(self) -> bool:
        if not self.with_resize_option or not hasattr(self, "resize_checkbox"):
            return False
        return self.resize_checkbox.isChecked()
```

</details>

### ⚙️ Method `get_selected_files`

```python
def get_selected_files(self) -> list[str]
```

Return selected file paths.

<details>
<summary>Code:</summary>

```python
def get_selected_files(self) -> list[str]:
        return self.selected_files
```

</details>

### ⚙️ Method `select_files`

```python
def select_files(self) -> None
```

Open native file dialog and add selected files.

<details>
<summary>Code:</summary>

```python
def select_files(self) -> None:
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.default_path, self.filter_)
        if filenames:
            self.add_files(filenames)
```

</details>

### ⚙️ Method `setup_ui`

```python
def setup_ui(self) -> None
```

Build widget layout for drag-drop file selection.

<details>
<summary>Code:</summary>

```python
def setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        title_label = QLabel("Select files for processing")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        self.drop_area = QLabel("Drag files here or click 'Select Files' button")
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background-color: #f9f9f9;
                color: #666;
                font-size: 12px;
            }
            QLabel:hover {
                border-color: #007acc;
                background-color: #f0f8ff;
            }
        """)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setMinimumHeight(150)
        layout.addWidget(self.drop_area)

        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(100)
        layout.addWidget(self.files_list)

        if self.with_resize_option:
            resize_layout = QHBoxLayout()
            self.resize_checkbox = QCheckBox("Resize images (max size, px)")
            self.resize_checkbox.setChecked(False)
            resize_layout.addWidget(self.resize_checkbox)
            self.max_size_edit = QLineEdit()
            self.max_size_edit.setPlaceholderText("1024")
            self.max_size_edit.setText("1024")
            self.max_size_edit.setEnabled(False)

            def toggle_max_size_edit(checked: bool) -> None:  # noqa: FBT001
                self.max_size_edit.setEnabled(checked)

            self.resize_checkbox.toggled.connect(toggle_max_size_edit)
            resize_layout.addWidget(self.max_size_edit)
            resize_layout.addStretch()
            layout.addLayout(resize_layout)

        buttons_layout = QHBoxLayout()

        self.select_files_btn = QPushButton("Select Files")
        self.select_files_btn.clicked.connect(self.select_files)
        buttons_layout.addWidget(self.select_files_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_files)
        buttons_layout.addWidget(self.clear_btn)

        buttons_layout.addStretch()

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        buttons_layout.addWidget(self.button_box)

        layout.addLayout(buttons_layout)
```

</details>

## 🏛️ Class `StandardActionDialog`

```python
class StandardActionDialog(QDialog)
```

QDialog that reapplies target size when shown (Windows may ignore initial `resize()`).

<details>
<summary>Code:</summary>

```python
class StandardActionDialog(QDialog):

    def __init__(self, target_size: QSize, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._target_size = target_size

    def showEvent(self, event: QShowEvent) -> None:  # noqa: D102, N802
        super().showEvent(event)
        self.setMinimumSize(self._target_size)
        self.resize(self._target_size)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, target_size: QSize, parent: QWidget | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, target_size: QSize, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._target_size = target_size
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: D102, N802
        super().showEvent(event)
        self.setMinimumSize(self._target_size)
        self.resize(self._target_size)
```

</details>
