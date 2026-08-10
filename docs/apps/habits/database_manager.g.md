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
  - [⚙️ Method `count_habit_checkins_between`](#%EF%B8%8F-method-count_habit_checkins_between)
  - [⚙️ Method `delete_habit`](#%EF%B8%8F-method-delete_habit)
  - [⚙️ Method `delete_process_habit_record`](#%EF%B8%8F-method-delete_process_habit_record)
  - [⚙️ Method `ensure_habits_schema`](#%EF%B8%8F-method-ensure_habits_schema)
  - [⚙️ Method `get_all_habits`](#%EF%B8%8F-method-get_all_habits)
  - [⚙️ Method `get_all_process_habits_records`](#%EF%B8%8F-method-get_all_process_habits_records)
  - [⚙️ Method `get_earliest_process_habit_date`](#%EF%B8%8F-method-get_earliest_process_habit_date)
  - [⚙️ Method `get_filtered_process_habits_records`](#%EF%B8%8F-method-get_filtered_process_habits_records)
  - [⚙️ Method `get_habit_by_id`](#%EF%B8%8F-method-get_habit_by_id)
  - [⚙️ Method `get_habit_calendar_data`](#%EF%B8%8F-method-get_habit_calendar_data)
  - [⚙️ Method `get_habit_done_dates_between`](#%EF%B8%8F-method-get_habit_done_dates_between)
  - [⚙️ Method `get_habit_streak`](#%EF%B8%8F-method-get_habit_streak)
  - [⚙️ Method `get_habit_total_checkins`](#%EF%B8%8F-method-get_habit_total_checkins)
  - [⚙️ Method `get_habits`](#%EF%B8%8F-method-get_habits)
  - [⚙️ Method `get_habits_years`](#%EF%B8%8F-method-get_habits_years)
  - [⚙️ Method `get_limited_process_habits_records`](#%EF%B8%8F-method-get_limited_process_habits_records)
  - [⚙️ Method `is_habit_done_on_date`](#%EF%B8%8F-method-is_habit_done_on_date)
  - [⚙️ Method `set_habit_archived`](#%EF%B8%8F-method-set_habit_archived)
  - [⚙️ Method `toggle_habit_checkin`](#%EF%B8%8F-method-toggle_habit_checkin)
  - [⚙️ Method `update_habit`](#%EF%B8%8F-method-update_habit)
  - [⚙️ Method `update_process_habit_record`](#%EF%B8%8F-method-update_process_habit_record)

</details>

## 🏛️ Class `DatabaseManager`

```python
class DatabaseManager(QtSqliteDatabaseManagerBase)
```

Manage the connection and operations for a habits tracking database.

Attributes:

- `db` (`QSqlDatabase | None`): A live connection object opened on an SQLite database file.
- `connection_name` (`str`): Unique name for this database connection.

<details>
<summary>Code:</summary>

```python
class DatabaseManager(QtSqliteDatabaseManagerBase):

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in `db_filename`.

        Args:

        - `db_filename` (`str`): The path to the target database file.

        Raises:

        - `ConnectionError`: If the underlying Qt driver fails to open the database.

        """
        super().__init__(prefix="habits_db", db_filename=db_filename)

    def add_habit(self, name: str, *, is_bool: bool | None = None) -> bool:
        """Add a new habit to the database.

        Args:

        - `name` (`str`): Habit name.
        - `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

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

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = "INSERT INTO process_habits (_id_habit, value, date) VALUES (:habit_id, :value, :date)"
        params = {
            "habit_id": habit_id,
            "value": value,
            "date": date,
        }

        result = self.execute_simple_query(query, params)
        if not result:
            logger.error("%s", f"Failed to add process habit record: habit_id={habit_id}, value={value}, date={date}")
        return result

    def count_habit_checkins_between(self, habit_id: int, date_from: str, date_to: str) -> int:
        """Count days with value > 0 for a habit in an inclusive date range."""
        rows = self.get_rows(
            """
            SELECT COUNT(*)
            FROM process_habits
            WHERE _id_habit = :habit_id
              AND date BETWEEN :date_from AND :date_to
              AND value > 0
            """,
            {"habit_id": habit_id, "date_from": date_from, "date_to": date_to},
        )
        if rows and rows[0][0] is not None:
            return int(rows[0][0])
        return 0

    def delete_habit(self, habit_id: int) -> bool:
        """Delete a habit from the database.

        Args:

        - `habit_id` (`int`): Habit ID to delete.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = "DELETE FROM habits WHERE _id = :id"
        return self.execute_simple_query(query, {"id": habit_id})

    def delete_process_habit_record(self, record_id: int) -> bool:
        """Delete a process habit record.

        Args:

        - `record_id` (`int`): Record ID to delete.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = "DELETE FROM process_habits WHERE _id = :id"
        return self.execute_simple_query(query, {"id": record_id})

    def ensure_habits_schema(self) -> bool:
        """Ensure the habits table has required columns for current app version.

        Returns:

        - `bool`: `True` when schema is compatible or successfully migrated.

        """
        if not self.table_exists("habits"):
            return True

        try:
            cols = self.get_rows("PRAGMA table_info(habits)")
            existing = {str(row[1]) for row in cols if len(row) > 1 and row[1]}
            if "is_archived" not in existing:
                return self.execute_simple_query("ALTER TABLE habits ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0")
        except Exception:
            logger.exception("Failed to ensure habits schema")
            return False
        else:
            return True

    def get_all_habits(self) -> list[list[Any]]:
        r"""Get all habits with their properties.

        Returns:

        - `list[list[Any]]`: List of habit records [\_id, name, is_bool, is_archived].

        """
        return self.get_rows("SELECT _id, name, is_bool, is_archived FROM habits")

    def get_all_process_habits_records(self) -> list[list[Any]]:
        r"""Get all process habits records with habit names.

        Returns:

        - `list[list[Any]]`: List of process habits records [\_id, habit_name, value, date].

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

        - `str | None`: Date string in YYYY-MM-DD format or `None` if no records.

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

    def get_habit_by_id(self, habit_id: int) -> list[Any] | None:
        """Return one habit row ``[_id, name, is_bool, is_archived]`` or ``None``."""
        rows = self.get_rows(
            "SELECT _id, name, is_bool, is_archived FROM habits WHERE _id = :id",
            {"id": habit_id},
        )
        if rows:
            return list(rows[0])
        return None

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

    def get_habit_done_dates_between(self, habit_id: int, date_from: str, date_to: str) -> list[str]:
        """Return ISO dates with value > 0 for a habit in an inclusive range."""
        rows = self.get_rows(
            """
            SELECT date
            FROM process_habits
            WHERE _id_habit = :habit_id
              AND date BETWEEN :date_from AND :date_to
              AND value > 0
            ORDER BY date ASC
            """,
            {"habit_id": habit_id, "date_from": date_from, "date_to": date_to},
        )
        return [str(row[0]) for row in rows if row and row[0]]

    def get_habit_streak(self, habit_id: int) -> int:
        """Return consecutive completed days ending at today or yesterday.

        If today is not completed yet, the streak may still continue from yesterday.
        A gap of one or more missed days resets the streak to zero.

        """
        rows = self.get_rows(
            """
            SELECT date
            FROM process_habits
            WHERE _id_habit = :habit_id AND value > 0 AND date IS NOT NULL
            ORDER BY date DESC
            """,
            {"habit_id": habit_id},
        )
        done: set[date] = set()
        for row in rows:
            parsed = _parse_iso_date(str(row[0]) if row and row[0] else "")
            if parsed is not None:
                done.add(parsed)

        if not done:
            return 0

        today = datetime.now(UTC).astimezone().date()
        cursor = today if today in done else today - timedelta(days=1)
        if cursor not in done:
            return 0

        streak = 0
        while cursor in done:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    def get_habit_total_checkins(self, habit_id: int) -> int:
        """Count distinct days with value > 0 for a habit (all time)."""
        rows = self.get_rows(
            """
            SELECT COUNT(DISTINCT date)
            FROM process_habits
            WHERE _id_habit = :habit_id AND value > 0 AND date IS NOT NULL
            """,
            {"habit_id": habit_id},
        )
        if rows and rows[0][0] is not None:
            return int(rows[0][0])
        return 0

    def get_habits(self, *, include_archived: bool = False) -> list[list[Any]]:
        """Get habits with optional inclusion of archived ones."""
        if include_archived:
            return self.get_all_habits()
        return self.get_rows("SELECT _id, name, is_bool, is_archived FROM habits WHERE is_archived = 0")

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

    def get_limited_process_habits_records(self, limit: int = 5000) -> list[list[Any]]:
        r"""Get limited number of process habits records with habit names.

        Args:

        - `limit` (`int`): Maximum number of records to return. Defaults to `5000`.

        Returns:

        - `list[list[Any]]`: List of process habits records [\_id, habit_name, value, date].

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

    def is_habit_done_on_date(self, habit_id: int, date_str: str) -> bool:
        """Return whether habit has value > 0 on ``date_str`` (YYYY-MM-DD)."""
        rows = self.get_rows(
            """
            SELECT value FROM process_habits
            WHERE _id_habit = :habit_id AND date = :date
            LIMIT 1
            """,
            {"habit_id": habit_id, "date": date_str},
        )
        if not rows or rows[0][0] is None:
            return False
        try:
            return int(rows[0][0]) > 0
        except (TypeError, ValueError):
            return False

    def set_habit_archived(self, habit_id: int, *, is_archived: bool) -> bool:
        """Archive/unarchive a habit by ID."""
        query = "UPDATE habits SET is_archived = :v WHERE _id = :id"
        return self.execute_simple_query(query, {"v": 1 if is_archived else 0, "id": habit_id})

    def toggle_habit_checkin(self, habit_id: int, date_str: str) -> bool:
        """Toggle completion for habit on a date.

        If a record with value > 0 exists, delete it (unchecked).
        If a record with value <= 0 exists, set value to 1.
        If no record exists, insert value 1.

        """
        rows = self.get_rows(
            """
            SELECT _id, value FROM process_habits
            WHERE _id_habit = :habit_id AND date = :date
            ORDER BY _id DESC LIMIT 1
            """,
            {"habit_id": habit_id, "date": date_str},
        )
        if not rows:
            return self.add_process_habit_record(habit_id, 1, date_str)

        record_id = int(rows[0][0])
        try:
            value = int(rows[0][1])
        except (TypeError, ValueError):
            value = 0

        if value > 0:
            return self.delete_process_habit_record(record_id)
        return self.update_process_habit_record(record_id, habit_id, 1, date_str)

    def update_habit(
        self,
        habit_id: int,
        name: str,
        *,
        is_bool: bool | None = None,
        is_archived: bool | None = None,
    ) -> bool:
        """Update an existing habit.

        Args:

        - `habit_id` (`int`): Habit ID.
        - `name` (`str`): Habit name.
        - `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.
        - `is_archived` (`bool | None`): Whether habit is archived. Defaults to `None` (do not change).

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = "UPDATE habits SET name = :n, is_bool = :is_bool WHERE _id = :id"
        params = {
            "n": name,
            "is_bool": 1 if is_bool is True else (0 if is_bool is False else None),
            "id": habit_id,
        }
        if is_archived is not None:
            query = "UPDATE habits SET name = :n, is_bool = :is_bool, is_archived = :is_archived WHERE _id = :id"
            params["is_archived"] = 1 if is_archived else 0
        return self.execute_simple_query(query, params)

    def update_process_habit_record(self, record_id: int, habit_id: int, value: int, date: str) -> bool:
        """Update an existing process habit record.

        Args:

        - `record_id` (`int`): Record ID.
        - `habit_id` (`int`): Habit ID.
        - `value` (`int`): Habit value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

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
        super().__init__(prefix="habits_db", db_filename=db_filename)
```

</details>

### ⚙️ Method `add_habit`

```python
def add_habit(self, name: str, *, is_bool: bool | None = None) -> bool
```

Add a new habit to the database.

Args:

- `name` (`str`): Habit name.
- `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.

Returns:

- `bool`: `True` if successful, `False` otherwise.

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

- [`habit_id`](dashboard_widgets.g.md#%EF%B8%8F-method-habit_id) (`int`): Habit ID.
- `value` (`int`): Habit value.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `bool`: `True` if successful, `False` otherwise.

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
            logger.error("%s", f"Failed to add process habit record: habit_id={habit_id}, value={value}, date={date}")
        return result
```

</details>

### ⚙️ Method `count_habit_checkins_between`

```python
def count_habit_checkins_between(self, habit_id: int, date_from: str, date_to: str) -> int
```

Count days with value > 0 for a habit in an inclusive date range.

<details>
<summary>Code:</summary>

```python
def count_habit_checkins_between(self, habit_id: int, date_from: str, date_to: str) -> int:
        rows = self.get_rows(
            """
            SELECT COUNT(*)
            FROM process_habits
            WHERE _id_habit = :habit_id
              AND date BETWEEN :date_from AND :date_to
              AND value > 0
            """,
            {"habit_id": habit_id, "date_from": date_from, "date_to": date_to},
        )
        if rows and rows[0][0] is not None:
            return int(rows[0][0])
        return 0
```

</details>

### ⚙️ Method `delete_habit`

```python
def delete_habit(self, habit_id: int) -> bool
```

Delete a habit from the database.

Args:

- [`habit_id`](dashboard_widgets.g.md#%EF%B8%8F-method-habit_id) (`int`): Habit ID to delete.

Returns:

- `bool`: `True` if successful, `False` otherwise.

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

- `bool`: `True` if successful, `False` otherwise.

<details>
<summary>Code:</summary>

```python
def delete_process_habit_record(self, record_id: int) -> bool:
        query = "DELETE FROM process_habits WHERE _id = :id"
        return self.execute_simple_query(query, {"id": record_id})
```

</details>

### ⚙️ Method `ensure_habits_schema`

```python
def ensure_habits_schema(self) -> bool
```

Ensure the habits table has required columns for current app version.

Returns:

- `bool`: `True` when schema is compatible or successfully migrated.

<details>
<summary>Code:</summary>

```python
def ensure_habits_schema(self) -> bool:
        if not self.table_exists("habits"):
            return True

        try:
            cols = self.get_rows("PRAGMA table_info(habits)")
            existing = {str(row[1]) for row in cols if len(row) > 1 and row[1]}
            if "is_archived" not in existing:
                return self.execute_simple_query("ALTER TABLE habits ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0")
        except Exception:
            logger.exception("Failed to ensure habits schema")
            return False
        else:
            return True
```

</details>

### ⚙️ Method `get_all_habits`

```python
def get_all_habits(self) -> list[list[Any]]
```

Get all habits with their properties.

Returns:

- `list[list[Any]]`: List of habit records [\_id, name, is_bool, is_archived].

<details>
<summary>Code:</summary>

```python
def get_all_habits(self) -> list[list[Any]]:
        return self.get_rows("SELECT _id, name, is_bool, is_archived FROM habits")
```

</details>

### ⚙️ Method `get_all_process_habits_records`

```python
def get_all_process_habits_records(self) -> list[list[Any]]
```

Get all process habits records with habit names.

Returns:

- `list[list[Any]]`: List of process habits records [\_id, habit_name, value, date].

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

- `str | None`: Date string in YYYY-MM-DD format or `None` if no records.

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

### ⚙️ Method `get_habit_by_id`

```python
def get_habit_by_id(self, habit_id: int) -> list[Any] | None
```

Return one habit row ``[_id, name, is_bool, is_archived]`` or ``None``.

<details>
<summary>Code:</summary>

```python
def get_habit_by_id(self, habit_id: int) -> list[Any] | None:
        rows = self.get_rows(
            "SELECT _id, name, is_bool, is_archived FROM habits WHERE _id = :id",
            {"id": habit_id},
        )
        if rows:
            return list(rows[0])
        return None
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

### ⚙️ Method `get_habit_done_dates_between`

```python
def get_habit_done_dates_between(self, habit_id: int, date_from: str, date_to: str) -> list[str]
```

Return ISO dates with value > 0 for a habit in an inclusive range.

<details>
<summary>Code:</summary>

```python
def get_habit_done_dates_between(self, habit_id: int, date_from: str, date_to: str) -> list[str]:
        rows = self.get_rows(
            """
            SELECT date
            FROM process_habits
            WHERE _id_habit = :habit_id
              AND date BETWEEN :date_from AND :date_to
              AND value > 0
            ORDER BY date ASC
            """,
            {"habit_id": habit_id, "date_from": date_from, "date_to": date_to},
        )
        return [str(row[0]) for row in rows if row and row[0]]
```

</details>

### ⚙️ Method `get_habit_streak`

```python
def get_habit_streak(self, habit_id: int) -> int
```

Return consecutive completed days ending at today or yesterday.

If today is not completed yet, the streak may still continue from yesterday.
A gap of one or more missed days resets the streak to zero.

<details>
<summary>Code:</summary>

```python
def get_habit_streak(self, habit_id: int) -> int:
        rows = self.get_rows(
            """
            SELECT date
            FROM process_habits
            WHERE _id_habit = :habit_id AND value > 0 AND date IS NOT NULL
            ORDER BY date DESC
            """,
            {"habit_id": habit_id},
        )
        done: set[date] = set()
        for row in rows:
            parsed = _parse_iso_date(str(row[0]) if row and row[0] else "")
            if parsed is not None:
                done.add(parsed)

        if not done:
            return 0

        today = datetime.now(UTC).astimezone().date()
        cursor = today if today in done else today - timedelta(days=1)
        if cursor not in done:
            return 0

        streak = 0
        while cursor in done:
            streak += 1
            cursor -= timedelta(days=1)
        return streak
```

</details>

### ⚙️ Method `get_habit_total_checkins`

```python
def get_habit_total_checkins(self, habit_id: int) -> int
```

Count distinct days with value > 0 for a habit (all time).

<details>
<summary>Code:</summary>

```python
def get_habit_total_checkins(self, habit_id: int) -> int:
        rows = self.get_rows(
            """
            SELECT COUNT(DISTINCT date)
            FROM process_habits
            WHERE _id_habit = :habit_id AND value > 0 AND date IS NOT NULL
            """,
            {"habit_id": habit_id},
        )
        if rows and rows[0][0] is not None:
            return int(rows[0][0])
        return 0
```

</details>

### ⚙️ Method `get_habits`

```python
def get_habits(self, *, include_archived: bool = False) -> list[list[Any]]
```

Get habits with optional inclusion of archived ones.

<details>
<summary>Code:</summary>

```python
def get_habits(self, *, include_archived: bool = False) -> list[list[Any]]:
        if include_archived:
            return self.get_all_habits()
        return self.get_rows("SELECT _id, name, is_bool, is_archived FROM habits WHERE is_archived = 0")
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

### ⚙️ Method `get_limited_process_habits_records`

```python
def get_limited_process_habits_records(self, limit: int = 5000) -> list[list[Any]]
```

Get limited number of process habits records with habit names.

Args:

- `limit` (`int`): Maximum number of records to return. Defaults to `5000`.

Returns:

- `list[list[Any]]`: List of process habits records [\_id, habit_name, value, date].

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

### ⚙️ Method `is_habit_done_on_date`

```python
def is_habit_done_on_date(self, habit_id: int, date_str: str) -> bool
```

Return whether habit has value > 0 on ``date_str`` (YYYY-MM-DD).

<details>
<summary>Code:</summary>

```python
def is_habit_done_on_date(self, habit_id: int, date_str: str) -> bool:
        rows = self.get_rows(
            """
            SELECT value FROM process_habits
            WHERE _id_habit = :habit_id AND date = :date
            LIMIT 1
            """,
            {"habit_id": habit_id, "date": date_str},
        )
        if not rows or rows[0][0] is None:
            return False
        try:
            return int(rows[0][0]) > 0
        except (TypeError, ValueError):
            return False
```

</details>

### ⚙️ Method `set_habit_archived`

```python
def set_habit_archived(self, habit_id: int, *, is_archived: bool) -> bool
```

Archive/unarchive a habit by ID.

<details>
<summary>Code:</summary>

```python
def set_habit_archived(self, habit_id: int, *, is_archived: bool) -> bool:
        query = "UPDATE habits SET is_archived = :v WHERE _id = :id"
        return self.execute_simple_query(query, {"v": 1 if is_archived else 0, "id": habit_id})
```

</details>

### ⚙️ Method `toggle_habit_checkin`

```python
def toggle_habit_checkin(self, habit_id: int, date_str: str) -> bool
```

Toggle completion for habit on a date.

If a record with value > 0 exists, delete it (unchecked).
If a record with value <= 0 exists, set value to 1.
If no record exists, insert value 1.

<details>
<summary>Code:</summary>

```python
def toggle_habit_checkin(self, habit_id: int, date_str: str) -> bool:
        rows = self.get_rows(
            """
            SELECT _id, value FROM process_habits
            WHERE _id_habit = :habit_id AND date = :date
            ORDER BY _id DESC LIMIT 1
            """,
            {"habit_id": habit_id, "date": date_str},
        )
        if not rows:
            return self.add_process_habit_record(habit_id, 1, date_str)

        record_id = int(rows[0][0])
        try:
            value = int(rows[0][1])
        except (TypeError, ValueError):
            value = 0

        if value > 0:
            return self.delete_process_habit_record(record_id)
        return self.update_process_habit_record(record_id, habit_id, 1, date_str)
```

</details>

### ⚙️ Method `update_habit`

```python
def update_habit(self, habit_id: int, name: str, *, is_bool: bool | None = None, is_archived: bool | None = None) -> bool
```

Update an existing habit.

Args:

- [`habit_id`](dashboard_widgets.g.md#%EF%B8%8F-method-habit_id) (`int`): Habit ID.
- `name` (`str`): Habit name.
- `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.
- `is_archived` (`bool | None`): Whether habit is archived. Defaults to `None` (do not change).

Returns:

- `bool`: `True` if successful, `False` otherwise.

<details>
<summary>Code:</summary>

```python
def update_habit(
        self,
        habit_id: int,
        name: str,
        *,
        is_bool: bool | None = None,
        is_archived: bool | None = None,
    ) -> bool:
        query = "UPDATE habits SET name = :n, is_bool = :is_bool WHERE _id = :id"
        params = {
            "n": name,
            "is_bool": 1 if is_bool is True else (0 if is_bool is False else None),
            "id": habit_id,
        }
        if is_archived is not None:
            query = "UPDATE habits SET name = :n, is_bool = :is_bool, is_archived = :is_archived WHERE _id = :id"
            params["is_archived"] = 1 if is_archived else 0
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
- [`habit_id`](dashboard_widgets.g.md#%EF%B8%8F-method-habit_id) (`int`): Habit ID.
- `value` (`int`): Habit value.
- `date` (`str`): Date in YYYY-MM-DD format.

Returns:

- `bool`: `True` if successful, `False` otherwise.

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
