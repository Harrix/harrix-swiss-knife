"""Equivalence tests for the cached chart compute path vs the legacy DB path.

Each ``compute_*`` chart helper is run twice: once with ``ctx=None`` (the legacy
per-row DB lookups) and once with a preloaded :class:`ChartComputeContext`. The
optimization must not change results, so the two outputs must match.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager
from harrix_swiss_knife.apps.finance.transaction_helpers import (
    ChartComputeContext,
    compute_balance_series,
    compute_cumulative_compare_last_months,
    compute_cumulative_compare_last_years,
    compute_cumulative_compare_same_months,
    compute_period_flow_by_category,
    compute_period_flow_compare_last_years,
    compute_period_flow_series,
    iter_period_end_dates,
)

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps" / "finance" / "recover.sql"

DATE_FROM = "2024-01-01"
DATE_TO = "2024-12-31"


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
    db.add_transaction(500.0, "Bonus", 1, 2, "2024-07-01")

    db.add_currency_exchange(2, 1, 100.0, 9300.0, 93.0, 1.0, "2024-04-01")

    yield db
    db.close()


@pytest.fixture
def chart_ctx(finance_db: DatabaseManager) -> ChartComputeContext:
    return ChartComputeContext.load(finance_db)


def _category_names(rows: list[list[Any]], category_type: int | None = None) -> set[str]:
    return {str(row[3]) for row in rows if category_type is None or int(row[7]) == category_type}


@pytest.mark.parametrize("period", ["Days", "Months"])
def test_balance_series_matches_legacy(
    finance_db: DatabaseManager, chart_ctx: ChartComputeContext, period: str
) -> None:
    transactions = finance_db.get_all_transactions()
    exchanges = finance_db.get_all_currency_exchanges()
    period_ends = iter_period_end_dates(DATE_FROM, DATE_TO, period)

    legacy = compute_balance_series(transactions, exchanges, finance_db, period_ends, ctx=None)
    cached = compute_balance_series(transactions, exchanges, finance_db, period_ends, ctx=chart_ctx)

    assert [d for d, _ in legacy] == [d for d, _ in cached]
    for (_, legacy_value), (_, cached_value) in zip(legacy, cached, strict=True):
        assert cached_value == pytest.approx(legacy_value)


@pytest.mark.parametrize("period", ["Days", "Months"])
def test_period_flow_series_matches_legacy(
    finance_db: DatabaseManager, chart_ctx: ChartComputeContext, period: str
) -> None:
    transactions = finance_db.get_all_transactions()
    names = _category_names(transactions, category_type=0)

    legacy = compute_period_flow_series(transactions, finance_db, DATE_FROM, DATE_TO, period, names, 0, ctx=None)
    cached = compute_period_flow_series(transactions, finance_db, DATE_FROM, DATE_TO, period, names, 0, ctx=chart_ctx)

    assert [d for d, _ in legacy] == [d for d, _ in cached]
    for (_, legacy_value), (_, cached_value) in zip(legacy, cached, strict=True):
        assert cached_value == pytest.approx(legacy_value)


@pytest.mark.parametrize("period", ["Days", "Months"])
def test_period_flow_by_category_matches_legacy(
    finance_db: DatabaseManager, chart_ctx: ChartComputeContext, period: str
) -> None:
    transactions = finance_db.get_all_transactions()
    names = _category_names(transactions)

    legacy = compute_period_flow_by_category(transactions, finance_db, DATE_FROM, DATE_TO, period, names, ctx=None)
    cached = compute_period_flow_by_category(transactions, finance_db, DATE_FROM, DATE_TO, period, names, ctx=chart_ctx)

    assert set(legacy) == set(cached)
    for name in legacy:
        assert [d for d, _ in legacy[name]] == [d for d, _ in cached[name]]
        for (_, legacy_value), (_, cached_value) in zip(legacy[name], cached[name], strict=True):
            assert cached_value == pytest.approx(legacy_value)


def test_period_flow_compare_last_years_matches_legacy(
    finance_db: DatabaseManager, chart_ctx: ChartComputeContext
) -> None:
    transactions = finance_db.get_all_transactions()
    names = _category_names(transactions, category_type=0)

    legacy, legacy_labels, legacy_colors = compute_period_flow_compare_last_years(
        transactions, finance_db, 3, names, 0, "Months", ctx=None
    )
    cached, cached_labels, cached_colors = compute_period_flow_compare_last_years(
        transactions, finance_db, 3, names, 0, "Months", ctx=chart_ctx
    )

    assert legacy_labels == cached_labels
    assert legacy_colors == cached_colors
    assert len(legacy) == len(cached)
    for legacy_year, cached_year in zip(legacy, cached, strict=True):
        assert len(legacy_year) == len(cached_year)
        for (l_idx, l_val, l_end), (c_idx, c_val, c_end) in zip(legacy_year, cached_year, strict=True):
            assert l_idx == c_idx
            assert l_end == c_end
            assert c_val == pytest.approx(l_val)


def _assert_cumulative_equal(
    legacy: tuple[list[list[tuple[int, float]]], list[str], list[str]],
    cached: tuple[list[list[tuple[int, float]]], list[str], list[str]],
) -> None:
    legacy_data, legacy_labels, legacy_colors = legacy
    cached_data, cached_labels, cached_colors = cached
    assert legacy_labels == cached_labels
    assert legacy_colors == cached_colors
    assert len(legacy_data) == len(cached_data)
    for legacy_series, cached_series in zip(legacy_data, cached_data, strict=True):
        assert len(legacy_series) == len(cached_series)
        for (l_day, l_val), (c_day, c_val) in zip(legacy_series, cached_series, strict=True):
            assert l_day == c_day
            assert c_val == pytest.approx(l_val)


def test_cumulative_compare_last_months_matches_legacy(
    finance_db: DatabaseManager, chart_ctx: ChartComputeContext
) -> None:
    transactions = finance_db.get_all_transactions()
    names = _category_names(transactions, category_type=0)
    _assert_cumulative_equal(
        compute_cumulative_compare_last_months(transactions, finance_db, 6, names, 0, ctx=None),
        compute_cumulative_compare_last_months(transactions, finance_db, 6, names, 0, ctx=chart_ctx),
    )


def test_cumulative_compare_last_years_matches_legacy(
    finance_db: DatabaseManager, chart_ctx: ChartComputeContext
) -> None:
    transactions = finance_db.get_all_transactions()
    names = _category_names(transactions, category_type=0)
    _assert_cumulative_equal(
        compute_cumulative_compare_last_years(transactions, finance_db, 3, names, 0, ctx=None),
        compute_cumulative_compare_last_years(transactions, finance_db, 3, names, 0, ctx=chart_ctx),
    )


def test_cumulative_compare_same_months_matches_legacy(
    finance_db: DatabaseManager, chart_ctx: ChartComputeContext
) -> None:
    transactions = finance_db.get_all_transactions()
    names = _category_names(transactions, category_type=0)
    _assert_cumulative_equal(
        compute_cumulative_compare_same_months(transactions, finance_db, 3, 2, names, 0, ctx=None),
        compute_cumulative_compare_same_months(transactions, finance_db, 3, 2, names, 0, ctx=chart_ctx),
    )
