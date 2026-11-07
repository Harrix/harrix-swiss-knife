---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `transaction_filter_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `advanced_transactions_filter_is_active`](#-function-advanced_transactions_filter_is_active)
- [🔧 Function `install_transactions_filter_chrome`](#-function-install_transactions_filter_chrome)
- [🔧 Function `populate_transactions_category_filter`](#-function-populate_transactions_category_filter)
- [🔧 Function `populate_transactions_currency_filter`](#-function-populate_transactions_currency_filter)
- [🔧 Function `populate_transactions_type_filter`](#-function-populate_transactions_type_filter)
- [🔧 Function `refresh_transactions_filter_chips`](#-function-refresh_transactions_filter_chips)
- [🔧 Function `selected_transactions_filter_value`](#-function-selected_transactions_filter_value)
- [🔧 Function `transactions_filter_combo_value`](#-function-transactions_filter_combo_value)

</details>

## 🔧 Function `advanced_transactions_filter_is_active`

```python
def advanced_transactions_filter_is_active(host: Any) -> bool
```

Return whether any non-search transaction filter is applied.

<details>
<summary>Code:</summary>

```python
def advanced_transactions_filter_is_active(host: Any) -> bool:
    if transactions_filter_combo_value(host.comboBox_filter_type) in {FILTER_TYPE_EXPENSE, FILTER_TYPE_INCOME}:
        return True
    if transactions_filter_combo_value(host.comboBox_filter_category):
        return True
    if transactions_filter_combo_value(host.comboBox_filter_currency):
        return True
    return bool(host.checkBox_use_date_filter.isChecked())
