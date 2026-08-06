"""Dialog to evaluate an arithmetic expression into an amount."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.finance.number_utils import try_evaluate_arithmetic_expression
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons


class AmountExpressionDialog(QDialog):
    """Modal dialog: type an expression and see its live numeric result."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        initial_expression: str = "",
        minimum: float = 0.0,
        maximum: float = 999999.99,
    ) -> None:
        """Initialize the expression dialog.

        Args:

        - `parent`: Parent widget.
        - `initial_expression`: Prefill for the expression field.
        - `minimum` / `maximum`: Allowed result range (matches the amount spin box).

        """
        super().__init__(parent)
        self._minimum = minimum
        self._maximum = maximum
        self._result: float | None = None

        self.setWindowTitle("Calculate Amount")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Expression:", self))
        self._expression_edit = QLineEdit(self)
        self._expression_edit.setPlaceholderText("e.g. 6522/2-600")
        self._expression_edit.setClearButtonEnabled(True)
        expression_font = QFont()
        expression_font.setPointSize(12)
        self._expression_edit.setFont(expression_font)
        layout.addWidget(self._expression_edit)

        self._result_label = QLabel(self)
        self._result_label.setWordWrap(True)
        self._result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        result_font = QFont()
        result_font.setPointSize(11)
        result_font.setBold(True)
        self._result_label.setFont(result_font)
        layout.addWidget(self._result_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        self._ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._expression_edit.textChanged.connect(self._update_preview)
        if initial_expression:
            self._expression_edit.setText(initial_expression)
        else:
            self._update_preview()

        self._expression_edit.setFocus()
        self._expression_edit.selectAll()

    def get_result(self) -> float | None:
        """Return the accepted numeric result, or `None` if cancelled."""
        return self._result

    def _on_accept(self) -> None:
        value, error = try_evaluate_arithmetic_expression(self._expression_edit.text())
        if error is not None or value is None:
            self._update_preview()
            return
        range_error = self._range_error(value)
        if range_error is not None:
            self._set_error(range_error)
            return
        self._result = value
        self.accept()

    def _range_error(self, value: float) -> str | None:
        if value < self._minimum:
            return f"Result {value:g} is below minimum {self._minimum:g}"
        if value > self._maximum:
            return f"Result {value:g} is above maximum {self._maximum:g}"
        return None

    def _set_error(self, message: str) -> None:
        self._result_label.setStyleSheet("color: #c62828;")
        self._result_label.setText(f"Error: {message}")
        if self._ok_button is not None:
            self._ok_button.setEnabled(False)

    def _set_result(self, value: float) -> None:
        self._result_label.setStyleSheet("color: #2e7d32;")
        self._result_label.setText(f"= {value:g}")
        if self._ok_button is not None:
            self._ok_button.setEnabled(True)

    def _update_preview(self) -> None:
        text = self._expression_edit.text().strip()
        if not text:
            self._result_label.setStyleSheet("color: #888;")
            self._result_label.setText("Enter an expression")
            if self._ok_button is not None:
                self._ok_button.setEnabled(False)
            return

        value, error = try_evaluate_arithmetic_expression(text)
        if error is not None or value is None:
            self._set_error(error or "Invalid expression")
            return

        range_error = self._range_error(value)
        if range_error is not None:
            self._set_error(range_error)
            return

        self._set_result(value)
