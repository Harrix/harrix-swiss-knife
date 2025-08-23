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
  - [⚙️ Method `__del__`](#%EF%B8%8F-method-__del__)
  - [⚙️ Method `add_account`](#%EF%B8%8F-method-add_account)
  - [⚙️ Method `add_category`](#%EF%B8%8F-method-add_category)
  - [⚙️ Method `add_currency`](#%EF%B8%8F-method-add_currency)
  - [⚙️ Method `add_currency_exchange`](#%EF%B8%8F-method-add_currency_exchange)
  - [⚙️ Method `add_exchange_rate`](#%EF%B8%8F-method-add_exchange_rate)
  - [⚙️ Method `add_exchange_rates_batch`](#%EF%B8%8F-method-add_exchange_rates_batch)
  - [⚙️ Method `add_transaction`](#%EF%B8%8F-method-add_transaction)
  - [⚙️ Method `check_exchange_rate_exists`](#%EF%B8%8F-method-check_exchange_rate_exists)
  - [⚙️ Method `clean_invalid_exchange_rates`](#%EF%B8%8F-method-clean_invalid_exchange_rates)
  - [⚙️ Method `close`](#%EF%B8%8F-method-close)
  - [⚙️ Method `convert_from_minor_units`](#%EF%B8%8F-method-convert_from_minor_units)
  - [⚙️ Method `convert_to_minor_units`](#%EF%B8%8F-method-convert_to_minor_units)
  - [⚙️ Method `create_database_from_sql`](#%EF%B8%8F-method-create_database_from_sql)
  - [⚙️ Method `delete_account`](#%EF%B8%8F-method-delete_account)
  - [⚙️ Method `delete_category`](#%EF%B8%8F-method-delete_category)
  - [⚙️ Method `delete_currency`](#%EF%B8%8F-method-delete_currency)
  - [⚙️ Method `delete_currency_exchange`](#%EF%B8%8F-method-delete_currency_exchange)
  - [⚙️ Method `delete_exchange_rate`](#%EF%B8%8F-method-delete_exchange_rate)
  - [⚙️ Method `delete_transaction`](#%EF%B8%8F-method-delete_transaction)
  - [⚙️ Method `execute_query`](#%EF%B8%8F-method-execute_query)
  - [⚙️ Method `execute_simple_query`](#%EF%B8%8F-method-execute_simple_query)
  - [⚙️ Method `fill_missing_exchange_rates`](#%EF%B8%8F-method-fill_missing_exchange_rates)
  - [⚙️ Method `fill_missing_exchange_rates_in_range`](#%EF%B8%8F-method-fill_missing_exchange_rates_in_range)
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
  - [⚙️ Method `get_currencies_except_usd`](#%EF%B8%8F-method-get_currencies_except_usd)
  - [⚙️ Method `get_currency_by_code`](#%EF%B8%8F-method-get_currency_by_code)
  - [⚙️ Method `get_currency_by_id`](#%EF%B8%8F-method-get_currency_by_id)
  - [⚙️ Method `get_currency_subdivision`](#%EF%B8%8F-method-get_currency_subdivision)
  - [⚙️ Method `get_currency_subdivision_by_code`](#%EF%B8%8F-method-get_currency_subdivision_by_code)
  - [⚙️ Method `get_default_currency`](#%EF%B8%8F-method-get_default_currency)
  - [⚙️ Method `get_default_currency_id`](#%EF%B8%8F-method-get_default_currency_id)
  - [⚙️ Method `get_earliest_currency_exchange_date`](#%EF%B8%8F-method-get_earliest_currency_exchange_date)
  - [⚙️ Method `get_earliest_financial_date`](#%EF%B8%8F-method-get_earliest_financial_date)
  - [⚙️ Method `get_earliest_transaction_date`](#%EF%B8%8F-method-get_earliest_transaction_date)
  - [⚙️ Method `get_exchange_rate`](#%EF%B8%8F-method-get_exchange_rate)
  - [⚙️ Method `get_filtered_transactions`](#%EF%B8%8F-method-get_filtered_transactions)
  - [⚙️ Method `get_id`](#%EF%B8%8F-method-get_id)
  - [⚙️ Method `get_income_vs_expenses_in_currency`](#%EF%B8%8F-method-get_income_vs_expenses_in_currency)
  - [⚙️ Method `get_last_exchange_rate_date`](#%EF%B8%8F-method-get_last_exchange_rate_date)
  - [⚙️ Method `get_last_exchange_rates_update_date`](#%EF%B8%8F-method-get_last_exchange_rates_update_date)
  - [⚙️ Method `get_last_two_exchange_rate_records`](#%EF%B8%8F-method-get_last_two_exchange_rate_records)
  - [⚙️ Method `get_missing_exchange_rates_info`](#%EF%B8%8F-method-get_missing_exchange_rates_info)
  - [⚙️ Method `get_recent_transaction_descriptions_for_autocomplete`](#%EF%B8%8F-method-get_recent_transaction_descriptions_for_autocomplete)
  - [⚙️ Method `get_rows`](#%EF%B8%8F-method-get_rows)
  - [⚙️ Method `get_today_balance_in_currency`](#%EF%B8%8F-method-get_today_balance_in_currency)
  - [⚙️ Method `get_today_expenses_in_currency`](#%EF%B8%8F-method-get_today_expenses_in_currency)
  - [⚙️ Method `get_transactions_chart_data`](#%EF%B8%8F-method-get_transactions_chart_data)
  - [⚙️ Method `get_usd_to_currency_rate`](#%EF%B8%8F-method-get_usd_to_currency_rate)
  - [⚙️ Method `is_database_open`](#%EF%B8%8F-method-is_database_open)
  - [⚙️ Method `set_default_currency`](#%EF%B8%8F-method-set_default_currency)
  - [⚙️ Method `set_last_exchange_rates_update_date`](#%EF%B8%8F-method-set_last_exchange_rates_update_date)
  - [⚙️ Method `table_exists`](#%EF%B8%8F-method-table_exists)
  - [⚙️ Method `update_account`](#%EF%B8%8F-method-update_account)
  - [⚙️ Method `update_category`](#%EF%B8%8F-method-update_category)
  - [⚙️ Method `update_currency`](#%EF%B8%8F-method-update_currency)
  - [⚙️ Method `update_exchange_rate`](#%EF%B8%8F-method-update_exchange_rate)
  - [⚙️ Method `update_transaction`](#%EF%B8%8F-method-update_transaction)
  - [⚙️ Method `_create_query`](#%EF%B8%8F-method-_create_query)
  - [⚙️ Method `_ensure_connection`](#%EF%B8%8F-method-_ensure_connection)
  - [⚙️ Method `_get_currency_conversion_sql`](#%EF%B8%8F-method-_get_currency_conversion_sql)
  - [⚙️ Method `_get_full_currency_conversion_sql`](#%EF%B8%8F-method-_get_full_currency_conversion_sql)
  - [⚙️ Method `_init_default_settings`](#%EF%B8%8F-method-_init_default_settings)
  - [⚙️ Method `_iter_query`](#%EF%B8%8F-method-_iter_query)
  - [⚙️ Method `_reconnect`](#%EF%B8%8F-method-_reconnect)
  - [⚙️ Method `_rows_from_query`](#%EF%B8%8F-method-_rows_from_query)
- [🔧 Function `_safe_identifier`](#-function-_safe_identifier)

</details>

## 🏛️ Class `DatabaseManager`

```python
class DatabaseManager
```

Manage the connection and operations for a finance tracking database.

Attributes:

- `db` (`QSqlDatabase`): A live connection object opened on an SQLite
  database file.
- `connection_name` (`str`): Unique name for this database connection.

<details>
<summary>Code:</summary>

```python
class DatabaseManager:

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in `db_filename`.

        Args:

        - `db_filename` (`str`): The path to the target database file.

        Raises:

        - `ConnectionError`: If the underlying Qt driver fails to open the
          database.

        """
        # Include thread ID to ensure unique connections across threads
        thread_id = threading.current_thread().ident
        self.connection_name = f"finance_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(db_filename)

        # Store the database filename for potential reconnection
        self._db_filename = db_filename

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown database error"
            msg = f"❌ Failed to open the database: {error_msg}"
            raise ConnectionError(msg)

        # Initialize default settings if they don't exist
        self._init_default_settings()

        self._exchange_rate_cache = {}
        self._cache_timestamp = None

    def __del__(self) -> None:
        """Clean up database connection when object is destroyed."""
        try:
            self.close()
        except Exception as e:
            print(f"Warning: Error during database cleanup: {e}")

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
        query = """INSERT INTO exchange_rates (_id_currency, rate, date)
                   VALUES (:currency_id, :rate, :date)"""
        params = {
            "currency_id": currency_id,
            "rate": rate,  # Store as REAL directly
            "date": date,
        }
        return self.execute_simple_query(query, params)

    def add_exchange_rates_batch(self, exchange_rates_data: list[tuple[int, float, str]]) -> int:
        """Add multiple exchange rates in a single transaction.

        Args:
            exchange_rates_data: List of tuples (currency_id, rate, date)

        Returns:
            int: Number of successfully inserted records
        """
        if not exchange_rates_data:
            return 0

        try:
            # Prepare batch insert query
            query = """INSERT INTO exchange_rates (_id_currency, rate, date)
                    VALUES (?, ?, ?)"""

            # Convert to the format expected by executemany
            batch_data = [(currency_id, rate, date) for currency_id, rate, date in exchange_rates_data]

            # Use Qt's batch execution
            sql_query = self._create_query()
            sql_query.prepare(query)

            # Execute batch insert
            success_count = 0
            batch_size = 1000  # Process in batches of 1000

            for i in range(0, len(batch_data), batch_size):
                batch = batch_data[i : i + batch_size]

                # Clear previous bindings
                sql_query.clear()
                sql_query.prepare(query)

                # Bind batch data
                currency_ids = [item[0] for item in batch]
                rates = [item[1] for item in batch]
                dates = [item[2] for item in batch]

                sql_query.addBindValue(currency_ids)
                sql_query.addBindValue(rates)
                sql_query.addBindValue(dates)

                if sql_query.execBatch():
                    success_count += len(batch)
                    print(f"✅ Batch inserted {len(batch)} exchange rates (total: {success_count})")
                else:
                    error_msg = sql_query.lastError().text() if sql_query.lastError().isValid() else "Unknown error"
                    print(f"❌ Batch insert failed: {error_msg}")
                    # Try individual inserts for this batch as fallback
                    for currency_id, rate, date in batch:
                        if self.add_exchange_rate(currency_id, rate, date):
                            success_count += 1

            sql_query.clear()
            return success_count

        except Exception as e:
            print(f"❌ Error in batch exchange rate insert: {e}")
            return 0

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
        rows = self.get_rows(
            "SELECT COUNT(*) FROM exchange_rates WHERE _id_currency = :currency_id AND date = :date",
            {"currency_id": currency_id, "date": date},
        )
        return rows[0][0] > 0 if rows else False

    def clean_invalid_exchange_rates(self) -> int:
        """Clean exchange rates with empty or invalid rate values.

        Returns:
        - int: Number of cleaned records
        """
        query = """DELETE FROM exchange_rates WHERE rate IS NULL OR rate = '' OR rate = 0"""
        cursor = self.db.exec(query)
        if cursor.lastError().isValid():
            print(f"❌ Error cleaning exchange rates: {cursor.lastError().text()}")
            return 0

        affected_rows = cursor.numRowsAffected()
        cursor.clear()
        print(f"🧹 Cleaned {affected_rows} invalid exchange rate records")
        return affected_rows

    def close(self) -> None:
        """Close the database connection."""
        db = getattr(self, "db", None)
        if db is not None and db.isValid():
            db.close()
            connection_name = self.connection_name
            self.db = None
            QTimer.singleShot(0, lambda: QSqlDatabase.removeDatabase(connection_name))

        # Remove the database connection
        if hasattr(self, "connection_name"):
            QSqlDatabase.removeDatabase(self.connection_name)

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

    @staticmethod
    def create_database_from_sql(db_filename: str, sql_file_path: str) -> bool:
        """Create a new database from SQL file.

        Args:

        - `db_filename` (`str`): Path to the database file to create.
        - `sql_file_path` (`str`): Path to the SQL file with database schema and data.

        Returns:

        - `bool`: True if database was created successfully, False otherwise.

        """
        try:
            # Create database directory if it doesn't exist
            db_path = Path(db_filename)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            # Read SQL file
            sql_path = Path(sql_file_path)
            if not sql_path.exists():
                print(f"SQL file not found: {sql_file_path}")
                return False

            sql_content = sql_path.read_text(encoding="utf-8")

            # Create temporary database connection
            temp_connection_name = f"temp_db_{uuid.uuid4().hex[:8]}"

            temp_db = QSqlDatabase.addDatabase("QSQLITE", temp_connection_name)
            temp_db.setDatabaseName(db_filename)

            if not temp_db.open():
                error_msg = temp_db.lastError().text() if temp_db.lastError().isValid() else "Unknown error"
                print(f"❌ Failed to create database: {error_msg}")
                QSqlDatabase.removeDatabase(temp_connection_name)
                return False

            try:
                # Execute SQL commands
                query = QSqlQuery(temp_db)

                # Split SQL content by semicolons and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

                for statement in statements:
                    if not query.exec(statement):
                        error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown error"
                        print(f"❌ Failed to execute SQL statement: {error_msg}")
                        print(f"Statement was: {statement}")
                        return False

                print(f"Database created successfully: {db_filename}")
                return True

            finally:
                temp_db.close()
                QSqlDatabase.removeDatabase(temp_connection_name)

        except Exception as e:
            print(f"Error creating database from SQL file: {e}")
            return False

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
        query = "DELETE FROM exchange_rates WHERE _id = :id"
        return self.execute_simple_query(query, {"id": rate_id})

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction.

        Args:

        - `transaction_id` (`int`): Transaction ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM transactions WHERE _id = :id"
        return self.execute_simple_query(query, {"id": transaction_id})

    def execute_query(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> QSqlQuery | None:
        """Prepare and execute `query_text` with optional bound `params`.

        Args:

        - `query_text` (`str`): A parametrised SQL statement.
        - `params` (`dict[str, Any] | None`): Run-time values to be bound to
          named placeholders in `query_text`. Defaults to `None`.

        Returns:

        - `QSqlQuery | None`: The executed query when successful, otherwise
          `None`.

        """
        # Ensure database connection is valid
        if not self._ensure_connection():
            print(f"Database connection is not available for query: {query_text}")
            return None

        try:
            query = self._create_query()
            if not query.prepare(query_text):
                error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown prepare error"
                print(f"❌ Failed to prepare query: {error_msg}")
                print(f"Query was: {query_text}")
                return None

            if params:
                for key, value in params.items():
                    query.bindValue(f":{key}", value)

            if not query.exec():
                error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown execution error"
                print(f"❌ Failed to execute query: {error_msg}")
                print(f"Query was: {query_text}")
                print(f"Params were: {params}")
                return None

        except Exception as e:
            print(f"❌ Exception during query execution: {e}")
            print(f"Query was: {query_text}")
            print(f"Params were: {params}")
            return None

        else:
            return query

    def execute_simple_query(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> bool:
        """Execute a simple query and return success status (for INSERT/UPDATE/DELETE operations).

        Args:

        - `query_text` (`str`): A parametrised SQL statement.
        - `params` (`dict[str, Any] | None`): Run-time values to be bound to
          named placeholders in `query_text`. Defaults to `None`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        # Ensure database connection is valid
        if not self._ensure_connection():
            print(f"Database connection is not available for query: {query_text}")
            return False

        try:
            query = self._create_query()
            if not query.prepare(query_text):
                error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown prepare error"
                print(f"Failed to prepare query: {error_msg}")
                print(f"Query was: {query_text}")
                return False

            if params:
                for key, value in params.items():
                    query.bindValue(f":{key}", value)

            success = query.exec()
            if not success:
                error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown execution error"
                print(f"❌ Failed to execute query: {error_msg}")
                print(f"Query was: {query_text}")
                print(f"Params were: {params}")
                return False

        except Exception as e:
            print(f"❌ Exception during query execution: {e}")
            print(f"Query was: {query_text}")
            print(f"Params were: {params}")
            return False

        else:
            # Clear the query to release resources
            query.clear()
            return True

    def fill_missing_exchange_rates(self) -> int:
        """Fill missing exchange rates with previous available rates for all date gaps.

        Returns:
            int: Number of exchange rates that were filled.
        """
        from datetime import datetime, timedelta

        currencies = self.get_currencies_except_usd()
        total_filled = 0

        # Get the earliest transaction date as the absolute start date
        earliest_transaction_date = self.get_earliest_transaction_date()
        if not earliest_transaction_date:
            print("No transactions found, cannot determine start date for filling rates")
            return 0

        start_date = datetime.strptime(earliest_transaction_date, "%Y-%m-%d").date()
        end_date = datetime.now().date()

        print(f"🔄 Filling missing exchange rates from {start_date} to {end_date}")

        for currency_id, currency_code, _, _ in currencies:
            print(f"📊 Processing {currency_code}...")

            # Get ALL existing rates for this currency (не только в диапазоне дат)
            query = """
                SELECT date, rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date ASC
            """
            rows = self.get_rows(query, {"currency_id": currency_id})

            if not rows:
                print(f"⚠️ No exchange rates found for {currency_code}, skipping")
                continue

            # Create a map of existing rates
            existing_rates = {row[0]: row[1] for row in rows}
            print(f"📈 Found {len(existing_rates)} existing rates for {currency_code}")

            # Fill missing dates from start_date to end_date
            current_date = start_date
            last_known_rate = None
            currency_filled = 0

            # Найти первый доступный курс для инициализации last_known_rate
            for date_str in sorted(existing_rates.keys()):
                if datetime.strptime(date_str, "%Y-%m-%d").date() <= current_date:
                    last_known_rate = existing_rates[date_str]
                else:
                    break

            print(f"🔍 Initial rate for {currency_code}: {last_known_rate}")

            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")

                if date_str in existing_rates:
                    # Update last known rate
                    last_known_rate = existing_rates[date_str]
                    print(f"📊 {currency_code} {date_str}: Found existing rate {last_known_rate}")
                elif last_known_rate is not None:
                    # Fill missing date with last known rate
                    print(f"🔍 {currency_code} {date_str}: Missing, trying to fill with {last_known_rate}")
                    if self.add_exchange_rate(currency_id, last_known_rate, date_str):
                        currency_filled += 1
                        total_filled += 1
                        print(f"✅ {currency_code} {date_str}: Filled with rate {last_known_rate}")
                    else:
                        print(f"❌ {currency_code} {date_str}: Failed to add rate")
                else:
                    print(f"⚠️ {currency_code} {date_str}: No known rate to use for filling")

                current_date += timedelta(days=1)

            print(f"📈 Filled {currency_filled} missing dates for {currency_code}")

        print(f"🎉 Total filled: {total_filled} exchange rate records")
        return total_filled

    def fill_missing_exchange_rates_in_range(self, start_date_str: str, end_date_str: str) -> int:
        """Fill missing exchange rates in specific date range.

        Args:
            start_date_str: Start date in YYYY-MM-DD format
            end_date_str: End date in YYYY-MM-DD format

        Returns:
            int: Number of exchange rates that were filled.
        """
        from datetime import datetime, timedelta

        currencies = self.get_currencies_except_usd()
        total_filled = 0

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        print(f"🔄 Filling missing exchange rates from {start_date} to {end_date}")

        for currency_id, currency_code, _, _ in currencies:
            print(f"📊 Processing {currency_code} for range {start_date} to {end_date}...")

            # Get ALL existing rates for this currency (не только в диапазоне)
            query = """
                SELECT date, rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date ASC
            """
            rows = self.get_rows(query, {"currency_id": currency_id})

            if not rows:
                print(f"⚠️ No exchange rates found for {currency_code}, skipping")
                continue

            # Create a map of existing rates
            existing_rates = {row[0]: row[1] for row in rows}

            # Find the most recent rate before start_date for initialization
            last_known_rate = None
            for date_str in sorted(existing_rates.keys()):
                rate_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if rate_date < start_date:
                    last_known_rate = existing_rates[date_str]
                elif rate_date >= start_date:
                    break

            print(f"🔍 Initial rate for {currency_code} before {start_date}: {last_known_rate}")

            # Fill missing dates in the specified range
            current_date = start_date
            currency_filled = 0

            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")

                if date_str in existing_rates:
                    # Update last known rate
                    last_known_rate = existing_rates[date_str]
                    print(f"📊 {currency_code} {date_str}: Found existing rate {last_known_rate}")
                elif last_known_rate is not None:
                    # Check if this date actually needs filling
                    if not self.check_exchange_rate_exists(currency_id, date_str):
                        print(f"🔍 {currency_code} {date_str}: Missing, filling with {last_known_rate}")
                        if self.add_exchange_rate(currency_id, last_known_rate, date_str):
                            currency_filled += 1
                            total_filled += 1
                            print(f"✅ {currency_code} {date_str}: Filled with rate {last_known_rate}")
                        else:
                            print(f"❌ {currency_code} {date_str}: Failed to add rate")
                    else:
                        print(f"📊 {currency_code} {date_str}: Already exists, skipping")
                else:
                    print(f"⚠️ {currency_code} {date_str}: No known rate to use for filling")

                current_date += timedelta(days=1)

            print(f"📈 Filled {currency_filled} missing dates for {currency_code} in range")

        print(f"🎉 Total filled in range: {total_filled} exchange rate records")
        return total_filled

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

        - `list[list[Any]]`: List of account records [_id, name, balance, currency_code, is_liquid, is_cash, currency_id].

        """
        rows = self.get_rows("""
            SELECT a._id, a.name, a.balance, c.code, a.is_liquid, a.is_cash, c._id as currency_id
            FROM accounts a
            JOIN currencies c ON a._id_currencies = c._id
            ORDER BY a.name
        """)

        # Convert balances from stored subdivision to actual values
        for row in rows:
            if len(row) >= 4 and row[2] is not None and row[3] is not None:  # balance and currency_code
                currency_code = row[3]
                subdivision = self.get_currency_subdivision_by_code(currency_code)
                row[2] = float(row[2]) / subdivision

        return rows

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

        # Convert amounts, rates and fees from stored subdivision to actual values
        for row in rows:
            if len(row) >= 9:
                # Get currency subdivisions for proper conversion
                from_currency_code = row[1]
                to_currency_code = row[2]

                from_subdivision = self.get_currency_subdivision_by_code(from_currency_code)
                to_subdivision = self.get_currency_subdivision_by_code(to_currency_code)

                # Convert amounts and fees
                if row[3] is not None:  # amount_from
                    row[3] = float(row[3]) / from_subdivision
                if row[4] is not None:  # amount_to
                    row[4] = float(row[4]) / to_subdivision
                if row[5] is not None:  # exchange_rate (already stored as REAL)
                    row[5] = float(row[5])
                if row[6] is not None:  # fee (in from_currency)
                    row[6] = float(row[6]) / from_subdivision

        return rows

    def get_all_exchange_rates(self, limit: int | None = None) -> list[list[Any]]:
        """Get all exchange rates with currency information.

        Args:

        - `limit` (`int | None`): Maximum number of records to return. None for all records. Defaults to `None`.

        Returns:

        - `list[list[Any]]`: List of exchange rate records.

        """
        query = """
            SELECT er._id, 'USD', c.code, er.rate, er.date
            FROM exchange_rates er
            JOIN currencies c ON er._id_currency = c._id
            ORDER BY er.date DESC, er._id DESC
        """

        if limit is not None:
            query += f" LIMIT {limit}"

        rows = self.get_rows(query)

        # Rates are already stored as REAL, no conversion needed
        # Just ensure they are float type for consistency and handle empty strings
        for row in rows:
            if len(row) >= 4 and row[3] is not None and row[3] != "":
                try:
                    row[3] = float(row[3])
                except (ValueError, TypeError):
                    row[3] = 0.0  # Set to 0 for invalid values
            elif len(row) >= 4:
                row[3] = 0.0  # Set to 0 for None or empty string

        return rows

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

        if limit is not None:
            query += f" LIMIT {limit}"

        return self.get_rows(query)

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

    def get_default_currency(self) -> str:
        """Get the default currency code.

        Returns:

        - `str`: Default currency code or 'RUB' if not set.

        """
        rows = self.get_rows("SELECT value FROM settings WHERE key = 'default_currency'")
        return rows[0][0] if rows else "RUB"

    def get_default_currency_id(self) -> int:
        """Get the default currency ID.

        Returns:

        - `int`: Default currency ID or 1 if not found.

        """
        default_code = self.get_default_currency()
        currency_info = self.get_currency_by_code(default_code)
        return currency_info[0] if currency_info else 1

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
        elif transaction_date:
            return transaction_date
        elif exchange_date:
            return exchange_date
        else:
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
        - from_currency_id (int): Source currency ID.
        - to_currency_id (int): Target currency ID.
        - date (str | None): Date for rate lookup. Uses latest if None.

        Returns:
        - float: Exchange rate or 1.0 if not found/same currency.
        """
        if from_currency_id == to_currency_id:
            return 1.0

        # Для избежания загрузки exchange_rates при старте,
        # возвращаем 1.0 если таблица exchange_rates пуста или недоступна
        try:
            # Быстрая проверка наличия данных в таблице
            check_query = "SELECT COUNT(*) FROM exchange_rates LIMIT 1"
            rows = self.get_rows(check_query)
            if not rows or rows[0][0] == 0:
                return 1.0  # Нет данных о курсах
        except Exception:
            return 1.0  # Таблица недоступна

        # Остальная логика остается прежней...
        # Get USD currency ID
        usd_currency = self.get_currency_by_code("USD")
        if not usd_currency:
            return 1.0
        usd_currency_id = usd_currency[0]

        # Now rates are stored as USD → currency (e.g., 1 USD = 79.85 RUB)
        if from_currency_id == usd_currency_id:
            # USD to other currency - direct rate from database
            return self.get_usd_to_currency_rate(to_currency_id, date)
        elif to_currency_id == usd_currency_id:
            # Other currency to USD - inverse of stored rate
            usd_rate = self.get_usd_to_currency_rate(from_currency_id, date)
            return 1.0 / usd_rate if usd_rate != 0 else 1.0
        else:
            # from_currency to to_currency via USD
            from_usd_rate = self.get_usd_to_currency_rate(from_currency_id, date)  # USD → from_currency
            to_usd_rate = self.get_usd_to_currency_rate(to_currency_id, date)  # USD → to_currency
            if from_usd_rate != 0 and to_usd_rate != 0:
                # from_currency → USD → to_currency = (1/from_usd_rate) * to_usd_rate
                return to_usd_rate / from_usd_rate
            return 1.0

    def get_filtered_transactions(
        self,
        category_type: int | None = None,
        category_name: str | None = None,
        currency_code: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[list[Any]]:
        """Get filtered transactions.

        Args:

        - `category_type` (`int | None`): Filter by category type. Defaults to `None`.
        - `category_name` (`str | None`): Filter by category name. Defaults to `None`.
        - `currency_code` (`str | None`): Filter by currency code. Defaults to `None`.
        - `date_from` (`str | None`): Filter from date. Defaults to `None`.
        - `date_to` (`str | None`): Filter to date. Defaults to `None`.

        Returns:

        - `list[list[Any]]`: List of filtered transaction records.

        """
        conditions: list[str] = []
        params: dict[str, str | int] = {}

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

    def get_id(
        self,
        table: str,
        name_column: str,
        name_value: str,
        id_column: str = "_id",
        condition: str | None = None,
    ) -> int | None:
        """Return a single ID that matches `name_value` in `table`.

        Args:

        - `table` (`str`): Target table name.
        - `name_column` (`str`): Column that stores the searched value.
        - `name_value` (`str`): Searched value itself.
        - `id_column` (`str`): Column that stores the ID. Defaults to `"_id"`.
        - `condition` (`str | None`): Extra SQL that will be appended to the
          `WHERE` clause. Defaults to `None`.

        Returns:

        - `int | None`: The found identifier or `None` when the query yields
          no rows.

        """
        # Validate identifiers to eliminate SQL-injection vectors.
        table = _safe_identifier(table)
        name_column = _safe_identifier(name_column)
        id_column = _safe_identifier(id_column)

        # nosec B608 - identifiers are validated by _safe_identifier
        query_text = f"SELECT {id_column} FROM {table} WHERE {name_column} = :name"
        if condition:
            query_text += f" AND {condition}"

        query = self.execute_query(query_text, {"name": name_value})
        if query and query.next():
            result = query.value(0)
            query.clear()  # Clear the query to release resources
            return result
        return None

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
        params = {"currency_id": currency_id}

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
            currency_id (int): Currency ID.

        Returns:
            str | None: Last date in YYYY-MM-DD format or None if no rates exist.
        """
        rows = self.get_rows(
            "SELECT MAX(date) FROM exchange_rates WHERE _id_currency = :currency_id", {"currency_id": currency_id}
        )
        return rows[0][0] if rows and rows[0][0] else None

    def get_last_exchange_rates_update_date(self) -> str | None:
        """Get the last date when exchange rates were updated.

        Returns:
            str | None: Last update date in YYYY-MM-DD format or None if never updated.
        """
        rows = self.get_rows("SELECT value FROM settings WHERE key = 'last_exchange_rates_update'")
        return rows[0][0] if rows else None

    def get_last_two_exchange_rate_records(self, currency_id: int) -> list[tuple[str, float]]:
        """Get the last two exchange rate records for a currency.

        Args:
            currency_id (int): Currency ID.

        Returns:
            list[tuple[str, float]]: List of tuples (date, rate) for the last two records, sorted by date.
        """
        rows = self.get_rows(
            """SELECT date, rate
               FROM exchange_rates
               WHERE _id_currency = :currency_id
               ORDER BY date DESC
               LIMIT 2""",
            {"currency_id": currency_id},
        )
        # Return in chronological order (oldest first)
        return [(row[0], float(row[1])) for row in reversed(rows)] if rows else []

    def get_missing_exchange_rates_info(self, date_from: str, date_to: str) -> dict[int, list[str]]:
        """Get information about missing exchange rates for each currency.

        Checks for missing rates for each day in the date range.

        Args:
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format

        Returns:
            Dictionary mapping currency_id to list of missing dates
        """
        from datetime import datetime, timedelta

        missing_info = {}

        # Get all currencies except USD
        currencies = self.get_currencies_except_usd()

        # Generate all dates in the range
        start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        end_date = datetime.strptime(date_to, "%Y-%m-%d").date()

        all_dates = []
        current_date = start_date
        while current_date <= end_date:
            all_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        print(f"Проверяем курсы валют с {date_from} по {date_to} ({len(all_dates)} дней)")

        for currency_id, currency_code, _, _ in currencies:
            # Get existing dates for this currency
            query = """
                SELECT DISTINCT date FROM exchange_rates
                WHERE _id_currency = :currency_id
                AND date BETWEEN :date_from AND :date_to
                ORDER BY date
            """

            rows = self.get_rows(query, {"currency_id": currency_id, "date_from": date_from, "date_to": date_to})

            existing_dates = set(row[0] for row in rows)

            # Find missing dates
            missing_dates = []
            for date_str in all_dates:
                if date_str not in existing_dates:
                    missing_dates.append(date_str)

            # Print information about missing dates
            if missing_dates:
                print(f"📊 {currency_code}: {len(missing_dates)} missing rates")

                # Show first 10 dates as sample
                sample_size = min(10, len(missing_dates))
                sample_dates = missing_dates[:sample_size]
                print(f"    Первые {sample_size} пропущенных дат: {', '.join(sample_dates)}")

                if len(missing_dates) > 10:
                    print(f"    ... и еще {len(missing_dates) - 10} дат")

                # Show date ranges for better understanding
                if len(missing_dates) > 1:
                    print(f"    Диапазон: с {missing_dates[0]} по {missing_dates[-1]}")

                missing_info[currency_id] = missing_dates
            else:
                print(f"✅ {currency_code}: все курсы присутствуют")

        if not missing_info:
            print("✅ Все курсы валют присутствуют в указанном диапазоне дат")
        else:
            total_missing = sum(len(dates) for dates in missing_info.values())
            print(f"\n📈 ИТОГО: {total_missing} пропущенных записей для {len(missing_info)} валют")

            # Show full list of all missing dates for first currency as example
            if missing_info:
                first_currency_id = next(iter(missing_info))
                first_currency_code = next(code for id, code, _, _ in currencies if id == first_currency_id)
                first_missing = missing_info[first_currency_id]

                print(f"\n🔍 ПОЛНЫЙ СПИСОК для {first_currency_code} ({len(first_missing)} дат):")
                for i, date in enumerate(first_missing, 1):
                    print(f"  {i:4d}. {date}")
                    if i >= 50:  # Ограничиваем вывод 50 датами
                        print(f"  ... и еще {len(first_missing) - 50} дат")
                        break

        return missing_info

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
        limit_frequent = int(limit * 0.7)
        limit_recent = limit - limit_frequent

        rows = self.get_rows(query, {"limit_frequent": limit_frequent, "limit_recent": limit_recent})
        return [row[0] for row in rows if row[0]]

    def get_rows(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> list[list[Any]]:
        """Execute `query_text` and fetch the whole result set.

        Args:

        - `query_text` (`str`): A SQL statement.
        - `params` (`dict[str, Any] | None`): Values to be bound at run time.
          Defaults to `None`.

        Returns:

        - `list[list[Any]]`: A list whose elements are the records returned by
          the database.

        """
        query = self.execute_query(query_text, params)
        if query:
            result = self._rows_from_query(query)
            query.clear()  # Clear the query to release resources
            return result
        return []

    def get_today_balance_in_currency(self, currency_id: int) -> float:
        """Get today's balance (income - expenses) in specified currency.

        Args:

        - `currency_id` (`int`): Target currency ID.

        Returns:

        - `float`: Today's balance in target currency.

        """
        today = datetime.now().strftime("%Y-%m-%d")
        total_income, total_expenses = self.get_income_vs_expenses_in_currency(currency_id, today, today)
        return total_income - total_expenses

    def get_today_expenses_in_currency(self, currency_id: int) -> float:
        """Get today's expenses in specified currency.

        Args:

        - `currency_id` (`int`): Currency ID for conversion.

        Returns:

        - `float`: Today's expenses in the specified currency.

        """
        today = datetime.now().strftime("%Y-%m-%d")
        _, expenses = self.get_income_vs_expenses_in_currency(currency_id, today, today)
        return expenses

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
        params = {"currency_id": currency_id}

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

    def get_usd_to_currency_rate(self, currency_id: int, date: str | None = None) -> float:
        """Get exchange rate from USD to currency (how many currency units for 1 USD).

        Uses caching to avoid repeated database queries.
        """
        # Check if currency is USD
        usd_currency = self.get_currency_by_code("USD")
        if usd_currency and currency_id == usd_currency[0]:
            return 1.0

        # Create cache key
        cache_key = f"{currency_id}_{date or 'latest'}"

        # Check cache (valid for 5 minutes)
        from datetime import datetime, timedelta

        now = datetime.now()
        if (
            self._cache_timestamp
            and (now - self._cache_timestamp) < timedelta(minutes=5)
            and cache_key in self._exchange_rate_cache
        ):
            return self._exchange_rate_cache[cache_key]

        # Query database
        if date:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency = :currency_id AND date <= :date
                ORDER BY date DESC LIMIT 1
            """
            params = {"currency_id": currency_id, "date": date}
        else:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date DESC LIMIT 1
            """
            params = {"currency_id": currency_id}

        rows = self.get_rows(query, params)
        if rows and rows[0][0] is not None and rows[0][0] != "":
            try:
                rate = float(rows[0][0])
                # Update cache
                self._exchange_rate_cache[cache_key] = rate
                self._cache_timestamp = now
                return rate
            except (ValueError, TypeError):
                return 1.0

        return 1.0

    def is_database_open(self) -> bool:
        """Check if the database connection is open.

        Returns:

        - `bool`: True if database is open, False otherwise.

        """
        return hasattr(self, "db") and self.db is not None and self.db.isValid() and self.db.isOpen()

    def set_default_currency(self, currency_code: str) -> bool:
        """Set the default currency.

        Args:

        - `currency_code` (`str`): Currency code to set as default.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        # First try to update existing setting
        update_query = "UPDATE settings SET value = :code WHERE key = 'default_currency'"
        if self.execute_simple_query(update_query, {"code": currency_code}):
            # Check if any rows were affected by checking if the setting exists
            check_query = "SELECT COUNT(*) FROM settings WHERE key = 'default_currency'"
            rows = self.get_rows(check_query)
            if rows and rows[0][0] > 0:
                return True

        # If update didn't affect any rows, insert new setting
        insert_query = "INSERT INTO settings (key, value) VALUES ('default_currency', :code)"
        return self.execute_simple_query(insert_query, {"code": currency_code})

    def set_last_exchange_rates_update_date(self, date: str) -> bool:
        """Set the last date when exchange rates were updated.

        Args:
            date (str): Date in YYYY-MM-DD format.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # First try to update existing setting
            update_query = "UPDATE settings SET value = :date WHERE key = 'last_exchange_rates_update'"
            if self.execute_simple_query(update_query, {"date": date}):
                # Check if any rows were affected
                check_query = "SELECT COUNT(*) FROM settings WHERE key = 'last_exchange_rates_update'"
                rows = self.get_rows(check_query)
                if rows and rows[0][0] > 0:
                    print(f"✅ Updated existing last_exchange_rates_update setting to {date}")
                    return True

            # If update didn't affect any rows, insert new setting
            insert_query = "INSERT INTO settings (key, value) VALUES ('last_exchange_rates_update', :date)"
            success = self.execute_simple_query(insert_query, {"date": date})
            if success:
                print(f"✅ Created new last_exchange_rates_update setting with date {date}")
            else:
                print(f"❌ Failed to create last_exchange_rates_update setting")
            return success
        except Exception as e:
            print(f"❌ Error setting last_exchange_rates_update_date: {e}")
            return False

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.

        Args:

        - `table_name` (`str`): Name of the table to check.

        Returns:

        - `bool`: True if table exists, False otherwise.

        """
        if not self.is_database_open():
            return False

        query = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name", {"table_name": table_name}
        )

        if query and query.next():
            return True
        return False

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

    def update_exchange_rate(self, currency_id: int, date: str, new_rate: float) -> bool:
        """Update an existing exchange rate record.

        Args:
            currency_id (int): Currency ID.
            date (str): Date in YYYY-MM-DD format.
            new_rate (float): New exchange rate value.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            query = """
                UPDATE exchange_rates
                SET rate = :rate
                WHERE _id_currency = :currency_id AND date = :date
            """
            params = {"currency_id": currency_id, "date": date, "rate": new_rate}

            result = self.execute_query(query, params)
            if result:
                result.clear()
                return True
            return False
        except Exception as e:
            print(f"Error updating exchange rate: {e}")
            return False

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

    def _create_query(self) -> QSqlQuery:
        """Create a QSqlQuery using this manager's database connection.

        Returns:

        - `QSqlQuery`: A query object bound to this database connection.

        """
        if not self._ensure_connection() or self.db is None:
            error_msg = "❌ Database connection is not available"
            raise ConnectionError(error_msg)
        return QSqlQuery(self.db)

    def _ensure_connection(self) -> bool:
        """Ensure database connection is open and valid.

        Returns:

        - `bool`: True if connection is valid, False otherwise.

        """
        if not hasattr(self, "db") or self.db is None or not self.db.isValid():
            print("Database object is invalid, attempting to reconnect...")
            try:
                self._reconnect()
                return self.db is not None and self.db.isOpen()
            except Exception as e:
                print(f"Failed to reconnect to database: {e}")
                return False

        if self.db is None or not self.db.isOpen():
            print("Database connection is closed, attempting to reopen...")
            if self.db is None or not self.db.open():
                error_msg = self.db.lastError().text() if self.db and self.db.lastError().isValid() else "Unknown error"
                print(f"❌ Failed to reopen database: {error_msg}")
                try:
                    self._reconnect()
                    return self.db is not None and self.db.isOpen()
                except Exception as e:
                    print(f"❌ Failed to reconnect to database: {e}")
                    return False

        return True

    def _get_currency_conversion_sql(self, currency_id: int) -> tuple[str, str, dict]:
        """Generate SQL for currency conversion via USD.

        Args:
        - currency_id (int): Target currency ID

        Returns:
        - tuple[str, str, dict]: (join_clause, conversion_case, extra_params)
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
        else:
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
        else:
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
                # Insert default currency setting
                self.execute_simple_query("INSERT INTO settings (key, value) VALUES ('default_currency', 'RUB')")
                print("✅ Initialized default currency setting")
        except Exception as e:
            print(f"Warning: Could not initialize default settings: {e}")

    def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]:
        """Yield every record in `query` one by one.

        Args:

        - `query` (`QSqlQuery | None`): A prepared and executed `QSqlQuery`
          object.

        Yields:

        - `QSqlQuery`: The same object positioned on consecutive records.

        """
        if query is None:
            return
        while query.next():
            yield query

    def _reconnect(self) -> None:
        """Attempt to reconnect to the database."""
        if hasattr(self, "db") and self.db is not None and self.db.isValid():
            self.db.close()

        # Remove the old connection
        if hasattr(self, "connection_name"):
            QSqlDatabase.removeDatabase(self.connection_name)

        # Create a new connection
        thread_id = threading.current_thread().ident
        self.connection_name = f"finance_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(self._db_filename)

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown error"
            error_msg = f"❌ Failed to reconnect to database: {error_msg}"
            raise ConnectionError(error_msg)

    def _rows_from_query(self, query: QSqlQuery) -> list[list[Any]]:
        """Convert the full result set in `query` into a list of rows.

        Args:

        - `query` (`QSqlQuery`): An executed query.

        Returns:

        - `list[list[Any]]`: Every database row represented as a list whose
          elements correspond to column values.

        """
        result: list[list[Any]] = []
        while query.next():
            row = [query.value(i) for i in range(query.record().count())]
            result.append(row)
        return result
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

- `ConnectionError`: If the underlying Qt driver fails to open the
  database.

<details>
<summary>Code:</summary>

```python
def __init__(self, db_filename: str) -> None:
        # Include thread ID to ensure unique connections across threads
        thread_id = threading.current_thread().ident
        self.connection_name = f"finance_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(db_filename)

        # Store the database filename for potential reconnection
        self._db_filename = db_filename

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown database error"
            msg = f"❌ Failed to open the database: {error_msg}"
            raise ConnectionError(msg)

        # Initialize default settings if they don't exist
        self._init_default_settings()

        self._exchange_rate_cache = {}
        self._cache_timestamp = None
```

</details>

### ⚙️ Method `__del__`

```python
def __del__(self) -> None
```

Clean up database connection when object is destroyed.

<details>
<summary>Code:</summary>

```python
def __del__(self) -> None:
        try:
            self.close()
        except Exception as e:
            print(f"Warning: Error during database cleanup: {e}")
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
        query = """INSERT INTO exchange_rates (_id_currency, rate, date)
                   VALUES (:currency_id, :rate, :date)"""
        params = {
            "currency_id": currency_id,
            "rate": rate,  # Store as REAL directly
            "date": date,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `add_exchange_rates_batch`

```python
def add_exchange_rates_batch(self, exchange_rates_data: list[tuple[int, float, str]]) -> int
```

Add multiple exchange rates in a single transaction.

Args:
exchange_rates_data: List of tuples (currency_id, rate, date)

Returns:
int: Number of successfully inserted records

<details>
<summary>Code:</summary>

```python
def add_exchange_rates_batch(self, exchange_rates_data: list[tuple[int, float, str]]) -> int:
        if not exchange_rates_data:
            return 0

        try:
            # Prepare batch insert query
            query = """INSERT INTO exchange_rates (_id_currency, rate, date)
                    VALUES (?, ?, ?)"""

            # Convert to the format expected by executemany
            batch_data = [(currency_id, rate, date) for currency_id, rate, date in exchange_rates_data]

            # Use Qt's batch execution
            sql_query = self._create_query()
            sql_query.prepare(query)

            # Execute batch insert
            success_count = 0
            batch_size = 1000  # Process in batches of 1000

            for i in range(0, len(batch_data), batch_size):
                batch = batch_data[i : i + batch_size]

                # Clear previous bindings
                sql_query.clear()
                sql_query.prepare(query)

                # Bind batch data
                currency_ids = [item[0] for item in batch]
                rates = [item[1] for item in batch]
                dates = [item[2] for item in batch]

                sql_query.addBindValue(currency_ids)
                sql_query.addBindValue(rates)
                sql_query.addBindValue(dates)

                if sql_query.execBatch():
                    success_count += len(batch)
                    print(f"✅ Batch inserted {len(batch)} exchange rates (total: {success_count})")
                else:
                    error_msg = sql_query.lastError().text() if sql_query.lastError().isValid() else "Unknown error"
                    print(f"❌ Batch insert failed: {error_msg}")
                    # Try individual inserts for this batch as fallback
                    for currency_id, rate, date in batch:
                        if self.add_exchange_rate(currency_id, rate, date):
                            success_count += 1

            sql_query.clear()
            return success_count

        except Exception as e:
            print(f"❌ Error in batch exchange rate insert: {e}")
            return 0
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
        rows = self.get_rows(
            "SELECT COUNT(*) FROM exchange_rates WHERE _id_currency = :currency_id AND date = :date",
            {"currency_id": currency_id, "date": date},
        )
        return rows[0][0] > 0 if rows else False
```

</details>

### ⚙️ Method `clean_invalid_exchange_rates`

```python
def clean_invalid_exchange_rates(self) -> int
```

Clean exchange rates with empty or invalid rate values.

Returns:

- int: Number of cleaned records

<details>
<summary>Code:</summary>

```python
def clean_invalid_exchange_rates(self) -> int:
        query = """DELETE FROM exchange_rates WHERE rate IS NULL OR rate = '' OR rate = 0"""
        cursor = self.db.exec(query)
        if cursor.lastError().isValid():
            print(f"❌ Error cleaning exchange rates: {cursor.lastError().text()}")
            return 0

        affected_rows = cursor.numRowsAffected()
        cursor.clear()
        print(f"🧹 Cleaned {affected_rows} invalid exchange rate records")
        return affected_rows
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
        db = getattr(self, "db", None)
        if db is not None and db.isValid():
            db.close()
            connection_name = self.connection_name
            self.db = None
            QTimer.singleShot(0, lambda: QSqlDatabase.removeDatabase(connection_name))

        # Remove the database connection
        if hasattr(self, "connection_name"):
            QSqlDatabase.removeDatabase(self.connection_name)
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

### ⚙️ Method `create_database_from_sql`

```python
def create_database_from_sql(db_filename: str, sql_file_path: str) -> bool
```

Create a new database from SQL file.

Args:

- `db_filename` (`str`): Path to the database file to create.
- `sql_file_path` (`str`): Path to the SQL file with database schema and data.

Returns:

- `bool`: True if database was created successfully, False otherwise.

<details>
<summary>Code:</summary>

```python
def create_database_from_sql(db_filename: str, sql_file_path: str) -> bool:
        try:
            # Create database directory if it doesn't exist
            db_path = Path(db_filename)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            # Read SQL file
            sql_path = Path(sql_file_path)
            if not sql_path.exists():
                print(f"SQL file not found: {sql_file_path}")
                return False

            sql_content = sql_path.read_text(encoding="utf-8")

            # Create temporary database connection
            temp_connection_name = f"temp_db_{uuid.uuid4().hex[:8]}"

            temp_db = QSqlDatabase.addDatabase("QSQLITE", temp_connection_name)
            temp_db.setDatabaseName(db_filename)

            if not temp_db.open():
                error_msg = temp_db.lastError().text() if temp_db.lastError().isValid() else "Unknown error"
                print(f"❌ Failed to create database: {error_msg}")
                QSqlDatabase.removeDatabase(temp_connection_name)
                return False

            try:
                # Execute SQL commands
                query = QSqlQuery(temp_db)

                # Split SQL content by semicolons and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

                for statement in statements:
                    if not query.exec(statement):
                        error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown error"
                        print(f"❌ Failed to execute SQL statement: {error_msg}")
                        print(f"Statement was: {statement}")
                        return False

                print(f"Database created successfully: {db_filename}")
                return True

            finally:
                temp_db.close()
                QSqlDatabase.removeDatabase(temp_connection_name)

        except Exception as e:
            print(f"Error creating database from SQL file: {e}")
            return False
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
        query = "DELETE FROM exchange_rates WHERE _id = :id"
        return self.execute_simple_query(query, {"id": rate_id})
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

### ⚙️ Method `execute_query`

```python
def execute_query(self, query_text: str, params: dict[str, Any] | None = None) -> QSqlQuery | None
```

Prepare and execute `query_text` with optional bound `params`.

Args:

- `query_text` (`str`): A parametrised SQL statement.
- `params` (`dict[str, Any] | None`): Run-time values to be bound to
  named placeholders in `query_text`. Defaults to `None`.

Returns:

- `QSqlQuery | None`: The executed query when successful, otherwise
  `None`.

<details>
<summary>Code:</summary>

```python
def execute_query(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> QSqlQuery | None:
        # Ensure database connection is valid
        if not self._ensure_connection():
            print(f"Database connection is not available for query: {query_text}")
            return None

        try:
            query = self._create_query()
            if not query.prepare(query_text):
                error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown prepare error"
                print(f"❌ Failed to prepare query: {error_msg}")
                print(f"Query was: {query_text}")
                return None

            if params:
                for key, value in params.items():
                    query.bindValue(f":{key}", value)

            if not query.exec():
                error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown execution error"
                print(f"❌ Failed to execute query: {error_msg}")
                print(f"Query was: {query_text}")
                print(f"Params were: {params}")
                return None

        except Exception as e:
            print(f"❌ Exception during query execution: {e}")
            print(f"Query was: {query_text}")
            print(f"Params were: {params}")
            return None

        else:
            return query
```

</details>

### ⚙️ Method `execute_simple_query`

```python
def execute_simple_query(self, query_text: str, params: dict[str, Any] | None = None) -> bool
```

Execute a simple query and return success status (for INSERT/UPDATE/DELETE operations).

Args:

- `query_text` (`str`): A parametrised SQL statement.
- `params` (`dict[str, Any] | None`): Run-time values to be bound to
  named placeholders in `query_text`. Defaults to `None`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def execute_simple_query(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> bool:
        # Ensure database connection is valid
        if not self._ensure_connection():
            print(f"Database connection is not available for query: {query_text}")
            return False

        try:
            query = self._create_query()
            if not query.prepare(query_text):
                error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown prepare error"
                print(f"Failed to prepare query: {error_msg}")
                print(f"Query was: {query_text}")
                return False

            if params:
                for key, value in params.items():
                    query.bindValue(f":{key}", value)

            success = query.exec()
            if not success:
                error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown execution error"
                print(f"❌ Failed to execute query: {error_msg}")
                print(f"Query was: {query_text}")
                print(f"Params were: {params}")
                return False

        except Exception as e:
            print(f"❌ Exception during query execution: {e}")
            print(f"Query was: {query_text}")
            print(f"Params were: {params}")
            return False

        else:
            # Clear the query to release resources
            query.clear()
            return True
```

</details>

### ⚙️ Method `fill_missing_exchange_rates`

```python
def fill_missing_exchange_rates(self) -> int
```

Fill missing exchange rates with previous available rates for all date gaps.

Returns:
int: Number of exchange rates that were filled.

<details>
<summary>Code:</summary>

```python
def fill_missing_exchange_rates(self) -> int:
        from datetime import datetime, timedelta

        currencies = self.get_currencies_except_usd()
        total_filled = 0

        # Get the earliest transaction date as the absolute start date
        earliest_transaction_date = self.get_earliest_transaction_date()
        if not earliest_transaction_date:
            print("No transactions found, cannot determine start date for filling rates")
            return 0

        start_date = datetime.strptime(earliest_transaction_date, "%Y-%m-%d").date()
        end_date = datetime.now().date()

        print(f"🔄 Filling missing exchange rates from {start_date} to {end_date}")

        for currency_id, currency_code, _, _ in currencies:
            print(f"📊 Processing {currency_code}...")

            # Get ALL existing rates for this currency (не только в диапазоне дат)
            query = """
                SELECT date, rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date ASC
            """
            rows = self.get_rows(query, {"currency_id": currency_id})

            if not rows:
                print(f"⚠️ No exchange rates found for {currency_code}, skipping")
                continue

            # Create a map of existing rates
            existing_rates = {row[0]: row[1] for row in rows}
            print(f"📈 Found {len(existing_rates)} existing rates for {currency_code}")

            # Fill missing dates from start_date to end_date
            current_date = start_date
            last_known_rate = None
            currency_filled = 0

            # Найти первый доступный курс для инициализации last_known_rate
            for date_str in sorted(existing_rates.keys()):
                if datetime.strptime(date_str, "%Y-%m-%d").date() <= current_date:
                    last_known_rate = existing_rates[date_str]
                else:
                    break

            print(f"🔍 Initial rate for {currency_code}: {last_known_rate}")

            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")

                if date_str in existing_rates:
                    # Update last known rate
                    last_known_rate = existing_rates[date_str]
                    print(f"📊 {currency_code} {date_str}: Found existing rate {last_known_rate}")
                elif last_known_rate is not None:
                    # Fill missing date with last known rate
                    print(f"🔍 {currency_code} {date_str}: Missing, trying to fill with {last_known_rate}")
                    if self.add_exchange_rate(currency_id, last_known_rate, date_str):
                        currency_filled += 1
                        total_filled += 1
                        print(f"✅ {currency_code} {date_str}: Filled with rate {last_known_rate}")
                    else:
                        print(f"❌ {currency_code} {date_str}: Failed to add rate")
                else:
                    print(f"⚠️ {currency_code} {date_str}: No known rate to use for filling")

                current_date += timedelta(days=1)

            print(f"📈 Filled {currency_filled} missing dates for {currency_code}")

        print(f"🎉 Total filled: {total_filled} exchange rate records")
        return total_filled
```

</details>

### ⚙️ Method `fill_missing_exchange_rates_in_range`

```python
def fill_missing_exchange_rates_in_range(self, start_date_str: str, end_date_str: str) -> int
```

Fill missing exchange rates in specific date range.

Args:
start_date_str: Start date in YYYY-MM-DD format
end_date_str: End date in YYYY-MM-DD format

Returns:
int: Number of exchange rates that were filled.

<details>
<summary>Code:</summary>

```python
def fill_missing_exchange_rates_in_range(self, start_date_str: str, end_date_str: str) -> int:
        from datetime import datetime, timedelta

        currencies = self.get_currencies_except_usd()
        total_filled = 0

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        print(f"🔄 Filling missing exchange rates from {start_date} to {end_date}")

        for currency_id, currency_code, _, _ in currencies:
            print(f"📊 Processing {currency_code} for range {start_date} to {end_date}...")

            # Get ALL existing rates for this currency (не только в диапазоне)
            query = """
                SELECT date, rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date ASC
            """
            rows = self.get_rows(query, {"currency_id": currency_id})

            if not rows:
                print(f"⚠️ No exchange rates found for {currency_code}, skipping")
                continue

            # Create a map of existing rates
            existing_rates = {row[0]: row[1] for row in rows}

            # Find the most recent rate before start_date for initialization
            last_known_rate = None
            for date_str in sorted(existing_rates.keys()):
                rate_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if rate_date < start_date:
                    last_known_rate = existing_rates[date_str]
                elif rate_date >= start_date:
                    break

            print(f"🔍 Initial rate for {currency_code} before {start_date}: {last_known_rate}")

            # Fill missing dates in the specified range
            current_date = start_date
            currency_filled = 0

            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")

                if date_str in existing_rates:
                    # Update last known rate
                    last_known_rate = existing_rates[date_str]
                    print(f"📊 {currency_code} {date_str}: Found existing rate {last_known_rate}")
                elif last_known_rate is not None:
                    # Check if this date actually needs filling
                    if not self.check_exchange_rate_exists(currency_id, date_str):
                        print(f"🔍 {currency_code} {date_str}: Missing, filling with {last_known_rate}")
                        if self.add_exchange_rate(currency_id, last_known_rate, date_str):
                            currency_filled += 1
                            total_filled += 1
                            print(f"✅ {currency_code} {date_str}: Filled with rate {last_known_rate}")
                        else:
                            print(f"❌ {currency_code} {date_str}: Failed to add rate")
                    else:
                        print(f"📊 {currency_code} {date_str}: Already exists, skipping")
                else:
                    print(f"⚠️ {currency_code} {date_str}: No known rate to use for filling")

                current_date += timedelta(days=1)

            print(f"📈 Filled {currency_filled} missing dates for {currency_code} in range")

        print(f"🎉 Total filled in range: {total_filled} exchange rate records")
        return total_filled
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

- `list[list[Any]]`: List of account records [_id, name, balance, currency_code, is_liquid, is_cash, currency_id].

<details>
<summary>Code:</summary>

```python
def get_all_accounts(self) -> list[list[Any]]:
        rows = self.get_rows("""
            SELECT a._id, a.name, a.balance, c.code, a.is_liquid, a.is_cash, c._id as currency_id
            FROM accounts a
            JOIN currencies c ON a._id_currencies = c._id
            ORDER BY a.name
        """)

        # Convert balances from stored subdivision to actual values
        for row in rows:
            if len(row) >= 4 and row[2] is not None and row[3] is not None:  # balance and currency_code
                currency_code = row[3]
                subdivision = self.get_currency_subdivision_by_code(currency_code)
                row[2] = float(row[2]) / subdivision

        return rows
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

        # Convert amounts, rates and fees from stored subdivision to actual values
        for row in rows:
            if len(row) >= 9:
                # Get currency subdivisions for proper conversion
                from_currency_code = row[1]
                to_currency_code = row[2]

                from_subdivision = self.get_currency_subdivision_by_code(from_currency_code)
                to_subdivision = self.get_currency_subdivision_by_code(to_currency_code)

                # Convert amounts and fees
                if row[3] is not None:  # amount_from
                    row[3] = float(row[3]) / from_subdivision
                if row[4] is not None:  # amount_to
                    row[4] = float(row[4]) / to_subdivision
                if row[5] is not None:  # exchange_rate (already stored as REAL)
                    row[5] = float(row[5])
                if row[6] is not None:  # fee (in from_currency)
                    row[6] = float(row[6]) / from_subdivision

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
        query = """
            SELECT er._id, 'USD', c.code, er.rate, er.date
            FROM exchange_rates er
            JOIN currencies c ON er._id_currency = c._id
            ORDER BY er.date DESC, er._id DESC
        """

        if limit is not None:
            query += f" LIMIT {limit}"

        rows = self.get_rows(query)

        # Rates are already stored as REAL, no conversion needed
        # Just ensure they are float type for consistency and handle empty strings
        for row in rows:
            if len(row) >= 4 and row[3] is not None and row[3] != "":
                try:
                    row[3] = float(row[3])
                except (ValueError, TypeError):
                    row[3] = 0.0  # Set to 0 for invalid values
            elif len(row) >= 4:
                row[3] = 0.0  # Set to 0 for None or empty string

        return rows
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

        if limit is not None:
            query += f" LIMIT {limit}"

        return self.get_rows(query)
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

### ⚙️ Method `get_default_currency`

```python
def get_default_currency(self) -> str
```

Get the default currency code.

Returns:

- `str`: Default currency code or 'RUB' if not set.

<details>
<summary>Code:</summary>

```python
def get_default_currency(self) -> str:
        rows = self.get_rows("SELECT value FROM settings WHERE key = 'default_currency'")
        return rows[0][0] if rows else "RUB"
```

</details>

### ⚙️ Method `get_default_currency_id`

```python
def get_default_currency_id(self) -> int
```

Get the default currency ID.

Returns:

- `int`: Default currency ID or 1 if not found.

<details>
<summary>Code:</summary>

```python
def get_default_currency_id(self) -> int:
        default_code = self.get_default_currency()
        currency_info = self.get_currency_by_code(default_code)
        return currency_info[0] if currency_info else 1
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
        elif transaction_date:
            return transaction_date
        elif exchange_date:
            return exchange_date
        else:
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

- from_currency_id (int): Source currency ID.
- to_currency_id (int): Target currency ID.
- date (str | None): Date for rate lookup. Uses latest if None.

Returns:

- float: Exchange rate or 1.0 if not found/same currency.

<details>
<summary>Code:</summary>

```python
def get_exchange_rate(self, from_currency_id: int, to_currency_id: int, date: str | None = None) -> float:
        if from_currency_id == to_currency_id:
            return 1.0

        # Для избежания загрузки exchange_rates при старте,
        # возвращаем 1.0 если таблица exchange_rates пуста или недоступна
        try:
            # Быстрая проверка наличия данных в таблице
            check_query = "SELECT COUNT(*) FROM exchange_rates LIMIT 1"
            rows = self.get_rows(check_query)
            if not rows or rows[0][0] == 0:
                return 1.0  # Нет данных о курсах
        except Exception:
            return 1.0  # Таблица недоступна

        # Остальная логика остается прежней...
        # Get USD currency ID
        usd_currency = self.get_currency_by_code("USD")
        if not usd_currency:
            return 1.0
        usd_currency_id = usd_currency[0]

        # Now rates are stored as USD → currency (e.g., 1 USD = 79.85 RUB)
        if from_currency_id == usd_currency_id:
            # USD to other currency - direct rate from database
            return self.get_usd_to_currency_rate(to_currency_id, date)
        elif to_currency_id == usd_currency_id:
            # Other currency to USD - inverse of stored rate
            usd_rate = self.get_usd_to_currency_rate(from_currency_id, date)
            return 1.0 / usd_rate if usd_rate != 0 else 1.0
        else:
            # from_currency to to_currency via USD
            from_usd_rate = self.get_usd_to_currency_rate(from_currency_id, date)  # USD → from_currency
            to_usd_rate = self.get_usd_to_currency_rate(to_currency_id, date)  # USD → to_currency
            if from_usd_rate != 0 and to_usd_rate != 0:
                # from_currency → USD → to_currency = (1/from_usd_rate) * to_usd_rate
                return to_usd_rate / from_usd_rate
            return 1.0
```

</details>

### ⚙️ Method `get_filtered_transactions`

```python
def get_filtered_transactions(self, category_type: int | None = None, category_name: str | None = None, currency_code: str | None = None, date_from: str | None = None, date_to: str | None = None) -> list[list[Any]]
```

Get filtered transactions.

Args:

- `category_type` (`int | None`): Filter by category type. Defaults to `None`.
- `category_name` (`str | None`): Filter by category name. Defaults to `None`.
- `currency_code` (`str | None`): Filter by currency code. Defaults to `None`.
- `date_from` (`str | None`): Filter from date. Defaults to `None`.
- `date_to` (`str | None`): Filter to date. Defaults to `None`.

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
    ) -> list[list[Any]]:
        conditions: list[str] = []
        params: dict[str, str | int] = {}

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

### ⚙️ Method `get_id`

```python
def get_id(self, table: str, name_column: str, name_value: str, id_column: str = "_id", condition: str | None = None) -> int | None
```

Return a single ID that matches `name_value` in `table`.

Args:

- `table` (`str`): Target table name.
- `name_column` (`str`): Column that stores the searched value.
- `name_value` (`str`): Searched value itself.
- `id_column` (`str`): Column that stores the ID. Defaults to `"_id"`.
- `condition` (`str | None`): Extra SQL that will be appended to the
  `WHERE` clause. Defaults to `None`.

Returns:

- `int | None`: The found identifier or `None` when the query yields
  no rows.

<details>
<summary>Code:</summary>

```python
def get_id(
        self,
        table: str,
        name_column: str,
        name_value: str,
        id_column: str = "_id",
        condition: str | None = None,
    ) -> int | None:
        # Validate identifiers to eliminate SQL-injection vectors.
        table = _safe_identifier(table)
        name_column = _safe_identifier(name_column)
        id_column = _safe_identifier(id_column)

        # nosec B608 - identifiers are validated by _safe_identifier
        query_text = f"SELECT {id_column} FROM {table} WHERE {name_column} = :name"
        if condition:
            query_text += f" AND {condition}"

        query = self.execute_query(query_text, {"name": name_value})
        if query and query.next():
            result = query.value(0)
            query.clear()  # Clear the query to release resources
            return result
        return None
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
        params = {"currency_id": currency_id}

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
currency_id (int): Currency ID.

Returns:
str | None: Last date in YYYY-MM-DD format or None if no rates exist.

<details>
<summary>Code:</summary>

```python
def get_last_exchange_rate_date(self, currency_id: int) -> str | None:
        rows = self.get_rows(
            "SELECT MAX(date) FROM exchange_rates WHERE _id_currency = :currency_id", {"currency_id": currency_id}
        )
        return rows[0][0] if rows and rows[0][0] else None
```

</details>

### ⚙️ Method `get_last_exchange_rates_update_date`

```python
def get_last_exchange_rates_update_date(self) -> str | None
```

Get the last date when exchange rates were updated.

Returns:
str | None: Last update date in YYYY-MM-DD format or None if never updated.

<details>
<summary>Code:</summary>

```python
def get_last_exchange_rates_update_date(self) -> str | None:
        rows = self.get_rows("SELECT value FROM settings WHERE key = 'last_exchange_rates_update'")
        return rows[0][0] if rows else None
```

</details>

### ⚙️ Method `get_last_two_exchange_rate_records`

```python
def get_last_two_exchange_rate_records(self, currency_id: int) -> list[tuple[str, float]]
```

Get the last two exchange rate records for a currency.

Args:
currency_id (int): Currency ID.

Returns:
list[tuple[str, float]]: List of tuples (date, rate) for the last two records, sorted by date.

<details>
<summary>Code:</summary>

```python
def get_last_two_exchange_rate_records(self, currency_id: int) -> list[tuple[str, float]]:
        rows = self.get_rows(
            """SELECT date, rate
               FROM exchange_rates
               WHERE _id_currency = :currency_id
               ORDER BY date DESC
               LIMIT 2""",
            {"currency_id": currency_id},
        )
        # Return in chronological order (oldest first)
        return [(row[0], float(row[1])) for row in reversed(rows)] if rows else []
```

</details>

### ⚙️ Method `get_missing_exchange_rates_info`

```python
def get_missing_exchange_rates_info(self, date_from: str, date_to: str) -> dict[int, list[str]]
```

Get information about missing exchange rates for each currency.

Checks for missing rates for each day in the date range.

Args:
date_from: Start date in YYYY-MM-DD format
date_to: End date in YYYY-MM-DD format

Returns:
Dictionary mapping currency_id to list of missing dates

<details>
<summary>Code:</summary>

```python
def get_missing_exchange_rates_info(self, date_from: str, date_to: str) -> dict[int, list[str]]:
        from datetime import datetime, timedelta

        missing_info = {}

        # Get all currencies except USD
        currencies = self.get_currencies_except_usd()

        # Generate all dates in the range
        start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        end_date = datetime.strptime(date_to, "%Y-%m-%d").date()

        all_dates = []
        current_date = start_date
        while current_date <= end_date:
            all_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        print(f"Проверяем курсы валют с {date_from} по {date_to} ({len(all_dates)} дней)")

        for currency_id, currency_code, _, _ in currencies:
            # Get existing dates for this currency
            query = """
                SELECT DISTINCT date FROM exchange_rates
                WHERE _id_currency = :currency_id
                AND date BETWEEN :date_from AND :date_to
                ORDER BY date
            """

            rows = self.get_rows(query, {"currency_id": currency_id, "date_from": date_from, "date_to": date_to})

            existing_dates = set(row[0] for row in rows)

            # Find missing dates
            missing_dates = []
            for date_str in all_dates:
                if date_str not in existing_dates:
                    missing_dates.append(date_str)

            # Print information about missing dates
            if missing_dates:
                print(f"📊 {currency_code}: {len(missing_dates)} missing rates")

                # Show first 10 dates as sample
                sample_size = min(10, len(missing_dates))
                sample_dates = missing_dates[:sample_size]
                print(f"    Первые {sample_size} пропущенных дат: {', '.join(sample_dates)}")

                if len(missing_dates) > 10:
                    print(f"    ... и еще {len(missing_dates) - 10} дат")

                # Show date ranges for better understanding
                if len(missing_dates) > 1:
                    print(f"    Диапазон: с {missing_dates[0]} по {missing_dates[-1]}")

                missing_info[currency_id] = missing_dates
            else:
                print(f"✅ {currency_code}: все курсы присутствуют")

        if not missing_info:
            print("✅ Все курсы валют присутствуют в указанном диапазоне дат")
        else:
            total_missing = sum(len(dates) for dates in missing_info.values())
            print(f"\n📈 ИТОГО: {total_missing} пропущенных записей для {len(missing_info)} валют")

            # Show full list of all missing dates for first currency as example
            if missing_info:
                first_currency_id = next(iter(missing_info))
                first_currency_code = next(code for id, code, _, _ in currencies if id == first_currency_id)
                first_missing = missing_info[first_currency_id]

                print(f"\n🔍 ПОЛНЫЙ СПИСОК для {first_currency_code} ({len(first_missing)} дат):")
                for i, date in enumerate(first_missing, 1):
                    print(f"  {i:4d}. {date}")
                    if i >= 50:  # Ограничиваем вывод 50 датами
                        print(f"  ... и еще {len(first_missing) - 50} дат")
                        break

        return missing_info
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
        limit_frequent = int(limit * 0.7)
        limit_recent = limit - limit_frequent

        rows = self.get_rows(query, {"limit_frequent": limit_frequent, "limit_recent": limit_recent})
        return [row[0] for row in rows if row[0]]
```

</details>

### ⚙️ Method `get_rows`

```python
def get_rows(self, query_text: str, params: dict[str, Any] | None = None) -> list[list[Any]]
```

Execute `query_text` and fetch the whole result set.

Args:

- `query_text` (`str`): A SQL statement.
- `params` (`dict[str, Any] | None`): Values to be bound at run time.
  Defaults to `None`.

Returns:

- `list[list[Any]]`: A list whose elements are the records returned by
  the database.

<details>
<summary>Code:</summary>

```python
def get_rows(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> list[list[Any]]:
        query = self.execute_query(query_text, params)
        if query:
            result = self._rows_from_query(query)
            query.clear()  # Clear the query to release resources
            return result
        return []
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
        today = datetime.now().strftime("%Y-%m-%d")
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
        today = datetime.now().strftime("%Y-%m-%d")
        _, expenses = self.get_income_vs_expenses_in_currency(currency_id, today, today)
        return expenses
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
        params = {"currency_id": currency_id}

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

### ⚙️ Method `get_usd_to_currency_rate`

```python
def get_usd_to_currency_rate(self, currency_id: int, date: str | None = None) -> float
```

Get exchange rate from USD to currency (how many currency units for 1 USD).

Uses caching to avoid repeated database queries.

<details>
<summary>Code:</summary>

```python
def get_usd_to_currency_rate(self, currency_id: int, date: str | None = None) -> float:
        # Check if currency is USD
        usd_currency = self.get_currency_by_code("USD")
        if usd_currency and currency_id == usd_currency[0]:
            return 1.0

        # Create cache key
        cache_key = f"{currency_id}_{date or 'latest'}"

        # Check cache (valid for 5 minutes)
        from datetime import datetime, timedelta

        now = datetime.now()
        if (
            self._cache_timestamp
            and (now - self._cache_timestamp) < timedelta(minutes=5)
            and cache_key in self._exchange_rate_cache
        ):
            return self._exchange_rate_cache[cache_key]

        # Query database
        if date:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency = :currency_id AND date <= :date
                ORDER BY date DESC LIMIT 1
            """
            params = {"currency_id": currency_id, "date": date}
        else:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency = :currency_id
                ORDER BY date DESC LIMIT 1
            """
            params = {"currency_id": currency_id}

        rows = self.get_rows(query, params)
        if rows and rows[0][0] is not None and rows[0][0] != "":
            try:
                rate = float(rows[0][0])
                # Update cache
                self._exchange_rate_cache[cache_key] = rate
                self._cache_timestamp = now
                return rate
            except (ValueError, TypeError):
                return 1.0

        return 1.0
```

</details>

### ⚙️ Method `is_database_open`

```python
def is_database_open(self) -> bool
```

Check if the database connection is open.

Returns:

- `bool`: True if database is open, False otherwise.

<details>
<summary>Code:</summary>

```python
def is_database_open(self) -> bool:
        return hasattr(self, "db") and self.db is not None and self.db.isValid() and self.db.isOpen()
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
        # First try to update existing setting
        update_query = "UPDATE settings SET value = :code WHERE key = 'default_currency'"
        if self.execute_simple_query(update_query, {"code": currency_code}):
            # Check if any rows were affected by checking if the setting exists
            check_query = "SELECT COUNT(*) FROM settings WHERE key = 'default_currency'"
            rows = self.get_rows(check_query)
            if rows and rows[0][0] > 0:
                return True

        # If update didn't affect any rows, insert new setting
        insert_query = "INSERT INTO settings (key, value) VALUES ('default_currency', :code)"
        return self.execute_simple_query(insert_query, {"code": currency_code})
```

</details>

### ⚙️ Method `set_last_exchange_rates_update_date`

```python
def set_last_exchange_rates_update_date(self, date: str) -> bool
```

Set the last date when exchange rates were updated.

Args:
date (str): Date in YYYY-MM-DD format.

Returns:
bool: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def set_last_exchange_rates_update_date(self, date: str) -> bool:
        try:
            # First try to update existing setting
            update_query = "UPDATE settings SET value = :date WHERE key = 'last_exchange_rates_update'"
            if self.execute_simple_query(update_query, {"date": date}):
                # Check if any rows were affected
                check_query = "SELECT COUNT(*) FROM settings WHERE key = 'last_exchange_rates_update'"
                rows = self.get_rows(check_query)
                if rows and rows[0][0] > 0:
                    print(f"✅ Updated existing last_exchange_rates_update setting to {date}")
                    return True

            # If update didn't affect any rows, insert new setting
            insert_query = "INSERT INTO settings (key, value) VALUES ('last_exchange_rates_update', :date)"
            success = self.execute_simple_query(insert_query, {"date": date})
            if success:
                print(f"✅ Created new last_exchange_rates_update setting with date {date}")
            else:
                print(f"❌ Failed to create last_exchange_rates_update setting")
            return success
        except Exception as e:
            print(f"❌ Error setting last_exchange_rates_update_date: {e}")
            return False
```

</details>

### ⚙️ Method `table_exists`

```python
def table_exists(self, table_name: str) -> bool
```

Check if a table exists in the database.

Args:

- `table_name` (`str`): Name of the table to check.

Returns:

- `bool`: True if table exists, False otherwise.

<details>
<summary>Code:</summary>

```python
def table_exists(self, table_name: str) -> bool:
        if not self.is_database_open():
            return False

        query = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name", {"table_name": table_name}
        )

        if query and query.next():
            return True
        return False
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

### ⚙️ Method `update_exchange_rate`

```python
def update_exchange_rate(self, currency_id: int, date: str, new_rate: float) -> bool
```

Update an existing exchange rate record.

Args:
currency_id (int): Currency ID.
date (str): Date in YYYY-MM-DD format.
new_rate (float): New exchange rate value.

Returns:
bool: True if update was successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_exchange_rate(self, currency_id: int, date: str, new_rate: float) -> bool:
        try:
            query = """
                UPDATE exchange_rates
                SET rate = :rate
                WHERE _id_currency = :currency_id AND date = :date
            """
            params = {"currency_id": currency_id, "date": date, "rate": new_rate}

            result = self.execute_query(query, params)
            if result:
                result.clear()
                return True
            return False
        except Exception as e:
            print(f"Error updating exchange rate: {e}")
            return False
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

### ⚙️ Method `_create_query`

```python
def _create_query(self) -> QSqlQuery
```

Create a QSqlQuery using this manager's database connection.

Returns:

- `QSqlQuery`: A query object bound to this database connection.

<details>
<summary>Code:</summary>

```python
def _create_query(self) -> QSqlQuery:
        if not self._ensure_connection() or self.db is None:
            error_msg = "❌ Database connection is not available"
            raise ConnectionError(error_msg)
        return QSqlQuery(self.db)
```

</details>

### ⚙️ Method `_ensure_connection`

```python
def _ensure_connection(self) -> bool
```

Ensure database connection is open and valid.

Returns:

- `bool`: True if connection is valid, False otherwise.

<details>
<summary>Code:</summary>

```python
def _ensure_connection(self) -> bool:
        if not hasattr(self, "db") or self.db is None or not self.db.isValid():
            print("Database object is invalid, attempting to reconnect...")
            try:
                self._reconnect()
                return self.db is not None and self.db.isOpen()
            except Exception as e:
                print(f"Failed to reconnect to database: {e}")
                return False

        if self.db is None or not self.db.isOpen():
            print("Database connection is closed, attempting to reopen...")
            if self.db is None or not self.db.open():
                error_msg = self.db.lastError().text() if self.db and self.db.lastError().isValid() else "Unknown error"
                print(f"❌ Failed to reopen database: {error_msg}")
                try:
                    self._reconnect()
                    return self.db is not None and self.db.isOpen()
                except Exception as e:
                    print(f"❌ Failed to reconnect to database: {e}")
                    return False

        return True
```

</details>

### ⚙️ Method `_get_currency_conversion_sql`

```python
def _get_currency_conversion_sql(self, currency_id: int) -> tuple[str, str, dict]
```

Generate SQL for currency conversion via USD.

Args:

- currency_id (int): Target currency ID

Returns:

- tuple[str, str, dict]: (join_clause, conversion_case, extra_params)

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
        else:
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
        else:
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
                # Insert default currency setting
                self.execute_simple_query("INSERT INTO settings (key, value) VALUES ('default_currency', 'RUB')")
                print("✅ Initialized default currency setting")
        except Exception as e:
            print(f"Warning: Could not initialize default settings: {e}")
```

</details>

### ⚙️ Method `_iter_query`

```python
def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]
```

Yield every record in `query` one by one.

Args:

- `query` (`QSqlQuery | None`): A prepared and executed `QSqlQuery`
  object.

Yields:

- `QSqlQuery`: The same object positioned on consecutive records.

<details>
<summary>Code:</summary>

```python
def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]:
        if query is None:
            return
        while query.next():
            yield query
```

</details>

### ⚙️ Method `_reconnect`

```python
def _reconnect(self) -> None
```

Attempt to reconnect to the database.

<details>
<summary>Code:</summary>

```python
def _reconnect(self) -> None:
        if hasattr(self, "db") and self.db is not None and self.db.isValid():
            self.db.close()

        # Remove the old connection
        if hasattr(self, "connection_name"):
            QSqlDatabase.removeDatabase(self.connection_name)

        # Create a new connection
        thread_id = threading.current_thread().ident
        self.connection_name = f"finance_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(self._db_filename)

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown error"
            error_msg = f"❌ Failed to reconnect to database: {error_msg}"
            raise ConnectionError(error_msg)
```

</details>

### ⚙️ Method `_rows_from_query`

```python
def _rows_from_query(self, query: QSqlQuery) -> list[list[Any]]
```

Convert the full result set in `query` into a list of rows.

Args:

- `query` (`QSqlQuery`): An executed query.

Returns:

- `list[list[Any]]`: Every database row represented as a list whose
  elements correspond to column values.

<details>
<summary>Code:</summary>

```python
def _rows_from_query(self, query: QSqlQuery) -> list[list[Any]]:
        result: list[list[Any]] = []
        while query.next():
            row = [query.value(i) for i in range(query.record().count())]
            result.append(row)
        return result
```

</details>

## 🔧 Function `_safe_identifier`

```python
def _safe_identifier(identifier: str) -> str
```

Return `identifier` unchanged if it is a valid SQL identifier.

The function guarantees that the returned string is composed only of
ASCII letters, digits, or underscores and does **not** start with a digit.
It is therefore safe to interpolate directly into an SQL statement.

Args:

- `identifier` (`str`): A candidate string that must be validated to be
  used as a table or column name.

Returns:

- `str`: The validated identifier (identical to the input).

Raises:

- `ValueError`: If `identifier` contains forbidden characters.

<details>
<summary>Code:</summary>

```python
def _safe_identifier(identifier: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        msg = f"Illegal SQL identifier: {identifier!r}"
        raise ValueError(msg)
    return identifier
```

</details>
