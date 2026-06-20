---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ai_source_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AiSourceDialog`](#%EF%B8%8F-class-aisourcedialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_image_bytes_and_mime`](#%EF%B8%8F-method-get_image_bytes_and_mime)
  - [⚙️ Method `get_raw_text`](#%EF%B8%8F-method-get_raw_text)
  - [⚙️ Method `_on_accept`](#%EF%B8%8F-method-_on_accept)
  - [⚙️ Method `_on_skip_to_manual`](#%EF%B8%8F-method-_on_skip_to_manual)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)
  - [⚙️ Method `_update_ok_enabled`](#%EF%B8%8F-method-_update_ok_enabled)

</details>

## 🏛️ Class `AiSourceDialog`

```python
class AiSourceDialog(QDialog)
```

Modal dialog to collect source text and/or an image for BotHub.

<details>
<summary>Code:</summary>

```python
class AiSourceDialog(QDialog):

    SKIP_MANUAL: int = 2

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Add with AI",
        description: str = "",
        placeholder: str = "",
        send_button_text: str = "Send to AI",
        max_image_side: int | None = None,
    ) -> None:
        """Initialize the AI source dialog."""
        super().__init__(parent)
        self._title = title
        self._description = description
        self._placeholder = placeholder
        self._send_button_text = send_button_text
        self._max_image_side = max_image_side
        self._raw_text: str = ""
        self._image_data: tuple[bytes, str] | None = None
        self._setup_ui()

    def get_image_bytes_and_mime(self) -> tuple[bytes, str] | None:
        """Return image bytes and MIME type if an image was provided."""
        return self._image_data

    def get_raw_text(self) -> str:
        """Return raw text entered by the user."""
        return self._raw_text

    def _on_accept(self) -> None:
        self._raw_text = self.text_edit.toPlainText().strip()
        self._image_data = self.image_widget.get_image_bytes_and_mime()
        if not self._raw_text and not self._image_data:
            return
        self.accept()

    def _on_skip_to_manual(self) -> None:
        self.done(self.SKIP_MANUAL)

    def _setup_ui(self) -> None:
        self.setWindowTitle(self._title)
        self.setMinimumSize(640, 520)
        self.setModal(True)

        layout = QVBoxLayout(self)

        if self._description:
            text_label = QLabel(self._description)
            text_label.setWordWrap(True)
            layout.addWidget(text_label)

        self.text_edit = QPlainTextEdit()
        if self._placeholder:
            self.text_edit.setPlaceholderText(self._placeholder)
        self.text_edit.setMinimumHeight(120)
        self.text_edit.textChanged.connect(self._update_ok_enabled)
        layout.addWidget(self.text_edit)

        image_label = QLabel("Image (drag, paste Ctrl+V, or select file):")
        layout.addWidget(image_label)

        self.image_widget = ImageDropWidget(max_image_side=self._max_image_side)
        self.image_widget.image_changed.connect(self._update_ok_enabled)
        layout.addWidget(self.image_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        skip_button = QPushButton("Enter Text Manually")
        skip_button.clicked.connect(self._on_skip_to_manual)
        button_layout.addWidget(skip_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self._ok_button = QPushButton(self._send_button_text)
        send_to_ai_font = QFont()
        send_to_ai_font.setBold(True)
        self._ok_button.setFont(send_to_ai_font)
        self._ok_button.setStyleSheet(SEND_TO_AI_BUTTON_STYLE)
        self._ok_button.setEnabled(False)
        self._ok_button.setDefault(True)
        self._ok_button.clicked.connect(self._on_accept)
        button_layout.addWidget(self._ok_button)

        layout.addLayout(button_layout)

    def _update_ok_enabled(self) -> None:
        has_text = bool(self.text_edit.toPlainText().strip())
        has_image = self.image_widget.has_image()
        self._ok_button.setEnabled(has_text or has_image)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the AI source dialog.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Add with AI",
        description: str = "",
        placeholder: str = "",
        send_button_text: str = "Send to AI",
        max_image_side: int | None = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._description = description
        self._placeholder = placeholder
        self._send_button_text = send_button_text
        self._max_image_side = max_image_side
        self._raw_text: str = ""
        self._image_data: tuple[bytes, str] | None = None
        self._setup_ui()
```

</details>

### ⚙️ Method `get_image_bytes_and_mime`

```python
def get_image_bytes_and_mime(self) -> tuple[bytes, str] | None
```

Return image bytes and MIME type if an image was provided.

<details>
<summary>Code:</summary>

```python
def get_image_bytes_and_mime(self) -> tuple[bytes, str] | None:
        return self._image_data
```

</details>

### ⚙️ Method `get_raw_text`

```python
def get_raw_text(self) -> str
```

Return raw text entered by the user.

<details>
<summary>Code:</summary>

```python
def get_raw_text(self) -> str:
        return self._raw_text
```

</details>

### ⚙️ Method `_on_accept`

```python
def _on_accept(self) -> None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _on_accept(self) -> None:
        self._raw_text = self.text_edit.toPlainText().strip()
        self._image_data = self.image_widget.get_image_bytes_and_mime()
        if not self._raw_text and not self._image_data:
            return
        self.accept()
```

</details>

### ⚙️ Method `_on_skip_to_manual`

```python
def _on_skip_to_manual(self) -> None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _on_skip_to_manual(self) -> None:
        self.done(self.SKIP_MANUAL)
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
        self.setWindowTitle(self._title)
        self.setMinimumSize(640, 520)
        self.setModal(True)

        layout = QVBoxLayout(self)

        if self._description:
            text_label = QLabel(self._description)
            text_label.setWordWrap(True)
            layout.addWidget(text_label)

        self.text_edit = QPlainTextEdit()
        if self._placeholder:
            self.text_edit.setPlaceholderText(self._placeholder)
        self.text_edit.setMinimumHeight(120)
        self.text_edit.textChanged.connect(self._update_ok_enabled)
        layout.addWidget(self.text_edit)

        image_label = QLabel("Image (drag, paste Ctrl+V, or select file):")
        layout.addWidget(image_label)

        self.image_widget = ImageDropWidget(max_image_side=self._max_image_side)
        self.image_widget.image_changed.connect(self._update_ok_enabled)
        layout.addWidget(self.image_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        skip_button = QPushButton("Enter Text Manually")
        skip_button.clicked.connect(self._on_skip_to_manual)
        button_layout.addWidget(skip_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self._ok_button = QPushButton(self._send_button_text)
        send_to_ai_font = QFont()
        send_to_ai_font.setBold(True)
        self._ok_button.setFont(send_to_ai_font)
        self._ok_button.setStyleSheet(SEND_TO_AI_BUTTON_STYLE)
        self._ok_button.setEnabled(False)
        self._ok_button.setDefault(True)
        self._ok_button.clicked.connect(self._on_accept)
        button_layout.addWidget(self._ok_button)

        layout.addLayout(button_layout)
```

</details>

### ⚙️ Method `_update_ok_enabled`

```python
def _update_ok_enabled(self) -> None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _update_ok_enabled(self) -> None:
        has_text = bool(self.text_edit.toPlainText().strip())
        has_image = self.image_widget.has_image()
        self._ok_button.setEnabled(has_text or has_image)
```

</details>
