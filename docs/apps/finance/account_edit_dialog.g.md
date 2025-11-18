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
  - [⚙️ Method `_evaluate_expression`](#%EF%B8%8F-method-_evaluate_expression)
  - [⚙️ Method `_is_safe_node`](#%EF%B8%8F-method-_is_safe_node)
  - [⚙️ Method `_on_delete`](#%EF%B8%8F-method-_on_delete)
  - [⚙️ Method `_on_expression_changed`](#%EF%B8%8F-method-_on_expression_changed)
  - [⚙️ Method `_on_save`](#%EF%B8%8F-method-_on_save)
  - [⚙️ Method `_populate_data`](#%EF%B8%8F-method-_populate_data)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)

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
    ) -> None:
        """Initialize the dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `account_data` (`dict | None`): Dictionary with account data (id, name, balance, currency_code, is_liquid,
          is_cash). Defaults to `None`.
        - `currencies` (`list | None`): List of currency codes. Defaults to `None`.

        """
        super().__init__(parent)
        self.account_data = account_data or {}
        self.currencies = currencies or []
        self.result_data = {}

        self.setWindowTitle("Edit Account")
        self.setModal(True)
        self.setFixedSize(400, 350)

        self._setup_ui()
        self._populate_data()

    def get_result(self) -> dict:
        """Get the dialog result.

        Returns:

        - `dict`: Dictionary with action and data.

        """
        return self.result_data

    def _evaluate_expression(self, expression: str) -> float:
        """Safely evaluate a mathematical expression.

        Args:

        - `expression` (`str`): String containing mathematical expression.

        Returns:

        - `float`: Calculated result as float.

        Raises:

        - `ValueError`: If expression is invalid or contains unsafe operations.

        """
        # Remove all whitespace
        expression = expression.replace(" ", "")

        # Only allow safe characters: numbers, operators, parentheses, decimal points
        if not re.match(r"^[0-9+\-*/().]+$", expression):
            msg = "Expression contains invalid characters"
            raise ValueError(msg)

        # Check for balanced parentheses
        if expression.count("(") != expression.count(")"):
            msg = "Unbalanced parentheses"
            raise ValueError(msg)

        # Check for division by zero
        if "/0" in expression or "/0." in expression:
            msg = "Division by zero"
            raise ValueError(msg)

        def _raise_value_error(msg: str) -> None:
            raise ValueError(msg)

        try:
            # Parse expression into AST
            tree = ast.parse(expression, mode="eval")

            # Check if AST is safe
            if not self._is_safe_node(tree):
                _raise_value_error("Expression contains unsafe operations")

            # Compile and evaluate safely
            code = compile(tree, "<string>", "eval")
            result = eval(code, {"__builtins__": {}}, {})

            if not isinstance(result, (int, float)):
                _raise_value_error("Expression does not evaluate to a number")
            return float(result)
        except SyntaxError as e:
            _raise_value_error(f"Invalid expression syntax: {e!s}")
        except Exception as e:
            _raise_value_error(f"Invalid expression: {e!s}")

    def _is_safe_node(self, node: ast.AST) -> bool:
        """Check if AST node is safe for evaluation.

        Args:

        - `node` (`ast.AST`): AST node to check.

        Returns:

        - `bool`: True if node is safe, False otherwise.

        """
        # Allow numbers (int, float)
        if isinstance(node, (ast.Constant, ast.Num)):
            return True

        # Allow binary operations (+, -, *, /)
        if isinstance(node, ast.BinOp):
            return (
                isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div))
                and self._is_safe_node(node.left)
                and self._is_safe_node(node.right)
            )

        # Allow unary operations (+, -)
        if isinstance(node, ast.UnaryOp):
            return isinstance(node.op, (ast.UAdd, ast.USub)) and self._is_safe_node(node.operand)

        # Allow parentheses (expression)
        if isinstance(node, ast.Expression):
            return self._is_safe_node(node.body)

        return False

    def _on_delete(self) -> None:
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

    def _on_expression_changed(self) -> None:
        """Handle expression field changes and update balance."""
        expression = self.expression_edit.text().strip()
        if not expression:
            return

        try:
            result = self._evaluate_expression(expression)
            self.balance_spin.setValue(result)
        except ValueError:
            # Don't show error for partial expressions, only for invalid ones
            pass

    def _on_save(self) -> None:
        """Handle save button click."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Account name cannot be empty")
            return

        # Check if expression field has content and try to evaluate it
        expression = self.expression_edit.text().strip()
        if expression:
            try:
                calculated_balance = self._evaluate_expression(expression)
                self.balance_spin.setValue(calculated_balance)
            except ValueError as e:
                QMessageBox.warning(self, "Error", f"Invalid expression: {e!s}")
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

    def _populate_data(self) -> None:
        """Populate the dialog with account data."""
        if self.account_data:
            self.name_edit.setText(self.account_data.get("name", ""))
            balance = self.account_data.get("balance", 0.0)
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
            self.expression_edit.setText("0.0")

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

        # Expression field for calculating balance
        expression_layout = QHBoxLayout()
        expression_layout.addWidget(QLabel("Expression:"))
        self.expression_edit = QLineEdit()
        self.expression_edit.setPlaceholderText("e.g., 3*200+100*3")
        self.expression_edit.textChanged.connect(self._on_expression_changed)
        expression_layout.addWidget(self.expression_edit)
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

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._on_delete)
        self.delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        button_layout.addWidget(self.delete_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        self.save_button.setDefault(True)  # Make Save button the default button
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, account_data: dict | None = None, currencies: list | None = None) -> None
```

Initialize the dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `account_data` (`dict | None`): Dictionary with account data (id, name, balance, currency_code, is_liquid,
  is_cash). Defaults to `None`.
- `currencies` (`list | None`): List of currency codes. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        account_data: dict | None = None,
        currencies: list | None = None,
    ) -> None:
        super().__init__(parent)
        self.account_data = account_data or {}
        self.currencies = currencies or []
        self.result_data = {}

        self.setWindowTitle("Edit Account")
        self.setModal(True)
        self.setFixedSize(400, 350)

        self._setup_ui()
        self._populate_data()
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

### ⚙️ Method `_evaluate_expression`

```python
def _evaluate_expression(self, expression: str) -> float
```

Safely evaluate a mathematical expression.

Args:

- `expression` (`str`): String containing mathematical expression.

Returns:

- `float`: Calculated result as float.

Raises:

- `ValueError`: If expression is invalid or contains unsafe operations.

<details>
<summary>Code:</summary>

```python
def _evaluate_expression(self, expression: str) -> float:
        # Remove all whitespace
        expression = expression.replace(" ", "")

        # Only allow safe characters: numbers, operators, parentheses, decimal points
        if not re.match(r"^[0-9+\-*/().]+$", expression):
            msg = "Expression contains invalid characters"
            raise ValueError(msg)

        # Check for balanced parentheses
        if expression.count("(") != expression.count(")"):
            msg = "Unbalanced parentheses"
            raise ValueError(msg)

        # Check for division by zero
        if "/0" in expression or "/0." in expression:
            msg = "Division by zero"
            raise ValueError(msg)

        def _raise_value_error(msg: str) -> None:
            raise ValueError(msg)

        try:
            # Parse expression into AST
            tree = ast.parse(expression, mode="eval")

            # Check if AST is safe
            if not self._is_safe_node(tree):
                _raise_value_error("Expression contains unsafe operations")

            # Compile and evaluate safely
            code = compile(tree, "<string>", "eval")
            result = eval(code, {"__builtins__": {}}, {})

            if not isinstance(result, (int, float)):
                _raise_value_error("Expression does not evaluate to a number")
            return float(result)
        except SyntaxError as e:
            _raise_value_error(f"Invalid expression syntax: {e!s}")
        except Exception as e:
            _raise_value_error(f"Invalid expression: {e!s}")
```

</details>

### ⚙️ Method `_is_safe_node`

```python
def _is_safe_node(self, node: ast.AST) -> bool
```

Check if AST node is safe for evaluation.

Args:

- `node` (`ast.AST`): AST node to check.

Returns:

- `bool`: True if node is safe, False otherwise.

<details>
<summary>Code:</summary>

```python
def _is_safe_node(self, node: ast.AST) -> bool:
        # Allow numbers (int, float)
        if isinstance(node, (ast.Constant, ast.Num)):
            return True

        # Allow binary operations (+, -, *, /)
        if isinstance(node, ast.BinOp):
            return (
                isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div))
                and self._is_safe_node(node.left)
                and self._is_safe_node(node.right)
            )

        # Allow unary operations (+, -)
        if isinstance(node, ast.UnaryOp):
            return isinstance(node.op, (ast.UAdd, ast.USub)) and self._is_safe_node(node.operand)

        # Allow parentheses (expression)
        if isinstance(node, ast.Expression):
            return self._is_safe_node(node.body)

        return False
```

</details>

### ⚙️ Method `_on_delete`

```python
def _on_delete(self) -> None
```

Handle delete button click.

<details>
<summary>Code:</summary>

```python
def _on_delete(self) -> None:
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

### ⚙️ Method `_on_expression_changed`

```python
def _on_expression_changed(self) -> None
```

Handle expression field changes and update balance.

<details>
<summary>Code:</summary>

```python
def _on_expression_changed(self) -> None:
        expression = self.expression_edit.text().strip()
        if not expression:
            return

        try:
            result = self._evaluate_expression(expression)
            self.balance_spin.setValue(result)
        except ValueError:
            # Don't show error for partial expressions, only for invalid ones
            pass
```

</details>

### ⚙️ Method `_on_save`

```python
def _on_save(self) -> None
```

Handle save button click.

<details>
<summary>Code:</summary>

```python
def _on_save(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Account name cannot be empty")
            return

        # Check if expression field has content and try to evaluate it
        expression = self.expression_edit.text().strip()
        if expression:
            try:
                calculated_balance = self._evaluate_expression(expression)
                self.balance_spin.setValue(calculated_balance)
            except ValueError as e:
                QMessageBox.warning(self, "Error", f"Invalid expression: {e!s}")
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
def _populate_data(self) -> None
```

Populate the dialog with account data.

<details>
<summary>Code:</summary>

```python
def _populate_data(self) -> None:
        if self.account_data:
            self.name_edit.setText(self.account_data.get("name", ""))
            balance = self.account_data.get("balance", 0.0)
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
            self.expression_edit.setText("0.0")
```

</details>

### ⚙️ Method `_setup_ui`

```python
def _setup_ui(self) -> None
```

Set up the user interface.

<details>
<summary>Code:</summary>

```python
def _setup_ui(self) -> None:
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

        # Expression field for calculating balance
        expression_layout = QHBoxLayout()
        expression_layout.addWidget(QLabel("Expression:"))
        self.expression_edit = QLineEdit()
        self.expression_edit.setPlaceholderText("e.g., 3*200+100*3")
        self.expression_edit.textChanged.connect(self._on_expression_changed)
        expression_layout.addWidget(self.expression_edit)
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

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._on_delete)
        self.delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        button_layout.addWidget(self.delete_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        self.save_button.setDefault(True)  # Make Save button the default button
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
```

</details>
