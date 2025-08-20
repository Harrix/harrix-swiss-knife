---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MainWindow`](#%EF%B8%8F-class-mainwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `apply_filter`](#%EF%B8%8F-method-apply_filter)
  - [⚙️ Method `clear_filter`](#%EF%B8%8F-method-clear_filter)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `delete_record`](#%EF%B8%8F-method-delete_record)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `generate_pastel_colors_mathematical`](#%EF%B8%8F-method-generate_pastel_colors_mathematical)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `load_exchange_rates_table`](#%EF%B8%8F-method-load_exchange_rates_table)
  - [⚙️ Method `on_add_account`](#%EF%B8%8F-method-on_add_account)
  - [⚙️ Method `on_add_category`](#%EF%B8%8F-method-on_add_category)
  - [⚙️ Method `on_add_currency`](#%EF%B8%8F-method-on_add_currency)
  - [⚙️ Method `on_add_exchange`](#%EF%B8%8F-method-on_add_exchange)
  - [⚙️ Method `on_add_transaction`](#%EF%B8%8F-method-on_add_transaction)
  - [⚙️ Method `on_calculate_exchange`](#%EF%B8%8F-method-on_calculate_exchange)
  - [⚙️ Method `on_category_selection_changed`](#%EF%B8%8F-method-on_category_selection_changed)
  - [⚙️ Method `on_clear_description`](#%EF%B8%8F-method-on_clear_description)
  - [⚙️ Method `on_exchange_rates_all_time`](#%EF%B8%8F-method-on_exchange_rates_all_time)
  - [⚙️ Method `on_exchange_rates_currency_changed`](#%EF%B8%8F-method-on_exchange_rates_currency_changed)
  - [⚙️ Method `on_exchange_rates_last_month`](#%EF%B8%8F-method-on_exchange_rates_last_month)
  - [⚙️ Method `on_exchange_rates_last_year`](#%EF%B8%8F-method-on_exchange_rates_last_year)
  - [⚙️ Method `on_exchange_rates_update`](#%EF%B8%8F-method-on_exchange_rates_update)
  - [⚙️ Method `on_export_csv`](#%EF%B8%8F-method-on_export_csv)
  - [⚙️ Method `on_generate_report`](#%EF%B8%8F-method-on_generate_report)
  - [⚙️ Method `on_set_default_currency`](#%EF%B8%8F-method-on_set_default_currency)
  - [⚙️ Method `on_show_all_records_clicked`](#%EF%B8%8F-method-on_show_all_records_clicked)
  - [⚙️ Method `on_tab_changed`](#%EF%B8%8F-method-on_tab_changed)
  - [⚙️ Method `on_update_exchange_rates`](#%EF%B8%8F-method-on_update_exchange_rates)
  - [⚙️ Method `on_yesterday`](#%EF%B8%8F-method-on_yesterday)
  - [⚙️ Method `on_yesterday_exchange`](#%EF%B8%8F-method-on_yesterday_exchange)
  - [⚙️ Method `set_chart_all_time`](#%EF%B8%8F-method-set_chart_all_time)
  - [⚙️ Method `set_chart_last_month`](#%EF%B8%8F-method-set_chart_last_month)
  - [⚙️ Method `set_chart_last_year`](#%EF%B8%8F-method-set_chart_last_year)
  - [⚙️ Method `set_today_date`](#%EF%B8%8F-method-set_today_date)
  - [⚙️ Method `show_balance_chart`](#%EF%B8%8F-method-show_balance_chart)
  - [⚙️ Method `show_pie_chart`](#%EF%B8%8F-method-show_pie_chart)
  - [⚙️ Method `show_tables`](#%EF%B8%8F-method-show_tables)
  - [⚙️ Method `update_all`](#%EF%B8%8F-method-update_all)
  - [⚙️ Method `update_chart_comboboxes`](#%EF%B8%8F-method-update_chart_comboboxes)
  - [⚙️ Method `update_charts`](#%EF%B8%8F-method-update_charts)
  - [⚙️ Method `update_filter_comboboxes`](#%EF%B8%8F-method-update_filter_comboboxes)
  - [⚙️ Method `update_summary_labels`](#%EF%B8%8F-method-update_summary_labels)
  - [⚙️ Method `_calculate_daily_expenses`](#%EF%B8%8F-method-_calculate_daily_expenses)
  - [⚙️ Method `_clear_account_form`](#%EF%B8%8F-method-_clear_account_form)
  - [⚙️ Method `_clear_all_forms`](#%EF%B8%8F-method-_clear_all_forms)
  - [⚙️ Method `_clear_category_form`](#%EF%B8%8F-method-_clear_category_form)
  - [⚙️ Method `_clear_currency_form`](#%EF%B8%8F-method-_clear_currency_form)
  - [⚙️ Method `_clear_exchange_form`](#%EF%B8%8F-method-_clear_exchange_form)
  - [⚙️ Method `_clear_layout`](#%EF%B8%8F-method-_clear_layout)
  - [⚙️ Method `_connect_signals`](#%EF%B8%8F-method-_connect_signals)
  - [⚙️ Method `_connect_table_auto_save_signals`](#%EF%B8%8F-method-_connect_table_auto_save_signals)
  - [⚙️ Method `_copy_table_selection_to_clipboard`](#%EF%B8%8F-method-_copy_table_selection_to_clipboard)
  - [⚙️ Method `_create_colored_table_model`](#%EF%B8%8F-method-_create_colored_table_model)
  - [⚙️ Method `_create_exchange_rate_chart`](#%EF%B8%8F-method-_create_exchange_rate_chart)
  - [⚙️ Method `_create_pie_chart`](#%EF%B8%8F-method-_create_pie_chart)
  - [⚙️ Method `_create_table_model`](#%EF%B8%8F-method-_create_table_model)
  - [⚙️ Method `_create_transactions_table_model`](#%EF%B8%8F-method-_create_transactions_table_model)
  - [⚙️ Method `_dispose_models`](#%EF%B8%8F-method-_dispose_models)
  - [⚙️ Method `_finish_window_initialization`](#%EF%B8%8F-method-_finish_window_initialization)
  - [⚙️ Method `_focus_amount_and_select_text`](#%EF%B8%8F-method-_focus_amount_and_select_text)
  - [⚙️ Method `_focus_description_and_select_text`](#%EF%B8%8F-method-_focus_description_and_select_text)
  - [⚙️ Method `_generate_account_balances_report`](#%EF%B8%8F-method-_generate_account_balances_report)
  - [⚙️ Method `_generate_category_analysis_report`](#%EF%B8%8F-method-_generate_category_analysis_report)
  - [⚙️ Method `_generate_currency_analysis_report`](#%EF%B8%8F-method-_generate_currency_analysis_report)
  - [⚙️ Method `_generate_income_vs_expenses_report`](#%EF%B8%8F-method-_generate_income_vs_expenses_report)
  - [⚙️ Method `_generate_monthly_summary_report`](#%EF%B8%8F-method-_generate_monthly_summary_report)
  - [⚙️ Method `_get_exchange_rates_data`](#%EF%B8%8F-method-_get_exchange_rates_data)
  - [⚙️ Method `_init_chart_controls`](#%EF%B8%8F-method-_init_chart_controls)
  - [⚙️ Method `_init_database`](#%EF%B8%8F-method-_init_database)
  - [⚙️ Method `_init_filter_controls`](#%EF%B8%8F-method-_init_filter_controls)
  - [⚙️ Method `_initial_load`](#%EF%B8%8F-method-_initial_load)
  - [⚙️ Method `_load_accounts_table`](#%EF%B8%8F-method-_load_accounts_table)
  - [⚙️ Method `_load_categories_table`](#%EF%B8%8F-method-_load_categories_table)
  - [⚙️ Method `_load_currencies_table`](#%EF%B8%8F-method-_load_currencies_table)
  - [⚙️ Method `_load_currency_exchanges_table`](#%EF%B8%8F-method-_load_currency_exchanges_table)
  - [⚙️ Method `_load_essential_tables`](#%EF%B8%8F-method-_load_essential_tables)
  - [⚙️ Method `_load_transactions_table`](#%EF%B8%8F-method-_load_transactions_table)
  - [⚙️ Method `_mark_categories_changed`](#%EF%B8%8F-method-_mark_categories_changed)
  - [⚙️ Method `_mark_currencies_changed`](#%EF%B8%8F-method-_mark_currencies_changed)
  - [⚙️ Method `_mark_default_currency_changed`](#%EF%B8%8F-method-_mark_default_currency_changed)
  - [⚙️ Method `_mark_exchange_rates_changed`](#%EF%B8%8F-method-_mark_exchange_rates_changed)
  - [⚙️ Method `_mark_transactions_changed`](#%EF%B8%8F-method-_mark_transactions_changed)
  - [⚙️ Method `_on_account_double_clicked`](#%EF%B8%8F-method-_on_account_double_clicked)
  - [⚙️ Method `_on_autocomplete_selected`](#%EF%B8%8F-method-_on_autocomplete_selected)
  - [⚙️ Method `_on_currency_started`](#%EF%B8%8F-method-_on_currency_started)
  - [⚙️ Method `_on_progress_updated`](#%EF%B8%8F-method-_on_progress_updated)
  - [⚙️ Method `_on_rate_added`](#%EF%B8%8F-method-_on_rate_added)
  - [⚙️ Method `_on_table_data_changed`](#%EF%B8%8F-method-_on_table_data_changed)
  - [⚙️ Method `_on_update_finished_error`](#%EF%B8%8F-method-_on_update_finished_error)
  - [⚙️ Method `_on_update_finished_success`](#%EF%B8%8F-method-_on_update_finished_success)
  - [⚙️ Method `_populate_form_from_description`](#%EF%B8%8F-method-_populate_form_from_description)
  - [⚙️ Method `_restore_table_column_widths`](#%EF%B8%8F-method-_restore_table_column_widths)
  - [⚙️ Method `_save_table_column_widths`](#%EF%B8%8F-method-_save_table_column_widths)
  - [⚙️ Method `_select_category_by_id`](#%EF%B8%8F-method-_select_category_by_id)
  - [⚙️ Method `_set_exchange_rates_date_range`](#%EF%B8%8F-method-_set_exchange_rates_date_range)
  - [⚙️ Method `_setup_autocomplete`](#%EF%B8%8F-method-_setup_autocomplete)
  - [⚙️ Method `_setup_exchange_rates_controls`](#%EF%B8%8F-method-_setup_exchange_rates_controls)
  - [⚙️ Method `_setup_tab_order`](#%EF%B8%8F-method-_setup_tab_order)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)
  - [⚙️ Method `_setup_window_size_and_position`](#%EF%B8%8F-method-_setup_window_size_and_position)
  - [⚙️ Method `_show_no_data_label`](#%EF%B8%8F-method-_show_no_data_label)
  - [⚙️ Method `_show_transactions_context_menu`](#%EF%B8%8F-method-_show_transactions_context_menu)
  - [⚙️ Method `_transform_transaction_data`](#%EF%B8%8F-method-_transform_transaction_data)
  - [⚙️ Method `_update_autocomplete_data`](#%EF%B8%8F-method-_update_autocomplete_data)
  - [⚙️ Method `_update_comboboxes`](#%EF%B8%8F-method-_update_comboboxes)
  - [⚙️ Method `_validate_database_connection`](#%EF%B8%8F-method-_validate_database_connection)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow, window.Ui_MainWindow, TableOperations, ChartOperations, DateOperations, AutoSaveOperations, ValidationOperations)
```

Main application window for the finance tracking application.

This class implements the main GUI window for the finance tracker, providing
functionality to record transactions, manage categories, accounts, currencies
and track financial progress.

Attributes:

- `_SAFE_TABLES` (`frozenset[str]`): Set of table names that can be safely modified.

- `db_manager` (`database_manager.DatabaseManager | None`): Database
  connection manager. Defaults to `None` until initialized.

- `models` (`dict[str, QSortFilterProxyModel | None]`): Dictionary of table models keyed
  by table name. All values default to `None` until tables are loaded.

- `table_config` (`dict[str, tuple[QTableView, str, list[str]]]`): Configuration for each
  table, mapping table names to tuples of (table view widget, model key, column headers).

<details>
<summary>Code:</summary>

