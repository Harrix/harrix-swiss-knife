"""Mixin classes for fitness tracker application.

This module contains reusable mixin classes that provide common functionality
for database operations, table management, chart creation, and date handling.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.chart_operations import ChartOperationsBase
from harrix_swiss_knife.apps.common.db_guard import requires_database
from harrix_swiss_knife.apps.common.qt_mixins import AutoSaveMixin, DateMixin, TableOperations, ValidationMixin
from harrix_swiss_knife.apps.fitness.exercise_favorites import parse_exercise_display_name

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QStandardItemModel

__all__ = [
    "AutoSaveOperations",
    "ChartOperations",
    "DateOperations",
    "TableOperations",
    "ValidationOperations",
    "requires_database",
]


class AutoSaveOperations(AutoSaveMixin):
    """Mixin class for auto-save operations."""

    db_manager: Any
    _validate_database_connection: Callable[[], bool]
    _update_comboboxes: Callable[..., None]
    update_filter_comboboxes: Callable[[], None]
    _is_valid_date: Callable[[str], bool]

    def _get_save_handlers(self) -> dict[str, Callable[..., None]]:
        return {
            "process": self._save_process_data,
            "exercises": self._save_exercise_data,
            "types": self._save_type_data,
            "weight": self._save_weight_data,
        }

    def _save_exercise_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save exercise data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        name = parse_exercise_display_name(model.data(model.index(row, 1)) or "")
        unit = model.data(model.index(row, 2)) or ""
        is_type_required_str = model.data(model.index(row, 3)) or "0"
        calories_per_unit_str = model.data(model.index(row, 4)) or "0"
        name_local = model.data(model.index(row, 5)) or ""

        # Validate exercise name
        if not name.strip():
            message_box.warning(None, "Validation Error", "Exercise name cannot be empty")
            return

        # Convert is_type_required to boolean
        is_type_required = is_type_required_str == "1"

        # Convert calories_per_unit to float
        try:
            calories_per_unit = float(calories_per_unit_str)
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid calories per unit value: {calories_per_unit_str}")
            return

        # Update database
        old_name = self.db_manager.get_exercise_name_by_id(int(row_id))
        new_name = name.strip()
        if self.db_manager.exercise_name_exists(new_name, exclude_id=int(row_id)):
            message_box.warning(None, "Validation Error", f"Exercise '{new_name}' already exists")
            return
        if not self.db_manager.update_exercise(
            int(row_id),
            new_name,
            unit.strip(),
            is_type_required=is_type_required,
            calories_per_unit=calories_per_unit,
            name_local=str(name_local).strip(),
        ):
            message_box.warning(None, "Database Error", "Failed to save exercise record")
        else:
            rename_media = getattr(self, "_rename_exercise_media", None)
            if callable(rename_media) and isinstance(old_name, str):
                rename_media(old_name, new_name)
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_process_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save process record data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        exercise = parse_exercise_display_name(model.data(model.index(row, 0)) or "")
        type_name = model.data(model.index(row, 1))
        value_raw = model.data(model.index(row, 2))
        date = model.data(model.index(row, 3))

        # Extract value from "value unit" format
        value = value_raw.split(" ")[0] if value_raw else ""

        # Validate date format
        if not self._is_valid_date(date):
            message_box.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            message_box.warning(None, "Validation Error", f"Exercise '{exercise}' not found")
            return

        # Get type ID (can be -1 for no type)
        if type_name:
            type_rows = self.db_manager.get_rows(
                "SELECT _id FROM types WHERE type = :name AND _id_exercises = :ex_id",
                {"name": type_name, "ex_id": ex_id},
            )
            tp_id = type_rows[0][0] if type_rows else None
        else:
            tp_id = -1

        # Validate numeric value
        try:
            float(value)
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid numeric value: {value}")
            return

        # Update database
        if not self.db_manager.update_process_record(int(row_id), ex_id, tp_id or -1, value, date):
            message_box.warning(None, "Database Error", "Failed to save process record")

    def _save_type_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save exercise type data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        exercise_name = parse_exercise_display_name(model.data(model.index(row, 1)) or "")
        type_name = model.data(model.index(row, 2)) or ""
        calories_modifier_str = model.data(model.index(row, 3)) or "1.0"
        name_local = model.data(model.index(row, 4)) or ""

        # Validate inputs
        if not exercise_name.strip():
            message_box.warning(None, "Validation Error", "Exercise name cannot be empty")
            return

        if not type_name.strip():
            message_box.warning(None, "Validation Error", "Type name cannot be empty")
            return

        # Convert calories_modifier to float
        try:
            calories_modifier = float(calories_modifier_str)
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid calories modifier value: {calories_modifier_str}")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if ex_id is None:
            message_box.warning(None, "Validation Error", f"Exercise '{exercise_name}' not found")
            return

        if self.db_manager.exercise_type_name_exists(ex_id, type_name.strip(), exclude_id=int(row_id)):
            message_box.warning(
                None,
                "Validation Error",
                f"Exercise type '{type_name.strip()}' already exists for '{exercise_name}'",
            )
            return

        # Update database
        if not self.db_manager.update_exercise_type(
            int(row_id),
            ex_id,
            type_name.strip(),
            calories_modifier,
            name_local=str(name_local).strip(),
        ):
            message_box.warning(None, "Database Error", "Failed to save type record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_weight_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save weight data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        weight_str = model.data(model.index(row, 0)) or ""
        date = model.data(model.index(row, 1)) or ""

        # Validate weight value
        try:
            weight_value = float(weight_str)
            if weight_value <= 0:
                message_box.warning(None, "Validation Error", "Weight must be a positive number")
                return
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid weight value: {weight_str}")
            return

        # Validate date format
        if not self._is_valid_date(date):
            message_box.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Update database
        if not self.db_manager.update_weight_record(int(row_id), weight_value, date):
            message_box.warning(None, "Database Error", "Failed to save weight record")


class ChartOperations(ChartOperationsBase):
    """Mixin class for chart operations."""


class DateOperations(DateMixin):
    """Mixin class for date operations."""

    db_manager: Any
    _validate_database_connection: Callable[[], bool]


class ValidationOperations(ValidationMixin):
    """Mixin class for validation operations."""
