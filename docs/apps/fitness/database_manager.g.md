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
  - [⚙️ Method `add_exercise`](#%EF%B8%8F-method-add_exercise)
  - [⚙️ Method `add_exercise_type`](#%EF%B8%8F-method-add_exercise_type)
  - [⚙️ Method `add_process_record`](#%EF%B8%8F-method-add_process_record)
  - [⚙️ Method `add_weight_record`](#%EF%B8%8F-method-add_weight_record)
  - [⚙️ Method `check_exercise_exists`](#%EF%B8%8F-method-check_exercise_exists)
  - [⚙️ Method `close`](#%EF%B8%8F-method-close)
  - [⚙️ Method `create_database_from_sql`](#%EF%B8%8F-method-create_database_from_sql)
  - [⚙️ Method `delete_exercise`](#%EF%B8%8F-method-delete_exercise)
  - [⚙️ Method `delete_exercise_type`](#%EF%B8%8F-method-delete_exercise_type)
  - [⚙️ Method `delete_process_record`](#%EF%B8%8F-method-delete_process_record)
  - [⚙️ Method `delete_weight_record`](#%EF%B8%8F-method-delete_weight_record)
  - [⚙️ Method `execute_query`](#%EF%B8%8F-method-execute_query)
  - [⚙️ Method `execute_simple_query`](#%EF%B8%8F-method-execute_simple_query)
  - [⚙️ Method `get_all_exercise_types`](#%EF%B8%8F-method-get_all_exercise_types)
  - [⚙️ Method `get_all_exercises`](#%EF%B8%8F-method-get_all_exercises)
  - [⚙️ Method `get_all_process_records`](#%EF%B8%8F-method-get_all_process_records)
  - [⚙️ Method `get_all_weight_records`](#%EF%B8%8F-method-get_all_weight_records)
  - [⚙️ Method `get_earliest_exercise_date`](#%EF%B8%8F-method-get_earliest_exercise_date)
  - [⚙️ Method `get_earliest_process_date`](#%EF%B8%8F-method-get_earliest_process_date)
  - [⚙️ Method `get_earliest_weight_date`](#%EF%B8%8F-method-get_earliest_weight_date)
  - [⚙️ Method `get_exercise_calories_info`](#%EF%B8%8F-method-get_exercise_calories_info)
  - [⚙️ Method `get_exercise_chart_data`](#%EF%B8%8F-method-get_exercise_chart_data)
  - [⚙️ Method `get_exercise_max_values`](#%EF%B8%8F-method-get_exercise_max_values)
  - [⚙️ Method `get_exercise_name_by_id`](#%EF%B8%8F-method-get_exercise_name_by_id)
  - [⚙️ Method `get_exercise_steps_records`](#%EF%B8%8F-method-get_exercise_steps_records)
  - [⚙️ Method `get_exercise_total_today`](#%EF%B8%8F-method-get_exercise_total_today)
  - [⚙️ Method `get_exercise_types`](#%EF%B8%8F-method-get_exercise_types)
  - [⚙️ Method `get_exercise_unit`](#%EF%B8%8F-method-get_exercise_unit)
  - [⚙️ Method `get_exercises_by_frequency`](#%EF%B8%8F-method-get_exercises_by_frequency)
  - [⚙️ Method `get_exercises_by_last_execution`](#%EF%B8%8F-method-get_exercises_by_last_execution)
  - [⚙️ Method `get_filtered_process_records`](#%EF%B8%8F-method-get_filtered_process_records)
  - [⚙️ Method `get_filtered_statistics_data`](#%EF%B8%8F-method-get_filtered_statistics_data)
  - [⚙️ Method `get_id`](#%EF%B8%8F-method-get_id)
  - [⚙️ Method `get_items`](#%EF%B8%8F-method-get_items)
  - [⚙️ Method `get_kcal_chart_data`](#%EF%B8%8F-method-get_kcal_chart_data)
  - [⚙️ Method `get_kcal_today`](#%EF%B8%8F-method-get_kcal_today)
  - [⚙️ Method `get_last_executed_exercise`](#%EF%B8%8F-method-get_last_executed_exercise)
  - [⚙️ Method `get_last_exercise_date`](#%EF%B8%8F-method-get_last_exercise_date)
  - [⚙️ Method `get_last_exercise_dates`](#%EF%B8%8F-method-get_last_exercise_dates)
  - [⚙️ Method `get_last_exercise_record`](#%EF%B8%8F-method-get_last_exercise_record)
  - [⚙️ Method `get_last_weight`](#%EF%B8%8F-method-get_last_weight)
  - [⚙️ Method `get_limited_process_records`](#%EF%B8%8F-method-get_limited_process_records)
  - [⚙️ Method `get_rows`](#%EF%B8%8F-method-get_rows)
  - [⚙️ Method `get_sets_chart_data`](#%EF%B8%8F-method-get_sets_chart_data)
  - [⚙️ Method `get_sets_count_today`](#%EF%B8%8F-method-get_sets_count_today)
  - [⚙️ Method `get_statistics_data`](#%EF%B8%8F-method-get_statistics_data)
  - [⚙️ Method `get_weight_chart_data`](#%EF%B8%8F-method-get_weight_chart_data)
  - [⚙️ Method `is_database_open`](#%EF%B8%8F-method-is_database_open)
  - [⚙️ Method `is_exercise_type_required`](#%EF%B8%8F-method-is_exercise_type_required)
  - [⚙️ Method `rows_from_query`](#%EF%B8%8F-method-rows_from_query)
  - [⚙️ Method `table_exists`](#%EF%B8%8F-method-table_exists)
  - [⚙️ Method `update_exercise`](#%EF%B8%8F-method-update_exercise)
  - [⚙️ Method `update_exercise_type`](#%EF%B8%8F-method-update_exercise_type)
  - [⚙️ Method `update_process_record`](#%EF%B8%8F-method-update_process_record)
  - [⚙️ Method `update_weight_record`](#%EF%B8%8F-method-update_weight_record)
  - [⚙️ Method `_create_query`](#%EF%B8%8F-method-_create_query)
  - [⚙️ Method `_ensure_connection`](#%EF%B8%8F-method-_ensure_connection)
  - [⚙️ Method `_iter_query`](#%EF%B8%8F-method-_iter_query)
  - [⚙️ Method `_reconnect`](#%EF%B8%8F-method-_reconnect)

</details>

## 🏛️ Class `DatabaseManager`

```python
class DatabaseManager
```

Manage the connection and operations for a fitness tracking database.

Attributes:

- `db` (`QSqlDatabase`): A live connection object opened on an SQLite database file.
- `connection_name` (`str`): Unique name for this database connection.

<details>
<summary>Code:</summary>

```python
class DatabaseManager:

    db: QSqlDatabase
    connection_name: str
    _db_filename: str

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in `db_filename`.

        Args:

        - `db_filename` (`str`): The path to the target database file.

        Raises:

        - `ConnectionError`: If the underlying Qt driver fails to open the database.

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

    def add_exercise(self, name: str, unit: str, *, is_type_required: bool, calories_per_unit: float = 0.0) -> bool:
        """Add a new exercise to the database.

        Args:

        - `name` (`str`): Exercise name.
        - `unit` (`str`): Unit of measurement.
        - `is_type_required` (`bool`): Whether exercise type is required.
        - `calories_per_unit` (`float`): Calories burned per unit. Defaults to `0.0`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = (
            "INSERT INTO exercises (name, unit, is_type_required, calories_per_unit) "
            "VALUES (:name, :unit, :is_type_required, :calories_per_unit)"
        )
        params = {
            "name": name,
            "unit": unit,
            "is_type_required": 1 if is_type_required else 0,
            "calories_per_unit": calories_per_unit,
        }
        return self.execute_simple_query(query, params)

    def add_exercise_type(self, exercise_id: int, type_name: str, calories_modifier: float = 1.0) -> bool:
        """Add a new exercise type.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `type_name` (`str`): Type name.
        - `calories_modifier` (`float`): Calories modifier for this type. Defaults to `1.0`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO types (_id_exercises, type, calories_modifier) VALUES (:ex, :tp, :calories_modifier)"
        return self.execute_simple_query(
            query, {"ex": exercise_id, "tp": type_name, "calories_modifier": calories_modifier}
        )

    def add_process_record(self, exercise_id: int, type_id: int, value: str, date: str) -> bool:
        """Add a new process record.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `type_id` (`int`): Type ID (-1 for no type).
        - `value` (`str`): Exercise value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = (
            "INSERT INTO process (_id_exercises, _id_types, value, date) VALUES (:exercise_id, :type_id, :value, :date)"
        )
        params = {
            "exercise_id": exercise_id,
            "type_id": type_id,
            "value": value,
            "date": date,
        }

        result = self.execute_simple_query(query, params)
        if not result:
            print(
                f"Failed to add process record: exercise_id={exercise_id}, "
                f"type_id={type_id}, value={value}, date={date}"
            )
        return result

    def add_weight_record(self, value: float, date: str) -> bool:
        """Add a new weight record.

        Args:

        - `value` (`float`): Weight value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO weight (value, date) VALUES (:val, :dt)"
        return self.execute_simple_query(query, {"val": value, "dt": date})

    def check_exercise_exists(self, exercise_id: int) -> bool:
        """Check if exercise exists by ID.

        Args:

        - `exercise_id` (`int`): Exercise ID to check.

        Returns:

        - `bool`: True if exercise exists, False otherwise.

        """
        rows = self.get_rows("SELECT 1 FROM exercises WHERE _id = :id LIMIT 1", {"id": exercise_id})
        return len(rows) > 0

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

    def delete_exercise(self, exercise_id: int) -> bool:
        """Delete an exercise from the database.

        Args:

        - `exercise_id` (`int`): Exercise ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM exercises WHERE _id = :id"
        return self.execute_simple_query(query, {"id": exercise_id})

    def delete_exercise_type(self, type_id: int) -> bool:
        """Delete an exercise type.

        Args:

        - `type_id` (`int`): Type ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM types WHERE _id = :id"
        return self.execute_simple_query(query, {"id": type_id})

    def delete_process_record(self, record_id: int) -> bool:
        """Delete a process record.

        Args:

        - `record_id` (`int`): Record ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM process WHERE _id = :id"
        return self.execute_simple_query(query, {"id": record_id})

    def delete_weight_record(self, record_id: int) -> bool:
        """Delete a weight record.

        Args:

        - `record_id` (`int`): Record ID to delete.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "DELETE FROM weight WHERE _id = :id"
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

    def get_all_exercise_types(self) -> list[list[Any]]:
        """Get all exercise types with exercise names.

        Returns:

        - `list[list[Any]]`: List of type records [_id, exercise_name, type_name, calories_modifier].

        """
        return self.get_rows("""
            SELECT t._id, e.name, t.type, t.calories_modifier
            FROM types t
            JOIN exercises e ON t._id_exercises = e._id
        """)

    def get_all_exercises(self) -> list[list[Any]]:
        """Get all exercises with their properties.

        Returns:

        - `list[list[Any]]`: List of exercise records [_id, name, unit, is_type_required, calories_per_unit].

        """
        return self.get_rows("SELECT _id, name, unit, is_type_required, calories_per_unit FROM exercises")

    def get_all_process_records(self) -> list[list[Any]]:
        """Get all process records with exercise and type names.

        Returns:

        - `list[list[Any]]`: List of process records [_id, exercise_name, type_name, value, unit, date].

        """
        return self.get_rows("""
            SELECT p._id,
                e.name,
                IFNULL(t.type, ''),
                p.value,
                e.unit,
                p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t
                ON p._id_types = t._id
                AND t._id_exercises = e._id
            ORDER BY p.date DESC, p._id DESC
        """)

    def get_all_weight_records(self) -> list[list[Any]]:
        """Get all weight records.

        Returns:

        - `list[list[Any]]`: List of weight records [_id, value, date].

        """
        return self.get_rows("SELECT _id, value, date FROM weight ORDER BY date DESC")

    def get_earliest_exercise_date(self, exercise_name: str, exercise_type: str | None = None) -> str | None:
        """Get the earliest date for a specific exercise.

        Args:

        - `exercise_name` (`str`): Exercise name.
        - `exercise_type` (`str | None`): Exercise type. Defaults to `None` for all types.

        Returns:

        - `str | None`: Earliest date in YYYY-MM-DD format or None if no data.

        """
        conditions = ["e.name = :exercise"]
        params = {"exercise": exercise_name}

        if exercise_type and exercise_type != "All types":
            conditions.append("t.type = :type")
            params["type"] = exercise_type

        query = f"""
            SELECT MIN(p.date)
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            WHERE {" AND ".join(conditions)}
            AND p.date IS NOT NULL"""

        rows = self.get_rows(query, params)
        return rows[0][0] if rows and rows[0][0] else None

    def get_earliest_process_date(self) -> str | None:
        """Get the earliest date from process records.

        Returns:

        - `str | None`: Earliest date in YYYY-MM-DD format or None if no data.

        """
        rows = self.get_rows("SELECT MIN(date) FROM process WHERE date IS NOT NULL")
        return rows[0][0] if rows and rows[0][0] else None

    def get_earliest_weight_date(self) -> str | None:
        """Get the earliest date from weight records.

        Returns:

        - `str | None`: Earliest date in YYYY-MM-DD format or None if no data.

        """
        rows = self.get_rows("SELECT MIN(date) FROM weight WHERE date IS NOT NULL")
        return rows[0][0] if rows and rows[0][0] else None

    def get_exercise_calories_info(self, exercise_id: int) -> tuple[float, list[tuple[str, float]]]:
        """Get calories information for an exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `tuple[float, list[tuple[str, float]]]`: Tuple of (calories_per_unit, [(type_name, calories_modifier), ...]).

        """
        # Get exercise calories_per_unit
        exercise_rows = self.get_rows("SELECT calories_per_unit FROM exercises WHERE _id = :id", {"id": exercise_id})
        calories_per_unit = exercise_rows[0][0] if exercise_rows else 0.0

        # Get types with their calories modifiers
        type_rows = self.get_rows(
            "SELECT type, calories_modifier FROM types WHERE _id_exercises = :id", {"id": exercise_id}
        )
        type_modifiers = [(row[0], row[1]) for row in type_rows]

        return calories_per_unit, type_modifiers

    def get_exercise_chart_data(
        self,
        exercise_name: str,
        exercise_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[tuple[str, str]]:
        """Get exercise data for charting.

        Args:

        - `exercise_name` (`str`): Exercise name.
        - `exercise_type` (`str | None`): Exercise type. Defaults to `None` for all types.
        - `date_from` (`str | None`): From date (YYYY-MM-DD). Defaults to `None`.
        - `date_to` (`str | None`): To date (YYYY-MM-DD). Defaults to `None`.

        Returns:

        - `list[tuple[str, str]]`: List of (date, value) tuples.

        """
        conditions = ["e.name = :exercise"]
        params = {"exercise": exercise_name}

        if date_from and date_to:
            conditions.append("p.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        if exercise_type and exercise_type != "All types":
            conditions.append("t.type = :type")
            params["type"] = exercise_type

        query = f"""
            SELECT p.date, p.value
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            WHERE {" AND ".join(conditions)}
            ORDER BY p.date ASC"""

        rows = self.get_rows(query, params)
        return [(row[0], row[1]) for row in rows]

    def get_exercise_max_values(
        self, exercise_id: int, type_id: int, date_from: str | None = None
    ) -> tuple[float, float]:
        """Get all-time and yearly max values for an exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `type_id` (`int`): Type ID (-1 for no type).
        - `date_from` (`str | None`): Start date for yearly calculation (YYYY-MM-DD). Defaults to `None`.

        Returns:

        - `tuple[float, float]`: Tuple of (all_time_max, yearly_max).

        """
        conditions = ["p._id_exercises = :ex_id"]
        params: dict[str, Any] = {"ex_id": exercise_id}

        if type_id != -1:
            conditions.append("p._id_types = :type_id")
            params["type_id"] = type_id
        else:
            conditions.append("p._id_types = -1")

        # Get all-time max
        all_time_query = f"""
            SELECT MAX(CAST(p.value AS REAL)) as max_value
            FROM process p
            WHERE {" AND ".join(conditions)}"""

        all_time_rows = self.get_rows(all_time_query, params)
        all_time_max = 0.0
        if all_time_rows and all_time_rows[0][0] is not None and all_time_rows[0][0] != "":
            try:
                all_time_max = float(all_time_rows[0][0])
            except (ValueError, TypeError):
                all_time_max = 0.0

        # Get yearly max if date_from provided
        yearly_max = 0.0
        if date_from:
            yearly_conditions = [*conditions, "p.date >= :year_ago"]
            yearly_params = params.copy()
            yearly_params["year_ago"] = date_from

            yearly_query = f"""
                SELECT MAX(CAST(p.value AS REAL)) as max_value
                FROM process p
                WHERE {" AND ".join(yearly_conditions)}"""

            yearly_rows = self.get_rows(yearly_query, yearly_params)
            if yearly_rows and yearly_rows[0][0] is not None and yearly_rows[0][0] != "":
                try:
                    yearly_max = float(yearly_rows[0][0])
                except (ValueError, TypeError):
                    yearly_max = 0.0

        return all_time_max, yearly_max

    def get_exercise_name_by_id(self, exercise_id: int) -> str | None:
        """Get exercise name by ID.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `str | None`: Exercise name or None if not found.

        """
        rows = self.get_rows("SELECT name FROM exercises WHERE _id = :id", {"id": exercise_id})
        return rows[0][0] if rows else None

    def get_exercise_steps_records(self, exercise_id: int) -> list[tuple[str, int, str]]:
        """Get steps records grouped by date.

        Args:

        - `exercise_id` (`int`): Exercise ID for steps.

        Returns:

        - `list[tuple[str, int, str]]`: List of (date, record_count, values) tuples.

        """
        rows = self.get_rows(
            """
            SELECT date, COUNT(*) as record_count, GROUP_CONCAT(value, ', ') as step_values
            FROM process
            WHERE _id_exercises = :id
            AND date IS NOT NULL
            GROUP BY date
            ORDER BY date ASC""",
            {"id": exercise_id},
        )

        # Convert to proper tuple format
        return [(row[0], int(row[1]), row[2]) for row in rows]

    def get_exercise_total_today(self, exercise_id: int) -> float:
        """Get the total value for a specific exercise today.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `float`: Total value for the exercise today, or 0.0 if no records found.

        """
        today = datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime(
            "%Y-%m-%d"
        )
        rows = self.get_rows(
            "SELECT SUM(CAST(value AS REAL)) FROM process WHERE _id_exercises = :ex_id AND date = :today",
            {"ex_id": exercise_id, "today": today},
        )
        if rows and rows[0][0] is not None:
            try:
                return float(rows[0][0])
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    def get_exercise_types(self, exercise_id: int) -> list[str]:
        """Get all types for a specific exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `list[str]`: List of type names.

        """
        return self.get_items("types", "type", condition=f"_id_exercises = {exercise_id}")

    def get_exercise_unit(self, exercise_name: str) -> str:
        """Get the unit of measurement for a given exercise.

        Args:

        - `exercise_name` (`str`): Name of the exercise.

        Returns:

        - `str`: Unit of measurement, or "times" as default.

        """
        rows = self.get_rows("SELECT unit FROM exercises WHERE name = :name", {"name": exercise_name})
        if rows and rows[0][0]:
            return rows[0][0]
        return "times"

    def get_exercises_by_frequency(self, limit: int = 500) -> list[str]:
        """Return exercise names ordered by frequency in recent `limit` rows.

        Args:

        - `limit` (`int`): Number of most recent rows from the `process` table to analyse. Defaults to `500`.

        Returns:

        - `list[str]`: Exercise names sorted by how often they appear; exercises
          not encountered in the inspected slice are appended afterwards.

        """
        if limit <= 0:
            return []

        # Full list of exercises `{id: name}`.
        all_exercises = {row[0]: row[1] for row in self.get_rows("SELECT _id, name FROM exercises")}

        # Recent usage statistics.
        recent_records = self.get_rows(
            "SELECT _id_exercises FROM process ORDER BY _id DESC LIMIT :limit",
            {"limit": limit},
        )
        exercise_counts = Counter(row[0] for row in recent_records)

        # Most common first.
        sorted_exercises = [
            all_exercises[ex_id] for ex_id, _ in exercise_counts.most_common() if ex_id in all_exercises
        ]

        # Preserve exercises not present in sorted_exercises.
        remainder = [name for name in all_exercises.values() if name not in sorted_exercises]
        return sorted_exercises + remainder

    def get_exercises_by_last_execution(self) -> list[str]:
        """Return exercise names ordered by last execution date (most recent first).

        Returns:

        - `list[str]`: Exercise names sorted by last execution date.
          Exercises never executed are appended at the end.

        """
        # Full list of exercises `{id: name}`.
        all_exercises = {row[0]: row[1] for row in self.get_rows("SELECT _id, name FROM exercises")}

        # Get exercises with their last execution date.
        last_execution = self.get_rows(
            """
            SELECT e._id, e.name, MAX(p.date) as last_date
            FROM exercises e
            LEFT JOIN process p ON e._id = p._id_exercises
            GROUP BY e._id, e.name
            ORDER BY last_date DESC NULLS LAST, e.name ASC
            """
        )

        return [row[1] for row in last_execution]

    def get_filtered_process_records(
        self,
        exercise_name: str | None = None,
        exercise_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[list[Any]]:
        """Get filtered process records.

        Args:

        - `exercise_name` (`str | None`): Filter by exercise name. Defaults to `None`.
        - `exercise_type` (`str | None`): Filter by exercise type. Defaults to `None`.
        - `date_from` (`str | None`): Filter from date (YYYY-MM-DD). Defaults to `None`.
        - `date_to` (`str | None`): Filter to date (YYYY-MM-DD). Defaults to `None`.

        Returns:

        - `list[list[Any]]`: List of filtered process records.

        """
        conditions: list[str] = []
        params: dict[str, str] = {}

        if exercise_name:
            conditions.append("e.name = :exercise")
            params["exercise"] = exercise_name

        if exercise_type:
            conditions.append("t.type = :type")
            params["type"] = exercise_type

        if date_from and date_to:
            conditions.append("p.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        query_text = """
            SELECT p._id,
                e.name,
                IFNULL(t.type, ''),
                p.value,
                e.unit,
                p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t
                ON p._id_types = t._id
                AND t._id_exercises = e._id
        """

        if conditions:
            query_text += " WHERE " + " AND ".join(conditions)

        query_text += " ORDER BY p.date DESC, p._id DESC"

        return self.get_rows(query_text, params)

    def get_filtered_statistics_data(self, exercise_name: str | None = None) -> list[tuple[str, str, float, str]]:
        """Get filtered data for statistics display.

        Args:

        - `exercise_name` (`str | None`): Exercise name to filter by. Defaults to `None` for all exercises.

        Returns:

        - `list[tuple[str, str, float, str]]`: List of (exercise_name, type_name, value, date) tuples.

        """
        conditions = []
        params = {}

        if exercise_name:
            conditions.append("e.name = :exercise")
            params["exercise"] = exercise_name

        query = """
            SELECT e.name,
                   IFNULL(t.type, ''),
                   p.value,
                   p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id
        """

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY p._id DESC"

        rows = self.get_rows(query, params)
        return [(row[0], row[1], float(row[2]), row[3]) for row in rows]

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

    def get_kcal_today(self) -> float:
        """Get the total calories burned today.

        Returns:

        - `float`: Total calories burned today, or 0.0 if no records found.

        """
        today = datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime(
            "%Y-%m-%d"
        )
        query = """
            SELECT SUM(p.value * e.calories_per_unit * COALESCE(t.calories_modifier, 1.0)) as total_calories
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            WHERE p.date = :today
            AND p.date IS NOT NULL
            AND e.calories_per_unit > 0
        """
        rows = self.get_rows(query, {"today": today})
        if rows and rows[0][0] is not None:
            try:
                return float(rows[0][0])
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    def get_last_executed_exercise(self) -> str | None:
        """Get the name of the last executed exercise from the process table.

        Returns:

        - `str | None`: Name of the last executed exercise or None if no records found.

        """
        query = """
            SELECT e.name
            FROM process p
            LEFT JOIN exercises e ON p._id_exercises = e._id
            ORDER BY p.date DESC, p._id DESC
            LIMIT 1
        """

        rows = self.get_rows(query)
        return rows[0][0] if rows else None

    def get_last_exercise_date(self, exercise_id: int) -> str | None:
        """Get the date of the last recorded exercise (regardless of type).

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `str | None`: Date string in YYYY-MM-DD format or None if not found.

        """
        query = """
            SELECT date
            FROM process
            WHERE _id_exercises = :ex_id
            ORDER BY _id DESC
            LIMIT 1
        """
        rows = self.get_rows(query, {"ex_id": exercise_id})
        if rows and rows[0][0]:
            return rows[0][0]
        return None

    def get_last_exercise_dates(self) -> list[tuple[str, str]]:
        """Get the last execution date for each exercise (ignoring exercise types).

        Returns:

        - `list[tuple[str, str]]`: List of (exercise_name, last_date) tuples sorted by exercise name.

        """
        query = """
            SELECT e.name, MAX(p.date) as last_date
            FROM exercises e
            LEFT JOIN process p ON e._id = p._id_exercises
            WHERE p.date IS NOT NULL
            GROUP BY e._id, e.name
            HAVING last_date IS NOT NULL
            ORDER BY e.name ASC
        """

        rows = self.get_rows(query)
        return [(row[0], row[1]) for row in rows]

    def get_last_exercise_record(self, exercise_id: int) -> tuple[str, str] | None:
        """Get the last recorded type and value for a specific exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `tuple[str, str] | None`: Tuple of (type_name, value) or None if not found.

        """
        query = """
            SELECT t.type, p.value
            FROM process p
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = p._id_exercises
            WHERE p._id_exercises = :ex_id
            ORDER BY p._id DESC
            LIMIT 1
        """
        rows = self.get_rows(query, {"ex_id": exercise_id})
        if rows:
            return (rows[0][0] or "", rows[0][1] or "")
        return None

    def get_last_weight(self) -> float | None:
        """Get the last recorded weight value.

        Returns:

        - `float | None`: The most recent weight value or None if no records found.

        """
        rows = self.get_rows("SELECT value FROM weight ORDER BY date DESC, _id DESC LIMIT 1")
        if rows and rows[0][0] is not None:
            try:
                return float(rows[0][0])
            except (ValueError, TypeError):
                return None
        return None

    def get_limited_process_records(self, limit: int = 5000) -> list[list[Any]]:
        """Get limited number of process records with exercise and type names.

        Args:

        - `limit` (`int`): Maximum number of records to return. Defaults to 5000.

        Returns:

        - `list[list[Any]]`: List of process records [_id, exercise_name, type_name, value, unit, date].

        """
        return self.get_rows(
            """
            SELECT p._id,
                e.name,
                IFNULL(t.type, ''),
                p.value,
                e.unit,
                p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t
                ON p._id_types = t._id
                AND t._id_exercises = e._id
            ORDER BY p.date DESC, p._id DESC
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

    def get_sets_chart_data(self, date_from: str, date_to: str) -> list[tuple[str, int]]:
        """Get sets (workout count) data for charting.

        Args:

        - `date_from` (`str`): From date (YYYY-MM-DD).
        - `date_to` (`str`): To date (YYYY-MM-DD).

        Returns:

        - `list[tuple[str, int]]`: List of (date, count) tuples.

        """
        query = """
            SELECT date, COUNT(*) as set_count
            FROM process
            WHERE date BETWEEN :date_from AND :date_to
            AND date IS NOT NULL
            GROUP BY date
            ORDER BY date ASC
        """
        rows = self.get_rows(query, {"date_from": date_from, "date_to": date_to})
        return [(row[0], row[1]) for row in rows]

    def get_sets_count_today(self) -> int:
        """Get the count of sets (process records) for today.

        Returns:

        - `int`: Number of process records for today's date.

        """
        today = datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime(
            "%Y-%m-%d"
        )
        rows = self.get_rows("SELECT COUNT(*) FROM process WHERE date = :today", {"today": today})
        return rows[0][0] if rows else 0

    def get_statistics_data(self) -> list[tuple[str, str, float, str]]:
        """Get data for statistics display.

        Returns:

        - `list[tuple[str, str, float, str]]`: List of (exercise_name, type_name, value, date) tuples.

        """
        rows = self.get_rows("""
            SELECT e.name,
                   IFNULL(t.type, ''),
                   p.value,
                   p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id
            ORDER BY p._id DESC
        """)
        return [(row[0], row[1], float(row[2]), row[3]) for row in rows]

    def get_weight_chart_data(self, date_from: str, date_to: str) -> list[tuple[float, str]]:
        """Get weight data for charting.

        Args:

        - `date_from` (`str`): From date (YYYY-MM-DD).
        - `date_to` (`str`): To date (YYYY-MM-DD).

        Returns:

        - `list[tuple[float, str]]`: List of (weight_value, date) tuples.

        """
        query = """
            SELECT value, date
            FROM weight
            WHERE date BETWEEN :date_from AND :date_to
            AND date IS NOT NULL
            ORDER BY date ASC
        """
        rows = self.get_rows(query, {"date_from": date_from, "date_to": date_to})
        return [(float(row[0]), row[1]) for row in rows]

    def is_database_open(self) -> bool:
        """Check if the database connection is open.

        Returns:

        - `bool`: True if database is open, False otherwise.

        """
        return hasattr(self, "db") and self.db is not None and self.db.isValid() and self.db.isOpen()

    def is_exercise_type_required(self, exercise_id: int) -> bool:
        """Check if exercise type is required for a given exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `bool`: True if type is required, False otherwise.

        """
        rows = self.get_rows("SELECT is_type_required FROM exercises WHERE _id = :ex_id", {"ex_id": exercise_id})
        return bool(rows and rows[0][0] == 1)

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

    def update_exercise(
        self, exercise_id: int, name: str, unit: str, *, is_type_required: bool, calories_per_unit: float = 0.0
    ) -> bool:
        """Update an existing exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `name` (`str`): Exercise name.
        - `unit` (`str`): Unit of measurement.
        - `is_type_required` (`bool`): Whether exercise type is required.
        - `calories_per_unit` (`float`): Calories burned per unit. Defaults to `0.0`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = (
            "UPDATE exercises SET name = :n, unit = :u, "
            "is_type_required = :itr, calories_per_unit = :cpu "
            "WHERE _id = :id"
        )
        params = {
            "n": name,
            "u": unit,
            "itr": 1 if is_type_required else 0,
            "cpu": calories_per_unit,
            "id": exercise_id,
        }
        return self.execute_simple_query(query, params)

    def update_exercise_type(
        self, type_id: int, exercise_id: int, type_name: str, calories_modifier: float = 1.0
    ) -> bool:
        """Update an existing exercise type.

        Args:

        - `type_id` (`int`): Type ID.
        - `exercise_id` (`int`): Exercise ID.
        - `type_name` (`str`): Type name.
        - `calories_modifier` (`float`): Calories modifier for this type. Defaults to `1.0`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "UPDATE types SET _id_exercises = :ex, type = :tp, calories_modifier = :cm WHERE _id = :id"
        params = {"ex": exercise_id, "tp": type_name, "cm": calories_modifier, "id": type_id}
        return self.execute_simple_query(query, params)

    def update_process_record(self, record_id: int, exercise_id: int, type_id: int, value: str, date: str) -> bool:
        """Update an existing process record.

        Args:

        - `record_id` (`int`): Record ID.
        - `exercise_id` (`int`): Exercise ID.
        - `type_id` (`int`): Type ID (-1 for no type).
        - `value` (`str`): Exercise value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """
            UPDATE process
            SET _id_exercises = :ex,
                _id_types = :tp,
                date = :dt,
                value = :val
            WHERE _id = :id
        """
        params = {
            "ex": exercise_id,
            "tp": type_id,
            "dt": date,
            "val": value,
            "id": record_id,
        }
        return self.execute_simple_query(query, params)

    def update_weight_record(self, record_id: int, value: float, date: str) -> bool:
        """Update an existing weight record.

        Args:

        - `record_id` (`int`): Record ID.
        - `value` (`float`): Weight value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = "UPDATE weight SET value = :v, date = :d WHERE _id = :id"
        params = {"v": value, "d": date, "id": record_id}
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
        self.connection_name = f"fitness_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(self._db_filename)

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown error"
            error_msg = f"❌ Failed to reconnect to database: {error_msg}"
            raise ConnectionError(error_msg)
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
        self.connection_name = f"fitness_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(db_filename)

        # Store the database filename for potential reconnection
        self._db_filename = db_filename

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown database error"
            msg = f"❌ Failed to open the database: {error_msg}"
            raise ConnectionError(msg)
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

### ⚙️ Method `add_exercise`

```python
def add_exercise(self, name: str, unit: str) -> bool
```

Add a new exercise to the database.

Args:

- `name` (`str`): Exercise name.
- `unit` (`str`): Unit of measurement.
- `is_type_required` (`bool`): Whether exercise type is required.
- `calories_per_unit` (`float`): Calories burned per unit. Defaults to `0.0`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_exercise(self, name: str, unit: str, *, is_type_required: bool, calories_per_unit: float = 0.0) -> bool:
        query = (
            "INSERT INTO exercises (name, unit, is_type_required, calories_per_unit) "
            "VALUES (:name, :unit, :is_type_required, :calories_per_unit)"
        )
        params = {
            "name": name,
            "unit": unit,
            "is_type_required": 1 if is_type_required else 0,
            "calories_per_unit": calories_per_unit,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `add_exercise_type`

```python
def add_exercise_type(self, exercise_id: int, type_name: str, calories_modifier: float = 1.0) -> bool
```

Add a new exercise type.

Args:

- `exercise_id` (`int`): Exercise ID.
- `type_name` (`str`): Type name.
- `calories_modifier` (`float`): Calories modifier for this type. Defaults to `1.0`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_exercise_type(self, exercise_id: int, type_name: str, calories_modifier: float = 1.0) -> bool:
        query = "INSERT INTO types (_id_exercises, type, calories_modifier) VALUES (:ex, :tp, :calories_modifier)"
        return self.execute_simple_query(
            query, {"ex": exercise_id, "tp": type_name, "calories_modifier": calories_modifier}
        )
```

</details>

### ⚙️ Method `add_process_record`

```python
def add_process_record(self, exercise_id: int, type_id: int, value: str, date: str) -> bool
```

Add a new process record.

Args:

- `exercise_id` (`int`): Exercise ID.
- `type_id` (`int`): Type ID (-1 for no type).
- `value` (`str`): Exercise value.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_process_record(self, exercise_id: int, type_id: int, value: str, date: str) -> bool:
        query = (
            "INSERT INTO process (_id_exercises, _id_types, value, date) VALUES (:exercise_id, :type_id, :value, :date)"
        )
        params = {
            "exercise_id": exercise_id,
            "type_id": type_id,
            "value": value,
            "date": date,
        }

        result = self.execute_simple_query(query, params)
        if not result:
            print(
                f"Failed to add process record: exercise_id={exercise_id}, "
                f"type_id={type_id}, value={value}, date={date}"
            )
        return result
```

</details>

### ⚙️ Method `add_weight_record`

```python
def add_weight_record(self, value: float, date: str) -> bool
```

Add a new weight record.

Args:

- `value` (`float`): Weight value.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_weight_record(self, value: float, date: str) -> bool:
        query = "INSERT INTO weight (value, date) VALUES (:val, :dt)"
        return self.execute_simple_query(query, {"val": value, "dt": date})
```

</details>

### ⚙️ Method `check_exercise_exists`

```python
def check_exercise_exists(self, exercise_id: int) -> bool
```

Check if exercise exists by ID.

Args:

- `exercise_id` (`int`): Exercise ID to check.

Returns:

- `bool`: True if exercise exists, False otherwise.

<details>
<summary>Code:</summary>

```python
def check_exercise_exists(self, exercise_id: int) -> bool:
        rows = self.get_rows("SELECT 1 FROM exercises WHERE _id = :id LIMIT 1", {"id": exercise_id})
        return len(rows) > 0
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

### ⚙️ Method `delete_exercise`

```python
def delete_exercise(self, exercise_id: int) -> bool
```

Delete an exercise from the database.

Args:

- `exercise_id` (`int`): Exercise ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_exercise(self, exercise_id: int) -> bool:
        query = "DELETE FROM exercises WHERE _id = :id"
        return self.execute_simple_query(query, {"id": exercise_id})
```

</details>

### ⚙️ Method `delete_exercise_type`

```python
def delete_exercise_type(self, type_id: int) -> bool
```

Delete an exercise type.

Args:

- `type_id` (`int`): Type ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_exercise_type(self, type_id: int) -> bool:
        query = "DELETE FROM types WHERE _id = :id"
        return self.execute_simple_query(query, {"id": type_id})
```

</details>

### ⚙️ Method `delete_process_record`

```python
def delete_process_record(self, record_id: int) -> bool
```

Delete a process record.

Args:

- `record_id` (`int`): Record ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_process_record(self, record_id: int) -> bool:
        query = "DELETE FROM process WHERE _id = :id"
        return self.execute_simple_query(query, {"id": record_id})
```

</details>

### ⚙️ Method `delete_weight_record`

```python
def delete_weight_record(self, record_id: int) -> bool
```

Delete a weight record.

Args:

- `record_id` (`int`): Record ID to delete.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def delete_weight_record(self, record_id: int) -> bool:
        query = "DELETE FROM weight WHERE _id = :id"
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

### ⚙️ Method `get_all_exercise_types`

```python
def get_all_exercise_types(self) -> list[list[Any]]
```

Get all exercise types with exercise names.

Returns:

- `list[list[Any]]`: List of type records [_id, exercise_name, type_name, calories_modifier].

<details>
<summary>Code:</summary>

```python
def get_all_exercise_types(self) -> list[list[Any]]:
        return self.get_rows("""
            SELECT t._id, e.name, t.type, t.calories_modifier
            FROM types t
            JOIN exercises e ON t._id_exercises = e._id
        """)
```

</details>

### ⚙️ Method `get_all_exercises`

```python
def get_all_exercises(self) -> list[list[Any]]
```

Get all exercises with their properties.

Returns:

- `list[list[Any]]`: List of exercise records [_id, name, unit, is_type_required, calories_per_unit].

<details>
<summary>Code:</summary>

```python
def get_all_exercises(self) -> list[list[Any]]:
        return self.get_rows("SELECT _id, name, unit, is_type_required, calories_per_unit FROM exercises")
```

</details>

### ⚙️ Method `get_all_process_records`

```python
def get_all_process_records(self) -> list[list[Any]]
```

Get all process records with exercise and type names.

Returns:

- `list[list[Any]]`: List of process records [_id, exercise_name, type_name, value, unit, date].

<details>
<summary>Code:</summary>

```python
def get_all_process_records(self) -> list[list[Any]]:
        return self.get_rows("""
            SELECT p._id,
                e.name,
                IFNULL(t.type, ''),
                p.value,
                e.unit,
                p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t
                ON p._id_types = t._id
                AND t._id_exercises = e._id
            ORDER BY p.date DESC, p._id DESC
        """)
```

</details>

### ⚙️ Method `get_all_weight_records`

```python
def get_all_weight_records(self) -> list[list[Any]]
```

Get all weight records.

Returns:

- `list[list[Any]]`: List of weight records [_id, value, date].

<details>
<summary>Code:</summary>

```python
def get_all_weight_records(self) -> list[list[Any]]:
        return self.get_rows("SELECT _id, value, date FROM weight ORDER BY date DESC")
```

</details>

### ⚙️ Method `get_earliest_exercise_date`

```python
def get_earliest_exercise_date(self, exercise_name: str, exercise_type: str | None = None) -> str | None
```

Get the earliest date for a specific exercise.

Args:

- `exercise_name` (`str`): Exercise name.
- `exercise_type` (`str | None`): Exercise type. Defaults to `None` for all types.

Returns:

- `str | None`: Earliest date in YYYY-MM-DD format or None if no data.

<details>
<summary>Code:</summary>

```python
def get_earliest_exercise_date(self, exercise_name: str, exercise_type: str | None = None) -> str | None:
        conditions = ["e.name = :exercise"]
        params = {"exercise": exercise_name}

        if exercise_type and exercise_type != "All types":
            conditions.append("t.type = :type")
            params["type"] = exercise_type

        query = f"""
            SELECT MIN(p.date)
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            WHERE {" AND ".join(conditions)}
            AND p.date IS NOT NULL"""

        rows = self.get_rows(query, params)
        return rows[0][0] if rows and rows[0][0] else None
```

</details>

### ⚙️ Method `get_earliest_process_date`

```python
def get_earliest_process_date(self) -> str | None
```

Get the earliest date from process records.

Returns:

- `str | None`: Earliest date in YYYY-MM-DD format or None if no data.

<details>
<summary>Code:</summary>

```python
def get_earliest_process_date(self) -> str | None:
        rows = self.get_rows("SELECT MIN(date) FROM process WHERE date IS NOT NULL")
        return rows[0][0] if rows and rows[0][0] else None
```

</details>

### ⚙️ Method `get_earliest_weight_date`

```python
def get_earliest_weight_date(self) -> str | None
```

Get the earliest date from weight records.

Returns:

- `str | None`: Earliest date in YYYY-MM-DD format or None if no data.

<details>
<summary>Code:</summary>

```python
def get_earliest_weight_date(self) -> str | None:
        rows = self.get_rows("SELECT MIN(date) FROM weight WHERE date IS NOT NULL")
        return rows[0][0] if rows and rows[0][0] else None
```

</details>

### ⚙️ Method `get_exercise_calories_info`

```python
def get_exercise_calories_info(self, exercise_id: int) -> tuple[float, list[tuple[str, float]]]
```

Get calories information for an exercise.

Args:

- `exercise_id` (`int`): Exercise ID.

Returns:

- `tuple[float, list[tuple[str, float]]]`: Tuple of (calories_per_unit, [(type_name, calories_modifier), ...]).

<details>
<summary>Code:</summary>

```python
def get_exercise_calories_info(self, exercise_id: int) -> tuple[float, list[tuple[str, float]]]:
        # Get exercise calories_per_unit
        exercise_rows = self.get_rows("SELECT calories_per_unit FROM exercises WHERE _id = :id", {"id": exercise_id})
        calories_per_unit = exercise_rows[0][0] if exercise_rows else 0.0

        # Get types with their calories modifiers
        type_rows = self.get_rows(
            "SELECT type, calories_modifier FROM types WHERE _id_exercises = :id", {"id": exercise_id}
        )
        type_modifiers = [(row[0], row[1]) for row in type_rows]

        return calories_per_unit, type_modifiers
```

</details>

### ⚙️ Method `get_exercise_chart_data`

```python
def get_exercise_chart_data(self, exercise_name: str, exercise_type: str | None = None, date_from: str | None = None, date_to: str | None = None) -> list[tuple[str, str]]
```

Get exercise data for charting.

Args:

- `exercise_name` (`str`): Exercise name.
- `exercise_type` (`str | None`): Exercise type. Defaults to `None` for all types.
- `date_from` (`str | None`): From date (YYYY-MM-DD). Defaults to `None`.
- `date_to` (`str | None`): To date (YYYY-MM-DD). Defaults to `None`.

Returns:

- `list[tuple[str, str]]`: List of (date, value) tuples.

<details>
<summary>Code:</summary>

```python
def get_exercise_chart_data(
        self,
        exercise_name: str,
        exercise_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[tuple[str, str]]:
        conditions = ["e.name = :exercise"]
        params = {"exercise": exercise_name}

        if date_from and date_to:
            conditions.append("p.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        if exercise_type and exercise_type != "All types":
            conditions.append("t.type = :type")
            params["type"] = exercise_type

        query = f"""
            SELECT p.date, p.value
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            WHERE {" AND ".join(conditions)}
            ORDER BY p.date ASC"""

        rows = self.get_rows(query, params)
        return [(row[0], row[1]) for row in rows]
```

</details>

### ⚙️ Method `get_exercise_max_values`

```python
def get_exercise_max_values(self, exercise_id: int, type_id: int, date_from: str | None = None) -> tuple[float, float]
```

Get all-time and yearly max values for an exercise.

Args:

- `exercise_id` (`int`): Exercise ID.
- `type_id` (`int`): Type ID (-1 for no type).
- `date_from` (`str | None`): Start date for yearly calculation (YYYY-MM-DD). Defaults to `None`.

Returns:

- `tuple[float, float]`: Tuple of (all_time_max, yearly_max).

<details>
<summary>Code:</summary>

```python
def get_exercise_max_values(
        self, exercise_id: int, type_id: int, date_from: str | None = None
    ) -> tuple[float, float]:
        conditions = ["p._id_exercises = :ex_id"]
        params: dict[str, Any] = {"ex_id": exercise_id}

        if type_id != -1:
            conditions.append("p._id_types = :type_id")
            params["type_id"] = type_id
        else:
            conditions.append("p._id_types = -1")

        # Get all-time max
        all_time_query = f"""
            SELECT MAX(CAST(p.value AS REAL)) as max_value
            FROM process p
            WHERE {" AND ".join(conditions)}"""

        all_time_rows = self.get_rows(all_time_query, params)
        all_time_max = 0.0
        if all_time_rows and all_time_rows[0][0] is not None and all_time_rows[0][0] != "":
            try:
                all_time_max = float(all_time_rows[0][0])
            except (ValueError, TypeError):
                all_time_max = 0.0

        # Get yearly max if date_from provided
        yearly_max = 0.0
        if date_from:
            yearly_conditions = [*conditions, "p.date >= :year_ago"]
            yearly_params = params.copy()
            yearly_params["year_ago"] = date_from

            yearly_query = f"""
                SELECT MAX(CAST(p.value AS REAL)) as max_value
                FROM process p
                WHERE {" AND ".join(yearly_conditions)}"""

            yearly_rows = self.get_rows(yearly_query, yearly_params)
            if yearly_rows and yearly_rows[0][0] is not None and yearly_rows[0][0] != "":
                try:
                    yearly_max = float(yearly_rows[0][0])
                except (ValueError, TypeError):
                    yearly_max = 0.0

        return all_time_max, yearly_max
```

</details>

### ⚙️ Method `get_exercise_name_by_id`

```python
def get_exercise_name_by_id(self, exercise_id: int) -> str | None
```

Get exercise name by ID.

Args:

- `exercise_id` (`int`): Exercise ID.

Returns:

- `str | None`: Exercise name or None if not found.

<details>
<summary>Code:</summary>

```python
def get_exercise_name_by_id(self, exercise_id: int) -> str | None:
        rows = self.get_rows("SELECT name FROM exercises WHERE _id = :id", {"id": exercise_id})
        return rows[0][0] if rows else None
```

</details>

### ⚙️ Method `get_exercise_steps_records`

```python
def get_exercise_steps_records(self, exercise_id: int) -> list[tuple[str, int, str]]
```

Get steps records grouped by date.

Args:

- `exercise_id` (`int`): Exercise ID for steps.

Returns:

- `list[tuple[str, int, str]]`: List of (date, record_count, values) tuples.

<details>
<summary>Code:</summary>

```python
def get_exercise_steps_records(self, exercise_id: int) -> list[tuple[str, int, str]]:
        rows = self.get_rows(
            """
            SELECT date, COUNT(*) as record_count, GROUP_CONCAT(value, ', ') as step_values
            FROM process
            WHERE _id_exercises = :id
            AND date IS NOT NULL
            GROUP BY date
            ORDER BY date ASC""",
            {"id": exercise_id},
        )

        # Convert to proper tuple format
        return [(row[0], int(row[1]), row[2]) for row in rows]
```

</details>

### ⚙️ Method `get_exercise_total_today`

```python
def get_exercise_total_today(self, exercise_id: int) -> float
```

Get the total value for a specific exercise today.

Args:

- `exercise_id` (`int`): Exercise ID.

Returns:

- `float`: Total value for the exercise today, or 0.0 if no records found.

<details>
<summary>Code:</summary>

```python
def get_exercise_total_today(self, exercise_id: int) -> float:
        today = datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime(
            "%Y-%m-%d"
        )
        rows = self.get_rows(
            "SELECT SUM(CAST(value AS REAL)) FROM process WHERE _id_exercises = :ex_id AND date = :today",
            {"ex_id": exercise_id, "today": today},
        )
        if rows and rows[0][0] is not None:
            try:
                return float(rows[0][0])
            except (ValueError, TypeError):
                return 0.0
        return 0.0
```

</details>

### ⚙️ Method `get_exercise_types`

```python
def get_exercise_types(self, exercise_id: int) -> list[str]
```

Get all types for a specific exercise.

Args:

- `exercise_id` (`int`): Exercise ID.

Returns:

- `list[str]`: List of type names.

<details>
<summary>Code:</summary>

```python
def get_exercise_types(self, exercise_id: int) -> list[str]:
        return self.get_items("types", "type", condition=f"_id_exercises = {exercise_id}")
```

</details>

### ⚙️ Method `get_exercise_unit`

```python
def get_exercise_unit(self, exercise_name: str) -> str
```

Get the unit of measurement for a given exercise.

Args:

- `exercise_name` (`str`): Name of the exercise.

Returns:

- `str`: Unit of measurement, or "times" as default.

<details>
<summary>Code:</summary>

```python
def get_exercise_unit(self, exercise_name: str) -> str:
        rows = self.get_rows("SELECT unit FROM exercises WHERE name = :name", {"name": exercise_name})
        if rows and rows[0][0]:
            return rows[0][0]
        return "times"
```

</details>

### ⚙️ Method `get_exercises_by_frequency`

```python
def get_exercises_by_frequency(self, limit: int = 500) -> list[str]
```

Return exercise names ordered by frequency in recent `limit` rows.

Args:

- `limit` (`int`): Number of most recent rows from the `process` table to analyse. Defaults to `500`.

Returns:

- `list[str]`: Exercise names sorted by how often they appear; exercises
  not encountered in the inspected slice are appended afterwards.

<details>
<summary>Code:</summary>

```python
def get_exercises_by_frequency(self, limit: int = 500) -> list[str]:
        if limit <= 0:
            return []

        # Full list of exercises `{id: name}`.
        all_exercises = {row[0]: row[1] for row in self.get_rows("SELECT _id, name FROM exercises")}

        # Recent usage statistics.
        recent_records = self.get_rows(
            "SELECT _id_exercises FROM process ORDER BY _id DESC LIMIT :limit",
            {"limit": limit},
        )
        exercise_counts = Counter(row[0] for row in recent_records)

        # Most common first.
        sorted_exercises = [
            all_exercises[ex_id] for ex_id, _ in exercise_counts.most_common() if ex_id in all_exercises
        ]

        # Preserve exercises not present in sorted_exercises.
        remainder = [name for name in all_exercises.values() if name not in sorted_exercises]
        return sorted_exercises + remainder
```

</details>

### ⚙️ Method `get_exercises_by_last_execution`

```python
def get_exercises_by_last_execution(self) -> list[str]
```

Return exercise names ordered by last execution date (most recent first).

Returns:

- `list[str]`: Exercise names sorted by last execution date.
  Exercises never executed are appended at the end.

<details>
<summary>Code:</summary>

```python
def get_exercises_by_last_execution(self) -> list[str]:
        # Full list of exercises `{id: name}`.
        all_exercises = {row[0]: row[1] for row in self.get_rows("SELECT _id, name FROM exercises")}

        # Get exercises with their last execution date.
        last_execution = self.get_rows(
            """
            SELECT e._id, e.name, MAX(p.date) as last_date
            FROM exercises e
            LEFT JOIN process p ON e._id = p._id_exercises
            GROUP BY e._id, e.name
            ORDER BY last_date DESC NULLS LAST, e.name ASC
            """
        )

        return [row[1] for row in last_execution]
```

</details>

### ⚙️ Method `get_filtered_process_records`

```python
def get_filtered_process_records(self, exercise_name: str | None = None, exercise_type: str | None = None, date_from: str | None = None, date_to: str | None = None) -> list[list[Any]]
```

Get filtered process records.

Args:

- `exercise_name` (`str | None`): Filter by exercise name. Defaults to `None`.
- `exercise_type` (`str | None`): Filter by exercise type. Defaults to `None`.
- `date_from` (`str | None`): Filter from date (YYYY-MM-DD). Defaults to `None`.
- `date_to` (`str | None`): Filter to date (YYYY-MM-DD). Defaults to `None`.

Returns:

- `list[list[Any]]`: List of filtered process records.

<details>
<summary>Code:</summary>

```python
def get_filtered_process_records(
        self,
        exercise_name: str | None = None,
        exercise_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[list[Any]]:
        conditions: list[str] = []
        params: dict[str, str] = {}

        if exercise_name:
            conditions.append("e.name = :exercise")
            params["exercise"] = exercise_name

        if exercise_type:
            conditions.append("t.type = :type")
            params["type"] = exercise_type

        if date_from and date_to:
            conditions.append("p.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        query_text = """
            SELECT p._id,
                e.name,
                IFNULL(t.type, ''),
                p.value,
                e.unit,
                p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t
                ON p._id_types = t._id
                AND t._id_exercises = e._id
        """

        if conditions:
            query_text += " WHERE " + " AND ".join(conditions)

        query_text += " ORDER BY p.date DESC, p._id DESC"

        return self.get_rows(query_text, params)
```

</details>

### ⚙️ Method `get_filtered_statistics_data`

```python
def get_filtered_statistics_data(self, exercise_name: str | None = None) -> list[tuple[str, str, float, str]]
```

Get filtered data for statistics display.

Args:

- `exercise_name` (`str | None`): Exercise name to filter by. Defaults to `None` for all exercises.

Returns:

- `list[tuple[str, str, float, str]]`: List of (exercise_name, type_name, value, date) tuples.

<details>
<summary>Code:</summary>

```python
def get_filtered_statistics_data(self, exercise_name: str | None = None) -> list[tuple[str, str, float, str]]:
        conditions = []
        params = {}

        if exercise_name:
            conditions.append("e.name = :exercise")
            params["exercise"] = exercise_name

        query = """
            SELECT e.name,
                   IFNULL(t.type, ''),
                   p.value,
                   p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id
        """

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY p._id DESC"

        rows = self.get_rows(query, params)
        return [(row[0], row[1], float(row[2]), row[3]) for row in rows]
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

### ⚙️ Method `get_kcal_chart_data`

```python
def get_kcal_chart_data(self, date_from: str, date_to: str) -> list[tuple[str, float]]
```

Get calories data for charting.

Args:

- `date_from` (`str`): From date (YYYY-MM-DD).
- `date_to` (`str`): To date (YYYY-MM-DD).

Returns:

- `list[tuple[str, float]]`: List of (date, calories) tuples.

<details>
<summary>Code:</summary>

```python
def get_kcal_chart_data(self, date_from: str, date_to: str) -> list[tuple[str, float]]:
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
```

</details>

### ⚙️ Method `get_kcal_today`

```python
def get_kcal_today(self) -> float
```

Get the total calories burned today.

Returns:

- `float`: Total calories burned today, or 0.0 if no records found.

<details>
<summary>Code:</summary>

```python
def get_kcal_today(self) -> float:
        today = datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime(
            "%Y-%m-%d"
        )
        query = """
            SELECT SUM(p.value * e.calories_per_unit * COALESCE(t.calories_modifier, 1.0)) as total_calories
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            WHERE p.date = :today
            AND p.date IS NOT NULL
            AND e.calories_per_unit > 0
        """
        rows = self.get_rows(query, {"today": today})
        if rows and rows[0][0] is not None:
            try:
                return float(rows[0][0])
            except (ValueError, TypeError):
                return 0.0
        return 0.0
```

</details>

### ⚙️ Method `get_last_executed_exercise`

```python
def get_last_executed_exercise(self) -> str | None
```

Get the name of the last executed exercise from the process table.

Returns:

- `str | None`: Name of the last executed exercise or None if no records found.

<details>
<summary>Code:</summary>

```python
def get_last_executed_exercise(self) -> str | None:
        query = """
            SELECT e.name
            FROM process p
            LEFT JOIN exercises e ON p._id_exercises = e._id
            ORDER BY p.date DESC, p._id DESC
            LIMIT 1
        """

        rows = self.get_rows(query)
        return rows[0][0] if rows else None
```

</details>

### ⚙️ Method `get_last_exercise_date`

```python
def get_last_exercise_date(self, exercise_id: int) -> str | None
```

Get the date of the last recorded exercise (regardless of type).

Args:

- `exercise_id` (`int`): Exercise ID.

Returns:

- `str | None`: Date string in YYYY-MM-DD format or None if not found.

<details>
<summary>Code:</summary>

```python
def get_last_exercise_date(self, exercise_id: int) -> str | None:
        query = """
            SELECT date
            FROM process
            WHERE _id_exercises = :ex_id
            ORDER BY _id DESC
            LIMIT 1
        """
        rows = self.get_rows(query, {"ex_id": exercise_id})
        if rows and rows[0][0]:
            return rows[0][0]
        return None
```

</details>

### ⚙️ Method `get_last_exercise_dates`

```python
def get_last_exercise_dates(self) -> list[tuple[str, str]]
```

Get the last execution date for each exercise (ignoring exercise types).

Returns:

- `list[tuple[str, str]]`: List of (exercise_name, last_date) tuples sorted by exercise name.

<details>
<summary>Code:</summary>

```python
def get_last_exercise_dates(self) -> list[tuple[str, str]]:
        query = """
            SELECT e.name, MAX(p.date) as last_date
            FROM exercises e
            LEFT JOIN process p ON e._id = p._id_exercises
            WHERE p.date IS NOT NULL
            GROUP BY e._id, e.name
            HAVING last_date IS NOT NULL
            ORDER BY e.name ASC
        """

        rows = self.get_rows(query)
        return [(row[0], row[1]) for row in rows]
```

</details>

### ⚙️ Method `get_last_exercise_record`

```python
def get_last_exercise_record(self, exercise_id: int) -> tuple[str, str] | None
```

Get the last recorded type and value for a specific exercise.

Args:

- `exercise_id` (`int`): Exercise ID.

Returns:

- `tuple[str, str] | None`: Tuple of (type_name, value) or None if not found.

<details>
<summary>Code:</summary>

```python
def get_last_exercise_record(self, exercise_id: int) -> tuple[str, str] | None:
        query = """
            SELECT t.type, p.value
            FROM process p
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = p._id_exercises
            WHERE p._id_exercises = :ex_id
            ORDER BY p._id DESC
            LIMIT 1
        """
        rows = self.get_rows(query, {"ex_id": exercise_id})
        if rows:
            return (rows[0][0] or "", rows[0][1] or "")
        return None
```

</details>

### ⚙️ Method `get_last_weight`

```python
def get_last_weight(self) -> float | None
```

Get the last recorded weight value.

Returns:

- `float | None`: The most recent weight value or None if no records found.

<details>
<summary>Code:</summary>

```python
def get_last_weight(self) -> float | None:
        rows = self.get_rows("SELECT value FROM weight ORDER BY date DESC, _id DESC LIMIT 1")
        if rows and rows[0][0] is not None:
            try:
                return float(rows[0][0])
            except (ValueError, TypeError):
                return None
        return None
```

</details>

### ⚙️ Method `get_limited_process_records`

```python
def get_limited_process_records(self, limit: int = 5000) -> list[list[Any]]
```

Get limited number of process records with exercise and type names.

Args:

- `limit` (`int`): Maximum number of records to return. Defaults to 5000.

Returns:

- `list[list[Any]]`: List of process records [_id, exercise_name, type_name, value, unit, date].

<details>
<summary>Code:</summary>

```python
def get_limited_process_records(self, limit: int = 5000) -> list[list[Any]]:
        return self.get_rows(
            """
            SELECT p._id,
                e.name,
                IFNULL(t.type, ''),
                p.value,
                e.unit,
                p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t
                ON p._id_types = t._id
                AND t._id_exercises = e._id
            ORDER BY p.date DESC, p._id DESC
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

### ⚙️ Method `get_sets_chart_data`

```python
def get_sets_chart_data(self, date_from: str, date_to: str) -> list[tuple[str, int]]
```

Get sets (workout count) data for charting.

Args:

- `date_from` (`str`): From date (YYYY-MM-DD).
- `date_to` (`str`): To date (YYYY-MM-DD).

Returns:

- `list[tuple[str, int]]`: List of (date, count) tuples.

<details>
<summary>Code:</summary>

```python
def get_sets_chart_data(self, date_from: str, date_to: str) -> list[tuple[str, int]]:
        query = """
            SELECT date, COUNT(*) as set_count
            FROM process
            WHERE date BETWEEN :date_from AND :date_to
            AND date IS NOT NULL
            GROUP BY date
            ORDER BY date ASC
        """
        rows = self.get_rows(query, {"date_from": date_from, "date_to": date_to})
        return [(row[0], row[1]) for row in rows]
```

</details>

### ⚙️ Method `get_sets_count_today`

```python
def get_sets_count_today(self) -> int
```

Get the count of sets (process records) for today.

Returns:

- `int`: Number of process records for today's date.

<details>
<summary>Code:</summary>

```python
def get_sets_count_today(self) -> int:
        today = datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime(
            "%Y-%m-%d"
        )
        rows = self.get_rows("SELECT COUNT(*) FROM process WHERE date = :today", {"today": today})
        return rows[0][0] if rows else 0
```

</details>

### ⚙️ Method `get_statistics_data`

```python
def get_statistics_data(self) -> list[tuple[str, str, float, str]]
```

Get data for statistics display.

Returns:

- `list[tuple[str, str, float, str]]`: List of (exercise_name, type_name, value, date) tuples.

<details>
<summary>Code:</summary>

```python
def get_statistics_data(self) -> list[tuple[str, str, float, str]]:
        rows = self.get_rows("""
            SELECT e.name,
                   IFNULL(t.type, ''),
                   p.value,
                   p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id
            ORDER BY p._id DESC
        """)
        return [(row[0], row[1], float(row[2]), row[3]) for row in rows]
```

</details>

### ⚙️ Method `get_weight_chart_data`

```python
def get_weight_chart_data(self, date_from: str, date_to: str) -> list[tuple[float, str]]
```

Get weight data for charting.

Args:

- `date_from` (`str`): From date (YYYY-MM-DD).
- `date_to` (`str`): To date (YYYY-MM-DD).

Returns:

- `list[tuple[float, str]]`: List of (weight_value, date) tuples.

<details>
<summary>Code:</summary>

```python
def get_weight_chart_data(self, date_from: str, date_to: str) -> list[tuple[float, str]]:
        query = """
            SELECT value, date
            FROM weight
            WHERE date BETWEEN :date_from AND :date_to
            AND date IS NOT NULL
            ORDER BY date ASC
        """
        rows = self.get_rows(query, {"date_from": date_from, "date_to": date_to})
        return [(float(row[0]), row[1]) for row in rows]
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

### ⚙️ Method `is_exercise_type_required`

```python
def is_exercise_type_required(self, exercise_id: int) -> bool
```

Check if exercise type is required for a given exercise.

Args:

- `exercise_id` (`int`): Exercise ID.

Returns:

- `bool`: True if type is required, False otherwise.

<details>
<summary>Code:</summary>

```python
def is_exercise_type_required(self, exercise_id: int) -> bool:
        rows = self.get_rows("SELECT is_type_required FROM exercises WHERE _id = :ex_id", {"ex_id": exercise_id})
        return bool(rows and rows[0][0] == 1)
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

### ⚙️ Method `update_exercise`

```python
def update_exercise(self, exercise_id: int, name: str, unit: str) -> bool
```

Update an existing exercise.

Args:

- `exercise_id` (`int`): Exercise ID.
- `name` (`str`): Exercise name.
- `unit` (`str`): Unit of measurement.
- `is_type_required` (`bool`): Whether exercise type is required.
- `calories_per_unit` (`float`): Calories burned per unit. Defaults to `0.0`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_exercise(
        self, exercise_id: int, name: str, unit: str, *, is_type_required: bool, calories_per_unit: float = 0.0
    ) -> bool:
        query = (
            "UPDATE exercises SET name = :n, unit = :u, "
            "is_type_required = :itr, calories_per_unit = :cpu "
            "WHERE _id = :id"
        )
        params = {
            "n": name,
            "u": unit,
            "itr": 1 if is_type_required else 0,
            "cpu": calories_per_unit,
            "id": exercise_id,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `update_exercise_type`

```python
def update_exercise_type(self, type_id: int, exercise_id: int, type_name: str, calories_modifier: float = 1.0) -> bool
```

Update an existing exercise type.

Args:

- `type_id` (`int`): Type ID.
- `exercise_id` (`int`): Exercise ID.
- `type_name` (`str`): Type name.
- `calories_modifier` (`float`): Calories modifier for this type. Defaults to `1.0`.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_exercise_type(
        self, type_id: int, exercise_id: int, type_name: str, calories_modifier: float = 1.0
    ) -> bool:
        query = "UPDATE types SET _id_exercises = :ex, type = :tp, calories_modifier = :cm WHERE _id = :id"
        params = {"ex": exercise_id, "tp": type_name, "cm": calories_modifier, "id": type_id}
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `update_process_record`

```python
def update_process_record(self, record_id: int, exercise_id: int, type_id: int, value: str, date: str) -> bool
```

Update an existing process record.

Args:

- `record_id` (`int`): Record ID.
- `exercise_id` (`int`): Exercise ID.
- `type_id` (`int`): Type ID (-1 for no type).
- `value` (`str`): Exercise value.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_process_record(self, record_id: int, exercise_id: int, type_id: int, value: str, date: str) -> bool:
        query = """
            UPDATE process
            SET _id_exercises = :ex,
                _id_types = :tp,
                date = :dt,
                value = :val
            WHERE _id = :id
        """
        params = {
            "ex": exercise_id,
            "tp": type_id,
            "dt": date,
            "val": value,
            "id": record_id,
        }
        return self.execute_simple_query(query, params)
```

</details>

### ⚙️ Method `update_weight_record`

```python
def update_weight_record(self, record_id: int, value: float, date: str) -> bool
```

Update an existing weight record.

Args:

- `record_id` (`int`): Record ID.
- `value` (`float`): Weight value.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_weight_record(self, record_id: int, value: float, date: str) -> bool:
        query = "UPDATE weight SET value = :v, date = :d WHERE _id = :id"
        params = {"v": value, "d": date, "id": record_id}
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
        self.connection_name = f"fitness_db_{uuid.uuid4().hex[:8]}_{thread_id}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(self._db_filename)

        if not self.db.open():
            error_msg = self.db.lastError().text() if self.db.lastError().isValid() else "Unknown error"
            error_msg = f"❌ Failed to reconnect to database: {error_msg}"
            raise ConnectionError(error_msg)
```

</details>
