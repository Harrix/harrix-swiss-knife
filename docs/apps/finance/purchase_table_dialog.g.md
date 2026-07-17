---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `purchase_table_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PurchaseTableDialog`](#️-class-purchasetabledialog)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `get_date`](#️-method-get_date)
  - [⚙️ Method `get_items`](#️-method-get_items)
  - [⚙️ Method `_add_row`](#️-method-_add_row)
  - [⚙️ Method `_add_row_and_update`](#️-method-_add_row_and_update)
  - [⚙️ Method `_cell_text`](#️-method-_cell_text)
  - [⚙️ Method `_current_input_mode`](#️-method-_current_input_mode)
  - [⚙️ Method `_delete_selected_rows`](#️-method-_delete_selected_rows)
  - [⚙️ Method `_format_amount_cell`](#️-method-_format_amount_cell)
  - [⚙️ Method `_is_text_mode`](#️-method-_is_text_mode)
  - [⚙️ Method `_on_accept`](#️-method-_on_accept)
  - [⚙️ Method `_on_input_mode_changed`](#️-method-_on_input_mode_changed)
  - [⚙️ Method `_on_item_changed`](#️-method-_on_item_changed)
  - [⚙️ Method `_on_text_changed`](#️-method-_on_text_changed)
  - [⚙️ Method `_populate_from_initial_text`](#️-method-_populate_from_initial_text)
  - [⚙️ Method `_populate_table_from_text`](#️-method-_populate_table_from_text)
  - [⚙️ Method `_read_table_items`](#️-method-_read_table_items)
  - [⚙️ Method `_read_text_items`](#️-method-_read_text_items)
  - [⚙️ Method `_setup_ui`](#️-method-_setup_ui)
  - [⚙️ Method `_table_to_text`](#️-method-_table_to_text)
  - [⚙️ Method `_update_total_label`](#️-method-_update_total_label)

</details>

## 🏛️ Class `PurchaseTableDialog`

```python
class PurchaseTableDialog(QDialog)
```

Show purchases in an editable table with a live total before saving.

<details>
<summary>Code:</summary>

```python
class PurchaseTableDialog(QDialog):

    _COL_NAME = 0
    _COL_CATEGORY = 1
    _COL_AMOUNT = 2
    _HEADERS = ("Name", "Category", "Amount")
    _MODE_TABLE = 0
    _MODE_TEXT = 1

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Add Purchases",
        description: str | None = None,
        default_date: QDate | None = None,
        initial_text: str | None = None,
        currency_symbol: str = "",
        text_placeholder: str = "",
    ) -> None:
        """Initialize the purchase table dialog."""
        super().__init__(parent)
        self._title = title
        self._description = description
        self._default_date = default_date
        self._initial_text = initial_text
        self._currency_symbol = currency_symbol
        self._text_placeholder = text_placeholder
        self._parser = TextParser()
        self._accepted_items: list[ParsedPurchaseItem] = []
        self._updating_total = False
        self._syncing_modes = False
        self._setup_ui()
        self._populate_from_initial_text()
        self._update_total_label()

    def get_date(self) -> str | None:
        """Return selected date in yyyy-MM-dd format, or None if cancelled."""
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        return self.date_edit.date().toString("yyyy-MM-dd")

    def get_items(self) -> list[ParsedPurchaseItem]:
        """Return validated purchase items accepted by the user."""
        if self.result() != QDialog.DialogCode.Accepted:
            return []
        return list(self._accepted_items)

    def _add_row(self, *, name: str = "", category: str = "", amount: str = "") -> None:
        row_idx = self._table.rowCount()
        self._table.insertRow(row_idx)
        self._table.setItem(row_idx, self._COL_NAME, QTableWidgetItem(name))
        self._table.setItem(row_idx, self._COL_CATEGORY, QTableWidgetItem(category))
        self._table.setItem(row_idx, self._COL_AMOUNT, QTableWidgetItem(amount))

    def _add_row_and_update(self) -> None:
        self._add_row()
        self._update_total_label()

    def _cell_text(self, row_idx: int, column: int) -> str:
        item = self._table.item(row_idx, column)
        return item.text().strip() if item is not None else ""

    def _current_input_mode(self) -> int:
        return self._mode_stack.currentIndex()

    def _delete_selected_rows(self) -> None:
        selected_rows = sorted({index.row() for index in self._table.selectedIndexes()}, reverse=True)
        if not selected_rows and self._table.rowCount() > 0:
            self._table.removeRow(self._table.rowCount() - 1)
            self._update_total_label()
            return
        for row_idx in selected_rows:
            self._table.removeRow(row_idx)
        if self._table.rowCount() == 0:
            self._add_row()
        self._update_total_label()

    def _format_amount_cell(self, item: ParsedPurchaseItem) -> str:
        amount_text = f"{item.amount:g}"
        if item.currency_symbol:
            return f"{amount_text} {item.currency_symbol}"
        if self._currency_symbol:
            return f"{amount_text} {self._currency_symbol}"
        return amount_text

    def _is_text_mode(self) -> bool:
        return self._current_input_mode() == self._MODE_TEXT

    def _on_accept(self) -> None:
        if self._is_text_mode():
            items, invalid_line_numbers = self._read_text_items()
            if not items:
                if invalid_line_numbers:
                    QMessageBox.warning(
                        self,
                        "Invalid Lines",
                        "Some lines have incomplete or invalid data. "
                        "Each line must be: Name<Tab>Category<Tab>Amount.\n\n"
                        f"Invalid lines: {', '.join(str(line_num) for line_num in invalid_line_numbers)}",
                    )
                else:
                    QMessageBox.information(self, "No Items", "Add at least one purchase line.")
                return
            self._accepted_items = items
            self.accept()
            return

        items, invalid_rows = self._read_table_items()
        if not items:
            if invalid_rows:
                QMessageBox.warning(
                    self,
                    "Invalid Rows",
                    "Some rows have incomplete or invalid data. "
                    "Each row must have Name, Category, and Amount.\n\n"
                    f"Invalid rows: {', '.join(str(row + 1) for row in invalid_rows)}",
                )
            else:
                QMessageBox.information(self, "No Items", "Add at least one purchase row.")
            return
        self._accepted_items = items
        self.accept()

    def _on_input_mode_changed(self, mode_id: int) -> None:
        if self._syncing_modes:
            return

        self._syncing_modes = True
        try:
            if mode_id == self._MODE_TEXT:
                self._text_edit.setPlainText(self._table_to_text())
            else:
                self._populate_table_from_text(self._text_edit.toPlainText())
        finally:
            self._syncing_modes = False

        self._mode_stack.setCurrentIndex(mode_id)
        self._row_buttons_widget.setVisible(mode_id == self._MODE_TABLE)
        self._update_total_label()

    def _on_item_changed(self, _item: QTableWidgetItem) -> None:
        if self._updating_total or self._is_text_mode():
            return
        self._update_total_label()

    def _on_text_changed(self) -> None:
        if self._updating_total or not self._is_text_mode():
            return
        self._update_total_label()

    def _populate_from_initial_text(self) -> None:
        self._table.setRowCount(0)
        if self._initial_text:
            self._populate_table_from_text(self._initial_text)
            self._text_edit.setPlainText(self._initial_text.strip())
        else:
            self._add_row()
            self._text_edit.clear()
        self._mode_table_radio.setChecked(True)
        self._mode_stack.setCurrentIndex(self._MODE_TABLE)
        self._row_buttons_widget.setVisible(True)

    def _populate_table_from_text(self, text: str) -> None:
        self._updating_total = True
        try:
            self._table.setRowCount(0)
            has_rows = False
            for _line_num, line in enumerate_stripped_non_empty_lines(text):
                has_rows = True
                parsed_items = self._parser.parse_text(line)
                if parsed_items:
                    item = parsed_items[0]
                    self._add_row(
                        name=item.name,
                        category=item.category,
                        amount=self._format_amount_cell(item),
                    )
                    continue

                parts = line.split("\t")
                column_count = len(self._HEADERS)
                while len(parts) < column_count:
                    parts.append("")
                self._add_row(
                    name=parts[0].strip(),
                    category=parts[1].strip(),
                    amount=parts[2].strip(),
                )

            if not has_rows:
                self._add_row()
        finally:
            self._updating_total = False

    def _read_table_items(self) -> tuple[list[ParsedPurchaseItem], list[int]]:
        items: list[ParsedPurchaseItem] = []
        invalid_rows: list[int] = []

        for row_idx in range(self._table.rowCount()):
            name = self._cell_text(row_idx, self._COL_NAME)
            category = self._cell_text(row_idx, self._COL_CATEGORY)
            amount_str = self._cell_text(row_idx, self._COL_AMOUNT)

            if not name and not category and not amount_str:
                continue

            parsed = self._parser.parse_row(name, category, amount_str)
            if parsed is None:
                invalid_rows.append(row_idx)
                continue
            items.append(parsed)

        return items, sorted(invalid_rows)

    def _read_text_items(self) -> tuple[list[ParsedPurchaseItem], list[int]]:
        items: list[ParsedPurchaseItem] = []
        invalid_line_numbers: list[int] = []

        for line_num, line in enumerate_stripped_non_empty_lines(self._text_edit.toPlainText()):
            parsed_items = self._parser.parse_text(line)
            if not parsed_items:
                invalid_line_numbers.append(line_num)
                continue
            items.append(parsed_items[0])

        return items, sorted(invalid_line_numbers)

    def _setup_ui(self) -> None:
        self.setWindowTitle(self._title)
        self.setMinimumSize(800, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        if self._description:
            description_label = QLabel(self._description)
            description_label.setWordWrap(True)
            layout.addWidget(description_label)

        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_layout.addWidget(date_label)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(self._default_date or QDate.currentDate())
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)

        mode_layout = QHBoxLayout()
        mode_label = QLabel("Input mode:")
        mode_layout.addWidget(mode_label)

        self._mode_button_group = QButtonGroup(self)
        self._mode_table_radio = QRadioButton("Table")
        self._mode_text_radio = QRadioButton("Text")
        self._mode_button_group.addButton(self._mode_table_radio, self._MODE_TABLE)
        self._mode_button_group.addButton(self._mode_text_radio, self._MODE_TEXT)
        self._mode_table_radio.setChecked(True)
        mode_layout.addWidget(self._mode_table_radio)
        mode_layout.addWidget(self._mode_text_radio)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        self._mode_stack = QStackedWidget(self)

        table_page = QWidget(self)
        table_page_layout = QVBoxLayout(table_page)
        table_page_layout.setContentsMargins(0, 0, 0, 0)

        self._table: QTableWidgetType = QTableWidget(table_page)
        self._table.setColumnCount(len(self._HEADERS))
        self._table.setHorizontalHeaderLabels(list(self._HEADERS))
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.itemChanged.connect(self._on_item_changed)

        header = self._table.horizontalHeader()
        if header is not None:
            for column in range(len(self._HEADERS)):
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

        table_page_layout.addWidget(self._table)

        self._row_buttons_widget = QWidget(table_page)
        row_buttons_layout = QHBoxLayout(self._row_buttons_widget)
        row_buttons_layout.setContentsMargins(0, 0, 0, 0)
        add_row_button = make_emoji_push_button("Add row", "➕")  # noqa: RUF001
        add_row_button.clicked.connect(self._add_row_and_update)
        row_buttons_layout.addWidget(add_row_button)
        delete_row_button = make_emoji_push_button("Delete row", "🗑️")
        delete_row_button.clicked.connect(self._delete_selected_rows)
        row_buttons_layout.addWidget(delete_row_button)
        row_buttons_layout.addStretch()
        table_page_layout.addWidget(self._row_buttons_widget)

        self._mode_stack.addWidget(table_page)

        self._text_edit = QPlainTextEdit(self)
        if self._text_placeholder:
            self._text_edit.setPlaceholderText(self._text_placeholder)
        self._text_edit.textChanged.connect(self._on_text_changed)
        self._mode_stack.addWidget(self._text_edit)

        layout.addWidget(self._mode_stack)

        self._mode_button_group.idClicked.connect(self._on_input_mode_changed)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.total_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = make_emoji_push_button("Cancel", "❌")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        ok_button = make_emoji_push_button("OK", "✅")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_accept)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

    def _table_to_text(self) -> str:
        lines: list[str] = []
        for row_idx in range(self._table.rowCount()):
            name = self._cell_text(row_idx, self._COL_NAME)
            category = self._cell_text(row_idx, self._COL_CATEGORY)
            amount_str = self._cell_text(row_idx, self._COL_AMOUNT)
            if not name and not category and not amount_str:
                continue
            lines.append(f"{name}\t{category}\t{amount_str}")
        return "\n".join(lines)

    def _update_total_label(self) -> None:
        self._updating_total = True
        try:
            if self._is_text_mode():
                items, _invalid_lines = self._read_text_items()
            else:
                items, _invalid_rows = self._read_table_items()
            total_amount = sum(item.amount for item in items)
            symbol = self._currency_symbol
            if symbol:
                self.total_label.setText(f"Total: {total_amount:,.2f} {symbol}")
            else:
                self.total_label.setText(f"Total: {total_amount:,.2f}")
        finally:
            self._updating_total = False
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the purchase table dialog.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Add Purchases",
        description: str | None = None,
        default_date: QDate | None = None,
        initial_text: str | None = None,
        currency_symbol: str = "",
        text_placeholder: str = "",
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._description = description
        self._default_date = default_date
        self._initial_text = initial_text
        self._currency_symbol = currency_symbol
        self._text_placeholder = text_placeholder
        self._parser = TextParser()
        self._accepted_items: list[ParsedPurchaseItem] = []
        self._updating_total = False
        self._syncing_modes = False
        self._setup_ui()
        self._populate_from_initial_text()
        self._update_total_label()
```

</details>

### ⚙️ Method `get_date`

```python
def get_date(self) -> str | None
```

Return selected date in yyyy-MM-dd format, or None if cancelled.

<details>
<summary>Code:</summary>

```python
def get_date(self) -> str | None:
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        return self.date_edit.date().toString("yyyy-MM-dd")
```

</details>

### ⚙️ Method `get_items`

```python
def get_items(self) -> list[ParsedPurchaseItem]
```

Return validated purchase items accepted by the user.

<details>
<summary>Code:</summary>

```python
def get_items(self) -> list[ParsedPurchaseItem]:
        if self.result() != QDialog.DialogCode.Accepted:
            return []
        return list(self._accepted_items)
```

</details>

### ⚙️ Method `_add_row`

```python
def _add_row(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _add_row(self, *, name: str = "", category: str = "", amount: str = "") -> None:
        row_idx = self._table.rowCount()
        self._table.insertRow(row_idx)
        self._table.setItem(row_idx, self._COL_NAME, QTableWidgetItem(name))
        self._table.setItem(row_idx, self._COL_CATEGORY, QTableWidgetItem(category))
        self._table.setItem(row_idx, self._COL_AMOUNT, QTableWidgetItem(amount))
```

</details>

### ⚙️ Method `_add_row_and_update`

```python
def _add_row_and_update(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _add_row_and_update(self) -> None:
        self._add_row()
        self._update_total_label()
```

</details>

### ⚙️ Method `_cell_text`

```python
def _cell_text(self, row_idx: int, column: int) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _cell_text(self, row_idx: int, column: int) -> str:
        item = self._table.item(row_idx, column)
        return item.text().strip() if item is not None else ""
```

</details>

### ⚙️ Method `_current_input_mode`

```python
def _current_input_mode(self) -> int
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _current_input_mode(self) -> int:
        return self._mode_stack.currentIndex()
```

</details>

### ⚙️ Method `_delete_selected_rows`

```python
def _delete_selected_rows(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _delete_selected_rows(self) -> None:
        selected_rows = sorted({index.row() for index in self._table.selectedIndexes()}, reverse=True)
        if not selected_rows and self._table.rowCount() > 0:
            self._table.removeRow(self._table.rowCount() - 1)
            self._update_total_label()
            return
        for row_idx in selected_rows:
            self._table.removeRow(row_idx)
        if self._table.rowCount() == 0:
            self._add_row()
        self._update_total_label()
```

</details>

### ⚙️ Method `_format_amount_cell`

```python
def _format_amount_cell(self, item: ParsedPurchaseItem) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _format_amount_cell(self, item: ParsedPurchaseItem) -> str:
        amount_text = f"{item.amount:g}"
        if item.currency_symbol:
            return f"{amount_text} {item.currency_symbol}"
        if self._currency_symbol:
            return f"{amount_text} {self._currency_symbol}"
        return amount_text
```

</details>

### ⚙️ Method `_is_text_mode`

```python
def _is_text_mode(self) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_text_mode(self) -> bool:
        return self._current_input_mode() == self._MODE_TEXT
```

</details>

### ⚙️ Method `_on_accept`

```python
def _on_accept(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _on_accept(self) -> None:
        if self._is_text_mode():
            items, invalid_line_numbers = self._read_text_items()
            if not items:
                if invalid_line_numbers:
                    QMessageBox.warning(
                        self,
                        "Invalid Lines",
                        "Some lines have incomplete or invalid data. "
                        "Each line must be: Name<Tab>Category<Tab>Amount.\n\n"
                        f"Invalid lines: {', '.join(str(line_num) for line_num in invalid_line_numbers)}",
                    )
                else:
                    QMessageBox.information(self, "No Items", "Add at least one purchase line.")
                return
            self._accepted_items = items
            self.accept()
            return

        items, invalid_rows = self._read_table_items()
        if not items:
            if invalid_rows:
                QMessageBox.warning(
                    self,
                    "Invalid Rows",
                    "Some rows have incomplete or invalid data. "
                    "Each row must have Name, Category, and Amount.\n\n"
                    f"Invalid rows: {', '.join(str(row + 1) for row in invalid_rows)}",
                )
            else:
                QMessageBox.information(self, "No Items", "Add at least one purchase row.")
            return
        self._accepted_items = items
        self.accept()
```

</details>

### ⚙️ Method `_on_input_mode_changed`

```python
def _on_input_mode_changed(self, mode_id: int) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _on_input_mode_changed(self, mode_id: int) -> None:
        if self._syncing_modes:
            return

        self._syncing_modes = True
        try:
            if mode_id == self._MODE_TEXT:
                self._text_edit.setPlainText(self._table_to_text())
            else:
                self._populate_table_from_text(self._text_edit.toPlainText())
        finally:
            self._syncing_modes = False

        self._mode_stack.setCurrentIndex(mode_id)
        self._row_buttons_widget.setVisible(mode_id == self._MODE_TABLE)
        self._update_total_label()
```

</details>

### ⚙️ Method `_on_item_changed`

```python
def _on_item_changed(self, _item: QTableWidgetItem) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _on_item_changed(self, _item: QTableWidgetItem) -> None:
        if self._updating_total or self._is_text_mode():
            return
        self._update_total_label()
```

</details>

### ⚙️ Method `_on_text_changed`

```python
def _on_text_changed(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _on_text_changed(self) -> None:
        if self._updating_total or not self._is_text_mode():
            return
        self._update_total_label()
```

</details>

### ⚙️ Method `_populate_from_initial_text`

```python
def _populate_from_initial_text(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _populate_from_initial_text(self) -> None:
        self._table.setRowCount(0)
        if self._initial_text:
            self._populate_table_from_text(self._initial_text)
            self._text_edit.setPlainText(self._initial_text.strip())
        else:
            self._add_row()
            self._text_edit.clear()
        self._mode_table_radio.setChecked(True)
        self._mode_stack.setCurrentIndex(self._MODE_TABLE)
        self._row_buttons_widget.setVisible(True)
```

</details>

### ⚙️ Method `_populate_table_from_text`

```python
def _populate_table_from_text(self, text: str) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _populate_table_from_text(self, text: str) -> None:
        self._updating_total = True
        try:
            self._table.setRowCount(0)
            has_rows = False
            for _line_num, line in enumerate_stripped_non_empty_lines(text):
                has_rows = True
                parsed_items = self._parser.parse_text(line)
                if parsed_items:
                    item = parsed_items[0]
                    self._add_row(
                        name=item.name,
                        category=item.category,
                        amount=self._format_amount_cell(item),
                    )
                    continue

                parts = line.split("\t")
                column_count = len(self._HEADERS)
                while len(parts) < column_count:
                    parts.append("")
                self._add_row(
                    name=parts[0].strip(),
                    category=parts[1].strip(),
                    amount=parts[2].strip(),
                )

            if not has_rows:
                self._add_row()
        finally:
            self._updating_total = False
```

</details>

### ⚙️ Method `_read_table_items`

```python
def _read_table_items(self) -> tuple[list[ParsedPurchaseItem], list[int]]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _read_table_items(self) -> tuple[list[ParsedPurchaseItem], list[int]]:
        items: list[ParsedPurchaseItem] = []
        invalid_rows: list[int] = []

        for row_idx in range(self._table.rowCount()):
            name = self._cell_text(row_idx, self._COL_NAME)
            category = self._cell_text(row_idx, self._COL_CATEGORY)
            amount_str = self._cell_text(row_idx, self._COL_AMOUNT)

            if not name and not category and not amount_str:
                continue

            parsed = self._parser.parse_row(name, category, amount_str)
            if parsed is None:
                invalid_rows.append(row_idx)
                continue
            items.append(parsed)

        return items, sorted(invalid_rows)
```

</details>

### ⚙️ Method `_read_text_items`

```python
def _read_text_items(self) -> tuple[list[ParsedPurchaseItem], list[int]]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _read_text_items(self) -> tuple[list[ParsedPurchaseItem], list[int]]:
        items: list[ParsedPurchaseItem] = []
        invalid_line_numbers: list[int] = []

        for line_num, line in enumerate_stripped_non_empty_lines(self._text_edit.toPlainText()):
            parsed_items = self._parser.parse_text(line)
            if not parsed_items:
                invalid_line_numbers.append(line_num)
                continue
            items.append(parsed_items[0])

        return items, sorted(invalid_line_numbers)
```

</details>

### ⚙️ Method `_setup_ui`

```python
def _setup_ui(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _setup_ui(self) -> None:
        self.setWindowTitle(self._title)
        self.setMinimumSize(800, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        if self._description:
            description_label = QLabel(self._description)
            description_label.setWordWrap(True)
            layout.addWidget(description_label)

        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_layout.addWidget(date_label)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(self._default_date or QDate.currentDate())
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)

        mode_layout = QHBoxLayout()
        mode_label = QLabel("Input mode:")
        mode_layout.addWidget(mode_label)

        self._mode_button_group = QButtonGroup(self)
        self._mode_table_radio = QRadioButton("Table")
        self._mode_text_radio = QRadioButton("Text")
        self._mode_button_group.addButton(self._mode_table_radio, self._MODE_TABLE)
        self._mode_button_group.addButton(self._mode_text_radio, self._MODE_TEXT)
        self._mode_table_radio.setChecked(True)
        mode_layout.addWidget(self._mode_table_radio)
        mode_layout.addWidget(self._mode_text_radio)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        self._mode_stack = QStackedWidget(self)

        table_page = QWidget(self)
        table_page_layout = QVBoxLayout(table_page)
        table_page_layout.setContentsMargins(0, 0, 0, 0)

        self._table: QTableWidgetType = QTableWidget(table_page)
        self._table.setColumnCount(len(self._HEADERS))
        self._table.setHorizontalHeaderLabels(list(self._HEADERS))
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.itemChanged.connect(self._on_item_changed)

        header = self._table.horizontalHeader()
        if header is not None:
            for column in range(len(self._HEADERS)):
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

        table_page_layout.addWidget(self._table)

        self._row_buttons_widget = QWidget(table_page)
        row_buttons_layout = QHBoxLayout(self._row_buttons_widget)
        row_buttons_layout.setContentsMargins(0, 0, 0, 0)
        add_row_button = make_emoji_push_button("Add row", "➕")  # noqa: RUF001
        add_row_button.clicked.connect(self._add_row_and_update)
        row_buttons_layout.addWidget(add_row_button)
        delete_row_button = make_emoji_push_button("Delete row", "🗑️")
        delete_row_button.clicked.connect(self._delete_selected_rows)
        row_buttons_layout.addWidget(delete_row_button)
        row_buttons_layout.addStretch()
        table_page_layout.addWidget(self._row_buttons_widget)

        self._mode_stack.addWidget(table_page)

        self._text_edit = QPlainTextEdit(self)
        if self._text_placeholder:
            self._text_edit.setPlaceholderText(self._text_placeholder)
        self._text_edit.textChanged.connect(self._on_text_changed)
        self._mode_stack.addWidget(self._text_edit)

        layout.addWidget(self._mode_stack)

        self._mode_button_group.idClicked.connect(self._on_input_mode_changed)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.total_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = make_emoji_push_button("Cancel", "❌")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        ok_button = make_emoji_push_button("OK", "✅")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_accept)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
```

</details>

### ⚙️ Method `_table_to_text`

```python
def _table_to_text(self) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _table_to_text(self) -> str:
        lines: list[str] = []
        for row_idx in range(self._table.rowCount()):
            name = self._cell_text(row_idx, self._COL_NAME)
            category = self._cell_text(row_idx, self._COL_CATEGORY)
            amount_str = self._cell_text(row_idx, self._COL_AMOUNT)
            if not name and not category and not amount_str:
                continue
            lines.append(f"{name}\t{category}\t{amount_str}")
        return "\n".join(lines)
```

</details>

### ⚙️ Method `_update_total_label`

```python
def _update_total_label(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _update_total_label(self) -> None:
        self._updating_total = True
        try:
            if self._is_text_mode():
                items, _invalid_lines = self._read_text_items()
            else:
                items, _invalid_rows = self._read_table_items()
            total_amount = sum(item.amount for item in items)
            symbol = self._currency_symbol
            if symbol:
                self.total_label.setText(f"Total: {total_amount:,.2f} {symbol}")
            else:
                self.total_label.setText(f"Total: {total_amount:,.2f}")
        finally:
            self._updating_total = False
```

</details>
