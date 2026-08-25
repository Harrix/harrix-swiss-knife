"""Tests for local transaction day-total recalculation."""

from __future__ import annotations

from typing import Any

import pytest
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.transaction_day_totals import (
    TRANSACTION_COL_AMOUNT,
    TRANSACTION_COL_TOTAL_PER_DAY,
    expense_in_default_currency,
    format_transaction_day_total,
    is_income_category_display,
    parse_transaction_amount_display,
    refresh_transaction_day_totals,
)


class _FakeDbManager:
    def get_default_currency_id(self) -> int:
        return 1

    def get_currency_by_code(self, code: str) -> tuple[int, str, str]:
        if code == "USD":
            return (2, "USD", "$")
        return (1, "RUB", "₽")

    def get_exchange_rate(self, from_id: int, to_id: int, _date: str | None = None) -> float:
        if from_id == to_id:
            return 1.0
        if from_id == 2 and to_id == 1:
            return 100.0
        return 1.0


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_parse_transaction_amount_display_strips_minus_and_spaces() -> None:
    assert parse_transaction_amount_display("-12.50") == 12.5
    assert parse_transaction_amount_display("1 234.56") == 1234.56


def test_income_category_uses_display_marker() -> None:
    assert is_income_category_display("💰 Salary (Income)")
    assert not is_income_category_display("🍕 Food")


def test_income_does_not_count_toward_day_total() -> None:
    assert (
        expense_in_default_currency(
            100.0,
            is_income=True,
            currency_code="RUB",
            date="2026-08-25",
            db_manager=None,
        )
        == 0.0
    )


def test_expense_converts_to_default_currency() -> None:
    converted = expense_in_default_currency(
        2.0,
        is_income=False,
        currency_code="USD",
        date="2026-08-25",
        db_manager=_FakeDbManager(),
    )
    assert converted == 200.0


def test_format_transaction_day_total_matches_table_load() -> None:
    assert format_transaction_day_total(12.5) == "-12.50"
    assert format_transaction_day_total(0.0) == ""


def test_refresh_transaction_day_totals_updates_last_column(qapp: QApplication) -> None:  # noqa: ARG001
    model = QStandardItemModel()
    model.setColumnCount(8)
    model.appendRow(_row("Coffee", "-80.00", "☕ Cafe", "RUB", "2026-08-25", ""))
    model.appendRow(_row("Bread", "-20.00", "🍞 Food", "RUB", "2026-08-25", ""))
    model.appendRow(_row("Salary", "1000.00", "💰 Job (Income)", "RUB", "2026-08-25", ""))
    model.appendRow(_row("Taxi", "-50.00", "🚕 Transport", "RUB", "2026-08-24", "-50.00"))

    model.item(0, TRANSACTION_COL_AMOUNT).setText("-40.00")
    totals = refresh_transaction_day_totals(model, None)

    assert totals["2026-08-25"] == 60.0
    assert model.item(0, TRANSACTION_COL_TOTAL_PER_DAY).text() == "-60.00"
    assert model.item(1, TRANSACTION_COL_TOTAL_PER_DAY).text() == ""
    assert model.item(2, TRANSACTION_COL_TOTAL_PER_DAY).text() == ""
    assert model.item(3, TRANSACTION_COL_TOTAL_PER_DAY).text() == "-50.00"


def _row(
    description: str,
    amount: str,
    category: str,
    currency: str,
    date: str,
    total: str,
) -> list[Any]:
    return [
        QStandardItem(description),
        QStandardItem(""),
        QStandardItem(amount),
        QStandardItem(category),
        QStandardItem(currency),
        QStandardItem(date),
        QStandardItem(""),
        QStandardItem(total),
    ]
