"""Account edit dialog."""

from __future__ import annotations

import re

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AccountEditDialog(QDialog):
    """Dialog for editing account information.

    This dialog allows users to create, edit, or delete account information
    including name, balance, currency, and account type settings.

    """

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

        try:
            # Use eval with a restricted namespace for safety
            result = eval(expression, {"__builtins__": {}}, {})
            if not isinstance(result, (int, float)):
                msg = "Expression does not evaluate to a number"
                raise ValueError(msg)
            return float(result)
        except Exception as e:
            msg = f"Invalid expression: {e!s}"
            raise ValueError(msg)

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
