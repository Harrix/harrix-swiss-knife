"""Mixin classes for food tracker application.

This module contains reusable mixin classes that provide common functionality
for database operations, table management, chart creation, and date handling.

"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from matplotlib.dates import date2num

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.chart_operations import ChartOperationsBase
from harrix_swiss_knife.apps.common.db_guard import requires_database
from harrix_swiss_knife.apps.common.qt_mixins import AutoSaveMixin, DateMixin, TableOperations, ValidationMixin
from harrix_swiss_knife.apps.common.text_case import capitalize_first_letter
from harrix_swiss_knife.apps.food.delegates import parse_is_drink_cell

if TYPE_CHECKING:
    from collections.abc import Callable

    from matplotlib.axes import Axes
    from PySide6.QtGui import QStandardItemModel
    from PySide6.QtWidgets import QLayout

__all__ = [
    "AutoSaveOperations",
    "ChartOperations",
    "DateOperations",
    "TableOperations",
    "ValidationOperations",
    "has_period_gap",
    "iter_nonempty_chart_segments",
    "requires_database",
]


class AutoSaveOperations(AutoSaveMixin):
    """Mixin class for auto-save operations."""

    db_manager: Any
    _validate_database_connection: Callable[[], bool]
    _update_comboboxes: Callable[[], None]
    update_filter_comboboxes: Callable[[], None]
    _is_valid_date: Callable[[str], bool]

    def _get_save_handlers(self) -> dict[str, Callable[..., None]]:
        return {"food_log": self._save_food_log_data}

    def _save_food_log_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save food log data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        # Get data from model columns
        name = capitalize_first_letter(model.data(model.index(row, 0)) or "")
        is_drink_str = model.data(model.index(row, 1)) or ""
        weight_str = model.data(model.index(row, 2)) or ""
        calories_per_100g_str = model.data(model.index(row, 3)) or ""
        portion_calories_str = model.data(model.index(row, 4)) or ""
        date = model.data(model.index(row, 6)) or ""
        name_en = capitalize_first_letter(model.data(model.index(row, 7)) or "")

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
            else:
                message_box.warning(None, "Validation Error", "Weight is required")
                return
        except (ValueError, TypeError):
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
            name=name,
            name_en=name_en or None,
            weight=weight,
            portion_calories=portion_calories,
            is_drink=is_drink,
        ):
            message_box.warning(None, "Database Error", "Failed to save food log record")


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

    def _format_default_stats(self, values: list, unit: str = "", *, filter_none: bool = True) -> str:
        """Format default statistics text.

        Food's historical behavior filters out `None` values and returns
        `No data` when nothing remains; overridden here to keep that
        default while delegating to the shared implementation.

        """
        return super()._format_default_stats(values, unit, filter_none=filter_none)

    def _plot_data(
        self,
        ax: Axes,
        x_values: list,
        y_values: list,
        color: str,
        non_zero_count: int | None = None,  # noqa: ARG002
        period: str | None = None,
        *,
        is_calories_chart: bool = False,
    ) -> None:
        """Plot data; calorie charts get zone lines and per-point colors."""
        segments = iter_nonempty_chart_segments(x_values, y_values, period)
        plotted_x = [x_value for segment_x, _segment_y in segments for x_value in segment_x]
        plotted_y = [y_value for _segment_x, segment_y in segments for y_value in segment_y]
        if not is_calories_chart:
            for segment_x, segment_y in segments:
                super()._plot_data(
                    ax,
                    segment_x,
                    segment_y,
                    color,
                    len(segment_y),
                    period,
                    is_calories_chart=False,
                )
            return

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

        min_points_for_line = 2
        for segment_x, segment_y in segments:
            if len(segment_x) < min_points_for_line:
                continue
            ax.plot(date2num(segment_x), segment_y, color="gray", linestyle="-", linewidth=1, alpha=0.6, zorder=2)

        if not plotted_x:
            return

        point_colors: list[str] = []
        level_low_calories = 1800
        level_medium_low_calories = 2100
        level_medium_high_calories = 2500
        for y in plotted_y:
            if y <= level_low_calories:
                point_colors.append("#90EE90")
            elif y <= level_medium_low_calories:
                point_colors.append("#FFFFE0")
            elif y <= level_medium_high_calories:
                point_colors.append("#FFE4C4")
            else:
                point_colors.append("#FFC0CB")

        ax.scatter(
            date2num(plotted_x),
            plotted_y,
            c=point_colors,
            s=36,
            zorder=3,
            edgecolors="gray",
            linewidths=0.5,
        )

        maximum_count_points_for_labels = 100
        if len(plotted_x) < maximum_count_points_for_labels:
            for x_dt, y in zip(plotted_x, plotted_y, strict=False):
                label_text = str(int(y)) if isinstance(y, int) or y == int(y) else f"{y:.1f}"
                if period == "Years" and hasattr(x_dt, "year"):
                    label_text += f" ({x_dt.year})"
                ax.annotate(
                    label_text,
                    (date2num(x_dt), y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=9,
                    alpha=0.8,
                    bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                    zorder=4,
                )


class DateOperations(DateMixin):
    """Mixin class for date operations."""

    db_manager: Any
    _validate_database_connection: Callable[[], bool]


class ValidationOperations(ValidationMixin):
    """Mixin class for validation operations."""


def has_period_gap(previous: datetime, current: datetime, period: str | None) -> bool:
    """Return whether `current` skips at least one period after `previous`."""
    if period == "Months":
        return (current.year - previous.year) * 12 + (current.month - previous.month) > 1
    if period == "Years":
        return current.year - previous.year > 1
    previous_day = previous.date() if isinstance(previous, datetime) else previous
    current_day = current.date() if isinstance(current, datetime) else current
    return (current_day - previous_day).days > 1


def iter_nonempty_chart_segments(
    x_values: list,
    y_values: list,
    period: str | None,
) -> list[tuple[list, list]]:
    """Split chart series into segments, skipping empty values and period gaps."""
    segments: list[tuple[list, list]] = []
    current_x: list = []
    current_y: list = []
    previous_x = None
    for x_value, y_value in zip(x_values, y_values, strict=False):
        if y_value is None or y_value == 0:
            if current_x:
                segments.append((current_x, current_y))
                current_x, current_y = [], []
            previous_x = None
            continue
        if previous_x is not None and has_period_gap(previous_x, x_value, period):
            if current_x:
                segments.append((current_x, current_y))
            current_x, current_y = [], []
        current_x.append(x_value)
        current_y.append(y_value)
        previous_x = x_value
    if current_x:
        segments.append((current_x, current_y))
    return segments
