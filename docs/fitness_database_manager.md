---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `fitness_database_manager.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Class `FitnessDatabaseManager`](#class-fitnessdatabasemanager)
  - [Method `__init__`](#method-__init__)
  - [Method `__del__`](#method-__del__)
  - [Method `_create_query`](#method-_create_query)
  - [Method `_iter_query`](#method-_iter_query)
  - [Method `_rows_from_query`](#method-_rows_from_query)
  - [Method `add_exercise`](#method-add_exercise)
  - [Method `add_exercise_type`](#method-add_exercise_type)
  - [Method `add_process_record`](#method-add_process_record)
  - [Method `add_weight_record`](#method-add_weight_record)
  - [Method `close`](#method-close)
  - [Method `delete_exercise`](#method-delete_exercise)
  - [Method `delete_exercise_type`](#method-delete_exercise_type)
  - [Method `delete_process_record`](#method-delete_process_record)
  - [Method `delete_weight_record`](#method-delete_weight_record)
  - [Method `execute_query`](#method-execute_query)
  - [Method `execute_simple_query`](#method-execute_simple_query)
  - [Method `get_all_exercise_types`](#method-get_all_exercise_types)
  - [Method `get_all_exercises`](#method-get_all_exercises)
  - [Method `get_all_process_records`](#method-get_all_process_records)
  - [Method `get_all_weight_records`](#method-get_all_weight_records)
  - [Method `get_earliest_process_date`](#method-get_earliest_process_date)
  - [Method `get_earliest_weight_date`](#method-get_earliest_weight_date)
  - [Method `get_exercise_chart_data`](#method-get_exercise_chart_data)
  - [Method `get_exercise_types`](#method-get_exercise_types)
  - [Method `get_exercise_unit`](#method-get_exercise_unit)
  - [Method `get_exercises_by_frequency`](#method-get_exercises_by_frequency)
  - [Method `get_filtered_process_records`](#method-get_filtered_process_records)
  - [Method `get_id`](#method-get_id)
  - [Method `get_items`](#method-get_items)
  - [Method `get_last_exercise_record`](#method-get_last_exercise_record)
  - [Method `get_last_weight`](#method-get_last_weight)
  - [Method `get_rows`](#method-get_rows)
  - [Method `get_sets_chart_data`](#method-get_sets_chart_data)
  - [Method `get_sets_count_today`](#method-get_sets_count_today)
  - [Method `get_statistics_data`](#method-get_statistics_data)
  - [Method `get_weight_chart_data`](#method-get_weight_chart_data)
  - [Method `is_database_open`](#method-is_database_open)
  - [Method `is_exercise_type_required`](#method-is_exercise_type_required)
  - [Method `update_exercise`](#method-update_exercise)
  - [Method `update_exercise_type`](#method-update_exercise_type)
  - [Method `update_process_record`](#method-update_process_record)
  - [Method `update_weight_record`](#method-update_weight_record)
- [Function `_safe_identifier`](#function-_safe_identifier)

</details>

## Class `FitnessDatabaseManager`

```python
class FitnessDatabaseManager
```

Manage the connection and operations for a fitness tracking database.

Attributes:

- `db` (`QSqlDatabase`): A live connection object opened on an SQLite
  database file.
- `connection_name` (`str`): Unique name for this database connection.

<details>
<summary>Code:</summary>

```python
class FitnessDatabaseManager:

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in *db_filename*.

        Args:

        - `db_filename` (`str`): The path to the target database file.

        Raises:

        - `ConnectionError`: If the underlying Qt driver fails to open the
          database.

        """
        # Create unique connection name to avoid conflicts
        import uuid

        self.connection_name = f"fitness_db_{uuid.uuid4().hex[:8]}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(db_filename)
        if not self.db.open():
            msg = f"Failed to open the database: {self.db.lastError().text()}"
            raise ConnectionError(msg)

    def __del__(self) -> None:
        """Clean up database connection when object is destroyed."""
        try:
            self.close()
        except Exception as e:
            print(f"Warning: Error during database cleanup: {e}")

    def _create_query(self) -> QSqlQuery:
        """Create a QSqlQuery using this manager's database connection.

        Returns:
        - `QSqlQuery`: A query object bound to this database connection.

        """
        return QSqlQuery(self.db)

    def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]:
        """Yield every record in *query* one by one.

        Args:

        - `query` (`Optional[QSqlQuery]`): A prepared and executed `QSqlQuery`
          object.

        Yields:

        - `QSqlQuery`: The same object positioned on consecutive records.

        """
        if query is None:
            return
        while query.next():
            yield query

    def _rows_from_query(self, query: QSqlQuery) -> list[list[Any]]:
        """Convert the full result set in *query* into a list of rows.

        Args:

        - `query` (`QSqlQuery`): An executed query.

        Returns:

        - `List[List[Any]]`: Every database row represented as a list whose
          elements correspond to column values.

        """
        result: list[list[Any]] = []
        while query.next():
            row = [query.value(i) for i in range(query.record().count())]
            result.append(row)
        return result

    def add_exercise(self, name: str, unit: str, *, is_type_required: bool) -> bool:
        """Add a new exercise to the database.

        Args:
        - `name` (`str`): Exercise name.
        - `unit` (`str`): Unit of measurement.
        - `is_type_required` (`bool`): Whether exercise type is required.

        Returns:
        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO exercises (name, unit, is_type_required) VALUES (:name, :unit, :is_type_required)"
        params = {"name": name, "unit": unit, "is_type_required": 1 if is_type_required else 0}
        return self.execute_simple_query(query, params)

    def add_exercise_type(self, exercise_id: int, type_name: str) -> bool:
        """Add a new exercise type.

        Args:
        - `exercise_id` (`int`): Exercise ID.
        - `type_name` (`str`): Type name.

        Returns:
        - `bool`: True if successful, False otherwise.

        """
        query = "INSERT INTO types (_id_exercises, type) VALUES (:ex, :tp)"
        return self.execute_simple_query(query, {"ex": exercise_id, "tp": type_name})

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

    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self, "db") and self.db.isOpen():
            self.db.close()

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
        """Prepare and execute *query_text* with optional bound *params*.

        Args:

        - `query_text` (`str`): A parametrised SQL statement.
        - `params` (`Optional[Dict[str, Any]]`): Run-time values to be bound to
          named placeholders in *query_text*. Defaults to `None`.

        Returns:

        - `Optional[QSqlQuery]`: The executed query when successful, otherwise
          `None`.

        """
        # Check if database is open
        if not self.db.isOpen():
            print(f"Database is not open for query: {query_text}")
            return None

        query = self._create_query()
        if not query.prepare(query_text):
            print(f"Failed to prepare query: {query.lastError().text()}")
            print(f"Query was: {query_text}")
            return None

        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)

        if not query.exec():
            print(f"Failed to execute query: {query.lastError().text()}")
            print(f"Query was: {query_text}")
            print(f"Params were: {params}")
            return None

        return query

    def execute_simple_query(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> bool:
        """Execute a simple query and return success status (for INSERT/UPDATE/DELETE operations).

        Args:

        - `query_text` (`str`): A parametrised SQL statement.
        - `params` (`Optional[Dict[str, Any]]`): Run-time values to be bound to
          named placeholders in *query_text*. Defaults to `None`.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        # Check if database is open
        if not self.db.isOpen():
            print(f"Database is not open for query: {query_text}")
            return False

        query = self._create_query()
        if not query.prepare(query_text):
            print(f"Failed to prepare query: {query.lastError().text()}")
            print(f"Query was: {query_text}")
            return False

        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)

        success = query.exec()
        if not success:
            print(f"Failed to execute query: {query.lastError().text()}")
            print(f"Query was: {query_text}")
            print(f"Params were: {params}")

        # Clear the query to release resources
        query.clear()
        return success

    def get_all_exercise_types(self) -> list[list[Any]]:
        """Get all exercise types with exercise names.

        Returns:
        - `List[List[Any]]`: List of type records [_id, exercise_name, type_name].

        """
        return self.get_rows("""
            SELECT t._id, e.name, t.type
            FROM types t
            JOIN exercises e ON t._id_exercises = e._id
        """)

    def get_all_exercises(self) -> list[list[Any]]:
        """Get all exercises with their properties.

        Returns:
        - `List[List[Any]]`: List of exercise records [_id, name, unit, is_type_required].

        """
        return self.get_rows("SELECT _id, name, unit, is_type_required FROM exercises")

    def get_all_process_records(self) -> list[list[Any]]:
        """Get all process records with exercise and type names.

        Returns:
        - `List[List[Any]]`: List of process records [_id, exercise_name, type_name, value, unit, date].

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
            ORDER BY p._id DESC
        """)

    def get_all_weight_records(self) -> list[list[Any]]:
        """Get all weight records.

        Returns:
        - `List[List[Any]]`: List of weight records [_id, value, date].

        """
        return self.get_rows("SELECT _id, value, date FROM weight ORDER BY date DESC")

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
        - `exercise_type` (`str | None`): Exercise type (None for all types).
        - `date_from` (`str | None`): From date (YYYY-MM-DD).
        - `date_to` (`str | None`): To date (YYYY-MM-DD).

        Returns:
        - `List[tuple[str, str]]`: List of (date, value) tuples.

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

    def get_exercise_types(self, exercise_id: int) -> list[str]:
        """Get all types for a specific exercise.

        Args:
        - `exercise_id` (`int`): Exercise ID.

        Returns:
        - `List[str]`: List of type names.

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
        """Return exercise names ordered by frequency in recent *limit* rows.

        Args:

        - `limit` (`int`): Number of most recent rows from the *process* table
          to analyse. Defaults to `500`.

        Returns:

        - `List[str]`: Exercise names sorted by how often they appear; exercises
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

        # Preserve exercises not present in *sorted_exercises*.
        remainder = [name for name in all_exercises.values() if name not in sorted_exercises]
        return sorted_exercises + remainder

    def get_filtered_process_records(
        self,
        exercise_name: str | None = None,
        exercise_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[list[Any]]:
        """Get filtered process records.

        Args:
        - `exercise_name` (`str | None`): Filter by exercise name.
        - `exercise_type` (`str | None`): Filter by exercise type.
        - `date_from` (`str | None`): Filter from date (YYYY-MM-DD).
        - `date_to` (`str | None`): Filter to date (YYYY-MM-DD).

        Returns:
        - `List[List[Any]]`: List of filtered process records.

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

        query_text += " ORDER BY p._id DESC"

        return self.get_rows(query_text, params)

    def get_id(
        self,
        table: str,
        name_column: str,
        name_value: str,
        id_column: str = "_id",
        condition: str | None = None,
    ) -> int | None:
        """Return a single ID that matches *name_value* in *table*.

        Args:

        - `table` (`str`): Target table name.
        - `name_column` (`str`): Column that stores the searched value.
        - `name_value` (`str`): Searched value itself.
        - `id_column` (`str`): Column that stores the ID. Defaults to `"_id"`.
        - `condition` (`Optional[str]`): Extra SQL that will be appended to the
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
        """Return all values stored in *column* from *table*.

        Args:

        - `table` (`str`): Table that will be queried.
        - `column` (`str`): The column to extract.
        - `condition` (`Optional[str]`): Optional `WHERE` clause. Defaults to
          `None`.
        - `order_by` (`Optional[str]`): Optional `ORDER BY` clause. Defaults to
          `None`.

        Returns:

        - `List[Any]`: The resulting data as a flat Python list.

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

    def get_rows(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> list[list[Any]]:
        """Execute *query_text* and fetch the whole result set.

        Args:

        - `query_text` (`str`): A SQL statement.
        - `params` (`Optional[Dict[str, Any]]`): Values to be bound at run time.
          Defaults to `None`.

        Returns:

        - `List[List[Any]]`: A list whose elements are the records returned by
          the database.

        """
        query = self.execute_query(query_text, params)
        if query:
            result = self._rows_from_query(query)
            query.clear()  # Clear the query to release resources
            return result
        return []

    def get_sets_chart_data(self, date_from: str, date_to: str) -> list[tuple[str, int]]:
        """Get sets (workout count) data for charting.

        Args:
        - `date_from` (`str`): From date (YYYY-MM-DD).
        - `date_to` (`str`): To date (YYYY-MM-DD).

        Returns:
        - `List[tuple[str, int]]`: List of (date, count) tuples.

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
        today = datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d")
        rows = self.get_rows("SELECT COUNT(*) FROM process WHERE date = :today", {"today": today})
        return rows[0][0] if rows else 0

    def get_statistics_data(self) -> list[tuple[str, str, float, str]]:
        """Get data for statistics display.

        Returns:
        - `List[tuple[str, str, float, str]]`: List of (exercise_name, type_name, value, date) tuples.

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
        - `List[tuple[float, str]]`: List of (weight_value, date) tuples.

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
        return hasattr(self, "db") and self.db.isOpen()

    def is_exercise_type_required(self, exercise_id: int) -> bool:
        """Check if exercise type is required for a given exercise.

        Args:
        - `exercise_id` (`int`): Exercise ID.

        Returns:
        - `bool`: True if type is required, False otherwise.

        """
        rows = self.get_rows("SELECT is_type_required FROM exercises WHERE _id = :ex_id", {"ex_id": exercise_id})
        return bool(rows and rows[0][0] == 1)

    def update_exercise(self, exercise_id: int, name: str, unit: str, *, is_type_required: bool) -> bool:
        """Update an existing exercise.

        Args:
        - `exercise_id` (`int`): Exercise ID.
        - `name` (`str`): Exercise name.
        - `unit` (`str`): Unit of measurement.
        - `is_type_required` (`bool`): Whether exercise type is required.

        Returns:
        - `bool`: True if successful, False otherwise.

        """
        query = "UPDATE exercises SET name = :n, unit = :u, is_type_required = :itr WHERE _id = :id"
        params = {
            "n": name,
            "u": unit,
            "itr": 1 if is_type_required else 0,
            "id": exercise_id,
        }
        return self.execute_simple_query(query, params)

    def update_exercise_type(self, type_id: int, exercise_id: int, type_name: str) -> bool:
        """Update an existing exercise type.

        Args:
        - `type_id` (`int`): Type ID.
        - `exercise_id` (`int`): Exercise ID.
        - `type_name` (`str`): Type name.

        Returns:
        - `bool`: True if successful, False otherwise.

        """
        query = "UPDATE types SET _id_exercises = :ex, type = :tp WHERE _id = :id"
        params = {"ex": exercise_id, "tp": type_name, "id": type_id}
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
```

</details>

### Method `__init__`

```python
def __init__(self, db_filename: str) -> None
```

Open a connection to an SQLite database stored in _db_filename_.

Args:

- `db_filename` (`str`): The path to the target database file.

Raises:

- `ConnectionError`: If the underlying Qt driver fails to open the
  database.

<details>
<summary>Code:</summary>

```python
def __init__(self, db_filename: str) -> None:
        # Create unique connection name to avoid conflicts
        import uuid

        self.connection_name = f"fitness_db_{uuid.uuid4().hex[:8]}"

        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(db_filename)
        if not self.db.open():
            msg = f"Failed to open the database: {self.db.lastError().text()}"
            raise ConnectionError(msg)
```

</details>

### Method `__del__`

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

### Method `_create_query`

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
        return QSqlQuery(self.db)
```

</details>

### Method `_iter_query`

```python
def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]
```

Yield every record in _query_ one by one.

Args:

- `query` (`Optional[QSqlQuery]`): A prepared and executed `QSqlQuery`
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

### Method `_rows_from_query`

```python
def _rows_from_query(self, query: QSqlQuery) -> list[list[Any]]
```

Convert the full result set in _query_ into a list of rows.

Args:

- `query` (`QSqlQuery`): An executed query.

Returns:

- `List[List[Any]]`: Every database row represented as a list whose
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

### Method `add_exercise`

```python
def add_exercise(self, name: str, unit: str) -> bool
```

Add a new exercise to the database.

Args:

- `name` (`str`): Exercise name.
- `unit` (`str`): Unit of measurement.
- `is_type_required` (`bool`): Whether exercise type is required.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_exercise(self, name: str, unit: str, *, is_type_required: bool) -> bool:
        query = "INSERT INTO exercises (name, unit, is_type_required) VALUES (:name, :unit, :is_type_required)"
        params = {"name": name, "unit": unit, "is_type_required": 1 if is_type_required else 0}
        return self.execute_simple_query(query, params)
```

</details>

### Method `add_exercise_type`

```python
def add_exercise_type(self, exercise_id: int, type_name: str) -> bool
```

Add a new exercise type.

Args:

- `exercise_id` (`int`): Exercise ID.
- `type_name` (`str`): Type name.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def add_exercise_type(self, exercise_id: int, type_name: str) -> bool:
        query = "INSERT INTO types (_id_exercises, type) VALUES (:ex, :tp)"
        return self.execute_simple_query(query, {"ex": exercise_id, "tp": type_name})
```

</details>

### Method `add_process_record`

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

### Method `add_weight_record`

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

### Method `close`

```python
def close(self) -> None
```

Close the database connection.

<details>
<summary>Code:</summary>

```python
def close(self) -> None:
        if hasattr(self, "db") and self.db.isOpen():
            self.db.close()
```

</details>

### Method `delete_exercise`

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

### Method `delete_exercise_type`

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

### Method `delete_process_record`

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

### Method `delete_weight_record`

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

### Method `execute_query`

```python
def execute_query(self, query_text: str, params: dict[str, Any] | None = None) -> QSqlQuery | None
```

Prepare and execute _query_text_ with optional bound _params_.

Args:

- `query_text` (`str`): A parametrised SQL statement.
- `params` (`Optional[Dict[str, Any]]`): Run-time values to be bound to
  named placeholders in _query_text_. Defaults to `None`.

Returns:

- `Optional[QSqlQuery]`: The executed query when successful, otherwise
  `None`.

<details>
<summary>Code:</summary>

```python
def execute_query(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> QSqlQuery | None:
        # Check if database is open
        if not self.db.isOpen():
            print(f"Database is not open for query: {query_text}")
            return None

        query = self._create_query()
        if not query.prepare(query_text):
            print(f"Failed to prepare query: {query.lastError().text()}")
            print(f"Query was: {query_text}")
            return None

        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)

        if not query.exec():
            print(f"Failed to execute query: {query.lastError().text()}")
            print(f"Query was: {query_text}")
            print(f"Params were: {params}")
            return None

        return query
```

</details>

### Method `execute_simple_query`

```python
def execute_simple_query(self, query_text: str, params: dict[str, Any] | None = None) -> bool
```

Execute a simple query and return success status (for INSERT/UPDATE/DELETE operations).

Args:

- `query_text` (`str`): A parametrised SQL statement.
- `params` (`Optional[Dict[str, Any]]`): Run-time values to be bound to
  named placeholders in _query_text_. Defaults to `None`.

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
        # Check if database is open
        if not self.db.isOpen():
            print(f"Database is not open for query: {query_text}")
            return False

        query = self._create_query()
        if not query.prepare(query_text):
            print(f"Failed to prepare query: {query.lastError().text()}")
            print(f"Query was: {query_text}")
            return False

        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)

        success = query.exec()
        if not success:
            print(f"Failed to execute query: {query.lastError().text()}")
            print(f"Query was: {query_text}")
            print(f"Params were: {params}")

        # Clear the query to release resources
        query.clear()
        return success
```

</details>

### Method `get_all_exercise_types`

```python
def get_all_exercise_types(self) -> list[list[Any]]
```

Get all exercise types with exercise names.

Returns:

- `List[List[Any]]`: List of type records [_id, exercise_name, type_name].

<details>
<summary>Code:</summary>

```python
def get_all_exercise_types(self) -> list[list[Any]]:
        return self.get_rows("""
            SELECT t._id, e.name, t.type
            FROM types t
            JOIN exercises e ON t._id_exercises = e._id
        """)
```

</details>

### Method `get_all_exercises`

```python
def get_all_exercises(self) -> list[list[Any]]
```

Get all exercises with their properties.

Returns:

- `List[List[Any]]`: List of exercise records [_id, name, unit, is_type_required].

<details>
<summary>Code:</summary>

```python
def get_all_exercises(self) -> list[list[Any]]:
        return self.get_rows("SELECT _id, name, unit, is_type_required FROM exercises")
```

</details>

### Method `get_all_process_records`

```python
def get_all_process_records(self) -> list[list[Any]]
```

Get all process records with exercise and type names.

Returns:

- `List[List[Any]]`: List of process records [_id, exercise_name, type_name, value, unit, date].

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
            ORDER BY p._id DESC
        """)
```

</details>

### Method `get_all_weight_records`

```python
def get_all_weight_records(self) -> list[list[Any]]
```

Get all weight records.

Returns:

- `List[List[Any]]`: List of weight records [_id, value, date].

<details>
<summary>Code:</summary>

```python
def get_all_weight_records(self) -> list[list[Any]]:
        return self.get_rows("SELECT _id, value, date FROM weight ORDER BY date DESC")
```

</details>

### Method `get_earliest_process_date`

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

### Method `get_earliest_weight_date`

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

### Method `get_exercise_chart_data`

```python
def get_exercise_chart_data(self, exercise_name: str, exercise_type: str | None = None, date_from: str | None = None, date_to: str | None = None) -> list[tuple[str, str]]
```

Get exercise data for charting.

Args:

- `exercise_name` (`str`): Exercise name.
- `exercise_type` (`str | None`): Exercise type (None for all types).
- `date_from` (`str | None`): From date (YYYY-MM-DD).
- `date_to` (`str | None`): To date (YYYY-MM-DD).

Returns:

- `List[tuple[str, str]]`: List of (date, value) tuples.

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

### Method `get_exercise_types`

```python
def get_exercise_types(self, exercise_id: int) -> list[str]
```

Get all types for a specific exercise.

Args:

- `exercise_id` (`int`): Exercise ID.

Returns:

- `List[str]`: List of type names.

<details>
<summary>Code:</summary>

```python
def get_exercise_types(self, exercise_id: int) -> list[str]:
        return self.get_items("types", "type", condition=f"_id_exercises = {exercise_id}")
```

</details>

### Method `get_exercise_unit`

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

### Method `get_exercises_by_frequency`

```python
def get_exercises_by_frequency(self, limit: int = 500) -> list[str]
```

Return exercise names ordered by frequency in recent _limit_ rows.

Args:

- `limit` (`int`): Number of most recent rows from the _process_ table
  to analyse. Defaults to `500`.

Returns:

- `List[str]`: Exercise names sorted by how often they appear; exercises
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

        # Preserve exercises not present in *sorted_exercises*.
        remainder = [name for name in all_exercises.values() if name not in sorted_exercises]
        return sorted_exercises + remainder
```

</details>

### Method `get_filtered_process_records`

```python
def get_filtered_process_records(self, exercise_name: str | None = None, exercise_type: str | None = None, date_from: str | None = None, date_to: str | None = None) -> list[list[Any]]
```

Get filtered process records.

Args:

- `exercise_name` (`str | None`): Filter by exercise name.
- `exercise_type` (`str | None`): Filter by exercise type.
- `date_from` (`str | None`): Filter from date (YYYY-MM-DD).
- `date_to` (`str | None`): Filter to date (YYYY-MM-DD).

Returns:

- `List[List[Any]]`: List of filtered process records.

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

        query_text += " ORDER BY p._id DESC"

        return self.get_rows(query_text, params)
```

</details>

### Method `get_id`

```python
def get_id(self, table: str, name_column: str, name_value: str, id_column: str = "_id", condition: str | None = None) -> int | None
```

Return a single ID that matches _name_value_ in _table_.

Args:

- `table` (`str`): Target table name.
- `name_column` (`str`): Column that stores the searched value.
- `name_value` (`str`): Searched value itself.
- `id_column` (`str`): Column that stores the ID. Defaults to `"_id"`.
- `condition` (`Optional[str]`): Extra SQL that will be appended to the
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

### Method `get_items`

```python
def get_items(self, table: str, column: str, condition: str | None = None, order_by: str | None = None) -> list[Any]
```

Return all values stored in _column_ from _table_.

Args:

- `table` (`str`): Table that will be queried.
- `column` (`str`): The column to extract.
- `condition` (`Optional[str]`): Optional `WHERE` clause. Defaults to
  `None`.
- `order_by` (`Optional[str]`): Optional `ORDER BY` clause. Defaults to
  `None`.

Returns:

- `List[Any]`: The resulting data as a flat Python list.

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

### Method `get_last_exercise_record`

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

### Method `get_last_weight`

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

### Method `get_rows`

```python
def get_rows(self, query_text: str, params: dict[str, Any] | None = None) -> list[list[Any]]
```

Execute _query_text_ and fetch the whole result set.

Args:

- `query_text` (`str`): A SQL statement.
- `params` (`Optional[Dict[str, Any]]`): Values to be bound at run time.
  Defaults to `None`.

Returns:

- `List[List[Any]]`: A list whose elements are the records returned by
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

### Method `get_sets_chart_data`

```python
def get_sets_chart_data(self, date_from: str, date_to: str) -> list[tuple[str, int]]
```

Get sets (workout count) data for charting.

Args:

- `date_from` (`str`): From date (YYYY-MM-DD).
- `date_to` (`str`): To date (YYYY-MM-DD).

Returns:

- `List[tuple[str, int]]`: List of (date, count) tuples.

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

### Method `get_sets_count_today`

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
        today = datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d")
        rows = self.get_rows("SELECT COUNT(*) FROM process WHERE date = :today", {"today": today})
        return rows[0][0] if rows else 0
```

</details>

### Method `get_statistics_data`

```python
def get_statistics_data(self) -> list[tuple[str, str, float, str]]
```

Get data for statistics display.

Returns:

- `List[tuple[str, str, float, str]]`: List of (exercise_name, type_name, value, date) tuples.

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

### Method `get_weight_chart_data`

```python
def get_weight_chart_data(self, date_from: str, date_to: str) -> list[tuple[float, str]]
```

Get weight data for charting.

Args:

- `date_from` (`str`): From date (YYYY-MM-DD).
- `date_to` (`str`): To date (YYYY-MM-DD).

Returns:

- `List[tuple[float, str]]`: List of (weight_value, date) tuples.

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

### Method `is_database_open`

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
        return hasattr(self, "db") and self.db.isOpen()
```

</details>

### Method `is_exercise_type_required`

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

### Method `update_exercise`

```python
def update_exercise(self, exercise_id: int, name: str, unit: str) -> bool
```

Update an existing exercise.

Args:

- `exercise_id` (`int`): Exercise ID.
- `name` (`str`): Exercise name.
- `unit` (`str`): Unit of measurement.
- `is_type_required` (`bool`): Whether exercise type is required.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_exercise(self, exercise_id: int, name: str, unit: str, *, is_type_required: bool) -> bool:
        query = "UPDATE exercises SET name = :n, unit = :u, is_type_required = :itr WHERE _id = :id"
        params = {
            "n": name,
            "u": unit,
            "itr": 1 if is_type_required else 0,
            "id": exercise_id,
        }
        return self.execute_simple_query(query, params)
```

</details>

### Method `update_exercise_type`

```python
def update_exercise_type(self, type_id: int, exercise_id: int, type_name: str) -> bool
```

Update an existing exercise type.

Args:

- `type_id` (`int`): Type ID.
- `exercise_id` (`int`): Exercise ID.
- `type_name` (`str`): Type name.

Returns:

- `bool`: True if successful, False otherwise.

<details>
<summary>Code:</summary>

```python
def update_exercise_type(self, type_id: int, exercise_id: int, type_name: str) -> bool:
        query = "UPDATE types SET _id_exercises = :ex, type = :tp WHERE _id = :id"
        params = {"ex": exercise_id, "tp": type_name, "id": type_id}
        return self.execute_simple_query(query, params)
```

</details>

### Method `update_process_record`

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

### Method `update_weight_record`

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

## Function `_safe_identifier`

```python
def _safe_identifier(identifier: str) -> str
```

Return _identifier_ unchanged if it is a valid SQL identifier.

The function guarantees that the returned string is composed only of
ASCII letters, digits, or underscores and does **not** start with a digit.
It is therefore safe to interpolate directly into an SQL statement.

Args:

- `identifier` (`str`): A candidate string that must be validated to be
  used as a table or column name.

Returns:

- `str`: The validated identifier (identical to the input).

Raises:

- `ValueError`: If _identifier_ contains forbidden characters.

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
