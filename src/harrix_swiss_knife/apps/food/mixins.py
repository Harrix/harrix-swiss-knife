"""Mixin classes for fitness tracker application.

This module contains reusable mixin classes that provide common functionality
for database operations, table management, chart creation, and date handling.
"""

from __future__ import annotations

import re
from collections import defaultdict
from functools import wraps
from typing import TYPE_CHECKING, Any, Concatenate, ParamSpec, TypeVar

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pendulum
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QDateEdit, QLabel, QMessageBox

if TYPE_CHECKING:
    from collections.abc import Callable

    from matplotlib.axes import Axes
    from PySide6.QtWidgets import QLayout

# Type variables for decorators
P = ParamSpec("P")
R = TypeVar("R")
SelfT = TypeVar("SelfT")


class AutoSaveOperations:
    """Mixin class for auto-save operations."""

    # Expected attributes from main class
    db_manager: Any
    _validate_database_connection: Callable[[], bool]
    _update_comboboxes: Callable[[], None]
    update_filter_comboboxes: Callable[[], None]
    _is_valid_date: Callable[[str], bool]
    update_food_calories_today: Callable[[], None]

    def _auto_save_row(self, table_name: str, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Auto-save table row data.

        Args:

        - `table_name` (`str`): Name of the table.
        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        if not self._validate_database_connection():
            return

        save_handlers = {
            "process": self._save_process_data,
            "exercises": self._save_exercise_data,
            "types": self._save_type_data,
            "weight": self._save_weight_data,
            "food_log": self._save_food_log_data,
        }

        handler = save_handlers.get(table_name)
        if handler:
            try:
                handler(model, row, row_id)
            except Exception as e:
                QMessageBox.warning(None, "Auto-save Error", f"Failed to save {table_name} row: {e!s}")

    def _save_exercise_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save exercise data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_type_required_str = model.data(model.index(row, 2)) or "0"

        # Validate exercise name
        if not name.strip():
            QMessageBox.warning(None, "Validation Error", "Exercise name cannot be empty")
            return

        # Convert is_type_required to boolean
        is_type_required = is_type_required_str == "1"

        # Update database
        if not self.db_manager.update_exercise(
            int(row_id), name.strip(), unit.strip(), is_type_required=is_type_required
        ):
            QMessageBox.warning(None, "Database Error", "Failed to save exercise record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_food_log_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save food log data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        # Get data from model columns
        name = model.data(model.index(row, 0)) or ""
        is_drink_str = model.data(model.index(row, 1)) or ""
        weight_str = model.data(model.index(row, 2)) or ""
        calories_per_100g_str = model.data(model.index(row, 3)) or ""
        portion_calories_str = model.data(model.index(row, 4)) or ""
        date = model.data(model.index(row, 6)) or ""
        name_en = model.data(model.index(row, 7)) or ""

        # Validate food name
        if not name.strip():
            QMessageBox.warning(None, "Validation Error", "Food name cannot be empty")
            return

        # Validate date format
        if not self._is_valid_date(date):
            QMessageBox.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Parse numeric values
        weight = None
        calories_per_100g = None
        portion_calories = None

        try:
            if weight_str.strip():
                weight = float(weight_str)
                if weight <= 0:
                    QMessageBox.warning(None, "Validation Error", "Weight must be a positive number")
                    return
        except (ValueError, TypeError):
            if weight_str.strip():  # Only show error if there's actually a value
                QMessageBox.warning(None, "Validation Error", f"Invalid weight value: {weight_str}")
                return

        try:
            if calories_per_100g_str.strip():
                calories_per_100g = float(calories_per_100g_str)
        except (ValueError, TypeError):
            if calories_per_100g_str.strip():  # Only show error if there's actually a value
                QMessageBox.warning(
                    None, "Validation Error", f"Invalid calories per 100g value: {calories_per_100g_str}"
                )
                return

        try:
            if portion_calories_str.strip():
                portion_calories = float(portion_calories_str)
                if portion_calories <= 0:
                    QMessageBox.warning(None, "Validation Error", "Portion calories must be a positive number")
                    return
        except (ValueError, TypeError):
            if portion_calories_str.strip():  # Only show error if there's actually a value
                QMessageBox.warning(None, "Validation Error", f"Invalid portion calories value: {portion_calories_str}")
                return

        # Parse is_drink value
        is_drink = is_drink_str.strip().lower() in ["yes", "true", "1", "да"]  # ignore: HP001

        # Update database
        if not self.db_manager.update_food_log_record(
            int(row_id),
            date=date,
            calories_per_100g=calories_per_100g,
            name=name.strip(),
            name_en=name_en.strip() if name_en.strip() else None,
            weight=weight,
            portion_calories=portion_calories,
            is_drink=is_drink,
        ):
            QMessageBox.warning(None, "Database Error", "Failed to save food log record")
        else:
            # Update related UI elements
            self.update_food_calories_today()

    def _save_process_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save process record data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        exercise = model.data(model.index(row, 0))
        type_name = model.data(model.index(row, 1))
        value_raw = model.data(model.index(row, 2))
        date = model.data(model.index(row, 3))

        # Extract value from "value unit" format
        value = value_raw.split(" ")[0] if value_raw else ""

        # Validate date format
        if not self._is_valid_date(date):
            QMessageBox.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            QMessageBox.warning(None, "Validation Error", f"Exercise '{exercise}' not found")
            return

        # Get type ID (can be -1 for no type)
        tp_id = (
            self.db_manager.get_id("types", "type", type_name, condition=f"_id_exercises = {ex_id}")
            if type_name
            else -1
        )

        # Validate numeric value
        try:
            float(value)
        except (ValueError, TypeError):
            QMessageBox.warning(None, "Validation Error", f"Invalid numeric value: {value}")
            return

        # Update database
        if not self.db_manager.update_process_record(int(row_id), ex_id, tp_id or -1, value, date):
            QMessageBox.warning(None, "Database Error", "Failed to save process record")

    def _save_type_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save exercise type data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        exercise_name = model.data(model.index(row, 0)) or ""
        type_name = model.data(model.index(row, 1)) or ""

        # Validate inputs
        if not exercise_name.strip():
            QMessageBox.warning(None, "Validation Error", "Exercise name cannot be empty")
            return

        if not type_name.strip():
            QMessageBox.warning(None, "Validation Error", "Type name cannot be empty")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if ex_id is None:
            QMessageBox.warning(None, "Validation Error", f"Exercise '{exercise_name}' not found")
            return

        # Update database
        if not self.db_manager.update_exercise_type(int(row_id), ex_id, type_name.strip()):
            QMessageBox.warning(None, "Database Error", "Failed to save type record")
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
                QMessageBox.warning(None, "Validation Error", "Weight must be a positive number")
                return
        except (ValueError, TypeError):
            QMessageBox.warning(None, "Validation Error", f"Invalid weight value: {weight_str}")
            return

        # Validate date format
        if not self._is_valid_date(date):
            QMessageBox.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Update database
        if not self.db_manager.update_weight_record(int(row_id), weight_value, date):
            QMessageBox.warning(None, "Database Error", "Failed to save weight record")


class ChartOperations:
    """Mixin class for chart operations."""

    # Expected attributes from main class
    max_count_points_in_charts: int

    def _add_stats_box(self, ax: Axes, stats_text: str, color: str = "lightgray") -> None:
        """Add statistics box to chart.

        Args:

        - `ax` (`Axes`): Matplotlib axes object.
        - `stats_text` (`str`): Statistics text to display.
        - `color` (`str`): Background color of the statistics box. Defaults to `"lightgray"`.

        """
        ax.text(
            0.5,
            0.02,
            stats_text,
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=10,
            bbox={"boxstyle": "round,pad=0.3", "facecolor": color, "alpha": 0.8},
        )

    def _clear_layout(self, layout: QLayout) -> None:
        """Clear all widgets from a layout.

        Args:

        - `layout` (`QLayout`): Layout to clear.

        """
        for i in reversed(range(layout.count())):
            child = layout.takeAt(i).widget()
            if child:
                child.setParent(None)

    def _create_chart(self, layout: QLayout, data: list, chart_config: dict) -> None:
        """Create and display a chart with given data and configuration.

        Args:

        - `layout` (`QLayout`): Layout to add chart to.
        - `data` (`list`): Chart data as list of (x, y) tuples.
        - `chart_config` (`dict`): Dictionary with chart configuration including:
        - title: Chart title
        - xlabel: X-axis label
        - ylabel: Y-axis label
        - color: Line color
        - show_stats: Whether to show statistics
        - stats_unit: Unit for statistics display
        - period: Period for x-axis formatting (Days/Months/Years)
        - stats_formatter: Optional function to format statistics
        - fill_zero_periods: Whether to fill missing periods with zero values
        - is_calories_chart: Whether this is a calories chart that needs color coding

        """
        # Clear existing chart
        self._clear_layout(layout)

        if not data:
            self._show_no_data_label(layout, "No data found for the selected period")
            return

        # Fill missing periods with zeros if requested
        if chart_config.get("fill_zero_periods", False):
            data = self._fill_missing_periods_with_zeros(
                data, chart_config.get("period", "Days"), chart_config.get("date_from"), chart_config.get("date_to")
            )

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Extract data
        x_values = [item[0] for item in data]
        y_values = [item[1] for item in data]

        # Count non-zero and non-None values for label display decision
        non_zero_count = sum(1 for y in y_values if y is not None and y != 0)

        # Plot data
        self._plot_data(
            ax,
            x_values,
            y_values,
            chart_config.get("color", "b"),
            non_zero_count,
            chart_config.get("period"),
            is_calories_chart=chart_config.get("is_calories_chart", False),  # Add this parameter
        )

        # Customize plot
        ax.set_xlabel(chart_config.get("xlabel", "X"), fontsize=12)
        ax.set_ylabel(chart_config.get("ylabel", "Y"), fontsize=12)
        ax.set_title(chart_config.get("title", "Chart"), fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)

        # Set Y-axis limits to start from non-zero value
        self._set_y_axis_limits(ax, y_values)

        # Format x-axis if dates
        if x_values and isinstance(x_values[0], pendulum.DateTime):
            self._format_chart_x_axis(ax, x_values, chart_config.get("period", "Days"))

        # Add statistics if requested (exclude zero values from stats)
        if chart_config.get("show_stats", True) and len(y_values) > 1:
            stats_formatter = chart_config.get("stats_formatter")
            if stats_formatter:
                # Filter out zero and None values for statistics
                non_zero_values = [y for y in y_values if y is not None and y != 0]
                if non_zero_values:
                    stats_text = stats_formatter(non_zero_values)
                    self._add_stats_box(ax, stats_text)
            else:
                non_zero_values = [y for y in y_values if y is not None and y != 0]
                if non_zero_values:
                    stats_text = self._format_default_stats(non_zero_values, chart_config.get("stats_unit", ""))
                    self._add_stats_box(ax, stats_text)

        fig.tight_layout()
        layout.addWidget(canvas)
        canvas.draw()

    def _fill_missing_periods_with_zeros(
        self, data: list[tuple], period: str, date_from: str | None = None, date_to: str | None = None
    ) -> list[tuple]:
        """Fill missing periods with None values (for gaps in chart).

        Args:

        - `data` (`list[tuple]`): List of (pendulum.DateTime, value) tuples.
        - `period` (`str`): Period type (Days/Months/Years).
        - `date_from` (`str | None`): Start date string in YYYY-MM-DD format. Defaults to `None`.
        - `date_to` (`str | None`): End date string in YYYY-MM-DD format. Defaults to `None`.

        Returns:

        - `list[tuple]`: List with filled missing periods.

        """
        if not data:
            return data

        data_dict = {item[0]: item[1] for item in data}

        # Always start from the first actual data point to avoid leading None values
        actual_start_date = min(item[0] for item in data)
        actual_end_date = max(item[0] for item in data)

        if date_from and date_to:
            try:
                user_start_date = pendulum.parse(date_from, strict=False).in_timezone(pendulum.UTC)
                user_end_date = pendulum.parse(date_to, strict=False).in_timezone(pendulum.UTC)
                # Use the later of actual start date or user start date to avoid leading None values
                start_date = max(actual_start_date, user_start_date)
                end_date = min(actual_end_date, user_end_date)
            except ValueError:
                return data
        else:
            # Use actual data range
            start_date = actual_start_date
            end_date = actual_end_date

        result = []
        current_date = start_date

        if period == "Months":
            current_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            while current_date <= end_date:
                value = data_dict.get(current_date)
                result.append((current_date, value))
                count_months = 12
                if current_date.month == count_months:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)

        elif period == "Years":
            current_date = start_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

            while current_date <= end_date:
                value = data_dict.get(current_date)
                result.append((current_date, value))
                current_date = current_date.replace(year=current_date.year + 1)

        else:  # "Days" period
            current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

            while current_date <= end_date:
                value = data_dict.get(current_date)
                result.append((current_date, value))
                current_date = current_date.add(days=1)

        return result

    def _format_chart_x_axis(self, ax: Axes, dates: list, period: str) -> None:
        """Format x-axis for charts based on period and data range.

        Args:

        - `ax` (`Axes`): Matplotlib axes object.
        - `dates` (`list`): List of pendulum.DateTime objects.
        - `period` (`str`): Time period for formatting.

        """
        if not dates:
            return

        days_in_month = 31
        days_in_year = 365

        if period == "Days":
            # Limit to max 10-15 ticks
            ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune="both"))

            date_range = (max(dates) - min(dates)).days
            if date_range <= days_in_month or date_range <= days_in_year:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        elif period == "Months":
            ax.xaxis.set_major_locator(MaxNLocator(nbins=12, prune="both"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        elif period == "Years":
            ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune="both"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

        # Rotate date labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

    def _format_default_stats(self, values: list, unit: str = "") -> str:
        """Format default statistics text.

        Args:

        - `values` (`list`): List of numeric values.
        - `unit` (`str`): Unit of measurement. Defaults to `""`.

        Returns:

        - `str`: Formatted statistics string.

        """
        # Filter out None values
        valid_values = [v for v in values if v is not None]

        if not valid_values:
            return "No data"

        min_val = min(valid_values)
        max_val = max(valid_values)
        avg_val = sum(valid_values) / len(valid_values)

        unit_suffix = f" {unit}" if unit else ""

        # Format based on value type
        if all(isinstance(v, int) for v in valid_values):
            return (
                f"Min: {int(min_val)}{unit_suffix} | Max: {int(max_val)}{unit_suffix} | Avg: {avg_val:.1f}{unit_suffix}"
            )
        return f"Min: {min_val:.1f}{unit_suffix} | Max: {max_val:.1f}{unit_suffix} | Avg: {avg_val:.1f}{unit_suffix}"

    def _group_data_by_period(self, rows: list, period: str, value_type: str = "float") -> dict:
        """Group data by the specified period (Days, Months, Years).

        Args:

        - `rows` (`list`): List of (date_str, value_str) tuples.
        - `period` (`str`): Grouping period (Days, Months, Years).
        - `value_type` (`str`): Type of value ('float' or 'int'). Defaults to `"float"`.

        Returns:

        - `dict`: Dictionary with pendulum.DateTime keys and aggregated values.

        """
        grouped = defaultdict(float if value_type == "float" else int)

        # Regex pattern for YYYY-MM-DD format
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for date_str, value_str in rows:
            # Quick validation without exceptions
            if not date_pattern.match(date_str):
                continue

            try:
                value = float(value_str) if value_type == "float" else int(value_str)
            except (ValueError, TypeError):
                continue

            # Safe date parsing with proper error handling
            try:
                date_obj = pendulum.parse(date_str, strict=False).in_timezone(pendulum.UTC)
            except ValueError:
                # Skip invalid dates (e.g., Feb 30, Apr 31, etc.)
                continue

            if period == "Days":
                key = date_obj
            elif period == "Months":
                key = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "Years":
                key = date_obj.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                key = date_obj

            grouped[key] += value

        return dict(sorted(grouped.items()))

    def _group_data_by_period_with_max(self, rows: list, period: str, value_type: str = "float") -> dict:
        """Group data by the specified period (Days, Months, Years) using maximum values.

        Args:

        - `rows` (`list`): List of (date_str, value_str) tuples.
        - `period` (`str`): Grouping period (Days, Months, Years).
        - `value_type` (`str`): Type of value ('float' or 'int'). Defaults to `"float"`.

        Returns:

        - `dict`: Dictionary with pendulum.DateTime keys and maximum values for each period.

        """
        grouped = defaultdict(list)

        # Regex pattern for YYYY-MM-DD format
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for date_str, value_str in rows:
            # Quick validation without exceptions
            if not date_pattern.match(date_str):
                continue

            try:
                value = float(value_str) if value_type == "float" else int(value_str)
            except (ValueError, TypeError):
                continue

            # Safe date parsing with proper error handling
            try:
                date_obj = pendulum.parse(date_str, strict=False).in_timezone(pendulum.UTC)
            except ValueError:
                # Skip invalid dates (e.g., Feb 30, Apr 31, etc.)
                continue

            if period == "Days":
                key = date_obj
            elif period == "Months":
                key = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "Years":
                key = date_obj.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                key = date_obj

            grouped[key].append(value)

        # Convert lists to maximum values
        max_grouped = {}
        for key, values in grouped.items():
            if values:  # Only add if there are values
                max_grouped[key] = max(values)

        return dict(sorted(max_grouped.items()))

    def _plot_data(
        self,
        ax: Axes,
        x_values: list,
        y_values: list,
        color: str,
        non_zero_count: int | None = None,
        period: str | None = None,
        *,
        is_calories_chart: bool = False,
    ) -> None:
        """Plot data with automatic marker selection based on data points.

        Args:

        - `ax` (`Axes`): Matplotlib axes object.
        - `x_values` (`list`): X-axis values.
        - `y_values` (`list`): Y-axis values.
        - `color` (`str`): Plot color.
        - `non_zero_count` (`int | None`): Number of non-zero points for label decision. Defaults to `None`.
        - `period` (`str | None`): Time period for formatting labels. Defaults to `None`.
        - `is_calories_chart` (`bool`): Whether this is a calories chart that needs color coding. Defaults to `False`.

        """
        # Map color names to matplotlib single-letter codes
        color_map = {
            "blue": "b",
            "green": "g",
            "red": "r",
            "orange": "orange",  # Keep full name for colors without single-letter codes
            "purple": "purple",
            "brown": "brown",
            "pink": "pink",
            "gray": "gray",
            "olive": "olive",
            "cyan": "c",
        }

        # Use mapped color or original if not in map
        plot_color = color_map.get(color, color)

        # Use non_zero_count if provided, otherwise use total length
        point_count_for_labels = non_zero_count if non_zero_count is not None else len(y_values)

        # For calories chart, plot colored points with line and critical zones
        if is_calories_chart:
            # Draw horizontal lines for critical zones only for Days period
            if period not in {"Months", "Years"}:
                ax.axhline(
                    y=1800, color="green", linestyle="--", linewidth=1, alpha=0.5, zorder=1, label="Low calories limit"
                )
                ax.axhline(
                    y=2100,
                    color="orange",
                    linestyle="--",
                    linewidth=1,
                    alpha=0.5,
                    zorder=1,
                    label="Medium-low calories limit",
                )
                ax.axhline(
                    y=2500,
                    color="red",
                    linestyle="--",
                    linewidth=1,
                    alpha=0.5,
                    zorder=1,
                    label="Medium-high calories limit",
                )

            # Draw thin connecting line behind points
            ax.plot(x_values, y_values, color="gray", linestyle="-", linewidth=1, alpha=0.6, zorder=2)

            # Get colors for each point based on calories value
            point_colors = []
            level_low_calories = 1800
            level_medium_low_calories = 2100
            level_medium_high_calories = 2500
            for y in y_values:
                if y is None or y == 0:
                    point_colors.append("lightgray")  # Gray for zero/None values
                elif y <= level_low_calories:
                    point_colors.append("#90EE90")  # Light green for low calories
                elif y <= level_medium_low_calories:
                    point_colors.append("#FFFFE0")  # Light yellow for medium-low calories
                elif y <= level_medium_high_calories:
                    point_colors.append("#FFE4C4")  # Bisque for medium-high calories
                else:
                    point_colors.append("#FFC0CB")  # Light pink for high calories

            # Add value labels only if there are fewer than
            maximum_count_points_for_labels = 100
            if len(x_values) < maximum_count_points_for_labels:
                for x, y in zip(x_values, y_values, strict=False):
                    if y is not None and y != 0:  # Only label non-zero and non-None points
                        # Format label based on value type - remove unnecessary .0
                        label_text = str(int(y)) if isinstance(y, int) or y == int(y) else f"{y:.1f}"

                        # Add year in parentheses for Years period
                        if period == "Years" and hasattr(x, "year"):
                            label_text += f" ({x.year})"

                        ax.annotate(
                            label_text,
                            (x, y),
                            textcoords="offset points",
                            xytext=(0, 10),
                            ha="center",
                            fontsize=9,
                            alpha=0.8,
                            # Add white outline for better readability
                            bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                            zorder=4,  # Ensure labels are on top
                        )

        # Original plotting logic for non-calories charts
        elif point_count_for_labels <= self.max_count_points_in_charts:
            ax.plot(
                x_values,
                y_values,
                color=plot_color,
                marker="o",
                linestyle="-",
                linewidth=2,
                alpha=0.8,
                markersize=6,
                markerfacecolor=plot_color,
                markeredgecolor=f"dark{color}" if color in ["blue", "green", "red"] else plot_color,
            )
            # Add value labels only for non-zero and non-None values
            for x, y in zip(x_values, y_values, strict=False):
                if y is not None and y != 0:  # Only label non-zero and non-None points
                    # Format label based on value type - remove unnecessary .0
                    label_text = str(int(y)) if isinstance(y, int) or y == int(y) else f"{y:.1f}"

                    # Add year in parentheses for Years period
                    if period == "Years" and hasattr(x, "year"):
                        label_text += f" ({x.year})"

                    ax.annotate(
                        label_text,
                        (x, y),
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha="center",
                        fontsize=9,
                        alpha=0.8,
                        # Add white outline for better readability
                        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                    )
        else:
            ax.plot(x_values, y_values, color=plot_color, linestyle="-", linewidth=2, alpha=0.8)

            # Always label the last point, even when there are many points
            if x_values and y_values:
                last_x = x_values[-1]
                last_y = y_values[-1]

                # Only label if the last point is non-zero and non-None
                if last_y is not None and last_y != 0:
                    # Format label based on value type - remove unnecessary .0
                    if isinstance(last_y, int) or last_y == int(last_y):
                        label_text = str(int(last_y))
                    else:
                        label_text = f"{last_y:.1f}"

                    # Add year in parentheses for Years period
                    if period == "Years" and hasattr(last_x, "year"):
                        label_text += f" ({last_x.year})"

                    ax.annotate(
                        label_text,
                        (last_x, last_y),
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha="center",
                        fontsize=9,
                        alpha=0.8,
                        # Add white outline for better readability
                        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                    )

    def _set_y_axis_limits(self, ax: Axes, y_values: list) -> None:
        """Set Y-axis limits to start from a non-zero value for better data visualization.

        Args:

        - `ax` (`Axes`): Matplotlib axes object.
        - `y_values` (`list`): Y-axis values.

        """
        if not y_values:
            return

        # Filter out zero and None values for limit calculation
        non_zero_values = [y for y in y_values if y is not None and y != 0]

        if not non_zero_values:
            return

        min_val = min(non_zero_values)
        max_val = max(non_zero_values)

        if min_val == max_val:
            # If all values are the same, create a reasonable range around the value
            center = min_val
            margin = abs(center) * 0.1 if center != 0 else 1
            ax.set_ylim(center - margin, center + margin)
        else:
            # Calculate range and add padding
            value_range = max_val - min_val
            padding = value_range * 0.1  # 10% padding

            # Set lower limit: don't go below 0 for positive values,
            # but allow some space below the minimum
            lower_limit = max(0, min_val - padding) if min_val > 0 else min_val - padding
            upper_limit = max_val + padding

            ax.set_ylim(lower_limit, upper_limit)

    def _show_no_data_label(self, layout: QLayout, text: str) -> None:
        """Show a 'no data' label in the layout.

        Args:

        - `layout` (`QLayout`): Layout to add the label to.
        - `text` (`str`): Text to display.

        """
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)


class DateOperations:
    """Mixin class for date operations."""

    db_manager: Any
    _validate_database_connection: Callable[[], bool]

    def _increment_date_widget(self, date_widget: QDateEdit) -> None:
        """Increment date widget by one day if not already today.

        Args:

        - `date_widget` (`QDateEdit`): QDateEdit widget to increment.

        """
        current_date = date_widget.date()
        today = QDate.currentDate()

        # If current date is today or later, do nothing
        if current_date >= today:
            return

        # Add one day to the current date
        next_date = current_date.addDays(1)
        date_widget.setDate(next_date)

    def _set_date_range(
        self,
        from_widget: QDateEdit,
        to_widget: QDateEdit,
        months: int = 0,
        years: int = 0,
        *,
        is_all_time: bool = False,
    ) -> None:
        """Set date range for date widgets.

        Args:

        - `from_widget` (`QDateEdit`): From date widget.
        - `to_widget` (`QDateEdit`): To date widget.
        - `months` (`int`): Number of months back from today. Defaults to `0`.
        - `years` (`int`): Number of years back from today. Defaults to `0`.
        - `is_all_time` (`bool`): If True, sets to earliest available date. Defaults to `False`.

        """
        current_date = QDate.currentDate()
        to_widget.setDate(current_date)

        if is_all_time and self._validate_database_connection():
            # Determine earliest date based on widget type
            if hasattr(from_widget, "objectName") and "weight" in from_widget.objectName():
                earliest = self.db_manager.get_earliest_weight_date()
            else:
                earliest = self.db_manager.get_earliest_process_date()

            if earliest:
                from_widget.setDate(QDate.fromString(earliest, "yyyy-MM-dd"))
            else:
                from_widget.setDate(current_date.addYears(-1))
        elif years:
            from_widget.setDate(current_date.addYears(-years))
        elif months:
            from_widget.setDate(current_date.addMonths(-months))


class TableOperations:
    """Mixin class for common table operations."""

    table_config: dict[str, tuple[Any, str, list[str]]]
    models: dict[str, Any]
    _create_table_model: Callable[[list, list[str]], Any]

    def _connect_table_signals(self, table_name: str, selection_handler: Callable) -> None:
        """Connect selection change signal for a table.

        Args:

        - `table_name` (`str`): Name of the table.
        - `selection_handler` (`Callable`): Handler function for selection changes.

        """
        view = self.table_config[table_name][0]
        selection_model = view.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(selection_handler)

    def _get_selected_row_id(self, table_name: str) -> int | None:
        """Get the database ID of the currently selected row.

        Args:

        - `table_name` (`str`): Name of the table.

        Returns:

        - `int | None`: Database ID of selected row or None if no selection.

        """
        try:
            table_view, model_key, _ = self.table_config[table_name]
            model = self.models[model_key]

            if model is None:
                return None

            index = table_view.currentIndex()
            if not index.isValid():
                return None

            source_model = model.sourceModel()
            if not isinstance(source_model, QStandardItemModel):
                return None

            vertical_header_item = source_model.verticalHeaderItem(index.row())
            return int(vertical_header_item.text()) if vertical_header_item else None

        except (KeyError, ValueError, TypeError, AttributeError):
            return None

    def _refresh_table(
        self, table_name: str, data_getter: Callable, data_transformer: Callable[[list], list] | None = None
    ) -> None:
        """Refresh a table with data.

        Args:

        - `table_name` (`str`): Name of the table to refresh.
        - `data_getter` (`Callable`): Function to get data from database.
        - `data_transformer` (`Callable[[list], list] | None`): Optional function to transform raw data.
          Defaults to `None`.

        Raises:

        - `ValueError`: If the table name is unknown.

        """
        if table_name not in self.table_config:
            error_msg = f"❌ Unknown table: {table_name}"
            raise ValueError(error_msg)

        rows = data_getter()
        if data_transformer:
            rows = data_transformer(rows)

        view, model_key, headers = self.table_config[table_name]
        self.models[model_key] = self._create_table_model(rows, headers)
        view.setModel(self.models[model_key])
        view.resizeColumnsToContents()


class ValidationOperations:
    """Mixin class for validation operations."""

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Return `True` if `YYYY-MM-DD` formatted `date_str` is correct.

        Args:

        - `date_str` (`str`): Date string to validate.

        Returns:

        - `bool`: True if the date is in the correct format and represents a valid date.

        """
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
            return False

        try:
            pendulum.parse(date_str, strict=False).in_timezone(pendulum.UTC)
        except (ValueError, TypeError):
            return False
        else:
            return True


def requires_database(
    *, is_show_warning: bool = True
) -> Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]:
    """Ensure database connection is available before executing method.

    Args:

    - `is_show_warning` (`bool`): If True, shows a QMessageBox warning on connection failure. Defaults to `True`.

    Returns:

    - `Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]`: Decorated function
      that checks database connection first.

    """

    def decorator(
        func: Callable[Concatenate[SelfT, P], R],
    ) -> Callable[Concatenate[SelfT, P], R | None]:
        @wraps(func)
        def wrapper(self: SelfT, *args: P.args, **kwargs: P.kwargs) -> R | None:
            if not self._validate_database_connection():  # type: ignore[attr-defined]
                if is_show_warning:
                    QMessageBox.warning(None, "❌ Database Error", "❌ Database connection not available")
                return None

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
