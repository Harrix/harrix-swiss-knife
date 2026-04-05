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
  - [⚙️ Method `add_habit`](#%EF%B8%8F-method-add_habit)
  - [⚙️ Method `add_process_habit_record`](#%EF%B8%8F-method-add_process_habit_record)
  - [⚙️ Method `close`](#%EF%B8%8F-method-close)
  - [⚙️ Method `create_database_from_sql`](#%EF%B8%8F-method-create_database_from_sql)
  - [⚙️ Method `delete_habit`](#%EF%B8%8F-method-delete_habit)
  - [⚙️ Method `delete_process_habit_record`](#%EF%B8%8F-method-delete_process_habit_record)
  - [⚙️ Method `execute_query`](#%EF%B8%8F-method-execute_query)
  - [⚙️ Method `execute_simple_query`](#%EF%B8%8F-method-execute_simple_query)
  - [⚙️ Method `get_all_habits`](#%EF%B8%8F-method-get_all_habits)
  - [⚙️ Method `get_all_process_habits_records`](#%EF%B8%8F-method-get_all_process_habits_records)
  - [⚙️ Method `get_earliest_process_habit_date`](#%EF%B8%8F-method-get_earliest_process_habit_date)
  - [⚙️ Method `get_filtered_process_habits_records`](#%EF%B8%8F-method-get_filtered_process_habits_records)
  - [⚙️ Method `get_habit_calendar_data`](#%EF%B8%8F-method-get_habit_calendar_data)
  - [⚙️ Method `get_habits_count_today`](#%EF%B8%8F-method-get_habits_count_today)
  - [⚙️ Method `get_habits_years`](#%EF%B8%8F-method-get_habits_years)
  - [⚙️ Method `get_id`](#%EF%B8%8F-method-get_id)
  - [⚙️ Method `get_items`](#%EF%B8%8F-method-get_items)
  - [⚙️ Method `get_limited_process_habits_records`](#%EF%B8%8F-method-get_limited_process_habits_records)
  - [⚙️ Method `get_rows`](#%EF%B8%8F-method-get_rows)
  - [⚙️ Method `is_database_open`](#%EF%B8%8F-method-is_database_open)
  - [⚙️ Method `rows_from_query`](#%EF%B8%8F-method-rows_from_query)
  - [⚙️ Method `table_exists`](#%EF%B8%8F-method-table_exists)
  - [⚙️ Method `update_habit`](#%EF%B8%8F-method-update_habit)
  - [⚙️ Method `update_process_habit_record`](#%EF%B8%8F-method-update_process_habit_record)
  - [⚙️ Method `_create_query`](#%EF%B8%8F-method-_create_query)
  - [⚙️ Method `_ensure_connection`](#%EF%B8%8F-method-_ensure_connection)
  - [⚙️ Method `_iter_query`](#%EF%B8%8F-method-_iter_query)
  - [⚙️ Method `_reconnect`](#%EF%B8%8F-method-_reconnect)

</details>

## 🏛️ Class `DatabaseManager`

```python
class DatabaseManager
```

Manage the connection and operations for a habits tracking database.

Attributes:

- `db` (`QSqlDatabase | None`): A live connection object opened on an SQLite database file.
- `connection_name` (`str`): Unique name for this database connection.

<details>
<summary>Code:</summary>

```python
class DatabaseManager:

    db: QSqlDatabase | None
    connection_name: str
    _db_filename: str
    _db_closed: bool

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in `db_filename`.

        Args:

        - `db_filename` (`str`): The path to the target database file.

        Raises:

        - `ConnectionError`: If the underlying Qt driver fails to open the database.

        """
        # Include thread ID to ensure unique connections across threads
        thread_id = threading.current_thread().ident
        self.connection_name = f"habits_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(db_filename)

        # Store the database filename for potential reconnection
        self._db_filename = db_filename

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown database error"
            msg = f"❌ Failed to open the database: {error_msg}"
            raise ConnectionError(msg)
        self._db_closed: bool = False

    def add_habit(self, name: str, *, is_bool: bool | None = None) -> bool:
        """Add a new habit to the database.

        Args:

        - `name` (`str`): Habit name.
        - `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO habits (name, is_bool) VALUES (:name, :is_bool)"
        params = {
            "name": name,
            "is_bool": 1 if is_bool is True else (0 if is_bool is False else None),
        }
        return self.execute_simple_query(query, params)

    def add_process_habit_record(self, habit_id: int, value: int, date: str) -> bool:
        """Add a new process habit record.

        Args:

        - `habit_id` (`int`): Habit ID.
        - `value` (`int`): Habit value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO process_habits (_id_habit, value, date) VALUES (:habit_id, :value, :date)"
        params = {
            "habit_id": habit_id,
            "value": value,
            "date": date,
        }

        result = self.execute_simple_query(query, params)
        if not result:
            print(f"Failed to add process habit record: habit_id={habit_id}, value={value}, date={date}")
        return result

    def close(self) -> None:
        """Close the database connection."""
        if self._db_closed:
            return
        self._db_closed = True
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

    def delete_habit(self, habit_id: int) -> bool:
        """Delete a habit from the database.

        Args:

        - `habit_id` (`int`): Habit ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM habits WHERE _id = :id"
        return self.execute_simple_query(query, {"id": habit_id})

    def delete_process_habit_record(self, record_id: int) -> bool:
        """Delete a process habit record.

        Args:

        - `record_id` (`int`): Record ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM process_habits WHERE _id = :id"
        return self.execute_simple_query(query, {"id": record_id})

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

        - `QSqlQuery | None`: The executed query when successful, otherwise `None`.

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

    def get_all_habits(self) -> list[list[Any]]:
        """Get all habits with their properties.

        Returns:

        - `list[list[Any]]`: List of habit records [_id, name, is_bool].

        """
        return self.get_rows("SELECT _id, name, is_bool FROM habits")

    def get_all_process_habits_records(self) -> list[list[Any]]:
        """Get all process habits records with habit names.

        Returns:

        - `list[list[Any]]`: List of process habits records [_id, habit_name, value, date].

        """
        return self.get_rows("""
            SELECT ph._id,
                h.name,
                ph.value,
                ph.date
            FROM process_habits ph
            JOIN habits h ON ph._id_habit = h._id
            ORDER BY ph.date DESC, ph._id DESC
        """)

    def get_earliest_process_habit_date(self) -> str | None:
        """Get the earliest date from process_habits table.

        Returns:

        - `str | None`: Date string in YYYY-MM-DD format or None if no records.

        """
        rows = self.get_rows("SELECT MIN(date) FROM process_habits WHERE date IS NOT NULL", {})
        if rows and rows[0][0]:
            return rows[0][0]
        return None

    def get_filtered_process_habits_records(
        self,
        habit_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[list[Any]]:
        """Get filtered process habits records.

        Args:

        - `habit_name` (`str | None`): Filter by habit name. Defaults to `None`.
        - `date_from` (`str | None`): Filter from date (YYYY-MM-DD). Defaults to `None`.
        - `date_to` (`str | None`): Filter to date (YYYY-MM-DD). Defaults to `None`.

        Returns:

        - `list[list[Any]]`: List of filtered process habits records.

        """
        conditions: list[str] = []
        params: dict[str, str] = {}

        if habit_name:
            conditions.append("h.name = :habit")
            params["habit"] = habit_name

        if date_from and date_to:
            conditions.append("ph.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        query_text = """
            SELECT ph._id,
                h.name,
                ph.value,
                ph.date
            FROM process_habits ph
            JOIN habits h ON ph._id_habit = h._id
        """

        if conditions:
            query_text += " WHERE " + " AND ".join(conditions)

        query_text += " ORDER BY ph.date DESC, ph._id DESC"

        return self.get_rows(query_text, params)

    def get_habit_calendar_data(
        self,
        habit_name: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[tuple[str, int]]:
        """Get habit data for calendar heatmap visualization.

        Args:

        - `habit_name` (`str`): Habit name.
        - `date_from` (`str | None`): From date (YYYY-MM-DD). Defaults to `None`.
        - `date_to` (`str | None`): To date (YYYY-MM-DD). Defaults to `None`.

        Returns:

        - `list[tuple[str, int]]`: List of (date, value) tuples sorted by date ascending.

        """
        conditions = ["h.name = :habit"]
        params: dict[str, str] = {"habit": habit_name}

        if date_from and date_to:
            conditions.append("ph.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        query = f"""
            SELECT ph.date, ph.value
            FROM process_habits ph
            JOIN habits h ON ph._id_habit = h._id
            WHERE {" AND ".join(conditions)}
            ORDER BY ph.date ASC
        """

        rows = self.get_rows(query, params)
        return [(row[0], int(row[1])) for row in rows]

    def get_habits_count_today(self) -> int:
        """Get the count of habits records for today.

        Returns:

        - `int`: Number of process habits records for today's date.

        """
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        rows = self.get_rows("SELECT COUNT(*) FROM process_habits WHERE date = :today", {"today": today})
        return rows[0][0] if rows else 0

    def get_habits_years(self) -> list[int]:
        """Get distinct years from process_habits table in descending order.

        Returns:

        - `list[int]`: List of years in descending order.

        """
        query = """
            SELECT DISTINCT CAST(strftime('%Y', date) AS INTEGER) as year
            FROM process_habits
            WHERE date IS NOT NULL
            ORDER BY year DESC
        """
        rows = self.get_rows(query, {})
        return [int(row[0]) for row in rows if row[0] is not None]

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

        - `int | None`: The found identifier or `None` when the query yields no rows.

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
        - `condition` (`str | None`): Optional `WHERE` clause. Defaults to `None`.
        - `order_by` (`str | None`): Optional `ORDER BY` clause. Defaults to `None`.

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

    def get_limited_process_habits_records(self, limit: int = 5000) -> list[list[Any]]:
        """Get limited number of process habits records with habit names.

        Args:

        - `limit` (`int`): Maximum number of records to return. Defaults to 5000.

        Returns:

        - `list[list[Any]]`: List of process habits records [_id, habit_name, value, date].

        """
        return self.get_rows(
            """
            SELECT ph._id,
                h.name,
                ph.value,
                ph.date
            FROM process_habits ph
            JOIN habits h ON ph._id_habit = h._id
            ORDER BY ph.date DESC, ph._id DESC
            LIMIT :limit
        """,
            {"limit": limit},
        )

    def get_rows(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> list[list[Any]]:
        """Execute `query_text` and fetch the whole result set.

        Args:

        - `query_text` (`str`): A SQL statement.
        - `params` (`dict[str, Any] | None`): Values to be bound at run time. Defaults to `None`.

        Returns:

        - `list[list[Any]]`: A list whose elements are the records returned by the database.

        """
        query = self.execute_query(query_text, params)
        if query:
            result = self.rows_from_query(query)
            query.clear()  # Clear the query to release resources
            return result
        return []

    def is_database_open(self) -> bool:
        """Check if the database connection is open.

        Returns:

        - `bool`: True if database is open, False otherwise.

        """
        return hasattr(self, "db") and self.db is not None and self.db.isValid() and self.db.isOpen()

    def rows_from_query(self, query: QSqlQuery) -> list[list[Any]]:
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

        return bool(query and query.next())

    def update_habit(self, habit_id: int, name: str, *, is_bool: bool | None = None) -> bool:
        """Update an existing habit.

        Args:

        - `habit_id` (`int`): Habit ID.
        - `name` (`str`): Habit name.
        - `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "UPDATE habits SET name = :n, is_bool = :is_bool WHERE _id = :id"
        params = {
            "n": name,
            "is_bool": 1 if is_bool is True else (0 if is_bool is False else None),
            "id": habit_id,
        }
        return self.execute_simple_query(query, params)

    def update_process_habit_record(self, record_id: int, habit_id: int, value: int, date: str) -> bool:
        """Update an existing process habit record.

        Args:

        - `record_id` (`int`): Record ID.
        - `habit_id` (`int`): Habit ID.
        - `value` (`int`): Habit value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """
            UPDATE process_habits
            SET _id_habit = :habit_id,
                date = :dt,
                value = :val
            WHERE _id = :id
        """
        params = {
            "habit_id": habit_id,
            "dt": date,
            "val": value,
            "id": record_id,
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

        - `query` (`QSqlQuery | None`): A prepared and executed `QSqlQuery` object.

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
        self.connection_name = f"habits_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(self._db_filename)

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown error"
            error_msg = f"❌ Failed to reconnect to database: {error_msg}"
            raise ConnectionError(error_msg)
        self._db_closed = False
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
        # Include thread ID to ensure unique connections across threads
        thread_id = threading.current_thread().ident
        self.connection_name = f"habits_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(db_filename)

        # Store the database filename for potential reconnection
        self._db_filename = db_filename

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown database error"
            msg = f"❌ Failed to open the database: {error_msg}"
            raise ConnectionError(msg)
        self._db_closed: bool = False
```

</details>

### ⚙️ Method `add_habit`

```python
def add_habit(self, name: str) -> bool
```

Add a new habit to the database.

Args:

- `name` (`str`): Habit name.
- `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_habit(self, name: str, *, is_bool: bool | None = None) -> bool:
        query = "INSERT INTO habits (name, is_bool) VALUES (:name, :is_bool)"
        params = {
            "name": name,
            "is_bool": 1 if is_bool is True else (0 if is_bool is False else None),
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `add_process_habit_record`

```python
def add_process_habit_record(self, habit_id: int, value: int, date: str) -> bool
```

Add a new process habit record.

Args:

- `habit_id` (`int`): Habit ID.
- `value` (`int`): Habit value.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_process_habit_record(self, habit_id: int, value: int, date: str) -> bool:
        query = "INSERT INTO process_habits (_id_habit, value, date) VALUES (:habit_id, :value, :date)"
        params = {
            "habit_id": habit_id,
            "value": value,
            "date": date,
        }

        result = self.execute_simple_query(query, params)
        if not result:
            print(f"Failed to add process habit record: habit_id={habit_id}, value={value}, date={date}")
        return result
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
        if self._db_closed:
            return
        self._db_closed = True
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

### ⚙️ Method `delete_habit`

```python
def delete_habit(self, habit_id: int) -> bool
```

Delete a habit from the database.

Args:

- `habit_id` (`int`): Habit ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_habit(self, habit_id: int) -> bool:
        query = "DELETE FROM habits WHERE _id = :id"
        return self.execute_simple_query(query, {"id": habit_id})
```

</details>

### ⚙️ Method `delete_process_habit_record`

```python
def delete_process_habit_record(self, record_id: int) -> bool
```

Delete a process habit record.

Args:

- `record_id` (`int`): Record ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_process_habit_record(self, record_id: int) -> bool:
        query = "DELETE FROM process_habits WHERE _id = :id"
        return self.execute_simple_query(query, {"id": record_id})
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

- `QSqlQuery | None`: The executed query when successful, otherwise `None`.

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

### ⚙️ Method `get_all_habits`

```python
def get_all_habits(self) -> list[list[Any]]
```

Get all habits with their properties.

Returns:

- `list[list[Any]]`: List of habit records [_id, name, is_bool].

<details>
<summary>Code:</summary>

```python
def get_all_habits(self) -> list[list[Any]]:
        return self.get_rows("SELECT _id, name, is_bool FROM habits")
```

</details>

### ⚙️ Method `get_all_process_habits_records`

```python
def get_all_process_habits_records(self) -> list[list[Any]]
```

Get all process habits records with habit names.

Returns:

- `list[list[Any]]`: List of process habits records [_id, habit_name, value, date].

<details>
<summary>Code:</summary>

```python
def get_all_process_habits_records(self) -> list[list[Any]]:
        return self.get_rows("""
            SELECT ph._id,
                h.name,
                ph.value,
                ph.date
            FROM process_habits ph
            JOIN habits h ON ph._id_habit = h._id
            ORDER BY ph.date DESC, ph._id DESC
        """)
```

</details>

### ⚙️ Method `get_earliest_process_habit_date`

```python
def get_earliest_process_habit_date(self) -> str | None
```

Get the earliest date from process_habits table.

Returns:

- `str | None`: Date string in YYYY-MM-DD format or None if no records.

<details>
<summary>Code:</summary>

```python
def get_earliest_process_habit_date(self) -> str | None:
        rows = self.get_rows("SELECT MIN(date) FROM process_habits WHERE date IS NOT NULL", {})
        if rows and rows[0][0]:
            return rows[0][0]
        return None
```

</details>

### ⚙️ Method `get_filtered_process_habits_records`

```python
def get_filtered_process_habits_records(self, habit_name: str | None = None, date_from: str | None = None, date_to: str | None = None) -> list[list[Any]]
```

Get filtered process habits records.

Args:

- `habit_name` (`str | None`): Filter by habit name. Defaults to `None`.
- `date_from` (`str | None`): Filter from date (YYYY-MM-DD). Defaults to `None`.
- `date_to` (`str | None`): Filter to date (YYYY-MM-DD). Defaults to `None`.

Returns:

- `list[list[Any]]`: List of filtered process habits records.

<details>
<summary>Code:</summary>

```python
def get_filtered_process_habits_records(
        self,
        habit_name: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[list[Any]]:
        conditions: list[str] = []
        params: dict[str, str] = {}

        if habit_name:
            conditions.append("h.name = :habit")
            params["habit"] = habit_name

        if date_from and date_to:
            conditions.append("ph.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        query_text = """
            SELECT ph._id,
                h.name,
                ph.value,
                ph.date
            FROM process_habits ph
            JOIN habits h ON ph._id_habit = h._id
        """

        if conditions:
            query_text += " WHERE " + " AND ".join(conditions)

        query_text += " ORDER BY ph.date DESC, ph._id DESC"

        return self.get_rows(query_text, params)
```

</details>

### ⚙️ Method `get_habit_calendar_data`

```python
def get_habit_calendar_data(self, habit_name: str, date_from: str | None = None, date_to: str | None = None) -> list[tuple[str, int]]
```

Get habit data for calendar heatmap visualization.

Args:

- `habit_name` (`str`): Habit name.
- `date_from` (`str | None`): From date (YYYY-MM-DD). Defaults to `None`.
- `date_to` (`str | None`): To date (YYYY-MM-DD). Defaults to `None`.

Returns:

- `list[tuple[str, int]]`: List of (date, value) tuples sorted by date ascending.

<details>
<summary>Code:</summary>

```python
def get_habit_calendar_data(
        self,
        habit_name: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[tuple[str, int]]:
        conditions = ["h.name = :habit"]
        params: dict[str, str] = {"habit": habit_name}

        if date_from and date_to:
            conditions.append("ph.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        query = f"""
            SELECT ph.date, ph.value
            FROM process_habits ph
            JOIN habits h ON ph._id_habit = h._id
            WHERE {" AND ".join(conditions)}
            ORDER BY ph.date ASC
        """

        rows = self.get_rows(query, params)
        return [(row[0], int(row[1])) for row in rows]
```

</details>

### ⚙️ Method `get_habits_count_today`

```python
def get_habits_count_today(self) -> int
```

Get the count of habits records for today.

Returns:

- `int`: Number of process habits records for today's date.

<details>
<summary>Code:</summary>

```python
def get_habits_count_today(self) -> int:
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        rows = self.get_rows("SELECT COUNT(*) FROM process_habits WHERE date = :today", {"today": today})
        return rows[0][0] if rows else 0
```

</details>

### ⚙️ Method `get_habits_years`

```python
def get_habits_years(self) -> list[int]
```

Get distinct years from process_habits table in descending order.

Returns:

- `list[int]`: List of years in descending order.

<details>
<summary>Code:</summary>

```python
def get_habits_years(self) -> list[int]:
        query = """
            SELECT DISTINCT CAST(strftime('%Y', date) AS INTEGER) as year
            FROM process_habits
            WHERE date IS NOT NULL
            ORDER BY year DESC
        """
        rows = self.get_rows(query, {})
        return [int(row[0]) for row in rows if row[0] is not None]
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

- `int | None`: The found identifier or `None` when the query yields no rows.

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

### ⚙️ Method `get_items`

```python
def get_items(self, table: str, column: str, condition: str | None = None, order_by: str | None = None) -> list[Any]
```

Return all values stored in `column` from `table`.

Args:

- `table` (`str`): Table that will be queried.
- `column` (`str`): The column to extract.
- `condition` (`str | None`): Optional `WHERE` clause. Defaults to `None`.
- `order_by` (`str | None`): Optional `ORDER BY` clause. Defaults to `None`.

Returns:

- `list[Any]`: The resulting data as a flat Python list.

<details>
<summary>Code:</summary>

```python
def get_items(
        self,
        table: str,
        column: str,
        condition: str | None = None,
        order_by: str | None = None,
    ) -> list[Any]:
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
```

</details>

### ⚙️ Method `get_limited_process_habits_records`

```python
def get_limited_process_habits_records(self, limit: int = 5000) -> list[list[Any]]
```

Get limited number of process habits records with habit names.

Args:

- `limit` (`int`): Maximum number of records to return. Defaults to 5000.

Returns:

- `list[list[Any]]`: List of process habits records [_id, habit_name, value, date].

<details>
<summary>Code:</summary>

```python
def get_limited_process_habits_records(self, limit: int = 5000) -> list[list[Any]]:
        return self.get_rows(
            """
            SELECT ph._id,
                h.name,
                ph.value,
                ph.date
            FROM process_habits ph
            JOIN habits h ON ph._id_habit = h._id
            ORDER BY ph.date DESC, ph._id DESC
            LIMIT :limit
        """,
            {"limit": limit},
        )
```

</details>

### ⚙️ Method `get_rows`

```python
def get_rows(self, query_text: str, params: dict[str, Any] | None = None) -> list[list[Any]]
```

Execute `query_text` and fetch the whole result set.

Args:

- `query_text` (`str`): A SQL statement.
- `params` (`dict[str, Any] | None`): Values to be bound at run time. Defaults to `None`.

Returns:

- `list[list[Any]]`: A list whose elements are the records returned by the database.

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
            result = self.rows_from_query(query)
            query.clear()  # Clear the query to release resources
            return result
        return []
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

### ⚙️ Method `rows_from_query`

```python
def rows_from_query(self, query: QSqlQuery) -> list[list[Any]]
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
def rows_from_query(self, query: QSqlQuery) -> list[list[Any]]:
        result: list[list[Any]] = []
        while query.next():
            row = [query.value(i) for i in range(query.record().count())]
            result.append(row)
        return result
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

        return bool(query and query.next())
```

</details>

### ⚙️ Method `update_habit`

```python
def update_habit(self, habit_id: int, name: str) -> bool
```

Update an existing habit.

Args:

- `habit_id` (`int`): Habit ID.
- `name` (`str`): Habit name.
- `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_habit(self, habit_id: int, name: str, *, is_bool: bool | None = None) -> bool:
        query = "UPDATE habits SET name = :n, is_bool = :is_bool WHERE _id = :id"
        params = {
            "n": name,
            "is_bool": 1 if is_bool is True else (0 if is_bool is False else None),
            "id": habit_id,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `update_process_habit_record`

```python
def update_process_habit_record(self, record_id: int, habit_id: int, value: int, date: str) -> bool
```

Update an existing process habit record.

Args:

- `record_id` (`int`): Record ID.
- `habit_id` (`int`): Habit ID.
- `value` (`int`): Habit value.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_process_habit_record(self, record_id: int, habit_id: int, value: int, date: str) -> bool:
        query = """
            UPDATE process_habits
            SET _id_habit = :habit_id,
                date = :dt,
                value = :val
            WHERE _id = :id
        """
        params = {
            "habit_id": habit_id,
            "dt": date,
            "val": value,
            "id": record_id,
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

### ⚙️ Method `_iter_query`

```python
def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]
```

Yield every record in `query` one by one.

Args:

- `query` (`QSqlQuery | None`): A prepared and executed `QSqlQuery` object.

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
        self.connection_name = f"habits_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(self._db_filename)

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown error"
            error_msg = f"❌ Failed to reconnect to database: {error_msg}"
            raise ConnectionError(error_msg)
        self._db_closed = False
```

</details>
