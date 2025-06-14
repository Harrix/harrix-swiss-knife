"""Mixin classes for fitness tracker application.

This module contains reusable mixin classes that provide common functionality
for database operations, table management, chart creation, and date handling.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timezone
from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QLabel, QMessageBox

if TYPE_CHECKING:
    from PySide6.QtWidgets import QLayout

# Type variables for decorators
P = ParamSpec("P")
T = TypeVar("T")


class AutoSaveOperations:
    """Mixin class for auto-save operations."""

    def _auto_save_row(self, table_name: str, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Generic auto-save method for table rows.

        Args:
            table_name: Name of the table
            model: The model containing the data
            row: Row index
            row_id: Database ID of the row

        """
        if not self._validate_database_connection():
            return

        save_handlers = {
            "process": self._save_process_data,
            "exercises": self._save_exercise_data,
            "types": self._save_type_data,
            "weight": self._save_weight_data,
        }

        handler = save_handlers.get(table_name)
        if handler:
            try:
                handler(model, row, row_id)
            except Exception as e:
                QMessageBox.warning(self, "Auto-save Error", f"Failed to save {table_name} row: {e!s}")

    def _save_exercise_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save exercise data."""
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_type_required_str = model.data(model.index(row, 2)) or "0"

        # Validate exercise name
        if not name.strip():
            QMessageBox.warning(self, "Validation Error", "Exercise name cannot be empty")
            return

        # Convert is_type_required to boolean
        is_type_required = is_type_required_str == "1"

        # Update database
        if not self.db_manager.update_exercise(
            int(row_id), name.strip(), unit.strip(), is_type_required=is_type_required
        ):
            QMessageBox.warning(self, "Database Error", "Failed to save exercise record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_process_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save process record data."""
        exercise = model.data(model.index(row, 0))
        type_name = model.data(model.index(row, 1))
        value_raw = model.data(model.index(row, 2))
        date = model.data(model.index(row, 3))

        # Extract value from "value unit" format
        value = value_raw.split(" ")[0] if value_raw else ""

        # Validate date format
        if not self._is_valid_date(date):
            QMessageBox.warning(self, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            QMessageBox.warning(self, "Validation Error", f"Exercise '{exercise}' not found")
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
            QMessageBox.warning(self, "Validation Error", f"Invalid numeric value: {value}")
            return

        # Update database
        if not self.db_manager.update_process_record(int(row_id), ex_id, tp_id or -1, value, date):
            QMessageBox.warning(self, "Database Error", "Failed to save process record")

    def _save_type_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save exercise type data."""
        exercise_name = model.data(model.index(row, 0)) or ""
        type_name = model.data(model.index(row, 1)) or ""

        # Validate inputs
        if not exercise_name.strip():
            QMessageBox.warning(self, "Validation Error", "Exercise name cannot be empty")
            return

        if not type_name.strip():
            QMessageBox.warning(self, "Validation Error", "Type name cannot be empty")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if ex_id is None:
            QMessageBox.warning(self, "Validation Error", f"Exercise '{exercise_name}' not found")
            return

        # Update database
        if not self.db_manager.update_exercise_type(int(row_id), ex_id, type_name.strip()):
            QMessageBox.warning(self, "Database Error", "Failed to save type record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_weight_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save weight data."""
        weight_str = model.data(model.index(row, 0)) or ""
        date = model.data(model.index(row, 1)) or ""

        # Validate weight value
        try:
            weight_value = float(weight_str)
            if weight_value <= 0:
                QMessageBox.warning(self, "Validation Error", "Weight must be a positive number")
                return
        except (ValueError, TypeError):
            QMessageBox.warning(self, "Validation Error", f"Invalid weight value: {weight_str}")
            return

        # Validate date format
        if not self._is_valid_date(date):
            QMessageBox.warning(self, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Update database
        if not self.db_manager.update_weight_record(int(row_id), weight_value, date):
            QMessageBox.warning(self, "Database Error", "Failed to save weight record")


class ChartOperations:
    """Mixin class for chart operations."""

    def _add_stats_box(self, ax: plt.Axes, stats_text: str, color: str = "lightgray") -> None:
        """Add statistics box to chart."""
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
        """Clear all widgets from a layout."""
        for i in reversed(range(layout.count())):
            child = layout.takeAt(i).widget()
            if child:
                child.setParent(None)

    def _create_chart(self, layout: QLayout, data: list, chart_config: dict) -> None:
        """Create and display a chart with given data and configuration.

        Args:
            layout: Layout to add chart to
            data: Chart data as list of (x, y) tuples
            chart_config: Dictionary with chart configuration including:
                - title: Chart title
                - xlabel: X-axis label
                - ylabel: Y-axis label
                - color: Line color
                - show_stats: Whether to show statistics
                - stats_unit: Unit for statistics display
                - period: Period for x-axis formatting (Days/Months/Years)
                - stats_formatter: Optional function to format statistics

        """
        # Clear existing chart
        self._clear_layout(layout)

        if not data:
            self._show_no_data_label(layout, "No data found for the selected period")
            return

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Extract data
        x_values = [item[0] for item in data]
        y_values = [item[1] for item in data]

        # Plot data
        self._plot_data(ax, x_values, y_values, chart_config.get("color", "b"))

        # Customize plot
        ax.set_xlabel(chart_config.get("xlabel", "X"), fontsize=12)
        ax.set_ylabel(chart_config.get("ylabel", "Y"), fontsize=12)
        ax.set_title(chart_config.get("title", "Chart"), fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)

        # Format x-axis if dates
        if x_values and isinstance(x_values[0], datetime):
            self._format_chart_x_axis(ax, x_values, chart_config.get("period", "Days"))

        # Add statistics if requested
        if chart_config.get("show_stats", True) and len(y_values) > 1:
            stats_formatter = chart_config.get("stats_formatter")
            if stats_formatter:
                stats_text = stats_formatter(y_values)
            else:
                stats_text = self._format_default_stats(y_values, chart_config.get("stats_unit", ""))
            self._add_stats_box(ax, stats_text)

        fig.tight_layout()
        layout.addWidget(canvas)
        canvas.draw()

    def _format_chart_x_axis(self, ax: plt.Axes, dates: list, period: str) -> None:
        """Format x-axis for charts based on period and data range."""
        if not dates:
            return

        from matplotlib.ticker import MaxNLocator

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
        """Format default statistics text."""
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)

        unit_suffix = f" {unit}" if unit else ""

        # Format based on value type
        if all(isinstance(v, int) for v in values):
            return (
                f"Min: {int(min_val)}{unit_suffix} | Max: {int(max_val)}{unit_suffix} | Avg: {avg_val:.1f}{unit_suffix}"
            )
        return (
            f"Min: {min_val:.1f}{unit_suffix} | Max: {max_val:.1f}{unit_suffix} | Avg: {avg_val:.1f}{unit_suffix}"
        )

    def _group_data_by_period(self, rows: list, period: str, value_type: str = "float") -> dict:
        """Group data by the specified period (Days, Months, Years).

        Args:
            rows: List of (date_str, value_str) tuples
            period: Grouping period (Days, Months, Years)
            value_type: Type of value ('float' or 'int')

        Returns:
            Dictionary with datetime keys and aggregated values

        """
        grouped = defaultdict(float if value_type == "float" else int)

        # Regex pattern for YYYY-MM-DD format
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for date_str, value_str in rows:
            # Quick validation without exceptions
            if not date_pattern.match(date_str):
                continue

            try:
                if value_type == "float":
                    value = float(value_str)
                else:
                    value = int(value_str)
            except (ValueError, TypeError):
                continue

            # Safe date parsing with proper error handling
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
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

    def _plot_data(self, ax: plt.Axes, x_values: list, y_values: list, color: str) -> None:
        """Plot data with automatic marker selection based on data points."""
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

        if len(y_values) <= self.max_count_points_in_charts:
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
            # Add value labels
            for x, y in zip(x_values, y_values, strict=False):
                # Format label based on value type
                if isinstance(y, int):
                    label_text = str(y)
                else:
                    label_text = f"{y:.1f}"

                ax.annotate(
                    label_text,
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=9,
                    alpha=0.8,
                )
        else:
            ax.plot(x_values, y_values, color=plot_color, linestyle="-", linewidth=2, alpha=0.8)

    def _show_no_data_label(self, layout: QLayout, text: str) -> None:
        """Show a 'no data' label in the layout."""
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


class DateOperations:
    """Mixin class for date operations."""

    def _increment_date_widget(self, date_widget) -> None:
        """Increment date widget by one day if not already today.

        Args:
            date_widget: QDateEdit widget to increment

        """
        current_date = date_widget.date()
        today = QDate.currentDate()

        # If current date is today or later, do nothing
        if current_date >= today:
            return

        # Add one day to the current date
        next_date = current_date.addDays(1)
        date_widget.setDate(next_date)

    def _set_date_range(self, from_widget, to_widget, months: int = 0, years: int = 0, all_time: bool = False) -> None:
        """Set date range for date widgets.

        Args:
            from_widget: From date widget
            to_widget: To date widget
            months: Number of months back from today
            years: Number of years back from today
            all_time: If True, sets to earliest available date

        """
        current_date = QDate.currentDate()
        to_widget.setDate(current_date)

        if all_time and self._validate_database_connection():
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

    def _connect_table_signals(self, table_name: str, selection_handler: Callable) -> None:
        """Connect selection change signal for a table.

        Args:
            table_name: Name of the table
            selection_handler: Handler function for selection changes

        """
        view = self.table_config[table_name][0]
        selection_model = view.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(selection_handler)

    def _get_selected_row_id(self, table_name: str) -> int | None:
        """Get the database ID of the currently selected row.

        Args:
            table_name: Name of the table

        Returns:
            Database ID of selected row or None if no selection

        """
        if table_name not in self.table_config:
            return None

        table_view, model_key, _ = self.table_config[table_name]
        model = self.models[model_key]
        if model is None:
            return None

        index = table_view.currentIndex()
        if not index.isValid():
            return None

        row = index.row()
        return int(model.sourceModel().verticalHeaderItem(row).text())

    def _refresh_table(
        self, table_name: str, data_getter: Callable, data_transformer: Callable[[list], list] | None = None
    ) -> None:
        """Generic method to refresh a table with data.

        Args:
            table_name: Name of the table to refresh
            data_getter: Function to get data from database
            data_transformer: Optional function to transform raw data

        """
        if table_name not in self.table_config:
            raise ValueError(f"Unknown table: {table_name}")

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
            date_str: Date string to validate.

        Returns:
            True if the date is in the correct format and represents a valid date.

        """
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
            return False

        try:
            datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return False
        else:
            return True


def requires_database(show_warning: bool = True) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to ensure database connection is available before executing method.

    Args:
        show_warning: If True, shows a QMessageBox warning on connection failure.

    Returns:
        Decorated function that checks database connection first.

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(self: Any, *args: P.args, **kwargs: P.kwargs) -> T | None:
            # Check if this is a Qt signal with index parameter
            if args and len(args) == 1 and isinstance(args[0], int):
                # This is likely a Qt signal callback with index
                if not self._validate_database_connection():
                    if show_warning:
                        from PySide6.QtWidgets import QMessageBox

                        QMessageBox.warning(self, "Database Error", "Database connection not available")
                    return None
                return func(self, *args, **kwargs)
            # Regular method call
            if not self._validate_database_connection():
                if show_warning:
                    from PySide6.QtWidgets import QMessageBox

                    QMessageBox.warning(self, "Database Error", "Database connection not available")
                return None
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
