"""Mixin classes for fitness tracker application.

This module contains reusable mixin classes that provide common functionality
for database operations, table management, chart creation, and date handling.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PySide6.QtCore import QDate

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.chart_operations import ChartOperationsBase
from harrix_swiss_knife.apps.common.db_guard import requires_database
from harrix_swiss_knife.apps.common.qt_mixins import DateMixin, TableOperations, ValidationMixin
from harrix_swiss_knife.apps.food.delegates import parse_is_drink_cell

if TYPE_CHECKING:
    from collections.abc import Callable

    from matplotlib.axes import Axes
    from PySide6.QtGui import QStandardItemModel
    from PySide6.QtWidgets import QDateEdit, QLayout

__all__ = [
    "AutoSaveOperations",
    "ChartOperations",
    "DateOperations",
    "TableOperations",
    "ValidationOperations",
    "requires_database",
]


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
                message_box.warning(None, "Auto-save Error", f"Failed to save {table_name} row: {e!s}")

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
            message_box.warning(None, "Validation Error", "Exercise name cannot be empty")
            return

        # Convert is_type_required to boolean
        is_type_required = is_type_required_str == "1"

        # Update database
        if not self.db_manager.update_exercise(
            int(row_id), name.strip(), unit.strip(), is_type_required=is_type_required
        ):
            message_box.warning(None, "Database Error", "Failed to save exercise record")
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
            message_box.warning(None, "Validation Error", "Food name cannot be empty")
            return

        # Validate date format
        if not self._is_valid_date(date):
            message_box.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Parse numeric values
        weight = None
        calories_per_100g = None
        portion_calories = None

        try:
            if weight_str.strip():
                weight = float(weight_str)
                if weight <= 0:
                    message_box.warning(None, "Validation Error", "Weight must be a positive number")
                    return
        except (ValueError, TypeError):
            if weight_str.strip():  # Only show error if there's actually a value
                message_box.warning(None, "Validation Error", f"Invalid weight value: {weight_str}")
                return

        try:
            if calories_per_100g_str.strip():
                calories_per_100g = float(calories_per_100g_str)
        except (ValueError, TypeError):
            if calories_per_100g_str.strip():  # Only show error if there's actually a value
                message_box.warning(
                    None, "Validation Error", f"Invalid calories per 100g value: {calories_per_100g_str}"
                )
                return

        try:
            if portion_calories_str.strip():
                portion_calories = float(portion_calories_str)
                if portion_calories <= 0:
                    message_box.warning(None, "Validation Error", "Portion calories must be a positive number")
                    return
        except (ValueError, TypeError):
            if portion_calories_str.strip():  # Only show error if there's actually a value
                message_box.warning(None, "Validation Error", f"Invalid portion calories value: {portion_calories_str}")
                return

        is_drink = parse_is_drink_cell(is_drink_str)

        # Update database
        if not self.db_manager.update_food_log_record(
            int(row_id),
            date=date,
            calories_per_100g=calories_per_100g,
            name=name.strip(),
            name_en=name_en.strip() or None,
            weight=weight,
            portion_calories=portion_calories,
            is_drink=is_drink,
        ):
            message_box.warning(None, "Database Error", "Failed to save food log record")
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
            message_box.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            message_box.warning(None, "Validation Error", f"Exercise '{exercise}' not found")
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
        exercise_name = model.data(model.index(row, 0)) or ""
        type_name = model.data(model.index(row, 1)) or ""

        # Validate inputs
        if not exercise_name.strip():
            message_box.warning(None, "Validation Error", "Exercise name cannot be empty")
            return

        if not type_name.strip():
            message_box.warning(None, "Validation Error", "Type name cannot be empty")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if ex_id is None:
            message_box.warning(None, "Validation Error", f"Exercise '{exercise_name}' not found")
            return

        # Update database
        if not self.db_manager.update_exercise_type(int(row_id), ex_id, type_name.strip()):
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

    # Expected attributes from main class
    max_count_points_in_charts: int

    def _clear_layout(self, layout: QLayout, *, close_matplotlib_figures: bool = False) -> None:
        """Clear all widgets from a layout.

        The food app historically reparented widgets without closing
        Matplotlib figures, so `close_matplotlib_figures` defaults to `False`
        here to preserve the previous behavior.
        """
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            if item is not None:
                child = item.widget()
                if child:
                    if close_matplotlib_figures:
                        super()._clear_layout(layout, close_matplotlib_figures=True)
                        return
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
        if x_values and isinstance(x_values[0], datetime):
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

    def _format_chart_x_axis(self, ax: Axes, dates: list, period: str) -> None:
        """Format x-axis for charts based on period and data range.

        Args:

        - `ax` (`Axes`): Matplotlib axes object.
        - `dates` (`list`): List of datetime objects.
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

    def _format_default_stats(self, values: list, unit: str = "", *, filter_none: bool = True) -> str:
        """Format default statistics text.

        Food's historical behavior filters out None values and returns
        `"No data"` when nothing remains; overridden here to keep that
        default while delegating to the shared implementation.
        """
        return super()._format_default_stats(values, unit, filter_none=filter_none)

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


class DateOperations(DateMixin):
    """Mixin class for date operations."""

    db_manager: Any
    _validate_database_connection: Callable[[], bool]


class ValidationOperations(ValidationMixin):
    """Mixin class for validation operations."""
