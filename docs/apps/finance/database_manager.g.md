---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `database_manager.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DatabaseManager`](#%EF%B8%8F-class-databasemanager)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `add_account`](#%EF%B8%8F-method-add_account)
  - [⚙️ Method `add_category`](#%EF%B8%8F-method-add_category)
  - [⚙️ Method `add_currency`](#%EF%B8%8F-method-add_currency)
  - [⚙️ Method `add_currency_exchange`](#%EF%B8%8F-method-add_currency_exchange)
  - [⚙️ Method `add_exchange_rate`](#%EF%B8%8F-method-add_exchange_rate)
  - [⚙️ Method `add_transaction`](#%EF%B8%8F-method-add_transaction)
  - [⚙️ Method `check_exchange_rate_exists`](#%EF%B8%8F-method-check_exchange_rate_exists)
  - [⚙️ Method `clean_invalid_exchange_rates`](#%EF%B8%8F-method-clean_invalid_exchange_rates)
  - [⚙️ Method `close`](#%EF%B8%8F-method-close)
  - [⚙️ Method `convert_from_minor_units`](#%EF%B8%8F-method-convert_from_minor_units)
  - [⚙️ Method `convert_to_minor_units`](#%EF%B8%8F-method-convert_to_minor_units)
  - [⚙️ Method `delete_account`](#%EF%B8%8F-method-delete_account)
  - [⚙️ Method `delete_category`](#%EF%B8%8F-method-delete_category)
  - [⚙️ Method `delete_currency`](#%EF%B8%8F-method-delete_currency)
  - [⚙️ Method `delete_currency_exchange`](#%EF%B8%8F-method-delete_currency_exchange)
  - [⚙️ Method `delete_exchange_rate`](#%EF%B8%8F-method-delete_exchange_rate)
  - [⚙️ Method `delete_exchange_rates_by_days`](#%EF%B8%8F-method-delete_exchange_rates_by_days)
  - [⚙️ Method `delete_transaction`](#%EF%B8%8F-method-delete_transaction)
  - [⚙️ Method `fill_missing_exchange_rates`](#%EF%B8%8F-method-fill_missing_exchange_rates)
  - [⚙️ Method `get_account_balances_in_currency`](#%EF%B8%8F-method-get_account_balances_in_currency)
  - [⚙️ Method `get_account_by_id`](#%EF%B8%8F-method-get_account_by_id)
  - [⚙️ Method `get_all_accounts`](#%EF%B8%8F-method-get_all_accounts)
  - [⚙️ Method `get_all_categories`](#%EF%B8%8F-method-get_all_categories)
  - [⚙️ Method `get_all_currencies`](#%EF%B8%8F-method-get_all_currencies)
  - [⚙️ Method `get_all_currency_exchanges`](#%EF%B8%8F-method-get_all_currency_exchanges)
  - [⚙️ Method `get_all_exchange_rates`](#%EF%B8%8F-method-get_all_exchange_rates)
  - [⚙️ Method `get_all_transactions`](#%EF%B8%8F-method-get_all_transactions)
  - [⚙️ Method `get_categories_by_type`](#%EF%B8%8F-method-get_categories_by_type)
  - [⚙️ Method `get_categories_with_icons_by_type`](#%EF%B8%8F-method-get_categories_with_icons_by_type)
  - [⚙️ Method `get_category_by_id`](#%EF%B8%8F-method-get_category_by_id)
  - [⚙️ Method `get_currencies_except_usd`](#%EF%B8%8F-method-get_currencies_except_usd)
  - [⚙️ Method `get_currency_by_code`](#%EF%B8%8F-method-get_currency_by_code)
  - [⚙️ Method `get_currency_by_id`](#%EF%B8%8F-method-get_currency_by_id)
  - [⚙️ Method `get_currency_exchange_rate_by_date`](#%EF%B8%8F-method-get_currency_exchange_rate_by_date)
  - [⚙️ Method `get_currency_subdivision`](#%EF%B8%8F-method-get_currency_subdivision)
  - [⚙️ Method `get_currency_subdivision_by_code`](#%EF%B8%8F-method-get_currency_subdivision_by_code)
  - [⚙️ Method `get_currency_ticker`](#%EF%B8%8F-method-get_currency_ticker)
  - [⚙️ Method `get_default_currency`](#%EF%B8%8F-method-get_default_currency)
  - [⚙️ Method `get_default_currency_id`](#%EF%B8%8F-method-get_default_currency_id)
  - [⚙️ Method `get_earliest_currency_exchange_date`](#%EF%B8%8F-method-get_earliest_currency_exchange_date)
  - [⚙️ Method `get_earliest_financial_date`](#%EF%B8%8F-method-get_earliest_financial_date)
  - [⚙️ Method `get_earliest_transaction_date`](#%EF%B8%8F-method-get_earliest_transaction_date)
  - [⚙️ Method `get_exchange_rate`](#%EF%B8%8F-method-get_exchange_rate)
  - [⚙️ Method `get_filtered_exchange_rates`](#%EF%B8%8F-method-get_filtered_exchange_rates)
  - [⚙️ Method `get_filtered_transactions`](#%EF%B8%8F-method-get_filtered_transactions)
  - [⚙️ Method `get_income_vs_expenses_in_currency`](#%EF%B8%8F-method-get_income_vs_expenses_in_currency)
  - [⚙️ Method `get_last_exchange_rate_date`](#%EF%B8%8F-method-get_last_exchange_rate_date)
  - [⚙️ Method `get_last_two_exchange_rate_records`](#%EF%B8%8F-method-get_last_two_exchange_rate_records)
  - [⚙️ Method `get_missing_exchange_rates_info`](#%EF%B8%8F-method-get_missing_exchange_rates_info)
  - [⚙️ Method `get_recent_transaction_descriptions_for_autocomplete`](#%EF%B8%8F-method-get_recent_transaction_descriptions_for_autocomplete)
  - [⚙️ Method `get_today_balance_in_currency`](#%EF%B8%8F-method-get_today_balance_in_currency)
  - [⚙️ Method `get_today_expenses_in_currency`](#%EF%B8%8F-method-get_today_expenses_in_currency)
  - [⚙️ Method `get_total_accounts_balance_in_currency`](#%EF%B8%8F-method-get_total_accounts_balance_in_currency)
  - [⚙️ Method `get_transaction_by_id`](#%EF%B8%8F-method-get_transaction_by_id)
  - [⚙️ Method `get_transactions_chart_data`](#%EF%B8%8F-method-get_transactions_chart_data)
  - [⚙️ Method `get_transactions_with_money_op_in_currency`](#%EF%B8%8F-method-get_transactions_with_money_op_in_currency)
  - [⚙️ Method `get_usd_to_currency_rate`](#%EF%B8%8F-method-get_usd_to_currency_rate)
  - [⚙️ Method `has_exchange_rates_data`](#%EF%B8%8F-method-has_exchange_rates_data)
  - [⚙️ Method `set_default_currency`](#%EF%B8%8F-method-set_default_currency)
  - [⚙️ Method `should_update_exchange_rates`](#%EF%B8%8F-method-should_update_exchange_rates)
  - [⚙️ Method `update_account`](#%EF%B8%8F-method-update_account)
  - [⚙️ Method `update_category`](#%EF%B8%8F-method-update_category)
  - [⚙️ Method `update_currency`](#%EF%B8%8F-method-update_currency)
  - [⚙️ Method `update_currency_exchange`](#%EF%B8%8F-method-update_currency_exchange)
  - [⚙️ Method `update_currency_exchange_full`](#%EF%B8%8F-method-update_currency_exchange_full)
  - [⚙️ Method `update_currency_ticker`](#%EF%B8%8F-method-update_currency_ticker)
  - [⚙️ Method `update_exchange_rate`](#%EF%B8%8F-method-update_exchange_rate)
  - [⚙️ Method `update_transaction`](#%EF%B8%8F-method-update_transaction)
  - [⚙️ Method `_ensure_performance_indexes`](#%EF%B8%8F-method-_ensure_performance_indexes)
  - [⚙️ Method `_ensure_system_categories`](#%EF%B8%8F-method-_ensure_system_categories)
  - [⚙️ Method `_get_currency_conversion_sql`](#%EF%B8%8F-method-_get_currency_conversion_sql)
  - [⚙️ Method `_get_full_currency_conversion_sql`](#%EF%B8%8F-method-_get_full_currency_conversion_sql)
  - [⚙️ Method `_init_default_settings`](#%EF%B8%8F-method-_init_default_settings)
  - [⚙️ Method `_load_default_currency_cache`](#%EF%B8%8F-method-_load_default_currency_cache)

</details>

## 🏛️ Class `DatabaseManager`

```python
class DatabaseManager(QtSqliteDatabaseManagerBase)
```

Manage the connection and operations for a finance tracking database.

Attributes:

- `db`: A live connection object opened on an SQLite database file.
- `connection_name`: Unique name for this database connection.

<details>
<summary>Code:</summary>

```python
class DatabaseManager(QtSqliteDatabaseManagerBase):

    _db_closed: bool

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in `db_filename`.

        Args:

        - `db_filename` (`str`): The path to the target database file.

        Raises:

        - `ConnectionError`: If the underlying Qt driver fails to open the database.

        """
        super().__init__(prefix="finance_db", db_filename=db_filename)

        self.exchange_rates = ExchangeRatesService(self)

        # Initialize default settings if they don't exist
        self._init_default_settings()
        self._ensure_system_categories()
        self._ensure_performance_indexes()

        # Cached default currency (code, id); loaded once from DB, updated only by set_default_currency
        self._default_currency_cache: tuple[str, int] | None = None

    def add_account(
        self, name: str, balance: float, currency_id: int, *, is_liquid: bool = True, is_cash: bool = False
    ) -> bool:
        """Add a new account to the database.

        Args:

        - `name` (`str`): Account name.
        - `balance` (`float`): Initial balance.
        - `currency_id` (`int`): Currency ID.
        - `is_liquid` (`bool`): Whether account is liquid. Defaults to `True`.
        - `is_cash` (`bool`): Whether account is cash. Defaults to `False`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """INSERT INTO accounts (name, balance, _id_currencies, is_liquid, is_cash)
                   VALUES (:name, :balance, :currency_id, :is_liquid, :is_cash)"""
        params = {
            "name": name,
            "balance": self.convert_to_minor_units(balance, currency_id),
            "currency_id": currency_id,
            "is_liquid": 1 if is_liquid else 0,
            "is_cash": 1 if is_cash else 0,
        }
        return self.execute_simple_query(query, params)

    def add_category(self, name: str, category_type: int, icon: str = "") -> bool:
        """Add a new category to the database.

        Args:

        - `name` (`str`): Category name.
        - `category_type` (`int`): Category type (0 = expense, 1 = income).
        - `icon` (`str`): Category icon. Defaults to `""`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO categories (name, type, icon) VALUES (:name, :type, :icon)"
        params = {
            "name": name,
            "type": category_type,
            "icon": icon,
        }
        return self.execute_simple_query(query, params)

    def add_currency(self, code: str, name: str, symbol: str, subdivision: int = 100) -> bool:
        """Add a new currency to the database.

        Args:

        - `code` (`str`): Currency code (e.g., USD, EUR).
        - `name` (`str`): Currency name.
        - `symbol` (`str`): Currency symbol.
        - `subdivision` (`int`): Number of minor units in one major unit (e.g., 100 for USD cents). Defaults to 100.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO currencies (code, name, symbol, subdivision) VALUES (:code, :name, :symbol, :subdivision)"
        params = {
            "code": code,
            "name": name,
            "symbol": symbol,
            "subdivision": subdivision,
        }
        return self.execute_simple_query(query, params)

    def add_currency_exchange(
        self,
        currency_from_id: int,
        currency_to_id: int,
        amount_from: float,
        amount_to: float,
        exchange_rate: float,
        fee: float,
        date: str,
        description: str = "",
    ) -> bool:
        """Add a new currency exchange record.

        Args:

        - `currency_from_id` (`int`): Source currency ID.
        - `currency_to_id` (`int`): Target currency ID.
        - `amount_from` (`float`): Amount in source currency.
        - `amount_to` (`float`): Amount in target currency.
        - `exchange_rate` (`float`): Exchange rate.
        - `fee` (`float`): Exchange fee.
        - `date` (`str`): Date in YYYY-MM-DD format.
        - `description` (`str`): Exchange description. Defaults to `""`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        from_subdivision = self.get_currency_subdivision(currency_from_id)
        to_subdivision = self.get_currency_subdivision(currency_to_id)
        # Exchange rate is now stored as REAL directly
        query = """INSERT INTO currency_exchanges
                   (_id_currency_from, _id_currency_to, amount_from, amount_to,
                    exchange_rate, fee, date, description)
                   VALUES (:from_id, :to_id, :amount_from, :amount_to,
                           :exchange_rate, :fee, :date, :description)"""
        params = {
            "from_id": currency_from_id,
            "to_id": currency_to_id,
            "amount_from": int(amount_from * from_subdivision),  # Convert to minor units
            "amount_to": int(amount_to * to_subdivision),  # Convert to minor units
            "exchange_rate": exchange_rate,  # Store as REAL directly
            "fee": int(fee * from_subdivision),  # Fee in from_currency minor units
            "date": date,
            "description": description,
        }
        return self.execute_simple_query(query, params)

    def add_exchange_rate(self, currency_id: int, rate: float, date: str) -> bool:
        """Add a new exchange rate to USD.

        Args:

        - `currency_id` (`int`): Currency ID (rate is always to USD).
        - `rate` (`float`): Exchange rate to USD.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        return self.exchange_rates.add_exchange_rate(currency_id, rate, date)

    def add_transaction(
        self,
        amount: float,
        description: str,
        category_id: int,
        currency_id: int,
        date: str,
        tag: str = "",
    ) -> bool:
        """Add a new transaction.

        Args:

        - `amount` (`float`): Transaction amount.
        - `description` (`str`): Transaction description.
        - `category_id` (`int`): Category ID.
        - `currency_id` (`int`): Currency ID.
        - `date` (`str`): Date in YYYY-MM-DD format.
        - `tag` (`str`): Transaction tag. Defaults to `""`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """INSERT INTO transactions (amount, description, _id_categories, _id_currencies, date, tag)
                   VALUES (:amount, :description, :category_id, :currency_id, :date, :tag)"""
        params = {
            "amount": self.convert_to_minor_units(amount, currency_id),
            "description": description,
            "category_id": category_id,
            "currency_id": currency_id,
            "date": date,
            "tag": tag,
        }
        return self.execute_simple_query(query, params)

    def check_exchange_rate_exists(self, currency_id: int, date: str) -> bool:
        """Check if exchange rate to USD exists for given currency and date.

        Args:

        - `currency_id` (`int`): Currency ID.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if exchange rate exists, False otherwise.

        """
        return self.exchange_rates.check_exchange_rate_exists(currency_id, date)

    def clean_invalid_exchange_rates(self) -> int:
        """Clean exchange rates with empty or invalid rate values.

        Returns:

        - `int`: Number of cleaned records.

        """
        return self.exchange_rates.clean_invalid_exchange_rates()

    def close(self) -> None:
        """Close the database connection."""
        self._default_currency_cache = None
        self.exchange_rates.clear_cache()
        super().close()

    def convert_from_minor_units(self, amount_minor: float, currency_id: int) -> float:
        """Convert amount from minor units to major units using currency subdivision.

        Args:

        - `amount_minor` (`int | float`): Amount in minor units (e.g., cents).
        - `currency_id` (`int`): Currency ID.

        Returns:

        - `float`: Amount in major units (e.g., dollars).

        """
        subdivision = self.get_currency_subdivision(currency_id)
        return float(amount_minor) / subdivision

    def convert_to_minor_units(self, amount_major: float, currency_id: int) -> int:
        """Convert amount from major units to minor units using currency subdivision.

        Args:

        - `amount_major` (`float`): Amount in major units (e.g., dollars).
        - `currency_id` (`int`): Currency ID.

        Returns:

        - `int`: Amount in minor units (e.g., cents).

        """
        subdivision = self.get_currency_subdivision(currency_id)
        return int(amount_major * subdivision)

    def delete_account(self, account_id: int) -> bool:
        """Delete an account from the database.

        Args:

        - `account_id` (`int`): Account ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM accounts WHERE _id = :id"
        return self.execute_simple_query(query, {"id": account_id})

    def delete_category(self, category_id: int) -> bool:
        """Delete a category from the database.

        Args:

        - `category_id` (`int`): Category ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM categories WHERE _id = :id"
        return self.execute_simple_query(query, {"id": category_id})

    def delete_currency(self, currency_id: int) -> bool:
        """Delete a currency from the database.

        Args:

        - `currency_id` (`int`): Currency ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM currencies WHERE _id = :id"
        return self.execute_simple_query(query, {"id": currency_id})

    def delete_currency_exchange(self, exchange_id: int) -> bool:
        """Delete a currency exchange record.

        Args:

        - `exchange_id` (`int`): Exchange ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM currency_exchanges WHERE _id = :id"
        return self.execute_simple_query(query, {"id": exchange_id})

    def delete_exchange_rate(self, rate_id: int) -> bool:
        """Delete an exchange rate.

        Args:

        - `rate_id` (`int`): Rate ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        return self.exchange_rates.delete_exchange_rate(rate_id)

    def delete_exchange_rates_by_days(self, days: int) -> tuple[bool, int]:
        """Delete exchange rates for the last N days for each currency.

        Args:

        - `days` (`int`): Number of days to look back from current date.

        Returns:

        - `tuple[bool, int]`: (success, deleted_count) where success is True if
          the operation completed successfully, and deleted_count is the number
          of records deleted.

        """
        return self.exchange_rates.delete_exchange_rates_by_days(days)

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction.

        Args:

        - `transaction_id` (`int`): Transaction ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM transactions WHERE _id = :id"
        return self.execute_simple_query(query, {"id": transaction_id})

    def fill_missing_exchange_rates(self) -> int:
        """Fill missing exchange rates with previous available rates for all date gaps.

        Returns:

        - `int`: Number of exchange rates that were filled.

        """
        return self.exchange_rates.fill_missing_exchange_rates()

    def get_account_balances_in_currency(self, currency_id: int) -> list[tuple[str, float]]:
        """Get all account balances converted to specified currency.

        Args:

        - `currency_id` (`int`): Target currency ID.

        Returns:

        - `list[tuple[str, float]]`: List of (account_name, balance) tuples in target currency.

        """
        # Get USD currency ID for conversion calculations
        usd_currency = self.get_currency_by_code("USD")
        usd_currency_id = usd_currency[0] if usd_currency else None

        if currency_id == usd_currency_id:
            # Converting to USD - direct rates
            query = """
                SELECT a.name,
                       CASE
                           WHEN a._id_currencies = :currency_id THEN a.balance
                           ELSE COALESCE(er.rate * a.balance, a.balance)
                       END as converted_balance
                FROM accounts a
                LEFT JOIN exchange_rates er ON er._id_currency = a._id_currencies
                                            AND er.date = (
                                                SELECT MAX(date)
                                                FROM exchange_rates er2
                                                WHERE er2._id_currency = a._id_currencies
                                                  AND er2.date <= date('now')
                                            )
                ORDER BY a.name
            """
        else:
            # Converting to non-USD currency via USD
            query = """
                SELECT a.name,
                       CASE
                           WHEN a._id_currencies = :currency_id THEN a.balance
                           WHEN a._id_currencies = :usd_currency_id THEN
                               COALESCE(a.balance / NULLIF(target_er.rate, 0), a.balance)
                           ELSE
                               COALESCE(source_er.rate * a.balance / NULLIF(target_er.rate, 0), a.balance)
                       END as converted_balance
                FROM accounts a
                LEFT JOIN exchange_rates source_er ON source_er._id_currency = a._id_currencies
                                                   AND source_er.date = (
                                                       SELECT MAX(date)
                                                       FROM exchange_rates ser2
                                                       WHERE ser2._id_currency = a._id_currencies
                                                         AND ser2.date <= date('now')
                                                   )
                LEFT JOIN exchange_rates target_er ON target_er._id_currency = :currency_id
                                                   AND target_er.date = (
                                                       SELECT MAX(date)
                                                       FROM exchange_rates ter2
                                                       WHERE ter2._id_currency = :currency_id
                                                         AND ter2.date <= date('now')
                                                   )
                ORDER BY a.name
            """
        if currency_id == usd_currency_id:
            rows = self.get_rows(query, {"currency_id": currency_id})
        else:
            rows = self.get_rows(query, {"currency_id": currency_id, "usd_currency_id": usd_currency_id})
        return [(row[0], float(row[1]) / 100) for row in rows]

    def get_account_by_id(self, account_id: int) -> list[Any] | None:
        """Get account data by ID.

        Args:

        - `account_id` (`int`): Account ID.

        Returns:

        - `list[Any] | None`: Account data or None if not found.

        """
        query = """
            SELECT a._id, a.name, a.balance, c.code, a.is_liquid, a.is_cash, c._id as currency_id
            FROM accounts a
            JOIN currencies c ON a._id_currencies = c._id
            WHERE a._id = :account_id
        """
        rows = self.get_rows(query, {"account_id": account_id})
        return rows[0] if rows else None

    def get_all_accounts(self) -> list[list[Any]]:
        """Get all accounts with currency information.

        Returns:

        - `list[list[Any]]`: List of account records [_id, name, balance, currency_code,
          is_liquid, is_cash, currency_id].

        """
        return self.get_rows("""
            SELECT a._id, a.name, a.balance, c.code, a.is_liquid, a.is_cash, c._id as currency_id
            FROM accounts a
            JOIN currencies c ON a._id_currencies = c._id
            ORDER BY a.name
        """)

        # Return raw balance values (in minor units) - conversion will be done in the UI layer

    def get_all_categories(self) -> list[list[Any]]:
        """Get all categories.

        Returns:

        - `list[list[Any]]`: List of category records [_id, name, type, icon].

        """
        return self.get_rows("SELECT _id, name, type, icon FROM categories ORDER BY type, name")

    def get_all_currencies(self) -> list[list[Any]]:
        """Get all currencies.

        Returns:

        - `list[list[Any]]`: List of currency records [_id, code, name, symbol].

        """
        return self.get_rows("SELECT _id, code, name, symbol FROM currencies ORDER BY code")

    def get_all_currency_exchanges(self) -> list[list[Any]]:
        """Get all currency exchange records with currency information.

        Returns:

        - `list[list[Any]]`: List of exchange records.

        """
        rows = self.get_rows("""
            SELECT ce._id, cf.code, ct.code, ce.amount_from, ce.amount_to,
                   ce.exchange_rate, ce.fee, ce.date, ce.description
            FROM currency_exchanges ce
            JOIN currencies cf ON ce._id_currency_from = cf._id
            JOIN currencies ct ON ce._id_currency_to = ct._id
            ORDER BY ce.date DESC, ce._id DESC
        """)

        # Return raw values (in minor units) - conversion will be done in the UI layer
        # Just ensure exchange_rate is float type for consistency
        exchange_rate_index = 5  # Use a constant instead of magic number
        for row in rows:
            if len(row) > exchange_rate_index and row[exchange_rate_index] is not None:
                try:
                    row[exchange_rate_index] = float(row[exchange_rate_index])
                except (ValueError, TypeError):
                    row[exchange_rate_index] = 0.0  # Set to 0 for invalid values
            elif len(row) > exchange_rate_index:
                row[exchange_rate_index] = 0.0  # Set to 0 for None

        return rows

    def get_all_exchange_rates(self, limit: int | None = None) -> list[list[Any]]:
        """Get all exchange rates with currency information.

        Args:

        - `limit` (`int | None`): Maximum number of records to return. None for all records. Defaults to `None`.

        Returns:

        - `list[list[Any]]`: List of exchange rate records.

        """
        return self.exchange_rates.get_all_exchange_rates(limit)

    def get_all_transactions(self, limit: int | None = None) -> list[list[Any]]:
        """Get all transactions with category and currency information.

        Args:

        - `limit` (`int | None`): Limit number of records. Defaults to `None` (no limit).

        Returns:

        - `list[list[Any]]`: List of transaction records.

        """
        query = """
            SELECT t._id, t.amount, t.description, cat.name, c.code, t.date, t.tag,
                   cat.type, cat.icon, c.symbol
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            JOIN currencies c ON t._id_currencies = c._id
            ORDER BY t.date DESC, t._id DESC
        """

        params: dict[str, Any] | None = None
        if limit is not None:
            query += " LIMIT :limit"
            params = {"limit": limit}

        return self.get_rows(query, params)

    def get_categories_by_type(self, category_type: int) -> list[str]:
        """Get category names by type.

        Args:

        - `category_type` (`int`): Category type (0 = expense, 1 = income).

        Returns:

        - `list[str]`: List of category names.

        """
        rows = self.get_rows("SELECT name FROM categories WHERE type = :type ORDER BY name", {"type": category_type})
        return [row[0] for row in rows]

    def get_categories_with_icons_by_type(self, category_type: int) -> list[tuple[str, str]]:
        """Get category names and icons by type.

        Args:

        - `category_type` (`int`): Category type (0 = expense, 1 = income).

        Returns:

        - `list[tuple[str, str]]`: List of (name, icon) tuples.

        """
        rows = self.get_rows(
            "SELECT name, icon FROM categories WHERE type = :type ORDER BY name", {"type": category_type}
        )
        return [(row[0], row[1]) for row in rows]

    def get_category_by_id(self, category_id: int) -> list[Any] | None:
        """Get category by ID.

        Args:

        - `category_id` (`int`): The category ID to retrieve.

        Returns:

        - `list[Any] | None`: Category data [_id, name, type, icon] or None if not found.

        """
        query = "SELECT _id, name, type, icon FROM categories WHERE _id = :category_id"
        rows = self.get_rows(query, {"category_id": category_id})
        return rows[0] if rows else None

    def get_currencies_except_usd(self) -> list[list[Any]]:
        """Get all currencies except USD (which is the base currency).

        Returns:

        - `list[list[Any]]`: List of currency records [_id, code, name, symbol] excluding USD.

        """
        return self.get_rows("SELECT _id, code, name, symbol FROM currencies WHERE code != 'USD' ORDER BY code")

    def get_currency_by_code(self, code: str) -> tuple[int, str, str] | None:
        """Get currency information by code.

        Args:

        - `code` (`str`): Currency code.

        Returns:

        - `tuple[int, str, str] | None`: Tuple of (id, name, symbol) or None if not found.

        """
        rows = self.get_rows("SELECT _id, name, symbol FROM currencies WHERE code = :code", {"code": code})
        return (rows[0][0], rows[0][1], rows[0][2]) if rows else None

    def get_currency_by_id(self, currency_id: int) -> tuple[str, str, str] | None:
        """Get currency information by ID.

        Args:

        - `currency_id` (`int`): Currency ID.

        Returns:

        - `tuple[str, str, str] | None`: Tuple of (code, name, symbol) or None if not found.

        """
        rows = self.get_rows("SELECT code, name, symbol FROM currencies WHERE _id = :id", {"id": currency_id})
        return (rows[0][0], rows[0][1], rows[0][2]) if rows else None

    def get_currency_exchange_rate_by_date(self, currency_id: int, date: str) -> float:
        """Get exchange rate for a specific currency on a specific date.

        Args:

        - `currency_id` (`int`): Currency ID.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `float`: Exchange rate (USD to currency) or 1.0 if not found.

        """
        return self.exchange_rates.get_currency_exchange_rate_by_date(currency_id, date)

    def get_currency_subdivision(self, currency_id: int) -> int:
        """Get subdivision value for a currency.

        Args:

        - `currency_id` (`int`): Currency ID.

        Returns:

        - `int`: Number of minor units in one major unit (e.g., 100 for USD cents). Returns 100 as default if not found.

        """
        rows = self.get_rows("SELECT subdivision FROM currencies WHERE _id = :id", {"id": currency_id})
        return rows[0][0] if rows else 100

    def get_currency_subdivision_by_code(self, currency_code: str) -> int:
        """Get subdivision value for a currency by currency code.

        Args:

        - `currency_code` (`str`): Currency code (e.g., 'USD', 'EUR').

        Returns:

        - `int`: Number of minor units in one major unit (e.g., 100 for USD cents). Returns 100 as default if not found.

        """
        rows = self.get_rows("SELECT subdivision FROM currencies WHERE code = :code", {"code": currency_code})
        return rows[0][0] if rows else 100

    def get_currency_ticker(self, currency_id: int) -> str | None:
        """Get currency ticker by ID.

        Args:

        - `currency_id` (`int`): Currency ID.

        Returns:

        - `str | None`: Currency ticker or None if not found or empty.

        """
        rows = self.get_rows("SELECT ticker FROM currencies WHERE _id = :id", {"id": currency_id})
        if rows and rows[0][0] and rows[0][0].strip():
            return rows[0][0].strip()
        return None

    def get_default_currency(self) -> str:
        """Get the default currency code (from in-memory cache, not DB).

        Returns:

        - `str`: Default currency code or 'RUB' if not set.

        """
        self._load_default_currency_cache()
        if self._default_currency_cache:
            return self._default_currency_cache[0]
        return "RUB"

    def get_default_currency_id(self) -> int:
        """Get the default currency ID (from in-memory cache, not DB).

        Returns:

        - `int`: Default currency ID or 1 if not found.

        """
        self._load_default_currency_cache()
        if self._default_currency_cache:
            return self._default_currency_cache[1]
        return 1

    def get_earliest_currency_exchange_date(self) -> str | None:
        """Get the earliest date from currency_exchanges table.

        Returns:

        - `str | None`: Earliest date in YYYY-MM-DD format or None if no records exist.

        """
        rows = self.get_rows("SELECT MIN(date) FROM currency_exchanges")
        return rows[0][0] if rows and rows[0][0] else None

    def get_earliest_financial_date(self) -> str | None:
        """Get the earliest date from either transactions or currency_exchanges tables.

        Returns:

        - `str | None`: Earliest date in YYYY-MM-DD format or None if no records exist.

        """
        transaction_date = self.get_earliest_transaction_date()
        exchange_date = self.get_earliest_currency_exchange_date()

        # Return the earliest of the two dates
        if transaction_date and exchange_date:
            return min(transaction_date, exchange_date)
        if transaction_date:
            return transaction_date
        if exchange_date:
            return exchange_date
        return None

    def get_earliest_transaction_date(self) -> str | None:
        """Get the earliest date from transactions table.

        Returns:

        - `str | None`: Earliest date in YYYY-MM-DD format or None if no records exist.

        """
        rows = self.get_rows("SELECT MIN(date) FROM transactions WHERE date IS NOT NULL")
        return rows[0][0] if rows and rows[0][0] else None

    def get_exchange_rate(self, from_currency_id: int, to_currency_id: int, date: str | None = None) -> float:
        """Get exchange rate between currencies (both referenced to USD).

        Args:

        - `from_currency_id` (`int`): Source currency ID.
        - `to_currency_id` (`int`): Target currency ID.
        - `date` (`str | None`): Date for rate lookup. Uses latest if None.

        Returns:

        - `float`: Exchange rate or 1.0 if not found/same currency.

        """
        return self.exchange_rates.get_exchange_rate(from_currency_id, to_currency_id, date)

    def get_filtered_exchange_rates(
        self,
        currency_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        """Get filtered exchange rates with currency information.

        Args:

        - `currency_id` (`int | None`): Currency ID to filter by. None for all currencies.
        - `date_from` (`str | None`): Start date in YYYY-MM-DD format. None for no start date filter.
        - `date_to` (`str | None`): End date in YYYY-MM-DD format. None for no end date filter.
        - `limit` (`int | None`): Maximum number of records to return. None for all records.

        Returns:

        - `list[list[Any]]`: List of filtered exchange rate records.

        """
        return self.exchange_rates.get_filtered_exchange_rates(currency_id, date_from, date_to, limit)

    def get_filtered_transactions(
        self,
        category_type: int | None = None,
        category_name: str | None = None,
        currency_code: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        description_filter: str | None = None,
    ) -> list[list[Any]]:
        """Get filtered transactions.

        Args:

        - `category_type` (`int | None`): Filter by category type. Defaults to `None`.
        - `category_name` (`str | None`): Filter by category name. Defaults to `None`.
        - `currency_code` (`str | None`): Filter by currency code. Defaults to `None`.
        - `date_from` (`str | None`): Filter from date. Defaults to `None`.
        - `date_to` (`str | None`): Filter to date. Defaults to `None`.
        - `description_filter` (`str | None`): Filter by description substring (case insensitive). Defaults to `None`.

        Returns:

        - `list[list[Any]]`: List of filtered transaction records.

        """
        conditions: list[str] = []
        params: dict[str, Any] = {}

        if category_type is not None:
            conditions.append("cat.type = :category_type")
            params["category_type"] = category_type

        if category_name:
            conditions.append("cat.name = :category_name")
            params["category_name"] = category_name

        if currency_code:
            conditions.append("c.code = :currency_code")
            params["currency_code"] = currency_code

        if date_from and date_to:
            conditions.append("t.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        if description_filter:
            conditions.append("LOWER(t.description) LIKE :description_filter")
            params["description_filter"] = f"%{description_filter.lower()}%"

        query_text = """
            SELECT t._id, t.amount, t.description, cat.name, c.code, t.date, t.tag,
                   cat.type, cat.icon, c.symbol
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            JOIN currencies c ON t._id_currencies = c._id
        """

        if conditions:
            query_text += " WHERE " + " AND ".join(conditions)

        query_text += " ORDER BY t.date DESC, t._id DESC"

        return self.get_rows(query_text, params)

    def get_income_vs_expenses_in_currency(
        self, currency_id: int, date_from: str | None = None, date_to: str | None = None
    ) -> tuple[float, float]:
        """Get total income and expenses in specified currency.

        Args:

        - `currency_id` (`int`): Target currency ID.
        - `date_from` (`str | None`): From date. Defaults to `None`.
        - `date_to` (`str | None`): To date. Defaults to `None`.

        Returns:

        - `tuple[float, float]`: Tuple of (total_income, total_expenses) in target currency.

        """
        conditions = []
        params: dict[str, Any] = {"currency_id": currency_id}

        if date_from and date_to:
            conditions.append("t.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        where_clause = " AND " + " AND ".join(conditions) if conditions else ""

        # Get currency conversion SQL
        join_clause, conversion_case, extra_params = self._get_currency_conversion_sql(currency_id)
        params.update(extra_params)

        # Get income (category type = 1)
        income_query = f"""
            SELECT SUM({conversion_case}) as total_income
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            {join_clause}
            WHERE cat.type = 1{where_clause}
        """

        # Get expenses (category type = 0)
        expenses_query = f"""
            SELECT SUM({conversion_case}) as total_expenses
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            {join_clause}
            WHERE cat.type = 0{where_clause}
        """

        income_rows = self.get_rows(income_query, params)
        expenses_rows = self.get_rows(expenses_query, params)

        total_income = float(income_rows[0][0] or 0) / 100 if income_rows and income_rows[0][0] else 0.0
        total_expenses = float(expenses_rows[0][0] or 0) / 100 if expenses_rows and expenses_rows[0][0] else 0.0

        return total_income, total_expenses

    def get_last_exchange_rate_date(self, currency_id: int) -> str | None:
        """Get the last date for which exchange rate exists for a currency.

        Args:

        - `currency_id` (`int`): Currency ID.

        Returns:

        - `str | None`: Last date in YYYY-MM-DD format or None if no rates exist.

        """
        return self.exchange_rates.get_last_exchange_rate_date(currency_id)

    def get_last_two_exchange_rate_records(self, currency_id: int) -> list[tuple[str, float]]:
        """Get the last two exchange rate records for a currency.

        Args:

        - `currency_id` (`int`): Currency ID.

        Returns:

        - `list[tuple[str, float]]`: List of tuples (date, rate) for the last two records, sorted by date.

        """
        return self.exchange_rates.get_last_two_exchange_rate_records(currency_id)

    def get_missing_exchange_rates_info(self, date_from: str, date_to: str) -> dict[int, list[str]]:
        """Get information about missing exchange rates for each currency.

        Checks for missing rates for each day in the date range.

        Args:

        - `date_from` (`str`): Start date in YYYY-MM-DD format.
        - `date_to` (`str`): End date in YYYY-MM-DD format.

        Returns:

        - `dict[int, list[str]]`: Dictionary mapping currency_id to list of missing dates.

        """
        return self.exchange_rates.get_missing_exchange_rates_info(date_from, date_to)

    def get_recent_transaction_descriptions_for_autocomplete(self, limit: int = 1000) -> list[str]:
        """Get recent unique transaction descriptions for autocomplete.

        Args:

        - `limit` (`int`): Number of recent transactions to analyze. Defaults to `1000`.

        Returns:

        - `list[str]`: List of unique transaction descriptions.

        """
        # Get descriptions ordered by frequency (most used first) and then by recency
        # Also include recent unique descriptions that might not be frequent
        query = """
            WITH frequent_descriptions AS (
                SELECT t.description, COUNT(*) as usage_count, MAX(t.date) as last_used
                FROM transactions t
                WHERE t.description IS NOT NULL AND t.description != ''
                GROUP BY t.description
                ORDER BY usage_count DESC, last_used DESC
                LIMIT :limit_frequent
            ),
            recent_descriptions AS (
                SELECT DISTINCT t.description
                FROM transactions t
                WHERE t.description IS NOT NULL AND t.description != ''
                ORDER BY t._id DESC
                LIMIT :limit_recent
            )
            SELECT DISTINCT description
            FROM (
                SELECT description FROM frequent_descriptions
                UNION
                SELECT description FROM recent_descriptions
            )
            ORDER BY description
        """

        # Use 70% for frequent, 30% for recent
        limit_frequent_percentage = 0.7
        limit_frequent = int(limit * limit_frequent_percentage)
        limit_recent = limit - limit_frequent

        rows = self.get_rows(query, {"limit_frequent": limit_frequent, "limit_recent": limit_recent})
        return [row[0] for row in rows if row[0]]

    def get_today_balance_in_currency(self, currency_id: int) -> float:
        """Get today's balance (income - expenses) in specified currency.

        Args:

        - `currency_id` (`int`): Target currency ID.

        Returns:

        - `float`: Today's balance in target currency.

        """
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        total_income, total_expenses = self.get_income_vs_expenses_in_currency(currency_id, today, today)
        return total_income - total_expenses

    def get_today_expenses_in_currency(self, currency_id: int) -> float:
        """Get today's expenses in specified currency.

        Args:

        - `currency_id` (`int`): Currency ID for conversion.

        Returns:

        - `float`: Today's expenses in the specified currency.

        """
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        _, expenses = self.get_income_vs_expenses_in_currency(currency_id, today, today)
        return expenses

    def get_total_accounts_balance_in_currency(self, currency_id: int | None = None) -> float:
        """Get total balance across all accounts in given or default currency.

        Sums balances of all accounts converted to the target currency (by current
        exchange rates). Used e.g. for label_balance_accounts.

        Args:

        - `currency_id` (`int | None`): Target currency ID. If None, uses default currency.

        Returns:

        - `float`: Total balance in target currency (major units).

        """
        if currency_id is None:
            currency_id = self.get_default_currency_id()
        balances: list[tuple[str, float]] = self.get_account_balances_in_currency(currency_id)
        return sum(balance for _name, balance in balances)

    def get_transaction_by_id(self, transaction_id: int) -> list[Any] | None:
        """Get transaction by ID with category and currency information.

        Args:

        - `transaction_id` (`int`): The transaction ID to retrieve.

        Returns:

        - `list[Any] | None`: Transaction data [id, amount, description, category_id,
          currency_id, date, tag] or None if not found.

        """
        query = """
            SELECT t._id, t.amount, t.description, t._id_categories, t._id_currencies, t.date, t.tag
            FROM transactions t
            WHERE t._id = :transaction_id
        """

        rows = self.get_rows(query, {"transaction_id": transaction_id})
        return rows[0] if rows else None

    def get_transactions_chart_data(
        self,
        currency_id: int,
        category_type: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[tuple[str, float]]:
        """Get transaction data for charting in specified currency.

        Args:

        - `currency_id` (`int`): Target currency ID.
        - `category_type` (`int | None`): Category type filter. Defaults to `None`.
        - `date_from` (`str | None`): From date. Defaults to `None`.
        - `date_to` (`str | None`): To date. Defaults to `None`.

        Returns:

        - `list[tuple[str, float]]`: List of (date, amount) tuples in target currency.

        """
        conditions = []
        params: dict[str, Any] = {"currency_id": currency_id}

        if category_type is not None:
            conditions.append("cat.type = :category_type")
            params["category_type"] = category_type

        if date_from and date_to:
            conditions.append("t.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        where_clause = " AND " + " AND ".join(conditions) if conditions else ""

        # Get currency conversion SQL
        join_clause, conversion_case, extra_params = self._get_currency_conversion_sql(currency_id)
        params.update(extra_params)

        query = f"""
            SELECT t.date, SUM({conversion_case}) as total_amount
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            {join_clause}
            WHERE 1=1{where_clause}
            GROUP BY t.date
            ORDER BY t.date ASC
        """

        rows = self.get_rows(query, params)
        return [(row[0], float(row[1]) / 100) for row in rows]

    def get_transactions_with_money_op_in_currency(
        self,
        target_currency_id: int | None = None,
        category_type: int | None = None,
        category_name: str | None = None,
        currency_code: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        description_filter: str | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        """Get transactions with signed monetary operation value in target currency.

        Money op: expense (category type 0) is negative, income (type 1) is positive.
        Conversion uses exchange_rates by transaction date (latest rate <= t.date).
        If target_currency_id is None, uses default currency from settings.

        Args:

        - `target_currency_id` (`int | None`): Target currency ID. None = default currency.
        - `category_type` (`int | None`): Filter by category type. Defaults to `None`.
        - `category_name` (`str | None`): Filter by category name. Defaults to `None`.
        - `currency_code` (`str | None`): Filter by currency code. Defaults to `None`.
        - `date_from` (`str | None`): Filter from date. Defaults to `None`.
        - `date_to` (`str | None`): Filter to date. Defaults to `None`.
        - `description_filter` (`str | None`): Filter by description substring. Defaults to `None`.
        - `limit` (`int | None`): Max records. Defaults to `None`.

        Returns:

        - `list[list[Any]]`: Each row is [t._id, t.amount, description, cat.name, c.code,
          t.date, t.tag, cat.type, cat.icon, c.symbol, money_op_major]. money_op_major
          is signed float in target currency (major units).

        """
        if target_currency_id is None:
            target_currency_id = self.get_default_currency_id()

        conditions: list[str] = []
        params: dict[str, Any] = {"currency_id": target_currency_id}

        if category_type is not None:
            conditions.append("cat.type = :category_type")
            params["category_type"] = category_type

        if category_name:
            conditions.append("cat.name = :category_name")
            params["category_name"] = category_name

        if currency_code:
            conditions.append("c.code = :currency_code")
            params["currency_code"] = currency_code

        if date_from and date_to:
            conditions.append("t.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        if description_filter:
            conditions.append("LOWER(t.description) LIKE :description_filter")
            params["description_filter"] = f"%{description_filter.lower()}%"

        join_clause, conversion_case, extra_params = self._get_currency_conversion_sql(target_currency_id)
        params.update(extra_params)

        money_op_sql = f"(CASE WHEN cat.type = 0 THEN -1 ELSE 1 END) * ({conversion_case.strip()})"
        where_sql = " AND " + " AND ".join(conditions) if conditions else ""

        query_text = f"""
            SELECT t._id, t.amount, t.description, cat.name, c.code, t.date, t.tag,
                   cat.type, cat.icon, c.symbol,
                   {money_op_sql} AS money_op_minor
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            JOIN currencies c ON t._id_currencies = c._id
            {join_clause}
            WHERE 1=1 {where_sql}
            ORDER BY t.date DESC, t._id DESC
        """
        if limit is not None:
            query_text += " LIMIT :limit"
            params["limit"] = limit

        rows = self.get_rows(query_text, params)
        subdivision = self.get_currency_subdivision(target_currency_id)
        result: list[list[Any]] = []
        for row in rows:
            money_op_minor = float(row[10] or 0)
            money_op_major = money_op_minor / subdivision
            result.append([*list(row[:10]), money_op_major])
        return result

    def get_usd_to_currency_rate(self, currency_id: int, date: str | None = None) -> float:
        """Get exchange rate from currency to USD (how many USD for 1 currency unit).

        Uses caching to avoid repeated database queries.
        Note: Despite the method name, this returns currency_to_USD rates.

        Args:

        - `currency_id` (`int`): Currency ID.
        - `date` (`str | None`): Date for rate lookup. Uses latest if None.

        Returns:

        - `float`: Exchange rate or 1.0 if not found.

        """
        return self.exchange_rates.get_usd_to_currency_rate(currency_id, date)

    def has_exchange_rates_data(self) -> bool:
        """Check if there are any exchange rate records in the database.

        Returns:

        - `bool`: True if exchange rates exist, False otherwise.

        """
        return self.exchange_rates.has_exchange_rates_data()

    def set_default_currency(self, currency_code: str) -> bool:
        """Set the default currency.

        Args:

        - `currency_code` (`str`): Currency code to set as default.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        # Get the currency ID from the currency code
        currency_info = self.get_currency_by_code(currency_code)
        if not currency_info:
            return False

        currency_id = str(currency_info[0])  # Convert ID to string for storage

        # First try to update existing setting
        update_query = "UPDATE settings SET value = :id WHERE key = 'default_currency'"
        if self.execute_simple_query(update_query, {"id": currency_id}):
            # Check if any rows were affected by checking if the setting exists
            check_query = "SELECT COUNT(*) FROM settings WHERE key = 'default_currency'"
            rows = self.get_rows(check_query)
            if rows and rows[0][0] > 0:
                self._default_currency_cache = (currency_code, currency_info[0])
                return True

        # If update didn't affect any rows, insert new setting
        insert_query = "INSERT INTO settings (key, value) VALUES ('default_currency', :id)"
        if self.execute_simple_query(insert_query, {"id": currency_id}):
            self._default_currency_cache = (currency_code, currency_info[0])
            return True
        return False

    def should_update_exchange_rates(self) -> bool:
        """Check if exchange rates need to be updated based on today's date.

        Returns:

        - `bool`: True if update is needed, False if all currencies have today's rates.

        """
        return self.exchange_rates.should_update_exchange_rates()

    def update_account(
        self,
        account_id: int,
        name: str,
        balance: float,
        currency_id: int,
        *,
        is_liquid: bool = True,
        is_cash: bool = False,
    ) -> bool:
        """Update an existing account.

        Args:

        - `account_id` (`int`): Account ID.
        - `name` (`str`): Account name.
        - `balance` (`float`): Account balance.
        - `currency_id` (`int`): Currency ID.
        - `is_liquid` (`bool`): Whether account is liquid. Defaults to `True`.
        - `is_cash` (`bool`): Whether account is cash. Defaults to `False`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """UPDATE accounts SET name = :name, balance = :balance, _id_currencies = :currency_id,
                   is_liquid = :is_liquid, is_cash = :is_cash WHERE _id = :id"""
        params = {
            "name": name,
            "balance": self.convert_to_minor_units(balance, currency_id),
            "currency_id": currency_id,
            "is_liquid": 1 if is_liquid else 0,
            "is_cash": 1 if is_cash else 0,
            "id": account_id,
        }
        return self.execute_simple_query(query, params)

    def update_category(self, category_id: int, name: str, category_type: int, icon: str = "") -> bool:
        """Update an existing category.

        Args:

        - `category_id` (`int`): Category ID.
        - `name` (`str`): Category name.
        - `category_type` (`int`): Category type.
        - `icon` (`str`): Category icon. Defaults to `""`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "UPDATE categories SET name = :name, type = :type, icon = :icon WHERE _id = :id"
        params = {
            "name": name,
            "type": category_type,
            "icon": icon,
            "id": category_id,
        }
        return self.execute_simple_query(query, params)

    def update_currency(self, currency_id: int, code: str, name: str, symbol: str) -> bool:
        """Update an existing currency.

        Args:

        - `currency_id` (`int`): Currency ID.
        - `code` (`str`): Currency code.
        - `name` (`str`): Currency name.
        - `symbol` (`str`): Currency symbol.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "UPDATE currencies SET code = :code, name = :name, symbol = :symbol WHERE _id = :id"
        params = {
            "code": code,
            "name": name,
            "symbol": symbol,
            "id": currency_id,
        }
        return self.execute_simple_query(query, params)

    def update_currency_exchange(self, exchange_id: int, amount_from: float, amount_to: float) -> bool:
        """Update currency exchange amounts.

        Args:

        - `exchange_id` (`int`): Exchange record ID.
        - `amount_from` (`float`): Amount from (in major units).
        - `amount_to` (`float`): Amount to (in major units).

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        try:
            # Get the exchange record to get currency information
            exchange_record = self.get_rows(
                """
                SELECT ce._id, ce._id_currency_from, ce._id_currency_to, ce.amount_from, ce.amount_to,
                       ce.exchange_rate, ce.fee, ce.date, ce.description
                FROM currency_exchanges ce
                WHERE ce._id = :id
                """,
                {"id": exchange_id},
            )

            if not exchange_record:
                logger.warning("Exchange record with ID %s not found", exchange_id)
                return False

            record = exchange_record[0]
            currency_from_id = record[1]
            currency_to_id = record[2]

            # Get currency subdivisions
            from_subdivision = self.get_currency_subdivision(currency_from_id)
            to_subdivision = self.get_currency_subdivision(currency_to_id)

            # Convert amounts to minor units
            amount_from_minor = int(amount_from * from_subdivision)
            amount_to_minor = int(amount_to * to_subdivision)

            # Update the exchange record
            query = """
                UPDATE currency_exchanges
                SET amount_from = :amount_from, amount_to = :amount_to
                WHERE _id = :id
            """
            params = {"amount_from": amount_from_minor, "amount_to": amount_to_minor, "id": exchange_id}

            return self.execute_simple_query(query, params)

        except Exception:
            logger.exception("Error updating currency exchange")
            return False

    def update_currency_exchange_full(
        self,
        exchange_id: int,
        currency_from_code: str,
        currency_to_code: str,
        amount_from: float,
        amount_to: float,
        exchange_rate: float,
        fee: float,
        date: str,
        description: str = "",
    ) -> bool:
        """Update full currency exchange record.

        Args:

        - `exchange_id` (`int`): Exchange record ID.
        - `currency_from_code` (`str`): Source currency code.
        - `currency_to_code` (`str`): Target currency code.
        - `amount_from` (`float`): Amount from (in major units).
        - `amount_to` (`float`): Amount to (in major units).
        - `exchange_rate` (`float`): Exchange rate.
        - `fee` (`float`): Exchange fee (in major units).
        - `date` (`str`): Date in YYYY-MM-DD format.
        - `description` (`str`): Exchange description. Defaults to `""`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        try:
            # Get currency IDs
            from_currency_info = self.get_currency_by_code(currency_from_code)
            to_currency_info = self.get_currency_by_code(currency_to_code)

            if not from_currency_info or not to_currency_info:
                logger.warning("Currency not found: %s or %s", currency_from_code, currency_to_code)
                return False

            from_currency_id = from_currency_info[0]
            to_currency_id = to_currency_info[0]

            # Get currency subdivisions
            from_subdivision = self.get_currency_subdivision(from_currency_id)
            to_subdivision = self.get_currency_subdivision(to_currency_id)

            # Convert amounts to minor units
            amount_from_minor = int(amount_from * from_subdivision)
            amount_to_minor = int(amount_to * to_subdivision)
            fee_minor = int(fee * from_subdivision)

            # Update the exchange record
            query = """
                UPDATE currency_exchanges
                SET _id_currency_from = :from_id,
                    _id_currency_to = :to_id,
                    amount_from = :amount_from,
                    amount_to = :amount_to,
                    exchange_rate = :exchange_rate,
                    fee = :fee,
                    date = :date,
                    description = :description
                WHERE _id = :id
            """
            params = {
                "from_id": from_currency_id,
                "to_id": to_currency_id,
                "amount_from": amount_from_minor,
                "amount_to": amount_to_minor,
                "exchange_rate": exchange_rate,
                "fee": fee_minor,
                "date": date,
                "description": description,
                "id": exchange_id,
            }

            success = self.execute_simple_query(query, params)
            if success:
                logger.info("Successfully updated currency exchange %s in database", exchange_id)
            else:
                logger.error("Failed to update currency exchange %s in database", exchange_id)

        except Exception:
            logger.exception("Error updating currency exchange")
            return False

        return success

    def update_currency_ticker(self, currency_id: int, ticker: str) -> bool:
        """Update currency ticker.

        Args:

        - `currency_id` (`int`): Currency ID.
        - `ticker` (`str`): New ticker value.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        try:
            query = "UPDATE currencies SET ticker = :ticker WHERE _id = :id"
            params = {"ticker": ticker, "id": currency_id}
            return self.execute_simple_query(query, params)
        except Exception:
            logger.exception("Error updating currency ticker")
            return False

    def update_exchange_rate(self, currency_id: int, date: str, rate: float) -> bool:
        """Update or insert exchange rate for a specific currency and date.

        Args:

        - `currency_id` (`int`): Currency ID.
        - `date` (`str`): Date in YYYY-MM-DD format.
        - `rate` (`float`): Exchange rate (USD to currency).

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        return self.exchange_rates.update_exchange_rate(currency_id, date, rate)

    def update_transaction(
        self,
        transaction_id: int,
        amount: float,
        description: str,
        category_id: int,
        currency_id: int,
        date: str,
        tag: str = "",
    ) -> bool:
        """Update an existing transaction.

        Args:

        - `transaction_id` (`int`): Transaction ID.
        - `amount` (`float`): Transaction amount.
        - `description` (`str`): Transaction description.
        - `category_id` (`int`): Category ID.
        - `currency_id` (`int`): Currency ID.
        - `date` (`str`): Date in YYYY-MM-DD format.
        - `tag` (`str`): Transaction tag. Defaults to `""`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """UPDATE transactions SET amount = :amount, description = :description,
                   _id_categories = :category_id, _id_currencies = :currency_id,
                   date = :date, tag = :tag WHERE _id = :id"""
        params = {
            "amount": self.convert_to_minor_units(amount, currency_id),
            "description": description,
            "category_id": category_id,
            "currency_id": currency_id,
            "date": date,
            "tag": tag,
            "id": transaction_id,
        }
        return self.execute_simple_query(query, params)

    def _ensure_performance_indexes(self) -> None:
        """Create indexes for exchange_rates and transactions if missing (faster currency conversion)."""
        try:
            self.execute_simple_query(
                "CREATE INDEX IF NOT EXISTS idx_exchange_rates_currency_date ON exchange_rates(_id_currency, date)"
            )
            self.execute_simple_query(
                "CREATE INDEX IF NOT EXISTS idx_transactions_date_currency ON transactions(date, _id_currencies)"
            )
        except Exception:
            logger.exception("Could not ensure performance indexes")

    def _ensure_system_categories(self) -> None:
        """Ensure revision categories exist for balance reconciliation actions."""
        try:
            rows = self.get_rows(
                "SELECT name, type FROM categories WHERE name IN ('Revision Income', 'Revision Expense')"
            )
            existing = {(row[0], int(row[1])) for row in rows}
            if ("Revision Income", 1) not in existing:
                self.add_category("Revision Income", 1, "🧾")
            if ("Revision Expense", 0) not in existing:
                self.add_category("Revision Expense", 0, "🧾")
        except Exception:
            logger.exception("Could not ensure system categories")

    def _get_currency_conversion_sql(self, currency_id: int) -> tuple[str, str, dict]:
        """Generate SQL for currency conversion via USD.

        Args:

        - `currency_id` (`int`): Target currency ID.

        Returns:

        - `tuple[str, str, dict]`: (join_clause, conversion_case, extra_params).

        """
        # Check if there's data in exchange_rates for optimization
        try:
            check_query = "SELECT COUNT(*) FROM exchange_rates LIMIT 1"
            rows = self.get_rows(check_query)
            has_exchange_rates = rows and rows[0][0] > 0
        except Exception:
            has_exchange_rates = False

        # If there's no exchange rate data, return simplified version
        if not has_exchange_rates:
            # Without JOIN and conversion - just return amount as is
            join_clause = ""
            conversion_case = "t.amount"
            return join_clause, conversion_case, {}

        # If there's exchange rate data, use full version with conversion
        usd_currency = self.get_currency_by_code("USD")
        usd_currency_id = usd_currency[0] if usd_currency else None

        if currency_id == usd_currency_id:
            # Converting to USD - direct rates
            join_clause = """
            LEFT JOIN exchange_rates er ON er._id_currency = t._id_currencies
                                        AND er.date = (
                                            SELECT MAX(date)
                                            FROM exchange_rates er2
                                            WHERE er2._id_currency = t._id_currencies
                                            AND er2.date <= t.date
                                        )
            """
            conversion_case = """
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    ELSE COALESCE(er.rate * t.amount, t.amount)
                END
            """
            return join_clause, conversion_case, {}
        # Converting to non-USD currency via USD
        join_clause = """
            LEFT JOIN exchange_rates source_er ON source_er._id_currency = t._id_currencies
                                            AND source_er.date = (
                                                SELECT MAX(date)
                                                FROM exchange_rates ser2
                                                WHERE ser2._id_currency = t._id_currencies
                                                    AND ser2.date <= t.date
                                            )
            LEFT JOIN exchange_rates target_er ON target_er._id_currency = :currency_id
                                            AND target_er.date = (
                                                SELECT MAX(date)
                                                FROM exchange_rates ter2
                                                WHERE ter2._id_currency = :currency_id
                                                    AND ter2.date <= t.date
                                            )
            """
        conversion_case = """
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    WHEN t._id_currencies = :usd_currency_id THEN
                        COALESCE(t.amount / NULLIF(target_er.rate, 0), t.amount)
                    ELSE
                        COALESCE(source_er.rate * t.amount / NULLIF(target_er.rate, 0), t.amount)
                END
            """
        return join_clause, conversion_case, {"usd_currency_id": usd_currency_id}

    def _get_full_currency_conversion_sql(self, currency_id: int) -> tuple[str, str, dict]:
        """Generate full SQL for currency conversion via USD with exchange rates.

        This method should only be called when exchange rates are actually needed.

        Args:

        - `currency_id` (`int`): Target currency ID.

        Returns:

        - `tuple[str, str, dict]`: (join_clause, conversion_case, extra_params).

        """
        usd_currency = self.get_currency_by_code("USD")
        usd_currency_id = usd_currency[0] if usd_currency else None

        if currency_id == usd_currency_id:
            # Converting to USD - direct rates
            join_clause = """
            LEFT JOIN exchange_rates er ON er._id_currency = t._id_currencies
                                        AND er.date = (
                                            SELECT MAX(date)
                                            FROM exchange_rates er2
                                            WHERE er2._id_currency = t._id_currencies
                                            AND er2.date <= t.date
                                        )
            """
            conversion_case = """
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    ELSE COALESCE(er.rate * t.amount, t.amount)
                END
            """
            return join_clause, conversion_case, {}
        # Converting to non-USD currency via USD
        join_clause = """
            LEFT JOIN exchange_rates source_er ON source_er._id_currency = t._id_currencies
                                            AND source_er.date = (
                                                SELECT MAX(date)
                                                FROM exchange_rates ser2
                                                WHERE ser2._id_currency = t._id_currencies
                                                    AND ser2.date <= t.date
                                            )
            LEFT JOIN exchange_rates target_er ON target_er._id_currency = :currency_id
                                            AND target_er.date = (
                                                SELECT MAX(date)
                                                FROM exchange_rates ter2
                                                WHERE ter2._id_currency = :currency_id
                                                    AND ter2.date <= t.date
                                            )
            """
        conversion_case = """
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    WHEN t._id_currencies = :usd_currency_id THEN
                        COALESCE(t.amount / NULLIF(target_er.rate, 0), t.amount)
                    ELSE
                        COALESCE(source_er.rate * t.amount / NULLIF(target_er.rate, 0), t.amount)
                END
            """
        return join_clause, conversion_case, {"usd_currency_id": usd_currency_id}

    def _init_default_settings(self) -> None:
        """Initialize default settings if they don't exist."""
        try:
            # Check if default_currency setting exists
            rows = self.get_rows("SELECT COUNT(*) FROM settings WHERE key = 'default_currency'")
            if rows and rows[0][0] == 0:
                # Insert default currency setting (RUB has ID 1)
                self.execute_simple_query("INSERT INTO settings (key, value) VALUES ('default_currency', '1')")
                logger.info("Initialized default currency setting")
        except Exception:
            logger.exception("Could not initialize default settings")

    def _load_default_currency_cache(self) -> None:
        """Load default currency from DB into cache (once per run)."""
        if self._default_currency_cache is not None:
            return
        rows = self.get_rows("SELECT value FROM settings WHERE key = 'default_currency'")
        code = "RUB"
        currency_id = 1
        if rows:
            stored_value = rows[0][0]
            try:
                currency_id = int(stored_value)
                currency_info = self.get_currency_by_id(currency_id)
                if currency_info:
                    code = currency_info[0]
                else:
                    currency_id = 1
            except (ValueError, TypeError):
                code = stored_value or "RUB"
        self._default_currency_cache = (code, currency_id)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, db_filename: str) -> None
```

Open a connection to an SQLite database stored in `db_filename`.

Args:

- `db_filename` (`str`): The path to the target database file.

Raises:

- `ConnectionError`: If the underlying Qt driver fails to open the database.

<details>
<summary>Code:</summary>

```python
def __init__(self, db_filename: str) -> None:
        super().__init__(prefix="finance_db", db_filename=db_filename)

        self.exchange_rates = ExchangeRatesService(self)

        # Initialize default settings if they don't exist
        self._init_default_settings()
        self._ensure_system_categories()
        self._ensure_performance_indexes()

        # Cached default currency (code, id); loaded once from DB, updated only by set_default_currency
        self._default_currency_cache: tuple[str, int] | None = None
```

</details>

### ⚙️ Method `add_account`

```python
def add_account(self, name: str, balance: float, currency_id: int) -> bool
```

Add a new account to the database.

Args:

- `name` (`str`): Account name.
- `balance` (`float`): Initial balance.
- `currency_id` (`int`): Currency ID.
- `is_liquid` (`bool`): Whether account is liquid. Defaults to `True`.
- `is_cash` (`bool`): Whether account is cash. Defaults to `False`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_account(
        self, name: str, balance: float, currency_id: int, *, is_liquid: bool = True, is_cash: bool = False
    ) -> bool:
        query = """INSERT INTO accounts (name, balance, _id_currencies, is_liquid, is_cash)
                   VALUES (:name, :balance, :currency_id, :is_liquid, :is_cash)"""
        params = {
            "name": name,
            "balance": self.convert_to_minor_units(balance, currency_id),
            "currency_id": currency_id,
            "is_liquid": 1 if is_liquid else 0,
            "is_cash": 1 if is_cash else 0,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `add_category`

```python
def add_category(self, name: str, category_type: int, icon: str = "") -> bool
```

Add a new category to the database.

Args:

- `name` (`str`): Category name.
- `category_type` (`int`): Category type (0 = expense, 1 = income).
- `icon` (`str`): Category icon. Defaults to `""`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_category(self, name: str, category_type: int, icon: str = "") -> bool:
        query = "INSERT INTO categories (name, type, icon) VALUES (:name, :type, :icon)"
        params = {
            "name": name,
            "type": category_type,
            "icon": icon,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `add_currency`

```python
def add_currency(self, code: str, name: str, symbol: str, subdivision: int = 100) -> bool
```

Add a new currency to the database.

Args:

- `code` (`str`): Currency code (e.g., USD, EUR).
- `name` (`str`): Currency name.
- `symbol` (`str`): Currency symbol.
- `subdivision` (`int`): Number of minor units in one major unit (e.g., 100 for USD cents). Defaults to 100.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_currency(self, code: str, name: str, symbol: str, subdivision: int = 100) -> bool:
        query = "INSERT INTO currencies (code, name, symbol, subdivision) VALUES (:code, :name, :symbol, :subdivision)"
        params = {
            "code": code,
            "name": name,
            "symbol": symbol,
            "subdivision": subdivision,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `add_currency_exchange`

```python
def add_currency_exchange(self, currency_from_id: int, currency_to_id: int, amount_from: float, amount_to: float, exchange_rate: float, fee: float, date: str, description: str = "") -> bool
```

Add a new currency exchange record.

Args:

- `currency_from_id` (`int`): Source currency ID.
- `currency_to_id` (`int`): Target currency ID.
- `amount_from` (`float`): Amount in source currency.
- `amount_to` (`float`): Amount in target currency.
- `exchange_rate` (`float`): Exchange rate.
- `fee` (`float`): Exchange fee.
- `date` (`str`): Date in YYYY-MM-DD format.
- `description` (`str`): Exchange description. Defaults to `""`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_currency_exchange(
        self,
        currency_from_id: int,
        currency_to_id: int,
        amount_from: float,
        amount_to: float,
        exchange_rate: float,
        fee: float,
        date: str,
        description: str = "",
    ) -> bool:
        from_subdivision = self.get_currency_subdivision(currency_from_id)
        to_subdivision = self.get_currency_subdivision(currency_to_id)
        # Exchange rate is now stored as REAL directly
        query = """INSERT INTO currency_exchanges
                   (_id_currency_from, _id_currency_to, amount_from, amount_to,
                    exchange_rate, fee, date, description)
                   VALUES (:from_id, :to_id, :amount_from, :amount_to,
                           :exchange_rate, :fee, :date, :description)"""
        params = {
            "from_id": currency_from_id,
            "to_id": currency_to_id,
            "amount_from": int(amount_from * from_subdivision),  # Convert to minor units
            "amount_to": int(amount_to * to_subdivision),  # Convert to minor units
            "exchange_rate": exchange_rate,  # Store as REAL directly
            "fee": int(fee * from_subdivision),  # Fee in from_currency minor units
            "date": date,
            "description": description,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `add_exchange_rate`

```python
def add_exchange_rate(self, currency_id: int, rate: float, date: str) -> bool
```

Add a new exchange rate to USD.

Args:

- `currency_id` (`int`): Currency ID (rate is always to USD).
- `rate` (`float`): Exchange rate to USD.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_exchange_rate(self, currency_id: int, rate: float, date: str) -> bool:
        return self.exchange_rates.add_exchange_rate(currency_id, rate, date)
```

</details>

### ⚙️ Method `add_transaction`

```python
def add_transaction(self, amount: float, description: str, category_id: int, currency_id: int, date: str, tag: str = "") -> bool
```

Add a new transaction.

Args:

- `amount` (`float`): Transaction amount.
- `description` (`str`): Transaction description.
- `category_id` (`int`): Category ID.
- `currency_id` (`int`): Currency ID.
- `date` (`str`): Date in YYYY-MM-DD format.
- `tag` (`str`): Transaction tag. Defaults to `""`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_transaction(
        self,
        amount: float,
        description: str,
        category_id: int,
        currency_id: int,
        date: str,
        tag: str = "",
    ) -> bool:
        query = """INSERT INTO transactions (amount, description, _id_categories, _id_currencies, date, tag)
                   VALUES (:amount, :description, :category_id, :currency_id, :date, :tag)"""
        params = {
            "amount": self.convert_to_minor_units(amount, currency_id),
            "description": description,
            "category_id": category_id,
            "currency_id": currency_id,
            "date": date,
            "tag": tag,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `check_exchange_rate_exists`

```python
def check_exchange_rate_exists(self, currency_id: int, date: str) -> bool
```

Check if exchange rate to USD exists for given currency and date.

Args:

- `currency_id` (`int`): Currency ID.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `bool`: True if exchange rate exists, False otherwise.

<details>
<summary>Code:</summary>

```python
def check_exchange_rate_exists(self, currency_id: int, date: str) -> bool:
        return self.exchange_rates.check_exchange_rate_exists(currency_id, date)
```

</details>

### ⚙️ Method `clean_invalid_exchange_rates`

```python
def clean_invalid_exchange_rates(self) -> int
```

Clean exchange rates with empty or invalid rate values.

Returns:

- `int`: Number of cleaned records.

<details>
<summary>Code:</summary>

```python
def clean_invalid_exchange_rates(self) -> int:
        return self.exchange_rates.clean_invalid_exchange_rates()
```

</details>

### ⚙️ Method `close`

```python
def close(self) -> None
```

Close the database connection.

<details>
<summary>Code:</summary>

```python
def close(self) -> None:
        self._default_currency_cache = None
        self.exchange_rates.clear_cache()
        super().close()
```

</details>

### ⚙️ Method `convert_from_minor_units`

```python
def convert_from_minor_units(self, amount_minor: float, currency_id: int) -> float
```

Convert amount from minor units to major units using currency subdivision.

Args:

- `amount_minor` (`int | float`): Amount in minor units (e.g., cents).
- `currency_id` (`int`): Currency ID.

Returns:

- `float`: Amount in major units (e.g., dollars).

<details>
<summary>Code:</summary>

```python
def convert_from_minor_units(self, amount_minor: float, currency_id: int) -> float:
        subdivision = self.get_currency_subdivision(currency_id)
        return float(amount_minor) / subdivision
```

</details>

### ⚙️ Method `convert_to_minor_units`

```python
def convert_to_minor_units(self, amount_major: float, currency_id: int) -> int
```

Convert amount from major units to minor units using currency subdivision.

Args:

- `amount_major` (`float`): Amount in major units (e.g., dollars).
- `currency_id` (`int`): Currency ID.

Returns:

- `int`: Amount in minor units (e.g., cents).

<details>
<summary>Code:</summary>

```python
def convert_to_minor_units(self, amount_major: float, currency_id: int) -> int:
        subdivision = self.get_currency_subdivision(currency_id)
        return int(amount_major * subdivision)
```

</details>

### ⚙️ Method `delete_account`

```python
def delete_account(self, account_id: int) -> bool
```

Delete an account from the database.

Args:

- `account_id` (`int`): Account ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_account(self, account_id: int) -> bool:
        query = "DELETE FROM accounts WHERE _id = :id"
        return self.execute_simple_query(query, {"id": account_id})
```

</details>

### ⚙️ Method `delete_category`

```python
def delete_category(self, category_id: int) -> bool
```

Delete a category from the database.

Args:

- `category_id` (`int`): Category ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_category(self, category_id: int) -> bool:
        query = "DELETE FROM categories WHERE _id = :id"
        return self.execute_simple_query(query, {"id": category_id})
```

</details>

### ⚙️ Method `delete_currency`

```python
def delete_currency(self, currency_id: int) -> bool
```

Delete a currency from the database.

Args:

- `currency_id` (`int`): Currency ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_currency(self, currency_id: int) -> bool:
        query = "DELETE FROM currencies WHERE _id = :id"
        return self.execute_simple_query(query, {"id": currency_id})
```

</details>

### ⚙️ Method `delete_currency_exchange`

```python
def delete_currency_exchange(self, exchange_id: int) -> bool
```

Delete a currency exchange record.

Args:

- `exchange_id` (`int`): Exchange ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_currency_exchange(self, exchange_id: int) -> bool:
        query = "DELETE FROM currency_exchanges WHERE _id = :id"
        return self.execute_simple_query(query, {"id": exchange_id})
```

</details>

### ⚙️ Method `delete_exchange_rate`

```python
def delete_exchange_rate(self, rate_id: int) -> bool
```

Delete an exchange rate.

Args:

- `rate_id` (`int`): Rate ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_exchange_rate(self, rate_id: int) -> bool:
        return self.exchange_rates.delete_exchange_rate(rate_id)
```

</details>

### ⚙️ Method `delete_exchange_rates_by_days`

```python
def delete_exchange_rates_by_days(self, days: int) -> tuple[bool, int]
```

Delete exchange rates for the last N days for each currency.

Args:

- `days` (`int`): Number of days to look back from current date.

Returns:

- `tuple[bool, int]`: (success, deleted_count) where success is True if
  the operation completed successfully, and deleted_count is the number
  of records deleted.

<details>
<summary>Code:</summary>

```python
def delete_exchange_rates_by_days(self, days: int) -> tuple[bool, int]:
        return self.exchange_rates.delete_exchange_rates_by_days(days)
```

</details>

### ⚙️ Method `delete_transaction`

```python
def delete_transaction(self, transaction_id: int) -> bool
```

Delete a transaction.

Args:

- `transaction_id` (`int`): Transaction ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_transaction(self, transaction_id: int) -> bool:
        query = "DELETE FROM transactions WHERE _id = :id"
        return self.execute_simple_query(query, {"id": transaction_id})
```

</details>

### ⚙️ Method `fill_missing_exchange_rates`

```python
def fill_missing_exchange_rates(self) -> int
```

Fill missing exchange rates with previous available rates for all date gaps.

Returns:

- `int`: Number of exchange rates that were filled.

<details>
<summary>Code:</summary>

```python
def fill_missing_exchange_rates(self) -> int:
        return self.exchange_rates.fill_missing_exchange_rates()
```

</details>

### ⚙️ Method `get_account_balances_in_currency`

```python
def get_account_balances_in_currency(self, currency_id: int) -> list[tuple[str, float]]
```

Get all account balances converted to specified currency.

Args:

- `currency_id` (`int`): Target currency ID.

Returns:

- `list[tuple[str, float]]`: List of (account_name, balance) tuples in target currency.

<details>
<summary>Code:</summary>

```python
def get_account_balances_in_currency(self, currency_id: int) -> list[tuple[str, float]]:
        # Get USD currency ID for conversion calculations
        usd_currency = self.get_currency_by_code("USD")
        usd_currency_id = usd_currency[0] if usd_currency else None

        if currency_id == usd_currency_id:
            # Converting to USD - direct rates
            query = """
                SELECT a.name,
                       CASE
                           WHEN a._id_currencies = :currency_id THEN a.balance
                           ELSE COALESCE(er.rate * a.balance, a.balance)
                       END as converted_balance
                FROM accounts a
                LEFT JOIN exchange_rates er ON er._id_currency = a._id_currencies
                                            AND er.date = (
                                                SELECT MAX(date)
                                                FROM exchange_rates er2
                                                WHERE er2._id_currency = a._id_currencies
                                                  AND er2.date <= date('now')
                                            )
                ORDER BY a.name
            """
        else:
            # Converting to non-USD currency via USD
            query = """
                SELECT a.name,
                       CASE
                           WHEN a._id_currencies = :currency_id THEN a.balance
                           WHEN a._id_currencies = :usd_currency_id THEN
                               COALESCE(a.balance / NULLIF(target_er.rate, 0), a.balance)
                           ELSE
                               COALESCE(source_er.rate * a.balance / NULLIF(target_er.rate, 0), a.balance)
                       END as converted_balance
                FROM accounts a
                LEFT JOIN exchange_rates source_er ON source_er._id_currency = a._id_currencies
                                                   AND source_er.date = (
                                                       SELECT MAX(date)
                                                       FROM exchange_rates ser2
                                                       WHERE ser2._id_currency = a._id_currencies
                                                         AND ser2.date <= date('now')
                                                   )
                LEFT JOIN exchange_rates target_er ON target_er._id_currency = :currency_id
                                                   AND target_er.date = (
                                                       SELECT MAX(date)
                                                       FROM exchange_rates ter2
                                                       WHERE ter2._id_currency = :currency_id
                                                         AND ter2.date <= date('now')
                                                   )
                ORDER BY a.name
            """
        if currency_id == usd_currency_id:
            rows = self.get_rows(query, {"currency_id": currency_id})
        else:
            rows = self.get_rows(query, {"currency_id": currency_id, "usd_currency_id": usd_currency_id})
        return [(row[0], float(row[1]) / 100) for row in rows]
```

</details>

### ⚙️ Method `get_account_by_id`

```python
def get_account_by_id(self, account_id: int) -> list[Any] | None
```

Get account data by ID.

Args:

- `account_id` (`int`): Account ID.

Returns:

- `list[Any] | None`: Account data or None if not found.

<details>
<summary>Code:</summary>

```python
def get_account_by_id(self, account_id: int) -> list[Any] | None:
        query = """
            SELECT a._id, a.name, a.balance, c.code, a.is_liquid, a.is_cash, c._id as currency_id
            FROM accounts a
            JOIN currencies c ON a._id_currencies = c._id
            WHERE a._id = :account_id
        """
        rows = self.get_rows(query, {"account_id": account_id})
        return rows[0] if rows else None
```

</details>

### ⚙️ Method `get_all_accounts`

```python
def get_all_accounts(self) -> list[list[Any]]
```

Get all accounts with currency information.

Returns:

- `list[list[Any]]`: List of account records [_id, name, balance, currency_code,
  is_liquid, is_cash, currency_id].

<details>
<summary>Code:</summary>

```python
def get_all_accounts(self) -> list[list[Any]]:
        return self.get_rows("""
            SELECT a._id, a.name, a.balance, c.code, a.is_liquid, a.is_cash, c._id as currency_id
            FROM accounts a
            JOIN currencies c ON a._id_currencies = c._id
            ORDER BY a.name
        """)
```

</details>

### ⚙️ Method `get_all_categories`

```python
def get_all_categories(self) -> list[list[Any]]
```

Get all categories.

Returns:

- `list[list[Any]]`: List of category records [_id, name, type, icon].

<details>
<summary>Code:</summary>

```python
def get_all_categories(self) -> list[list[Any]]:
        return self.get_rows("SELECT _id, name, type, icon FROM categories ORDER BY type, name")
```

</details>

### ⚙️ Method `get_all_currencies`

```python
def get_all_currencies(self) -> list[list[Any]]
```

Get all currencies.

Returns:

- `list[list[Any]]`: List of currency records [_id, code, name, symbol].

<details>
<summary>Code:</summary>

```python
def get_all_currencies(self) -> list[list[Any]]:
        return self.get_rows("SELECT _id, code, name, symbol FROM currencies ORDER BY code")
```

</details>

### ⚙️ Method `get_all_currency_exchanges`

```python
def get_all_currency_exchanges(self) -> list[list[Any]]
```

Get all currency exchange records with currency information.

Returns:

- `list[list[Any]]`: List of exchange records.

<details>
<summary>Code:</summary>

```python
def get_all_currency_exchanges(self) -> list[list[Any]]:
        rows = self.get_rows("""
            SELECT ce._id, cf.code, ct.code, ce.amount_from, ce.amount_to,
                   ce.exchange_rate, ce.fee, ce.date, ce.description
            FROM currency_exchanges ce
            JOIN currencies cf ON ce._id_currency_from = cf._id
            JOIN currencies ct ON ce._id_currency_to = ct._id
            ORDER BY ce.date DESC, ce._id DESC
        """)

        # Return raw values (in minor units) - conversion will be done in the UI layer
        # Just ensure exchange_rate is float type for consistency
        exchange_rate_index = 5  # Use a constant instead of magic number
        for row in rows:
            if len(row) > exchange_rate_index and row[exchange_rate_index] is not None:
                try:
                    row[exchange_rate_index] = float(row[exchange_rate_index])
                except (ValueError, TypeError):
                    row[exchange_rate_index] = 0.0  # Set to 0 for invalid values
            elif len(row) > exchange_rate_index:
                row[exchange_rate_index] = 0.0  # Set to 0 for None

        return rows
```

</details>

### ⚙️ Method `get_all_exchange_rates`

```python
def get_all_exchange_rates(self, limit: int | None = None) -> list[list[Any]]
```

Get all exchange rates with currency information.

Args:

- `limit` (`int | None`): Maximum number of records to return. None for all records. Defaults to `None`.

Returns:

- `list[list[Any]]`: List of exchange rate records.

<details>
<summary>Code:</summary>

```python
def get_all_exchange_rates(self, limit: int | None = None) -> list[list[Any]]:
        return self.exchange_rates.get_all_exchange_rates(limit)
```

</details>

### ⚙️ Method `get_all_transactions`

```python
def get_all_transactions(self, limit: int | None = None) -> list[list[Any]]
```

Get all transactions with category and currency information.

Args:

- `limit` (`int | None`): Limit number of records. Defaults to `None` (no limit).

Returns:

- `list[list[Any]]`: List of transaction records.

<details>
<summary>Code:</summary>

```python
def get_all_transactions(self, limit: int | None = None) -> list[list[Any]]:
        query = """
            SELECT t._id, t.amount, t.description, cat.name, c.code, t.date, t.tag,
                   cat.type, cat.icon, c.symbol
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            JOIN currencies c ON t._id_currencies = c._id
            ORDER BY t.date DESC, t._id DESC
        """

        params: dict[str, Any] | None = None
        if limit is not None:
            query += " LIMIT :limit"
            params = {"limit": limit}

        return self.get_rows(query, params)
```

</details>

### ⚙️ Method `get_categories_by_type`

```python
def get_categories_by_type(self, category_type: int) -> list[str]
```

Get category names by type.

Args:

- `category_type` (`int`): Category type (0 = expense, 1 = income).

Returns:

- `list[str]`: List of category names.

<details>
<summary>Code:</summary>

```python
def get_categories_by_type(self, category_type: int) -> list[str]:
        rows = self.get_rows("SELECT name FROM categories WHERE type = :type ORDER BY name", {"type": category_type})
        return [row[0] for row in rows]
```

</details>

### ⚙️ Method `get_categories_with_icons_by_type`

```python
def get_categories_with_icons_by_type(self, category_type: int) -> list[tuple[str, str]]
```

Get category names and icons by type.

Args:

- `category_type` (`int`): Category type (0 = expense, 1 = income).

Returns:

- `list[tuple[str, str]]`: List of (name, icon) tuples.

<details>
<summary>Code:</summary>

```python
def get_categories_with_icons_by_type(self, category_type: int) -> list[tuple[str, str]]:
        rows = self.get_rows(
            "SELECT name, icon FROM categories WHERE type = :type ORDER BY name", {"type": category_type}
        )
        return [(row[0], row[1]) for row in rows]
```

</details>

### ⚙️ Method `get_category_by_id`

```python
def get_category_by_id(self, category_id: int) -> list[Any] | None
```

Get category by ID.

Args:

- `category_id` (`int`): The category ID to retrieve.

Returns:

- `list[Any] | None`: Category data [_id, name, type, icon] or None if not found.

<details>
<summary>Code:</summary>

```python
def get_category_by_id(self, category_id: int) -> list[Any] | None:
        query = "SELECT _id, name, type, icon FROM categories WHERE _id = :category_id"
        rows = self.get_rows(query, {"category_id": category_id})
        return rows[0] if rows else None
```

</details>

### ⚙️ Method `get_currencies_except_usd`

```python
def get_currencies_except_usd(self) -> list[list[Any]]
```

Get all currencies except USD (which is the base currency).

Returns:

- `list[list[Any]]`: List of currency records [_id, code, name, symbol] excluding USD.

<details>
<summary>Code:</summary>

```python
def get_currencies_except_usd(self) -> list[list[Any]]:
        return self.get_rows("SELECT _id, code, name, symbol FROM currencies WHERE code != 'USD' ORDER BY code")
```

</details>

### ⚙️ Method `get_currency_by_code`

```python
def get_currency_by_code(self, code: str) -> tuple[int, str, str] | None
```

Get currency information by code.

Args:

- `code` (`str`): Currency code.

Returns:

- `tuple[int, str, str] | None`: Tuple of (id, name, symbol) or None if not found.

<details>
<summary>Code:</summary>

```python
def get_currency_by_code(self, code: str) -> tuple[int, str, str] | None:
        rows = self.get_rows("SELECT _id, name, symbol FROM currencies WHERE code = :code", {"code": code})
        return (rows[0][0], rows[0][1], rows[0][2]) if rows else None
```

</details>

### ⚙️ Method `get_currency_by_id`

```python
def get_currency_by_id(self, currency_id: int) -> tuple[str, str, str] | None
```

Get currency information by ID.

Args:

- `currency_id` (`int`): Currency ID.

Returns:

- `tuple[str, str, str] | None`: Tuple of (code, name, symbol) or None if not found.

<details>
<summary>Code:</summary>

```python
def get_currency_by_id(self, currency_id: int) -> tuple[str, str, str] | None:
        rows = self.get_rows("SELECT code, name, symbol FROM currencies WHERE _id = :id", {"id": currency_id})
        return (rows[0][0], rows[0][1], rows[0][2]) if rows else None
```

</details>

### ⚙️ Method `get_currency_exchange_rate_by_date`

```python
def get_currency_exchange_rate_by_date(self, currency_id: int, date: str) -> float
```

Get exchange rate for a specific currency on a specific date.

Args:

- `currency_id` (`int`): Currency ID.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `float`: Exchange rate (USD to currency) or 1.0 if not found.

<details>
<summary>Code:</summary>

```python
def get_currency_exchange_rate_by_date(self, currency_id: int, date: str) -> float:
        return self.exchange_rates.get_currency_exchange_rate_by_date(currency_id, date)
```

</details>

### ⚙️ Method `get_currency_subdivision`

```python
def get_currency_subdivision(self, currency_id: int) -> int
```

Get subdivision value for a currency.

Args:

- `currency_id` (`int`): Currency ID.

Returns:

- `int`: Number of minor units in one major unit (e.g., 100 for USD cents). Returns 100 as default if not found.

<details>
<summary>Code:</summary>

```python
def get_currency_subdivision(self, currency_id: int) -> int:
        rows = self.get_rows("SELECT subdivision FROM currencies WHERE _id = :id", {"id": currency_id})
        return rows[0][0] if rows else 100
```

</details>

### ⚙️ Method `get_currency_subdivision_by_code`

```python
def get_currency_subdivision_by_code(self, currency_code: str) -> int
```

Get subdivision value for a currency by currency code.

Args:

- `currency_code` (`str`): Currency code (e.g., 'USD', 'EUR').

Returns:

- `int`: Number of minor units in one major unit (e.g., 100 for USD cents). Returns 100 as default if not found.

<details>
<summary>Code:</summary>

```python
def get_currency_subdivision_by_code(self, currency_code: str) -> int:
        rows = self.get_rows("SELECT subdivision FROM currencies WHERE code = :code", {"code": currency_code})
        return rows[0][0] if rows else 100
```

</details>

### ⚙️ Method `get_currency_ticker`

```python
def get_currency_ticker(self, currency_id: int) -> str | None
```

Get currency ticker by ID.

Args:

- `currency_id` (`int`): Currency ID.

Returns:

- `str | None`: Currency ticker or None if not found or empty.

<details>
<summary>Code:</summary>

```python
def get_currency_ticker(self, currency_id: int) -> str | None:
        rows = self.get_rows("SELECT ticker FROM currencies WHERE _id = :id", {"id": currency_id})
        if rows and rows[0][0] and rows[0][0].strip():
            return rows[0][0].strip()
        return None
```

</details>

### ⚙️ Method `get_default_currency`

```python
def get_default_currency(self) -> str
```

Get the default currency code (from in-memory cache, not DB).

Returns:

- `str`: Default currency code or 'RUB' if not set.

<details>
<summary>Code:</summary>

```python
def get_default_currency(self) -> str:
        self._load_default_currency_cache()
        if self._default_currency_cache:
            return self._default_currency_cache[0]
        return "RUB"
```

</details>

### ⚙️ Method `get_default_currency_id`

```python
def get_default_currency_id(self) -> int
```

Get the default currency ID (from in-memory cache, not DB).

Returns:

- `int`: Default currency ID or 1 if not found.

<details>
<summary>Code:</summary>

```python
def get_default_currency_id(self) -> int:
        self._load_default_currency_cache()
        if self._default_currency_cache:
            return self._default_currency_cache[1]
        return 1
```

</details>

### ⚙️ Method `get_earliest_currency_exchange_date`

```python
def get_earliest_currency_exchange_date(self) -> str | None
```

Get the earliest date from currency_exchanges table.

Returns:

- `str | None`: Earliest date in YYYY-MM-DD format or None if no records exist.

<details>
<summary>Code:</summary>

```python
def get_earliest_currency_exchange_date(self) -> str | None:
        rows = self.get_rows("SELECT MIN(date) FROM currency_exchanges")
        return rows[0][0] if rows and rows[0][0] else None
```

</details>

### ⚙️ Method `get_earliest_financial_date`

```python
def get_earliest_financial_date(self) -> str | None
```

Get the earliest date from either transactions or currency_exchanges tables.

Returns:

- `str | None`: Earliest date in YYYY-MM-DD format or None if no records exist.

<details>
<summary>Code:</summary>

```python
def get_earliest_financial_date(self) -> str | None:
        transaction_date = self.get_earliest_transaction_date()
        exchange_date = self.get_earliest_currency_exchange_date()

        # Return the earliest of the two dates
        if transaction_date and exchange_date:
            return min(transaction_date, exchange_date)
        if transaction_date:
            return transaction_date
        if exchange_date:
            return exchange_date
        return None
```

</details>

### ⚙️ Method `get_earliest_transaction_date`

```python
def get_earliest_transaction_date(self) -> str | None
```

Get the earliest date from transactions table.

Returns:

- `str | None`: Earliest date in YYYY-MM-DD format or None if no records exist.

<details>
<summary>Code:</summary>

```python
def get_earliest_transaction_date(self) -> str | None:
        rows = self.get_rows("SELECT MIN(date) FROM transactions WHERE date IS NOT NULL")
        return rows[0][0] if rows and rows[0][0] else None
```

</details>

### ⚙️ Method `get_exchange_rate`

```python
def get_exchange_rate(self, from_currency_id: int, to_currency_id: int, date: str | None = None) -> float
```

Get exchange rate between currencies (both referenced to USD).

Args:

- `from_currency_id` (`int`): Source currency ID.
- `to_currency_id` (`int`): Target currency ID.
- `date` (`str | None`): Date for rate lookup. Uses latest if None.

Returns:

- `float`: Exchange rate or 1.0 if not found/same currency.

<details>
<summary>Code:</summary>

```python
def get_exchange_rate(self, from_currency_id: int, to_currency_id: int, date: str | None = None) -> float:
        return self.exchange_rates.get_exchange_rate(from_currency_id, to_currency_id, date)
```

</details>

### ⚙️ Method `get_filtered_exchange_rates`

```python
def get_filtered_exchange_rates(self, currency_id: int | None = None, date_from: str | None = None, date_to: str | None = None, limit: int | None = None) -> list[list[Any]]
```

Get filtered exchange rates with currency information.

Args:

- `currency_id` (`int | None`): Currency ID to filter by. None for all currencies.
- `date_from` (`str | None`): Start date in YYYY-MM-DD format. None for no start date filter.
- `date_to` (`str | None`): End date in YYYY-MM-DD format. None for no end date filter.
- `limit` (`int | None`): Maximum number of records to return. None for all records.

Returns:

- `list[list[Any]]`: List of filtered exchange rate records.

<details>
<summary>Code:</summary>

```python
def get_filtered_exchange_rates(
        self,
        currency_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        return self.exchange_rates.get_filtered_exchange_rates(currency_id, date_from, date_to, limit)
```

</details>

### ⚙️ Method `get_filtered_transactions`

```python
def get_filtered_transactions(self, category_type: int | None = None, category_name: str | None = None, currency_code: str | None = None, date_from: str | None = None, date_to: str | None = None, description_filter: str | None = None) -> list[list[Any]]
```

Get filtered transactions.

Args:

- `category_type` (`int | None`): Filter by category type. Defaults to `None`.
- `category_name` (`str | None`): Filter by category name. Defaults to `None`.
- `currency_code` (`str | None`): Filter by currency code. Defaults to `None`.
- `date_from` (`str | None`): Filter from date. Defaults to `None`.
- `date_to` (`str | None`): Filter to date. Defaults to `None`.
- `description_filter` (`str | None`): Filter by description substring (case insensitive). Defaults to `None`.

Returns:

- `list[list[Any]]`: List of filtered transaction records.

<details>
<summary>Code:</summary>

```python
def get_filtered_transactions(
        self,
        category_type: int | None = None,
        category_name: str | None = None,
        currency_code: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        description_filter: str | None = None,
    ) -> list[list[Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}

        if category_type is not None:
            conditions.append("cat.type = :category_type")
            params["category_type"] = category_type

        if category_name:
            conditions.append("cat.name = :category_name")
            params["category_name"] = category_name

        if currency_code:
            conditions.append("c.code = :currency_code")
            params["currency_code"] = currency_code

        if date_from and date_to:
            conditions.append("t.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        if description_filter:
            conditions.append("LOWER(t.description) LIKE :description_filter")
            params["description_filter"] = f"%{description_filter.lower()}%"

        query_text = """
            SELECT t._id, t.amount, t.description, cat.name, c.code, t.date, t.tag,
                   cat.type, cat.icon, c.symbol
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            JOIN currencies c ON t._id_currencies = c._id
        """

        if conditions:
            query_text += " WHERE " + " AND ".join(conditions)

        query_text += " ORDER BY t.date DESC, t._id DESC"

        return self.get_rows(query_text, params)
```

</details>

### ⚙️ Method `get_income_vs_expenses_in_currency`

```python
def get_income_vs_expenses_in_currency(self, currency_id: int, date_from: str | None = None, date_to: str | None = None) -> tuple[float, float]
```

Get total income and expenses in specified currency.

Args:

- `currency_id` (`int`): Target currency ID.
- `date_from` (`str | None`): From date. Defaults to `None`.
- `date_to` (`str | None`): To date. Defaults to `None`.

Returns:

- `tuple[float, float]`: Tuple of (total_income, total_expenses) in target currency.

<details>
<summary>Code:</summary>

```python
def get_income_vs_expenses_in_currency(
        self, currency_id: int, date_from: str | None = None, date_to: str | None = None
    ) -> tuple[float, float]:
        conditions = []
        params: dict[str, Any] = {"currency_id": currency_id}

        if date_from and date_to:
            conditions.append("t.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        where_clause = " AND " + " AND ".join(conditions) if conditions else ""

        # Get currency conversion SQL
        join_clause, conversion_case, extra_params = self._get_currency_conversion_sql(currency_id)
        params.update(extra_params)

        # Get income (category type = 1)
        income_query = f"""
            SELECT SUM({conversion_case}) as total_income
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            {join_clause}
            WHERE cat.type = 1{where_clause}
        """

        # Get expenses (category type = 0)
        expenses_query = f"""
            SELECT SUM({conversion_case}) as total_expenses
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            {join_clause}
            WHERE cat.type = 0{where_clause}
        """

        income_rows = self.get_rows(income_query, params)
        expenses_rows = self.get_rows(expenses_query, params)

        total_income = float(income_rows[0][0] or 0) / 100 if income_rows and income_rows[0][0] else 0.0
        total_expenses = float(expenses_rows[0][0] or 0) / 100 if expenses_rows and expenses_rows[0][0] else 0.0

        return total_income, total_expenses
```

</details>

### ⚙️ Method `get_last_exchange_rate_date`

```python
def get_last_exchange_rate_date(self, currency_id: int) -> str | None
```

Get the last date for which exchange rate exists for a currency.

Args:

- `currency_id` (`int`): Currency ID.

Returns:

- `str | None`: Last date in YYYY-MM-DD format or None if no rates exist.

<details>
<summary>Code:</summary>

```python
def get_last_exchange_rate_date(self, currency_id: int) -> str | None:
        return self.exchange_rates.get_last_exchange_rate_date(currency_id)
```

</details>

### ⚙️ Method `get_last_two_exchange_rate_records`

```python
def get_last_two_exchange_rate_records(self, currency_id: int) -> list[tuple[str, float]]
```

Get the last two exchange rate records for a currency.

Args:

- `currency_id` (`int`): Currency ID.

Returns:

- `list[tuple[str, float]]`: List of tuples (date, rate) for the last two records, sorted by date.

<details>
<summary>Code:</summary>

```python
def get_last_two_exchange_rate_records(self, currency_id: int) -> list[tuple[str, float]]:
        return self.exchange_rates.get_last_two_exchange_rate_records(currency_id)
```

</details>

### ⚙️ Method `get_missing_exchange_rates_info`

```python
def get_missing_exchange_rates_info(self, date_from: str, date_to: str) -> dict[int, list[str]]
```

Get information about missing exchange rates for each currency.

Checks for missing rates for each day in the date range.

Args:

- `date_from` (`str`): Start date in YYYY-MM-DD format.
- `date_to` (`str`): End date in YYYY-MM-DD format.

Returns:

- `dict[int, list[str]]`: Dictionary mapping currency_id to list of missing dates.

<details>
<summary>Code:</summary>

```python
def get_missing_exchange_rates_info(self, date_from: str, date_to: str) -> dict[int, list[str]]:
        return self.exchange_rates.get_missing_exchange_rates_info(date_from, date_to)
```

</details>

### ⚙️ Method `get_recent_transaction_descriptions_for_autocomplete`

```python
def get_recent_transaction_descriptions_for_autocomplete(self, limit: int = 1000) -> list[str]
```

Get recent unique transaction descriptions for autocomplete.

Args:

- `limit` (`int`): Number of recent transactions to analyze. Defaults to `1000`.

Returns:

- `list[str]`: List of unique transaction descriptions.

<details>
<summary>Code:</summary>

```python
def get_recent_transaction_descriptions_for_autocomplete(self, limit: int = 1000) -> list[str]:
        # Get descriptions ordered by frequency (most used first) and then by recency
        # Also include recent unique descriptions that might not be frequent
        query = """
            WITH frequent_descriptions AS (
                SELECT t.description, COUNT(*) as usage_count, MAX(t.date) as last_used
                FROM transactions t
                WHERE t.description IS NOT NULL AND t.description != ''
                GROUP BY t.description
                ORDER BY usage_count DESC, last_used DESC
                LIMIT :limit_frequent
            ),
            recent_descriptions AS (
                SELECT DISTINCT t.description
                FROM transactions t
                WHERE t.description IS NOT NULL AND t.description != ''
                ORDER BY t._id DESC
                LIMIT :limit_recent
            )
            SELECT DISTINCT description
            FROM (
                SELECT description FROM frequent_descriptions
                UNION
                SELECT description FROM recent_descriptions
            )
            ORDER BY description
        """

        # Use 70% for frequent, 30% for recent
        limit_frequent_percentage = 0.7
        limit_frequent = int(limit * limit_frequent_percentage)
        limit_recent = limit - limit_frequent

        rows = self.get_rows(query, {"limit_frequent": limit_frequent, "limit_recent": limit_recent})
        return [row[0] for row in rows if row[0]]
```

</details>

### ⚙️ Method `get_today_balance_in_currency`

```python
def get_today_balance_in_currency(self, currency_id: int) -> float
```

Get today's balance (income - expenses) in specified currency.

Args:

- `currency_id` (`int`): Target currency ID.

Returns:

- `float`: Today's balance in target currency.

<details>
<summary>Code:</summary>

```python
def get_today_balance_in_currency(self, currency_id: int) -> float:
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        total_income, total_expenses = self.get_income_vs_expenses_in_currency(currency_id, today, today)
        return total_income - total_expenses
```

</details>

### ⚙️ Method `get_today_expenses_in_currency`

```python
def get_today_expenses_in_currency(self, currency_id: int) -> float
```

Get today's expenses in specified currency.

Args:

- `currency_id` (`int`): Currency ID for conversion.

Returns:

- `float`: Today's expenses in the specified currency.

<details>
<summary>Code:</summary>

```python
def get_today_expenses_in_currency(self, currency_id: int) -> float:
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        _, expenses = self.get_income_vs_expenses_in_currency(currency_id, today, today)
        return expenses
```

</details>

### ⚙️ Method `get_total_accounts_balance_in_currency`

```python
def get_total_accounts_balance_in_currency(self, currency_id: int | None = None) -> float
```

Get total balance across all accounts in given or default currency.

Sums balances of all accounts converted to the target currency (by current
exchange rates). Used e.g. for label_balance_accounts.

Args:

- `currency_id` (`int | None`): Target currency ID. If None, uses default currency.

Returns:

- `float`: Total balance in target currency (major units).

<details>
<summary>Code:</summary>

```python
def get_total_accounts_balance_in_currency(self, currency_id: int | None = None) -> float:
        if currency_id is None:
            currency_id = self.get_default_currency_id()
        balances: list[tuple[str, float]] = self.get_account_balances_in_currency(currency_id)
        return sum(balance for _name, balance in balances)
```

</details>

### ⚙️ Method `get_transaction_by_id`

```python
def get_transaction_by_id(self, transaction_id: int) -> list[Any] | None
```

Get transaction by ID with category and currency information.

Args:

- `transaction_id` (`int`): The transaction ID to retrieve.

Returns:

- `list[Any] | None`: Transaction data [id, amount, description, category_id,
  currency_id, date, tag] or None if not found.

<details>
<summary>Code:</summary>

```python
def get_transaction_by_id(self, transaction_id: int) -> list[Any] | None:
        query = """
            SELECT t._id, t.amount, t.description, t._id_categories, t._id_currencies, t.date, t.tag
            FROM transactions t
            WHERE t._id = :transaction_id
        """

        rows = self.get_rows(query, {"transaction_id": transaction_id})
        return rows[0] if rows else None
```

</details>

### ⚙️ Method `get_transactions_chart_data`

```python
def get_transactions_chart_data(self, currency_id: int, category_type: int | None = None, date_from: str | None = None, date_to: str | None = None) -> list[tuple[str, float]]
```

Get transaction data for charting in specified currency.

Args:

- `currency_id` (`int`): Target currency ID.
- `category_type` (`int | None`): Category type filter. Defaults to `None`.
- `date_from` (`str | None`): From date. Defaults to `None`.
- `date_to` (`str | None`): To date. Defaults to `None`.

Returns:

- `list[tuple[str, float]]`: List of (date, amount) tuples in target currency.

<details>
<summary>Code:</summary>

```python
def get_transactions_chart_data(
        self,
        currency_id: int,
        category_type: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[tuple[str, float]]:
        conditions = []
        params: dict[str, Any] = {"currency_id": currency_id}

        if category_type is not None:
            conditions.append("cat.type = :category_type")
            params["category_type"] = category_type

        if date_from and date_to:
            conditions.append("t.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        where_clause = " AND " + " AND ".join(conditions) if conditions else ""

        # Get currency conversion SQL
        join_clause, conversion_case, extra_params = self._get_currency_conversion_sql(currency_id)
        params.update(extra_params)

        query = f"""
            SELECT t.date, SUM({conversion_case}) as total_amount
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            {join_clause}
            WHERE 1=1{where_clause}
            GROUP BY t.date
            ORDER BY t.date ASC
        """

        rows = self.get_rows(query, params)
        return [(row[0], float(row[1]) / 100) for row in rows]
```

</details>

### ⚙️ Method `get_transactions_with_money_op_in_currency`

```python
def get_transactions_with_money_op_in_currency(self, target_currency_id: int | None = None, category_type: int | None = None, category_name: str | None = None, currency_code: str | None = None, date_from: str | None = None, date_to: str | None = None, description_filter: str | None = None, limit: int | None = None) -> list[list[Any]]
```

Get transactions with signed monetary operation value in target currency.

Money op: expense (category type 0) is negative, income (type 1) is positive.
Conversion uses exchange_rates by transaction date (latest rate <= t.date).
If target_currency_id is None, uses default currency from settings.

Args:

- `target_currency_id` (`int | None`): Target currency ID. None = default currency.
- `category_type` (`int | None`): Filter by category type. Defaults to `None`.
- `category_name` (`str | None`): Filter by category name. Defaults to `None`.
- `currency_code` (`str | None`): Filter by currency code. Defaults to `None`.
- `date_from` (`str | None`): Filter from date. Defaults to `None`.
- `date_to` (`str | None`): Filter to date. Defaults to `None`.
- `description_filter` (`str | None`): Filter by description substring. Defaults to `None`.
- `limit` (`int | None`): Max records. Defaults to `None`.

Returns:

- `list[list[Any]]`: Each row is [t._id, t.amount, description, cat.name, c.code,
  t.date, t.tag, cat.type, cat.icon, c.symbol, money_op_major]. money_op_major
  is signed float in target currency (major units).

<details>
<summary>Code:</summary>

```python
def get_transactions_with_money_op_in_currency(
        self,
        target_currency_id: int | None = None,
        category_type: int | None = None,
        category_name: str | None = None,
        currency_code: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        description_filter: str | None = None,
        limit: int | None = None,
    ) -> list[list[Any]]:
        if target_currency_id is None:
            target_currency_id = self.get_default_currency_id()

        conditions: list[str] = []
        params: dict[str, Any] = {"currency_id": target_currency_id}

        if category_type is not None:
            conditions.append("cat.type = :category_type")
            params["category_type"] = category_type

        if category_name:
            conditions.append("cat.name = :category_name")
            params["category_name"] = category_name

        if currency_code:
            conditions.append("c.code = :currency_code")
            params["currency_code"] = currency_code

        if date_from and date_to:
            conditions.append("t.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        if description_filter:
            conditions.append("LOWER(t.description) LIKE :description_filter")
            params["description_filter"] = f"%{description_filter.lower()}%"

        join_clause, conversion_case, extra_params = self._get_currency_conversion_sql(target_currency_id)
        params.update(extra_params)

        money_op_sql = f"(CASE WHEN cat.type = 0 THEN -1 ELSE 1 END) * ({conversion_case.strip()})"
        where_sql = " AND " + " AND ".join(conditions) if conditions else ""

        query_text = f"""
            SELECT t._id, t.amount, t.description, cat.name, c.code, t.date, t.tag,
                   cat.type, cat.icon, c.symbol,
                   {money_op_sql} AS money_op_minor
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            JOIN currencies c ON t._id_currencies = c._id
            {join_clause}
            WHERE 1=1 {where_sql}
            ORDER BY t.date DESC, t._id DESC
        """
        if limit is not None:
            query_text += " LIMIT :limit"
            params["limit"] = limit

        rows = self.get_rows(query_text, params)
        subdivision = self.get_currency_subdivision(target_currency_id)
        result: list[list[Any]] = []
        for row in rows:
            money_op_minor = float(row[10] or 0)
            money_op_major = money_op_minor / subdivision
            result.append([*list(row[:10]), money_op_major])
        return result
```

</details>

### ⚙️ Method `get_usd_to_currency_rate`

```python
def get_usd_to_currency_rate(self, currency_id: int, date: str | None = None) -> float
```

Get exchange rate from currency to USD (how many USD for 1 currency unit).

Uses caching to avoid repeated database queries.
Note: Despite the method name, this returns currency_to_USD rates.

Args:

- `currency_id` (`int`): Currency ID.
- `date` (`str | None`): Date for rate lookup. Uses latest if None.

Returns:

- `float`: Exchange rate or 1.0 if not found.

<details>
<summary>Code:</summary>

```python
def get_usd_to_currency_rate(self, currency_id: int, date: str | None = None) -> float:
        return self.exchange_rates.get_usd_to_currency_rate(currency_id, date)
```

</details>

### ⚙️ Method `has_exchange_rates_data`

```python
def has_exchange_rates_data(self) -> bool
```

Check if there are any exchange rate records in the database.

Returns:

- `bool`: True if exchange rates exist, False otherwise.

<details>
<summary>Code:</summary>

```python
def has_exchange_rates_data(self) -> bool:
        return self.exchange_rates.has_exchange_rates_data()
```

</details>

### ⚙️ Method `set_default_currency`

```python
def set_default_currency(self, currency_code: str) -> bool
```

Set the default currency.

Args:

- `currency_code` (`str`): Currency code to set as default.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def set_default_currency(self, currency_code: str) -> bool:
        # Get the currency ID from the currency code
        currency_info = self.get_currency_by_code(currency_code)
        if not currency_info:
            return False

        currency_id = str(currency_info[0])  # Convert ID to string for storage

        # First try to update existing setting
        update_query = "UPDATE settings SET value = :id WHERE key = 'default_currency'"
        if self.execute_simple_query(update_query, {"id": currency_id}):
            # Check if any rows were affected by checking if the setting exists
            check_query = "SELECT COUNT(*) FROM settings WHERE key = 'default_currency'"
            rows = self.get_rows(check_query)
            if rows and rows[0][0] > 0:
                self._default_currency_cache = (currency_code, currency_info[0])
                return True

        # If update didn't affect any rows, insert new setting
        insert_query = "INSERT INTO settings (key, value) VALUES ('default_currency', :id)"
        if self.execute_simple_query(insert_query, {"id": currency_id}):
            self._default_currency_cache = (currency_code, currency_info[0])
            return True
        return False
```

</details>

### ⚙️ Method `should_update_exchange_rates`

```python
def should_update_exchange_rates(self) -> bool
```

Check if exchange rates need to be updated based on today's date.

Returns:

- `bool`: True if update is needed, False if all currencies have today's rates.

<details>
<summary>Code:</summary>

```python
def should_update_exchange_rates(self) -> bool:
        return self.exchange_rates.should_update_exchange_rates()
```

</details>

### ⚙️ Method `update_account`

```python
def update_account(self, account_id: int, name: str, balance: float, currency_id: int) -> bool
```

Update an existing account.

Args:

- `account_id` (`int`): Account ID.
- `name` (`str`): Account name.
- `balance` (`float`): Account balance.
- `currency_id` (`int`): Currency ID.
- `is_liquid` (`bool`): Whether account is liquid. Defaults to `True`.
- `is_cash` (`bool`): Whether account is cash. Defaults to `False`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_account(
        self,
        account_id: int,
        name: str,
        balance: float,
        currency_id: int,
        *,
        is_liquid: bool = True,
        is_cash: bool = False,
    ) -> bool:
        query = """UPDATE accounts SET name = :name, balance = :balance, _id_currencies = :currency_id,
                   is_liquid = :is_liquid, is_cash = :is_cash WHERE _id = :id"""
        params = {
            "name": name,
            "balance": self.convert_to_minor_units(balance, currency_id),
            "currency_id": currency_id,
            "is_liquid": 1 if is_liquid else 0,
            "is_cash": 1 if is_cash else 0,
            "id": account_id,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `update_category`

```python
def update_category(self, category_id: int, name: str, category_type: int, icon: str = "") -> bool
```

Update an existing category.

Args:

- `category_id` (`int`): Category ID.
- `name` (`str`): Category name.
- `category_type` (`int`): Category type.
- `icon` (`str`): Category icon. Defaults to `""`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_category(self, category_id: int, name: str, category_type: int, icon: str = "") -> bool:
        query = "UPDATE categories SET name = :name, type = :type, icon = :icon WHERE _id = :id"
        params = {
            "name": name,
            "type": category_type,
            "icon": icon,
            "id": category_id,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `update_currency`

```python
def update_currency(self, currency_id: int, code: str, name: str, symbol: str) -> bool
```

Update an existing currency.

Args:

- `currency_id` (`int`): Currency ID.
- `code` (`str`): Currency code.
- `name` (`str`): Currency name.
- `symbol` (`str`): Currency symbol.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_currency(self, currency_id: int, code: str, name: str, symbol: str) -> bool:
        query = "UPDATE currencies SET code = :code, name = :name, symbol = :symbol WHERE _id = :id"
        params = {
            "code": code,
            "name": name,
            "symbol": symbol,
            "id": currency_id,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `update_currency_exchange`

```python
def update_currency_exchange(self, exchange_id: int, amount_from: float, amount_to: float) -> bool
```

Update currency exchange amounts.

Args:

- `exchange_id` (`int`): Exchange record ID.
- `amount_from` (`float`): Amount from (in major units).
- `amount_to` (`float`): Amount to (in major units).

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_currency_exchange(self, exchange_id: int, amount_from: float, amount_to: float) -> bool:
        try:
            # Get the exchange record to get currency information
            exchange_record = self.get_rows(
                """
                SELECT ce._id, ce._id_currency_from, ce._id_currency_to, ce.amount_from, ce.amount_to,
                       ce.exchange_rate, ce.fee, ce.date, ce.description
                FROM currency_exchanges ce
                WHERE ce._id = :id
                """,
                {"id": exchange_id},
            )

            if not exchange_record:
                logger.warning("Exchange record with ID %s not found", exchange_id)
                return False

            record = exchange_record[0]
            currency_from_id = record[1]
            currency_to_id = record[2]

            # Get currency subdivisions
            from_subdivision = self.get_currency_subdivision(currency_from_id)
            to_subdivision = self.get_currency_subdivision(currency_to_id)

            # Convert amounts to minor units
            amount_from_minor = int(amount_from * from_subdivision)
            amount_to_minor = int(amount_to * to_subdivision)

            # Update the exchange record
            query = """
                UPDATE currency_exchanges
                SET amount_from = :amount_from, amount_to = :amount_to
                WHERE _id = :id
            """
            params = {"amount_from": amount_from_minor, "amount_to": amount_to_minor, "id": exchange_id}

            return self.execute_simple_query(query, params)

        except Exception:
            logger.exception("Error updating currency exchange")
            return False
```

</details>

### ⚙️ Method `update_currency_exchange_full`

```python
def update_currency_exchange_full(self, exchange_id: int, currency_from_code: str, currency_to_code: str, amount_from: float, amount_to: float, exchange_rate: float, fee: float, date: str, description: str = "") -> bool
```

Update full currency exchange record.

Args:

- `exchange_id` (`int`): Exchange record ID.
- `currency_from_code` (`str`): Source currency code.
- `currency_to_code` (`str`): Target currency code.
- `amount_from` (`float`): Amount from (in major units).
- `amount_to` (`float`): Amount to (in major units).
- `exchange_rate` (`float`): Exchange rate.
- `fee` (`float`): Exchange fee (in major units).
- `date` (`str`): Date in YYYY-MM-DD format.
- `description` (`str`): Exchange description. Defaults to `""`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_currency_exchange_full(
        self,
        exchange_id: int,
        currency_from_code: str,
        currency_to_code: str,
        amount_from: float,
        amount_to: float,
        exchange_rate: float,
        fee: float,
        date: str,
        description: str = "",
    ) -> bool:
        try:
            # Get currency IDs
            from_currency_info = self.get_currency_by_code(currency_from_code)
            to_currency_info = self.get_currency_by_code(currency_to_code)

            if not from_currency_info or not to_currency_info:
                logger.warning("Currency not found: %s or %s", currency_from_code, currency_to_code)
                return False

            from_currency_id = from_currency_info[0]
            to_currency_id = to_currency_info[0]

            # Get currency subdivisions
            from_subdivision = self.get_currency_subdivision(from_currency_id)
            to_subdivision = self.get_currency_subdivision(to_currency_id)

            # Convert amounts to minor units
            amount_from_minor = int(amount_from * from_subdivision)
            amount_to_minor = int(amount_to * to_subdivision)
            fee_minor = int(fee * from_subdivision)

            # Update the exchange record
            query = """
                UPDATE currency_exchanges
                SET _id_currency_from = :from_id,
                    _id_currency_to = :to_id,
                    amount_from = :amount_from,
                    amount_to = :amount_to,
                    exchange_rate = :exchange_rate,
                    fee = :fee,
                    date = :date,
                    description = :description
                WHERE _id = :id
            """
            params = {
                "from_id": from_currency_id,
                "to_id": to_currency_id,
                "amount_from": amount_from_minor,
                "amount_to": amount_to_minor,
                "exchange_rate": exchange_rate,
                "fee": fee_minor,
                "date": date,
                "description": description,
                "id": exchange_id,
            }

            success = self.execute_simple_query(query, params)
            if success:
                logger.info("Successfully updated currency exchange %s in database", exchange_id)
            else:
                logger.error("Failed to update currency exchange %s in database", exchange_id)

        except Exception:
            logger.exception("Error updating currency exchange")
            return False

        return success
```

</details>

### ⚙️ Method `update_currency_ticker`

```python
def update_currency_ticker(self, currency_id: int, ticker: str) -> bool
```

Update currency ticker.

Args:

- `currency_id` (`int`): Currency ID.
- `ticker` (`str`): New ticker value.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_currency_ticker(self, currency_id: int, ticker: str) -> bool:
        try:
            query = "UPDATE currencies SET ticker = :ticker WHERE _id = :id"
            params = {"ticker": ticker, "id": currency_id}
            return self.execute_simple_query(query, params)
        except Exception:
            logger.exception("Error updating currency ticker")
            return False
```

</details>

### ⚙️ Method `update_exchange_rate`

```python
def update_exchange_rate(self, currency_id: int, date: str, rate: float) -> bool
```

Update or insert exchange rate for a specific currency and date.

Args:

- `currency_id` (`int`): Currency ID.
- `date` (`str`): Date in YYYY-MM-DD format.
- `rate` (`float`): Exchange rate (USD to currency).

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_exchange_rate(self, currency_id: int, date: str, rate: float) -> bool:
        return self.exchange_rates.update_exchange_rate(currency_id, date, rate)
```

</details>

### ⚙️ Method `update_transaction`

```python
def update_transaction(self, transaction_id: int, amount: float, description: str, category_id: int, currency_id: int, date: str, tag: str = "") -> bool
```

Update an existing transaction.

Args:

- `transaction_id` (`int`): Transaction ID.
- `amount` (`float`): Transaction amount.
- `description` (`str`): Transaction description.
- `category_id` (`int`): Category ID.
- `currency_id` (`int`): Currency ID.
- `date` (`str`): Date in YYYY-MM-DD format.
- `tag` (`str`): Transaction tag. Defaults to `""`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_transaction(
        self,
        transaction_id: int,
        amount: float,
        description: str,
        category_id: int,
        currency_id: int,
        date: str,
        tag: str = "",
    ) -> bool:
        query = """UPDATE transactions SET amount = :amount, description = :description,
                   _id_categories = :category_id, _id_currencies = :currency_id,
                   date = :date, tag = :tag WHERE _id = :id"""
        params = {
            "amount": self.convert_to_minor_units(amount, currency_id),
            "description": description,
            "category_id": category_id,
            "currency_id": currency_id,
            "date": date,
            "tag": tag,
            "id": transaction_id,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `_ensure_performance_indexes`

```python
def _ensure_performance_indexes(self) -> None
```

Create indexes for exchange_rates and transactions if missing (faster currency conversion).

<details>
<summary>Code:</summary>

```python
def _ensure_performance_indexes(self) -> None:
        try:
            self.execute_simple_query(
                "CREATE INDEX IF NOT EXISTS idx_exchange_rates_currency_date ON exchange_rates(_id_currency, date)"
            )
            self.execute_simple_query(
                "CREATE INDEX IF NOT EXISTS idx_transactions_date_currency ON transactions(date, _id_currencies)"
            )
        except Exception:
            logger.exception("Could not ensure performance indexes")
```

</details>

### ⚙️ Method `_ensure_system_categories`

```python
def _ensure_system_categories(self) -> None
```

Ensure revision categories exist for balance reconciliation actions.

<details>
<summary>Code:</summary>

```python
def _ensure_system_categories(self) -> None:
        try:
            rows = self.get_rows(
                "SELECT name, type FROM categories WHERE name IN ('Revision Income', 'Revision Expense')"
            )
            existing = {(row[0], int(row[1])) for row in rows}
            if ("Revision Income", 1) not in existing:
                self.add_category("Revision Income", 1, "🧾")
            if ("Revision Expense", 0) not in existing:
                self.add_category("Revision Expense", 0, "🧾")
        except Exception:
            logger.exception("Could not ensure system categories")
```

</details>

### ⚙️ Method `_get_currency_conversion_sql`

```python
def _get_currency_conversion_sql(self, currency_id: int) -> tuple[str, str, dict]
```

Generate SQL for currency conversion via USD.

Args:

- `currency_id` (`int`): Target currency ID.

Returns:

- `tuple[str, str, dict]`: (join_clause, conversion_case, extra_params).

<details>
<summary>Code:</summary>

```python
def _get_currency_conversion_sql(self, currency_id: int) -> tuple[str, str, dict]:
        # Check if there's data in exchange_rates for optimization
        try:
            check_query = "SELECT COUNT(*) FROM exchange_rates LIMIT 1"
            rows = self.get_rows(check_query)
            has_exchange_rates = rows and rows[0][0] > 0
        except Exception:
            has_exchange_rates = False

        # If there's no exchange rate data, return simplified version
        if not has_exchange_rates:
            # Without JOIN and conversion - just return amount as is
            join_clause = ""
            conversion_case = "t.amount"
            return join_clause, conversion_case, {}

        # If there's exchange rate data, use full version with conversion
        usd_currency = self.get_currency_by_code("USD")
        usd_currency_id = usd_currency[0] if usd_currency else None

        if currency_id == usd_currency_id:
            # Converting to USD - direct rates
            join_clause = """
            LEFT JOIN exchange_rates er ON er._id_currency = t._id_currencies
                                        AND er.date = (
                                            SELECT MAX(date)
                                            FROM exchange_rates er2
                                            WHERE er2._id_currency = t._id_currencies
                                            AND er2.date <= t.date
                                        )
            """
            conversion_case = """
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    ELSE COALESCE(er.rate * t.amount, t.amount)
                END
            """
            return join_clause, conversion_case, {}
        # Converting to non-USD currency via USD
        join_clause = """
            LEFT JOIN exchange_rates source_er ON source_er._id_currency = t._id_currencies
                                            AND source_er.date = (
                                                SELECT MAX(date)
                                                FROM exchange_rates ser2
                                                WHERE ser2._id_currency = t._id_currencies
                                                    AND ser2.date <= t.date
                                            )
            LEFT JOIN exchange_rates target_er ON target_er._id_currency = :currency_id
                                            AND target_er.date = (
                                                SELECT MAX(date)
                                                FROM exchange_rates ter2
                                                WHERE ter2._id_currency = :currency_id
                                                    AND ter2.date <= t.date
                                            )
            """
        conversion_case = """
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    WHEN t._id_currencies = :usd_currency_id THEN
                        COALESCE(t.amount / NULLIF(target_er.rate, 0), t.amount)
                    ELSE
                        COALESCE(source_er.rate * t.amount / NULLIF(target_er.rate, 0), t.amount)
                END
            """
        return join_clause, conversion_case, {"usd_currency_id": usd_currency_id}
```

</details>

### ⚙️ Method `_get_full_currency_conversion_sql`

```python
def _get_full_currency_conversion_sql(self, currency_id: int) -> tuple[str, str, dict]
```

Generate full SQL for currency conversion via USD with exchange rates.

This method should only be called when exchange rates are actually needed.

Args:

- `currency_id` (`int`): Target currency ID.

Returns:

- `tuple[str, str, dict]`: (join_clause, conversion_case, extra_params).

<details>
<summary>Code:</summary>

```python
def _get_full_currency_conversion_sql(self, currency_id: int) -> tuple[str, str, dict]:
        usd_currency = self.get_currency_by_code("USD")
        usd_currency_id = usd_currency[0] if usd_currency else None

        if currency_id == usd_currency_id:
            # Converting to USD - direct rates
            join_clause = """
            LEFT JOIN exchange_rates er ON er._id_currency = t._id_currencies
                                        AND er.date = (
                                            SELECT MAX(date)
                                            FROM exchange_rates er2
                                            WHERE er2._id_currency = t._id_currencies
                                            AND er2.date <= t.date
                                        )
            """
            conversion_case = """
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    ELSE COALESCE(er.rate * t.amount, t.amount)
                END
            """
            return join_clause, conversion_case, {}
        # Converting to non-USD currency via USD
        join_clause = """
            LEFT JOIN exchange_rates source_er ON source_er._id_currency = t._id_currencies
                                            AND source_er.date = (
                                                SELECT MAX(date)
                                                FROM exchange_rates ser2
                                                WHERE ser2._id_currency = t._id_currencies
                                                    AND ser2.date <= t.date
                                            )
            LEFT JOIN exchange_rates target_er ON target_er._id_currency = :currency_id
                                            AND target_er.date = (
                                                SELECT MAX(date)
                                                FROM exchange_rates ter2
                                                WHERE ter2._id_currency = :currency_id
                                                    AND ter2.date <= t.date
                                            )
            """
        conversion_case = """
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    WHEN t._id_currencies = :usd_currency_id THEN
                        COALESCE(t.amount / NULLIF(target_er.rate, 0), t.amount)
                    ELSE
                        COALESCE(source_er.rate * t.amount / NULLIF(target_er.rate, 0), t.amount)
                END
            """
        return join_clause, conversion_case, {"usd_currency_id": usd_currency_id}
```

</details>

### ⚙️ Method `_init_default_settings`

```python
def _init_default_settings(self) -> None
```

Initialize default settings if they don't exist.

<details>
<summary>Code:</summary>

```python
def _init_default_settings(self) -> None:
        try:
            # Check if default_currency setting exists
            rows = self.get_rows("SELECT COUNT(*) FROM settings WHERE key = 'default_currency'")
            if rows and rows[0][0] == 0:
                # Insert default currency setting (RUB has ID 1)
                self.execute_simple_query("INSERT INTO settings (key, value) VALUES ('default_currency', '1')")
                logger.info("Initialized default currency setting")
        except Exception:
            logger.exception("Could not initialize default settings")
```

</details>

### ⚙️ Method `_load_default_currency_cache`

```python
def _load_default_currency_cache(self) -> None
```

Load default currency from DB into cache (once per run).

<details>
<summary>Code:</summary>

```python
def _load_default_currency_cache(self) -> None:
        if self._default_currency_cache is not None:
            return
        rows = self.get_rows("SELECT value FROM settings WHERE key = 'default_currency'")
        code = "RUB"
        currency_id = 1
        if rows:
            stored_value = rows[0][0]
            try:
                currency_id = int(stored_value)
                currency_info = self.get_currency_by_id(currency_id)
                if currency_info:
                    code = currency_info[0]
                else:
                    currency_id = 1
            except (ValueError, TypeError):
                code = stored_value or "RUB"
        self._default_currency_cache = (code, currency_id)
```

</details>
