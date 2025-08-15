"""Finance tracker GUI.

This module contains a single `MainWindow` class that provides a Qt-based GUI for a
SQLite database with transactions, categories, accounts, currencies and exchange rates.
"""

from __future__ import annotations

import colorsys
import sys
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Any

import harrix_pylib as h
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import QDate, QDateTime, QModelIndex, QSortFilterProxyModel, QStringListModel, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QBrush, QCloseEvent, QColor, QIcon, QKeyEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QCompleter, QDialog, QFileDialog, QMainWindow, QMessageBox, QTableView

from harrix_swiss_knife import resources_rc  # noqa: F401
from harrix_swiss_knife.finance import database_manager, window
from harrix_swiss_knife.finance.account_edit_dialog import AccountEditDialog
from harrix_swiss_knife.finance.mixins import (
    AutoSaveOperations,
    ChartOperations,
    DateOperations,
    TableOperations,
    ValidationOperations,
    requires_database,
)

config = h.dev.load_config("config/config.json")


class ExchangeRateUpdateWorker(QThread):
    """Worker thread for updating exchange rates."""

    # Signals
    progress_updated = Signal(str)  # Progress message
    currency_started = Signal(str)  # Currency being processed
    rates_added = Signal(str, float, str)  # currency_code, rate, date
    finished_success = Signal(int)  # Total updates count
    finished_error = Signal(str)  # Error message

    def __init__(self, db_manager, currencies, start_date, end_date):
        super().__init__()
        self.db_manager = db_manager
        self.currencies = currencies
        self.start_date = start_date
        self.end_date = end_date
        self.should_stop = False

    def stop(self):
        """Request worker to stop."""
        self.should_stop = True

    def run(self):
        """Main worker execution."""
        try:
            # Import required libraries
            import requests
            import yfinance as yf
            import pandas as pd

            total_updates = 0

            # Clean invalid exchange rates first
            self.progress_updated.emit("🧹 Cleaning invalid exchange rates...")
            cleaned_count = self.db_manager.clean_invalid_exchange_rates()

            # Methods for getting exchange rates from different sources
            def get_exchangerate_api_data(currency: str, start_date: str, end_date: str) -> dict:
                """Get historical exchange rates from ExchangeRate-API."""
                rates_data = {}
                try:
                    # ExchangeRate-API provides historical data
                    base_url = "https://api.exchangerate-api.com/v4/history"

                    # Get data for date range (API has limitations, so we'll get recent data)
                    current_date = datetime.now().date()
                    url = f"{base_url}/USD/{current_date.strftime('%Y-%m-%d')}"

                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if currency in data.get('rates', {}):
                            # For USD base, we get XXX/USD rate (how many XXX for 1 USD)
                            # We need USD/XXX rate (how many USD for 1 XXX)
                            usd_to_currency_rate = data['rates'][currency]
                            currency_to_usd_rate = 1.0 / usd_to_currency_rate if usd_to_currency_rate != 0 else 0

                            # For simplicity, use the same rate for all dates in range
                            current = datetime.strptime(start_date, '%Y-%m-%d').date()
                            end = datetime.strptime(end_date, '%Y-%m-%d').date()

                            while current <= end:
                                rates_data[current.strftime('%Y-%m-%d')] = currency_to_usd_rate
                                current += timedelta(days=1)

                            self.progress_updated.emit(f"📊 Got {currency}/USD rate from ExchangeRate-API: {currency_to_usd_rate:.6f}")
                        else:
                            self.progress_updated.emit(f"⚠️ Currency {currency} not found in ExchangeRate-API")
                    else:
                        self.progress_updated.emit(f"❌ ExchangeRate-API error: {response.status_code}")

                except Exception as e:
                    self.progress_updated.emit(f"❌ Error with ExchangeRate-API for {currency}: {e}")

                return rates_data

            def get_yfinance_data(currency_code: str, start_date, end_date, alternative_tickers: dict) -> dict:
                """Get exchange rate data from yfinance."""
                rates_data = {}
                ticker_symbol = f"{currency_code}USD=X"

                # Alternative ticker formats for problematic currencies
                alternative_tickers = {
                    'VND': ['USD/VND=X', 'USDVND=X'],  # Vietnamese Dong alternatives
                    'TRY': ['USD/TRY=X', 'USDTRY=X'],  # Turkish Lira alternatives
                    'RUB': ['USD/RUB=X', 'USDRUB=X']   # Russian Ruble alternatives
                }

                try:
                    # Download historical data
                    ticker = yf.Ticker(ticker_symbol)
                    hist = ticker.history(start=start_date, end=end_date + timedelta(days=1))

                    # If no data found, try alternative ticker formats
                    if hist.empty and currency_code in alternative_tickers:
                        self.progress_updated.emit(f"⚠️ No data found for {ticker_symbol}, trying alternatives...")

                        for alt_ticker in alternative_tickers[currency_code]:
                            if self.should_stop:
                                return {}
                            self.progress_updated.emit(f"🔄 Trying alternative ticker: {alt_ticker}")
                            ticker = yf.Ticker(alt_ticker)
                            hist = ticker.history(start=start_date, end=end_date + timedelta(days=1))

                            if not hist.empty:
                                self.progress_updated.emit(f"✅ Found data with alternative ticker: {alt_ticker}")
                                ticker_symbol = alt_ticker  # Update for logging

                                # For inverse rates (USD/XXX), we need to invert the values
                                if alt_ticker.startswith('USD/') or alt_ticker.startswith('USD'):
                                    self.progress_updated.emit(f"🔄 Inverting rates for {alt_ticker}")
                                    hist = hist.copy()
                                    for col in ['Open', 'High', 'Low', 'Close']:
                                        if col in hist.columns:
                                            hist[col] = 1.0 / hist[col]
                                break

                    if hist.empty:
                        self.progress_updated.emit(f"⚠️ No data found for {currency_code} with any yfinance ticker format")
                        return {}

                    self.progress_updated.emit(f"📊 Processing {len(hist)} days of yfinance data for {ticker_symbol}")

                    # Process each day
                    for date_idx, row in hist.iterrows():
                        if self.should_stop:
                            return {}
                        date_str = date_idx.strftime("%Y-%m-%d")
                        close_price = row["Close"]

                        if not pd.isna(close_price) and close_price > 0:
                            rates_data[date_str] = float(close_price)
                        else:
                            self.progress_updated.emit(f"⚠️ Invalid yfinance price for {currency_code} on {date_str}: {close_price}")

                except Exception as e:
                    self.progress_updated.emit(f"❌ Error with yfinance for {currency_code}: {e}")

                return rates_data

            # Process each currency
            for currency_id, currency_code, currency_name, currency_symbol in self.currencies:
                if self.should_stop:
                    break

                self.currency_started.emit(currency_code)

                success = False
                rates_data = {}

                # Try multiple data sources in order of preference
                data_sources = [
                    ("ExchangeRate-API", lambda: get_exchangerate_api_data(currency_code, self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d'))),
                    ("yfinance", lambda: get_yfinance_data(currency_code, self.start_date, self.end_date, {}))
                ]

                for source_name, get_data_func in data_sources:
                    if self.should_stop:
                        break
                    try:
                        self.progress_updated.emit(f"🔄 Trying {source_name} for {currency_code}...")
                        rates_data = get_data_func()

                        if rates_data:
                            self.progress_updated.emit(f"✅ Successfully got data from {source_name} for {currency_code}")
                            success = True
                            break
                        else:
                            self.progress_updated.emit(f"⚠️ No data from {source_name} for {currency_code}")

                    except Exception as e:
                        self.progress_updated.emit(f"❌ Error with {source_name} for {currency_code}: {e}")
                        continue

                if not success or not rates_data:
                    self.progress_updated.emit(f"❌ Failed to get exchange rate data for {currency_code} from any source")
                    continue

                # Save the rates to database
                self.progress_updated.emit(f"💾 Saving {len(rates_data)} exchange rates for {currency_code}")

                for date_str, rate in rates_data.items():
                    if self.should_stop:
                        break
                    try:
                        # Check if exchange rate already exists
                        if not self.db_manager.check_exchange_rate_exists(currency_id, date_str):
                            if rate is not None and rate > 0:
                                if self.db_manager.add_exchange_rate(currency_id, rate, date_str):
                                    total_updates += 1
                                    self.rates_added.emit(currency_code, rate, date_str)
                                else:
                                    self.progress_updated.emit(f"❌ Failed to add {currency_code}/USD rate for {date_str}")
                            else:
                                self.progress_updated.emit(f"⚠️ Skipping invalid rate for {currency_code} on {date_str}: {rate}")
                    except Exception as e:
                        self.progress_updated.emit(f"❌ Error saving rate for {currency_code} on {date_str}: {e}")
                        continue

            if not self.should_stop:
                self.finished_success.emit(total_updates)

        except Exception as e:
            self.finished_error.emit(f"Exchange rate update error: {e}")


class MainWindow(
    QMainWindow,
    window.Ui_MainWindow,
    TableOperations,
    ChartOperations,
    DateOperations,
    AutoSaveOperations,
    ValidationOperations,
):
    """Main application window for the finance tracking application.

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

    """

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
        self.count_transactions_to_show = 5000
        self.show_all_transactions = False

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
        self.update_all()

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

    def clear_filter(self) -> None:
        """Reset all transaction filters."""
        self.radioButton.setChecked(True)  # All
        self.comboBox_filter_category.setCurrentIndex(0)
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
        # Stop any running worker threads
        if hasattr(self, 'exchange_rate_worker') and self.exchange_rate_worker.isRunning():
            self.exchange_rate_worker.stop()
            self.exchange_rate_worker.wait(3000)  # Wait up to 3 seconds

        # Close progress dialog if open
        if hasattr(self, 'progress_dialog'):
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
    def on_add_rate(self) -> None:
        """Add a new exchange rate to USD using database manager."""
        from_currency = self.comboBox_rate_from.currentText()
        rate = self.doubleSpinBox_rate_value.value()
        date = self.dateEdit_rate.date().toString("yyyy-MM-dd")

        if not from_currency:
            QMessageBox.warning(self, "Error", "Select currency")
            return

        if from_currency == "USD":
            QMessageBox.warning(self, "Error", "Cannot add USD to USD exchange rate")
            return

        if rate <= 0:
            QMessageBox.warning(self, "Error", "Exchange rate must be positive")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get currency ID
        from_currency_info = self.db_manager.get_currency_by_code(from_currency)

        if not from_currency_info:
            QMessageBox.warning(self, "Error", "Currency not found")
            return

        from_currency_id = from_currency_info[0]

        try:
            if self.db_manager.add_exchange_rate(from_currency_id, rate, date):
                # Save current column widths before update
                column_widths = self._save_table_column_widths(self.tableView_exchange)

                self.update_all()

                # Restore column widths after update
                self._restore_table_column_widths(self.tableView_exchange, column_widths)

                self._clear_rate_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add exchange rate")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add exchange rate: {e}")

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
        self.show_tables()

    def on_tab_changed(self, index: int) -> None:
        """React to tab change.

        Args:

        - `index` (`int`): The index of the newly selected tab.

        """
        # Update relevant data when switching to different tabs
        if index == 6:  # Charts tab
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
            # Get the earliest date from transactions or currency_exchanges
            earliest_date = self.db_manager.get_earliest_financial_date()
            if not earliest_date:
                QMessageBox.warning(
                    self, "No Data", "No transactions or currency exchanges found. Please add some financial data first."
                )
                return

            # Get all currencies except USD (base currency)
            currencies = self.db_manager.get_currencies_except_usd()
            if not currencies:
                QMessageBox.warning(self, "No Currencies", "No currencies found except USD.")
                return

            # Calculate date range
            start_date = datetime.strptime(earliest_date, "%Y-%m-%d").date()
            end_date = datetime.now().date()

            # Check if worker is already running
            if hasattr(self, 'exchange_rate_worker') and self.exchange_rate_worker.isRunning():
                reply = QMessageBox.question(
                    self,
                    "Update in Progress",
                    "Exchange rate update is already running. Do you want to stop it and start a new one?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.exchange_rate_worker.stop()
                    self.exchange_rate_worker.wait()
                else:
                    return

            # Create and configure progress dialog
            self.progress_dialog = QMessageBox(self)
            self.progress_dialog.setWindowTitle("Updating Exchange Rates")
            self.progress_dialog.setText(f"Starting exchange rate update from {start_date} to {end_date}...")
            self.progress_dialog.setStandardButtons(QMessageBox.StandardButton.Cancel)
            self.progress_dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)

            # Connect cancel button
            def cancel_update():
                if hasattr(self, 'exchange_rate_worker'):
                    self.exchange_rate_worker.stop()
                self.progress_dialog.close()

            self.progress_dialog.buttonClicked.connect(lambda: cancel_update())
            self.progress_dialog.show()

            # Create and start worker thread
            self.exchange_rate_worker = ExchangeRateUpdateWorker(
                self.db_manager, currencies, start_date, end_date
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

    def _on_progress_updated(self, message: str):
        """Handle progress updates from worker."""
        print(message)
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setText(message)

    def _on_currency_started(self, currency_code: str):
        """Handle currency processing start."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setText(f"Processing {currency_code}...")

    def _on_rate_added(self, currency_code: str, rate: float, date_str: str):
        """Handle successful rate addition."""
        print(f"✅ Added {currency_code}/USD rate: {rate:.6f} for {date_str}")

    def _on_update_finished_success(self, total_updates: int):
        """Handle successful completion."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        if total_updates > 0:
            QMessageBox.information(
                self,
                "Update Complete",
                f"Successfully updated {total_updates} exchange rates.",
            )
            # Refresh the exchange rates table
            self.update_all()
        else:
            QMessageBox.information(
                self,
                "Update Complete",
                "No new exchange rates were added.",
            )

    def _on_update_finished_error(self, error_message: str):
        """Handle error completion."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        QMessageBox.critical(self, "Update Error", f"Failed to update exchange rates:\n{error_message}")
        print(f"❌ {error_message}")

    def _get_yfinance_data(self, currency_code: str, start_date, end_date, alternative_tickers: dict) -> dict:
        """Get exchange rate data from yfinance."""
        import yfinance as yf
        import pandas as pd

        rates_data = {}
        ticker_symbol = f"{currency_code}USD=X"

        try:
            # Download historical data
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(start=start_date, end=end_date + timedelta(days=1))

            # If no data found, try alternative ticker formats
            if hist.empty and currency_code in alternative_tickers:
                print(f"⚠️ No data found for {ticker_symbol}, trying alternatives...")

                for alt_ticker in alternative_tickers[currency_code]:
                    print(f"🔄 Trying alternative ticker: {alt_ticker}")
                    ticker = yf.Ticker(alt_ticker)
                    hist = ticker.history(start=start_date, end=end_date + timedelta(days=1))

                    if not hist.empty:
                        print(f"✅ Found data with alternative ticker: {alt_ticker}")
                        ticker_symbol = alt_ticker  # Update for logging

                        # For inverse rates (USD/XXX), we need to invert the values
                        if alt_ticker.startswith('USD/') or alt_ticker.startswith('USD'):
                            print(f"🔄 Inverting rates for {alt_ticker}")
                            hist = hist.copy()
                            for col in ['Open', 'High', 'Low', 'Close']:
                                if col in hist.columns:
                                    hist[col] = 1.0 / hist[col]
                        break

            if hist.empty:
                print(f"⚠️ No data found for {currency_code} with any yfinance ticker format")
                return {}

            print(f"📊 Processing {len(hist)} days of yfinance data for {ticker_symbol}")

            # Process each day
            for date_idx, row in hist.iterrows():
                date_str = date_idx.strftime("%Y-%m-%d")
                close_price = row["Close"]

                if not pd.isna(close_price) and close_price > 0:
                    rates_data[date_str] = float(close_price)
                else:
                    print(f"⚠️ Invalid yfinance price for {currency_code} on {date_str}: {close_price}")

        except Exception as e:
            print(f"❌ Error with yfinance for {currency_code}: {e}")

        return rates_data

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
        self.dateEdit_rate.setDate(today_qdate)

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
        """Populate all QTableViews using database manager methods."""
        if not self._validate_database_connection():
            print("Database connection not available for showing tables")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Refresh transactions table
            # Show last self.count_transactions_to_show records by default, or all records if toggle is on
            limit = None if self.show_all_transactions else self.count_transactions_to_show
            transactions_data = self.db_manager.get_all_transactions(limit=limit)
            transactions_transformed_data = self._transform_transaction_data(transactions_data)
            self.models["transactions"] = self._create_transactions_table_model(
                transactions_transformed_data, self.table_config["transactions"][2]
            )
            self.tableView_transactions.setModel(self.models["transactions"])

            # Refresh categories table
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

            # Refresh accounts table with sorting and color coding
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

            # Refresh currencies table
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

            # Refresh currency exchanges table
            exchanges_data = self.db_manager.get_all_currency_exchanges()
            exchanges_transformed_data = []
            for row in exchanges_data:
                # Transform: [id, from_code, to_code, amount_from_cents, amount_to_cents, rate_cents, fee_cents, date, description]
                amount_from = float(row[3]) / 100
                amount_to = float(row[4]) / 100
                rate = float(row[5]) / 100
                fee = float(row[6]) / 100
                color = QColor(255, 240, 255)
                transformed_row = [
                    row[1],
                    row[2],
                    f"{amount_from:.2f}",
                    f"{amount_to:.2f}",
                    f"{rate:.4f}",
                    f"{fee:.2f}",
                    row[7],
                    row[8],
                    row[0],
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

            # Refresh exchange rates table
            rates_data = self.db_manager.get_all_exchange_rates()
            rates_transformed_data = []
            for row in rates_data:
                # Transform: [id, from_code, to_code, rate_cents, date]
                rate = float(row[3]) / 100
                color = QColor(240, 255, 255)
                transformed_row = [row[1], row[2], f"{rate:.4f}", row[4], row[0], color]
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

            # Resize columns to content (excluding exchange table to preserve stretch settings)
            for table_name in self.table_config:
                if table_name != "currency_exchanges":  # Skip exchange table to preserve stretch settings
                    view = self.table_config[table_name][0]
                    view.resizeColumnsToContents()

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

            # Connect auto-save signals
            self._connect_table_auto_save_signals()

        except Exception as e:
            print(f"Error showing tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load tables: {e}")

    def update_all(self) -> None:
        """Refresh all tables and comboboxes."""
        if not self._validate_database_connection():
            print("Database connection not available for update_all")
            return

        self.show_tables()
        self._update_comboboxes()
        self.update_filter_comboboxes()
        self.update_chart_comboboxes()
        self.set_today_date()
        self.update_summary_labels()

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

            # Get total income and expenses
            total_income, total_expenses = self.db_manager.get_income_vs_expenses_in_currency(default_currency_id)

            # Update labels
            self.label_total_income.setText(f"Total Income: {total_income:.2f}{currency_symbol}")
            self.label_total_expenses.setText(f"Total Expenses: {total_expenses:.2f}{currency_symbol}")

            # Get today's balance
            today_balance = self.db_manager.get_today_balance_in_currency(default_currency_id)
            self.label_daily_balance.setText(f"{today_balance:.2f}{currency_symbol}")

            # Get today's expenses
            today_expenses = self.db_manager.get_today_expenses_in_currency(default_currency_id)
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
                    amount = self.db_manager.convert_from_minor_units(amount_cents,
                                                                     self.db_manager.get_currency_by_code(currency_code)[0]
                                                                     if self.db_manager.get_currency_by_code(currency_code) else 1)
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

        # Rate form
        self._clear_rate_form()

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

    def _clear_rate_form(self) -> None:
        """Clear the rate addition form."""
        self.doubleSpinBox_rate_value.setValue(73.5)

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
        self.pushButton_rate_add.clicked.connect(self.on_add_rate)

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
        self.doubleSpinBox_rate_value.setValue(73.5)
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
                amount = self.db_manager.convert_from_minor_units(amount_cents,
                                                                 self.db_manager.get_currency_by_code(currency_code)[0]
                                                                 if self.db_manager.get_currency_by_code(currency_code) else 1)
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
                self.comboBox_rate_from,
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))
    win = MainWindow()
    win.tabWidget.setCurrentIndex(0)
    sys.exit(app.exec())
