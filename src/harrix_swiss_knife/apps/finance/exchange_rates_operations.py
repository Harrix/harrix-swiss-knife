"""Exchange rates operations for finance tracker.

This module contains methods for handling exchange rates operations,
including loading, updating, filtering, and chart creation.
"""

from __future__ import annotations

from datetime import datetime
from typing import cast

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import QDate, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QMessageBox, QWidget

from harrix_swiss_knife.apps.finance.delegates import AmountDelegate
from harrix_swiss_knife.apps.finance.exchange_rate_checker_worker import ExchangeRateCheckerWorker
from harrix_swiss_knife.apps.finance.exchange_rate_worker import ExchangeRateUpdateWorker


class ExchangeRatesOperations:
    """Mixin class for exchange rates operations."""

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

            # Set up amount delegate for the Rate column (index 2)
            self.rate_delegate = AmountDelegate(self.tableView_exchange_rates, self.db_manager)
            self.tableView_exchange_rates.setItemDelegateForColumn(2, self.rate_delegate)

            # Disable editing for the Rate column
            self.tableView_exchange_rates.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

            # Configure column stretching for exchange rates table
            rates_header = self.tableView_exchange_rates.horizontalHeader()
            if rates_header.count() > 0:
                for i in range(rates_header.count()):
                    rates_header.setSectionResizeMode(i, rates_header.ResizeMode.Stretch)

            # Mark as loaded
            self.exchange_rates_loaded = True

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
                QMessageBox.warning(cast("QWidget", self), "Invalid Input", "Number of days must be greater than 0.")
                return

            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
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
                    QMessageBox.information(
                        self,
                        "Deletion Successful",
                        f"Successfully deleted {deleted_count} exchange rate records for the last {days} days.",
                    )
                else:
                    QMessageBox.information(
                        self, "No Records Found", f"No exchange rate records were found for the last {days} days."
                    )

                # Mark exchange rates as changed and update the view
                self._mark_exchange_rates_changed()
                self.update_all()
                self.update_summary_labels()
            else:
                QMessageBox.warning(
                    self,
                    "Deletion Failed",
                    "Failed to delete exchange rate records. Please check the database connection.",
                )

        except Exception as e:
            QMessageBox.critical(
                cast("QWidget", self),
                "Error",
                f"An error occurred while deleting exchange rates: {e}"
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
                QMessageBox.warning(cast("QWidget", self), "Invalid Date Range", "Start date cannot be after end date.")
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
                QMessageBox.warning(cast("QWidget", self), "Invalid Date Range", "Start date cannot be after end date.")
                return

            # Get filtered data
            filtered_data = self.db_manager.get_filtered_exchange_rates(
                currency_id=currency_id, date_from=date_from, date_to=date_to, limit=self.count_exchange_rates_to_show
            )

            # Update table
            self._update_exchange_rates_table(filtered_data)

            # Show information about filter results
            filter_info = []
            if currency_id is not None:
                currency_text = self.comboBox_exchange_rates_filter_currency.currentText()
                filter_info.append(f"Currency: {currency_text}")
            else:
                filter_info.append("Currency: All currencies")

            filter_info.append(f"Date range: {date_from} to {date_to}")
            filter_info.append(f"Records found: {len(filtered_data)}")

            QMessageBox.information(
                self, "Filter Applied", "Exchange rates filter has been applied.\n\n" + "\n".join(filter_info)
            )

        except Exception as e:
            QMessageBox.critical(cast("QWidget", self), "Filter Error", f"An error occurred while applying filter: {e}")

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

            # Get unfiltered data with default limit
            unfiltered_data = self.db_manager.get_all_exchange_rates(limit=self.count_exchange_rates_to_show)

            # Update table
            self._update_exchange_rates_table(unfiltered_data)

            QMessageBox.information(
                self,
                "Filter Cleared",
                f"Exchange rates filter has been cleared.\nShowing {len(unfiltered_data)} most recent records.",
            )

        except Exception as e:
            QMessageBox.critical(
                cast("QWidget", self),
                "Clear Filter Error",
                f"An error occurred while clearing filter: {e}"
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
                QMessageBox.warning(
                    self, "Check in Progress", "Exchange rate check is already running. Please wait for it to complete."
                )
                return

            # Check if updater is already running
            if hasattr(self, "exchange_rate_worker") and self.exchange_rate_worker.isRunning():
                reply = QMessageBox.question(
                    cast("QWidget", self),
                    "Update in Progress",
                    "Exchange rate update is already running. Do you want to stop it and start a new check?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
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

            self.check_progress_dialog.buttonClicked.connect(lambda: cancel_check())
            self.check_progress_dialog.show()

            # Create and start checker thread
            self.exchange_rate_checker = ExchangeRateCheckerWorker(
                self.db_manager, check_from_first_transaction=check_from_first_transaction
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
            QMessageBox.critical(cast("QWidget", self), "Check Error", f"Failed to start exchange rate check: {e}")
            print(f"❌ Exchange rate check error: {e}")

    def _auto_update_exchange_rates_on_startup(self) -> None:
        """Automatically update exchange rates on startup with modal dialog.

        Strategy:

        - First check if all currencies have today's rates.
        - If yes: skip update.
        - If no: proceed with normal update strategy.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # First check if we need to update exchange rates at all
            if not self.db_manager.should_update_exchange_rates():
                print("✅ [Startup] Exchange rates are up to date. Skipping update.")
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
                    return

            # Create modal progress dialog
            self.startup_progress_dialog = QMessageBox(cast("QWidget", self))
            self.startup_progress_dialog.setWindowTitle("Loading Exchange Rates")
            self.startup_progress_dialog.setText(f"Checking exchange rates {strategy_text}...\nPlease wait...")
            self.startup_progress_dialog.setStandardButtons(QMessageBox.StandardButton.Cancel)
            self.startup_progress_dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)

            # Make dialog modal to block main window
            self.startup_progress_dialog.setModal(True)

            # Connect cancel button
            self.startup_progress_dialog.buttonClicked.connect(self._on_startup_dialog_cancelled)

            # Show dialog (non-blocking)
            self.startup_progress_dialog.show()

            # Create and start checker thread
            self.startup_exchange_rate_checker = ExchangeRateCheckerWorker(
                self.db_manager, check_from_first_transaction=check_from_first_transaction
            )

            # Connect signals
            self.startup_exchange_rate_checker.progress_updated.connect(self._on_startup_check_progress_updated)
            self.startup_exchange_rate_checker.check_completed.connect(self._on_startup_check_completed)
            self.startup_exchange_rate_checker.check_failed.connect(self._on_startup_check_failed)

            # Start the checker
            self.startup_exchange_rate_checker.start()

        except Exception as e:
            print(f"❌ Startup exchange rate check error: {e}")
            self._cleanup_startup_dialog()

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

            # Plot the data
            ax.plot(date_objects, transformed_rates, color="#2E86AB", linewidth=1)

            # Highlight min and max points
            if len(transformed_rates) > 1:
                min_rate = min(transformed_rates)
                max_rate = max(transformed_rates)
                min_index = transformed_rates.index(min_rate)
                max_index = transformed_rates.index(max_rate)

                # Plot min point in red
                ax.scatter(date_objects[min_index], min_rate, color="red", s=5, zorder=5, marker="o")

                # Plot max point in green
                ax.scatter(date_objects[max_index], max_rate, color="green", s=5, zorder=5, marker="o")

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
                    xy=(date_objects[0], transformed_rates[0]),
                    xytext=(10, 10),
                    textcoords="offset points",
                    bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.9},
                    fontsize=10,
                )

                dates[-1]
                ax.annotate(
                    f"{transformed_rates[-1]:.6f}",
                    xy=(date_objects[-1], transformed_rates[-1]),
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
                        xy=(date_objects[min_index], min_rate),
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
                        xy=(date_objects[max_index], max_rate),
                        xytext=(10, 20),
                        textcoords="offset points",
                        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.9},
                        fontsize=10,
                        color="green",
                    )

            # Add the canvas to the layout
            self.verticalLayout_exchange_rates_content.addWidget(canvas)

            # Mark as initialized
            self._exchange_rates_initialized = True

        except Exception as e:
            print(f"Error creating exchange rate chart: {e}")
            self._show_no_data_label(self.verticalLayout_exchange_rates_content, f"Error creating chart: {e}")

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

    def _mark_exchange_rates_changed(self) -> None:
        """Mark exchange rates as changed to trigger updates."""
        if hasattr(self, "exchange_rates_loaded"):
            self.exchange_rates_loaded = False

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

            # Mark as initialized
            self._exchange_rates_initialized = True

        except Exception as e:
            print(f"Error setting up exchange rates controls: {e}")

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

            self.progress_dialog.buttonClicked.connect(lambda: cancel_update())
            self.progress_dialog.show()

            # Create and start worker thread
            self.exchange_rate_worker = ExchangeRateUpdateWorker(self.db_manager, currencies_to_process)

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
            QMessageBox.critical(cast("QWidget", self), "Update Error", f"Failed to start exchange rate update: {e}")
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

            # Create and start worker thread
            self.startup_exchange_rate_worker = ExchangeRateUpdateWorker(self.db_manager, currencies_to_process)

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
            if hasattr(self, "startup_progress_dialog"):
                self.startup_progress_dialog.setText(f"❌ Update error:\n{e}")
                # Auto-close after 3 seconds
                QTimer.singleShot(3000, self._cleanup_startup_dialog)
            else:
                self._cleanup_startup_dialog()

    def _update_exchange_rates_table(self, data: list[list]) -> None:
        """Update the exchange rates table with provided data.

        Args:

        - `data` (`list[list]`): List of exchange rate records to display.

        """
        try:
            # Transform the data to match the expected format for exchange rates table
            rates_transformed_data = []
            for row in data:
                # Input format: [id, from_code, to_code, rate, date]
                # Transform: Rate is stored as USD→currency, but display as currency→USD
                usd_to_currency_rate = float(row[3]) if row[3] else 0.0
                currency_to_usd_rate = 1.0 / usd_to_currency_rate if usd_to_currency_rate != 0 else 0.0
                color = QColor(240, 255, 255)
                # Show as currency → USD instead of USD → currency
                transformed_row = [row[2], row[1], f"{currency_to_usd_rate:.6f}", row[4], row[0], color]
                rates_transformed_data.append(transformed_row)

            # Create new model with the filtered data
            self.models["exchange_rates"] = self._create_colored_table_model(
                rates_transformed_data, self.table_config["exchange_rates"][2]
            )
            self.tableView_exchange_rates.setModel(self.models["exchange_rates"])

            # Set up amount delegate for the Rate column (index 2)
            self.rate_delegate = AmountDelegate(self.tableView_exchange_rates, self.db_manager)
            self.tableView_exchange_rates.setItemDelegateForColumn(2, self.rate_delegate)

            # Disable editing for the Rate column
            self.tableView_exchange_rates.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

            # Configure column stretching for exchange rates table
            rates_header = self.tableView_exchange_rates.horizontalHeader()
            if rates_header:
                rates_header.setStretchLastSection(True)

            print(f"✅ Updated exchange rates table with {len(data)} records")

        except Exception as e:
            print(f"❌ Error updating exchange rates table: {e}")
