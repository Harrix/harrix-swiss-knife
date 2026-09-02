"""Tests for optimized finance report generators."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager
from harrix_swiss_knife.apps.finance.report_build_context import ReportBuildContext
from harrix_swiss_knife.apps.finance.report_generators import (
    get_account_balances_report_data,
    get_category_analysis_report_data,
    get_currency_analysis_report_data,
    get_income_vs_expenses_report_data,
    get_monthly_income_year_delta_report_data,
    get_monthly_summary_report_data,
)
from harrix_swiss_knife.apps.finance.report_operations import REPORT_TYPES

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps" / "finance" / "recover.sql"


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture
def finance_db(tmp_path: Path, qapp: QApplication) -> Iterator[DatabaseManager]:  # noqa: ARG001
    db_path = tmp_path / "finance.db"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))

    db = DatabaseManager(str(db_path))
    db.add_exchange_rate(1, 90.0, "2024-01-01")
    db.add_exchange_rate(1, 95.0, "2024-06-01")
    db.add_exchange_rate(2, 1.0, "2024-01-01")
    db.add_exchange_rate(3, 1.1, "2024-01-01")

    db.add_transaction(1000.0, "Salary", 1, 1, "2024-01-15")
    db.add_transaction(250.0, "Food", 2, 1, "2024-02-10")
    db.add_transaction(75.0, "Transport", 3, 1, "2024-02-20")
    db.add_transaction(50.0, "Freelance USD", 1, 2, "2024-03-05")
    db.add_transaction(10.0, "Snack", 2, 3, "2024-03-12")

    yield db
    db.close()


@pytest.fixture
def report_ctx(finance_db: DatabaseManager) -> ReportBuildContext:
    currencies_by_code, currencies_by_id = finance_db.get_all_currencies_map()
    return ReportBuildContext(
        db_manager=finance_db,
        currency_id=finance_db.get_default_currency_id(),
        rates=finance_db.exchange_rates.preload_all_rates(),
        currencies_by_code=currencies_by_code,
        currencies_by_id=currencies_by_id,
    )


def _row_for_month(
    rows: list[tuple[str, float, float, dict[int, float]]],
    month: str,
) -> tuple[str, float, float, dict[int, float]]:
    match = next((row for row in rows if row[0] == month), None)
    assert match is not None, f"month {month} missing from report rows"
    return match


def test_monthly_summary_totals_per_month(report_ctx: ReportBuildContext) -> None:
    headers, rows, categories, combined_ids = get_monthly_summary_report_data(report_ctx)

    assert headers[:3] == ["Month", "Total", "Cafe + Food"]
    # Only expense categories are reported, and Cafe/Food are pinned to the front.
    assert [name for _cid, name, _icon in categories[:2]] == ["☕ Cafe", "🍔 Food"]
    assert combined_ids == {cid for cid, name, _icon in categories if name in {"☕ Cafe", "🍔 Food"}}

    # Rows run newest first and cover every month from the earliest transaction to today.
    assert rows[-1][0] == "2024-01"
    assert [row[0] for row in rows] == sorted((row[0] for row in rows), reverse=True)

    # 2024-01 holds the single 1000 RUB transaction, needing no conversion.
    january = _row_for_month(rows, "2024-01")
    assert january[1] == pytest.approx(1000.0)

    # 2024-02 holds 250 + 75, both in RUB, so no conversion applies.
    february = _row_for_month(rows, "2024-02")
    assert february[1] == pytest.approx(325.0)

    # 2024-03 holds 50 USD and 10 EUR converted into RUB at the 2024-01 rates.
    march = _row_for_month(rows, "2024-03")
    assert march[1] == pytest.approx(50.0 / 90.0 + 10.0 * 1.1 / 90.0)


def test_category_analysis_groups_recent_expenses(finance_db: DatabaseManager) -> None:
    # The report covers a rolling 30-day window, so it needs transactions dated near today.
    today = datetime.now(UTC).astimezone().date()
    recent = (today - timedelta(days=3)).strftime("%Y-%m-%d")
    finance_db.add_exchange_rate(1, 100.0, recent)
    finance_db.add_transaction(400.0, "Food", 2, 1, recent)
    finance_db.add_transaction(150.0, "Transport", 3, 1, recent)

    currencies_by_code, currencies_by_id = finance_db.get_all_currencies_map()
    ctx = ReportBuildContext(
        db_manager=finance_db,
        currency_id=finance_db.get_default_currency_id(),
        rates=finance_db.exchange_rates.preload_all_rates(),
        currencies_by_code=currencies_by_code,
        currencies_by_id=currencies_by_id,
    )

    headers, rows = get_category_analysis_report_data(ctx)

    assert headers == ["Category", "Amount", "Type"]
    assert rows[0] == ["EXPENSES", "", ""]
    # Expenses are listed largest first, grouped by category name rather than description.
    assert rows[1] == ["Beauty Services", "400.00 RUB", "Expense"]
    assert rows[2] == ["Books", "150.00 RUB", "Expense"]


def test_currency_analysis_counts_and_totals_per_currency(report_ctx: ReportBuildContext) -> None:
    headers, rows = get_currency_analysis_report_data(report_ctx)

    assert headers == ["Currency", "Transaction Count", "Total Amount"]
    # Every currency appears, including those without transactions.
    assert rows == [
        ["CNY", "0", "0.00"],
        ["EUR", "1", "10.00"],
        ["RUB", "3", "1325.00"],
        ["TRY", "0", "0.00"],
        ["USD", "1", "50.00"],
        ["VND", "0", "0.00"],
    ]


def test_account_balances_smoke(report_ctx: ReportBuildContext) -> None:
    headers, rows = get_account_balances_report_data(report_ctx)
    assert headers == ["Account", "Balance"]
    assert rows
    assert rows[-1][0] == "TOTAL"


def test_income_vs_expenses_smoke(report_ctx: ReportBuildContext) -> None:
    headers, rows = get_income_vs_expenses_report_data(report_ctx)
    assert headers == ["Period", "Income", "Expenses", "Balance"]
    assert len(rows) == 5


def _salary_category_id(finance_db: DatabaseManager) -> int:
    rows = finance_db.get_rows("SELECT _id FROM categories WHERE name = 'Salary'")
    assert rows
    return int(rows[0][0])


def test_monthly_income_year_delta_compares_same_month(finance_db: DatabaseManager) -> None:
    today = datetime.now(UTC).astimezone()
    current_year = today.year
    last_year = current_year - 1
    two_years_ago = current_year - 2
    salary_id = _salary_category_id(finance_db)
    existing_rate_dates = {
        str(row[0]) for row in finance_db.get_rows("SELECT date FROM exchange_rates WHERE _id_currency = 1")
    }
    for year in (two_years_ago, last_year, current_year):
        rate_date = f"{year}-01-01"
        if rate_date not in existing_rate_dates:
            finance_db.add_exchange_rate(1, 90.0, rate_date)
    finance_db.add_transaction(1000.0, "Salary", salary_id, 1, f"{two_years_ago}-01-15")
    finance_db.add_transaction(1200.0, "Salary", salary_id, 1, f"{last_year}-01-15")
    finance_db.add_transaction(1500.0, "Salary", salary_id, 1, f"{current_year}-01-15")

    currencies_by_code, currencies_by_id = finance_db.get_all_currencies_map()
    ctx = ReportBuildContext(
        db_manager=finance_db,
        currency_id=finance_db.get_default_currency_id(),
        rates=finance_db.exchange_rates.preload_all_rates(),
        currencies_by_code=currencies_by_code,
        currencies_by_id=currencies_by_id,
    )

    headers, rows = get_monthly_income_year_delta_report_data(ctx)
    assert headers[:3] == ["Month", str(current_year), f"vs {last_year}"]
    assert f"vs {two_years_ago}" in headers
    january = next(row for row in rows if row[0] == "January")
    assert january[1] == "1500.00 RUB"
    assert january[2] == "+300.00 RUB"
    assert january[3] == "+500.00 RUB"
    if today.month < 12:
        december = next(row for row in rows if row[0] == "December")
        assert december[1:] == ["—"] * (len(headers) - 1)
    assert rows[-1][0] == "TOTAL"
    assert rows[-1][1] == "1500.00 RUB"
    assert rows[-1][2] == "+300.00 RUB"
    assert rows[-1][3] == "+500.00 RUB"


def test_report_types_include_monthly_income_year_delta() -> None:
    names = [report_type for _icon, report_type in REPORT_TYPES]
    assert "Monthly Income vs Previous Years" in names
