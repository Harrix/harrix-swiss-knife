---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exchange_rates_operations.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DbFilenameUnavailableForWorkerThreadError`](#️-class-dbfilenameunavailableforworkerthreaderror)
  - [⚙️ Method `__init__`](#️-method-__init__)
- [🏛️ Class `ExchangeRatesOperations`](#️-class-exchangeratesoperations)
  - [⚙️ Method `load_exchange_rates_table`](#️-method-load_exchange_rates_table)
  - [⚙️ Method `on_delete_exchange_rates_by_days`](#️-method-on_delete_exchange_rates_by_days)
  - [⚙️ Method `on_exchange_rates_all_time`](#️-method-on_exchange_rates_all_time)
  - [⚙️ Method `on_exchange_rates_currency_changed`](#️-method-on_exchange_rates_currency_changed)
  - [⚙️ Method `on_exchange_rates_last_month`](#️-method-on_exchange_rates_last_month)
  - [⚙️ Method `on_exchange_rates_last_year`](#️-method-on_exchange_rates_last_year)
  - [⚙️ Method `on_exchange_rates_update`](#️-method-on_exchange_rates_update)
  - [⚙️ Method `on_filter_exchange_rates_apply`](#️-method-on_filter_exchange_rates_apply)
  - [⚙️ Method `on_filter_exchange_rates_clear`](#️-method-on_filter_exchange_rates_clear)
  - [⚙️ Method `on_update_exchange_rates`](#️-method-on_update_exchange_rates)

</details>

## 🏛️ Class `DbFilenameUnavailableForWorkerThreadError`

```python
class DbFilenameUnavailableForWorkerThreadError(RuntimeError)
```

Database filename is not available for worker thread.

<details>
<summary>Code:</summary>

```python
class DbFilenameUnavailableForWorkerThreadError(RuntimeError):

    def __init__(self) -> None:
        """Create exception with standard message."""
        super().__init__("Database filename is not available for worker thread")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create exception with standard message.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__("Database filename is not available for worker thread")
