"""Tests for finance transaction helper planning functions."""

from __future__ import annotations

from typing import Any, cast

from harrix_swiss_knife.apps.finance.transaction_helpers import (
    compute_balance_series,
    iter_period_buckets,
    iter_period_end_dates,
    plan_revision_expense_consolidation_for_positive_diff,
)


def _revision_row(transaction_id: int, amount_minor: int) -> list:
    return [transaction_id, amount_minor, "", "Revision Expense", "RUB", "2026-01-01", "revision", 0, "", "₽"]


def test_plan_consolidation_user_example() -> None:
    rows = [_revision_row(1, 50_00), _revision_row(2, 80_00), _revision_row(3, 60_00)]
    plan = plan_revision_expense_consolidation_for_positive_diff(rows, 100_00)
    assert plan == ([1, 2], 30_00)


def test_plan_consolidation_exact_match_no_remainder() -> None:
    rows = [_revision_row(1, 60_00), _revision_row(2, 40_00)]
    plan = plan_revision_expense_consolidation_for_positive_diff(rows, 100_00)
    assert plan == ([1, 2], 0)


def test_plan_consolidation_insufficient_sum() -> None:
    rows = [_revision_row(1, 30_00), _revision_row(2, 20_00)]
    assert plan_revision_expense_consolidation_for_positive_diff(rows, 100_00) is None


def test_plan_consolidation_non_positive_diff() -> None:
    rows = [_revision_row(1, 50_00)]
    assert plan_revision_expense_consolidation_for_positive_diff(rows, 0) is None
    assert plan_revision_expense_consolidation_for_positive_diff(rows, -10) is None


def test_iter_period_end_dates_months_caps_last_bucket() -> None:
    assert iter_period_end_dates("2024-01-15", "2024-03-10", "Months") == [
        "2024-01-31",
        "2024-02-29",
        "2024-03-10",
    ]


def test_iter_period_buckets_months() -> None:
    assert iter_period_buckets("2024-01-15", "2024-02-10", "Months") == [
        ("2024-01-15", "2024-01-31"),
        ("2024-02-01", "2024-02-10"),
    ]


class _FakeDbManager:
    def get_default_currency_id(self) -> int:
        return 1

    def get_currency_by_code(self, code: str) -> tuple[int, str, str]:
        return (1, code, code)

    def convert_from_minor_units(self, amount_minor: int, _currency_id: int) -> float:
        return amount_minor / 100

    def get_exchange_rate(self, _from_id: int, _to_id: int, _date: str | None = None) -> float:
        return 1.0


def test_compute_balance_series_single_currency() -> None:
    db = _FakeDbManager()
    transactions = [
        [1, 100_00, "income", "Salary", "RUB", "2024-01-01", "", 1, "", "₽"],
        [2, 40_00, "expense", "Food", "RUB", "2024-01-15", "", 0, "", "₽"],
    ]
    series = compute_balance_series(transactions, [], cast("Any", db), ["2024-01-31"])
    assert series == [("2024-01-31", 60.0)]
