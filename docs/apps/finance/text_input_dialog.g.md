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
  - [⚙️ Method `get_text`](#%EF%B8%8F-method-get_text)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)

</details>

## 🏛️ Class `TextInputDialog`

```python
class TextInputDialog(QDialog)
```

Dialog for entering purchase information as text.

This dialog provides a text area where users can enter purchase information
in a simple text format, which will be parsed according to specific rules.

Attributes:

- `text_edit` (`QPlainTextEdit`): Text area for entering purchase information.
- `accepted_text` (`str | None`): The text that was accepted by the user.

<details>
<summary>Code:</summary>

```python
class TextInputDialog(QDialog):

    text_edit: QPlainTextEdit
    accepted_text: str | None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the text input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.

        """
        super().__init__(parent)
        self.accepted_text: str | None = None
        self._setup_ui()

    def get_text(self) -> str | None:
        """Get the entered text.

        Returns:

        - `str | None`: The entered text, or None if dialog was cancelled.

        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self.text_edit.toPlainText().strip()
        return None

    def _setup_ui(self) -> None:
        """Set up the user interface for the dialog."""
        self.setWindowTitle("Add Purchases as Text")
        self.setMinimumSize(600, 400)
        self.setModal(True)

        # Create main layout
        layout = QVBoxLayout(self)

        # Add description label
        description = QLabel(
            "Enter purchase information in text format. Each line represents one purchase.\n"
            "Format: Name\tCategory\tAmount\n"
            "Format examples:\n"
            "• Sugar-free Cola 'From Store'\tFood\t99 ₽\n"
            "• Milk Cocktail 'Wonder' coconut-cream 2%\tFood\t65 ₽\n"
            "• Olivier salad with chicken 'From Store'\tFood\t285 ₽\n"
            "• Cat litter filler 'Barsik'\tPet Care\t179 ₽\n"
            "• Universal wet wipes\tHousehold Goods\t29 ₽\n\n"
            "Note: Use Tab character to separate columns. Date will be taken from the main form."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Add text edit
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            "Enter your purchases here...\n"
            "Example:\n"
            "Sugar-free Cola 'From Store'\tFood\t99 ₽\n"
            "Milk Cocktail 'Wonder'\tFood\t65 ₽"
        )
        layout.addWidget(self.text_edit)

        # Add buttons
        button_layout = QHBoxLayout()

        # Add spacer to push buttons to the right
        button_layout.addStretch()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # OK button
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

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.accepted_text: str | None = None
        self._setup_ui()
```

</details>

### ⚙️ Method `get_text`

```python
def get_text(self) -> str | None
```

Get the entered text.

Returns:

- `str | None`: The entered text, or None if dialog was cancelled.

<details>
<summary>Code:</summary>

```python
def get_text(self) -> str | None:
        if self.result() == QDialog.DialogCode.Accepted:
            return self.text_edit.toPlainText().strip()
        return None
```

</details>

### ⚙️ Method `_setup_ui`

```python
def _setup_ui(self) -> None
```

Set up the user interface for the dialog.

<details>
<summary>Code:</summary>

```python
def _setup_ui(self) -> None:
        self.setWindowTitle("Add Purchases as Text")
        self.setMinimumSize(600, 400)
        self.setModal(True)

        # Create main layout
        layout = QVBoxLayout(self)

        # Add description label
        description = QLabel(
            "Enter purchase information in text format. Each line represents one purchase.\n"
            "Format: Name\tCategory\tAmount\n"
            "Format examples:\n"
            "• Sugar-free Cola 'From Store'\tFood\t99 ₽\n"
            "• Milk Cocktail 'Wonder' coconut-cream 2%\tFood\t65 ₽\n"
            "• Olivier salad with chicken 'From Store'\tFood\t285 ₽\n"
            "• Cat litter filler 'Barsik'\tPet Care\t179 ₽\n"
            "• Universal wet wipes\tHousehold Goods\t29 ₽\n\n"
            "Note: Use Tab character to separate columns. Date will be taken from the main form."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Add text edit
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            "Enter your purchases here...\n"
            "Example:\n"
            "Sugar-free Cola 'From Store'\tFood\t99 ₽\n"
            "Milk Cocktail 'Wonder'\tFood\t65 ₽"
        )
        layout.addWidget(self.text_edit)

        # Add buttons
        button_layout = QHBoxLayout()

        # Add spacer to push buttons to the right
        button_layout.addStretch()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # OK button
        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)
```

</details>
