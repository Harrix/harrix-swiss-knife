"""Utility for working with a local SQLite database that stores financial information."""

from __future__ import annotations

import re
import threading
import uuid
from collections import Counter
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

    def __del__(self) -> None:
        """Clean up database connection when object is destroyed."""
        try:
            self.close()
        except Exception as e:
            print(f"Warning: Error during database cleanup: {e}")

    def add_account(self, name: str, currency_id: int, balance: float, is_liquid: bool, is_cash: bool) -> bool:
        """Add a new account to the database.

        Args:

        - `name` (`str`): Account name.
        - `currency_id` (`int`): Currency ID.
        - `balance` (`float`): Initial balance.
        - `is_liquid` (`bool`): Whether account is liquid.
        - `is_cash` (`bool`): Whether account is cash.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """INSERT INTO accounts (name, _id_currencies, balance, is_liquid, is_cash)
                   VALUES (:name, :currency_id, :balance, :is_liquid, :is_cash)"""
        params = {
            "name": name,
            "currency_id": currency_id,
            "balance": balance,
            "is_liquid": 1 if is_liquid else 0,
            "is_cash": 1 if is_cash else 0,
        }
        return self.execute_simple_query(query, params)

    def add_category(self, name: str, category_type: str) -> bool:
        """Add a new category to the database.

        Args:

        - `name` (`str`): Category name.
        - `category_type` (`str`): Category type (expense/income/transfer).

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO categories (name, type) VALUES (:name, :type)"
        params = {"name": name, "type": category_type}
        return self.execute_simple_query(query, params)

    def add_currency(self, code: str, name: str, symbol: str) -> bool:
        """Add a new currency to the database.

        Args:

        - `code` (`str`): Currency code (USD, EUR, etc.).
        - `name` (`str`): Currency name.
        - `symbol` (`str`): Currency symbol.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO currencies (code, name, symbol) VALUES (:code, :name, :symbol)"
        params = {"code": code, "name": name, "symbol": symbol}
        return self.execute_simple_query(query, params)

    def add_transaction(
        self,
        transaction_type: str,
        amount: float,
        currency_id: int,
        category_id: int,
        account_id: int | None,
        description: str,
        date: str,
    ) -> bool:
        """Add a new transaction to the database.

        Args:

        - `transaction_type` (`str`): Type of transaction (income/expense/transfer).
        - `amount` (`float`): Transaction amount.
        - `currency_id` (`int`): Currency ID.
        - `category_id` (`int`): Category ID.
        - `account_id` (`int | None`): Account ID (optional).
        - `description` (`str`): Transaction description.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """INSERT INTO transactions (amount, description, _id_categories, _id_currencies, _id_accounts, date)
                   VALUES (:amount, :description, :category_id, :currency_id, :account_id, :date)"""
        params = {
            "amount": amount,
            "description": description,
            "category_id": category_id,
            "currency_id": currency_id,
            "account_id": account_id,
            "date": date,
        }
        return self.execute_simple_query(query, params)

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

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction from the database.

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

    def get_accounts_list(self) -> list[str]:
        """Get list of account names.

        Returns:

        - `list[str]`: List of account names.

        """
        return self.get_items("accounts", "name", order_by="name")

    def get_all_accounts(self) -> list[list[Any]]:
        """Get all accounts with currency information.

        Returns:

        - `list[list[Any]]`: List of account records.

        """
        return self.get_rows("""
            SELECT a._id, a.name, c.code, a.balance, a.is_liquid, a.is_cash
            FROM accounts a
            JOIN currencies c ON a._id_currencies = c._id
            ORDER BY a.name
        """)

    def get_all_categories(self) -> list[list[Any]]:
        """Get all categories.

        Returns:

        - `list[list[Any]]`: List of category records.

        """
        return self.get_rows("SELECT _id, name, type FROM categories ORDER BY name")

    def get_all_currencies(self) -> list[list[Any]]:
        """Get all currencies.

        Returns:

        - `list[list[Any]]`: List of currency records.

        """
        return self.get_rows("SELECT _id, code, name, symbol FROM currencies ORDER BY code")

    def get_all_transactions(self) -> list[list[Any]]:
        """Get all transactions with category and currency information.

        Returns:

        - `list[list[Any]]`: List of transaction records.

        """
        return self.get_rows("""
            SELECT t._id, cat.type, t.amount, c.symbol, cat.name, a.name, t.description, t.date
            FROM transactions t
            JOIN currencies c ON t._id_currencies = c._id
            JOIN categories cat ON t._id_categories = cat._id
            LEFT JOIN accounts a ON t._id_accounts = a._id
            ORDER BY t.date DESC, t._id DESC
        """)

    def get_categories_by_type(self, category_type: str) -> list[str]:
        """Get category names by type.

        Args:

        - `category_type` (`str`): Category type to filter by.

        Returns:

        - `list[str]`: List of category names.

        """
        return self.get_items("categories", "name", condition=f"type = '{category_type}'", order_by="name")

    def get_currencies_list(self) -> list[str]:
        """Get list of currency codes.

        Returns:

        - `list[str]`: List of currency codes.

        """
        return self.get_items("currencies", "code", order_by="code")

    def get_daily_balance(self, date: str) -> float:
        """Get daily balance for a specific date.

        Args:

        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `float`: Daily balance.

        """
        rows = self.get_rows(
            """
            SELECT
                COALESCE(SUM(CASE WHEN cat.type = 1 THEN t.amount ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN cat.type = 0 THEN t.amount ELSE 0 END), 0)
            FROM transactions t
            JOIN categories cat ON t._id_categories = cat._id
            WHERE t.date = :date
        """,
            {"date": date},
        )

        return float(rows[0][0]) if rows and rows[0][0] is not None else 0.0

    def get_filtered_transactions(
        self,
        category: str | None = None,
        transaction_type: str | None = None,
        currency: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[list[Any]]:
        """Get filtered transactions.

        Args:

        - `category` (`str | None`): Filter by category name.
        - `transaction_type` (`str | None`): Filter by transaction type.
        - `currency` (`str | None`): Filter by currency code.
        - `date_from` (`str | None`): Filter from date.
        - `date_to` (`str | None`): Filter to date.

        Returns:

        - `list[list[Any]]`: List of filtered transaction records.

        """
        conditions: list[str] = []
        params: dict[str, str] = {}

        if category:
            conditions.append("cat.name = :category")
            params["category"] = category

        if transaction_type and transaction_type != "All":
            # Map transaction type strings to category type integers
            type_mapping = {"income": 1, "expense": 0, "transfer": 2}
            if transaction_type.lower() in type_mapping:
                conditions.append("cat.type = :type")
                params["type"] = str(type_mapping[transaction_type.lower()])

        if currency:
            conditions.append("c.code = :currency")
            params["currency"] = currency

        if date_from and date_to:
            conditions.append("t.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        query_text = """
            SELECT t._id, cat.type, t.amount, c.symbol, cat.name, a.name, t.description, t.date
            FROM transactions t
            JOIN currencies c ON t._id_currencies = c._id
            JOIN categories cat ON t._id_categories = cat._id
            LEFT JOIN accounts a ON t._id_accounts = a._id
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
        - `id_column` (`str`): Column that stores the ID. Defaults to `"id"`.
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

    def get_items(
        self,
        table: str,
        column: str,
        condition: str | None = None,
        order_by: str | None = None,
    ) -> list[Any]:
        """Return all values stored in `column` from `table`.

        Args:

        - `table` (`str`): Table that will be queried.
        - `column` (`str`): The column to extract.
        - `condition` (`str | None`): Optional `WHERE` clause. Defaults to
          `None`.
        - `order_by` (`str | None`): Optional `ORDER BY` clause. Defaults to
          `None`.

        Returns:

        - `list[Any]`: The resulting data as a flat Python list.

        """
        table = _safe_identifier(table)
        column = _safe_identifier(column)

        # nosec B608 - identifiers are validated by _safe_identifier
        query_text = f"SELECT {column} FROM {table}"
        if condition:
            query_text += f" WHERE {condition}"
        if order_by:
            # The order_by expression may legitimately contain ASC/DESC or
            # multiple columns; validation is left to the caller.
            query_text += f" ORDER BY {order_by}"

        result = []
        query = self.execute_query(query_text)
        if query:
            while query.next():
                result.append(query.value(0))
            query.clear()  # Clear the query to release resources
        return result

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

    def is_database_open(self) -> bool:
        """Check if the database connection is open.

        Returns:

        - `bool`: True if database is open, False otherwise.

        """
        return hasattr(self, "db") and self.db is not None and self.db.isValid() and self.db.isOpen()

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
        self, account_id: int, name: str, currency_id: int, balance: float, is_liquid: bool, is_cash: bool
    ) -> bool:
        """Update an existing account.

        Args:

        - `account_id` (`int`): Account ID.
        - `name` (`str`): Account name.
        - `currency_id` (`int`): Currency ID.
        - `balance` (`float`): Account balance.
        - `is_liquid` (`bool`): Whether account is liquid.
        - `is_cash` (`bool`): Whether account is cash.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """UPDATE accounts
                   SET name = :name, _id_currencies = :currency_id, balance = :balance,
                       is_liquid = :is_liquid, is_cash = :is_cash
                   WHERE _id = :id"""
        params = {
            "name": name,
            "currency_id": currency_id,
            "balance": balance,
            "is_liquid": 1 if is_liquid else 0,
            "is_cash": 1 if is_cash else 0,
            "id": account_id,
        }
        return self.execute_simple_query(query, params)

    def update_category(self, category_id: int, name: str, category_type: str) -> bool:
        """Update an existing category.

        Args:

        - `category_id` (`int`): Category ID.
        - `name` (`str`): Category name.
        - `category_type` (`str`): Category type.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "UPDATE categories SET name = :name, type = :type WHERE _id = :id"
        params = {"name": name, "type": category_type, "id": category_id}
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
        params = {"code": code, "name": name, "symbol": symbol, "id": currency_id}
        return self.execute_simple_query(query, params)

    def update_transaction(
        self,
        transaction_id: int,
        transaction_type: str,
        amount: float,
        currency_id: int,
        category_id: int,
        account_id: int | None,
        description: str,
        date: str,
    ) -> bool:
        """Update an existing transaction.

        Args:

        - `transaction_id` (`int`): Transaction ID.
        - `transaction_type` (`str`): Type of transaction.
        - `amount` (`float`): Transaction amount.
        - `currency_id` (`int`): Currency ID.
        - `category_id` (`int`): Category ID.
        - `account_id` (`int | None`): Account ID (optional).
        - `description` (`str`): Transaction description.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """UPDATE transactions
                   SET amount = :amount, _id_currencies = :currency_id,
                       _id_categories = :category_id, _id_accounts = :account_id,
                       description = :description, date = :date
                   WHERE _id = :id"""
        params = {
            "amount": amount,
            "currency_id": currency_id,
            "category_id": category_id,
            "account_id": account_id,
            "description": description,
            "date": date,
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
