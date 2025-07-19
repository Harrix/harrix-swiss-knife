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
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `on_add_account`](#%EF%B8%8F-method-on_add_account)
  - [⚙️ Method `on_add_category`](#%EF%B8%8F-method-on_add_category)
  - [⚙️ Method `on_add_currency`](#%EF%B8%8F-method-on_add_currency)
  - [⚙️ Method `on_add_transaction`](#%EF%B8%8F-method-on_add_transaction)
  - [⚙️ Method `on_category_selection_changed`](#%EF%B8%8F-method-on_category_selection_changed)
  - [⚙️ Method `on_export_csv`](#%EF%B8%8F-method-on_export_csv)
  - [⚙️ Method `on_generate_report`](#%EF%B8%8F-method-on_generate_report)
  - [⚙️ Method `on_show_balance_chart`](#%EF%B8%8F-method-on_show_balance_chart)
  - [⚙️ Method `on_show_pie_chart`](#%EF%B8%8F-method-on_show_pie_chart)
  - [⚙️ Method `on_tab_changed`](#%EF%B8%8F-method-on_tab_changed)
  - [⚙️ Method `on_update_chart`](#%EF%B8%8F-method-on_update_chart)
  - [⚙️ Method `set_chart_all_time`](#%EF%B8%8F-method-set_chart_all_time)
  - [⚙️ Method `set_chart_last_month`](#%EF%B8%8F-method-set_chart_last_month)
  - [⚙️ Method `set_chart_last_year`](#%EF%B8%8F-method-set_chart_last_year)
  - [⚙️ Method `set_today_date`](#%EF%B8%8F-method-set_today_date)
  - [⚙️ Method `set_yesterday_date`](#%EF%B8%8F-method-set_yesterday_date)
  - [⚙️ Method `show_tables`](#%EF%B8%8F-method-show_tables)
  - [⚙️ Method `update_all`](#%EF%B8%8F-method-update_all)
  - [⚙️ Method `update_daily_balance`](#%EF%B8%8F-method-update_daily_balance)
  - [⚙️ Method `update_filter_comboboxes`](#%EF%B8%8F-method-update_filter_comboboxes)
  - [⚙️ Method `update_summary_labels`](#%EF%B8%8F-method-update_summary_labels)
  - [⚙️ Method `_calculate_running_balance`](#%EF%B8%8F-method-_calculate_running_balance)
  - [⚙️ Method `_connect_signals`](#%EF%B8%8F-method-_connect_signals)
  - [⚙️ Method `_connect_table_auto_save_signals`](#%EF%B8%8F-method-_connect_table_auto_save_signals)
  - [⚙️ Method `_connect_table_selection_signals`](#%EF%B8%8F-method-_connect_table_selection_signals)
  - [⚙️ Method `_copy_table_selection_to_clipboard`](#%EF%B8%8F-method-_copy_table_selection_to_clipboard)
  - [⚙️ Method `_create_pie_chart`](#%EF%B8%8F-method-_create_pie_chart)
  - [⚙️ Method `_create_table_model`](#%EF%B8%8F-method-_create_table_model)
  - [⚙️ Method `_dispose_models`](#%EF%B8%8F-method-_dispose_models)
  - [⚙️ Method `_generate_account_balances`](#%EF%B8%8F-method-_generate_account_balances)
  - [⚙️ Method `_generate_category_analysis`](#%EF%B8%8F-method-_generate_category_analysis)
  - [⚙️ Method `_generate_currency_analysis`](#%EF%B8%8F-method-_generate_currency_analysis)
  - [⚙️ Method `_generate_income_vs_expenses`](#%EF%B8%8F-method-_generate_income_vs_expenses)
  - [⚙️ Method `_generate_monthly_summary`](#%EF%B8%8F-method-_generate_monthly_summary)
  - [⚙️ Method `_get_current_selected_category`](#%EF%B8%8F-method-_get_current_selected_category)
  - [⚙️ Method `_group_data_by_period`](#%EF%B8%8F-method-_group_data_by_period)
  - [⚙️ Method `_init_categories_list`](#%EF%B8%8F-method-_init_categories_list)
  - [⚙️ Method `_init_chart_controls`](#%EF%B8%8F-method-_init_chart_controls)
  - [⚙️ Method `_init_database`](#%EF%B8%8F-method-_init_database)
  - [⚙️ Method `_init_filter_controls`](#%EF%B8%8F-method-_init_filter_controls)
  - [⚙️ Method `_on_table_data_changed`](#%EF%B8%8F-method-_on_table_data_changed)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)
  - [⚙️ Method `_setup_window_size_and_position`](#%EF%B8%8F-method-_setup_window_size_and_position)
  - [⚙️ Method `_update_comboboxes`](#%EF%B8%8F-method-_update_comboboxes)
  - [⚙️ Method `_validate_database_connection`](#%EF%B8%8F-method-_validate_database_connection)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow, window.Ui_MainWindow, TableOperations, ChartOperations, DateOperations, AutoSaveOperations, ValidationOperations)
```

Main application window for the finance tracking application.

This class implements the main GUI window for the finance tracker, providing
functionality to record transactions, manage categories, accounts, and currencies.

Attributes:

- `_SAFE_TABLES` (`frozenset[str]`): Set of table names that can be safely modified.

- `db_manager` (`database_manager.DatabaseManager | None`): Database
  connection manager. Defaults to `None` until initialized.

- `models` (`dict[str, QSortFilterProxyModel | None]`): Dictionary of table models keyed
  by table name. All values default to `None` until tables are loaded.

- `table_config` (`dict[str, tuple[QTableView, str, list[str]]]`): Configuration for each
  table, mapping table names to tuples of (table view widget, model key, column headers).

- `categories_list_model` (`QStandardItemModel | None`): Model for the categories list view.
  Defaults to `None` until initialized.

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
        {"transactions", "categories", "accounts", "currencies"},
    )

    def __init__(self) -> None:  # noqa: D107  (inherited from Qt widgets)
        super().__init__()
        self.setupUi(self)
        self._setup_ui()

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Initialize core attributes
        self.db_manager: database_manager.DatabaseManager | None = None

        # Categories list model
        self.categories_list_model: QStandardItemModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "transactions": None,
            "categories": None,
            "accounts": None,
            "currencies": None,
            "reports": None,
        }

        # Chart configuration
        self.max_count_points_in_charts = 40

        # Table configuration mapping
        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "transactions": (
                self.tableView_transactions,
                "transactions",
                ["ID", "Type", "Amount", "Currency", "Category", "Description", "Date"],
            ),
            "categories": (
                self.tableView_categories,
                "categories",
                ["ID", "Name", "Type"],
            ),
            "accounts": (
                self.tableView_accounts,
                "accounts",
                ["ID", "Name", "Currency", "Balance", "Liquid", "Cash"],
            ),
            "currencies": (
                self.tableView_currencies,
                "currencies",
                ["ID", "Code", "Name", "Symbol"],
            ),
            "reports": (
                self.tableView_reports,
                "reports",
                ["Category", "Type", "Amount", "Currency"],
            ),
        }

        # Initialize application
        self._init_database()
        self._connect_signals()
        self._init_filter_controls()
        self._init_categories_list()
        self._init_chart_controls()
        self.update_all()

        # Set window size and position
        self._setup_window_size_and_position()

        # Show window after initialization
        QTimer.singleShot(200, self.show)

    @requires_database()
    def apply_filter(self) -> None:
        """Apply combo-box/date filters to the transactions table."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        category = self.comboBox_filter_category.currentText()
        transaction_type = self.comboBox_filter_type.currentText()
        currency = self.comboBox_filter_currency.currentText()
        use_date_filter = self.checkBox_use_date_filter.isChecked()
        date_from = self.dateEdit_filter_from.date().toString("yyyy-MM-dd") if use_date_filter else None
        date_to = self.dateEdit_filter_to.date().toString("yyyy-MM-dd") if use_date_filter else None

        # Use database manager method
        rows = self.db_manager.get_filtered_transactions(
            category=category if category else None,
            transaction_type=transaction_type if transaction_type else None,
            currency=currency if currency else None,
            date_from=date_from,
            date_to=date_to,
        )

        self.models["transactions"] = self._create_table_model(rows, self.table_config["transactions"][2])
        self.tableView_transactions.setModel(self.models["transactions"])
        self.tableView_transactions.resizeColumnsToContents()

    def clear_filter(self) -> None:
        """Reset all transaction-table filters."""
        self.comboBox_filter_category.setCurrentIndex(0)
        self.comboBox_filter_type.setCurrentIndex(0)
        self.comboBox_filter_currency.setCurrentIndex(0)
        self.checkBox_use_date_filter.setChecked(False)

        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        self.show_tables()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle application close event.

        Args:

        - `event` (`QCloseEvent`): The close event.

        """
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
            elif table_name == "categories":
                success = self.db_manager.delete_category(record_id)
            elif table_name == "accounts":
                success = self.db_manager.delete_account(record_id)
            elif table_name == "currencies":
                success = self.db_manager.delete_currency(record_id)
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            self.update_all()
            self.update_daily_balance()
        else:
            QMessageBox.warning(self, "Error", f"Deletion failed in {table_name}")

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
                self.tableView_reports,
            ]

            for table_view in table_views:
                if focused_widget == table_view:
                    self._copy_table_selection_to_clipboard(table_view)
                    return

            # If focused widget is a child of a table view (like the viewport)
            for table_view in table_views:
                if focused_widget and table_view.isAncestorOf(focused_widget):
                    self._copy_table_selection_to_clipboard(table_view)
                    return

        # Call parent implementation for other key events
        super().keyPressEvent(event)

    @requires_database()
    def on_add_account(self) -> None:
        """Insert a new account using database manager."""
        account_name = self.lineEdit_account_name.text().strip()
        currency_code = self.comboBox_account_currency.currentText()
        balance = self.doubleSpinBox_account_balance.value()
        is_liquid = self.checkBox_is_liquid.isChecked()
        is_cash = self.checkBox_is_cash.isChecked()

        if not account_name:
            QMessageBox.warning(self, "Error", "Enter account name")
            return

        if not currency_code:
            QMessageBox.warning(self, "Error", "Select currency")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            currency_id = self.db_manager.get_id("currencies", "code", currency_code)
            if currency_id is None:
                QMessageBox.warning(self, "Error", f"Currency '{currency_code}' not found")
                return

            if self.db_manager.add_account(account_name, currency_id, balance, is_liquid, is_cash):
                self.update_all()
                self.lineEdit_account_name.clear()
                self.doubleSpinBox_account_balance.setValue(0.0)
            else:
                QMessageBox.warning(self, "Error", "Failed to add account")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add account: {e}")

    @requires_database()
    def on_add_category(self) -> None:
        """Insert a new category using database manager."""
        category_name = self.lineEdit_category_name.text().strip()
        category_type = self.comboBox_category_type.currentText().lower()

        if not category_name:
            QMessageBox.warning(self, "Error", "Enter category name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.add_category(category_name, category_type):
                self.update_all()
                self.lineEdit_category_name.clear()
            else:
                QMessageBox.warning(self, "Error", "Failed to add category")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add category: {e}")

    @requires_database()
    def on_add_currency(self) -> None:
        """Insert a new currency using database manager."""
        currency_code = self.lineEdit_currency_code.text().strip().upper()
        currency_name = self.lineEdit_currency_name.text().strip()
        currency_symbol = self.lineEdit_currency_symbol.text().strip()

        if not currency_code:
            QMessageBox.warning(self, "Error", "Enter currency code")
            return

        if not currency_name:
            QMessageBox.warning(self, "Error", "Enter currency name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.add_currency(currency_code, currency_name, currency_symbol):
                self.update_all()
                self.lineEdit_currency_code.clear()
                self.lineEdit_currency_name.clear()
                self.lineEdit_currency_symbol.clear()
            else:
                QMessageBox.warning(self, "Error", "Failed to add currency")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add currency: {e}")

    @requires_database()
    def on_add_transaction(self) -> None:
        """Insert a new transaction using database manager."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get transaction type
            if self.radioButton_income.isChecked():
                transaction_type = "income"
            elif self.radioButton_expense.isChecked():
                transaction_type = "expense"
            elif self.radioButton_transfer.isChecked():
                transaction_type = "transfer"
            else:
                QMessageBox.warning(self, "Error", "Please select transaction type")
                return

            # Get amount
            amount = self.doubleSpinBox_amount.value()
            if amount <= 0:
                QMessageBox.warning(self, "Error", "Amount must be greater than 0")
                return

            # Get currency
            currency_code = self.comboBox_currency.currentText()
            if not currency_code:
                QMessageBox.warning(self, "Error", "Please select currency")
                return

            currency_id = self.db_manager.get_id("currencies", "code", currency_code)
            if currency_id is None:
                QMessageBox.warning(self, "Error", f"Currency '{currency_code}' not found")
                return

            # Get category
            category_name = self.comboBox_category.currentText()
            if not category_name:
                QMessageBox.warning(self, "Error", "Please select category")
                return

            category_id = self.db_manager.get_id("categories", "name", category_name)
            if category_id is None:
                QMessageBox.warning(self, "Error", f"Category '{category_name}' not found")
                return

            # Get description
            description = self.lineEdit_description.text().strip()

            # Get date
            date_str = self.dateEdit.date().toString("yyyy-MM-dd")

            # Use database manager method
            if self.db_manager.add_transaction(
                transaction_type, amount, currency_id, category_id, description, date_str
            ):
                # Apply date increment logic
                self._increment_date_widget(self.dateEdit)

                # Update UI
                self.show_tables()
                self._update_comboboxes()
                self.update_filter_comboboxes()
                self.update_daily_balance()
            else:
                QMessageBox.warning(self, "Error", "Failed to add transaction")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add transaction: {e}")

    def on_category_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle category selection change in the list view."""
        category = self._get_current_selected_category()
        if not category:
            return

        # Update category selection in transaction form
        index = self.comboBox_category.findText(category)
        if index >= 0:
            self.comboBox_category.setCurrentIndex(index)

    def on_export_csv(self) -> None:
        """Save current `transactions` view to a CSV file (semicolon-separated)."""
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

    def on_generate_report(self) -> None:
        """Generate selected report type."""
        report_type = self.comboBox_report_type.currentText()

        if not self._validate_database_connection():
            return

        if report_type == "Monthly Summary":
            self._generate_monthly_summary()
        elif report_type == "Category Analysis":
            self._generate_category_analysis()
        elif report_type == "Currency Analysis":
            self._generate_currency_analysis()
        elif report_type == "Account Balances":
            self._generate_account_balances()
        elif report_type == "Income vs Expenses":
            self._generate_income_vs_expenses()

    def on_show_balance_chart(self) -> None:
        """Show balance chart over time."""
        if not self._validate_database_connection():
            return

        # Get date range
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get all transactions in date range
        rows = self.db_manager.get_filtered_transactions(
            date_from=date_from,
            date_to=date_to,
        )

        if not rows:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found")
            return

        # Calculate running balance
        balance_data = self._calculate_running_balance(rows)

        if not balance_data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No balance data to display")
            return

        # Create chart configuration
        chart_config = {
            "title": "Account Balance Over Time",
            "xlabel": "Date",
            "ylabel": "Balance (₽)",
            "color": "green",
            "show_stats": True,
            "stats_unit": "₽",
        }

        self._create_chart(self.verticalLayout_charts_content, balance_data, chart_config)

    def on_show_pie_chart(self) -> None:
        """Show pie chart of expenses by category."""
        if not self._validate_database_connection():
            return

        # Get date range
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get expense data
        rows = self.db_manager.get_filtered_transactions(
            transaction_type="expense",
            date_from=date_from,
            date_to=date_to,
        )

        if not rows:
            self._show_no_data_label(self.verticalLayout_charts_content, "No expense data found")
            return

        # Group by category
        category_totals = {}
        for row in rows:
            category = row[4]  # Category name
            amount = float(row[2])  # Amount
            category_totals[category] = category_totals.get(category, 0) + amount

        # Create pie chart
        self._create_pie_chart(category_totals, "Expenses by Category")

    def on_tab_changed(self, index: int) -> None:
        """React to `QTabWidget` index change.

        Args:

        - `index` (`int`): The index of the newly selected tab.

        """
        if index == 0:  # Transactions tab
            self.update_filter_comboboxes()
            self.update_daily_balance()
        elif index == 1:  # Categories tab
            pass
        elif index == 2:  # Accounts tab
            pass
        elif index == 3:  # Currencies tab
            pass
        elif index == 4:  # Charts tab
            pass
        elif index == 5:  # Reports tab
            self.update_summary_labels()

    def on_update_chart(self) -> None:
        """Update chart based on selected filters."""
        if not self._validate_database_connection():
            return

        # Get chart parameters
        category = self.comboBox_chart_category.currentText()
        chart_type = self.comboBox_chart_type.currentText()
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get filtered data
        rows = self.db_manager.get_filtered_transactions(
            category=category if category else None,
            transaction_type=chart_type.lower() if chart_type != "All" else None,
            date_from=date_from,
            date_to=date_to,
        )

        if not rows:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found for the selected filters")
            return

        # Group data by period
        grouped_data = self._group_data_by_period(rows, period)

        if not grouped_data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data to display")
            return

        # Prepare chart data
        chart_data = list(grouped_data.items())

        # Create chart configuration
        chart_config = {
            "title": f"{chart_type} - {category if category else 'All Categories'} ({period})",
            "xlabel": "Date",
            "ylabel": "Amount",
            "color": "blue",
            "show_stats": True,
            "stats_unit": "₽",
        }

        self._create_chart(self.verticalLayout_charts_content, chart_data, chart_config)

    def set_chart_all_time(self) -> None:
        """Set chart date range to all available data."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, is_all_time=True)

    def set_chart_last_month(self) -> None:
        """Set chart date range to last month."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, months=1)

    def set_chart_last_year(self) -> None:
        """Set chart date range to last year."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, years=1)

    def set_today_date(self) -> None:
        """Set today's date in the date edit fields."""
        today_qdate = QDate.currentDate()
        self.dateEdit.setDate(today_qdate)

    def set_yesterday_date(self) -> None:
        """Set yesterday's date in the main date edit field."""
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit.setDate(yesterday)

    def show_tables(self) -> None:
        """Populate all QTableViews using database manager methods."""
        if not self._validate_database_connection():
            print("Database connection not available for showing tables")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Refresh all tables
            self._refresh_table("transactions", self.db_manager.get_all_transactions)
            self._refresh_table("categories", self.db_manager.get_all_categories)
            self._refresh_table("accounts", self.db_manager.get_all_accounts)
            self._refresh_table("currencies", self.db_manager.get_all_currencies)

            # Connect selection change signals after models are set
            self._connect_table_selection_signals()

            # Connect auto-save signals after all models are created
            self._connect_table_auto_save_signals()

        except Exception as e:
            print(f"Error showing tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load tables: {e}")

    def update_all(self) -> None:
        """Refresh tables, list view and dates."""
        if not self._validate_database_connection():
            print("Database connection not available for update_all")
            return

        self.show_tables()
        self._update_comboboxes()
        self.set_today_date()
        self.update_filter_comboboxes()
        self.update_daily_balance()

        # Clear forms
        self.lineEdit_category_name.clear()
        self.lineEdit_account_name.clear()
        self.doubleSpinBox_account_balance.setValue(0.0)
        self.lineEdit_currency_code.clear()
        self.lineEdit_currency_name.clear()
        self.lineEdit_currency_symbol.clear()

    def update_daily_balance(self) -> None:
        """Update the daily balance display."""
        if not self._validate_database_connection():
            self.label_daily_balance.setText("0.00₽")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            today = QDate.currentDate().toString("yyyy-MM-dd")
            balance = self.db_manager.get_daily_balance(today)

            # Format balance with appropriate color
            if balance > 0:
                color = "green"
                sign = "+"
            elif balance < 0:
                color = "red"
                sign = ""
            else:
                color = "black"
                sign = ""

            self.label_daily_balance.setText(f'<span style="color: {color};">{sign}{balance:.2f}₽</span>')
        except Exception as e:
            print(f"Error updating daily balance: {e}")
            self.label_daily_balance.setText("0.00₽")

    @requires_database(is_show_warning=False)
    def update_filter_comboboxes(self) -> None:
        """Refresh filter combo-boxes."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update category filter
            current_category = self.comboBox_filter_category.currentText()
            self.comboBox_filter_category.blockSignals(True)  # noqa: FBT003
            self.comboBox_filter_category.clear()
            self.comboBox_filter_category.addItem("")
            categories = self.db_manager.get_items("categories", "name", order_by="name")
            self.comboBox_filter_category.addItems(categories)
            if current_category:
                idx = self.comboBox_filter_category.findText(current_category)
                if idx >= 0:
                    self.comboBox_filter_category.setCurrentIndex(idx)
            self.comboBox_filter_category.blockSignals(False)  # noqa: FBT003

            # Update type filter
            current_type = self.comboBox_filter_type.currentText()
            self.comboBox_filter_type.blockSignals(True)  # noqa: FBT003
            self.comboBox_filter_type.clear()
            self.comboBox_filter_type.addItems(["", "All", "Income", "Expense", "Transfer"])
            if current_type:
                idx = self.comboBox_filter_type.findText(current_type)
                if idx >= 0:
                    self.comboBox_filter_type.setCurrentIndex(idx)
            self.comboBox_filter_type.blockSignals(False)  # noqa: FBT003

            # Update currency filter
            current_currency = self.comboBox_filter_currency.currentText()
            self.comboBox_filter_currency.blockSignals(True)  # noqa: FBT003
            self.comboBox_filter_currency.clear()
            self.comboBox_filter_currency.addItem("")
            currencies = self.db_manager.get_currencies_list()
            self.comboBox_filter_currency.addItems(currencies)
            if current_currency:
                idx = self.comboBox_filter_currency.findText(current_currency)
                if idx >= 0:
                    self.comboBox_filter_currency.setCurrentIndex(idx)
            self.comboBox_filter_currency.blockSignals(False)  # noqa: FBT003

        except Exception as e:
            print(f"Error updating filter comboboxes: {e}")

    def update_summary_labels(self) -> None:
        """Update summary labels in reports tab."""
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get all transactions
            rows = self.db_manager.get_all_transactions()

            total_income = 0.0
            total_expenses = 0.0

            for row in rows:
                transaction_type = row[1]  # Type
                amount = float(row[2])  # Amount

                if transaction_type == "income":
                    total_income += amount
                elif transaction_type == "expense":
                    total_expenses += amount

            net_balance = total_income - total_expenses

            # Update labels
            self.label_total_income.setText(f"Total Income: {total_income:.2f}₽")
            self.label_total_expenses.setText(f"Total Expenses: {total_expenses:.2f}₽")

            # Set net balance color
            if net_balance > 0:
                color = "green"
            elif net_balance < 0:
                color = "red"
            else:
                color = "black"

            self.label_net_balance.setText(f'<span style="color: {color};">Net Balance: {net_balance:.2f}₽</span>')

            # Get total accounts balance
            account_rows = self.db_manager.get_all_accounts()
            total_accounts = sum(float(row[3]) for row in account_rows)  # Balance column
            self.label_total_accounts.setText(f"Total in Accounts: {total_accounts:.2f}₽")

        except Exception as e:
            print(f"Error updating summary labels: {e}")

    def _calculate_running_balance(self, rows: list) -> list:
        """Calculate running balance from transaction data.

        Args:

        - `rows` (`list`): List of transaction rows.

        Returns:

        - `list`: List of (date, balance) tuples.

        """
        # Sort by date
        sorted_rows = sorted(rows, key=lambda x: x[7])  # Date is at index 7

        balance_data = []
        running_balance = 0.0

        for row in sorted_rows:
            transaction_type = row[1]  # Type
            amount = float(row[2])  # Amount
            date_str = row[7]  # Date

            if transaction_type == "income":
                running_balance += amount
            elif transaction_type == "expense":
                running_balance -= amount

            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                balance_data.append((date_obj, running_balance))
            except ValueError:
                continue

        return balance_data

    def _connect_signals(self) -> None:
        """Wire Qt widgets to their Python slots."""
        self.pushButton_add.clicked.connect(self.on_add_transaction)
        self.pushButton_yesterday.clicked.connect(self.set_yesterday_date)

        # Connect delete and refresh buttons for all tables
        tables_with_controls = {"transactions", "categories", "accounts", "currencies"}
        for table_name in tables_with_controls:
            # Delete buttons
            if table_name == "transactions":
                delete_btn_name = "pushButton_delete"
                refresh_btn_name = "pushButton_refresh"
            else:
                delete_btn_name = f"pushButton_{table_name}_delete"
                refresh_btn_name = f"pushButton_{table_name}_refresh"

            delete_button = getattr(self, delete_btn_name)
            delete_button.clicked.connect(partial(self.delete_record, table_name))

            refresh_button = getattr(self, refresh_btn_name)
            refresh_button.clicked.connect(self.update_all)

        # Add buttons
        self.pushButton_category_add.clicked.connect(self.on_add_category)
        self.pushButton_account_add.clicked.connect(self.on_add_account)
        self.pushButton_currency_add.clicked.connect(self.on_add_currency)

        # Export
        # self.pushButton_export_csv.clicked.connect(self.on_export_csv)  # Button not available in UI

        # Tab change
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Filter signals
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

        # Chart signals
        self.pushButton_update_chart.clicked.connect(self.on_update_chart)
        self.pushButton_pie_chart.clicked.connect(self.on_show_pie_chart)
        self.pushButton_balance_chart.clicked.connect(self.on_show_balance_chart)
        self.pushButton_chart_last_month.clicked.connect(self.set_chart_last_month)
        self.pushButton_chart_last_year.clicked.connect(self.set_chart_last_year)
        self.pushButton_chart_all_time.clicked.connect(self.set_chart_all_time)

        # Reports
        self.pushButton_generate_report.clicked.connect(self.on_generate_report)

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

    def _connect_table_selection_signals(self) -> None:
        """Connect selection change signals for all tables."""
        # Connect categories list selection
        selection_model = self.listView_categories.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_category_selection_changed)

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

    def _create_pie_chart(self, data: dict, title: str) -> None:
        """Create a pie chart with the given data.

        Args:

        - `data` (`dict`): Dictionary with labels as keys and values as values.
        - `title` (`str`): Chart title.

        """
        # Clear existing chart
        self._clear_layout(self.verticalLayout_charts_content)

        if not data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data to display")
            return

        # Create matplotlib figure
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        fig = Figure(figsize=(10, 8), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Create pie chart
        labels = list(data.keys())
        values = list(data.values())

        ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.set_title(title, fontsize=14, fontweight="bold")

        fig.tight_layout()
        self.verticalLayout_charts_content.addWidget(canvas)
        canvas.draw()

    def _create_table_model(
        self,
        data: list[list[str]],
        headers: list[str],
        id_column: int = 0,
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with `data`.

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

    def _dispose_models(self) -> None:
        """Detach all models from QTableView and delete them."""
        for key, model in self.models.items():
            if key in self.table_config:
                view = self.table_config[key][0]
                view.setModel(None)
            if model is not None:
                model.deleteLater()
            self.models[key] = None

        # list-view
        self.listView_categories.setModel(None)
        if self.categories_list_model is not None:
            self.categories_list_model.deleteLater()
        self.categories_list_model = None

    def _generate_account_balances(self) -> None:
        """Generate account balances report."""
        if self.db_manager is None:
            return

        try:
            rows = self.db_manager.get_all_accounts()

            # Transform data for display
            report_data = []
            for row in rows:
                account_name = row[1]  # Name
                currency = row[2]  # Currency
                balance = row[3]  # Balance
                liquid = "Yes" if row[4] else "No"  # Liquid
                cash = "Yes" if row[5] else "No"  # Cash

                report_data.append([account_name, currency, f"{balance:.2f}", liquid, cash])

            # Update table
            headers = ["Account", "Currency", "Balance", "Liquid", "Cash"]
            self.models["reports"] = self._create_table_model(report_data, headers, id_column=-1)
            self.tableView_reports.setModel(self.models["reports"])
            self.tableView_reports.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate account balances report: {e}")

    def _generate_category_analysis(self) -> None:
        """Generate category analysis report."""
        if self.db_manager is None:
            return

        try:
            rows = self.db_manager.get_all_transactions()

            # Group by category
            category_totals = {}
            for row in rows:
                category = row[4]  # Category
                transaction_type = row[1]  # Type
                amount = float(row[2])  # Amount

                if category not in category_totals:
                    category_totals[category] = {"income": 0.0, "expense": 0.0, "transfer": 0.0}

                category_totals[category][transaction_type] += amount

            # Transform data for display
            report_data = []
            for category, totals in category_totals.items():
                income = totals["income"]
                expense = totals["expense"]
                transfer = totals["transfer"]
                net = income - expense

                report_data.append([category, f"{income:.2f}", f"{expense:.2f}", f"{transfer:.2f}", f"{net:.2f}"])

            # Sort by net amount descending
            report_data.sort(key=lambda x: float(x[4]), reverse=True)

            # Update table
            headers = ["Category", "Income", "Expense", "Transfer", "Net"]
            self.models["reports"] = self._create_table_model(report_data, headers, id_column=-1)
            self.tableView_reports.setModel(self.models["reports"])
            self.tableView_reports.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate category analysis report: {e}")

    def _generate_currency_analysis(self) -> None:
        """Generate currency analysis report."""
        if self.db_manager is None:
            return

        try:
            rows = self.db_manager.get_all_transactions()

            # Group by currency
            currency_totals = {}
            for row in rows:
                currency = row[3]  # Currency symbol
                transaction_type = row[1]  # Type
                amount = float(row[2])  # Amount

                if currency not in currency_totals:
                    currency_totals[currency] = {"income": 0.0, "expense": 0.0, "transfer": 0.0}

                currency_totals[currency][transaction_type] += amount

            # Transform data for display
            report_data = []
            for currency, totals in currency_totals.items():
                income = totals["income"]
                expense = totals["expense"]
                transfer = totals["transfer"]
                net = income - expense

                report_data.append([currency, f"{income:.2f}", f"{expense:.2f}", f"{transfer:.2f}", f"{net:.2f}"])

            # Sort by net amount descending
            report_data.sort(key=lambda x: float(x[4]), reverse=True)

            # Update table
            headers = ["Currency", "Income", "Expense", "Transfer", "Net"]
            self.models["reports"] = self._create_table_model(report_data, headers, id_column=-1)
            self.tableView_reports.setModel(self.models["reports"])
            self.tableView_reports.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate currency analysis report: {e}")

    def _generate_income_vs_expenses(self) -> None:
        """Generate income vs expenses report."""
        if self.db_manager is None:
            return

        try:
            rows = self.db_manager.get_all_transactions()

            # Group by month
            monthly_totals = {}
            for row in rows:
                date_str = row[7]  # Date
                transaction_type = row[1]  # Type
                amount = float(row[2])  # Amount

                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    month_key = date_obj.strftime("%Y-%m")

                    if month_key not in monthly_totals:
                        monthly_totals[month_key] = {"income": 0.0, "expense": 0.0}

                    if transaction_type in ["income", "expense"]:
                        monthly_totals[month_key][transaction_type] += amount

                except ValueError:
                    continue

            # Transform data for display
            report_data = []
            for month, totals in sorted(monthly_totals.items(), reverse=True):
                income = totals["income"]
                expense = totals["expense"]
                net = income - expense

                report_data.append([month, f"{income:.2f}", f"{expense:.2f}", f"{net:.2f}"])

            # Update table
            headers = ["Month", "Income", "Expense", "Net"]
            self.models["reports"] = self._create_table_model(report_data, headers, id_column=-1)
            self.tableView_reports.setModel(self.models["reports"])
            self.tableView_reports.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate income vs expenses report: {e}")

    def _generate_monthly_summary(self) -> None:
        """Generate monthly summary report."""
        if self.db_manager is None:
            return

        try:
            rows = self.db_manager.get_all_transactions()

            # Group by month and category
            monthly_data = {}
            for row in rows:
                date_str = row[7]  # Date
                category = row[4]  # Category
                transaction_type = row[1]  # Type
                amount = float(row[2])  # Amount

                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    month_key = date_obj.strftime("%Y-%m")

                    if month_key not in monthly_data:
                        monthly_data[month_key] = {}

                    if category not in monthly_data[month_key]:
                        monthly_data[month_key][category] = {"income": 0.0, "expense": 0.0, "transfer": 0.0}

                    monthly_data[month_key][category][transaction_type] += amount

                except ValueError:
                    continue

            # Transform data for display
            report_data = []
            for month in sorted(monthly_data.keys(), reverse=True):
                for category, totals in monthly_data[month].items():
                    income = totals["income"]
                    expense = totals["expense"]
                    transfer = totals["transfer"]
                    net = income - expense

                    report_data.append(
                        [month, category, f"{income:.2f}", f"{expense:.2f}", f"{transfer:.2f}", f"{net:.2f}"]
                    )

            # Update table
            headers = ["Month", "Category", "Income", "Expense", "Transfer", "Net"]
            self.models["reports"] = self._create_table_model(report_data, headers, id_column=-1)
            self.tableView_reports.setModel(self.models["reports"])
            self.tableView_reports.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate monthly summary report: {e}")

    def _get_current_selected_category(self) -> str | None:
        """Get the currently selected category from the list view.

        Returns:

        - `str | None`: The name of the selected category, or None if nothing is selected.

        """
        selection_model = self.listView_categories.selectionModel()
        if not selection_model or not self.categories_list_model:
            return None

        current_index = selection_model.currentIndex()
        if not current_index.isValid():
            return None

        item = self.categories_list_model.itemFromIndex(current_index)
        return item.text() if item else None

    def _group_data_by_period(self, rows: list, period: str) -> dict:
        """Group data by the specified period (Days, Months, Years).

        Args:

        - `rows` (`list`): List of transaction rows.
        - `period` (`str`): Grouping period (Days, Months, Years).

        Returns:

        - `dict`: Dictionary with datetime keys and aggregated values.

        """
        from collections import defaultdict

        grouped = defaultdict(float)

        for row in rows:
            date_str = row[7]  # Date
            amount = float(row[2])  # Amount
            transaction_type = row[1]  # Type

            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue

            # Adjust amount based on transaction type
            if transaction_type == "expense":
                amount = -amount

            if period == "Days":
                key = date_obj
            elif period == "Months":
                key = date_obj.replace(day=1)
            elif period == "Years":
                key = date_obj.replace(month=1, day=1)
            else:
                key = date_obj

            grouped[key] += amount

        return dict(sorted(grouped.items()))

    def _init_categories_list(self) -> None:
        """Initialize the categories list view with a model and connect signals."""
        self.categories_list_model = QStandardItemModel()
        self.listView_categories.setModel(self.categories_list_model)

        # Disable editing for categories list
        self.listView_categories.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

        # Connect selection change signal after model is set
        selection_model = self.listView_categories.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_category_selection_changed)

    def _init_chart_controls(self) -> None:
        """Initialize chart controls."""
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)

    def _init_database(self) -> None:
        """Open the SQLite file from `config` (create from recover.sql if missing)."""
        filename = Path(config["sqlite_finance"])

        # Try to open existing database first
        if filename.exists():
            try:
                temp_db_manager = database_manager.DatabaseManager(str(filename))

                # Check if transactions table exists
                if temp_db_manager.table_exists("transactions"):
                    print(f"Database opened successfully: {filename}")
                    self.db_manager = temp_db_manager
                    return
                print(f"Database exists but transactions table is missing at {filename}")
                temp_db_manager.close()
            except Exception as e:
                print(f"Failed to open existing database: {e}")

        # Database doesn't exist or is missing required table - create from recover.sql
        app_dir = Path(__file__).parent
        recover_sql_path = app_dir / "recover.sql"

        if recover_sql_path.exists():
            print(f"Database not found or missing transactions table at {filename}")
            print(f"Attempting to create database from {recover_sql_path}")

            if database_manager.DatabaseManager.create_database_from_sql(str(filename), str(recover_sql_path)):
                print("Database created successfully from recover.sql")
            else:
                QMessageBox.warning(
                    self,
                    "Database Creation Failed",
                    f"Failed to create database from {recover_sql_path}\nPlease select an existing database file.",
                )
        else:
            QMessageBox.information(
                self,
                "Database Not Found",
                f"Database file not found: {filename}\n"
                f"recover.sql file not found: {recover_sql_path}\n"
                "Please select an existing database file.",
            )

        # If database still doesn't exist, ask user to select one
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
        """Prepare widgets on the `Filters` group box."""
        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        self.checkBox_use_date_filter.setChecked(False)

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
                row_id = model.verticalHeaderItem(row).text()
                self._auto_save_row(table_name, model, row, row_id)

        except Exception as e:
            QMessageBox.warning(self, "Auto-save Error", f"Failed to auto-save changes: {e!s}")

    def _setup_ui(self) -> None:
        """Set up additional UI elements after basic initialization."""
        # Set emoji for buttons
        self.pushButton_yesterday.setText(f"📅 {self.pushButton_yesterday.text()}")
        self.pushButton_add.setText(f"➕ {self.pushButton_add.text()}")
        self.pushButton_delete.setText(f"🗑️ {self.pushButton_delete.text()}")
        self.pushButton_refresh.setText(f"🔄 {self.pushButton_refresh.text()}")
        self.pushButton_clear_filter.setText(f"🧹 {self.pushButton_clear_filter.text()}")
        self.pushButton_apply_filter.setText(f"✔️ {self.pushButton_apply_filter.text()}")
        self.pushButton_category_add.setText(f"➕ {self.pushButton_category_add.text()}")
        self.pushButton_categories_delete.setText(f"🗑️ {self.pushButton_categories_delete.text()}")
        self.pushButton_categories_refresh.setText(f"🔄 {self.pushButton_categories_refresh.text()}")
        self.pushButton_account_add.setText(f"➕ {self.pushButton_account_add.text()}")
        self.pushButton_accounts_delete.setText(f"🗑️ {self.pushButton_accounts_delete.text()}")
        self.pushButton_accounts_refresh.setText(f"🔄 {self.pushButton_accounts_refresh.text()}")
        self.pushButton_currency_add.setText(f"➕ {self.pushButton_currency_add.text()}")
        self.pushButton_currencies_delete.setText(f"🗑️ {self.pushButton_currencies_delete.text()}")
        self.pushButton_currencies_refresh.setText(f"🔄 {self.pushButton_currencies_refresh.text()}")
        self.pushButton_update_chart.setText(f"🔄 {self.pushButton_update_chart.text()}")
        self.pushButton_pie_chart.setText(f"🥧 {self.pushButton_pie_chart.text()}")
        self.pushButton_balance_chart.setText(f"📊 {self.pushButton_balance_chart.text()}")
        self.pushButton_chart_last_month.setText(f"📅 {self.pushButton_chart_last_month.text()}")
        self.pushButton_chart_last_year.setText(f"📅 {self.pushButton_chart_last_year.text()}")
        self.pushButton_chart_all_time.setText(f"📅 {self.pushButton_chart_all_time.text()}")
        self.pushButton_generate_report.setText(f"📋 {self.pushButton_generate_report.text()}")

        # Configure splitter proportions
        self.splitter.setStretchFactor(0, 0)  # frame with fixed size
        self.splitter.setStretchFactor(1, 1)  # listView gets less space
        self.splitter.setStretchFactor(2, 3)  # tableView gets more space

    def _setup_window_size_and_position(self) -> None:
        """Set window size and position based on screen resolution."""
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Determine window size and position based on screen characteristics
        aspect_ratio = screen_width / screen_height
        is_standard_aspect = aspect_ratio <= 2.0

        if is_standard_aspect and screen_width >= 1920:
            # For standard aspect ratios with width >= 1920, maximize window
            self.showMaximized()
        else:
            title_bar_height = 30
            windows_task_bar_height = 48
            # For other cases, use fixed width and full height minus title bar
            window_width = 1920
            window_height = screen_height - title_bar_height - windows_task_bar_height
            # Position window on screen
            screen_center = screen_geometry.center()
            self.setGeometry(
                screen_center.x() - window_width // 2,
                title_bar_height,
                window_width,
                window_height,
            )

    def _update_comboboxes(self) -> None:
        """Refresh comboboxes with current data."""
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update categories list
            categories = self.db_manager.get_items("categories", "name", order_by="name")
            if self.categories_list_model is not None:
                self.categories_list_model.clear()
                for category in categories:
                    item = QStandardItem(category)
                    self.categories_list_model.appendRow(item)

            # Update transaction form comboboxes
            self.comboBox_category.clear()
            self.comboBox_category.addItems(categories)

            currencies = self.db_manager.get_currencies_list()
            self.comboBox_currency.clear()
            self.comboBox_currency.addItems(currencies)

            # Update account form currency combobox
            self.comboBox_account_currency.clear()
            self.comboBox_account_currency.addItems(currencies)

            # Update chart category combobox
            self.comboBox_chart_category.clear()
            self.comboBox_chart_category.addItem("")  # All categories
            self.comboBox_chart_category.addItems(categories)

        except Exception as e:
            print(f"Error updating comboboxes: {e}")

    def _validate_database_connection(self) -> bool:
        """Validate that database connection is available and open.

        Returns:

        - `bool`: True if database connection is valid, False otherwise.

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

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Initialize core attributes
        self.db_manager: database_manager.DatabaseManager | None = None

        # Categories list model
        self.categories_list_model: QStandardItemModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "transactions": None,
            "categories": None,
            "accounts": None,
            "currencies": None,
            "reports": None,
        }

        # Chart configuration
        self.max_count_points_in_charts = 40

        # Table configuration mapping
        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "transactions": (
                self.tableView_transactions,
                "transactions",
                ["ID", "Type", "Amount", "Currency", "Category", "Description", "Date"],
            ),
            "categories": (
                self.tableView_categories,
                "categories",
                ["ID", "Name", "Type"],
            ),
            "accounts": (
                self.tableView_accounts,
                "accounts",
                ["ID", "Name", "Currency", "Balance", "Liquid", "Cash"],
            ),
            "currencies": (
                self.tableView_currencies,
                "currencies",
                ["ID", "Code", "Name", "Symbol"],
            ),
            "reports": (
                self.tableView_reports,
                "reports",
                ["Category", "Type", "Amount", "Currency"],
            ),
        }

        # Initialize application
        self._init_database()
        self._connect_signals()
        self._init_filter_controls()
        self._init_categories_list()
        self._init_chart_controls()
        self.update_all()

        # Set window size and position
        self._setup_window_size_and_position()

        # Show window after initialization
        QTimer.singleShot(200, self.show)
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

        category = self.comboBox_filter_category.currentText()
        transaction_type = self.comboBox_filter_type.currentText()
        currency = self.comboBox_filter_currency.currentText()
        use_date_filter = self.checkBox_use_date_filter.isChecked()
        date_from = self.dateEdit_filter_from.date().toString("yyyy-MM-dd") if use_date_filter else None
        date_to = self.dateEdit_filter_to.date().toString("yyyy-MM-dd") if use_date_filter else None

        # Use database manager method
        rows = self.db_manager.get_filtered_transactions(
            category=category if category else None,
            transaction_type=transaction_type if transaction_type else None,
            currency=currency if currency else None,
            date_from=date_from,
            date_to=date_to,
        )

        self.models["transactions"] = self._create_table_model(rows, self.table_config["transactions"][2])
        self.tableView_transactions.setModel(self.models["transactions"])
        self.tableView_transactions.resizeColumnsToContents()
```

</details>

### ⚙️ Method `clear_filter`

```python
def clear_filter(self) -> None
```

Reset all transaction-table filters.

<details>
<summary>Code:</summary>

```python
def clear_filter(self) -> None:
        self.comboBox_filter_category.setCurrentIndex(0)
        self.comboBox_filter_type.setCurrentIndex(0)
        self.comboBox_filter_currency.setCurrentIndex(0)
        self.checkBox_use_date_filter.setChecked(False)

        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        self.show_tables()
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
            elif table_name == "categories":
                success = self.db_manager.delete_category(record_id)
            elif table_name == "accounts":
                success = self.db_manager.delete_account(record_id)
            elif table_name == "currencies":
                success = self.db_manager.delete_currency(record_id)
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            self.update_all()
            self.update_daily_balance()
        else:
            QMessageBox.warning(self, "Error", f"Deletion failed in {table_name}")
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
                self.tableView_reports,
            ]

            for table_view in table_views:
                if focused_widget == table_view:
                    self._copy_table_selection_to_clipboard(table_view)
                    return

            # If focused widget is a child of a table view (like the viewport)
            for table_view in table_views:
                if focused_widget and table_view.isAncestorOf(focused_widget):
                    self._copy_table_selection_to_clipboard(table_view)
                    return

        # Call parent implementation for other key events
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `on_add_account`

```python
def on_add_account(self) -> None
```

Insert a new account using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_account(self) -> None:
        account_name = self.lineEdit_account_name.text().strip()
        currency_code = self.comboBox_account_currency.currentText()
        balance = self.doubleSpinBox_account_balance.value()
        is_liquid = self.checkBox_is_liquid.isChecked()
        is_cash = self.checkBox_is_cash.isChecked()

        if not account_name:
            QMessageBox.warning(self, "Error", "Enter account name")
            return

        if not currency_code:
            QMessageBox.warning(self, "Error", "Select currency")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            currency_id = self.db_manager.get_id("currencies", "code", currency_code)
            if currency_id is None:
                QMessageBox.warning(self, "Error", f"Currency '{currency_code}' not found")
                return

            if self.db_manager.add_account(account_name, currency_id, balance, is_liquid, is_cash):
                self.update_all()
                self.lineEdit_account_name.clear()
                self.doubleSpinBox_account_balance.setValue(0.0)
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

Insert a new category using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_category(self) -> None:
        category_name = self.lineEdit_category_name.text().strip()
        category_type = self.comboBox_category_type.currentText().lower()

        if not category_name:
            QMessageBox.warning(self, "Error", "Enter category name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.add_category(category_name, category_type):
                self.update_all()
                self.lineEdit_category_name.clear()
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

Insert a new currency using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_currency(self) -> None:
        currency_code = self.lineEdit_currency_code.text().strip().upper()
        currency_name = self.lineEdit_currency_name.text().strip()
        currency_symbol = self.lineEdit_currency_symbol.text().strip()

        if not currency_code:
            QMessageBox.warning(self, "Error", "Enter currency code")
            return

        if not currency_name:
            QMessageBox.warning(self, "Error", "Enter currency name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.add_currency(currency_code, currency_name, currency_symbol):
                self.update_all()
                self.lineEdit_currency_code.clear()
                self.lineEdit_currency_name.clear()
                self.lineEdit_currency_symbol.clear()
            else:
                QMessageBox.warning(self, "Error", "Failed to add currency")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add currency: {e}")
```

</details>

### ⚙️ Method `on_add_transaction`

```python
def on_add_transaction(self) -> None
```

Insert a new transaction using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_transaction(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get transaction type
            if self.radioButton_income.isChecked():
                transaction_type = "income"
            elif self.radioButton_expense.isChecked():
                transaction_type = "expense"
            elif self.radioButton_transfer.isChecked():
                transaction_type = "transfer"
            else:
                QMessageBox.warning(self, "Error", "Please select transaction type")
                return

            # Get amount
            amount = self.doubleSpinBox_amount.value()
            if amount <= 0:
                QMessageBox.warning(self, "Error", "Amount must be greater than 0")
                return

            # Get currency
            currency_code = self.comboBox_currency.currentText()
            if not currency_code:
                QMessageBox.warning(self, "Error", "Please select currency")
                return

            currency_id = self.db_manager.get_id("currencies", "code", currency_code)
            if currency_id is None:
                QMessageBox.warning(self, "Error", f"Currency '{currency_code}' not found")
                return

            # Get category
            category_name = self.comboBox_category.currentText()
            if not category_name:
                QMessageBox.warning(self, "Error", "Please select category")
                return

            category_id = self.db_manager.get_id("categories", "name", category_name)
            if category_id is None:
                QMessageBox.warning(self, "Error", f"Category '{category_name}' not found")
                return

            # Get description
            description = self.lineEdit_description.text().strip()

            # Get date
            date_str = self.dateEdit.date().toString("yyyy-MM-dd")

            # Use database manager method
            if self.db_manager.add_transaction(
                transaction_type, amount, currency_id, category_id, description, date_str
            ):
                # Apply date increment logic
                self._increment_date_widget(self.dateEdit)

                # Update UI
                self.show_tables()
                self._update_comboboxes()
                self.update_filter_comboboxes()
                self.update_daily_balance()
            else:
                QMessageBox.warning(self, "Error", "Failed to add transaction")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add transaction: {e}")
```

</details>

### ⚙️ Method `on_category_selection_changed`

```python
def on_category_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None
```

Handle category selection change in the list view.

<details>
<summary>Code:</summary>

```python
def on_category_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
        category = self._get_current_selected_category()
        if not category:
            return

        # Update category selection in transaction form
        index = self.comboBox_category.findText(category)
        if index >= 0:
            self.comboBox_category.setCurrentIndex(index)
```

</details>

### ⚙️ Method `on_export_csv`

```python
def on_export_csv(self) -> None
```

Save current `transactions` view to a CSV file (semicolon-separated).

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

Generate selected report type.

<details>
<summary>Code:</summary>

```python
def on_generate_report(self) -> None:
        report_type = self.comboBox_report_type.currentText()

        if not self._validate_database_connection():
            return

        if report_type == "Monthly Summary":
            self._generate_monthly_summary()
        elif report_type == "Category Analysis":
            self._generate_category_analysis()
        elif report_type == "Currency Analysis":
            self._generate_currency_analysis()
        elif report_type == "Account Balances":
            self._generate_account_balances()
        elif report_type == "Income vs Expenses":
            self._generate_income_vs_expenses()
```

</details>

### ⚙️ Method `on_show_balance_chart`

```python
def on_show_balance_chart(self) -> None
```

Show balance chart over time.

<details>
<summary>Code:</summary>

```python
def on_show_balance_chart(self) -> None:
        if not self._validate_database_connection():
            return

        # Get date range
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get all transactions in date range
        rows = self.db_manager.get_filtered_transactions(
            date_from=date_from,
            date_to=date_to,
        )

        if not rows:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found")
            return

        # Calculate running balance
        balance_data = self._calculate_running_balance(rows)

        if not balance_data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No balance data to display")
            return

        # Create chart configuration
        chart_config = {
            "title": "Account Balance Over Time",
            "xlabel": "Date",
            "ylabel": "Balance (₽)",
            "color": "green",
            "show_stats": True,
            "stats_unit": "₽",
        }

        self._create_chart(self.verticalLayout_charts_content, balance_data, chart_config)
```

</details>

### ⚙️ Method `on_show_pie_chart`

```python
def on_show_pie_chart(self) -> None
```

Show pie chart of expenses by category.

<details>
<summary>Code:</summary>

```python
def on_show_pie_chart(self) -> None:
        if not self._validate_database_connection():
            return

        # Get date range
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get expense data
        rows = self.db_manager.get_filtered_transactions(
            transaction_type="expense",
            date_from=date_from,
            date_to=date_to,
        )

        if not rows:
            self._show_no_data_label(self.verticalLayout_charts_content, "No expense data found")
            return

        # Group by category
        category_totals = {}
        for row in rows:
            category = row[4]  # Category name
            amount = float(row[2])  # Amount
            category_totals[category] = category_totals.get(category, 0) + amount

        # Create pie chart
        self._create_pie_chart(category_totals, "Expenses by Category")
```

</details>

### ⚙️ Method `on_tab_changed`

```python
def on_tab_changed(self, index: int) -> None
```

React to `QTabWidget` index change.

Args:

- `index` (`int`): The index of the newly selected tab.

<details>
<summary>Code:</summary>

```python
def on_tab_changed(self, index: int) -> None:
        if index == 0:  # Transactions tab
            self.update_filter_comboboxes()
            self.update_daily_balance()
        elif index == 1:  # Categories tab
            pass
        elif index == 2:  # Accounts tab
            pass
        elif index == 3:  # Currencies tab
            pass
        elif index == 4:  # Charts tab
            pass
        elif index == 5:  # Reports tab
            self.update_summary_labels()
```

</details>

### ⚙️ Method `on_update_chart`

```python
def on_update_chart(self) -> None
```

Update chart based on selected filters.

<details>
<summary>Code:</summary>

```python
def on_update_chart(self) -> None:
        if not self._validate_database_connection():
            return

        # Get chart parameters
        category = self.comboBox_chart_category.currentText()
        chart_type = self.comboBox_chart_type.currentText()
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get filtered data
        rows = self.db_manager.get_filtered_transactions(
            category=category if category else None,
            transaction_type=chart_type.lower() if chart_type != "All" else None,
            date_from=date_from,
            date_to=date_to,
        )

        if not rows:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found for the selected filters")
            return

        # Group data by period
        grouped_data = self._group_data_by_period(rows, period)

        if not grouped_data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data to display")
            return

        # Prepare chart data
        chart_data = list(grouped_data.items())

        # Create chart configuration
        chart_config = {
            "title": f"{chart_type} - {category if category else 'All Categories'} ({period})",
            "xlabel": "Date",
            "ylabel": "Amount",
            "color": "blue",
            "show_stats": True,
            "stats_unit": "₽",
        }

        self._create_chart(self.verticalLayout_charts_content, chart_data, chart_config)
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
```

</details>

### ⚙️ Method `set_today_date`

```python
def set_today_date(self) -> None
```

Set today's date in the date edit fields.

<details>
<summary>Code:</summary>

```python
def set_today_date(self) -> None:
        today_qdate = QDate.currentDate()
        self.dateEdit.setDate(today_qdate)
```

</details>

### ⚙️ Method `set_yesterday_date`

```python
def set_yesterday_date(self) -> None
```

Set yesterday's date in the main date edit field.

<details>
<summary>Code:</summary>

```python
def set_yesterday_date(self) -> None:
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit.setDate(yesterday)
```

</details>

### ⚙️ Method `show_tables`

```python
def show_tables(self) -> None
```

Populate all QTableViews using database manager methods.

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
            # Refresh all tables
            self._refresh_table("transactions", self.db_manager.get_all_transactions)
            self._refresh_table("categories", self.db_manager.get_all_categories)
            self._refresh_table("accounts", self.db_manager.get_all_accounts)
            self._refresh_table("currencies", self.db_manager.get_all_currencies)

            # Connect selection change signals after models are set
            self._connect_table_selection_signals()

            # Connect auto-save signals after all models are created
            self._connect_table_auto_save_signals()

        except Exception as e:
            print(f"Error showing tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load tables: {e}")
```

</details>

### ⚙️ Method `update_all`

```python
def update_all(self) -> None
```

Refresh tables, list view and dates.

<details>
<summary>Code:</summary>

```python
def update_all(self) -> None:
        if not self._validate_database_connection():
            print("Database connection not available for update_all")
            return

        self.show_tables()
        self._update_comboboxes()
        self.set_today_date()
        self.update_filter_comboboxes()
        self.update_daily_balance()

        # Clear forms
        self.lineEdit_category_name.clear()
        self.lineEdit_account_name.clear()
        self.doubleSpinBox_account_balance.setValue(0.0)
        self.lineEdit_currency_code.clear()
        self.lineEdit_currency_name.clear()
        self.lineEdit_currency_symbol.clear()
```

</details>

### ⚙️ Method `update_daily_balance`

```python
def update_daily_balance(self) -> None
```

Update the daily balance display.

<details>
<summary>Code:</summary>

```python
def update_daily_balance(self) -> None:
        if not self._validate_database_connection():
            self.label_daily_balance.setText("0.00₽")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            today = QDate.currentDate().toString("yyyy-MM-dd")
            balance = self.db_manager.get_daily_balance(today)

            # Format balance with appropriate color
            if balance > 0:
                color = "green"
                sign = "+"
            elif balance < 0:
                color = "red"
                sign = ""
            else:
                color = "black"
                sign = ""

            self.label_daily_balance.setText(f'<span style="color: {color};">{sign}{balance:.2f}₽</span>')
        except Exception as e:
            print(f"Error updating daily balance: {e}")
            self.label_daily_balance.setText("0.00₽")
```

</details>

### ⚙️ Method `update_filter_comboboxes`

```python
def update_filter_comboboxes(self) -> None
```

Refresh filter combo-boxes.

<details>
<summary>Code:</summary>

```python
def update_filter_comboboxes(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update category filter
            current_category = self.comboBox_filter_category.currentText()
            self.comboBox_filter_category.blockSignals(True)  # noqa: FBT003
            self.comboBox_filter_category.clear()
            self.comboBox_filter_category.addItem("")
            categories = self.db_manager.get_items("categories", "name", order_by="name")
            self.comboBox_filter_category.addItems(categories)
            if current_category:
                idx = self.comboBox_filter_category.findText(current_category)
                if idx >= 0:
                    self.comboBox_filter_category.setCurrentIndex(idx)
            self.comboBox_filter_category.blockSignals(False)  # noqa: FBT003

            # Update type filter
            current_type = self.comboBox_filter_type.currentText()
            self.comboBox_filter_type.blockSignals(True)  # noqa: FBT003
            self.comboBox_filter_type.clear()
            self.comboBox_filter_type.addItems(["", "All", "Income", "Expense", "Transfer"])
            if current_type:
                idx = self.comboBox_filter_type.findText(current_type)
                if idx >= 0:
                    self.comboBox_filter_type.setCurrentIndex(idx)
            self.comboBox_filter_type.blockSignals(False)  # noqa: FBT003

            # Update currency filter
            current_currency = self.comboBox_filter_currency.currentText()
            self.comboBox_filter_currency.blockSignals(True)  # noqa: FBT003
            self.comboBox_filter_currency.clear()
            self.comboBox_filter_currency.addItem("")
            currencies = self.db_manager.get_currencies_list()
            self.comboBox_filter_currency.addItems(currencies)
            if current_currency:
                idx = self.comboBox_filter_currency.findText(current_currency)
                if idx >= 0:
                    self.comboBox_filter_currency.setCurrentIndex(idx)
            self.comboBox_filter_currency.blockSignals(False)  # noqa: FBT003

        except Exception as e:
            print(f"Error updating filter comboboxes: {e}")
```

</details>

### ⚙️ Method `update_summary_labels`

```python
def update_summary_labels(self) -> None
```

Update summary labels in reports tab.

<details>
<summary>Code:</summary>

```python
def update_summary_labels(self) -> None:
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get all transactions
            rows = self.db_manager.get_all_transactions()

            total_income = 0.0
            total_expenses = 0.0

            for row in rows:
                transaction_type = row[1]  # Type
                amount = float(row[2])  # Amount

                if transaction_type == "income":
                    total_income += amount
                elif transaction_type == "expense":
                    total_expenses += amount

            net_balance = total_income - total_expenses

            # Update labels
            self.label_total_income.setText(f"Total Income: {total_income:.2f}₽")
            self.label_total_expenses.setText(f"Total Expenses: {total_expenses:.2f}₽")

            # Set net balance color
            if net_balance > 0:
                color = "green"
            elif net_balance < 0:
                color = "red"
            else:
                color = "black"

            self.label_net_balance.setText(f'<span style="color: {color};">Net Balance: {net_balance:.2f}₽</span>')

            # Get total accounts balance
            account_rows = self.db_manager.get_all_accounts()
            total_accounts = sum(float(row[3]) for row in account_rows)  # Balance column
            self.label_total_accounts.setText(f"Total in Accounts: {total_accounts:.2f}₽")

        except Exception as e:
            print(f"Error updating summary labels: {e}")
```

</details>

### ⚙️ Method `_calculate_running_balance`

```python
def _calculate_running_balance(self, rows: list) -> list
```

Calculate running balance from transaction data.

Args:

- `rows` (`list`): List of transaction rows.

Returns:

- `list`: List of (date, balance) tuples.

<details>
<summary>Code:</summary>

```python
def _calculate_running_balance(self, rows: list) -> list:
        # Sort by date
        sorted_rows = sorted(rows, key=lambda x: x[7])  # Date is at index 7

        balance_data = []
        running_balance = 0.0

        for row in sorted_rows:
            transaction_type = row[1]  # Type
            amount = float(row[2])  # Amount
            date_str = row[7]  # Date

            if transaction_type == "income":
                running_balance += amount
            elif transaction_type == "expense":
                running_balance -= amount

            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                balance_data.append((date_obj, running_balance))
            except ValueError:
                continue

        return balance_data
```

</details>

### ⚙️ Method `_connect_signals`

```python
def _connect_signals(self) -> None
```

Wire Qt widgets to their Python slots.

<details>
<summary>Code:</summary>

```python
def _connect_signals(self) -> None:
        self.pushButton_add.clicked.connect(self.on_add_transaction)
        self.pushButton_yesterday.clicked.connect(self.set_yesterday_date)

        # Connect delete and refresh buttons for all tables
        tables_with_controls = {"transactions", "categories", "accounts", "currencies"}
        for table_name in tables_with_controls:
            # Delete buttons
            if table_name == "transactions":
                delete_btn_name = "pushButton_delete"
                refresh_btn_name = "pushButton_refresh"
            else:
                delete_btn_name = f"pushButton_{table_name}_delete"
                refresh_btn_name = f"pushButton_{table_name}_refresh"

            delete_button = getattr(self, delete_btn_name)
            delete_button.clicked.connect(partial(self.delete_record, table_name))

            refresh_button = getattr(self, refresh_btn_name)
            refresh_button.clicked.connect(self.update_all)

        # Add buttons
        self.pushButton_category_add.clicked.connect(self.on_add_category)
        self.pushButton_account_add.clicked.connect(self.on_add_account)
        self.pushButton_currency_add.clicked.connect(self.on_add_currency)

        # Export
        # self.pushButton_export_csv.clicked.connect(self.on_export_csv)  # Button not available in UI

        # Tab change
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Filter signals
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

        # Chart signals
        self.pushButton_update_chart.clicked.connect(self.on_update_chart)
        self.pushButton_pie_chart.clicked.connect(self.on_show_pie_chart)
        self.pushButton_balance_chart.clicked.connect(self.on_show_balance_chart)
        self.pushButton_chart_last_month.clicked.connect(self.set_chart_last_month)
        self.pushButton_chart_last_year.clicked.connect(self.set_chart_last_year)
        self.pushButton_chart_all_time.clicked.connect(self.set_chart_all_time)

        # Reports
        self.pushButton_generate_report.clicked.connect(self.on_generate_report)
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

### ⚙️ Method `_connect_table_selection_signals`

```python
def _connect_table_selection_signals(self) -> None
```

Connect selection change signals for all tables.

<details>
<summary>Code:</summary>

```python
def _connect_table_selection_signals(self) -> None:
        # Connect categories list selection
        selection_model = self.listView_categories.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_category_selection_changed)
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

### ⚙️ Method `_create_pie_chart`

```python
def _create_pie_chart(self, data: dict, title: str) -> None
```

Create a pie chart with the given data.

Args:

- `data` (`dict`): Dictionary with labels as keys and values as values.
- `title` (`str`): Chart title.

<details>
<summary>Code:</summary>

```python
def _create_pie_chart(self, data: dict, title: str) -> None:
        # Clear existing chart
        self._clear_layout(self.verticalLayout_charts_content)

        if not data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data to display")
            return

        # Create matplotlib figure
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        fig = Figure(figsize=(10, 8), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Create pie chart
        labels = list(data.keys())
        values = list(data.values())

        ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.set_title(title, fontsize=14, fontweight="bold")

        fig.tight_layout()
        self.verticalLayout_charts_content.addWidget(canvas)
        canvas.draw()
```

</details>

### ⚙️ Method `_create_table_model`

```python
def _create_table_model(self, data: list[list[str]], headers: list[str], id_column: int = 0) -> QSortFilterProxyModel
```

Return a proxy model filled with `data`.

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

        # list-view
        self.listView_categories.setModel(None)
        if self.categories_list_model is not None:
            self.categories_list_model.deleteLater()
        self.categories_list_model = None
```

</details>

### ⚙️ Method `_generate_account_balances`

```python
def _generate_account_balances(self) -> None
```

Generate account balances report.

<details>
<summary>Code:</summary>

```python
def _generate_account_balances(self) -> None:
        if self.db_manager is None:
            return

        try:
            rows = self.db_manager.get_all_accounts()

            # Transform data for display
            report_data = []
            for row in rows:
                account_name = row[1]  # Name
                currency = row[2]  # Currency
                balance = row[3]  # Balance
                liquid = "Yes" if row[4] else "No"  # Liquid
                cash = "Yes" if row[5] else "No"  # Cash

                report_data.append([account_name, currency, f"{balance:.2f}", liquid, cash])

            # Update table
            headers = ["Account", "Currency", "Balance", "Liquid", "Cash"]
            self.models["reports"] = self._create_table_model(report_data, headers, id_column=-1)
            self.tableView_reports.setModel(self.models["reports"])
            self.tableView_reports.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate account balances report: {e}")
```

</details>

### ⚙️ Method `_generate_category_analysis`

```python
def _generate_category_analysis(self) -> None
```

Generate category analysis report.

<details>
<summary>Code:</summary>

```python
def _generate_category_analysis(self) -> None:
        if self.db_manager is None:
            return

        try:
            rows = self.db_manager.get_all_transactions()

            # Group by category
            category_totals = {}
            for row in rows:
                category = row[4]  # Category
                transaction_type = row[1]  # Type
                amount = float(row[2])  # Amount

                if category not in category_totals:
                    category_totals[category] = {"income": 0.0, "expense": 0.0, "transfer": 0.0}

                category_totals[category][transaction_type] += amount

            # Transform data for display
            report_data = []
            for category, totals in category_totals.items():
                income = totals["income"]
                expense = totals["expense"]
                transfer = totals["transfer"]
                net = income - expense

                report_data.append([category, f"{income:.2f}", f"{expense:.2f}", f"{transfer:.2f}", f"{net:.2f}"])

            # Sort by net amount descending
            report_data.sort(key=lambda x: float(x[4]), reverse=True)

            # Update table
            headers = ["Category", "Income", "Expense", "Transfer", "Net"]
            self.models["reports"] = self._create_table_model(report_data, headers, id_column=-1)
            self.tableView_reports.setModel(self.models["reports"])
            self.tableView_reports.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate category analysis report: {e}")
```

</details>

### ⚙️ Method `_generate_currency_analysis`

```python
def _generate_currency_analysis(self) -> None
```

Generate currency analysis report.

<details>
<summary>Code:</summary>

```python
def _generate_currency_analysis(self) -> None:
        if self.db_manager is None:
            return

        try:
            rows = self.db_manager.get_all_transactions()

            # Group by currency
            currency_totals = {}
            for row in rows:
                currency = row[3]  # Currency symbol
                transaction_type = row[1]  # Type
                amount = float(row[2])  # Amount

                if currency not in currency_totals:
                    currency_totals[currency] = {"income": 0.0, "expense": 0.0, "transfer": 0.0}

                currency_totals[currency][transaction_type] += amount

            # Transform data for display
            report_data = []
            for currency, totals in currency_totals.items():
                income = totals["income"]
                expense = totals["expense"]
                transfer = totals["transfer"]
                net = income - expense

                report_data.append([currency, f"{income:.2f}", f"{expense:.2f}", f"{transfer:.2f}", f"{net:.2f}"])

            # Sort by net amount descending
            report_data.sort(key=lambda x: float(x[4]), reverse=True)

            # Update table
            headers = ["Currency", "Income", "Expense", "Transfer", "Net"]
            self.models["reports"] = self._create_table_model(report_data, headers, id_column=-1)
            self.tableView_reports.setModel(self.models["reports"])
            self.tableView_reports.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate currency analysis report: {e}")
```

</details>

### ⚙️ Method `_generate_income_vs_expenses`

```python
def _generate_income_vs_expenses(self) -> None
```

Generate income vs expenses report.

<details>
<summary>Code:</summary>

```python
def _generate_income_vs_expenses(self) -> None:
        if self.db_manager is None:
            return

        try:
            rows = self.db_manager.get_all_transactions()

            # Group by month
            monthly_totals = {}
            for row in rows:
                date_str = row[7]  # Date
                transaction_type = row[1]  # Type
                amount = float(row[2])  # Amount

                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    month_key = date_obj.strftime("%Y-%m")

                    if month_key not in monthly_totals:
                        monthly_totals[month_key] = {"income": 0.0, "expense": 0.0}

                    if transaction_type in ["income", "expense"]:
                        monthly_totals[month_key][transaction_type] += amount

                except ValueError:
                    continue

            # Transform data for display
            report_data = []
            for month, totals in sorted(monthly_totals.items(), reverse=True):
                income = totals["income"]
                expense = totals["expense"]
                net = income - expense

                report_data.append([month, f"{income:.2f}", f"{expense:.2f}", f"{net:.2f}"])

            # Update table
            headers = ["Month", "Income", "Expense", "Net"]
            self.models["reports"] = self._create_table_model(report_data, headers, id_column=-1)
            self.tableView_reports.setModel(self.models["reports"])
            self.tableView_reports.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate income vs expenses report: {e}")
```

</details>

### ⚙️ Method `_generate_monthly_summary`

```python
def _generate_monthly_summary(self) -> None
```

Generate monthly summary report.

<details>
<summary>Code:</summary>

```python
def _generate_monthly_summary(self) -> None:
        if self.db_manager is None:
            return

        try:
            rows = self.db_manager.get_all_transactions()

            # Group by month and category
            monthly_data = {}
            for row in rows:
                date_str = row[7]  # Date
                category = row[4]  # Category
                transaction_type = row[1]  # Type
                amount = float(row[2])  # Amount

                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    month_key = date_obj.strftime("%Y-%m")

                    if month_key not in monthly_data:
                        monthly_data[month_key] = {}

                    if category not in monthly_data[month_key]:
                        monthly_data[month_key][category] = {"income": 0.0, "expense": 0.0, "transfer": 0.0}

                    monthly_data[month_key][category][transaction_type] += amount

                except ValueError:
                    continue

            # Transform data for display
            report_data = []
            for month in sorted(monthly_data.keys(), reverse=True):
                for category, totals in monthly_data[month].items():
                    income = totals["income"]
                    expense = totals["expense"]
                    transfer = totals["transfer"]
                    net = income - expense

                    report_data.append(
                        [month, category, f"{income:.2f}", f"{expense:.2f}", f"{transfer:.2f}", f"{net:.2f}"]
                    )

            # Update table
            headers = ["Month", "Category", "Income", "Expense", "Transfer", "Net"]
            self.models["reports"] = self._create_table_model(report_data, headers, id_column=-1)
            self.tableView_reports.setModel(self.models["reports"])
            self.tableView_reports.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.warning(self, "Report Error", f"Failed to generate monthly summary report: {e}")
```

</details>

### ⚙️ Method `_get_current_selected_category`

```python
def _get_current_selected_category(self) -> str | None
```

Get the currently selected category from the list view.

Returns:

- `str | None`: The name of the selected category, or None if nothing is selected.

<details>
<summary>Code:</summary>

```python
def _get_current_selected_category(self) -> str | None:
        selection_model = self.listView_categories.selectionModel()
        if not selection_model or not self.categories_list_model:
            return None

        current_index = selection_model.currentIndex()
        if not current_index.isValid():
            return None

        item = self.categories_list_model.itemFromIndex(current_index)
        return item.text() if item else None
```

</details>

### ⚙️ Method `_group_data_by_period`

```python
def _group_data_by_period(self, rows: list, period: str) -> dict
```

Group data by the specified period (Days, Months, Years).

Args:

- `rows` (`list`): List of transaction rows.
- `period` (`str`): Grouping period (Days, Months, Years).

Returns:

- `dict`: Dictionary with datetime keys and aggregated values.

<details>
<summary>Code:</summary>

```python
def _group_data_by_period(self, rows: list, period: str) -> dict:
        from collections import defaultdict

        grouped = defaultdict(float)

        for row in rows:
            date_str = row[7]  # Date
            amount = float(row[2])  # Amount
            transaction_type = row[1]  # Type

            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue

            # Adjust amount based on transaction type
            if transaction_type == "expense":
                amount = -amount

            if period == "Days":
                key = date_obj
            elif period == "Months":
                key = date_obj.replace(day=1)
            elif period == "Years":
                key = date_obj.replace(month=1, day=1)
            else:
                key = date_obj

            grouped[key] += amount

        return dict(sorted(grouped.items()))
```

</details>

### ⚙️ Method `_init_categories_list`

```python
def _init_categories_list(self) -> None
```

Initialize the categories list view with a model and connect signals.

<details>
<summary>Code:</summary>

```python
def _init_categories_list(self) -> None:
        self.categories_list_model = QStandardItemModel()
        self.listView_categories.setModel(self.categories_list_model)

        # Disable editing for categories list
        self.listView_categories.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

        # Connect selection change signal after model is set
        selection_model = self.listView_categories.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_category_selection_changed)
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

Open the SQLite file from `config` (create from recover.sql if missing).

<details>
<summary>Code:</summary>

```python
def _init_database(self) -> None:
        filename = Path(config["sqlite_finance"])

        # Try to open existing database first
        if filename.exists():
            try:
                temp_db_manager = database_manager.DatabaseManager(str(filename))

                # Check if transactions table exists
                if temp_db_manager.table_exists("transactions"):
                    print(f"Database opened successfully: {filename}")
                    self.db_manager = temp_db_manager
                    return
                print(f"Database exists but transactions table is missing at {filename}")
                temp_db_manager.close()
            except Exception as e:
                print(f"Failed to open existing database: {e}")

        # Database doesn't exist or is missing required table - create from recover.sql
        app_dir = Path(__file__).parent
        recover_sql_path = app_dir / "recover.sql"

        if recover_sql_path.exists():
            print(f"Database not found or missing transactions table at {filename}")
            print(f"Attempting to create database from {recover_sql_path}")

            if database_manager.DatabaseManager.create_database_from_sql(str(filename), str(recover_sql_path)):
                print("Database created successfully from recover.sql")
            else:
                QMessageBox.warning(
                    self,
                    "Database Creation Failed",
                    f"Failed to create database from {recover_sql_path}\nPlease select an existing database file.",
                )
        else:
            QMessageBox.information(
                self,
                "Database Not Found",
                f"Database file not found: {filename}\n"
                f"recover.sql file not found: {recover_sql_path}\n"
                "Please select an existing database file.",
            )

        # If database still doesn't exist, ask user to select one
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

Prepare widgets on the `Filters` group box.

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
                row_id = model.verticalHeaderItem(row).text()
                self._auto_save_row(table_name, model, row, row_id)

        except Exception as e:
            QMessageBox.warning(self, "Auto-save Error", f"Failed to auto-save changes: {e!s}")
```

</details>

### ⚙️ Method `_setup_ui`

```python
def _setup_ui(self) -> None
```

Set up additional UI elements after basic initialization.

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
        self.pushButton_category_add.setText(f"➕ {self.pushButton_category_add.text()}")
        self.pushButton_categories_delete.setText(f"🗑️ {self.pushButton_categories_delete.text()}")
        self.pushButton_categories_refresh.setText(f"🔄 {self.pushButton_categories_refresh.text()}")
        self.pushButton_account_add.setText(f"➕ {self.pushButton_account_add.text()}")
        self.pushButton_accounts_delete.setText(f"🗑️ {self.pushButton_accounts_delete.text()}")
        self.pushButton_accounts_refresh.setText(f"🔄 {self.pushButton_accounts_refresh.text()}")
        self.pushButton_currency_add.setText(f"➕ {self.pushButton_currency_add.text()}")
        self.pushButton_currencies_delete.setText(f"🗑️ {self.pushButton_currencies_delete.text()}")
        self.pushButton_currencies_refresh.setText(f"🔄 {self.pushButton_currencies_refresh.text()}")
        self.pushButton_update_chart.setText(f"🔄 {self.pushButton_update_chart.text()}")
        self.pushButton_pie_chart.setText(f"🥧 {self.pushButton_pie_chart.text()}")
        self.pushButton_balance_chart.setText(f"📊 {self.pushButton_balance_chart.text()}")
        self.pushButton_chart_last_month.setText(f"📅 {self.pushButton_chart_last_month.text()}")
        self.pushButton_chart_last_year.setText(f"📅 {self.pushButton_chart_last_year.text()}")
        self.pushButton_chart_all_time.setText(f"📅 {self.pushButton_chart_all_time.text()}")
        self.pushButton_generate_report.setText(f"📋 {self.pushButton_generate_report.text()}")

        # Configure splitter proportions
        self.splitter.setStretchFactor(0, 0)  # frame with fixed size
        self.splitter.setStretchFactor(1, 1)  # listView gets less space
        self.splitter.setStretchFactor(2, 3)  # tableView gets more space
```

</details>

### ⚙️ Method `_setup_window_size_and_position`

```python
def _setup_window_size_and_position(self) -> None
```

Set window size and position based on screen resolution.

<details>
<summary>Code:</summary>

```python
def _setup_window_size_and_position(self) -> None:
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Determine window size and position based on screen characteristics
        aspect_ratio = screen_width / screen_height
        is_standard_aspect = aspect_ratio <= 2.0

        if is_standard_aspect and screen_width >= 1920:
            # For standard aspect ratios with width >= 1920, maximize window
            self.showMaximized()
        else:
            title_bar_height = 30
            windows_task_bar_height = 48
            # For other cases, use fixed width and full height minus title bar
            window_width = 1920
            window_height = screen_height - title_bar_height - windows_task_bar_height
            # Position window on screen
            screen_center = screen_geometry.center()
            self.setGeometry(
                screen_center.x() - window_width // 2,
                title_bar_height,
                window_width,
                window_height,
            )
```

</details>

### ⚙️ Method `_update_comboboxes`

```python
def _update_comboboxes(self) -> None
```

Refresh comboboxes with current data.

<details>
<summary>Code:</summary>

```python
def _update_comboboxes(self) -> None:
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update categories list
            categories = self.db_manager.get_items("categories", "name", order_by="name")
            if self.categories_list_model is not None:
                self.categories_list_model.clear()
                for category in categories:
                    item = QStandardItem(category)
                    self.categories_list_model.appendRow(item)

            # Update transaction form comboboxes
            self.comboBox_category.clear()
            self.comboBox_category.addItems(categories)

            currencies = self.db_manager.get_currencies_list()
            self.comboBox_currency.clear()
            self.comboBox_currency.addItems(currencies)

            # Update account form currency combobox
            self.comboBox_account_currency.clear()
            self.comboBox_account_currency.addItems(currencies)

            # Update chart category combobox
            self.comboBox_chart_category.clear()
            self.comboBox_chart_category.addItem("")  # All categories
            self.comboBox_chart_category.addItems(categories)

        except Exception as e:
            print(f"Error updating comboboxes: {e}")
```

</details>

### ⚙️ Method `_validate_database_connection`

```python
def _validate_database_connection(self) -> bool
```

Validate that database connection is available and open.

Returns:

- `bool`: True if database connection is valid, False otherwise.

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
