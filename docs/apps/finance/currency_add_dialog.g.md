---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `currency_add_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CurrencyAddDialog`](#%EF%B8%8F-class-currencyadddialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_result`](#%EF%B8%8F-method-get_result)

</details>

## 🏛️ Class `CurrencyAddDialog`

```python
class CurrencyAddDialog(QDialog)
```

Modal dialog to enter currency code, name, symbol, and subdivision.

<details>
<summary>Code:</summary>

```python
class CurrencyAddDialog(QDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the add-currency dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.

        """
        super().__init__(parent)
        self._result: dict[str, str | int] | None = None

        self.setWindowTitle("Add Currency")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)

        code_row = QHBoxLayout()
        code_row.addWidget(QLabel("Code:"))
        self._code_edit = QLineEdit()
        self._code_edit.setPlaceholderText("USD, EUR, RUB")
        code_row.addWidget(self._code_edit, 1)
        layout.addLayout(code_row)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:"))
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("US Dollar")
        name_row.addWidget(self._name_edit, 1)
        layout.addLayout(name_row)

        symbol_row = QHBoxLayout()
        symbol_row.addWidget(QLabel("Symbol:"))
        self._symbol_edit = QLineEdit()
        self._symbol_edit.setPlaceholderText("$, €, ₽")
        symbol_row.addWidget(self._symbol_edit, 1)
        layout.addLayout(symbol_row)

        subdivision_row = QHBoxLayout()
        subdivision_row.addWidget(QLabel("Subdivision:"))
        self._subdivision_spin = QSpinBox()
        self._subdivision_spin.setMaximum(1_000_000_000)
        self._subdivision_spin.setValue(100)
        subdivision_row.addWidget(self._subdivision_spin, 1)
        layout.addLayout(subdivision_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._code_edit.setFocus()

    def get_result(self) -> dict[str, str | int] | None:
        """Return currency fields when accepted, else `None`."""
        return self._result

    def _on_accept(self) -> None:
        """Validate fields and accept the dialog."""
        code = self._code_edit.text().strip().upper()
        name = self._name_edit.text().strip()
        symbol = self._symbol_edit.text().strip()
        subdivision = self._subdivision_spin.value()
        if not code:
            message_box.warning(self, "Validation Error", "Enter currency code")
            return
        if not name:
            message_box.warning(self, "Validation Error", "Enter currency name")
            return
        if not symbol:
            message_box.warning(self, "Validation Error", "Enter currency symbol")
            return
        if subdivision <= 0:
            message_box.warning(self, "Validation Error", "Subdivision must be a positive number")
            return
        self._result = {"code": code, "name": name, "symbol": symbol, "subdivision": subdivision}
        self.accept()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the add-currency dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._result: dict[str, str | int] | None = None

        self.setWindowTitle("Add Currency")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)

        code_row = QHBoxLayout()
        code_row.addWidget(QLabel("Code:"))
        self._code_edit = QLineEdit()
        self._code_edit.setPlaceholderText("USD, EUR, RUB")
        code_row.addWidget(self._code_edit, 1)
        layout.addLayout(code_row)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:"))
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("US Dollar")
        name_row.addWidget(self._name_edit, 1)
        layout.addLayout(name_row)

        symbol_row = QHBoxLayout()
        symbol_row.addWidget(QLabel("Symbol:"))
        self._symbol_edit = QLineEdit()
        self._symbol_edit.setPlaceholderText("$, €, ₽")
        symbol_row.addWidget(self._symbol_edit, 1)
        layout.addLayout(symbol_row)

        subdivision_row = QHBoxLayout()
        subdivision_row.addWidget(QLabel("Subdivision:"))
        self._subdivision_spin = QSpinBox()
        self._subdivision_spin.setMaximum(1_000_000_000)
        self._subdivision_spin.setValue(100)
        subdivision_row.addWidget(self._subdivision_spin, 1)
        layout.addLayout(subdivision_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._code_edit.setFocus()
```

</details>

### ⚙️ Method `get_result`

```python
def get_result(self) -> dict[str, str | int] | None
```

Return currency fields when accepted, else `None`.

<details>
<summary>Code:</summary>

```python
def get_result(self) -> dict[str, str | int] | None:
        return self._result
```

</details>
