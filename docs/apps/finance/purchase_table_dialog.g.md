---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `purchase_table_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PurchaseTableDialog`](#%EF%B8%8F-class-purchasetabledialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_date`](#%EF%B8%8F-method-get_date)
  - [⚙️ Method `get_items`](#%EF%B8%8F-method-get_items)
  - [⚙️ Method `_add_row`](#%EF%B8%8F-method-_add_row)
  - [⚙️ Method `_add_row_and_update`](#%EF%B8%8F-method-_add_row_and_update)
  - [⚙️ Method `_cell_text`](#%EF%B8%8F-method-_cell_text)
  - [⚙️ Method `_delete_selected_rows`](#%EF%B8%8F-method-_delete_selected_rows)
  - [⚙️ Method `_format_amount_cell`](#%EF%B8%8F-method-_format_amount_cell)
  - [⚙️ Method `_on_accept`](#%EF%B8%8F-method-_on_accept)
  - [⚙️ Method `_on_item_changed`](#%EF%B8%8F-method-_on_item_changed)
  - [⚙️ Method `_populate_from_initial_text`](#%EF%B8%8F-method-_populate_from_initial_text)
  - [⚙️ Method `_read_table_items`](#%EF%B8%8F-method-_read_table_items)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)
  - [⚙️ Method `_update_total_label`](#%EF%B8%8F-method-_update_total_label)

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

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Add Purchases",
        description: str | None = None,
        default_date: QDate | None = None,
        initial_text: str | None = None,
        currency_symbol: str = "",
    ) -> None:
        """Initialize the purchase table dialog."""
        super().__init__(parent)
        self._title = title
        self._description = description
        self._default_date = default_date
        self._initial_text = initial_text
        self._currency_symbol = currency_symbol
        self._parser = TextParser()
        self._accepted_items: list[ParsedPurchaseItem] = []
        self._updating_total = False
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

    def _on_accept(self) -> None:
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

    def _on_item_changed(self, _item: QTableWidgetItem) -> None:
        if self._updating_total:
            return
        self._update_total_label()

    def _populate_from_initial_text(self) -> None:
        self._table.setRowCount(0)
        if self._initial_text:
            for item in self._parser.parse_text(self._initial_text):
                self._add_row(
                    name=item.name,
                    category=item.category,
                    amount=self._format_amount_cell(item),
                )
        if self._table.rowCount() == 0:
            self._add_row()

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

        self._table: QTableWidgetType = QTableWidget(self)
        self._table.setColumnCount(len(self._HEADERS))
        self._table.setHorizontalHeaderLabels(list(self._HEADERS))
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.itemChanged.connect(self._on_item_changed)

        header = self._table.horizontalHeader()
        if header is not None:
            for column in range(len(self._HEADERS)):
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self._table)

        row_buttons_layout = QHBoxLayout()
        add_row_button = QPushButton("Add row")
        add_row_button.clicked.connect(self._add_row_and_update)
        row_buttons_layout.addWidget(add_row_button)
        delete_row_button = QPushButton("Delete row")
        delete_row_button.clicked.connect(self._delete_selected_rows)
        row_buttons_layout.addWidget(delete_row_button)
        row_buttons_layout.addStretch()
        layout.addLayout(row_buttons_layout)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.total_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_accept)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

    def _update_total_label(self) -> None:
        self._updating_total = True
        try:
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
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._description = description
        self._default_date = default_date
        self._initial_text = initial_text
        self._currency_symbol = currency_symbol
        self._parser = TextParser()
        self._accepted_items: list[ParsedPurchaseItem] = []
        self._updating_total = False
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

### ⚙️ Method `_on_accept`

```python
def _on_accept(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _on_accept(self) -> None:
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

### ⚙️ Method `_on_item_changed`

```python
def _on_item_changed(self, _item: QTableWidgetItem) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _on_item_changed(self, _item: QTableWidgetItem) -> None:
        if self._updating_total:
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
            for item in self._parser.parse_text(self._initial_text):
                self._add_row(
                    name=item.name,
                    category=item.category,
                    amount=self._format_amount_cell(item),
                )
        if self._table.rowCount() == 0:
            self._add_row()
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

        self._table: QTableWidgetType = QTableWidget(self)
        self._table.setColumnCount(len(self._HEADERS))
        self._table.setHorizontalHeaderLabels(list(self._HEADERS))
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.itemChanged.connect(self._on_item_changed)

        header = self._table.horizontalHeader()
        if header is not None:
            for column in range(len(self._HEADERS)):
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self._table)

        row_buttons_layout = QHBoxLayout()
        add_row_button = QPushButton("Add row")
        add_row_button.clicked.connect(self._add_row_and_update)
        row_buttons_layout.addWidget(add_row_button)
        delete_row_button = QPushButton("Delete row")
        delete_row_button.clicked.connect(self._delete_selected_rows)
        row_buttons_layout.addWidget(delete_row_button)
        row_buttons_layout.addStretch()
        layout.addLayout(row_buttons_layout)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.total_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_accept)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
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