```python
class MainWindow(
    QMainWindow,
    window.Ui_MainWindow,
    TableOperations,
    ChartOperations,
    DateOperations,
    AutoSaveOperations,
    ValidationOperations,
):

    _SAFE_TABLES: frozenset[str] = frozenset(
        {"transactions", "categories", "accounts", "currencies", "currency_exchanges", "exchange_rates"},
    )

    def __init__(self) -> None:  # noqa: D107  (inherited from Qt widgets)
        super().__init__()
        self.setupUi(self)
        self._setup_ui()

        # Set window icon
        self.setWindowIcon(QIcon(":/assets/logo.svg"))

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Initialize core attributes
        self.db_manager: database_manager.DatabaseManager | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "transactions": None,
            "categories": None,
            "accounts": None,
            "currencies": None,
            "currency_exchanges": None,
            "exchange_rates": None,
        }

        # Chart configuration
        self.max_count_points_in_charts = 40

        # Generate pastel colors for date-based coloring
        self.date_colors = self.generate_pastel_colors_mathematical(50)

        # Toggle for showing all records vs last self.count_transactions_to_show
        self.count_transactions_to_show = 1000
        self.count_exchange_rates_to_show = 1000
        self.show_all_transactions = False

        # Lazy loading flags
        self.exchange_rates_loaded = False

        # Exchange rates initialization flag
        self._exchange_rates_initialized = False

        # Table configuration mapping
        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "transactions": (
                self.tableView_transactions,
                "transactions",
                ["Description", "Amount", "Category", "Currency", "Date", "Tag", "Total per day"],
            ),
            "categories": (
                self.tableView_categories,
                "categories",
                ["Name", "Type", "Icon"],
            ),
            "accounts": (
                self.tableView_accounts,
                "accounts",
                ["Name", "Balance", "Currency", "Liquid", "Cash"],
            ),
            "currencies": (
                self.tableView_currencies,
                "currencies",
                ["Code", "Name", "Symbol"],
            ),
            "currency_exchanges": (
                self.tableView_exchange,
                "currency_exchanges",
                ["From", "To", "Amount From", "Amount To", "Rate", "Fee", "Date", "Description"],
            ),
            "exchange_rates": (
                self.tableView_exchange_rates,
                "exchange_rates",
                ["From", "To", "Rate", "Date"],
            ),
        }

        # Initialize application
        self._init_database()
        self._connect_signals()
        self._init_filter_controls()
        self._init_chart_controls()
        self._setup_autocomplete()
        self._initial_load()

        # Set window size and position
        self._setup_window_size_and_position()

        # Setup tab order
        self._setup_tab_order()

        # Show window after initialization
        QTimer.singleShot(200, self._finish_window_initialization)

    @requires_database()
    def apply_filter(self) -> None:
        """Apply combo-box/date filters to the transactions table."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get filter values
        transaction_type = None
        if self.radioButton_2.isChecked():  # Expense
            transaction_type = 0
        elif self.radioButton_3.isChecked():  # Income
            transaction_type = 1
        # If radioButton (All) is checked, transaction_type remains None

        category = self.comboBox_filter_category.currentText() if self.comboBox_filter_category.currentText() else None
        currency = self.comboBox_filter_currency.currentText() if self.comboBox_filter_currency.currentText() else None

        use_date_filter = self.checkBox_use_date_filter.isChecked()
        date_from = self.dateEdit_filter_from.date().toString("yyyy-MM-dd") if use_date_filter else None
        date_to = self.dateEdit_filter_to.date().toString("yyyy-MM-dd") if use_date_filter else None

        # Use database manager method
        rows = self.db_manager.get_filtered_transactions(
            category_type=transaction_type,
            category_name=category,
            currency_code=currency,
            date_from=date_from,
            date_to=date_to,
        )

        # Transform data for display
        transformed_data = self._transform_transaction_data(rows)

        # Create model and set to table
        self.models["transactions"] = self._create_transactions_table_model(
            transformed_data, self.table_config["transactions"][2]
        )
        self.tableView_transactions.setModel(self.models["transactions"])

        # Column stretching setup (like in show_tables)
        self.tableView_transactions.resizeColumnsToContents()

        # Table header behavior setup for column stretching
        header = self.tableView_transactions.horizontalHeader()
        if header.count() > 0:
            # Set stretch mode for all columns except the last two
            for i in range(header.count() - 2):
                header.setSectionResizeMode(i, header.ResizeMode.Stretch)

            # For the second-to-last column (Tag) set fixed width
            second_last_column = header.count() - 2
            header.setSectionResizeMode(second_last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(second_last_column, 100)

            # For the last column (Total per day) set fixed width
            last_column = header.count() - 1
            header.setSectionResizeMode(last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(last_column, 120)

        # Reconnect auto-save signals for the updated table
        self._connect_table_auto_save_signals()

    def clear_filter(self) -> None:
        """Reset all transaction filters."""
        self.radioButton.setChecked(True)  # All
        self.comboBox_filter_category.setCurrentIndex(0)
        self.comboBox_filter_currency.setCurrentIndex(0)
        self.checkBox_use_date_filter.setChecked(False)

        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        # Load transactions table instead of all tables
        self._load_transactions_table()
        # Reconnect auto-save signals for the updated table
        self._connect_table_auto_save_signals()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle application close event.

        Args:

        - `event` (`QCloseEvent`): The close event.

        """
        # Stop any running worker threads
        if hasattr(self, "exchange_rate_worker") and self.exchange_rate_worker.isRunning():
            self.exchange_rate_worker.stop()
            self.exchange_rate_worker.wait(3000)  # Wait up to 3 seconds

        # Close progress dialog if open
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        # Dispose Models
        self._dispose_models()

        # Close DB
        if self.db_manager:
            self.db_manager.close()
            self.db_manager = None

        super().closeEvent(event)

    @requires_database()
    def delete_record(self, table_name: str) -> None:
        """Delete selected row from table using database manager methods.

        Args:

        - `table_name` (`str`): Name of the table to delete from. Must be in _SAFE_TABLES.

        Raises:

        - `ValueError`: If table_name is not in _SAFE_TABLES.

        """
        if table_name not in self._SAFE_TABLES:
            error_message = f"Illegal table name: {table_name}"
            raise ValueError(error_message)

        record_id = self._get_selected_row_id(table_name)
        if record_id is None:
            QMessageBox.warning(self, "Error", "Select a record to delete")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Use appropriate database manager method
        success = False
        try:
            if table_name == "transactions":
                success = self.db_manager.delete_transaction(record_id)
                if success:
                    self._mark_transactions_changed()
            elif table_name == "categories":
                success = self.db_manager.delete_category(record_id)
                if success:
                    self._mark_categories_changed()
            elif table_name == "accounts":
                success = self.db_manager.delete_account(record_id)
            elif table_name == "currencies":
                success = self.db_manager.delete_currency(record_id)
                if success:
                    self._mark_currencies_changed()
            elif table_name == "currency_exchanges":
                success = self.db_manager.delete_currency_exchange(record_id)
            elif table_name == "exchange_rates":
                success = self.db_manager.delete_exchange_rate(record_id)
                if success:
                    self._mark_exchange_rates_changed()
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            # Save current column widths before update for exchange table
            column_widths = None
            if table_name == "currency_exchanges":
                column_widths = self._save_table_column_widths(self.tableView_exchange)

            self.update_all()

            # Restore column widths after update for exchange table
            if table_name == "currency_exchanges" and column_widths:
                self._restore_table_column_widths(self.tableView_exchange, column_widths)

            self.update_summary_labels()
        else:
            QMessageBox.warning(self, "Error", f"Deletion failed in {table_name}")

    def eventFilter(self, obj, event) -> bool:
        """Event filter for handling Enter key in doubleSpinBox_amount.

        Args:

        - `obj`: The object that generated the event.
        - `event`: The event that occurred.

        Returns:

        - `bool`: True if event was handled, False otherwise.

        """
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QKeyEvent

        if (
            (obj == self.doubleSpinBox_amount and event.type() == QEvent.Type.KeyPress)
            or (obj == self.dateEdit and event.type() == QEvent.Type.KeyPress)
            or (obj == self.lineEdit_tag and event.type() == QEvent.Type.KeyPress)
            or (obj == self.pushButton_add and event.type() == QEvent.Type.KeyPress)
        ):
            key_event = QKeyEvent(event)
            if key_event.key() == Qt.Key.Key_Return or key_event.key() == Qt.Key.Key_Enter:
                self.on_add_transaction()
                return True
        return super().eventFilter(obj, event)

    def generate_pastel_colors_mathematical(self, count: int = 100) -> list[QColor]:
        """Generate pastel colors using mathematical distribution.

        Args:

        - `count` (`int`): Number of colors to generate. Defaults to `100`.

        Returns:

        - `list[QColor]`: List of pastel QColor objects.

        """
        colors = []

        for i in range(count):
            # Use golden ratio for even hue distribution
            hue = (i * 0.618033988749895) % 1.0  # Golden ratio

            # Lower saturation and higher lightness for very light pastel effect
            saturation = 0.6  # Very low saturation
            lightness = 0.95  # Very high lightness

            # Convert HSL to RGB
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

            # Convert to 0-255 range and create QColor
            color = QColor(int(r * 255), int(g * 255), int(b * 255))
            colors.append(color)

        return colors

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle key press events for the main window.

        Args:

        - `event` (`QKeyEvent`): The key press event.

        """
        # Handle Ctrl+C for copying table selections
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Determine which table is currently focused
            focused_widget = QApplication.focusWidget()

            # Check if the focused widget is one of our table views
            table_views = [
                self.tableView_transactions,
                self.tableView_categories,
                self.tableView_accounts,
                self.tableView_currencies,
                self.tableView_exchange,
                self.tableView_exchange_rates,
                self.tableView_reports,
            ]

            for table_view in table_views:
                if focused_widget == table_view:
                    self._copy_table_selection_to_clipboard(table_view)
                    return

            # If focused widget is a child of a table view
            for table_view in table_views:
                if focused_widget and table_view.isAncestorOf(focused_widget):
                    self._copy_table_selection_to_clipboard(table_view)
                    return

        # Call parent implementation for other key events
        super().keyPressEvent(event)

    def load_exchange_rates_table(self) -> None:
        """Load exchange rates table data (lazy loading)."""
        if not self._validate_database_connection():
            print("Database connection not available for loading exchange rates")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Refresh exchange rates table - get only the latest records sorted by date
            rates_data = self.db_manager.get_all_exchange_rates(limit=self.count_exchange_rates_to_show)
            rates_transformed_data = []
            for row in rates_data:
                # Transform: [id, from_code, to_code, rate, date]
                # Rate is stored as USD→currency, but display as currency→USD
                usd_to_currency_rate = float(row[3]) if row[3] else 0.0
                currency_to_usd_rate = 1.0 / usd_to_currency_rate if usd_to_currency_rate != 0 else 0.0
                color = QColor(240, 255, 255)
                # Show as currency → USD instead of USD → currency
                transformed_row = [row[2], row[1], f"{currency_to_usd_rate:.6f}", row[4], row[0], color]
                rates_transformed_data.append(transformed_row)

            self.models["exchange_rates"] = self._create_colored_table_model(
                rates_transformed_data, self.table_config["exchange_rates"][2]
            )
            self.tableView_exchange_rates.setModel(self.models["exchange_rates"])

            # Configure column stretching for exchange rates table
            rates_header = self.tableView_exchange_rates.horizontalHeader()
            if rates_header.count() > 0:
                for i in range(rates_header.count()):
                    rates_header.setSectionResizeMode(i, rates_header.ResizeMode.Stretch)

            # Mark as loaded
            self.exchange_rates_loaded = True

        except Exception as e:
            print(f"❌ Error loading exchange rates table: {e}")

    @requires_database()
    def on_add_account(self) -> None:
        """Add a new account using database manager."""
        name = self.lineEdit_account_name.text().strip()
        balance = self.doubleSpinBox_account_balance.value()
        currency_code = self.comboBox_account_currency.currentText()
        is_liquid = self.checkBox_is_liquid.isChecked()
        is_cash = self.checkBox_is_cash.isChecked()

        if not name:
            QMessageBox.warning(self, "Error", "Enter account name")
            return

        if not currency_code:
            QMessageBox.warning(self, "Error", "Select a currency")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get currency ID
        currency_info = self.db_manager.get_currency_by_code(currency_code)
        if not currency_info:
            QMessageBox.warning(self, "Error", f"Currency '{currency_code}' not found")
            return

        currency_id = currency_info[0]

        try:
            if self.db_manager.add_account(name, balance, currency_id, is_liquid=is_liquid, is_cash=is_cash):
                self.update_all()
                self._clear_account_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add account")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add account: {e}")

    @requires_database()
    def on_add_category(self) -> None:
        """Add a new category using database manager."""
        name = self.lineEdit_category_name.text().strip()
        category_type = self.comboBox_category_type.currentIndex()  # 0 = Expense, 1 = Income

        if not name:
            QMessageBox.warning(self, "Error", "Enter category name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.add_category(name, category_type):
                self._mark_categories_changed()
                self.update_all()
                self._clear_category_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add category")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add category: {e}")

    @requires_database()
    def on_add_currency(self) -> None:
        """Add a new currency using database manager."""
        code = self.lineEdit_currency_code.text().strip().upper()
        name = self.lineEdit_currency_name.text().strip()
        symbol = self.lineEdit_currency_symbol.text().strip()
        subdivision = self.spinBox_subdivision.value()

        if not code:
            QMessageBox.warning(self, "Error", "Enter currency code")
            return

        if not name:
            QMessageBox.warning(self, "Error", "Enter currency name")
            return

        if not symbol:
            QMessageBox.warning(self, "Error", "Enter currency symbol")
            return

        if subdivision <= 0:
            QMessageBox.warning(self, "Error", "Subdivision must be a positive number")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.add_currency(code, name, symbol, subdivision):
                self._mark_currencies_changed()
                self.update_all()
                self._clear_currency_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add currency")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add currency: {e}")

    @requires_database()
    def on_add_exchange(self) -> None:
        """Add a new currency exchange using database manager."""
        from_currency = self.comboBox_exchange_from.currentText()
        to_currency = self.comboBox_exchange_to.currentText()
        amount_from = self.doubleSpinBox_exchange_from.value()
        amount_to = self.doubleSpinBox_exchange_to.value()
        exchange_rate = self.doubleSpinBox_exchange_rate.value()
        fee = self.doubleSpinBox_exchange_fee.value()
        date = self.dateEdit_exchange.date().toString("yyyy-MM-dd")
        description = self.lineEdit_exchange_description.text().strip()

        if not from_currency or not to_currency:
            QMessageBox.warning(self, "Error", "Select both currencies")
            return

        if from_currency == to_currency:
            QMessageBox.warning(self, "Error", "From and To currencies must be different")
            return

        if amount_from <= 0 or amount_to <= 0:
            QMessageBox.warning(self, "Error", "Amounts must be positive")
            return

        if exchange_rate <= 0:
            QMessageBox.warning(self, "Error", "Exchange rate must be positive")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get currency IDs
        from_currency_info = self.db_manager.get_currency_by_code(from_currency)
        to_currency_info = self.db_manager.get_currency_by_code(to_currency)

        if not from_currency_info or not to_currency_info:
            QMessageBox.warning(self, "Error", "Currency not found")
            return

        from_currency_id = from_currency_info[0]
        to_currency_id = to_currency_info[0]

        try:
            if self.db_manager.add_currency_exchange(
                from_currency_id, to_currency_id, amount_from, amount_to, exchange_rate, fee, date, description
            ):
                # Save current column widths before update
                column_widths = self._save_table_column_widths(self.tableView_exchange)

                self.update_all()

                # Restore column widths after update
                self._restore_table_column_widths(self.tableView_exchange, column_widths)

                self._clear_exchange_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add currency exchange")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add currency exchange: {e}")

    @requires_database()
    def on_add_transaction(self) -> None:
        """Add a new transaction using database manager."""
        amount = self.doubleSpinBox_amount.value()
        description = self.lineEdit_description.text().strip()
        category_name = (
            self.listView_categories.currentIndex().data(Qt.ItemDataRole.UserRole)
            if self.listView_categories.currentIndex().isValid()
            else None
        )
        currency_code = self.comboBox_currency.currentText()
        date = self.dateEdit.date().toString("yyyy-MM-dd")
        tag = self.lineEdit_tag.text().strip()

        if amount <= 0:
            QMessageBox.warning(self, "Error", "Amount must be positive")
            return

        if not description:
            QMessageBox.warning(self, "Error", "Enter description")
            return

        if not category_name:
            QMessageBox.warning(self, "Error", "Select a category")
            return

        if not currency_code:
            QMessageBox.warning(self, "Error", "Select a currency")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get category ID
        cat_id = self.db_manager.get_id("categories", "name", category_name)
        if cat_id is None:
            QMessageBox.warning(self, "Error", f"Category '{category_name}' not found")
            return

        # Get currency ID
        currency_info = self.db_manager.get_currency_by_code(currency_code)
        if not currency_info:
            QMessageBox.warning(self, "Error", f"Currency '{currency_code}' not found")
            return

        currency_id = currency_info[0]

        try:
            if self.db_manager.add_transaction(amount, description, cat_id, currency_id, date, tag):
                # Save current date before updating UI
                current_date = self.dateEdit.date()

                # Mark transactions changed for lazy loading
                self._mark_transactions_changed()

                # Update UI
                self.update_all()
                self.update_summary_labels()

                # Update autocomplete data with new transaction
                self._update_autocomplete_data()

                # Clear form except date
                self.doubleSpinBox_amount.setValue(100.0)
                self.lineEdit_description.clear()
                self.lineEdit_tag.clear()

                # Restore the original date
                self.dateEdit.setDate(current_date)

                # Set focus to description field and select all text after a short delay
                # This ensures UI updates are complete before focusing
                QTimer.singleShot(100, self._focus_description_and_select_text)

                # Select the category of the just added transaction
                self._select_category_by_id(cat_id)
            else:
                QMessageBox.warning(self, "Error", "Failed to add transaction")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add transaction: {e}")

    @requires_database()
    def on_calculate_exchange(self) -> None:
        """Calculate exchange amount based on rate."""
        amount_from = self.doubleSpinBox_exchange_from.value()
        rate = self.doubleSpinBox_exchange_rate.value()

        if rate > 0:
            amount_to = amount_from * rate
            self.doubleSpinBox_exchange_to.setValue(amount_to)

    def on_category_selection_changed(self, current: QModelIndex, previous: QModelIndex) -> None:
        """Handle category selection change in listView_categories.

        Args:

        - `current` (`QModelIndex`): Current selected index.
        - `previous` (`QModelIndex`): Previously selected index.

        """
        if current.isValid():
            # Get the display text (with icon and income marker if applicable)
            display_text = current.data(Qt.ItemDataRole.DisplayRole)
            if display_text:
                self.label_category_now.setText(display_text)
            else:
                self.label_category_now.setText("No category selected")

            # Move focus to description field and select all text
            QTimer.singleShot(100, self._focus_description_and_select_text)
        else:
            self.label_category_now.setText("No category selected")

    def on_clear_description(self) -> None:
        """Clear the description field."""
        self.lineEdit_description.clear()

    def on_exchange_rates_all_time(self) -> None:
        """Set date range to all available data."""
        self._set_exchange_rates_date_range()
        # Automatically update the chart
        self.on_exchange_rates_update()

    def on_exchange_rates_currency_changed(self) -> None:
        """Handle currency selection change in exchange rates tab."""
        # Update chart if dates are set
        if self.dateEdit_exchange_rates_from.date().isValid() and self.dateEdit_exchange_rates_to.date().isValid():
            self.on_exchange_rates_update()

    def on_exchange_rates_last_month(self) -> None:
        """Set date range to last month."""
        current_date = QDate.currentDate()
        last_month = current_date.addMonths(-1)
        self.dateEdit_exchange_rates_from.setDate(last_month)
        self.dateEdit_exchange_rates_to.setDate(current_date)
        # Automatically update the chart
        self.on_exchange_rates_update()

    def on_exchange_rates_last_year(self) -> None:
        """Set date range to last year."""
        current_date = QDate.currentDate()
        last_year = current_date.addYears(-1)
        self.dateEdit_exchange_rates_from.setDate(last_year)
        self.dateEdit_exchange_rates_to.setDate(current_date)
        # Automatically update the chart
        self.on_exchange_rates_update()

    def on_exchange_rates_update(self) -> None:
        """Update the exchange rate chart."""
        # Check if exchange rates controls have been initialized
        if not hasattr(self, "_exchange_rates_initialized") or not self._exchange_rates_initialized:
            return

        # Get selected currency
        current_index = self.comboBox_exchange_rates_currency.currentIndex()
        if current_index < 0:
            return

        currency_id = self.comboBox_exchange_rates_currency.itemData(current_index)
        if not currency_id:
            return

        # Get date range
        date_from = self.dateEdit_exchange_rates_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_exchange_rates_to.date().toString("yyyy-MM-dd")

        # Validate date range
        if self.dateEdit_exchange_rates_from.date() > self.dateEdit_exchange_rates_to.date():
            QMessageBox.warning(self, "Invalid Date Range", "Start date cannot be after end date.")
            return

        # Create chart
        self._create_exchange_rate_chart(currency_id, date_from, date_to)

    def on_export_csv(self) -> None:
        """Save current transactions view to a CSV file."""
        filename_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save Table",
            "",
            "CSV (*.csv)",
        )
        if not filename_str:
            return

        try:
            filename = Path(filename_str)
            model = self.models["transactions"].sourceModel()  # type: ignore[call-arg]
            with filename.open("w", encoding="utf-8") as file:
                headers = [
                    model.headerData(col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) or ""
                    for col in range(model.columnCount())
                ]
                file.write(";".join(headers) + "\n")

                for row in range(model.rowCount()):
                    row_values = [f'"{model.data(model.index(row, col)) or ""}"' for col in range(model.columnCount())]
                    file.write(";".join(row_values) + "\n")

        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export CSV: {e}")

    @requires_database()
    def on_generate_report(self) -> None:
        """Generate selected report."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        report_type = self.comboBox_report_type.currentText()
        default_currency_id = self.db_manager.get_default_currency_id()

        try:
            if report_type == "Monthly Summary":
                self._generate_monthly_summary_report(default_currency_id)
            elif report_type == "Category Analysis":
                self._generate_category_analysis_report(default_currency_id)
            elif report_type == "Currency Analysis":
                self._generate_currency_analysis_report()
            elif report_type == "Account Balances":
                self._generate_account_balances_report(default_currency_id)
            elif report_type == "Income vs Expenses":
                self._generate_income_vs_expenses_report(default_currency_id)
        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate report: {e}")

    @requires_database()
    def on_set_default_currency(self) -> None:
        """Set the default currency."""
        currency_code = self.comboBox_default_currency.currentText()

        if not currency_code:
            QMessageBox.warning(self, "Error", "Select a currency")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.set_default_currency(currency_code):
                QMessageBox.information(self, "Success", f"Default currency set to {currency_code}")
                # Mark default currency changed for lazy loading
                self._mark_default_currency_changed()
                # Update all displays to reflect new currency
                self.update_summary_labels()
                self._update_comboboxes()
            else:
                QMessageBox.warning(self, "Error", "Failed to set default currency")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to set default currency: {e}")

    def on_show_all_records_clicked(self) -> None:
        """Toggle between showing all records and last self.count_transactions_to_show records."""
        self.show_all_transactions = not self.show_all_transactions

        # Update button text and icon
        if self.show_all_transactions:
            self.pushButton_show_all_records.setText(f"📊 Show Last {self.count_transactions_to_show}")
        else:
            self.pushButton_show_all_records.setText("📊 Show All Records")

        # Refresh the transactions table
        self._load_transactions_table()

        # Reconnect auto-save signals for the updated table
        self._connect_table_auto_save_signals()

    def on_tab_changed(self, index: int) -> None:
        """React to tab change.

        Args:

        - `index` (`int`): The index of the newly selected tab.

        """
        # Update relevant data when switching to different tabs
        if index == 4:  # Exchange Rates tab - lazy loading
            if not self.exchange_rates_loaded:
                self.load_exchange_rates_table()
        elif index == 6:  # Charts tab
            self.update_chart_comboboxes()
        elif index == 7:  # Reports tab
            self.update_summary_labels()
        # Note: Transactions tab (index 0) needs no updates - data loaded on startup

    @requires_database()
    def on_update_exchange_rates(self) -> None:
        """Update exchange rates using a background thread."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get the earliest date from transactions
            earliest_transaction_date = self.db_manager.get_earliest_transaction_date()
            if not earliest_transaction_date:
                QMessageBox.warning(
                    self,
                    "No Data",
                    "No transactions found. Please add some transactions first.",
                )
                return

            # Get all currencies except USD (base currency)
            currencies = self.db_manager.get_currencies_except_usd()
            if not currencies:
                QMessageBox.warning(self, "No Currencies", "No currencies found except USD.")
                return

            # Calculate which currencies need updates
            currencies_to_update = []
            today = datetime.now().date()
            earliest_date = datetime.strptime(earliest_transaction_date, "%Y-%m-%d").date()

            print(f"🔍 Checking which currencies need updates...")
            print(f"📅 Earliest transaction date: {earliest_date}")
            print(f"📅 Today's date: {today}")

            for currency_id, currency_code, currency_name, currency_symbol in currencies:
                # Get the last date for this currency
                last_date_str = self.db_manager.get_last_exchange_rate_date(currency_id)

                if last_date_str:
                    last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
                    # Need to update from the day after last_date to today
                    start_date = last_date + timedelta(days=1)

                    # But make sure we don't go earlier than earliest transaction date
                    if start_date < earliest_date:
                        start_date = earliest_date

                    if start_date <= today:
                        currencies_to_update.append((currency_id, currency_code, start_date, today))
                        days_to_update = (today - start_date).days + 1
                        print(f"📊 {currency_code}: Update from {start_date} to {today} ({days_to_update} days)")
                    else:
                        print(f"✅ {currency_code}: Already up to date (last: {last_date})")
                else:
                    # No rates exist for this currency, need to download from earliest transaction date
                    currencies_to_update.append((currency_id, currency_code, earliest_date, today))
                    days_to_update = (today - earliest_date).days + 1
                    print(
                        f"📊 {currency_code}: First time download from {earliest_date} to {today} ({days_to_update} days)"
                    )

            # If no currencies need updates, inform user
            if not currencies_to_update:
                QMessageBox.information(
                    self,
                    "Exchange Rates Up to Date",
                    f"All exchange rates are already up to date as of {today}.\n"
                    f"No updates needed for {len(currencies)} currencies.",
                )
                print(f"✅ All exchange rates are up to date. No updates needed.")
                return

            # Show summary and ask for confirmation
            total_days = sum((end_date - start_date).days + 1 for _, _, start_date, end_date in currencies_to_update)
            currencies_text = ", ".join([curr[1] for curr in currencies_to_update])

            reply = QMessageBox.question(
                self,
                "Update Exchange Rates",
                f"Found {len(currencies_to_update)} currencies that need updates:\n"
                f"{currencies_text}\n\n"
                f"Total days to download: {total_days}\n\n"
                f"Do you want to proceed with the update?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Check if worker is already running
            if hasattr(self, "exchange_rate_worker") and self.exchange_rate_worker.isRunning():
                reply = QMessageBox.question(
                    self,
                    "Update in Progress",
                    "Exchange rate update is already running. Do you want to stop it and start a new one?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.exchange_rate_worker.stop()
                    self.exchange_rate_worker.wait()
                else:
                    return

            # Create and configure progress dialog
            self.progress_dialog = QMessageBox(self)
            self.progress_dialog.setWindowTitle("Updating Exchange Rates")
            self.progress_dialog.setText(f"Starting exchange rate update for {len(currencies_to_update)} currencies...")
            self.progress_dialog.setStandardButtons(QMessageBox.StandardButton.Cancel)
            self.progress_dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)

            # Connect cancel button
            def cancel_update():
                if hasattr(self, "exchange_rate_worker"):
                    self.exchange_rate_worker.stop()
                self.progress_dialog.close()

            self.progress_dialog.buttonClicked.connect(lambda: cancel_update())
            self.progress_dialog.show()

            # Create and start worker thread
            self.exchange_rate_worker = ExchangeRateUpdateWorker(
                self.db_manager, currencies_to_update, earliest_date, today
            )

            # Connect signals
            self.exchange_rate_worker.progress_updated.connect(self._on_progress_updated)
            self.exchange_rate_worker.currency_started.connect(self._on_currency_started)
            self.exchange_rate_worker.rates_added.connect(self._on_rate_added)
            self.exchange_rate_worker.finished_success.connect(self._on_update_finished_success)
            self.exchange_rate_worker.finished_error.connect(self._on_update_finished_error)

            # Start the worker
            self.exchange_rate_worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Update Error", f"Failed to start exchange rate update: {e}")
            print(f"❌ Exchange rate update error: {e}")

    def on_yesterday(self) -> None:
        """Set yesterday's date in the main date field."""
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit.setDate(yesterday)

    def on_yesterday_exchange(self) -> None:
        """Set yesterday's date in the exchange date field."""
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit_exchange.setDate(yesterday)

    def set_chart_all_time(self) -> None:
        """Set chart date range to all available data."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, is_all_time=True)
        self.update_charts()

    def set_chart_last_month(self) -> None:
        """Set chart date range to last month."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, months=1)
        self.update_charts()

    def set_chart_last_year(self) -> None:
        """Set chart date range to last year."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, years=1)
        self.update_charts()

    def set_today_date(self) -> None:
        """Set today's date in all date fields."""
        today_qdate = QDate.currentDate()
        self.dateEdit.setDate(today_qdate)
        self.dateEdit_exchange.setDate(today_qdate)

    def show_balance_chart(self) -> None:
        """Show balance chart."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get default currency
        default_currency_id = self.db_manager.get_default_currency_id()
        default_currency_code = self.db_manager.get_default_currency()

        # Get date range
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get transaction data for balance calculation
        rows = self.db_manager.get_transactions_chart_data(default_currency_id, date_from=date_from, date_to=date_to)

        if not rows:
            self._show_no_data_label(self.scrollAreaWidgetContents_charts.layout(), "No data found for balance chart")
            return

        # Calculate running balance
        balance = 0.0
        balance_data = []

        for date_str, amount in rows:
            # Get transactions for this date
            daily_transactions = self.db_manager.get_transactions_chart_data(
                default_currency_id, date_from=date_str, date_to=date_str
            )

            daily_balance = 0.0
            for _, daily_amount in daily_transactions:
                # Get category type for each transaction to determine if it's income or expense
                trans_rows = self.db_manager.get_filtered_transactions(date_from=date_str, date_to=date_str)
                for trans_row in trans_rows:
                    if trans_row[5] == date_str:  # date column
                        category_type = trans_row[7]  # type column
                        trans_amount = float(trans_row[1]) / 100  # amount in cents
                        if category_type == 1:  # Income
                            daily_balance += trans_amount
                        else:  # Expense
                            daily_balance -= trans_amount

            balance += daily_balance
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            balance_data.append((date_obj, balance))

        # Create chart configuration
        chart_config = {
            "title": f"Balance Over Time ({default_currency_code})",
            "xlabel": "Date",
            "ylabel": f"Balance ({default_currency_code})",
            "color": "blue",
            "show_stats": True,
            "period": "Days",
        }

        self._create_chart(self.scrollAreaWidgetContents_charts.layout(), balance_data, chart_config)

    @requires_database()
    def show_pie_chart(self) -> None:
        """Show pie chart of expenses by category."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get default currency
        default_currency_id = self.db_manager.get_default_currency_id()
        default_currency_code = self.db_manager.get_default_currency()

        # Get date range
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get expense transactions by category
        expense_rows = self.db_manager.get_filtered_transactions(category_type=0, date_from=date_from, date_to=date_to)

        if not expense_rows:
            self._show_no_data_label(
                self.scrollAreaWidgetContents_charts.layout(), "No expense data found for pie chart"
            )
            return

        # Group by category and sum amounts (converted to default currency)
        category_totals = {}
        for row in expense_rows:
            category_name = row[3]  # category name
            amount_cents = row[1]  # amount in cents
            currency_code = row[4]  # currency code

            # Convert to default currency
            if currency_code != default_currency_code:
                currency_info = self.db_manager.get_currency_by_code(currency_code)
                if currency_info:
                    source_currency_id = currency_info[0]
                    exchange_rate = self.db_manager.get_exchange_rate(source_currency_id, default_currency_id)
                    amount = (float(amount_cents) / 100) * exchange_rate
                else:
                    amount = float(amount_cents) / 100
            else:
                amount = float(amount_cents) / 100

            if category_name in category_totals:
                category_totals[category_name] += amount
            else:
                category_totals[category_name] = amount

        # Create pie chart
        self._create_pie_chart(category_totals, f"Expenses by Category ({default_currency_code})")

    def show_tables(self) -> None:
        """Populate all QTableViews using database manager methods (except exchange rates - lazy loaded)."""
        if not self._validate_database_connection():
            print("Database connection not available for showing tables")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Load essential tables only (exclude exchange_rates)
            self._load_essential_tables()

            # Exchange rates table loaded lazily on first tab access

        except Exception as e:
            print(f"Error showing tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load tables: {e}")

    def update_all(self) -> None:
        """Refresh all tables and comboboxes."""
        if not self._validate_database_connection():
            print("Database connection not available for update_all")
            return

        # Load essential tables
        self._load_essential_tables()
        self._update_comboboxes()
        self.update_filter_comboboxes()
        self.update_chart_comboboxes()
        self.set_today_date()
        self.update_summary_labels()

        # If exchange rates tab is currently active, reload the data
        current_tab_index = self.tabWidget.currentIndex()
        if current_tab_index == 4:  # Exchange Rates tab
            self.load_exchange_rates_table()
        else:
            # Mark exchange rates as not loaded to force reload when tab is accessed
            self.exchange_rates_loaded = False

        # Clear forms
        self._clear_all_forms()

    @requires_database()
    def update_chart_comboboxes(self) -> None:
        """Update comboboxes for charts."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update category combobox for charts
            categories = self.db_manager.get_categories_by_type(0) + self.db_manager.get_categories_by_type(1)

            self.comboBox_chart_category.clear()
            self.comboBox_chart_category.addItem("All Categories")
            self.comboBox_chart_category.addItems(categories)

        except Exception as e:
            print(f"Error updating chart comboboxes: {e}")

    @requires_database()
    def update_charts(self) -> None:
        """Update charts based on current settings."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        category = self.comboBox_chart_category.currentText()
        chart_type = self.comboBox_chart_type.currentText()
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get default currency
        default_currency_id = self.db_manager.get_default_currency_id()
        default_currency_code = self.db_manager.get_default_currency()

        # Determine category type filter
        category_type = None
        if chart_type == "Income":
            category_type = 1
        elif chart_type == "Expense":
            category_type = 0

        # Get chart data
        rows = self.db_manager.get_transactions_chart_data(
            default_currency_id, category_type=category_type, date_from=date_from, date_to=date_to
        )

        if not rows:
            self._show_no_data_label(
                self.scrollAreaWidgetContents_charts.layout(), "No data found for the selected period"
            )
            return

        # Group data by period
        grouped_data = self._group_data_by_period(rows, period)
        chart_data = list(grouped_data.items())

        # Create chart configuration
        chart_title = f"{chart_type} Transactions"
        if category != "All Categories":
            chart_title += f" - {category}"
        chart_title += f" ({period})"

        chart_config = {
            "title": chart_title,
            "xlabel": "Date",
            "ylabel": f"Amount ({default_currency_code})",
            "color": "green" if chart_type == "Income" else "red" if chart_type == "Expense" else "blue",
            "show_stats": True,
            "period": period,
        }

        self._create_chart(self.scrollAreaWidgetContents_charts.layout(), chart_data, chart_config)

    @requires_database(is_show_warning=False)
    def update_filter_comboboxes(self) -> None:
        """Update filter comboboxes with current data."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update category filter
            categories = self.db_manager.get_categories_by_type(0) + self.db_manager.get_categories_by_type(1)

            self.comboBox_filter_category.clear()
            self.comboBox_filter_category.addItem("")  # All categories
            self.comboBox_filter_category.addItems(categories)

            # Update currency filter
            currencies = [row[1] for row in self.db_manager.get_all_currencies()]  # Get codes

            self.comboBox_filter_currency.clear()
            self.comboBox_filter_currency.addItem("")  # All currencies
            self.comboBox_filter_currency.addItems(currencies)

        except Exception as e:
            print(f"Error updating filter comboboxes: {e}")

    @requires_database()
    def update_summary_labels(self) -> None:
        """Update summary labels with current totals in default currency."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get default currency
            default_currency_id = self.db_manager.get_default_currency_id()
            default_currency_info = self.db_manager.get_currency_by_code(self.db_manager.get_default_currency())
            currency_symbol = default_currency_info[2] if default_currency_info else "₽"

            # Для начальной загрузки показываем только суммы в валюте по умолчанию
            # без конвертации из других валют

            # Упрощенный запрос для получения сумм только в валюте по умолчанию
            query_income = """
                SELECT SUM(t.amount) as total_income
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 1 AND t._id_currencies = :currency_id
            """

            query_expenses = """
                SELECT SUM(t.amount) as total_expenses
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 0 AND t._id_currencies = :currency_id
            """

            income_rows = self.db_manager.get_rows(query_income, {"currency_id": default_currency_id})
            expenses_rows = self.db_manager.get_rows(query_expenses, {"currency_id": default_currency_id})

            total_income = float(income_rows[0][0] or 0) / 100 if income_rows and income_rows[0][0] else 0.0
            total_expenses = float(expenses_rows[0][0] or 0) / 100 if expenses_rows and expenses_rows[0][0] else 0.0

            # Update labels
            self.label_total_income.setText(f"Total Income: {total_income:.2f}{currency_symbol}")
            self.label_total_expenses.setText(f"Total Expenses: {total_expenses:.2f}{currency_symbol}")

            # Для today's balance и expenses также используем упрощенные запросы
            today = datetime.now().strftime("%Y-%m-%d")

            today_query_income = """
                SELECT SUM(t.amount) as total
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 1 AND t._id_currencies = :currency_id AND t.date = :date
            """

            today_query_expenses = """
                SELECT SUM(t.amount) as total
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 0 AND t._id_currencies = :currency_id AND t.date = :date
            """

            today_income_rows = self.db_manager.get_rows(
                today_query_income, {"currency_id": default_currency_id, "date": today}
            )
            today_expenses_rows = self.db_manager.get_rows(
                today_query_expenses, {"currency_id": default_currency_id, "date": today}
            )

            today_income = (
                float(today_income_rows[0][0] or 0) / 100 if today_income_rows and today_income_rows[0][0] else 0.0
            )
            today_expenses = (
                float(today_expenses_rows[0][0] or 0) / 100
                if today_expenses_rows and today_expenses_rows[0][0]
                else 0.0
            )

            today_balance = today_income - today_expenses

            self.label_daily_balance.setText(f"{today_balance:.2f}{currency_symbol}")
            self.label_today_expense.setText(f"{today_expenses:.2f}{currency_symbol}")

        except Exception as e:
            print(f"Error updating summary labels: {e}")
            # Set default values on error
            self.label_total_income.setText("Total Income: 0.00₽")
            self.label_total_expenses.setText("Total Expenses: 0.00₽")
            self.label_daily_balance.setText("0.00₽")
            self.label_today_expense.setText("0.00₽")

    def _calculate_daily_expenses(self, rows: list[list[Any]]) -> dict[str, float]:
        """Calculate daily expenses from transaction data.

        Args:
            rows: Raw transaction data from database.

        Returns:
            Dictionary mapping dates to total expenses for that day.

        """
        daily_expenses = {}

        for row in rows:
            # Raw data: [id, amount_cents, description, category_name, currency_code, date, tag, category_type, icon, symbol]
            amount_cents = row[1]
            date = row[5]
            category_type = row[7]

            # Only count expenses (category_type == 0)
            if category_type == 0:
                # Convert amount from minor units to display format using currency subdivision
                currency_code = row[4]
                if self.db_manager:
                    amount = self.db_manager.convert_from_minor_units(
                        amount_cents,
                        self.db_manager.get_currency_by_code(currency_code)[0]
                        if self.db_manager.get_currency_by_code(currency_code)
                        else 1,
                    )
                else:
                    amount = float(amount_cents) / 100  # Fallback

                if date in daily_expenses:
                    daily_expenses[date] += amount
                else:
                    daily_expenses[date] = amount

        return daily_expenses

    def _clear_account_form(self) -> None:
        """Clear the account addition form."""
        self.lineEdit_account_name.clear()
        self.doubleSpinBox_account_balance.setValue(0.0)
        self.checkBox_is_liquid.setChecked(True)
        self.checkBox_is_cash.setChecked(False)

    def _clear_all_forms(self) -> None:
        """Clear all input forms."""
        # Transaction form
        self.doubleSpinBox_amount.setValue(100.0)
        self.lineEdit_description.clear()
        self.lineEdit_tag.clear()

        # Category form
        self._clear_category_form()

        # Account form
        self._clear_account_form()

        # Currency form
        self._clear_currency_form()

        # Exchange form
        self._clear_exchange_form()

    def _clear_category_form(self) -> None:
        """Clear the category addition form."""
        self.lineEdit_category_name.clear()
        self.comboBox_category_type.setCurrentIndex(0)

    def _clear_currency_form(self) -> None:
        """Clear the currency addition form."""
        self.lineEdit_currency_code.clear()
        self.lineEdit_currency_name.clear()
        self.lineEdit_currency_symbol.clear()
        self.spinBox_subdivision.setValue(100)

    def _clear_exchange_form(self) -> None:
        """Clear the exchange addition form."""
        self.doubleSpinBox_exchange_from.setValue(100.0)
        self.doubleSpinBox_exchange_to.setValue(73.5)
        self.doubleSpinBox_exchange_rate.setValue(73.5)
        self.doubleSpinBox_exchange_fee.setValue(0.0)
        self.lineEdit_exchange_description.clear()

    def _clear_layout(self, layout) -> None:
        """Clear all widgets from the specified layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers."""
        # Main transaction signals
        self.pushButton_add.clicked.connect(self.on_add_transaction)
        self.pushButton_description_clear.clicked.connect(self.on_clear_description)
        self.pushButton_yesterday.clicked.connect(self.on_yesterday)

        # Delete and refresh buttons for all tables
        tables_with_controls = {
            "transactions": ("pushButton_delete", "pushButton_refresh"),
            "categories": ("pushButton_categories_delete", "pushButton_categories_refresh"),
            "accounts": ("pushButton_accounts_delete", "pushButton_accounts_refresh"),
            "currencies": ("pushButton_currencies_delete", "pushButton_currencies_refresh"),
            "currency_exchanges": ("pushButton_exchange_delete", "pushButton_exchange_refresh"),
            "exchange_rates": ("pushButton_rates_delete", "pushButton_rates_refresh"),
        }

        for table_name, (delete_btn_name, refresh_btn_name) in tables_with_controls.items():
            delete_button = getattr(self, delete_btn_name)
            refresh_button = getattr(self, refresh_btn_name)
            delete_button.clicked.connect(partial(self.delete_record, table_name))
            refresh_button.clicked.connect(self.update_all)

        # Add buttons
        self.pushButton_category_add.clicked.connect(self.on_add_category)
        self.pushButton_account_add.clicked.connect(self.on_add_account)
        self.pushButton_currency_add.clicked.connect(self.on_add_currency)
        self.pushButton_exchange_add.clicked.connect(self.on_add_exchange)

        # Filter signals
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

        # Auto-filter signals for radio buttons
        self.radioButton.clicked.connect(self.apply_filter)
        self.radioButton_2.clicked.connect(self.apply_filter)
        self.radioButton_3.clicked.connect(self.apply_filter)

        # Auto-filter signals for combo boxes
        self.comboBox_filter_category.currentTextChanged.connect(lambda _: self.apply_filter())
        self.comboBox_filter_currency.currentTextChanged.connect(lambda _: self.apply_filter())

        # Chart signals
        self.pushButton_update_chart.clicked.connect(self.update_charts)
        self.pushButton_pie_chart.clicked.connect(self.show_pie_chart)
        self.pushButton_balance_chart.clicked.connect(self.show_balance_chart)
        self.pushButton_chart_last_month.clicked.connect(self.set_chart_last_month)
        self.pushButton_chart_last_year.clicked.connect(self.set_chart_last_year)
        self.pushButton_chart_all_time.clicked.connect(self.set_chart_all_time)

        # Exchange signals
        self.pushButton_calculate_exchange.clicked.connect(self.on_calculate_exchange)
        self.pushButton_exchange_yesterday.clicked.connect(self.on_yesterday_exchange)

        # Currency signals
        self.pushButton_set_default_currency.clicked.connect(self.on_set_default_currency)

        # Rate signals
        self.pushButton_exchange_update.clicked.connect(self.on_update_exchange_rates)

        # Exchange rates chart signals
        self.comboBox_exchange_rates_currency.currentIndexChanged.connect(self.on_exchange_rates_currency_changed)
        self.pushButton_exchange_rates_last_month.clicked.connect(self.on_exchange_rates_last_month)
        self.pushButton_exchange_rates_last_year.clicked.connect(self.on_exchange_rates_last_year)
        self.pushButton_exchange_rates_all_time.clicked.connect(self.on_exchange_rates_all_time)

        # Auto-update chart when dates change
        self.dateEdit_exchange_rates_from.dateChanged.connect(self.on_exchange_rates_update)
        self.dateEdit_exchange_rates_to.dateChanged.connect(self.on_exchange_rates_update)

        # Report signals
        self.pushButton_generate_report.clicked.connect(self.on_generate_report)

        # Export signal
        self.pushButton_show_all_records.clicked.connect(self.on_show_all_records_clicked)

        # Add context menu for transactions table
        self.tableView_transactions.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_transactions.customContextMenuRequested.connect(self._show_transactions_context_menu)

        # Tab change signal
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Enter key handling for doubleSpinBox_amount
        self.doubleSpinBox_amount.installEventFilter(self)

        # Enter key handling for dateEdit
        self.dateEdit.installEventFilter(self)

        # Enter key handling for lineEdit_tag
        self.lineEdit_tag.installEventFilter(self)

        # Enter key handling for pushButton_add
        self.pushButton_add.installEventFilter(self)

    def _connect_table_auto_save_signals(self) -> None:
        """Connect dataChanged signals for auto-save functionality."""
        # Connect auto-save signals for each table
        for table_name in self._SAFE_TABLES:
            if self.models[table_name] is not None:
                # Use partial to properly bind table_name
                handler = partial(self._on_table_data_changed, table_name)
                model = self.models[table_name]
                if model is not None and hasattr(model, "sourceModel") and model.sourceModel() is not None:
                    model.sourceModel().dataChanged.connect(handler)

    def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None:
        """Copy selected cells from table to clipboard as tab-separated text.

        Args:

        - `table_view` (`QTableView`): The table view to copy data from.

        """
        selection_model = table_view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return

        # Get selected indexes and sort them by row and column
        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            return

        # Sort indexes by row first, then by column
        selected_indexes.sort(key=lambda index: (index.row(), index.column()))

        # Group indexes by row
        rows_data = {}
        for index in selected_indexes:
            row = index.row()
            if row not in rows_data:
                rows_data[row] = {}

            # Get cell data
            cell_data = table_view.model().data(index, Qt.ItemDataRole.DisplayRole)
            rows_data[row][index.column()] = str(cell_data) if cell_data is not None else ""

        # Build clipboard text
        clipboard_text = []
        for row in sorted(rows_data.keys()):
            row_data = rows_data[row]
            # Get all columns for this row and fill missing ones with empty strings
            if row_data:
                min_col = min(row_data.keys())
                max_col = max(row_data.keys())
                clipboard_text.append("\t".join([row_data.get(col, "") for col in range(min_col, max_col + 1)]))

        # Copy to clipboard
        if clipboard_text:
            final_text = "\n".join(clipboard_text)
            clipboard = QApplication.clipboard()
            clipboard.setText(final_text)
            print(f"Copied {len(clipboard_text)} rows to clipboard")

    def _create_colored_table_model(
        self,
        data: list[list],
        headers: list[str],
        id_column: int = -2,
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with colored table data.

        Args:

        - `data` (`list[list]`): The table data with color information.
        - `headers` (`list[str]`): Column header names.
        - `id_column` (`int`): Index of the ID column. Defaults to `-2` (second-to-last).

        Returns:

        - `QSortFilterProxyModel`: A filterable and sortable model with colored data.

        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID (second-to-last element)
            row_color = row[-1]  # Color is at the last position
            row_id = row[id_column]  # ID is at second-to-last position

            # Create items for display columns only (exclude ID and color)
            items = []
            display_data = row[:-2]  # Exclude last two elements (ID and color)

            for _col_idx, value in enumerate(display_data):
                item = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

                items.append(item)

            model.appendRow(items)

            # Set the ID in vertical header
            model.setVerticalHeaderItem(
                row_idx,
                QStandardItem(str(row_id)),
            )

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy

    def _create_exchange_rate_chart(self, currency_id: int, date_from: str, date_to: str) -> None:
        """Create and display exchange rate chart.

        Args:
            currency_id: ID of the currency
            date_from: Start date in yyyy-MM-dd format
            date_to: End date in yyyy-MM-dd format
        """
        if not self._validate_database_connection():
            return

        try:
            # Get currency info
            currency_info = self.db_manager.get_currency_by_id(currency_id)
            if not currency_info:
                self._show_no_data_label(self.verticalLayout_exchange_rates_content, "Currency not found")
                return

            currency_code, currency_name, currency_symbol = currency_info

            # Get exchange rates data
            rates_data = self._get_exchange_rates_data(currency_id, date_from, date_to)

            if not rates_data:
                self._show_no_data_label(
                    self.verticalLayout_exchange_rates_content, "No exchange rate data found for the selected period"
                )
                return

            # Clear existing chart
            self._clear_layout(self.verticalLayout_exchange_rates_content)

            # Create matplotlib figure
            fig = Figure(figsize=(12, 6), dpi=100)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            # Extract dates and rates, and transform rates to match table display
            dates = [row[0] for row in rates_data]
            # Transform rates: stored as USD→currency, but display as currency→USD (like in table)
            transformed_rates = []
            for row in rates_data:
                usd_to_currency_rate = float(row[1])
                if usd_to_currency_rate != 0:
                    currency_to_usd_rate = 1.0 / usd_to_currency_rate
                    transformed_rates.append(currency_to_usd_rate)
                else:
                    transformed_rates.append(0.0)

            # Convert dates to datetime objects for plotting
            from datetime import datetime

            date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

            # Plot the data
            ax.plot(date_objects, transformed_rates, color="#2E86AB", linewidth=2)

            # Customize plot
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel(f"Exchange Rate ({currency_code} to USD)", fontsize=12)
            ax.set_title(f"Exchange Rate: {currency_code} to USD ({currency_name})", fontsize=14, fontweight="bold")

            # Format x-axis dates
            ax.tick_params(axis="x", rotation=45)
            fig.autofmt_xdate()

            # Add grid
            ax.grid(visible=True, alpha=0.3)

            # Add value labels for significant points
            if len(transformed_rates) > 1:
                # Label first and last points
                ax.annotate(
                    f"{transformed_rates[0]:.6f}",
                    (date_objects[0], transformed_rates[0]),
                    xytext=(10, 10),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
                )

                ax.annotate(
                    f"{transformed_rates[-1]:.6f}",
                    (date_objects[-1], transformed_rates[-1]),
                    xytext=(10, 10),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
                )

                # Label min and max points if different from first/last
                min_rate = min(transformed_rates)
                max_rate = max(transformed_rates)
                min_idx = transformed_rates.index(min_rate)
                max_idx = transformed_rates.index(max_rate)

                if min_idx != 0 and min_idx != len(transformed_rates) - 1:
                    ax.annotate(
                        f"{min_rate:.6f}",
                        (date_objects[min_idx], min_rate),
                        xytext=(10, -15),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7),
                    )

                if max_idx != 0 and max_idx != len(transformed_rates) - 1:
                    ax.annotate(
                        f"{max_rate:.6f}",
                        (date_objects[max_idx], max_rate),
                        xytext=(10, 15),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7),
                    )

            # Add statistics text
            if len(transformed_rates) > 1:
                avg_rate = sum(transformed_rates) / len(transformed_rates)
                rate_change = transformed_rates[-1] - transformed_rates[0]
                rate_change_percent = (rate_change / transformed_rates[0]) * 100 if transformed_rates[0] != 0 else 0

                stats_text = f"Period: {date_from} to {date_to}\n"
                stats_text += f"Data points: {len(transformed_rates)}\n"
                stats_text += f"Average rate: {avg_rate:.6f}\n"
                stats_text += f"Change: {rate_change:+.6f} ({rate_change_percent:+.2f}%)"

                ax.text(
                    0.02,
                    0.98,
                    stats_text,
                    transform=ax.transAxes,
                    verticalalignment="top",
                    fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8),
                )

            fig.tight_layout()
            self.verticalLayout_exchange_rates_content.addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error creating exchange rate chart: {e}")
            self._show_no_data_label(self.verticalLayout_exchange_rates_content, f"Error creating chart: {e}")

    def _create_pie_chart(self, data: dict[str, float], title: str) -> None:
        """Create a pie chart with the given data.

        Args:

        - `data` (`dict[str, float]`): Dictionary of category names and amounts.
        - `title` (`str`): Chart title.

        """
        # Clear existing chart
        self._clear_layout(self.scrollAreaWidgetContents_charts.layout())

        if not data:
            self._show_no_data_label(self.scrollAreaWidgetContents_charts.layout(), "No data for pie chart")
            return

        # Create matplotlib figure
        fig = Figure(figsize=(10, 8), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Prepare data for pie chart
        labels = list(data.keys())
        sizes = list(data.values())

        # Create pie chart
        pie_result = ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        wedges, texts, autotexts = pie_result if len(pie_result) == 3 else (pie_result[0], pie_result[1], [])

        # Customize appearance
        ax.set_title(title, fontsize=14, fontweight="bold")

        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        fig.tight_layout()
        self.scrollAreaWidgetContents_charts.layout().addWidget(canvas)
        canvas.draw()

    def _create_table_model(
        self,
        data: list[list[str]],
        headers: list[str],
        id_column: int = 0,
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with data.

        Args:

        - `data` (`list[list[str]]`): The table data as a list of rows.
        - `headers` (`list[str]`): Column header names.
        - `id_column` (`int`): Index of the ID column. Defaults to `0`.

        Returns:

        - `QSortFilterProxyModel`: A filterable and sortable model with the data.

        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            items = [
                QStandardItem(str(value) if value is not None else "")
                for col_idx, value in enumerate(row)
                if col_idx != id_column
            ]
            model.appendRow(items)
            model.setVerticalHeaderItem(
                row_idx,
                QStandardItem(str(row[id_column])),
            )

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy

    def _create_transactions_table_model(
        self,
        data: list[list],
        headers: list[str],
        id_column: int = -2,
    ) -> QSortFilterProxyModel:
        """Create a special model for transactions table with non-editable total column.

        Args:
            data: The table data with color information.
            headers: Column header names.
            id_column: Index of the ID column. Defaults to -2 (second-to-last).

        Returns:
            A filterable and sortable model with colored data and non-editable total column.

        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID (second-to-last element)
            row_color = row[-1]  # Color is at the last position
            row_id = row[id_column]  # ID is at second-to-last position

            # Create items for display columns only (exclude ID and color)
            items = []
            display_data = row[:-2]  # Exclude last two elements (ID and color)

            for col_idx, value in enumerate(display_data):
                item = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

                # For amount column (index 1), store original value without minus sign for editing
                if col_idx == 1:  # Amount column
                    # Remove minus sign for editing, keep only the numeric value
                    original_value = str(value).replace("-", "") if value and str(value).startswith("-") else str(value)
                    item.setData(original_value, Qt.ItemDataRole.UserRole)

                # Make the "Total per day" column (last column) non-editable
                if col_idx == len(display_data) - 1:  # Last column
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                items.append(item)

            model.appendRow(items)

            # Set the ID in vertical header
            model.setVerticalHeaderItem(
                row_idx,
                QStandardItem(str(row_id)),
            )

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy

    def _dispose_models(self) -> None:
        """Detach all models from QTableView and delete them."""
        for key, model in self.models.items():
            if key in self.table_config:
                view = self.table_config[key][0]
                view.setModel(None)
            if model is not None:
                model.deleteLater()
            self.models[key] = None

    def _finish_window_initialization(self) -> None:
        """Finish window initialization by showing the window."""
        self.show()

        # Set focus to description field
        self.lineEdit_description.setFocus()

        # Select category with _id = 1
        self._select_category_by_id(1)

        # Setup exchange rates controls
        self._setup_exchange_rates_controls()

    def _focus_amount_and_select_text(self) -> None:
        """Set focus to amount field and select all text."""
        self.doubleSpinBox_amount.setFocus()
        self.doubleSpinBox_amount.selectAll()

    def _focus_description_and_select_text(self) -> None:
        """Set focus to description field and select all text."""
        self.lineEdit_description.setFocus()
        self.lineEdit_description.selectAll()

    def _generate_account_balances_report(self, currency_id: int) -> None:
        """Generate account balances report.

        Args:

        - `currency_id` (`int`): Currency ID for conversion.

        """
        if self.db_manager is None:
            return

        account_balances = self.db_manager.get_account_balances_in_currency(currency_id)
        currency_code = self.db_manager.get_default_currency()

        # Create report data
        report_data = []
        total_balance = 0.0

        for account_name, balance in account_balances:
            report_data.append([account_name, f"{balance:.2f} {currency_code}"])
            total_balance += balance

        # Add total row
        report_data.append(["TOTAL", f"{total_balance:.2f} {currency_code}"])

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Account", "Balance"])

        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            # Highlight total row
            if row_data[0] == "TOTAL":
                for item in items:
                    item.setBackground(QBrush(QColor(255, 255, 0)))  # Yellow background
            model.appendRow(items)

        self.tableView_reports.setModel(model)

        # Configure column stretching for reports table
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)

    def _generate_category_analysis_report(self, currency_id: int) -> None:
        """Generate category analysis report.

        Args:

        - `currency_id` (`int`): Currency ID for conversion.

        """
        if self.db_manager is None:
            return

        currency_code = self.db_manager.get_default_currency()

        # Get transactions for last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        date_from = start_date.strftime("%Y-%m-%d")
        date_to = end_date.strftime("%Y-%m-%d")

        # Get expenses and income separately
        expense_rows = self.db_manager.get_filtered_transactions(category_type=0, date_from=date_from, date_to=date_to)
        income_rows = self.db_manager.get_filtered_transactions(category_type=1, date_from=date_from, date_to=date_to)

        # Group by category
        expense_totals = {}
        income_totals = {}

        for row in expense_rows:
            category = row[3]  # category name
            amount = float(row[1]) / 100  # amount in cents
            expense_totals[category] = expense_totals.get(category, 0) + amount

        for row in income_rows:
            category = row[3]  # category name
            amount = float(row[1]) / 100  # amount in cents
            income_totals[category] = income_totals.get(category, 0) + amount

        # Create report data
        report_data = []

        # Add expense categories
        if expense_totals:
            report_data.append(["EXPENSES", "", ""])
            for category, amount in sorted(expense_totals.items(), key=lambda x: x[1], reverse=True):
                report_data.append([category, f"{amount:.2f} {currency_code}", "Expense"])

        # Add income categories
        if income_totals:
            report_data.append(["INCOME", "", ""])
            for category, amount in sorted(income_totals.items(), key=lambda x: x[1], reverse=True):
                report_data.append([category, f"{amount:.2f} {currency_code}", "Income"])

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Category", "Amount", "Type"])

        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            # Highlight section headers
            if row_data[0] in ["EXPENSES", "INCOME"]:
                for item in items:
                    item.setBackground(QBrush(QColor(200, 200, 255)))  # Light blue background
            model.appendRow(items)

        self.tableView_reports.setModel(model)

        # Configure column stretching for reports table
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)

    def _generate_currency_analysis_report(self) -> None:
        """Generate currency analysis report."""
        if self.db_manager is None:
            return

        # Get all currencies and their usage
        currencies = self.db_manager.get_all_currencies()

        report_data = []
        for currency_row in currencies:
            currency_id = currency_row[0]
            currency_code = currency_row[1]

            # Count transactions in this currency
            transactions = self.db_manager.get_filtered_transactions(currency_code=currency_code)
            transaction_count = len(transactions)

            # Calculate total amount
            total_amount = sum(float(row[1]) / 100 for row in transactions)

            report_data.append([currency_code, str(transaction_count), f"{total_amount:.2f}"])

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Currency", "Transaction Count", "Total Amount"])

        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            model.appendRow(items)

        self.tableView_reports.setModel(model)

        # Configure column stretching for reports table
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)

    def _generate_income_vs_expenses_report(self, currency_id: int) -> None:
        """Generate income vs expenses report.

        Args:

        - `currency_id` (`int`): Currency ID for conversion.

        """
        if self.db_manager is None:
            return

        currency_code = self.db_manager.get_default_currency()

        # Get data for different periods
        periods = [
            ("Today", 0),
            ("Last 7 days", 7),
            ("Last 30 days", 30),
            ("Last 90 days", 90),
            ("Last 365 days", 365),
        ]

        report_data = []

        for period_name, days in periods:
            if days == 0:
                # Today
                today = datetime.now().strftime("%Y-%m-%d")
                date_from = date_to = today
            else:
                # Last N days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                date_from = start_date.strftime("%Y-%m-%d")
                date_to = end_date.strftime("%Y-%m-%d")

            income, expenses = self.db_manager.get_income_vs_expenses_in_currency(currency_id, date_from, date_to)

            balance = income - expenses

            report_data.append(
                [
                    period_name,
                    f"{income:.2f} {currency_code}",
                    f"{expenses:.2f} {currency_code}",
                    f"{balance:.2f} {currency_code}",
                ]
            )

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Period", "Income", "Expenses", "Balance"])

        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            # Color code the balance
            balance_str = row_data[3]
            balance_value = float(balance_str.split()[0])
            if balance_value > 0:
                items[3].setBackground(QBrush(QColor(200, 255, 200)))  # Light green
            elif balance_value < 0:
                items[3].setBackground(QBrush(QColor(255, 200, 200)))  # Light red

            model.appendRow(items)

        self.tableView_reports.setModel(model)

        # Configure column stretching for reports table
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)

    def _generate_monthly_summary_report(self, currency_id: int) -> None:
        """Generate monthly summary report.

        Args:

        - `currency_id` (`int`): Currency ID for conversion.

        """
        if self.db_manager is None:
            return

        currency_code = self.db_manager.get_default_currency()

        # Get last 12 months
        report_data = []
        end_date = datetime.now()

        for i in range(12):
            # Calculate month start and end
            month_date = end_date.replace(day=1) - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)

            # Calculate last day of month
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            month_end = next_month - timedelta(days=1)

            date_from = month_start.strftime("%Y-%m-%d")
            date_to = month_end.strftime("%Y-%m-%d")

            income, expenses = self.db_manager.get_income_vs_expenses_in_currency(currency_id, date_from, date_to)

            balance = income - expenses
            month_name = month_start.strftime("%Y-%m")

            report_data.append(
                [
                    month_name,
                    f"{income:.2f} {currency_code}",
                    f"{expenses:.2f} {currency_code}",
                    f"{balance:.2f} {currency_code}",
                ]
            )

        # Reverse to show oldest first
        report_data.reverse()

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Month", "Income", "Expenses", "Balance"])

        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            model.appendRow(items)

        self.tableView_reports.setModel(model)

        # Configure column stretching for reports table
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)

    def _get_exchange_rates_data(self, currency_id: int, date_from: str, date_to: str) -> list[tuple[str, float]]:
        """Get exchange rates data for the specified currency and date range.

        Args:
            currency_id: ID of the currency
            date_from: Start date in yyyy-MM-dd format
            date_to: End date in yyyy-MM-dd format

        Returns:
            List of tuples (date, rate) sorted by date
        """
        if not self._validate_database_connection():
            return []

        try:
            # Get exchange rates for the currency in the date range
            query = """
                SELECT date, rate
                FROM exchange_rates
                WHERE _id_currency = :currency_id
                AND date BETWEEN :date_from AND :date_to
                ORDER BY date ASC
            """
            params = {"currency_id": currency_id, "date_from": date_from, "date_to": date_to}

            # Execute query and get results
            query_obj = self.db_manager.execute_query(query, params)
            if query_obj:
                rows = self.db_manager._rows_from_query(query_obj)
                query_obj.clear()
                return [(row[0], float(row[1])) for row in rows if row[1] is not None]
            return []

        except Exception as e:
            print(f"Error getting exchange rates data: {e}")
            return []

    def _init_chart_controls(self) -> None:
        """Initialize chart controls."""
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)

    def _init_database(self) -> None:
        """Initialize database connection."""
        filename = Path(config["sqlite_finance"])

        # Try to open existing database first
        if filename.exists():
            try:
                temp_db_manager = database_manager.DatabaseManager(str(filename))

                # Check if required tables exist
                if temp_db_manager.table_exists("transactions"):
                    print(f"Database opened successfully: {filename}")
                    self.db_manager = temp_db_manager
                    return
                print(f"Database exists but required tables are missing at {filename}")
                temp_db_manager.close()
            except Exception as e:
                print(f"Failed to open existing database: {e}")

        # Database doesn't exist or is missing required tables
        if not filename.exists():
            filename_str, _ = QFileDialog.getOpenFileName(
                self,
                "Open Database",
                str(filename.parent),
                "SQLite Database (*.db)",
            )
            if not filename_str:
                QMessageBox.critical(self, "Error", "No database selected")
                sys.exit(1)
            filename = Path(filename_str)

        try:
            self.db_manager = database_manager.DatabaseManager(str(filename))
            print(f"Database opened successfully: {filename}")
        except (OSError, RuntimeError, ConnectionError) as exc:
            QMessageBox.critical(self, "Error", f"Failed to open database: {exc}")
            sys.exit(1)

    def _init_filter_controls(self) -> None:
        """Initialize filter controls."""
        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)
        self.checkBox_use_date_filter.setChecked(False)

    def _initial_load(self) -> None:
        """Initial load of essential data at startup (without exchange rates)."""
        if not self._validate_database_connection():
            print("Database connection not available for initial load")
            return

        # Load essential tables only (excluding exchange rates)
        self._load_essential_tables()
        self._update_comboboxes()
        self.update_filter_comboboxes()
        self.update_chart_comboboxes()
        self.set_today_date()
        self.update_summary_labels()

        # Clear forms
        self._clear_all_forms()

        # Setup exchange rates controls
        self._setup_exchange_rates_controls()

    def _load_accounts_table(self) -> None:
        """Load accounts table."""
        accounts_data = self.db_manager.get_all_accounts()

        # Define colors for different account groups
        account_colors = {
            (0, 1): QColor(220, 255, 220),  # is_cash=0, is_liquid=1 - Light green
            (1, 1): QColor(255, 255, 200),  # is_cash=1, is_liquid=1 - Light yellow
            (0, 0): QColor(255, 220, 220),  # is_cash=0, is_liquid=0 - Light red
            (1, 0): QColor(255, 200, 255),  # is_cash=1, is_liquid=0 - Light purple
        }

        # Group accounts by (is_cash, is_liquid) and sort within groups
        account_groups = {
            (0, 1): [],  # is_cash=0, is_liquid=1
            (1, 1): [],  # is_cash=1, is_liquid=1
            (0, 0): [],  # is_cash=0, is_liquid=0
            (1, 0): [],  # is_cash=1, is_liquid=0
        }

        for row in accounts_data:
            # Raw data: [id, name, balance_cents, currency_code, is_liquid, is_cash]
            is_liquid = row[4]
            is_cash = row[5]
            group_key = (is_cash, is_liquid)
            account_groups[group_key].append(row)

        # Sort each group alphabetically by name
        for group in account_groups.values():
            group.sort(key=lambda x: x[1].lower())  # Sort by name (case-insensitive)

        # Combine groups in the specified order
        accounts_transformed_data = []
        for group_key in [(0, 1), (1, 1), (0, 0), (1, 0)]:
            color = account_colors[group_key]
            for row in account_groups[group_key]:
                # Transform: [id, name, balance_cents, currency_code, is_liquid, is_cash, currency_id] -> [name, balance, currency, liquid, cash, id, color]
                currency_id = row[6]  # currency_id
                balance = self.db_manager.convert_from_minor_units(row[2], currency_id)
                liquid_str = "👍" if row[4] == 1 else "👎"
                cash_str = "💵" if row[5] == 1 else "💳"
                transformed_row = [row[1], f"{balance:.2f}", row[3], liquid_str, cash_str, row[0], color]
                accounts_transformed_data.append(transformed_row)

        self.models["accounts"] = self._create_colored_table_model(
            accounts_transformed_data, self.table_config["accounts"][2]
        )
        self.tableView_accounts.setModel(self.models["accounts"])

        # Make accounts table non-editable and connect double-click signal
        self.tableView_accounts.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.tableView_accounts.doubleClicked.connect(self._on_account_double_clicked)

        # Configure column stretching for accounts table
        accounts_header = self.tableView_accounts.horizontalHeader()
        if accounts_header.count() > 0:
            for i in range(accounts_header.count()):
                accounts_header.setSectionResizeMode(i, accounts_header.ResizeMode.Stretch)
            # Ensure stretch settings are applied
            accounts_header.setStretchLastSection(False)

    def _load_categories_table(self) -> None:
        """Load categories table."""
        categories_data = self.db_manager.get_all_categories()
        categories_transformed_data = []
        for row in categories_data:
            # Transform: [id, name, type, icon] -> [name, type_str, icon, id, color]
            type_str = "Expense" if row[2] == 0 else "Income"
            color = QColor(255, 200, 200) if row[2] == 0 else QColor(200, 255, 200)
            transformed_row = [row[1], type_str, row[3], row[0], color]
            categories_transformed_data.append(transformed_row)

        self.models["categories"] = self._create_colored_table_model(
            categories_transformed_data, self.table_config["categories"][2]
        )
        self.tableView_categories.setModel(self.models["categories"])

        # Configure column stretching for categories table
        categories_header = self.tableView_categories.horizontalHeader()
        if categories_header.count() > 0:
            for i in range(categories_header.count()):
                categories_header.setSectionResizeMode(i, categories_header.ResizeMode.Stretch)

    def _load_currencies_table(self) -> None:
        """Load currencies table."""
        currencies_data = self.db_manager.get_all_currencies()
        currencies_transformed_data = []
        for row in currencies_data:
            # Transform: [id, code, name, symbol] -> [code, name, symbol, id, color]
            color = QColor(255, 255, 220)
            transformed_row = [row[1], row[2], row[3], row[0], color]
            currencies_transformed_data.append(transformed_row)

        self.models["currencies"] = self._create_colored_table_model(
            currencies_transformed_data, self.table_config["currencies"][2]
        )
        self.tableView_currencies.setModel(self.models["currencies"])

        # Configure column stretching for currencies table
        currencies_header = self.tableView_currencies.horizontalHeader()
        if currencies_header.count() > 0:
            for i in range(currencies_header.count()):
                currencies_header.setSectionResizeMode(i, currencies_header.ResizeMode.Stretch)

    def _load_currency_exchanges_table(self) -> None:
        """Load currency exchanges table."""
        if self.db_manager is None:
            return

        exchanges_data = self.db_manager.get_all_currency_exchanges()
        exchanges_transformed_data = []
        for row in exchanges_data:
            # Transform: [id, from_code, to_code, amount_from, amount_to, rate, fee, date, description]
            # Данные уже конвертированы в get_all_currency_exchanges()
            color = QColor(255, 240, 255)
            transformed_row = [
                row[1],  # from_code
                row[2],  # to_code
                f"{row[3]:.2f}",  # amount_from (уже конвертировано)
                f"{row[4]:.2f}",  # amount_to (уже конвертировано)
                f"{row[5]:.4f}",  # rate (уже конвертировано)
                f"{row[6]:.2f}",  # fee (уже конвертировано)
                row[7],  # date
                row[8] or "",  # description
                row[0],  # id
                color,
            ]
            exchanges_transformed_data.append(transformed_row)

        self.models["currency_exchanges"] = self._create_colored_table_model(
            exchanges_transformed_data, self.table_config["currency_exchanges"][2]
        )
        self.tableView_exchange.setModel(self.models["currency_exchanges"])

        # Configure column stretching for exchange table
        exchange_header = self.tableView_exchange.horizontalHeader()
        if exchange_header.count() > 0:
            for i in range(exchange_header.count()):
                exchange_header.setSectionResizeMode(i, exchange_header.ResizeMode.Stretch)
            # Ensure stretch settings are applied
            exchange_header.setStretchLastSection(False)

    def _load_essential_tables(self) -> None:
        """Load essential tables at startup (excluding exchange rates for lazy loading)."""
        if not self._validate_database_connection():
            print("Database connection not available for showing essential tables")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Load each table individually with error handling
            tables_to_load = [
                ("transactions", self._load_transactions_table),
                ("categories", self._load_categories_table),
                ("accounts", self._load_accounts_table),
                ("currencies", self._load_currencies_table),
                ("currency_exchanges", self._load_currency_exchanges_table),
            ]

            for table_name, load_method in tables_to_load:
                try:
                    load_method()
                except Exception as e:
                    print(f"❌ Error loading {table_name} table: {e}")
                    # Продолжаем загрузку других таблиц

            # Connect auto-save signals for loaded tables
            self._connect_table_auto_save_signals()

        except Exception as e:
            print(f"Error loading essential tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load essential tables: {e}")

    def _load_transactions_table(self) -> None:
        """Load transactions table."""
        limit = None if self.show_all_transactions else self.count_transactions_to_show
        transactions_data = self.db_manager.get_all_transactions(limit=limit)
        transactions_transformed_data = self._transform_transaction_data(transactions_data)
        self.models["transactions"] = self._create_transactions_table_model(
            transactions_transformed_data, self.table_config["transactions"][2]
        )
        self.tableView_transactions.setModel(self.models["transactions"])

        # Special handling for transactions table - column stretching setup
        header = self.tableView_transactions.horizontalHeader()
        if header.count() > 0:
            # Set stretch mode for all columns except the last two
            for i in range(header.count() - 2):
                header.setSectionResizeMode(i, header.ResizeMode.Stretch)

            # For the second-to-last column (Tag) set fixed width
            second_last_column = header.count() - 2
            header.setSectionResizeMode(second_last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(second_last_column, 100)

            # For the last column (Total per day) set fixed width
            last_column = header.count() - 1
            header.setSectionResizeMode(last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(last_column, 120)

    def _mark_categories_changed(self) -> None:
        """Mark that category data has changed and needs refresh."""
        # No specific action needed for categories as they load immediately
        pass

    def _mark_currencies_changed(self) -> None:
        """Mark that currency data has changed and needs refresh."""
        # No specific action needed for currencies as they load immediately
        pass

    def _mark_default_currency_changed(self) -> None:
        """Mark that default currency has changed and needs refresh."""
        # No specific action needed as this affects multiple areas that reload immediately
        pass

    def _mark_exchange_rates_changed(self) -> None:
        """Mark that exchange rates data has changed and needs refresh."""
        # Mark exchange rates as needing reload
        self.exchange_rates_loaded = False

    # Lazy loading change markers
    def _mark_transactions_changed(self) -> None:
        """Mark that transaction data has changed and needs refresh."""
        # No specific action needed for transactions as they load immediately
        pass

    def _on_account_double_clicked(self, index: QModelIndex) -> None:
        """Handle double-click on accounts table.

        Args:

        - `index` (`QModelIndex`): The clicked index.

        """
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # Get the row ID from vertical header
            proxy_model = self.models["accounts"]
            if proxy_model is None:
                return

            source_model = proxy_model.sourceModel()
            if source_model is None:
                return

            row_id_item = source_model.verticalHeaderItem(index.row())
            if row_id_item is None:
                return

            account_id = int(row_id_item.text())

            # Get account data
            account_data = self.db_manager.get_account_by_id(account_id)
            if not account_data:
                QMessageBox.warning(self, "Error", "Account not found")
                return

            # Prepare account data for dialog
            currency_id = account_data[6]  # currency_id
            account_dict = {
                "id": account_data[0],
                "name": account_data[1],
                "balance": self.db_manager.convert_from_minor_units(account_data[2], currency_id),
                "currency_code": account_data[3],
                "is_liquid": account_data[4] == 1,
                "is_cash": account_data[5] == 1,
            }

            # Get currency codes for dialog
            currencies = [row[1] for row in self.db_manager.get_all_currencies()]

            # Show edit dialog
            dialog = AccountEditDialog(self, account_dict, currencies)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                result = dialog.get_result()

                if result["action"] == "save":
                    # Update account
                    currency_info = self.db_manager.get_currency_by_code(result["currency_code"])
                    if not currency_info:
                        QMessageBox.warning(self, "Error", "Currency not found")
                        return

                    currency_id = currency_info[0]

                    success = self.db_manager.update_account(
                        account_id,
                        result["name"],
                        result["balance"],
                        currency_id,
                        is_liquid=result["is_liquid"],
                        is_cash=result["is_cash"],
                    )

                    if success:
                        # Save current column widths before update
                        column_widths = self._save_table_column_widths(self.tableView_accounts)

                        self.update_all()

                        # Restore column widths after update
                        self._restore_table_column_widths(self.tableView_accounts, column_widths)

                        QMessageBox.information(self, "Success", "Account updated successfully")
                        return  # Exit the method to prevent reopening the dialog
                    QMessageBox.warning(self, "Error", "Failed to update account")

                elif result["action"] == "delete":
                    # Save current column widths before update
                    column_widths = self._save_table_column_widths(self.tableView_accounts)

                    # Delete account
                    success = self.db_manager.delete_account(account_id)
                    if success:
                        self.update_all()

                        # Restore column widths after update
                        self._restore_table_column_widths(self.tableView_accounts, column_widths)

                        QMessageBox.information(self, "Success", "Account deleted successfully")
                        return  # Exit the method to prevent reopening the dialog
                    QMessageBox.warning(self, "Error", "Failed to delete account")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit account: {e}")

    def _on_autocomplete_selected(self, text: str) -> None:
        """Handle autocomplete selection and populate form fields."""
        if not text:
            return

        # Set the selected text
        self.lineEdit_description.setText(text)

        # Try to populate other fields based on the selected description
        self._populate_form_from_description(text)

        # Set focus to amount field and select all text after a short delay
        # This ensures form population is complete before focusing
        QTimer.singleShot(100, self._focus_amount_and_select_text)

    def _on_currency_started(self, currency_code: str):
        """Handle currency processing start."""
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.setText(f"Processing {currency_code}...")

    def _on_progress_updated(self, message: str):
        """Handle progress updates from worker."""
        print(message)
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.setText(message)

    def _on_rate_added(self, currency_code: str, rate: float, date_str: str):
        """Handle successful rate addition."""
        print(f"✅ Added {currency_code}/USD rate: {rate:.6f} for {date_str}")

    def _on_table_data_changed(
        self, table_name: str, top_left: QModelIndex, bottom_right: QModelIndex, _roles: list | None = None
    ) -> None:
        """Handle data changes in table models and auto-save to database.

        Args:

        - `table_name` (`str`): Name of the table that was modified.
        - `top_left` (`QModelIndex`): Top-left index of the changed area.
        - `bottom_right` (`QModelIndex`): Bottom-right index of the changed area.
        - `_roles` (`list | None`): List of roles that changed. Defaults to `None`.

        """
        if table_name not in self._SAFE_TABLES:
            return

        if not self._validate_database_connection():
            return

        try:
            proxy_model = self.models[table_name]
            if proxy_model is None:
                return
            model = proxy_model.sourceModel()
            if not isinstance(model, QStandardItemModel):
                return

            # Process each changed row
            for row in range(top_left.row(), bottom_right.row() + 1):
                vertical_header_item = model.verticalHeaderItem(row)
                if vertical_header_item:
                    row_id = vertical_header_item.text()
                    self._auto_save_row(table_name, model, row, row_id)

        except Exception as e:
            QMessageBox.warning(self, "Auto-save Error", f"Failed to auto-save changes: {e!s}")

    def _on_update_finished_error(self, error_message: str):
        """Handle error completion."""
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        QMessageBox.critical(self, "Update Error", f"Failed to update exchange rates:\n{error_message}")
        print(f"❌ {error_message}")

    def _on_update_finished_success(self, downloaded_count: int, filled_count: int):
        """Handle successful completion."""
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        total_updates = downloaded_count + filled_count
        message_parts = []

        if downloaded_count > 0:
            message_parts.append(f"Downloaded {downloaded_count} new exchange rates")

        if filled_count > 0:
            message_parts.append(f"Filled {filled_count} missing dates")

        if message_parts:
            message = "Successfully completed exchange rate update:\n• " + "\n• ".join(message_parts)
            QMessageBox.information(self, "Update Complete", message)

            # Mark exchange rates as changed to trigger reload if tab is active
            self._mark_exchange_rates_changed()
            # If exchange rates tab is currently active, reload the data
            current_tab_index = self.tabWidget.currentIndex()
            if current_tab_index == 4:  # Exchange Rates tab
                self.load_exchange_rates_table()
        else:
            QMessageBox.information(
                self,
                "Update Complete",
                "Exchange rates are already up to date.",
            )

    def _populate_form_from_description(self, description: str) -> None:
        """Populate form fields based on description from database."""
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # Get the most recent transaction with this description
            query = """
                SELECT t.amount, cat.name, c.code, t.tag
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                JOIN currencies c ON t._id_currencies = c._id
                WHERE t.description = :description
                ORDER BY t.date DESC, t._id DESC
                LIMIT 1
            """

            rows = self.db_manager.get_rows(query, {"description": description})

            if rows:
                amount_cents, category_name, currency_code, tag = rows[0]

                # Populate form fields
                amount = float(amount_cents) / 100  # Convert from cents
                self.doubleSpinBox_amount.setValue(amount)
                self.lineEdit_tag.setText(tag or "")

                # Set category if found
                if category_name:
                    # Find the category in the list view
                    model = self.listView_categories.model()
                    if model:
                        for row in range(model.rowCount()):
                            index = model.index(row, 0)
                            item_data = model.data(index, Qt.ItemDataRole.UserRole)
                            if item_data == category_name:
                                self.listView_categories.setCurrentIndex(index)
                                break

                # Set currency if found
                if currency_code:
                    index = self.comboBox_currency.findText(currency_code)
                    if index >= 0:
                        self.comboBox_currency.setCurrentIndex(index)

        except Exception as e:
            print(f"Error populating form from description: {e}")

    def _restore_table_column_widths(self, table_view: QTableView, column_widths: list[int]) -> None:
        """Restore column widths for a table view.

        Args:
            table_view: The table view to restore column widths for.
            column_widths: List of column widths to restore.

        """
        header = table_view.horizontalHeader()
        if column_widths and header.count() == len(column_widths):
            for i, width in enumerate(column_widths):
                table_view.setColumnWidth(i, width)

    def _save_table_column_widths(self, table_view: QTableView) -> list[int]:
        """Save column widths for a table view.

        Args:
            table_view: The table view to save column widths for.

        Returns:
            List of column widths.

        """
        header = table_view.horizontalHeader()
        column_widths = []
        for i in range(header.count()):
            column_widths.append(table_view.columnWidth(i))
        return column_widths

    def _select_category_by_id(self, category_id: int) -> None:
        """Select category in listView_categories by database ID.

        Args:

        - `category_id` (`int`): Database ID of the category to select.

        """
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # Get category name by ID using get_id method
            query = "SELECT name FROM categories WHERE _id = :category_id"
            rows = self.db_manager.get_rows(query, {"category_id": category_id})
            if not rows:
                print(f"Category with ID {category_id} not found")
                return

            category_name = rows[0][0]

            # Find the category in the list view
            model = self.listView_categories.model()
            if model:
                for row in range(model.rowCount()):
                    index = model.index(row, 0)
                    item_data = model.data(index, Qt.ItemDataRole.UserRole)
                    if item_data == category_name:
                        self.listView_categories.setCurrentIndex(index)
                        # Update the category label
                        display_text = model.data(index, Qt.ItemDataRole.DisplayRole)
                        if display_text:
                            self.label_category_now.setText(display_text)
                        break

        except Exception as e:
            print(f"Error selecting category by ID: {e}")

    def _set_exchange_rates_date_range(self) -> None:
        """Set the date range for exchange rates chart."""
        if not self._validate_database_connection():
            return

        try:
            # Get earliest transaction date for start date
            earliest_date = self.db_manager.get_earliest_transaction_date()
            if earliest_date:
                start_date = QDate.fromString(earliest_date, "yyyy-MM-dd")
                self.dateEdit_exchange_rates_from.setDate(start_date)
            else:
                # Fallback to 1 year ago
                start_date = QDate.currentDate().addYears(-1)
                self.dateEdit_exchange_rates_from.setDate(start_date)

            # Set end date to current date
            self.dateEdit_exchange_rates_to.setDate(QDate.currentDate())

        except Exception as e:
            print(f"Error setting exchange rates date range: {e}")

    def _setup_autocomplete(self) -> None:
        """Setup autocomplete functionality for description input."""
        # Create completer
        self.description_completer = QCompleter(self)
        self.description_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.description_completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Search by content
        self.description_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        # Create model for completer
        self.description_completer_model = QStringListModel(self)
        self.description_completer.setModel(self.description_completer_model)

        # Set completer to the line edit
        self.lineEdit_description.setCompleter(self.description_completer)

        # Update autocomplete data
        self._update_autocomplete_data()

        # Connect selection signal
        self.description_completer.activated.connect(self._on_autocomplete_selected)

    def _setup_exchange_rates_controls(self) -> None:
        """Setup exchange rates chart controls with initial values."""
        if not self._validate_database_connection():
            return

        try:
            # Block signals temporarily to prevent chart drawing during setup
            self.dateEdit_exchange_rates_from.blockSignals(True)
            self.dateEdit_exchange_rates_to.blockSignals(True)

            # Fill currency combo box
            currencies = self.db_manager.get_all_currencies()
            self.comboBox_exchange_rates_currency.clear()

            # Add currencies with format: "RUB - Russian Ruble"
            for currency in currencies:
                currency_id, code, name, symbol = currency
                display_text = f"{code} - {name}"
                self.comboBox_exchange_rates_currency.addItem(display_text, currency_id)

            # Set default currency (ID = 1)
            default_index = self.comboBox_exchange_rates_currency.findData(1)
            if default_index >= 0:
                self.comboBox_exchange_rates_currency.setCurrentIndex(default_index)

            # Set date range
            self._set_exchange_rates_date_range()

            # Mark that initial setup is complete
            self._exchange_rates_initialized = True

            # Unblock signals after setup is complete
            self.dateEdit_exchange_rates_from.blockSignals(False)
            self.dateEdit_exchange_rates_to.blockSignals(False)

            # Draw initial chart
            self.on_exchange_rates_update()

        except Exception as e:
            print(f"Error setting up exchange rates controls: {e}")
            # Ensure signals are unblocked even if there's an error
            self.dateEdit_exchange_rates_from.blockSignals(False)
            self.dateEdit_exchange_rates_to.blockSignals(False)

    def _setup_tab_order(self) -> None:
        """Setup tab order for widgets in groupBox_transaction."""
        from PySide6.QtWidgets import QWidget

        # Set tab order for widgets in groupBox_transaction
        # Make pushButton_description_clear the last in tab order
        QWidget.setTabOrder(self.lineEdit_description, self.doubleSpinBox_amount)
        QWidget.setTabOrder(self.doubleSpinBox_amount, self.comboBox_currency)
        QWidget.setTabOrder(self.comboBox_currency, self.dateEdit)
        QWidget.setTabOrder(self.dateEdit, self.pushButton_yesterday)
        QWidget.setTabOrder(self.pushButton_yesterday, self.pushButton_add)
        QWidget.setTabOrder(self.pushButton_add, self.lineEdit_tag)
        QWidget.setTabOrder(self.lineEdit_tag, self.listView_categories)
        QWidget.setTabOrder(self.listView_categories, self.pushButton_delete)
        QWidget.setTabOrder(self.pushButton_delete, self.pushButton_show_all_records)
        QWidget.setTabOrder(self.pushButton_show_all_records, self.pushButton_refresh)
        QWidget.setTabOrder(self.pushButton_refresh, self.pushButton_clear_filter)
        QWidget.setTabOrder(self.pushButton_clear_filter, self.pushButton_apply_filter)
        QWidget.setTabOrder(self.pushButton_apply_filter, self.pushButton_description_clear)

    def _setup_ui(self) -> None:
        """Set up additional UI elements."""
        # Set emoji for buttons
        self.pushButton_yesterday.setText(f"📅 {self.pushButton_yesterday.text()}")
        self.pushButton_add.setText(f"➕ {self.pushButton_add.text()}")
        self.pushButton_delete.setText(f"🗑️ {self.pushButton_delete.text()}")
        self.pushButton_refresh.setText(f"🔄 {self.pushButton_refresh.text()}")
        self.pushButton_clear_filter.setText(f"🧹 {self.pushButton_clear_filter.text()}")
        self.pushButton_apply_filter.setText(f"✔️ {self.pushButton_apply_filter.text()}")
        self.pushButton_description_clear.setText("🧹")
        self.pushButton_show_all_records.setText("📊 Show All Records")

        # Configure splitter proportions
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 3)

        # Set default values
        self.doubleSpinBox_amount.setValue(100.0)
        self.doubleSpinBox_exchange_from.setValue(100.0)
        self.doubleSpinBox_exchange_to.setValue(73.5)
        self.doubleSpinBox_exchange_rate.setValue(73.5)
        self.spinBox_subdivision.setValue(100)

    def _setup_window_size_and_position(self) -> None:
        """Set window size and position based on screen resolution and characteristics."""
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Determine window size and position based on screen characteristics
        aspect_ratio = screen_width / screen_height
        is_standard_aspect = aspect_ratio <= 2.0  # Standard aspect ratio (16:9, 16:10, etc.)

        if is_standard_aspect and screen_width >= 1920:
            # For standard aspect ratios with width >= 1920, maximize window
            self.showMaximized()
        else:
            title_bar_height = 30  # Approximate title bar height
            windows_task_bar_height = 48  # Approximate windows task bar height
            # For other cases, use fixed width and full height minus title bar
            window_width = 1920
            window_height = screen_height - title_bar_height - windows_task_bar_height
            # Position window on screen
            screen_center = screen_geometry.center()
            # Center horizontally, position at top vertically with title bar offset
            self.setGeometry(
                screen_center.x() - window_width // 2,
                title_bar_height,  # Position below title bar
                window_width,
                window_height,
            )

    def _show_no_data_label(self, layout, message: str) -> None:
        """Show a message when no data is available for the chart."""
        from PySide6.QtWidgets import QLabel

        # Clear existing content
        self._clear_layout(layout)

        # Create and add label
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #666; padding: 20px;")
        layout.addWidget(label)

    def _show_transactions_context_menu(self, position) -> None:
        """Show context menu for transactions table.

        Args:

        - `position`: Position where context menu should appear.

        """
        from PySide6.QtWidgets import QMenu

        context_menu = QMenu(self)
        export_action = context_menu.addAction("Export to CSV")

        action = context_menu.exec(self.tableView_transactions.mapToGlobal(position))

        if action == export_action:
            self.on_export_csv()

    def _transform_transaction_data(self, rows: list[list[Any]]) -> list[list[Any]]:
        """Transform transaction data for display with colors and daily totals.

        Args:

        - `rows` (`list[list[Any]]`): Raw transaction data.

        Returns:

        - `list[list[Any]]`: Transformed data with colors and daily totals.

        """
        transformed_data = []

        # Calculate daily expenses
        daily_expenses = self._calculate_daily_expenses(rows)

        # Create a mapping of dates to color indices
        date_to_color_index = {}
        color_index = 0

        # Track which dates we've already shown totals for
        dates_with_totals = set()

        for row in rows:
            # Raw data: [id, amount_cents, description, category_name, currency_code, date, tag, category_type, icon, symbol]
            transaction_id = row[0]
            amount_cents = row[1]
            description = row[2]
            category_name = row[3]
            currency_code = row[4]
            date = row[5]
            tag = row[6]
            category_type = row[7]

            # Convert amount from minor units to display format using currency subdivision
            if self.db_manager:
                amount = self.db_manager.convert_from_minor_units(
                    amount_cents,
                    self.db_manager.get_currency_by_code(currency_code)[0]
                    if self.db_manager.get_currency_by_code(currency_code)
                    else 1,
                )
            else:
                amount = float(amount_cents) / 100  # Fallback

            # Determine color based on date
            if date not in date_to_color_index:
                date_to_color_index[date] = color_index % len(self.date_colors)
                color_index += 1

            color = self.date_colors[date_to_color_index[date]]

            # Add "(Income)" suffix for income categories
            display_category_name = category_name
            if category_type == 1:  # Income category
                display_category_name = f"{category_name} (Income)"

            # Determine if this is the first transaction for this date
            is_first_of_day = date not in dates_with_totals
            if is_first_of_day:
                dates_with_totals.add(date)

            # Get daily total for this date
            daily_total = daily_expenses.get(date, 0.0)
            total_display = f"-{daily_total:.2f}" if is_first_of_day and daily_total > 0 else ""

            # Format amount with minus sign for expenses
            amount_display = f"-{amount:.2f}" if category_type == 0 else f"{amount:.2f}"

            # Transform to display format: [description, amount, category, currency, date, tag, total_per_day, id, color]
            transformed_row = [
                description,
                amount_display,
                display_category_name,
                currency_code,
                date,
                tag,
                total_display,
                transaction_id,
                color,
            ]
            transformed_data.append(transformed_row)

        return transformed_data

    def _update_autocomplete_data(self) -> None:
        """Update autocomplete data from database."""
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # Get recent transaction descriptions for autocomplete
            recent_descriptions = self.db_manager.get_recent_transaction_descriptions_for_autocomplete(1000)

            # Update completer model
            self.description_completer_model.setStringList(recent_descriptions)

        except Exception as e:
            print(f"Error updating autocomplete data: {e}")

    @requires_database()
    def _update_comboboxes(self) -> None:
        """Update all comboboxes with current data."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update currency comboboxes
            currencies = [row[1] for row in self.db_manager.get_all_currencies()]  # Get codes

            for combo in [
                self.comboBox_currency,
                self.comboBox_account_currency,
                self.comboBox_exchange_from,
                self.comboBox_exchange_to,
                self.comboBox_default_currency,
            ]:
                combo.clear()
                combo.addItems(currencies)

            # Update categories list view with icons
            expense_categories = self.db_manager.get_categories_with_icons_by_type(0)
            income_categories = self.db_manager.get_categories_with_icons_by_type(1)

            model = QStandardItemModel()

            # Add expense categories first
            for category_name, icon in expense_categories:
                # Create display text with icon
                display_text = f"{icon} {category_name}" if icon else category_name
                item = QStandardItem(display_text)
                # Store the original category name as data for selection handling
                item.setData(category_name, Qt.ItemDataRole.UserRole)
                model.appendRow(item)

            # Add income categories with special marking
            for category_name, icon in income_categories:
                # Create display text with icon and income marker
                base_text = f"{icon} {category_name}" if icon else category_name
                display_text = f"{base_text} (Income)"  # Add income marker in parentheses
                item = QStandardItem(display_text)
                # Store the original category name as data for selection handling
                item.setData(category_name, Qt.ItemDataRole.UserRole)
                model.appendRow(item)

            self.listView_categories.setModel(model)

            # Connect category selection signal after model is set
            self.listView_categories.selectionModel().currentChanged.connect(self.on_category_selection_changed)

            # Reset category selection label
            self.label_category_now.setText("No category selected")

            # Set default currency selection
            default_currency = self.db_manager.get_default_currency()
            for combo in [
                self.comboBox_currency,
                self.comboBox_account_currency,
                self.comboBox_exchange_from,
                self.comboBox_default_currency,
            ]:
                index = combo.findText(default_currency)
                if index >= 0:
                    combo.setCurrentIndex(index)

            # Set exchange_to currency based on logic
            # If current currency is not USD, set USD as exchange_to, otherwise set currency with _id = 1
            if default_currency != "USD":
                # Set USD as exchange_to
                usd_index = self.comboBox_exchange_to.findText("USD")
                if usd_index >= 0:
                    self.comboBox_exchange_to.setCurrentIndex(usd_index)
            else:
                # Current currency is USD, set currency with _id = 1 as exchange_to
                currency_info = self.db_manager.get_currency_by_id(1)
                if currency_info:
                    currency_code = currency_info[0]  # Get code from (code, name, symbol)
                    currency_index = self.comboBox_exchange_to.findText(currency_code)
                    if currency_index >= 0:
                        self.comboBox_exchange_to.setCurrentIndex(currency_index)

        except Exception as e:
            print(f"Error updating comboboxes: {e}")

    def _validate_database_connection(self) -> bool:
        """Validate database connection.

        Returns:

        - `bool`: True if connection is valid, False otherwise.

        """
        if not self.db_manager:
            print("Database manager is None")
            return False

        if not self.db_manager.is_database_open():
            print("Database connection is not open")
            return False

        return True
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:  # noqa: D107  (inherited from Qt widgets)
        super().__init__()
        self.setupUi(self)
        self._setup_ui()

        # Set window icon
        self.setWindowIcon(QIcon(":/assets/logo.svg"))

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Initialize core attributes
        self.db_manager: database_manager.DatabaseManager | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "transactions": None,
            "categories": None,
            "accounts": None,
            "currencies": None,
            "currency_exchanges": None,
            "exchange_rates": None,
        }

        # Chart configuration
        self.max_count_points_in_charts = 40

        # Generate pastel colors for date-based coloring
        self.date_colors = self.generate_pastel_colors_mathematical(50)

        # Toggle for showing all records vs last self.count_transactions_to_show
        self.count_transactions_to_show = 1000
        self.count_exchange_rates_to_show = 1000
        self.show_all_transactions = False

        # Lazy loading flags
        self.exchange_rates_loaded = False

        # Exchange rates initialization flag
        self._exchange_rates_initialized = False

        # Table configuration mapping
        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "transactions": (
                self.tableView_transactions,
                "transactions",
                ["Description", "Amount", "Category", "Currency", "Date", "Tag", "Total per day"],
            ),
            "categories": (
                self.tableView_categories,
                "categories",
                ["Name", "Type", "Icon"],
            ),
            "accounts": (
                self.tableView_accounts,
                "accounts",
                ["Name", "Balance", "Currency", "Liquid", "Cash"],
            ),
            "currencies": (
                self.tableView_currencies,
                "currencies",
                ["Code", "Name", "Symbol"],
            ),
            "currency_exchanges": (
                self.tableView_exchange,
                "currency_exchanges",
                ["From", "To", "Amount From", "Amount To", "Rate", "Fee", "Date", "Description"],
            ),
            "exchange_rates": (
                self.tableView_exchange_rates,
                "exchange_rates",
                ["From", "To", "Rate", "Date"],
            ),
        }

        # Initialize application
        self._init_database()
        self._connect_signals()
        self._init_filter_controls()
        self._init_chart_controls()
        self._setup_autocomplete()
        self._initial_load()

        # Set window size and position
        self._setup_window_size_and_position()

        # Setup tab order
        self._setup_tab_order()

        # Show window after initialization
        QTimer.singleShot(200, self._finish_window_initialization)
```

