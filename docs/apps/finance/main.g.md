---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MainWindow`](#️-class-mainwindow)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `apply_filter`](#️-method-apply_filter)
  - [⚙️ Method `clear_filter`](#️-method-clear_filter)
  - [⚙️ Method `closeEvent`](#️-method-closeevent)
  - [⚙️ Method `delete_record`](#️-method-delete_record)
  - [⚙️ Method `eventFilter`](#️-method-eventfilter)
  - [⚙️ Method `keyPressEvent`](#️-method-keypressevent)
  - [⚙️ Method `on_add_account`](#️-method-on_add_account)
  - [⚙️ Method `on_add_as_text_with_ai`](#️-method-on_add_as_text_with_ai)
  - [⚙️ Method `on_add_category`](#️-method-on_add_category)
  - [⚙️ Method `on_add_currency`](#️-method-on_add_currency)
  - [⚙️ Method `on_add_exchange`](#️-method-on_add_exchange)
  - [⚙️ Method `on_add_transaction`](#️-method-on_add_transaction)
  - [⚙️ Method `on_calculate_exchange`](#️-method-on_calculate_exchange)
  - [⚙️ Method `on_calculate_fee`](#️-method-on_calculate_fee)
  - [⚙️ Method `on_category_selection_changed`](#️-method-on_category_selection_changed)
  - [⚙️ Method `on_clear_description`](#️-method-on_clear_description)
  - [⚙️ Method `on_copy_categories_as_text`](#️-method-on_copy_categories_as_text)
  - [⚙️ Method `on_exchange_item_update_button_clicked`](#️-method-on_exchange_item_update_button_clicked)
  - [⚙️ Method `on_exchange_item_update_changed`](#️-method-on_exchange_item_update_changed)
  - [⚙️ Method `on_export_csv`](#️-method-on_export_csv)
  - [⚙️ Method `on_generate_report`](#️-method-on_generate_report)
  - [⚙️ Method `on_select_only_expense_chart_categories`](#️-method-on_select_only_expense_chart_categories)
  - [⚙️ Method `on_select_only_income_chart_categories`](#️-method-on_select_only_income_chart_categories)
  - [⚙️ Method `on_set_default_currency`](#️-method-on_set_default_currency)
  - [⚙️ Method `on_show_all_records_clicked`](#️-method-on_show_all_records_clicked)
  - [⚙️ Method `on_tab_changed`](#️-method-on_tab_changed)
  - [⚙️ Method `on_yesterday`](#️-method-on_yesterday)
  - [⚙️ Method `on_yesterday_exchange`](#️-method-on_yesterday_exchange)
  - [⚙️ Method `set_chart_all_time`](#️-method-set_chart_all_time)
  - [⚙️ Method `set_chart_last_month`](#️-method-set_chart_last_month)
  - [⚙️ Method `set_chart_last_year`](#️-method-set_chart_last_year)
  - [⚙️ Method `set_today_date`](#️-method-set_today_date)
  - [⚙️ Method `show_tables`](#️-method-show_tables)
  - [⚙️ Method `update_all`](#️-method-update_all)
  - [⚙️ Method `update_filter_comboboxes`](#️-method-update_filter_comboboxes)
  - [⚙️ Method `update_summary_labels`](#️-method-update_summary_labels)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow, window.Ui_MainWindow, AppWindowMixin, TableOperations, DateOperations, ChartOperations, AutoSaveOperations, ValidationOperations, ExchangeRatesOperations)
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
    AppWindowMixin,
    TableOperations,
    DateOperations,
    ChartOperations,
    AutoSaveOperations,
    ValidationOperations,
    ExchangeRatesOperations,
):

    _SAFE_TABLES: frozenset[str] = frozenset(
        {"transactions", "categories", "accounts", "currencies", "currency_exchanges", "exchange_rates"},
    )
    _NO_CATEGORY_LABEL: str = "No selected category"

    def __init__(self, *, hide_on_close: bool = False) -> None:  # noqa: ARG002
        """Initialize main window for finance tracking application."""
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setupUi(self)
        self._setup_ui()
        self.setWindowIcon(QIcon(":/assets/logo.svg"))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Initialize core attributes
        self._is_closing = False
        self.db_manager: database_manager.DatabaseManager | None = None
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        self._auto_save_handlers: dict[str, Any] = {}
        self._auto_save_source_models: dict[str, QObject | None] = {}
        self._transaction_selection_selection_model: QItemSelectionModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "transactions": None,
            "categories": None,
            "accounts": None,
            "currencies": None,
            "currency_exchanges": None,
            "exchange_rates": None,
        }

        # Delegates for transactions table
        self.description_delegate: DescriptionDelegate | None = None
        self.category_delegate: CategoryComboBoxDelegate | None = None
        self.currency_delegate: CurrencyComboBoxDelegate | None = None
        self.date_delegate: DateDelegate | None = None
        self.tag_delegate: TagDelegate | None = None

        # Dialog state flags
        self._exchange_dialog_open: bool = False
        self._bothub_state = BothubRequestState()

        # Generate pastel colors for date-based coloring
        self.date_colors: list[QColor] = generate_pastel_qcolors(50)

        # Initialize mouse button tracking
        self._right_click_in_progress: bool = False

        # Track whether account double-click handler is connected
        self._account_double_click_connected: bool = False

        # Toggle for showing all records vs last self.count_transactions_to_show
        finance_cfg: dict[str, Any] = self._app_config.get("finance") or {}
        self.count_transactions_to_show: int = finance_cfg.get("transactions_initial_count", 1000)
        self.transactions_load_more_count: int = finance_cfg.get("transactions_load_more_count", 500)
        self.count_exchange_rates_to_show: int = finance_cfg.get("exchange_rates_initial_count", 1000)
        self.exchange_rates_load_more_count: int = finance_cfg.get("exchange_rates_load_more_count", 500)
        self.description_autocomplete_limit: int = finance_cfg.get("description_autocomplete_limit", 1000)
        self.show_all_transactions: bool = False

        # Transactions table pagination state
        self._transactions_pagination = ScrollPagination()
        self._transactions_dates_with_totals: set[str] = set()
        self._transactions_date_color_map: dict[str, int] = {}
        self._transactions_color_index: int = 0

        # Exchange rates table pagination state
        self._exchange_rates_pagination = ScrollPagination()
        self._exchange_rates_filter_params: dict[str, Any] | None = None

        # Lazy loading flags
        self.exchange_rates_loaded: bool = False

        # Exchange rates initialization flag
        self._exchange_rates_initialized: bool = False
        self._exchange_rates_updating: bool = False

        # Reports-tab summary can be expensive to compute; refresh lazily.
        self._summary_dirty: bool = True

        # Charts tab: auto-draw only on first visit.
        self._charts_initialized: bool = False
        self._chart_build_toast: toast_countdown_notification.ToastCountdownNotification | None = None
        self._report_build_toast: toast_countdown_notification.ToastCountdownNotification | None = None
        self._compare_last_years_start_month: int = 1
        self._compare_last_years_start_day: int = 1

        # Dialog state flags
        self._account_edit_dialog_open: bool = False

        # Matplotlib object references
        self._current_exchange_rate_fig: Figure | None = None
        self._current_exchange_rate_canvas: FigureCanvas | None = None

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
                [
                    "From",
                    "To",
                    "Amount From",
                    "Amount To",
                    "Rate",
                    "Fee",
                    "Date",
                    "Description",
                    "Loss",
                    "Today's Loss",
                ],
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

        self._load_transactions_page(reset=True)

    def clear_filter(self) -> None:
        """Reset all transaction filters."""
        self.radioButton_filter_type_all.setChecked(True)  # All
        self.comboBox_filter_category.setCurrentIndex(0)
        self.comboBox_filter_currency.setCurrentIndex(0)
        self.lineEdit_filter_description.clear()
        self.checkBox_use_date_filter.setChecked(False)

        current_date: QDate = QDateTime.currentDateTime().date()
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
        self._is_closing = True

        # Stop any running worker threads
        if hasattr(self, "exchange_rate_worker") and self.exchange_rate_worker.isRunning():
            self.exchange_rate_worker.stop()
            self.exchange_rate_worker.wait(3000)  # Wait up to 3 seconds

        # Stop checker thread if running
        if hasattr(self, "exchange_rate_checker") and self.exchange_rate_checker.isRunning():
            self.exchange_rate_checker.stop()
            self.exchange_rate_checker.wait(3000)  # Wait up to 3 seconds

        # Stop startup threads if running
        if hasattr(self, "startup_exchange_rate_worker") and self.startup_exchange_rate_worker.isRunning():
            self.startup_exchange_rate_worker.stop()
            self.startup_exchange_rate_worker.wait(3000)  # Wait up to 3 seconds

        if hasattr(self, "startup_exchange_rate_checker") and self.startup_exchange_rate_checker.isRunning():
            self.startup_exchange_rate_checker.stop()
            self.startup_exchange_rate_checker.wait(3000)  # Wait up to 3 seconds

        report_worker = getattr(self, "_report_build_worker", None)
        if report_worker is not None and report_worker.isRunning():
            report_worker.wait(3000)

        self._close_report_build_toast()

        # Close progress dialogs if open
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        if hasattr(self, "check_progress_dialog"):
            self.check_progress_dialog.close()

        if hasattr(self, "startup_progress_dialog"):
            self.startup_progress_dialog.close()

        # Dispose Models
        self._dispose_models()

        # Close DB
        if self.db_manager:
            self.db_manager.close()
            self.db_manager = None

        super().closeEvent(event)

    @requires_database()
    def delete_record(self, table_name: str) -> None:
        """Delete selected row(s) from table using database manager methods.

        For `transactions`, deletes every selected row; other tables delete one row.

        Args:

        - `table_name` (`str`): Name of the table to delete from. Must be in `_SAFE_TABLES`.

        Raises:

        - `ValueError`: If table_name is not in `_SAFE_TABLES`.

        """
        if table_name not in self._SAFE_TABLES:
            error_message = f"Illegal table name: {table_name}"
            raise ValueError(error_message)

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Use appropriate database manager method
        success: bool = False
        try:
            if table_name == "transactions":
                record_ids: list[int] = self._get_selected_row_ids(table_name)
                if not record_ids:
                    message_box.warning(self, "Error", "Select a record to delete")
                    return
                deleted_any = False
                for rid in record_ids:
                    if self.db_manager.delete_transaction(rid):
                        deleted_any = True
                    else:
                        message_box.warning(self, "Error", f"Failed to delete transaction {rid}")
                if deleted_any:
                    self._mark_transactions_changed()
                success = deleted_any
            else:
                record_id: int | None = self._get_selected_row_id(table_name)
                if record_id is None:
                    message_box.warning(self, "Error", "Select a record to delete")
                    return
                if table_name == "categories":
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
            message_box.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            # Save current column widths before update for exchange table
            column_widths: list[int] | None = None
            if table_name == "currency_exchanges":
                column_widths = self._save_table_column_widths(self.tableView_exchange)

            self.update_all()

            # Restore column widths after update for exchange table
            if table_name == "currency_exchanges" and column_widths:
                self._restore_table_column_widths(self.tableView_exchange, column_widths)

            self.update_summary_labels()
        else:
            message_box.warning(self, "Error", f"Deletion failed in {table_name}")

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Event filter for handling mouse and key events.

        Args:

        - `obj` (`QObject`): The object being filtered.
        - `event` (`QEvent`): The event being filtered.

        Returns:

        - `bool`: True if event should be filtered, False otherwise.

        """
        # Track right mouse button on the table's viewport to suppress data copy on right-click
        if obj == self.tableView_transactions.viewport():
            if event.type() == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent):
                if event.button() == Qt.MouseButton.RightButton:
                    self._right_click_in_progress = True
                else:
                    self._right_click_in_progress = False

            elif (
                event.type() == QEvent.Type.MouseButtonRelease
                and isinstance(event, QMouseEvent)
                and event.button() == Qt.MouseButton.RightButton
            ):
                # Reset the flag shortly after release to allow context menu to process
                QTimer.singleShot(100, lambda: setattr(self, "_right_click_in_progress", False))

        if (
            obj == self.label_category_now
            and event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._show_category_label_context_menu(event.position().toPoint())
            return True

        # Handle Enter key to add transaction quickly
        if (
            (
                (obj == self.doubleSpinBox_amount and event.type() == QEvent.Type.KeyPress)
                or (obj == self.dateEdit and event.type() == QEvent.Type.KeyPress)
                or (obj == self.lineEdit_tag and event.type() == QEvent.Type.KeyPress)
                or (obj == self.lineEdit_description and event.type() == QEvent.Type.KeyPress)
                or (obj == self.pushButton_add and event.type() == QEvent.Type.KeyPress)
            )
            and isinstance(event, QKeyEvent)
            and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
        ):
            self.on_add_transaction()
            return True

        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle key press events for the main window.

        Args:

        - `event` (`QKeyEvent`): The key press event.

        """
        if self._handle_ctrl_c_for_tables(
            event,
            [
                self.tableView_transactions,
                self.tableView_categories,
                self.tableView_accounts,
                self.tableView_currencies,
                self.tableView_exchange,
                self.tableView_exchange_rates,
                self.tableView_reports,
            ],
        ):
            return

        super().keyPressEvent(event)

    @requires_database()
    def on_add_account(self) -> None:
        """Add a new account using database manager."""

        def get_and_validate() -> tuple[str | None, Any]:
            name = self.lineEdit_account_name.text().strip()
            balance = self.doubleSpinBox_account_balance.value()
            currency_code = self.comboBox_account_currency.currentText()
            is_liquid = self.checkBox_is_liquid.isChecked()
            is_cash = self.checkBox_is_cash.isChecked()
            if not name:
                return ("Enter account name", None)
            if not currency_code:
                return ("Select a currency", None)
            if self.db_manager is None:
                return ("Database not initialized", None)
            currency_info = self.db_manager.get_currency_by_code(currency_code)
            if not currency_info:
                return (f"Currency '{currency_code}' not found", None)
            return (None, (name, balance, currency_info[0], is_liquid, is_cash))

        def add_db(data: Any) -> bool:
            name, balance, currency_id, is_liquid, is_cash = data
            return bool(
                self.db_manager
                and self.db_manager.add_account(name, balance, currency_id, is_liquid=is_liquid, is_cash=is_cash)
            )

        def on_success(_data: Any) -> None:
            self.update_all()
            self._clear_account_form()

        self._add_record("account", get_and_validate, add_db, on_success)

    @requires_database()
    def on_add_as_text_with_ai(self) -> None:
        """Collect text/image, call BotHub, then open purchase text dialog with AI result."""
        bothub_cfg = self._app_config.get("bothub") or {}
        max_image_side = int(bothub_cfg.get("max_image_side", 1600))
        source_dialog = AiSourceDialog(self, max_image_side=max_image_side)
        source_result = source_dialog.exec()
        if source_result == QDialog.DialogCode.Rejected:
            return
        if source_result == AiSourceDialog.SKIP_MANUAL:
            self._open_text_input_dialog(self.dateEdit.date())
            return

        raw_text = source_dialog.get_raw_text()
        image_data = source_dialog.get_image_bytes_and_mime()

        try:
            prompt_text = build_prompt(self._app_config, "finance_purchases_to_tsv", {"RAW_DATA": raw_text})
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            self._open_text_input_dialog(
                self.dateEdit.date(),
                initial_text=response_text,
                focus_text_on_show=False,
            )

        run_bothub_request(
            self,
            self._app_config,
            prompt_text,
            on_success,
            image=image_data,
            is_busy=lambda: self._bothub_state.worker is not None,
            state=self._bothub_state,
        )

    @requires_database()
    def on_add_category(self) -> None:
        """Add a new category using database manager."""

        def get_and_validate() -> tuple[str | None, Any]:
            name = self.lineEdit_category_name.text().strip()
            category_type = self.comboBox_category_type.currentIndex()
            if not name:
                return ("Enter category name", None)
            if self.db_manager is None:
                return ("Database not initialized", None)
            return (None, (name, category_type))

        def add_db(data: Any) -> bool:
            name, category_type = data
            return bool(self.db_manager and self.db_manager.add_category(name, category_type))

        def on_success(_data: Any) -> None:
            self._mark_categories_changed()
            self.update_all()
            self._clear_category_form()

        self._add_record("category", get_and_validate, add_db, on_success)

    @requires_database()
    def on_add_currency(self) -> None:
        """Add a new currency using database manager."""

        def get_and_validate() -> tuple[str | None, Any]:
            code = self.lineEdit_currency_code.text().strip().upper()
            name = self.lineEdit_currency_name.text().strip()
            symbol = self.lineEdit_currency_symbol.text().strip()
            subdivision = self.spinBox_subdivision.value()
            if not code:
                return ("Enter currency code", None)
            if not name:
                return ("Enter currency name", None)
            if not symbol:
                return ("Enter currency symbol", None)
            if subdivision <= 0:
                return ("Subdivision must be a positive number", None)
            if self.db_manager is None:
                return ("Database not initialized", None)
            return (None, (code, name, symbol, subdivision))

        def add_db(data: Any) -> bool:
            code, name, symbol, subdivision = data
            return bool(self.db_manager and self.db_manager.add_currency(code, name, symbol, subdivision))

        def on_success(_data: Any) -> None:
            self._mark_currencies_changed()
            self.update_all()
            self._clear_currency_form()

        self._add_record("currency", get_and_validate, add_db, on_success)

    @requires_database()
    def on_add_exchange(self) -> None:
        """Add a new currency exchange using database manager."""

        def get_and_validate() -> tuple[str | None, Any]:
            from_currency = self.comboBox_exchange_from.currentText()
            to_currency = self.comboBox_exchange_to.currentText()
            amount_from = self.doubleSpinBox_exchange_from.value()
            amount_to = self.doubleSpinBox_exchange_to.value()
            exchange_rate = self.doubleSpinBox_exchange_rate.value()
            fee = self.doubleSpinBox_exchange_fee.value()
            date = self.dateEdit_exchange.date().toString("yyyy-MM-dd")
            description = self.lineEdit_exchange_description.text().strip()
            errors = validate_exchange_data(from_currency, to_currency, amount_from, amount_to, exchange_rate, fee)
            if errors:
                return (errors[0], None)
            if self.db_manager is None:
                return ("Database not initialized", None)
            from_currency_info = self.db_manager.get_currency_by_code(from_currency)
            to_currency_info = self.db_manager.get_currency_by_code(to_currency)
            if not from_currency_info or not to_currency_info:
                return ("Currency not found", None)
            return (
                None,
                (
                    from_currency_info[0],
                    to_currency_info[0],
                    amount_from,
                    amount_to,
                    exchange_rate,
                    fee,
                    date,
                    description,
                ),
            )

        def add_db(data: Any) -> bool:
            (from_id, to_id, amount_from, amount_to, rate, fee, date, description) = data
            return bool(
                self.db_manager
                and self.db_manager.add_currency_exchange(
                    from_id, to_id, amount_from, amount_to, rate, fee, date, description
                )
            )

        def on_success(_data: Any) -> None:
            column_widths = self._save_table_column_widths(self.tableView_exchange)
            self.update_all()
            self._restore_table_column_widths(self.tableView_exchange, column_widths)
            self._clear_exchange_form()

        self._add_record("currency exchange", get_and_validate, add_db, on_success)

    @requires_database()
    def on_add_transaction(self) -> None:
        """Add a new transaction using database manager."""

        def get_and_validate() -> tuple[str | None, Any]:
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
                return ("Amount must be positive", None)
            if not description:
                return ("Enter description", None)
            if not category_name:
                return ("Select a category", None)
            if not currency_code:
                return ("Select a currency", None)
            if self.db_manager is None:
                return ("Database not initialized", None)
            cat_id = self.db_manager.get_id("categories", "name", category_name)
            if cat_id is None:
                return (f"Category '{category_name}' not found", None)
            currency_info = self.db_manager.get_currency_by_code(currency_code)
            if not currency_info:
                return (f"Currency '{currency_code}' not found", None)
            return (None, (amount, description, cat_id, currency_info[0], date, tag))

        def add_db(data: Any) -> bool:
            amount, description, cat_id, currency_id, date, tag = data
            return bool(
                self.db_manager and self.db_manager.add_transaction(amount, description, cat_id, currency_id, date, tag)
            )

        def on_success(data: Any) -> None:
            _amount, _desc, _cat_id, _curr_id, _date, _tag = data
            current_date = self.dateEdit.date()
            self._mark_transactions_changed()
            self.update_all()
            self._update_autocomplete_data()
            self.doubleSpinBox_amount.setValue(100.0)
            self.lineEdit_description.clear()
            self.lineEdit_tag.clear()
            self.dateEdit.setDate(current_date)
            QTimer.singleShot(100, self._focus_description_and_select_text)

        self._add_record("transaction", get_and_validate, add_db, on_success)

    @requires_database()
    def on_calculate_exchange(self) -> None:
        """Calculate exchange amount based on rate."""
        amount_from: float = self.doubleSpinBox_exchange_from.value()
        rate: float = self.doubleSpinBox_exchange_rate.value()

        if rate > 0:
            amount_to: float = amount_from * rate
            self.doubleSpinBox_exchange_to.setValue(amount_to)

    def on_calculate_fee(self) -> None:
        """Calculate fee based on actual exchange vs expected exchange."""
        amount_from: float = self.doubleSpinBox_exchange_from.value()
        amount_to: float = self.doubleSpinBox_exchange_to.value()
        exchange_rate: float = self.doubleSpinBox_exchange_rate.value()

        if exchange_rate > 0:
            # Calculate what amount_from should have been if they received amount_to at exchange_rate
            expected_amount_from: float = amount_to / exchange_rate

            # Calculate the fee as the difference
            calculated_fee: float = amount_from - expected_amount_from

            # Get current fee value
            current_fee: float = self.doubleSpinBox_exchange_fee.value()

            # If current fee is non-zero, add to it, otherwise set it
            if current_fee != 0:
                new_fee: float = current_fee + calculated_fee
            else:
                new_fee: float = calculated_fee

            self.doubleSpinBox_exchange_fee.setValue(new_fee)

    def on_category_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle category selection change in listView_categories.

        Args:

        - `current` (`QModelIndex`): Current selected index.
        - `_previous` (`QModelIndex`): Previously selected index.

        """
        if current.isValid():
            # Get the display text (with icon and income marker if applicable)
            display_text: str | None = current.data(Qt.ItemDataRole.DisplayRole)
            if display_text:
                self.label_category_now.setText(display_text)
            else:
                self.label_category_now.setText(self._NO_CATEGORY_LABEL)

            # Move focus to description field and select all text
            QTimer.singleShot(100, self._focus_description_and_select_text)
        else:
            self.label_category_now.setText(self._NO_CATEGORY_LABEL)

    def on_clear_description(self) -> None:
        """Clear the description field."""
        self.lineEdit_description.clear()

    def on_copy_categories_as_text(self) -> None:
        """Copy list of categories to clipboard as text."""
        if self.db_manager is None:
            message_box.warning(
                self, "Database Error", "❌ Database manager is not initialized. Please try again later."
            )
            return

        try:
            # Get all categories
            categories_data: list = self.db_manager.get_all_categories()

            if not categories_data:
                message_box.information(self, "No Categories", "No categories found in the database.")
                return

            # Create text representation
            categories_text: list[str] = []
            for row in categories_data:
                category_name: str = row[1]  # name column
                categories_text.append(category_name)

            # Join with newlines
            clipboard_text: str = "\n".join(categories_text)

            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(clipboard_text)

            # Show success message to user
            message_box.information(
                self,
                "Categories Copied",
                f"✅ Successfully copied {len(categories_text)} categories to clipboard:\n\n{clipboard_text}",
            )

        except Exception as e:
            message_box.critical(self, "Error", f"❌ Error copying categories to clipboard:\n\n{e!s}")

    @requires_database()
    def on_exchange_item_update_button_clicked(self) -> None:
        """Update exchange rate in database when pushButton_exchange_item_update is clicked."""
        try:
            # Get selected currency ID
            currency_index: int = self.comboBox_exchange_item_update.currentIndex()
            if currency_index < 0:
                message_box.warning(self, "Invalid Selection", "Please select a currency.")
                return

            currency_id = self.comboBox_exchange_item_update.itemData(currency_index)
            if currency_id is None:
                message_box.warning(self, "Invalid Selection", "Please select a valid currency.")
                return

            # Get selected date
            selected_date: QDate = self.dateEdit_exchange_item_update.date()
            date_str: str = selected_date.toString("yyyy-MM-dd")

            # Get exchange rate value
            exchange_rate: float = self.doubleSpinBox_exchange_item_update.value()
            if exchange_rate <= 0:
                message_box.warning(self, "Invalid Rate", "Exchange rate must be greater than 0.")
                return

            # Get currency info for confirmation dialog
            currency_text: str = self.comboBox_exchange_item_update.currentText()

            # Confirm update
            reply = message_box.question(
                self,
                "Confirm Exchange Rate Update",
                f"Update exchange rate for {currency_text} on {date_str} to {exchange_rate}?\n\n"
                "This action will overwrite any existing rate for this currency and date.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Update exchange rate in database
            success: bool = self.db_manager.update_exchange_rate(currency_id, date_str, exchange_rate)

            if success:
                message_box.information(
                    self,
                    "Update Successful",
                    f"Exchange rate for {currency_text} on {date_str} has been updated to {exchange_rate}.",
                )
                # Clear exchange rate cache to ensure fresh data
                self.db_manager.exchange_rates.clear_cache()
                # Update all views
                self.update_all()
                self.update_summary_labels()
                # Update exchange rates chart if on the same currency
                self.on_exchange_rates_update()
            else:
                message_box.warning(
                    self,
                    "Update Failed",
                    "Failed to update exchange rate. Please check the database connection and try again.",
                )

        except Exception as e:
            message_box.critical(self, "Error", f"An error occurred while updating exchange rate: {e}")

    def on_exchange_item_update_changed(self) -> None:
        """Update exchange rate in doubleSpinBox_exchange_item_update when currency or date changes."""
        if not self._validate_database_connection():
            return

        try:
            # Get selected currency ID
            currency_index: int = self.comboBox_exchange_item_update.currentIndex()
            if currency_index < 0:
                self.doubleSpinBox_exchange_item_update.setValue(0.0)
                return

            currency_id = self.comboBox_exchange_item_update.itemData(currency_index)
            if currency_id is None:
                self.doubleSpinBox_exchange_item_update.setValue(0.0)
                return

            # Get selected date
            selected_date: QDate = self.dateEdit_exchange_item_update.date()
            date_str: str = selected_date.toString("yyyy-MM-dd")

            # Get exchange rate from database
            exchange_rate: float = self.db_manager.get_currency_exchange_rate_by_date(currency_id, date_str)

            # Update the doubleSpinBox
            self.doubleSpinBox_exchange_item_update.setValue(exchange_rate)

        except Exception as e:
            print(f"Error updating exchange item update rate: {e}")
            self.doubleSpinBox_exchange_item_update.setValue(0.0)

    def on_export_csv(self) -> None:
        """Save current transactions view to a CSV file."""
        filename_str: str
        filename_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save Table",
            "",
            "CSV (*.csv)",
        )
        if not filename_str:
            return

        try:
            filename: Path = Path(filename_str)
            proxy_model = self.models["transactions"]
            if proxy_model is None or not isinstance(proxy_model, QSortFilterProxyModel):
                return
            model = proxy_model.sourceModel()
            if model is None:
                return
            with filename.open("w", encoding="utf-8") as file:
                headers: list[str] = [
                    model.headerData(col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) or ""
                    for col in range(model.columnCount())
                ]
                file.write(";".join(headers) + "\n")

                for row in range(model.rowCount()):
                    row_values: list[str] = [
                        f'"{model.data(model.index(row, col)) or ""}"' for col in range(model.columnCount())
                    ]
                    file.write(";".join(row_values) + "\n")

        except Exception as e:
            message_box.warning(self, "Export Error", f"Failed to export CSV: {e}")

    @requires_database()
    def on_generate_report(self, *, refresh_summary: bool = False) -> None:
        """Generate selected report on a background thread with a countdown toast."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        worker = getattr(self, "_report_build_worker", None)
        if worker is not None and worker.isRunning():
            return

        report_type: str = self.comboBox_report_type.currentText()

        try:
            db_filename = _require_db_filename_for_worker(self.db_manager)
        except DbFilenameUnavailableForWorkerThreadError:
            message_box.warning(self, "Error", "Database path is not available for report generation.")
            return

        self._report_build_toast = toast_countdown_notification.ToastCountdownNotification("Building report…")
        self._report_build_toast.start_countdown()

        if refresh_summary:
            self._refresh_summary_if_needed()

        self._report_build_worker = ReportBuildWorker(db_filename, report_type)
        self._report_build_worker.report_completed.connect(self._on_report_build_completed)
        self._report_build_worker.report_failed.connect(self._on_report_build_failed)
        self._report_build_worker.finished.connect(self._cleanup_report_build_worker)
        self.pushButton_generate_report.setEnabled(False)
        self._report_build_worker.start()

    def on_select_only_expense_chart_categories(self) -> None:
        """Check only expense categories in the Charts category list."""
        self._select_only_chart_categories(0)

    def on_select_only_income_chart_categories(self) -> None:
        """Check only income categories in the Charts category list."""
        self._select_only_chart_categories(1)

    @requires_database()
    def on_set_default_currency(self) -> None:
        """Set the default currency."""
        currency_code: str = self.comboBox_default_currency.currentText()

        if not currency_code:
            message_box.warning(self, "Error", "Select a currency")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.set_default_currency(currency_code):
                message_box.information(self, "Success", f"Default currency set to {currency_code}")
                # Mark default currency changed for lazy loading
                self._mark_default_currency_changed()
                # Update all displays that depend on default currency
                self.update_summary_labels()
                self._update_comboboxes()
                self._update_accounts_balance_display()
                # Recalculate transaction-derived columns (e.g., "Total per day") in new default currency
                self._load_transactions_table()
                self._connect_table_auto_save_signals()
                self._load_currency_exchanges_table()
            else:
                message_box.warning(self, "Error", "Failed to set default currency")
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to set default currency: {e}")

    def on_show_all_records_clicked(self) -> None:
        """Toggle between showing all records and last self.count_transactions_to_show records."""
        self.show_all_transactions = not self.show_all_transactions

        # Update button text and icon
        if self.show_all_transactions:
            self.pushButton_show_all_records.setText(f"📊 Show Last {self.count_transactions_to_show}")
        else:
            self.pushButton_show_all_records.setText("📊 Show All Records")

        self._load_transactions_page(reset=True)

    def on_tab_changed(self, index: int) -> None:
        """React to tab change.

        Args:

        - `index` (`int`): The index of the newly selected tab.

        """
        # Update relevant data when switching to different tabs
        id_exchange_rates_tab: int = 4
        id_charts_tab: int = 5
        id_reports_tab: int = 6
        if index == id_exchange_rates_tab:  # Exchange Rates tab - lazy loading
            if not self.exchange_rates_loaded:
                self.load_exchange_rates_table()
        elif index == id_charts_tab:  # Charts tab - auto-draw on first visit
            if not self._charts_initialized:
                self._update_finance_chart()
                self._charts_initialized = True
        elif index == id_reports_tab:  # Reports tab
            self.on_generate_report(refresh_summary=True)
        # Note: Transactions tab (index 0) needs no updates - data loaded on startup

    def on_yesterday(self) -> None:
        """Set yesterday's date in the main date field."""
        yesterday: QDate = QDate.currentDate().addDays(-1)
        self.dateEdit.setDate(yesterday)

    def on_yesterday_exchange(self) -> None:
        """Set yesterday's date in the exchange date field."""
        yesterday: QDate = QDate.currentDate().addDays(-1)
        self.dateEdit_exchange.setDate(yesterday)

    def set_chart_all_time(self) -> None:
        """Set chart date range from the first transaction to today."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, is_all_time=True)

    def set_chart_last_month(self) -> None:
        """Set chart start date to one month ago and end date to today."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, months=1)

    def set_chart_last_year(self) -> None:
        """Set chart start date to one year ago and end date to today."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, years=1)

    def set_today_date(self) -> None:
        """Set today's date in all date fields."""
        today_qdate: QDate = QDate.currentDate()
        self.dateEdit.setDate(today_qdate)
        self.dateEdit_exchange.setDate(today_qdate)

    @requires_database(is_show_warning=False)
    def show_tables(self) -> None:
        """Populate all QTableViews using database manager methods (except exchange rates - lazy loaded)."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Load essential tables only (exclude exchange_rates)
            self._load_essential_tables()

            # Exchange rates table loaded lazily on first tab access

        except Exception as e:
            print(f"Error showing tables: {e}")
            message_box.warning(self, "Database Error", f"Failed to load tables: {e}")

    @requires_database(is_show_warning=False)
    def update_all(self) -> None:
        """Refresh all tables and comboboxes."""
        # Load essential tables
        self._load_essential_tables()
        self._update_comboboxes()
        self.update_filter_comboboxes()
        self.set_today_date()
        self._mark_summary_dirty()
        self._refresh_summary_if_needed()

        # If exchange rates tab is currently active, reload the data
        current_tab_index: int = self.tabWidget.currentIndex()
        id_exchange_rates_tab = 4
        if current_tab_index == id_exchange_rates_tab:  # Exchange Rates tab
            self.load_exchange_rates_table()
        else:
            # Mark exchange rates as not loaded to force reload when tab is accessed
            self.exchange_rates_loaded = False

        # Clear forms
        self._clear_all_forms()

    @requires_database(is_show_warning=False)
    def update_filter_comboboxes(self) -> None:
        """Update filter comboboxes with current data."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update category filter
            categories: list[str] = self.db_manager.get_categories_by_type(0) + self.db_manager.get_categories_by_type(
                1
            )

            self.comboBox_filter_category.clear()
            self.comboBox_filter_category.addItem("")  # All categories
            self.comboBox_filter_category.addItems(categories)

            # Update currency filter
            currencies: list[str] = [row[1] for row in self.db_manager.get_all_currencies()]  # Get codes

            self.comboBox_filter_currency.clear()
            self.comboBox_filter_currency.addItem("")  # All currencies
            self.comboBox_filter_currency.addItems(currencies)

        except Exception as e:
            print(f"Error updating filter comboboxes: {e}")

    @requires_database()
    def update_summary_labels(self) -> None:
        """Update Quick Summary / today and yesterday labels using natural per-currency amounts."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            db = self.db_manager
            default_currency_info = db.get_currency_by_code(db.get_default_currency())
            currency_symbol: str = default_currency_info[2] if default_currency_info else "₽"

            transaction_rows: list = db.get_all_transactions()

            income_minor: dict[int, int]
            expense_minor: dict[int, int]
            income_minor, expense_minor = get_natural_cumulative_income_expense_minor_by_currency(transaction_rows, db)

            def _currency_sort_key(cid: int) -> str:
                cur = db.get_currency_by_id(cid)
                return cur[0] if cur else f"#{cid}"

            income_lines: list[str] = []
            for cid in sorted(income_minor, key=_currency_sort_key):
                minor = income_minor[cid]
                if minor == 0:
                    continue
                cur = db.get_currency_by_id(cid)
                code = cur[0] if cur else str(cid)
                sym = cur[2] if cur else ""
                major = db.convert_from_minor_units(minor, cid)
                income_lines.append(f"{code}: {major:,.2f}{sym}")
            income_text = (
                "Total Income:\n" + "\n".join(income_lines) if income_lines else f"Total Income:\n0.00{currency_symbol}"
            )
            self.label_total_income.setText(income_text)

            expense_lines: list[str] = []
            for cid in sorted(expense_minor, key=_currency_sort_key):
                minor = expense_minor[cid]
                if minor == 0:
                    continue
                cur = db.get_currency_by_id(cid)
                code = cur[0] if cur else str(cid)
                sym = cur[2] if cur else ""
                major = db.convert_from_minor_units(minor, cid)
                expense_lines.append(f"{code}: {major:,.2f}{sym}")
            expense_text = (
                "Total Expenses:\n" + "\n".join(expense_lines)
                if expense_lines
                else f"Total Expenses:\n0.00{currency_symbol}"
            )
            self.label_total_expenses.setText(expense_text)

            today: date = datetime.now(UTC).astimezone().date()
            today_str: str = today.strftime("%Y-%m-%d")
            yesterday_str: str = (today - timedelta(days=1)).strftime("%Y-%m-%d")

            def _expense_lines_for_date(target_date: str) -> list[str]:
                expense_minor_by_date: dict[int, int] = {}
                for row in transaction_rows:
                    if len(row) < MIN_TRANSACTION_ROW_LENGTH:
                        continue
                    if row[5] != target_date or int(row[7]) != 0:
                        continue
                    currency_info = db.get_currency_by_code(row[4])
                    cid = currency_info[0] if currency_info else 1
                    expense_minor_by_date[cid] = expense_minor_by_date.get(cid, 0) + int(row[1])

                lines: list[str] = []
                for cid in sorted(expense_minor_by_date, key=_currency_sort_key):
                    minor = expense_minor_by_date[cid]
                    if minor == 0:
                        continue
                    cur = db.get_currency_by_id(cid)
                    code = cur[0] if cur else str(cid)
                    sym = cur[2] if cur else ""
                    major = db.convert_from_minor_units(minor, cid)
                    lines.append(f"{code}: {major:,.2f}{sym}")
                return lines

            expense_today_lines: list[str] = _expense_lines_for_date(today_str)
            if expense_today_lines:
                self.label_today_expense.setText("\n".join(expense_today_lines))
            else:
                self.label_today_expense.setText(f"0.00{currency_symbol}")

            expense_yesterday_lines: list[str] = _expense_lines_for_date(yesterday_str)
            if expense_yesterday_lines:
                self.label_yesterday_expense.setText("\n".join(expense_yesterday_lines))
            else:
                self.label_yesterday_expense.setText(f"0.00{currency_symbol}")

        except Exception as e:
            print(f"Error updating summary labels: {e}")
            # Set default values on error
            self.label_total_income.setText("Total Income: 0.00₽")
            self.label_total_expenses.setText("Total Expenses: 0.00₽")
            self.label_today_expense.setText("0.00₽")
            self.label_yesterday_expense.setText("0.00₽")

    def _add_chart_canvas(self, fig: Figure) -> None:
        canvas = FigureCanvas(fig)
        fig.tight_layout()
        self.verticalLayout_charts_content.addWidget(canvas)
        canvas.draw()

    def _add_one_day_to_main(self) -> None:
        """Add one day to the current date in main date field."""
        current_date: QDate = self.dateEdit.date()
        new_date: QDate = current_date.addDays(1)
        self.dateEdit.setDate(new_date)

    def _add_record(
        self,
        entity_name: str,
        get_and_validate: Callable[[], tuple[str | None, Any]],
        add_db: Callable[[Any], bool],
        on_success: Callable[[Any], None],
    ) -> None:
        """Run add-record flow: validate form data, call DB add, run on_success or show errors.

        Args:

        - `entity_name` (`str`): Name for error messages (e.g. "account").
        - `get_and_validate` (`Callable`): Returns (error_message_or_None, data).
        - `add_db` (`Callable`): Takes data, returns True if add succeeded.
        - `on_success` (`Callable`): Called with data when add succeeded.

        """
        error_msg, data = get_and_validate()
        if error_msg:
            self._show_error("Error", error_msg)
            return
        try:
            if add_db(data):
                on_success(data)
            else:
                if entity_name == "account" and self.db_manager is not None and isinstance(data, tuple) and data:
                    name = str(data[0]).strip()
                    if name:
                        rows = self.db_manager.get_rows(
                            """
                            SELECT a.balance, c.symbol, c._id
                            FROM accounts a
                            JOIN currencies c ON a._id_currencies = c._id
                            WHERE a.name = :name
                            """,
                            {"name": name},
                        )
                        if rows:
                            balance_minor = int(rows[0][0])
                            symbol = str(rows[0][1] or "")
                            currency_id = int(rows[0][2])
                            balance_major = self.db_manager.convert_from_minor_units(balance_minor, currency_id)
                            self._show_error(
                                "Error",
                                f"The account name must be unique.\n"
                                f"An account with the name “{name}” already exists.\n"
                                f"Balance: {balance_major:,.2f}{symbol}",
                            )
                            return

                self._show_error("Error", f"Failed to add {entity_name}")
        except Exception as e:
            self._show_db_error(f"Failed to add {entity_name}: {e}")

    def _append_colored_rows_to_model(
        self,
        model: QStandardItemModel,
        transformed_data: list[list],
        id_column: int = -2,
    ) -> None:
        """Append colored table rows to an existing source model."""
        start_row_idx: int = model.rowCount()
        for row_offset, row in enumerate(transformed_data):
            row_idx: int = start_row_idx + row_offset
            row_color: QColor = row[-1]
            row_id: int = row[id_column]
            items: list[QStandardItem] = []
            display_data: list = row[:-2]

            for value in display_data:
                item: QStandardItem = QStandardItem(str(value) if value is not None else "")
                item.setBackground(QBrush(row_color))
                items.append(item)

            model.appendRow(items)
            model.setVerticalHeaderItem(row_idx, QStandardItem(str(row_id)))

    def _append_transformed_rows_to_model(
        self,
        model: QStandardItemModel,
        transformed_data: list[list],
        id_column: int = -2,
    ) -> None:
        """Append transformed transaction rows to an existing source model."""
        start_row_idx: int = model.rowCount()
        for row_offset, row in enumerate(transformed_data):
            row_idx: int = start_row_idx + row_offset
            row_color: QColor = row[-1]
            row_id: int = row[id_column]
            items: list[QStandardItem] = []
            display_data: list = row[:-2]

            for col_idx, value in enumerate(display_data):
                item: QStandardItem = QStandardItem(str(value) if value is not None else "")
                item.setBackground(QBrush(row_color))

                if col_idx == 1:
                    original_value: str = (
                        str(value).replace("-", "") if value and str(value).startswith("-") else str(value)
                    )
                    item.setData(original_value, Qt.ItemDataRole.UserRole)

                if col_idx == len(display_data) - 1:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                items.append(item)

            model.appendRow(items)
            model.setVerticalHeaderItem(row_idx, QStandardItem(str(row_id)))

    def _apply_account_balances_report(self, headers: list[str], report_data: list[list[str]]) -> None:
        """Bind account balances report data to the reports table."""
        if not report_data:
            return

        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        for row_data in report_data:
            items: list[QStandardItem] = [QStandardItem(str(value)) for value in row_data]
            if row_data[0] == "TOTAL":
                for item in items:
                    item.setBackground(QBrush(QColor(255, 255, 0)))
            model.appendRow(items)
        self._set_reports_model_and_stretch(model)

    def _apply_category_analysis_report(self, headers: list[str], report_data: list[list[str]]) -> None:
        """Bind category analysis report data to the reports table."""
        if not report_data:
            return

        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            if row_data[0] in ["EXPENSES", "INCOME"]:
                for item in items:
                    item.setBackground(QBrush(QColor(200, 200, 255)))
            model.appendRow(items)
        self._set_reports_model_and_stretch(model)

    def _apply_currency_analysis_report(self, headers: list[str], report_data: list[list[str]]) -> None:
        """Bind currency analysis report data to the reports table."""
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            model.appendRow(items)
        self._set_reports_model_and_stretch(model)

    def _apply_income_vs_expenses_report(self, headers: list[str], report_data: list[list[str]]) -> None:
        """Bind income vs expenses report data to the reports table."""
        if not report_data:
            return

        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            balance_str: str = row_data[3]
            try:
                balance_value: float = float(balance_str.split(maxsplit=1)[0])
                if balance_value > 0:
                    items[3].setBackground(QBrush(QColor(200, 255, 200)))
                elif balance_value < 0:
                    items[3].setBackground(QBrush(QColor(255, 200, 200)))
            except (ValueError, IndexError):
                pass
            model.appendRow(items)
        self._set_reports_model_and_stretch(model)

    def _apply_monthly_summary_report(
        self,
        headers: list[str],
        rows: list[tuple[str, float, float, dict[int, float]]],
        expense_categories: list[tuple[int, str, str]],
    ) -> None:
        """Bind monthly summary report data to the reports table."""
        if not expense_categories:
            model: QStandardItemModel = QStandardItemModel()
            model.setHorizontalHeaderLabels(headers)
            self.tableView_reports.setModel(model)
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        num_categories = len(expense_categories)
        category_colors: list[QColor] = []
        for i in range(num_categories):
            hue = (i * 360) / num_categories if num_categories > 0 else 0
            category_colors.append(QColor.fromHsv(int(hue), 80, 240))

        current_year_prefix: str = datetime.now(UTC).astimezone().strftime("%Y-")

        for month_name, month_total, combined_total, by_category in rows:
            row_items = []
            month_item = QStandardItem(month_name)
            if month_name.startswith(current_year_prefix):
                font = month_item.font()
                font.setBold(True)
                month_item.setFont(font)
            row_items.append(month_item)

            total_item = QStandardItem(f"{month_total:.2f}")
            total_item.setBackground(QBrush(QColor(255, 250, 205)))
            total_item.setData(month_total, Qt.ItemDataRole.UserRole)
            row_items.append(total_item)

            combined_item = QStandardItem(f"{combined_total:.2f}")
            combined_item.setBackground(QBrush(QColor(220, 220, 220)))
            combined_item.setData(combined_total, Qt.ItemDataRole.UserRole)
            row_items.append(combined_item)

            for idx, (category_id, _name, _icon) in enumerate(expense_categories):
                amount = by_category.get(category_id, 0.0)
                item = QStandardItem(f"{amount:.2f}")
                item.setBackground(QBrush(category_colors[idx]))
                item.setData(amount, Qt.ItemDataRole.UserRole)
                row_items.append(item)

            model.appendRow(row_items)

        self.tableView_reports.setModel(model)
        self.tableView_reports.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView_reports.setSortingEnabled(True)
        self.tableView_reports.sortByColumn(0, Qt.SortOrder.DescendingOrder)
        model.setSortRole(Qt.ItemDataRole.UserRole)

        total_delegate = ReportAmountDelegate(self.tableView_reports, is_bold=True)
        self.tableView_reports.setItemDelegateForColumn(1, total_delegate)
        combined_delegate = ReportAmountDelegate(self.tableView_reports, is_bold=True)
        self.tableView_reports.setItemDelegateForColumn(2, combined_delegate)
        for col_idx in range(3, model.columnCount()):
            self.tableView_reports.setItemDelegateForColumn(
                col_idx, ReportAmountDelegate(self.tableView_reports, is_bold=False)
            )

        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Interactive)
            self.tableView_reports.resizeColumnsToContents()
            if reports_header.count() > 1:
                self.tableView_reports.setColumnWidth(1, self.tableView_reports.columnWidth(1) + 30)

    def _apply_report_build_result(self, result: ReportBuildResult) -> None:
        """Dispatch report build result to the appropriate table binder."""
        report_type = result.report_type
        if report_type == "Monthly Summary":
            if result.monthly_rows is None or result.expense_categories is None:
                return
            self._apply_monthly_summary_report(result.headers, result.monthly_rows, result.expense_categories)
        elif report_type == "Category Analysis":
            self._apply_category_analysis_report(result.headers, result.table_rows or [])
        elif report_type == "Currency Analysis":
            self._apply_currency_analysis_report(result.headers, result.table_rows or [])
        elif report_type == "Account Balances":
            self._apply_account_balances_report(result.headers, result.table_rows or [])
        elif report_type == "Income vs Expenses":
            self._apply_income_vs_expenses_report(result.headers, result.table_rows or [])

    def _calculate_exchange_loss(
        self,
        from_currency_id: int,
        to_currency_id: int,
        amount_from: float,
        amount_to: float,
        default_currency_id: int | None,
        fee: float = 0.0,
        use_date: str | None = None,
    ) -> float:
        """Calculate loss due to exchange rate difference.

        Args:

        - `from_currency_id` (`int`): Source currency ID
        - `to_currency_id` (`int`): Target currency ID
        - `amount_from` (`float`): Amount in source currency
        - `amount_to` (`float`): Amount in target currency
        - `default_currency_id` (`int | None`): Default currency ID for conversion
        - `fee` (`float`): Exchange fee in source currency
        - `use_date` (`str | None`): Date to use for rate calculation. If None, uses today's date

        Returns:

        - `float`: Loss amount in default currency (negative = loss, positive = profit)

        """
        return calc_exchange_loss(
            from_currency_id,
            to_currency_id,
            amount_from,
            amount_to,
            default_currency_id,
            self.db_manager,
            fee=fee,
            use_date=use_date,
        )

    def _calculate_total_accounts_balance(self) -> tuple[float, str]:
        """Calculate total balance across all accounts in default currency.

        Uses get_total_accounts_balance_in_currency for the total; builds details
        per currency for label_balance_account_details.

        Returns:

        - `tuple[float, str]`: (total_balance, formatted_details)

        """
        if not self._validate_database_connection() or self.db_manager is None:
            return 0.0, "Database not available"

        return format_total_accounts_balance_details(self.db_manager)

    def _can_net_negative_revisions(self, currency_id: int, diff_minor: int) -> bool:
        """Return whether recent Revision Expense rows can cover a positive diff."""
        if self.db_manager is None or diff_minor <= 0:
            return False
        revision_rows = self.db_manager.get_revision_expense_transactions(currency_id)
        return plan_revision_expense_consolidation_for_positive_diff(revision_rows, diff_minor) is not None

    @staticmethod
    def _chart_date_nums(x_values: list[datetime]) -> list[float]:
        return list(date2num(x_values))

    def _cleanup_balance_check_worker(self) -> None:
        """Release the balance check worker after the thread finishes."""
        worker = getattr(self, "_balance_check_worker", None)
        if worker is not None:
            worker.deleteLater()
            self._balance_check_worker = None

    def _cleanup_report_build_worker(self) -> None:
        """Release the report build worker after the thread finishes."""
        worker = getattr(self, "_report_build_worker", None)
        if worker is not None:
            worker.deleteLater()
            self._report_build_worker = None
        self.pushButton_generate_report.setEnabled(True)

    def _cleanup_startup_dialog(self) -> None:
        """Clean up startup dialog and re-enable main window."""
        # Close dialog if exists
        if hasattr(self, "startup_progress_dialog"):
            self.startup_progress_dialog.close()
            delattr(self, "startup_progress_dialog")

        # Re-enable main window
        self.setEnabled(True)

        # Ensure main window gets focus back
        self.activateWindow()
        self.raise_()

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
        self._clear_category_selection()

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

    def _clear_category_selection(self) -> None:
        """Clear selected category in the transaction form."""
        self.label_category_now.setText(self._NO_CATEGORY_LABEL)
        selection_model = self.listView_categories.selectionModel()
        if selection_model is not None:
            selection_model.blockSignals(True)  # noqa: FBT003
            selection_model.clear()
            selection_model.setCurrentIndex(QModelIndex(), QItemSelectionModel.SelectionFlag.NoUpdate)
            selection_model.blockSignals(False)  # noqa: FBT003
        self.listView_categories.setCurrentIndex(QModelIndex())

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

    def _clear_layout(self, layout: QLayout, *, close_matplotlib_figures: bool = True) -> None:
        """Clear all widgets from the specified layout.

        Args:

        - `layout` (`QLayout`): The layout to clear.
        - `close_matplotlib_figures` (`bool`): When True, clear and close Matplotlib canvases.

        """
        while layout.count():
            child = layout.takeAt(0)
            if child is not None:
                widget = child.widget()
                if widget is not None:
                    # Special handling for matplotlib canvas
                    if close_matplotlib_figures and hasattr(widget, "figure"):
                        try:
                            # Mark canvas as being deleted to prevent new updates
                            widget.deleting = True  # ty: ignore[invalid-assignment]
                            # Clear the figure first
                            widget.figure.clear()
                            # Close the canvas properly
                            widget.close()
                            # Force garbage collection
                            gc.collect()
                        except Exception as e:
                            print(f"Error while clearing matplotlib canvas: {e}")
                    widget.deleteLater()

    def _close_balance_check_toast(self) -> None:
        """Close the balance-check countdown toast if it is open."""
        toast = getattr(self, "_balance_check_toast", None)
        if toast is not None:
            toast.close()
            self._balance_check_toast = None

    def _close_chart_build_toast(self) -> None:
        """Close the chart-building countdown toast if it is open."""
        toast = getattr(self, "_chart_build_toast", None)
        if toast is not None:
            toast.close()
            self._chart_build_toast = None

    def _close_report_build_toast(self) -> None:
        """Close the report-building countdown toast if it is open."""
        toast = getattr(self, "_report_build_toast", None)
        if toast is not None:
            toast.close()
            self._report_build_toast = None

    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers."""
        # Main transaction signals
        self.pushButton_add.clicked.connect(self.on_add_transaction)
        self.pushButton_add_as_text_with_ai.clicked.connect(self.on_add_as_text_with_ai)
        self.pushButton_description_clear.clicked.connect(self.on_clear_description)
        self.pushButton_yesterday.clicked.connect(self.on_yesterday)

        # Add context menu for yesterday button
        self.pushButton_yesterday.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.pushButton_yesterday.customContextMenuRequested.connect(self._show_yesterday_context_menu)

        # Delete and refresh buttons for all tables
        tables_with_controls: dict[str, tuple[str, str]] = {
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

            # Special handling for exchange_rates delete button
            if table_name == "exchange_rates":
                delete_button.clicked.connect(self.on_delete_exchange_rates_by_days)
            else:
                delete_button.clicked.connect(partial(self.delete_record, table_name))

            refresh_button.clicked.connect(self.update_all)

        # Add buttons
        self.pushButton_category_add.clicked.connect(self.on_add_category)
        self.pushButton_account_add.clicked.connect(self.on_add_account)
        self.pushButton_balance_check.clicked.connect(self._on_balance_check_clicked)
        self.pushButton_currency_add.clicked.connect(self.on_add_currency)
        self.pushButton_exchange_add.clicked.connect(self.on_add_exchange)

        # Copy categories as text button
        self.pushButton_copy_categories_as_text.clicked.connect(self.on_copy_categories_as_text)

        # Filter signals
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

        # Auto-filter signals for radio buttons
        self.radioButton_filter_type_all.clicked.connect(self.apply_filter)
        self.radioButton_filter_type_expense.clicked.connect(self.apply_filter)
        self.radioButton_filter_type_income.clicked.connect(self.apply_filter)

        # Auto-filter signals for combo boxes
        self.comboBox_filter_category.currentTextChanged.connect(lambda _: self.apply_filter())
        self.comboBox_filter_currency.currentTextChanged.connect(lambda _: self.apply_filter())

        self.checkBox_use_date_filter.toggled.connect(
            lambda enabled: self._update_date_filter_visibility(enabled=enabled)
        )

        # Chart date range signals
        self.pushButton_chart_last_month.clicked.connect(self.set_chart_last_month)
        self.pushButton_chart_last_year.clicked.connect(self.set_chart_last_year)
        self.pushButton_chart_all_time.clicked.connect(self.set_chart_all_time)
        self.pushButton_update_chart.clicked.connect(self._update_finance_chart)

        self.list_chart_categories.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.list_chart_categories.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_chart_categories.customContextMenuRequested.connect(self._show_chart_categories_context_menu)
        self.pushButton_select_all.clicked.connect(partial(self._set_chart_categories_check_state, checked=True))
        self.pushButton_select_deselect_all.clicked.connect(
            partial(self._set_chart_categories_check_state, checked=False)
        )
        self.pushButton_select_only_expense.clicked.connect(self.on_select_only_expense_chart_categories)
        self.pushButton_select_only_income.clicked.connect(self.on_select_only_income_chart_categories)

        # Exchange signals
        self.pushButton_calculate_exchange.clicked.connect(self.on_calculate_exchange)
        self.pushButton_exchange_yesterday.clicked.connect(self.on_yesterday_exchange)
        self.pushButton_calculate_fee.clicked.connect(self.on_calculate_fee)

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

        # Exchange item update signals
        self.comboBox_exchange_item_update.currentIndexChanged.connect(self.on_exchange_item_update_changed)
        self.dateEdit_exchange_item_update.dateChanged.connect(self.on_exchange_item_update_changed)
        self.pushButton_exchange_item_update.clicked.connect(self.on_exchange_item_update_button_clicked)

        # Exchange rates filter signals
        self.pushButton_filter_exchange_rates_apply.clicked.connect(self.on_filter_exchange_rates_apply)
        self.pushButton_filter_exchange_rates_clear.clicked.connect(self.on_filter_exchange_rates_clear)

        # Report signals
        self.pushButton_generate_report.clicked.connect(self.on_generate_report)

        # Export signal
        self.pushButton_show_all_records.clicked.connect(self.on_show_all_records_clicked)

        # Add context menu for transactions table
        self.tableView_transactions.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_transactions.customContextMenuRequested.connect(self._show_transactions_context_menu)

        # Install event filter to track mouse events on transactions table
        self.tableView_transactions.viewport().installEventFilter(self)

        # Load more transactions when scrolling near the bottom
        self.tableView_transactions.verticalScrollBar().valueChanged.connect(self._on_transactions_scroll)

        # Load more exchange rates when scrolling near the bottom
        self.tableView_exchange_rates.verticalScrollBar().valueChanged.connect(self._on_exchange_rates_scroll)

        # Add selection signal for transactions table to copy data to form fields
        # This will be connected after the model is set in _load_transactions_table

        # Tab change signal
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Enter key handling for doubleSpinBox_amount
        self.doubleSpinBox_amount.installEventFilter(self)

        # Enter key handling for dateEdit
        self.dateEdit.installEventFilter(self)

        # Enter key handling for lineEdit_tag
        self.lineEdit_tag.installEventFilter(self)

        # Enter key handling for lineEdit_description
        self.lineEdit_description.installEventFilter(self)

        # Enter key handling for pushButton_add
        self.pushButton_add.installEventFilter(self)

    def _connect_transaction_selection_signal(self) -> None:
        """Connect transaction table selection to the form-fill handler (after model reload)."""
        selection_model = self.tableView_transactions.selectionModel()
        if selection_model is None:
            return
        old_selection_model = self._transaction_selection_selection_model
        if old_selection_model is not None:
            with contextlib.suppress(TypeError, RuntimeError):
                old_selection_model.currentChanged.disconnect(self._on_transaction_selection_changed)
        selection_model.currentChanged.connect(self._on_transaction_selection_changed)
        self._transaction_selection_selection_model = selection_model

    def _copy_test_balance_to_clipboard(self, summary_lines: list[str], natural_rows: list[dict[str, Any]]) -> None:
        """Copy test balance summary and currency table to clipboard."""
        if self.db_manager is None:
            return
        lines: list[str] = []
        lines.extend(summary_lines)
        lines.append("")
        lines.append("--- By currency (no FX) ---")
        for item in natural_rows:
            cid = int(item["currency_id"])
            j_maj = self.db_manager.convert_from_minor_units(int(item["journal_minor"]), cid)
            a_maj = self.db_manager.convert_from_minor_units(int(item["accounts_minor"]), cid)
            d_maj = self.db_manager.convert_from_minor_units(int(item["diff_minor"]), cid)
            lines.append(
                f"{item['code']} ({item['symbol']}): journal {j_maj:,.2f}, accounts {a_maj:,.2f}, diff {d_maj:,.2f}"
            )
        text = "\n".join(lines)
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)

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
        return create_table_proxy_model(data, headers, id_column=id_column)

    def _create_transactions_table_model(
        self,
        data: list[list],
        headers: list[str],
        id_column: int = -2,
    ) -> QSortFilterProxyModel:
        """Create a special model for transactions table with non-editable total column.

        Args:

        - `data` (`list[list]`): The table data with color information.
        - `headers` (`list[str]`): Column header names.
        - `id_column` (`int`): Index of the ID column. Defaults to `-2` (second-to-last).

        Returns:

        - `QSortFilterProxyModel`: A filterable and sortable model with colored data and non-editable total column.

        """
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID (second-to-last element)
            row_color: QColor = row[-1]  # Color is at the last position
            row_id: int = row[id_column]  # ID is at second-to-last position

            # Create items for display columns only (exclude ID and color)
            items: list[QStandardItem] = []
            display_data: list = row[:-2]  # Exclude last two elements (ID and color)

            for col_idx, value in enumerate(display_data):
                item: QStandardItem = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

                # For amount column (index 1), store original value without minus sign for editing
                if col_idx == 1:  # Amount column
                    # Remove minus sign for editing, keep only the numeric value
                    original_value: str = (
                        str(value).replace("-", "") if value and str(value).startswith("-") else str(value)
                    )
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

        proxy: QSortFilterProxyModel = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy

    def _dispose_models(self) -> None:
        """Detach all models from QTableView and delete them."""
        for key, model in self.models.items():
            if key in self.table_config:
                view: QTableView = self.table_config[key][0]
                view.setModel(None)
            if model is not None:
                model.deleteLater()
            self.models[key] = None

    def _draw_balance_chart(
        self,
        series: list[tuple[str, float]],
        period: str,
        currency_symbol: str,
    ) -> None:
        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        x_values = [datetime.fromisoformat(date_str).replace(tzinfo=UTC) for date_str, _value in series]
        y_values = [value for _date_str, value in series]
        x_nums = self._chart_date_nums(x_values)
        ax.plot(x_nums, y_values, color="steelblue", linewidth=2, marker="o", markersize=4)
        self._annotate_balance_chart_extrema(
            ax,
            series,
            x_nums,
            fig,
            period=period,
            currency_symbol=currency_symbol,
        )
        ax.set_xlabel("Period", fontsize=12)
        ax.set_ylabel(f"Balance ({currency_symbol})", fontsize=12)
        ax.set_title("Balance", fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)
        self._format_chart_x_axis(ax, x_values, period)
        self._add_finance_chart_stats_box(ax, y_values, currency_symbol)
        self._add_chart_canvas(fig)

    def _draw_category_chart(
        self,
        category_series: dict[str, list[tuple[str, float]]],
        period: str,
        currency_symbol: str,
    ) -> None:
        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        color_palette = [
            "blue",
            "green",
            "orange",
            "purple",
            "brown",
            "pink",
            "gray",
            "olive",
            "cyan",
            "magenta",
            "teal",
            "navy",
            "maroon",
            "lime",
            "indigo",
            "coral",
        ]
        x_values: list[datetime] = []
        x_nums: list[float] = []
        for index, (category_name, series) in enumerate(category_series.items()):
            if not series:
                continue
            if not x_values:
                x_values = [datetime.fromisoformat(date_str).replace(tzinfo=UTC) for date_str, _value in series]
                x_nums = self._chart_date_nums(x_values)
            y_values = [value for _date_str, value in series]
            color = color_palette[index % len(color_palette)]
            ax.plot(
                x_nums,
                y_values,
                color=color,
                linewidth=2,
                marker="o",
                markersize=3,
                label=category_name,
            )
            self._annotate_datetime_line_last_point(
                ax,
                x_values,
                x_nums,
                y_values,
                prefix=category_name,
                currency_symbol=currency_symbol,
                period=period,
            )
        ax.set_xlabel("Period", fontsize=12)
        ax.set_ylabel(f"Amount ({currency_symbol})", fontsize=12)
        ax.set_title("Category", fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)
        ax.legend(loc="upper left", fontsize=9)
        self._format_chart_x_axis(ax, x_values, period)
        all_values: list[float] = [value for series in category_series.values() for _date_str, value in series]
        self._add_finance_chart_stats_box(ax, all_values, currency_symbol)
        self._add_chart_canvas(fig)

    def _draw_compare_chart(self, mode: str) -> None:
        if self.db_manager is None:
            return

        expense_names, income_names, all_names = self._get_checked_chart_categories()
        if not all_names:
            self._show_no_data_label(self.verticalLayout_charts_content, "Please select at least one category")
            return

        transaction_rows = self.db_manager.get_all_transactions()
        currency_symbol = self._get_default_currency_symbol()
        sections: list[tuple[str, int, set[str]]] = []
        if expense_names:
            sections.append(("Expense", 0, expense_names))
        if income_names:
            sections.append(("Income", 1, income_names))

        if not sections:
            self._show_no_data_label(self.verticalLayout_charts_content, "Please select at least one category")
            return

        compare_count = self.spinBox_compare_last.value()
        max_days_in_all_periods = 0
        rendered_any = False

        if mode == "last_years":
            self.label_compare_last.setText("Number of years:")
        else:
            self.label_compare_last.setText("Number of months:")

        for section_title, category_type, selected_names in sections:
            if mode == "last":
                series_data, labels, colors = compute_cumulative_compare_last_months(
                    transaction_rows,
                    self.db_manager,
                    compare_count,
                    selected_names,
                    category_type,
                )
                chart_title = f"{section_title} (Last {compare_count} months comparison)"
                x_label = "Day of Month"
                default_max_x = 31
            elif mode == "last_years":
                year_start_month = self._compare_last_years_start_month
                year_start_day = self._compare_last_years_start_day
                series_data, labels, colors = compute_cumulative_compare_last_years(
                    transaction_rows,
                    self.db_manager,
                    compare_count,
                    selected_names,
                    category_type,
                    year_start_month=year_start_month,
                    year_start_day=year_start_day,
                )
                if year_start_month == 1 and year_start_day == 1:
                    chart_title = f"{section_title} (Last {compare_count} years comparison)"
                else:
                    chart_title = (
                        f"{section_title} (Last {compare_count} years from {year_start_day:02d}.{year_start_month:02d})"
                    )
                x_label = "Day of Year"
                default_max_x = 366
            else:
                selected_month = self.comboBox_compare_same_months.currentIndex() + 1
                series_data, labels, colors = compute_cumulative_compare_same_months(
                    transaction_rows,
                    self.db_manager,
                    compare_count,
                    selected_month,
                    selected_names,
                    category_type,
                )
                month_name = self.comboBox_compare_same_months.currentText()
                chart_title = f"{section_title} ({month_name} comparison)"
                x_label = "Day of Month"
                default_max_x = 31

            if not series_data or all(len(data) == 0 for data in series_data):
                continue

            rendered_any = True
            for data in series_data:
                if data:
                    max_days_in_all_periods = max(max_days_in_all_periods, data[-1][0])

            fig = Figure(figsize=(12, 6), dpi=100)
            ax = fig.add_subplot(111)
            self._plot_compare_series_on_axes(
                ax,
                series_data,
                labels,
                colors,
                max_x_limit=max_days_in_all_periods or default_max_x,
            )
            ax.set_xlabel(x_label, fontsize=12)
            ax.set_ylabel(f"Cumulative Amount ({currency_symbol})", fontsize=12)
            ax.set_title(chart_title, fontsize=14, fontweight="bold")
            self._add_chart_canvas(fig)

        if not rendered_any:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found for the selected period")

    def _draw_expense_income_chart(
        self,
        expense_series: list[tuple[str, float]] | None,
        income_series: list[tuple[str, float]] | None,
        period: str,
        currency_symbol: str,
    ) -> None:
        reference_series = expense_series or income_series
        if reference_series is None:
            return

        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        x_values = [datetime.fromisoformat(date_str).replace(tzinfo=UTC) for date_str, _value in reference_series]
        x_nums = self._chart_date_nums(x_values)
        if expense_series is not None:
            expense_values = [value for _date_str, value in expense_series]
            ax.plot(x_nums, expense_values, color="crimson", linewidth=2, marker="o", markersize=4, label="Expense")
            self._annotate_balance_chart_extrema(
                ax,
                expense_series,
                x_nums,
                fig,
                period=period,
                currency_symbol=currency_symbol,
                point_color="crimson",
            )
        if income_series is not None:
            income_values = [value for _date_str, value in income_series]
            ax.plot(x_nums, income_values, color="forestgreen", linewidth=2, marker="o", markersize=4, label="Income")
            self._annotate_balance_chart_extrema(
                ax,
                income_series,
                x_nums,
                fig,
                period=period,
                currency_symbol=currency_symbol,
                point_color="forestgreen",
            )
        ax.set_xlabel("Period", fontsize=12)
        ax.set_ylabel(f"Amount ({currency_symbol})", fontsize=12)
        ax.set_title("Expense and Income", fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)
        ax.legend(loc="upper left", fontsize=10)
        self._format_chart_x_axis(ax, x_values, period)
        self._add_finance_expense_income_stats_box(ax, expense_series, income_series, currency_symbol)
        self._add_chart_canvas(fig)

    def _draw_expense_income_compare_last_years_chart(
        self,
        expense_names: set[str],
        income_names: set[str],
        period: str,
        currency_symbol: str,
        years_count: int,
    ) -> None:
        if self.db_manager is None:
            return

        transaction_rows = self.db_manager.get_all_transactions()
        year_start_month = self._compare_last_years_start_month
        year_start_day = self._compare_last_years_start_day
        self.label_compare_last.setText("Number of years:")

        all_series: list[list[tuple[int, float, str]]] = []
        all_labels: list[str] = []
        all_colors: list[str] = []
        max_period = 0

        if expense_names:
            expense_data, expense_labels, expense_colors = compute_period_flow_compare_last_years(
                transaction_rows,
                self.db_manager,
                years_count,
                expense_names,
                0,
                period,
                year_start_month=year_start_month,
                year_start_day=year_start_day,
            )
            for series, label, color in zip(expense_data, expense_labels, expense_colors, strict=False):
                if not series:
                    continue
                all_series.append(series)
                all_labels.append(f"Expense {label}")
                all_colors.append(color)
                max_period = max(max_period, series[-1][0])

        if income_names:
            income_data, income_labels, income_colors = compute_period_flow_compare_last_years(
                transaction_rows,
                self.db_manager,
                years_count,
                income_names,
                1,
                period,
                year_start_month=year_start_month,
                year_start_day=year_start_day,
            )
            for series, label, color in zip(income_data, income_labels, income_colors, strict=False):
                if not series:
                    continue
                all_series.append(series)
                all_labels.append(f"Income {label}")
                all_colors.append(color)
                max_period = max(max_period, series[-1][0])

        if not all_series:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found for the selected period")
            return

        if year_start_month == 1 and year_start_day == 1:
            chart_title = f"Expense and Income (Last {years_count} years comparison)"
        else:
            chart_title = (
                f"Expense and Income (Last {years_count} years from {year_start_day:02d}.{year_start_month:02d})"
            )

        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        pending_current: list[tuple[list[tuple[int, float, str]], str, str]] = []
        for series, color, label in zip(all_series, all_colors, all_labels, strict=False):
            if "(Current)" in label:
                pending_current.append((series, color, label))
                continue
            self._plot_compare_flow_series_line(
                ax,
                series,
                fig,
                color=color,
                label=label,
                period=period,
                currency_symbol=currency_symbol,
            )

        for series, color, label in pending_current:
            self._plot_compare_flow_series_line(
                ax,
                series,
                fig,
                color=color,
                label=label,
                period=period,
                currency_symbol=currency_symbol,
                linestyle="-",
                linewidth=3,
            )

        ax.set_xlim(1, max(max_period, 1))
        ticks = self._sparse_integer_ticks(max_period)
        ax.set_xticks(ticks)
        if period == "Months":
            month_labels = fiscal_period_month_labels_by_index(
                datetime.now(UTC).astimezone().date(),
                period,
                year_start_month=year_start_month,
                year_start_day=year_start_day,
            )
            ax.set_xticklabels([month_labels.get(tick, str(tick)) for tick in ticks], rotation=45, ha="right")
            ax.set_xlabel("Month", fontsize=12)
        else:
            ax.set_xlabel(period, fontsize=12)
        ax.set_ylabel(f"Amount ({currency_symbol})", fontsize=12)
        ax.set_title(chart_title, fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)
        ax.legend(loc="upper left", fontsize=9)
        self._add_chart_canvas(fig)

    def _fetch_transaction_rows(self, limit: int | None, offset: int) -> list[list[Any]]:
        """Fetch transaction rows with optional filters and pagination."""
        if self.db_manager is None:
            return []

        filter_params: dict[str, Any] | None = self._get_transactions_filter_params()
        if filter_params is not None:
            return self.db_manager.get_filtered_transactions(**filter_params, limit=limit, offset=offset)
        return self.db_manager.get_all_transactions(limit=limit, offset=offset)

    def _filter_by_category_from_table(self, category_value: str) -> None:
        """Filter transactions by category from table row.

        Args:

        - `category_value` (`str`): Category string from the table (may include emoji and "(Income)" suffix).

        """
        try:
            # Remove emoji prefix and "(Income)" suffix if present for database lookup
            clean_category_name: str = category_value
            # Remove emoji prefix (emoji is typically at the start, followed by a space)
            if (
                clean_category_name
                and clean_category_name[0] not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            ):
                # Find first letter/number character (skip emoji)
                for i, char in enumerate(clean_category_name):
                    if char in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
                        clean_category_name = clean_category_name[i:].lstrip()
                        break
            # Remove "(Income)" suffix
            clean_category_name = clean_category_name.replace(" (Income)", "")

            # Set the category in the filter combo box
            self.comboBox_filter_category.setCurrentText(clean_category_name)

            # Apply the filter
            self.apply_filter()
        except Exception as e:
            print(f"❌ Error filtering by category from table: {e}")

    def _finish_window_initialization(self) -> None:
        """Finish window initialization by showing the window."""
        if self._is_closing:
            return
        self.show()

        # Set focus to description field
        self.lineEdit_description.setFocus()

        self._clear_category_selection()

        # Start automatic exchange rate update with modal dialog
        # Use QTimer to delay startup update to ensure all initialization is complete
        QTimer.singleShot(1000, self._auto_update_exchange_rates_on_startup)  # 1 second delay

    def _focus_amount_and_select_text(self) -> None:
        """Set focus to amount field and select all text."""
        self.doubleSpinBox_amount.setFocus()
        self.doubleSpinBox_amount.selectAll()

    def _focus_description_and_select_text(self) -> None:
        """Set focus to description field and select all text."""
        self.lineEdit_description.setFocus()
        self.lineEdit_description.selectAll()

    def _get_categories_for_delegate(self) -> list[str]:
        """Get list of category names for the delegate dropdown.

        Returns:

        - `list[str]`: List of category names with icons and income markers.

        """
        if self.db_manager is None:
            return []

        try:
            categories: list = self.db_manager.get_all_categories()
            category_names: list[str] = []
            for category in categories:
                name: str = category[1]  # category name is at index 1
                category_type: int = category[2]  # category type is at index 2
                icon: str = category[3]  # category icon is at index 3

                # Add emoji prefix if icon exists
                if icon:
                    name = f"{icon} {name}"

                # Add "(Income)" suffix for income categories (type == 1)
                if category_type == 1:
                    name += " (Income)"

                category_names.append(name)

        except Exception as e:
            print(f"Error getting categories for delegate: {e}")
            return []
        return category_names

    def _get_checked_chart_categories(self) -> tuple[set[str], set[str], set[str]]:
        """Return checked expense names, income names, and their union."""
        expense_names: set[str] = set()
        income_names: set[str] = set()
        model = self.list_chart_categories.model()
        if not isinstance(model, QStandardItemModel):
            return expense_names, income_names, set()

        for row in range(model.rowCount()):
            item = model.item(row)
            if item is None or item.checkState() != Qt.CheckState.Checked:
                continue
            name = item.data(Qt.ItemDataRole.UserRole)
            category_type = item.data(Qt.ItemDataRole.UserRole + 1)
            if not name:
                continue
            name_str = str(name)
            if category_type == 0:
                expense_names.add(name_str)
            elif category_type == 1:
                income_names.add(name_str)

        return expense_names, income_names, expense_names | income_names

    def _get_currencies_for_delegate(self) -> list[str]:
        """Get list of currency codes for the delegate dropdown.

        Returns:

        - `list[str]`: List of currency codes.

        """
        if self.db_manager is None:
            return []

        try:
            currencies: list = self.db_manager.get_all_currencies()
            currency_codes: list[str] = []
            for currency in currencies:
                code: str = currency[1]  # currency code is at index 1
                currency_codes.append(code)
        except Exception as e:
            print(f"Error getting currencies for delegate: {e}")
            return []
        return currency_codes

    def _get_default_currency_symbol(self) -> str:
        if self.db_manager is None:
            return ""
        default_currency_info = self.db_manager.get_currency_by_code(self.db_manager.get_default_currency())
        return default_currency_info[2] if default_currency_info else ""

    def _get_or_create_category(self, category_name: str) -> int | None:
        """Get existing category ID or create new one.

        Args:

        - `category_name` (`str`): Category name.

        Returns:

        - `int | None`: Category ID or None if creation failed.

        """
        if self.db_manager is None:
            return None

        try:
            # Try to find existing category
            categories: list[str] = self.db_manager.get_categories_by_type(0)  # 0 = expense
            if category_name in categories:
                # Get category ID by name
                rows: list = self.db_manager.get_rows(
                    "SELECT _id FROM categories WHERE name = :name AND type = 0", {"name": category_name}
                )
                if rows:
                    return rows[0][0]
                return None

            # Create new category if not exists
            if self.db_manager.add_category(category_name, 0, ""):  # 0 = expense, empty icon
                # Get the ID of the newly created category
                rows: list = self.db_manager.get_rows(
                    "SELECT _id FROM categories WHERE name = :name AND type = 0", {"name": category_name}
                )
                if rows:
                    return rows[0][0]
                return None
        except Exception as e:
            print(f"Error creating category {category_name}: {e}")
            return None
        return None

    def _get_tags_for_delegate(self) -> list[str]:
        """Get list of unique tags for the delegate dropdown.

        Returns:

        - `list[str]`: Sorted list of unique tags.

        """
        if self.db_manager is None:
            return []

        try:
            transactions: list = self.db_manager.get_all_transactions()
            tags: set[str] = set()
            for transaction in transactions:
                tag: str = transaction[6]  # tag is at index 6
                if tag and tag.strip():
                    tags.add(tag.strip())

            return sorted(tags)
        except Exception as e:
            print(f"Error getting tags for delegate: {e}")
            return []

    def _get_transactions_filter_params(self) -> dict[str, Any] | None:
        """Return active filter parameters or None when no filter is applied."""
        if not self._transactions_filter_is_active():
            return None

        transaction_type: int | None = None
        if self.radioButton_filter_type_expense.isChecked():
            transaction_type = 0
        elif self.radioButton_filter_type_income.isChecked():
            transaction_type = 1

        category: str | None = self.comboBox_filter_category.currentText() or None
        currency: str | None = self.comboBox_filter_currency.currentText() or None
        description_filter: str | None = self.lineEdit_filter_description.text().strip() or None

        use_date_filter: bool = self.checkBox_use_date_filter.isChecked()
        date_from: str | None = self.dateEdit_filter_from.date().toString("yyyy-MM-dd") if use_date_filter else None
        date_to: str | None = self.dateEdit_filter_to.date().toString("yyyy-MM-dd") if use_date_filter else None

        return {
            "category_type": transaction_type,
            "category_name": category,
            "currency_code": currency,
            "date_from": date_from,
            "date_to": date_to,
            "description_filter": description_filter,
        }

    def _init_chart_controls(self) -> None:
        """Initialize Charts tab date range and comparison month combobox."""
        current_date: QDate = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addYears(-2))
        self.dateEdit_chart_to.setDate(current_date)

        self.comboBox_compare_same_months.clear()
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        self.comboBox_compare_same_months.addItems(months)
        self.comboBox_compare_same_months.setCurrentIndex(current_date.month() - 1)

        self.radioButton_type_of_chart_balance.setChecked(True)
        self.comboBox_chart_period.setCurrentIndex(1)

        self._populate_chart_categories_list()

    def _init_database(self) -> None:
        """Initialize database connection."""
        filename: Path = database_manager.DatabaseManager.resolve_db_path_with_fallback(
            Path(self._app_config["sqlite_finance"]),
            "finance",
        )

        # Try to open existing database first
        if filename.exists():
            try:
                temp_db_manager: database_manager.DatabaseManager = database_manager.DatabaseManager(str(filename))

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
            filename_str: str
            filename_str, _ = QFileDialog.getOpenFileName(
                self,
                "Open Database",
                str(filename.parent),
                "SQLite Database (*.db)",
            )
            if not filename_str:
                message_box.critical(self, "Error", "No database selected")
                msg = "No database selected"
                raise RuntimeError(msg)
            filename = Path(filename_str)

        try:
            self.db_manager = database_manager.DatabaseManager(str(filename))
            print(f"Database opened successfully: {filename}")
        except (OSError, RuntimeError, ConnectionError) as exc:
            message_box.critical(self, "Error", f"Failed to open database: {exc}")
            raise

    def _init_filter_controls(self) -> None:
        """Initialize filter controls."""
        current_date: QDate = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)
        self.checkBox_use_date_filter.setChecked(False)
        self._update_date_filter_visibility(enabled=False)

    def _initial_load(self) -> None:
        """Load essential data at startup (excluding exchange rates)."""
        if not self._validate_database_connection():
            print("Database connection not available for initial load")
            return

        # Load essential tables only (excluding exchange rates)
        self._load_essential_tables()
        self._update_comboboxes()
        self.update_filter_comboboxes()
        self.set_today_date()
        self.update_summary_labels()

        # Clear forms
        self._clear_all_forms()

        # Setup exchange rates controls
        self._setup_exchange_rates_controls()

    def _load_accounts_table(self) -> None:
        """Load accounts table."""
        accounts_data: list = self.db_manager.get_all_accounts()

        # Define colors for different account groups
        account_colors: dict[tuple[int, int], QColor] = {
            (0, 1): QColor(220, 255, 220),  # is_cash=0, is_liquid=1 - Light green
            (1, 1): QColor(255, 255, 200),  # is_cash=1, is_liquid=1 - Light yellow
            (0, 0): QColor(255, 220, 220),  # is_cash=0, is_liquid=0 - Light red
            (1, 0): QColor(255, 200, 255),  # is_cash=1, is_liquid=0 - Light purple
        }

        # Group accounts by (is_cash, is_liquid) and sort within groups
        account_groups: dict[tuple[int, int], list] = {
            (0, 1): [],  # is_cash=0, is_liquid=1
            (1, 1): [],  # is_cash=1, is_liquid=1
            (0, 0): [],  # is_cash=0, is_liquid=0
            (1, 0): [],  # is_cash=1, is_liquid=0
        }

        for row in accounts_data:
            # Raw data: [id, name, balance_cents, currency_code, is_liquid, is_cash]
            is_liquid: int = row[4]
            is_cash: int = row[5]
            group_key: tuple[int, int] = (is_cash, is_liquid)
            account_groups[group_key].append(row)

        # Sort each group alphabetically by name
        for group in account_groups.values():
            group.sort(key=lambda x: x[1].lower())  # Sort by name (case-insensitive)

        # Combine groups in the specified order
        accounts_transformed_data: list[list] = []
        for group_key in [(0, 1), (1, 1), (0, 0), (1, 0)]:
            color: QColor = account_colors[group_key]
            for row in account_groups[group_key]:
                currency_id: int = row[6]  # currency_id
                balance: float = self.db_manager.convert_from_minor_units(row[2], currency_id)
                liquid_str: str = "👍" if row[4] == 1 else "⛔"
                cash_str: str = "💵" if row[5] == 1 else "💳"
                transformed_row: list = [row[1], f"{balance:.2f}", row[3], liquid_str, cash_str, row[0], color]
                accounts_transformed_data.append(transformed_row)

        self.models["accounts"] = self._create_colored_table_model(
            accounts_transformed_data, self.table_config["accounts"][2]
        )
        accounts_model = self.models["accounts"]
        if accounts_model is None:
            return
        self._set_table_model_and_stretch_columns(self.tableView_accounts, accounts_model, stretch_last=False)

        # Set up amount delegate for the Balance column (index 1)
        self.accounts_balance_delegate = AmountDelegate(self.tableView_accounts, self.db_manager)
        self.tableView_accounts.setItemDelegateForColumn(1, self.accounts_balance_delegate)

        # Make accounts table non-editable and connect double-click signal
        self.tableView_accounts.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        # Reconnect double-click signal only when previously connected
        if self._account_double_click_connected:
            with contextlib.suppress(TypeError, RuntimeError):
                self.tableView_accounts.doubleClicked.disconnect(self._on_account_double_clicked)
            self._account_double_click_connected = False

        self.tableView_accounts.doubleClicked.connect(self._on_account_double_clicked)
        self._account_double_click_connected = True

    def _load_categories_table(self) -> None:
        """Load categories table."""

        def transform(rows: list) -> list[list]:
            result: list[list] = []
            for row in rows:
                type_str: str = "Expense" if row[2] == 0 else "Income"
                color: QColor = QColor(255, 200, 200) if row[2] == 0 else QColor(200, 255, 200)
                result.append([row[1], type_str, row[3], row[0], color])
            return result

        self._load_simple_colored_table("categories", self.db_manager.get_all_categories, transform)

    def _load_currencies_table(self) -> None:
        """Load currencies table."""

        def transform(rows: list) -> list[list]:
            result: list[list] = []
            for row in rows:
                color: QColor = QColor(255, 255, 220)
                result.append([row[1], row[2], row[3], row[0], color])
            return result

        self._load_simple_colored_table("currencies", self.db_manager.get_all_currencies, transform)

    def _load_currency_exchanges_table(self) -> None:
        """Load currency exchanges table."""
        if self.db_manager is None:
            return

        exchanges_data: list = self.db_manager.get_all_currency_exchanges()
        # Get default currency info once
        default_currency_id: int | None = None
        try:
            if self.db_manager is not None:
                default_currency_id = self.db_manager.get_default_currency_id()
        except Exception:
            default_currency_id = None
        exchanges_transformed_data: list[list] = []
        for row in exchanges_data:
            # Convert amounts and fees from minor units to major units
            from_currency_code: str = row[1]
            to_currency_code: str = row[2]

            # Get currency subdivisions for proper conversion
            from_subdivision: int = self.db_manager.get_currency_subdivision_by_code(from_currency_code)
            to_subdivision: int = self.db_manager.get_currency_subdivision_by_code(to_currency_code)

            # Convert amounts and fees
            amount_from: float = float(row[3]) / from_subdivision if row[3] is not None else 0.0
            amount_to: float = float(row[4]) / to_subdivision if row[4] is not None else 0.0
            fee: float = float(row[6]) / from_subdivision if row[6] is not None else 0.0

            # Calculate loss due to exchange rate difference (displayed in default currency, negative = loss)
            loss: float = 0.0
            today_loss: float = 0.0
            try:
                # Get currency IDs
                from_currency_info = self.db_manager.get_currency_by_code(from_currency_code)
                to_currency_info = self.db_manager.get_currency_by_code(to_currency_code)

                if from_currency_info and to_currency_info:
                    from_currency_id: int = from_currency_info[0]
                    to_currency_id: int = to_currency_info[0]
                    exchange_date: str = row[7]

                    # Calculate loss on exchange date
                    loss = self._calculate_exchange_loss(
                        from_currency_id,
                        to_currency_id,
                        amount_from,
                        amount_to,
                        default_currency_id,
                        fee,
                        use_date=exchange_date,
                    )

                    # Calculate today's loss
                    today_loss = self._calculate_exchange_loss(
                        from_currency_id, to_currency_id, amount_from, amount_to, default_currency_id, fee
                    )

            except Exception as e:
                # If there's any error in calculation, set losses to 0
                print(f"Error calculating losses for exchange {row[0]}: {e}")
                loss = 0.0
                today_loss = 0.0

            color: QColor = QColor(255, 240, 255)
            transformed_row: list = [
                row[1],  # from_code
                row[2],  # to_code
                f"{amount_from:.2f}",  # amount_from (converted)
                f"{amount_to:.2f}",  # amount_to (converted)
                f"{row[5]:.4f}",  # rate (already float)
                f"{fee:.2f}",  # fee (converted)
                row[7],  # date
                row[8] or "",  # description
                f"{loss:.2f}",  # loss (calculated)
                f"{today_loss:.2f}",  # today's loss (calculated)
                row[0],  # id
                color,
            ]
            exchanges_transformed_data.append(transformed_row)

        self.models["currency_exchanges"] = self._create_colored_table_model(
            exchanges_transformed_data, self.table_config["currency_exchanges"][2]
        )
        exchange_model = self.models["currency_exchanges"]
        if exchange_model is None:
            return
        self._set_table_model_and_stretch_columns(
            self.tableView_exchange,
            exchange_model,
            stretch_last=False,
        )

        # Disable all editing triggers
        self.tableView_exchange.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def _load_essential_tables(self) -> None:
        """Load essential tables at startup (excluding exchange rates for lazy loading)."""
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

            # Connect auto-save signals for loaded tables
            self._connect_table_auto_save_signals()

            # Update accounts balance display
            self._update_accounts_balance_display()

        except Exception as e:
            print(f"Error loading essential tables: {e}")
            message_box.warning(self, "Database Error", f"Failed to load essential tables: {e}")

    def _load_more_transactions(self) -> None:
        """Append the next page of transactions when scrolling to the bottom."""
        if self.show_all_transactions or self.db_manager is None or self.models["transactions"] is None:
            return

        def append_rows(rows: list) -> None:
            transformed_data: list[list] = self._transform_transaction_data(rows, append_state=True)
            proxy = cast("QSortFilterProxyModel", self.models["transactions"])
            source_model = cast("QStandardItemModel", proxy.sourceModel())
            self._append_transformed_rows_to_model(source_model, transformed_data)

        self._transactions_pagination.load_more(
            load_more_count=self.transactions_load_more_count,
            fetch_rows=self._fetch_transaction_rows,
            append_rows=append_rows,
        )

    def _load_simple_colored_table(
        self,
        table_name: str,
        get_data_fn: Callable[[], list],
        transform_fn: Callable[[list], list],
    ) -> None:
        """Load a table with colored model: fetch data, transform, create model, set view.

        Args:

        - `table_name` (`str`): Key in table_config and models.
        - `get_data_fn` (`Callable[[], list]`): No-arg callable that returns raw rows.
        - `transform_fn` (`Callable[[list], list]`): Maps raw rows to display rows (with color).

        """
        data = get_data_fn()
        transformed = transform_fn(data)
        view, _model_key, headers = self.table_config[table_name]
        table_model = self._create_colored_table_model(transformed, headers)
        if table_model is None:
            return
        self.models[table_name] = table_model
        self._set_table_model_and_stretch_columns(view, table_model)

    def _load_transactions_page(self, *, reset: bool = True) -> None:
        """Load the first page of transactions (with optional active filters)."""
        if self.db_manager is None:
            return

        if reset:
            self._reset_transactions_pagination_state()

        limit: int | None = None if self.show_all_transactions else self.count_transactions_to_show
        rows: list = self._fetch_transaction_rows(limit, 0)
        transformed_data: list[list] = self._transform_transaction_data(rows, append_state=False)

        self.models["transactions"] = self._create_transactions_table_model(
            transformed_data, self.table_config["transactions"][2]
        )
        self.tableView_transactions.setModel(self.models["transactions"])
        self._setup_transactions_table_delegates()
        self._setup_transactions_table_column_widths()
        self._connect_transaction_selection_signal()

        self._transactions_pagination.record_first_page(
            len(rows),
            limit,
            pagination_enabled=not self.show_all_transactions,
        )
        self._connect_table_auto_save_signals()

    def _load_transactions_table(self) -> None:
        """Load transactions table."""
        self._load_transactions_page(reset=True)

    def _mark_categories_changed(self) -> None:
        """Mark that category data has changed and needs refresh."""
        # No specific action needed for categories as they load immediately

    def _mark_currencies_changed(self) -> None:
        """Mark that currency data has changed and needs refresh."""
        # No specific action needed for currencies as they load immediately

    def _mark_default_currency_changed(self) -> None:
        """Mark that default currency has changed and needs refresh."""
        # No specific action needed as this affects multiple areas that reload immediately

    def _mark_summary_dirty(self) -> None:
        """Mark reports summary as needing recomputation."""
        self._summary_dirty = True

    # Lazy loading change markers
    def _mark_transactions_changed(self) -> None:
        """Mark that transaction data has changed and needs refresh."""
        # No specific action needed for transactions as they load immediately

    def _on_account_double_clicked(self, index: QModelIndex) -> None:
        """Handle double-click on accounts table.

        Args:

        - `index` (`QModelIndex`): The clicked index.

        """
        # Prevent multiple dialogs from opening
        if hasattr(self, "_account_edit_dialog_open") and self._account_edit_dialog_open:
            return

        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # Get the row ID from vertical header
            proxy_model: QSortFilterProxyModel | None = self.models["accounts"]
            if proxy_model is None:
                return

            source_model = proxy_model.sourceModel()
            if source_model is None or not isinstance(source_model, QStandardItemModel):
                return

            row_id_item = source_model.verticalHeaderItem(index.row())
            if row_id_item is None:
                return

            account_id: int = int(row_id_item.text())

            # Get account data
            account_data = self.db_manager.get_account_by_id(account_id)
            if not account_data:
                message_box.warning(self, "Error", "Account not found")
                return

            # Prepare account data for dialog
            currency_id: int = account_data[6]  # currency_id
            account_dict: dict[str, str | float | bool | int] = {
                "id": account_data[0],
                "name": account_data[1],
                "balance": self.db_manager.convert_from_minor_units(account_data[2], currency_id),
                "currency_code": account_data[3],
                "is_liquid": account_data[4] == 1,
                "is_cash": account_data[5] == 1,
            }

            # Get currency codes for dialog
            currencies: list[str] = [row[1] for row in self.db_manager.get_all_currencies()]

            # Show edit dialog
            self._account_edit_dialog_open = True
            dialog: AccountEditDialog = AccountEditDialog(self, account_dict, currencies)
            result_code: int = dialog.exec()
            self._account_edit_dialog_open = False

            if result_code == QDialog.DialogCode.Accepted:
                result: dict = dialog.get_result()

                if result["action"] == "save":
                    # Update account
                    currency_info = self.db_manager.get_currency_by_code(result["currency_code"])
                    if not currency_info:
                        message_box.warning(self, "Error", "Currency not found")
                        return

                    currency_id: int = currency_info[0]

                    success: bool = self.db_manager.update_account(
                        account_id,
                        result["name"],
                        result["balance"],
                        currency_id,
                        is_liquid=result["is_liquid"],
                        is_cash=result["is_cash"],
                    )

                    if success:
                        # Save current column widths before update
                        column_widths: list[int] = self._save_table_column_widths(self.tableView_accounts)

                        self.update_all()

                        # Restore column widths after update
                        self._restore_table_column_widths(self.tableView_accounts, column_widths)

                        return  # Exit the method to prevent reopening the dialog
                    message_box.warning(self, "Error", "Failed to update account")

                elif result["action"] == "delete":
                    # Save current column widths before update
                    column_widths: list[int] = self._save_table_column_widths(self.tableView_accounts)

                    # Delete account
                    success: bool = self.db_manager.delete_account(account_id)
                    if success:
                        self.update_all()

                        # Restore column widths after update
                        self._restore_table_column_widths(self.tableView_accounts, column_widths)

                        message_box.information(self, "Success", "Account deleted successfully")
                        return  # Exit the method to prevent reopening the dialog
                    message_box.warning(self, "Error", "Failed to delete account")
            elif result_code == QDialog.DialogCode.Rejected:
                # Dialog was cancelled, do nothing and return
                return

        except Exception as e:
            self._account_edit_dialog_open = False
            message_box.warning(self, "Error", f"Failed to edit account: {e}")

    def _on_add_revision_clicked(
        self,
        currency_id: int,
        diff_minor: int,
        table: QTableWidget,
    ) -> None:
        """Add balancing revision transaction for selected currency."""
        if self.db_manager is None:
            return

        currency_info = self.db_manager.get_currency_by_id(currency_id)
        if not currency_info:
            message_box.warning(self, "Revision", "Currency not found")
            return
        currency_code = currency_info[0]

        # diff = accounts - journal; to make diff zero:
        # if diff > 0 => add income by diff
        # if diff < 0 => add expense by abs(diff)
        is_income = diff_minor > 0
        category_name = "Revision Income" if is_income else "Revision Expense"
        category_id = self.db_manager.get_id("categories", "name", category_name)
        if category_id is None:
            message_box.warning(self, "Revision", f"Category '{category_name}' not found")
            return

        amount_major = self.db_manager.convert_from_minor_units(abs(diff_minor), currency_id)
        today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
        description = f"Revision for {currency_code}"
        success = self.db_manager.add_transaction(
            amount_major, description, category_id, currency_id, today, "revision"
        )

        if not success:
            message_box.warning(self, "Revision", "Failed to add revision transaction")
            return

        self._refresh_test_balance_dialog_table(table)

    def _on_autocomplete_selected(self, text: str) -> None:
        """Handle autocomplete selection and populate form fields.

        Args:

        - `text` (`str`): The selected autocomplete text.

        """
        if not text:
            return

        # Save current date before populating form
        current_date: QDate = self.dateEdit.date()

        # Set the selected text
        self.lineEdit_description.setText(text)

        # Try to populate other fields based on the selected description
        self._populate_form_from_description(text)

        # Restore the original date (this is redundant now, but kept for safety)
        self.dateEdit.setDate(current_date)

        # Set focus to amount field and select all text after a short delay
        # This ensures form population is complete before focusing
        QTimer.singleShot(100, self._focus_amount_and_select_text)

    def _on_balance_check_clicked(self) -> None:
        """Show sum of accounts, accounting balance (transactions + exchanges), and difference in current currency."""
        if not self._validate_database_connection() or self.db_manager is None:
            return

        worker = getattr(self, "_balance_check_worker", None)
        if worker is not None and worker.isRunning():
            return

        try:
            db_filename = _require_db_filename_for_worker(self.db_manager)
        except DbFilenameUnavailableForWorkerThreadError:
            message_box.warning(self, "Error", "Database path is not available for balance check.")
            return

        self._balance_check_toast = toast_countdown_notification.ToastCountdownNotification("Checking balance…")
        self._balance_check_toast.start_countdown()

        self._balance_check_worker = BalanceCheckWorker(db_filename)
        self._balance_check_worker.check_completed.connect(self._on_balance_check_completed)
        self._balance_check_worker.check_failed.connect(self._on_balance_check_failed)
        self._balance_check_worker.finished.connect(self._cleanup_balance_check_worker)
        self._balance_check_worker.start()

    def _on_balance_check_completed(self, result: BalanceCheckResult) -> None:
        """Show balance dialog after background check succeeds."""
        self._close_balance_check_toast()
        self._show_test_balance_dialog(
            default_currency_symbol=result.default_currency_symbol,
            accounts_balance=result.accounts_balance,
            accounting_balance_latest=result.accounting_balance_latest,
            difference_latest=result.difference_latest,
            accounting_balance_historical=result.accounting_balance,
            difference_historical=result.difference,
            natural_rows=result.natural_rows,
        )

    def _on_balance_check_failed(self, error_message: str) -> None:
        """Handle balance check worker failure."""
        self._close_balance_check_toast()
        print(f"Error in test balance: {error_message}")
        message_box.warning(self, "Error", f"Error: {error_message}")

    def _on_check_completed(self, currencies_to_process: list) -> None:
        """Handle successful completion of exchange rate check.

        Args:

        - `currencies_to_process` (`list`): List of currencies that need processing.

        """
        if hasattr(self, "check_progress_dialog"):
            self.check_progress_dialog.close()

        # If no currencies need processing, inform user
        if not currencies_to_process:
            message_box.information(
                self,
                "No Updates Needed",
                "All exchange rates are up to date.",
            )
            print("✅ All exchange rates are up to date.")
            return

        # Calculate totals
        total_missing: int = sum(len(records["missing_dates"]) for _, _, records in currencies_to_process)
        total_updates: int = sum(len(records["existing_records"]) for _, _, records in currencies_to_process)
        currencies_text: str = ", ".join([curr[1] for curr in currencies_to_process])

        # Determine check mode for display
        check_from_first_transaction: bool = getattr(self.exchange_rate_checker, "check_from_first_transaction", True)
        check_mode: str = "from first transaction" if check_from_first_transaction else "from last exchange rate"

        # Show summary and ask for confirmation
        reply = message_box.question(
            self,
            "Update Exchange Rates",
            f"Check completed ({check_mode})\n\n"
            f"Found {len(currencies_to_process)} currencies to process:\n"
            f"{currencies_text}\n\n"
            f"Missing records to add: {total_missing}\n"
            f"Existing records to update: {total_updates}\n"
            f"Total operations: {total_missing + total_updates}\n\n"
            f"This may take several minutes for large date ranges.\n"
            f"Do you want to proceed with downloading from yfinance?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Start the update process
        self._start_exchange_rate_update(currencies_to_process)

    def _on_check_failed(self, error_message: str) -> None:
        """Handle check failure.

        Args:

        - `error_message` (`str`): The error message.

        """
        if hasattr(self, "check_progress_dialog"):
            self.check_progress_dialog.close()

        message_box.critical(self, "Check Failed", f"Failed to check exchange rates:\n{error_message}")
        print(f"❌ Check failed: {error_message}")

    def _on_check_progress_updated(self, message: str) -> None:
        """Handle progress updates from checker worker.

        Args:

        - `message` (`str`): Progress update message.

        """
        print(message)
        if hasattr(self, "check_progress_dialog"):
            self.check_progress_dialog.setText(message)

    def _on_currency_started(self, currency_code: str) -> None:
        """Handle currency processing start.

        Args:

        - `currency_code` (`str`): The currency code being processed.

        """
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.setText(f"Processing {currency_code}...")

    def _on_description_text_edited(self, text: str) -> None:
        """Update autocomplete filter and sorting when description text changes."""
        self.description_completer_proxy.set_filter_text(text)

        if text:
            self.description_completer.setCompletionPrefix(text)
            self.description_completer.complete()
        else:
            self.description_completer_proxy.set_filter_text("")
            popup = self.description_completer.popup()
            if popup is not None and popup.isVisible():
                popup.hide()

    @requires_database()
    def _on_exchange_table_double_clicked(self, index: QModelIndex) -> None:
        """Handle double-click on exchange table to open edit dialog.

        Args:

        - `index` (`QModelIndex`): Model index of the clicked cell.

        """
        # Prevent opening multiple dialogs
        if self._exchange_dialog_open:
            return

        if not index.isValid():
            return

        model = self.tableView_exchange.model()
        if not model:
            return

        # Get the row data
        row = index.row()

        # Get exchange ID from vertical header
        exchange_id = model.headerData(row, Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole)
        if not exchange_id:
            return

        # Get all row data
        from_currency = model.data(model.index(row, 0)) or ""
        to_currency = model.data(model.index(row, 1)) or ""
        amount_from_text = model.data(model.index(row, 2)) or "0"
        amount_to_text = model.data(model.index(row, 3)) or "0"
        rate_text = model.data(model.index(row, 4)) or "0"
        fee_text = model.data(model.index(row, 5)) or "0"
        date = model.data(model.index(row, 6)) or ""
        description = model.data(model.index(row, 7)) or ""

        # Parse values
        try:
            amount_from = float(str(amount_from_text))
            amount_to = float(str(amount_to_text))
            rate = float(str(rate_text))
            fee = float(str(fee_text))
        except (ValueError, TypeError):
            message_box.warning(self, "Error", "Failed to parse exchange values")
            return

        # Get currencies list from combobox
        currencies = [self.comboBox_exchange_from.itemText(i) for i in range(self.comboBox_exchange_from.count())]

        # Prepare exchange data
        exchange_data = {
            "id": exchange_id,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount_from": amount_from,
            "amount_to": amount_to,
            "rate": rate,
            "fee": fee,
            "date": date,
            "description": description,
        }

        # Set flag to prevent multiple dialogs
        self._exchange_dialog_open = True

        try:
            # Open dialog
            dialog = ExchangeEditDialog(self, exchange_data, currencies)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                result = dialog.get_result()

                # Update the exchange record
                if self.db_manager.update_currency_exchange_full(
                    int(exchange_id),
                    result["from_currency"],
                    result["to_currency"],
                    result["amount_from"],
                    result["amount_to"],
                    result["rate"],
                    result["fee"],
                    result["date"],
                    result["description"],
                ):
                    # Save current column widths before update
                    column_widths: list[int] = self._save_table_column_widths(self.tableView_exchange)

                    # Refresh the table
                    self._load_currency_exchanges_table()

                    # Restore column widths after update
                    self._restore_table_column_widths(self.tableView_exchange, column_widths)
                else:
                    message_box.warning(self, "Error", "Failed to update exchange record")
        finally:
            # Reset flag when dialog is closed
            self._exchange_dialog_open = False

    def _on_exchange_update_finished_error(self, error_message: str, *, startup: bool = False) -> None:
        """Handle error completion of exchange rate update (startup or normal).

        Args:

        - `error_message` (`str`): The error message.
        - `startup` (`bool`): If True, use startup dialog and auto-close; else
        close progress_dialog and show QMessageBox.

        """
        if startup:
            print(f"❌ [Startup] Update failed: {error_message}")
            if hasattr(self, "startup_progress_dialog"):
                self.startup_progress_dialog.setText(f"❌ Update failed:\n{error_message}")
                QTimer.singleShot(4000, self._cleanup_startup_dialog)
            else:
                self._cleanup_startup_dialog()
        else:
            if hasattr(self, "progress_dialog"):
                self.progress_dialog.close()
            message_box.critical(self, "Update Error", f"Failed to update exchange rates:\n{error_message}")
            print(f"❌ {error_message}")

    def _on_exchange_update_finished_success(
        self, processed_count: int, total_operations: int, *, startup: bool = False
    ) -> None:
        """Handle successful completion of exchange rate update (startup or normal).

        Args:

        - `processed_count` (`int`): Number of successfully processed operations.
        - `total_operations` (`int`): Total number of operations.
        - `startup` (`bool`): If True, use startup dialog and auto-close; else
        close progress_dialog and show QMessageBox.

        """
        id_exchange_rates_tab: int = 4

        def _reload_if_tab_active() -> None:
            self._mark_exchange_rates_changed()
            if self.tabWidget.currentIndex() == id_exchange_rates_tab:
                self.load_exchange_rates_table()

        if startup:
            if processed_count > 0:
                has_exchange_rates: bool = self.db_manager.has_exchange_rates_data() if self.db_manager else True
                strategy: str = "from last exchange rate date" if has_exchange_rates else "from first transaction date"
                print(
                    "✅ [Startup] Successfully processed "
                    f"{processed_count} out of {total_operations} "
                    f"exchange rate operations ({strategy})"
                )
                if hasattr(self, "startup_progress_dialog"):
                    self.startup_progress_dialog.setText(
                        f"✅ Exchange rates updated successfully!\n"
                        f"Processed {processed_count} out of {total_operations} operations\n"
                        f"Strategy: {strategy}"
                    )
                    QTimer.singleShot(2000, self._cleanup_startup_dialog)
                else:
                    self._cleanup_startup_dialog()
                _reload_if_tab_active()

                unresolved = {}
                if hasattr(self, "startup_exchange_rate_worker") and hasattr(
                    self.startup_exchange_rate_worker, "unresolved_rates"
                ):
                    unresolved = getattr(self.startup_exchange_rate_worker, "unresolved_rates", {}) or {}
                if unresolved:
                    preview_limit = 50

                    def _show_unresolved() -> None:
                        lines = ["No exchange rate data for some dates:", ""]
                        for code in sorted(unresolved):
                            dates = sorted(set(unresolved[code]))
                            preview = ", ".join(dates[:preview_limit])
                            suffix = "" if len(dates) <= preview_limit else f" … (+{len(dates) - preview_limit} more)"
                            lines.append(f"{code}: {preview}{suffix}")
                        message_box.warning(self, "Missing Exchange Rates", "\n".join(lines))

                    QTimer.singleShot(2100, _show_unresolved)
            else:
                print("ℹ️ [Startup] No exchange rate records were processed")  # noqa: RUF001
                if hasattr(self, "startup_progress_dialog"):
                    self.startup_progress_dialog.setText(
                        "ℹ️ No exchange rate records were processed"  # noqa: RUF001
                    )
                    QTimer.singleShot(2000, self._cleanup_startup_dialog)
                else:
                    self._cleanup_startup_dialog()
        else:
            if hasattr(self, "progress_dialog"):
                self.progress_dialog.close()
            if processed_count > 0:
                message_box.information(
                    self,
                    "Update Complete",
                    "Successfully completed exchange rate update:\n"
                    f"• Processed {processed_count} out of {total_operations} operations from yfinance",
                )
                _reload_if_tab_active()
            else:
                message_box.information(
                    self,
                    "Update Complete",
                    "No exchange rate records were processed.",
                )

            unresolved = {}
            if hasattr(self, "exchange_rate_worker") and hasattr(self.exchange_rate_worker, "unresolved_rates"):
                unresolved = getattr(self.exchange_rate_worker, "unresolved_rates", {}) or {}
            if unresolved:
                preview_limit = 50
                lines = ["No exchange rate data for some dates:", ""]
                for code in sorted(unresolved):
                    dates = sorted(set(unresolved[code]))
                    preview = ", ".join(dates[:preview_limit])
                    suffix = "" if len(dates) <= preview_limit else f" … (+{len(dates) - preview_limit} more)"
                    lines.append(f"{code}: {preview}{suffix}")
                message_box.warning(self, "Missing Exchange Rates", "\n".join(lines))

    def _on_net_negative_revisions_clicked(
        self,
        currency_id: int,
        diff_minor: int,
        table: QTableWidget,
    ) -> None:
        """Net positive diff by removing recent Revision Expense rows and optional remainder."""
        if self.db_manager is None:
            return

        currency_info = self.db_manager.get_currency_by_id(currency_id)
        if not currency_info:
            message_box.warning(self, "Revision", "Currency not found")
            return
        currency_code = currency_info[0]

        revision_rows = self.db_manager.get_revision_expense_transactions(currency_id)
        plan = plan_revision_expense_consolidation_for_positive_diff(revision_rows, diff_minor)
        if plan is None:
            message_box.warning(self, "Revision", "Cannot net revisions for this currency")
            return

        ids_to_delete, remainder_minor = plan
        ids_set = set(ids_to_delete)
        deleted_amounts: list[str] = []
        for row in revision_rows:
            if len(row) < MIN_TRANSACTION_ROW_LENGTH:
                continue
            if int(row[0]) not in ids_set:
                continue
            amount_major = self.db_manager.convert_from_minor_units(int(row[1]), currency_id)
            deleted_amounts.append(f"{amount_major:,.2f}")

        if remainder_minor > 0:
            remainder_major = self.db_manager.convert_from_minor_units(remainder_minor, currency_id)
            remainder_line = f"Add Revision Expense {remainder_major:,.2f} {currency_code}."
        else:
            remainder_line = "No new revision will be added."

        delete_summary = ", ".join(deleted_amounts)
        reply = message_box.question(
            self,
            "Net revisions",
            f"Delete {len(ids_to_delete)} revision(s) ({delete_summary} {currency_code}) "
            f"to net the balance difference?\n{remainder_line}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        category_id = self.db_manager.get_id("categories", "name", "Revision Expense")
        if category_id is None:
            message_box.warning(self, "Revision", "Category 'Revision Expense' not found")
            return

        for transaction_id in ids_to_delete:
            if not self.db_manager.delete_transaction(transaction_id):
                message_box.warning(self, "Revision", f"Failed to delete transaction {transaction_id}")
                return

        if remainder_minor > 0:
            today = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")
            description = f"Revision for {currency_code}"
            amount_major = self.db_manager.convert_from_minor_units(remainder_minor, currency_id)
            if not self.db_manager.add_transaction(
                amount_major, description, category_id, currency_id, today, "revision"
            ):
                message_box.warning(self, "Revision", "Failed to add consolidated revision")
                return

        self._refresh_test_balance_dialog_table(table)

    def _on_progress_updated(self, message: str) -> None:
        """Handle progress updates from worker.

        Args:

        - `message` (`str`): Progress update message.

        """
        print(message)
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.setText(message)

    def _on_rate_added(self, currency_code: str, rate: float, date_str: str) -> None:
        """Handle successful rate addition.

        Args:

        - `currency_code` (`str`): The currency code.
        - `rate` (`float`): The exchange rate.
        - `date_str` (`str`): The date string.

        """
        print(f"✅ Added {currency_code}/USD rate: {rate:.6f} for {date_str}")

    def _on_report_build_completed(self, result: ReportBuildResult) -> None:
        """Apply report data to the reports table after background computation."""
        self._close_report_build_toast()
        try:
            self._apply_report_build_result(result)
        except Exception as e:
            message_box.warning(self, "Report Error", f"Failed to display report: {e}")

    def _on_report_build_failed(self, error_message: str) -> None:
        """Handle report build worker failure."""
        self._close_report_build_toast()
        message_box.warning(self, "Report Error", f"Failed to generate report: {error_message}")

    def _on_startup_check_completed(self, currencies_to_process: list) -> None:
        """Handle successful completion of startup exchange rate check.

        Args:

        - `currencies_to_process` (`list`): List of currencies that need processing.

        """
        # If no currencies need processing, cleanup and exit
        if not currencies_to_process:
            print("✅ [Startup] All exchange rates are up to date.")
            if hasattr(self, "startup_progress_dialog"):
                self.startup_progress_dialog.setText("✅ All exchange rates are up to date!")
                # Auto-close after 1 second
                QTimer.singleShot(1000, self._cleanup_startup_dialog)
            else:
                self._cleanup_startup_dialog()
            return

        # Calculate totals
        total_missing: int = sum(len(records["missing_dates"]) for _, _, records in currencies_to_process)
        total_updates: int = sum(len(records["existing_records"]) for _, _, records in currencies_to_process)
        currencies_text: str = ", ".join([curr[1] for curr in currencies_to_process])

        # Determine the strategy used
        has_exchange_rates: bool = self.db_manager.has_exchange_rates_data() if self.db_manager else False
        strategy: str = "from last exchange rate date" if has_exchange_rates else "from first transaction date"

        print(f"🔄 [Startup] Strategy: Update {strategy}")
        print(f"📊 [Startup] Found {len(currencies_to_process)} currencies to process: {currencies_text}")
        print(f"📊 [Startup] Missing records: {total_missing}, Updates: {total_updates}")

        # Update dialog text
        if hasattr(self, "startup_progress_dialog"):
            self.startup_progress_dialog.setText(
                f"Downloading exchange rates {strategy}...\n"
                f"Processing {len(currencies_to_process)} currencies: {currencies_text}\n"
                f"Total operations: {total_missing + total_updates}"
            )

        # Start the update process
        self._start_startup_exchange_rate_update(currencies_to_process)

    def _on_startup_check_failed(self, error_message: str) -> None:
        """Handle startup check failure.

        Args:

        - `error_message` (`str`): The error message.

        """
        print(f"❌ [Startup] Check failed: {error_message}")

        if hasattr(self, "startup_progress_dialog"):
            self.startup_progress_dialog.setText(f"❌ Check failed:\n{error_message}")
            # Auto-close after 3 seconds
            QTimer.singleShot(3000, self._cleanup_startup_dialog)
        else:
            self._cleanup_startup_dialog()

    def _on_startup_check_progress_updated(self, message: str) -> None:
        """Handle progress updates from startup checker worker.

        Args:

        - `message` (`str`): Progress update message.

        """
        print(f"[Startup] {message}")
        if hasattr(self, "startup_progress_dialog"):
            # Update dialog text with current progress
            self.startup_progress_dialog.setText(f"Checking exchange rates...\n{message}")

    def _on_startup_currency_started(self, currency_code: str) -> None:
        """Handle currency processing start for startup.

        Args:

        - `currency_code` (`str`): The currency code being processed.

        """
        print(f"[Startup] Processing {currency_code}...")
        if hasattr(self, "startup_progress_dialog"):
            current_text: str = self.startup_progress_dialog.text()
            lines: list[str] = current_text.split("\n")
            max_lines = 2
            if len(lines) >= max_lines:
                main_info: str = "\n".join(lines[:3])  # Keep first 3 lines
                self.startup_progress_dialog.setText(f"{main_info}\n\n🔄 Processing {currency_code}...")

    def _on_startup_dialog_cancelled(self) -> None:
        """Handle cancel button click in startup dialog."""
        print("🚫 [Startup] User cancelled exchange rate update")

        # Stop checker if running
        if hasattr(self, "startup_exchange_rate_checker") and self.startup_exchange_rate_checker.isRunning():
            self.startup_exchange_rate_checker.stop()
            self.startup_exchange_rate_checker.wait(2000)  # Wait up to 2 seconds

        # Stop worker if running
        if hasattr(self, "startup_exchange_rate_worker") and self.startup_exchange_rate_worker.isRunning():
            self.startup_exchange_rate_worker.stop()
            self.startup_exchange_rate_worker.wait(2000)  # Wait up to 2 seconds

        self._cleanup_startup_dialog()

    def _on_startup_progress_updated(self, message: str) -> None:
        """Handle progress updates from startup worker.

        Args:

        - `message` (`str`): Progress update message.

        """
        print(f"[Startup] {message}")
        if hasattr(self, "startup_progress_dialog"):
            # Keep the main info and update with current progress
            current_text: str = self.startup_progress_dialog.text()
            # Extract the first two lines (main info) and add current progress
            lines: list[str] = current_text.split("\n")
            max_lines = 2
            if len(lines) >= max_lines:
                main_info: str = "\n".join(lines[:3])  # Keep first 3 lines
                self.startup_progress_dialog.setText(f"{main_info}\n\n{message}")
            else:
                self.startup_progress_dialog.setText(f"Downloading exchange rates...\n{message}")

    def _on_startup_rate_added(self, currency_code: str, rate: float, date_str: str) -> None:
        """Handle successful rate addition for startup.

        Args:

        - `currency_code` (`str`): The currency code.
        - `rate` (`float`): The exchange rate.
        - `date_str` (`str`): The date string.

        """
        print(f"✅ [Startup] Added {currency_code}/USD rate: {rate:.6f} for {date_str}")

    def _on_startup_update_finished_error(self, error_message: str) -> None:
        """Handle error completion of startup update."""
        self._on_exchange_update_finished_error(error_message, startup=True)

    def _on_startup_update_finished_success(self, processed_count: int, total_operations: int) -> None:
        """Handle successful completion of startup update."""
        self._on_exchange_update_finished_success(processed_count, total_operations, startup=True)

    def _on_transaction_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle transaction selection change and copy data to form fields (except tag).

        Args:

        - `current` (`QModelIndex`): The current selected index.
        - `_previous` (`QModelIndex`): The previously selected index.

        """
        # Don't copy data if right click is in progress
        if hasattr(self, "_right_click_in_progress") and self._right_click_in_progress:
            return

        if not current.isValid():
            return

        if self.db_manager is None:
            return

        try:
            # Get the proxy model and source model
            proxy_model: QSortFilterProxyModel | None = self.models["transactions"]
            if proxy_model is None:
                return

            source_model = proxy_model.sourceModel()
            if source_model is None or not isinstance(source_model, QStandardItemModel):
                return

            # Get the row ID from vertical header
            row_id_item = source_model.verticalHeaderItem(current.row())
            if row_id_item is None:
                return

            transaction_id: int = int(row_id_item.text())

            # Get transaction data from database
            transaction_data = self.db_manager.get_transaction_by_id(transaction_id)
            if not transaction_data:
                return

            amount_cents: int = transaction_data[1]
            description: str = transaction_data[2]
            category_id: int = transaction_data[3]
            currency_id: int = transaction_data[4]

            # Get category and currency information
            category_data = self.db_manager.get_category_by_id(category_id)
            currency_data = self.db_manager.get_currency_by_id(currency_id)

            if not category_data or not currency_data:
                return

            # Convert amount from minor units to display format
            amount: float = self.db_manager.convert_from_minor_units(amount_cents, currency_id)

            # Populate form fields
            self.lineEdit_description.setText(description)
            self.doubleSpinBox_amount.setValue(amount)

            # Set currency in comboBox
            currency_code: str = currency_data[0]  # currency_code
            index: int = self.comboBox_currency.findText(currency_code)
            if index >= 0:
                self.comboBox_currency.setCurrentIndex(index)

            # Set category label
            category_name: str = category_data[1]  # name
            category_type: int = category_data[2]  # type
            display_text: str = f"{category_name} ({'Income' if category_type == 1 else 'Expense'})"
            self.label_category_now.setText(display_text)

            # Select category in listView_categories
            self._select_category_by_id(category_id)

        except Exception as e:
            print(f"Error copying transaction data to form: {e}")

    def _on_transactions_scroll(self, value: int) -> None:
        """Trigger loading more transactions when scrolled near the bottom."""
        scrollbar = self.tableView_transactions.verticalScrollBar()
        on_scroll_load_more(value, scrollbar.maximum(), self._load_more_transactions)

    def _on_update_finished_error(self, error_message: str) -> None:
        """Handle error completion."""
        self._on_exchange_update_finished_error(error_message, startup=False)

    def _on_update_finished_success(self, processed_count: int, total_operations: int) -> None:
        """Handle successful completion."""
        self._on_exchange_update_finished_success(processed_count, total_operations, startup=False)

    def _open_text_input_dialog(
        self,
        default_date: QDate,
        *,
        initial_text: str | None = None,
        focus_text_on_show: bool = True,
    ) -> None:
        """Show purchase table dialog and process accepted input."""
        if self.db_manager is None:
            return

        default_currency: str | None = self.db_manager.get_default_currency()
        currency_symbol = ""
        if default_currency:
            default_currency_info = self.db_manager.get_currency_by_code(default_currency)
            if default_currency_info:
                currency_symbol = default_currency_info[2]

        dialog = TextInputDialog(
            self,
            default_date=default_date,
            initial_text=initial_text,
            focus_text_on_show=focus_text_on_show,
            currency_symbol=currency_symbol,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        items = dialog.get_items()
        date = dialog.get_date()
        if items and date:
            self._process_purchase_items(items, date)

    def _plot_compare_flow_series_line(
        self,
        ax: Any,
        series: list[tuple[int, float, str]],
        fig: Figure,
        *,
        color: str,
        label: str,
        period: str,
        currency_symbol: str,
        linestyle: str = "--",
        linewidth: float = 2,
    ) -> None:
        x_values = [period_index for period_index, _value, _bucket_end in series]
        y_values = [value for _period_index, value, _bucket_end in series]
        self._plot_compare_line(
            ax,
            x_values,
            y_values,
            color=color,
            label=label,
            linestyle=linestyle,
            linewidth=linewidth,
            annotate_last_point=False,
        )
        self._annotate_compare_flow_chart_extrema(
            ax,
            series,
            fig,
            period=period,
            currency_symbol=currency_symbol,
            point_color=color,
        )

    def _plot_compare_line(
        self,
        ax: Any,
        x_values: list[int],
        y_values: list[float],
        *,
        color: str,
        label: str,
        linestyle: str,
        linewidth: float,
        annotate_last_point: bool = True,
    ) -> None:
        max_points = 10
        ax.plot(
            x_values,
            y_values,
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=0.8,
            label=label,
            marker="o" if len(x_values) <= max_points else None,
            markersize=4,
        )
        if not annotate_last_point or not x_values or not y_values:
            return
        last_x = x_values[-1]
        last_y = y_values[-1]
        period_label = label.replace(" (Current)", "")
        label_text = f"{period_label}: {self._format_chart_last_point_value(last_y)}"
        self._annotate_chart_last_point(ax, float(last_x), last_y, label_text)

    def _plot_compare_series_on_axes(
        self,
        ax: Any,
        series_data: list[list[tuple[int, float]]],
        labels: list[str],
        colors: list[str],
        *,
        max_x_limit: int,
    ) -> None:
        current_series: tuple[list[int], list[float]] | None = None
        current_color: str | None = None
        current_label: str | None = None

        for index, (data, color, label) in enumerate(zip(series_data, colors, labels, strict=False)):
            if not data:
                continue
            x_values = [item[0] for item in data]
            y_values = [item[1] for item in data]
            if index == 0 or "(Current)" in label:
                current_series = (x_values, y_values)
                current_color = color
                current_label = label
                continue

            self._plot_compare_line(
                ax,
                x_values,
                y_values,
                color=color,
                label=label,
                linestyle="--",
                linewidth=2,
            )

        if current_series is not None and current_color is not None and current_label is not None:
            x_values, y_values = current_series
            self._plot_compare_line(
                ax,
                x_values,
                y_values,
                color=current_color,
                label=current_label,
                linestyle="-",
                linewidth=3,
            )

        ax.set_xlim(1, max(max_x_limit, 1))
        ax.set_xticks(self._sparse_integer_ticks(max_x_limit))
        ax.grid(visible=True, alpha=0.3)
        ax.legend(loc="upper left", fontsize=10)

    @requires_database(is_show_warning=False)
    def _populate_chart_categories_list(self) -> None:
        """Fill chart categories list with checkable categories (expenses checked by default)."""
        if self.db_manager is None:
            return

        model = QStandardItemModel()
        for cat_id, name, category_type, icon in self.db_manager.get_all_categories():
            display_text = f"{icon} {name}" if icon else name
            if category_type == 1:
                display_text = f"{display_text} (Income)"

            item = QStandardItem(display_text)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Checked if category_type == 0 else Qt.CheckState.Unchecked)
            item.setData(name, Qt.ItemDataRole.UserRole)
            item.setData(int(category_type), Qt.ItemDataRole.UserRole + 1)
            item.setData(int(cat_id), Qt.ItemDataRole.UserRole + 2)
            model.appendRow(item)

        self.list_chart_categories.setModel(model)

    def _populate_form_from_description(self, description: str) -> None:
        """Populate form fields based on description from database.

        Args:

        - `description` (`str`): The transaction description.

        """
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        # Save current date before populating form
        current_date: QDate = self.dateEdit.date()

        try:
            # Get the most recent transaction with this description
            query: str = """
                SELECT t.amount, cat.name, c.code
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                JOIN currencies c ON t._id_currencies = c._id
                WHERE t.description = :description
                ORDER BY t.date DESC, t._id DESC
                LIMIT 1
            """

            rows: list = self.db_manager.get_rows(query, {"description": description})

            if rows:
                amount_cents: int
                category_name: str
                currency_code: str
                amount_cents, category_name, currency_code = rows[0]

                # Populate form fields
                amount: float = float(amount_cents) / 100  # Convert from cents
                self.doubleSpinBox_amount.setValue(amount)

                # Set category if found
                if category_name:
                    # Find the category in the list view
                    model = self.listView_categories.model()
                    if model:
                        for row in range(model.rowCount()):
                            index: QModelIndex = model.index(row, 0)
                            item_data = model.data(index, Qt.ItemDataRole.UserRole)
                            if item_data == category_name:
                                self.listView_categories.setCurrentIndex(index)
                                break

                # Set currency if found
                if currency_code:
                    index: int = self.comboBox_currency.findText(currency_code)
                    if index >= 0:
                        self.comboBox_currency.setCurrentIndex(index)

        except Exception as e:
            print(f"Error populating form from description: {e}")
        finally:
            # Always restore the original date
            self.dateEdit.setDate(current_date)

    def _process_purchase_items(self, parsed_items: list, purchase_date: str) -> None:
        """Add validated purchase items to the database.

        Args:

        - `parsed_items` (`list[ParsedPurchaseItem]`): Purchases from the table dialog.
        - `purchase_date` (`str`): Date for purchases in yyyy-MM-dd format.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        if not parsed_items:
            message_box.information(self, "No Items", "No valid purchase items found.")
            return

        # Get default currency ID
        default_currency: str | None = self.db_manager.get_default_currency()
        if not default_currency:
            message_box.warning(self, "Error", "No default currency set")
            return

        default_currency_info = self.db_manager.get_currency_by_code(default_currency)
        default_currency_id: int = default_currency_info[0]

        # Add items to database
        success_count: int = 0
        error_count: int = 0
        error_messages: list[str] = []

        for item in parsed_items:
            try:
                # Find or create category
                category_id: int | None = self._get_or_create_category(item.category)
                if not category_id:
                    error_count += 1
                    error_messages.append(f"Failed to create category: {item.category}")
                    continue

                # Add transaction
                success: bool = self.db_manager.add_transaction(
                    amount=item.amount,
                    description=item.name,
                    category_id=category_id,
                    currency_id=default_currency_id,
                    date=purchase_date,
                    tag="",
                )

                if success:
                    success_count += 1
                else:
                    error_count += 1
                    error_messages.append(f"Failed to add: {item.name}")
            except Exception as e:
                error_count += 1
                error_messages.append(f"Error adding {item.name}: {e}")

        # Show results
        if success_count > 0:
            # Save current date before update_all
            current_date: QDate = self.dateEdit.date()
            self.update_all()
            # Restore the original date
            self.dateEdit.setDate(current_date)

        max_error_messages = 10
        if error_count > 0:
            error_text: str = f"Added {success_count} purchases successfully.\n\nErrors:\n" + "\n".join(
                error_messages[:max_error_messages]
            )
            if len(error_messages) > max_error_messages:
                error_text += f"\n... and {len(error_messages) - 10} more errors"
            message_box.warning(self, "Results", error_text)
        else:
            toast = toast_notification.ToastNotification(
                f"Successfully added {success_count} purchases.",
                duration=2000,
                parent=self,
            )
            toast.exec()

    def _prompt_compare_last_years_start(self) -> bool:
        """Ask for the day and month when each comparison year begins."""
        dialog = ChartYearStartDialog(
            self,
            start_month=self._compare_last_years_start_month,
            start_day=self._compare_last_years_start_day,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        month, day = dialog.get_year_start()
        self._compare_last_years_start_month = month
        self._compare_last_years_start_day = day
        return True

    def _refresh_summary_if_needed(self) -> None:
        """Recompute summary only when reports tab is active."""
        id_reports_tab = 6
        if self.tabWidget.currentIndex() == id_reports_tab and self._summary_dirty:
            self.update_summary_labels()
            self._summary_dirty = False

    def _refresh_test_balance_dialog_table(self, table: QTableWidget) -> None:
        """Recompute natural reconciliation and refresh balance-check table."""
        if self.db_manager is None:
            return
        refreshed_tx = self.db_manager.get_all_transactions()
        refreshed_ex = self.db_manager.get_all_currency_exchanges()
        refreshed_accounts = self.db_manager.get_all_accounts()
        refreshed_natural = get_natural_currency_reconciliation(
            refreshed_tx, refreshed_ex, refreshed_accounts, self.db_manager
        )
        self._refresh_test_balance_table(table, refreshed_natural)

    def _refresh_test_balance_table(self, table: QTableWidget, natural_rows: list[dict[str, Any]]) -> None:
        """Refresh per-currency rows in test balance table."""
        for row_idx, item in enumerate(natural_rows):
            cid = int(item["currency_id"])
            j_maj = self.db_manager.convert_from_minor_units(int(item["journal_minor"]), cid)
            a_maj = self.db_manager.convert_from_minor_units(int(item["accounts_minor"]), cid)
            d_minor = int(item["diff_minor"])
            d_maj = self.db_manager.convert_from_minor_units(d_minor, cid)
            table.setItem(row_idx, 1, QTableWidgetItem(f"{j_maj:,.2f}"))
            table.setItem(row_idx, 2, QTableWidgetItem(f"{a_maj:,.2f}"))
            table.setItem(row_idx, 3, QTableWidgetItem(f"{d_maj:,.2f}"))
            self._set_balance_check_action_cell(table, row_idx, cid, d_minor)

    def _refresh_transactions_table(self) -> None:
        """Reload transactions table, keeping active filters when applied."""
        if self._transactions_filter_is_active():
            self.apply_filter()
        else:
            self._load_transactions_table()
            self._connect_table_auto_save_signals()

    def _reset_transactions_pagination_state(self) -> None:
        """Reset pagination counters and display state for transactions table."""
        self._transactions_pagination.reset()
        self._transactions_dates_with_totals = set()
        self._transactions_date_color_map = {}
        self._transactions_color_index = 0

    def _restore_table_column_widths(self, table_view: QTableView, column_widths: list[int]) -> None:
        """Restore column widths for a table view.

        Args:

        - `table_view` (`QTableView`): The table view to restore column widths for.
        - `column_widths` (`list[int]`): List of column widths to restore.

        """
        header = table_view.horizontalHeader()
        if column_widths and header.count() == len(column_widths):
            for i, width in enumerate(column_widths):
                table_view.setColumnWidth(i, width)

    def _save_table_column_widths(self, table_view: QTableView) -> list[int]:
        """Save column widths for a table view.

        Args:

        - `table_view` (`QTableView`): The table view to save column widths for.

        Returns:

        - `list[int]`: List of column widths.

        """
        header = table_view.horizontalHeader()
        return [table_view.columnWidth(i) for i in range(header.count())]

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
            query: str = "SELECT name FROM categories WHERE _id = :category_id"
            rows: list = self.db_manager.get_rows(query, {"category_id": category_id})
            if not rows:
                print(f"Category with ID {category_id} not found")
                return

            category_name: str = rows[0][0]

            # Find the category in the list view
            model = self.listView_categories.model()
            if model:
                for row in range(model.rowCount()):
                    index: QModelIndex = model.index(row, 0)
                    item_data = model.data(index, Qt.ItemDataRole.UserRole)
                    if item_data == category_name:
                        # Set the current index
                        self.listView_categories.setCurrentIndex(index)

                        # Also try to select the item in the selection model
                        selection_model = self.listView_categories.selectionModel()
                        if selection_model:
                            selection_model.select(index, selection_model.SelectionFlag.Select)

                        # Update the category label
                        display_text: str | None = model.data(index, Qt.ItemDataRole.DisplayRole)
                        if display_text:
                            self.label_category_now.setText(display_text)
                        break

        except Exception as e:
            print(f"Error selecting category by ID: {e}")

    def _select_only_chart_categories(self, category_type: int) -> None:
        """Check categories of the given type and uncheck all others (0 expense, 1 income)."""
        model = self.list_chart_categories.model()
        if not isinstance(model, QStandardItemModel):
            return

        for row in range(model.rowCount()):
            item = model.item(row)
            if item is None:
                continue
            item.setCheckState(
                Qt.CheckState.Checked
                if item.data(Qt.ItemDataRole.UserRole + 1) == category_type
                else Qt.CheckState.Unchecked
            )

    def _set_balance_check_action_cell(
        self,
        table: QTableWidget,
        row_idx: int,
        currency_id: int,
        diff_minor: int,
    ) -> None:
        """Set Action column widgets for one balance-check row."""
        if diff_minor == 0:
            table.removeCellWidget(row_idx, 4)
            table.setItem(row_idx, 4, QTableWidgetItem("-"))
            return

        container = QWidget(table)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        add_btn = make_emoji_push_button("Add revision", "➕", parent=container)  # noqa: RUF001
        add_btn.clicked.connect(
            lambda _checked=False, c=currency_id, dm=diff_minor: self._on_add_revision_clicked(c, dm, table)
        )
        layout.addWidget(add_btn)

        if diff_minor > 0 and self._can_net_negative_revisions(currency_id, diff_minor):
            net_btn = make_emoji_push_button("Net revisions", "🧮", parent=container)
            net_btn.clicked.connect(
                lambda _checked=False, c=currency_id, dm=diff_minor: self._on_net_negative_revisions_clicked(
                    c, dm, table
                )
            )
            layout.addWidget(net_btn)

        table.setCellWidget(row_idx, 4, container)

    def _set_chart_categories_check_state(
        self,
        *,
        checked: bool,
        category_type: int | None = None,
    ) -> None:
        """Set check state for chart category rows, optionally filtered by type (0 expense, 1 income)."""
        model = self.list_chart_categories.model()
        if not isinstance(model, QStandardItemModel):
            return

        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(model.rowCount()):
            item = model.item(row)
            if item is None:
                continue
            if category_type is not None and item.data(Qt.ItemDataRole.UserRole + 1) != category_type:
                continue
            item.setCheckState(state)

    @requires_database()
    def _set_date_for_selected_transactions(self, transaction_ids: list[int]) -> None:
        """Set the same date on several transactions after user picks a date in a dialog."""
        min_rows_for_bulk_date = 2
        if len(transaction_ids) < min_rows_for_bulk_date or self.db_manager is None:
            return
        if not self._validate_database_connection():
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Set date for selected transactions")
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(
            QLabel(f"New date for {len(transaction_ids)} transactions:", dialog),
        )
        date_edit = QDateEdit(dialog)
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")
        date_edit.setDate(self.dateEdit.date())
        dialog_layout.addWidget(date_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        new_date: str = date_edit.date().toString("yyyy-MM-dd")
        if self.db_manager.update_transactions_date(transaction_ids, new_date):
            self._mark_transactions_changed()
            self._mark_summary_dirty()
            self.update_summary_labels()
            # Defer reload until the context menu / dialog event loop finishes.
            QTimer.singleShot(0, self._refresh_transactions_table)
        else:
            message_box.warning(self, "Date", "Could not update date for one or more transactions.")

    def _set_date_from_table(self, date_value: str) -> None:
        """Set the date from table row to the main dateEdit field.

        Args:

        - `date_value` (`str`): Date string from the table (format: yyyy-MM-dd).

        """
        try:
            # Parse the date string and set it in dateEdit
            date_obj: QDate = QDate.fromString(date_value, "yyyy-MM-dd")
            if not date_obj.isNull():
                self.dateEdit.setDate(date_obj)
            else:
                print(f"❌ Invalid date format: {date_value}")
        except Exception as e:
            print(f"❌ Error setting date from table: {e}")

    def _set_date_from_table_minus_one_day(self, date_value: str) -> None:
        """Set the date from table row - 1 day to the main dateEdit field.

        Args:

        - `date_value` (`str`): Date string from the table (format: yyyy-MM-dd).

        """
        try:
            # Parse the date string, subtract 1 day and set it in dateEdit
            date_obj: QDate = QDate.fromString(date_value, "yyyy-MM-dd")
            if not date_obj.isNull():
                new_date: QDate = date_obj.addDays(-1)
                self.dateEdit.setDate(new_date)
            else:
                print(f"❌ Invalid date format: {date_value}")
        except Exception as e:
            print(f"❌ Error setting date from table - 1 day: {e}")

    def _set_date_from_table_plus_one_day(self, date_value: str) -> None:
        """Set the date from table row + 1 day to the main dateEdit field.

        Args:

        - `date_value` (`str`): Date string from the table (format: yyyy-MM-dd).

        """
        try:
            # Parse the date string, add 1 day and set it in dateEdit
            date_obj: QDate = QDate.fromString(date_value, "yyyy-MM-dd")
            if not date_obj.isNull():
                new_date: QDate = date_obj.addDays(1)
                self.dateEdit.setDate(new_date)
            else:
                print(f"❌ Invalid date format: {date_value}")
        except Exception as e:
            print(f"❌ Error setting date from table + 1 day: {e}")

    def _set_reports_model_and_stretch(self, model: QStandardItemModel) -> None:
        """Set model on reports table and stretch columns."""
        self.tableView_reports.setModel(model)
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)

    def _set_table_model_and_stretch_columns(
        self,
        table_view: QTableView,
        model: QSortFilterProxyModel,
        *,
        stretch_last: bool = True,
    ) -> None:
        """Set model on table view and stretch all columns.

        Args:

        - `table_view` (`QTableView`): Table view to configure.
        - `model` (`QSortFilterProxyModel`): Model to set.
        - `stretch_last` (`bool`): If False, call setStretchLastSection(False). Defaults to True.

        """
        table_view.setModel(model)
        header = table_view.horizontalHeader()
        if header.count() > 0:
            for i in range(header.count()):
                header.setSectionResizeMode(i, header.ResizeMode.Stretch)
            if not stretch_last:
                header.setStretchLastSection(False)

    def _set_today_date_in_main(self) -> None:
        """Set today's date in the main date field."""
        today: QDate = QDate.currentDate()
        self.dateEdit.setDate(today)

    def _setup_autocomplete(self) -> None:
        """Set up autocomplete functionality for description input."""
        self.description_completer_source_model: QStringListModel = QStringListModel(self)
        self.description_completer_proxy: DescriptionAutocompleteProxyModel = DescriptionAutocompleteProxyModel(self)
        self.description_completer_proxy.setSourceModel(self.description_completer_source_model)

        self.description_completer = QCompleter(self.description_completer_proxy, self)
        self.description_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.description_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.description_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        self.lineEdit_description.setCompleter(self.description_completer)

        self._update_autocomplete_data()

        self.lineEdit_description.textEdited.connect(self._on_description_text_edited)
        self.description_completer.activated.connect(self._on_autocomplete_selected)

    def _setup_tab_order(self) -> None:
        """Se tup tab order for widgets in groupBox_transaction."""
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

    def _setup_transactions_table_column_widths(self) -> None:
        """Configure column resize modes for the transactions table."""
        header = self.tableView_transactions.horizontalHeader()
        if header.count() > 0:
            for i in range(header.count() - 2):
                header.setSectionResizeMode(i, header.ResizeMode.Stretch)

            second_last_column: int = header.count() - 2
            header.setSectionResizeMode(second_last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(second_last_column, 100)

            last_column: int = header.count() - 1
            header.setSectionResizeMode(last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(last_column, 120)

    def _setup_transactions_table_delegates(self) -> None:
        """Set up item delegates for the transactions table."""
        self.description_delegate = DescriptionDelegate(self.tableView_transactions)
        self.tableView_transactions.setItemDelegateForColumn(0, self.description_delegate)

        categories: list[str] = self._get_categories_for_delegate()
        self.category_delegate = CategoryComboBoxDelegate(self.tableView_transactions, categories)
        self.tableView_transactions.setItemDelegateForColumn(2, self.category_delegate)

        currencies: list[str] = self._get_currencies_for_delegate()
        self.currency_delegate = CurrencyComboBoxDelegate(self.tableView_transactions, currencies)
        self.tableView_transactions.setItemDelegateForColumn(3, self.currency_delegate)

        self.date_delegate = DateDelegate(self.tableView_transactions)
        self.tableView_transactions.setItemDelegateForColumn(4, self.date_delegate)

        tags: list[str] = self._get_tags_for_delegate()
        self.tag_delegate = TagDelegate(self.tableView_transactions, tags)
        self.tableView_transactions.setItemDelegateForColumn(5, self.tag_delegate)

        self.amount_delegate = AmountDelegate(self.tableView_transactions, self.db_manager)
        self.tableView_transactions.setItemDelegateForColumn(1, self.amount_delegate)

        self.total_per_day_delegate = AmountDelegate(self.tableView_transactions, self.db_manager)
        self.tableView_transactions.setItemDelegateForColumn(6, self.total_per_day_delegate)

        self.tableView_transactions.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)

    def _setup_ui(self) -> None:
        """Set up additional UI elements."""
        # Set emoji for buttons
        self.pushButton_yesterday.setText(f"📅 {self.pushButton_yesterday.text()}")
        self.pushButton_add.setText(f"➕ {self.pushButton_add.text()}")  # noqa: RUF001
        self.pushButton_add_as_text_with_ai.setText(f"🤖 {self.pushButton_add_as_text_with_ai.text()}")
        self.pushButton_delete.setText(f"🗑️ {self.pushButton_delete.text()}")
        self.pushButton_refresh.setText(f"🔄 {self.pushButton_refresh.text()}")
        self.pushButton_clear_filter.setText(f"🧹 {self.pushButton_clear_filter.text()}")
        self.pushButton_apply_filter.setText(f"✔️ {self.pushButton_apply_filter.text()}")
        self.pushButton_description_clear.setText("🧹")
        self.pushButton_show_all_records.setText("📊 Show All Records")

        # Multi-line natural currency summaries (Quick Summary / today)
        self.label_total_income.setWordWrap(True)
        self.label_total_expenses.setWordWrap(True)
        self.label_today_expense.setWordWrap(True)
        self.label_yesterday_expense.setWordWrap(True)

        # Set emoji for exchange rate buttons
        self.pushButton_exchange_update.setText(f"🔄 {self.pushButton_exchange_update.text()}")
        self.pushButton_rates_delete.setText(f"🗑️ {self.pushButton_rates_delete.text()}")
        self.pushButton_exchange_item_update.setText(f"✏️ {self.pushButton_exchange_item_update.text()}")
        self.pushButton_filter_exchange_rates_clear.setText(f"🧹 {self.pushButton_filter_exchange_rates_clear.text()}")
        self.pushButton_filter_exchange_rates_apply.setText(f"✔️ {self.pushButton_filter_exchange_rates_apply.text()}")
        self.pushButton_exchange_rates_last_month.setText(f"📅 {self.pushButton_exchange_rates_last_month.text()}")
        self.pushButton_exchange_rates_last_year.setText(f"📅 {self.pushButton_exchange_rates_last_year.text()}")
        self.pushButton_exchange_rates_all_time.setText(f"📊 {self.pushButton_exchange_rates_all_time.text()}")
        self.pushButton_chart_last_month.setText(f"📅 {self.pushButton_chart_last_month.text()}")
        self.pushButton_chart_last_year.setText(f"📅 {self.pushButton_chart_last_year.text()}")
        self.pushButton_chart_all_time.setText(f"📅 {self.pushButton_chart_all_time.text()}")
        chart_category_button_icon_size = 18
        self.pushButton_select_all.setIcon(create_emoji_icon("☑️", chart_category_button_icon_size))
        self.pushButton_select_deselect_all.setIcon(create_emoji_icon("⬜", chart_category_button_icon_size))
        self.pushButton_select_only_expense.setText(f"💸 {self.pushButton_select_only_expense.text()}")
        self.pushButton_select_only_income.setText(f"💰 {self.pushButton_select_only_income.text()}")

        # Set emoji for additional exchange and currency buttons
        self.pushButton_exchange_yesterday.setText(f"📅 {self.pushButton_exchange_yesterday.text()}")
        self.pushButton_calculate_exchange.setText(f"🧮 {self.pushButton_calculate_exchange.text()}")
        self.pushButton_currency_add.setText(f"➕ {self.pushButton_currency_add.text()}")  # noqa: RUF001
        self.pushButton_set_default_currency.setText(f"⭐ {self.pushButton_set_default_currency.text()}")
        self.pushButton_currencies_delete.setText(f"🗑️ {self.pushButton_currencies_delete.text()}")
        self.pushButton_currencies_refresh.setText(f"🔄 {self.pushButton_currencies_refresh.text()}")

        # Set emoji for account and category buttons
        self.pushButton_account_add.setText(f"➕ {self.pushButton_account_add.text()}")  # noqa: RUF001
        self.pushButton_accounts_delete.setText(f"🗑️ {self.pushButton_accounts_delete.text()}")
        self.pushButton_accounts_refresh.setText(f"🔄 {self.pushButton_accounts_refresh.text()}")
        self.pushButton_category_add.setText(f"➕ {self.pushButton_category_add.text()}")  # noqa: RUF001
        self.pushButton_categories_delete.setText(f"🗑️ {self.pushButton_categories_delete.text()}")
        self.pushButton_categories_refresh.setText(f"🔄 {self.pushButton_categories_refresh.text()}")
        self.pushButton_copy_categories_as_text.setText(f"📋 {self.pushButton_copy_categories_as_text.text()}")

        # Set emoji for exchange buttons
        self.pushButton_exchange_add.setText(f"➕ {self.pushButton_exchange_add.text()}")  # noqa: RUF001
        self.pushButton_exchange_delete.setText(f"🗑️ {self.pushButton_exchange_delete.text()}")
        self.pushButton_exchange_refresh.setText(f"🔄 {self.pushButton_exchange_refresh.text()}")

        self.pushButton_calculate_fee.setText(f"💰 {self.pushButton_calculate_fee.text()}")
        self.pushButton_rates_refresh.setText(f"🔄 {self.pushButton_rates_refresh.text()}")
        self.pushButton_update_chart.setText(f"🔄 {self.pushButton_update_chart.text()}")
        self.pushButton_generate_report.setText(f"📄 {self.pushButton_generate_report.text()}")

        # Connect double-click signal for exchange table
        self.tableView_exchange.doubleClicked.connect(self._on_exchange_table_double_clicked)

        # Replace label_category_now with custom label that has dropdown arrow
        old_label = self.label_category_now
        parent = old_label.parentWidget()
        if parent is None:
            parent_widget = old_label.parent()
            if isinstance(parent_widget, QWidget):
                parent = parent_widget
            else:
                return  # Cannot replace if no valid parent widget

        if not isinstance(parent, QWidget):
            return  # Cannot replace if parent is not a QWidget

        layout = parent.layout()
        if layout is not None:
            layout_index = layout.indexOf(old_label)

            # Create new custom label with same properties
            new_label = ClickableCategoryLabel(parent=parent)
            new_label.setObjectName("label_category_now")
            new_label.setFont(old_label.font())
            new_label.setFocusPolicy(old_label.focusPolicy())
            new_label.setText(self._NO_CATEGORY_LABEL)

            # Replace in layout
            layout.removeWidget(old_label)
            layout.insertWidget(layout_index, new_label)
            old_label.deleteLater()
            self.label_category_now = new_label

        # Enable category selection via label context menu
        self.label_category_now.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.label_category_now.customContextMenuRequested.connect(self._show_category_label_context_menu)
        self.label_category_now.installEventFilter(self)

        # Add context menu for categories list (Filter by this category)
        self.listView_categories.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listView_categories.customContextMenuRequested.connect(self._show_categories_list_context_menu)

        # Configure splitter proportions
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 3)

        # Configure splitter_4 proportions (frame_exchange narrow, tableView_exchange wide)
        self.splitter_4.setStretchFactor(0, 1)  # frame_exchange gets less space
        self.splitter_4.setStretchFactor(1, 3)  # tableView_exchange gets more space

        # Configure splitter_2 proportions (frame_accounts narrow, tableView_accounts wide)
        self.splitter_2.setStretchFactor(0, 1)  # frame_accounts gets less space
        self.splitter_2.setStretchFactor(1, 3)  # tableView_accounts gets more space

        # Configure splitter_3 proportions (frames narrow, tableViews wide)
        self.splitter_3.setStretchFactor(0, 1)  # frame_2 gets less space
        self.splitter_3.setStretchFactor(1, 3)  # tableView_categories gets more space
        self.splitter_3.setStretchFactor(2, 1)  # frame_currencies gets less space
        self.splitter_3.setStretchFactor(3, 3)  # tableView_currencies gets more space

        # Configure splitter_5 proportions (frame_5 narrow, tableView_reports wide)
        self.splitter_5.setStretchFactor(0, 1)  # frame_5 gets less space
        self.splitter_5.setStretchFactor(1, 3)  # tableView_reports gets more space

        # Configure splitter_6 proportions (frame_rates narrow, widget_exchange_rates_right wide)
        self.splitter_6.setStretchFactor(0, 1)  # frame_rates gets less space
        self.splitter_6.setStretchFactor(1, 3)  # widget_exchange_rates_right gets more space

        # Set default values
        self.doubleSpinBox_amount.setValue(100.0)
        self.doubleSpinBox_exchange_from.setValue(100.0)
        self.doubleSpinBox_exchange_to.setValue(73.5)
        self.doubleSpinBox_exchange_rate.setValue(73.5)
        self.spinBox_subdivision.setValue(100)

    def _show_categories_list_context_menu(self, position: QPoint) -> None:
        """Show context menu on listView_categories with Filter by this category."""
        index: QModelIndex = self.listView_categories.indexAt(position)
        if not index.isValid():
            return
        category_value: str | None = self.listView_categories.model().data(index, Qt.ItemDataRole.UserRole)
        if not category_value:
            return
        context_menu = QMenu(self)
        filter_action = context_menu.addAction("🔍 Filter by this category")
        filter_action.triggered.connect(lambda: self._filter_by_category_from_table(category_value))
        context_menu.exec_(self.listView_categories.mapToGlobal(position))

    def _show_category_label_context_menu(self, position: QPoint) -> None:
        """Show context menu on the category label with all available categories.

        Args:

        - `position` (`QPoint`): Position where the menu is requested.

        """
        model = self.listView_categories.model()
        if model is None or model.rowCount() == 0:
            return

        context_menu = QMenu(self)
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            display_text = model.data(index, Qt.ItemDataRole.DisplayRole)
            if not display_text:
                continue
            action = context_menu.addAction(display_text)
            action.setData(row)

        if context_menu.isEmpty():
            return

        # Execute the context menu and get the selected action
        selected_action = context_menu.exec_(self.label_category_now.mapToGlobal(position))
        if selected_action is None:
            return

        row_data = selected_action.data()
        if not isinstance(row_data, int):
            return

        index = model.index(row_data, 0)
        if not index.isValid():
            return

        self.listView_categories.setCurrentIndex(index)
        selection_model = self.listView_categories.selectionModel()
        if selection_model:
            selection_model.setCurrentIndex(
                index,
                QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows,
            )

    def _show_chart_categories_context_menu(self, position: QPoint) -> None:
        """Context menu for bulk selection of chart categories."""
        if self.list_chart_categories.model() is None:
            return

        menu = QMenu(self)
        select_all = menu.addAction("Select all categories")
        deselect_all = menu.addAction("Deselect all categories")
        menu.addSeparator()
        select_expenses = menu.addAction("Select all expense categories")
        deselect_expenses = menu.addAction("Deselect all expense categories")
        menu.addSeparator()
        select_income = menu.addAction("Select all income categories")
        deselect_income = menu.addAction("Deselect all income categories")

        select_all.triggered.connect(partial(self._set_chart_categories_check_state, checked=True))
        deselect_all.triggered.connect(partial(self._set_chart_categories_check_state, checked=False))
        select_expenses.triggered.connect(
            partial(self._set_chart_categories_check_state, checked=True, category_type=0)
        )
        deselect_expenses.triggered.connect(
            partial(self._set_chart_categories_check_state, checked=False, category_type=0)
        )
        select_income.triggered.connect(partial(self._set_chart_categories_check_state, checked=True, category_type=1))
        deselect_income.triggered.connect(
            partial(self._set_chart_categories_check_state, checked=False, category_type=1)
        )

        cast("Any", menu).exec(self.list_chart_categories.viewport().mapToGlobal(position))

    def _show_no_data_label(self, layout: QLayout, text: str) -> None:
        """Show a message when no data is available for the chart.

        Args:

        - `layout` (`QLayout`): The layout to add the message to.
        - `text` (`str`): The message to display.

        """
        # Clear existing content
        self._clear_layout(layout)

        # Create and add label
        label: QLabel = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #666; padding: 20px;")
        layout.addWidget(label)

    def _show_tag_totals_dialog(self, tag: str) -> None:
        """Open dialog listing all purchases with this tag and per-currency totals."""
        if not self._validate_database_connection() or self.db_manager is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Totals for tag: {tag}")
        dialog.resize(920, 560)

        layout = QVBoxLayout(dialog)

        count_label = QLabel(dialog)
        layout.addWidget(count_label)

        purchases_label = QLabel("Purchases", dialog)
        layout.addWidget(purchases_label)

        purchases_table = QTableWidget(dialog)
        purchases_table.setColumnCount(5)
        purchases_table.setHorizontalHeaderLabels(["Date", "Description", "Amount", "Currency", "Category"])
        purchases_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        purchases_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        purchases_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        purchases_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        ph = purchases_table.horizontalHeader()
        if ph is not None:
            ph.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            ph.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            ph.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            ph.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            ph.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(purchases_table)

        totals_label = QLabel("Totals by currency", dialog)
        layout.addWidget(totals_label)

        totals_table = QTableWidget(dialog)
        totals_table.setColumnCount(3)
        totals_table.setHorizontalHeaderLabels(["Currency", "Symbol", "Total"])
        totals_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        totals_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        totals_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        th = totals_table.horizontalHeader()
        if th is not None:
            th.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            th.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            th.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(totals_table)

        def refresh_tag_tables() -> None:
            db = self.db_manager
            if db is None:
                return
            rows = db.get_transactions_for_tag(tag)
            totals = db.get_tag_amount_totals_by_currency(tag)
            count_label.setText(f'Transactions with tag "{tag}": {len(rows)}')

            purchases_table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                tx_id, date_v, description, amount_minor, currency_id, code, _symbol, category_name = row
                amount_major = db.convert_from_minor_units(int(amount_minor), int(currency_id))
                date_item = QTableWidgetItem(str(date_v))
                date_item.setData(Qt.ItemDataRole.UserRole, int(tx_id))
                purchases_table.setItem(row_idx, 0, date_item)
                purchases_table.setItem(row_idx, 1, QTableWidgetItem(str(description)))
                purchases_table.setItem(row_idx, 2, QTableWidgetItem(f"{amount_major:,.2f}"))
                purchases_table.setItem(row_idx, 3, QTableWidgetItem(str(code)))
                purchases_table.setItem(row_idx, 4, QTableWidgetItem(str(category_name)))

            totals_table.setRowCount(len(totals))
            for row_idx, (currency_id, code, symbol, sum_minor) in enumerate(totals):
                total_major = db.convert_from_minor_units(sum_minor, currency_id)
                totals_table.setItem(row_idx, 0, QTableWidgetItem(code))
                totals_table.setItem(row_idx, 1, QTableWidgetItem(symbol))
                totals_table.setItem(row_idx, 2, QTableWidgetItem(f"{total_major:,.2f}"))

        def on_purchases_context_menu(position: QPoint) -> None:
            idx = purchases_table.indexAt(position)
            if not idx.isValid():
                return
            row = idx.row()
            date_item = purchases_table.item(row, 0)
            if date_item is None:
                return
            tx_id = date_item.data(Qt.ItemDataRole.UserRole)
            if tx_id is None:
                return
            menu: QMenu = QMenu(purchases_table)
            remove_action = menu.addAction("🏷️ Remove tag from this transaction")
            chosen = cast("Any", menu).exec(purchases_table.mapToGlobal(position))
            if chosen != remove_action:
                return
            if self.db_manager is None:
                return
            if not self.db_manager.clear_transaction_tag(int(tx_id)):
                message_box.warning(dialog, "Tag", "Could not clear tag for this transaction.")
                return
            self.apply_filter()
            refresh_tag_tables()
            if purchases_table.rowCount() == 0:
                dialog.accept()

        purchases_table.customContextMenuRequested.connect(on_purchases_context_menu)

        refresh_tag_tables()

        button_row = QHBoxLayout()
        close_btn = make_emoji_push_button("Close", CLOSE_BUTTON_EMOJI, parent=dialog)
        close_btn.clicked.connect(dialog.accept)
        button_row.addStretch()
        button_row.addWidget(close_btn)
        layout.addLayout(button_row)

        dialog.exec()

    def _show_test_balance_dialog(
        self,
        *,
        default_currency_symbol: str,
        accounts_balance: float,
        accounting_balance_latest: float,
        difference_latest: float,
        accounting_balance_historical: float,
        difference_historical: float,
        natural_rows: list[dict[str, Any]],
    ) -> None:
        """Show reconciliation details in dialog with action buttons for non-zero currency diffs."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Balance check")
        dialog.resize(920, 560)

        layout = QVBoxLayout(dialog)
        fx_revaluation_effect = difference_historical - difference_latest
        summary_lines = [
            f"Total of all accounts: {accounts_balance:,.2f}{default_currency_symbol}",
            f"Accounting total (latest rates): {accounting_balance_latest:,.2f}{default_currency_symbol}",
            f"Difference (accounts - accounting, latest rates): {difference_latest:,.2f}{default_currency_symbol}",
            (
                f"Accounting total (historical rates by operation date): "
                f"{accounting_balance_historical:,.2f}{default_currency_symbol}"
            ),
            f"Difference (accounts - accounting, historical): {difference_historical:,.2f}{default_currency_symbol}",
            f"FX revaluation effect (historical - latest): {fx_revaluation_effect:,.2f}{default_currency_symbol}",
        ]
        summary_label = QLabel("\n".join(summary_lines), dialog)
        summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        summary_label.setWordWrap(True)
        layout.addWidget(summary_label)

        table = QTableWidget(dialog)
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Currency", "Journal", "Accounts", "Diff (accounts-journal)", "Action"])
        table.setRowCount(len(natural_rows))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        for row_idx, item in enumerate(natural_rows):
            currency_text = f"{item['code']} ({item['symbol']})"
            cid = int(item["currency_id"])
            j_maj = self.db_manager.convert_from_minor_units(int(item["journal_minor"]), cid)
            a_maj = self.db_manager.convert_from_minor_units(int(item["accounts_minor"]), cid)
            d_minor = int(item["diff_minor"])
            d_maj = self.db_manager.convert_from_minor_units(d_minor, cid)

            table.setItem(row_idx, 0, QTableWidgetItem(currency_text))
            table.setItem(row_idx, 1, QTableWidgetItem(f"{j_maj:,.2f}"))
            table.setItem(row_idx, 2, QTableWidgetItem(f"{a_maj:,.2f}"))
            table.setItem(row_idx, 3, QTableWidgetItem(f"{d_maj:,.2f}"))

            self._set_balance_check_action_cell(table, row_idx, cid, d_minor)

        header = table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(table)

        button_row = QHBoxLayout()
        copy_btn = make_emoji_push_button("Copy", COPY_BUTTON_EMOJI, parent=dialog)
        copy_btn.clicked.connect(lambda: self._copy_test_balance_to_clipboard(summary_lines, natural_rows))
        close_btn = make_emoji_push_button("Close", CLOSE_BUTTON_EMOJI, parent=dialog)
        close_btn.clicked.connect(dialog.accept)
        button_row.addWidget(copy_btn)
        button_row.addStretch()
        button_row.addWidget(close_btn)
        layout.addLayout(button_row)

        dialog.exec()

    def _show_transactions_context_menu(self, position: QPoint) -> None:
        """Show context menu for transactions table.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        context_menu: QMenu = QMenu(self)

        # Get the clicked index
        index: QModelIndex = self.tableView_transactions.indexAt(position)
        filter_by_category_action = None
        if index.isValid():
            # Get the category from the Category column (index 2)
            category_index: QModelIndex = self.tableView_transactions.model().index(index.row(), 2)
            if category_index.isValid():
                category_value: str = self.tableView_transactions.model().data(category_index)
                if category_value:
                    # Add menu item to filter by this category
                    filter_by_category_action = context_menu.addAction("🔍 Filter by this category")
                    filter_by_category_action.triggered.connect(
                        lambda: self._filter_by_category_from_table(category_value)
                    )

            tag_index: QModelIndex = self.tableView_transactions.model().index(index.row(), 5)
            tag_for_totals: str = ""
            if tag_index.isValid():
                raw_tag = self.tableView_transactions.model().data(tag_index)
                if raw_tag is not None and str(raw_tag).strip():
                    tag_for_totals = str(raw_tag).strip()
            if tag_for_totals:
                if filter_by_category_action is not None:
                    context_menu.addSeparator()
                tag_totals_action = context_menu.addAction("📊 Show totals for this tag")
                tag_totals_action.triggered.connect(
                    lambda _checked=False, t=tag_for_totals: self._show_tag_totals_dialog(t)
                )

            # Get the date from the Date column (index 4)
            date_index: QModelIndex = self.tableView_transactions.model().index(index.row(), 4)
            if date_index.isValid():
                date_value: str = self.tableView_transactions.model().data(date_index)
                if date_value:
                    # Add separator if category filter action was added
                    if filter_by_category_action:
                        context_menu.addSeparator()

                    # Add menu item to set this date in dateEdit
                    set_date_action = context_menu.addAction("📅 Set this date in main field")
                    set_date_action.triggered.connect(lambda: self._set_date_from_table(date_value))

                    # Add menu item to set this date + 1 day in dateEdit
                    set_date_plus_one_action = context_menu.addAction("📅 Set this date + 1 day in main field")
                    set_date_plus_one_action.triggered.connect(
                        lambda: self._set_date_from_table_plus_one_day(date_value)
                    )

                    # Add menu item to set this date - 1 day in dateEdit
                    set_date_minus_one_action = context_menu.addAction("📅 Set this date - 1 day in main field")
                    set_date_minus_one_action.triggered.connect(
                        lambda: self._set_date_from_table_minus_one_day(date_value)
                    )

                    # Add separator
                    context_menu.addSeparator()

        # Add separator before export action
        context_menu.addSeparator()

        # Delete action (plural label when multiple transaction rows are selected)
        selected_transaction_ids = self._get_selected_row_ids("transactions")
        delete_label = "🗑 Delete selected rows" if len(selected_transaction_ids) > 1 else "🗑 Delete selected row"
        delete_action = context_menu.addAction(delete_label)

        bulk_date_action = None
        ids_for_date_change: list[int] = []
        if len(selected_transaction_ids) > 1:
            ids_for_date_change = list(selected_transaction_ids)
            bulk_date_action = context_menu.addAction("✍️ Set date for all selected rows…")

        export_action = context_menu.addAction("📤 Export to CSV")

        # Add separator before clear filters action
        context_menu.addSeparator()

        # Add menu item to clear all filters (always available)
        clear_filters_action = context_menu.addAction("🧹 Clear all filters")
        clear_filters_action.triggered.connect(self.clear_filter)

        # Calculate sum of selected cells in Amount column (index 1)
        selected_indexes = self.tableView_transactions.selectionModel().selectedIndexes()
        amount_column_index = 1
        selected_amount_values: list[float] = []

        for selected_index in selected_indexes:
            # Only process cells in Amount column
            if selected_index.column() == amount_column_index:
                # Try to get the value from EditRole first (raw numeric value)
                # If not available, fall back to DisplayRole (formatted string)
                value = self.tableView_transactions.model().data(selected_index, Qt.ItemDataRole.EditRole)
                if value is None or value == "":
                    value = self.tableView_transactions.model().data(selected_index, Qt.ItemDataRole.DisplayRole)

                if value is not None and value != "":
                    try:
                        # If value is already a number, use it directly
                        if isinstance(value, (int, float)):
                            amount_value = float(value)
                        else:
                            # Clean the value: remove spaces, format characters, and convert subscript decimals
                            clean_value = str(value).replace(" ", "")
                            # Replace subscript decimal digits with normal digits
                            subscript_map = {
                                "₀": "0",
                                "₁": "1",
                                "₂": "2",
                                "₃": "3",
                                "₄": "4",
                                "₅": "5",
                                "₆": "6",
                                "₇": "7",
                                "₈": "8",
                                "₉": "9",
                            }
                            for sub, digit in subscript_map.items():
                                clean_value = clean_value.replace(sub, digit)
                            # Remove any non-numeric characters except decimal point and minus
                            clean_value = re.sub(r"[^\d.-]", "", clean_value)
                            # Convert to float
                            amount_value = float(clean_value)
                        selected_amount_values.append(amount_value)
                    except (ValueError, TypeError):
                        # Skip invalid values
                        continue

        # Add sum action if there are selected amount cells
        if selected_amount_values:
            total_sum = sum(selected_amount_values)
            # Format the sum using AmountDelegate logic
            is_negative = total_sum < 0
            num = abs(total_sum)

            # Format with spaces as thousands separator
            # Format number to 2 decimal places
            num_str = f"{num:.2f}"
            if "." in num_str:
                integer_part, decimal_part = num_str.split(".")
            else:
                integer_part = str(int(num))
                decimal_part = "00"

            # Add spaces every 3 digits from right to left
            formatted_integer = ""
            for i, digit in enumerate(reversed(integer_part)):
                if i > 0 and i % 3 == 0:
                    formatted_integer = " " + formatted_integer
                formatted_integer = digit + formatted_integer

            # Convert decimal digits to subscript Unicode characters
            subscript_map = {
                "0": "₀",
                "1": "₁",
                "2": "₂",
                "3": "₃",
                "4": "₄",
                "5": "₅",
                "6": "₆",
                "7": "₇",
                "8": "₈",
                "9": "₉",
            }
            subscript_decimal = "".join(subscript_map.get(digit, digit) for digit in decimal_part)

            # Construct final formatted number with subscript decimals
            # Check if the original sum is a whole number (within floating point precision)
            near_zero = 0.01
            is_whole_number = abs(total_sum - round(total_sum)) < near_zero
            formatted = formatted_integer if is_whole_number else f"{formatted_integer}.{subscript_decimal}"

            # Add minus sign back if needed
            if is_negative:
                formatted = "-" + formatted

            # Add separator before sum action
            context_menu.addSeparator()

            # Add menu item with sum (disabled, just for display)
            sum_action = context_menu.addAction(f"💰 Sum of selected: {formatted}")
            sum_action.setEnabled(False)

        # Execute the context menu and get the selected action
        action = context_menu.exec_(self.tableView_transactions.mapToGlobal(position))

        # Process the action only if it was actually selected (not None)
        if action is None:
            # User clicked outside the menu or pressed Esc - do nothing
            return

        if action == export_action:
            self.on_export_csv()
        elif bulk_date_action is not None and action == bulk_date_action:
            self._set_date_for_selected_transactions(ids_for_date_change)
        elif action == delete_action:
            print("🔧 Context menu: Delete action triggered")
            # Perform the deletion
            self.delete_record("transactions")
        elif (
            action == clear_filters_action
            or (filter_by_category_action and action == filter_by_category_action)
            or (
                ("set_date_action" in locals() and action == set_date_action)
                or ("set_date_plus_one_action" in locals() and action == set_date_plus_one_action)
                or ("set_date_minus_one_action" in locals() and action == set_date_minus_one_action)
            )
        ):
            # This will be handled by the lambda connection above
            pass

    def _show_yesterday_context_menu(self, position: QPoint) -> None:
        """Show context menu for yesterday button with date options.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        context_menu: QMenu = QMenu(self)

        # Today's date
        today_action = context_menu.addAction("📅 Today's date")
        today_action.triggered.connect(self._set_today_date_in_main)

        # Add separator
        context_menu.addSeparator()

        # Plus 1 day
        plus_one_action = context_menu.addAction("➕ Add 1 day")  # noqa: RUF001
        plus_one_action.triggered.connect(self._add_one_day_to_main)

        # Minus 1 day
        minus_one_action = context_menu.addAction("➖ Subtract 1 day")  # noqa: RUF001
        minus_one_action.triggered.connect(self._subtract_one_day_from_main)

        # Show context menu at cursor position
        context_menu.exec_(self.pushButton_yesterday.mapToGlobal(position))

    def _subtract_one_day_from_main(self) -> None:
        """Subtract one day from the current date in main date field."""
        current_date: QDate = self.dateEdit.date()
        new_date: QDate = current_date.addDays(-1)
        self.dateEdit.setDate(new_date)

    def _transactions_filter_is_active(self) -> bool:
        """Return True when any transaction table filter is applied."""
        if self.radioButton_filter_type_expense.isChecked() or self.radioButton_filter_type_income.isChecked():
            return True
        if self.comboBox_filter_category.currentText().strip():
            return True
        if self.comboBox_filter_currency.currentText().strip():
            return True
        if self.lineEdit_filter_description.text().strip():
            return True
        return self.checkBox_use_date_filter.isChecked()

    def _transform_transaction_data(self, rows: list[list], *, append_state: bool = False) -> list[list]:
        """Transform transaction data for display with colors and daily totals.

        Args:

        - `rows` (`list[list]`): Raw transaction data.
        - `append_state` (`bool`): Reuse pagination color/total state when appending rows.

        Returns:

        - `list[list]`: Transformed data with colors and daily totals.

        """
        daily_expenses: dict[str, float] = calc_daily_expenses(rows, self.db_manager)
        result = transform_transaction_data_helper(
            rows,
            daily_expenses,
            self.date_colors,
            self.db_manager,
            dates_with_totals=self._transactions_dates_with_totals if append_state else None,
            date_to_color_index=self._transactions_date_color_map if append_state else None,
            color_index=self._transactions_color_index if append_state else 0,
        )
        self._transactions_dates_with_totals = result.dates_with_totals
        self._transactions_date_color_map = result.date_to_color_index
        self._transactions_color_index = result.color_index
        return result.rows

    def _update_accounts_balance_display(self) -> None:
        """Update the display of total accounts balance."""
        if not self._validate_database_connection():
            return

        try:
            total_balance: float
            details: str
            total_balance, details = self._calculate_total_accounts_balance()

            # Get default currency symbol for proper display
            default_currency_code: str = self.db_manager.get_default_currency()
            default_currency_info = self.db_manager.get_currency_by_code(default_currency_code)
            default_currency_symbol: str = default_currency_info[2] if default_currency_info else ""

            # Update main balance label with proper currency symbol
            self.label_balance_accounts.setText(f"{total_balance:,.2f}{default_currency_symbol}")

            # Update details label
            self.label_balance_account_details.setText(details)

        except Exception as e:
            print(f"Error updating accounts balance display: {e}")
            self.label_balance_accounts.setText("Error")
            self.label_balance_account_details.setText("Failed to load balance")

    def _update_autocomplete_data(self) -> None:
        """Update autocomplete data from database."""
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            raw_descriptions: list[str] = self.db_manager.get_recent_transaction_descriptions_for_autocomplete(
                self.description_autocomplete_limit,
            )
            descriptions = dedupe_descriptions_for_autocomplete(raw_descriptions)

            self.description_completer_source_model.setStringList(descriptions)
            self.description_completer_proxy.invalidateFilter()

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
            currencies: list[str] = [row[1] for row in self.db_manager.get_all_currencies()]  # Get codes

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
            expense_categories: list[tuple[str, str]] = self.db_manager.get_categories_with_icons_by_type(0)
            income_categories: list[tuple[str, str]] = self.db_manager.get_categories_with_icons_by_type(1)

            model: QStandardItemModel = QStandardItemModel()

            # Add expense categories first
            for category_name, icon in expense_categories:
                # Create display text with icon
                display_text: str = f"{icon} {category_name}" if icon else category_name
                item: QStandardItem = QStandardItem(display_text)
                # Store the original category name as data for selection handling
                item.setData(category_name, Qt.ItemDataRole.UserRole)
                model.appendRow(item)

            # Add income categories with special marking
            for category_name, icon in income_categories:
                # Create display text with icon and income marker
                base_text: str = f"{icon} {category_name}" if icon else category_name
                display_text: str = f"{base_text} (Income)"  # Add income marker in parentheses
                item: QStandardItem = QStandardItem(display_text)
                # Store the original category name as data for selection handling
                item.setData(category_name, Qt.ItemDataRole.UserRole)
                model.appendRow(item)

            self.listView_categories.setModel(model)

            # Connect category selection signal after model is set
            self.listView_categories.selectionModel().currentChanged.connect(self.on_category_selection_changed)

            # Reset category selection
            self._clear_category_selection()

            # Set default currency selection
            default_currency: str = self.db_manager.get_default_currency()
            for combo in [
                self.comboBox_currency,
                self.comboBox_account_currency,
                self.comboBox_exchange_from,
                self.comboBox_default_currency,
            ]:
                index: int = combo.findText(default_currency)
                if index >= 0:
                    combo.setCurrentIndex(index)

            self._populate_chart_categories_list()

        except Exception as e:
            print(f"Error updating comboboxes: {e}")

    def _update_date_filter_visibility(self, *, enabled: bool) -> None:
        """Show or hide date filter fields based on checkBox_use_date_filter."""
        self.label_filter_date.setVisible(enabled)
        self.dateEdit_filter_from.setVisible(enabled)
        self.label_filter_to.setVisible(enabled)
        self.dateEdit_filter_to.setVisible(enabled)

    @requires_database()
    def _update_finance_chart(self) -> None:
        """Build and render the finance chart according to the selected chart type."""
        if self.db_manager is None:
            return

        if (
            self.radioButton_type_of_chart_compare_last_years.isChecked()
            or self.radioButton_expense_and_income_compare_last_years.isChecked()
        ) and not self._prompt_compare_last_years_start():
            return

        self._chart_build_toast = toast_countdown_notification.ToastCountdownNotification("Building chart…")
        self._chart_build_toast.start_countdown()
        QApplication.processEvents()

        try:
            self._clear_layout(self.verticalLayout_charts_content)

            period = self.comboBox_chart_period.currentText()
            date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
            date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")
            currency_symbol = self._get_default_currency_symbol()
            transaction_rows = self.db_manager.get_all_transactions()
            exchange_rows = self.db_manager.get_all_currency_exchanges()

            if self.radioButton_type_of_chart_balance.isChecked():
                period_end_dates = iter_period_end_dates(date_from, date_to, period)
                series = compute_balance_series(transaction_rows, exchange_rows, self.db_manager, period_end_dates)
                if not series:
                    self._show_no_data_label(
                        self.verticalLayout_charts_content,
                        "No data found for the selected period",
                    )
                    return
                self._draw_balance_chart(series, period, currency_symbol)
                return

            if self.radioButton_type_of_chart_compare_last.isChecked():
                self._draw_compare_chart("last")
                return

            if self.radioButton_type_of_chart_compare_last_years.isChecked():
                self._draw_compare_chart("last_years")
                return

            if self.radioButton_type_of_chart_compare_same_months.isChecked():
                self._draw_compare_chart("same")
                return

            expense_names, income_names, all_names = self._get_checked_chart_categories()

            if self.radioButton_expense_and_income_compare_last_years.isChecked():
                if not expense_names and not income_names:
                    self._show_no_data_label(
                        self.verticalLayout_charts_content,
                        "Please select at least one category",
                    )
                    return
                years_count = self.spinBox_compare_last.value()
                self._draw_expense_income_compare_last_years_chart(
                    expense_names,
                    income_names,
                    period,
                    currency_symbol,
                    years_count,
                )
                return

            if self.radioButton_expense_and_income.isChecked():
                if not expense_names and not income_names:
                    self._show_no_data_label(
                        self.verticalLayout_charts_content,
                        "Please select at least one category",
                    )
                    return

                expense_series: list[tuple[str, float]] | None = None
                income_series: list[tuple[str, float]] | None = None
                if expense_names:
                    expense_series = compute_period_flow_series(
                        transaction_rows,
                        self.db_manager,
                        date_from,
                        date_to,
                        period,
                        expense_names,
                        category_type=0,
                    )
                if income_names:
                    income_series = compute_period_flow_series(
                        transaction_rows,
                        self.db_manager,
                        date_from,
                        date_to,
                        period,
                        income_names,
                        category_type=1,
                    )
                if expense_series is None and income_series is None:
                    self._show_no_data_label(
                        self.verticalLayout_charts_content,
                        "No data found for the selected period",
                    )
                    return
                self._draw_expense_income_chart(expense_series, income_series, period, currency_symbol)
                return

            if not all_names:
                self._show_no_data_label(self.verticalLayout_charts_content, "Please select at least one category")
                return

            if self.radioButton_type_of_chart_category.isChecked():
                category_series = compute_period_flow_by_category(
                    transaction_rows,
                    self.db_manager,
                    date_from,
                    date_to,
                    period,
                    all_names,
                )
                if not category_series or all(not values for values in category_series.values()):
                    self._show_no_data_label(
                        self.verticalLayout_charts_content,
                        "No data found for the selected period",
                    )
                    return
                self._draw_category_chart(category_series, period, currency_symbol)
        finally:
            self._close_chart_build_toast()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Initialize main window for finance tracking application.

<details>
<summary>Code:</summary>

```python
def __init__(self, *, hide_on_close: bool = False) -> None:  # noqa: ARG002
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setupUi(self)
        self._setup_ui()
        self.setWindowIcon(QIcon(":/assets/logo.svg"))
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Initialize core attributes
        self._is_closing = False
        self.db_manager: database_manager.DatabaseManager | None = None
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        self._auto_save_handlers: dict[str, Any] = {}
        self._auto_save_source_models: dict[str, QObject | None] = {}
        self._transaction_selection_selection_model: QItemSelectionModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "transactions": None,
            "categories": None,
            "accounts": None,
            "currencies": None,
            "currency_exchanges": None,
            "exchange_rates": None,
        }

        # Delegates for transactions table
        self.description_delegate: DescriptionDelegate | None = None
        self.category_delegate: CategoryComboBoxDelegate | None = None
        self.currency_delegate: CurrencyComboBoxDelegate | None = None
        self.date_delegate: DateDelegate | None = None
        self.tag_delegate: TagDelegate | None = None

        # Dialog state flags
        self._exchange_dialog_open: bool = False
        self._bothub_state = BothubRequestState()

        # Generate pastel colors for date-based coloring
        self.date_colors: list[QColor] = generate_pastel_qcolors(50)

        # Initialize mouse button tracking
        self._right_click_in_progress: bool = False

        # Track whether account double-click handler is connected
        self._account_double_click_connected: bool = False

        # Toggle for showing all records vs last self.count_transactions_to_show
        finance_cfg: dict[str, Any] = self._app_config.get("finance") or {}
        self.count_transactions_to_show: int = finance_cfg.get("transactions_initial_count", 1000)
        self.transactions_load_more_count: int = finance_cfg.get("transactions_load_more_count", 500)
        self.count_exchange_rates_to_show: int = finance_cfg.get("exchange_rates_initial_count", 1000)
        self.exchange_rates_load_more_count: int = finance_cfg.get("exchange_rates_load_more_count", 500)
        self.description_autocomplete_limit: int = finance_cfg.get("description_autocomplete_limit", 1000)
        self.show_all_transactions: bool = False

        # Transactions table pagination state
        self._transactions_pagination = ScrollPagination()
        self._transactions_dates_with_totals: set[str] = set()
        self._transactions_date_color_map: dict[str, int] = {}
        self._transactions_color_index: int = 0

        # Exchange rates table pagination state
        self._exchange_rates_pagination = ScrollPagination()
        self._exchange_rates_filter_params: dict[str, Any] | None = None

        # Lazy loading flags
        self.exchange_rates_loaded: bool = False

        # Exchange rates initialization flag
        self._exchange_rates_initialized: bool = False
        self._exchange_rates_updating: bool = False

        # Reports-tab summary can be expensive to compute; refresh lazily.
        self._summary_dirty: bool = True

        # Charts tab: auto-draw only on first visit.
        self._charts_initialized: bool = False
        self._chart_build_toast: toast_countdown_notification.ToastCountdownNotification | None = None
        self._report_build_toast: toast_countdown_notification.ToastCountdownNotification | None = None
        self._compare_last_years_start_month: int = 1
        self._compare_last_years_start_day: int = 1

        # Dialog state flags
        self._account_edit_dialog_open: bool = False

        # Matplotlib object references
        self._current_exchange_rate_fig: Figure | None = None
        self._current_exchange_rate_canvas: FigureCanvas | None = None

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
                [
                    "From",
                    "To",
                    "Amount From",
                    "Amount To",
                    "Rate",
                    "Fee",
                    "Date",
                    "Description",
                    "Loss",
                    "Today's Loss",
                ],
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

        self._load_transactions_page(reset=True)
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
        self.radioButton_filter_type_all.setChecked(True)  # All
        self.comboBox_filter_category.setCurrentIndex(0)
        self.comboBox_filter_currency.setCurrentIndex(0)
        self.lineEdit_filter_description.clear()
        self.checkBox_use_date_filter.setChecked(False)

        current_date: QDate = QDateTime.currentDateTime().date()
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
        self._is_closing = True

        # Stop any running worker threads
        if hasattr(self, "exchange_rate_worker") and self.exchange_rate_worker.isRunning():
            self.exchange_rate_worker.stop()
            self.exchange_rate_worker.wait(3000)  # Wait up to 3 seconds

        # Stop checker thread if running
        if hasattr(self, "exchange_rate_checker") and self.exchange_rate_checker.isRunning():
            self.exchange_rate_checker.stop()
            self.exchange_rate_checker.wait(3000)  # Wait up to 3 seconds

        # Stop startup threads if running
        if hasattr(self, "startup_exchange_rate_worker") and self.startup_exchange_rate_worker.isRunning():
            self.startup_exchange_rate_worker.stop()
            self.startup_exchange_rate_worker.wait(3000)  # Wait up to 3 seconds

        if hasattr(self, "startup_exchange_rate_checker") and self.startup_exchange_rate_checker.isRunning():
            self.startup_exchange_rate_checker.stop()
            self.startup_exchange_rate_checker.wait(3000)  # Wait up to 3 seconds

        report_worker = getattr(self, "_report_build_worker", None)
        if report_worker is not None and report_worker.isRunning():
            report_worker.wait(3000)

        self._close_report_build_toast()

        # Close progress dialogs if open
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        if hasattr(self, "check_progress_dialog"):
            self.check_progress_dialog.close()

        if hasattr(self, "startup_progress_dialog"):
            self.startup_progress_dialog.close()

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