```

</details>

## 🏛️ Class `ExchangeRatesOperations`

```python
class ExchangeRatesOperations
```

Mixin class for exchange rates operations.

<details>
<summary>Code:</summary>

```python
class ExchangeRatesOperations:

    def load_exchange_rates_table(self) -> None:
        """Load exchange rates table data (lazy loading)."""
        if not self._validate_database_connection():
            print("Database connection not available for loading exchange rates")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            self._exchange_rates_filter_params = None
            self._load_exchange_rates_page(reset=True)
            self.exchange_rates_loaded = True
            QTimer.singleShot(50, self.on_exchange_rates_update)
        except Exception as e:
            print(f"❌ Error loading exchange rates table: {e}")

    def on_delete_exchange_rates_by_days(self) -> None:
        """Delete exchange rates for the last N days based on spinBox_exchange_rate_count_days value."""
        if not self._validate_database_connection():
            return

        try:
            # Get the number of days from the spin box
            days = self.spinBox_exchange_rate_count_days.value()

            if days <= 0:
                message_box.warning(cast("QWidget", self), "Invalid Input", "Number of days must be greater than 0.")
                return

            # Show confirmation dialog
            reply = message_box.question(
                cast("QWidget", self),
                "Confirm Deletion",
                f"Are you sure you want to delete exchange rates for the last {days} days?\n\n"
                "This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Delete exchange rates
            success, deleted_count = self.db_manager.delete_exchange_rates_by_days(days)

            if success:
                if deleted_count > 0:
                    message_box.information(
                        cast("QWidget", self),
                        "Deletion Successful",
                        f"Successfully deleted {deleted_count} exchange rate records for the last {days} days.",
                    )
                else:
                    message_box.information(
                        cast("QWidget", self),
                        "No Records Found",
                        (f"No exchange rate records were found for the last {days} days."),
                    )

                # Mark exchange rates as changed and update the view
                self._mark_exchange_rates_changed()
                self.update_all()
                self.update_summary_labels()
            else:
                message_box.warning(
                    cast("QWidget", self),
                    "Deletion Failed",
                    "Failed to delete exchange rate records. Please check the database connection.",
                )

        except Exception as e:
            message_box.critical(
                cast("QWidget", self), "Error", f"An error occurred while deleting exchange rates: {e}"
            )

    def on_exchange_rates_all_time(self) -> None:
        """Set date range to all available data."""
        self._set_exchange_rates_date_range()
        # Automatically update the chart with a small delay to ensure dates are properly set
        QTimer.singleShot(50, self.on_exchange_rates_update)

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
        # Automatically update the chart with a small delay to ensure dates are properly set
        QTimer.singleShot(50, self.on_exchange_rates_update)

    def on_exchange_rates_last_year(self) -> None:
        """Set date range to last year."""
        current_date = QDate.currentDate()
        last_year = current_date.addYears(-1)
        self.dateEdit_exchange_rates_from.setDate(last_year)
        self.dateEdit_exchange_rates_to.setDate(current_date)
        # Automatically update the chart with a small delay to ensure dates are properly set
        QTimer.singleShot(50, self.on_exchange_rates_update)

    def on_exchange_rates_update(self) -> None:
        """Update the exchange rate chart."""
        # Check if exchange rates controls have been initialized
        if not hasattr(self, "_exchange_rates_initialized") or not self._exchange_rates_initialized:
            return

        # Prevent multiple simultaneous updates
        if hasattr(self, "_exchange_rates_updating") and self._exchange_rates_updating:
            return

        # Check if previous chart is still being created or if we need to wait for cleanup
        if hasattr(self, "_current_exchange_rate_canvas") and self._current_exchange_rate_canvas is not None:
            try:
                # Test if canvas is still valid
                if not self._current_exchange_rate_canvas.figure:
                    return
                # Additional check: if canvas is being deleted, wait a bit
                if (
                    hasattr(self._current_exchange_rate_canvas, "deleting")
                    and self._current_exchange_rate_canvas.deleting
                ):
                    return
            except Exception:
                return

        try:
            self._exchange_rates_updating = True

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
                message_box.warning(cast("QWidget", self), "Invalid Date Range", "Start date cannot be after end date.")
                return

            # Create chart
            self._create_exchange_rate_chart(currency_id, date_from, date_to)

        finally:
            self._exchange_rates_updating = False

    def on_filter_exchange_rates_apply(self) -> None:
        """Apply filter to exchange rates based on selected criteria."""
        if not self._validate_database_connection():
            return

        try:
            # Get filter criteria
            currency_id = None
            currency_index = self.comboBox_exchange_rates_filter_currency.currentIndex()

            # Check if "All currencies" is selected (index 0)
            if currency_index > 0:
                currency_id = self.comboBox_exchange_rates_filter_currency.itemData(currency_index)

            # Get date range
            date_from = self.dateEdit_filter_exchange_rates_from.date().toString("yyyy-MM-dd")
            date_to = self.dateEdit_filter_exchange_rates_to.date().toString("yyyy-MM-dd")

            # Validate date range
            if self.dateEdit_filter_exchange_rates_from.date() > self.dateEdit_filter_exchange_rates_to.date():
                message_box.warning(cast("QWidget", self), "Invalid Date Range", "Start date cannot be after end date.")
                return

            self._exchange_rates_filter_params = {
                "currency_id": currency_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            self._load_exchange_rates_page(reset=True)

            # Show information about filter results
            filter_info = []
            if currency_id is not None:
                currency_text = self.comboBox_exchange_rates_filter_currency.currentText()
                filter_info.append(f"Currency: {currency_text}")
            else:
                filter_info.append("Currency: All currencies")

            filter_info.append(f"Date range: {date_from} to {date_to}")
            filter_info.append(f"Records loaded: {self._exchange_rates_pagination.loaded_count}")
            if self._exchange_rates_pagination.has_more:
                filter_info.append("Scroll down to load more records")

            message_box.information(
                cast("QWidget", self),
                "Filter Applied",
                "Exchange rates filter has been applied.\n\n" + "\n".join(filter_info),
            )

        except Exception as e:
            message_box.critical(cast("QWidget", self), "Filter Error", f"An error occurred while applying filter: {e}")

    def on_filter_exchange_rates_clear(self) -> None:
        """Clear exchange rates filter and show default number of records."""
        if not self._validate_database_connection():
            return

        try:
            # Reset filter controls to default values
            self.comboBox_exchange_rates_filter_currency.setCurrentIndex(0)  # "All currencies"

            # Reset date range to match main date controls
            self.dateEdit_filter_exchange_rates_from.setDate(self.dateEdit_exchange_rates_from.date())
            self.dateEdit_filter_exchange_rates_to.setDate(self.dateEdit_exchange_rates_to.date())

            self._exchange_rates_filter_params = None
            self._load_exchange_rates_page(reset=True)

            message_box.information(
                cast("QWidget", self),
                "Filter Cleared",
                (
                    "Exchange rates filter has been cleared.\n"
                    f"Showing {self._exchange_rates_pagination.loaded_count} most recent records."
                ),
            )

        except Exception as e:
            message_box.critical(
                cast("QWidget", self), "Clear Filter Error", f"An error occurred while clearing filter: {e}"
            )

    def on_update_exchange_rates(self) -> None:
        """Update and fill missing exchange rate records for each currency from yfinance."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Configuration option: check from first transaction or from last exchange rate
            check_from_first_transaction = True  # Set to False to check only from last exchange rate

            # Check if checker is already running
            if hasattr(self, "exchange_rate_checker") and self.exchange_rate_checker.isRunning():
                message_box.warning(
                    cast("QWidget", self),
                    "Check in Progress",
                    "Exchange rate check is already running. Please wait for it to complete.",
                )
                return

            # Check if updater is already running
            if hasattr(self, "exchange_rate_worker") and self.exchange_rate_worker.isRunning():
                reply = message_box.question(
                    cast("QWidget", self),
                    "Update in Progress",
                    "Exchange rate update is already running. Do you want to stop it and start a new check?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.exchange_rate_worker.stop()
                    self.exchange_rate_worker.wait()
                else:
                    return

            # Create and configure check progress dialog
            self.check_progress_dialog = QMessageBox(cast("QWidget", self))
            self.check_progress_dialog.setWindowTitle("Checking Exchange Rates")
            check_mode = "from first transaction" if check_from_first_transaction else "from last exchange rate"
            self.check_progress_dialog.setText(
                f"Checking exchange rates {check_mode}...\nThis may take a few moments for large date ranges."
            )
            self.check_progress_dialog.setStandardButtons(QMessageBox.StandardButton.Cancel)
            self.check_progress_dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)

            # Connect cancel button for checker
            def cancel_check() -> None:
                if hasattr(self, "exchange_rate_checker"):
                    self.exchange_rate_checker.stop()
                self.check_progress_dialog.close()

            self.check_progress_dialog.buttonClicked.connect(cancel_check)
            self.check_progress_dialog.show()

            # Create and start checker thread
            db_filename = _require_db_filename_for_worker(self.db_manager)
            self.exchange_rate_checker = ExchangeRateCheckerWorker(
                db_filename, check_from_first_transaction=check_from_first_transaction
            )

            # Connect checker signals
            self.exchange_rate_checker.progress_updated.connect(self._on_check_progress_updated)
            self.exchange_rate_checker.check_completed.connect(self._on_check_completed)
            self.exchange_rate_checker.check_failed.connect(self._on_check_failed)

            # Start the checker
            self.exchange_rate_checker.start()

        except Exception as e:
            if hasattr(self, "check_progress_dialog"):
                self.check_progress_dialog.close()
            message_box.critical(cast("QWidget", self), "Check Error", f"Failed to start exchange rate check: {e}")
            print(f"❌ Exchange rate check error: {e}")

    def _auto_update_exchange_rates_on_startup(self) -> None:
        """Automatically update exchange rates on startup in the background.

        Strategy:

        - First check if all currencies have today's rates.
        - If yes: skip update.
        - If no: proceed with normal update strategy.
        - Progress is shown in the status bar without blocking the main window.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            self.statusBar().showMessage("Exchange rate check failed: database is not initialized", 10000)
            return

        try:
            self.statusBar().showMessage("Checking exchange rates...")

            # First check if we need to update exchange rates at all
            if not self.db_manager.should_update_exchange_rates():
                print("✅ [Startup] Exchange rates are up to date. Skipping update.")
                self.statusBar().showMessage("Exchange rates are up to date", 5000)
                return

            # Check if exchange rates data exists
            has_exchange_rates = self.db_manager.has_exchange_rates_data()

            if has_exchange_rates:
                # Exchange rates exist - check from last exchange rate date
                check_from_first_transaction = False
                strategy_text = "from last exchange rate date"
                print("🔄 [Startup] Starting exchange rate update from last exchange rate date...")
            else:
                # No exchange rates - check from first transaction date
                check_from_first_transaction = True
                strategy_text = "from first transaction date"
                print("🔄 [Startup] No exchange rates found. Starting update from first transaction date...")

                # Additional check: ensure transactions exist
                earliest_transaction = self.db_manager.get_earliest_transaction_date()
                if not earliest_transaction:
                    print("ℹ️ [Startup] No transactions found. Skipping exchange rate update.")  # noqa: RUF001
                    self.statusBar().showMessage("No transactions found. Exchange rate update skipped", 5000)
                    return

            self.statusBar().showMessage(f"Checking exchange rates {strategy_text}...")

            # Create and start checker thread
            db_filename = _require_db_filename_for_worker(self.db_manager)
            self.startup_exchange_rate_checker = ExchangeRateCheckerWorker(
                db_filename, check_from_first_transaction=check_from_first_transaction
            )

            # Connect signals
            self.startup_exchange_rate_checker.progress_updated.connect(self._on_startup_check_progress_updated)
            self.startup_exchange_rate_checker.check_completed.connect(self._on_startup_check_completed)
            self.startup_exchange_rate_checker.check_failed.connect(self._on_startup_check_failed)

            # Start the checker
            self.startup_exchange_rate_checker.start()

        except Exception as e:
            print(f"❌ Startup exchange rate check error: {e}")
            self.statusBar().showMessage(f"Exchange rate check failed: {e}", 10000)

    def _create_exchange_rate_chart(self, currency_id: int, date_from: str, date_to: str) -> None:
        """Create and display exchange rate chart.

        Args:

        - `currency_id` (`int`): ID of the currency.
        - `date_from` (`str`): Start date in yyyy-MM-dd format.
        - `date_to` (`str`): End date in yyyy-MM-dd format.

        """
        if not self._validate_database_connection():
            return

        # Additional safety check: ensure no previous chart is being deleted
        if hasattr(self, "_current_exchange_rate_canvas") and self._current_exchange_rate_canvas is not None:
            try:
                if (
                    hasattr(self._current_exchange_rate_canvas, "_deleting")
                    and self._current_exchange_rate_canvas._deleting  # noqa: SLF001
                ):
                    # Wait a bit for cleanup to complete
                    QTimer.singleShot(100, lambda: self._create_exchange_rate_chart(currency_id, date_from, date_to))
                    return
            except Exception as e:
                print(f"Error while checking for previous chart deletion: {e}")

        try:
            # Get currency info
            currency_info = self.db_manager.get_currency_by_id(currency_id)
            if not currency_info:
                self._show_no_data_label(self.verticalLayout_exchange_rates_content, "Currency not found")
                return

            currency_code, currency_name, _currency_symbol = currency_info

            # Get exchange rates data
            rates_data = self._get_exchange_rates_data(currency_id, date_from, date_to)

            if not rates_data:
                self._show_no_data_label(
                    self.verticalLayout_exchange_rates_content, "No exchange rate data found for the selected period"
                )
                return

            # Clear existing chart
            self._clear_layout(self.verticalLayout_exchange_rates_content)

            # Create matplotlib figure with proper cleanup
            fig = Figure(figsize=(12, 6), dpi=100)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            # Store references to prevent premature deletion
            self._current_exchange_rate_fig = fig
            self._current_exchange_rate_canvas = canvas

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
            date_objects = [datetime.fromisoformat(date) for date in dates]
            # Convert to numeric values for matplotlib type checking
            date_numeric = [date2num(dt) for dt in date_objects]

            # Plot the data
            ax.plot(date_numeric, transformed_rates, color="#2E86AB", linewidth=1)

            # Highlight min and max points
            if len(transformed_rates) > 1:
                min_rate = min(transformed_rates)
                max_rate = max(transformed_rates)
                min_index = transformed_rates.index(min_rate)
                max_index = transformed_rates.index(max_rate)

                # Plot min point in red
                ax.scatter(date_numeric[min_index], min_rate, color="red", s=5, zorder=5, marker="o")

                # Plot max point in green
                ax.scatter(date_numeric[max_index], max_rate, color="green", s=5, zorder=5, marker="o")

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
                # Find min and max rates and their indices
                min_rate = min(transformed_rates)
                max_rate = max(transformed_rates)
                min_index = transformed_rates.index(min_rate)
                max_index = transformed_rates.index(max_rate)

                # Label first and last points
                first_date = dates[0]
                ax.annotate(
                    f"{transformed_rates[0]:.6f} ({first_date})",
                    xy=(date_numeric[0], transformed_rates[0]),
                    xytext=(10, 10),
                    textcoords="offset points",
                    bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.9},
                    fontsize=10,
                )

                dates[-1]
                ax.annotate(
                    f"{transformed_rates[-1]:.6f}",
                    xy=(date_numeric[-1], transformed_rates[-1]),
                    xytext=(10, 10),
                    textcoords="offset points",
                    bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.9},
                    fontsize=10,
                )

                # Label minimum rate point
                if min_index != 0 and min_index != len(transformed_rates) - 1:  # Don't duplicate first/last labels
                    min_date = dates[min_index]
                    ax.annotate(
                        f"MIN: {min_rate:.6f} ({min_date})",
                        xy=(date_numeric[min_index], min_rate),
                        xytext=(10, -20),
                        textcoords="offset points",
                        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.9},
                        fontsize=10,
                        color="red",
                    )

                # Label maximum rate point
                if max_index != 0 and max_index != len(transformed_rates) - 1:  # Don't duplicate first/last labels
                    max_date = dates[max_index]
                    ax.annotate(
                        f"MAX: {max_rate:.6f} ({max_date})",
                        xy=(date_numeric[max_index], max_rate),
                        xytext=(10, 20),
                        textcoords="offset points",
                        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.9},
                        fontsize=10,
                        color="green",
                    )

            # Add the canvas to the layout
            fig.tight_layout()
            self.verticalLayout_exchange_rates_content.addWidget(canvas)
            canvas.draw()

            # Mark as initialized
            self._exchange_rates_initialized = True

        except Exception as e:
            print(f"Error creating exchange rate chart: {e}")
            self._show_no_data_label(self.verticalLayout_exchange_rates_content, f"Error creating chart: {e}")

    def _fetch_exchange_rates_rows(self, limit: int | None, offset: int) -> list[list[Any]]:
        """Fetch exchange rate rows with optional filters and pagination."""
        if self.db_manager is None:
            return []

        if self._exchange_rates_filter_params is not None:
            return self.db_manager.get_filtered_exchange_rates(
                **self._exchange_rates_filter_params,
                limit=limit,
                offset=offset,
            )
        return self.db_manager.get_all_exchange_rates(limit=limit, offset=offset)

    def _get_exchange_rates_data(self, currency_id: int, date_from: str, date_to: str) -> list[tuple[str, float]]:
        """Get exchange rates data for the specified currency and date range.

        Args:

        - `currency_id` (`int`): ID of the currency.
        - `date_from` (`str`): Start date in yyyy-MM-dd format.
        - `date_to` (`str`): End date in yyyy-MM-dd format.

        Returns:

        - `list[tuple[str, float]]`: List of tuples (date, rate) sorted by date.

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
                rows = self.db_manager.rows_from_query(query_obj)
                query_obj.clear()
                return [(row[0], float(row[1])) for row in rows if row[1] is not None]
        except Exception as e:
            print(f"Error getting exchange rates data: {e}")
        return []

    def _load_exchange_rates_page(self, *, reset: bool = True) -> None:
        """Load the first page of exchange rates (with optional active filters)."""
        if self.db_manager is None:
            return

        if reset:
            self._reset_exchange_rates_pagination_state()

        limit: int = self.count_exchange_rates_to_show
        rows: list[list[Any]] = self._fetch_exchange_rates_rows(limit, 0)
        transformed_data: list[list] = self._transform_exchange_rates_data(rows)

        self.models["exchange_rates"] = self._create_colored_table_model(
            transformed_data, self.table_config["exchange_rates"][2]
        )
        self._set_table_model_and_stretch_columns(self.tableView_exchange_rates, self.models["exchange_rates"])
        self._setup_exchange_rates_table_delegates()

        self._exchange_rates_pagination.record_first_page(len(rows), limit)

    def _load_more_exchange_rates(self) -> None:
        """Append the next page of exchange rates when scrolling to the bottom."""
        if self.db_manager is None or self.models["exchange_rates"] is None:
            return

        def append_rows(rows: list[list[Any]]) -> None:
            transformed_data: list[list] = self._transform_exchange_rates_data(rows)
            proxy = cast("QSortFilterProxyModel", self.models["exchange_rates"])
            source_model = cast("QStandardItemModel", proxy.sourceModel())
            self._append_colored_rows_to_model(source_model, transformed_data)

        self._exchange_rates_pagination.load_more(
            load_more_count=self.exchange_rates_load_more_count,
            fetch_rows=self._fetch_exchange_rates_rows,
            append_rows=append_rows,
        )

    def _mark_exchange_rates_changed(self) -> None:
        """Mark exchange rates as changed to trigger updates."""
        if hasattr(self, "exchange_rates_loaded"):
            self.exchange_rates_loaded = False

    def _on_exchange_rates_scroll(self, value: int) -> None:
        """Trigger loading more exchange rates when scrolled near the bottom."""
        scrollbar = self.tableView_exchange_rates.verticalScrollBar()
        on_scroll_load_more(value, scrollbar.maximum(), self._load_more_exchange_rates)

    def _reset_exchange_rates_pagination_state(self) -> None:
        """Reset pagination counters for exchange rates table."""
        self._exchange_rates_pagination.reset()

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
            end_date = QDate.currentDate()
            self.dateEdit_exchange_rates_to.setDate(end_date)

            # Set filter date edits to match the main date edits
            self.dateEdit_filter_exchange_rates_from.setDate(start_date)
            self.dateEdit_filter_exchange_rates_to.setDate(end_date)

        except Exception as e:
            print(f"Error setting exchange rates date range: {e}")

    def _setup_exchange_rates_controls(self) -> None:
        """Set up exchange rates chart controls with initial values."""
        if not self._validate_database_connection():
            return

        try:
            # Block signals temporarily to prevent chart drawing during setup
            self.dateEdit_exchange_rates_from.blockSignals(True)  # noqa: FBT003
            self.dateEdit_exchange_rates_to.blockSignals(True)  # noqa: FBT003
            self.comboBox_exchange_rates_currency.blockSignals(True)  # noqa: FBT003

            # Fill currency combo box
            currencies = self.db_manager.get_all_currencies()
            self.comboBox_exchange_rates_currency.clear()

            # Add currencies with format: "RUB - Russian Ruble" (excluding USD)
            for currency in currencies:
                currency_id, code, name, _ = currency
                # Skip USD currency
                if code.upper() == "USD":
                    continue
                display_text = f"{code} - {name}"
                self.comboBox_exchange_rates_currency.addItem(display_text, currency_id)

            # Set default currency (ID = 1)
            default_index = self.comboBox_exchange_rates_currency.findData(1)
            if default_index >= 0:
                self.comboBox_exchange_rates_currency.setCurrentIndex(default_index)

            # Fill filter currency combo box with the same data
            self.comboBox_exchange_rates_filter_currency.clear()
            self.comboBox_exchange_rates_filter_currency.addItem("")  # All currencies option
            for currency in currencies:
                currency_id, code, name, _symbol = currency
                # Skip USD currency
                if code.upper() == "USD":
                    continue
                display_text = f"{code} - {name}"
                self.comboBox_exchange_rates_filter_currency.addItem(display_text, currency_id)

            # Fill exchange item update currency combo box with the same data
            self.comboBox_exchange_item_update.clear()
            for currency in currencies:
                currency_id, code, name, _symbol = currency
                # Skip USD currency
                if code.upper() == "USD":
                    continue
                display_text = f"{code} - {name}"
                self.comboBox_exchange_item_update.addItem(display_text, currency_id)

            # Set default currency for exchange item update (ID = 1)
            default_index = self.comboBox_exchange_item_update.findData(1)
            if default_index >= 0:
                self.comboBox_exchange_item_update.setCurrentIndex(default_index)

            # Set initial date range
            self._set_exchange_rates_date_range()

            # Unblock signals
            self.dateEdit_exchange_rates_from.blockSignals(False)  # noqa: FBT003
            self.dateEdit_exchange_rates_to.blockSignals(False)  # noqa: FBT003
            self.comboBox_exchange_rates_currency.blockSignals(False)  # noqa: FBT003

            # Mark as initialized
            self._exchange_rates_initialized = True

        except Exception as e:
            print(f"Error setting up exchange rates controls: {e}")

    def _setup_exchange_rates_table_delegates(self) -> None:
        """Set up item delegates for the exchange rates table."""
        self.rate_delegate = AmountDelegate(self.tableView_exchange_rates, self.db_manager)
        self.tableView_exchange_rates.setItemDelegateForColumn(2, self.rate_delegate)
        self.tableView_exchange_rates.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def _start_exchange_rate_update(self, currencies_to_process: list) -> None:
        """Start the exchange rate update process after check is complete.

        Args:

        - `currencies_to_process` (`list`): List of currencies to process.

        """
        try:
            # Create and configure update progress dialog
            self.progress_dialog = QMessageBox(cast("QWidget", self))
            self.progress_dialog.setWindowTitle("Updating Exchange Rates")
            self.progress_dialog.setText(
                f"Starting exchange rate update for {len(currencies_to_process)} currencies from yfinance..."
            )
            self.progress_dialog.setStandardButtons(QMessageBox.StandardButton.Cancel)
            self.progress_dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)

            # Connect cancel button for updater
            def cancel_update() -> None:
                if hasattr(self, "exchange_rate_worker"):
                    self.exchange_rate_worker.stop()
                self.progress_dialog.close()

            self.progress_dialog.buttonClicked.connect(cancel_update)
            self.progress_dialog.show()

            # Create and start worker thread
            db_filename = _require_db_filename_for_worker(self.db_manager)
            self.exchange_rate_worker = ExchangeRateUpdateWorker(db_filename, currencies_to_process)

            # Connect signals
            self.exchange_rate_worker.progress_updated.connect(self._on_progress_updated)
            self.exchange_rate_worker.currency_started.connect(self._on_currency_started)
            self.exchange_rate_worker.rates_added.connect(self._on_rate_added)
            self.exchange_rate_worker.finished_success.connect(self._on_update_finished_success)
            self.exchange_rate_worker.finished_error.connect(self._on_update_finished_error)

            # Start the worker
            self.exchange_rate_worker.start()

        except Exception as e:
            if hasattr(self, "progress_dialog"):
                self.progress_dialog.close()
            message_box.critical(cast("QWidget", self), "Update Error", f"Failed to start exchange rate update: {e}")
            print(f"❌ Exchange rate update error: {e}")

    def _start_startup_exchange_rate_update(self, currencies_to_process: list) -> None:
        """Start the exchange rate update process for startup.

        Args:

        - `currencies_to_process` (`list`): List of currencies to process.

        """
        try:
            # Determine the strategy for logging
            has_exchange_rates = self.db_manager.has_exchange_rates_data() if self.db_manager else False
            strategy = "from last exchange rate date" if has_exchange_rates else "from first transaction date"

            print(
                f"🔄 [Startup] Starting exchange rate update for "
                f"{len(currencies_to_process)} currencies ({strategy})..."
            )

            currencies_text = ", ".join(currency_code for _, currency_code, _ in currencies_to_process)
            self.statusBar().showMessage(f"Downloading exchange rates {strategy} ({currencies_text})...")

            # Create and start worker thread
            db_filename = _require_db_filename_for_worker(self.db_manager)
            self.startup_exchange_rate_worker = ExchangeRateUpdateWorker(db_filename, currencies_to_process)

            # Connect signals
            self.startup_exchange_rate_worker.progress_updated.connect(self._on_startup_progress_updated)
            self.startup_exchange_rate_worker.currency_started.connect(self._on_startup_currency_started)
            self.startup_exchange_rate_worker.rates_added.connect(self._on_startup_rate_added)
            self.startup_exchange_rate_worker.finished_success.connect(self._on_startup_update_finished_success)
            self.startup_exchange_rate_worker.finished_error.connect(self._on_startup_update_finished_error)

            # Start the worker
            self.startup_exchange_rate_worker.start()

        except Exception as e:
            print(f"❌ [Startup] Exchange rate update error: {e}")
            self.statusBar().showMessage(f"Exchange rate update failed: {e}", 10000)

    def _transform_exchange_rates_data(self, rows: list[list[Any]]) -> list[list]:
        """Transform raw exchange rate rows for table display."""
        rates_transformed_data: list[list] = []
        color = QColor(240, 255, 255)
        for row in rows:
            usd_to_currency_rate = float(row[3]) if row[3] else 0.0
            currency_to_usd_rate = 1.0 / usd_to_currency_rate if usd_to_currency_rate != 0 else 0.0
            transformed_row = [row[2], row[1], f"{currency_to_usd_rate:.6f}", row[4], row[0], color]
            rates_transformed_data.append(transformed_row)
        return rates_transformed_data
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
            self._exchange_rates_filter_params = None
            self._load_exchange_rates_page(reset=True)
            self.exchange_rates_loaded = True
            QTimer.singleShot(50, self.on_exchange_rates_update)
        except Exception as e:
            print(f"❌ Error loading exchange rates table: {e}")
```

</details>

### ⚙️ Method `on_delete_exchange_rates_by_days`

```python
def on_delete_exchange_rates_by_days(self) -> None
```

Delete exchange rates for the last N days based on spinBox_exchange_rate_count_days value.

<details>
<summary>Code:</summary>

```python
def on_delete_exchange_rates_by_days(self) -> None:
        if not self._validate_database_connection():
            return

        try:
            # Get the number of days from the spin box
            days = self.spinBox_exchange_rate_count_days.value()

            if days <= 0:
                message_box.warning(cast("QWidget", self), "Invalid Input", "Number of days must be greater than 0.")
                return

            # Show confirmation dialog
            reply = message_box.question(
                cast("QWidget", self),
                "Confirm Deletion",
                f"Are you sure you want to delete exchange rates for the last {days} days?\n\n"
                "This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Delete exchange rates
            success, deleted_count = self.db_manager.delete_exchange_rates_by_days(days)

            if success:
                if deleted_count > 0:
                    message_box.information(
                        cast("QWidget", self),
                        "Deletion Successful",
                        f"Successfully deleted {deleted_count} exchange rate records for the last {days} days.",
                    )
                else:
                    message_box.information(
                        cast("QWidget", self),
                        "No Records Found",
                        (f"No exchange rate records were found for the last {days} days."),
                    )

                # Mark exchange rates as changed and update the view
                self._mark_exchange_rates_changed()
                self.update_all()
                self.update_summary_labels()
            else:
                message_box.warning(
                    cast("QWidget", self),
                    "Deletion Failed",
                    "Failed to delete exchange rate records. Please check the database connection.",
                )

        except Exception as e:
            message_box.critical(
                cast("QWidget", self), "Error", f"An error occurred while deleting exchange rates: {e}"
            )
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
        # Automatically update the chart with a small delay to ensure dates are properly set
        QTimer.singleShot(50, self.on_exchange_rates_update)
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
        # Automatically update the chart with a small delay to ensure dates are properly set
        QTimer.singleShot(50, self.on_exchange_rates_update)
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
        # Automatically update the chart with a small delay to ensure dates are properly set
        QTimer.singleShot(50, self.on_exchange_rates_update)
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

        # Prevent multiple simultaneous updates
        if hasattr(self, "_exchange_rates_updating") and self._exchange_rates_updating:
            return

        # Check if previous chart is still being created or if we need to wait for cleanup
        if hasattr(self, "_current_exchange_rate_canvas") and self._current_exchange_rate_canvas is not None:
            try:
                # Test if canvas is still valid
                if not self._current_exchange_rate_canvas.figure:
                    return
                # Additional check: if canvas is being deleted, wait a bit
                if (
                    hasattr(self._current_exchange_rate_canvas, "deleting")
                    and self._current_exchange_rate_canvas.deleting
                ):
                    return
            except Exception:
                return

        try:
            self._exchange_rates_updating = True

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
                message_box.warning(cast("QWidget", self), "Invalid Date Range", "Start date cannot be after end date.")
                return

            # Create chart
            self._create_exchange_rate_chart(currency_id, date_from, date_to)

        finally:
            self._exchange_rates_updating = False
```

</details>

### ⚙️ Method `on_filter_exchange_rates_apply`

```python
def on_filter_exchange_rates_apply(self) -> None
```

Apply filter to exchange rates based on selected criteria.

<details>
<summary>Code:</summary>

```python
def on_filter_exchange_rates_apply(self) -> None:
        if not self._validate_database_connection():
            return

        try:
            # Get filter criteria
            currency_id = None
            currency_index = self.comboBox_exchange_rates_filter_currency.currentIndex()

            # Check if "All currencies" is selected (index 0)
            if currency_index > 0:
                currency_id = self.comboBox_exchange_rates_filter_currency.itemData(currency_index)

            # Get date range
            date_from = self.dateEdit_filter_exchange_rates_from.date().toString("yyyy-MM-dd")
            date_to = self.dateEdit_filter_exchange_rates_to.date().toString("yyyy-MM-dd")

            # Validate date range
            if self.dateEdit_filter_exchange_rates_from.date() > self.dateEdit_filter_exchange_rates_to.date():
                message_box.warning(cast("QWidget", self), "Invalid Date Range", "Start date cannot be after end date.")
                return

            self._exchange_rates_filter_params = {
                "currency_id": currency_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            self._load_exchange_rates_page(reset=True)

            # Show information about filter results
            filter_info = []
            if currency_id is not None:
                currency_text = self.comboBox_exchange_rates_filter_currency.currentText()
                filter_info.append(f"Currency: {currency_text}")
            else:
                filter_info.append("Currency: All currencies")

            filter_info.append(f"Date range: {date_from} to {date_to}")
            filter_info.append(f"Records loaded: {self._exchange_rates_pagination.loaded_count}")
            if self._exchange_rates_pagination.has_more:
                filter_info.append("Scroll down to load more records")

            message_box.information(
                cast("QWidget", self),
                "Filter Applied",
                "Exchange rates filter has been applied.\n\n" + "\n".join(filter_info),
            )

        except Exception as e:
            message_box.critical(cast("QWidget", self), "Filter Error", f"An error occurred while applying filter: {e}")
```

</details>

### ⚙️ Method `on_filter_exchange_rates_clear`

```python
def on_filter_exchange_rates_clear(self) -> None
```

Clear exchange rates filter and show default number of records.

<details>
<summary>Code:</summary>

```python
def on_filter_exchange_rates_clear(self) -> None:
        if not self._validate_database_connection():
            return

        try:
            # Reset filter controls to default values
            self.comboBox_exchange_rates_filter_currency.setCurrentIndex(0)  # "All currencies"

            # Reset date range to match main date controls
            self.dateEdit_filter_exchange_rates_from.setDate(self.dateEdit_exchange_rates_from.date())
            self.dateEdit_filter_exchange_rates_to.setDate(self.dateEdit_exchange_rates_to.date())

            self._exchange_rates_filter_params = None
            self._load_exchange_rates_page(reset=True)

            message_box.information(
                cast("QWidget", self),
                "Filter Cleared",
                (
                    "Exchange rates filter has been cleared.\n"
                    f"Showing {self._exchange_rates_pagination.loaded_count} most recent records."
                ),
            )

        except Exception as e:
            message_box.critical(
                cast("QWidget", self), "Clear Filter Error", f"An error occurred while clearing filter: {e}"
            )
```

</details>

### ⚙️ Method `on_update_exchange_rates`

```python
def on_update_exchange_rates(self) -> None
```

Update and fill missing exchange rate records for each currency from yfinance.

<details>
<summary>Code:</summary>

```python
def on_update_exchange_rates(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Configuration option: check from first transaction or from last exchange rate
            check_from_first_transaction = True  # Set to False to check only from last exchange rate

            # Check if checker is already running
            if hasattr(self, "exchange_rate_checker") and self.exchange_rate_checker.isRunning():
                message_box.warning(
                    cast("QWidget", self),
                    "Check in Progress",
                    "Exchange rate check is already running. Please wait for it to complete.",
                )
                return

            # Check if updater is already running
            if hasattr(self, "exchange_rate_worker") and self.exchange_rate_worker.isRunning():
                reply = message_box.question(
                    cast("QWidget", self),
                    "Update in Progress",
                    "Exchange rate update is already running. Do you want to stop it and start a new check?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.exchange_rate_worker.stop()
                    self.exchange_rate_worker.wait()
                else:
                    return

            # Create and configure check progress dialog
            self.check_progress_dialog = QMessageBox(cast("QWidget", self))
            self.check_progress_dialog.setWindowTitle("Checking Exchange Rates")
            check_mode = "from first transaction" if check_from_first_transaction else "from last exchange rate"
            self.check_progress_dialog.setText(
                f"Checking exchange rates {check_mode}...\nThis may take a few moments for large date ranges."
            )
            self.check_progress_dialog.setStandardButtons(QMessageBox.StandardButton.Cancel)
            self.check_progress_dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)

            # Connect cancel button for checker
            def cancel_check() -> None:
                if hasattr(self, "exchange_rate_checker"):
                    self.exchange_rate_checker.stop()
                self.check_progress_dialog.close()

            self.check_progress_dialog.buttonClicked.connect(cancel_check)
            self.check_progress_dialog.show()

            # Create and start checker thread
            db_filename = _require_db_filename_for_worker(self.db_manager)
            self.exchange_rate_checker = ExchangeRateCheckerWorker(
                db_filename, check_from_first_transaction=check_from_first_transaction
            )

            # Connect checker signals
            self.exchange_rate_checker.progress_updated.connect(self._on_check_progress_updated)
            self.exchange_rate_checker.check_completed.connect(self._on_check_completed)
            self.exchange_rate_checker.check_failed.connect(self._on_check_failed)

            # Start the checker
            self.exchange_rate_checker.start()

        except Exception as e:
            if hasattr(self, "check_progress_dialog"):
                self.check_progress_dialog.close()
            message_box.critical(cast("QWidget", self), "Check Error", f"Failed to start exchange rate check: {e}")
            print(f"❌ Exchange rate check error: {e}")
```

</details>
