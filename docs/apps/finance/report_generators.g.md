---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `report_generators.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PeriodExpenseCategory`](#%EF%B8%8F-class-periodexpensecategory)
- [🏛️ Class `PeriodExpenseTransaction`](#%EF%B8%8F-class-periodexpensetransaction)
- [🔧 Function `get_account_balances_report_data`](#-function-get_account_balances_report_data)
- [🔧 Function `get_average_salary_by_year_report_data`](#-function-get_average_salary_by_year_report_data)
- [🔧 Function `get_category_analysis_report_data`](#-function-get_category_analysis_report_data)
- [🔧 Function `get_currency_analysis_report_data`](#-function-get_currency_analysis_report_data)
- [🔧 Function `get_income_vs_expenses_report_data`](#-function-get_income_vs_expenses_report_data)
- [🔧 Function `get_month_summary_report_data`](#-function-get_month_summary_report_data)
- [🔧 Function `get_monthly_income_year_delta_report_data`](#-function-get_monthly_income_year_delta_report_data)
- [🔧 Function `get_monthly_summary_report_data`](#-function-get_monthly_summary_report_data)
- [🔧 Function `get_year_summary_report_data`](#-function-get_year_summary_report_data)
- [🔧 Function `get_yearly_summary_report_data`](#-function-get_yearly_summary_report_data)

</details>

## 🏛️ Class `PeriodExpenseCategory`

```python
class PeriodExpenseCategory
```

Expense category total with drill-down transactions for a period report.

<details>
<summary>Code:</summary>

```python
class PeriodExpenseCategory:

    category_id: int
    name: str
    icon: str
    icon_lucide: str
    total: float
    transactions: tuple[PeriodExpenseTransaction, ...]
```

</details>

## 🏛️ Class `PeriodExpenseTransaction`

```python
class PeriodExpenseTransaction
```

One expense line inside a Month/Year Summary category.

<details>
<summary>Code:</summary>

```python
class PeriodExpenseTransaction:

    date: str
    description: str
    amount: float
```

</details>

## 🔧 Function `get_account_balances_report_data`

```python
def get_account_balances_report_data(ctx: ReportBuildContext) -> tuple[list[str], list[list[str]]]
```

Build account balances report data.

Returns:

- `tuple[list[str], list[list[str]]]`: (headers, rows). Last row is TOTAL.

<details>
<summary>Code:</summary>

```python
def get_account_balances_report_data(
    ctx: ReportBuildContext,
) -> tuple[list[str], list[list[str]]]:
    db_manager = ctx.db_manager
    currency_id = ctx.currency_id
    account_balances: list[tuple[str, float]] = db_manager.get_account_balances_in_currency(currency_id)
    currency_code: str = db_manager.get_default_currency()

    report_data: list[list[str]] = []
    total_balance: float = 0.0

    for account_name, balance in account_balances:
        report_data.append([account_name, with_currency(f"{balance:.2f}", currency_code)])
        total_balance += balance

    report_data.append(["TOTAL", with_currency(f"{total_balance:.2f}", currency_code)])
    return ["Account", "Balance"], report_data
```

</details>

## 🔧 Function `get_average_salary_by_year_report_data`

```python
def get_average_salary_by_year_report_data(ctx: ReportBuildContext, *, year_start_month: int = 1, year_start_day: int = 1) -> tuple[list[str], list[list[str]]]
```

Build average monthly and annual income by fiscal year.

<details>
<summary>Code:</summary>

```python
def get_average_salary_by_year_report_data(
    ctx: ReportBuildContext,
    *,
    year_start_month: int = 1,
    year_start_day: int = 1,
) -> tuple[list[str], list[list[str]]]:
    db_manager = ctx.db_manager
    currency_code: str = db_manager.get_default_currency()
    year_rows = compute_average_salary_by_year(
        db_manager,
        ctx.currency_id,
        year_start_month=year_start_month,
        year_start_day=year_start_day,
    )
    report_data: list[list[str]] = [
        [
            label,
            with_currency(f"{average_monthly:.2f}", currency_code),
            with_currency(f"{annual:.2f}", currency_code),
        ]
        for label, average_monthly, annual in year_rows
    ]
    return ["Year", "Average Monthly Income", "Annual Income"], report_data
```

</details>

## 🔧 Function `get_category_analysis_report_data`

```python
def get_category_analysis_report_data(ctx: ReportBuildContext) -> tuple[list[str], list[list[str]]]
```

Build category analysis report data (last 30 days) in default currency.

<details>
<summary>Code:</summary>

```python
def get_category_analysis_report_data(
    ctx: ReportBuildContext,
) -> tuple[list[str], list[list[str]]]:
    db_manager = ctx.db_manager
    currency_id = ctx.currency_id
    currency_code: str = db_manager.get_default_currency()
    end_date: datetime = datetime.now(UTC).astimezone()
    start_date: datetime = end_date - timedelta(days=30)
    date_from: str = start_date.strftime("%Y-%m-%d")
    date_to: str = end_date.strftime("%Y-%m-%d")

    expense_totals = db_manager.get_category_totals_in_currency(currency_id, date_from, date_to, category_type=0)
    income_totals = db_manager.get_category_totals_in_currency(currency_id, date_from, date_to, category_type=1)

    report_data: list[list[str]] = []
    if expense_totals:
        report_data.append(["EXPENSES", "", ""])
        for category, amount in sorted(expense_totals.items(), key=lambda x: x[1], reverse=True):
            report_data.append([category, with_currency(f"{amount:.2f}", currency_code), "Expense"])
    if income_totals:
        report_data.append(["INCOME", "", ""])
        for category, amount in sorted(income_totals.items(), key=lambda x: x[1], reverse=True):
            report_data.append([category, with_currency(f"{amount:.2f}", currency_code), "Income"])

    return ["Category", "Amount", "Type"], report_data
```

</details>

## 🔧 Function `get_currency_analysis_report_data`

```python
def get_currency_analysis_report_data(ctx: ReportBuildContext) -> tuple[list[str], list[list[str]]]
```

Build currency analysis report data.

<details>
<summary>Code:</summary>

```python
def get_currency_analysis_report_data(
    ctx: ReportBuildContext,
) -> tuple[list[str], list[list[str]]]:
    totals = ctx.db_manager.get_transaction_totals_by_currency()
    report_data: list[list[str]] = [
        [currency_code, str(transaction_count), f"{total_amount:.2f}"]
        for currency_code, transaction_count, total_amount in totals
    ]
    return ["Currency", "Transaction Count", "Total Amount"], report_data
```

</details>

## 🔧 Function `get_income_vs_expenses_report_data`

```python
def get_income_vs_expenses_report_data(ctx: ReportBuildContext) -> tuple[list[str], list[list[str]]]
```

Build income vs expenses report data.

<details>
<summary>Code:</summary>

```python
def get_income_vs_expenses_report_data(
    ctx: ReportBuildContext,
) -> tuple[list[str], list[list[str]]]:
    db_manager = ctx.db_manager
    currency_id = ctx.currency_id
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

        income, expenses = db_manager.get_income_vs_expenses_in_currency(currency_id, date_from, date_to)
        balance: float = income - expenses
        report_data.append(
            [
                period_name,
                with_currency(f"{income:.2f}", currency_code),
                with_currency(f"{expenses:.2f}", currency_code),
                with_currency(f"{balance:.2f}", currency_code),
            ]
        )

    return ["Period", "Income", "Expenses", "Balance"], report_data
```

</details>

## 🔧 Function `get_month_summary_report_data`

```python
def get_month_summary_report_data(ctx: ReportBuildContext, *, year: int, month: int) -> tuple[list[str], list[PeriodExpenseCategory], float]
```

Build Month Summary: expenses by category for one calendar month, largest first.

<details>
<summary>Code:</summary>

```python
def get_month_summary_report_data(
    ctx: ReportBuildContext,
    *,
    year: int,
    month: int,
) -> tuple[list[str], list[PeriodExpenseCategory], float]:
    safe_month = max(1, min(12, month))
    last_day = calendar.monthrange(year, safe_month)[1]
    date_from = f"{year:04d}-{safe_month:02d}-01"
    date_to = f"{year:04d}-{safe_month:02d}-{last_day:02d}"
    return _get_period_expense_drilldown(ctx, date_from, date_to)
```

</details>

## 🔧 Function `get_monthly_income_year_delta_report_data`

```python
def get_monthly_income_year_delta_report_data(ctx: ReportBuildContext) -> tuple[list[str], list[list[str]]]
```

Build monthly income compared with the same month in previous years.

Rows are January — December. The first data column is this calendar year.
Before December, the next column is last year and shows only months that have
not started yet; that column is omitted from TOTAL. Later columns are deltas.
Each delta cell's second line is the amount the delta is measured against.
Months that have not started yet compare last year with older years, and those
deltas stay out of TOTAL.

<details>
<summary>Code:</summary>

```python
def get_monthly_income_year_delta_report_data(
    ctx: ReportBuildContext,
) -> tuple[list[str], list[list[str]]]:
    db_manager = ctx.db_manager
    currency_code: str = db_manager.get_default_currency()
    currency_info = db_manager.get_currency_by_code(currency_code)
    currency_symbol = currency_info[2] if currency_info and currency_info[2] else currency_code
    monthly = db_manager.get_monthly_income_totals(ctx.currency_id)
    today = _report_today()
    current_year = today.year
    current_month = today.month
    previous_year = current_year - 1
    show_remainder = current_month < _MONTHS_IN_YEAR

    years_with_data: set[int] = set()
    for month_key in monthly:
        year_text, _sep, _rest = month_key.partition("-")
        if year_text.isdigit():
            years_with_data.add(int(year_text))
    years_with_data.add(current_year)
    previous_years = sorted((year for year in years_with_data if year < current_year), reverse=True)

    headers = ["Month", str(current_year)]
    if show_remainder:
        headers.append(str(previous_year))
    headers.extend(f"vs {year}" for year in previous_years)

    def income_for(year: int, month: int) -> float:
        return monthly.get(f"{year}-{month:02d}", 0.0)

    def format_amount(amount: float) -> str:
        return with_currency(f"{amount:.2f}", currency_symbol)

    def format_delta(amount: float) -> str:
        sign = "+" if amount > 0 else ""
        return f"{sign}{with_currency(f'{amount:.2f}', currency_symbol)}"

    def delta_cell(reference: float, baseline: float) -> str:
        return f"{format_delta(reference - baseline)}\n{format_amount(baseline)}"

    report_data: list[list[str]] = []
    total_current = 0.0
    total_deltas = [0.0] * len(previous_years)
    total_baselines = [0.0] * len(previous_years)

    for month in range(1, _MONTHS_IN_YEAR + 1):
        month_name = _MONTH_NAMES[month - 1]
        elapsed = month <= current_month
        row = [month_name]
        if elapsed:
            current_income = income_for(current_year, month)
            total_current += current_income
            row.append(format_amount(current_income))
        else:
            row.append("—")
        if show_remainder:
            if elapsed:
                row.append("—")
            else:
                row.append(format_amount(income_for(previous_year, month)))
        reference = income_for(current_year, month) if elapsed else income_for(previous_year, month)
        for index, year in enumerate(previous_years):
            if not elapsed and year == previous_year:
                row.append("—")
                continue
            baseline = income_for(year, month)
            row.append(delta_cell(reference, baseline))
            if elapsed:
                total_deltas[index] += reference - baseline
                total_baselines[index] += baseline
        report_data.append(row)

    total_row = ["TOTAL", format_amount(total_current)]
    if show_remainder:
        total_row.append("—")
    total_row.extend(
        f"{format_delta(delta_sum)}\n{format_amount(baseline_sum)}"
        for delta_sum, baseline_sum in zip(total_deltas, total_baselines, strict=True)
    )
    report_data.append(total_row)
    return headers, report_data
```

</details>

## 🔧 Function `get_monthly_summary_report_data`

```python
def get_monthly_summary_report_data(ctx: ReportBuildContext) -> tuple[list[str], list[tuple[str, float, float, dict[int, float]]], list[tuple[int, str, str, str]], set[int]]
```

Build monthly summary report data (expenses by category per month).

Each expense category is `(id, name, emoji, icon_lucide)`.

<details>
<summary>Code:</summary>

```python
def get_monthly_summary_report_data(
    ctx: ReportBuildContext,
) -> tuple[
    list[str],
    list[tuple[str, float, float, dict[int, float]]],
    list[tuple[int, str, str, str]],
    set[int],
]:
    return _get_period_summary_report_data(
        ctx,
        period_header="Month",
        period_keys=_iter_month_keys_from_earliest,
        load_totals=lambda db, currency_id: db.get_monthly_expense_totals_by_category(currency_id),
    )
```

</details>

## 🔧 Function `get_year_summary_report_data`

```python
def get_year_summary_report_data(ctx: ReportBuildContext, *, year: int) -> tuple[list[str], list[PeriodExpenseCategory], float]
```

Build Year Summary: expenses by category for one calendar year, largest first.

<details>
<summary>Code:</summary>

```python
def get_year_summary_report_data(
    ctx: ReportBuildContext,
    *,
    year: int,
) -> tuple[list[str], list[PeriodExpenseCategory], float]:
    return _get_period_expense_drilldown(ctx, f"{year:04d}-01-01", f"{year:04d}-12-31")
```

</details>

## 🔧 Function `get_yearly_summary_report_data`

```python
def get_yearly_summary_report_data(ctx: ReportBuildContext) -> tuple[list[str], list[tuple[str, float, float, dict[int, float]]], list[tuple[int, str, str, str]], set[int]]
```

Build yearly summary report data (expenses by category per year).

Each expense category is `(id, name, emoji, icon_lucide)`.

<details>
<summary>Code:</summary>

```python
def get_yearly_summary_report_data(
    ctx: ReportBuildContext,
) -> tuple[
    list[str],
    list[tuple[str, float, float, dict[int, float]]],
    list[tuple[int, str, str, str]],
    set[int],
]:
    return _get_period_summary_report_data(
        ctx,
        period_header="Year",
        period_keys=_iter_year_keys_from_earliest,
        load_totals=lambda db, currency_id: db.get_yearly_expense_totals_by_category(currency_id),
    )
```

</details>