```

</details>

## 🔧 Function `install_transactions_filter_chrome`

```python
def install_transactions_filter_chrome(host: Any) -> None
```

Rebuild the transactions filter strip: search + Filter + chips + advanced panel.

<details>
<summary>Code:</summary>

```python
def install_transactions_filter_chrome(host: Any) -> None:
    layout = host.horizontalLayout_filter
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(host.groupBox_filter)

    for label in (
        host.label_filter_description,
        host.label_filter_type,
        host.label_filter_category,
        host.label_filter_currency,
        host.label_filter_date,
        host.label_filter_to,
    ):
        label.hide()

    host.lineEdit_filter_description.setPlaceholderText("Search description…")
    host.lineEdit_filter_description.setClearButtonEnabled(False)

    host.pushButton_filter = QPushButton("Filter", host.groupBox_filter)
    host.pushButton_filter.setObjectName("pushButton_filter")
    host.pushButton_filter.setCheckable(True)
    host.pushButton_filter.setCursor(Qt.CursorShape.PointingHandCursor)
    host.pushButton_filter.setIcon(create_lucide_icon("list-filter", 16))
    host.pushButton_filter.setMinimumHeight(CONTROL_HEIGHT)

    apply_lucide_button_icon(host.pushButton_clear_filter, CLEAR_BUTTON_ICON)
    host.pushButton_clear_filter.setText("")
    host.pushButton_clear_filter.setToolTip("Clear filter")
    host.pushButton_clear_filter.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    host.pushButton_clear_filter.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)

    toolbar = QWidget(host.groupBox_filter)
    toolbar.setObjectName("transactionsFilterToolbar")
    toolbar.setSizePolicy(_FILTER_MAX_POLICY)
    toolbar_row = QHBoxLayout(toolbar)
    toolbar_row.setContentsMargins(0, 0, 0, 0)
    toolbar_row.setSpacing(SPACE_S)
    toolbar_row.addWidget(host.lineEdit_filter_description, 1)
    toolbar_row.addWidget(host.pushButton_filter, 0)
    toolbar_row.addWidget(host.pushButton_clear_filter, 0)

    chips_host = QWidget(host.groupBox_filter)
    chips_host.setObjectName("transactionsFilterChips")
    chips_host.setSizePolicy(_FILTER_MAX_POLICY)
    chips_row = QHBoxLayout(chips_host)
    chips_row.setContentsMargins(0, 0, 0, 0)
    chips_row.setSpacing(SPACE_XS)
    chips_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    chips_host.hide()
    host.filter_chips_host = chips_host
    host.filter_chips_layout = chips_row

    populate_transactions_type_filter(host.comboBox_filter_type)
    _prepare_filter_combo(host.comboBox_filter_type, FILTER_ALL_TYPES, "Type")
    _prepare_filter_combo(host.comboBox_filter_category, FILTER_ALL_CATEGORIES, "Category")
    _prepare_filter_combo(host.comboBox_filter_currency, "₽ RUB", "Currency")
    for date_edit in (host.dateEdit_filter_from, host.dateEdit_filter_to):
        date_edit.setFixedWidth(date_filter_field_width(date_edit))
        date_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    host.dateEdit_filter_from.setToolTip("From date")
    host.dateEdit_filter_to.setToolTip("To date")
    host.checkBox_use_date_filter.setText("Date range")
    host.checkBox_use_date_filter.setToolTip("Filter by date range")
    host.checkBox_use_date_filter.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    advanced = QWidget(host.groupBox_filter)
    advanced.setObjectName("transactionsFilterAdvanced")
    advanced.setSizePolicy(_FILTER_MAX_POLICY)
    advanced_column = QVBoxLayout(advanced)
    advanced_column.setContentsMargins(0, SPACE_XS, 0, 0)
    advanced_column.setSpacing(SPACE_XS)

    combos_row = QHBoxLayout()
    combos_row.setContentsMargins(0, 0, 0, 0)
    combos_row.setSpacing(SPACE_S)
    combos_row.addWidget(host.comboBox_filter_type, 1)
    combos_row.addWidget(host.comboBox_filter_category, 2)
    combos_row.addWidget(host.comboBox_filter_currency, 1)

    dates_row = QHBoxLayout()
    dates_row.setContentsMargins(0, 0, 0, 0)
    dates_row.setSpacing(SPACE_S)
    dates_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    dates_row.addWidget(_inline_caption("From", host.dateEdit_filter_from, advanced), 0)
    dates_row.addWidget(_inline_caption("To", host.dateEdit_filter_to, advanced), 0)
    dates_row.addWidget(host.checkBox_use_date_filter, 0)
    dates_row.addStretch(1)

    advanced_column.addLayout(combos_row)
    advanced_column.addLayout(dates_row)
    advanced.hide()
    host.filter_advanced_panel = advanced

    shell = QWidget(host.groupBox_filter)
    shell.setObjectName("transactionsFilterShell")
    shell.setSizePolicy(_FILTER_MAX_POLICY)
    shell_column = QVBoxLayout(shell)
    shell_column.setContentsMargins(0, 0, 0, 0)
    shell_column.setSpacing(SPACE_XS)
    shell_column.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinAndMaxSize)
    shell_column.addWidget(toolbar, 0)
    shell_column.addWidget(chips_host, 0)
    shell_column.addWidget(advanced, 0)
    layout.setContentsMargins(SPACE_S, SPACE_XS, SPACE_S, SPACE_XS)
    layout.setSpacing(0)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    layout.addWidget(shell, 0)

    host.groupBox_filter.setTitle("")
    host.groupBox_filter.setFlat(True)
    host.groupBox_filter.setSizePolicy(_FILTER_MAX_POLICY)
    host.groupBox_filter.setStyleSheet(
        "QGroupBox#groupBox_filter { border: none; margin-top: 0px; padding-top: 0px; background: transparent; }"
        "QGroupBox#groupBox_filter::title { height: 0px; width: 0px; padding: 0px; margin: 0px; }",
    )
    transactions_layout = host.verticalLayout_transactions
    transactions_layout.setAlignment(host.groupBox_filter, Qt.AlignmentFlag.AlignTop)
    transactions_layout.setStretch(transactions_layout.indexOf(host.groupBox_filter), 0)
    table_index = transactions_layout.indexOf(host.tableView_transactions)
    if table_index >= 0:
        transactions_layout.setStretch(table_index, 1)

    host.pushButton_filter.toggled.connect(advanced.setVisible)
```

</details>

## 🔧 Function `populate_transactions_category_filter`

```python
def populate_transactions_category_filter(combo: QComboBox, expense_categories: list[tuple[str, str, str]], income_categories: list[tuple[str, str, str]]) -> None
```

Fill the category filter with icons and optional local-name parentheses.

<details>
<summary>Code:</summary>

```python
def populate_transactions_category_filter(
    combo: QComboBox,
    expense_categories: list[tuple[str, str, str]],
    income_categories: list[tuple[str, str, str]],
) -> None:
    selected = transactions_filter_combo_value(combo)
    combo.blockSignals(True)  # noqa: FBT003
    try:
        combo.clear()
        combo.addItem(FILTER_ALL_CATEGORIES, "")
        for name, icon, name_local in expense_categories:
            combo.addItem(_category_filter_display(name, icon, name_local, income=False), name)
        for name, icon, name_local in income_categories:
            combo.addItem(_category_filter_display(name, icon, name_local, income=True), name)
        index = combo.findData(selected)
        combo.setCurrentIndex(max(index, 0))
    finally:
        combo.blockSignals(False)  # noqa: FBT003
    _prepare_filter_combo(combo, FILTER_ALL_CATEGORIES, "Category")