</details>

### ⚙️ Method `apply_filter`

```python
def apply_filter(self) -> None
```

Apply combo-box/date filters to the transactions table.

<details>
<summary>Code:</summary>

```python
def apply_filter(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get filter values
        transaction_type = None
        if self.radioButton_2.isChecked():  # Expense
            transaction_type = 0
        elif self.radioButton_3.isChecked():  # Income
            transaction_type = 1
        # If radioButton (All) is checked, transaction_type remains None

        category = self.comboBox_filter_category.currentText() if self.comboBox_filter_category.currentText() else None
        currency = self.comboBox_filter_currency.currentText() if self.comboBox_filter_currency.currentText() else None

        use_date_filter = self.checkBox_use_date_filter.isChecked()
        date_from = self.dateEdit_filter_from.date().toString("yyyy-MM-dd") if use_date_filter else None
        date_to = self.dateEdit_filter_to.date().toString("yyyy-MM-dd") if use_date_filter else None

        # Use database manager method
        rows = self.db_manager.get_filtered_transactions(
            category_type=transaction_type,
            category_name=category,
            currency_code=currency,
            date_from=date_from,
            date_to=date_to,
        )

        # Transform data for display
        transformed_data = self._transform_transaction_data(rows)

        # Create model and set to table
        self.models["transactions"] = self._create_transactions_table_model(
            transformed_data, self.table_config["transactions"][2]
        )
        self.tableView_transactions.setModel(self.models["transactions"])

        # Column stretching setup (like in show_tables)
        self.tableView_transactions.resizeColumnsToContents()

        # Table header behavior setup for column stretching
        header = self.tableView_transactions.horizontalHeader()
        if header.count() > 0:
            # Set stretch mode for all columns except the last two
            for i in range(header.count() - 2):
                header.setSectionResizeMode(i, header.ResizeMode.Stretch)

            # For the second-to-last column (Tag) set fixed width
            second_last_column = header.count() - 2
            header.setSectionResizeMode(second_last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(second_last_column, 100)

            # For the last column (Total per day) set fixed width
            last_column = header.count() - 1
            header.setSectionResizeMode(last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(last_column, 120)

        # Reconnect auto-save signals for the updated table
        self._connect_table_auto_save_signals()
```

