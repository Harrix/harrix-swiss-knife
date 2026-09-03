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

</details>

## 🏛️ Class `AccountEditDialog`

```python
class AccountEditDialog(QDialog)
```

Dialog for editing account information.

This dialog allows users to create, edit, or delete account information
including name, balance, currency, and account type settings.

<details>
<summary>Code:</summary>

```python
class AccountEditDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        account_data: dict | None = None,
        currencies: list | None = None,
        default_currency_code: str | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `account_data` (`dict | None`): Dictionary with account data (ID, name, balance, currency_code, is_liquid,
          is_cash). Defaults to `None`.
        - `currencies` (`list | None`): List of currency codes. Defaults to `None`.
        - `default_currency_code` (`str | None`): Currency selected for a new account.
          Defaults to `None`.

        """
        super().__init__(parent)
        self.account_data = account_data or {}
        self.currencies = currencies or []
        self._default_currency_code = default_currency_code
        self.result_data = {}
        self._initial_balance: float = 0.0

        self.setWindowTitle("Add Account" if not self.account_data else "Edit Account")
        qt_modality.set_owner_window_modal(self)
        self.setFixedSize(400, 350)

        self._setup_ui()
        self._populate_data()
        if not self.account_data:
            self.delete_button.hide()
            self.name_edit.setFocus()

        self.balance_spin.valueChanged.connect(self._update_balance_delta_label)
        self._update_balance_delta_label()

    def get_result(self) -> dict:
        """Get the dialog result.

        Returns:

        - `dict`: Dictionary with action and data.

        """
        return self.result_data

    def _on_delete(self) -> None:
        """Handle delete button click."""
        reply = message_box.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete account '{self.account_data.get('name', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.result_data = {"action": "delete", "id": self.account_data.get("id")}
            self.accept()

    def _on_equals_clicked(self) -> None:
        """Handle equals button click — evaluate expression and set balance."""
        expression = self.expression_edit.text().strip()
        if not expression:
            message_box.warning(self, "Error", "Expression is empty")
            return

        try:
            result = evaluate_arithmetic_expression(expression)
            self.balance_spin.setValue(result)
        except ValueError as e:
            message_box.warning(self, "Error", f"Invalid expression: {e}")

    def _on_expression_changed(self) -> None:
        """Handle expression field changes and update balance."""
        # This method is called on every text change, but we don't auto-update
        # to avoid errors while typing. Use the equals button to calculate.

    def _on_save(self) -> None:
        """Handle save button click."""
        name = capitalize_first_letter(self.name_edit.text())
        if not name:
            message_box.warning(self, "Error", "Account name cannot be empty")
            return

        # Get balance value directly from balance_spin field
        self.result_data = {
            "action": "save",
            "name": name,
            "balance": self.balance_spin.value(),
            "currency_code": self.currency_combo.currentText(),
            "is_liquid": self.is_liquid_check.isChecked(),
            "is_cash": self.is_cash_check.isChecked(),
        }

        self.accept()

    def _populate_data(self) -> None:
        """Populate the dialog with account data."""
        if self.account_data:
            self.name_edit.setText(self.account_data.get("name", ""))
            balance = self.account_data.get("balance", 0.0)
            self._initial_balance = float(balance)
            self.balance_spin.setValue(balance)

            # Set balance value in Expression field
            self.expression_edit.setText(str(balance))

            currency_code = self.account_data.get("currency_code", "")
            if currency_code in self.currencies:
                index = self.currencies.index(currency_code)
                self.currency_combo.setCurrentIndex(index)

            self.is_liquid_check.setChecked(self.account_data.get("is_liquid", True))
            self.is_cash_check.setChecked(self.account_data.get("is_cash", False))

            # Set focus to balance field and select all text
            self.balance_spin.setFocus()
            self.balance_spin.selectAll()
        else:
            # For new account, set default balance in Expression field
            self._initial_balance = 0.0
            self.expression_edit.setText("0.0")
            if self._default_currency_code in self.currencies:
                self.currency_combo.setCurrentIndex(self.currencies.index(self._default_currency_code))

    def _setup_ui(self) -> None:
        """Set up the user interface."""
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

        self.balance_delta_label = QLabel("")
        self.balance_delta_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.balance_delta_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.balance_delta_label.setWordWrap(False)
        self.balance_delta_label.setStyleSheet("color: #000;")
        layout.addWidget(self.balance_delta_label)

        # Expression field for calculating balance
        expression_layout = QHBoxLayout()
        expression_layout.addWidget(QLabel("Expression:"))
        self.expression_edit = QLineEdit()
        self.expression_edit.setPlaceholderText("e.g., 3*200+100*3")
        self.expression_edit.textChanged.connect(self._on_expression_changed)
        expression_layout.addWidget(self.expression_edit)

        # Add equals button to evaluate expression
        self.equals_button = QPushButton("=")
        self.equals_button.setFixedWidth(40)
        self.equals_button.clicked.connect(self._on_equals_clicked)
        self.equals_button.setToolTip("Calculate expression and set balance")
        expression_layout.addWidget(self.equals_button)

        layout.addLayout(expression_layout)

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

        self.delete_button = make_emoji_push_button("Delete", DELETE_BUTTON_EMOJI)
        self.delete_button.clicked.connect(self._on_delete)
        self.delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        button_layout.addWidget(self.delete_button)

        self.cancel_button = make_emoji_push_button("Cancel", CANCEL_BUTTON_EMOJI)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = make_emoji_push_button("Save", SAVE_BUTTON_EMOJI)
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        self.save_button.setDefault(True)  # Make Save button the default button
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _update_balance_delta_label(self) -> None:
        """Update label showing balance delta relative to initial value."""
        current = float(self.balance_spin.value())
        delta = current - self._initial_balance

        if abs(delta) < _BALANCE_DELTA_EPSILON:
            self.balance_delta_label.setStyleSheet("color: #000;")
            self.balance_delta_label.setText("0.00")
            return

        if delta > 0:
            self.balance_delta_label.setStyleSheet("color: #2e7d32;")  # green
            self.balance_delta_label.setText(f"+{delta:.2f}")
        else:
            self.balance_delta_label.setStyleSheet("color: #c62828;")  # red
            self.balance_delta_label.setText(f"{delta:.2f}")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, account_data: dict | None = None, currencies: list | None = None, default_currency_code: str | None = None) -> None
```

Initialize the dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `account_data` (`dict | None`): Dictionary with account data (ID, name, balance, currency_code, is_liquid,
  is_cash). Defaults to `None`.
- `currencies` (`list | None`): List of currency codes. Defaults to `None`.
- `default_currency_code` (`str | None`): Currency selected for a new account.
  Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        account_data: dict | None = None,
        currencies: list | None = None,
        default_currency_code: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.account_data = account_data or {}
        self.currencies = currencies or []
        self._default_currency_code = default_currency_code
        self.result_data = {}
        self._initial_balance: float = 0.0

        self.setWindowTitle("Add Account" if not self.account_data else "Edit Account")
        qt_modality.set_owner_window_modal(self)
        self.setFixedSize(400, 350)

        self._setup_ui()
        self._populate_data()
        if not self.account_data:
            self.delete_button.hide()
            self.name_edit.setFocus()

        self.balance_spin.valueChanged.connect(self._update_balance_delta_label)
        self._update_balance_delta_label()
```

</details>

### ⚙️ Method `get_result`

```python
def get_result(self) -> dict
```

Get the dialog result.

Returns:

- `dict`: Dictionary with action and data.

<details>
<summary>Code:</summary>

```python
def get_result(self) -> dict:
        return self.result_data
```

</details>
