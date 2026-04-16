"""Utility for working with a local SQLite database that stores food-related information."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from harrix_swiss_knife.apps.common.qt_database_manager_base import QtSqliteDatabaseManagerBase


class DatabaseManager(QtSqliteDatabaseManagerBase):
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
        super().__init__(prefix="food_db", db_filename=db_filename)

    def add_food_item(
        self,
        name: str,
        name_en: str | None = None,
        *,
        is_drink: bool = False,
        calories_per_100g: float | None = None,
        default_portion_weight: float | None = None,
        default_portion_calories: float | None = None,
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
            INSERT INTO food_items (
                name, name_en, is_drink, calories_per_100g,
                default_portion_weight, default_portion_calories
            )
            VALUES (
                :name, :name_en, :is_drink, :calories_per_100g,
                :default_portion_weight, :default_portion_calories
            )
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
        *,
        is_drink: bool = False,
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

    def get_all_food_items(self) -> list[list[Any]]:
        """Get all food items.

        Returns:

        - `list[list[Any]]`: List of food items [_id, name, name_en, is_drink, calories_per_100g,
          default_portion_weight, default_portion_calories].

        """
        return self.get_rows("""
            SELECT _id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories
            FROM food_items
            ORDER BY name
        """)

    def get_all_food_log_records(self) -> list[list[Any]]:
        """Get all food log records.

        Returns:

        - `list[list[Any]]`: List of food log records [_id, date, weight, portion_calories,
          calories_per_100g, name, name_en, is_drink].

        """
        return self.get_rows("""
            SELECT _id, date, weight, portion_calories, calories_per_100g, name, name_en, is_drink
            FROM food_log
            ORDER BY date DESC, _id DESC
        """)

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
                        WHEN calories_per_100g IS NOT NULL AND calories_per_100g > 0
                             AND weight IS NOT NULL AND weight > 0
                        THEN (calories_per_100g * weight) / 100
                        ELSE 0
                    END
                ) as total_calories
            FROM food_log
            GROUP BY date
            ORDER BY date DESC
        """
        return self.get_rows(query)

    def get_drinks_weight_per_day(self) -> list[list[Any]]:
        """Get drinks weight consumed per day for all days.

        Returns:

        - `list[list[Any]]`: List of [date, total_weight] records.

        """
        query = """
            SELECT
                date,
                SUM(weight) as total_weight
            FROM food_log
            WHERE is_drink = 1 AND weight IS NOT NULL AND weight > 0
            GROUP BY date
            ORDER BY date DESC
        """
        return self.get_rows(query)

    def get_drinks_weight_today(self) -> int:
        """Get total weight of drinks consumed today.

        Returns:

        - `int`: Total weight of drinks in grams.

        """
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        query = "SELECT SUM(weight) FROM food_log WHERE date = :today AND is_drink = 1 AND weight IS NOT NULL"
        params = {"today": today}
        rows = self.get_rows(query, params)
        try:
            return int(rows[0][0]) if rows and rows[0][0] is not None and rows[0][0] != "" else 0
        except (ValueError, TypeError):
            return 0

    def get_earliest_food_log_date(self) -> str | None:
        """Get the earliest date from food_log table.

        Returns:

        - `str | None`: The earliest date in YYYY-MM-DD format, or None if no records exist.

        """
        query = "SELECT MIN(date) FROM food_log WHERE date IS NOT NULL"
        rows = self.get_rows(query)

        if not rows or not rows[0] or rows[0][0] is None:
            return None

        return str(rows[0][0])

    def get_food_calories_today(self) -> float:
        """Get total calories consumed today.

        Returns:

        - `float`: Total calories today.

        """
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        query = """
            SELECT SUM(
                CASE
                    WHEN portion_calories IS NOT NULL AND portion_calories > 0
                    THEN portion_calories
                    WHEN calories_per_100g IS NOT NULL AND calories_per_100g > 0 AND weight IS NOT NULL AND weight > 0
                    THEN (calories_per_100g * weight) / 100
                    ELSE 0
                END
            ) as total_calories
            FROM food_log
            WHERE date = :today
        """
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

    def get_food_item_by_name(self, name: str) -> FoodItemByNameRow | None:
        """Get food item by name.

        Args:

        - `name` (`str`): Food item name.

        Returns:

        - `FoodItemByNameRow | None`: Food item data or None if not found.

        """
        query = (
            "SELECT _id, name, name_en, is_drink, calories_per_100g, "
            "default_portion_weight, default_portion_calories FROM food_items WHERE name = :name"
        )
        params = {"name": name}
        rows = self.get_rows(query, params)
        if not rows:
            return None
        row = rows[0]
        return FoodItemByNameRow(
            id=int(row[0]),
            name=str(row[1]),
            name_en=str(row[2]) if row[2] is not None else None,
            is_drink=bool(row[3]) if row[3] is not None else False,
            calories_per_100g=float(row[4]) if row[4] not in (None, "") else None,
            default_portion_weight=float(row[5]) if row[5] not in (None, "") else None,
            default_portion_calories=float(row[6]) if row[6] not in (None, "") else None,
        )

    def get_food_items_by_name(self, limit: int = 500) -> list[str]:
        """Get food items sorted by name.

        Args:

        - `limit` (`int`): Maximum number of items to return. Defaults to `500`.

        Returns:

        - `list[str]`: List of food item names.

        """
        query = "SELECT name FROM food_items ORDER BY name LIMIT :limit"
        rows = self.get_rows(query, {"limit": limit})
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
                calories_float = 0.0 if calories_value is None or calories_value == "" else float(calories_value)
                result.append((date_str, calories_float))
            except (ValueError, TypeError):
                # Skip invalid rows
                continue

        return result

    def get_food_log_item_by_name(self, name: str) -> FoodLogItemByNameRow | None:
        """Get food item data by name from food_log table (most recent record).

        Args:

        - `name` (`str`): Name of the food item to find.

        Returns:

        - `FoodLogItemByNameRow | None`: Food item data or None if not found.

        """
        query = """
            SELECT name, name_en, is_drink, calories_per_100g, weight, portion_calories
            FROM food_log
            WHERE name = :name
            ORDER BY date DESC, _id DESC
            LIMIT 1
        """
        params = {"name": name}
        rows = self.get_rows(query, params)
        if not rows:
            return None
        row = rows[0]
        return FoodLogItemByNameRow(
            name=str(row[0]) if row[0] is not None else None,
            name_en=str(row[1]) if row[1] is not None else None,
            is_drink=bool(row[2]) if row[2] is not None else False,
            calories_per_100g=float(row[3]) if row[3] not in (None, "") else None,
            weight=float(row[4]) if row[4] not in (None, "") else None,
            portion_calories=float(row[5]) if row[5] not in (None, "") else None,
        )

    def get_food_weight_per_day(self) -> list[list[Any]]:
        """Get food weight consumed per day for all days (excluding drinks).

        Returns:

        - `list[list[Any]]`: List of [date, total_weight] records.

        """
        query = """
            SELECT
                date,
                SUM(weight) as total_weight
            FROM food_log
            WHERE is_drink = 0 AND weight IS NOT NULL AND weight > 0
            GROUP BY date
            ORDER BY date DESC
        """
        return self.get_rows(query)

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

    def get_popular_food_items(self, limit: int = 500) -> list[str]:
        """Get popular food items from recent food_log records.

        Args:

        - `limit` (`int`): Maximum number of recent records to analyze. Defaults to `500`.

        Returns:

        - `list[str]`: List of food item names sorted by popularity (most popular first).

        """
        query = """
            SELECT name, COUNT(*) as usage_count
            FROM (
                SELECT name FROM food_log
                WHERE name IS NOT NULL AND name != ''
                ORDER BY date DESC, _id DESC
                LIMIT :limit
            ) as recent_foods
            GROUP BY name
            ORDER BY usage_count DESC, name ASC
        """
        rows = self.get_rows(query, {"limit": limit})
        return [row[0] for row in rows if row[0]]

    def get_popular_food_items_with_calories(self, limit: int = 500) -> list[list[Any]]:
        """Get popular food items with calories information from recent food_log records.

        Args:

        - `limit` (`int`): Maximum number of recent records to analyze. Defaults to `500`.

        Returns:

        - `list[list[Any]]`: List of food item data with calories info.

        """
        query = """
            SELECT name, COUNT(*) as usage_count
            FROM (
                SELECT name FROM food_log
                WHERE name IS NOT NULL AND name != ''
                ORDER BY date DESC, _id DESC
                LIMIT :limit
            ) as recent_foods
            GROUP BY name
            ORDER BY usage_count DESC, name ASC
        """
        popular_names = self.get_rows(query, {"limit": limit})

        # Get full data for popular items from food_items table
        result = []
        for row in popular_names:
            name = row[0]
            if name:
                # First try to get data from food_items table
                food_item_data = self.get_food_item_by_name(name)
                if food_item_data:
                    result.append(
                        [
                            food_item_data.id,
                            food_item_data.name,
                            food_item_data.name_en,
                            food_item_data.is_drink,
                            food_item_data.calories_per_100g,
                            food_item_data.default_portion_weight,
                            food_item_data.default_portion_calories,
                        ]
                    )
                else:
                    # If not found in food_items, get data from food_log
                    food_log_data = self.get_food_log_item_by_name(name)
                    if food_log_data:
                        result.append(
                            [
                                None,
                                food_log_data.name,
                                food_log_data.name_en,
                                food_log_data.is_drink,
                                food_log_data.calories_per_100g,
                                food_log_data.weight,
                                food_log_data.portion_calories,
                            ]
                        )
                    else:
                        # If not found anywhere, create minimal data
                        result.append([None, name, None, 0, None, None, None])

        return result

    def get_problematic_food_records(self) -> list[list[Any]]:
        """Get problematic food records that need attention.

        Returns records with:
        - NULL or zero weight, OR
        - Both calories_per_100g and portion_calories are NULL or zero (and not a drink)

        Returns:

        - `list[list[Any]]`: List of problematic food log records.

        """
        query = """
            SELECT _id, date, weight, portion_calories, calories_per_100g, name, name_en, is_drink
            FROM food_log
            WHERE (
                -- Records with NULL or zero weight
                (weight IS NULL OR weight = 0)
                OR
                -- Records where both calories_per_100g and portion_calories are NULL or zero (and not a drink)
                (
                    (calories_per_100g IS NULL OR calories_per_100g = 0)
                    AND (portion_calories IS NULL OR portion_calories = 0)
                    AND is_drink = 0
                )
            )
            ORDER BY date DESC, _id DESC
        """
        return self.get_rows(query)

    def get_recent_food_log_records(self, limit: int = 5000) -> list[list[Any]]:
        """Get recent food log records for table display.

        Args:

        - `limit` (`int`): Maximum number of records to return. Defaults to `5000`.

        Returns:

        - `list[list[Any]]`: List of recent food log records [_id, date, weight, portion_calories,
          calories_per_100g, name, name_en, is_drink].

        """
        return self.get_rows(
            """
            SELECT _id, date, weight, portion_calories, calories_per_100g, name, name_en, is_drink
            FROM food_log
            ORDER BY date DESC, _id DESC
            LIMIT :limit
            """,
            {"limit": limit},
        )

    def get_recent_food_names_for_autocomplete(self, limit: int = 100) -> list[str]:
        """Get recent unique food names for autocomplete functionality.

        Args:

        - `limit` (`int`): Maximum number of recent records to analyze. Defaults to `100`.

        Returns:

        - `list[str]`: List of unique food names from recent records.

        """
        query = """
            SELECT DISTINCT name
            FROM (
                SELECT name FROM food_log
                WHERE name IS NOT NULL AND name != ''
                ORDER BY date DESC, _id DESC
                LIMIT :limit
            ) as recent_foods
            ORDER BY name ASC
        """
        rows = self.get_rows(query, {"limit": limit})
        return [row[0] for row in rows if row[0]]

    def update_food_item(
        self,
        food_item_id: int,
        name: str,
        name_en: str | None = None,
        *,
        is_drink: bool = False,
        calories_per_100g: float | None = None,
        default_portion_weight: float | None = None,
        default_portion_calories: float | None = None,
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
        *,
        is_drink: bool = False,
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

    def update_food_log_weight_and_calories(
        self,
        record_id: int,
        weight: float | None,
        calories_per_100g: float | None,
    ) -> bool:
        """Update only weight and calories_per_100g for a food log record.

        Args:

        - `record_id` (`int`): Record ID.
        - `weight` (`float | None`): Weight in grams.
        - `calories_per_100g` (`float | None`): Calories per 100g.

        Returns:

        - `bool`: True if successful, False otherwise.

        """
        query = """
            UPDATE food_log
            SET weight = :weight, calories_per_100g = :calories_per_100g
            WHERE _id = :id
        """
        params = {
            "id": record_id,
            "weight": weight,
            "calories_per_100g": calories_per_100g,
        }
        return self.execute_simple_query(query, params)


@dataclass(frozen=True, slots=True)
class FoodItemByNameRow:
    """Row from `food_items` for lookups by exact name."""

    id: int
    name: str
    name_en: str | None
    is_drink: bool
    calories_per_100g: float | None
    default_portion_weight: float | None
    default_portion_calories: float | None


@dataclass(frozen=True, slots=True)
class FoodLogItemByNameRow:
    """Row from `food_log` (most recent) for lookups by exact name."""

    name: str | None
    name_en: str | None
    is_drink: bool
    calories_per_100g: float | None
    weight: float | None
    portion_calories: float | None
