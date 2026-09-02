"""Report data generators for finance tracker (no Qt dependency)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.finance.transaction_helpers import (
    compute_average_salary_by_year,
)

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager
    from harrix_swiss_knife.apps.finance.report_build_context import ReportBuildContext

_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def get_account_balances_report_data(
    ctx: ReportBuildContext,
) -> tuple[list[str], list[list[str]]]:
    """Build account balances report data.

    Returns:

    - `tuple[list[str], list[list[str]]]`: (headers, rows). Last row is TOTAL.

    """
    db_manager = ctx.db_manager
    currency_id = ctx.currency_id
    account_balances: list[tuple[str, float]] = db_manager.get_account_balances_in_currency(currency_id)
    currency_code: str = db_manager.get_default_currency()

    report_data: list[list[str]] = []
    total_balance: float = 0.0

    for account_name, balance in account_balances:
        report_data.append([account_name, f"{balance:.2f} {currency_code}"])
        total_balance += balance

    report_data.append(["TOTAL", f"{total_balance:.2f} {currency_code}"])
    return ["Account", "Balance"], report_data


def get_average_salary_by_year_report_data(
    ctx: ReportBuildContext,
    *,
    year_start_month: int = 1,
    year_start_day: int = 1,
) -> tuple[list[str], list[list[str]]]:
    """Build average monthly and annual income by fiscal year."""
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
            f"{average_monthly:.2f} {currency_code}",
            f"{annual:.2f} {currency_code}",
        ]
        for label, average_monthly, annual in year_rows
    ]
    return ["Year", "Average Monthly Income", "Annual Income"], report_data


def get_category_analysis_report_data(
    ctx: ReportBuildContext,
) -> tuple[list[str], list[list[str]]]:
    """Build category analysis report data (last 30 days) in default currency."""
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
            report_data.append([category, f"{amount:.2f} {currency_code}", "Expense"])
    if income_totals:
        report_data.append(["INCOME", "", ""])
        for category, amount in sorted(income_totals.items(), key=lambda x: x[1], reverse=True):
            report_data.append([category, f"{amount:.2f} {currency_code}", "Income"])

    return ["Category", "Amount", "Type"], report_data


def get_currency_analysis_report_data(
    ctx: ReportBuildContext,
) -> tuple[list[str], list[list[str]]]:
    """Build currency analysis report data."""
    totals = ctx.db_manager.get_transaction_totals_by_currency()
    report_data: list[list[str]] = [
        [currency_code, str(transaction_count), f"{total_amount:.2f}"]
        for currency_code, transaction_count, total_amount in totals
    ]
    return ["Currency", "Transaction Count", "Total Amount"], report_data


def get_income_vs_expenses_report_data(
    ctx: ReportBuildContext,
) -> tuple[list[str], list[list[str]]]:
    """Build income vs expenses report data."""
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
                f"{income:.2f} {currency_code}",
                f"{expenses:.2f} {currency_code}",
                f"{balance:.2f} {currency_code}",
            ]
        )

    return ["Period", "Income", "Expenses", "Balance"], report_data


def get_monthly_income_year_delta_report_data(
    ctx: ReportBuildContext,
) -> tuple[list[str], list[list[str]]]:
    """Build monthly income compared with the same month in previous years.

    Rows are January — December. The first data column is this calendar year.
    The next columns are deltas versus last year, the year before that, and so on.

    """
    db_manager = ctx.db_manager
    currency_code: str = db_manager.get_default_currency()
    monthly = db_manager.get_monthly_income_totals(ctx.currency_id)
    today = datetime.now(UTC).astimezone()
    current_year = today.year
    current_month = today.month

    years_with_data: set[int] = set()
    for month_key in monthly:
        year_text, _sep, _rest = month_key.partition("-")
        if year_text.isdigit():
            years_with_data.add(int(year_text))
    years_with_data.add(current_year)
    previous_years = sorted((year for year in years_with_data if year < current_year), reverse=True)

    headers = ["Month", str(current_year), *[f"vs {year}" for year in previous_years]]

    def income_for(year: int, month: int) -> float:
        return monthly.get(f"{year}-{month:02d}", 0.0)

    def format_amount(amount: float) -> str:
        return f"{amount:.2f} {currency_code}"

    def format_delta(amount: float) -> str:
        sign = "+" if amount > 0 else ""
        return f"{sign}{amount:.2f} {currency_code}"

    report_data: list[list[str]] = []
    total_current = 0.0
    total_deltas = [0.0] * len(previous_years)

    for month in range(1, 13):
        month_name = _MONTH_NAMES[month - 1]
        if month > current_month:
            report_data.append([month_name, "—", *["—" for _ in previous_years]])
            continue

        current_income = income_for(current_year, month)
        total_current += current_income
        row = [month_name, format_amount(current_income)]
        for index, year in enumerate(previous_years):
            delta = current_income - income_for(year, month)
            total_deltas[index] += delta
            row.append(format_delta(delta))
        report_data.append(row)

    report_data.append(["TOTAL", format_amount(total_current), *[format_delta(delta) for delta in total_deltas]])
    return headers, report_data


def get_monthly_summary_report_data(
    ctx: ReportBuildContext,
) -> tuple[
    list[str],
    list[tuple[str, float, float, dict[int, float]]],
    list[tuple[int, str, str]],
    set[int],
]:
    """Build monthly summary report data (expenses by category per month)."""
    db_manager = ctx.db_manager
    currency_id = ctx.currency_id
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

    def _sort_key(cat: tuple[int, str, str]) -> tuple[int, str]:
        tokens = _normalize_category_tokens(cat[1])
        if "cafe" in tokens:
            return (0, cat[1])
        if "food" in tokens:
            return (1, cat[1])
        return (2, cat[1])

    expense_categories.sort(key=_sort_key)

    end_date: datetime = datetime.now(UTC).astimezone()
    month_names = _iter_month_keys_from_earliest(db_manager, end_date)
    monthly_data: dict[str, dict[int, float]] = {month: {} for month in month_names}
    sql_monthly = db_manager.get_monthly_expense_totals_by_category(currency_id)
    for month_name, category_amounts in sql_monthly.items():
        if month_name not in monthly_data:
            monthly_data[month_name] = {}
        monthly_data[month_name].update(category_amounts)

    combined_category_targets = {"cafe", "food"}
    combined_category_ids: set[int] = {
        cid for name, cid in category_name_to_id.items() if _normalize_category_tokens(name) & combined_category_targets
    }

    headers: list[str] = ["Month", "Total", "Cafe + Food"]
    headers.extend([cat[1] for cat in expense_categories])

    rows: list[tuple[str, float, float, dict[int, float]]] = []
    for month_name in reversed(month_names):
        month_total = sum(monthly_data[month_name].get(cid, 0.0) for cid, _name, _icon in expense_categories)
        combined_total = sum(monthly_data[month_name].get(cid, 0.0) for cid in combined_category_ids)
        rows.append((month_name, month_total, combined_total, monthly_data[month_name]))

    return headers, rows, expense_categories, combined_category_ids


def _iter_month_keys_from_earliest(db_manager: DatabaseManager, end_date: datetime) -> list[str]:
    """Return YYYY-MM keys from earliest transaction month through end_date month."""
    earliest_transaction_date_str = db_manager.get_earliest_transaction_date()
    if earliest_transaction_date_str:
        earliest_dt = datetime.fromisoformat(earliest_transaction_date_str).replace(tzinfo=end_date.tzinfo)
        month_cursor = earliest_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        month_cursor = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    end_month = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_names: list[str] = []
    months_in_year = 12

    while month_cursor <= end_month:
        month_names.append(month_cursor.strftime("%Y-%m"))
        if month_cursor.month == months_in_year:
            month_cursor = month_cursor.replace(
                year=month_cursor.year + 1,
                month=1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        else:
            month_cursor = month_cursor.replace(
                month=month_cursor.month + 1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
    return month_names


def _normalize_category_tokens(name: str) -> set[str]:
    cleaned = "".join(ch if ch.isalnum() else " " for ch in name)
    return {token for token in cleaned.casefold().split() if token}