</details>

### ⚙️ Method `clear_filter`

```python
def clear_filter(self) -> None
```

Reset all transaction filters.

<details>
<summary>Code:</summary>

```python
def clear_filter(self) -> None:
        self.radioButton.setChecked(True)  # All
        self.comboBox_filter_category.setCurrentIndex(0)
        self.comboBox_filter_currency.setCurrentIndex(0)
        self.checkBox_use_date_filter.setChecked(False)

        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        # Load transactions table instead of all tables
        self._load_transactions_table()
        # Reconnect auto-save signals for the updated table
        self._connect_table_auto_save_signals()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Handle application close event.

Args:

- `event` (`QCloseEvent`): The close event.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        # Stop any running worker threads
        if hasattr(self, "exchange_rate_worker") and self.exchange_rate_worker.isRunning():
            self.exchange_rate_worker.stop()
            self.exchange_rate_worker.wait(3000)  # Wait up to 3 seconds

        # Close progress dialog if open
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        # Dispose Models
        self._dispose_models()

        # Close DB
        if self.db_manager:
            self.db_manager.close()
            self.db_manager = None

        super().closeEvent(event)
```

</details>

### ⚙️ Method `delete_record`

```python
def delete_record(self, table_name: str) -> None
```

Delete selected row from table using database manager methods.

