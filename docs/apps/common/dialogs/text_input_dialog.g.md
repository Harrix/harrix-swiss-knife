---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_input_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TextInputDialog`](#%EF%B8%8F-class-textinputdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_date`](#%EF%B8%8F-method-get_date)
  - [⚙️ Method `get_text`](#%EF%B8%8F-method-get_text)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)

</details>

## 🏛️ Class `TextInputDialog`

```python
class TextInputDialog(QDialog)
```

Configurable multiline text input dialog.

Attributes:

- `text_edit` (`QPlainTextEdit`): Text area for user input.
- `date_edit` (`QDateEdit | None`): Optional date picker when `show_date` is True.
- `accepted_text` (`str | None`): The text that was accepted by the user.

<details>
<summary>Code:</summary>

```python
class TextInputDialog(QDialog):

    text_edit: QPlainTextEdit
    date_edit: QDateEdit | None
    accepted_text: str | None

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Add Text",
        description: str | None = None,
        placeholder: str | None = None,
        show_date: bool = False,
        default_date: QDate | None = None,
        focus_text_on_show: bool = False,
        min_width: int = 600,
        min_height: int = 400,
    ) -> None:
        """Initialize the text input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `title` (`str`): Window title. Defaults to `"Add Text"`.
        - `description` (`str | None`): Optional description label shown above the text area.
        - `placeholder` (`str | None`): Optional placeholder text for the text area.
        - `show_date` (`bool`): Whether to show a `QDateEdit`. Defaults to `False`.
        - `default_date` (`QDate | None`): Default value for the date picker.
          Defaults to today when `show_date` is `True`.
        - `focus_text_on_show` (`bool`): Focus the text edit on `showEvent`. Defaults to `False`.
        - `min_width` (`int`): Minimum dialog width. Defaults to `600`.
        - `min_height` (`int`): Minimum dialog height. Defaults to `400`.

        """
        super().__init__(parent)
        self.accepted_text = None
        self.date_edit = None
        self._title = title
        self._description = description
        self._placeholder = placeholder
        self._show_date = show_date
        self._default_date = default_date
        self._focus_text_on_show = focus_text_on_show
        self._min_width = min_width
        self._min_height = min_height
        self._setup_ui()

    def get_date(self) -> str | None:
        """Get the selected date.

        Returns:

        - `str | None`: The selected date in `yyyy-MM-dd` format, or `None` if
          the dialog was cancelled or has no date picker.

        """
        if self.date_edit is None:
            return None
        if self.result() == QDialog.DialogCode.Accepted:
            return self.date_edit.date().toString("yyyy-MM-dd")
        return None

    def get_text(self) -> str | None:
        """Get the entered text.

        Returns:

        - `str | None`: The entered text, or `None` if dialog was cancelled.

        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self.text_edit.toPlainText().strip()
        return None

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Override `showEvent` to optionally focus the text edit."""
        super().showEvent(event)
        if self._focus_text_on_show:
            self.text_edit.setFocus()

    def _setup_ui(self) -> None:
        self.setWindowTitle(self._title)
        self.setMinimumSize(self._min_width, self._min_height)
        self.setModal(True)

        layout = QVBoxLayout(self)

        if self._description is not None:
            description_label = QLabel(self._description)
            description_label.setWordWrap(True)
            layout.addWidget(description_label)

        if self._show_date:
            date_layout = QHBoxLayout()
            date_label = QLabel("Date:")
            date_layout.addWidget(date_label)
            self.date_edit = QDateEdit()
            self.date_edit.setCalendarPopup(True)
            self.date_edit.setDisplayFormat("yyyy-MM-dd")
            self.date_edit.setDate(self._default_date or QDate.currentDate())
            date_layout.addWidget(self.date_edit)
            date_layout.addStretch()
            layout.addLayout(date_layout)

        self.text_edit = QPlainTextEdit()
        if self._placeholder is not None:
            self.text_edit.setPlaceholderText(self._placeholder)
        layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the text input dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `title` (`str`): Window title. Defaults to `"Add Text"`.
- `description` (`str | None`): Optional description label shown above the text area.
- `placeholder` (`str | None`): Optional placeholder text for the text area.
- `show_date` (`bool`): Whether to show a `QDateEdit`. Defaults to `False`.
- `default_date` (`QDate | None`): Default value for the date picker.
  Defaults to today when `show_date` is `True`.
- `focus_text_on_show` (`bool`): Focus the text edit on `showEvent`. Defaults to `False`.
- `min_width` (`int`): Minimum dialog width. Defaults to `600`.
- `min_height` (`int`): Minimum dialog height. Defaults to `400`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Add Text",
        description: str | None = None,
        placeholder: str | None = None,
        show_date: bool = False,
        default_date: QDate | None = None,
        focus_text_on_show: bool = False,
        min_width: int = 600,
        min_height: int = 400,
    ) -> None:
        super().__init__(parent)
        self.accepted_text = None
        self.date_edit = None
        self._title = title
        self._description = description
        self._placeholder = placeholder
        self._show_date = show_date
        self._default_date = default_date
        self._focus_text_on_show = focus_text_on_show
        self._min_width = min_width
        self._min_height = min_height
        self._setup_ui()
```

</details>

### ⚙️ Method `get_date`

```python
def get_date(self) -> str | None
```

Get the selected date.

Returns:

- `str | None`: The selected date in `yyyy-MM-dd` format, or `None` if
  the dialog was cancelled or has no date picker.

<details>
<summary>Code:</summary>

```python
def get_date(self) -> str | None:
        if self.date_edit is None:
            return None
        if self.result() == QDialog.DialogCode.Accepted:
            return self.date_edit.date().toString("yyyy-MM-dd")
        return None
```

</details>

### ⚙️ Method `get_text`

```python
def get_text(self) -> str | None
```

Get the entered text.

Returns:

- `str | None`: The entered text, or `None` if dialog was cancelled.

<details>
<summary>Code:</summary>

```python
def get_text(self) -> str | None:
        if self.result() == QDialog.DialogCode.Accepted:
            return self.text_edit.toPlainText().strip()
        return None
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Override `showEvent` to optionally focus the text edit.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        if self._focus_text_on_show:
            self.text_edit.setFocus()
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
        self.setWindowTitle(self._title)
        self.setMinimumSize(self._min_width, self._min_height)
        self.setModal(True)

        layout = QVBoxLayout(self)

        if self._description is not None:
            description_label = QLabel(self._description)
            description_label.setWordWrap(True)
            layout.addWidget(description_label)

        if self._show_date:
            date_layout = QHBoxLayout()
            date_label = QLabel("Date:")
            date_layout.addWidget(date_label)
            self.date_edit = QDateEdit()
            self.date_edit.setCalendarPopup(True)
            self.date_edit.setDisplayFormat("yyyy-MM-dd")
            self.date_edit.setDate(self._default_date or QDate.currentDate())
            date_layout.addWidget(self.date_edit)
            date_layout.addStretch()
            layout.addLayout(date_layout)

        self.text_edit = QPlainTextEdit()
        if self._placeholder is not None:
            self.text_edit.setPlaceholderText(self._placeholder)
        layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)
```

</details>