Delete selected row(s) from table using database manager methods.

For `transactions`, deletes every selected row; other tables delete one row.

Args:

- `table_name` (`str`): Name of the table to delete from. Must be in `_SAFE_TABLES`.

Raises:

- `ValueError`: If table_name is not in `_SAFE_TABLES`.

<details>
<summary>Code:</summary>

```python
def delete_record(self, table_name: str) -> None:
        if table_name not in self._SAFE_TABLES:
            error_message = f"Illegal table name: {table_name}"
            raise ValueError(error_message)

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Use appropriate database manager method
        success: bool = False
        try:
            if table_name == "transactions":
                record_ids: list[int] = self._get_selected_row_ids(table_name)
                if not record_ids:
                    message_box.warning(self, "Error", "Select a record to delete")
                    return
                deleted_any = False
                for rid in record_ids:
                    if self.db_manager.delete_transaction(rid):
                        deleted_any = True
                    else:
                        message_box.warning(self, "Error", f"Failed to delete transaction {rid}")
                if deleted_any:
                    self._mark_transactions_changed()
                success = deleted_any
            else:
                record_id: int | None = self._get_selected_row_id(table_name)
                if record_id is None:
                    message_box.warning(self, "Error", "Select a record to delete")
                    return
                if table_name == "categories":
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
            message_box.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            # Save current column widths before update for exchange table
            column_widths: list[int] | None = None
            if table_name == "currency_exchanges":
                column_widths = self._save_table_column_widths(self.tableView_exchange)

            self.update_all()

            # Restore column widths after update for exchange table
            if table_name == "currency_exchanges" and column_widths:
                self._restore_table_column_widths(self.tableView_exchange, column_widths)

            self.update_summary_labels()
        else:
            message_box.warning(self, "Error", f"Deletion failed in {table_name}")
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool
```

