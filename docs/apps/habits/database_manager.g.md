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
  - [⚙️ Method `get_habit_value_on_date`](#%EF%B8%8F-method-get_habit_value_on_date)
  - [⚙️ Method `get_habit_values_between`](#%EF%B8%8F-method-get_habit_values_between)
  - [⚙️ Method `get_habit_years`](#%EF%B8%8F-method-get_habit_years)
  - [⚙️ Method `get_habits`](#%EF%B8%8F-method-get_habits)
  - [⚙️ Method `get_habits_years`](#%EF%B8%8F-method-get_habits_years)
  - [⚙️ Method `get_limited_process_habits_records`](#%EF%B8%8F-method-get_limited_process_habits_records)
  - [⚙️ Method `is_habit_done_on_date`](#%EF%B8%8F-method-is_habit_done_on_date)
  - [⚙️ Method `reorder_habits`](#%EF%B8%8F-method-reorder_habits)
  - [⚙️ Method `set_habit_archived`](#%EF%B8%8F-method-set_habit_archived)
  - [⚙️ Method `set_habit_checkin`](#%EF%B8%8F-method-set_habit_checkin)
  - [⚙️ Method `toggle_habit_checkin`](#%EF%B8%8F-method-toggle_habit_checkin)
  - [⚙️ Method `update_habit`](#%EF%B8%8F-method-update_habit)
  - [⚙️ Method `update_process_habit_record`](#%EF%B8%8F-method-update_process_habit_record)
  - [⚙️ Method `upsert_habit_checkins`](#%EF%B8%8F-method-upsert_habit_checkins)

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

    def add_habit(self, name: str, *, is_bool: bool | None = None, emoji: str = "") -> bool:
        """Add a new habit to the database.

        Args:

        - `name` (`str`): Habit name.
        - `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.
        - `emoji` (`str`): Habit emoji. Defaults to `""` (assigned after insert when empty).

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        cleaned_emoji = (emoji or "").strip()
        query = "INSERT INTO habits (name, is_bool, emoji, sort_order) VALUES (:name, :is_bool, :emoji, :sort_order)"
        params = {
            "name": name,
            "is_bool": 1 if is_bool is True else (0 if is_bool is False else None),
            "emoji": cleaned_emoji,
            "sort_order": self._next_habit_sort_order(),
        }
        if not self.execute_simple_query(query, params):
            return False
        if cleaned_emoji:
            return True
        rows = self.get_rows(
            "SELECT _id FROM habits WHERE name = :name ORDER BY _id DESC LIMIT 1",
            {"name": name},
        )
        if not rows or rows[0][0] is None:
            return True
        habit_id = int(rows[0][0])
        return self.execute_simple_query(
            "UPDATE habits SET emoji = :emoji WHERE _id = :id",
            {"emoji": default_habit_emoji(habit_id), "id": habit_id},
        )

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
            if "is_archived" not in existing and not self.execute_simple_query(
                "ALTER TABLE habits ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0"
            ):
                return False
            if "emoji" not in existing and not self.execute_simple_query(
                "ALTER TABLE habits ADD COLUMN emoji TEXT NOT NULL DEFAULT ''"
            ):
                return False
            if "sort_order" not in existing:
                if not self.execute_simple_query("ALTER TABLE habits ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"):
                    return False
                if not self._backfill_habit_sort_orders():
                    return False
            return self._backfill_habit_emojis()
        except Exception:
            logger.exception("Failed to ensure habits schema")
            return False

    def get_all_habits(self) -> list[list[Any]]:
        r"""Get all habits with their properties.

        Returns:

        - `list[list[Any]]`: List of habit records [\_id, name, is_bool, is_archived, emoji].

        """
        return self.get_rows(f"SELECT {_HABIT_COLUMNS} FROM habits ORDER BY {_HABIT_ORDER_BY}")

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
        """Return one habit row ``[_id, name, is_bool, is_archived, emoji]`` or ``None``."""
        rows = self.get_rows(
            f"SELECT {_HABIT_COLUMNS} FROM habits WHERE _id = :id",
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

    def get_habit_value_on_date(self, habit_id: int, date_str: str) -> int | None:
        """Return stored value for habit on ``date_str``, or ``None`` if no record."""
        rows = self.get_rows(
            """
            SELECT value FROM process_habits
            WHERE _id_habit = :habit_id AND date = :date
            ORDER BY _id DESC
            LIMIT 1
            """,
            {"habit_id": habit_id, "date": date_str},
        )
        if not rows or rows[0][0] is None:
            return None
        try:
            return int(rows[0][0])
        except (TypeError, ValueError):
            return None

    def get_habit_values_between(self, habit_id: int, date_from: str, date_to: str) -> dict[str, int]:
        """Return date → value map for a habit in an inclusive range.

        Dates without a `process_habits` row are omitted. If several rows exist
        for one date, the latest `_id` wins.

        """
        rows = self.get_rows(
            """
            SELECT date, value
            FROM process_habits
            WHERE _id_habit = :habit_id
              AND date BETWEEN :date_from AND :date_to
            ORDER BY date ASC, _id ASC
            """,
            {"habit_id": habit_id, "date_from": date_from, "date_to": date_to},
        )
        result: dict[str, int] = {}
        for row in rows:
            if not row or row[0] is None or row[1] is None:
                continue
            try:
                result[str(row[0])] = int(row[1])
            except (TypeError, ValueError):
                continue
        return result

    def get_habit_years(self, habit_id: int) -> list[int]:
        """Return distinct check-in years for one habit, newest first.

        Args:

        - `habit_id` (`int`): Habit primary key.

        Returns:

        - `list[int]`: Years from `process_habits` for this habit.

        """
        rows = self.get_rows(
            """
            SELECT DISTINCT CAST(strftime('%Y', date) AS INTEGER) AS year
            FROM process_habits
            WHERE _id_habit = :habit_id AND date IS NOT NULL
            ORDER BY year DESC
            """,
            {"habit_id": habit_id},
        )
        return [int(row[0]) for row in rows if row[0] is not None]

    def get_habits(self, *, include_archived: bool = False) -> list[list[Any]]:
        """Get habits with optional inclusion of archived ones."""
        if include_archived:
            return self.get_all_habits()
        return self.get_rows(f"SELECT {_HABIT_COLUMNS} FROM habits WHERE is_archived = 0 ORDER BY {_HABIT_ORDER_BY}")

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

    def reorder_habits(self, habit_ids: Sequence[int]) -> bool:
        """Save dashboard list order as `sort_order` values 0, 1, … for `habit_ids`.

        Args:

        - `habit_ids` (`Sequence[int]`): Habit primary keys in the desired display
          order. Archived habits not listed keep their current `sort_order`.

        Returns:

        - `bool`: `True` if every update succeeded.

        """
        for index, habit_id in enumerate(habit_ids):
            if not self.execute_simple_query(
                "UPDATE habits SET sort_order = :ord WHERE _id = :id",
                {"ord": index, "id": habit_id},
            ):
                return False
        return True

    def set_habit_archived(self, habit_id: int, *, is_archived: bool) -> bool:
        """Archive/unarchive a habit by ID."""
        query = "UPDATE habits SET is_archived = :v WHERE _id = :id"
        return self.execute_simple_query(query, {"v": 1 if is_archived else 0, "id": habit_id})

    def set_habit_checkin(self, habit_id: int, date_str: str, value: int | None) -> bool:
        """Set or clear the process-habit value for a habit on a date.

        `None` deletes all records for that day. A numeric value updates the
        latest row or inserts a new one.

        """
        rows = self.get_rows(
            """
            SELECT _id FROM process_habits
            WHERE _id_habit = :habit_id AND date = :date
            ORDER BY _id DESC
            """,
            {"habit_id": habit_id, "date": date_str},
        )
        record_ids = [int(row[0]) for row in rows if row and row[0] is not None]
        if value is None:
            return all(self.delete_process_habit_record(record_id) for record_id in record_ids)

        if not record_ids:
            return self.add_process_habit_record(habit_id, value, date_str)

        extras_ok = all(self.delete_process_habit_record(record_id) for record_id in record_ids[1:])
        return extras_ok and self.update_process_habit_record(record_ids[0], habit_id, value, date_str)

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
        emoji: str | None = None,
    ) -> bool:
        """Update an existing habit.

        Args:

        - `habit_id` (`int`): Habit ID.
        - `name` (`str`): Habit name.
        - `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.
        - `is_archived` (`bool | None`): Whether habit is archived. Defaults to `None` (do not change).
        - `emoji` (`str | None`): Habit emoji. Defaults to `None` (do not change).

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        fields = ["name = :n", "is_bool = :is_bool"]
        params: dict[str, Any] = {
            "n": name,
            "is_bool": 1 if is_bool is True else (0 if is_bool is False else None),
            "id": habit_id,
        }
        if is_archived is not None:
            fields.append("is_archived = :is_archived")
            params["is_archived"] = 1 if is_archived else 0
        if emoji is not None:
            fields.append("emoji = :emoji")
            params["emoji"] = normalize_habit_emoji(emoji, habit_id=habit_id)
        query = f"UPDATE habits SET {', '.join(fields)} WHERE _id = :id"
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

    def upsert_habit_checkins(self, records: list[tuple[int, str, int]]) -> int:
        """Set many habit/date values in one SQLite transaction.

        The latest value for each `(habit_id, date)` wins. Existing latest rows
        are updated, extra rows for those days are deleted, and missing days
        are inserted with one multi-row `INSERT` per chunk.

        Args:

        - `records` (`list[tuple[int, str, int]]`): `(habit_id, YYYY-MM-DD, value)`.

        Returns:

        - `int`: Number of unique habit/date pairs written.

        """
        merged: dict[tuple[int, str], int] = {}
        for habit_id, date_str, value in records:
            merged[(int(habit_id), str(date_str))] = int(value)
        if not merged:
            return 0

        habit_ids = sorted({habit_id for habit_id, _date in merged})
        id_params = {f"hid{index}": habit_id for index, habit_id in enumerate(habit_ids)}
        id_placeholders = ", ".join(f":hid{index}" for index in range(len(habit_ids)))
        rows = self.get_rows(
            f"""
            SELECT _id, _id_habit, date
            FROM process_habits
            WHERE _id_habit IN ({id_placeholders})
            ORDER BY _id ASC
            """,
            id_params,
        )
        latest: dict[tuple[int, str], int] = {}
        extra_ids: list[int] = []
        for row in rows:
            if not row or row[0] is None or row[1] is None or not row[2]:
                continue
            key = (int(row[1]), str(row[2]))
            if key not in merged:
                continue
            record_id = int(row[0])
            previous = latest.get(key)
            if previous is not None:
                extra_ids.append(previous)
            latest[key] = record_id

        updates = [(latest[key], value) for key, value in merged.items() if key in latest]
        inserts = [
            (habit_id, value, date_str)
            for (habit_id, date_str), value in merged.items()
            if (habit_id, date_str) not in latest
        ]

        with self.sql_transaction():
            for chunk in _chunks(extra_ids, _CHECKIN_SQL_CHUNK):
                params = {f"id{index}": record_id for index, record_id in enumerate(chunk)}
                placeholders = ", ".join(f":id{index}" for index in range(len(chunk)))
                if not self.execute_simple_query(f"DELETE FROM process_habits WHERE _id IN ({placeholders})", params):
                    msg = "Failed to delete extra process_habits rows during batch upsert"
                    raise RuntimeError(msg)
            for chunk in _chunks(updates, _CHECKIN_SQL_CHUNK):
                params: dict[str, Any] = {}
                cases: list[str] = []
                ids: list[str] = []
                for index, (record_id, value) in enumerate(chunk):
                    params[f"id{index}"] = record_id
                    params[f"v{index}"] = value
                    cases.append(f"WHEN :id{index} THEN :v{index}")
                    ids.append(f":id{index}")
                query = (
                    "UPDATE process_habits SET value = CASE _id "
                    + " ".join(cases)
                    + " END WHERE _id IN ("
                    + ", ".join(ids)
                    + ")"
                )
                if not self.execute_simple_query(query, params):
                    msg = "Failed to update process_habits rows during batch upsert"
                    raise RuntimeError(msg)
            for chunk in _chunks(inserts, _CHECKIN_SQL_CHUNK):
                params = {}
                values_sql: list[str] = []
                for index, (habit_id, value, date_str) in enumerate(chunk):
                    params[f"h{index}"] = habit_id
                    params[f"v{index}"] = value
                    params[f"d{index}"] = date_str
                    values_sql.append(f"(:h{index}, :v{index}, :d{index})")
                query = "INSERT INTO process_habits (_id_habit, value, date) VALUES " + ", ".join(values_sql)
                if not self.execute_simple_query(query, params):
                    msg = "Failed to insert process_habits rows during batch upsert"
                    raise RuntimeError(msg)
        return len(merged)

    def _backfill_habit_emojis(self) -> bool:
        """Assign preset emoji to habits that still have an empty emoji value."""
        rows = self.get_rows("SELECT _id FROM habits WHERE emoji IS NULL OR TRIM(emoji) = ''")
        for row in rows:
            if not row or row[0] is None:
                continue
            habit_id = int(row[0])
            if not self.execute_simple_query(
                "UPDATE habits SET emoji = :emoji WHERE _id = :id",
                {"emoji": default_habit_emoji(habit_id), "id": habit_id},
            ):
                return False
        return True

    def _backfill_habit_sort_orders(self) -> bool:
        """Copy `_id` into `sort_order` so existing habits keep insertion order."""
        return self.execute_simple_query("UPDATE habits SET sort_order = _id")

    def _next_habit_sort_order(self) -> int:
        """Return the next `sort_order` so a new habit is appended."""
        rows = self.get_rows("SELECT COALESCE(MAX(sort_order), -1) FROM habits")
        if not rows or rows[0][0] is None:
            return 0
        return int(rows[0][0]) + 1
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
def add_habit(self, name: str, *, is_bool: bool | None = None, emoji: str = '') -> bool
```

Add a new habit to the database.

Args:

- `name` (`str`): Habit name.
- `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.
- `emoji` (`str`): Habit emoji. Defaults to `""` (assigned after insert when empty).

Returns:

- `bool`: `True` if successful, `False` otherwise.

<details>
<summary>Code:</summary>

```python
def add_habit(self, name: str, *, is_bool: bool | None = None, emoji: str = "") -> bool:
        cleaned_emoji = (emoji or "").strip()
        query = "INSERT INTO habits (name, is_bool, emoji, sort_order) VALUES (:name, :is_bool, :emoji, :sort_order)"
        params = {
            "name": name,
            "is_bool": 1 if is_bool is True else (0 if is_bool is False else None),
            "emoji": cleaned_emoji,
            "sort_order": self._next_habit_sort_order(),
        }
        if not self.execute_simple_query(query, params):
            return False
        if cleaned_emoji:
            return True
        rows = self.get_rows(
            "SELECT _id FROM habits WHERE name = :name ORDER BY _id DESC LIMIT 1",
            {"name": name},
        )
        if not rows or rows[0][0] is None:
            return True
        habit_id = int(rows[0][0])
        return self.execute_simple_query(
            "UPDATE habits SET emoji = :emoji WHERE _id = :id",
            {"emoji": default_habit_emoji(habit_id), "id": habit_id},
        )
```

</details>

### ⚙️ Method `add_process_habit_record`

```python
def add_process_habit_record(self, habit_id: int, value: int, date: str) -> bool
```

Add a new process habit record.

Args:

- [`habit_id`](dashboard_widgets.g.md#%EF%B8%8F-method-habit_id) (`int`): Habit ID.
- [`value`](dashboard_widgets.g.md#%EF%B8%8F-method-value) (`int`): Habit value.
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
            if "is_archived" not in existing and not self.execute_simple_query(
                "ALTER TABLE habits ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0"
            ):
                return False
            if "emoji" not in existing and not self.execute_simple_query(
                "ALTER TABLE habits ADD COLUMN emoji TEXT NOT NULL DEFAULT ''"
            ):
                return False
            if "sort_order" not in existing:
                if not self.execute_simple_query("ALTER TABLE habits ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"):
                    return False
                if not self._backfill_habit_sort_orders():
                    return False
            return self._backfill_habit_emojis()
        except Exception:
            logger.exception("Failed to ensure habits schema")
            return False
```

</details>

### ⚙️ Method `get_all_habits`

```python
def get_all_habits(self) -> list[list[Any]]
```

Get all habits with their properties.

Returns:

- `list[list[Any]]`: List of habit records [\_id, name, is_bool, is_archived, emoji].

<details>
<summary>Code:</summary>

```python
def get_all_habits(self) -> list[list[Any]]:
        return self.get_rows(f"SELECT {_HABIT_COLUMNS} FROM habits ORDER BY {_HABIT_ORDER_BY}")
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

- [`habit_name`](habit_edit_dialog.g.md#%EF%B8%8F-method-habit_name) (`str | None`): Filter by habit name. Defaults to `None`.
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

Return one habit row ``[_id, name, is_bool, is_archived, emoji]`` or ``None``.

<details>
<summary>Code:</summary>

```python
def get_habit_by_id(self, habit_id: int) -> list[Any] | None:
        rows = self.get_rows(
            f"SELECT {_HABIT_COLUMNS} FROM habits WHERE _id = :id",
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

- [`habit_name`](habit_edit_dialog.g.md#%EF%B8%8F-method-habit_name) (`str`): Habit name.
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

### ⚙️ Method `get_habit_value_on_date`

```python
def get_habit_value_on_date(self, habit_id: int, date_str: str) -> int | None
```

Return stored value for habit on ``date_str``, or ``None`` if no record.

<details>
<summary>Code:</summary>

```python
def get_habit_value_on_date(self, habit_id: int, date_str: str) -> int | None:
        rows = self.get_rows(
            """
            SELECT value FROM process_habits
            WHERE _id_habit = :habit_id AND date = :date
            ORDER BY _id DESC
            LIMIT 1
            """,
            {"habit_id": habit_id, "date": date_str},
        )
        if not rows or rows[0][0] is None:
            return None
        try:
            return int(rows[0][0])
        except (TypeError, ValueError):
            return None
```

</details>

### ⚙️ Method `get_habit_values_between`

```python
def get_habit_values_between(self, habit_id: int, date_from: str, date_to: str) -> dict[str, int]
```

Return date → value map for a habit in an inclusive range.

Dates without a `process_habits` row are omitted. If several rows exist
for one date, the latest `_id` wins.

<details>
<summary>Code:</summary>

```python
def get_habit_values_between(self, habit_id: int, date_from: str, date_to: str) -> dict[str, int]:
        rows = self.get_rows(
            """
            SELECT date, value
            FROM process_habits
            WHERE _id_habit = :habit_id
              AND date BETWEEN :date_from AND :date_to
            ORDER BY date ASC, _id ASC
            """,
            {"habit_id": habit_id, "date_from": date_from, "date_to": date_to},
        )
        result: dict[str, int] = {}
        for row in rows:
            if not row or row[0] is None or row[1] is None:
                continue
            try:
                result[str(row[0])] = int(row[1])
            except (TypeError, ValueError):
                continue
        return result
```

</details>

### ⚙️ Method `get_habit_years`

```python
def get_habit_years(self, habit_id: int) -> list[int]
```

Return distinct check-in years for one habit, newest first.

Args:

- [`habit_id`](dashboard_widgets.g.md#%EF%B8%8F-method-habit_id) (`int`): Habit primary key.

Returns:

- `list[int]`: Years from `process_habits` for this habit.

<details>
<summary>Code:</summary>

```python
def get_habit_years(self, habit_id: int) -> list[int]:
        rows = self.get_rows(
            """
            SELECT DISTINCT CAST(strftime('%Y', date) AS INTEGER) AS year
            FROM process_habits
            WHERE _id_habit = :habit_id AND date IS NOT NULL
            ORDER BY year DESC
            """,
            {"habit_id": habit_id},
        )
        return [int(row[0]) for row in rows if row[0] is not None]
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
        return self.get_rows(f"SELECT {_HABIT_COLUMNS} FROM habits WHERE is_archived = 0 ORDER BY {_HABIT_ORDER_BY}")
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

### ⚙️ Method `reorder_habits`

```python
def reorder_habits(self, habit_ids: Sequence[int]) -> bool
```

Save dashboard list order as `sort_order` values 0, 1, … for `habit_ids`.

Args:

- `habit_ids` (`Sequence[int]`): Habit primary keys in the desired display
  order. Archived habits not listed keep their current `sort_order`.

Returns:

- `bool`: `True` if every update succeeded.

<details>
<summary>Code:</summary>

```python
def reorder_habits(self, habit_ids: Sequence[int]) -> bool:
        for index, habit_id in enumerate(habit_ids):
            if not self.execute_simple_query(
                "UPDATE habits SET sort_order = :ord WHERE _id = :id",
                {"ord": index, "id": habit_id},
            ):
                return False
        return True
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

### ⚙️ Method `set_habit_checkin`

```python
def set_habit_checkin(self, habit_id: int, date_str: str, value: int | None) -> bool
```

Set or clear the process-habit value for a habit on a date.

`None` deletes all records for that day. A numeric value updates the
latest row or inserts a new one.

<details>
<summary>Code:</summary>

```python
def set_habit_checkin(self, habit_id: int, date_str: str, value: int | None) -> bool:
        rows = self.get_rows(
            """
            SELECT _id FROM process_habits
            WHERE _id_habit = :habit_id AND date = :date
            ORDER BY _id DESC
            """,
            {"habit_id": habit_id, "date": date_str},
        )
        record_ids = [int(row[0]) for row in rows if row and row[0] is not None]
        if value is None:
            return all(self.delete_process_habit_record(record_id) for record_id in record_ids)

        if not record_ids:
            return self.add_process_habit_record(habit_id, value, date_str)

        extras_ok = all(self.delete_process_habit_record(record_id) for record_id in record_ids[1:])
        return extras_ok and self.update_process_habit_record(record_ids[0], habit_id, value, date_str)
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
def update_habit(self, habit_id: int, name: str, *, is_bool: bool | None = None, is_archived: bool | None = None, emoji: str | None = None) -> bool
```

Update an existing habit.

Args:

- [`habit_id`](dashboard_widgets.g.md#%EF%B8%8F-method-habit_id) (`int`): Habit ID.
- `name` (`str`): Habit name.
- `is_bool` (`bool | None`): Whether habit accepts only 0 or 1 values. Defaults to `None`.
- `is_archived` (`bool | None`): Whether habit is archived. Defaults to `None` (do not change).
- `emoji` (`str | None`): Habit emoji. Defaults to `None` (do not change).

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
        emoji: str | None = None,
    ) -> bool:
        fields = ["name = :n", "is_bool = :is_bool"]
        params: dict[str, Any] = {
            "n": name,
            "is_bool": 1 if is_bool is True else (0 if is_bool is False else None),
            "id": habit_id,
        }
        if is_archived is not None:
            fields.append("is_archived = :is_archived")
            params["is_archived"] = 1 if is_archived else 0
        if emoji is not None:
            fields.append("emoji = :emoji")
            params["emoji"] = normalize_habit_emoji(emoji, habit_id=habit_id)
        query = f"UPDATE habits SET {', '.join(fields)} WHERE _id = :id"
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
- [`value`](dashboard_widgets.g.md#%EF%B8%8F-method-value) (`int`): Habit value.
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

### ⚙️ Method `upsert_habit_checkins`

```python
def upsert_habit_checkins(self, records: list[tuple[int, str, int]]) -> int
```

Set many habit/date values in one SQLite transaction.

The latest value for each `(habit_id, date)` wins. Existing latest rows
are updated, extra rows for those days are deleted, and missing days
are inserted with one multi-row `INSERT` per chunk.

Args:

- `records` (`list[tuple[int, str, int]]`): `(habit_id, YYYY-MM-DD, value)`.

Returns:

- `int`: Number of unique habit/date pairs written.

<details>
<summary>Code:</summary>

```python
def upsert_habit_checkins(self, records: list[tuple[int, str, int]]) -> int:
        merged: dict[tuple[int, str], int] = {}
        for habit_id, date_str, value in records:
            merged[(int(habit_id), str(date_str))] = int(value)
        if not merged:
            return 0

        habit_ids = sorted({habit_id for habit_id, _date in merged})
        id_params = {f"hid{index}": habit_id for index, habit_id in enumerate(habit_ids)}
        id_placeholders = ", ".join(f":hid{index}" for index in range(len(habit_ids)))
        rows = self.get_rows(
            f"""
            SELECT _id, _id_habit, date
            FROM process_habits
            WHERE _id_habit IN ({id_placeholders})
            ORDER BY _id ASC
            """,
            id_params,
        )
        latest: dict[tuple[int, str], int] = {}
        extra_ids: list[int] = []
        for row in rows:
            if not row or row[0] is None or row[1] is None or not row[2]:
                continue
            key = (int(row[1]), str(row[2]))
            if key not in merged:
                continue
            record_id = int(row[0])
            previous = latest.get(key)
            if previous is not None:
                extra_ids.append(previous)
            latest[key] = record_id

        updates = [(latest[key], value) for key, value in merged.items() if key in latest]
        inserts = [
            (habit_id, value, date_str)
            for (habit_id, date_str), value in merged.items()
            if (habit_id, date_str) not in latest
        ]

        with self.sql_transaction():
            for chunk in _chunks(extra_ids, _CHECKIN_SQL_CHUNK):
                params = {f"id{index}": record_id for index, record_id in enumerate(chunk)}
                placeholders = ", ".join(f":id{index}" for index in range(len(chunk)))
                if not self.execute_simple_query(f"DELETE FROM process_habits WHERE _id IN ({placeholders})", params):
                    msg = "Failed to delete extra process_habits rows during batch upsert"
                    raise RuntimeError(msg)
            for chunk in _chunks(updates, _CHECKIN_SQL_CHUNK):
                params: dict[str, Any] = {}
                cases: list[str] = []
                ids: list[str] = []
                for index, (record_id, value) in enumerate(chunk):
                    params[f"id{index}"] = record_id
                    params[f"v{index}"] = value
                    cases.append(f"WHEN :id{index} THEN :v{index}")
                    ids.append(f":id{index}")
                query = (
                    "UPDATE process_habits SET value = CASE _id "
                    + " ".join(cases)
                    + " END WHERE _id IN ("
                    + ", ".join(ids)
                    + ")"
                )
                if not self.execute_simple_query(query, params):
                    msg = "Failed to update process_habits rows during batch upsert"
                    raise RuntimeError(msg)
            for chunk in _chunks(inserts, _CHECKIN_SQL_CHUNK):
                params = {}
                values_sql: list[str] = []
                for index, (habit_id, value, date_str) in enumerate(chunk):
                    params[f"h{index}"] = habit_id
                    params[f"v{index}"] = value
                    params[f"d{index}"] = date_str
                    values_sql.append(f"(:h{index}, :v{index}, :d{index})")
                query = "INSERT INTO process_habits (_id_habit, value, date) VALUES " + ", ".join(values_sql)
                if not self.execute_simple_query(query, params):
                    msg = "Failed to insert process_habits rows during batch upsert"
                    raise RuntimeError(msg)
        return len(merged)
```

</details>
