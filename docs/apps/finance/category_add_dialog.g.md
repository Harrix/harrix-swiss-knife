---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_add_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CategoryAddDialog`](#️-class-categoryadddialog)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `get_result`](#️-method-get_result)

</details>

## 🏛️ Class `CategoryAddDialog`

```python
class CategoryAddDialog(QDialog)
```

Modal dialog to enter category name and type (expense or income).

<details>
<summary>Code:</summary>

```python
class CategoryAddDialog(QDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the add-category dialog."""
        super().__init__(parent)
        self._result: tuple[str, int] | None = None

        self.setWindowTitle("Add Category")
        self.setModal(True)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)

        form_group = QGroupBox("Category", self)
        form_layout = QVBoxLayout(form_group)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:", form_group))
        self._name_edit = QLineEdit(form_group)
        self._name_edit.setPlaceholderText("Category name")
        name_row.addWidget(self._name_edit, 1)
        form_layout.addLayout(name_row)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:", form_group))
        self._type_combo = QComboBox(form_group)
        self._type_combo.addItems(["Expense", "Income"])
        type_row.addWidget(self._type_combo, 1)
        form_layout.addLayout(type_row)

        layout.addWidget(form_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._name_edit.setFocus()

    def get_result(self) -> tuple[str, int] | None:
        """Return `(name, category_type)` when accepted, else `None`."""
        return self._result

    def _on_accept(self) -> None:
        name = self._name_edit.text().strip()
        if not name:
            message_box.warning(self, "Validation Error", "Enter category name")
            return
        self._result = (name, self._type_combo.currentIndex())
        self.accept()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the add-category dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._result: tuple[str, int] | None = None

        self.setWindowTitle("Add Category")
        self.setModal(True)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)

        form_group = QGroupBox("Category", self)
        form_layout = QVBoxLayout(form_group)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:", form_group))
        self._name_edit = QLineEdit(form_group)
        self._name_edit.setPlaceholderText("Category name")
        name_row.addWidget(self._name_edit, 1)
        form_layout.addLayout(name_row)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:", form_group))
        self._type_combo = QComboBox(form_group)
        self._type_combo.addItems(["Expense", "Income"])
        type_row.addWidget(self._type_combo, 1)
        form_layout.addLayout(type_row)

        layout.addWidget(form_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._name_edit.setFocus()
```

</details>

### ⚙️ Method `get_result`

```python
def get_result(self) -> tuple[str, int] | None
```

Return `(name, category_type)` when accepted, else `None`.

<details>
<summary>Code:</summary>

```python
def get_result(self) -> tuple[str, int] | None:
        return self._result
```

</details>
