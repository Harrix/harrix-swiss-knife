---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `transaction_day_totals.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `expense_in_default_currency`](#-function-expense_in_default_currency)
- [🔧 Function `format_transaction_day_total`](#-function-format_transaction_day_total)
- [🔧 Function `format_transaction_selection_status`](#-function-format_transaction_selection_status)
- [🔧 Function `is_income_category_display`](#-function-is_income_category_display)
- [🔧 Function `parse_transaction_amount_display`](#-function-parse_transaction_amount_display)
- [🔧 Function `refresh_transaction_day_totals`](#-function-refresh_transaction_day_totals)
- [🔧 Function `signed_amount_in_default_currency`](#-function-signed_amount_in_default_currency)
- [🔧 Function `sum_transaction_rows_in_default_currency`](#-function-sum_transaction_rows_in_default_currency)

</details>

## 🔧 Function `expense_in_default_currency`

```python
def expense_in_default_currency(amount_major: float, *, is_income: bool, currency_code: str, date: str, db_manager: Any | None) -> float
```

Return an expense in the default currency, or `0` for income.

Args:

- `amount_major` (`float`): Absolute amount in the transaction currency.
- `is_income` (`bool`): Whether the row is income.
- `currency_code` (`str`): Transaction currency code.
- `date` (`str`): Transaction date `YYYY-MM-DD`.
- `db_manager` (`Any | None`): Database manager for FX conversion.

Returns:

- `float`: Expense in the default currency.

<details>
<summary>Code:</summary>

```python
def expense_in_default_currency(
    amount_major: float,
    *,
    is_income: bool,
    currency_code: str,
    date: str,
    db_manager: Any | None,
) -> float:
    if is_income or amount_major <= 0:
        return 0.0
    if db_manager is None:
        return amount_major
    currency_info = db_manager.get_currency_by_code(currency_code)
    source_id = currency_info[0] if currency_info else 1
    target_id = db_manager.get_default_currency_id()
    return convert_currency_amount(amount_major, source_id, target_id, db_manager, date)
```

</details>

## 🔧 Function `format_transaction_day_total`

```python
def format_transaction_day_total(total: float) -> str
```

Format the last-column daily expense the same way as table load.

Args:

- [`total`](../../toast_progress_notification.g.md#%EF%B8%8F-method-total-property) (`float`): Daily expense in the default currency.

Returns:

- `str`: `-{total:.2f}` when `total > 0`, otherwise empty.

<details>
<summary>Code:</summary>

```python
def format_transaction_day_total(total: float) -> str:
    return f"-{total:.2f}" if total > 0 else ""
```

</details>

## 🔧 Function `format_transaction_selection_status`

```python
def format_transaction_selection_status(count: int, total: float, currency_symbol: str) -> str
```

Format the status-bar text for selected transaction rows.

Args:

- [`count`](../../qt_flow_layout.g.md#%EF%B8%8F-method-count) (`int`): Number of selected rows.
- [`total`](../../toast_progress_notification.g.md#%EF%B8%8F-method-total-property) (`float`): Signed sum in the default currency (income +, expense -).
- `currency_symbol` (`str`): Default currency symbol.

Returns:

- `str`: Status text, or empty when nothing is selected.

<details>
<summary>Code:</summary>

```python
def format_transaction_selection_status(count: int, total: float, currency_symbol: str) -> str:
    if count <= 0:
        return ""
    rows_word = "row" if count == 1 else "rows"
    formatted = format_amount(f"{total:.2f}")
    return f"{count} {rows_word} selected · sum {formatted}{currency_symbol}"
```

</details>

## 🔧 Function `is_income_category_display`

```python
def is_income_category_display(category: str) -> bool
```

Return whether a category cell is shown as income.

<details>
<summary>Code:</summary>

```python
def is_income_category_display(category: str) -> bool:
    return _INCOME_MARKER in category
```

</details>

## 🔧 Function `parse_transaction_amount_display`

```python
def parse_transaction_amount_display(text: str) -> float
```

Parse a stored amount cell, ignoring the expense minus sign.

Args:

- `text` (`str`): Amount text from the table model.

Returns:

- `float`: Absolute major-unit amount.

<details>
<summary>Code:</summary>

```python
def parse_transaction_amount_display(text: str) -> float:
    cleaned = clean_number_text(str(text or ""))
    if not cleaned or cleaned in {"-", ".", "-."}:
        return 0.0
    try:
        return abs(float(cleaned))
    except ValueError:
        return 0.0
