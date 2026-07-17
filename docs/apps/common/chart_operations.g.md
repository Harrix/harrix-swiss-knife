---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_operations.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ChartOperationsBase`](#️-class-chartoperationsbase)
  - [⚙️ Method `_add_stats_box`](#️-method-_add_stats_box)
  - [⚙️ Method `_clear_layout`](#️-method-_clear_layout)
  - [⚙️ Method `_create_chart`](#️-method-_create_chart)
  - [⚙️ Method `_fill_missing_periods_with_zeros`](#️-method-_fill_missing_periods_with_zeros)
  - [⚙️ Method `_format_chart_x_axis`](#️-method-_format_chart_x_axis)
  - [⚙️ Method `_format_default_stats`](#️-method-_format_default_stats)
  - [⚙️ Method `_group_data_by_period`](#️-method-_group_data_by_period)
  - [⚙️ Method `_group_data_by_period_with_max`](#️-method-_group_data_by_period_with_max)
  - [⚙️ Method `_plot_data`](#️-method-_plot_data)
  - [⚙️ Method `_set_y_axis_limits`](#️-method-_set_y_axis_limits)
  - [⚙️ Method `_show_no_data_label`](#️-method-_show_no_data_label)

</details>

## 🏛️ Class `ChartOperationsBase`

```python
class ChartOperationsBase
```

Mixin with generic chart / layout helpers.

<details>
<summary>Code:</summary>

```python
class ChartOperationsBase:

    max_count_points_in_charts: int

    def _add_stats_box(self, ax: Axes, stats_text: str, color: str = "lightgray") -> None:
        """Add a statistics box at the bottom-center of an axes.

        Args:

        - `ax` (`Axes`): Matplotlib axes object.
        - `stats_text` (`str`): Text to display.
        - `color` (`str`): Background color. Defaults to `"lightgray"`.

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

    def _clear_layout(self, layout: QLayout, *, close_matplotlib_figures: bool = True) -> None:
        """Clear all widgets from a layout.

        Args:

        - `layout` (`QLayout`): Layout to clear.
        - `close_matplotlib_figures` (`bool`): When True (default), close
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
                    except Exception as e:
                        print(f"Error closing Matplotlib figure: {e}")

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
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Extract data
        x_values = [item[0] for item in data]
        y_values = [item[1] for item in data]

        # Count non-zero values for label display decision
        non_zero_count = sum(1 for y in y_values if y != 0)

        # Plot data
        self._plot_data(
            ax, x_values, y_values, chart_config.get("color", "b"), non_zero_count, chart_config.get("period")
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
                # Filter out zero values for statistics
                non_zero_values = [y for y in y_values if y != 0]
                if non_zero_values:
                    stats_text = stats_formatter(non_zero_values)
                    self._add_stats_box(ax, stats_text)
            else:
                non_zero_values = [y for y in y_values if y != 0]
                if non_zero_values:
                    stats_text = self._format_default_stats(non_zero_values, chart_config.get("stats_unit", ""))
                    self._add_stats_box(ax, stats_text)

        fig.tight_layout()
        layout.addWidget(canvas)
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
        - `filter_none` (`bool`): When True, remove `None` items first and
        return `"No data"` if no values remain. Defaults to `False`.

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
        unit_suffix = f" {unit}" if unit else ""

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
    ) -> None:
        """Plot data with automatic marker selection based on data points.

        Args:

        - `ax` (`Axes`): Matplotlib axes object.
        - `x_values` (`list[datetime]`): X-axis values.
        - `y_values` (`list[float]`): Y-axis values.
        - `color` (`str`): Plot color.
        - `non_zero_count` (`int | None`): Number of non-zero points for label decision. Defaults to `None`.
        - `period` (`str | None`): Time period for formatting labels. Defaults to `None`.

        """
        # Convert datetime to numerical date values for type safety and plotting
        x_nums: list[float] = date2num(x_values)  # This satisfies the type checker

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

        if point_count_for_labels <= self.max_count_points_in_charts:
            ax.plot(
                x_nums,  # Use numerical x-values
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
            # Add value labels only for non-zero values
            for x_dt, y in zip(x_values, y_values, strict=False):
                if y != 0:  # Only label non-zero points
                    # Format label based on value type - remove unnecessary .0
                    label_text = str(int(y)) if isinstance(y, int) or y == int(y) else f"{y:.1f}"

                    # Add year in parentheses for Years period
                    if period == "Years" and hasattr(x_dt, "year"):
                        label_text += f" ({x_dt.year})"

                    # Annotate using numerical x-value
                    ax.annotate(
                        label_text,
                        (date2num(x_dt), y),  # Convert to num here for consistency
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha="center",
                        fontsize=9,
                        alpha=0.8,
                        # Add white outline for better readability
                        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                    )
        else:
            ax.plot(x_nums, y_values, color=plot_color, linestyle="-", linewidth=2, alpha=0.8)  # Use numerical x-values

            # Always label the last point, even when there are many points
            if x_values and y_values:
                last_x_dt = x_values[-1]
                last_y = y_values[-1]

                # Only label if the last point is non-zero
                if last_y != 0:
                    # Format label based on value type - remove unnecessary .0
                    if isinstance(last_y, int) or last_y == int(last_y):
                        label_text = str(int(last_y))
                    else:
                        label_text = f"{last_y:.1f}"

                    # Add year in parentheses for Years period
                    if period == "Years" and hasattr(last_x_dt, "year"):
                        label_text += f" ({last_x_dt.year})"

                    # Annotate using numerical x-value
                    ax.annotate(
                        label_text,
                        (date2num(last_x_dt), last_y),  # Convert to num here for consistency
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha="center",
                        fontsize=9,
                        alpha=0.8,
                        # Add white outline for better readability
                        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
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
```

</details>

### ⚙️ Method `_add_stats_box`

```python
def _add_stats_box(self, ax: Axes, stats_text: str, color: str = "lightgray") -> None
```

Add a statistics box at the bottom-center of an axes.

Args:

- `ax` (`Axes`): Matplotlib axes object.
- `stats_text` (`str`): Text to display.
- `color` (`str`): Background color. Defaults to `"lightgray"`.

<details>
<summary>Code:</summary>

```python
def _add_stats_box(self, ax: Axes, stats_text: str, color: str = "lightgray") -> None:
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
```

</details>

### ⚙️ Method `_clear_layout`

```python
def _clear_layout(self, layout: QLayout) -> None
```

Clear all widgets from a layout.

Args:

- `layout` (`QLayout`): Layout to clear.
- `close_matplotlib_figures` (`bool`): When True (default), close
  Matplotlib figures attached to removed canvases.

<details>
<summary>Code:</summary>

```python
def _clear_layout(self, layout: QLayout, *, close_matplotlib_figures: bool = True) -> None:
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            if item is None:
                continue

            widget = item.widget()
            if widget is not None:
                if close_matplotlib_figures and isinstance(widget, FigureCanvas) and hasattr(widget, "figure"):
                    try:
                        plt.close(widget.figure)
                    except Exception as e:
                        print(f"Error closing Matplotlib figure: {e}")

                widget.hide()
                widget.deleteLater()
                continue

            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout(child_layout, close_matplotlib_figures=close_matplotlib_figures)
```

</details>

### ⚙️ Method `_create_chart`

```python
def _create_chart(self, layout: QLayout, data: list[tuple], chart_config: dict[str, Any]) -> None
```

Create and display a chart with given data and configuration.

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

<details>
<summary>Code:</summary>

```python
def _create_chart(self, layout: QLayout, data: list[tuple], chart_config: dict[str, Any]) -> None:
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

        # Count non-zero values for label display decision
        non_zero_count = sum(1 for y in y_values if y != 0)

        # Plot data
        self._plot_data(
            ax, x_values, y_values, chart_config.get("color", "b"), non_zero_count, chart_config.get("period")
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
                # Filter out zero values for statistics
                non_zero_values = [y for y in y_values if y != 0]
                if non_zero_values:
                    stats_text = stats_formatter(non_zero_values)
                    self._add_stats_box(ax, stats_text)
            else:
                non_zero_values = [y for y in y_values if y != 0]
                if non_zero_values:
                    stats_text = self._format_default_stats(non_zero_values, chart_config.get("stats_unit", ""))
                    self._add_stats_box(ax, stats_text)

        fig.tight_layout()
        layout.addWidget(canvas)
        canvas.draw()
```

</details>

### ⚙️ Method `_fill_missing_periods_with_zeros`

```python
def _fill_missing_periods_with_zeros(self, data: list[tuple], period: str, date_from: str | None = None, date_to: str | None = None) -> list[tuple]
```

Fill missing periods with zero values.

<details>
<summary>Code:</summary>

```python
def _fill_missing_periods_with_zeros(
        self, data: list[tuple], period: str, date_from: str | None = None, date_to: str | None = None
    ) -> list[tuple]:
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
```

</details>

### ⚙️ Method `_format_chart_x_axis`

```python
def _format_chart_x_axis(self, ax: Axes, dates: list[datetime], period: str) -> None
```

Format x-axis for charts based on period and data range.

Args:

- `ax` (`Axes`): Matplotlib axes object.
- `dates` (`list[datetime]`): List of datetime objects.
- `period` (`str`): Time period for formatting.

<details>
<summary>Code:</summary>

```python
def _format_chart_x_axis(self, ax: Axes, dates: list[datetime], period: str) -> None:
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
```

</details>

### ⚙️ Method `_format_default_stats`

```python
def _format_default_stats(self, values: list[float], unit: str = "") -> str
```

Format a `Min | Max | Avg` summary line.

Args:

- `values` (`list[float]`): Numeric values.
- `unit` (`str`): Unit suffix. Defaults to `""`.
- `filter_none` (`bool`): When True, remove `None` items first and
  return `"No data"` if no values remain. Defaults to `False`.

Returns:

- `str`: Formatted stats string.

<details>
<summary>Code:</summary>

```python
def _format_default_stats(
        self,
        values: list[float],
        unit: str = "",
        *,
        filter_none: bool = False,
    ) -> str:
        if filter_none:
            values = [v for v in values if v is not None]
            if not values:
                return "No data"

        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        unit_suffix = f" {unit}" if unit else ""

        if all(isinstance(v, int) for v in values):
            return (
                f"Min: {int(min_val)}{unit_suffix} | Max: {int(max_val)}{unit_suffix} | Avg: {avg_val:.1f}{unit_suffix}"
            )
        return f"Min: {min_val:.1f}{unit_suffix} | Max: {max_val:.1f}{unit_suffix} | Avg: {avg_val:.1f}{unit_suffix}"
```

</details>

### ⚙️ Method `_group_data_by_period`

```python
def _group_data_by_period(self, rows: list[tuple[str, str | int | float]], period: str, value_type: str = "float") -> dict[datetime, float | int]
```

Group data by the specified period (Days, Months, Years).

<details>
<summary>Code:</summary>

```python
def _group_data_by_period(
        self, rows: list[tuple[str, str | int | float]], period: str, value_type: str = "float"
    ) -> dict[datetime, float | int]:
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
```

</details>

### ⚙️ Method `_group_data_by_period_with_max`

```python
def _group_data_by_period_with_max(self, rows: list[tuple[str, str]], period: str, value_type: str = "float") -> dict[datetime, float | int]
```

Group data by period using maximum values per bucket.

<details>
<summary>Code:</summary>

```python
def _group_data_by_period_with_max(
        self, rows: list[tuple[str, str]], period: str, value_type: str = "float"
    ) -> dict[datetime, float | int]:
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
```

</details>

### ⚙️ Method `_plot_data`

```python
def _plot_data(self, ax: Axes, x_values: list[datetime], y_values: list[float], color: str, non_zero_count: int | None = None, period: str | None = None) -> None
```

Plot data with automatic marker selection based on data points.

Args:

- `ax` (`Axes`): Matplotlib axes object.
- `x_values` (`list[datetime]`): X-axis values.
- `y_values` (`list[float]`): Y-axis values.
- `color` (`str`): Plot color.
- `non_zero_count` (`int | None`): Number of non-zero points for label decision. Defaults to `None`.
- `period` (`str | None`): Time period for formatting labels. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def _plot_data(
        self,
        ax: Axes,
        x_values: list[datetime],
        y_values: list[float],
        color: str,
        non_zero_count: int | None = None,
        period: str | None = None,
    ) -> None:
        # Convert datetime to numerical date values for type safety and plotting
        x_nums: list[float] = date2num(x_values)  # This satisfies the type checker

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

        if point_count_for_labels <= self.max_count_points_in_charts:
            ax.plot(
                x_nums,  # Use numerical x-values
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
            # Add value labels only for non-zero values
            for x_dt, y in zip(x_values, y_values, strict=False):
                if y != 0:  # Only label non-zero points
                    # Format label based on value type - remove unnecessary .0
                    label_text = str(int(y)) if isinstance(y, int) or y == int(y) else f"{y:.1f}"

                    # Add year in parentheses for Years period
                    if period == "Years" and hasattr(x_dt, "year"):
                        label_text += f" ({x_dt.year})"

                    # Annotate using numerical x-value
                    ax.annotate(
                        label_text,
                        (date2num(x_dt), y),  # Convert to num here for consistency
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha="center",
                        fontsize=9,
                        alpha=0.8,
                        # Add white outline for better readability
                        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                    )
        else:
            ax.plot(x_nums, y_values, color=plot_color, linestyle="-", linewidth=2, alpha=0.8)  # Use numerical x-values

            # Always label the last point, even when there are many points
            if x_values and y_values:
                last_x_dt = x_values[-1]
                last_y = y_values[-1]

                # Only label if the last point is non-zero
                if last_y != 0:
                    # Format label based on value type - remove unnecessary .0
                    if isinstance(last_y, int) or last_y == int(last_y):
                        label_text = str(int(last_y))
                    else:
                        label_text = f"{last_y:.1f}"

                    # Add year in parentheses for Years period
                    if period == "Years" and hasattr(last_x_dt, "year"):
                        label_text += f" ({last_x_dt.year})"

                    # Annotate using numerical x-value
                    ax.annotate(
                        label_text,
                        (date2num(last_x_dt), last_y),  # Convert to num here for consistency
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha="center",
                        fontsize=9,
                        alpha=0.8,
                        # Add white outline for better readability
                        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                    )
```

</details>

### ⚙️ Method `_set_y_axis_limits`

```python
def _set_y_axis_limits(self, ax: Axes, y_values: list[float]) -> None
```

Set Y-axis limits for clearer non-zero data visualization.

<details>
<summary>Code:</summary>

```python
def _set_y_axis_limits(self, ax: Axes, y_values: list[float]) -> None:
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
```

</details>

### ⚙️ Method `_show_no_data_label`

```python
def _show_no_data_label(self, layout: QLayout, text: str) -> None
```

Show a centered text label in the layout.

Args:

- `layout` (`QLayout`): Layout to populate.
- `text` (`str`): Text to display.

<details>
<summary>Code:</summary>

```python
def _show_no_data_label(self, layout: QLayout, text: str) -> None:
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
```

</details>
