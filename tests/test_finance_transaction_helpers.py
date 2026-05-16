"""Tests for finance transaction helper planning functions."""

from __future__ import annotations

from harrix_swiss_knife.apps.finance.transaction_helpers import (
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