```

</details>

## 🔧 Function `refresh_transaction_day_totals`

```python
def refresh_transaction_day_totals(model: QStandardItemModel, db_manager: Any | None) -> dict[str, float]
```

Recalculate the Total per day column from the open transactions model.

Does not emit `dataChanged` (signals are blocked) so auto-save does not run
again.

Args:

- `model` (`QStandardItemModel`): Transactions source model.
- `db_manager` (`Any | None`): Database manager for FX conversion.

Returns:

- `dict[str, float]`: Date → daily expense in the default currency.

<details>
<summary>Code:</summary>

```python
def refresh_transaction_day_totals(model: QStandardItemModel, db_manager: Any | None) -> dict[str, float]:
    row_count = model.rowCount()
    dates: list[str] = []
    totals: dict[str, float] = {}

    for row in range(row_count):
        date_str = _item_text(model, row, TRANSACTION_COL_DATE)
        amount = parse_transaction_amount_display(_item_text(model, row, TRANSACTION_COL_AMOUNT))
        expense = expense_in_default_currency(
            amount,
            is_income=is_income_category_display(_item_text(model, row, TRANSACTION_COL_CATEGORY)),
            currency_code=_item_text(model, row, TRANSACTION_COL_CURRENCY),
            date=date_str,
            db_manager=db_manager,
        )
        dates.append(date_str)
        if date_str:
            totals[date_str] = totals.get(date_str, 0.0) + expense

    seen_dates: set[str] = set()
    model.blockSignals(True)  # noqa: FBT003
    try:
        for row in range(row_count):
            date_str = dates[row]
            is_first = bool(date_str) and date_str not in seen_dates
            if is_first:
                seen_dates.add(date_str)
            total_text = format_transaction_day_total(totals.get(date_str, 0.0)) if is_first else ""
            _set_item_text(model, row, TRANSACTION_COL_TOTAL_PER_DAY, total_text)
    finally:
        model.blockSignals(False)  # noqa: FBT003

    return totals
```

</details>

## 🔧 Function `signed_amount_in_default_currency`

```python
def signed_amount_in_default_currency(amount_major: float, *, is_income: bool, currency_code: str, date: str, db_manager: Any | None) -> float
```

Return a signed amount in the default currency (income +, expense -).

Args:

- `amount_major` (`float`): Absolute amount in the transaction currency.
- `is_income` (`bool`): Whether the row is income.
- `currency_code` (`str`): Transaction currency code.
- `date` (`str`): Transaction date `YYYY-MM-DD`.
- `db_manager` (`Any | None`): Database manager for FX conversion.

Returns:

- `float`: Signed amount in the default currency.

<details>
<summary>Code:</summary>

```python
def signed_amount_in_default_currency(
    amount_major: float,
    *,
    is_income: bool,
    currency_code: str,
    date: str,
    db_manager: Any | None,
) -> float:
    if amount_major <= 0:
        return 0.0
    if db_manager is None:
        converted = amount_major
    else:
        currency_info = db_manager.get_currency_by_code(currency_code)
        source_id = currency_info[0] if currency_info else 1
        target_id = db_manager.get_default_currency_id()
        converted = convert_currency_amount(amount_major, source_id, target_id, db_manager, date)
    return converted if is_income else -converted
```

</details>

## 🔧 Function `sum_transaction_rows_in_default_currency`

```python
def sum_transaction_rows_in_default_currency(model: QStandardItemModel, source_rows: list[int], db_manager: Any | None) -> tuple[int, float]
```

Sum selected transaction rows in the default currency.

Args:

- `model` (`QStandardItemModel`): Transactions source model.
- `source_rows` (`list[int]`): Source-model row indexes.
- `db_manager` (`Any | None`): Database manager for FX conversion.

Returns:

- `tuple[int, float]`: Selected row count and signed sum.

<details>
<summary>Code:</summary>

```python
def sum_transaction_rows_in_default_currency(
    model: QStandardItemModel,
    source_rows: list[int],
    db_manager: Any | None,
) -> tuple[int, float]:
    total = 0.0
    count = 0
    row_count = model.rowCount()
    for row in source_rows:
        if row < 0 or row >= row_count:
            continue
        amount = parse_transaction_amount_display(_item_text(model, row, TRANSACTION_COL_AMOUNT))
        total += signed_amount_in_default_currency(
            amount,
            is_income=is_income_category_display(_item_text(model, row, TRANSACTION_COL_CATEGORY)),
            currency_code=_item_text(model, row, TRANSACTION_COL_CURRENCY),
            date=_item_text(model, row, TRANSACTION_COL_DATE),
            db_manager=db_manager,
        )
        count += 1
    return count, total
```

</details>
