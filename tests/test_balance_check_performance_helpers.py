"""Tests for optimized balance check calculations."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager
from harrix_swiss_knife.apps.finance.services.exchange_rates import PreloadedExchangeRates
from harrix_swiss_knife.apps.finance.transaction_helpers import (
    compute_fast_balance_check,
    get_accounting_balance,
    get_accounting_balance_latest_rates,
    get_balance_difference,
    get_natural_currency_reconciliation,
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
    db.add_exchange_rate(3, 1.2, "2024-06-01")

    db.add_transaction(1000.0, "Salary", 1, 1, "2024-01-15")
    db.add_transaction(250.0, "Food", 2, 1, "2024-02-10")
    db.add_transaction(50.0, "Freelance USD", 1, 2, "2024-03-05")
    db.add_currency_exchange(2, 1, 10.0, 900.0, 90.0, 1.0, "2024-04-01", "USD to RUB")

    db.execute_simple_query("UPDATE accounts SET balance = :balance WHERE name = 'Cash'", {"balance": 150_000})
    db.execute_simple_query(
        "UPDATE accounts SET balance = :balance WHERE name = 'Bank Account'",
        {"balance": 50_000},
    )

    yield db
    db.close()


def test_preloaded_exchange_rates_lookup_on_date() -> None:
    rates = PreloadedExchangeRates(
        has_data=True,
        usd_currency_id=2,
        latest_rates={1: 95.0, 3: 1.2},
        dated_rates={
            1: [("2024-01-01", 90.0), ("2024-06-01", 95.0)],
            3: [("2024-01-01", 1.1), ("2024-06-01", 1.2)],
        },
    )
    assert rates.get_usd_to_currency_rate(1, "2024-02-01") == 90.0
    assert rates.get_usd_to_currency_rate(1, "2024-06-01") == 95.0
    assert rates.get_usd_to_currency_rate(1, None) == 95.0
    assert rates.get_exchange_rate(3, 1, "2024-02-01") == pytest.approx(1.1 / 90.0)


def test_get_income_vs_expenses_latest_matches_python_loop(finance_db: DatabaseManager) -> None:
    currency_id = finance_db.get_default_currency_id()
    transaction_rows = finance_db.get_all_transactions()

    tx_only_sql = finance_db.get_transaction_accounting_balance(currency_id, use_latest_rates=True)
    tx_only_python = get_accounting_balance_latest_rates(transaction_rows, [], finance_db, currency_id)
    assert tx_only_sql == pytest.approx(tx_only_python)

    tx_historical_sql = finance_db.get_transaction_accounting_balance(currency_id, use_latest_rates=False)
    tx_historical_python = get_accounting_balance(transaction_rows, [], finance_db, currency_id)
    assert tx_historical_sql == pytest.approx(tx_historical_python)


def test_compute_fast_balance_check_matches_legacy(finance_db: DatabaseManager) -> None:
    transaction_rows = finance_db.get_all_transactions()
    exchange_rows = finance_db.get_all_currency_exchanges()
    accounts_rows = finance_db.get_all_accounts()
    rates = finance_db.exchange_rates.preload_all_rates()
    currencies_by_code, currencies_by_id = finance_db.get_all_currencies_map()

    legacy_accounting, legacy_accounts, legacy_difference = get_balance_difference(
        transaction_rows,
        exchange_rows,
        finance_db,
    )
    legacy_latest = get_accounting_balance_latest_rates(transaction_rows, exchange_rows, finance_db)
    legacy_natural = get_natural_currency_reconciliation(
        transaction_rows,
        exchange_rows,
        accounts_rows,
        finance_db,
    )

    fast_accounting, fast_accounts, fast_difference, fast_latest, fast_natural = compute_fast_balance_check(
        finance_db,
        transaction_rows,
        exchange_rows,
        accounts_rows,
        rates,
        currencies_by_code,
        currencies_by_id,
    )

    assert fast_accounts == pytest.approx(legacy_accounts)
    assert fast_accounting == pytest.approx(legacy_accounting)
    assert fast_difference == pytest.approx(legacy_difference)
    assert fast_latest == pytest.approx(legacy_latest)
    assert fast_natural == legacy_natural


def test_natural_reconciliation_with_currency_maps_matches_legacy(finance_db: DatabaseManager) -> None:
    transaction_rows = finance_db.get_all_transactions()
    exchange_rows = finance_db.get_all_currency_exchanges()
    accounts_rows = finance_db.get_all_accounts()
    currencies_by_code, currencies_by_id = finance_db.get_all_currencies_map()

    legacy = get_natural_currency_reconciliation(transaction_rows, exchange_rows, accounts_rows, finance_db)
    cached = get_natural_currency_reconciliation(
        transaction_rows,
        exchange_rows,
        accounts_rows,
        finance_db,
        currencies_by_code=currencies_by_code,
        currencies_by_id=currencies_by_id,
    )
    assert cached == legacy