```

</details>

## 🔧 Function `populate_transactions_currency_filter`

```python
def populate_transactions_currency_filter(combo: QComboBox, currencies: list[list[Any]]) -> None
```

Fill the currency filter with DB symbols before each code.

<details>
<summary>Code:</summary>

```python
def populate_transactions_currency_filter(combo: QComboBox, currencies: list[list[Any]]) -> None:
    selected = transactions_filter_combo_value(combo)
    combo.blockSignals(True)  # noqa: FBT003
    try:
        combo.clear()
        combo.addItem(FILTER_ALL_CURRENCIES, "")
        longest = FILTER_ALL_CURRENCIES
        for row in currencies:
            code = str(row[1])
            symbol = str(row[3] or "").strip()
            display = f"{symbol} {code}".strip() if symbol else code
            combo.addItem(display, code)
            if len(display) > len(longest):
                longest = display
        index = combo.findData(selected)
        combo.setCurrentIndex(max(index, 0))
    finally:
        combo.blockSignals(False)  # noqa: FBT003
    _prepare_filter_combo(combo, longest, "Currency")
```

</details>

## 🔧 Function `populate_transactions_type_filter`

```python
def populate_transactions_type_filter(combo: QComboBox) -> None
```

Fill the type filter with Expense/Income Lucide icons.

<details>
<summary>Code:</summary>

```python
def populate_transactions_type_filter(combo: QComboBox) -> None:
    selected = transactions_filter_combo_value(combo)
    combo.blockSignals(True)  # noqa: FBT003
    try:
        combo.clear()
        combo.addItem(FILTER_ALL_TYPES, "")
        combo.addItem(
            create_lucide_icon(EXPENSE_LUCIDE_ICON, _FILTER_TYPE_ICON_SIZE),
            FILTER_TYPE_EXPENSE,
            FILTER_TYPE_EXPENSE,
        )
        combo.addItem(
            create_lucide_icon(INCOME_LUCIDE_ICON, _FILTER_TYPE_ICON_SIZE),
            FILTER_TYPE_INCOME,
            FILTER_TYPE_INCOME,
        )
        index = combo.findData(selected)
        combo.setCurrentIndex(max(index, 0))
    finally:
        combo.blockSignals(False)  # noqa: FBT003
    _prepare_filter_combo(combo, FILTER_ALL_TYPES, "Type")
```

</details>

## 🔧 Function `refresh_transactions_filter_chips`

```python
def refresh_transactions_filter_chips(host: Any) -> None
```

Rebuild closable chips for active advanced filters (not description search).

<details>
<summary>Code:</summary>

```python
def refresh_transactions_filter_chips(host: Any) -> None:
    layout = host.filter_chips_layout
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    chips: list[tuple[str, Any]] = []
    type_value = transactions_filter_combo_value(host.comboBox_filter_type)
    if type_value == FILTER_TYPE_EXPENSE:
        chips.append((FILTER_TYPE_EXPENSE, host.clear_transactions_type_filter))
    elif type_value == FILTER_TYPE_INCOME:
        chips.append((FILTER_TYPE_INCOME, host.clear_transactions_type_filter))
    category = transactions_filter_combo_value(host.comboBox_filter_category)
    if category:
        chips.append((host.comboBox_filter_category.currentText(), host.clear_transactions_category_filter))
    currency = transactions_filter_combo_value(host.comboBox_filter_currency)
    if currency:
        chips.append((host.comboBox_filter_currency.currentText(), host.clear_transactions_currency_filter))
    if host.checkBox_use_date_filter.isChecked():
        date_from = host.dateEdit_filter_from.date().toString("yyyy-MM-dd")
        date_to = host.dateEdit_filter_to.date().toString("yyyy-MM-dd")
        chips.append((f"{date_from} → {date_to}", host.clear_transactions_date_filter))

    for text, on_clear in chips:
        tag = FluentTag(text, host.filter_chips_host, severity=Severity.ACCENT, closable=True)
        tag.closed.connect(on_clear)
        layout.addWidget(tag)
    layout.addStretch(1)
    host.filter_chips_host.setVisible(bool(chips))
```

</details>

## 🔧 Function `selected_transactions_filter_value`

```python
def selected_transactions_filter_value(text: str) -> str
```

Return a concrete filter value, or `""` for an 'all / empty' sentinel.

<details>
<summary>Code:</summary>

```python
def selected_transactions_filter_value(text: str) -> str:
    value = text.strip()
    return "" if value in _FILTER_ALL_VALUES else value
```

</details>

## 🔧 Function `transactions_filter_combo_value`

```python
def transactions_filter_combo_value(combo: QComboBox) -> str
```

Return the stored filter value for a combo item (`itemData`), not display text.

<details>
<summary>Code:</summary>

```python
def transactions_filter_combo_value(combo: QComboBox) -> str:
    data = combo.currentData()
    if isinstance(data, str):
        return data.strip()
    if data is not None:
        text = str(data).strip()
        if text:
            return text
    return selected_transactions_filter_value(combo.currentText())
```

</details>
