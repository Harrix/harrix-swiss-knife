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
  - [⚙️ Method `_save_account_data`](#%EF%B8%8F-method-_save_account_data)
  - [⚙️ Method `_save_category_data`](#%EF%B8%8F-method-_save_category_data)
  - [⚙️ Method `_save_currency_data`](#%EF%B8%8F-method-_save_currency_data)
  - [⚙️ Method `_save_transaction_data`](#%EF%B8%8F-method-_save_transaction_data)
- [🏛️ Class `ChartOperations`](#%EF%B8%8F-class-chartoperations)
  - [⚙️ Method `_add_stats_box`](#%EF%B8%8F-method-_add_stats_box)
  - [⚙️ Method `_clear_layout`](#%EF%B8%8F-method-_clear_layout)
  - [⚙️ Method `_create_chart`](#%EF%B8%8F-method-_create_chart)
  - [⚙️ Method `_format_chart_x_axis`](#%EF%B8%8F-method-_format_chart_x_axis)
  - [⚙️ Method `_format_default_stats`](#%EF%B8%8F-method-_format_default_stats)
  - [⚙️ Method `_plot_data`](#%EF%B8%8F-method-_plot_data)
  - [⚙️ Method `_show_no_data_label`](#%EF%B8%8F-method-_show_no_data_label)
- [🏛️ Class `DateOperations`](#%EF%B8%8F-class-dateoperations)
  - [⚙️ Method `_increment_date_widget`](#%EF%B8%8F-method-_increment_date_widget)
  - [⚙️ Method `_set_date_range`](#%EF%B8%8F-method-_set_date_range)
- [🏛️ Class `TableOperations`](#%EF%B8%8F-class-tableoperations)
  - [⚙️ Method `_connect_table_signals`](#%EF%B8%8F-method-_connect_table_signals)
  - [⚙️ Method `_get_selected_row_id`](#%EF%B8%8F-method-_get_selected_row_id)
  - [⚙️ Method `_refresh_table`](#%EF%B8%8F-method-_refresh_table)
- [🏛️ Class `ValidationOperations`](#%EF%B8%8F-class-validationoperations)
  - [⚙️ Method `_is_valid_date`](#%EF%B8%8F-method-_is_valid_date)
- [🔧 Function `requires_database`](#-function-requires_database)

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
    _update_comboboxes: Callable[[], None]
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
            "transactions": self._save_transaction_data,
            "categories": self._save_category_data,
            "accounts": self._save_account_data,
            "currencies": self._save_currency_data,
        }

        handler = save_handlers.get(table_name)
        if handler:
            try:
                handler(model, row, row_id)
            except Exception as e:
                QMessageBox.warning(None, "Auto-save Error", f"Failed to save {table_name} row: {e!s}")

    def _save_account_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save account data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        name = model.data(model.index(row, 1)) or ""
        currency_code = model.data(model.index(row, 2)) or ""
        balance_str = model.data(model.index(row, 3)) or "0"
        is_liquid_str = model.data(model.index(row, 4)) or "0"
        is_cash_str = model.data(model.index(row, 5)) or "0"

        # Validate account name
        if not name.strip():
            QMessageBox.warning(None, "Validation Error", "Account name cannot be empty")
            return

        # Convert balance to float
        try:
            balance = float(balance_str)
        except (ValueError, TypeError):
            QMessageBox.warning(None, "Validation Error", f"Invalid balance value: {balance_str}")
            return

        # Get currency ID
        currency_id = self.db_manager.get_id("currencies", "code", currency_code)
        if currency_id is None:
            QMessageBox.warning(None, "Validation Error", f"Currency '{currency_code}' not found")
            return

        # Convert flags to boolean
        is_liquid = is_liquid_str == "1"
        is_cash = is_cash_str == "1"

        # Update database
        if not self.db_manager.update_account(int(row_id), name.strip(), currency_id, balance, is_liquid, is_cash):
            QMessageBox.warning(None, "Database Error", "Failed to save account record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_category_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save category data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        name = model.data(model.index(row, 1)) or ""
        category_type = model.data(model.index(row, 2)) or ""

        # Validate category name
        if not name.strip():
            QMessageBox.warning(None, "Validation Error", "Category name cannot be empty")
            return

        # Update database
        if not self.db_manager.update_category(int(row_id), name.strip(), category_type):
            QMessageBox.warning(None, "Database Error", "Failed to save category record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_currency_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save currency data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        code = model.data(model.index(row, 1)) or ""
        name = model.data(model.index(row, 2)) or ""
        symbol = model.data(model.index(row, 3)) or ""

        # Validate inputs
        if not code.strip():
            QMessageBox.warning(None, "Validation Error", "Currency code cannot be empty")
            return

        if not name.strip():
            QMessageBox.warning(None, "Validation Error", "Currency name cannot be empty")
            return

        # Update database
        if not self.db_manager.update_currency(int(row_id), code.strip(), name.strip(), symbol.strip()):
            QMessageBox.warning(None, "Database Error", "Failed to save currency record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_transaction_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save transaction data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        transaction_type = model.data(model.index(row, 1)) or ""
        amount_str = model.data(model.index(row, 2)) or "0"
        currency_symbol = model.data(model.index(row, 3)) or ""
        category_name = model.data(model.index(row, 4)) or ""
        description = model.data(model.index(row, 5)) or ""
        date = model.data(model.index(row, 6)) or ""

        # Validate date format
        if not self._is_valid_date(date):
            QMessageBox.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Validate amount
        try:
            amount = float(amount_str)
        except (ValueError, TypeError):
            QMessageBox.warning(None, "Validation Error", f"Invalid amount value: {amount_str}")
            return

        # Get currency ID
        currency_id = self.db_manager.get_id("currencies", "symbol", currency_symbol)
        if currency_id is None:
            QMessageBox.warning(None, "Validation Error", f"Currency '{currency_symbol}' not found")
            return

        # Get category ID
        category_id = self.db_manager.get_id("categories", "name", category_name)
        if category_id is None:
            QMessageBox.warning(None, "Validation Error", f"Category '{category_name}' not found")
            return

        # Update database
        if not self.db_manager.update_transaction(
            int(row_id), transaction_type, amount, currency_id, category_id, description, date
        ):
            QMessageBox.warning(None, "Database Error", "Failed to save transaction record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()
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
            "transactions": self._save_transaction_data,
            "categories": self._save_category_data,
            "accounts": self._save_account_data,
            "currencies": self._save_currency_data,
        }

        handler = save_handlers.get(table_name)
        if handler:
            try:
                handler(model, row, row_id)
            except Exception as e:
                QMessageBox.warning(None, "Auto-save Error", f"Failed to save {table_name} row: {e!s}")
```

</details>

### ⚙️ Method `_save_account_data`

```python
def _save_account_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save account data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_account_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        name = model.data(model.index(row, 1)) or ""
        currency_code = model.data(model.index(row, 2)) or ""
        balance_str = model.data(model.index(row, 3)) or "0"
        is_liquid_str = model.data(model.index(row, 4)) or "0"
        is_cash_str = model.data(model.index(row, 5)) or "0"

        # Validate account name
        if not name.strip():
            QMessageBox.warning(None, "Validation Error", "Account name cannot be empty")
            return

        # Convert balance to float
        try:
            balance = float(balance_str)
        except (ValueError, TypeError):
            QMessageBox.warning(None, "Validation Error", f"Invalid balance value: {balance_str}")
            return

        # Get currency ID
        currency_id = self.db_manager.get_id("currencies", "code", currency_code)
        if currency_id is None:
            QMessageBox.warning(None, "Validation Error", f"Currency '{currency_code}' not found")
            return

        # Convert flags to boolean
        is_liquid = is_liquid_str == "1"
        is_cash = is_cash_str == "1"

        # Update database
        if not self.db_manager.update_account(int(row_id), name.strip(), currency_id, balance, is_liquid, is_cash):
            QMessageBox.warning(None, "Database Error", "Failed to save account record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()
```

</details>

### ⚙️ Method `_save_category_data`

```python
def _save_category_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save category data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_category_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        name = model.data(model.index(row, 1)) or ""
        category_type = model.data(model.index(row, 2)) or ""

        # Validate category name
        if not name.strip():
            QMessageBox.warning(None, "Validation Error", "Category name cannot be empty")
            return

        # Update database
        if not self.db_manager.update_category(int(row_id), name.strip(), category_type):
            QMessageBox.warning(None, "Database Error", "Failed to save category record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()
```

</details>

### ⚙️ Method `_save_currency_data`

```python
def _save_currency_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save currency data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_currency_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        code = model.data(model.index(row, 1)) or ""
        name = model.data(model.index(row, 2)) or ""
        symbol = model.data(model.index(row, 3)) or ""

        # Validate inputs
        if not code.strip():
            QMessageBox.warning(None, "Validation Error", "Currency code cannot be empty")
            return

        if not name.strip():
            QMessageBox.warning(None, "Validation Error", "Currency name cannot be empty")
            return

        # Update database
        if not self.db_manager.update_currency(int(row_id), code.strip(), name.strip(), symbol.strip()):
            QMessageBox.warning(None, "Database Error", "Failed to save currency record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()
```

</details>

### ⚙️ Method `_save_transaction_data`

```python
def _save_transaction_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save transaction data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_transaction_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        transaction_type = model.data(model.index(row, 1)) or ""
        amount_str = model.data(model.index(row, 2)) or "0"
        currency_symbol = model.data(model.index(row, 3)) or ""
        category_name = model.data(model.index(row, 4)) or ""
        description = model.data(model.index(row, 5)) or ""
        date = model.data(model.index(row, 6)) or ""

        # Validate date format
        if not self._is_valid_date(date):
            QMessageBox.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Validate amount
        try:
            amount = float(amount_str)
        except (ValueError, TypeError):
            QMessageBox.warning(None, "Validation Error", f"Invalid amount value: {amount_str}")
            return

        # Get currency ID
        currency_id = self.db_manager.get_id("currencies", "symbol", currency_symbol)
        if currency_id is None:
            QMessageBox.warning(None, "Validation Error", f"Currency '{currency_symbol}' not found")
            return

        # Get category ID
        category_id = self.db_manager.get_id("categories", "name", category_name)
        if category_id is None:
            QMessageBox.warning(None, "Validation Error", f"Category '{category_name}' not found")
            return

        # Update database
        if not self.db_manager.update_transaction(
            int(row_id), transaction_type, amount, currency_id, category_id, description, date
        ):
            QMessageBox.warning(None, "Database Error", "Failed to save transaction record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()
```

</details>

## 🏛️ Class `ChartOperations`

```python
class ChartOperations
```

Mixin class for chart operations.

<details>
<summary>Code:</summary>

```python
class ChartOperations:

    # Expected attributes from main class
    max_count_points_in_charts: int

    def _add_stats_box(self, ax: Axes, stats_text: str, color: str = "lightgray") -> None:
        """Add statistics box to chart.

        Args:

        - `ax` (`plt.Axes`): Matplotlib axes object.
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
        - `chart_config` (`dict`): Dictionary with chart configuration.

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
            self._format_chart_x_axis(ax, x_values)

        # Add statistics if requested
        if chart_config.get("show_stats", True) and len(y_values) > 1:
            stats_text = self._format_default_stats(y_values, chart_config.get("stats_unit", ""))
            self._add_stats_box(ax, stats_text)

        fig.tight_layout()
        layout.addWidget(canvas)
        canvas.draw()

    def _format_chart_x_axis(self, ax: Axes, dates: list) -> None:
        """Format x-axis for charts based on date range.

        Args:

        - `ax` (`plt.Axes`): Matplotlib axes object.
        - `dates` (`list`): List of datetime objects.

        """
        if not dates:
            return

        # Limit to max 10-15 ticks
        ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune="both"))

        date_range = (max(dates) - min(dates)).days
        if date_range <= 31:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        elif date_range <= 365:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        else:
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
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        total_val = sum(values)

        unit_suffix = f" {unit}" if unit else ""

        return (
            f"Min: {min_val:.2f}{unit_suffix} | Max: {max_val:.2f}{unit_suffix} | "
            f"Avg: {avg_val:.2f}{unit_suffix} | Total: {total_val:.2f}{unit_suffix}"
        )

    def _plot_data(self, ax: Axes, x_values: list, y_values: list, color: str) -> None:
        """Plot data with automatic marker selection based on data points.

        Args:

        - `ax` (`plt.Axes`): Matplotlib axes object.
        - `x_values` (`list`): X-axis values.
        - `y_values` (`list`): Y-axis values.
        - `color` (`str`): Plot color.

        """
        # Map color names to matplotlib single-letter codes
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
            )
            # Add value labels
            for x, y in zip(x_values, y_values, strict=False):
                ax.annotate(
                    f"{y:.2f}",
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
        """Show a 'no data' label in the layout.

        Args:

        - `layout` (`QLayout`): Layout to add the label to.
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

Add statistics box to chart.

Args:

- `ax` (`plt.Axes`): Matplotlib axes object.
- `stats_text` (`str`): Statistics text to display.
- `color` (`str`): Background color of the statistics box. Defaults to `"lightgray"`.

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

<details>
<summary>Code:</summary>

```python
def _clear_layout(self, layout: QLayout) -> None:
        for i in reversed(range(layout.count())):
            child = layout.takeAt(i).widget()
            if child:
                child.setParent(None)
```

</details>

### ⚙️ Method `_create_chart`

```python
def _create_chart(self, layout: QLayout, data: list, chart_config: dict) -> None
```

Create and display a chart with given data and configuration.

Args:

- `layout` (`QLayout`): Layout to add chart to.
- `data` (`list`): Chart data as list of (x, y) tuples.
- `chart_config` (`dict`): Dictionary with chart configuration.

<details>
<summary>Code:</summary>

```python
def _create_chart(self, layout: QLayout, data: list, chart_config: dict) -> None:
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
            self._format_chart_x_axis(ax, x_values)

        # Add statistics if requested
        if chart_config.get("show_stats", True) and len(y_values) > 1:
            stats_text = self._format_default_stats(y_values, chart_config.get("stats_unit", ""))
            self._add_stats_box(ax, stats_text)

        fig.tight_layout()
        layout.addWidget(canvas)
        canvas.draw()
```

</details>

### ⚙️ Method `_format_chart_x_axis`

```python
def _format_chart_x_axis(self, ax: Axes, dates: list) -> None
```

Format x-axis for charts based on date range.

Args:

- `ax` (`plt.Axes`): Matplotlib axes object.
- `dates` (`list`): List of datetime objects.

<details>
<summary>Code:</summary>

```python
def _format_chart_x_axis(self, ax: Axes, dates: list) -> None:
        if not dates:
            return

        # Limit to max 10-15 ticks
        ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune="both"))

        date_range = (max(dates) - min(dates)).days
        if date_range <= 31:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        elif date_range <= 365:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

        # Rotate date labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
```

</details>

### ⚙️ Method `_format_default_stats`

```python
def _format_default_stats(self, values: list, unit: str = "") -> str
```

Format default statistics text.

Args:

- `values` (`list`): List of numeric values.
- `unit` (`str`): Unit of measurement. Defaults to `""`.

Returns:

- `str`: Formatted statistics string.

<details>
<summary>Code:</summary>

```python
def _format_default_stats(self, values: list, unit: str = "") -> str:
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
        total_val = sum(values)

        unit_suffix = f" {unit}" if unit else ""

        return (
            f"Min: {min_val:.2f}{unit_suffix} | Max: {max_val:.2f}{unit_suffix} | "
            f"Avg: {avg_val:.2f}{unit_suffix} | Total: {total_val:.2f}{unit_suffix}"
        )
```

</details>

### ⚙️ Method `_plot_data`

```python
def _plot_data(self, ax: Axes, x_values: list, y_values: list, color: str) -> None
```

Plot data with automatic marker selection based on data points.

Args:

- `ax` (`plt.Axes`): Matplotlib axes object.
- `x_values` (`list`): X-axis values.
- `y_values` (`list`): Y-axis values.
- `color` (`str`): Plot color.

<details>
<summary>Code:</summary>

```python
def _plot_data(self, ax: Axes, x_values: list, y_values: list, color: str) -> None:
        # Map color names to matplotlib single-letter codes
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
            )
            # Add value labels
            for x, y in zip(x_values, y_values, strict=False):
                ax.annotate(
                    f"{y:.2f}",
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=9,
                    alpha=0.8,
                )
        else:
            ax.plot(x_values, y_values, color=plot_color, linestyle="-", linewidth=2, alpha=0.8)
```

</details>

### ⚙️ Method `_show_no_data_label`

```python
def _show_no_data_label(self, layout: QLayout, text: str) -> None
```

Show a 'no data' label in the layout.

Args:

- `layout` (`QLayout`): Layout to add the label to.
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

## 🏛️ Class `DateOperations`

```python
class DateOperations
```

Mixin class for date operations.

<details>
<summary>Code:</summary>

```python
class DateOperations:

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

        if is_all_time:
            # Set to one year ago as default for all time
            from_widget.setDate(current_date.addYears(-1))
        elif years:
            from_widget.setDate(current_date.addYears(-years))
        elif months:
            from_widget.setDate(current_date.addMonths(-months))
```

</details>

### ⚙️ Method `_increment_date_widget`

```python
def _increment_date_widget(self, date_widget: QDateEdit) -> None
```

Increment date widget by one day if not already today.

Args:

- `date_widget` (`QDateEdit`): QDateEdit widget to increment.

<details>
<summary>Code:</summary>

```python
def _increment_date_widget(self, date_widget: QDateEdit) -> None:
        current_date = date_widget.date()
        today = QDate.currentDate()

        # If current date is today or later, do nothing
        if current_date >= today:
            return

        # Add one day to the current date
        next_date = current_date.addDays(1)
        date_widget.setDate(next_date)
```

</details>

### ⚙️ Method `_set_date_range`

```python
def _set_date_range(self, from_widget: QDateEdit, to_widget: QDateEdit, months: int = 0, years: int = 0) -> None
```

Set date range for date widgets.

Args:

- `from_widget` (`QDateEdit`): From date widget.
- `to_widget` (`QDateEdit`): To date widget.
- `months` (`int`): Number of months back from today. Defaults to `0`.
- `years` (`int`): Number of years back from today. Defaults to `0`.
- `is_all_time` (`bool`): If True, sets to earliest available date. Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def _set_date_range(
        self,
        from_widget: QDateEdit,
        to_widget: QDateEdit,
        months: int = 0,
        years: int = 0,
        *,
        is_all_time: bool = False,
    ) -> None:
        current_date = QDate.currentDate()
        to_widget.setDate(current_date)

        if is_all_time:
            # Set to one year ago as default for all time
            from_widget.setDate(current_date.addYears(-1))
        elif years:
            from_widget.setDate(current_date.addYears(-years))
        elif months:
            from_widget.setDate(current_date.addMonths(-months))
```

</details>

## 🏛️ Class `TableOperations`

```python
class TableOperations
```

Mixin class for common table operations.

<details>
<summary>Code:</summary>

```python
class TableOperations:

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
```

</details>

### ⚙️ Method `_connect_table_signals`

```python
def _connect_table_signals(self, table_name: str, selection_handler: Callable) -> None
```

Connect selection change signal for a table.

Args:

- `table_name` (`str`): Name of the table.
- `selection_handler` (`Callable`): Handler function for selection changes.

<details>
<summary>Code:</summary>

```python
def _connect_table_signals(self, table_name: str, selection_handler: Callable) -> None:
        view = self.table_config[table_name][0]
        selection_model = view.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(selection_handler)
```

</details>

### ⚙️ Method `_get_selected_row_id`

```python
def _get_selected_row_id(self, table_name: str) -> int | None
```

Get the database ID of the currently selected row.

Args:

- `table_name` (`str`): Name of the table.

Returns:

- `int | None`: Database ID of selected row or None if no selection.

<details>
<summary>Code:</summary>

```python
def _get_selected_row_id(self, table_name: str) -> int | None:
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
```

</details>

### ⚙️ Method `_refresh_table`

```python
def _refresh_table(self, table_name: str, data_getter: Callable, data_transformer: Callable[[list], list] | None = None) -> None
```

Refresh a table with data.

Args:

- `table_name` (`str`): Name of the table to refresh.
- `data_getter` (`Callable`): Function to get data from database.
- `data_transformer` (`Callable[[list], list] | None`): Optional function to transform raw data.
  Defaults to `None`.

Raises:

- `ValueError`: If the table name is unknown.

<details>
<summary>Code:</summary>

```python
def _refresh_table(
        self, table_name: str, data_getter: Callable, data_transformer: Callable[[list], list] | None = None
    ) -> None:
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
```

</details>

## 🏛️ Class `ValidationOperations`

```python
class ValidationOperations
```

Mixin class for validation operations.

<details>
<summary>Code:</summary>

```python
class ValidationOperations:

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
            datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return False
        else:
            return True
```

</details>

### ⚙️ Method `_is_valid_date`

```python
def _is_valid_date(date_str: str) -> bool
```

Return `True` if `YYYY-MM-DD` formatted `date_str` is correct.

Args:

- `date_str` (`str`): Date string to validate.

Returns:

- `bool`: True if the date is in the correct format and represents a valid date.

<details>
<summary>Code:</summary>

```python
def _is_valid_date(date_str: str) -> bool:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
            return False

        try:
            datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return False
        else:
            return True
```

</details>

## 🔧 Function `requires_database`

```python
def requires_database() -> Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]
```

Ensure database connection is available before executing method.

Args:

- `is_show_warning` (`bool`): If True, shows a QMessageBox warning on connection failure. Defaults to `True`.

Returns:

- ` Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]`: Decorated function
  that checks database connection first.

<details>
<summary>Code:</summary>

```python
def requires_database(
    *, is_show_warning: bool = True
) -> Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]:

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
```

</details>
