"""Utility for working with a local SQLite database that stores fitness-related information."""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, NoReturn

from harrix_swiss_knife.apps.common.qt_database_manager_base import QtSqliteDatabaseManagerBase
from harrix_swiss_knife.apps.fitness.dumbbell_weight_types import (
    DUMBBELL_WEIGHT_TEMPLATE_EXERCISE,
    WeightTypeSpec,
    is_dumbbell_exercise,
)
from harrix_swiss_knife.apps.fitness.exercise_favorites import prefer_favorite_names

logger = logging.getLogger(__name__)


class DatabaseManager(QtSqliteDatabaseManagerBase):
    """Manage the connection and operations for a fitness tracking database.

    Attributes:

    - `db` (`QSqlDatabase | None`): A live connection object opened on an SQLite database file.
    - `connection_name` (`str`): Unique name for this database connection.

    """

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in `db_filename`.

        Args:

        - `db_filename` (`str`): The path to the target database file.

        Raises:

        - `ConnectionError`: If the underlying Qt driver fails to open the database.

        """
        super().__init__(prefix="fitness_db", db_filename=db_filename)
        self._ensure_name_local_columns()

    def add_exercise(
        self,
        name: str,
        unit: str,
        *,
        is_type_required: bool,
        calories_per_unit: float = 0.0,
        name_local: str = "",
        is_favorite: bool = False,
    ) -> bool:
        """Add a new exercise to the database.

        Args:

        - `name` (`str`): Exercise name.
        - `unit` (`str`): Unit of measurement.
        - `is_type_required` (`bool`): Whether exercise type is required.
        - `calories_per_unit` (`float`): Calories burned per unit. Defaults to `0.0`.
        - `name_local` (`str`): Local-language exercise name. Defaults to `""`.
        - `is_favorite` (`bool`): Whether the exercise is pinned as a favorite. Defaults to `False`.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = (
            "INSERT INTO exercises (name, unit, is_type_required, calories_per_unit, name_local, is_favorite) "
            "VALUES (:name, :unit, :is_type_required, :calories_per_unit, :name_local, :is_favorite)"
        )
        params = {
            "name": name,
            "unit": unit,
            "is_type_required": 1 if is_type_required else 0,
            "calories_per_unit": calories_per_unit,
            "name_local": name_local or None,
            "is_favorite": 1 if is_favorite else 0,
        }
        return self.execute_simple_query(query, params)

    def add_exercise_type(
        self,
        exercise_id: int,
        type_name: str,
        calories_modifier: float = 1.0,
        name_local: str = "",
    ) -> bool:
        """Add a new exercise type.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `type_name` (`str`): Type name.
        - `calories_modifier` (`float`): Calories modifier for this type. Defaults to `1.0`.
        - `name_local` (`str`): Local-language type name. Defaults to `""`.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = (
            "INSERT INTO types (_id_exercises, type, calories_modifier, name_local) "
            "VALUES (:ex, :tp, :calories_modifier, :name_local)"
        )
        return self.execute_simple_query(
            query,
            {
                "ex": exercise_id,
                "tp": type_name,
                "calories_modifier": calories_modifier,
                "name_local": name_local or None,
            },
        )

    def add_process_record(self, exercise_id: int, type_id: int, value: str, date: str) -> bool:
        """Add a new process record.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `type_id` (`int`): Type ID (-1 for no type).
        - `value` (`str`): Exercise value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

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
            logger.error(
                "%s",
                f"Failed to add process record: exercise_id={exercise_id}, "
                f"type_id={type_id}, value={value}, date={date}",
            )
        return result

    def add_process_record_returning_id(self, exercise_id: int, type_id: int, value: str, date: str) -> int | None:
        """Insert a process row and return its `_id`."""
        if not self.add_process_record(exercise_id, type_id, value, date):
            return None
        rows = self.get_rows("SELECT last_insert_rowid()")
        if not rows or rows[0][0] is None:
            return None
        return int(rows[0][0])

    def add_weight_record(self, value: float, date: str) -> bool:
        """Add a new weight record.

        Args:

        - `value` (`float`): Weight value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = "INSERT INTO weight (value, date) VALUES (:val, :dt)"
        return self.execute_simple_query(query, {"val": value, "dt": date})

    def check_exercise_exists(self, exercise_id: int) -> bool:
        """Check if exercise exists by ID.

        Args:

        - `exercise_id` (`int`): Exercise ID to check.

        Returns:

        - `bool`: `True` if exercise exists, `False` otherwise.

        """
        rows = self.get_rows("SELECT 1 FROM exercises WHERE _id = :id LIMIT 1", {"id": exercise_id})
        return len(rows) > 0

    def count_process_records_for_exercise(self, exercise_id: int) -> int:
        """Count completed exercise records linked to an exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `int`: Number of related `process` rows.

        """
        rows = self.get_rows(
            "SELECT COUNT(*) FROM process WHERE _id_exercises = :id",
            {"id": exercise_id},
        )
        return int(rows[0][0]) if rows and rows[0][0] is not None else 0

    def count_process_records_for_type(self, type_id: int) -> int:
        """Count completed exercise records linked to an exercise type.

        Args:

        - `type_id` (`int`): Type ID.

        Returns:

        - `int`: Number of related `process` rows.

        """
        rows = self.get_rows(
            "SELECT COUNT(*) FROM process WHERE _id_types = :id",
            {"id": type_id},
        )
        return int(rows[0][0]) if rows and rows[0][0] is not None else 0

    def count_process_records_for_type_name(self, type_name: str) -> int:
        """Count set records whose type name matches `type_name`.

        Args:

        - `type_name` (`str`): Exercise type name, compared case-insensitively.

        Returns:

        - `int`: Number of related `process` rows.

        """
        rows = self.get_rows(
            """
            SELECT COUNT(*)
            FROM process p
            INNER JOIN types t ON t._id = p._id_types
            WHERE LOWER(TRIM(t.type)) = LOWER(TRIM(:tp))
            """,
            {"tp": type_name},
        )
        return int(rows[0][0]) if rows and rows[0][0] is not None else 0

    def delete_exercise(self, exercise_id: int) -> bool:
        """Delete an exercise and related process records and types.

        Args:

        - `exercise_id` (`int`): Exercise ID to delete.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        if not self.delete_process_records_for_exercise(exercise_id):
            return False
        if not self.delete_types_for_exercise(exercise_id):
            return False
        return self.execute_simple_query("DELETE FROM exercises WHERE _id = :id", {"id": exercise_id})

    def delete_exercise_type(self, type_id: int) -> bool:
        """Delete an exercise type and related process records.

        Args:

        - `type_id` (`int`): Type ID to delete.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        if not self.delete_process_records_for_type(type_id):
            return False
        return self.execute_simple_query("DELETE FROM types WHERE _id = :id", {"id": type_id})

    def delete_process_record(self, record_id: int) -> bool:
        """Delete a process record.

        Args:

        - `record_id` (`int`): Record ID to delete.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = "DELETE FROM process WHERE _id = :id"
        return self.execute_simple_query(query, {"id": record_id})

    def delete_process_records_for_exercise(self, exercise_id: int) -> bool:
        """Delete all process records for an exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        return self.execute_simple_query(
            "DELETE FROM process WHERE _id_exercises = :id",
            {"id": exercise_id},
        )

    def delete_process_records_for_type(self, type_id: int) -> bool:
        """Delete all process records for an exercise type.

        Args:

        - `type_id` (`int`): Type ID.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        return self.execute_simple_query(
            "DELETE FROM process WHERE _id_types = :id",
            {"id": type_id},
        )

    def delete_types_by_name(self, type_name: str) -> bool:
        """Delete every type row whose name matches `type_name`.

        Args:

        - `type_name` (`str`): Type name, compared case-insensitively.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        return self.execute_simple_query(
            "DELETE FROM types WHERE LOWER(TRIM(type)) = LOWER(TRIM(:tp))",
            {"tp": type_name},
        )

    def delete_types_for_exercise(self, exercise_id: int) -> bool:
        """Delete all types for an exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        return self.execute_simple_query(
            "DELETE FROM types WHERE _id_exercises = :id",
            {"id": exercise_id},
        )

    def delete_weight_record(self, record_id: int) -> bool:
        """Delete a weight record.

        Args:

        - `record_id` (`int`): Record ID to delete.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = "DELETE FROM weight WHERE _id = :id"
        return self.execute_simple_query(query, {"id": record_id})

    def delete_workout(self, workout_id: int) -> bool:
        """Delete a workout and its items."""
        try:
            with self.sql_transaction():
                if not self.execute_simple_query(
                    "DELETE FROM workout_items WHERE workout_id = :id",
                    {"id": workout_id},
                ):
                    _raise_runtime_error(f"Failed to delete items for workout id={workout_id}")
                if not self.execute_simple_query("DELETE FROM workouts WHERE _id = :id", {"id": workout_id}):
                    _raise_runtime_error(f"Failed to delete workout id={workout_id}")
        except Exception:
            return False
        else:
            return True

    def delete_workout_item(self, item_id: int) -> bool:
        """Delete one exercise row from a saved workout."""
        return self.execute_simple_query("DELETE FROM workout_items WHERE _id = :id", {"id": item_id})

    def exercise_name_exists(self, name: str, *, exclude_id: int | None = None) -> bool:
        """Return whether an exercise already uses `name`.

        Args:

        - `name` (`str`): Exercise name to check.
        - `exclude_id` (`int | None`): Exercise ID to ignore (when renaming). Defaults to `None`.

        Returns:

        - `bool`: `True` when another exercise has the same name.

        """
        rows = self.get_rows("SELECT _id, name FROM exercises")
        return catalog_name_taken(rows, name, exclude_id=exclude_id)

    def exercise_name_local_exists(self, name_local: str, *, exclude_id: int | None = None) -> bool:
        """Return whether an exercise already uses `name_local`.

        Args:

        - `name_local` (`str`): Local exercise name to check.
        - `exclude_id` (`int | None`): Exercise ID to ignore (when renaming). Defaults to `None`.

        Returns:

        - `bool`: `True` when another exercise has the same local name.

        """
        rows = self.get_rows("SELECT _id, IFNULL(name_local, '') FROM exercises")
        return catalog_name_taken(rows, name_local, exclude_id=exclude_id)

    def exercise_type_name_exists(
        self,
        exercise_id: int,
        type_name: str,
        *,
        exclude_id: int | None = None,
    ) -> bool:
        """Return whether this exercise already has a type named `type_name`.

        Args:

        - `exercise_id` (`int`): Exercise that owns the types.
        - `type_name` (`str`): Type name to check.
        - `exclude_id` (`int | None`): Type ID to ignore (when renaming). Defaults to `None`.

        Returns:

        - `bool`: `True` when another type of this exercise has the same name.

        """
        rows = self.get_rows(
            "SELECT _id, type FROM types WHERE _id_exercises = :ex",
            {"ex": exercise_id},
        )
        return catalog_name_taken(rows, type_name, exclude_id=exclude_id)

    def find_duplicate_exercise(
        self,
        *,
        name: str = "",
        name_local: str = "",
        exclude_id: int | None = None,
    ) -> tuple[str, str] | None:
        """Return English and local names of an exercise that already uses one of them.

        Args:

        - `name` (`str`): English exercise name to look up. Defaults to `""`.
        - `name_local` (`str`): Local exercise name to look up. Defaults to `""`.
        - `exclude_id` (`int | None`): Exercise ID to ignore (when editing). Defaults to `None`.

        Returns:

        - `tuple[str, str] | None`: `(name, name_local)` of the first match, or `None`.

        """
        rows = self.get_rows("SELECT _id, name, IFNULL(name_local, '') FROM exercises")
        match = catalog_matching_row(rows, name, exclude_id=exclude_id, name_index=1)
        if match is None:
            match = catalog_matching_row(rows, name_local, exclude_id=exclude_id, name_index=2)
        if match is None:
            return None
        return str(match[1] or "").strip(), str(match[2] or "").strip()

    def get_all_exercise_types(self) -> list[list[Any]]:
        r"""Get all exercise types with exercise names.

        Returns:

        - `list[list[Any]]`: List of type records
          [\_id, exercise_name, type_name, calories_modifier, name_local].

        """
        return self.get_rows("""
            SELECT t._id, e.name, t.type, t.calories_modifier, IFNULL(t.name_local, '')
            FROM types t
            JOIN exercises e ON t._id_exercises = e._id
        """)

    def get_all_exercises(self) -> list[list[Any]]:
        r"""Get all exercises with their properties.

        Returns:

        - `list[list[Any]]`: List of exercise records
          [\_id, name, unit, is_type_required, calories_per_unit, name_local].

        """
        return self.get_rows(
            "SELECT _id, name, unit, is_type_required, calories_per_unit, IFNULL(name_local, '') "
            "FROM exercises ORDER BY is_favorite DESC, name ASC"
        )

    def get_all_process_records(self) -> list[list[Any]]:
        r"""Get all process records with exercise and type names.

        Returns:

        - `list[list[Any]]`: List of process records [\_id, exercise_name, type_name, value, unit, date].

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
        r"""Get all weight records.

        Returns:

        - `list[list[Any]]`: List of weight records [\_id, value, date].

        """
        return self.get_rows("SELECT _id, value, date FROM weight ORDER BY date DESC")

    def get_all_workouts(self) -> list[WorkoutRow]:
        """Return saved workouts, newest first."""
        rows = self.get_rows(
            """
            SELECT _id, name, gender, duration_min, created_date, notes
            FROM workouts
            ORDER BY created_date DESC, _id DESC
            """
        )
        return [_workout_row_from_sql(row) for row in rows if row]

    def get_dumbbell_exercise_names(self) -> set[str]:
        """Return English names of exercises that use template dumbbell weights."""
        template_id = self.get_id("exercises", "name", DUMBBELL_WEIGHT_TEMPLATE_EXERCISE)
        template_names = (
            [spec.name for spec in self.get_exercise_weight_type_specs(template_id)] if template_id is not None else []
        )
        types_by_exercise: dict[str, list[str]] = defaultdict(list)
        for row in self.get_all_exercise_types():
            exercise_name = str(row[1] or "").strip()
            type_name = str(row[2] or "").strip()
            if exercise_name and type_name:
                types_by_exercise[exercise_name].append(type_name)
        names: set[str] = set()
        for row in self.get_all_exercises():
            name = str(row[1] or "").strip()
            if name and is_dumbbell_exercise(name, types_by_exercise.get(name, ()), template_names):
                names.add(name)
        return names

    def get_earliest_process_date(self) -> str | None:
        """Get the earliest date from process records.

        Returns:

        - `str | None`: Earliest date in YYYY-MM-DD format or `None` if no data.

        """
        rows = self.get_rows("SELECT MIN(date) FROM process WHERE date IS NOT NULL")
        return rows[0][0] if rows and rows[0][0] else None

    def get_earliest_weight_date(self) -> str | None:
        """Get the earliest date from weight records.

        Returns:

        - `str | None`: Earliest date in YYYY-MM-DD format or `None` if no data.

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

        - `str | None`: Exercise name or `None` if not found.

        """
        rows = self.get_rows("SELECT name FROM exercises WHERE _id = :id", {"id": exercise_id})
        return rows[0][0] if rows else None

    def get_exercise_name_local(self, exercise_name: str) -> str:
        """Return local name for `exercise_name`, or empty string when missing."""
        rows = self.get_rows(
            "SELECT IFNULL(name_local, '') FROM exercises WHERE name = :name",
            {"name": exercise_name},
        )
        if rows and rows[0][0]:
            return str(rows[0][0])
        return ""

    def get_exercise_name_local_map(self) -> dict[str, str]:
        """Return mapping of English exercise name to non-empty local name."""
        rows = self.get_rows("SELECT name, IFNULL(name_local, '') FROM exercises")
        result: dict[str, str] = {}
        for row in rows:
            if not row or row[0] is None:
                continue
            name = str(row[0])
            name_local = str(row[1] or "").strip()
            if name and name_local:
                result[name] = name_local
        return result

    def get_exercise_names_missing_name_local(self, *, limit: int = 250) -> list[str]:
        """Return distinct exercise names that still need a local translation."""
        rows = self.get_rows(
            """
            SELECT name FROM exercises
            WHERE name IS NOT NULL AND TRIM(name) != ''
              AND (name_local IS NULL OR TRIM(name_local) = '')
            ORDER BY name
            LIMIT :limit
            """,
            {"limit": limit},
        )
        return [str(row[0]) for row in rows if row and row[0] is not None]

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
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
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

    def get_exercise_type_name_by_id(self, type_id: int) -> str | None:
        """Get exercise type name by ID.

        Args:

        - `type_id` (`int`): Type ID.

        Returns:

        - `str | None`: Type name or `None` if not found.

        """
        rows = self.get_rows("SELECT type FROM types WHERE _id = :id", {"id": type_id})
        return rows[0][0] if rows else None

    def get_exercise_type_names_missing_name_local(self, *, limit: int = 250) -> list[str]:
        """Return distinct type names that still need a local translation."""
        rows = self.get_rows(
            """
            SELECT DISTINCT type FROM types
            WHERE type IS NOT NULL AND TRIM(type) != ''
              AND (name_local IS NULL OR TRIM(name_local) = '')
            ORDER BY type
            LIMIT :limit
            """,
            {"limit": limit},
        )
        return [str(row[0]) for row in rows if row and row[0] is not None]

    def get_exercise_types(self, exercise_id: int) -> list[str]:
        """Get all types for a specific exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `list[str]`: List of type names.

        """
        rows = self.get_rows(
            "SELECT type FROM types WHERE _id_exercises = :ex_id",
            {"ex_id": exercise_id},
        )
        return [row[0] for row in rows]

    def get_exercise_unit(self, exercise_name: str) -> str:
        """Get the unit of measurement for a given exercise.

        Args:

        - `exercise_name` (`str`): Name of the exercise.

        Returns:

        - `str`: Unit of measurement, or `times` as default.

        """
        rows = self.get_rows("SELECT unit FROM exercises WHERE name = :name", {"name": exercise_name})
        if rows and rows[0][0]:
            return rows[0][0]
        return "times"

    def get_exercise_weight_type_specs(self, exercise_id: int) -> list[WeightTypeSpec]:
        """Return type name, calories modifier, and local name for one exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `list[WeightTypeSpec]`: Types belonging to the exercise.

        """
        rows = self.get_rows(
            """
            SELECT type, calories_modifier, IFNULL(name_local, '')
            FROM types
            WHERE _id_exercises = :ex_id
            ORDER BY type
            """,
            {"ex_id": exercise_id},
        )
        specs: list[WeightTypeSpec] = []
        for row in rows:
            name = str(row[0] or "").strip()
            if not name:
                continue
            try:
                modifier = float(row[1] or 1.0)
            except (TypeError, ValueError):
                modifier = 1.0
            specs.append(
                WeightTypeSpec(
                    name=name,
                    calories_modifier=modifier,
                    name_local=str(row[2] or "").strip(),
                )
            )
        return specs

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
        return prefer_favorite_names(sorted_exercises + remainder, self.get_favorite_exercise_names())

    def get_exercises_by_last_execution(self) -> list[str]:
        """Return exercise names ordered by last execution date (most recent first).

        Returns:

        - `list[str]`: Exercise names sorted by last execution date.
          Exercises never executed are appended at the end.

        """
        last_execution = self.get_rows(
            """
            SELECT
                e._id,
                e.name,
                MAX(p.date) AS last_date,
                MAX(p._id) AS last_process_id
            FROM exercises e
            LEFT JOIN process p ON e._id = p._id_exercises
            GROUP BY e._id, e.name
            ORDER BY
                (last_process_id IS NULL),
                last_process_id DESC,
                last_date DESC,
                e.name ASC
            """
        )

        return prefer_favorite_names([row[1] for row in last_execution], self.get_favorite_exercise_names())

    def get_favorite_exercise_names(self) -> set[str]:
        """Return English names of exercises marked as favorites."""
        return {
            str(row[0]) for row in self.get_rows("SELECT name FROM exercises WHERE is_favorite = 1") if row and row[0]
        }

    def get_filtered_process_records(
        self,
        exercise_name: str | None = None,
        exercise_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[list[Any]]:
        """Get filtered process records.

        Args:

        - `exercise_name` (`str | None`): Filter by exercise name. Defaults to `None`.
        - `exercise_type` (`str | None`): Filter by exercise type. Defaults to `None`.
        - `date_from` (`str | None`): Filter from date (YYYY-MM-DD). Defaults to `None`.
        - `date_to` (`str | None`): Filter to date (YYYY-MM-DD). Defaults to `None`.
        - `limit` (`int | None`): Limit number of records. Defaults to `None` (no limit).
        - `offset` (`int`): Number of records to skip. Defaults to `0`.

        Returns:

        - `list[list[Any]]`: List of filtered process records.

        """
        conditions: list[str] = []
        params: dict[str, Any] = {}

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

        if limit is not None:
            query_text += " LIMIT :limit OFFSET :offset"
            params["limit"] = limit
            params["offset"] = offset

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
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
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

        - `str | None`: Name of the last executed exercise or `None` if no records found.

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

        - `str | None`: Date string in YYYY-MM-DD format or `None` if not found.

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

        - `tuple[str, str] | None`: Tuple of (type_name, value) or `None` if not found.

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

        - `float | None`: The most recent weight value or `None` if no records found.

        """
        rows = self.get_rows("SELECT value FROM weight ORDER BY date DESC, _id DESC LIMIT 1")
        if rows and rows[0][0] is not None:
            try:
                return float(rows[0][0])
            except (ValueError, TypeError):
                return None
        return None

    def get_limited_process_records(self, limit: int = 5000, offset: int = 0) -> list[list[Any]]:
        r"""Get limited number of process records with exercise and type names.

        Args:

        - `limit` (`int`): Maximum number of records to return. Defaults to `5000`.
        - `offset` (`int`): Number of records to skip. Defaults to `0`.

        Returns:

        - `list[list[Any]]`: List of process records [\_id, exercise_name, type_name, value, unit, date].

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
            LIMIT :limit OFFSET :offset
        """,
            {"limit": limit, "offset": offset},
        )

    def get_monthly_totals_by_exercise(self, date_from: str, date_to: str) -> list[tuple[str, str, float]]:
        """Return per-exercise monthly totals for the whole catalog in one query.

        Args:

        - `date_from` (`str`): Inclusive lower bound (YYYY-MM-DD).
        - `date_to` (`str`): Inclusive upper bound (YYYY-MM-DD).

        Returns:

        - `list[tuple[str, str, float]]`: Tuples of (exercise name, `YYYY-MM`, total value).

        """
        rows = self.get_rows(
            """
            SELECT e.name, SUBSTR(p.date, 1, 7) AS month_key, SUM(CAST(p.value AS REAL))
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            WHERE p.date BETWEEN :date_from AND :date_to
            GROUP BY e.name, month_key
            """,
            {"date_from": date_from, "date_to": date_to},
        )
        result: list[tuple[str, str, float]] = []
        for row in rows:
            if not row or row[0] is None or row[1] is None:
                continue
            try:
                total = float(row[2] or 0.0)
            except (TypeError, ValueError):
                continue
            result.append((str(row[0]), str(row[1]), total))
        return result

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
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        rows = self.get_rows("SELECT COUNT(*) FROM process WHERE date = :today", {"today": today})
        return rows[0][0] if rows else 0

    def get_totals_by_exercise_for_date(self, date: str) -> dict[str, float]:
        """Return total value per exercise name for a single date in one query.

        Args:

        - `date` (`str`): Target date (YYYY-MM-DD).

        Returns:

        - `dict[str, float]`: Mapping of exercise name to total value on that date.

        """
        rows = self.get_rows(
            """
            SELECT e.name, SUM(CAST(p.value AS REAL))
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            WHERE p.date = :date
            GROUP BY e.name
            """,
            {"date": date},
        )
        totals: dict[str, float] = {}
        for row in rows:
            if not row or row[0] is None:
                continue
            try:
                totals[str(row[0])] = float(row[1] or 0.0)
            except (TypeError, ValueError):
                continue
        return totals

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

    def get_workout_by_id(self, workout_id: int) -> WorkoutRow | None:
        """Return one workout by primary key."""
        rows = self.get_rows(
            """
            SELECT _id, name, gender, duration_min, created_date, notes
            FROM workouts WHERE _id = :id
            """,
            {"id": workout_id},
        )
        if not rows:
            return None
        return _workout_row_from_sql(rows[0])

    def get_workout_item_by_id(self, item_id: int) -> WorkoutItemRow | None:
        """Return one workout item by primary key."""
        rows = self.get_rows(
            """
            SELECT
                wi._id, wi.workout_id, wi._id_exercises, wi._id_types,
                wi.exercise_name, wi.type_name, wi.target_value, wi.sort_order,
                wi.is_done, wi.process_id,
                IFNULL(e.unit, ''),
                IFNULL(e.calories_per_unit, 0),
                IFNULL(t.calories_modifier, 1.0)
            FROM workout_items wi
            LEFT JOIN exercises e ON e._id = wi._id_exercises
            LEFT JOIN types t ON t._id = wi._id_types AND t._id_exercises = wi._id_exercises
            WHERE wi._id = :id
            """,
            {"id": item_id},
        )
        if not rows:
            return None
        return _workout_item_row_from_sql(rows[0])

    def get_workout_items(self, workout_id: int) -> list[WorkoutItemRow]:
        """Return items for `workout_id` ordered by `sort_order`."""
        rows = self.get_rows(
            """
            SELECT
                wi._id, wi.workout_id, wi._id_exercises, wi._id_types,
                wi.exercise_name, wi.type_name, wi.target_value, wi.sort_order,
                wi.is_done, wi.process_id,
                IFNULL(e.unit, ''),
                IFNULL(e.calories_per_unit, 0),
                IFNULL(t.calories_modifier, 1.0)
            FROM workout_items wi
            LEFT JOIN exercises e ON e._id = wi._id_exercises
            LEFT JOIN types t ON t._id = wi._id_types AND t._id_exercises = wi._id_exercises
            WHERE wi.workout_id = :workout_id
            ORDER BY wi.sort_order ASC, wi._id ASC
            """,
            {"workout_id": workout_id},
        )
        return [_workout_item_row_from_sql(row) for row in rows if row]

    def is_exercise_favorite(self, exercise_id: int) -> bool:
        """Return whether the exercise is pinned as a favorite."""
        rows = self.get_rows("SELECT is_favorite FROM exercises WHERE _id = :id", {"id": exercise_id})
        if not rows or not rows[0]:
            return False
        try:
            return int(rows[0][0] or 0) != 0
        except (TypeError, ValueError):
            return False

    def is_exercise_type_required(self, exercise_id: int) -> bool:
        """Check if exercise type is required for a given exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `bool`: `True` if type is required, `False` otherwise.

        """
        rows = self.get_rows("SELECT is_type_required FROM exercises WHERE _id = :ex_id", {"ex_id": exercise_id})
        return bool(rows and rows[0][0] == 1)

    def mark_workout_item_done(self, item_id: int, process_id: int) -> bool:
        """Mark a workout item completed and store the logged `process` row."""
        return self.execute_simple_query(
            """
            UPDATE workout_items
            SET is_done = 1, process_id = :process_id
            WHERE _id = :id AND is_done = 0
            """,
            {"id": item_id, "process_id": process_id},
        )

    def rename_types_by_name(self, old_name: str, new_name: str) -> bool:
        """Rename every type row that currently uses `old_name`.

        Args:

        - `old_name` (`str`): Current type name, compared case-insensitively.
        - `new_name` (`str`): Replacement type name.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        return self.execute_simple_query(
            "UPDATE types SET type = :new WHERE LOWER(TRIM(type)) = LOWER(TRIM(:old))",
            {"old": old_name, "new": new_name},
        )

    def save_workout(
        self,
        name: str,
        gender: str,
        duration_min: int,
        items: list[WorkoutItemInput],
        *,
        created_date: str,
        notes: str | None = None,
    ) -> int | None:
        """Insert a workout and its items. Return the new `_id` or `None`."""
        try:
            with self.sql_transaction():
                if not self.execute_simple_query(
                    """
                    INSERT INTO workouts (name, gender, duration_min, created_date, notes)
                    VALUES (:name, :gender, :duration_min, :created_date, :notes)
                    """,
                    {
                        "name": name,
                        "gender": gender,
                        "duration_min": duration_min,
                        "created_date": created_date,
                        "notes": notes,
                    },
                ):
                    _raise_runtime_error(f"Failed to insert workout {name!r}")
                id_rows = self.get_rows("SELECT last_insert_rowid()")
                if not id_rows or id_rows[0][0] is None:
                    _raise_runtime_error("Failed to read new workout id")
                workout_id = int(id_rows[0][0])
                for sort_order, item in enumerate(items):
                    if not self.execute_simple_query(
                        """
                        INSERT INTO workout_items (
                            workout_id, _id_exercises, _id_types, exercise_name, type_name,
                            target_value, sort_order, is_done, process_id
                        )
                        VALUES (
                            :workout_id, :exercise_id, :type_id, :exercise_name, :type_name,
                            :target_value, :sort_order, 0, NULL
                        )
                        """,
                        {
                            "workout_id": workout_id,
                            "exercise_id": item.exercise_id,
                            "type_id": item.type_id,
                            "exercise_name": item.exercise_name,
                            "type_name": item.type_name,
                            "target_value": item.target_value,
                            "sort_order": sort_order,
                        },
                    ):
                        _raise_runtime_error(f"Failed to insert workout item {item.exercise_name!r}")
        except Exception:
            return None
        else:
            return workout_id

    def set_exercise_favorite(self, exercise_id: int, *, favorite: bool) -> bool:
        """Pin or unpin an exercise as a favorite."""
        return self.execute_simple_query(
            "UPDATE exercises SET is_favorite = :fav WHERE _id = :id",
            {"fav": 1 if favorite else 0, "id": exercise_id},
        )

    def set_exercise_type_required(self, exercise_id: int, *, required: bool) -> bool:
        """Set `is_type_required` for one exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `required` (`bool`): Whether a type must be chosen when logging a set.

        Returns:

        - `bool`: `True` if the update succeeded.

        """
        return self.execute_simple_query(
            "UPDATE exercises SET is_type_required = :itr WHERE _id = :id",
            {"itr": 1 if required else 0, "id": exercise_id},
        )

    def update_exercise(
        self,
        exercise_id: int,
        name: str,
        unit: str,
        *,
        is_type_required: bool,
        calories_per_unit: float = 0.0,
        name_local: str = "",
        is_favorite: bool | None = None,
    ) -> bool:
        """Update an existing exercise.

        Args:

        - `exercise_id` (`int`): Exercise ID.
        - `name` (`str`): Exercise name.
        - `unit` (`str`): Unit of measurement.
        - `is_type_required` (`bool`): Whether exercise type is required.
        - `calories_per_unit` (`float`): Calories burned per unit. Defaults to `0.0`.
        - `name_local` (`str`): Local-language exercise name. Defaults to `""`.
        - `is_favorite` (`bool | None`): Favorite flag, or `None` to leave it unchanged.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = (
            "UPDATE exercises SET name = :n, unit = :u, "
            "is_type_required = :itr, calories_per_unit = :cpu, name_local = :nl"
        )
        params: dict[str, Any] = {
            "n": name,
            "u": unit,
            "itr": 1 if is_type_required else 0,
            "cpu": calories_per_unit,
            "nl": name_local or None,
            "id": exercise_id,
        }
        if is_favorite is not None:
            query += ", is_favorite = :fav"
            params["fav"] = 1 if is_favorite else 0
        query += " WHERE _id = :id"
        return self.execute_simple_query(query, params)

    def update_exercise_name_local_by_name(self, name: str, name_local: str) -> int:
        """Set `name_local` for all exercises matching English `name` with empty local name.

        Returns:

        - `int`: Number of updated rows when known, otherwise `1` on success and `0` on failure.

        """
        before = self.get_rows(
            """
            SELECT COUNT(*) FROM exercises
            WHERE name = :name AND (name_local IS NULL OR TRIM(name_local) = '')
            """,
            {"name": name},
        )
        ok = self.execute_simple_query(
            """
            UPDATE exercises
            SET name_local = :nl
            WHERE name = :name AND (name_local IS NULL OR TRIM(name_local) = '')
            """,
            {"nl": name_local, "name": name},
        )
        if not ok:
            return 0
        return int(before[0][0]) if before and before[0] and before[0][0] is not None else 0

    def update_exercise_type(
        self,
        type_id: int,
        exercise_id: int,
        type_name: str,
        calories_modifier: float = 1.0,
        name_local: str = "",
    ) -> bool:
        """Update an existing exercise type.

        Args:

        - `type_id` (`int`): Type ID.
        - `exercise_id` (`int`): Exercise ID.
        - `type_name` (`str`): Type name.
        - `calories_modifier` (`float`): Calories modifier for this type. Defaults to `1.0`.
        - `name_local` (`str`): Local-language type name. Defaults to `""`.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = (
            "UPDATE types SET _id_exercises = :ex, type = :tp, "
            "calories_modifier = :cm, name_local = :nl WHERE _id = :id"
        )
        params = {
            "ex": exercise_id,
            "tp": type_name,
            "cm": calories_modifier,
            "nl": name_local or None,
            "id": type_id,
        }
        return self.execute_simple_query(query, params)

    def update_exercise_type_name_local_by_type(self, type_name: str, name_local: str) -> int:
        """Set `name_local` for all types matching English `type_name` with empty local name."""
        before = self.get_rows(
            """
            SELECT COUNT(*) FROM types
            WHERE type = :tp AND (name_local IS NULL OR TRIM(name_local) = '')
            """,
            {"tp": type_name},
        )
        ok = self.execute_simple_query(
            """
            UPDATE types
            SET name_local = :nl
            WHERE type = :tp AND (name_local IS NULL OR TRIM(name_local) = '')
            """,
            {"nl": name_local, "tp": type_name},
        )
        if not ok:
            return 0
        return int(before[0][0]) if before and before[0] and before[0][0] is not None else 0

    def update_process_record(self, record_id: int, exercise_id: int, type_id: int, value: str, date: str) -> bool:
        """Update an existing process record.

        Args:

        - `record_id` (`int`): Record ID.
        - `exercise_id` (`int`): Exercise ID.
        - `type_id` (`int`): Type ID (-1 for no type).
        - `value` (`str`): Exercise value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

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

    def update_process_records_date(self, record_ids: list[int], date: str) -> bool:
        """Set the same calendar date on many process rows (only the `date` column).

        Args:

        - `record_ids` (`list[int]`): Process primary keys to update.
        - `date` (`str`): New date in YYYY-MM-DD format.

        Returns:

        - `bool`: `True` if every update succeeded.

        """
        if not record_ids:
            return True
        try:
            with self.sql_transaction():
                for record_id in record_ids:
                    if not self.execute_simple_query(
                        "UPDATE process SET date = :date WHERE _id = :id",
                        {"date": date, "id": record_id},
                    ):
                        msg = f"Failed to update process date for id={record_id}"
                        _raise_runtime_error(msg)
        except Exception:
            logger.exception("Failed to update process dates in batch")
            return False
        else:
            return True

    def update_weight_record(self, record_id: int, value: float, date: str) -> bool:
        """Update an existing weight record.

        Args:

        - `record_id` (`int`): Record ID.
        - `value` (`float`): Weight value.
        - `date` (`str`): Date in YYYY-MM-DD format.

        Returns:

        - `bool`: `True` if successful, `False` otherwise.

        """
        query = "UPDATE weight SET value = :v, date = :d WHERE _id = :id"
        params = {"v": value, "d": date, "id": record_id}
        return self.execute_simple_query(query, params)

    def update_workout_duration(self, workout_id: int, duration_min: int) -> bool:
        """Update the planned duration of a saved workout."""
        return self.execute_simple_query(
            "UPDATE workouts SET duration_min = :duration WHERE _id = :id",
            {"duration": duration_min, "id": workout_id},
        )

    def update_workout_item_target_value(self, item_id: int, target_value: str) -> bool:
        """Update the planned value for one workout item."""
        return self.execute_simple_query(
            "UPDATE workout_items SET target_value = :value WHERE _id = :id",
            {"id": item_id, "value": target_value},
        )

    def _ensure_name_local_columns(self) -> None:
        """Ensure optional columns exist on `exercises` and `types`."""
        self._ensure_table_column("exercises", "name_local", "TEXT")
        self._ensure_table_column("types", "name_local", "TEXT")
        self._ensure_table_column("exercises", "is_favorite", "INTEGER NOT NULL DEFAULT 0")

    def _ensure_table_column(self, table_name: str, column_name: str, column_ddl: str) -> None:
        """Add an allow-listed column when it is missing."""
        allowed = {
            ("exercises", "name_local"): "TEXT",
            ("types", "name_local"): "TEXT",
            ("exercises", "is_favorite"): "INTEGER NOT NULL DEFAULT 0",
        }
        expected_ddl = allowed.get((table_name, column_name))
        if expected_ddl is None or expected_ddl != column_ddl:
            logger.error("Refusing to alter unexpected table/column: %s.%s", table_name, column_name)
            return
        try:
            columns = {
                str(row[1])
                for row in self.get_rows(f"PRAGMA table_info({table_name})")
                if row and len(row) > 1 and row[1] is not None
            }
            if column_name in columns:
                return
            if not self.execute_simple_query(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_ddl}"):
                logger.error("Failed to add %s.%s column", table_name, column_name)
        except Exception:
            logger.exception("Could not ensure %s.%s column", table_name, column_name)


@dataclass(frozen=True, slots=True)
class WorkoutItemInput:
    """One item to store when saving a generated workout."""

    exercise_id: int
    type_id: int
    exercise_name: str
    type_name: str
    target_value: str


@dataclass(frozen=True, slots=True)
class WorkoutItemRow:
    """Stored workout item plus catalog calorie fields."""

    id: int
    workout_id: int
    exercise_id: int
    type_id: int
    exercise_name: str
    type_name: str
    target_value: str
    sort_order: int
    is_done: bool
    process_id: int | None
    unit: str
    calories_per_unit: float
    calories_modifier: float


@dataclass(frozen=True, slots=True)
class WorkoutRow:
    """One saved workout."""

    id: int
    name: str
    gender: str
    duration_min: int
    created_date: str
    notes: str | None


def catalog_matching_row(
    rows: list[list[Any]],
    candidate: str,
    *,
    exclude_id: int | None = None,
    name_index: int = 1,
) -> list[Any] | None:
    """Return the first row whose name at `name_index` matches `candidate`.

    Args:

    - `rows` (`list[list[Any]]`): Rows with an ID in column `0`.
    - `candidate` (`str`): Name to look up.
    - `exclude_id` (`int | None`): ID to ignore. Defaults to `None`.
    - `name_index` (`int`): Column that holds the name. Defaults to `1`.

    Returns:

    - `list[Any] | None`: Matching row, or `None`.

    """
    folded = candidate.strip().casefold()
    if not folded:
        return None
    for row in rows:
        if len(row) <= name_index:
            continue
        try:
            row_id = int(row[0])
        except (TypeError, ValueError):
            continue
        if exclude_id is not None and row_id == exclude_id:
            continue
        if str(row[name_index] or "").strip().casefold() == folded:
            return row
    return None


def catalog_name_taken(
    rows: list[list[Any]],
    candidate: str,
    *,
    exclude_id: int | None = None,
) -> bool:
    """Return whether `candidate` matches a name in `(_id, name)` rows.

    Args:

    - `rows` (`list[list[Any]]`): Rows whose first two values are ID and name.
    - `candidate` (`str`): Name to look up.
    - `exclude_id` (`int | None`): ID to ignore. Defaults to `None`.

    Returns:

    - `bool`: `True` when another row already uses this name.

    """
    return catalog_matching_row(rows, candidate, exclude_id=exclude_id) is not None


def _optional_sql_float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _optional_sql_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _raise_runtime_error(message: str) -> NoReturn:
    """Raise `RuntimeError` (helper for TRY301 inside SQL transactions)."""
    raise RuntimeError(message)


def _workout_item_row_from_sql(row: list[Any] | tuple[Any, ...]) -> WorkoutItemRow:
    return WorkoutItemRow(
        id=int(row[0]),
        workout_id=int(row[1]),
        exercise_id=int(row[2]),
        type_id=int(row[3]),
        exercise_name=str(row[4]),
        type_name=str(row[5] or ""),
        target_value=str(row[6]),
        sort_order=int(row[7]) if row[7] is not None else 0,
        is_done=bool(row[8]),
        process_id=_optional_sql_int(row[9]),
        unit=str(row[10] or ""),
        calories_per_unit=_optional_sql_float(row[11]),
        calories_modifier=_optional_sql_float(row[12], 1.0),
    )


def _workout_row_from_sql(row: list[Any] | tuple[Any, ...]) -> WorkoutRow:
    notes = str(row[5]).strip() if row[5] not in (None, "") else None
    return WorkoutRow(
        id=int(row[0]),
        name=str(row[1]),
        gender=str(row[2]),
        duration_min=int(row[3]),
        created_date=str(row[4]),
        notes=notes or None,
    )
