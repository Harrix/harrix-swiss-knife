"""Shared chart helpers used by tracker applications.

Contains the stable parts of `ChartOperations` that were previously duplicated
in `finance/mixins.py`, `fitness/mixins.py`, `food/mixins.py`, and
`habits/mixins.py`:

- `_add_stats_box`: renders a semi-transparent statistics box on an axes.
- `_show_no_data_label`: inserts a centered `No data` `QLabel` into a layout.
- `_format_default_stats`: formats `Min | Max | Avg` summary.
- `_clear_layout`: removes widgets (and closes matplotlib figures) from a
  layout; parametrised via `close_matplotlib_figures`.
- `_fill_missing_periods_with_zeros`, `_group_data_by_period`,

`_group_data_by_period_with_max`, `_set_y_axis_limits`: shared period
aggregation helpers.

- `_create_chart`, `_format_chart_x_axis`, `_plot_data`: standard line-chart
  rendering used by habits and fitness (food overrides `_plot_data` for calories).

Domain-specific balance charts and other specialised plotting remain in each
app's own `ChartOperations` mixin.

"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.dates import date2num
from matplotlib.ticker import MaxNLocator
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from harrix_swiss_knife.apps.common.chart_extrema_labels import (
    ChartExtremaLabelsConfig,
    annotate_chart_extrema_labels,
)
from harrix_swiss_knife.apps.common.chart_hover import create_chart_canvas
from harrix_swiss_knife.apps.common.chart_page_chrome import install_chart_label_mode_combo as _install_label_mode_combo
from harrix_swiss_knife.apps.common.chart_theme import (
    CHART_LABEL_FONTSIZE,
    CHART_LINEWIDTH,
    CHART_MARKERSIZE,
    CHART_TITLE_FONTSIZE,
    LabelMode,
    chart_annotation_style,
    chart_label_face,
    chart_series_color,
    style_axes,
    themed_figure,
)

# FigureCanvas kept for isinstance checks in `_clear_layout`.

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from PySide6.QtWidgets import QLayout


logger = logging.getLogger(__name__)


class ChartOperationsBase:
    """Mixin with generic chart / layout helpers."""

    max_count_points_in_charts: int

    def _add_stats_box(self, ax: Axes, stats_text: str, color: str | None = None) -> None:
        """Draw a compact bottom stats chip on axes (prefer `_add_stats_caption`).

        Kept for call sites that still pass an axes.

        """
        if color is None:
            color = chart_label_face()
        ax.text(
            0.5,
            0.02,
            stats_text,
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=CHART_LABEL_FONTSIZE,
            bbox={"boxstyle": "round,pad=0.3", "facecolor": color, "alpha": 0.8},
        )

    def _add_stats_caption(self, layout: QLayout, stats_text: str) -> None:
        """Add a compact Min/Max/Avg line under the chart (outside the plot face)."""
        label = QLabel(stats_text)
        label.setObjectName("chartStatsCaption")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {chart_label_face()}; font-size: {CHART_LABEL_FONTSIZE}pt;")
        # Prefer muted ink via palette when available; face is for chips — use muted text QSS.
        from harrix_swiss_knife.apps.common.ui_chrome import muted_caption_qss  # noqa: PLC0415

        label.setStyleSheet(f"{muted_caption_qss(bold=False)} padding: 2px 0px;")
        layout.addWidget(label)

    def _clear_layout(self, layout: QLayout, *, close_matplotlib_figures: bool = True) -> None:
        """Clear all widgets from a layout.

        Args:

        - `layout` (`QLayout`): Layout to clear.
        - `close_matplotlib_figures` (`bool`): When `True` (default), close
          Matplotlib figures attached to removed canvases.

        """
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            if item is None:
                continue

            widget = item.widget()
            if widget is not None:
                if close_matplotlib_figures and isinstance(widget, FigureCanvas) and hasattr(widget, "figure"):
                    try:
                        plt.close(widget.figure)
                    except Exception:
                        logger.exception("Error closing Matplotlib figure")

                widget.hide()
                widget.deleteLater()
                continue

            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout(child_layout, close_matplotlib_figures=close_matplotlib_figures)

    def _create_chart(self, layout: QLayout, data: list[tuple], chart_config: dict[str, Any]) -> None:
        """Create and display a chart with given data and configuration.

        Args:

        - `layout` (`QLayout`): Layout to add chart to.
        - `data` (`list[tuple]`): Chart data as list of (x, y) tuples.
        - `chart_config` (`dict[str, Any]`): Dictionary with chart configuration including:
          - `title`: Chart title
          - `xlabel`: X-axis label
          - `ylabel`: Y-axis label
          - `color`: Line color
          - `show_stats`: Whether to show statistics
          - `stats_unit`: Unit for statistics display
          - `period`: Period for x-axis formatting (Days/Months/Years)
          - `stats_formatter`: Optional function to format statistics
          - `fill_zero_periods`: Whether to fill missing periods with zero values
          - `date_from`: Start date for filling periods
          - `date_to`: End date for filling periods

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
        fig = themed_figure(figsize=(12, 6), dpi=100)
        canvas = create_chart_canvas(fig)
        ax = fig.add_subplot(111)
        style_axes(ax)

        # Extract data
        x_values = [item[0] for item in data]
        y_values = [item[1] for item in data]

        # Count non-zero / non-None values for label display decision
        non_zero_count = sum(1 for y in y_values if y is not None and y != 0)
        label_mode = _resolve_label_mode(chart_config)

        # Plot data
        self._plot_data(
            ax,
            x_values,
            y_values,
            chart_config.get("color") or chart_series_color(0),
            non_zero_count,
            chart_config.get("period"),
            is_calories_chart=bool(chart_config.get("is_calories_chart", False)),
            label_mode=label_mode,
            figure=fig,
        )

        # Customize plot
        ax.set_xlabel(chart_config.get("xlabel", "X"), fontsize=CHART_LABEL_FONTSIZE)
        ax.set_ylabel(chart_config.get("ylabel", "Y"), fontsize=CHART_LABEL_FONTSIZE)
        title = chart_config.get("title", "")
        if title and not chart_config.get("suppress_axes_title", False):
            ax.set_title(title, fontsize=CHART_TITLE_FONTSIZE, fontweight="bold")
        style_axes(ax)

        # Set Y-axis limits to start from non-zero value
        self._set_y_axis_limits(ax, y_values)

        # Format x-axis if dates
        if x_values and isinstance(x_values[0], datetime):
            self._format_chart_x_axis(ax, x_values, chart_config.get("period", "Days"))

        stats_text = ""
        if chart_config.get("show_stats", True) and len(y_values) > 1:
            stats_formatter = chart_config.get("stats_formatter")
            non_zero_values = [y for y in y_values if y is not None and y != 0]
            if non_zero_values:
                if stats_formatter:
                    stats_text = stats_formatter(non_zero_values)
                else:
                    stats_text = self._format_default_stats(non_zero_values, chart_config.get("stats_unit", ""))

        fig.tight_layout()
        layout.addWidget(canvas)
        set_stretch = getattr(layout, "setStretch", None)
        if callable(set_stretch):
            set_stretch(layout.count() - 1, 1)
        if stats_text:
            self._add_stats_caption(layout, stats_text)
        canvas.draw()

    def _fill_missing_periods_with_zeros(
        self, data: list[tuple], period: str, date_from: str | None = None, date_to: str | None = None
    ) -> list[tuple]:
        """Fill missing periods with zero values."""
        if not data:
            return data

        data_dict = {item[0]: item[1] for item in data}
        actual_start_date = min(item[0] for item in data)
        actual_end_date = max(item[0] for item in data)

        if date_from and date_to:
            try:
                user_start_date = datetime.fromisoformat(date_from).replace(tzinfo=UTC)
                user_end_date = datetime.fromisoformat(date_to).replace(tzinfo=UTC)
                start_date = max(actual_start_date, user_start_date)
                end_date = min(actual_end_date, user_end_date)
            except ValueError:
                return data
        else:
            start_date = actual_start_date
            end_date = actual_end_date

        result = []
        current_date = start_date

        if period == "Months":
            current_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            while current_date <= end_date:
                value = data_dict.get(current_date, 0)
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
                value = data_dict.get(current_date, 0)
                result.append((current_date, value))
                current_date = current_date.replace(year=current_date.year + 1)

        else:
            current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

            while current_date <= end_date:
                value = data_dict.get(current_date, 0)
                result.append((current_date, value))
                current_date = current_date + timedelta(days=1)

        return result

    def _format_chart_x_axis(self, ax: Axes, dates: list[datetime], period: str) -> None:
        """Format x-axis for charts based on period and data range.

        Args:

        - `ax` (`Axes`): Matplotlib axes object.
        - `dates` (`list[datetime]`): List of datetime objects.
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

    def _format_default_stats(
        self,
        values: list[float],
        unit: str = "",
        *,
        filter_none: bool = False,
    ) -> str:
        """Format a `Min | Max | Avg` summary line.

        Args:

        - `values` (`list[float]`): Numeric values.
        - `unit` (`str`): Unit suffix. Defaults to `""`.
        - `filter_none` (`bool`): When `True`, remove `None` items first and
          return `No data` if no values remain. Defaults to `False`.

        Returns:

        - `str`: Formatted stats string.

        """
        if filter_none:
            values = [v for v in values if v is not None]
            if not values:
                return "No data"

        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        # Non-breaking space before unit / currency (GOST typography).
        unit_suffix = f"\u00a0{unit}" if unit else ""

        if all(isinstance(v, int) for v in values):
            return (
                f"Min: {int(min_val)}{unit_suffix} | Max: {int(max_val)}{unit_suffix} | Avg: {avg_val:.1f}{unit_suffix}"
            )
        return f"Min: {min_val:.1f}{unit_suffix} | Max: {max_val:.1f}{unit_suffix} | Avg: {avg_val:.1f}{unit_suffix}"

    def _group_data_by_period(
        self, rows: list[tuple[str, str | int | float]], period: str, value_type: str = "float"
    ) -> dict[datetime, float | int]:
        """Group data by the specified period (Days, Months, Years)."""
        grouped = defaultdict(float if value_type == "float" else int)
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for date_str, value_str in rows:
            if not date_pattern.match(date_str):
                continue
            try:
                value = float(value_str) if value_type == "float" else int(value_str)
            except (ValueError, TypeError):
                continue
            try:
                date_obj = datetime.fromisoformat(date_str).replace(tzinfo=UTC)
            except (ValueError, TypeError):
                continue

            if period == "Months":
                key = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "Years":
                key = date_obj.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                key = date_obj

            grouped[key] += value

        return dict(sorted(grouped.items()))

    def _group_data_by_period_with_max(
        self, rows: list[tuple[str, str]], period: str, value_type: str = "float"
    ) -> dict[datetime, float | int]:
        """Group data by period using maximum values per bucket."""
        grouped = defaultdict(list)
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for date_str, value_str in rows:
            if not date_pattern.match(date_str):
                continue
            try:
                value = float(value_str) if value_type == "float" else int(value_str)
            except (ValueError, TypeError):
                continue
            try:
                date_obj = datetime.fromisoformat(date_str).replace(tzinfo=UTC)
            except (ValueError, TypeError):
                continue

            if period == "Months":
                key = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "Years":
                key = date_obj.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                key = date_obj

            grouped[key].append(value)

        max_grouped = {}
        for key, values in grouped.items():
            if values:
                max_grouped[key] = max(values)

        return dict(sorted(max_grouped.items()))

    def _plot_data(
        self,
        ax: Axes,
        x_values: list[datetime],
        y_values: list[float],
        color: str,
        non_zero_count: int | None = None,
        period: str | None = None,
        *,
        is_calories_chart: bool = False,
        label_mode: LabelMode = "auto",
        figure: Any | None = None,
    ) -> None:
        """Plot data with markers for sparse series and Auto/All/Off value labels.

        Args:

        - `ax` (`Axes`): Matplotlib axes object.
        - `x_values` (`list[datetime]`): X-axis values.
        - `y_values` (`list[float]`): Y-axis values.
        - `color` (`str`): Plot color.
        - `non_zero_count` (`int | None`): Number of non-zero points for marker decision.
        - `period` (`str | None`): Time period for formatting labels.
        - `is_calories_chart` (`bool`): Reserved for subclasses (e.g. food calorie zones).
        - `label_mode` (`LabelMode`): `auto` (extrema), `all` (every non-zero when sparse), `off`.
        - `figure` (`Any | None`): Figure for extrema label layout measurement.

        """
        _ = is_calories_chart
        x_nums: list[float] = date2num(x_values)

        color_map = {
            "blue": "b",
            "green": "g",
            "red": "r",
            "orange": "orange",
            "purple": "purple",
            "brown": "brown",
            "pink": "pink",
            "gray": "gray",
            "olive": "olive",
            "cyan": "c",
        }
        plot_color = color_map.get(color, color)
        point_count = non_zero_count if non_zero_count is not None else len(y_values)
        sparse = point_count <= self.max_count_points_in_charts

        if sparse:
            ax.plot(
                x_nums,
                y_values,
                color=plot_color,
                marker="o",
                linestyle="-",
                linewidth=CHART_LINEWIDTH,
                alpha=0.9,
                markersize=CHART_MARKERSIZE,
                markerfacecolor=plot_color,
                markeredgecolor=f"dark{color}" if color in {"blue", "green", "red"} else plot_color,
            )
        else:
            ax.plot(x_nums, y_values, color=plot_color, linestyle="-", linewidth=CHART_LINEWIDTH, alpha=0.9)

        if label_mode == "off" or not x_values or not y_values:
            return

        def _label_for_index(index: int) -> str:
            y = y_values[index]
            if y is None:
                return ""
            text = str(int(y)) if isinstance(y, int) or y == int(y) else f"{y:.1f}"
            x_dt = x_values[index]
            if period == "Years" and hasattr(x_dt, "year"):
                text += f" ({x_dt.year})"
            return text

        if label_mode == "all" and sparse:
            for index, y in enumerate(y_values):
                if y is None or y == 0:
                    continue
                ax.annotate(
                    _label_for_index(index),
                    (x_nums[index], y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    **chart_annotation_style(),
                )
            return

        # Auto: extrema + last point (works for dense Food series without labeling every day).
        from matplotlib.figure import Figure as MplFigure  # noqa: PLC0415

        fig = figure if figure is not None else ax.figure
        if not isinstance(fig, MplFigure):
            return
        annotate_chart_extrema_labels(
            ax,
            fig,
            x_nums,
            [float(y) if y is not None else float("nan") for y in y_values],
            _label_for_index,
            enabled=True,
            config=ChartExtremaLabelsConfig(max_annotations=8 if sparse else 6, max_local_extrema_each=3),
            point_color=plot_color,
        )

    def _set_y_axis_limits(self, ax: Axes, y_values: list[float]) -> None:
        """Set Y-axis limits for clearer non-zero data visualization."""
        if not y_values:
            return

        non_zero_values = [y for y in y_values if y is not None and y != 0]
        if not non_zero_values:
            return

        min_val = min(non_zero_values)
        max_val = max(non_zero_values)

        if min_val == max_val:
            center = min_val
            margin = abs(center) * 0.1 if center != 0 else 1
            ax.set_ylim(center - margin, center + margin)
        else:
            value_range = max_val - min_val
            padding = value_range * 0.1
            lower_limit = max(0, min_val - padding) if min_val > 0 else min_val - padding
            upper_limit = max_val + padding
            ax.set_ylim(lower_limit, upper_limit)

    def _show_no_data_label(self, layout: QLayout, text: str) -> None:
        """Show a centered text label in the layout.

        Args:

        - `layout` (`QLayout`): Layout to populate.
        - `text` (`str`): Text to display.

        """
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)


def install_chart_label_mode_combo(
    host: Any,
    layout: Any,
    *,
    replace_widget: Any | None = None,
    on_changed: Any | None = None,
    insert_index: int | None = None,
) -> Any:
    """Add or reuse Labels Auto/All/Off combo on a chart toolbar layout.

    Delegates to `chart_page_chrome.install_chart_label_mode_combo`.

    """
    return _install_label_mode_combo(
        host,
        layout,
        replace_widget=replace_widget,
        on_changed=on_changed,
        insert_index=insert_index,
    )


def label_mode_from_combo(host: Any) -> LabelMode:
    """Read Auto / All / Off from `comboBox_chart_label_mode` on `host`."""
    combo = getattr(host, "comboBox_chart_label_mode", None)
    if combo is not None:
        data = combo.currentData()
        if data in {"auto", "all", "off"}:
            return data  # type: ignore[return-value]
    return "auto"


def _resolve_label_mode(chart_config: dict[str, Any]) -> LabelMode:
    """Map chart config / legacy show_labels flags to Auto / All / Off."""
    raw = chart_config.get("label_mode")
    if raw in {"auto", "all", "off"}:
        return raw  # type: ignore[return-value]
    if chart_config.get("show_labels") is False:
        return "off"
    if chart_config.get("show_all_labels") is True:
        return "all"
    return "auto"
