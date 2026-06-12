---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_operations.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ChartOperationsBase`](#%EF%B8%8F-class-chartoperationsbase)
  - [⚙️ Method `_add_stats_box`](#%EF%B8%8F-method-_add_stats_box)
  - [⚙️ Method `_clear_layout`](#%EF%B8%8F-method-_clear_layout)
  - [⚙️ Method `_fill_missing_periods_with_zeros`](#%EF%B8%8F-method-_fill_missing_periods_with_zeros)
  - [⚙️ Method `_format_default_stats`](#%EF%B8%8F-method-_format_default_stats)
  - [⚙️ Method `_group_data_by_period`](#%EF%B8%8F-method-_group_data_by_period)
  - [⚙️ Method `_group_data_by_period_with_max`](#%EF%B8%8F-method-_group_data_by_period_with_max)
  - [⚙️ Method `_set_y_axis_limits`](#%EF%B8%8F-method-_set_y_axis_limits)
  - [⚙️ Method `_show_no_data_label`](#%EF%B8%8F-method-_show_no_data_label)

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
        self, rows: list[tuple[str, str]], period: str, value_type: str = "float"
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
def _group_data_by_period(self, rows: list[tuple[str, str]], period: str, value_type: str = "float") -> dict[datetime, float | int]
```

Group data by the specified period (Days, Months, Years).

<details>
<summary>Code:</summary>

```python
def _group_data_by_period(
        self, rows: list[tuple[str, str]], period: str, value_type: str = "float"
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
