"""Tests for optimized finance report generators."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager
from harrix_swiss_knife.apps.finance.report_build_context import ReportBuildContext
from harrix_swiss_knife.apps.finance.report_generators import (
    get_account_balances_report_data,
    get_category_analysis_report_data,
    get_category_analysis_report_data_legacy,
    get_currency_analysis_report_data,
    get_currency_analysis_report_data_legacy,
    get_income_vs_expenses_report_data,
    get_monthly_summary_report_data,
    get_monthly_summary_report_data_legacy,
)

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


def _monthly_rows_equal(
    left: list[tuple[str, float, float, dict[int, float]]],
    right: list[tuple[str, float, float, dict[int, float]]],
) -> None:
    assert len(left) == len(right)
    for (l_month, l_total, l_combined, l_map), (r_month, r_total, r_combined, r_map) in zip(left, right, strict=True):
        assert l_month == r_month
        assert l_total == pytest.approx(r_total)
        assert l_combined == pytest.approx(r_combined)
        assert set(l_map) == set(r_map)
        for cid in l_map:
            assert l_map[cid] == pytest.approx(r_map[cid])


def test_monthly_summary_matches_legacy(report_ctx: ReportBuildContext, finance_db: DatabaseManager) -> None:
    new_headers, new_rows, new_categories, new_combined = get_monthly_summary_report_data(report_ctx)
    old_headers, old_rows, old_categories, old_combined = get_monthly_summary_report_data_legacy(
        finance_db,
        finance_db.get_default_currency_id(),
    )
    assert new_headers == old_headers
    assert new_categories == old_categories
    assert new_combined == old_combined
    _monthly_rows_equal(new_rows, old_rows)


def test_category_analysis_matches_legacy(report_ctx: ReportBuildContext, finance_db: DatabaseManager) -> None:
    new_headers, new_rows = get_category_analysis_report_data(report_ctx)
    old_headers, old_rows = get_category_analysis_report_data_legacy(finance_db)
    assert new_headers == old_headers
    assert new_rows == old_rows


def test_currency_analysis_matches_legacy(report_ctx: ReportBuildContext, finance_db: DatabaseManager) -> None:
    new_headers, new_rows = get_currency_analysis_report_data(report_ctx)
    old_headers, old_rows = get_currency_analysis_report_data_legacy(finance_db)
    assert new_headers == old_headers
    assert new_rows == old_rows


def test_account_balances_smoke(report_ctx: ReportBuildContext) -> None:
    headers, rows = get_account_balances_report_data(report_ctx)
    assert headers == ["Account", "Balance"]
    assert rows
    assert rows[-1][0] == "TOTAL"


def test_income_vs_expenses_smoke(report_ctx: ReportBuildContext) -> None:
    headers, rows = get_income_vs_expenses_report_data(report_ctx)
    assert headers == ["Period", "Income", "Expenses", "Balance"]
    assert len(rows) == 5
