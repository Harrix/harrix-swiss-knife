---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `report_generators.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_account_balances_report_data`](#-function-get_account_balances_report_data)
- [🔧 Function `get_category_analysis_report_data`](#-function-get_category_analysis_report_data)
- [🔧 Function `get_currency_analysis_report_data`](#-function-get_currency_analysis_report_data)
- [🔧 Function `get_income_vs_expenses_report_data`](#-function-get_income_vs_expenses_report_data)
- [🔧 Function `get_monthly_summary_report_data`](#-function-get_monthly_summary_report_data)

</details>

## 🔧 Function `get_account_balances_report_data`

```python
def get_account_balances_report_data(db_manager: DatabaseManager | None, currency_id: int) -> tuple[list[str], list[list[str]]]
```

Build account balances report data.

Returns:

- `tuple[list[str], list[list[str]]]`: (headers, rows). Last row is TOTAL.

<details>
<summary>Code:</summary>

```python
def get_account_balances_report_data(
    db_manager: DatabaseManager | None,
    currency_id: int,
) -> tuple[list[str], list[list[str]]]:
    if db_manager is None:
        return ["Account", "Balance"], []

    account_balances: list[tuple[str, float]] = db_manager.get_account_balances_in_currency(currency_id)
    currency_code: str = db_manager.get_default_currency()

    report_data: list[list[str]] = []
    total_balance: float = 0.0

    for account_name, balance in account_balances:
        report_data.append([account_name, f"{balance:.2f} {currency_code}"])
        total_balance += balance

    report_data.append(["TOTAL", f"{total_balance:.2f} {currency_code}"])
    return ["Account", "Balance"], report_data
```

</details>

## 🔧 Function `get_category_analysis_report_data`

```python
def get_category_analysis_report_data(db_manager: DatabaseManager | None) -> tuple[list[str], list[list[str]]]
```

Build category analysis report data (last 30 days) in default currency.

Each transaction is converted via get_transaction_money_op_value to the current
system (default) currency using the rate on the transaction date, then summed by category.

Returns:

- `tuple[list[str], list[list[str]]]`: (headers, rows). Section rows have first cell "EXPENSES" or "INCOME".

<details>
<summary>Code:</summary>

```python
def get_category_analysis_report_data(
    db_manager: DatabaseManager | None,
) -> tuple[list[str], list[list[str]]]:
    if db_manager is None:
        return ["Category", "Amount", "Type"], []

    currency_code: str = db_manager.get_default_currency()
    default_currency_id: int = db_manager.get_default_currency_id()
    end_date: datetime = datetime.now(UTC).astimezone()
    start_date: datetime = end_date - timedelta(days=30)
    date_from: str = start_date.strftime("%Y-%m-%d")
    date_to: str = end_date.strftime("%Y-%m-%d")

    expense_rows: list = db_manager.get_filtered_transactions(category_type=0, date_from=date_from, date_to=date_to)
    income_rows: list = db_manager.get_filtered_transactions(category_type=1, date_from=date_from, date_to=date_to)

    expense_totals: dict[str, float] = {}
    income_totals: dict[str, float] = {}

    for row in expense_rows:
        category: str = row[3]
        amount: float = abs(get_transaction_money_op_value(row, db_manager, default_currency_id))
        expense_totals[category] = expense_totals.get(category, 0) + amount

    for row in income_rows:
        category = row[3]
        amount = get_transaction_money_op_value(row, db_manager, default_currency_id)
        income_totals[category] = income_totals.get(category, 0) + amount

    report_data: list[list[str]] = []
    if expense_totals:
        report_data.append(["EXPENSES", "", ""])
        for category, amount in sorted(expense_totals.items(), key=lambda x: x[1], reverse=True):
            report_data.append([category, f"{amount:.2f} {currency_code}", "Expense"])
    if income_totals:
        report_data.append(["INCOME", "", ""])
        for category, amount in sorted(income_totals.items(), key=lambda x: x[1], reverse=True):
            report_data.append([category, f"{amount:.2f} {currency_code}", "Income"])

    return ["Category", "Amount", "Type"], report_data
```

</details>

## 🔧 Function `get_currency_analysis_report_data`

```python
def get_currency_analysis_report_data(db_manager: DatabaseManager | None) -> tuple[list[str], list[list[str]]]
```

Build currency analysis report data.

Returns:

- `tuple[list[str], list[list[str]]]`: (headers, rows).

<details>
<summary>Code:</summary>

```python
def get_currency_analysis_report_data(
    db_manager: DatabaseManager | None,
) -> tuple[list[str], list[list[str]]]:
    if db_manager is None:
        return ["Currency", "Transaction Count", "Total Amount"], []

    currencies: list = db_manager.get_all_currencies()
    report_data: list[list[str]] = []

    for currency_row in currencies:
        currency_code: str = currency_row[1]
        transactions: list = db_manager.get_filtered_transactions(currency_code=currency_code)
        transaction_count: int = len(transactions)
        total_amount: float = sum(float(row[1]) / 100 for row in transactions)
        report_data.append([currency_code, str(transaction_count), f"{total_amount:.2f}"])

    return ["Currency", "Transaction Count", "Total Amount"], report_data
```

</details>

## 🔧 Function `get_income_vs_expenses_report_data`

```python
def get_income_vs_expenses_report_data(db_manager: DatabaseManager | None, currency_id: int) -> tuple[list[str], list[list[str]]]
```

Build income vs expenses report data.

Returns:

- `tuple[list[str], list[list[str]]]`: (headers, rows). Each row is [period, income, expenses, balance].

<details>
<summary>Code:</summary>

```python
def get_income_vs_expenses_report_data(
    db_manager: DatabaseManager | None,
    currency_id: int,
) -> tuple[list[str], list[list[str]]]:
    if db_manager is None:
        return ["Period", "Income", "Expenses", "Balance"], []

    currency_code: str = db_manager.get_default_currency()
    periods: list[tuple[str, int]] = [
        ("Today", 0),
        ("Last 7 days", 7),
        ("Last 30 days", 30),
        ("Last 90 days", 90),
        ("Last 365 days", 365),
    ]

    report_data: list[list[str]] = []

    for period_name, days in periods:
        if days == 0:
            today: str = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
            date_from = date_to = today
        else:
            end_date = datetime.now(UTC).astimezone()
            start_date = end_date - timedelta(days=days)
            date_from = start_date.strftime("%Y-%m-%d")
            date_to = end_date.strftime("%Y-%m-%d")

        income: float
        expenses: float
        income, expenses = db_manager.get_income_vs_expenses_in_currency(currency_id, date_from, date_to)
        balance: float = income - expenses
        report_data.append(
            [
                period_name,
                f"{income:.2f} {currency_code}",
                f"{expenses:.2f} {currency_code}",
                f"{balance:.2f} {currency_code}",
            ]
        )

    return ["Period", "Income", "Expenses", "Balance"], report_data
```

</details>

## 🔧 Function `get_monthly_summary_report_data`

```python
def get_monthly_summary_report_data(db_manager: DatabaseManager | None, currency_id: int) -> tuple[list[str], list[tuple[str, float, float, dict[int, float]]], list[tuple[int, str, str]], set[int]]
```

Build monthly summary report data (expenses by category per month).

Returns:

- `headers`: ["Month", "Total", "Cafe + Food", ...category display names].
- `rows`: List of (month_name, month_total, combined_cafe_food_total, {category_id: amount}).
- `expense_categories`: List of (category_id, display_name, icon).
- `combined_category_ids`: Set of category IDs that count as "Cafe + Food".

<details>
<summary>Code:</summary>

```python
def get_monthly_summary_report_data(
    db_manager: DatabaseManager | None,
    currency_id: int,
) -> tuple[
    list[str],
    list[tuple[str, float, float, dict[int, float]]],
    list[tuple[int, str, str]],
    set[int],
]:
    if db_manager is None:
        return [], [], [], set()

    _currency_code: str = db_manager.get_default_currency()
    all_categories: list = db_manager.get_all_categories()
    expense_categories: list[tuple[int, str, str]] = []
    category_name_to_id: dict[str, int] = {}

    for category in all_categories:
        cat_id, category_name, category_type, category_icon = (
            category[0],
            category[1],
            category[2],
            category[3],
        )
        if category_type == 0:
            display_name = f"{category_icon} {category_name}" if category_icon else category_name
            expense_categories.append((cat_id, display_name, category_icon or ""))
            category_name_to_id[category_name] = cat_id

    if not expense_categories:
        return ["Month"], [], [], set()

    expense_categories.sort(key=lambda x: x[1])

    end_date: datetime = datetime.now(UTC).astimezone()
    earliest_transaction_date_str = db_manager.get_earliest_transaction_date()

    if earliest_transaction_date_str:
        earliest_dt = datetime.fromisoformat(earliest_transaction_date_str).replace(tzinfo=end_date.tzinfo)
        month_cursor = earliest_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        month_cursor = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    end_month = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_data: dict[str, dict[int, float]] = {}
    month_names: list[str] = []

    def _normalize_category_tokens(name: str) -> set[str]:
        cleaned = "".join(ch if ch.isalnum() else " " for ch in name)
        return {token for token in cleaned.casefold().split() if token}

    combined_category_targets = {"cafe", "food"}
    combined_category_ids: set[int] = {
        cid for name, cid in category_name_to_id.items() if _normalize_category_tokens(name) & combined_category_targets
    }

    while month_cursor <= end_month:
        month_start = month_cursor
        months_in_year = 12
        if month_start.month == months_in_year:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

        date_from = month_start.strftime("%Y-%m-%d")
        date_to = month_end.strftime("%Y-%m-%d")
        month_name = month_start.strftime("%Y-%m")

        month_names.append(month_name)
        monthly_data[month_name] = {}

        expense_rows = db_manager.get_filtered_transactions(category_type=0, date_from=date_from, date_to=date_to)

        for row in expense_rows:
            amount_cents: int = row[1]
            category_name_from_row: str = row[3]
            currency_code_tx: str = row[4]
            transaction_date: str = row[5]

            category_id_matched = category_name_to_id.get(category_name_from_row)
            if category_id_matched is None:
                continue

            currency_info = db_manager.get_currency_by_code(currency_code_tx)
            source_currency_id: int = currency_info[0] if currency_info else currency_id
            amount: float = money_amount_in_currency(
                amount_cents, source_currency_id, db_manager, currency_id, transaction_date
            )

            if category_id_matched in monthly_data[month_name]:
                monthly_data[month_name][category_id_matched] += amount
            else:
                monthly_data[month_name][category_id_matched] = amount

        if month_start.month == months_in_year:
            month_cursor = month_start.replace(
                year=month_start.year + 1,
                month=1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        else:
            month_cursor = month_start.replace(
                month=month_start.month + 1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

    headers: list[str] = ["Month", "Total", "Cafe + Food"]
    headers.extend([cat[1] for cat in expense_categories])

    rows: list[tuple[str, float, float, dict[int, float]]] = []
    for month_name in reversed(month_names):
        month_total = sum(monthly_data[month_name].get(cid, 0.0) for cid, _name, _icon in expense_categories)
        combined_total = sum(monthly_data[month_name].get(cid, 0.0) for cid in combined_category_ids)
        rows.append((month_name, month_total, combined_total, monthly_data[month_name]))

    return headers, rows, expense_categories, combined_category_ids
```

</details>
