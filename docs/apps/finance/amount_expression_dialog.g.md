---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `amount_expression_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AmountExpressionDialog`](#%EF%B8%8F-class-amountexpressiondialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_result`](#%EF%B8%8F-method-get_result)

</details>

## 🏛️ Class `AmountExpressionDialog`

```python
class AmountExpressionDialog(QDialog)
```

Modal dialog: type an expression and see its live numeric result.

<details>
<summary>Code:</summary>

```python
class AmountExpressionDialog(QDialog):

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the expression dialog.

Args:

- `parent`: Parent widget.
- `initial_expression`: Prefill for the expression field.
- `minimum` / `maximum`: Allowed result range (matches the amount spin box).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        initial_expression: str = "",
        minimum: float = 0.0,
        maximum: float = 999999.99,
    ) -> None:
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
```

</details>

### ⚙️ Method `get_result`

```python
def get_result(self) -> float | None
```

Return the accepted numeric result, or `None` if cancelled.

<details>
<summary>Code:</summary>

```python
def get_result(self) -> float | None:
        return self._result
```

</details>
