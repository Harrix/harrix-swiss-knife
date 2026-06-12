---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `mixins.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AutoSaveOperations`](#%EF%B8%8F-class-autosaveoperations)
  - [⚙️ Method `_auto_save_row`](#%EF%B8%8F-method-_auto_save_row)
  - [⚙️ Method `_save_exercise_data`](#%EF%B8%8F-method-_save_exercise_data)
  - [⚙️ Method `_save_process_data`](#%EF%B8%8F-method-_save_process_data)
  - [⚙️ Method `_save_type_data`](#%EF%B8%8F-method-_save_type_data)
  - [⚙️ Method `_save_weight_data`](#%EF%B8%8F-method-_save_weight_data)
- [🏛️ Class `ChartOperations`](#%EF%B8%8F-class-chartoperations)
  - [⚙️ Method `_create_chart`](#%EF%B8%8F-method-_create_chart)
  - [⚙️ Method `_format_chart_x_axis`](#%EF%B8%8F-method-_format_chart_x_axis)
  - [⚙️ Method `_plot_data`](#%EF%B8%8F-method-_plot_data)
- [🏛️ Class `DateOperations`](#%EF%B8%8F-class-dateoperations)
- [🏛️ Class `ValidationOperations`](#%EF%B8%8F-class-validationoperations)

</details>

## 🏛️ Class `AutoSaveOperations`

```python
class AutoSaveOperations
```

Mixin class for auto-save operations.

<details>
<summary>Code:</summary>

```python
class AutoSaveOperations:

    # Expected attributes from main class
    db_manager: Any
    _validate_database_connection: Callable[[], bool]
    _update_comboboxes: Callable[..., None]
    update_filter_comboboxes: Callable[[], None]
    _is_valid_date: Callable[[str], bool]

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
        calories_per_unit_str = model.data(model.index(row, 3)) or "0"

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
        if not self.db_manager.update_exercise(
            int(row_id),
            name.strip(),
            unit.strip(),
            is_type_required=is_type_required,
            calories_per_unit=calories_per_unit,
        ):
            message_box.warning(None, "Database Error", "Failed to save exercise record")
        else:
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
        calories_modifier_str = model.data(model.index(row, 2)) or "1.0"

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

        # Update database
        if not self.db_manager.update_exercise_type(int(row_id), ex_id, type_name.strip(), calories_modifier):
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
```

</details>

### ⚙️ Method `_auto_save_row`

```python
def _auto_save_row(self, table_name: str, model: QStandardItemModel, row: int, row_id: str) -> None
```

Auto-save table row data.

Args:

- `table_name` (`str`): Name of the table.
- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _auto_save_row(self, table_name: str, model: QStandardItemModel, row: int, row_id: str) -> None:
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
                message_box.warning(None, "Auto-save Error", f"Failed to save {table_name} row: {e!s}")
```

</details>

### ⚙️ Method `_save_exercise_data`

```python
def _save_exercise_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save exercise data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_exercise_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_type_required_str = model.data(model.index(row, 2)) or "0"
        calories_per_unit_str = model.data(model.index(row, 3)) or "0"

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
        if not self.db_manager.update_exercise(
            int(row_id),
            name.strip(),
            unit.strip(),
            is_type_required=is_type_required,
            calories_per_unit=calories_per_unit,
        ):
            message_box.warning(None, "Database Error", "Failed to save exercise record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()
```

</details>

### ⚙️ Method `_save_process_data`

```python
def _save_process_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save process record data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_process_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
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
```

</details>

### ⚙️ Method `_save_type_data`

```python
def _save_type_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save exercise type data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_type_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        exercise_name = model.data(model.index(row, 0)) or ""
        type_name = model.data(model.index(row, 1)) or ""
        calories_modifier_str = model.data(model.index(row, 2)) or "1.0"

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

        # Update database
        if not self.db_manager.update_exercise_type(int(row_id), ex_id, type_name.strip(), calories_modifier):
            message_box.warning(None, "Database Error", "Failed to save type record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()
```

</details>

### ⚙️ Method `_save_weight_data`

```python
def _save_weight_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save weight data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_weight_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
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
```

</details>

## 🏛️ Class `ChartOperations`

```python
class ChartOperations(ChartOperationsBase)
```

Mixin class for chart operations.

<details>
<summary>Code:</summary>

```python
class ChartOperations(ChartOperationsBase):

    # Expected attributes from main class
    max_count_points_in_charts: int

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

## 🏛️ Class `DateOperations`

```python
class DateOperations(DateMixin)
```

Mixin class for date operations.

<details>
<summary>Code:</summary>

```python
class DateOperations(DateMixin):

    db_manager: Any
    _validate_database_connection: Callable[[], bool]
```

</details>

## 🏛️ Class `ValidationOperations`

```python
class ValidationOperations(ValidationMixin)
```

Mixin class for validation operations.

<details>
<summary>Code:</summary>

```python
class ValidationOperations(ValidationMixin):
```

</details>
