---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `account_edit_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AccountEditDialog`](#%EF%B8%8F-class-accounteditdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_result`](#%EF%B8%8F-method-get_result)
  - [⚙️ Method `_on_delete`](#%EF%B8%8F-method-_on_delete)
  - [⚙️ Method `_on_save`](#%EF%B8%8F-method-_on_save)
  - [⚙️ Method `_populate_data`](#%EF%B8%8F-method-_populate_data)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)

</details>

## 🏛️ Class `AccountEditDialog`

```python
class AccountEditDialog(QDialog)
```

Dialog for editing account information.

<details>
<summary>Code:</summary>

```python
class AccountEditDialog(QDialog):

    def __init__(self, parent=None, account_data=None, currencies=None):
        """Initialize the dialog.

        Args:
            parent: Parent widget.
            account_data: Dictionary with account data (id, name, balance, currency_code, is_liquid, is_cash).
            currencies: List of currency codes.

        """
        super().__init__(parent)
        self.account_data = account_data or {}
        self.currencies = currencies or []
        self.result_data = {}

        self.setWindowTitle("Edit Account")
        self.setModal(True)
        self.setFixedSize(400, 300)

        self._setup_ui()
        self._populate_data()

    def get_result(self):
        """Get the dialog result.

        Returns:
            Dictionary with action and data.

        """
        return self.result_data

    def _on_delete(self):
        """Handle delete button click."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete account '{self.account_data.get('name', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.result_data = {"action": "delete", "id": self.account_data.get("id")}
            self.accept()

    def _on_save(self):
        """Handle save button click."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Account name cannot be empty")
            return

        self.result_data = {
            "action": "save",
            "name": name,
            "balance": self.balance_spin.value(),
            "currency_code": self.currency_combo.currentText(),
            "is_liquid": self.is_liquid_check.isChecked(),
            "is_cash": self.is_cash_check.isChecked(),
        }

        self.accept()

    def _populate_data(self):
        """Populate the dialog with account data."""
        if self.account_data:
            self.name_edit.setText(self.account_data.get("name", ""))
            self.balance_spin.setValue(self.account_data.get("balance", 0.0))

            currency_code = self.account_data.get("currency_code", "")
            if currency_code in self.currencies:
                index = self.currencies.index(currency_code)
                self.currency_combo.setCurrentIndex(index)

            self.is_liquid_check.setChecked(self.account_data.get("is_liquid", True))
            self.is_cash_check.setChecked(self.account_data.get("is_cash", False))

            # Set focus to balance field and select all text
            self.balance_spin.setFocus()
            self.balance_spin.selectAll()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()

        # Account name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Balance
        balance_layout = QHBoxLayout()
        balance_layout.addWidget(QLabel("Balance:"))
        self.balance_spin = QDoubleSpinBox()
        self.balance_spin.setRange(-999999999.99, 999999999.99)
        self.balance_spin.setDecimals(2)
        balance_layout.addWidget(self.balance_spin)
        layout.addLayout(balance_layout)

        # Currency
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel("Currency:"))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(self.currencies)
        currency_layout.addWidget(self.currency_combo)
        layout.addLayout(currency_layout)

        # Checkboxes
        self.is_liquid_check = QCheckBox("Liquid")
        self.is_liquid_check.setChecked(True)
        layout.addWidget(self.is_liquid_check)

        self.is_cash_check = QCheckBox("Cash")
        layout.addWidget(self.is_cash_check)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._on_delete)
        self.delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        button_layout.addWidget(self.delete_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent = None, account_data = None, currencies = None)
```

Initialize the dialog.

Args:
parent: Parent widget.
account_data: Dictionary with account data (id, name, balance, currency_code, is_liquid, is_cash).
currencies: List of currency codes.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent=None, account_data=None, currencies=None):
        super().__init__(parent)
        self.account_data = account_data or {}
        self.currencies = currencies or []
        self.result_data = {}

        self.setWindowTitle("Edit Account")
        self.setModal(True)
        self.setFixedSize(400, 300)

        self._setup_ui()
        self._populate_data()
```

</details>

### ⚙️ Method `get_result`

```python
def get_result(self)
```

Get the dialog result.

Returns:
Dictionary with action and data.

<details>
<summary>Code:</summary>

```python
def get_result(self):
        return self.result_data
```

</details>

### ⚙️ Method `_on_delete`

```python
def _on_delete(self)
```

Handle delete button click.

<details>
<summary>Code:</summary>

```python
def _on_delete(self):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete account '{self.account_data.get('name', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.result_data = {"action": "delete", "id": self.account_data.get("id")}
            self.accept()
```

</details>

### ⚙️ Method `_on_save`

```python
def _on_save(self)
```

Handle save button click.

<details>
<summary>Code:</summary>

```python
def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Account name cannot be empty")
            return

        self.result_data = {
            "action": "save",
            "name": name,
            "balance": self.balance_spin.value(),
            "currency_code": self.currency_combo.currentText(),
            "is_liquid": self.is_liquid_check.isChecked(),
            "is_cash": self.is_cash_check.isChecked(),
        }

        self.accept()
```

</details>

### ⚙️ Method `_populate_data`

```python
def _populate_data(self)
```

Populate the dialog with account data.

<details>
<summary>Code:</summary>

```python
def _populate_data(self):
        if self.account_data:
            self.name_edit.setText(self.account_data.get("name", ""))
            self.balance_spin.setValue(self.account_data.get("balance", 0.0))

            currency_code = self.account_data.get("currency_code", "")
            if currency_code in self.currencies:
                index = self.currencies.index(currency_code)
                self.currency_combo.setCurrentIndex(index)

            self.is_liquid_check.setChecked(self.account_data.get("is_liquid", True))
            self.is_cash_check.setChecked(self.account_data.get("is_cash", False))

            # Set focus to balance field and select all text
            self.balance_spin.setFocus()
            self.balance_spin.selectAll()
```

</details>

### ⚙️ Method `_setup_ui`

```python
def _setup_ui(self)
```

Setup the user interface.

<details>
<summary>Code:</summary>

```python
def _setup_ui(self):
        layout = QVBoxLayout()

        # Account name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Balance
        balance_layout = QHBoxLayout()
        balance_layout.addWidget(QLabel("Balance:"))
        self.balance_spin = QDoubleSpinBox()
        self.balance_spin.setRange(-999999999.99, 999999999.99)
        self.balance_spin.setDecimals(2)
        balance_layout.addWidget(self.balance_spin)
        layout.addLayout(balance_layout)

        # Currency
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel("Currency:"))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(self.currencies)
        currency_layout.addWidget(self.currency_combo)
        layout.addLayout(currency_layout)

        # Checkboxes
        self.is_liquid_check = QCheckBox("Liquid")
        self.is_liquid_check.setChecked(True)
        layout.addWidget(self.is_liquid_check)

        self.is_cash_check = QCheckBox("Cash")
        layout.addWidget(self.is_cash_check)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._on_delete)
        self.delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        button_layout.addWidget(self.delete_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
```

</details>
