"""Tests for the SQL summary aggregates and the cached currency catalog."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps" / "finance" / "recover.sql"

RUB_ID = 1
USD_ID = 2


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _category_id(db: DatabaseManager, name: str) -> int:
    rows = db.get_rows("SELECT _id FROM categories WHERE name = :name", {"name": name})
    assert rows, f"Category {name!r} is missing from recover.sql"
    return int(rows[0][0])


@pytest.fixture
def finance_db(tmp_path: Path, qapp: QApplication) -> Iterator[DatabaseManager]:  # noqa: ARG001
    db_path = tmp_path / "finance.db"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))

    db = DatabaseManager(str(db_path))
    salary = _category_id(db, "Salary")
    freelance = _category_id(db, "Freelance")
    food = _category_id(db, "Food")
    cafe = _category_id(db, "Cafe")

    db.add_transaction(1000.0, "Salary", salary, RUB_ID, "2024-01-15")
    db.add_transaction(250.0, "Food", food, RUB_ID, "2024-02-10")
    db.add_transaction(40.0, "Groceries", food, RUB_ID, "2024-02-10")
    db.add_transaction(50.0, "Freelance USD", freelance, USD_ID, "2024-03-05")
    db.add_transaction(12.5, "Coffee USD", cafe, USD_ID, "2024-03-05")

    yield db
    db.close()


def _python_cumulative_by_currency(
    rows: list[list[Any]],
    db: DatabaseManager,
) -> tuple[dict[int, int], dict[int, int]]:
    """Total income and expense minors per currency with a plain loop, as an oracle."""
    income: dict[int, int] = {}
    expense: dict[int, int] = {}
    for row in rows:
        currency_info = db.get_currency_by_code(row[4])
        currency_id = currency_info[0] if currency_info else 1
        target = expense if int(row[7]) == 0 else income
        target[currency_id] = target.get(currency_id, 0) + int(row[1])
    return income, expense


def test_cumulative_aggregate_matches_python_loop(finance_db: DatabaseManager) -> None:
    rows = finance_db.get_all_transactions()
    expected_income, expected_expense = _python_cumulative_by_currency(rows, finance_db)

    income, expense = finance_db.get_cumulative_income_expense_minor_by_currency()

    assert {cid: value for cid, value in income.items() if value} == expected_income
    assert {cid: value for cid, value in expense.items() if value} == expected_expense


def test_cumulative_aggregate_known_totals(finance_db: DatabaseManager) -> None:
    income, expense = finance_db.get_cumulative_income_expense_minor_by_currency()

    assert income[RUB_ID] == 100_000
    assert expense[RUB_ID] == 29_000
    assert income[USD_ID] == 5_000
    assert expense[USD_ID] == 1_250


def test_expense_for_date_sums_only_expense_categories(finance_db: DatabaseManager) -> None:
    assert finance_db.get_expense_minor_by_currency_for_date("2024-02-10") == {RUB_ID: 29_000}
    # The same day also holds an income transaction, which must not be counted.
    assert finance_db.get_expense_minor_by_currency_for_date("2024-03-05") == {USD_ID: 1_250}
    assert finance_db.get_expense_minor_by_currency_for_date("2024-01-15") == {}
    assert finance_db.get_expense_minor_by_currency_for_date("2020-01-01") == {}


def test_distinct_transaction_tags_are_trimmed_and_sorted(finance_db: DatabaseManager) -> None:
    assert finance_db.get_distinct_transaction_tags() == []

    finance_db.execute_simple_query("UPDATE transactions SET tag = ' work ' WHERE _id = 1")
    finance_db.execute_simple_query("UPDATE transactions SET tag = 'food' WHERE _id = 2")
    finance_db.execute_simple_query("UPDATE transactions SET tag = 'work' WHERE _id = 3")
    finance_db.execute_simple_query("UPDATE transactions SET tag = '   ' WHERE _id = 4")

    assert finance_db.get_distinct_transaction_tags() == ["food", "work"]


def test_currency_lookups_are_served_from_cache(
    finance_db: DatabaseManager,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    currency_queries = 0
    original_get_rows = finance_db.get_rows

    def counting_get_rows(query_text: str, params: dict[str, Any] | None = None) -> list[list[Any]]:
        nonlocal currency_queries
        if "currencies" in query_text:
            currency_queries += 1
        return original_get_rows(query_text, params)

    finance_db.get_currency_by_code("USD")  # Warm the cache before counting.
    monkeypatch.setattr(finance_db, "get_rows", counting_get_rows)

    for _ in range(5):
        assert finance_db.get_currency_by_code("USD") is not None
        assert finance_db.get_currency_by_id(RUB_ID) is not None
        assert finance_db.get_currency_subdivision(RUB_ID) == 100
        assert finance_db.get_all_currencies()
    assert currency_queries == 0

    # A write to the catalog must force exactly one reload on the next lookup.
    assert finance_db.add_currency("GBP", "Pound Sterling", "£", 100)
    assert finance_db.get_currency_by_code("GBP") is not None
    assert finance_db.get_currency_by_code("GBP") is not None
    assert currency_queries == 1


def test_currency_cache_reflects_writes(finance_db: DatabaseManager) -> None:
    assert finance_db.get_currency_by_code("GBP") is None

    assert finance_db.add_currency("GBP", "Pound Sterling", "£", 100)
    added = finance_db.get_currency_by_code("GBP")
    assert added is not None
    gbp_id = added[0]
    assert finance_db.get_currency_subdivision(gbp_id) == 100

    assert finance_db.update_currency(gbp_id, "GBP", "British Pound", "£")
    updated = finance_db.get_currency_by_id(gbp_id)
    assert updated is not None
    assert updated[1] == "British Pound"

    assert finance_db.update_currency_ticker(gbp_id, "GBPUSD=X")
    assert finance_db.get_currency_ticker(gbp_id) == "GBPUSD=X"

    assert finance_db.delete_currency(gbp_id)
    assert finance_db.get_currency_by_code("GBP") is None