Event filter for handling mouse and key events.

Args:

- `obj` (`QObject`): The object being filtered.
- `event` (`QEvent`): The event being filtered.

Returns:

- `bool`: True if event should be filtered, False otherwise.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        # Track right mouse button on the table's viewport to suppress data copy on right-click
        if obj == self.tableView_transactions.viewport():
            if event.type() == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent):
                if event.button() == Qt.MouseButton.RightButton:
                    self._right_click_in_progress = True
                else:
                    self._right_click_in_progress = False

            elif (
                event.type() == QEvent.Type.MouseButtonRelease
                and isinstance(event, QMouseEvent)
                and event.button() == Qt.MouseButton.RightButton
            ):
                # Reset the flag shortly after release to allow context menu to process
                QTimer.singleShot(100, lambda: setattr(self, "_right_click_in_progress", False))

        if (
            obj == self.label_category_now
            and event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._show_category_label_context_menu(event.position().toPoint())
            return True

        # Handle Enter key to add transaction quickly
        if (
            (
                (obj == self.doubleSpinBox_amount and event.type() == QEvent.Type.KeyPress)
                or (obj == self.dateEdit and event.type() == QEvent.Type.KeyPress)
                or (obj == self.lineEdit_tag and event.type() == QEvent.Type.KeyPress)
                or (obj == self.lineEdit_description and event.type() == QEvent.Type.KeyPress)
                or (obj == self.pushButton_add and event.type() == QEvent.Type.KeyPress)
            )
            and isinstance(event, QKeyEvent)
            and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
        ):
            self.on_add_transaction()
            return True

        return super().eventFilter(obj, event)
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
        if self._handle_ctrl_c_for_tables(
            event,
            [
                self.tableView_transactions,
                self.tableView_categories,
                self.tableView_accounts,
                self.tableView_currencies,
                self.tableView_exchange,
                self.tableView_exchange_rates,
                self.tableView_reports,
            ],
        ):
            return

        super().keyPressEvent(event)
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

        def get_and_validate() -> tuple[str | None, Any]:
            name = self.lineEdit_account_name.text().strip()
            balance = self.doubleSpinBox_account_balance.value()
            currency_code = self.comboBox_account_currency.currentText()
            is_liquid = self.checkBox_is_liquid.isChecked()
            is_cash = self.checkBox_is_cash.isChecked()
            if not name:
                return ("Enter account name", None)
            if not currency_code:
                return ("Select a currency", None)
            if self.db_manager is None:
                return ("Database not initialized", None)
            currency_info = self.db_manager.get_currency_by_code(currency_code)
            if not currency_info:
                return (f"Currency '{currency_code}' not found", None)
            return (None, (name, balance, currency_info[0], is_liquid, is_cash))

        def add_db(data: Any) -> bool:
            name, balance, currency_id, is_liquid, is_cash = data
            return bool(
                self.db_manager
                and self.db_manager.add_account(name, balance, currency_id, is_liquid=is_liquid, is_cash=is_cash)
            )

        def on_success(_data: Any) -> None:
            self.update_all()
            self._clear_account_form()

        self._add_record("account", get_and_validate, add_db, on_success)
```

</details>

### ⚙️ Method `on_add_as_text_with_ai`

```python
def on_add_as_text_with_ai(self) -> None
```

Collect text/image, call BotHub, then open purchase text dialog with AI result.

<details>
<summary>Code:</summary>

```python
def on_add_as_text_with_ai(self) -> None:
        bothub_cfg = self._app_config.get("bothub") or {}
        max_image_side = int(bothub_cfg.get("max_image_side", 1600))
        source_dialog = AiSourceDialog(self, max_image_side=max_image_side)
        source_result = source_dialog.exec()
        if source_result == QDialog.DialogCode.Rejected:
            return
        if source_result == AiSourceDialog.SKIP_MANUAL:
            self._open_text_input_dialog(self.dateEdit.date())
            return

        raw_text = source_dialog.get_raw_text()
        image_data = source_dialog.get_image_bytes_and_mime()

        try:
            prompt_text = build_prompt(self._app_config, "finance_purchases_to_tsv", {"RAW_DATA": raw_text})
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            self._open_text_input_dialog(
                self.dateEdit.date(),
                initial_text=response_text,
                focus_text_on_show=False,
            )

        run_bothub_request(
            self,
            self._app_config,
            prompt_text,
            on_success,
            image=image_data,
            is_busy=lambda: self._bothub_state.worker is not None,
            state=self._bothub_state,
        )
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

        def get_and_validate() -> tuple[str | None, Any]:
            name = self.lineEdit_category_name.text().strip()
            category_type = self.comboBox_category_type.currentIndex()
            if not name:
                return ("Enter category name", None)
            if self.db_manager is None:
                return ("Database not initialized", None)
            return (None, (name, category_type))

        def add_db(data: Any) -> bool:
            name, category_type = data
            return bool(self.db_manager and self.db_manager.add_category(name, category_type))

        def on_success(_data: Any) -> None:
            self._mark_categories_changed()
            self.update_all()
            self._clear_category_form()

        self._add_record("category", get_and_validate, add_db, on_success)
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

        def get_and_validate() -> tuple[str | None, Any]:
            code = self.lineEdit_currency_code.text().strip().upper()
            name = self.lineEdit_currency_name.text().strip()
            symbol = self.lineEdit_currency_symbol.text().strip()
            subdivision = self.spinBox_subdivision.value()
            if not code:
                return ("Enter currency code", None)
            if not name:
                return ("Enter currency name", None)
            if not symbol:
                return ("Enter currency symbol", None)
            if subdivision <= 0:
                return ("Subdivision must be a positive number", None)
            if self.db_manager is None:
                return ("Database not initialized", None)
            return (None, (code, name, symbol, subdivision))

        def add_db(data: Any) -> bool:
            code, name, symbol, subdivision = data
            return bool(self.db_manager and self.db_manager.add_currency(code, name, symbol, subdivision))

        def on_success(_data: Any) -> None:
            self._mark_currencies_changed()
            self.update_all()
            self._clear_currency_form()

        self._add_record("currency", get_and_validate, add_db, on_success)
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

        def get_and_validate() -> tuple[str | None, Any]:
            from_currency = self.comboBox_exchange_from.currentText()
            to_currency = self.comboBox_exchange_to.currentText()
            amount_from = self.doubleSpinBox_exchange_from.value()
            amount_to = self.doubleSpinBox_exchange_to.value()
            exchange_rate = self.doubleSpinBox_exchange_rate.value()
            fee = self.doubleSpinBox_exchange_fee.value()
            date = self.dateEdit_exchange.date().toString("yyyy-MM-dd")
            description = self.lineEdit_exchange_description.text().strip()
            errors = validate_exchange_data(from_currency, to_currency, amount_from, amount_to, exchange_rate, fee)
            if errors:
                return (errors[0], None)
            if self.db_manager is None:
                return ("Database not initialized", None)
            from_currency_info = self.db_manager.get_currency_by_code(from_currency)
            to_currency_info = self.db_manager.get_currency_by_code(to_currency)
            if not from_currency_info or not to_currency_info:
                return ("Currency not found", None)
            return (
                None,
                (
                    from_currency_info[0],
                    to_currency_info[0],
                    amount_from,
                    amount_to,
                    exchange_rate,
                    fee,
                    date,
                    description,
                ),
            )

        def add_db(data: Any) -> bool:
            (from_id, to_id, amount_from, amount_to, rate, fee, date, description) = data
            return bool(
                self.db_manager
                and self.db_manager.add_currency_exchange(
                    from_id, to_id, amount_from, amount_to, rate, fee, date, description
                )
            )

        def on_success(_data: Any) -> None:
            column_widths = self._save_table_column_widths(self.tableView_exchange)
            self.update_all()
            self._restore_table_column_widths(self.tableView_exchange, column_widths)
            self._clear_exchange_form()

        self._add_record("currency exchange", get_and_validate, add_db, on_success)
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

        def get_and_validate() -> tuple[str | None, Any]:
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
                return ("Amount must be positive", None)
            if not description:
                return ("Enter description", None)
            if not category_name:
                return ("Select a category", None)
            if not currency_code:
                return ("Select a currency", None)
            if self.db_manager is None:
                return ("Database not initialized", None)
            cat_id = self.db_manager.get_id("categories", "name", category_name)
            if cat_id is None:
                return (f"Category '{category_name}' not found", None)
            currency_info = self.db_manager.get_currency_by_code(currency_code)
            if not currency_info:
                return (f"Currency '{currency_code}' not found", None)
            return (None, (amount, description, cat_id, currency_info[0], date, tag))

        def add_db(data: Any) -> bool:
            amount, description, cat_id, currency_id, date, tag = data
            return bool(
                self.db_manager and self.db_manager.add_transaction(amount, description, cat_id, currency_id, date, tag)
            )

        def on_success(data: Any) -> None:
            _amount, _desc, _cat_id, _curr_id, _date, _tag = data
            current_date = self.dateEdit.date()
            self._mark_transactions_changed()
            self.update_all()
            self._update_autocomplete_data()
            self.doubleSpinBox_amount.setValue(100.0)
            self.lineEdit_description.clear()
            self.lineEdit_tag.clear()
            self.dateEdit.setDate(current_date)
            QTimer.singleShot(100, self._focus_description_and_select_text)

        self._add_record("transaction", get_and_validate, add_db, on_success)
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
        amount_from: float = self.doubleSpinBox_exchange_from.value()
        rate: float = self.doubleSpinBox_exchange_rate.value()

        if rate > 0:
            amount_to: float = amount_from * rate
            self.doubleSpinBox_exchange_to.setValue(amount_to)
```

</details>

### ⚙️ Method `on_calculate_fee`

```python
def on_calculate_fee(self) -> None
```

Calculate fee based on actual exchange vs expected exchange.

<details>
<summary>Code:</summary>

```python
def on_calculate_fee(self) -> None:
        amount_from: float = self.doubleSpinBox_exchange_from.value()
        amount_to: float = self.doubleSpinBox_exchange_to.value()
        exchange_rate: float = self.doubleSpinBox_exchange_rate.value()

        if exchange_rate > 0:
            # Calculate what amount_from should have been if they received amount_to at exchange_rate
            expected_amount_from: float = amount_to / exchange_rate

            # Calculate the fee as the difference
            calculated_fee: float = amount_from - expected_amount_from

            # Get current fee value
            current_fee: float = self.doubleSpinBox_exchange_fee.value()

            # If current fee is non-zero, add to it, otherwise set it
            if current_fee != 0:
                new_fee: float = current_fee + calculated_fee
            else:
                new_fee: float = calculated_fee

            self.doubleSpinBox_exchange_fee.setValue(new_fee)
```

</details>

### ⚙️ Method `on_category_selection_changed`

```python
def on_category_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None
```

Handle category selection change in listView_categories.

Args:

- `current` (`QModelIndex`): Current selected index.
- `_previous` (`QModelIndex`): Previously selected index.

<details>
<summary>Code:</summary>

```python
def on_category_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if current.isValid():
            # Get the display text (with icon and income marker if applicable)
            display_text: str | None = current.data(Qt.ItemDataRole.DisplayRole)
            if display_text:
                self.label_category_now.setText(display_text)
            else:
                self.label_category_now.setText(self._NO_CATEGORY_LABEL)

            # Move focus to description field and select all text
            QTimer.singleShot(100, self._focus_description_and_select_text)
        else:
            self.label_category_now.setText(self._NO_CATEGORY_LABEL)
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

### ⚙️ Method `on_copy_categories_as_text`

```python
def on_copy_categories_as_text(self) -> None
```

Copy list of categories to clipboard as text.

<details>
<summary>Code:</summary>

```python
def on_copy_categories_as_text(self) -> None:
        if self.db_manager is None:
            message_box.warning(
                self, "Database Error", "❌ Database manager is not initialized. Please try again later."
            )
            return

        try:
            # Get all categories
            categories_data: list = self.db_manager.get_all_categories()

            if not categories_data:
                message_box.information(self, "No Categories", "No categories found in the database.")
                return

            # Create text representation
            categories_text: list[str] = []
            for row in categories_data:
                category_name: str = row[1]  # name column
                categories_text.append(category_name)

            # Join with newlines
            clipboard_text: str = "\n".join(categories_text)

            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(clipboard_text)

            # Show success message to user
            message_box.information(
                self,
                "Categories Copied",
                f"✅ Successfully copied {len(categories_text)} categories to clipboard:\n\n{clipboard_text}",
            )

        except Exception as e:
            message_box.critical(self, "Error", f"❌ Error copying categories to clipboard:\n\n{e!s}")
```

</details>

### ⚙️ Method `on_exchange_item_update_button_clicked`

```python
def on_exchange_item_update_button_clicked(self) -> None
```

Update exchange rate in database when pushButton_exchange_item_update is clicked.

<details>
<summary>Code:</summary>

```python
def on_exchange_item_update_button_clicked(self) -> None:
        try:
            # Get selected currency ID
            currency_index: int = self.comboBox_exchange_item_update.currentIndex()
            if currency_index < 0:
                message_box.warning(self, "Invalid Selection", "Please select a currency.")
                return

            currency_id = self.comboBox_exchange_item_update.itemData(currency_index)
            if currency_id is None:
                message_box.warning(self, "Invalid Selection", "Please select a valid currency.")
                return

            # Get selected date
            selected_date: QDate = self.dateEdit_exchange_item_update.date()
            date_str: str = selected_date.toString("yyyy-MM-dd")

            # Get exchange rate value
            exchange_rate: float = self.doubleSpinBox_exchange_item_update.value()
            if exchange_rate <= 0:
                message_box.warning(self, "Invalid Rate", "Exchange rate must be greater than 0.")
                return

            # Get currency info for confirmation dialog
            currency_text: str = self.comboBox_exchange_item_update.currentText()

            # Confirm update
            reply = message_box.question(
                self,
                "Confirm Exchange Rate Update",
                f"Update exchange rate for {currency_text} on {date_str} to {exchange_rate}?\n\n"
                "This action will overwrite any existing rate for this currency and date.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Update exchange rate in database
            success: bool = self.db_manager.update_exchange_rate(currency_id, date_str, exchange_rate)

            if success:
                message_box.information(
                    self,
                    "Update Successful",
                    f"Exchange rate for {currency_text} on {date_str} has been updated to {exchange_rate}.",
                )
                # Clear exchange rate cache to ensure fresh data
                self.db_manager.exchange_rates.clear_cache()
                # Update all views
                self.update_all()
                self.update_summary_labels()
                # Update exchange rates chart if on the same currency
                self.on_exchange_rates_update()
            else:
                message_box.warning(
                    self,
                    "Update Failed",
                    "Failed to update exchange rate. Please check the database connection and try again.",
                )

        except Exception as e:
            message_box.critical(self, "Error", f"An error occurred while updating exchange rate: {e}")
```

</details>

### ⚙️ Method `on_exchange_item_update_changed`

```python
def on_exchange_item_update_changed(self) -> None
```

Update exchange rate in doubleSpinBox_exchange_item_update when currency or date changes.

<details>
<summary>Code:</summary>

```python
def on_exchange_item_update_changed(self) -> None:
        if not self._validate_database_connection():
            return

        try:
            # Get selected currency ID
            currency_index: int = self.comboBox_exchange_item_update.currentIndex()
            if currency_index < 0:
                self.doubleSpinBox_exchange_item_update.setValue(0.0)
                return

            currency_id = self.comboBox_exchange_item_update.itemData(currency_index)
            if currency_id is None:
                self.doubleSpinBox_exchange_item_update.setValue(0.0)
                return

            # Get selected date
            selected_date: QDate = self.dateEdit_exchange_item_update.date()
            date_str: str = selected_date.toString("yyyy-MM-dd")

            # Get exchange rate from database
            exchange_rate: float = self.db_manager.get_currency_exchange_rate_by_date(currency_id, date_str)

            # Update the doubleSpinBox
            self.doubleSpinBox_exchange_item_update.setValue(exchange_rate)

        except Exception as e:
            print(f"Error updating exchange item update rate: {e}")
            self.doubleSpinBox_exchange_item_update.setValue(0.0)
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
        filename_str: str
        filename_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save Table",
            "",
            "CSV (*.csv)",
        )
        if not filename_str:
            return

        try:
            filename: Path = Path(filename_str)
            proxy_model = self.models["transactions"]
            if proxy_model is None or not isinstance(proxy_model, QSortFilterProxyModel):
                return
            model = proxy_model.sourceModel()
            if model is None:
                return
            with filename.open("w", encoding="utf-8") as file:
                headers: list[str] = [
                    model.headerData(col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) or ""
                    for col in range(model.columnCount())
                ]
                file.write(";".join(headers) + "\n")

                for row in range(model.rowCount()):
                    row_values: list[str] = [
                        f'"{model.data(model.index(row, col)) or ""}"' for col in range(model.columnCount())
                    ]
                    file.write(";".join(row_values) + "\n")

        except Exception as e:
            message_box.warning(self, "Export Error", f"Failed to export CSV: {e}")
```

</details>

### ⚙️ Method `on_generate_report`

```python
def on_generate_report(self) -> None
```

Generate selected report on a background thread with a countdown toast.

<details>
<summary>Code:</summary>

```python
def on_generate_report(self, *, refresh_summary: bool = False) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        worker = getattr(self, "_report_build_worker", None)
        if worker is not None and worker.isRunning():
            return

        report_type: str = self.comboBox_report_type.currentText()

        try:
            db_filename = _require_db_filename_for_worker(self.db_manager)
        except DbFilenameUnavailableForWorkerThreadError:
            message_box.warning(self, "Error", "Database path is not available for report generation.")
            return

        self._report_build_toast = toast_countdown_notification.ToastCountdownNotification("Building report…")
        self._report_build_toast.start_countdown()

        if refresh_summary:
            self._refresh_summary_if_needed()

        self._report_build_worker = ReportBuildWorker(db_filename, report_type)
        self._report_build_worker.report_completed.connect(self._on_report_build_completed)
        self._report_build_worker.report_failed.connect(self._on_report_build_failed)
        self._report_build_worker.finished.connect(self._cleanup_report_build_worker)
        self.pushButton_generate_report.setEnabled(False)
        self._report_build_worker.start()
```

</details>

### ⚙️ Method `on_select_only_expense_chart_categories`

```python
def on_select_only_expense_chart_categories(self) -> None
```

Check only expense categories in the Charts category list.

<details>
<summary>Code:</summary>

```python
def on_select_only_expense_chart_categories(self) -> None:
        self._select_only_chart_categories(0)
```

</details>

### ⚙️ Method `on_select_only_income_chart_categories`

```python
def on_select_only_income_chart_categories(self) -> None
```

Check only income categories in the Charts category list.

<details>
<summary>Code:</summary>

```python
def on_select_only_income_chart_categories(self) -> None:
        self._select_only_chart_categories(1)
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
        currency_code: str = self.comboBox_default_currency.currentText()

        if not currency_code:
            message_box.warning(self, "Error", "Select a currency")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.set_default_currency(currency_code):
                message_box.information(self, "Success", f"Default currency set to {currency_code}")
                # Mark default currency changed for lazy loading
                self._mark_default_currency_changed()
                # Update all displays that depend on default currency
                self.update_summary_labels()
                self._update_comboboxes()
                self._update_accounts_balance_display()
                # Recalculate transaction-derived columns (e.g., "Total per day") in new default currency
                self._load_transactions_table()
                self._connect_table_auto_save_signals()
                self._load_currency_exchanges_table()
            else:
                message_box.warning(self, "Error", "Failed to set default currency")
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to set default currency: {e}")
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

        self._load_transactions_page(reset=True)
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
        id_exchange_rates_tab: int = 4
        id_charts_tab: int = 5
        id_reports_tab: int = 6
        if index == id_exchange_rates_tab:  # Exchange Rates tab - lazy loading
            if not self.exchange_rates_loaded:
                self.load_exchange_rates_table()
        elif index == id_charts_tab:  # Charts tab - auto-draw on first visit
            if not self._charts_initialized:
                self._update_finance_chart()
                self._charts_initialized = True
        elif index == id_reports_tab:  # Reports tab
            self.on_generate_report(refresh_summary=True)
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
        yesterday: QDate = QDate.currentDate().addDays(-1)
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
        yesterday: QDate = QDate.currentDate().addDays(-1)
        self.dateEdit_exchange.setDate(yesterday)
```

</details>

### ⚙️ Method `set_chart_all_time`

```python
def set_chart_all_time(self) -> None
```

Set chart date range from the first transaction to today.

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

Set chart start date to one month ago and end date to today.

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

Set chart start date to one year ago and end date to today.

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

Set today's date in all date fields.

<details>
<summary>Code:</summary>

```python
def set_today_date(self) -> None:
        today_qdate: QDate = QDate.currentDate()
        self.dateEdit.setDate(today_qdate)
        self.dateEdit_exchange.setDate(today_qdate)
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
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Load essential tables only (exclude exchange_rates)
            self._load_essential_tables()

            # Exchange rates table loaded lazily on first tab access

        except Exception as e:
            print(f"Error showing tables: {e}")
            message_box.warning(self, "Database Error", f"Failed to load tables: {e}")
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
        # Load essential tables
        self._load_essential_tables()
        self._update_comboboxes()
        self.update_filter_comboboxes()
        self.set_today_date()
        self._mark_summary_dirty()
        self._refresh_summary_if_needed()

        # If exchange rates tab is currently active, reload the data
        current_tab_index: int = self.tabWidget.currentIndex()
        id_exchange_rates_tab = 4
        if current_tab_index == id_exchange_rates_tab:  # Exchange Rates tab
            self.load_exchange_rates_table()
        else:
            # Mark exchange rates as not loaded to force reload when tab is accessed
            self.exchange_rates_loaded = False

        # Clear forms
        self._clear_all_forms()
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
            categories: list[str] = self.db_manager.get_categories_by_type(0) + self.db_manager.get_categories_by_type(
                1
            )

            self.comboBox_filter_category.clear()
            self.comboBox_filter_category.addItem("")  # All categories
            self.comboBox_filter_category.addItems(categories)

            # Update currency filter
            currencies: list[str] = [row[1] for row in self.db_manager.get_all_currencies()]  # Get codes

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

Update Quick Summary / today and yesterday labels using natural per-currency amounts.

<details>
<summary>Code:</summary>

```python
def update_summary_labels(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            db = self.db_manager
            default_currency_info = db.get_currency_by_code(db.get_default_currency())
            currency_symbol: str = default_currency_info[2] if default_currency_info else "₽"

            transaction_rows: list = db.get_all_transactions()

            income_minor: dict[int, int]
            expense_minor: dict[int, int]
            income_minor, expense_minor = get_natural_cumulative_income_expense_minor_by_currency(transaction_rows, db)

            def _currency_sort_key(cid: int) -> str:
                cur = db.get_currency_by_id(cid)
                return cur[0] if cur else f"#{cid}"

            income_lines: list[str] = []
            for cid in sorted(income_minor, key=_currency_sort_key):
                minor = income_minor[cid]
                if minor == 0:
                    continue
                cur = db.get_currency_by_id(cid)
                code = cur[0] if cur else str(cid)
                sym = cur[2] if cur else ""
                major = db.convert_from_minor_units(minor, cid)
                income_lines.append(f"{code}: {major:,.2f}{sym}")
            income_text = (
                "Total Income:\n" + "\n".join(income_lines) if income_lines else f"Total Income:\n0.00{currency_symbol}"
            )
            self.label_total_income.setText(income_text)

            expense_lines: list[str] = []
            for cid in sorted(expense_minor, key=_currency_sort_key):
                minor = expense_minor[cid]
                if minor == 0:
                    continue
                cur = db.get_currency_by_id(cid)
                code = cur[0] if cur else str(cid)
                sym = cur[2] if cur else ""
                major = db.convert_from_minor_units(minor, cid)
                expense_lines.append(f"{code}: {major:,.2f}{sym}")
            expense_text = (
                "Total Expenses:\n" + "\n".join(expense_lines)
                if expense_lines
                else f"Total Expenses:\n0.00{currency_symbol}"
            )
            self.label_total_expenses.setText(expense_text)

            today: date = datetime.now(UTC).astimezone().date()
            today_str: str = today.strftime("%Y-%m-%d")
            yesterday_str: str = (today - timedelta(days=1)).strftime("%Y-%m-%d")

            def _expense_lines_for_date(target_date: str) -> list[str]:
                expense_minor_by_date: dict[int, int] = {}
                for row in transaction_rows:
                    if len(row) < MIN_TRANSACTION_ROW_LENGTH:
                        continue
                    if row[5] != target_date or int(row[7]) != 0:
                        continue
                    currency_info = db.get_currency_by_code(row[4])
                    cid = currency_info[0] if currency_info else 1
                    expense_minor_by_date[cid] = expense_minor_by_date.get(cid, 0) + int(row[1])

                lines: list[str] = []
                for cid in sorted(expense_minor_by_date, key=_currency_sort_key):
                    minor = expense_minor_by_date[cid]
                    if minor == 0:
                        continue
                    cur = db.get_currency_by_id(cid)
                    code = cur[0] if cur else str(cid)
                    sym = cur[2] if cur else ""
                    major = db.convert_from_minor_units(minor, cid)
                    lines.append(f"{code}: {major:,.2f}{sym}")
                return lines

            expense_today_lines: list[str] = _expense_lines_for_date(today_str)
            if expense_today_lines:
                self.label_today_expense.setText("\n".join(expense_today_lines))
            else:
                self.label_today_expense.setText(f"0.00{currency_symbol}")

            expense_yesterday_lines: list[str] = _expense_lines_for_date(yesterday_str)
            if expense_yesterday_lines:
                self.label_yesterday_expense.setText("\n".join(expense_yesterday_lines))
            else:
                self.label_yesterday_expense.setText(f"0.00{currency_symbol}")

        except Exception as e:
            print(f"Error updating summary labels: {e}")
            # Set default values on error
            self.label_total_income.setText("Total Income: 0.00₽")
            self.label_total_expenses.setText("Total Expenses: 0.00₽")
            self.label_today_expense.setText("0.00₽")
            self.label_yesterday_expense.setText("0.00₽")
```

</details>