Args:

- `table_name` (`str`): Name of the table to delete from. Must be in \_SAFE_TABLES.

Raises:

- `ValueError`: If table_name is not in \_SAFE_TABLES.

<details>
<summary>Code:</summary>

```python
def delete_record(self, table_name: str) -> None:
        if table_name not in self._SAFE_TABLES:
            error_message = f"Illegal table name: {table_name}"
            raise ValueError(error_message)

        record_id = self._get_selected_row_id(table_name)
        if record_id is None:
            QMessageBox.warning(self, "Error", "Select a record to delete")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Use appropriate database manager method
        success = False
        try:
            if table_name == "transactions":
                success = self.db_manager.delete_transaction(record_id)
                if success:
                    self._mark_transactions_changed()
            elif table_name == "categories":
                success = self.db_manager.delete_category(record_id)
                if success:
                    self._mark_categories_changed()
            elif table_name == "accounts":
                success = self.db_manager.delete_account(record_id)
            elif table_name == "currencies":
                success = self.db_manager.delete_currency(record_id)
                if success:
                    self._mark_currencies_changed()
            elif table_name == "currency_exchanges":
                success = self.db_manager.delete_currency_exchange(record_id)
            elif table_name == "exchange_rates":
                success = self.db_manager.delete_exchange_rate(record_id)
                if success:
                    self._mark_exchange_rates_changed()
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            # Save current column widths before update for exchange table
            column_widths = None
            if table_name == "currency_exchanges":
                column_widths = self._save_table_column_widths(self.tableView_exchange)

            self.update_all()

            # Restore column widths after update for exchange table
            if table_name == "currency_exchanges" and column_widths:
                self._restore_table_column_widths(self.tableView_exchange, column_widths)

            self.update_summary_labels()
        else:
            QMessageBox.warning(self, "Error", f"Deletion failed in {table_name}")
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, obj, event) -> bool
```

Event filter for handling Enter key in doubleSpinBox_amount.

Args:

- `obj`: The object that generated the event.
- `event`: The event that occurred.

Returns:

- `bool`: True if event was handled, False otherwise.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, obj, event) -> bool:
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QKeyEvent

        if (
            (obj == self.doubleSpinBox_amount and event.type() == QEvent.Type.KeyPress)
            or (obj == self.dateEdit and event.type() == QEvent.Type.KeyPress)
            or (obj == self.lineEdit_tag and event.type() == QEvent.Type.KeyPress)
            or (obj == self.pushButton_add and event.type() == QEvent.Type.KeyPress)
        ):
            key_event = QKeyEvent(event)
            if key_event.key() == Qt.Key.Key_Return or key_event.key() == Qt.Key.Key_Enter:
                self.on_add_transaction()
                return True
        return super().eventFilter(obj, event)
```

</details>

### ⚙️ Method `generate_pastel_colors_mathematical`

```python
def generate_pastel_colors_mathematical(self, count: int = 100) -> list[QColor]
```

Generate pastel colors using mathematical distribution.

Args:

- `count` (`int`): Number of colors to generate. Defaults to `100`.

Returns:

- `list[QColor]`: List of pastel QColor objects.

<details>
<summary>Code:</summary>

```python
def generate_pastel_colors_mathematical(self, count: int = 100) -> list[QColor]:
        colors = []

        for i in range(count):
            # Use golden ratio for even hue distribution
            hue = (i * 0.618033988749895) % 1.0  # Golden ratio

            # Lower saturation and higher lightness for very light pastel effect
            saturation = 0.6  # Very low saturation
            lightness = 0.95  # Very high lightness

            # Convert HSL to RGB
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

            # Convert to 0-255 range and create QColor
            color = QColor(int(r * 255), int(g * 255), int(b * 255))
            colors.append(color)

        return colors
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Handle key press events for the main window.

Args:

- `event` (`QKeyEvent`): The key press event.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        # Handle Ctrl+C for copying table selections
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Determine which table is currently focused
            focused_widget = QApplication.focusWidget()

            # Check if the focused widget is one of our table views
            table_views = [
                self.tableView_transactions,
                self.tableView_categories,
                self.tableView_accounts,
                self.tableView_currencies,
                self.tableView_exchange,
                self.tableView_exchange_rates,
                self.tableView_reports,
            ]

            for table_view in table_views:
                if focused_widget == table_view:
                    self._copy_table_selection_to_clipboard(table_view)
                    return

            # If focused widget is a child of a table view
            for table_view in table_views:
                if focused_widget and table_view.isAncestorOf(focused_widget):
                    self._copy_table_selection_to_clipboard(table_view)
                    return

        # Call parent implementation for other key events
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `load_exchange_rates_table`

```python
def load_exchange_rates_table(self) -> None
```

Load exchange rates table data (lazy loading).

<details>
<summary>Code:</summary>

```python
def load_exchange_rates_table(self) -> None:
        if not self._validate_database_connection():
            print("Database connection not available for loading exchange rates")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Refresh exchange rates table - get only the latest records sorted by date
            rates_data = self.db_manager.get_all_exchange_rates(limit=self.count_exchange_rates_to_show)
            rates_transformed_data = []
            for row in rates_data:
                # Transform: [id, from_code, to_code, rate, date]
                # Rate is stored as USD→currency, but display as currency→USD
                usd_to_currency_rate = float(row[3]) if row[3] else 0.0
                currency_to_usd_rate = 1.0 / usd_to_currency_rate if usd_to_currency_rate != 0 else 0.0
                color = QColor(240, 255, 255)
                # Show as currency → USD instead of USD → currency
                transformed_row = [row[2], row[1], f"{currency_to_usd_rate:.6f}", row[4], row[0], color]
                rates_transformed_data.append(transformed_row)

            self.models["exchange_rates"] = self._create_colored_table_model(
                rates_transformed_data, self.table_config["exchange_rates"][2]
            )
            self.tableView_exchange_rates.setModel(self.models["exchange_rates"])

            # Configure column stretching for exchange rates table
            rates_header = self.tableView_exchange_rates.horizontalHeader()
            if rates_header.count() > 0:
                for i in range(rates_header.count()):
                    rates_header.setSectionResizeMode(i, rates_header.ResizeMode.Stretch)

            # Mark as loaded
            self.exchange_rates_loaded = True

        except Exception as e:
            print(f"❌ Error loading exchange rates table: {e}")
```

</details>

### ⚙️ Method `on_add_account`

```python
def on_add_account(self) -> None
```

Add a new account using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_account(self) -> None:
        name = self.lineEdit_account_name.text().strip()
        balance = self.doubleSpinBox_account_balance.value()
        currency_code = self.comboBox_account_currency.currentText()
        is_liquid = self.checkBox_is_liquid.isChecked()
        is_cash = self.checkBox_is_cash.isChecked()

        if not name:
            QMessageBox.warning(self, "Error", "Enter account name")
            return

        if not currency_code:
            QMessageBox.warning(self, "Error", "Select a currency")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get currency ID
        currency_info = self.db_manager.get_currency_by_code(currency_code)
        if not currency_info:
            QMessageBox.warning(self, "Error", f"Currency '{currency_code}' not found")
            return

        currency_id = currency_info[0]

        try:
            if self.db_manager.add_account(name, balance, currency_id, is_liquid=is_liquid, is_cash=is_cash):
                self.update_all()
                self._clear_account_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add account")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add account: {e}")
```

</details>

### ⚙️ Method `on_add_category`

```python
def on_add_category(self) -> None
```

Add a new category using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_category(self) -> None:
        name = self.lineEdit_category_name.text().strip()
        category_type = self.comboBox_category_type.currentIndex()  # 0 = Expense, 1 = Income

        if not name:
            QMessageBox.warning(self, "Error", "Enter category name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.add_category(name, category_type):
                self._mark_categories_changed()
                self.update_all()
                self._clear_category_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add category")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add category: {e}")
```

</details>

### ⚙️ Method `on_add_currency`

```python
def on_add_currency(self) -> None
```

Add a new currency using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_currency(self) -> None:
        code = self.lineEdit_currency_code.text().strip().upper()
        name = self.lineEdit_currency_name.text().strip()
        symbol = self.lineEdit_currency_symbol.text().strip()
        subdivision = self.spinBox_subdivision.value()

        if not code:
            QMessageBox.warning(self, "Error", "Enter currency code")
            return

        if not name:
            QMessageBox.warning(self, "Error", "Enter currency name")
            return

        if not symbol:
            QMessageBox.warning(self, "Error", "Enter currency symbol")
            return

        if subdivision <= 0:
            QMessageBox.warning(self, "Error", "Subdivision must be a positive number")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.add_currency(code, name, symbol, subdivision):
                self._mark_currencies_changed()
                self.update_all()
                self._clear_currency_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add currency")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add currency: {e}")
```

</details>

### ⚙️ Method `on_add_exchange`

```python
def on_add_exchange(self) -> None
```

Add a new currency exchange using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_exchange(self) -> None:
        from_currency = self.comboBox_exchange_from.currentText()
        to_currency = self.comboBox_exchange_to.currentText()
        amount_from = self.doubleSpinBox_exchange_from.value()
        amount_to = self.doubleSpinBox_exchange_to.value()
        exchange_rate = self.doubleSpinBox_exchange_rate.value()
        fee = self.doubleSpinBox_exchange_fee.value()
        date = self.dateEdit_exchange.date().toString("yyyy-MM-dd")
        description = self.lineEdit_exchange_description.text().strip()

        if not from_currency or not to_currency:
            QMessageBox.warning(self, "Error", "Select both currencies")
            return

        if from_currency == to_currency:
            QMessageBox.warning(self, "Error", "From and To currencies must be different")
            return

        if amount_from <= 0 or amount_to <= 0:
            QMessageBox.warning(self, "Error", "Amounts must be positive")
            return

        if exchange_rate <= 0:
            QMessageBox.warning(self, "Error", "Exchange rate must be positive")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get currency IDs
        from_currency_info = self.db_manager.get_currency_by_code(from_currency)
        to_currency_info = self.db_manager.get_currency_by_code(to_currency)

        if not from_currency_info or not to_currency_info:
            QMessageBox.warning(self, "Error", "Currency not found")
            return

        from_currency_id = from_currency_info[0]
        to_currency_id = to_currency_info[0]

        try:
            if self.db_manager.add_currency_exchange(
                from_currency_id, to_currency_id, amount_from, amount_to, exchange_rate, fee, date, description
            ):
                # Save current column widths before update
                column_widths = self._save_table_column_widths(self.tableView_exchange)

                self.update_all()

                # Restore column widths after update
                self._restore_table_column_widths(self.tableView_exchange, column_widths)

                self._clear_exchange_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add currency exchange")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add currency exchange: {e}")
```

</details>

### ⚙️ Method `on_add_transaction`

```python
def on_add_transaction(self) -> None
```

Add a new transaction using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_transaction(self) -> None:
        amount = self.doubleSpinBox_amount.value()
        description = self.lineEdit_description.text().strip()
        category_name = (
            self.listView_categories.currentIndex().data(Qt.ItemDataRole.UserRole)
            if self.listView_categories.currentIndex().isValid()
            else None
        )
        currency_code = self.comboBox_currency.currentText()
        date = self.dateEdit.date().toString("yyyy-MM-dd")
        tag = self.lineEdit_tag.text().strip()

        if amount <= 0:
            QMessageBox.warning(self, "Error", "Amount must be positive")
            return

        if not description:
            QMessageBox.warning(self, "Error", "Enter description")
            return

        if not category_name:
            QMessageBox.warning(self, "Error", "Select a category")
            return

        if not currency_code:
            QMessageBox.warning(self, "Error", "Select a currency")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get category ID
        cat_id = self.db_manager.get_id("categories", "name", category_name)
        if cat_id is None:
            QMessageBox.warning(self, "Error", f"Category '{category_name}' not found")
            return

        # Get currency ID
        currency_info = self.db_manager.get_currency_by_code(currency_code)
        if not currency_info:
            QMessageBox.warning(self, "Error", f"Currency '{currency_code}' not found")
            return

        currency_id = currency_info[0]

        try:
            if self.db_manager.add_transaction(amount, description, cat_id, currency_id, date, tag):
                # Save current date before updating UI
                current_date = self.dateEdit.date()

                # Mark transactions changed for lazy loading
                self._mark_transactions_changed()

                # Update UI
                self.update_all()
                self.update_summary_labels()

                # Update autocomplete data with new transaction
                self._update_autocomplete_data()

                # Clear form except date
                self.doubleSpinBox_amount.setValue(100.0)
                self.lineEdit_description.clear()
                self.lineEdit_tag.clear()

                # Restore the original date
                self.dateEdit.setDate(current_date)

                # Set focus to description field and select all text after a short delay
                # This ensures UI updates are complete before focusing
                QTimer.singleShot(100, self._focus_description_and_select_text)

                # Select the category of the just added transaction
                self._select_category_by_id(cat_id)
            else:
                QMessageBox.warning(self, "Error", "Failed to add transaction")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add transaction: {e}")
```

</details>

### ⚙️ Method `on_calculate_exchange`

```python
def on_calculate_exchange(self) -> None
```

Calculate exchange amount based on rate.

<details>
<summary>Code:</summary>

```python
def on_calculate_exchange(self) -> None:
        amount_from = self.doubleSpinBox_exchange_from.value()
        rate = self.doubleSpinBox_exchange_rate.value()

        if rate > 0:
            amount_to = amount_from * rate
            self.doubleSpinBox_exchange_to.setValue(amount_to)
```

</details>

### ⚙️ Method `on_category_selection_changed`

```python
def on_category_selection_changed(self, current: QModelIndex, previous: QModelIndex) -> None
```

Handle category selection change in listView_categories.

Args:

- `current` (`QModelIndex`): Current selected index.
- `previous` (`QModelIndex`): Previously selected index.

<details>
<summary>Code:</summary>

```python
def on_category_selection_changed(self, current: QModelIndex, previous: QModelIndex) -> None:
        if current.isValid():
            # Get the display text (with icon and income marker if applicable)
            display_text = current.data(Qt.ItemDataRole.DisplayRole)
            if display_text:
                self.label_category_now.setText(display_text)
            else:
                self.label_category_now.setText("No category selected")

            # Move focus to description field and select all text
            QTimer.singleShot(100, self._focus_description_and_select_text)
        else:
            self.label_category_now.setText("No category selected")
```

</details>

### ⚙️ Method `on_clear_description`

```python
def on_clear_description(self) -> None
```

Clear the description field.

<details>
<summary>Code:</summary>

```python
def on_clear_description(self) -> None:
        self.lineEdit_description.clear()
```

</details>

### ⚙️ Method `on_exchange_rates_all_time`

```python
def on_exchange_rates_all_time(self) -> None
```

Set date range to all available data.

<details>
<summary>Code:</summary>

```python
def on_exchange_rates_all_time(self) -> None:
        self._set_exchange_rates_date_range()
        # Automatically update the chart
        self.on_exchange_rates_update()
```

</details>

### ⚙️ Method `on_exchange_rates_currency_changed`

```python
def on_exchange_rates_currency_changed(self) -> None
```

Handle currency selection change in exchange rates tab.

<details>
<summary>Code:</summary>

```python
def on_exchange_rates_currency_changed(self) -> None:
        # Update chart if dates are set
        if self.dateEdit_exchange_rates_from.date().isValid() and self.dateEdit_exchange_rates_to.date().isValid():
            self.on_exchange_rates_update()
```

</details>

### ⚙️ Method `on_exchange_rates_last_month`

```python
def on_exchange_rates_last_month(self) -> None
```

Set date range to last month.

<details>
<summary>Code:</summary>

```python
def on_exchange_rates_last_month(self) -> None:
        current_date = QDate.currentDate()
        last_month = current_date.addMonths(-1)
        self.dateEdit_exchange_rates_from.setDate(last_month)
        self.dateEdit_exchange_rates_to.setDate(current_date)
        # Automatically update the chart
        self.on_exchange_rates_update()
```

</details>

### ⚙️ Method `on_exchange_rates_last_year`

```python
def on_exchange_rates_last_year(self) -> None
```

Set date range to last year.

<details>
<summary>Code:</summary>

```python
def on_exchange_rates_last_year(self) -> None:
        current_date = QDate.currentDate()
        last_year = current_date.addYears(-1)
        self.dateEdit_exchange_rates_from.setDate(last_year)
        self.dateEdit_exchange_rates_to.setDate(current_date)
        # Automatically update the chart
        self.on_exchange_rates_update()
```

</details>

### ⚙️ Method `on_exchange_rates_update`

```python
def on_exchange_rates_update(self) -> None
```

Update the exchange rate chart.

<details>
<summary>Code:</summary>

```python
def on_exchange_rates_update(self) -> None:
        # Check if exchange rates controls have been initialized
        if not hasattr(self, "_exchange_rates_initialized") or not self._exchange_rates_initialized:
            return

        # Get selected currency
        current_index = self.comboBox_exchange_rates_currency.currentIndex()
        if current_index < 0:
            return

        currency_id = self.comboBox_exchange_rates_currency.itemData(current_index)
        if not currency_id:
            return

        # Get date range
        date_from = self.dateEdit_exchange_rates_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_exchange_rates_to.date().toString("yyyy-MM-dd")

        # Validate date range
        if self.dateEdit_exchange_rates_from.date() > self.dateEdit_exchange_rates_to.date():
            QMessageBox.warning(self, "Invalid Date Range", "Start date cannot be after end date.")
            return

        # Create chart
        self._create_exchange_rate_chart(currency_id, date_from, date_to)
```

</details>

### ⚙️ Method `on_export_csv`

```python
def on_export_csv(self) -> None
```

Save current transactions view to a CSV file.

<details>
<summary>Code:</summary>

```python
def on_export_csv(self) -> None:
        filename_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save Table",
            "",
            "CSV (*.csv)",
        )
        if not filename_str:
            return

        try:
            filename = Path(filename_str)
            model = self.models["transactions"].sourceModel()  # type: ignore[call-arg]
            with filename.open("w", encoding="utf-8") as file:
                headers = [
                    model.headerData(col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) or ""
                    for col in range(model.columnCount())
                ]
                file.write(";".join(headers) + "\n")

                for row in range(model.rowCount()):
                    row_values = [f'"{model.data(model.index(row, col)) or ""}"' for col in range(model.columnCount())]
                    file.write(";".join(row_values) + "\n")

        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export CSV: {e}")
```

</details>

### ⚙️ Method `on_generate_report`

```python
def on_generate_report(self) -> None
```

Generate selected report.

<details>
<summary>Code:</summary>

```python
def on_generate_report(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        report_type = self.comboBox_report_type.currentText()
        default_currency_id = self.db_manager.get_default_currency_id()

        try:
            if report_type == "Monthly Summary":
                self._generate_monthly_summary_report(default_currency_id)
            elif report_type == "Category Analysis":
                self._generate_category_analysis_report(default_currency_id)
            elif report_type == "Currency Analysis":
                self._generate_currency_analysis_report()
            elif report_type == "Account Balances":
                self._generate_account_balances_report(default_currency_id)
            elif report_type == "Income vs Expenses":
                self._generate_income_vs_expenses_report(default_currency_id)
        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate report: {e}")
```

</details>

### ⚙️ Method `on_set_default_currency`

```python
def on_set_default_currency(self) -> None
```

Set the default currency.

<details>
<summary>Code:</summary>

```python
def on_set_default_currency(self) -> None:
        currency_code = self.comboBox_default_currency.currentText()

        if not currency_code:
            QMessageBox.warning(self, "Error", "Select a currency")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.set_default_currency(currency_code):
                QMessageBox.information(self, "Success", f"Default currency set to {currency_code}")
                # Mark default currency changed for lazy loading
                self._mark_default_currency_changed()
                # Update all displays to reflect new currency
                self.update_summary_labels()
                self._update_comboboxes()
            else:
                QMessageBox.warning(self, "Error", "Failed to set default currency")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to set default currency: {e}")
```

</details>

### ⚙️ Method `on_show_all_records_clicked`

```python
def on_show_all_records_clicked(self) -> None
```

Toggle between showing all records and last self.count_transactions_to_show records.

<details>
<summary>Code:</summary>

```python
def on_show_all_records_clicked(self) -> None:
        self.show_all_transactions = not self.show_all_transactions

        # Update button text and icon
        if self.show_all_transactions:
            self.pushButton_show_all_records.setText(f"📊 Show Last {self.count_transactions_to_show}")
        else:
            self.pushButton_show_all_records.setText("📊 Show All Records")

        # Refresh the transactions table
        self._load_transactions_table()

        # Reconnect auto-save signals for the updated table
        self._connect_table_auto_save_signals()
```

</details>

### ⚙️ Method `on_tab_changed`

```python
def on_tab_changed(self, index: int) -> None
```

React to tab change.

Args:

- `index` (`int`): The index of the newly selected tab.

<details>
<summary>Code:</summary>

```python
def on_tab_changed(self, index: int) -> None:
        # Update relevant data when switching to different tabs
        if index == 4:  # Exchange Rates tab - lazy loading
            if not self.exchange_rates_loaded:
                self.load_exchange_rates_table()
        elif index == 6:  # Charts tab
            self.update_chart_comboboxes()
        elif index == 7:  # Reports tab
            self.update_summary_labels()
```

</details>

### ⚙️ Method `on_update_exchange_rates`

```python
def on_update_exchange_rates(self) -> None
```

Update exchange rates using a background thread.

<details>
<summary>Code:</summary>

```python
def on_update_exchange_rates(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get the earliest date from transactions
            earliest_transaction_date = self.db_manager.get_earliest_transaction_date()
            if not earliest_transaction_date:
                QMessageBox.warning(
                    self,
                    "No Data",
                    "No transactions found. Please add some transactions first.",
                )
                return

            # Get all currencies except USD (base currency)
            currencies = self.db_manager.get_currencies_except_usd()
            if not currencies:
                QMessageBox.warning(self, "No Currencies", "No currencies found except USD.")
                return

            # Calculate which currencies need updates
            currencies_to_update = []
            today = datetime.now().date()
            earliest_date = datetime.strptime(earliest_transaction_date, "%Y-%m-%d").date()

            print(f"🔍 Checking which currencies need updates...")
            print(f"📅 Earliest transaction date: {earliest_date}")
            print(f"📅 Today's date: {today}")

            for currency_id, currency_code, currency_name, currency_symbol in currencies:
                # Get the last date for this currency
                last_date_str = self.db_manager.get_last_exchange_rate_date(currency_id)

                if last_date_str:
                    last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
                    # Need to update from the day after last_date to today
                    start_date = last_date + timedelta(days=1)

                    # But make sure we don't go earlier than earliest transaction date
                    if start_date < earliest_date:
                        start_date = earliest_date

                    if start_date <= today:
                        currencies_to_update.append((currency_id, currency_code, start_date, today))
                        days_to_update = (today - start_date).days + 1
                        print(f"📊 {currency_code}: Update from {start_date} to {today} ({days_to_update} days)")
                    else:
                        print(f"✅ {currency_code}: Already up to date (last: {last_date})")
                else:
                    # No rates exist for this currency, need to download from earliest transaction date
                    currencies_to_update.append((currency_id, currency_code, earliest_date, today))
                    days_to_update = (today - earliest_date).days + 1
                    print(
                        f"📊 {currency_code}: First time download from {earliest_date} to {today} ({days_to_update} days)"
                    )

            # If no currencies need updates, inform user
            if not currencies_to_update:
                QMessageBox.information(
                    self,
                    "Exchange Rates Up to Date",
                    f"All exchange rates are already up to date as of {today}.\n"
                    f"No updates needed for {len(currencies)} currencies.",
                )
                print(f"✅ All exchange rates are up to date. No updates needed.")
                return

            # Show summary and ask for confirmation
            total_days = sum((end_date - start_date).days + 1 for _, _, start_date, end_date in currencies_to_update)
            currencies_text = ", ".join([curr[1] for curr in currencies_to_update])

            reply = QMessageBox.question(
                self,
                "Update Exchange Rates",
                f"Found {len(currencies_to_update)} currencies that need updates:\n"
                f"{currencies_text}\n\n"
                f"Total days to download: {total_days}\n\n"
                f"Do you want to proceed with the update?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Check if worker is already running
            if hasattr(self, "exchange_rate_worker") and self.exchange_rate_worker.isRunning():
                reply = QMessageBox.question(
                    self,
                    "Update in Progress",
                    "Exchange rate update is already running. Do you want to stop it and start a new one?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.exchange_rate_worker.stop()
                    self.exchange_rate_worker.wait()
                else:
                    return

            # Create and configure progress dialog
            self.progress_dialog = QMessageBox(self)
            self.progress_dialog.setWindowTitle("Updating Exchange Rates")
            self.progress_dialog.setText(f"Starting exchange rate update for {len(currencies_to_update)} currencies...")
            self.progress_dialog.setStandardButtons(QMessageBox.StandardButton.Cancel)
            self.progress_dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)

            # Connect cancel button
            def cancel_update():
                if hasattr(self, "exchange_rate_worker"):
                    self.exchange_rate_worker.stop()
                self.progress_dialog.close()

            self.progress_dialog.buttonClicked.connect(lambda: cancel_update())
            self.progress_dialog.show()

            # Create and start worker thread
            self.exchange_rate_worker = ExchangeRateUpdateWorker(
                self.db_manager, currencies_to_update, earliest_date, today
            )

            # Connect signals
            self.exchange_rate_worker.progress_updated.connect(self._on_progress_updated)
            self.exchange_rate_worker.currency_started.connect(self._on_currency_started)
            self.exchange_rate_worker.rates_added.connect(self._on_rate_added)
            self.exchange_rate_worker.finished_success.connect(self._on_update_finished_success)
            self.exchange_rate_worker.finished_error.connect(self._on_update_finished_error)

            # Start the worker
            self.exchange_rate_worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Update Error", f"Failed to start exchange rate update: {e}")
            print(f"❌ Exchange rate update error: {e}")
```

</details>

### ⚙️ Method `on_yesterday`

```python
def on_yesterday(self) -> None
```

Set yesterday's date in the main date field.

<details>
<summary>Code:</summary>

```python
def on_yesterday(self) -> None:
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit.setDate(yesterday)
```

</details>

### ⚙️ Method `on_yesterday_exchange`

```python
def on_yesterday_exchange(self) -> None
```

Set yesterday's date in the exchange date field.

<details>
<summary>Code:</summary>

```python
def on_yesterday_exchange(self) -> None:
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit_exchange.setDate(yesterday)
```

</details>

### ⚙️ Method `set_chart_all_time`

```python
def set_chart_all_time(self) -> None
```

Set chart date range to all available data.

<details>
<summary>Code:</summary>

```python
def set_chart_all_time(self) -> None:
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, is_all_time=True)
        self.update_charts()
```

</details>

### ⚙️ Method `set_chart_last_month`

```python
def set_chart_last_month(self) -> None
```

Set chart date range to last month.

<details>
<summary>Code:</summary>

```python
def set_chart_last_month(self) -> None:
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, months=1)
        self.update_charts()
```

</details>

### ⚙️ Method `set_chart_last_year`

```python
def set_chart_last_year(self) -> None
```

Set chart date range to last year.

<details>
<summary>Code:</summary>

```python
def set_chart_last_year(self) -> None:
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, years=1)
        self.update_charts()
