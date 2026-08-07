---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `balance_check_worker.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BalanceCheckResult`](#%EF%B8%8F-class-balancecheckresult)
  - [📎 Attribute `accounts_balance`](#-attribute-accounts_balance)
  - [📎 Attribute `accounting_balance`](#-attribute-accounting_balance)
  - [📎 Attribute `difference`](#-attribute-difference)
  - [📎 Attribute `accounting_balance_latest`](#-attribute-accounting_balance_latest)
  - [📎 Attribute `difference_latest`](#-attribute-difference_latest)
  - [📎 Attribute `natural_rows`](#-attribute-natural_rows)
  - [📎 Attribute `default_currency_symbol`](#-attribute-default_currency_symbol)
- [🏛️ Class `BalanceCheckWorker`](#%EF%B8%8F-class-balancecheckworker)
  - [📎 Attribute `check_completed`](#-attribute-check_completed)
  - [📎 Attribute `check_failed`](#-attribute-check_failed)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `run`](#%EF%B8%8F-method-run)

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

### 📎 Attribute `accounts_balance`

```python
accounts_balance: float
```

_No docstring provided._

### 📎 Attribute `accounting_balance`

```python
accounting_balance: float
```

_No docstring provided._

### 📎 Attribute `difference`

```python
difference: float
```

_No docstring provided._

### 📎 Attribute `accounting_balance_latest`

```python
accounting_balance_latest: float
```

_No docstring provided._

### 📎 Attribute `difference_latest`

```python
difference_latest: float
```

_No docstring provided._

### 📎 Attribute `natural_rows`

```python
natural_rows: list[dict[str, Any]]
```

_No docstring provided._

### 📎 Attribute `default_currency_symbol`

```python
default_currency_symbol: str
```

_No docstring provided._

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
            rates = db_manager.exchange_rates.preload_all_rates()
            currencies_by_code, currencies_by_id = db_manager.get_all_currencies_map()
            transaction_rows: list = db_manager.get_all_transactions()
            exchange_rows: list = db_manager.get_all_currency_exchanges()
            accounts_rows: list = db_manager.get_all_accounts()

            (
                accounting_balance,
                accounts_balance,
                difference,
                accounting_balance_latest,
                natural_rows,
            ) = compute_fast_balance_check(
                db_manager,
                transaction_rows,
                exchange_rows,
                accounts_rows,
                rates,
                currencies_by_code,
                currencies_by_id,
            )
            difference_latest = accounts_balance - accounting_balance_latest

            default_currency_code: str = db_manager.get_default_currency()
            default_currency_info = currencies_by_code.get(default_currency_code)
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

### 📎 Attribute `check_completed`

```python
check_completed: Signal = Signal(object)
```

_No docstring provided._

### 📎 Attribute `check_failed`

```python
check_failed: Signal = Signal(str)
```

_No docstring provided._

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
            rates = db_manager.exchange_rates.preload_all_rates()
            currencies_by_code, currencies_by_id = db_manager.get_all_currencies_map()
            transaction_rows: list = db_manager.get_all_transactions()
            exchange_rows: list = db_manager.get_all_currency_exchanges()
            accounts_rows: list = db_manager.get_all_accounts()

            (
                accounting_balance,
                accounts_balance,
                difference,
                accounting_balance_latest,
                natural_rows,
            ) = compute_fast_balance_check(
                db_manager,
                transaction_rows,
                exchange_rows,
                accounts_rows,
                rates,
                currencies_by_code,
                currencies_by_id,
            )
            difference_latest = accounts_balance - accounting_balance_latest

            default_currency_code: str = db_manager.get_default_currency()
            default_currency_info = currencies_by_code.get(default_currency_code)
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
