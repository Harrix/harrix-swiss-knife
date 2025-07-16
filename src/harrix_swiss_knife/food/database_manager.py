"""Utility for working with a local SQLite database that stores food-related information."""

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
    """Manage the connection and operations for a food tracking database.

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
        self.connection_name = f"fitness_db_{uuid.uuid4().hex[:8]}_{thread_id}"

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

    def get_all_exercise_types(self) -> list[list[Any]]:
        """Get all exercise types with exercise names.

        Returns:

        - `list[list[Any]]`: List of type records [_id, exercise_name, type_name].

        """
        return self.get_rows("""
            SELECT t._id, e.name, t.type
            FROM types t
            JOIN exercises e ON t._id_exercises = e._id
        """)

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

    def get_kcal_chart_data(self, date_from: str, date_to: str) -> list[tuple[str, float]]:
        """Get calories data for charting.

        Args:

        - `date_from` (`str`): From date (YYYY-MM-DD).
        - `date_to` (`str`): To date (YYYY-MM-DD).

        Returns:

        - `list[tuple[str, float]]`: List of (date, calories) tuples.

        """
        query = """
            SELECT p.date,
                   SUM(p.value * e.calories_per_unit * COALESCE(t.calories_modifier, 1.0)) as total_calories
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            WHERE p.date BETWEEN :date_from AND :date_to
            AND p.date IS NOT NULL
            AND e.calories_per_unit > 0
            GROUP BY p.date
            ORDER BY p.date ASC
        """
        rows = self.get_rows(query, {"date_from": date_from, "date_to": date_to})
        return [(row[0], float(row[1])) for row in rows]

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

    def get_all_food_items(self) -> list[list[Any]]:
        """Get all food items.

        Returns:

        - `list[list[Any]]`: List of food items [_id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories].

        """
        return self.get_rows("""
            SELECT _id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories
            FROM food_items
            ORDER BY name
        """)

    def get_all_food_log_records(self) -> list[list[Any]]:
        """Get all food log records.

        Returns:

        - `list[list[Any]]`: List of food log records [_id, date, weight, portion_calories, calories_per_100g, name, name_en, is_drink].

        """
        return self.get_rows("""
            SELECT _id, date, weight, portion_calories, calories_per_100g, name, name_en, is_drink
            FROM food_log
            ORDER BY date DESC, _id DESC
        """)

    def get_recent_food_log_records(self, limit: int = 5000) -> list[list[Any]]:
        """Get recent food log records for table display.

        Args:

        - `limit` (`int`): Maximum number of records to return. Defaults to `5000`.

        Returns:

        - `list[list[Any]]`: List of recent food log records [_id, date, weight, portion_calories, calories_per_100g, name, name_en, is_drink].

        """
        return self.get_rows(f"""
            SELECT _id, date, weight, portion_calories, calories_per_100g, name, name_en, is_drink
            FROM food_log
            ORDER BY date DESC, _id DESC
            LIMIT {limit}
        """)

    def add_food_item(
        self,
        name: str,
        name_en: str | None = None,
        is_drink: bool = False,
        calories_per_100g: float | None = None,
        default_portion_weight: float | None = None,
        default_portion_calories: float | None = None
    ) -> bool:
        """Add a new food item.

        Args:

        - `name` (`str`): Food item name.
        - `name_en` (`str | None`): English name. Defaults to `None`.
        - `is_drink` (`bool`): Whether it's a drink. Defaults to `False`.
        - `calories_per_100g` (`float | None`): Calories per 100g. Defaults to `None`.
        - `default_portion_weight` (`float | None`): Default portion weight. Defaults to `None`.
        - `default_portion_calories` (`float | None`): Default portion calories. Defaults to `None`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """
            INSERT INTO food_items (name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories)
            VALUES (:name, :name_en, :is_drink, :calories_per_100g, :default_portion_weight, :default_portion_calories)
        """
        params = {
            "name": name,
            "name_en": name_en,
            "is_drink": 1 if is_drink else 0,
            "calories_per_100g": calories_per_100g,
            "default_portion_weight": default_portion_weight,
            "default_portion_calories": default_portion_calories,
        }
        return self.execute_simple_query(query, params)

    def add_food_log_record(
        self,
        date: str,
        calories_per_100g: float | None = None,
        name: str | None = None,
        name_en: str | None = None,
        weight: float | None = None,
        portion_calories: float | None = None,
        is_drink: bool = False
    ) -> bool:
        """Add a new food log record.

        Args:

        - `date` (`str`): Date in YYYY-MM-DD format.
        - `calories_per_100g` (`float | None`): Calories per 100g. Defaults to `None`.
        - `name` (`str | None`): Food name. Defaults to `None`.
        - `name_en` (`str | None`): English food name. Defaults to `None`.
        - `weight` (`float | None`): Weight in grams. Defaults to `None`.
        - `portion_calories` (`float | None`): Portion calories. Defaults to `None`.
        - `is_drink` (`bool`): Whether it's a drink. Defaults to `False`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """
            INSERT INTO food_log (date, weight, portion_calories, calories_per_100g, name, name_en, is_drink)
            VALUES (:date, :weight, :portion_calories, :calories_per_100g, :name, :name_en, :is_drink)
        """
        params = {
            "date": date,
            "weight": weight,
            "portion_calories": portion_calories,
            "calories_per_100g": calories_per_100g,
            "name": name,
            "name_en": name_en,
            "is_drink": 1 if is_drink else 0,
        }
        return self.execute_simple_query(query, params)

    def delete_food_item(self, food_item_id: int) -> bool:
        """Delete a food item.

        Args:

        - `food_item_id` (`int`): Food item ID.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM food_items WHERE _id = :id"
        params = {"id": food_item_id}
        return self.execute_simple_query(query, params)

    def delete_food_log_record(self, record_id: int) -> bool:
        """Delete a food log record.

        Args:

        - `record_id` (`int`): Record ID.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM food_log WHERE _id = :id"
        params = {"id": record_id}
        return self.execute_simple_query(query, params)

    def update_food_item(
        self,
        food_item_id: int,
        name: str,
        name_en: str | None = None,
        is_drink: bool = False,
        calories_per_100g: float | None = None,
        default_portion_weight: float | None = None,
        default_portion_calories: float | None = None
    ) -> bool:
        """Update a food item.

        Args:

        - `food_item_id` (`int`): Food item ID.
        - `name` (`str`): Food item name.
        - `name_en` (`str | None`): English name. Defaults to `None`.
        - `is_drink` (`bool`): Whether it's a drink. Defaults to `False`.
        - `calories_per_100g` (`float | None`): Calories per 100g. Defaults to `None`.
        - `default_portion_weight` (`float | None`): Default portion weight. Defaults to `None`.
        - `default_portion_calories` (`float | None`): Default portion calories. Defaults to `None`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """
            UPDATE food_items
            SET name = :name, name_en = :name_en, is_drink = :is_drink,
                calories_per_100g = :calories_per_100g, default_portion_weight = :default_portion_weight,
                default_portion_calories = :default_portion_calories
            WHERE _id = :id
        """
        params = {
            "id": food_item_id,
            "name": name,
            "name_en": name_en,
            "is_drink": 1 if is_drink else 0,
            "calories_per_100g": calories_per_100g,
            "default_portion_weight": default_portion_weight,
            "default_portion_calories": default_portion_calories,
        }
        return self.execute_simple_query(query, params)

    def update_food_log_record(
        self,
        record_id: int,
        date: str,
        calories_per_100g: float | None = None,
        name: str | None = None,
        name_en: str | None = None,
        weight: float | None = None,
        portion_calories: float | None = None,
        is_drink: bool = False
    ) -> bool:
        """Update a food log record.

        Args:

        - `record_id` (`int`): Record ID.
        - `date` (`str`): Date in YYYY-MM-DD format.
        - `calories_per_100g` (`float | None`): Calories per 100g. Defaults to `None`.
        - `name` (`str | None`): Food name. Defaults to `None`.
        - `name_en` (`str | None`): English food name. Defaults to `None`.
        - `weight` (`float | None`): Weight in grams. Defaults to `None`.
        - `portion_calories` (`float | None`): Portion calories. Defaults to `None`.
        - `is_drink` (`bool`): Whether it's a drink. Defaults to `False`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """
            UPDATE food_log
            SET date = :date, weight = :weight, portion_calories = :portion_calories,
                calories_per_100g = :calories_per_100g, name = :name, name_en = :name_en, is_drink = :is_drink
            WHERE _id = :id
        """
        params = {
            "id": record_id,
            "date": date,
            "weight": weight,
            "portion_calories": portion_calories,
            "calories_per_100g": calories_per_100g,
            "name": name,
            "name_en": name_en,
            "is_drink": 1 if is_drink else 0,
        }
        return self.execute_simple_query(query, params)

    def get_food_items_by_name(self, limit: int = 500) -> list[str]:
        """Get food items sorted by name.

        Args:

        - `limit` (`int`): Maximum number of items to return. Defaults to `500`.

        Returns:

        - `list[str]`: List of food item names.

        """
        query = f"SELECT name FROM food_items ORDER BY name LIMIT {limit}"
        rows = self.get_rows(query)
        return [row[0] for row in rows if row[0]]

    def get_food_item_by_name(self, name: str) -> list[Any] | None:
        """Get food item by name.

        Args:

        - `name` (`str`): Food item name.

        Returns:

        - `list[Any] | None`: Food item data or None if not found.

        """
        query = "SELECT _id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories FROM food_items WHERE name = :name"
        params = {"name": name}
        rows = self.get_rows(query, params)
        return rows[0] if rows else None

    def get_popular_food_items(self, limit: int = 500) -> list[str]:
        """Get popular food items from recent food_log records.

        Args:

        - `limit` (`int`): Maximum number of recent records to analyze. Defaults to `500`.

        Returns:

        - `list[str]`: List of food item names sorted by popularity (most popular first).

        """
        query = f"""
            SELECT name, COUNT(*) as usage_count
            FROM (
                SELECT name FROM food_log
                WHERE name IS NOT NULL AND name != ''
                ORDER BY date DESC, _id DESC
                LIMIT {limit}
            ) as recent_foods
            GROUP BY name
            ORDER BY usage_count DESC, name ASC
        """
        rows = self.get_rows(query)
        return [row[0] for row in rows if row[0]]

    def get_food_log_chart_data(self, date_from: str, date_to: str) -> list[tuple[str, float]]:
        """Get food log data for charting.

        Args:

        - `date_from` (`str`): From date (YYYY-MM-DD).
        - `date_to` (`str`): To date (YYYY-MM-DD).

        Returns:

        - `list[tuple[str, float]]`: List of (date, calories_per_100g) tuples.

        """
        query = """
            SELECT date, SUM(calories_per_100g) as total_calories
            FROM food_log
            WHERE date BETWEEN :date_from AND :date_to
            GROUP BY date
            ORDER BY date ASC
        """
        params = {"date_from": date_from, "date_to": date_to}
        rows = self.get_rows(query, params)

        result = []
        for row in rows:
            try:
                date_str = str(row[0]) if row[0] is not None else ""
                calories_value = row[1]
                if calories_value is None or calories_value == "":
                    calories_float = 0.0
                else:
                    calories_float = float(calories_value)
                result.append((date_str, calories_float))
            except (ValueError, TypeError):
                # Skip invalid rows
                continue

        return result

    def get_food_calories_today(self) -> float:
        """Get total calories consumed today.

        Returns:

        - `float`: Total calories today.

        """
        today = datetime.now().strftime("%Y-%m-%d")
        query = "SELECT SUM(calories_per_100g) FROM food_log WHERE date = :today"
        params = {"today": today}
        rows = self.get_rows(query, params)

        if not rows or not rows[0] or rows[0][0] is None:
            return 0.0

        try:
            # Handle empty string or other non-numeric values
            value = rows[0][0]
            if value == "" or value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            # If conversion fails, return 0.0
            return 0.0

    def get_food_calories_count_today(self) -> int:
        """Get count of food entries today.

        Returns:

        - `int`: Count of food entries today.

        """
        today = datetime.now().strftime("%Y-%m-%d")
        query = "SELECT COUNT(*) FROM food_log WHERE date = :today"
        params = {"today": today}
        rows = self.get_rows(query, params)
        return int(rows[0][0]) if rows else 0

    def get_drinks_weight_today(self) -> int:
        """Get total weight of drinks consumed today.

        Returns:

        - `int`: Total weight of drinks in grams.

        """
        today = datetime.now().strftime("%Y-%m-%d")
        query = "SELECT SUM(weight) FROM food_log WHERE date = :today AND is_drink = 1 AND weight IS NOT NULL"
        params = {"today": today}
        rows = self.get_rows(query, params)
        try:
            return int(rows[0][0]) if rows and rows[0][0] is not None and rows[0][0] != "" else 0
        except (ValueError, TypeError):
            return 0

    def get_calories_per_day(self) -> list[list[Any]]:
        """Get calories consumed per day for all days.

        Returns:

        - `list[list[Any]]`: List of [date, total_calories] records.

        """
        query = """
            SELECT
                date,
                SUM(
                    CASE
                        WHEN portion_calories IS NOT NULL AND portion_calories > 0
                        THEN portion_calories
                        WHEN calories_per_100g IS NOT NULL AND calories_per_100g > 0 AND weight IS NOT NULL AND weight > 0
                        THEN (calories_per_100g * weight) / 100
                        ELSE 0
                    END
                ) as total_calories
            FROM food_log
            GROUP BY date
            ORDER BY date DESC
        """
        return self.get_rows(query)

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
        self.connection_name = f"fitness_db_{uuid.uuid4().hex[:8]}_{thread_id}"

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
