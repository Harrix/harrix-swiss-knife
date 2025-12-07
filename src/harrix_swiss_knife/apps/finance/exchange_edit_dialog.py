"""Exchange edit dialog."""

from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
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


class ExchangeEditDialog(QDialog):
    """Dialog for editing currency exchange information.

    This dialog allows users to edit exchange information including currencies,
    amounts, rate, fee, date, and description.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        exchange_data: dict | None = None,
        currencies: list[str] | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to None.
        - `exchange_data` (`dict | None`): Dictionary with exchange data. Defaults to None.
        - `currencies` (`list[str] | None`): List of currency codes. Defaults to None.

        """
        super().__init__(parent)
        self.exchange_data = exchange_data or {}
        self.currencies = currencies or []
        self.result_data = {}

        self.setWindowTitle("Edit Currency Exchange")
        self.setModal(True)
        self.setMinimumSize(450, 400)

        self._setup_ui()
        self._populate_data()

    def get_result(self) -> dict:
        """Get the dialog result.

        Returns:

        - `dict`: Dictionary with exchange data if accepted, empty dict if cancelled.

        """
        return self.result_data

    def _on_ok(self) -> None:
        """Handle OK button click."""
        # Get values
        from_currency = self.from_currency_combo.currentText()
        to_currency = self.to_currency_combo.currentText()
        amount_from = self.amount_from_spin.value()
        amount_to = self.amount_to_spin.value()
        rate = self.rate_spin.value()
        fee = self.fee_spin.value()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        description = self.description_edit.text()

        # Validate
        if not from_currency or not to_currency:
            QMessageBox.warning(self, "Validation Error", "Please select both currencies")
            return

        if from_currency == to_currency:
            QMessageBox.warning(self, "Validation Error", "From and To currencies must be different")
            return

        if amount_from <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount From must be positive")
            return

        if amount_to <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount To must be positive")
            return

        if rate <= 0:
            QMessageBox.warning(self, "Validation Error", "Exchange rate must be positive")
            return

        if fee < 0:
            QMessageBox.warning(self, "Validation Error", "Fee cannot be negative")
            return

        # Store result
        self.result_data = {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount_from": amount_from,
            "amount_to": amount_to,
            "rate": rate,
            "fee": fee,
            "date": date,
            "description": description,
        }

        self.accept()

    def _populate_data(self) -> None:
        """Populate the dialog with existing data."""
        if not self.exchange_data:
            return

        # Set currency combos
        from_currency = self.exchange_data.get("from_currency", "")
        to_currency = self.exchange_data.get("to_currency", "")

        from_idx = self.from_currency_combo.findText(from_currency)
        if from_idx >= 0:
            self.from_currency_combo.setCurrentIndex(from_idx)

        to_idx = self.to_currency_combo.findText(to_currency)
        if to_idx >= 0:
            self.to_currency_combo.setCurrentIndex(to_idx)

        # Set amounts
        self.amount_from_spin.setValue(float(self.exchange_data.get("amount_from", 0)))
        self.amount_to_spin.setValue(float(self.exchange_data.get("amount_to", 0)))

        # Set rate
        self.rate_spin.setValue(float(self.exchange_data.get("rate", 0)))

        # Set fee
        self.fee_spin.setValue(float(self.exchange_data.get("fee", 0)))

        # Set date
        date_str = self.exchange_data.get("date", "")
        if date_str:
            try:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():  # type: ignore[no-matching-overload]
                    self.date_edit.setDate(date)
            except Exception as e:
                print(f"Failed to parse or set date '{date_str}': {e}")

        # Set description
        self.description_edit.setText(self.exchange_data.get("description", ""))

        # Set focus on amount_from
        self.amount_from_spin.setFocus()
        self.amount_from_spin.selectAll()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout()

        # From currency
        from_layout = QHBoxLayout()
        from_layout.addWidget(QLabel("From Currency:"))
        self.from_currency_combo = QComboBox()
        self.from_currency_combo.addItems(self.currencies)
        from_layout.addWidget(self.from_currency_combo)
        layout.addLayout(from_layout)

        # To currency
        to_layout = QHBoxLayout()
        to_layout.addWidget(QLabel("To Currency:"))
        self.to_currency_combo = QComboBox()
        self.to_currency_combo.addItems(self.currencies)
        to_layout.addWidget(self.to_currency_combo)
        layout.addLayout(to_layout)

        # Amount from
        amount_from_layout = QHBoxLayout()
        amount_from_layout.addWidget(QLabel("Amount From:"))
        self.amount_from_spin = QDoubleSpinBox()
        self.amount_from_spin.setRange(0, 999999999.99)
        self.amount_from_spin.setDecimals(2)
        amount_from_layout.addWidget(self.amount_from_spin)
        layout.addLayout(amount_from_layout)

        # Amount to
        amount_to_layout = QHBoxLayout()
        amount_to_layout.addWidget(QLabel("Amount To:"))
        self.amount_to_spin = QDoubleSpinBox()
        self.amount_to_spin.setRange(0, 999999999.99)
        self.amount_to_spin.setDecimals(2)
        amount_to_layout.addWidget(self.amount_to_spin)
        layout.addLayout(amount_to_layout)

        # Rate
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("Rate:"))
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0, 999999999.99)
        self.rate_spin.setDecimals(6)
        rate_layout.addWidget(self.rate_spin)
        layout.addLayout(rate_layout)

        # Fee
        fee_layout = QHBoxLayout()
        fee_layout.addWidget(QLabel("Fee:"))
        self.fee_spin = QDoubleSpinBox()
        self.fee_spin.setRange(0, 999999999.99)
        self.fee_spin.setDecimals(2)
        fee_layout.addWidget(self.fee_spin)
        layout.addLayout(fee_layout)

        # Date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)

        # Description
        description_layout = QHBoxLayout()
        description_layout.addWidget(QLabel("Description:"))
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Optional description")
        description_layout.addWidget(self.description_edit)
        layout.addLayout(description_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