```

</details>

### ⚙️ Method `set_today_date`

```python
def set_today_date(self) -> None
```

Set today's date in all date fields.

<details>
<summary>Code:</summary>

```python
def set_today_date(self) -> None:
        today_qdate = QDate.currentDate()
        self.dateEdit.setDate(today_qdate)
        self.dateEdit_exchange.setDate(today_qdate)
```

</details>

### ⚙️ Method `show_balance_chart`

```python
def show_balance_chart(self) -> None
```

Show balance chart.

<details>
<summary>Code:</summary>

```python
def show_balance_chart(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get default currency
        default_currency_id = self.db_manager.get_default_currency_id()
        default_currency_code = self.db_manager.get_default_currency()

        # Get date range
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get transaction data for balance calculation
        rows = self.db_manager.get_transactions_chart_data(default_currency_id, date_from=date_from, date_to=date_to)

        if not rows:
            self._show_no_data_label(self.scrollAreaWidgetContents_charts.layout(), "No data found for balance chart")
            return

        # Calculate running balance
        balance = 0.0
        balance_data = []

        for date_str, amount in rows:
            # Get transactions for this date
            daily_transactions = self.db_manager.get_transactions_chart_data(
                default_currency_id, date_from=date_str, date_to=date_str
            )

            daily_balance = 0.0
            for _, daily_amount in daily_transactions:
                # Get category type for each transaction to determine if it's income or expense
                trans_rows = self.db_manager.get_filtered_transactions(date_from=date_str, date_to=date_str)
                for trans_row in trans_rows:
                    if trans_row[5] == date_str:  # date column
                        category_type = trans_row[7]  # type column
                        trans_amount = float(trans_row[1]) / 100  # amount in cents
                        if category_type == 1:  # Income
                            daily_balance += trans_amount
                        else:  # Expense
                            daily_balance -= trans_amount

            balance += daily_balance
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            balance_data.append((date_obj, balance))

        # Create chart configuration
        chart_config = {
            "title": f"Balance Over Time ({default_currency_code})",
            "xlabel": "Date",
            "ylabel": f"Balance ({default_currency_code})",
            "color": "blue",
            "show_stats": True,
            "period": "Days",
        }

        self._create_chart(self.scrollAreaWidgetContents_charts.layout(), balance_data, chart_config)
```

</details>

### ⚙️ Method `show_pie_chart`

```python
def show_pie_chart(self) -> None
```

Show pie chart of expenses by category.

<details>
<summary>Code:</summary>

```python
def show_pie_chart(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get default currency
        default_currency_id = self.db_manager.get_default_currency_id()
        default_currency_code = self.db_manager.get_default_currency()

        # Get date range
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get expense transactions by category
        expense_rows = self.db_manager.get_filtered_transactions(category_type=0, date_from=date_from, date_to=date_to)

        if not expense_rows:
            self._show_no_data_label(
                self.scrollAreaWidgetContents_charts.layout(), "No expense data found for pie chart"
            )
            return

        # Group by category and sum amounts (converted to default currency)
        category_totals = {}
        for row in expense_rows:
            category_name = row[3]  # category name
            amount_cents = row[1]  # amount in cents
            currency_code = row[4]  # currency code

            # Convert to default currency
            if currency_code != default_currency_code:
                currency_info = self.db_manager.get_currency_by_code(currency_code)
                if currency_info:
                    source_currency_id = currency_info[0]
                    exchange_rate = self.db_manager.get_exchange_rate(source_currency_id, default_currency_id)
                    amount = (float(amount_cents) / 100) * exchange_rate
                else:
                    amount = float(amount_cents) / 100
            else:
                amount = float(amount_cents) / 100

            if category_name in category_totals:
                category_totals[category_name] += amount
            else:
                category_totals[category_name] = amount

        # Create pie chart
        self._create_pie_chart(category_totals, f"Expenses by Category ({default_currency_code})")
```

</details>

### ⚙️ Method `show_tables`

```python
def show_tables(self) -> None
```

Populate all QTableViews using database manager methods (except exchange rates - lazy loaded).

<details>
<summary>Code:</summary>

```python
def show_tables(self) -> None:
        if not self._validate_database_connection():
            print("Database connection not available for showing tables")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Load essential tables only (exclude exchange_rates)
            self._load_essential_tables()

            # Exchange rates table loaded lazily on first tab access

        except Exception as e:
            print(f"Error showing tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load tables: {e}")
```

</details>

### ⚙️ Method `update_all`

```python
def update_all(self) -> None
```

Refresh all tables and comboboxes.

<details>
<summary>Code:</summary>

```python
def update_all(self) -> None:
        if not self._validate_database_connection():
            print("Database connection not available for update_all")
            return

        # Load essential tables
        self._load_essential_tables()
        self._update_comboboxes()
        self.update_filter_comboboxes()
        self.update_chart_comboboxes()
        self.set_today_date()
        self.update_summary_labels()

        # If exchange rates tab is currently active, reload the data
        current_tab_index = self.tabWidget.currentIndex()
        if current_tab_index == 4:  # Exchange Rates tab
            self.load_exchange_rates_table()
        else:
            # Mark exchange rates as not loaded to force reload when tab is accessed
            self.exchange_rates_loaded = False

        # Clear forms
        self._clear_all_forms()
```

</details>

### ⚙️ Method `update_chart_comboboxes`

```python
def update_chart_comboboxes(self) -> None
```

Update comboboxes for charts.

<details>
<summary>Code:</summary>

```python
def update_chart_comboboxes(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update category combobox for charts
            categories = self.db_manager.get_categories_by_type(0) + self.db_manager.get_categories_by_type(1)

            self.comboBox_chart_category.clear()
            self.comboBox_chart_category.addItem("All Categories")
            self.comboBox_chart_category.addItems(categories)

        except Exception as e:
            print(f"Error updating chart comboboxes: {e}")
```

</details>

### ⚙️ Method `update_charts`

```python
def update_charts(self) -> None
```

Update charts based on current settings.

<details>
<summary>Code:</summary>

```python
def update_charts(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        category = self.comboBox_chart_category.currentText()
        chart_type = self.comboBox_chart_type.currentText()
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get default currency
        default_currency_id = self.db_manager.get_default_currency_id()
        default_currency_code = self.db_manager.get_default_currency()

        # Determine category type filter
        category_type = None
        if chart_type == "Income":
            category_type = 1
        elif chart_type == "Expense":
            category_type = 0

        # Get chart data
        rows = self.db_manager.get_transactions_chart_data(
            default_currency_id, category_type=category_type, date_from=date_from, date_to=date_to
        )

        if not rows:
            self._show_no_data_label(
                self.scrollAreaWidgetContents_charts.layout(), "No data found for the selected period"
            )
            return

        # Group data by period
        grouped_data = self._group_data_by_period(rows, period)
        chart_data = list(grouped_data.items())

        # Create chart configuration
        chart_title = f"{chart_type} Transactions"
        if category != "All Categories":
            chart_title += f" - {category}"
        chart_title += f" ({period})"

        chart_config = {
            "title": chart_title,
            "xlabel": "Date",
            "ylabel": f"Amount ({default_currency_code})",
            "color": "green" if chart_type == "Income" else "red" if chart_type == "Expense" else "blue",
            "show_stats": True,
            "period": period,
        }

        self._create_chart(self.scrollAreaWidgetContents_charts.layout(), chart_data, chart_config)
```

</details>

### ⚙️ Method `update_filter_comboboxes`

```python
def update_filter_comboboxes(self) -> None
```

Update filter comboboxes with current data.

<details>
<summary>Code:</summary>

```python
def update_filter_comboboxes(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update category filter
            categories = self.db_manager.get_categories_by_type(0) + self.db_manager.get_categories_by_type(1)

            self.comboBox_filter_category.clear()
            self.comboBox_filter_category.addItem("")  # All categories
            self.comboBox_filter_category.addItems(categories)

            # Update currency filter
            currencies = [row[1] for row in self.db_manager.get_all_currencies()]  # Get codes

            self.comboBox_filter_currency.clear()
            self.comboBox_filter_currency.addItem("")  # All currencies
            self.comboBox_filter_currency.addItems(currencies)

        except Exception as e:
            print(f"Error updating filter comboboxes: {e}")
```

</details>

### ⚙️ Method `update_summary_labels`

```python
def update_summary_labels(self) -> None
```

Update summary labels with current totals in default currency.

<details>
<summary>Code:</summary>

```python
def update_summary_labels(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get default currency
            default_currency_id = self.db_manager.get_default_currency_id()
            default_currency_info = self.db_manager.get_currency_by_code(self.db_manager.get_default_currency())
            currency_symbol = default_currency_info[2] if default_currency_info else "₽"

            # Для начальной загрузки показываем только суммы в валюте по умолчанию
            # без конвертации из других валют

            # Упрощенный запрос для получения сумм только в валюте по умолчанию
            query_income = """
                SELECT SUM(t.amount) as total_income
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 1 AND t._id_currencies = :currency_id
            """

            query_expenses = """
                SELECT SUM(t.amount) as total_expenses
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 0 AND t._id_currencies = :currency_id
            """

            income_rows = self.db_manager.get_rows(query_income, {"currency_id": default_currency_id})
            expenses_rows = self.db_manager.get_rows(query_expenses, {"currency_id": default_currency_id})

            total_income = float(income_rows[0][0] or 0) / 100 if income_rows and income_rows[0][0] else 0.0
            total_expenses = float(expenses_rows[0][0] or 0) / 100 if expenses_rows and expenses_rows[0][0] else 0.0

            # Update labels
            self.label_total_income.setText(f"Total Income: {total_income:.2f}{currency_symbol}")
            self.label_total_expenses.setText(f"Total Expenses: {total_expenses:.2f}{currency_symbol}")

            # Для today's balance и expenses также используем упрощенные запросы
            today = datetime.now().strftime("%Y-%m-%d")

            today_query_income = """
                SELECT SUM(t.amount) as total
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 1 AND t._id_currencies = :currency_id AND t.date = :date
            """

            today_query_expenses = """
                SELECT SUM(t.amount) as total
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 0 AND t._id_currencies = :currency_id AND t.date = :date
            """

            today_income_rows = self.db_manager.get_rows(
                today_query_income, {"currency_id": default_currency_id, "date": today}
            )
            today_expenses_rows = self.db_manager.get_rows(
                today_query_expenses, {"currency_id": default_currency_id, "date": today}
            )

            today_income = (
                float(today_income_rows[0][0] or 0) / 100 if today_income_rows and today_income_rows[0][0] else 0.0
            )
            today_expenses = (
                float(today_expenses_rows[0][0] or 0) / 100
                if today_expenses_rows and today_expenses_rows[0][0]
                else 0.0
            )

            today_balance = today_income - today_expenses

            self.label_daily_balance.setText(f"{today_balance:.2f}{currency_symbol}")
            self.label_today_expense.setText(f"{today_expenses:.2f}{currency_symbol}")

        except Exception as e:
            print(f"Error updating summary labels: {e}")
            # Set default values on error
            self.label_total_income.setText("Total Income: 0.00₽")
            self.label_total_expenses.setText("Total Expenses: 0.00₽")
            self.label_daily_balance.setText("0.00₽")
            self.label_today_expense.setText("0.00₽")
```

</details>

### ⚙️ Method `_calculate_daily_expenses`

```python
def _calculate_daily_expenses(self, rows: list[list[Any]]) -> dict[str, float]
```

Calculate daily expenses from transaction data.

Args:
rows: Raw transaction data from database.

Returns:
Dictionary mapping dates to total expenses for that day.

<details>
<summary>Code:</summary>

```python
def _calculate_daily_expenses(self, rows: list[list[Any]]) -> dict[str, float]:
        daily_expenses = {}

        for row in rows:
            # Raw data: [id, amount_cents, description, category_name, currency_code, date, tag, category_type, icon, symbol]
            amount_cents = row[1]
            date = row[5]
            category_type = row[7]

            # Only count expenses (category_type == 0)
            if category_type == 0:
                # Convert amount from minor units to display format using currency subdivision
                currency_code = row[4]
                if self.db_manager:
                    amount = self.db_manager.convert_from_minor_units(
                        amount_cents,
                        self.db_manager.get_currency_by_code(currency_code)[0]
                        if self.db_manager.get_currency_by_code(currency_code)
                        else 1,
                    )
                else:
                    amount = float(amount_cents) / 100  # Fallback

                if date in daily_expenses:
                    daily_expenses[date] += amount
                else:
                    daily_expenses[date] = amount

        return daily_expenses
```

</details>

### ⚙️ Method `_clear_account_form`

```python
def _clear_account_form(self) -> None
```

Clear the account addition form.

<details>
<summary>Code:</summary>

```python
def _clear_account_form(self) -> None:
        self.lineEdit_account_name.clear()
        self.doubleSpinBox_account_balance.setValue(0.0)
        self.checkBox_is_liquid.setChecked(True)
        self.checkBox_is_cash.setChecked(False)
```

</details>

### ⚙️ Method `_clear_all_forms`

```python
def _clear_all_forms(self) -> None
```

Clear all input forms.

<details>
<summary>Code:</summary>

```python
def _clear_all_forms(self) -> None:
        # Transaction form
        self.doubleSpinBox_amount.setValue(100.0)
        self.lineEdit_description.clear()
        self.lineEdit_tag.clear()

        # Category form
        self._clear_category_form()

        # Account form
        self._clear_account_form()

        # Currency form
        self._clear_currency_form()

        # Exchange form
        self._clear_exchange_form()
```

</details>

### ⚙️ Method `_clear_category_form`

```python
def _clear_category_form(self) -> None
```

Clear the category addition form.

<details>
<summary>Code:</summary>

```python
def _clear_category_form(self) -> None:
        self.lineEdit_category_name.clear()
        self.comboBox_category_type.setCurrentIndex(0)
```

</details>

### ⚙️ Method `_clear_currency_form`

```python
def _clear_currency_form(self) -> None
```

Clear the currency addition form.

<details>
<summary>Code:</summary>

```python
def _clear_currency_form(self) -> None:
        self.lineEdit_currency_code.clear()
        self.lineEdit_currency_name.clear()
        self.lineEdit_currency_symbol.clear()
        self.spinBox_subdivision.setValue(100)
```

</details>

### ⚙️ Method `_clear_exchange_form`

```python
def _clear_exchange_form(self) -> None
```

Clear the exchange addition form.

<details>
<summary>Code:</summary>

```python
def _clear_exchange_form(self) -> None:
        self.doubleSpinBox_exchange_from.setValue(100.0)
        self.doubleSpinBox_exchange_to.setValue(73.5)
        self.doubleSpinBox_exchange_rate.setValue(73.5)
        self.doubleSpinBox_exchange_fee.setValue(0.0)
        self.lineEdit_exchange_description.clear()
```

</details>

### ⚙️ Method `_clear_layout`

```python
def _clear_layout(self, layout) -> None
```

Clear all widgets from the specified layout.

<details>
<summary>Code:</summary>

```python
def _clear_layout(self, layout) -> None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
```

</details>

### ⚙️ Method `_connect_signals`

```python
def _connect_signals(self) -> None
```

Connect UI signals to their handlers.

<details>
<summary>Code:</summary>

```python
def _connect_signals(self) -> None:
        # Main transaction signals
        self.pushButton_add.clicked.connect(self.on_add_transaction)
        self.pushButton_description_clear.clicked.connect(self.on_clear_description)
        self.pushButton_yesterday.clicked.connect(self.on_yesterday)

        # Delete and refresh buttons for all tables
        tables_with_controls = {
            "transactions": ("pushButton_delete", "pushButton_refresh"),
            "categories": ("pushButton_categories_delete", "pushButton_categories_refresh"),
            "accounts": ("pushButton_accounts_delete", "pushButton_accounts_refresh"),
            "currencies": ("pushButton_currencies_delete", "pushButton_currencies_refresh"),
            "currency_exchanges": ("pushButton_exchange_delete", "pushButton_exchange_refresh"),
            "exchange_rates": ("pushButton_rates_delete", "pushButton_rates_refresh"),
        }

        for table_name, (delete_btn_name, refresh_btn_name) in tables_with_controls.items():
            delete_button = getattr(self, delete_btn_name)
            refresh_button = getattr(self, refresh_btn_name)
            delete_button.clicked.connect(partial(self.delete_record, table_name))
            refresh_button.clicked.connect(self.update_all)

        # Add buttons
        self.pushButton_category_add.clicked.connect(self.on_add_category)
        self.pushButton_account_add.clicked.connect(self.on_add_account)
        self.pushButton_currency_add.clicked.connect(self.on_add_currency)
        self.pushButton_exchange_add.clicked.connect(self.on_add_exchange)

        # Filter signals
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

        # Auto-filter signals for radio buttons
        self.radioButton.clicked.connect(self.apply_filter)
        self.radioButton_2.clicked.connect(self.apply_filter)
        self.radioButton_3.clicked.connect(self.apply_filter)

        # Auto-filter signals for combo boxes
        self.comboBox_filter_category.currentTextChanged.connect(lambda _: self.apply_filter())
        self.comboBox_filter_currency.currentTextChanged.connect(lambda _: self.apply_filter())

        # Chart signals
        self.pushButton_update_chart.clicked.connect(self.update_charts)
        self.pushButton_pie_chart.clicked.connect(self.show_pie_chart)
        self.pushButton_balance_chart.clicked.connect(self.show_balance_chart)
        self.pushButton_chart_last_month.clicked.connect(self.set_chart_last_month)
        self.pushButton_chart_last_year.clicked.connect(self.set_chart_last_year)
        self.pushButton_chart_all_time.clicked.connect(self.set_chart_all_time)

        # Exchange signals
        self.pushButton_calculate_exchange.clicked.connect(self.on_calculate_exchange)
        self.pushButton_exchange_yesterday.clicked.connect(self.on_yesterday_exchange)

        # Currency signals
        self.pushButton_set_default_currency.clicked.connect(self.on_set_default_currency)

        # Rate signals
        self.pushButton_exchange_update.clicked.connect(self.on_update_exchange_rates)

        # Exchange rates chart signals
        self.comboBox_exchange_rates_currency.currentIndexChanged.connect(self.on_exchange_rates_currency_changed)
        self.pushButton_exchange_rates_last_month.clicked.connect(self.on_exchange_rates_last_month)
        self.pushButton_exchange_rates_last_year.clicked.connect(self.on_exchange_rates_last_year)
        self.pushButton_exchange_rates_all_time.clicked.connect(self.on_exchange_rates_all_time)

        # Auto-update chart when dates change
        self.dateEdit_exchange_rates_from.dateChanged.connect(self.on_exchange_rates_update)
        self.dateEdit_exchange_rates_to.dateChanged.connect(self.on_exchange_rates_update)

        # Report signals
        self.pushButton_generate_report.clicked.connect(self.on_generate_report)

        # Export signal
        self.pushButton_show_all_records.clicked.connect(self.on_show_all_records_clicked)

        # Add context menu for transactions table
        self.tableView_transactions.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_transactions.customContextMenuRequested.connect(self._show_transactions_context_menu)

        # Tab change signal
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Enter key handling for doubleSpinBox_amount
        self.doubleSpinBox_amount.installEventFilter(self)

        # Enter key handling for dateEdit
        self.dateEdit.installEventFilter(self)

        # Enter key handling for lineEdit_tag
        self.lineEdit_tag.installEventFilter(self)

        # Enter key handling for pushButton_add
        self.pushButton_add.installEventFilter(self)
```

</details>

### ⚙️ Method `_connect_table_auto_save_signals`

```python
def _connect_table_auto_save_signals(self) -> None
```

Connect dataChanged signals for auto-save functionality.

<details>
<summary>Code:</summary>

```python
def _connect_table_auto_save_signals(self) -> None:
        # Connect auto-save signals for each table
        for table_name in self._SAFE_TABLES:
            if self.models[table_name] is not None:
                # Use partial to properly bind table_name
                handler = partial(self._on_table_data_changed, table_name)
                model = self.models[table_name]
                if model is not None and hasattr(model, "sourceModel") and model.sourceModel() is not None:
                    model.sourceModel().dataChanged.connect(handler)
```

</details>

### ⚙️ Method `_copy_table_selection_to_clipboard`

```python
def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None
```

Copy selected cells from table to clipboard as tab-separated text.

Args:

- `table_view` (`QTableView`): The table view to copy data from.

<details>
<summary>Code:</summary>

```python
def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None:
        selection_model = table_view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return

        # Get selected indexes and sort them by row and column
        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            return

        # Sort indexes by row first, then by column
        selected_indexes.sort(key=lambda index: (index.row(), index.column()))

        # Group indexes by row
        rows_data = {}
        for index in selected_indexes:
            row = index.row()
            if row not in rows_data:
                rows_data[row] = {}

            # Get cell data
            cell_data = table_view.model().data(index, Qt.ItemDataRole.DisplayRole)
            rows_data[row][index.column()] = str(cell_data) if cell_data is not None else ""

        # Build clipboard text
        clipboard_text = []
        for row in sorted(rows_data.keys()):
            row_data = rows_data[row]
            # Get all columns for this row and fill missing ones with empty strings
            if row_data:
                min_col = min(row_data.keys())
                max_col = max(row_data.keys())
                clipboard_text.append("\t".join([row_data.get(col, "") for col in range(min_col, max_col + 1)]))

        # Copy to clipboard
        if clipboard_text:
            final_text = "\n".join(clipboard_text)
            clipboard = QApplication.clipboard()
            clipboard.setText(final_text)
            print(f"Copied {len(clipboard_text)} rows to clipboard")
```

</details>

### ⚙️ Method `_create_colored_table_model`

```python
def _create_colored_table_model(self, data: list[list], headers: list[str], id_column: int = -2) -> QSortFilterProxyModel
```

Return a proxy model filled with colored table data.

Args:

- `data` (`list[list]`): The table data with color information.
- `headers` (`list[str]`): Column header names.
- `id_column` (`int`): Index of the ID column. Defaults to `-2` (second-to-last).

Returns:

- `QSortFilterProxyModel`: A filterable and sortable model with colored data.

<details>
<summary>Code:</summary>

```python
def _create_colored_table_model(
        self,
        data: list[list],
        headers: list[str],
        id_column: int = -2,
    ) -> QSortFilterProxyModel:
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID (second-to-last element)
            row_color = row[-1]  # Color is at the last position
            row_id = row[id_column]  # ID is at second-to-last position

            # Create items for display columns only (exclude ID and color)
            items = []
            display_data = row[:-2]  # Exclude last two elements (ID and color)

            for _col_idx, value in enumerate(display_data):
                item = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

                items.append(item)

            model.appendRow(items)

            # Set the ID in vertical header
            model.setVerticalHeaderItem(
                row_idx,
                QStandardItem(str(row_id)),
            )

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy
```

</details>

### ⚙️ Method `_create_exchange_rate_chart`

```python
def _create_exchange_rate_chart(self, currency_id: int, date_from: str, date_to: str) -> None
```

Create and display exchange rate chart.

Args:
currency_id: ID of the currency
date_from: Start date in yyyy-MM-dd format
date_to: End date in yyyy-MM-dd format

<details>
<summary>Code:</summary>

```python
def _create_exchange_rate_chart(self, currency_id: int, date_from: str, date_to: str) -> None:
        if not self._validate_database_connection():
            return

        try:
            # Get currency info
            currency_info = self.db_manager.get_currency_by_id(currency_id)
            if not currency_info:
                self._show_no_data_label(self.verticalLayout_exchange_rates_content, "Currency not found")
                return

            currency_code, currency_name, currency_symbol = currency_info

            # Get exchange rates data
            rates_data = self._get_exchange_rates_data(currency_id, date_from, date_to)

            if not rates_data:
                self._show_no_data_label(
                    self.verticalLayout_exchange_rates_content, "No exchange rate data found for the selected period"
                )
                return

            # Clear existing chart
            self._clear_layout(self.verticalLayout_exchange_rates_content)

            # Create matplotlib figure
            fig = Figure(figsize=(12, 6), dpi=100)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            # Extract dates and rates, and transform rates to match table display
            dates = [row[0] for row in rates_data]
            # Transform rates: stored as USD→currency, but display as currency→USD (like in table)
            transformed_rates = []
            for row in rates_data:
                usd_to_currency_rate = float(row[1])
                if usd_to_currency_rate != 0:
                    currency_to_usd_rate = 1.0 / usd_to_currency_rate
                    transformed_rates.append(currency_to_usd_rate)
                else:
                    transformed_rates.append(0.0)

            # Convert dates to datetime objects for plotting
            from datetime import datetime

            date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

            # Plot the data
            ax.plot(date_objects, transformed_rates, color="#2E86AB", linewidth=2)

            # Customize plot
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel(f"Exchange Rate ({currency_code} to USD)", fontsize=12)
            ax.set_title(f"Exchange Rate: {currency_code} to USD ({currency_name})", fontsize=14, fontweight="bold")

            # Format x-axis dates
            ax.tick_params(axis="x", rotation=45)
            fig.autofmt_xdate()

            # Add grid
            ax.grid(visible=True, alpha=0.3)

            # Add value labels for significant points
            if len(transformed_rates) > 1:
                # Label first and last points
                ax.annotate(
                    f"{transformed_rates[0]:.6f}",
                    (date_objects[0], transformed_rates[0]),
                    xytext=(10, 10),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
                )

                ax.annotate(
                    f"{transformed_rates[-1]:.6f}",
                    (date_objects[-1], transformed_rates[-1]),
                    xytext=(10, 10),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
                )

                # Label min and max points if different from first/last
                min_rate = min(transformed_rates)
                max_rate = max(transformed_rates)
                min_idx = transformed_rates.index(min_rate)
                max_idx = transformed_rates.index(max_rate)

                if min_idx != 0 and min_idx != len(transformed_rates) - 1:
                    ax.annotate(
                        f"{min_rate:.6f}",
                        (date_objects[min_idx], min_rate),
                        xytext=(10, -15),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7),
                    )

                if max_idx != 0 and max_idx != len(transformed_rates) - 1:
                    ax.annotate(
                        f"{max_rate:.6f}",
                        (date_objects[max_idx], max_rate),
                        xytext=(10, 15),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7),
                    )

            # Add statistics text
            if len(transformed_rates) > 1:
                avg_rate = sum(transformed_rates) / len(transformed_rates)
                rate_change = transformed_rates[-1] - transformed_rates[0]
                rate_change_percent = (rate_change / transformed_rates[0]) * 100 if transformed_rates[0] != 0 else 0

                stats_text = f"Period: {date_from} to {date_to}\n"
                stats_text += f"Data points: {len(transformed_rates)}\n"
                stats_text += f"Average rate: {avg_rate:.6f}\n"
                stats_text += f"Change: {rate_change:+.6f} ({rate_change_percent:+.2f}%)"

                ax.text(
                    0.02,
                    0.98,
                    stats_text,
                    transform=ax.transAxes,
                    verticalalignment="top",
                    fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8),
                )

            fig.tight_layout()
            self.verticalLayout_exchange_rates_content.addWidget(canvas)
            canvas.draw()

        except Exception as e:
            print(f"Error creating exchange rate chart: {e}")
            self._show_no_data_label(self.verticalLayout_exchange_rates_content, f"Error creating chart: {e}")
```

</details>

### ⚙️ Method `_create_pie_chart`

```python
def _create_pie_chart(self, data: dict[str, float], title: str) -> None
```

Create a pie chart with the given data.

Args:

- `data` (`dict[str, float]`): Dictionary of category names and amounts.
- `title` (`str`): Chart title.

<details>
<summary>Code:</summary>

```python
def _create_pie_chart(self, data: dict[str, float], title: str) -> None:
        # Clear existing chart
        self._clear_layout(self.scrollAreaWidgetContents_charts.layout())

        if not data:
            self._show_no_data_label(self.scrollAreaWidgetContents_charts.layout(), "No data for pie chart")
            return

        # Create matplotlib figure
        fig = Figure(figsize=(10, 8), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Prepare data for pie chart
        labels = list(data.keys())
        sizes = list(data.values())

        # Create pie chart
        pie_result = ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        wedges, texts, autotexts = pie_result if len(pie_result) == 3 else (pie_result[0], pie_result[1], [])

        # Customize appearance
        ax.set_title(title, fontsize=14, fontweight="bold")

        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        fig.tight_layout()
        self.scrollAreaWidgetContents_charts.layout().addWidget(canvas)
        canvas.draw()
```

</details>

### ⚙️ Method `_create_table_model`

```python
def _create_table_model(self, data: list[list[str]], headers: list[str], id_column: int = 0) -> QSortFilterProxyModel
```

Return a proxy model filled with data.

Args:

- `data` (`list[list[str]]`): The table data as a list of rows.
- `headers` (`list[str]`): Column header names.
- `id_column` (`int`): Index of the ID column. Defaults to `0`.

Returns:

- `QSortFilterProxyModel`: A filterable and sortable model with the data.

<details>
<summary>Code:</summary>

```python
def _create_table_model(
        self,
        data: list[list[str]],
        headers: list[str],
        id_column: int = 0,
    ) -> QSortFilterProxyModel:
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            items = [
                QStandardItem(str(value) if value is not None else "")
                for col_idx, value in enumerate(row)
                if col_idx != id_column
            ]
            model.appendRow(items)
            model.setVerticalHeaderItem(
                row_idx,
                QStandardItem(str(row[id_column])),
            )

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy
```

</details>

### ⚙️ Method `_create_transactions_table_model`

```python
def _create_transactions_table_model(self, data: list[list], headers: list[str], id_column: int = -2) -> QSortFilterProxyModel
```

Create a special model for transactions table with non-editable total column.

Args:
data: The table data with color information.
headers: Column header names.
id_column: Index of the ID column. Defaults to -2 (second-to-last).

Returns:
A filterable and sortable model with colored data and non-editable total column.

<details>
<summary>Code:</summary>

```python
def _create_transactions_table_model(
        self,
        data: list[list],
        headers: list[str],
        id_column: int = -2,
    ) -> QSortFilterProxyModel:
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID (second-to-last element)
            row_color = row[-1]  # Color is at the last position
            row_id = row[id_column]  # ID is at second-to-last position

            # Create items for display columns only (exclude ID and color)
            items = []
            display_data = row[:-2]  # Exclude last two elements (ID and color)

            for col_idx, value in enumerate(display_data):
                item = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

                # For amount column (index 1), store original value without minus sign for editing
                if col_idx == 1:  # Amount column
                    # Remove minus sign for editing, keep only the numeric value
                    original_value = str(value).replace("-", "") if value and str(value).startswith("-") else str(value)
                    item.setData(original_value, Qt.ItemDataRole.UserRole)

                # Make the "Total per day" column (last column) non-editable
                if col_idx == len(display_data) - 1:  # Last column
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                items.append(item)

            model.appendRow(items)

            # Set the ID in vertical header
            model.setVerticalHeaderItem(
                row_idx,
                QStandardItem(str(row_id)),
            )

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy
```

</details>

### ⚙️ Method `_dispose_models`

```python
def _dispose_models(self) -> None
```

Detach all models from QTableView and delete them.

<details>
<summary>Code:</summary>

```python
def _dispose_models(self) -> None:
        for key, model in self.models.items():
            if key in self.table_config:
                view = self.table_config[key][0]
                view.setModel(None)
            if model is not None:
                model.deleteLater()
            self.models[key] = None
```

</details>

### ⚙️ Method `_finish_window_initialization`

```python
def _finish_window_initialization(self) -> None
```

Finish window initialization by showing the window.

<details>
<summary>Code:</summary>

```python
def _finish_window_initialization(self) -> None:
        self.show()

        # Set focus to description field
        self.lineEdit_description.setFocus()

        # Select category with _id = 1
        self._select_category_by_id(1)

        # Setup exchange rates controls
        self._setup_exchange_rates_controls()
```

</details>

### ⚙️ Method `_focus_amount_and_select_text`

```python
def _focus_amount_and_select_text(self) -> None
```

Set focus to amount field and select all text.

<details>
<summary>Code:</summary>

```python
def _focus_amount_and_select_text(self) -> None:
        self.doubleSpinBox_amount.setFocus()
        self.doubleSpinBox_amount.selectAll()
```

</details>

### ⚙️ Method `_focus_description_and_select_text`

```python
def _focus_description_and_select_text(self) -> None
```

Set focus to description field and select all text.

<details>
<summary>Code:</summary>

```python
def _focus_description_and_select_text(self) -> None:
        self.lineEdit_description.setFocus()
        self.lineEdit_description.selectAll()
```

</details>

### ⚙️ Method `_generate_account_balances_report`

```python
def _generate_account_balances_report(self, currency_id: int) -> None
```

Generate account balances report.

Args:

- `currency_id` (`int`): Currency ID for conversion.

<details>
<summary>Code:</summary>

```python
def _generate_account_balances_report(self, currency_id: int) -> None:
        if self.db_manager is None:
            return

        account_balances = self.db_manager.get_account_balances_in_currency(currency_id)
        currency_code = self.db_manager.get_default_currency()

        # Create report data
        report_data = []
        total_balance = 0.0

        for account_name, balance in account_balances:
            report_data.append([account_name, f"{balance:.2f} {currency_code}"])
            total_balance += balance

        # Add total row
        report_data.append(["TOTAL", f"{total_balance:.2f} {currency_code}"])

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Account", "Balance"])

        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            # Highlight total row
            if row_data[0] == "TOTAL":
                for item in items:
                    item.setBackground(QBrush(QColor(255, 255, 0)))  # Yellow background
            model.appendRow(items)

        self.tableView_reports.setModel(model)

        # Configure column stretching for reports table
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)
```

</details>

### ⚙️ Method `_generate_category_analysis_report`

```python
def _generate_category_analysis_report(self, currency_id: int) -> None
```

Generate category analysis report.

Args:

- `currency_id` (`int`): Currency ID for conversion.

<details>
<summary>Code:</summary>

```python
def _generate_category_analysis_report(self, currency_id: int) -> None:
        if self.db_manager is None:
            return

        currency_code = self.db_manager.get_default_currency()

        # Get transactions for last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        date_from = start_date.strftime("%Y-%m-%d")
        date_to = end_date.strftime("%Y-%m-%d")

        # Get expenses and income separately
        expense_rows = self.db_manager.get_filtered_transactions(category_type=0, date_from=date_from, date_to=date_to)
        income_rows = self.db_manager.get_filtered_transactions(category_type=1, date_from=date_from, date_to=date_to)

        # Group by category
        expense_totals = {}
        income_totals = {}

        for row in expense_rows:
            category = row[3]  # category name
            amount = float(row[1]) / 100  # amount in cents
            expense_totals[category] = expense_totals.get(category, 0) + amount

        for row in income_rows:
            category = row[3]  # category name
            amount = float(row[1]) / 100  # amount in cents
            income_totals[category] = income_totals.get(category, 0) + amount

        # Create report data
        report_data = []

        # Add expense categories
        if expense_totals:
            report_data.append(["EXPENSES", "", ""])
            for category, amount in sorted(expense_totals.items(), key=lambda x: x[1], reverse=True):
                report_data.append([category, f"{amount:.2f} {currency_code}", "Expense"])

        # Add income categories
        if income_totals:
            report_data.append(["INCOME", "", ""])
            for category, amount in sorted(income_totals.items(), key=lambda x: x[1], reverse=True):
                report_data.append([category, f"{amount:.2f} {currency_code}", "Income"])

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Category", "Amount", "Type"])

        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            # Highlight section headers
            if row_data[0] in ["EXPENSES", "INCOME"]:
                for item in items:
                    item.setBackground(QBrush(QColor(200, 200, 255)))  # Light blue background
            model.appendRow(items)

        self.tableView_reports.setModel(model)

        # Configure column stretching for reports table
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)
```

</details>

### ⚙️ Method `_generate_currency_analysis_report`

```python
def _generate_currency_analysis_report(self) -> None
```

Generate currency analysis report.

<details>
<summary>Code:</summary>

```python
def _generate_currency_analysis_report(self) -> None:
        if self.db_manager is None:
            return

        # Get all currencies and their usage
        currencies = self.db_manager.get_all_currencies()

        report_data = []
        for currency_row in currencies:
            currency_id = currency_row[0]
            currency_code = currency_row[1]

            # Count transactions in this currency
            transactions = self.db_manager.get_filtered_transactions(currency_code=currency_code)
            transaction_count = len(transactions)

            # Calculate total amount
            total_amount = sum(float(row[1]) / 100 for row in transactions)

            report_data.append([currency_code, str(transaction_count), f"{total_amount:.2f}"])

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Currency", "Transaction Count", "Total Amount"])

        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            model.appendRow(items)

        self.tableView_reports.setModel(model)

        # Configure column stretching for reports table
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)
```

</details>

### ⚙️ Method `_generate_income_vs_expenses_report`

```python
def _generate_income_vs_expenses_report(self, currency_id: int) -> None
```

Generate income vs expenses report.

Args:

- `currency_id` (`int`): Currency ID for conversion.

<details>
<summary>Code:</summary>

```python
def _generate_income_vs_expenses_report(self, currency_id: int) -> None:
        if self.db_manager is None:
            return

        currency_code = self.db_manager.get_default_currency()

        # Get data for different periods
        periods = [
            ("Today", 0),
            ("Last 7 days", 7),
            ("Last 30 days", 30),
            ("Last 90 days", 90),
            ("Last 365 days", 365),
        ]

        report_data = []

        for period_name, days in periods:
            if days == 0:
                # Today
                today = datetime.now().strftime("%Y-%m-%d")
                date_from = date_to = today
            else:
                # Last N days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                date_from = start_date.strftime("%Y-%m-%d")
                date_to = end_date.strftime("%Y-%m-%d")

            income, expenses = self.db_manager.get_income_vs_expenses_in_currency(currency_id, date_from, date_to)

            balance = income - expenses

            report_data.append(
                [
                    period_name,
                    f"{income:.2f} {currency_code}",
                    f"{expenses:.2f} {currency_code}",
                    f"{balance:.2f} {currency_code}",
                ]
            )

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Period", "Income", "Expenses", "Balance"])

        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            # Color code the balance
            balance_str = row_data[3]
            balance_value = float(balance_str.split()[0])
            if balance_value > 0:
                items[3].setBackground(QBrush(QColor(200, 255, 200)))  # Light green
            elif balance_value < 0:
                items[3].setBackground(QBrush(QColor(255, 200, 200)))  # Light red

            model.appendRow(items)

        self.tableView_reports.setModel(model)

        # Configure column stretching for reports table
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)
```

</details>

### ⚙️ Method `_generate_monthly_summary_report`

```python
def _generate_monthly_summary_report(self, currency_id: int) -> None
```

Generate monthly summary report.

Args:

- `currency_id` (`int`): Currency ID for conversion.

<details>
<summary>Code:</summary>

```python
def _generate_monthly_summary_report(self, currency_id: int) -> None:
        if self.db_manager is None:
            return

        currency_code = self.db_manager.get_default_currency()

        # Get last 12 months
        report_data = []
        end_date = datetime.now()

        for i in range(12):
            # Calculate month start and end
            month_date = end_date.replace(day=1) - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)

            # Calculate last day of month
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            month_end = next_month - timedelta(days=1)

            date_from = month_start.strftime("%Y-%m-%d")
            date_to = month_end.strftime("%Y-%m-%d")

            income, expenses = self.db_manager.get_income_vs_expenses_in_currency(currency_id, date_from, date_to)

            balance = income - expenses
            month_name = month_start.strftime("%Y-%m")

            report_data.append(
                [
                    month_name,
                    f"{income:.2f} {currency_code}",
                    f"{expenses:.2f} {currency_code}",
                    f"{balance:.2f} {currency_code}",
                ]
            )

        # Reverse to show oldest first
        report_data.reverse()

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Month", "Income", "Expenses", "Balance"])

        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            model.appendRow(items)

        self.tableView_reports.setModel(model)

        # Configure column stretching for reports table
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)
```

</details>

### ⚙️ Method `_get_exchange_rates_data`

```python
def _get_exchange_rates_data(self, currency_id: int, date_from: str, date_to: str) -> list[tuple[str, float]]
```

Get exchange rates data for the specified currency and date range.

Args:
currency_id: ID of the currency
date_from: Start date in yyyy-MM-dd format
date_to: End date in yyyy-MM-dd format

Returns:
List of tuples (date, rate) sorted by date

<details>
<summary>Code:</summary>

```python
def _get_exchange_rates_data(self, currency_id: int, date_from: str, date_to: str) -> list[tuple[str, float]]:
        if not self._validate_database_connection():
            return []

        try:
            # Get exchange rates for the currency in the date range
            query = """
                SELECT date, rate
                FROM exchange_rates
                WHERE _id_currency = :currency_id
                AND date BETWEEN :date_from AND :date_to
                ORDER BY date ASC
            """
            params = {"currency_id": currency_id, "date_from": date_from, "date_to": date_to}

            # Execute query and get results
            query_obj = self.db_manager.execute_query(query, params)
            if query_obj:
                rows = self.db_manager._rows_from_query(query_obj)
                query_obj.clear()
                return [(row[0], float(row[1])) for row in rows if row[1] is not None]
            return []

        except Exception as e:
            print(f"Error getting exchange rates data: {e}")
            return []
