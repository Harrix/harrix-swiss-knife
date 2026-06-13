---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `transaction_helpers.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TransformTransactionDataResult`](#%EF%B8%8F-class-transformtransactiondataresult)
- [🔧 Function `calculate_daily_expenses`](#-function-calculate_daily_expenses)
- [🔧 Function `calculate_exchange_loss`](#-function-calculate_exchange_loss)
- [🔧 Function `calculate_exchange_loss_in_source_currency`](#-function-calculate_exchange_loss_in_source_currency)
- [🔧 Function `compute_balance_series`](#-function-compute_balance_series)
- [🔧 Function `compute_cumulative_compare_last_months`](#-function-compute_cumulative_compare_last_months)
- [🔧 Function `compute_cumulative_compare_last_years`](#-function-compute_cumulative_compare_last_years)
- [🔧 Function `compute_cumulative_compare_same_months`](#-function-compute_cumulative_compare_same_months)
- [🔧 Function `compute_period_flow_by_category`](#-function-compute_period_flow_by_category)
- [🔧 Function `compute_period_flow_compare_last_years`](#-function-compute_period_flow_compare_last_years)
- [🔧 Function `compute_period_flow_series`](#-function-compute_period_flow_series)
- [🔧 Function `convert_currency_amount`](#-function-convert_currency_amount)
- [🔧 Function `fiscal_period_month_labels_by_index`](#-function-fiscal_period_month_labels_by_index)
- [🔧 Function `get_accounting_balance`](#-function-get_accounting_balance)
- [🔧 Function `get_accounting_balance_latest_rates`](#-function-get_accounting_balance_latest_rates)
- [🔧 Function `get_balance_difference`](#-function-get_balance_difference)
- [🔧 Function `get_currency_exchange_fee_and_loss_signed`](#-function-get_currency_exchange_fee_and_loss_signed)
- [🔧 Function `get_natural_cumulative_income_expense_minor_by_currency`](#-function-get_natural_cumulative_income_expense_minor_by_currency)
- [🔧 Function `get_natural_currency_reconciliation`](#-function-get_natural_currency_reconciliation)
- [🔧 Function `get_natural_journal_net_minor_by_date`](#-function-get_natural_journal_net_minor_by_date)
- [🔧 Function `get_transaction_money_op_value`](#-function-get_transaction_money_op_value)
- [🔧 Function `iter_period_buckets`](#-function-iter_period_buckets)
- [🔧 Function `iter_period_end_dates`](#-function-iter_period_end_dates)
- [🔧 Function `money_amount_in_currency`](#-function-money_amount_in_currency)
- [🔧 Function `plan_revision_expense_consolidation_for_positive_diff`](#-function-plan_revision_expense_consolidation_for_positive_diff)
- [🔧 Function `transform_transaction_data`](#-function-transform_transaction_data)
- [🔧 Function `_add_calendar_years`](#-function-_add_calendar_years)
- [🔧 Function `_apply_natural_journal_event`](#-function-_apply_natural_journal_event)
- [🔧 Function `_build_cumulative_by_day_in_range`](#-function-_build_cumulative_by_day_in_range)
- [🔧 Function `_build_cumulative_by_day_of_year_in_range`](#-function-_build_cumulative_by_day_of_year_in_range)
- [🔧 Function `_fiscal_year_end`](#-function-_fiscal_year_end)
- [🔧 Function `_fiscal_year_length_days`](#-function-_fiscal_year_length_days)
- [🔧 Function `_fiscal_year_start_containing`](#-function-_fiscal_year_start_containing)
- [🔧 Function `_format_compare_year_label`](#-function-_format_compare_year_label)
- [🔧 Function `_merge_finance_events_ascending`](#-function-_merge_finance_events_ascending)
- [🔧 Function `_natural_minor_to_default_major`](#-function-_natural_minor_to_default_major)
- [🔧 Function `_parse_iso_date`](#-function-_parse_iso_date)
- [🔧 Function `_transaction_amount_in_default`](#-function-_transaction_amount_in_default)
- [🔧 Function `_transaction_matches_chart_filter`](#-function-_transaction_matches_chart_filter)

</details>

## 🏛️ Class `TransformTransactionDataResult`

```python
class TransformTransactionDataResult(NamedTuple)
```

Result of transform_transaction_data with pagination state.

<details>
<summary>Code:</summary>

```python
class TransformTransactionDataResult(NamedTuple):

    rows: list[list[Any]]
    dates_with_totals: set[str]
    date_to_color_index: dict[str, int]
    color_index: int
```

</details>

## 🔧 Function `calculate_daily_expenses`

```python
def calculate_daily_expenses(rows: list[list[Any]], db_manager: DatabaseManager | None, target_currency_id: int | None = None) -> dict[str, float]
```

Calculate daily expenses from transaction data in target or default currency.

Each expense is converted to target currency at the transaction date via
money_amount_in_currency, then summed per day. So each amount is converted
first, then summed — not summed then converted.

Args:

- `rows` (`list[list[Any]]`): Raw transaction data from database.
- `db_manager` (`DatabaseManager | None`): Database manager for currency conversion.
- `target_currency_id` (`int | None`): Target currency ID. None = project default currency.

Returns:

- `dict[str, float]`: Dictionary mapping dates to total expenses for that day (in target currency).

<details>
<summary>Code:</summary>

```python
def calculate_daily_expenses(
    rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> dict[str, float]:
    daily_expenses: dict[str, float] = {}

    for row in rows:
        amount_cents: int = row[1]
        date: str = row[5]
        category_type: int = row[7]

        # Only count expenses (category_type == 0)
        if category_type == 0:
            if db_manager:
                currency_code: str = row[4]
                currency_info = db_manager.get_currency_by_code(currency_code)
                source_currency_id: int = currency_info[0] if currency_info else 1
                amount = money_amount_in_currency(
                    amount_cents,
                    source_currency_id,
                    db_manager,
                    target_currency_id=target_currency_id,
                    date=date,
                )
            else:
                amount = float(amount_cents) / 100  # Fallback

            if date in daily_expenses:
                daily_expenses[date] += amount
            else:
                daily_expenses[date] = amount

    return daily_expenses
```

</details>

## 🔧 Function `calculate_exchange_loss`

```python
def calculate_exchange_loss(from_currency_id: int, to_currency_id: int, amount_from: float, amount_to: float, default_currency_id: int | None, db_manager: DatabaseManager | None, fee: float = 0.0, use_date: str | None = None) -> float
```

Calculate loss due to exchange rate difference.

Args:

- `from_currency_id` (`int`): Source currency ID.
- `to_currency_id` (`int`): Target currency ID.
- `amount_from` (`float`): Amount in source currency.
- `amount_to` (`float`): Amount in target currency.
- `default_currency_id` (`int | None`): Default currency ID for conversion.
- `db_manager` (`DatabaseManager | None`): Database manager for rates.
- `fee` (`float`): Exchange fee in source currency.
- `use_date` (`str | None`): Date to use for rate calculation. If None, uses today.

Returns:

- `float`: Loss amount in default currency (negative = loss, positive = profit).

<details>
<summary>Code:</summary>

```python
def calculate_exchange_loss(
    from_currency_id: int,
    to_currency_id: int,
    amount_from: float,
    amount_to: float,
    default_currency_id: int | None,
    db_manager: DatabaseManager | None,
    fee: float = 0.0,
    use_date: str | None = None,
) -> float:
    if db_manager is None:
        return 0.0
    try:
        target_date: str = (
            use_date if use_date is not None else datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        )

        rate_to_per_from: float = db_manager.get_exchange_rate(from_currency_id, to_currency_id, target_date)

        if rate_to_per_from == 1.0 and from_currency_id != to_currency_id and use_date is None:
            rate_to_per_from = db_manager.get_exchange_rate(from_currency_id, to_currency_id)

        loss_in_from_currency: float = calculate_exchange_loss_in_source_currency(
            amount_from, amount_to, rate_to_per_from, fee
        )

        if default_currency_id is not None and from_currency_id != default_currency_id:
            today: str = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
            return convert_currency_amount(
                loss_in_from_currency, from_currency_id, default_currency_id, db_manager, today
            )
        result = loss_in_from_currency
    except Exception:
        date_info = f"date {use_date}" if use_date else "today"
        logger.exception("Error calculating exchange loss for %s", date_info)
        return 0.0

    return result
```

</details>

## 🔧 Function `calculate_exchange_loss_in_source_currency`

```python
def calculate_exchange_loss_in_source_currency(amount_from: float, amount_to: float, rate_to_per_from: float, fee: float = 0.0) -> float
```

Calculate exchange loss in source currency using given rate.

Args:

- `amount_from` (`float`): Amount in source currency.
- `amount_to` (`float`): Amount in target currency.
- `rate_to_per_from` (`float`): Exchange rate (to per 1 from).
- `fee` (`float`): Exchange fee in source currency.

Returns:

- `float`: Loss amount in source currency (negative = loss, positive = profit).

<details>
<summary>Code:</summary>

```python
def calculate_exchange_loss_in_source_currency(
    amount_from: float,
    amount_to: float,
    rate_to_per_from: float,
    fee: float = 0.0,
) -> float:
    try:
        if rate_to_per_from and rate_to_per_from != 0:
            expected_from: float = amount_to / rate_to_per_from
            total_cost: float = amount_from + fee
            diff_from: float = total_cost - expected_from
            return -diff_from
    except Exception:
        logger.exception("Error calculating exchange loss in source currency")
    return 0.0
```

</details>

## 🔧 Function `compute_balance_series`

```python
def compute_balance_series(transaction_rows: list[list[Any]], exchange_rows: list[list[Any]], db_manager: DatabaseManager | None, period_end_dates: list[str]) -> list[tuple[str, float]]
```

Cumulative natural journal balance converted at each period-end rate.

<details>
<summary>Code:</summary>

```python
def compute_balance_series(
    transaction_rows: list[list[Any]],
    exchange_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    period_end_dates: list[str],
) -> list[tuple[str, float]]:
    if db_manager is None or not period_end_dates:
        return []

    events = _merge_finance_events_ascending(transaction_rows, exchange_rows)
    journal_minor: defaultdict[int, int] = defaultdict(int)
    event_idx = 0
    result: list[tuple[str, float]] = []

    for period_end in sorted(period_end_dates):
        while event_idx < len(events) and events[event_idx][0] <= period_end:
            _apply_natural_journal_event(journal_minor, events[event_idx][1], events[event_idx][2], db_manager)
            event_idx += 1
        balance = _natural_minor_to_default_major(journal_minor, db_manager, period_end)
        result.append((period_end, balance))
    return result
```

</details>

## 🔧 Function `compute_cumulative_compare_last_months`

```python
def compute_cumulative_compare_last_months(transaction_rows: list[list[Any]], db_manager: DatabaseManager | None, months_count: int, selected_category_names: set[str], category_type: int) -> tuple[list[list[tuple[int, float]]], list[str], list[str]]
```

Cumulative spending/income by day-of-month for the last N months.

<details>
<summary>Code:</summary>

```python
def compute_cumulative_compare_last_months(
    transaction_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    months_count: int,
    selected_category_names: set[str],
    category_type: int,
) -> tuple[list[list[tuple[int, float]]], list[str], list[str]]:
    if db_manager is None or not selected_category_names or months_count <= 0:
        return [], [], []

    today = datetime.now(UTC).astimezone()
    monthly_data: list[list[tuple[int, float]]] = []
    labels: list[str] = []
    colors: list[str] = []

    for i in range(months_count):
        month_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        for _ in range(i):
            if month_date.month == 1:
                month_date = month_date.replace(year=month_date.year - 1, month=12)
            else:
                month_date = month_date.replace(month=month_date.month - 1)

        month_start = month_date.replace(day=1)
        days_in_month = calendar.monthrange(month_start.year, month_start.month)[1]
        if i == 0:
            month_end = today
            max_day = min(today.day, days_in_month)
        else:
            month_end = month_start.replace(
                day=days_in_month,
                hour=23,
                minute=59,
                second=59,
                microsecond=999999,
            )
            max_day = days_in_month

        date_from = month_start.strftime("%Y-%m-%d")
        date_to = month_end.strftime("%Y-%m-%d")
        cumulative_data = _build_cumulative_by_day_in_range(
            transaction_rows,
            db_manager,
            date_from,
            date_to,
            selected_category_names,
            category_type,
            max_day,
        )
        monthly_data.append(cumulative_data)

        if i == 0:
            colors.append("red")
            labels.append(f"{month_start.strftime('%B %Y')} (Current)")
        else:
            color_index = (i - 1) % len(CHART_COMPARE_COLOR_PALETTE)
            colors.append(CHART_COMPARE_COLOR_PALETTE[color_index])
            labels.append(month_start.strftime("%B %Y"))

    return monthly_data, labels, colors
```

</details>

## 🔧 Function `compute_cumulative_compare_last_years`

```python
def compute_cumulative_compare_last_years(transaction_rows: list[list[Any]], db_manager: DatabaseManager | None, years_count: int, selected_category_names: set[str], category_type: int) -> tuple[list[list[tuple[int, float]]], list[str], list[str]]
```

Cumulative spending/income by day within each of the last N comparison years.

<details>
<summary>Code:</summary>

```python
def compute_cumulative_compare_last_years(
    transaction_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    years_count: int,
    selected_category_names: set[str],
    category_type: int,
    *,
    year_start_month: int = 1,
    year_start_day: int = 1,
) -> tuple[list[list[tuple[int, float]]], list[str], list[str]]:
    if db_manager is None or not selected_category_names or years_count <= 0:
        return [], [], []

    today = datetime.now(UTC).astimezone()
    today_date = today.date()
    calendar_year_start = year_start_month == 1 and year_start_day == 1
    current_fiscal_start = _fiscal_year_start_containing(
        today_date,
        start_month=year_start_month,
        start_day=year_start_day,
    )
    yearly_data: list[list[tuple[int, float]]] = []
    labels: list[str] = []
    colors: list[str] = []

    for i in range(years_count):
        fiscal_start = _add_calendar_years(current_fiscal_start, -i)
        fiscal_end_full = _fiscal_year_end(fiscal_start)
        period_length = _fiscal_year_length_days(fiscal_start)

        if i == 0:
            period_end = today_date
            max_day = (today_date - fiscal_start).days + 1
        else:
            period_end = fiscal_end_full
            max_day = period_length

        date_from = fiscal_start.strftime("%Y-%m-%d")
        date_to = period_end.strftime("%Y-%m-%d")
        cumulative_data = _build_cumulative_by_day_of_year_in_range(
            transaction_rows,
            db_manager,
            date_from,
            date_to,
            selected_category_names,
            category_type,
            max_day,
            period_start=fiscal_start,
        )
        yearly_data.append(cumulative_data)

        label = _format_compare_year_label(
            fiscal_start,
            fiscal_end_full,
            is_current=i == 0,
            calendar_year_start=calendar_year_start,
        )
        if i == 0:
            colors.append("red")
        else:
            color_index = (i - 1) % len(CHART_COMPARE_COLOR_PALETTE)
            colors.append(CHART_COMPARE_COLOR_PALETTE[color_index])
        labels.append(label)

    return yearly_data, labels, colors
```

</details>

## 🔧 Function `compute_cumulative_compare_same_months`

```python
def compute_cumulative_compare_same_months(transaction_rows: list[list[Any]], db_manager: DatabaseManager | None, years_count: int, selected_month: int, selected_category_names: set[str], category_type: int) -> tuple[list[list[tuple[int, float]]], list[str], list[str]]
```

Cumulative totals by day-of-month for the same month across years.

<details>
<summary>Code:</summary>

```python
def compute_cumulative_compare_same_months(
    transaction_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    years_count: int,
    selected_month: int,
    selected_category_names: set[str],
    category_type: int,
) -> tuple[list[list[tuple[int, float]]], list[str], list[str]]:
    if db_manager is None or not selected_category_names or years_count <= 0:
        return [], [], []

    today = datetime.now(UTC).astimezone()
    current_year = today.year
    yearly_data: list[list[tuple[int, float]]] = []
    labels: list[str] = []
    colors: list[str] = []

    for year_offset in range(years_count):
        year = current_year - year_offset
        month_start = datetime(year, selected_month, 1, tzinfo=UTC)
        last_day = calendar.monthrange(year, selected_month)[1]
        month_end = month_start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

        if year == current_year:
            if today.month < selected_month:
                continue
            if today.month == selected_month:
                month_end = today
                max_day = min(today.day, last_day)
            else:
                max_day = last_day
        else:
            max_day = last_day

        date_from = month_start.strftime("%Y-%m-%d")
        date_to = month_end.strftime("%Y-%m-%d")
        cumulative_data = _build_cumulative_by_day_in_range(
            transaction_rows,
            db_manager,
            date_from,
            date_to,
            selected_category_names,
            category_type,
            max_day,
        )
        if not cumulative_data:
            continue

        yearly_data.append(cumulative_data)
        label = month_start.strftime("%B %Y")
        if year == current_year:
            colors.append("red")
            labels.append(f"{label} (Current)")
        else:
            color_index = (len(yearly_data) - 2) % len(CHART_COMPARE_COLOR_PALETTE)
            colors.append(CHART_COMPARE_COLOR_PALETTE[color_index])
            labels.append(label)

    return yearly_data, labels, colors
```

</details>

## 🔧 Function `compute_period_flow_by_category`

```python
def compute_period_flow_by_category(transaction_rows: list[list[Any]], db_manager: DatabaseManager | None, date_from: str, date_to: str, period: str, selected_category_names: set[str]) -> dict[str, list[tuple[str, float]]]
```

Per-category per-period flow totals in default currency.

<details>
<summary>Code:</summary>

```python
def compute_period_flow_by_category(
    transaction_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    date_from: str,
    date_to: str,
    period: str,
    selected_category_names: set[str],
) -> dict[str, list[tuple[str, float]]]:
    if db_manager is None or not selected_category_names:
        return {}

    buckets = iter_period_buckets(date_from, date_to, period)
    series: dict[str, list[tuple[str, float]]] = {name: [] for name in sorted(selected_category_names)}

    for bucket_start, bucket_end in buckets:
        bucket_totals: defaultdict[str, float] = defaultdict(float)
        for row in transaction_rows:
            if not _transaction_matches_chart_filter(row, selected_category_names, None):
                continue
            date_str = str(row[5])
            if date_str < bucket_start or date_str > bucket_end:
                continue
            bucket_totals[str(row[3])] += _transaction_amount_in_default(row, db_manager)

        for name, values in series.items():
            values.append((bucket_end, bucket_totals.get(name, 0.0)))
    return series
```

</details>

## 🔧 Function `compute_period_flow_compare_last_years`

```python
def compute_period_flow_compare_last_years(transaction_rows: list[list[Any]], db_manager: DatabaseManager | None, years_count: int, selected_category_names: set[str], category_type: int, period: str) -> tuple[list[list[tuple[int, float, str]]], list[str], list[str]]
```

Per-period flow totals by period index within each of the last N fiscal years.

<details>
<summary>Code:</summary>

```python
def compute_period_flow_compare_last_years(
    transaction_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    years_count: int,
    selected_category_names: set[str],
    category_type: int,
    period: str,
    *,
    year_start_month: int = 1,
    year_start_day: int = 1,
) -> tuple[list[list[tuple[int, float, str]]], list[str], list[str]]:
    if db_manager is None or not selected_category_names or years_count <= 0:
        return [], [], []

    today = datetime.now(UTC).astimezone()
    today_date = today.date()
    calendar_year_start = year_start_month == 1 and year_start_day == 1
    current_fiscal_start = _fiscal_year_start_containing(
        today_date,
        start_month=year_start_month,
        start_day=year_start_day,
    )
    yearly_data: list[list[tuple[int, float, str]]] = []
    labels: list[str] = []
    colors: list[str] = []

    for i in range(years_count):
        fiscal_start = _add_calendar_years(current_fiscal_start, -i)
        fiscal_end_full = _fiscal_year_end(fiscal_start)

        period_end = today_date if i == 0 else fiscal_end_full

        date_from = fiscal_start.strftime("%Y-%m-%d")
        date_to = period_end.strftime("%Y-%m-%d")
        period_data: list[tuple[int, float, str]] = []
        for period_index, (bucket_start, bucket_end) in enumerate(
            iter_period_buckets(date_from, date_to, period),
            start=1,
        ):
            total = 0.0
            for row in transaction_rows:
                if not _transaction_matches_chart_filter(row, selected_category_names, category_type):
                    continue
                date_str = str(row[5])
                if date_str < bucket_start or date_str > bucket_end:
                    continue
                total += _transaction_amount_in_default(row, db_manager)
            period_data.append((period_index, total, bucket_end))

        yearly_data.append(period_data)

        label = _format_compare_year_label(
            fiscal_start,
            fiscal_end_full,
            is_current=i == 0,
            calendar_year_start=calendar_year_start,
        )
        if i == 0:
            colors.append("red")
        else:
            color_index = (i - 1) % len(CHART_COMPARE_COLOR_PALETTE)
            colors.append(CHART_COMPARE_COLOR_PALETTE[color_index])
        labels.append(label)

    return yearly_data, labels, colors
```

</details>

## 🔧 Function `compute_period_flow_series`

```python
def compute_period_flow_series(transaction_rows: list[list[Any]], db_manager: DatabaseManager | None, date_from: str, date_to: str, period: str, selected_category_names: set[str], category_type: int | None = None) -> list[tuple[str, float]]
```

Per-period flow totals for selected categories in default currency.

<details>
<summary>Code:</summary>

```python
def compute_period_flow_series(
    transaction_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    date_from: str,
    date_to: str,
    period: str,
    selected_category_names: set[str],
    category_type: int | None = None,
) -> list[tuple[str, float]]:
    if db_manager is None or not selected_category_names:
        return []

    result: list[tuple[str, float]] = []
    for bucket_start, bucket_end in iter_period_buckets(date_from, date_to, period):
        total = 0.0
        for row in transaction_rows:
            if not _transaction_matches_chart_filter(row, selected_category_names, category_type):
                continue
            date_str = str(row[5])
            if date_str < bucket_start or date_str > bucket_end:
                continue
            total += _transaction_amount_in_default(row, db_manager)
        result.append((bucket_end, total))
    return result
```

</details>

## 🔧 Function `convert_currency_amount`

```python
def convert_currency_amount(amount: float, from_currency_id: int, to_currency_id: int, db_manager: DatabaseManager | None, date: str | None = None) -> float
```

Convert amount from one currency to another.

Args:

- `amount` (`float`): Amount to convert.
- `from_currency_id` (`int`): Source currency ID.
- `to_currency_id` (`int`): Target currency ID.
- `db_manager` (`DatabaseManager | None`): Database manager for rate lookup.
- `date` (`str | None`): Date for rate lookup (uses today if None).

Returns:

- `float`: Converted amount in target currency.

<details>
<summary>Code:</summary>

```python
def convert_currency_amount(
    amount: float,
    from_currency_id: int,
    to_currency_id: int,
    db_manager: DatabaseManager | None,
    date: str | None = None,
) -> float:
    if db_manager is None:
        return amount
    try:
        if from_currency_id == to_currency_id:
            return amount

        if date is None:
            date = datetime.now(UTC).astimezone().strftime("%Y-%m-%d")

        rate: float = db_manager.get_exchange_rate(from_currency_id, to_currency_id, date)
        if rate == 1.0 and from_currency_id != to_currency_id:
            rate = db_manager.get_exchange_rate(from_currency_id, to_currency_id)

        if rate and rate != 0:
            return amount * rate
    except Exception:
        logger.exception("Error converting currency amount")
    return amount
```

</details>

## 🔧 Function `fiscal_period_month_labels_by_index`

```python
def fiscal_period_month_labels_by_index(date_to: date, period: str) -> dict[int, str]
```

Map 1-based period index to month name for the current fiscal year through `date_to`.

<details>
<summary>Code:</summary>

```python
def fiscal_period_month_labels_by_index(
    date_to: date,
    period: str,
    *,
    year_start_month: int = 1,
    year_start_day: int = 1,
) -> dict[int, str]:
    if period != "Months":
        return {}

    fiscal_start = _fiscal_year_start_containing(
        date_to,
        start_month=year_start_month,
        start_day=year_start_day,
    )
    buckets = iter_period_buckets(fiscal_start.isoformat(), date_to.isoformat(), period)
    return {
        index: _parse_iso_date(bucket_end).strftime("%B")
        for index, (_bucket_start, bucket_end) in enumerate(buckets, start=1)
    }
```

</details>

## 🔧 Function `get_accounting_balance`

```python
def get_accounting_balance(transaction_rows: list[list[Any]], exchange_rows: list[list[Any]], db_manager: DatabaseManager | None, target_currency_id: int | None = None) -> float
```

Total income minus total expenses in target currency (one pass over preloaded data).

All amounts are converted to target currency at the date of the transaction or
exchange. Expenses (transactions with category_type==0, positive fee, exchange
loss) count as negative; income (category_type==1, negative fee, exchange profit)
count as positive. No per-date SELECTs: pass preloaded transaction_rows and
exchange_rows (e.g. one get_filtered_transactions and one get_all_currency_exchanges).

Args:

- `transaction_rows` (`list[list[Any]]`): Raw transaction data.
- `exchange_rows` (`list[list[Any]]`): All currency exchange rows.
- `db_manager` (`DatabaseManager | None`): Database manager for conversion.
- `target_currency_id` (`int | None`): Target currency. None = project default.

Returns:

- `float`: Accounting balance (income - expenses) in target currency.

<details>
<summary>Code:</summary>

```python
def get_accounting_balance(
    transaction_rows: list[list[Any]],
    exchange_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> float:
    total: float = 0.0

    for row in transaction_rows:
        if len(row) < MIN_TRANSACTION_ROW_LENGTH:
            continue
        amount_cents: int = row[1]
        category_type: int = row[7]
        date_str: str = row[5]
        if db_manager is None:
            amount = float(amount_cents) / 100
        else:
            currency_code: str = row[4]
            currency_info = db_manager.get_currency_by_code(currency_code)
            source_currency_id: int = currency_info[0] if currency_info else 1
            amount = money_amount_in_currency(
                amount_cents,
                source_currency_id,
                db_manager,
                target_currency_id=target_currency_id,
                date=date_str,
            )
        if category_type == 0:
            total -= amount
        else:
            total += amount

    for row in exchange_rows:
        if len(row) < MIN_EXCHANGE_ROW_LENGTH:
            continue
        fee_signed: float
        loss_signed: float
        fee_signed, loss_signed = get_currency_exchange_fee_and_loss_signed(
            row, db_manager, target_currency_id=target_currency_id
        )
        total -= fee_signed
        total += loss_signed

    return total
```

</details>

## 🔧 Function `get_accounting_balance_latest_rates`

```python
def get_accounting_balance_latest_rates(transaction_rows: list[list[Any]], exchange_rows: list[list[Any]], db_manager: DatabaseManager | None, target_currency_id: int | None = None) -> float
```

Accounting balance but valuated at latest exchange rates (date=None conversions).

This is useful for debugging mismatches with accounts table, which is also converted
by "latest <= today" exchange rates.

<details>
<summary>Code:</summary>

```python
def get_accounting_balance_latest_rates(
    transaction_rows: list[list[Any]],
    exchange_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> float:
    if db_manager is None:
        return get_accounting_balance(
            transaction_rows, exchange_rows, db_manager, target_currency_id=target_currency_id
        )

    total: float = 0.0

    for row in transaction_rows:
        if len(row) < MIN_TRANSACTION_ROW_LENGTH:
            continue
        amount_cents: int = row[1]
        category_type: int = row[7]
        if db_manager is None:
            amount = float(amount_cents) / 100
        else:
            currency_code: str = row[4]
            currency_info = db_manager.get_currency_by_code(currency_code)
            source_currency_id: int = currency_info[0] if currency_info else 1
            # date=None => latest rate (valuation like accounts)
            amount = money_amount_in_currency(
                amount_cents,
                source_currency_id,
                db_manager,
                target_currency_id=target_currency_id,
                date=None,
            )
        if category_type == 0:
            total -= amount
        else:
            total += amount

    # Exchanges: valuate fee and loss in target currency using latest rates too.
    # This uses the same row math but forces conversion date=None.
    for row in exchange_rows:
        if len(row) < MIN_EXCHANGE_ROW_LENGTH:
            continue
        if db_manager is None:
            continue
        try:
            from_code: str = row[1]
            to_code: str = row[2]
            from_currency_info = db_manager.get_currency_by_code(from_code)
            to_currency_info = db_manager.get_currency_by_code(to_code)
            if not from_currency_info or not to_currency_info:
                continue
            from_currency_id: int = from_currency_info[0]
            to_currency_id: int = to_currency_info[0]
            amount_from_major: float = db_manager.convert_from_minor_units(row[3], from_currency_id)
            amount_to_major: float = db_manager.convert_from_minor_units(row[4], to_currency_id)
            fee_major: float = db_manager.convert_from_minor_units(row[6] or 0, from_currency_id)
            if target_currency_id is None:
                target_currency_id = db_manager.get_default_currency_id()
            fee_in_target: float = convert_currency_amount(
                fee_major, from_currency_id, target_currency_id, db_manager, date=None
            )
            default_currency_id: int = db_manager.get_default_currency_id()
            loss_in_default: float = calculate_exchange_loss(
                from_currency_id,
                to_currency_id,
                amount_from_major,
                amount_to_major,
                default_currency_id,
                db_manager,
                fee=fee_major,
                use_date=None,
            )
            if target_currency_id == default_currency_id:
                loss_in_target_signed: float = loss_in_default
            else:
                loss_abs: float = abs(loss_in_default)
                loss_in_target: float = convert_currency_amount(
                    loss_abs,
                    default_currency_id,
                    target_currency_id,
                    db_manager,
                    date=None,
                )
                loss_in_target_signed = loss_in_target if loss_in_default >= 0 else -loss_in_target
        except Exception:
            logger.debug(
                "Skipping exchange row in get_accounting_balance_latest_rates",
                exc_info=True,
            )
            continue
        total -= fee_in_target
        total += loss_in_target_signed

    return total
```

</details>

## 🔧 Function `get_balance_difference`

```python
def get_balance_difference(transaction_rows: list[list[Any]], exchange_rows: list[list[Any]], db_manager: DatabaseManager | None, target_currency_id: int | None = None) -> tuple[float, float, float]
```

Accounting balance, total accounts balance, and their difference (optimal: no per-date SELECTs).

Uses get_accounting_balance (income - expenses from transactions and exchanges, all
in target currency) and db_manager.get_total_accounts_balance_in_currency for
current sum of all accounts. Difference = accounts_balance - accounting_balance
(positive means accounts show more than accounting; negative means less).

Args:

- `transaction_rows` (`list[list[Any]]`): Raw transaction data (load once).
- `exchange_rows` (`list[list[Any]]`): All currency exchange rows (load once).
- `db_manager` (`DatabaseManager | None`): Database manager.
- `target_currency_id` (`int | None`): Target currency. None = project default.

Returns:

- `tuple[float, float, float]`: (accounting_balance, accounts_balance, difference).
  difference = accounts_balance - accounting_balance.

<details>
<summary>Code:</summary>

```python
def get_balance_difference(
    transaction_rows: list[list[Any]],
    exchange_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> tuple[float, float, float]:
    accounting_balance: float = get_accounting_balance(
        transaction_rows, exchange_rows, db_manager, target_currency_id=target_currency_id
    )
    accounts_balance: float = 0.0
    if db_manager is not None:
        accounts_balance = db_manager.get_total_accounts_balance_in_currency(target_currency_id)
    difference: float = accounts_balance - accounting_balance

    return (accounting_balance, accounts_balance, difference)
```

</details>

## 🔧 Function `get_currency_exchange_fee_and_loss_signed`

```python
def get_currency_exchange_fee_and_loss_signed(row: list[Any], db_manager: DatabaseManager | None, target_currency_id: int | None = None) -> tuple[float, float]
```

Return fee and loss/profit for one currency exchange row in target currency (signed).

Fee: positive = we pay (expense), negative = refund. Loss: negative = loss (expense),
positive = profit (income). Uses exchange rate at the exchange date.

Row format: same as get_all_currency_exchanges():
[ce._id, from_code, to_code, amount_from, amount_to, exchange_rate, fee, date, description].

Args:

- `row` (`list[Any]`): One currency exchange row (at least 9 elements).
- `db_manager` (`DatabaseManager | None`): Database manager for rates and default currency.
- `target_currency_id` (`int | None`): Target currency ID. None = default currency.

Returns:

- `tuple[float, float]`: (fee_signed, loss_signed) in target currency (major units).
  fee_signed: positive = expense, negative = refund. loss_signed: negative = loss, positive = profit.

<details>
<summary>Code:</summary>

```python
def get_currency_exchange_fee_and_loss_signed(
    row: list[Any],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> tuple[float, float]:
    if db_manager is None or len(row) < MIN_EXCHANGE_ROW_LENGTH:
        return (0.0, 0.0)
    try:
        from_code: str = row[1]
        to_code: str = row[2]
        exchange_date: str = row[7]

        from_currency_info = db_manager.get_currency_by_code(from_code)
        to_currency_info = db_manager.get_currency_by_code(to_code)
        if not from_currency_info or not to_currency_info:
            return (0.0, 0.0)

        from_currency_id: int = from_currency_info[0]
        to_currency_id: int = to_currency_info[0]

        amount_from_major: float = db_manager.convert_from_minor_units(row[3], from_currency_id)
        amount_to_major: float = db_manager.convert_from_minor_units(row[4], to_currency_id)
        fee_major: float = db_manager.convert_from_minor_units(row[6] or 0, from_currency_id)

        if target_currency_id is None:
            target_currency_id = db_manager.get_default_currency_id()

        fee_in_target: float = convert_currency_amount(
            fee_major, from_currency_id, target_currency_id, db_manager, exchange_date
        )

        default_currency_id: int = db_manager.get_default_currency_id()
        loss_in_default: float = calculate_exchange_loss(
            from_currency_id,
            to_currency_id,
            amount_from_major,
            amount_to_major,
            default_currency_id,
            db_manager,
            fee=fee_major,
            use_date=exchange_date,
        )
        if target_currency_id == default_currency_id:
            loss_in_target_signed: float = loss_in_default
        else:
            loss_abs: float = abs(loss_in_default)
            loss_in_target: float = convert_currency_amount(
                loss_abs,
                default_currency_id,
                target_currency_id,
                db_manager,
                exchange_date,
            )
            loss_in_target_signed = loss_in_target if loss_in_default >= 0 else -loss_in_target

    except Exception:
        logger.exception("Error computing currency exchange fee and loss (signed)")
        return (0.0, 0.0)
    else:
        return (fee_in_target, loss_in_target_signed)
```

</details>

## 🔧 Function `get_natural_cumulative_income_expense_minor_by_currency`

```python
def get_natural_cumulative_income_expense_minor_by_currency(transaction_rows: list[list[Any]], db_manager: DatabaseManager | None) -> tuple[dict[int, int], dict[int, int]]
```

Sum income (category type 1) and expense (type 0) amounts per currency in minor units.

Transactions only; same storage interpretation as `get_natural_currency_reconciliation`.

<details>
<summary>Code:</summary>

```python
def get_natural_cumulative_income_expense_minor_by_currency(
    transaction_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
) -> tuple[dict[int, int], dict[int, int]]:
    income_minor: defaultdict[int, int] = defaultdict(int)
    expense_minor: defaultdict[int, int] = defaultdict(int)
    if db_manager is None:
        return income_minor, expense_minor

    for row in transaction_rows:
        if len(row) < MIN_TRANSACTION_ROW_LENGTH:
            continue
        amount_minor = int(row[1])
        category_type = int(row[7])
        currency_info = db_manager.get_currency_by_code(row[4])
        currency_id: int = currency_info[0] if currency_info else 1
        if category_type == 0:
            expense_minor[currency_id] += amount_minor
        else:
            income_minor[currency_id] += amount_minor

    return income_minor, expense_minor
```

</details>

## 🔧 Function `get_natural_currency_reconciliation`

```python
def get_natural_currency_reconciliation(transaction_rows: list[list[Any]], exchange_rows: list[list[Any]], accounts_rows: list[list[Any]], db_manager: DatabaseManager | None) -> list[dict[str, Any]]
```

Compute per-currency journal vs account balances (minor units, no FX).

Assumes starting from zero: net journal in each currency is income minus expenses
in that currency, plus exchange legs: debit `from` by `amount_from + fee` (fee
in from-currency minor units), credit `to` by `amount_to`.

Row formats: same as `get_all_transactions`, `get_all_currency_exchanges`,
`get_all_accounts`.

Args:

- `transaction_rows` (`list[list[Any]]`): All transactions.
- `exchange_rows` (`list[list[Any]]`): All currency exchanges.
- `accounts_rows` (`list[list[Any]]`): All accounts with currency id in column 6.
- `db_manager` (`DatabaseManager | None`): For currency codes/symbols.

Returns:

- `list[dict[str, Any]]`: One dict per currency with keys `currency_id`, `code`,
  `symbol`, `journal_minor`, `accounts_minor`, `diff_minor`
  (`diff_minor = accounts_minor - journal_minor`). Sorted by `code`.

<details>
<summary>Code:</summary>

```python
def get_natural_currency_reconciliation(
    transaction_rows: list[list[Any]],
    exchange_rows: list[list[Any]],
    accounts_rows: list[list[Any]],
    db_manager: DatabaseManager | None,
) -> list[dict[str, Any]]:
    if db_manager is None:
        return []

    journal_minor: defaultdict[int, int] = defaultdict(int)

    for row in transaction_rows:
        if len(row) < MIN_TRANSACTION_ROW_LENGTH:
            continue
        amount_minor = int(row[1])
        category_type: int = row[7]
        currency_code: str = row[4]
        currency_info = db_manager.get_currency_by_code(currency_code)
        currency_id: int = currency_info[0] if currency_info else 1
        if category_type == 0:
            journal_minor[currency_id] -= amount_minor
        else:
            journal_minor[currency_id] += amount_minor

    for row in exchange_rows:
        if len(row) < MIN_EXCHANGE_ROW_LENGTH:
            continue
        from_info = db_manager.get_currency_by_code(row[1])
        to_info = db_manager.get_currency_by_code(row[2])
        if not from_info or not to_info:
            continue
        from_id: int = from_info[0]
        to_id: int = to_info[0]
        try:
            amount_from_minor = int(row[3])
            amount_to_minor = int(row[4])
            fee_minor = int(row[6] or 0)
        except (TypeError, ValueError):
            continue
        journal_minor[from_id] -= amount_from_minor + fee_minor
        journal_minor[to_id] += amount_to_minor

    accounts_minor: defaultdict[int, int] = defaultdict(int)
    for row in accounts_rows:
        if len(row) < MIN_ACCOUNTS_ROW_LENGTH:
            continue
        try:
            cid = int(row[6])
            bal = int(row[2])
        except (TypeError, ValueError):
            continue
        accounts_minor[cid] += bal

    all_ids: set[int] = set(journal_minor) | set(accounts_minor)
    result: list[dict[str, Any]] = []
    for currency_id in sorted(all_ids, key=lambda i: (db_manager.get_currency_by_id(i) or ("", "", ""))[0]):
        cur = db_manager.get_currency_by_id(currency_id)
        code: str = cur[0] if cur else f"#{currency_id}"
        symbol: str = cur[2] if cur else ""
        jm = journal_minor[currency_id]
        am = accounts_minor[currency_id]
        result.append(
            {
                "currency_id": currency_id,
                "code": code,
                "symbol": symbol,
                "journal_minor": jm,
                "accounts_minor": am,
                "diff_minor": am - jm,
            }
        )
    return result
```

</details>

## 🔧 Function `get_natural_journal_net_minor_by_date`

```python
def get_natural_journal_net_minor_by_date(transaction_rows: list[list[Any]], exchange_rows: list[list[Any]], date: str, db_manager: DatabaseManager | None) -> dict[int, int]
```

Net journal change on `date` per currency (minor units, no FX).

Uses the same rules as `get_natural_currency_reconciliation` but only rows whose
transaction or exchange date equals `date`.

<details>
<summary>Code:</summary>

```python
def get_natural_journal_net_minor_by_date(
    transaction_rows: list[list[Any]],
    exchange_rows: list[list[Any]],
    date: str,
    db_manager: DatabaseManager | None,
) -> dict[int, int]:
    journal_minor: defaultdict[int, int] = defaultdict(int)
    if db_manager is None:
        return journal_minor

    for row in transaction_rows:
        if len(row) < MIN_TRANSACTION_ROW_LENGTH:
            continue
        if row[5] != date:
            continue
        amount_minor = int(row[1])
        category_type = int(row[7])
        currency_info = db_manager.get_currency_by_code(row[4])
        currency_id: int = currency_info[0] if currency_info else 1
        if category_type == 0:
            journal_minor[currency_id] -= amount_minor
        else:
            journal_minor[currency_id] += amount_minor

    for row in exchange_rows:
        if len(row) < MIN_EXCHANGE_ROW_LENGTH:
            continue
        if row[7] != date:
            continue
        from_info = db_manager.get_currency_by_code(row[1])
        to_info = db_manager.get_currency_by_code(row[2])
        if not from_info or not to_info:
            continue
        from_id: int = from_info[0]
        to_id: int = to_info[0]
        try:
            amount_from_minor = int(row[3])
            amount_to_minor = int(row[4])
            fee_minor = int(row[6] or 0)
        except (TypeError, ValueError):
            continue
        journal_minor[from_id] -= amount_from_minor + fee_minor
        journal_minor[to_id] += amount_to_minor

    return dict(journal_minor)
```

</details>

## 🔧 Function `get_transaction_money_op_value`

```python
def get_transaction_money_op_value(row: list[Any], db_manager: DatabaseManager | None, target_currency_id: int | None = None) -> float
```

Return signed monetary operation value for one transaction row in target currency.

Expense (category type 0) is negative, income (type 1) is positive.
Uses exchange rate at transaction date. If target_currency_id is None, uses
default currency from settings.

Row format: same as get_filtered_transactions / get_all_transactions:
[t._id, t.amount, description, cat.name, c.code, t.date, t.tag, cat.type, cat.icon, c.symbol].

Args:

- `row` (`list[Any]`): One transaction row (at least 8 elements).
- `db_manager` (`DatabaseManager | None`): Database manager for rates and default currency.
- `target_currency_id` (`int | None`): Target currency ID. None = default currency.

Returns:

- `float`: Signed amount in target currency (major units).

<details>
<summary>Code:</summary>

```python
def get_transaction_money_op_value(
    row: list[Any],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> float:
    if db_manager is None or len(row) < MIN_TRANSACTION_ROW_LENGTH:
        return 0.0
    try:
        amount_minor: int = row[1]
        currency_code: str = row[4]
        transaction_date: str = row[5]
        category_type: int = row[7]

        if target_currency_id is None:
            target_currency_id = db_manager.get_default_currency_id()

        currency_info = db_manager.get_currency_by_code(currency_code)
        source_currency_id: int = currency_info[0] if currency_info else 1
        amount_major: float = db_manager.convert_from_minor_units(amount_minor, source_currency_id)
        converted: float = convert_currency_amount(
            amount_major, source_currency_id, target_currency_id, db_manager, transaction_date
        )
        sign: int = -1 if category_type == 0 else 1
        return sign * converted
    except Exception:
        logger.exception("Error computing transaction money op value")
        return 0.0
```

</details>

## 🔧 Function `iter_period_buckets`

```python
def iter_period_buckets(date_from: str, date_to: str, period: str) -> list[tuple[str, str]]
```

Return `(bucket_start, bucket_end)` pairs for each chart period.

<details>
<summary>Code:</summary>

```python
def iter_period_buckets(date_from: str, date_to: str, period: str) -> list[tuple[str, str]]:
    end_dates = iter_period_end_dates(date_from, date_to, period)
    if not end_dates:
        return []

    buckets: list[tuple[str, str]] = []
    range_start = _parse_iso_date(date_from)
    prev_end: date | None = None
    for end_str in end_dates:
        end_d = _parse_iso_date(end_str)
        bucket_start = range_start.isoformat() if prev_end is None else (prev_end + timedelta(days=1)).isoformat()
        buckets.append((bucket_start, end_str))
        prev_end = end_d
    return buckets
```

</details>

## 🔧 Function `iter_period_end_dates`

```python
def iter_period_end_dates(date_from: str, date_to: str, period: str) -> list[str]
```

Return inclusive period-end dates between `date_from` and `date_to`.

The last bucket is capped at `date_to` when the natural period end falls later.

<details>
<summary>Code:</summary>

```python
def iter_period_end_dates(date_from: str, date_to: str, period: str) -> list[str]:
    start = _parse_iso_date(date_from)
    end = _parse_iso_date(date_to)
    if start > end:
        return []

    result: list[str] = []
    if period == "Days":
        current = start
        while current <= end:
            result.append(current.isoformat())
            current += timedelta(days=1)
    elif period == "Months":
        year = start.year
        month = start.month
        while True:
            last_day = calendar.monthrange(year, month)[1]
            period_end = date(year, month, last_day)
            if period_end < start:
                if month == DECEMBER:
                    year += 1
                    month = 1
                else:
                    month += 1
                continue
            if period_end >= end:
                result.append(end.isoformat())
                break
            result.append(period_end.isoformat())
            if month == DECEMBER:
                year += 1
                month = 1
            else:
                month += 1
    elif period == "Years":
        year = start.year
        while True:
            period_end = date(year, 12, 31)
            if period_end < start:
                year += 1
                continue
            if period_end >= end:
                result.append(end.isoformat())
                break
            result.append(period_end.isoformat())
            year += 1
    return result
```

</details>

## 🔧 Function `money_amount_in_currency`

```python
def money_amount_in_currency(amount_minor: int, source_currency_id: int, db_manager: DatabaseManager | None, target_currency_id: int | None = None, date: str | None = None) -> float
```

Convert arbitrary amount from source currency to target currency.

Input amount is in minor units (e.g. kopecks, cents), as stored in transactions.
Result is in major units (e.g. rubles, euros) in target currency. Uses exchange
rate for the given date; if date is None, uses today. If target_currency_id is
None, uses project default currency.

Args:

- `amount_minor` (`int`): Amount in minor units (same as in transactions).
- `source_currency_id` (`int`): Source currency ID.
- `db_manager` (`DatabaseManager | None`): Database manager for rates and default currency.
- `target_currency_id` (`int | None`): Target currency ID. None = default currency.
- `date` (`str | None`): Date for exchange rate (YYYY-MM-DD). None = today.

Returns:

- `float`: Amount in target currency in major units.

<details>
<summary>Code:</summary>

```python
def money_amount_in_currency(
    amount_minor: int,
    source_currency_id: int,
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
    date: str | None = None,
) -> float:
    if db_manager is None:
        return 0.0
    try:
        amount_major: float = db_manager.convert_from_minor_units(amount_minor, source_currency_id)
        if target_currency_id is None:
            target_currency_id = db_manager.get_default_currency_id()
        return convert_currency_amount(amount_major, source_currency_id, target_currency_id, db_manager, date)
    except Exception:
        logger.exception("Error converting money amount to currency")
        return 0.0
```

</details>

## 🔧 Function `plan_revision_expense_consolidation_for_positive_diff`

```python
def plan_revision_expense_consolidation_for_positive_diff(revision_expense_rows: list[list[Any]], diff_minor: int) -> tuple[list[int], int] | None
```

Plan deleting recent Revision Expense rows to offset a positive accounts-journal diff.

Greedy from newest rows until cumulative amount is at least `diff_minor`.

Args:

- `revision_expense_rows` (`list[list[Any]]`): Rows newest-first (same shape as transactions).
- `diff_minor` (`int`): Positive difference in minor units (accounts minus journal).

Returns:

- `tuple[list[int], int] | None`: `(transaction_ids_to_delete, remainder_minor)` where
  `remainder_minor` is the new Revision Expense amount to insert, or `None` if coverage
  is impossible.

<details>
<summary>Code:</summary>

```python
def plan_revision_expense_consolidation_for_positive_diff(
    revision_expense_rows: list[list[Any]],
    diff_minor: int,
) -> tuple[list[int], int] | None:
    if diff_minor <= 0:
        return None

    ids_to_delete: list[int] = []
    total_minor = 0
    for row in revision_expense_rows:
        if len(row) < MIN_TRANSACTION_ROW_LENGTH:
            continue
        try:
            transaction_id = int(row[0])
            amount_minor = int(row[1])
        except (TypeError, ValueError):
            continue
        ids_to_delete.append(transaction_id)
        total_minor += amount_minor
        if total_minor >= diff_minor:
            return ids_to_delete, total_minor - diff_minor

    return None
```

</details>

## 🔧 Function `transform_transaction_data`

```python
def transform_transaction_data(rows: list[list[Any]], daily_expenses: dict[str, float], date_colors: list[Any], db_manager: DatabaseManager | None, dates_with_totals: set[str] | None = None, date_to_color_index: dict[str, int] | None = None, color_index: int = 0) -> TransformTransactionDataResult
```

Transform transaction data for display with colors and daily totals.

Args:

- `rows` (`list[list[Any]]`): Raw transaction data.
- `daily_expenses` (`dict[str, float]`): Pre-calculated daily expense totals.
- `date_colors` (`list[Any]`): List of color objects (e.g. QColor) for date-based coloring.
- `db_manager` (`DatabaseManager | None`): Database manager for currency conversion.
- `dates_with_totals` (`set[str] | None`): Dates that already have a daily total shown.
- `date_to_color_index` (`dict[str, int] | None`): Existing date-to-color mapping for pagination.
- `color_index` (`int`): Next color index when extending date_to_color_index.

Returns:

- `TransformTransactionDataResult`: Transformed rows and updated pagination state.

<details>
<summary>Code:</summary>

```python
def transform_transaction_data(
    rows: list[list[Any]],
    daily_expenses: dict[str, float],
    date_colors: list[Any],
    db_manager: DatabaseManager | None,
    dates_with_totals: set[str] | None = None,
    date_to_color_index: dict[str, int] | None = None,
    color_index: int = 0,
) -> TransformTransactionDataResult:
    transformed_data: list[list[Any]] = []
    date_to_color_index = dict(date_to_color_index or {})
    dates_with_totals: set[str] = set(dates_with_totals or set())

    for row in rows:
        transaction_id: int = row[0]
        amount_cents: int = row[1]
        description: str = row[2]
        category_name: str = row[3]
        currency_code: str = row[4]
        date: str = row[5]
        tag: str = row[6]
        category_type: int = row[7]
        icon: str = row[8]

        amount: float
        if db_manager:
            currency_info = db_manager.get_currency_by_code(currency_code)
            currency_id = currency_info[0] if currency_info else 1
            amount = db_manager.convert_from_minor_units(amount_cents, currency_id)
        else:
            amount = float(amount_cents) / 100

        if date not in date_to_color_index:
            date_to_color_index[date] = color_index % len(date_colors) if date_colors else 0
            color_index += 1

        color: Any = date_colors[date_to_color_index[date]] if date_colors else None

        display_category_name: str = category_name
        if icon:
            display_category_name = f"{icon} {category_name}"
        if category_type == 1:  # Income category
            display_category_name = f"{display_category_name} (Income)"

        is_first_of_day: bool = date not in dates_with_totals
        if is_first_of_day:
            dates_with_totals.add(date)

        daily_total: float = daily_expenses.get(date, 0.0)
        total_display: str = f"-{daily_total:.2f}" if is_first_of_day and daily_total > 0 else ""

        amount_display: str = f"-{amount:.2f}" if category_type == 0 else f"{amount:.2f}"

        transformed_row: list[Any] = [
            description,
            amount_display,
            display_category_name,
            currency_code,
            date,
            tag,
            total_display,
            transaction_id,
            color,
        ]
        transformed_data.append(transformed_row)

    return TransformTransactionDataResult(
        rows=transformed_data,
        dates_with_totals=dates_with_totals,
        date_to_color_index=date_to_color_index,
        color_index=color_index,
    )
```

</details>

## 🔧 Function `_add_calendar_years`

```python
def _add_calendar_years(d: date, years: int) -> date
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _add_calendar_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)
```

</details>

## 🔧 Function `_apply_natural_journal_event`

```python
def _apply_natural_journal_event(journal_minor: defaultdict[int, int], kind: str, row: list[Any], db_manager: DatabaseManager) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _apply_natural_journal_event(
    journal_minor: defaultdict[int, int],
    kind: str,
    row: list[Any],
    db_manager: DatabaseManager,
) -> None:
    if kind == "txn":
        amount_minor = int(row[1])
        category_type = int(row[7])
        currency_info = db_manager.get_currency_by_code(row[4])
        currency_id: int = currency_info[0] if currency_info else 1
        if category_type == 0:
            journal_minor[currency_id] -= amount_minor
        else:
            journal_minor[currency_id] += amount_minor
        return

    from_info = db_manager.get_currency_by_code(row[1])
    to_info = db_manager.get_currency_by_code(row[2])
    if not from_info or not to_info:
        return
    from_id: int = from_info[0]
    to_id: int = to_info[0]
    try:
        amount_from_minor = int(row[3])
        amount_to_minor = int(row[4])
        fee_minor = int(row[6] or 0)
    except (TypeError, ValueError):
        return
    journal_minor[from_id] -= amount_from_minor + fee_minor
    journal_minor[to_id] += amount_to_minor
```

</details>

## 🔧 Function `_build_cumulative_by_day_in_range`

```python
def _build_cumulative_by_day_in_range(transaction_rows: list[list[Any]], db_manager: DatabaseManager, date_from: str, date_to: str, selected_category_names: set[str], category_type: int, max_day: int) -> list[tuple[int, float]]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _build_cumulative_by_day_in_range(
    transaction_rows: list[list[Any]],
    db_manager: DatabaseManager,
    date_from: str,
    date_to: str,
    selected_category_names: set[str],
    category_type: int,
    max_day: int,
) -> list[tuple[int, float]]:
    cumulative_data: list[tuple[int, float]] = []
    cumulative_value = 0.0

    filtered_rows = [
        row
        for row in transaction_rows
        if _transaction_matches_chart_filter(row, selected_category_names, category_type)
        and date_from <= str(row[5]) <= date_to
    ]
    filtered_rows.sort(key=lambda row: (str(row[5]), int(row[0])))

    for row in filtered_rows:
        cumulative_value += _transaction_amount_in_default(row, db_manager)
        day_of_month = _parse_iso_date(str(row[5])).day
        cumulative_data.append((day_of_month, cumulative_value))

    if cumulative_data:
        last_day = cumulative_data[-1][0]
        last_value = cumulative_data[-1][1]
        if last_day < max_day:
            cumulative_data.append((max_day, last_value))

    return cumulative_data
```

</details>

## 🔧 Function `_build_cumulative_by_day_of_year_in_range`

```python
def _build_cumulative_by_day_of_year_in_range(transaction_rows: list[list[Any]], db_manager: DatabaseManager, date_from: str, date_to: str, selected_category_names: set[str], category_type: int, max_day: int) -> list[tuple[int, float]]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _build_cumulative_by_day_of_year_in_range(
    transaction_rows: list[list[Any]],
    db_manager: DatabaseManager,
    date_from: str,
    date_to: str,
    selected_category_names: set[str],
    category_type: int,
    max_day: int,
    *,
    period_start: date | None = None,
) -> list[tuple[int, float]]:
    cumulative_data: list[tuple[int, float]] = []
    cumulative_value = 0.0

    filtered_rows = [
        row
        for row in transaction_rows
        if _transaction_matches_chart_filter(row, selected_category_names, category_type)
        and date_from <= str(row[5]) <= date_to
    ]
    filtered_rows.sort(key=lambda row: (str(row[5]), int(row[0])))

    for row in filtered_rows:
        cumulative_value += _transaction_amount_in_default(row, db_manager)
        tx_date = _parse_iso_date(str(row[5]))
        day_index = (tx_date - period_start).days + 1 if period_start is not None else tx_date.timetuple().tm_yday
        cumulative_data.append((day_index, cumulative_value))

    if cumulative_data:
        last_day = cumulative_data[-1][0]
        last_value = cumulative_data[-1][1]
        if last_day < max_day:
            cumulative_data.append((max_day, last_value))

    return cumulative_data
```

</details>

## 🔧 Function `_fiscal_year_end`

```python
def _fiscal_year_end(fiscal_start: date) -> date
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _fiscal_year_end(fiscal_start: date) -> date:
    return _add_calendar_years(fiscal_start, 1) - timedelta(days=1)
```

</details>

## 🔧 Function `_fiscal_year_length_days`

```python
def _fiscal_year_length_days(fiscal_start: date) -> int
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _fiscal_year_length_days(fiscal_start: date) -> int:
    return (_fiscal_year_end(fiscal_start) - fiscal_start).days + 1
```

</details>

## 🔧 Function `_fiscal_year_start_containing`

```python
def _fiscal_year_start_containing(d: date) -> date
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _fiscal_year_start_containing(
    d: date,
    *,
    start_month: int,
    start_day: int,
) -> date:
    candidate = date(d.year, start_month, start_day)
    if d < candidate:
        candidate = date(d.year - 1, start_month, start_day)
    return candidate
```

</details>

## 🔧 Function `_format_compare_year_label`

```python
def _format_compare_year_label(fiscal_start: date, fiscal_end: date) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _format_compare_year_label(
    fiscal_start: date,
    fiscal_end: date,
    *,
    is_current: bool,
    calendar_year_start: bool,
) -> str:
    label = str(fiscal_start.year) if calendar_year_start else f"{fiscal_start.year}/{fiscal_end.year % 100:02d}"
    if is_current:
        label += " (Current)"
    return label
```

</details>

## 🔧 Function `_merge_finance_events_ascending`

```python
def _merge_finance_events_ascending(transaction_rows: list[list[Any]], exchange_rows: list[list[Any]]) -> list[tuple[str, str, list[Any]]]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _merge_finance_events_ascending(
    transaction_rows: list[list[Any]],
    exchange_rows: list[list[Any]],
) -> list[tuple[str, str, list[Any]]]:
    events: list[tuple[str, str, list[Any]]] = []
    for row in transaction_rows:
        if len(row) < MIN_TRANSACTION_ROW_LENGTH:
            continue
        events.append((str(row[5]), "txn", row))
    for row in exchange_rows:
        if len(row) < MIN_EXCHANGE_ROW_LENGTH:
            continue
        events.append((str(row[7]), "exch", row))
    events.sort(key=lambda item: (item[0], 0 if item[1] == "txn" else 1))
    return events
```

</details>

## 🔧 Function `_natural_minor_to_default_major`

```python
def _natural_minor_to_default_major(journal_minor: dict[int, int], db_manager: DatabaseManager, rate_date: str, target_currency_id: int | None = None) -> float
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _natural_minor_to_default_major(
    journal_minor: dict[int, int],
    db_manager: DatabaseManager,
    rate_date: str,
    target_currency_id: int | None = None,
) -> float:
    if target_currency_id is None:
        target_currency_id = db_manager.get_default_currency_id()
    total: float = 0.0
    for currency_id, minor in journal_minor.items():
        major = db_manager.convert_from_minor_units(minor, currency_id)
        total += convert_currency_amount(major, currency_id, target_currency_id, db_manager, rate_date)
    return total
```

</details>

## 🔧 Function `_parse_iso_date`

```python
def _parse_iso_date(date_str: str) -> date
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _parse_iso_date(date_str: str) -> date:
    return date.fromisoformat(date_str)
```

</details>

## 🔧 Function `_transaction_amount_in_default`

```python
def _transaction_amount_in_default(row: list[Any], db_manager: DatabaseManager) -> float
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _transaction_amount_in_default(
    row: list[Any],
    db_manager: DatabaseManager,
) -> float:
    amount_minor = int(row[1])
    currency_info = db_manager.get_currency_by_code(row[4])
    source_currency_id: int = currency_info[0] if currency_info else 1
    return money_amount_in_currency(
        amount_minor,
        source_currency_id,
        db_manager,
        target_currency_id=None,
        date=str(row[5]),
    )
```

</details>

## 🔧 Function `_transaction_matches_chart_filter`

```python
def _transaction_matches_chart_filter(row: list[Any], selected_category_names: set[str], category_type: int | None) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _transaction_matches_chart_filter(
    row: list[Any],
    selected_category_names: set[str],
    category_type: int | None,
) -> bool:
    if len(row) < MIN_TRANSACTION_ROW_LENGTH:
        return False
    if row[3] not in selected_category_names:
        return False
    return category_type is None or int(row[7]) == category_type
```

</details>
