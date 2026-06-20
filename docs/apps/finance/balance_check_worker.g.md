---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `balance_check_worker.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BalanceCheckResult`](#️-class-balancecheckresult)
- [🏛️ Class `BalanceCheckWorker`](#️-class-balancecheckworker)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `run`](#️-method-run)

</details>

## 🏛️ Class `BalanceCheckResult`

```python
class BalanceCheckResult
```

Computed balance check values for the reconciliation dialog.

<details>
<summary>Code:</summary>

```python
class BalanceCheckResult:

    accounts_balance: float
    accounting_balance: float
    difference: float
    accounting_balance_latest: float
    difference_latest: float
    natural_rows: list[dict[str, Any]]
    default_currency_symbol: str
```

</details>

## 🏛️ Class `BalanceCheckWorker`

```python
class BalanceCheckWorker(QThread)
```

Worker thread that loads data and computes balance reconciliation off the UI thread.

<details>
<summary>Code:</summary>

```python
class BalanceCheckWorker(QThread):

    check_completed: Signal = Signal(object)  # BalanceCheckResult
    check_failed: Signal = Signal(str)

    def __init__(self, db_filename: str) -> None:
        """Initialize the worker with the SQLite database path.

        Args:

        - `db_filename` (`str`): Path to the finance SQLite database file.

        """
        super().__init__()
        self.db_filename = db_filename

    def run(self) -> None:
        """Load transactions and compute balance reconciliation."""
        try:
            db_manager = DatabaseManager(self.db_filename)
            transaction_rows: list = db_manager.get_all_transactions()
            exchange_rows: list = db_manager.get_all_currency_exchanges()
            accounts_rows: list = db_manager.get_all_accounts()
            accounting_balance, accounts_balance, difference = get_balance_difference(
                transaction_rows, exchange_rows, db_manager, target_currency_id=None
            )
            accounting_balance_latest = get_accounting_balance_latest_rates(
                transaction_rows, exchange_rows, db_manager, target_currency_id=None
            )
            difference_latest = accounts_balance - accounting_balance_latest
            natural_rows = get_natural_currency_reconciliation(
                transaction_rows, exchange_rows, accounts_rows, db_manager
            )
            default_currency_code: str = db_manager.get_default_currency()
            default_currency_info = db_manager.get_currency_by_code(default_currency_code)
            symbol: str = default_currency_info[2] if default_currency_info else ""
            result = BalanceCheckResult(
                accounts_balance=accounts_balance,
                accounting_balance=accounting_balance,
                difference=difference,
                accounting_balance_latest=accounting_balance_latest,
                difference_latest=difference_latest,
                natural_rows=natural_rows,
                default_currency_symbol=symbol,
            )
            self.check_completed.emit(result)
        except Exception as e:
            self.check_failed.emit(str(e))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, db_filename: str) -> None
```

Initialize the worker with the SQLite database path.

Args:

- `db_filename` (`str`): Path to the finance SQLite database file.

<details>
<summary>Code:</summary>

```python
def __init__(self, db_filename: str) -> None:
        super().__init__()
        self.db_filename = db_filename
```

</details>

### ⚙️ Method `run`

```python
def run(self) -> None
```

Load transactions and compute balance reconciliation.

<details>
<summary>Code:</summary>

```python
def run(self) -> None:
        try:
            db_manager = DatabaseManager(self.db_filename)
            transaction_rows: list = db_manager.get_all_transactions()
            exchange_rows: list = db_manager.get_all_currency_exchanges()
            accounts_rows: list = db_manager.get_all_accounts()
            accounting_balance, accounts_balance, difference = get_balance_difference(
                transaction_rows, exchange_rows, db_manager, target_currency_id=None
            )
            accounting_balance_latest = get_accounting_balance_latest_rates(
                transaction_rows, exchange_rows, db_manager, target_currency_id=None
            )
            difference_latest = accounts_balance - accounting_balance_latest
            natural_rows = get_natural_currency_reconciliation(
                transaction_rows, exchange_rows, accounts_rows, db_manager
            )
            default_currency_code: str = db_manager.get_default_currency()
            default_currency_info = db_manager.get_currency_by_code(default_currency_code)
            symbol: str = default_currency_info[2] if default_currency_info else ""
            result = BalanceCheckResult(
                accounts_balance=accounts_balance,
                accounting_balance=accounting_balance,
                difference=difference,
                accounting_balance_latest=accounting_balance_latest,
                difference_latest=difference_latest,
                natural_rows=natural_rows,
                default_currency_symbol=symbol,
            )
            self.check_completed.emit(result)
        except Exception as e:
            self.check_failed.emit(str(e))
```

</details>