```

</details>

### ⚙️ Method `_init_chart_controls`

```python
def _init_chart_controls(self) -> None
```

Initialize chart controls.

<details>
<summary>Code:</summary>

```python
def _init_chart_controls(self) -> None:
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)
```

</details>

### ⚙️ Method `_init_database`

```python
def _init_database(self) -> None
```

Initialize database connection.

<details>
<summary>Code:</summary>

```python
def _init_database(self) -> None:
        filename = Path(config["sqlite_finance"])

        # Try to open existing database first
        if filename.exists():
            try:
                temp_db_manager = database_manager.DatabaseManager(str(filename))

                # Check if required tables exist
                if temp_db_manager.table_exists("transactions"):
                    print(f"Database opened successfully: {filename}")
                    self.db_manager = temp_db_manager
                    return
                print(f"Database exists but required tables are missing at {filename}")
                temp_db_manager.close()
            except Exception as e:
                print(f"Failed to open existing database: {e}")

        # Database doesn't exist or is missing required tables
        if not filename.exists():
            filename_str, _ = QFileDialog.getOpenFileName(
                self,
                "Open Database",
                str(filename.parent),
                "SQLite Database (*.db)",
            )
            if not filename_str:
                QMessageBox.critical(self, "Error", "No database selected")
                sys.exit(1)
            filename = Path(filename_str)

        try:
            self.db_manager = database_manager.DatabaseManager(str(filename))
            print(f"Database opened successfully: {filename}")
        except (OSError, RuntimeError, ConnectionError) as exc:
            QMessageBox.critical(self, "Error", f"Failed to open database: {exc}")
            sys.exit(1)
```

</details>

### ⚙️ Method `_init_filter_controls`

```python
def _init_filter_controls(self) -> None
```

Initialize filter controls.

<details>
<summary>Code:</summary>

```python
def _init_filter_controls(self) -> None:
        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)
        self.checkBox_use_date_filter.setChecked(False)
```

</details>

### ⚙️ Method `_initial_load`

```python
def _initial_load(self) -> None
```

Initial load of essential data at startup (without exchange rates).

<details>
<summary>Code:</summary>

```python
def _initial_load(self) -> None:
        if not self._validate_database_connection():
            print("Database connection not available for initial load")
            return

        # Load essential tables only (excluding exchange rates)
        self._load_essential_tables()
        self._update_comboboxes()
        self.update_filter_comboboxes()
        self.update_chart_comboboxes()
        self.set_today_date()
        self.update_summary_labels()

        # Clear forms
        self._clear_all_forms()

        # Setup exchange rates controls
        self._setup_exchange_rates_controls()
```

</details>

### ⚙️ Method `_load_accounts_table`

```python
def _load_accounts_table(self) -> None
```

Load accounts table.

<details>
<summary>Code:</summary>

```python
def _load_accounts_table(self) -> None:
        accounts_data = self.db_manager.get_all_accounts()

        # Define colors for different account groups
        account_colors = {
            (0, 1): QColor(220, 255, 220),  # is_cash=0, is_liquid=1 - Light green
            (1, 1): QColor(255, 255, 200),  # is_cash=1, is_liquid=1 - Light yellow
            (0, 0): QColor(255, 220, 220),  # is_cash=0, is_liquid=0 - Light red
            (1, 0): QColor(255, 200, 255),  # is_cash=1, is_liquid=0 - Light purple
        }

        # Group accounts by (is_cash, is_liquid) and sort within groups
        account_groups = {
            (0, 1): [],  # is_cash=0, is_liquid=1
            (1, 1): [],  # is_cash=1, is_liquid=1
            (0, 0): [],  # is_cash=0, is_liquid=0
            (1, 0): [],  # is_cash=1, is_liquid=0
        }

        for row in accounts_data:
            # Raw data: [id, name, balance_cents, currency_code, is_liquid, is_cash]
            is_liquid = row[4]
            is_cash = row[5]
            group_key = (is_cash, is_liquid)
            account_groups[group_key].append(row)

        # Sort each group alphabetically by name
        for group in account_groups.values():
            group.sort(key=lambda x: x[1].lower())  # Sort by name (case-insensitive)

        # Combine groups in the specified order
        accounts_transformed_data = []
        for group_key in [(0, 1), (1, 1), (0, 0), (1, 0)]:
            color = account_colors[group_key]
            for row in account_groups[group_key]:
                # Transform: [id, name, balance_cents, currency_code, is_liquid, is_cash, currency_id] -> [name, balance, currency, liquid, cash, id, color]
                currency_id = row[6]  # currency_id
                balance = self.db_manager.convert_from_minor_units(row[2], currency_id)
                liquid_str = "👍" if row[4] == 1 else "👎"
                cash_str = "💵" if row[5] == 1 else "💳"
                transformed_row = [row[1], f"{balance:.2f}", row[3], liquid_str, cash_str, row[0], color]
                accounts_transformed_data.append(transformed_row)

        self.models["accounts"] = self._create_colored_table_model(
            accounts_transformed_data, self.table_config["accounts"][2]
        )
        self.tableView_accounts.setModel(self.models["accounts"])

        # Make accounts table non-editable and connect double-click signal
        self.tableView_accounts.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.tableView_accounts.doubleClicked.connect(self._on_account_double_clicked)

        # Configure column stretching for accounts table
        accounts_header = self.tableView_accounts.horizontalHeader()
        if accounts_header.count() > 0:
            for i in range(accounts_header.count()):
                accounts_header.setSectionResizeMode(i, accounts_header.ResizeMode.Stretch)
            # Ensure stretch settings are applied
            accounts_header.setStretchLastSection(False)
```

</details>

### ⚙️ Method `_load_categories_table`

```python
def _load_categories_table(self) -> None
```

Load categories table.

<details>
<summary>Code:</summary>

```python
def _load_categories_table(self) -> None:
        categories_data = self.db_manager.get_all_categories()
        categories_transformed_data = []
        for row in categories_data:
            # Transform: [id, name, type, icon] -> [name, type_str, icon, id, color]
            type_str = "Expense" if row[2] == 0 else "Income"
            color = QColor(255, 200, 200) if row[2] == 0 else QColor(200, 255, 200)
            transformed_row = [row[1], type_str, row[3], row[0], color]
            categories_transformed_data.append(transformed_row)

        self.models["categories"] = self._create_colored_table_model(
            categories_transformed_data, self.table_config["categories"][2]
        )
        self.tableView_categories.setModel(self.models["categories"])

        # Configure column stretching for categories table
        categories_header = self.tableView_categories.horizontalHeader()
        if categories_header.count() > 0:
            for i in range(categories_header.count()):
                categories_header.setSectionResizeMode(i, categories_header.ResizeMode.Stretch)
```

</details>

### ⚙️ Method `_load_currencies_table`

```python
def _load_currencies_table(self) -> None
```

Load currencies table.

<details>
<summary>Code:</summary>

```python
def _load_currencies_table(self) -> None:
        currencies_data = self.db_manager.get_all_currencies()
        currencies_transformed_data = []
        for row in currencies_data:
            # Transform: [id, code, name, symbol] -> [code, name, symbol, id, color]
            color = QColor(255, 255, 220)
            transformed_row = [row[1], row[2], row[3], row[0], color]
            currencies_transformed_data.append(transformed_row)

        self.models["currencies"] = self._create_colored_table_model(
            currencies_transformed_data, self.table_config["currencies"][2]
        )
        self.tableView_currencies.setModel(self.models["currencies"])

        # Configure column stretching for currencies table
        currencies_header = self.tableView_currencies.horizontalHeader()
        if currencies_header.count() > 0:
            for i in range(currencies_header.count()):
                currencies_header.setSectionResizeMode(i, currencies_header.ResizeMode.Stretch)
```

</details>

### ⚙️ Method `_load_currency_exchanges_table`

```python
def _load_currency_exchanges_table(self) -> None
```

Load currency exchanges table.

<details>
<summary>Code:</summary>

```python
def _load_currency_exchanges_table(self) -> None:
        if self.db_manager is None:
            return

        exchanges_data = self.db_manager.get_all_currency_exchanges()
        exchanges_transformed_data = []
        for row in exchanges_data:
            # Transform: [id, from_code, to_code, amount_from, amount_to, rate, fee, date, description]
            # Данные уже конвертированы в get_all_currency_exchanges()
            color = QColor(255, 240, 255)
            transformed_row = [
                row[1],  # from_code
                row[2],  # to_code
                f"{row[3]:.2f}",  # amount_from (уже конвертировано)
                f"{row[4]:.2f}",  # amount_to (уже конвертировано)
                f"{row[5]:.4f}",  # rate (уже конвертировано)
                f"{row[6]:.2f}",  # fee (уже конвертировано)
                row[7],  # date
                row[8] or "",  # description
                row[0],  # id
                color,
            ]
            exchanges_transformed_data.append(transformed_row)

        self.models["currency_exchanges"] = self._create_colored_table_model(
            exchanges_transformed_data, self.table_config["currency_exchanges"][2]
        )
        self.tableView_exchange.setModel(self.models["currency_exchanges"])

        # Configure column stretching for exchange table
        exchange_header = self.tableView_exchange.horizontalHeader()
        if exchange_header.count() > 0:
            for i in range(exchange_header.count()):
                exchange_header.setSectionResizeMode(i, exchange_header.ResizeMode.Stretch)
            # Ensure stretch settings are applied
            exchange_header.setStretchLastSection(False)
```

</details>

### ⚙️ Method `_load_essential_tables`

```python
def _load_essential_tables(self) -> None
```

Load essential tables at startup (excluding exchange rates for lazy loading).

<details>
<summary>Code:</summary>

```python
def _load_essential_tables(self) -> None:
        if not self._validate_database_connection():
            print("Database connection not available for showing essential tables")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Load each table individually with error handling
            tables_to_load = [
                ("transactions", self._load_transactions_table),
                ("categories", self._load_categories_table),
                ("accounts", self._load_accounts_table),
                ("currencies", self._load_currencies_table),
                ("currency_exchanges", self._load_currency_exchanges_table),
            ]

            for table_name, load_method in tables_to_load:
                try:
                    load_method()
                except Exception as e:
                    print(f"❌ Error loading {table_name} table: {e}")
                    # Продолжаем загрузку других таблиц

            # Connect auto-save signals for loaded tables
            self._connect_table_auto_save_signals()

        except Exception as e:
            print(f"Error loading essential tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load essential tables: {e}")
