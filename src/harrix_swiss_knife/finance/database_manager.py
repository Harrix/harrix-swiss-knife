"""Utility for working with a local SQLite database that stores finance-related information."""

from __future__ import annotations

import re
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator

from PySide6.QtCore import QTimer
from PySide6.QtSql import QSqlDatabase, QSqlQuery


class DatabaseManager:
    """Manage the connection and operations for a finance tracking database.

    Attributes:

    - `db` (`QSqlDatabase`): A live connection object opened on an SQLite
      database file.
    - `connection_name` (`str`): Unique name for this database connection.

    """

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
            "balance": int(balance * 100),  # Convert to cents
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

    def add_currency(self, code: str, name: str, symbol: str) -> bool:
        """Add a new currency to the database.

        Args:

        - `code` (`str`): Currency code (e.g., USD, EUR).
        - `name` (`str`): Currency name.
        - `symbol` (`str`): Currency symbol.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO currencies (code, name, symbol) VALUES (:code, :name, :symbol)"
        params = {
            "code": code,
            "name": name,
            "symbol": symbol,
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
        query = """INSERT INTO currency_exchanges
                   (_id_currency_from, _id_currency_to, amount_from, amount_to,
                    exchange_rate, fee, date, description)
                   VALUES (:from_id, :to_id, :amount_from, :amount_to,
                           :exchange_rate, :fee, :date, :description)"""
        params = {
            "from_id": currency_from_id,
            "to_id": currency_to_id,
            "amount_from": int(amount_from * 100),  # Convert to cents
            "amount_to": int(amount_to * 100),  # Convert to cents
            "exchange_rate": int(exchange_rate * 100),  # Convert to cents
            "fee": int(fee * 100),  # Convert to cents
            "date": date,
            "description": description,
        }
        return self.execute_simple_query(query, params)

    def add_exchange_rate(self, currency_from_id: int, currency_to_id: int, rate: float, date: str) -> bool:
        """Add a new exchange rate.

        Args:

        - `currency_from_id` (`int`): Source currency ID.
        - `currency_to_id` (`int`): Target currency ID.
        - `rate` (`float`): Exchange rate.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """INSERT INTO exchange_rates (_id_currency_from, _id_currency_to, rate, date)
                   VALUES (:from_id, :to_id, :rate, :date)"""
        params = {
            "from_id": currency_from_id,
            "to_id": currency_to_id,
            "rate": int(rate * 100),  # Convert to cents
            "date": date,
        }
        return self.execute_simple_query(query, params)

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
            "amount": int(amount * 100),  # Convert to cents
            "description": description,
            "category_id": category_id,
            "currency_id": currency_id,
            "date": date,
            "tag": tag,
        }
        return self.execute_simple_query(query, params)

    def check_exchange_rate_exists(self, currency_from_id: int, currency_to_id: int, date: str) -> bool:
        """Check if exchange rate exists for given currencies and date.

        Args:

        - `currency_from_id` (`int`): Source currency ID.
        - `currency_to_id` (`int`): Target currency ID.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if exchange rate exists, False otherwise.

        """
        rows = self.get_rows(
            "SELECT COUNT(*) FROM exchange_rates WHERE _id_currency_from = :from_id AND _id_currency_to = :to_id AND date = :date",
            {"from_id": currency_from_id, "to_id": currency_to_id, "date": date},
        )
        return rows[0][0] > 0 if rows else False

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

    def get_account_balances_in_currency(self, currency_id: int) -> list[tuple[str, float]]:
        """Get all account balances converted to specified currency.

        Args:

        - `currency_id` (`int`): Target currency ID.

        Returns:

        - `list[tuple[str, float]]`: List of (account_name, balance) tuples in target currency.

        """
        query = """
            SELECT a.name,
                   CASE
                       WHEN a._id_currencies = :currency_id THEN a.balance
                       ELSE COALESCE(er.rate * a.balance / 100, a.balance)
                   END as converted_balance
            FROM accounts a
            LEFT JOIN exchange_rates er ON er._id_currency_from = a._id_currencies
                                        AND er._id_currency_to = :currency_id
                                        AND er.date = (
                                            SELECT MAX(date)
                                            FROM exchange_rates er2
                                            WHERE er2._id_currency_from = a._id_currencies
                                              AND er2._id_currency_to = :currency_id
                                        )
            ORDER BY a.name
        """
        rows = self.get_rows(query, {"currency_id": currency_id})
        return [(row[0], float(row[1]) / 100) for row in rows]

    def get_account_by_id(self, account_id: int) -> list[Any] | None:
        """Get account data by ID.

        Args:

        - `account_id` (`int`): Account ID.

        Returns:

        - `list[Any] | None`: Account data or None if not found.

        """
        query = """
            SELECT a._id, a.name, a.balance, c.code, a.is_liquid, a.is_cash
            FROM accounts a
            JOIN currencies c ON a._id_currencies = c._id
            WHERE a._id = :account_id
        """
        rows = self.get_rows(query, {"account_id": account_id})
        return rows[0] if rows else None

    def get_all_accounts(self) -> list[list[Any]]:
        """Get all accounts with currency information.

        Returns:

        - `list[list[Any]]`: List of account records [_id, name, balance, currency_code, is_liquid, is_cash].

        """
        return self.get_rows("""
            SELECT a._id, a.name, a.balance, c.code, a.is_liquid, a.is_cash
            FROM accounts a
            JOIN currencies c ON a._id_currencies = c._id
            ORDER BY a.name
        """)

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
        return self.get_rows("""
            SELECT ce._id, cf.code, ct.code, ce.amount_from, ce.amount_to,
                   ce.exchange_rate, ce.fee, ce.date, ce.description
            FROM currency_exchanges ce
            JOIN currencies cf ON ce._id_currency_from = cf._id
            JOIN currencies ct ON ce._id_currency_to = ct._id
            ORDER BY ce.date DESC, ce._id DESC
        """)

    def get_all_exchange_rates(self) -> list[list[Any]]:
        """Get all exchange rates with currency information.

        Returns:

        - `list[list[Any]]`: List of exchange rate records.

        """
        return self.get_rows("""
            SELECT er._id, cf.code, ct.code, er.rate, er.date
            FROM exchange_rates er
            JOIN currencies cf ON er._id_currency_from = cf._id
            JOIN currencies ct ON er._id_currency_to = ct._id
            ORDER BY er.date DESC, er._id DESC
        """)

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

    def get_exchange_rate(self, from_currency_id: int, to_currency_id: int, date: str | None = None) -> float:
        """Get exchange rate between currencies.

        Args:

        - `from_currency_id` (`int`): Source currency ID.
        - `to_currency_id` (`int`): Target currency ID.
        - `date` (`str | None`): Date for rate lookup. Uses latest if None. Defaults to `None`.

        Returns:

        - `float`: Exchange rate or 1.0 if not found/same currency.

        """
        if from_currency_id == to_currency_id:
            return 1.0

        if date:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency_from = :from_id AND _id_currency_to = :to_id
                  AND date <= :date
                ORDER BY date DESC LIMIT 1
            """
            params = {"from_id": from_currency_id, "to_id": to_currency_id, "date": date}
        else:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency_from = :from_id AND _id_currency_to = :to_id
                ORDER BY date DESC LIMIT 1
            """
            params = {"from_id": from_currency_id, "to_id": to_currency_id}

        rows = self.get_rows(query, params)
        if rows:
            return float(rows[0][0]) / 100  # Convert from cents

        # Try inverse rate
        if date:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency_from = :to_id AND _id_currency_to = :from_id
                  AND date <= :date
                ORDER BY date DESC LIMIT 1
            """
            params = {"from_id": to_currency_id, "to_id": from_currency_id, "date": date}
        else:
            query = """
                SELECT rate FROM exchange_rates
                WHERE _id_currency_from = :to_id AND _id_currency_to = :from_id
                ORDER BY date DESC LIMIT 1
            """
            params = {"from_id": to_currency_id, "to_id": from_currency_id}

        rows = self.get_rows(query, params)
        if rows:
            rate = float(rows[0][0]) / 100
            return 1.0 / rate if rate != 0 else 1.0

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

        # Get income (category type = 1)
        income_query = f"""
            SELECT SUM(
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    ELSE COALESCE(er.rate * t.amount / 100, t.amount)
                END
            ) as total_income
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            LEFT JOIN exchange_rates er ON er._id_currency_from = t._id_currencies
                                        AND er._id_currency_to = :currency_id
                                        AND er.date = (
                                            SELECT MAX(date)
                                            FROM exchange_rates er2
                                            WHERE er2._id_currency_from = t._id_currencies
                                              AND er2._id_currency_to = :currency_id
                                              AND er2.date <= t.date
                                        )
            WHERE cat.type = 1{where_clause}
        """

        # Get expenses (category type = 0)
        expenses_query = f"""
            SELECT SUM(
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    ELSE COALESCE(er.rate * t.amount / 100, t.amount)
                END
            ) as total_expenses
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            LEFT JOIN exchange_rates er ON er._id_currency_from = t._id_currencies
                                        AND er._id_currency_to = :currency_id
                                        AND er.date = (
                                            SELECT MAX(date)
                                            FROM exchange_rates er2
                                            WHERE er2._id_currency_from = t._id_currencies
                                              AND er2._id_currency_to = :currency_id
                                              AND er2.date <= t.date
                                        )
            WHERE cat.type = 0{where_clause}
        """

        income_rows = self.get_rows(income_query, params)
        expenses_rows = self.get_rows(expenses_query, params)

        total_income = float(income_rows[0][0] or 0) / 100 if income_rows and income_rows[0][0] else 0.0
        total_expenses = float(expenses_rows[0][0] or 0) / 100 if expenses_rows and expenses_rows[0][0] else 0.0

        return total_income, total_expenses

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

        query = f"""
            SELECT t.date, SUM(
                CASE
                    WHEN t._id_currencies = :currency_id THEN t.amount
                    ELSE COALESCE(er.rate * t.amount / 100, t.amount)
                END
            ) as total_amount
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            LEFT JOIN exchange_rates er ON er._id_currency_from = t._id_currencies
                                        AND er._id_currency_to = :currency_id
                                        AND er.date = (
                                            SELECT MAX(date)
                                            FROM exchange_rates er2
                                            WHERE er2._id_currency_from = t._id_currencies
                                              AND er2._id_currency_to = :currency_id
                                              AND er2.date <= t.date
                                        )
            WHERE 1=1{where_clause}
            GROUP BY t.date
            ORDER BY t.date ASC
        """

        rows = self.get_rows(query, params)
        return [(row[0], float(row[1]) / 100) for row in rows]

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
            "balance": int(balance * 100),  # Convert to cents
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
            "amount": int(amount * 100),  # Convert to cents
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


def _safe_identifier(identifier: str) -> str:
    """Return `identifier` unchanged if it is a valid SQL identifier.

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

    """
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        msg = f"Illegal SQL identifier: {identifier!r}"
        raise ValueError(msg)
    return identifier