```

</details>

### ⚙️ Method `_load_transactions_table`

```python
def _load_transactions_table(self) -> None
```

Load transactions table.

<details>
<summary>Code:</summary>

```python
def _load_transactions_table(self) -> None:
        limit = None if self.show_all_transactions else self.count_transactions_to_show
        transactions_data = self.db_manager.get_all_transactions(limit=limit)
        transactions_transformed_data = self._transform_transaction_data(transactions_data)
        self.models["transactions"] = self._create_transactions_table_model(
            transactions_transformed_data, self.table_config["transactions"][2]
        )
        self.tableView_transactions.setModel(self.models["transactions"])

        # Special handling for transactions table - column stretching setup
        header = self.tableView_transactions.horizontalHeader()
        if header.count() > 0:
            # Set stretch mode for all columns except the last two
            for i in range(header.count() - 2):
                header.setSectionResizeMode(i, header.ResizeMode.Stretch)

            # For the second-to-last column (Tag) set fixed width
            second_last_column = header.count() - 2
            header.setSectionResizeMode(second_last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(second_last_column, 100)

            # For the last column (Total per day) set fixed width
            last_column = header.count() - 1
            header.setSectionResizeMode(last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(last_column, 120)
```

</details>

### ⚙️ Method `_mark_categories_changed`

```python
def _mark_categories_changed(self) -> None
```

Mark that category data has changed and needs refresh.

<details>
<summary>Code:</summary>

```python
def _mark_categories_changed(self) -> None:
        # No specific action needed for categories as they load immediately
        pass
```

</details>

### ⚙️ Method `_mark_currencies_changed`

```python
def _mark_currencies_changed(self) -> None
```

Mark that currency data has changed and needs refresh.

<details>
<summary>Code:</summary>

```python
def _mark_currencies_changed(self) -> None:
        # No specific action needed for currencies as they load immediately
        pass
```

</details>

### ⚙️ Method `_mark_default_currency_changed`

```python
def _mark_default_currency_changed(self) -> None
```

Mark that default currency has changed and needs refresh.

<details>
<summary>Code:</summary>

```python
def _mark_default_currency_changed(self) -> None:
        # No specific action needed as this affects multiple areas that reload immediately
        pass
```

</details>

### ⚙️ Method `_mark_exchange_rates_changed`

```python
def _mark_exchange_rates_changed(self) -> None
```

Mark that exchange rates data has changed and needs refresh.

<details>
<summary>Code:</summary>

```python
def _mark_exchange_rates_changed(self) -> None:
        # Mark exchange rates as needing reload
        self.exchange_rates_loaded = False
```

</details>

### ⚙️ Method `_mark_transactions_changed`

```python
def _mark_transactions_changed(self) -> None
```

Mark that transaction data has changed and needs refresh.

<details>
<summary>Code:</summary>

```python
def _mark_transactions_changed(self) -> None:
        # No specific action needed for transactions as they load immediately
        pass
```

</details>

### ⚙️ Method `_on_account_double_clicked`

```python
def _on_account_double_clicked(self, index: QModelIndex) -> None
```

Handle double-click on accounts table.

Args:

- `index` (`QModelIndex`): The clicked index.

<details>
<summary>Code:</summary>

```python
def _on_account_double_clicked(self, index: QModelIndex) -> None:
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # Get the row ID from vertical header
            proxy_model = self.models["accounts"]
            if proxy_model is None:
                return

            source_model = proxy_model.sourceModel()
            if source_model is None:
                return

            row_id_item = source_model.verticalHeaderItem(index.row())
            if row_id_item is None:
                return

            account_id = int(row_id_item.text())

            # Get account data
            account_data = self.db_manager.get_account_by_id(account_id)
            if not account_data:
                QMessageBox.warning(self, "Error", "Account not found")
                return

            # Prepare account data for dialog
            currency_id = account_data[6]  # currency_id
            account_dict = {
                "id": account_data[0],
                "name": account_data[1],
                "balance": self.db_manager.convert_from_minor_units(account_data[2], currency_id),
                "currency_code": account_data[3],
                "is_liquid": account_data[4] == 1,
                "is_cash": account_data[5] == 1,
            }

            # Get currency codes for dialog
            currencies = [row[1] for row in self.db_manager.get_all_currencies()]

            # Show edit dialog
            dialog = AccountEditDialog(self, account_dict, currencies)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                result = dialog.get_result()

                if result["action"] == "save":
                    # Update account
                    currency_info = self.db_manager.get_currency_by_code(result["currency_code"])
                    if not currency_info:
                        QMessageBox.warning(self, "Error", "Currency not found")
                        return

                    currency_id = currency_info[0]

                    success = self.db_manager.update_account(
                        account_id,
                        result["name"],
                        result["balance"],
                        currency_id,
                        is_liquid=result["is_liquid"],
                        is_cash=result["is_cash"],
                    )

                    if success:
                        # Save current column widths before update
                        column_widths = self._save_table_column_widths(self.tableView_accounts)

                        self.update_all()

                        # Restore column widths after update
                        self._restore_table_column_widths(self.tableView_accounts, column_widths)

                        QMessageBox.information(self, "Success", "Account updated successfully")
                        return  # Exit the method to prevent reopening the dialog
                    QMessageBox.warning(self, "Error", "Failed to update account")

                elif result["action"] == "delete":
                    # Save current column widths before update
                    column_widths = self._save_table_column_widths(self.tableView_accounts)

                    # Delete account
                    success = self.db_manager.delete_account(account_id)
                    if success:
                        self.update_all()

                        # Restore column widths after update
                        self._restore_table_column_widths(self.tableView_accounts, column_widths)

                        QMessageBox.information(self, "Success", "Account deleted successfully")
                        return  # Exit the method to prevent reopening the dialog
                    QMessageBox.warning(self, "Error", "Failed to delete account")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit account: {e}")
```

</details>

### ⚙️ Method `_on_autocomplete_selected`

```python
def _on_autocomplete_selected(self, text: str) -> None
```

Handle autocomplete selection and populate form fields.

<details>
<summary>Code:</summary>

```python
def _on_autocomplete_selected(self, text: str) -> None:
        if not text:
            return

        # Set the selected text
        self.lineEdit_description.setText(text)

        # Try to populate other fields based on the selected description
        self._populate_form_from_description(text)

        # Set focus to amount field and select all text after a short delay
        # This ensures form population is complete before focusing
        QTimer.singleShot(100, self._focus_amount_and_select_text)
```

</details>

### ⚙️ Method `_on_currency_started`

```python
def _on_currency_started(self, currency_code: str)
```

Handle currency processing start.

<details>
<summary>Code:</summary>

```python
def _on_currency_started(self, currency_code: str):
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.setText(f"Processing {currency_code}...")
```

</details>

### ⚙️ Method `_on_progress_updated`

```python
def _on_progress_updated(self, message: str)
```

Handle progress updates from worker.

<details>
<summary>Code:</summary>

```python
def _on_progress_updated(self, message: str):
        print(message)
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.setText(message)
```

</details>

### ⚙️ Method `_on_rate_added`

```python
def _on_rate_added(self, currency_code: str, rate: float, date_str: str)
```

Handle successful rate addition.

<details>
<summary>Code:</summary>

```python
def _on_rate_added(self, currency_code: str, rate: float, date_str: str):
        print(f"✅ Added {currency_code}/USD rate: {rate:.6f} for {date_str}")
```

</details>

### ⚙️ Method `_on_table_data_changed`

```python
def _on_table_data_changed(self, table_name: str, top_left: QModelIndex, bottom_right: QModelIndex, _roles: list | None = None) -> None
```

Handle data changes in table models and auto-save to database.

Args:

- `table_name` (`str`): Name of the table that was modified.
- `top_left` (`QModelIndex`): Top-left index of the changed area.
- `bottom_right` (`QModelIndex`): Bottom-right index of the changed area.
- `_roles` (`list | None`): List of roles that changed. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def _on_table_data_changed(
        self, table_name: str, top_left: QModelIndex, bottom_right: QModelIndex, _roles: list | None = None
    ) -> None:
        if table_name not in self._SAFE_TABLES:
            return

        if not self._validate_database_connection():
            return

        try:
            proxy_model = self.models[table_name]
            if proxy_model is None:
                return
            model = proxy_model.sourceModel()
            if not isinstance(model, QStandardItemModel):
                return

            # Process each changed row
            for row in range(top_left.row(), bottom_right.row() + 1):
                vertical_header_item = model.verticalHeaderItem(row)
                if vertical_header_item:
                    row_id = vertical_header_item.text()
                    self._auto_save_row(table_name, model, row, row_id)

        except Exception as e:
            QMessageBox.warning(self, "Auto-save Error", f"Failed to auto-save changes: {e!s}")
```

</details>

### ⚙️ Method `_on_update_finished_error`

```python
def _on_update_finished_error(self, error_message: str)
```

Handle error completion.

<details>
<summary>Code:</summary>

```python
def _on_update_finished_error(self, error_message: str):
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        QMessageBox.critical(self, "Update Error", f"Failed to update exchange rates:\n{error_message}")
        print(f"❌ {error_message}")
```

</details>

### ⚙️ Method `_on_update_finished_success`

```python
def _on_update_finished_success(self, downloaded_count: int, filled_count: int)
```

Handle successful completion.

<details>
<summary>Code:</summary>

```python
def _on_update_finished_success(self, downloaded_count: int, filled_count: int):
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        total_updates = downloaded_count + filled_count
        message_parts = []

        if downloaded_count > 0:
            message_parts.append(f"Downloaded {downloaded_count} new exchange rates")

        if filled_count > 0:
            message_parts.append(f"Filled {filled_count} missing dates")

        if message_parts:
            message = "Successfully completed exchange rate update:\n• " + "\n• ".join(message_parts)
            QMessageBox.information(self, "Update Complete", message)

            # Mark exchange rates as changed to trigger reload if tab is active
            self._mark_exchange_rates_changed()
            # If exchange rates tab is currently active, reload the data
            current_tab_index = self.tabWidget.currentIndex()
            if current_tab_index == 4:  # Exchange Rates tab
                self.load_exchange_rates_table()
        else:
            QMessageBox.information(
                self,
                "Update Complete",
                "Exchange rates are already up to date.",
            )
```

</details>

### ⚙️ Method `_populate_form_from_description`

```python
def _populate_form_from_description(self, description: str) -> None
```

Populate form fields based on description from database.

<details>
<summary>Code:</summary>

```python
def _populate_form_from_description(self, description: str) -> None:
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # Get the most recent transaction with this description
            query = """
                SELECT t.amount, cat.name, c.code, t.tag
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                JOIN currencies c ON t._id_currencies = c._id
                WHERE t.description = :description
                ORDER BY t.date DESC, t._id DESC
                LIMIT 1
            """

            rows = self.db_manager.get_rows(query, {"description": description})

            if rows:
                amount_cents, category_name, currency_code, tag = rows[0]

                # Populate form fields
                amount = float(amount_cents) / 100  # Convert from cents
                self.doubleSpinBox_amount.setValue(amount)
                self.lineEdit_tag.setText(tag or "")

                # Set category if found
                if category_name:
                    # Find the category in the list view
                    model = self.listView_categories.model()
                    if model:
                        for row in range(model.rowCount()):
                            index = model.index(row, 0)
                            item_data = model.data(index, Qt.ItemDataRole.UserRole)
                            if item_data == category_name:
                                self.listView_categories.setCurrentIndex(index)
                                break

                # Set currency if found
                if currency_code:
                    index = self.comboBox_currency.findText(currency_code)
                    if index >= 0:
                        self.comboBox_currency.setCurrentIndex(index)

        except Exception as e:
            print(f"Error populating form from description: {e}")
```

</details>

### ⚙️ Method `_restore_table_column_widths`

```python
def _restore_table_column_widths(self, table_view: QTableView, column_widths: list[int]) -> None
```

Restore column widths for a table view.

Args:
table_view: The table view to restore column widths for.
column_widths: List of column widths to restore.

<details>
<summary>Code:</summary>

```python
def _restore_table_column_widths(self, table_view: QTableView, column_widths: list[int]) -> None:
        header = table_view.horizontalHeader()
        if column_widths and header.count() == len(column_widths):
            for i, width in enumerate(column_widths):
                table_view.setColumnWidth(i, width)
```

</details>

### ⚙️ Method `_save_table_column_widths`

```python
def _save_table_column_widths(self, table_view: QTableView) -> list[int]
```

Save column widths for a table view.

Args:
table_view: The table view to save column widths for.

Returns:
List of column widths.

<details>
<summary>Code:</summary>

```python
def _save_table_column_widths(self, table_view: QTableView) -> list[int]:
        header = table_view.horizontalHeader()
        column_widths = []
        for i in range(header.count()):
            column_widths.append(table_view.columnWidth(i))
        return column_widths
```

</details>

### ⚙️ Method `_select_category_by_id`

```python
def _select_category_by_id(self, category_id: int) -> None
```

Select category in listView_categories by database ID.

Args:

- `category_id` (`int`): Database ID of the category to select.

<details>
<summary>Code:</summary>

```python
def _select_category_by_id(self, category_id: int) -> None:
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # Get category name by ID using get_id method
            query = "SELECT name FROM categories WHERE _id = :category_id"
            rows = self.db_manager.get_rows(query, {"category_id": category_id})
            if not rows:
                print(f"Category with ID {category_id} not found")
                return

            category_name = rows[0][0]

            # Find the category in the list view
            model = self.listView_categories.model()
            if model:
                for row in range(model.rowCount()):
                    index = model.index(row, 0)
                    item_data = model.data(index, Qt.ItemDataRole.UserRole)
                    if item_data == category_name:
                        self.listView_categories.setCurrentIndex(index)
                        # Update the category label
                        display_text = model.data(index, Qt.ItemDataRole.DisplayRole)
                        if display_text:
                            self.label_category_now.setText(display_text)
                        break

        except Exception as e:
            print(f"Error selecting category by ID: {e}")
```

</details>

### ⚙️ Method `_set_exchange_rates_date_range`

```python
def _set_exchange_rates_date_range(self) -> None
```

Set the date range for exchange rates chart.

<details>
<summary>Code:</summary>

```python
def _set_exchange_rates_date_range(self) -> None:
        if not self._validate_database_connection():
            return

        try:
            # Get earliest transaction date for start date
            earliest_date = self.db_manager.get_earliest_transaction_date()
            if earliest_date:
                start_date = QDate.fromString(earliest_date, "yyyy-MM-dd")
                self.dateEdit_exchange_rates_from.setDate(start_date)
            else:
                # Fallback to 1 year ago
                start_date = QDate.currentDate().addYears(-1)
                self.dateEdit_exchange_rates_from.setDate(start_date)

            # Set end date to current date
            self.dateEdit_exchange_rates_to.setDate(QDate.currentDate())

        except Exception as e:
            print(f"Error setting exchange rates date range: {e}")
```

</details>

### ⚙️ Method `_setup_autocomplete`

```python
def _setup_autocomplete(self) -> None
```

Setup autocomplete functionality for description input.

<details>
<summary>Code:</summary>

```python
def _setup_autocomplete(self) -> None:
        # Create completer
        self.description_completer = QCompleter(self)
        self.description_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.description_completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Search by content
        self.description_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        # Create model for completer
        self.description_completer_model = QStringListModel(self)
        self.description_completer.setModel(self.description_completer_model)

        # Set completer to the line edit
        self.lineEdit_description.setCompleter(self.description_completer)

        # Update autocomplete data
        self._update_autocomplete_data()

        # Connect selection signal
        self.description_completer.activated.connect(self._on_autocomplete_selected)
```

</details>

### ⚙️ Method `_setup_exchange_rates_controls`

```python
def _setup_exchange_rates_controls(self) -> None
```

Setup exchange rates chart controls with initial values.

<details>
<summary>Code:</summary>

```python
def _setup_exchange_rates_controls(self) -> None:
        if not self._validate_database_connection():
            return

        try:
            # Block signals temporarily to prevent chart drawing during setup
            self.dateEdit_exchange_rates_from.blockSignals(True)
            self.dateEdit_exchange_rates_to.blockSignals(True)

            # Fill currency combo box
            currencies = self.db_manager.get_all_currencies()
            self.comboBox_exchange_rates_currency.clear()

            # Add currencies with format: "RUB - Russian Ruble"
            for currency in currencies:
                currency_id, code, name, symbol = currency
                display_text = f"{code} - {name}"
                self.comboBox_exchange_rates_currency.addItem(display_text, currency_id)

            # Set default currency (ID = 1)
            default_index = self.comboBox_exchange_rates_currency.findData(1)
            if default_index >= 0:
                self.comboBox_exchange_rates_currency.setCurrentIndex(default_index)

            # Set date range
            self._set_exchange_rates_date_range()

            # Mark that initial setup is complete
            self._exchange_rates_initialized = True

            # Unblock signals after setup is complete
            self.dateEdit_exchange_rates_from.blockSignals(False)
            self.dateEdit_exchange_rates_to.blockSignals(False)

            # Draw initial chart
            self.on_exchange_rates_update()

        except Exception as e:
            print(f"Error setting up exchange rates controls: {e}")
            # Ensure signals are unblocked even if there's an error
            self.dateEdit_exchange_rates_from.blockSignals(False)
            self.dateEdit_exchange_rates_to.blockSignals(False)
```

</details>

### ⚙️ Method `_setup_tab_order`

```python
def _setup_tab_order(self) -> None
```

Setup tab order for widgets in groupBox_transaction.

<details>
<summary>Code:</summary>

```python
def _setup_tab_order(self) -> None:
        from PySide6.QtWidgets import QWidget

        # Set tab order for widgets in groupBox_transaction
        # Make pushButton_description_clear the last in tab order
        QWidget.setTabOrder(self.lineEdit_description, self.doubleSpinBox_amount)
        QWidget.setTabOrder(self.doubleSpinBox_amount, self.comboBox_currency)
        QWidget.setTabOrder(self.comboBox_currency, self.dateEdit)
        QWidget.setTabOrder(self.dateEdit, self.pushButton_yesterday)
        QWidget.setTabOrder(self.pushButton_yesterday, self.pushButton_add)
        QWidget.setTabOrder(self.pushButton_add, self.lineEdit_tag)
        QWidget.setTabOrder(self.lineEdit_tag, self.listView_categories)
        QWidget.setTabOrder(self.listView_categories, self.pushButton_delete)
        QWidget.setTabOrder(self.pushButton_delete, self.pushButton_show_all_records)
        QWidget.setTabOrder(self.pushButton_show_all_records, self.pushButton_refresh)
        QWidget.setTabOrder(self.pushButton_refresh, self.pushButton_clear_filter)
        QWidget.setTabOrder(self.pushButton_clear_filter, self.pushButton_apply_filter)
        QWidget.setTabOrder(self.pushButton_apply_filter, self.pushButton_description_clear)
```

</details>

### ⚙️ Method `_setup_ui`

```python
def _setup_ui(self) -> None
```

Set up additional UI elements.

<details>
<summary>Code:</summary>

```python
def _setup_ui(self) -> None:
        # Set emoji for buttons
        self.pushButton_yesterday.setText(f"📅 {self.pushButton_yesterday.text()}")
        self.pushButton_add.setText(f"➕ {self.pushButton_add.text()}")
        self.pushButton_delete.setText(f"🗑️ {self.pushButton_delete.text()}")
        self.pushButton_refresh.setText(f"🔄 {self.pushButton_refresh.text()}")
        self.pushButton_clear_filter.setText(f"🧹 {self.pushButton_clear_filter.text()}")
        self.pushButton_apply_filter.setText(f"✔️ {self.pushButton_apply_filter.text()}")
        self.pushButton_description_clear.setText("🧹")
        self.pushButton_show_all_records.setText("📊 Show All Records")

        # Configure splitter proportions
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 3)

        # Set default values
        self.doubleSpinBox_amount.setValue(100.0)
        self.doubleSpinBox_exchange_from.setValue(100.0)
        self.doubleSpinBox_exchange_to.setValue(73.5)
        self.doubleSpinBox_exchange_rate.setValue(73.5)
        self.spinBox_subdivision.setValue(100)
```

</details>

### ⚙️ Method `_setup_window_size_and_position`

```python
def _setup_window_size_and_position(self) -> None
```

Set window size and position based on screen resolution and characteristics.

<details>
<summary>Code:</summary>

```python
def _setup_window_size_and_position(self) -> None:
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Determine window size and position based on screen characteristics
        aspect_ratio = screen_width / screen_height
        is_standard_aspect = aspect_ratio <= 2.0  # Standard aspect ratio (16:9, 16:10, etc.)

        if is_standard_aspect and screen_width >= 1920:
            # For standard aspect ratios with width >= 1920, maximize window
            self.showMaximized()
        else:
            title_bar_height = 30  # Approximate title bar height
            windows_task_bar_height = 48  # Approximate windows task bar height
            # For other cases, use fixed width and full height minus title bar
            window_width = 1920
            window_height = screen_height - title_bar_height - windows_task_bar_height
            # Position window on screen
            screen_center = screen_geometry.center()
            # Center horizontally, position at top vertically with title bar offset
            self.setGeometry(
                screen_center.x() - window_width // 2,
                title_bar_height,  # Position below title bar
                window_width,
                window_height,
            )
```

</details>

### ⚙️ Method `_show_no_data_label`

```python
def _show_no_data_label(self, layout, message: str) -> None
```

Show a message when no data is available for the chart.

<details>
<summary>Code:</summary>

```python
def _show_no_data_label(self, layout, message: str) -> None:
        from PySide6.QtWidgets import QLabel

        # Clear existing content
        self._clear_layout(layout)

        # Create and add label
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #666; padding: 20px;")
        layout.addWidget(label)
```

</details>

### ⚙️ Method `_show_transactions_context_menu`

```python
def _show_transactions_context_menu(self, position) -> None
```

Show context menu for transactions table.

Args:

- `position`: Position where context menu should appear.

<details>
<summary>Code:</summary>

```python
def _show_transactions_context_menu(self, position) -> None:
        from PySide6.QtWidgets import QMenu

        context_menu = QMenu(self)
        export_action = context_menu.addAction("Export to CSV")

        action = context_menu.exec(self.tableView_transactions.mapToGlobal(position))

        if action == export_action:
            self.on_export_csv()
```

</details>

### ⚙️ Method `_transform_transaction_data`

```python
def _transform_transaction_data(self, rows: list[list[Any]]) -> list[list[Any]]
```

Transform transaction data for display with colors and daily totals.

Args:

- `rows` (`list[list[Any]]`): Raw transaction data.

Returns:

- `list[list[Any]]`: Transformed data with colors and daily totals.

<details>
<summary>Code:</summary>

```python
def _transform_transaction_data(self, rows: list[list[Any]]) -> list[list[Any]]:
        transformed_data = []

        # Calculate daily expenses
        daily_expenses = self._calculate_daily_expenses(rows)

        # Create a mapping of dates to color indices
        date_to_color_index = {}
        color_index = 0

        # Track which dates we've already shown totals for
        dates_with_totals = set()

        for row in rows:
            # Raw data: [id, amount_cents, description, category_name, currency_code, date, tag, category_type, icon, symbol]
            transaction_id = row[0]
            amount_cents = row[1]
            description = row[2]
            category_name = row[3]
            currency_code = row[4]
            date = row[5]
            tag = row[6]
            category_type = row[7]

            # Convert amount from minor units to display format using currency subdivision
            if self.db_manager:
                amount = self.db_manager.convert_from_minor_units(
                    amount_cents,
                    self.db_manager.get_currency_by_code(currency_code)[0]
                    if self.db_manager.get_currency_by_code(currency_code)
                    else 1,
                )
            else:
                amount = float(amount_cents) / 100  # Fallback

            # Determine color based on date
            if date not in date_to_color_index:
                date_to_color_index[date] = color_index % len(self.date_colors)
                color_index += 1

            color = self.date_colors[date_to_color_index[date]]

            # Add "(Income)" suffix for income categories
            display_category_name = category_name
            if category_type == 1:  # Income category
                display_category_name = f"{category_name} (Income)"

            # Determine if this is the first transaction for this date
            is_first_of_day = date not in dates_with_totals
            if is_first_of_day:
                dates_with_totals.add(date)

            # Get daily total for this date
            daily_total = daily_expenses.get(date, 0.0)
            total_display = f"-{daily_total:.2f}" if is_first_of_day and daily_total > 0 else ""

            # Format amount with minus sign for expenses
            amount_display = f"-{amount:.2f}" if category_type == 0 else f"{amount:.2f}"

            # Transform to display format: [description, amount, category, currency, date, tag, total_per_day, id, color]
            transformed_row = [
                description,
                amount_display,
                display_category_name,
                currency_code,
                date,
                tag,
                total_display,
                transaction_id,
                color,
            ]
            transformed_data.append(transformed_row)

        return transformed_data
```

</details>

### ⚙️ Method `_update_autocomplete_data`

```python
def _update_autocomplete_data(self) -> None
```

Update autocomplete data from database.

<details>
<summary>Code:</summary>

```python
def _update_autocomplete_data(self) -> None:
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # Get recent transaction descriptions for autocomplete
            recent_descriptions = self.db_manager.get_recent_transaction_descriptions_for_autocomplete(1000)

            # Update completer model
            self.description_completer_model.setStringList(recent_descriptions)

        except Exception as e:
            print(f"Error updating autocomplete data: {e}")
```

</details>

### ⚙️ Method `_update_comboboxes`

```python
def _update_comboboxes(self) -> None
```

Update all comboboxes with current data.

<details>
<summary>Code:</summary>

```python
def _update_comboboxes(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update currency comboboxes
            currencies = [row[1] for row in self.db_manager.get_all_currencies()]  # Get codes

            for combo in [
                self.comboBox_currency,
                self.comboBox_account_currency,
                self.comboBox_exchange_from,
                self.comboBox_exchange_to,
                self.comboBox_default_currency,
            ]:
                combo.clear()
                combo.addItems(currencies)

            # Update categories list view with icons
            expense_categories = self.db_manager.get_categories_with_icons_by_type(0)
            income_categories = self.db_manager.get_categories_with_icons_by_type(1)

            model = QStandardItemModel()

            # Add expense categories first
            for category_name, icon in expense_categories:
                # Create display text with icon
                display_text = f"{icon} {category_name}" if icon else category_name
                item = QStandardItem(display_text)
                # Store the original category name as data for selection handling
                item.setData(category_name, Qt.ItemDataRole.UserRole)
                model.appendRow(item)

            # Add income categories with special marking
            for category_name, icon in income_categories:
                # Create display text with icon and income marker
                base_text = f"{icon} {category_name}" if icon else category_name
                display_text = f"{base_text} (Income)"  # Add income marker in parentheses
                item = QStandardItem(display_text)
                # Store the original category name as data for selection handling
                item.setData(category_name, Qt.ItemDataRole.UserRole)
                model.appendRow(item)

            self.listView_categories.setModel(model)

            # Connect category selection signal after model is set
            self.listView_categories.selectionModel().currentChanged.connect(self.on_category_selection_changed)

            # Reset category selection label
            self.label_category_now.setText("No category selected")

            # Set default currency selection
            default_currency = self.db_manager.get_default_currency()
            for combo in [
                self.comboBox_currency,
                self.comboBox_account_currency,
                self.comboBox_exchange_from,
                self.comboBox_default_currency,
            ]:
                index = combo.findText(default_currency)
                if index >= 0:
                    combo.setCurrentIndex(index)

            # Set exchange_to currency based on logic
            # If current currency is not USD, set USD as exchange_to, otherwise set currency with _id = 1
            if default_currency != "USD":
                # Set USD as exchange_to
                usd_index = self.comboBox_exchange_to.findText("USD")
                if usd_index >= 0:
                    self.comboBox_exchange_to.setCurrentIndex(usd_index)
            else:
                # Current currency is USD, set currency with _id = 1 as exchange_to
                currency_info = self.db_manager.get_currency_by_id(1)
                if currency_info:
                    currency_code = currency_info[0]  # Get code from (code, name, symbol)
                    currency_index = self.comboBox_exchange_to.findText(currency_code)
                    if currency_index >= 0:
                        self.comboBox_exchange_to.setCurrentIndex(currency_index)

        except Exception as e:
            print(f"Error updating comboboxes: {e}")
```

</details>

### ⚙️ Method `_validate_database_connection`

```python
def _validate_database_connection(self) -> bool
```

Validate database connection.

Returns:

- `bool`: True if connection is valid, False otherwise.

<details>
<summary>Code:</summary>

```python
def _validate_database_connection(self) -> bool:
        if not self.db_manager:
            print("Database manager is None")
            return False

        if not self.db_manager.is_database_open():
            print("Database connection is not open")
            return False

        return True
```

</details>
