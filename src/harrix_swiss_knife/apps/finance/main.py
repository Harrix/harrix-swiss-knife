"""Finance tracker GUI.

This module contains a single `MainWindow` class that provides a Qt-based GUI for a
SQLite database with transactions, categories, accounts, currencies and exchange rates.
"""

from __future__ import annotations

import colorsys
import contextlib
import gc
import sys
from datetime import datetime, timedelta, timezone
from functools import partial
from pathlib import Path

import harrix_pylib as h
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import (
    QAbstractItemModel,
    QDate,
    QDateTime,
    QEvent,
    QItemSelectionModel,
    QModelIndex,
    QObject,
    QPoint,
    QSortFilterProxyModel,
    QStringListModel,
    Qt,
    QTimer,
)
from PySide6.QtGui import QBrush, QCloseEvent, QColor, QIcon, QKeyEvent, QMouseEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QCompleter,
    QDateEdit,
    QDialog,
    QFileDialog,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QWidget,
)

from harrix_swiss_knife import resources_rc  # noqa: F401
from harrix_swiss_knife.apps.finance import database_manager, window
from harrix_swiss_knife.apps.finance.account_edit_dialog import AccountEditDialog
from harrix_swiss_knife.apps.finance.delegates import (
    AmountDelegate,
    CategoryComboBoxDelegate,
    CurrencyComboBoxDelegate,
    DateDelegate,
    DescriptionDelegate,
    ReportAmountDelegate,
    TagDelegate,
)
from harrix_swiss_knife.apps.finance.exchange_edit_dialog import ExchangeEditDialog
from harrix_swiss_knife.apps.finance.exchange_rates_operations import ExchangeRatesOperations
from harrix_swiss_knife.apps.finance.mixins import (
    AutoSaveOperations,
    ChartOperations,
    DateOperations,
    TableOperations,
    ValidationOperations,
    requires_database,
)
from harrix_swiss_knife.apps.finance.text_input_dialog import TextInputDialog
from harrix_swiss_knife.apps.finance.text_parser import TextParser

config = h.dev.load_config("config/config.json")


class MainWindow(
    QMainWindow,
    window.Ui_MainWindow,
    TableOperations,
    ChartOperations,
    DateOperations,
    AutoSaveOperations,
    ValidationOperations,
    ExchangeRatesOperations,
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

    def __init__(self) -> None:
        """Initialize main window for finance tracking application."""
        super().__init__()
        self.setupUi(self)
        self._setup_ui()
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

        # Delegates for transactions table
        self.description_delegate: DescriptionDelegate | None = None
        self.category_delegate: CategoryComboBoxDelegate | None = None
        self.currency_delegate: CurrencyComboBoxDelegate | None = None
        self.date_delegate: DateDelegate | None = None
        self.tag_delegate: TagDelegate | None = None

        # Dialog state flags
        self._exchange_dialog_open: bool = False

        # Chart configuration
        self.max_count_points_in_charts: int = 40

        # Generate pastel colors for date-based coloring
        self.date_colors: list[QColor] = self.generate_pastel_colors_mathematical(50)

        # Initialize mouse button tracking
        self._right_click_in_progress: bool = False

        # Track whether account double-click handler is connected
        self._account_double_click_connected: bool = False

        # Toggle for showing all records vs last self.count_transactions_to_show
        self.count_transactions_to_show: int = 1000
        self.count_exchange_rates_to_show: int = 1000
        self.show_all_transactions: bool = False

        # Lazy loading flags
        self.exchange_rates_loaded: bool = False

        # Exchange rates initialization flag
        self._exchange_rates_initialized: bool = False
        self._exchange_rates_updating: bool = False

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

        # Get filter values
        transaction_type: int | None = None
        if self.radioButton_2.isChecked():  # Expense
            transaction_type = 0
        elif self.radioButton_3.isChecked():  # Income
            transaction_type = 1
        # If radioButton (All) is checked, transaction_type remains None

        category: str | None = (
            self.comboBox_filter_category.currentText() if self.comboBox_filter_category.currentText() else None
        )
        currency: str | None = (
            self.comboBox_filter_currency.currentText() if self.comboBox_filter_currency.currentText() else None
        )
        description_filter: str | None = (
            self.lineEdit_filter_description.text().strip() if self.lineEdit_filter_description.text().strip() else None
        )

        use_date_filter: bool = self.checkBox_use_date_filter.isChecked()
        date_from: str | None = self.dateEdit_filter_from.date().toString("yyyy-MM-dd") if use_date_filter else None
        date_to: str | None = self.dateEdit_filter_to.date().toString("yyyy-MM-dd") if use_date_filter else None

        # Use database manager method
        rows: list = self.db_manager.get_filtered_transactions(
            category_type=transaction_type,
            category_name=category,
            currency_code=currency,
            date_from=date_from,
            date_to=date_to,
            description_filter=description_filter,
        )

        # Transform data for display
        transformed_data: list[list] = self._transform_transaction_data(rows)

        # Create model and set to table
        self.models["transactions"] = self._create_transactions_table_model(
            transformed_data, self.table_config["transactions"][2]
        )
        self.tableView_transactions.setModel(self.models["transactions"])

        # Set up description delegate for the Description column (index 0)
        self.description_delegate = DescriptionDelegate(self.tableView_transactions)
        self.tableView_transactions.setItemDelegateForColumn(0, self.description_delegate)

        # Set up category delegate for the Category column (index 2)
        categories: list[str] = self._get_categories_for_delegate()
        self.category_delegate = CategoryComboBoxDelegate(self.tableView_transactions, categories)
        self.tableView_transactions.setItemDelegateForColumn(2, self.category_delegate)

        # Set up currency delegate for the Currency column (index 3)
        currencies: list[str] = self._get_currencies_for_delegate()
        self.currency_delegate = CurrencyComboBoxDelegate(self.tableView_transactions, currencies)
        self.tableView_transactions.setItemDelegateForColumn(3, self.currency_delegate)

        # Set up date delegate for the Date column (index 4)
        self.date_delegate = DateDelegate(self.tableView_transactions)
        self.tableView_transactions.setItemDelegateForColumn(4, self.date_delegate)

        # Set up tag delegate for the Tag column (index 5)
        tags: list[str] = self._get_tags_for_delegate()
        self.tag_delegate = TagDelegate(self.tableView_transactions, tags)
        self.tableView_transactions.setItemDelegateForColumn(5, self.tag_delegate)

        # Set up amount delegate for the Amount column (index 1)
        self.amount_delegate = AmountDelegate(self.tableView_transactions, self.db_manager)
        self.tableView_transactions.setItemDelegateForColumn(1, self.amount_delegate)

        # Set up amount delegate for the Total per day column (index 6)
        self.total_per_day_delegate = AmountDelegate(self.tableView_transactions, self.db_manager)
        self.tableView_transactions.setItemDelegateForColumn(6, self.total_per_day_delegate)

        # Enable editing for the Category column
        self.tableView_transactions.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)

        # Column stretching setup (like in show_tables)
        self.tableView_transactions.resizeColumnsToContents()

        # Table header behavior setup for column stretching
        header = self.tableView_transactions.horizontalHeader()
        if header.count() > 0:
            # Set stretch mode for all columns except the last two
            for i in range(header.count() - 2):
                header.setSectionResizeMode(i, header.ResizeMode.Stretch)

            # For the second-to-last column (Tag) set fixed width
            second_last_column: int = header.count() - 2
            header.setSectionResizeMode(second_last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(second_last_column, 100)

            # For the last column (Total per day) set fixed width
            last_column: int = header.count() - 1
            header.setSectionResizeMode(last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(last_column, 120)

        # Reconnect auto-save signals for the updated table
        self._connect_table_auto_save_signals()

    def clear_filter(self) -> None:
        """Reset all transaction filters."""
        self.radioButton.setChecked(True)  # All
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
        """Delete selected row from table using database manager methods.

        Args:

        - `table_name` (`str`): Name of the table to delete from. Must be in _SAFE_TABLES.

        Raises:

        - `ValueError`: If table_name is not in _SAFE_TABLES.

        """
        if table_name not in self._SAFE_TABLES:
            error_message = f"Illegal table name: {table_name}"
            raise ValueError(error_message)

        record_id: int | None = self._get_selected_row_id(table_name)
        if record_id is None:
            QMessageBox.warning(self, "Error", "Select a record to delete")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Use appropriate database manager method
        success: bool = False
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
            column_widths: list[int] | None = None
            if table_name == "currency_exchanges":
                column_widths = self._save_table_column_widths(self.tableView_exchange)

            self.update_all()

            # Restore column widths after update for exchange table
            if table_name == "currency_exchanges" and column_widths:
                self._restore_table_column_widths(self.tableView_exchange, column_widths)

            self.update_summary_labels()
        else:
            QMessageBox.warning(self, "Error", f"Deletion failed in {table_name}")

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
            if event.type() == QEvent.Type.MouseButtonPress:
                mouse_event = QMouseEvent(event)
                if mouse_event.button() == Qt.MouseButton.RightButton:
                    self._right_click_in_progress = True
                else:
                    self._right_click_in_progress = False

            elif event.type() == QEvent.Type.MouseButtonRelease:
                mouse_event = QMouseEvent(event)
                if mouse_event.button() == Qt.MouseButton.RightButton:
                    # Reset the flag shortly after release to allow context menu to process
                    QTimer.singleShot(100, lambda: setattr(self, "_right_click_in_progress", False))

        if obj == self.label_category_now and event.type() == QEvent.Type.MouseButtonPress:
            mouse_event = QMouseEvent(event)
            if mouse_event.button() == Qt.MouseButton.LeftButton:
                self._show_category_label_context_menu(mouse_event.position().toPoint())
                return True

        # Handle Enter key to add transaction quickly
        if (
            (obj == self.doubleSpinBox_amount and event.type() == QEvent.Type.KeyPress)
            or (obj == self.dateEdit and event.type() == QEvent.Type.KeyPress)
            or (obj == self.lineEdit_tag and event.type() == QEvent.Type.KeyPress)
            or (obj == self.lineEdit_description and event.type() == QEvent.Type.KeyPress)
            or (obj == self.pushButton_add and event.type() == QEvent.Type.KeyPress)
        ):
            key_event = QKeyEvent(event)
            if key_event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
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
        colors: list[QColor] = []

        for i in range(count):
            # Use golden ratio for even hue distribution
            hue: float = (i * 0.618033988749895) % 1.0  # Golden ratio

            # Lower saturation and higher lightness for very light pastel effect
            saturation: float = 0.6  # Very low saturation
            lightness: float = 0.95  # Very high lightness

            # Convert HSL to RGB
            r: float
            g: float
            b: float
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

            # Convert to 0-255 range and create QColor
            color: QColor = QColor(int(r * 255), int(g * 255), int(b * 255))
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
            table_views: list[QTableView] = [
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
        name: str = self.lineEdit_account_name.text().strip()
        balance: float = self.doubleSpinBox_account_balance.value()
        currency_code: str = self.comboBox_account_currency.currentText()
        is_liquid: bool = self.checkBox_is_liquid.isChecked()
        is_cash: bool = self.checkBox_is_cash.isChecked()

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

        currency_id: int = currency_info[0]

        try:
            if self.db_manager.add_account(name, balance, currency_id, is_liquid=is_liquid, is_cash=is_cash):
                self.update_all()
                self._clear_account_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to add account")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add account: {e}")

    def on_add_as_text(self) -> None:
        """Open text input dialog and process entered purchases."""
        if not self._validate_database_connection():
            QMessageBox.warning(self, "Error", "Database connection not available")
            return

        # Create and show the text input dialog
        dialog: TextInputDialog = TextInputDialog(self)
        result: int = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            text: str = dialog.get_text()
            if text:
                self._process_text_input(text)

    @requires_database()
    def on_add_category(self) -> None:
        """Add a new category using database manager."""
        name: str = self.lineEdit_category_name.text().strip()
        category_type: int = self.comboBox_category_type.currentIndex()  # 0 = Expense, 1 = Income

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
        code: str = self.lineEdit_currency_code.text().strip().upper()
        name: str = self.lineEdit_currency_name.text().strip()
        symbol: str = self.lineEdit_currency_symbol.text().strip()
        subdivision: int = self.spinBox_subdivision.value()

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
        from_currency: str = self.comboBox_exchange_from.currentText()
        to_currency: str = self.comboBox_exchange_to.currentText()
        amount_from: float = self.doubleSpinBox_exchange_from.value()
        amount_to: float = self.doubleSpinBox_exchange_to.value()
        exchange_rate: float = self.doubleSpinBox_exchange_rate.value()
        fee: float = self.doubleSpinBox_exchange_fee.value()
        date: str = self.dateEdit_exchange.date().toString("yyyy-MM-dd")
        description: str = self.lineEdit_exchange_description.text().strip()

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

        from_currency_id: int = from_currency_info[0]
        to_currency_id: int = to_currency_info[0]

        try:
            if self.db_manager.add_currency_exchange(
                from_currency_id, to_currency_id, amount_from, amount_to, exchange_rate, fee, date, description
            ):
                # Save current column widths before update
                column_widths: list[int] = self._save_table_column_widths(self.tableView_exchange)

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
        amount: float = self.doubleSpinBox_amount.value()
        description: str = self.lineEdit_description.text().strip()
        category_name: str | None = (
            self.listView_categories.currentIndex().data(Qt.ItemDataRole.UserRole)
            if self.listView_categories.currentIndex().isValid()
            else None
        )
        currency_code: str = self.comboBox_currency.currentText()
        date: str = self.dateEdit.date().toString("yyyy-MM-dd")
        tag: str = self.lineEdit_tag.text().strip()

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
        cat_id: int | None = self.db_manager.get_id("categories", "name", category_name)
        if cat_id is None:
            QMessageBox.warning(self, "Error", f"Category '{category_name}' not found")
            return

        # Get currency ID
        currency_info = self.db_manager.get_currency_by_code(currency_code)
        if not currency_info:
            QMessageBox.warning(self, "Error", f"Currency '{currency_code}' not found")
            return

        currency_id: int = currency_info[0]

        try:
            if self.db_manager.add_transaction(amount, description, cat_id, currency_id, date, tag):
                # Save current date before updating UI
                current_date: QDate = self.dateEdit.date()

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
                self.label_category_now.setText("No category selected")

            # Move focus to description field and select all text
            QTimer.singleShot(100, self._focus_description_and_select_text)
        else:
            self.label_category_now.setText("No category selected")

    def on_clear_description(self) -> None:
        """Clear the description field."""
        self.lineEdit_description.clear()

    def on_copy_categories_as_text(self) -> None:
        """Copy list of categories to clipboard as text."""
        if self.db_manager is None:
            QMessageBox.warning(
                self, "Database Error", "❌ Database manager is not initialized. Please try again later."
            )
            return

        try:
            # Get all categories
            categories_data: list = self.db_manager.get_all_categories()

            if not categories_data:
                QMessageBox.information(self, "No Categories", "No categories found in the database.")
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
            QMessageBox.information(
                self,
                "Categories Copied",
                f"✅ Successfully copied {len(categories_text)} categories to clipboard:\n\n{clipboard_text}",
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Error copying categories to clipboard:\n\n{e!s}")

    def on_exchange_item_update_button_clicked(self) -> None:
        """Update exchange rate in database when pushButton_exchange_item_update is clicked."""
        if not self._validate_database_connection():
            return

        try:
            # Get selected currency ID
            currency_index: int = self.comboBox_exchange_item_update.currentIndex()
            if currency_index < 0:
                QMessageBox.warning(self, "Invalid Selection", "Please select a currency.")
                return

            currency_id = self.comboBox_exchange_item_update.itemData(currency_index)
            if currency_id is None:
                QMessageBox.warning(self, "Invalid Selection", "Please select a valid currency.")
                return

            # Get selected date
            selected_date: QDate = self.dateEdit_exchange_item_update.date()
            date_str: str = selected_date.toString("yyyy-MM-dd")

            # Get exchange rate value
            exchange_rate: float = self.doubleSpinBox_exchange_item_update.value()
            if exchange_rate <= 0:
                QMessageBox.warning(self, "Invalid Rate", "Exchange rate must be greater than 0.")
                return

            # Get currency info for confirmation dialog
            currency_text: str = self.comboBox_exchange_item_update.currentText()

            # Confirm update
            reply = QMessageBox.question(
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
                QMessageBox.information(
                    self,
                    "Update Successful",
                    f"Exchange rate for {currency_text} on {date_str} has been updated to {exchange_rate}.",
                )
                # Clear exchange rate cache to ensure fresh data
                if hasattr(self.db_manager, "_exchange_rate_cache"):
                    self.db_manager._exchange_rate_cache.clear()  # noqa: SLF001
                # Update all views
                self.update_all()
                self.update_summary_labels()
                # Update exchange rates chart if on the same currency
                self.on_exchange_rates_update()
            else:
                QMessageBox.warning(
                    self,
                    "Update Failed",
                    "Failed to update exchange rate. Please check the database connection and try again.",
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while updating exchange rate: {e}")

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
            model = self.models["transactions"].sourceModel()
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
            QMessageBox.warning(self, "Export Error", f"Failed to export CSV: {e}")

    @requires_database()
    def on_generate_report(self) -> None:
        """Generate selected report."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        report_type: str = self.comboBox_report_type.currentText()
        default_currency_id: int = self.db_manager.get_default_currency_id()

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
        currency_code: str = self.comboBox_default_currency.currentText()

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
        id_exchange_rates_tab: int = 4
        id_charts_tab: int = 6
        id_reports_tab: int = 7
        if index == id_exchange_rates_tab:  # Exchange Rates tab - lazy loading
            if not self.exchange_rates_loaded:
                self.load_exchange_rates_table()
        elif index == id_charts_tab:  # Charts tab
            self.update_chart_comboboxes()
        elif index == id_reports_tab:  # Reports tab
            self.update_summary_labels()
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
        today_qdate: QDate = QDate.currentDate()
        self.dateEdit.setDate(today_qdate)
        self.dateEdit_exchange.setDate(today_qdate)

    def show_balance_chart(self) -> None:
        """Show balance chart."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get default currency
        default_currency_id: int = self.db_manager.get_default_currency_id()
        default_currency_code: str = self.db_manager.get_default_currency()

        # Get date range
        date_from: str = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to: str = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get transaction data for balance calculation
        rows: list = self.db_manager.get_transactions_chart_data(
            default_currency_id, date_from=date_from, date_to=date_to
        )

        if not rows:
            self._show_no_data_label(self.scrollAreaWidgetContents_charts.layout(), "No data found for balance chart")
            return

        # Calculate running balance
        balance: float = 0.0
        balance_data: list[tuple[datetime, float]] = []

        for date_str, _amount in rows:
            # Get transactions for this date
            daily_transactions: list = self.db_manager.get_transactions_chart_data(
                default_currency_id, date_from=date_str, date_to=date_str
            )

            daily_balance: float = 0.0
            for _, _daily_amount in daily_transactions:
                # Get category type for each transaction to determine if it's income or expense
                trans_rows: list = self.db_manager.get_filtered_transactions(date_from=date_str, date_to=date_str)
                for trans_row in trans_rows:
                    if trans_row[5] == date_str:  # date column
                        category_type: int = trans_row[7]  # type column
                        trans_amount: float = float(trans_row[1]) / 100  # amount in cents
                        if category_type == 1:  # Income
                            daily_balance += trans_amount
                        else:  # Expense
                            daily_balance -= trans_amount

            balance += daily_balance
            date_obj: datetime = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
            balance_data.append((date_obj, balance))

        # Create chart configuration
        chart_config: dict[str, str | bool] = {
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
        default_currency_id: int = self.db_manager.get_default_currency_id()
        default_currency_code: str = self.db_manager.get_default_currency()

        # Get date range
        date_from: str = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to: str = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get expense transactions by category
        expense_rows: list = self.db_manager.get_filtered_transactions(
            category_type=0, date_from=date_from, date_to=date_to
        )

        if not expense_rows:
            self._show_no_data_label(
                self.scrollAreaWidgetContents_charts.layout(), "No expense data found for pie chart"
            )
            return

        # Group by category and sum amounts (converted to default currency)
        category_totals: dict[str, float] = {}
        for row in expense_rows:
            category_name: str = row[3]  # category name
            amount_cents: int = row[1]  # amount in cents
            currency_code: str = row[4]  # currency code
            transaction_date: str = row[5]  # transaction date

            # Convert to default currency
            amount: float = float(amount_cents) / 100
            if currency_code != default_currency_code:
                currency_info = self.db_manager.get_currency_by_code(currency_code)
                if currency_info:
                    source_currency_id: int = currency_info[0]
                    amount = self._convert_currency_amount(
                        amount, source_currency_id, default_currency_id, transaction_date
                    )

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
        current_tab_index: int = self.tabWidget.currentIndex()
        id_exchange_rates_tab = 4
        if current_tab_index == id_exchange_rates_tab:  # Exchange Rates tab
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
            categories: list[str] = self.db_manager.get_categories_by_type(0) + self.db_manager.get_categories_by_type(
                1
            )

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

        category: str = self.comboBox_chart_category.currentText()
        chart_type: str = self.comboBox_chart_type.currentText()
        period: str = self.comboBox_chart_period.currentText()
        date_from: str = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to: str = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get default currency
        default_currency_id: int = self.db_manager.get_default_currency_id()
        default_currency_code: str = self.db_manager.get_default_currency()

        # Determine category type filter
        category_type: int | None = None
        if chart_type == "Income":
            category_type = 1
        elif chart_type == "Expense":
            category_type = 0

        # Get chart data
        rows: list = self.db_manager.get_transactions_chart_data(
            default_currency_id, category_type=category_type, date_from=date_from, date_to=date_to
        )

        if not rows:
            self._show_no_data_label(
                self.scrollAreaWidgetContents_charts.layout(), "No data found for the selected period"
            )
            return

        # Group data by period
        grouped_data: dict = self._group_data_by_period(rows, period)
        chart_data: list = list(grouped_data.items())

        # Create chart configuration
        chart_title: str = f"{chart_type} Transactions"
        if category != "All Categories":
            chart_title += f" - {category}"
        chart_title += f" ({period})"

        chart_config: dict[str, str | bool] = {
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
        """Update summary labels with current totals in default currency."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get default currency
            default_currency_id: int = self.db_manager.get_default_currency_id()
            default_currency_info = self.db_manager.get_currency_by_code(self.db_manager.get_default_currency())
            currency_symbol: str = default_currency_info[2] if default_currency_info else "₽"

            # For initial loading, only show sums in default currency
            # without conversion from other currencies

            # Simplified query for getting sums only in default currency
            query_income: str = """
                SELECT SUM(t.amount) as total_income
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 1 AND t._id_currencies = :currency_id
            """

            query_expenses: str = """
                SELECT SUM(t.amount) as total_expenses
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 0 AND t._id_currencies = :currency_id
            """

            income_rows: list = self.db_manager.get_rows(query_income, {"currency_id": default_currency_id})
            expenses_rows: list = self.db_manager.get_rows(query_expenses, {"currency_id": default_currency_id})

            total_income: float = float(income_rows[0][0] or 0) / 100 if income_rows and income_rows[0][0] else 0.0
            total_expenses: float = (
                float(expenses_rows[0][0] or 0) / 100 if expenses_rows and expenses_rows[0][0] else 0.0
            )

            # Update labels
            self.label_total_income.setText(f"Total Income: {total_income:.2f}{currency_symbol}")
            self.label_total_expenses.setText(f"Total Expenses: {total_expenses:.2f}{currency_symbol}")

            # For today's balance and expenses also use simplified queries
            today: str = datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d")

            today_query_income: str = """
                SELECT SUM(t.amount) as total
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 1 AND t._id_currencies = :currency_id AND t.date = :date
            """

            today_query_expenses: str = """
                SELECT SUM(t.amount) as total
                FROM transactions t
                JOIN categories cat ON t._id_categories = cat._id
                WHERE cat.type = 0 AND t._id_currencies = :currency_id AND t.date = :date
            """

            today_income_rows: list = self.db_manager.get_rows(
                today_query_income, {"currency_id": default_currency_id, "date": today}
            )
            today_expenses_rows: list = self.db_manager.get_rows(
                today_query_expenses, {"currency_id": default_currency_id, "date": today}
            )

            today_income: float = (
                float(today_income_rows[0][0] or 0) / 100 if today_income_rows and today_income_rows[0][0] else 0.0
            )
            today_expenses: float = (
                float(today_expenses_rows[0][0] or 0) / 100
                if today_expenses_rows and today_expenses_rows[0][0]
                else 0.0
            )

            today_balance: float = today_income - today_expenses

            self.label_daily_balance.setText(f"{today_balance:.2f}{currency_symbol}")
            self.label_today_expense.setText(f"{today_expenses:.2f}{currency_symbol}")

        except Exception as e:
            print(f"Error updating summary labels: {e}")
            # Set default values on error
            self.label_total_income.setText("Total Income: 0.00₽")
            self.label_total_expenses.setText("Total Expenses: 0.00₽")
            self.label_daily_balance.setText("0.00₽")
            self.label_today_expense.setText("0.00₽")

    def _add_one_day_to_main(self) -> None:
        """Add one day to the current date in main date field."""
        current_date: QDate = self.dateEdit.date()
        new_date: QDate = current_date.addDays(1)
        self.dateEdit.setDate(new_date)

    def _calculate_daily_expenses(self, rows: list[list]) -> dict[str, float]:
        """Calculate daily expenses from transaction data.

        Args:

        - `rows` (`list[list]`): Raw transaction data from database.

        Returns:

        - `dict[str, float]`: Dictionary mapping dates to total expenses for that day.

        """
        daily_expenses: dict[str, float] = {}

        for row in rows:
            amount_cents: int = row[1]
            date: str = row[5]
            category_type: int = row[7]

            # Only count expenses (category_type == 0)
            if category_type == 0:
                # Convert amount from minor units to display format using currency subdivision
                currency_code: str = row[4]
                amount: float
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
        try:
            # Determine which date to use
            target_date: str = (
                use_date
                if use_date is not None
                else datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d")
            )

            # Get exchange rate for the target date
            rate_to_per_from: float = self.db_manager.get_exchange_rate(from_currency_id, to_currency_id, target_date)

            # If rate is 1.0 and currencies are different, get the latest available rate
            if rate_to_per_from == 1.0 and from_currency_id != to_currency_id and use_date is None:
                rate_to_per_from = self.db_manager.get_exchange_rate(from_currency_id, to_currency_id)

            # Calculate loss in source currency using the rate
            loss_in_from_currency: float = self._calculate_exchange_loss_in_source_currency(
                from_currency_id, to_currency_id, amount_from, amount_to, rate_to_per_from, fee
            )

            # Convert loss to default currency using today's rate
            if default_currency_id is not None and from_currency_id != default_currency_id:
                today: str = datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d")
                return self._convert_currency_amount(
                    loss_in_from_currency, from_currency_id, default_currency_id, today
                )
        except Exception as e:
            date_info = f"date {use_date}" if use_date else "today"
            print(f"Error calculating exchange loss for {date_info}: {e}")
            return 0.0

        return loss_in_from_currency

    def _calculate_exchange_loss_in_source_currency(
        self,
        _from_currency_id: int,
        _to_currency_id: int,
        amount_from: float,
        amount_to: float,
        rate_to_per_from: float,
        fee: float = 0.0,
    ) -> float:
        """Calculate exchange loss in source currency using given rate.

        Args:

        - `from_currency_id` (`int`): Source currency ID
        - `to_currency_id` (`int`): Target currency ID
        - `amount_from` (`float`): Amount in source currency
        - `amount_to` (`float`): Amount in target currency
        - `rate_to_per_from` (`float`): Exchange rate (to per 1 from)
        - `fee` (`float`): Exchange fee in source currency

        Returns:

        - `float`: Loss amount in source currency (negative = loss, positive = profit)

        """
        try:
            if rate_to_per_from and rate_to_per_from != 0:
                expected_from: float = amount_to / rate_to_per_from
                # Include fee in the total cost
                total_cost: float = amount_from + fee
                diff_from: float = total_cost - expected_from
                # Displayed value should be negative for loss, positive for profit
                return -diff_from
        except Exception as e:
            print(f"Error calculating exchange loss in source currency: {e}")
        return 0.0

    def _calculate_total_accounts_balance(self) -> tuple[float, str]:
        """Calculate total balance across all accounts in default currency.

        Returns:

        - `tuple[float, str]`: (total_balance, formatted_details)

        """
        if not self._validate_database_connection() or self.db_manager is None:
            return 0.0, "Database not available"

        try:
            # Get default currency info
            default_currency_code: str = self.db_manager.get_default_currency()
            default_currency_info = self.db_manager.get_currency_by_code(default_currency_code)
            if not default_currency_info:
                return 0.0, "Default currency not found"

            default_currency_id: int = default_currency_info[0]
            default_currency_symbol: str = default_currency_info[2]
            self.db_manager.get_currency_subdivision(default_currency_id)

            # Get all accounts
            accounts_data: list = self.db_manager.get_all_accounts()

            total_balance: float = 0.0
            today: str = datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d")

            # Group accounts by currency for summary display
            currency_balances: dict[str, float] = {}

            for account in accounts_data:
                _account_id, _account_name, balance_minor_units, currency_code, _is_liquid, _is_cash, currency_id = (
                    account
                )

                # Convert balance from minor units to major units
                account_subdivision: int = self.db_manager.get_currency_subdivision(currency_id)
                balance_major_units: float = balance_minor_units / account_subdivision

                if currency_id == default_currency_id:
                    # Same currency - no conversion needed
                    total_balance += balance_major_units
                    if currency_code not in currency_balances:
                        currency_balances[currency_code] = 0.0
                    currency_balances[currency_code] += balance_major_units
                else:
                    # Different currency - need to convert via USD
                    # Convert to default currency using centralized conversion method
                    converted_balance: float = self._convert_currency_amount(
                        balance_major_units, currency_id, default_currency_id, today
                    )

                    # Check if conversion was successful (not equal to original when currencies differ)
                    if converted_balance == balance_major_units and currency_id != default_currency_id:
                        print(f"Warning: No exchange rate found for {currency_code} to {default_currency_code}")

                    total_balance += converted_balance

                    # Group by currency for summary
                    if currency_code not in currency_balances:
                        currency_balances[currency_code] = 0.0
                    currency_balances[currency_code] += balance_major_units

            # Format total balance with proper symbol and subdivision

            # Format details by currency (show summary by currency)
            details_lines: list[str] = []
            for currency_code, balance in currency_balances.items():
                if currency_code == default_currency_code:
                    # Default currency - show as is
                    details_lines.append(f"{currency_code}: {balance:,.2f}{default_currency_symbol}")
                else:
                    # Other currency - show converted amount
                    # Get currency info for display
                    currency_info = self.db_manager.get_currency_by_id(
                        self.db_manager.get_currency_by_code(currency_code)[0]
                    )
                    currency_symbol: str = currency_info[2] if currency_info else currency_code

                    # Calculate converted amount for this currency
                    currency_id: int = self.db_manager.get_currency_by_code(currency_code)[0]
                    converted_amount: float = self._convert_currency_amount(
                        balance, currency_id, default_currency_id, today
                    )

                    if converted_amount == balance and currency_id != default_currency_id:
                        # No valid exchange rate found
                        details_lines.append(
                            f"{currency_code}: {balance:,.2f}{currency_symbol} (exchange rate not found)"
                        )
                    else:
                        details_lines.append(
                            f"{currency_code}: {balance:,.2f}{currency_symbol} → "
                            f"{converted_amount:,.2f}{default_currency_symbol}"
                        )

            details_text: str = "\n".join(details_lines)

        except Exception as e:
            print(f"Error calculating total accounts balance: {e}")
            return 0.0, f"Error: {e!s}"
        return total_balance, details_text

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

    def _clear_layout(self, layout: QLayout) -> None:
        """Clear all widgets from the specified layout.

        Args:

        - `layout` (`QLayout`): The layout to clear.

        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                widget = child.widget()
                # Special handling for matplotlib canvas
                if hasattr(widget, "figure"):
                    try:
                        # Mark canvas as being deleted to prevent new updates
                        widget._deleting = True  # noqa: SLF001
                        # Clear the figure first
                        widget.figure.clear()
                        # Close the canvas properly
                        widget.close()
                        # Force garbage collection
                        gc.collect()
                    except Exception as e:
                        print(f"Error while clearing matplotlib canvas: {e}")
                widget.deleteLater()

    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers."""
        # Main transaction signals
        self.pushButton_add.clicked.connect(self.on_add_transaction)
        self.pushButton_add_as_text.clicked.connect(self.on_add_as_text)
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
        self.pushButton_currency_add.clicked.connect(self.on_add_currency)
        self.pushButton_exchange_add.clicked.connect(self.on_add_exchange)

        # Copy categories as text button
        self.pushButton_copy_categories_as_text.clicked.connect(self.on_copy_categories_as_text)

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

    def _convert_currency_amount(
        self,
        amount: float,
        from_currency_id: int,
        to_currency_id: int,
        date: str | None = None,
    ) -> float:
        """Convert amount from one currency to another.

        Args:

        - `amount` (`float`): Amount to convert
        - `from_currency_id` (`int`): Source currency ID
        - `to_currency_id` (`int`): Target currency ID
        - `date` (`str`): Date for rate lookup (uses today if None)

        Returns:

        - `float`: Converted amount in target currency

        """
        try:
            if from_currency_id == to_currency_id:
                return amount

            if date is None:
                date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            rate: float = self.db_manager.get_exchange_rate(from_currency_id, to_currency_id, date)
            if rate == 1.0 and from_currency_id != to_currency_id:
                rate = self.db_manager.get_exchange_rate(from_currency_id, to_currency_id)

            if rate and rate != 0:
                return amount * rate
        except Exception as e:
            print(f"Error converting currency amount: {e}")
        return amount

    def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None:
        """Copy selected cells from table to clipboard as tab-separated text.

        Args:

        - `table_view` (`QTableView`): The table view to copy data from.

        """
        selection_model = table_view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return

        # Get selected indexes and sort them by row and column
        selected_indexes: list[QModelIndex] = selection_model.selectedIndexes()
        if not selected_indexes:
            return

        # Sort indexes by row first, then by column
        selected_indexes.sort(key=lambda index: (index.row(), index.column()))

        # Group indexes by row
        rows_data: dict[int, dict[int, str]] = {}
        for index in selected_indexes:
            row: int = index.row()
            if row not in rows_data:
                rows_data[row] = {}

            # Get cell data
            cell_data = table_view.model().data(index, Qt.ItemDataRole.DisplayRole)
            rows_data[row][index.column()] = str(cell_data) if cell_data is not None else ""

        # Build clipboard text
        clipboard_text: list[str] = []
        for row in sorted(rows_data.keys()):
            row_data: dict[int, str] = rows_data[row]
            # Get all columns for this row and fill missing ones with empty strings
            if row_data:
                min_col: int = min(row_data.keys())
                max_col: int = max(row_data.keys())
                clipboard_text.append("\t".join([row_data.get(col, "") for col in range(min_col, max_col + 1)]))

        # Copy to clipboard
        if clipboard_text:
            final_text: str = "\n".join(clipboard_text)
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
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID (second-to-last element)
            row_color: QColor = row[-1]  # Color is at the last position
            row_id: int = row[id_column]  # ID is at second-to-last position

            # Create items for display columns only (exclude ID and color)
            items: list[QStandardItem] = []
            display_data: list = row[:-2]  # Exclude last two elements (ID and color)

            for _col_idx, value in enumerate(display_data):
                item: QStandardItem = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

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
        fig: Figure = Figure(figsize=(10, 8), dpi=100)
        canvas: FigureCanvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Prepare data for pie chart
        labels: list[str] = list(data.keys())
        sizes: list[float] = list(data.values())

        # Create pie chart
        pie_result_len: int = 3  # Number of expected return values from ax.pie
        pie_result = ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        if len(pie_result) == pie_result_len:
            _wedges, _texts, autotexts = pie_result
        else:
            _wedges, _texts = pie_result[0], pie_result[1]
            autotexts = []

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
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            items: list[QStandardItem] = [
                QStandardItem(str(value) if value is not None else "")
                for col_idx, value in enumerate(row)
                if col_idx != id_column
            ]
            model.appendRow(items)
            model.setVerticalHeaderItem(
                row_idx,
                QStandardItem(str(row[id_column])),
            )

        proxy: QSortFilterProxyModel = QSortFilterProxyModel()
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

    def _finish_window_initialization(self) -> None:
        """Finish window initialization by showing the window."""
        self.show()

        # Set focus to description field
        self.lineEdit_description.setFocus()

        # Select category with _id = 1
        self._select_category_by_id(1)

        # Setup exchange rates controls
        self._setup_exchange_rates_controls()

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

    def _generate_account_balances_report(self, currency_id: int) -> None:
        """Generate account balances report.

        Args:

        - `currency_id` (`int`): Currency ID for conversion.

        """
        if self.db_manager is None:
            return

        account_balances: list[tuple[str, float]] = self.db_manager.get_account_balances_in_currency(currency_id)
        currency_code: str = self.db_manager.get_default_currency()

        # Create report data
        report_data: list[list[str]] = []
        total_balance: float = 0.0

        for account_name, balance in account_balances:
            report_data.append([account_name, f"{balance:.2f} {currency_code}"])
            total_balance += balance

        # Add total row
        report_data.append(["TOTAL", f"{total_balance:.2f} {currency_code}"])

        # Create model
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Account", "Balance"])

        for row_data in report_data:
            items: list[QStandardItem] = [QStandardItem(str(value)) for value in row_data]
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

    def _generate_category_analysis_report(self, _currency_id: int) -> None:
        """Generate category analysis report.

        Args:

        - `_currency_id` (`int`): Currency ID for conversion.

        """
        if self.db_manager is None:
            return

        currency_code: str = self.db_manager.get_default_currency()

        # Get transactions for last 30 days
        end_date: datetime = datetime.now(tz=datetime.now().astimezone().tzinfo)
        start_date: datetime = end_date - timedelta(days=30)
        date_from: str = start_date.strftime("%Y-%m-%d")
        date_to: str = end_date.strftime("%Y-%m-%d")

        # Get expenses and income separately
        expense_rows: list = self.db_manager.get_filtered_transactions(
            category_type=0, date_from=date_from, date_to=date_to
        )
        income_rows: list = self.db_manager.get_filtered_transactions(
            category_type=1, date_from=date_from, date_to=date_to
        )

        # Group by category
        expense_totals: dict[str, float] = {}
        income_totals: dict[str, float] = {}

        for row in expense_rows:
            category: str = row[3]  # category name
            amount: float = float(row[1]) / 100  # amount in cents
            expense_totals[category] = expense_totals.get(category, 0) + amount

        for row in income_rows:
            category: str = row[3]  # category name
            amount: float = float(row[1]) / 100  # amount in cents
            income_totals[category] = income_totals.get(category, 0) + amount

        # Create report data
        report_data: list[list[str]] = []

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
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Category", "Amount", "Type"])

        for row_data in report_data:
            items: list[QStandardItem] = [QStandardItem(str(value)) for value in row_data]
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
        currencies: list = self.db_manager.get_all_currencies()

        report_data: list[list[str]] = []
        for currency_row in currencies:
            currency_row[0]
            currency_code: str = currency_row[1]

            # Count transactions in this currency
            transactions: list = self.db_manager.get_filtered_transactions(currency_code=currency_code)
            transaction_count: int = len(transactions)

            # Calculate total amount
            total_amount: float = sum(float(row[1]) / 100 for row in transactions)

            report_data.append([currency_code, str(transaction_count), f"{total_amount:.2f}"])

        # Create model
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Currency", "Transaction Count", "Total Amount"])

        for row_data in report_data:
            items: list[QStandardItem] = [QStandardItem(str(value)) for value in row_data]
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

        currency_code: str = self.db_manager.get_default_currency()

        # Get data for different periods
        periods: list[tuple[str, int]] = [
            ("Today", 0),
            ("Last 7 days", 7),
            ("Last 30 days", 30),
            ("Last 90 days", 90),
            ("Last 365 days", 365),
        ]

        report_data: list[list[str]] = []

        for period_name, days in periods:
            if days == 0:
                # Today
                today: str = datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d")
                date_from = date_to = today
            else:
                # Last N days
                end_date: datetime = datetime.now(tz=datetime.now().astimezone().tzinfo)
                start_date: datetime = end_date - timedelta(days=days)
                date_from: str = start_date.strftime("%Y-%m-%d")
                date_to: str = end_date.strftime("%Y-%m-%d")

            income: float
            expenses: float
            income, expenses = self.db_manager.get_income_vs_expenses_in_currency(currency_id, date_from, date_to)

            balance: float = income - expenses

            report_data.append(
                [
                    period_name,
                    f"{income:.2f} {currency_code}",
                    f"{expenses:.2f} {currency_code}",
                    f"{balance:.2f} {currency_code}",
                ]
            )

        # Create model
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Period", "Income", "Expenses", "Balance"])

        for row_data in report_data:
            items: list[QStandardItem] = [QStandardItem(str(value)) for value in row_data]
            # Color code the balance
            balance_str: str = row_data[3]
            balance_value: float = float(balance_str.split()[0])
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
        """Generate monthly summary report showing expenses by category per month.

        Args:

        - `currency_id` (`int`): Currency ID for conversion.

        """
        if self.db_manager is None:
            return

        currency_code: str = self.db_manager.get_default_currency()

        # Get all expense categories
        all_categories: list = self.db_manager.get_all_categories()
        expense_categories: list[tuple[int, str, str]] = []  # (id, name, icon)
        category_name_to_id: dict[str, int] = {}  # Map category name to ID for fast lookup

        for category in all_categories:
            category_id, category_name, category_type, category_icon = (
                category[0],
                category[1],
                category[2],
                category[3],
            )
            if category_type == 0:  # 0 = expense
                # Create display name with icon
                display_name = f"{category_icon} {category_name}" if category_icon else category_name
                expense_categories.append((category_id, display_name, category_icon))
                category_name_to_id[category_name] = category_id

        if not expense_categories:
            # No categories found, show empty table
            model: QStandardItemModel = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Month"])
            self.tableView_reports.setModel(model)
            return

        # Sort categories by name for consistent display
        expense_categories.sort(key=lambda x: x[1])

        # Determine month range based on available transaction history
        end_date: datetime = datetime.now(tz=datetime.now().astimezone().tzinfo)
        earliest_transaction_date_str = self.db_manager.get_earliest_transaction_date()

        if earliest_transaction_date_str:
            earliest_transaction_date = datetime.strptime(
                earliest_transaction_date_str, "%Y-%m-%d"
            ).replace(tzinfo=end_date.tzinfo)
            month_cursor = earliest_transaction_date.replace(day=1)
        else:
            month_cursor = end_date.replace(day=1)

        end_month = end_date.replace(day=1)

        # Dictionary to store data: {month_name: {category_id: amount}}
        monthly_data: dict[str, dict[int, float]] = {}
        month_names: list[str] = []

        while month_cursor <= end_month:
            month_start: datetime = month_cursor

            # Calculate last day of month
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            month_end: datetime = next_month - timedelta(days=1)

            date_from: str = month_start.strftime("%Y-%m-%d")
            date_to: str = month_end.strftime("%Y-%m-%d")
            month_name: str = month_start.strftime("%Y-%m")

            month_names.append(month_name)
            monthly_data[month_name] = {}

            # Get all expense transactions for this month
            expense_rows: list = self.db_manager.get_filtered_transactions(
                category_type=0, date_from=date_from, date_to=date_to
            )

            # Process transactions and group by category
            for row in expense_rows:
                # row structure: [_id, amount, description, cat.name, c.code, date, tag, cat.type, cat.icon, c.symbol]
                amount_cents: int = row[1]  # amount in cents
                category_name_from_row: str = row[3]  # category name
                currency_code_tx: str = row[4]  # currency code
                transaction_date: str = row[5]  # transaction date

                # Get category_id from name using lookup dictionary
                category_id_matched: int | None = category_name_to_id.get(category_name_from_row)

                if category_id_matched is None:
                    continue

                # Convert amount to default currency
                amount: float = float(amount_cents) / 100
                if currency_code_tx != currency_code:
                    currency_info = self.db_manager.get_currency_by_code(currency_code_tx)
                    if currency_info:
                        source_currency_id: int = currency_info[0]
                        amount = self._convert_currency_amount(
                            amount, source_currency_id, currency_id, transaction_date
                        )

                # Add to category total for this month
                if category_id_matched in monthly_data[month_name]:
                    monthly_data[month_name][category_id_matched] += amount
                else:
                    monthly_data[month_name][category_id_matched] = amount

            month_cursor = next_month

        # Create model with column headers
        model: QStandardItemModel = QStandardItemModel()
        headers: list[str] = ["Month", "Total", "Cafe + Food"]  # Month, Total, combined column
        headers.extend([cat[1] for cat in expense_categories])  # Add category names
        model.setHorizontalHeaderLabels(headers)

        # Generate colors for categories (using HSV color space for distinct colors)
        num_categories = len(expense_categories)
        category_colors: list[QColor] = []
        for i in range(num_categories):
            # Generate evenly distributed hues
            hue = (i * 360) / num_categories if num_categories > 0 else 0
            # Use pastel colors (high lightness, low saturation)
            color = QColor.fromHsv(int(hue), 80, 240)  # Saturation=80, Value=240
            category_colors.append(color)

        # Pre-calculate category IDs for Cafe and Food (case-insensitive match)
        combined_category_targets = {"cafe", "food"}

        def _normalize_category_tokens(name: str) -> set[str]:
            cleaned = "".join(ch if ch.isalnum() else " " for ch in name)
            return {token for token in cleaned.casefold().split() if token}

        combined_category_ids: set[int] = {
            category_id
            for name, category_id in category_name_to_id.items()
            if _normalize_category_tokens(name) & combined_category_targets
        }

        # Create rows (newest first)
        current_year_prefix = datetime.now(tz=end_date.tzinfo).strftime("%Y-")

        for month_name in reversed(month_names):
            row_items: list[QStandardItem] = []

            # Month name (no background color)
            month_item = QStandardItem(month_name)
            if month_name.startswith(current_year_prefix):
                font = month_item.font()
                font.setBold(True)
                month_item.setFont(font)
            row_items.append(month_item)

            # Calculate total first
            month_total: float = 0.0
            for category_id, _category_name, _category_icon in expense_categories:
                amount = monthly_data[month_name].get(category_id, 0.0)
                month_total += amount

            # Total for the month (light gray background) - add as second column
            total_item = QStandardItem(f"{month_total:.2f}")
            total_item.setBackground(QBrush(QColor(220, 220, 220)))  # Light gray
            total_item.setData(month_total, Qt.ItemDataRole.UserRole)
            row_items.append(total_item)

            # Combined Cafe + Food column (light yellow background)
            combined_total: float = 0.0
            for category_id in combined_category_ids:
                combined_total += monthly_data[month_name].get(category_id, 0.0)

            combined_item = QStandardItem(f"{combined_total:.2f}")
            combined_item.setBackground(QBrush(QColor(255, 250, 205)))  # Lemon chiffon
            combined_item.setData(combined_total, Qt.ItemDataRole.UserRole)
            row_items.append(combined_item)

            # Category amounts with colors
            for idx, (category_id, _category_name, _category_icon) in enumerate(expense_categories):
                amount = monthly_data[month_name].get(category_id, 0.0)

                item = QStandardItem(f"{amount:.2f}")
                # Set background color for this category
                item.setBackground(QBrush(category_colors[idx]))
                item.setData(amount, Qt.ItemDataRole.UserRole)
                row_items.append(item)

            model.appendRow(row_items)

        self.tableView_reports.setModel(model)

        # Disable editing for reports table
        self.tableView_reports.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView_reports.setSortingEnabled(True)
        self.tableView_reports.sortByColumn(0, Qt.SortOrder.DescendingOrder)
        model.setSortRole(Qt.ItemDataRole.UserRole)

        # Set up amount delegates for all monetary columns (Total and all categories)
        # Column 0 is Month (no delegate needed)
        # Column 1 is Total (bold font)
        # Column 2 is Cafe + Food (bold font)
        # Columns 3+ are categories (normal font)

        # Total column (bold)
        total_delegate = ReportAmountDelegate(self.tableView_reports, is_bold=True)
        self.tableView_reports.setItemDelegateForColumn(1, total_delegate)

        # Cafe + Food combined column (bold)
        combined_delegate = ReportAmountDelegate(self.tableView_reports, is_bold=True)
        self.tableView_reports.setItemDelegateForColumn(2, combined_delegate)

        # Category columns (normal font)
        for col_idx in range(3, model.columnCount()):
            category_delegate = ReportAmountDelegate(self.tableView_reports, is_bold=False)
            self.tableView_reports.setItemDelegateForColumn(col_idx, category_delegate)

        # Configure columns - allow manual resizing by user
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            # Set interactive mode to allow user to resize columns manually
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Interactive)

            # Optionally resize columns to content initially, but allow manual resizing after
            self.tableView_reports.resizeColumnsToContents()

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

    def _init_chart_controls(self) -> None:
        """Initialize chart controls."""
        current_date: QDate = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)

    def _init_database(self) -> None:
        """Initialize database connection."""
        filename: Path = Path(config["sqlite_finance"])

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
        current_date: QDate = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)
        self.checkBox_use_date_filter.setChecked(False)

    def _initial_load(self) -> None:
        """Load essential data at startup (excluding exchange rates)."""
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
        self.tableView_accounts.setModel(self.models["accounts"])

        # Set up amount delegate for the Balance column (index 1)
        self.accounts_balance_delegate = AmountDelegate(self.tableView_accounts, self.db_manager)
        self.tableView_accounts.setItemDelegateForColumn(1, self.accounts_balance_delegate)

        # Make accounts table non-editable and connect double-click signal
        self.tableView_accounts.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        # Reconnect double-click signal only when previously connected
        if self._account_double_click_connected:
            try:
                self.tableView_accounts.doubleClicked.disconnect(self._on_account_double_clicked)
            except (TypeError, RuntimeError):
                pass
            self._account_double_click_connected = False

        self.tableView_accounts.doubleClicked.connect(self._on_account_double_clicked)
        self._account_double_click_connected = True

        # Configure column stretching for accounts table
        accounts_header = self.tableView_accounts.horizontalHeader()
        if accounts_header.count() > 0:
            for i in range(accounts_header.count()):
                accounts_header.setSectionResizeMode(i, accounts_header.ResizeMode.Stretch)
            # Ensure stretch settings are applied
            accounts_header.setStretchLastSection(False)

    def _load_categories_table(self) -> None:
        """Load categories table."""
        categories_data: list = self.db_manager.get_all_categories()
        categories_transformed_data: list[list] = []
        for row in categories_data:
            # Transform: [id, name, type, icon] -> [name, type_str, icon, id, color]
            type_str: str = "Expense" if row[2] == 0 else "Income"
            color: QColor = QColor(255, 200, 200) if row[2] == 0 else QColor(200, 255, 200)
            transformed_row: list = [row[1], type_str, row[3], row[0], color]
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
        currencies_data: list = self.db_manager.get_all_currencies()
        currencies_transformed_data: list[list] = []
        for row in currencies_data:
            # Transform: [id, code, name, symbol] -> [code, name, symbol, id, color]
            color: QColor = QColor(255, 255, 220)
            transformed_row: list = [row[1], row[2], row[3], row[0], color]
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
        self.tableView_exchange.setModel(self.models["currency_exchanges"])

        # Disable all editing triggers
        self.tableView_exchange.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

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

            # Connect auto-save signals for loaded tables
            self._connect_table_auto_save_signals()

            # Update accounts balance display
            self._update_accounts_balance_display()

        except Exception as e:
            print(f"Error loading essential tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load essential tables: {e}")

    def _load_transactions_table(self) -> None:
        """Load transactions table."""
        limit: int | None = None if self.show_all_transactions else self.count_transactions_to_show
        transactions_data: list = self.db_manager.get_all_transactions(limit=limit)
        transactions_transformed_data: list[list] = self._transform_transaction_data(transactions_data)
        self.models["transactions"] = self._create_transactions_table_model(
            transactions_transformed_data, self.table_config["transactions"][2]
        )
        self.tableView_transactions.setModel(self.models["transactions"])

        # Set up description delegate for the Description column (index 0)
        self.description_delegate = DescriptionDelegate(self.tableView_transactions)
        self.tableView_transactions.setItemDelegateForColumn(0, self.description_delegate)

        # Set up category delegate for the Category column (index 2)
        categories: list[str] = self._get_categories_for_delegate()
        self.category_delegate = CategoryComboBoxDelegate(self.tableView_transactions, categories)
        self.tableView_transactions.setItemDelegateForColumn(2, self.category_delegate)

        # Set up currency delegate for the Currency column (index 3)
        currencies: list[str] = self._get_currencies_for_delegate()
        self.currency_delegate = CurrencyComboBoxDelegate(self.tableView_transactions, currencies)
        self.tableView_transactions.setItemDelegateForColumn(3, self.currency_delegate)

        # Set up date delegate for the Date column (index 4)
        self.date_delegate = DateDelegate(self.tableView_transactions)
        self.tableView_transactions.setItemDelegateForColumn(4, self.date_delegate)

        # Set up tag delegate for the Tag column (index 5)
        tags: list[str] = self._get_tags_for_delegate()
        self.tag_delegate = TagDelegate(self.tableView_transactions, tags)
        self.tableView_transactions.setItemDelegateForColumn(5, self.tag_delegate)

        # Set up amount delegate for the Amount column (index 1)
        self.amount_delegate = AmountDelegate(self.tableView_transactions, self.db_manager)
        self.tableView_transactions.setItemDelegateForColumn(1, self.amount_delegate)

        # Set up amount delegate for the Total per day column (index 6)
        self.total_per_day_delegate = AmountDelegate(self.tableView_transactions, self.db_manager)
        self.tableView_transactions.setItemDelegateForColumn(6, self.total_per_day_delegate)

        # Enable editing for the Category and Amount columns
        self.tableView_transactions.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)

        # Connect selection signal for transactions table to copy data to form fields
        # This must be done after the model is set
        self.tableView_transactions.selectionModel().currentChanged.connect(self._on_transaction_selection_changed)

        # Special handling for transactions table - column stretching setup
        header = self.tableView_transactions.horizontalHeader()
        if header.count() > 0:
            # Set stretch mode for all columns except the last two
            for i in range(header.count() - 2):
                header.setSectionResizeMode(i, header.ResizeMode.Stretch)

            # For the second-to-last column (Tag) set fixed width
            second_last_column: int = header.count() - 2
            header.setSectionResizeMode(second_last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(second_last_column, 100)

            # For the last column (Total per day) set fixed width
            last_column: int = header.count() - 1
            header.setSectionResizeMode(last_column, header.ResizeMode.Fixed)
            self.tableView_transactions.setColumnWidth(last_column, 120)

    def _mark_categories_changed(self) -> None:
        """Mark that category data has changed and needs refresh."""
        # No specific action needed for categories as they load immediately

    def _mark_currencies_changed(self) -> None:
        """Mark that currency data has changed and needs refresh."""
        # No specific action needed for currencies as they load immediately

    def _mark_default_currency_changed(self) -> None:
        """Mark that default currency has changed and needs refresh."""
        # No specific action needed as this affects multiple areas that reload immediately

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
            if source_model is None:
                return

            row_id_item = source_model.verticalHeaderItem(index.row())
            if row_id_item is None:
                return

            account_id: int = int(row_id_item.text())

            # Get account data
            account_data = self.db_manager.get_account_by_id(account_id)
            if not account_data:
                QMessageBox.warning(self, "Error", "Account not found")
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
                        QMessageBox.warning(self, "Error", "Currency not found")
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
                    QMessageBox.warning(self, "Error", "Failed to update account")

                elif result["action"] == "delete":
                    # Save current column widths before update
                    column_widths: list[int] = self._save_table_column_widths(self.tableView_accounts)

                    # Delete account
                    success: bool = self.db_manager.delete_account(account_id)
                    if success:
                        self.update_all()

                        # Restore column widths after update
                        self._restore_table_column_widths(self.tableView_accounts, column_widths)

                        QMessageBox.information(self, "Success", "Account deleted successfully")
                        return  # Exit the method to prevent reopening the dialog
                    QMessageBox.warning(self, "Error", "Failed to delete account")
            elif result_code == QDialog.DialogCode.Rejected:
                # Dialog was cancelled, do nothing and return
                return

        except Exception as e:
            self._account_edit_dialog_open = False
            QMessageBox.warning(self, "Error", f"Failed to edit account: {e}")

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

    def _on_check_completed(self, currencies_to_process: list) -> None:
        """Handle successful completion of exchange rate check.

        Args:

        - `currencies_to_process` (`list`): List of currencies that need processing.

        """
        if hasattr(self, "check_progress_dialog"):
            self.check_progress_dialog.close()

        # If no currencies need processing, inform user
        if not currencies_to_process:
            QMessageBox.information(
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
        reply = QMessageBox.question(
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

        QMessageBox.critical(self, "Check Failed", f"Failed to check exchange rates:\n{error_message}")
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
            QMessageBox.warning(self, "Error", "Failed to parse exchange values")
            return

        # Get currencies list
        currencies = self.comboBox_exchange_from.allItems() if hasattr(self.comboBox_exchange_from, "allItems") else []
        if not currencies:
            # Fallback: get currencies from combobox
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
                    QMessageBox.warning(self, "Error", "Failed to update exchange record")
        finally:
            # Reset flag when dialog is closed
            self._exchange_dialog_open = False

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
        """Handle error completion of startup update.

        Args:

        - `error_message` (`str`): The error message.

        """
        print(f"❌ [Startup] Update failed: {error_message}")

        if hasattr(self, "startup_progress_dialog"):
            self.startup_progress_dialog.setText(f"❌ Update failed:\n{error_message}")
            # Auto-close after 4 seconds
            QTimer.singleShot(4000, self._cleanup_startup_dialog)
        else:
            self._cleanup_startup_dialog()

    def _on_startup_update_finished_success(self, processed_count: int, total_operations: int) -> None:
        """Handle successful completion of startup update.

        Args:

        - `processed_count` (`int`): Number of successfully processed operations.
        - `total_operations` (`int`): Total number of operations.

        """
        if processed_count > 0:
            # Determine the strategy for logging
            has_exchange_rates: bool = (
                self.db_manager.has_exchange_rates_data() if self.db_manager else True
            )  # True because we just added data
            strategy: str = "from last exchange rate date" if has_exchange_rates else "from first transaction date"

            print(
                "✅ [Startup] Successfully processed "
                f"{processed_count} out of {total_operations} "
                f"exchange rate operations ({strategy})"
            )

            # Update dialog with success message
            if hasattr(self, "startup_progress_dialog"):
                self.startup_progress_dialog.setText(
                    f"✅ Exchange rates updated successfully!\n"
                    f"Processed {processed_count} out of {total_operations} operations\n"
                    f"Strategy: {strategy}"
                )
                # Auto-close after 2 seconds
                QTimer.singleShot(2000, self._cleanup_startup_dialog)
            else:
                self._cleanup_startup_dialog()

            # Mark exchange rates as changed to trigger reload if tab is active
            self._mark_exchange_rates_changed()
            # If exchange rates tab is currently active, reload the data
            current_tab_index: int = self.tabWidget.currentIndex()
            id_exchange_rates_tab = 4
            if current_tab_index == id_exchange_rates_tab:  # Exchange Rates tab
                self.load_exchange_rates_table()
        else:
            print("ℹ️ [Startup] No exchange rate records were processed")  # noqa: RUF001

            if hasattr(self, "startup_progress_dialog"):
                self.startup_progress_dialog.setText("ℹ️ No exchange rate records were processed")  # noqa: RUF001
                # Auto-close after 2 seconds
                QTimer.singleShot(2000, self._cleanup_startup_dialog)
            else:
                self._cleanup_startup_dialog()

    def _on_table_data_changed(
        self, table_name: str, top_left: QModelIndex, bottom_right: QModelIndex, _roles: list | None = None
    ) -> None:
        """Handle data changes in table models and auto-save to database."""
        if table_name not in self._SAFE_TABLES:
            return

        if not self._validate_database_connection():
            return

        try:
            print(f"🔄 Data changed in table: {table_name}, rows: {top_left.row()}-{bottom_right.row()}")  # Add logging

            proxy_model: QSortFilterProxyModel | None = self.models[table_name]
            if proxy_model is None:
                print(f"❌ Proxy model is None for table {table_name}")  # Add logging
                return
            model = proxy_model.sourceModel()
            if not isinstance(model, QStandardItemModel):
                print(f"❌ Source model is not QStandardItemModel for table {table_name}")  # Add logging
                return

            # Process each changed row
            for row in range(top_left.row(), bottom_right.row() + 1):
                if row >= model.rowCount():
                    continue

                vertical_header_item = model.verticalHeaderItem(row)
                if vertical_header_item:
                    row_id: str = vertical_header_item.text()
                    print(f"🔄 Processing row {row}, ID: {row_id}")  # Add logging
                    self._auto_save_row(table_name, model, row, row_id)

        except Exception as e:
            error_msg = f"Failed to auto-save changes: {e!s}"
            print(f"❌ {error_msg}")  # Add logging
            QMessageBox.warning(self, "Auto-save Error", error_msg)

    def _on_transaction_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle transaction selection change and copy data to form fields.

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
            if source_model is None:
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
            tag: str = transaction_data[6]

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

            # Set tag if exists
            if tag:
                self.lineEdit_tag.setText(tag)

        except Exception as e:
            print(f"Error copying transaction data to form: {e}")

    def _on_update_finished_error(self, error_message: str) -> None:
        """Handle error completion.

        Args:

        - `error_message` (`str`): The error message.

        """
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        QMessageBox.critical(self, "Update Error", f"Failed to update exchange rates:\n{error_message}")
        print(f"❌ {error_message}")

    def _on_update_finished_success(self, processed_count: int, total_operations: int) -> None:
        """Handle successful completion.

        Args:

        - `processed_count` (`int`): Number of successfully processed operations.
        - `total_operations` (`int`): Total number of operations.

        """
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()

        if processed_count > 0:
            message: str = (
                "Successfully completed exchange rate update:\n"
                f"• Processed {processed_count} out of {total_operations} operations from yfinance"
            )
            QMessageBox.information(self, "Update Complete", message)

            # Mark exchange rates as changed to trigger reload if tab is active
            self._mark_exchange_rates_changed()
            # If exchange rates tab is currently active, reload the data
            current_tab_index: int = self.tabWidget.currentIndex()
            id_exchange_rates_tab = 4
            if current_tab_index == id_exchange_rates_tab:  # Exchange Rates tab
                self.load_exchange_rates_table()
        else:
            QMessageBox.information(
                self,
                "Update Complete",
                "No exchange rate records were processed.",
            )

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
                SELECT t.amount, cat.name, c.code, t.tag
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
                tag: str
                amount_cents, category_name, currency_code, tag = rows[0]

                # Populate form fields
                amount: float = float(amount_cents) / 100  # Convert from cents
                self.doubleSpinBox_amount.setValue(amount)
                self.lineEdit_tag.setText(tag or "")

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

    def _process_text_input(self, text: str) -> None:
        """Process text input and add purchases to database.

        Args:

        - `text` (`str`): Text input to process.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Create parser and parse text
        parser: TextParser = TextParser()
        parsed_items: list = parser.parse_text(text)

        if not parsed_items:
            QMessageBox.information(self, "No Items", "No valid purchase items found in the text.")
            return

        # Get date from dateEdit
        purchase_date: str = self.dateEdit.date().toString("yyyy-MM-dd")

        # Get default currency ID
        default_currency: str | None = self.db_manager.get_default_currency()
        if not default_currency:
            QMessageBox.warning(self, "Error", "No default currency set")
            return

        default_currency_id: int = self.db_manager.get_currency_by_code(default_currency)[0]

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
            QMessageBox.warning(self, "Results", error_text)
        else:
            QMessageBox.information(self, "Success", f"Successfully added {success_count} purchases.")

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

    def _set_date_from_table(self, date_value: str) -> None:
        """Set the date from table row to the main dateEdit field.

        Args:

        - `date_value` (`str`): Date string from the table (format: yyyy-MM-dd).

        """
        try:
            # Parse the date string and set it in dateEdit
            date_obj: QDate = QDate.fromString(date_value, "yyyy-MM-dd")
            if date_obj.isValid():
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
            if date_obj.isValid():
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
            if date_obj.isValid():
                new_date: QDate = date_obj.addDays(1)
                self.dateEdit.setDate(new_date)
            else:
                print(f"❌ Invalid date format: {date_value}")
        except Exception as e:
            print(f"❌ Error setting date from table + 1 day: {e}")

    def _set_today_date_in_main(self) -> None:
        """Set today's date in the main date field."""
        today: QDate = QDate.currentDate()
        self.dateEdit.setDate(today)

    def _setup_autocomplete(self) -> None:
        """Set up autocomplete functionality for description input."""
        # Create completer
        self.description_completer: QCompleter = QCompleter(self)
        self.description_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.description_completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Search by content
        self.description_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        # Create model for completer
        self.description_completer_model: QStringListModel = QStringListModel(self)
        self.description_completer.setModel(self.description_completer_model)

        # Set completer to the line edit
        self.lineEdit_description.setCompleter(self.description_completer)

        # Update autocomplete data
        self._update_autocomplete_data()

        # Connect selection signal
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

    def _setup_ui(self) -> None:
        """Set up additional UI elements."""
        # Set emoji for buttons
        self.pushButton_yesterday.setText(f"📅 {self.pushButton_yesterday.text()}")
        self.pushButton_add.setText(f"➕ {self.pushButton_add.text()}")  # noqa: RUF001
        self.pushButton_add_as_text.setText(f"📝 {self.pushButton_add_as_text.text()}")
        self.pushButton_delete.setText(f"🗑️ {self.pushButton_delete.text()}")
        self.pushButton_refresh.setText(f"🔄 {self.pushButton_refresh.text()}")
        self.pushButton_clear_filter.setText(f"🧹 {self.pushButton_clear_filter.text()}")
        self.pushButton_apply_filter.setText(f"✔️ {self.pushButton_apply_filter.text()}")
        self.pushButton_description_clear.setText("🧹")
        self.pushButton_show_all_records.setText("📊 Show All Records")

        # Set emoji for exchange rate buttons
        self.pushButton_exchange_update.setText(f"🔄 {self.pushButton_exchange_update.text()}")
        self.pushButton_rates_delete.setText(f"🗑️ {self.pushButton_rates_delete.text()}")
        self.pushButton_exchange_item_update.setText(f"✏️ {self.pushButton_exchange_item_update.text()}")
        self.pushButton_filter_exchange_rates_clear.setText(f"🧹 {self.pushButton_filter_exchange_rates_clear.text()}")
        self.pushButton_filter_exchange_rates_apply.setText(f"✔️ {self.pushButton_filter_exchange_rates_apply.text()}")
        self.pushButton_exchange_rates_last_month.setText(f"📅 {self.pushButton_exchange_rates_last_month.text()}")
        self.pushButton_exchange_rates_last_year.setText(f"📅 {self.pushButton_exchange_rates_last_year.text()}")
        self.pushButton_exchange_rates_all_time.setText(f"📊 {self.pushButton_exchange_rates_all_time.text()}")

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

        # Connect double-click signal for exchange table
        self.tableView_exchange.doubleClicked.connect(self._on_exchange_table_double_clicked)

        # Enable category selection via label context menu
        self.label_category_now.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.label_category_now.customContextMenuRequested.connect(self._show_category_label_context_menu)
        self.label_category_now.installEventFilter(self)

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

    def _setup_window_size_and_position(self) -> None:
        """Set window size and position based on screen resolution and characteristics."""
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width: int = screen_geometry.width()
        screen_height: int = screen_geometry.height()

        # Determine window size and position based on screen characteristics
        aspect_ratio: float = screen_width / screen_height
        standard_width = 1920
        standard_aspect_ratio = 2.0
        is_standard_aspect: bool = aspect_ratio <= standard_aspect_ratio  # Standard aspect ratio (16:9, 16:10, etc.)

        if is_standard_aspect and screen_width >= standard_width:
            # For standard aspect ratios with width >= 1920, maximize window
            self.showMaximized()
        else:
            title_bar_height: int = 30  # Approximate title bar height
            windows_task_bar_height: int = 48  # Approximate windows task bar height
            # For other cases, use fixed width and full height minus title bar
            window_width: int = standard_width
            window_height: int = screen_height - title_bar_height - windows_task_bar_height
            # Position window on screen
            screen_center = screen_geometry.center()
            # Center horizontally, position at top vertically with title bar offset
            self.setGeometry(
                screen_center.x() - window_width // 2,
                title_bar_height,  # Position below title bar
                window_width,
                window_height,
            )

    def _show_no_data_label(self, layout: QLayout, message: str) -> None:
        """Show a message when no data is available for the chart.

        Args:

        - `layout` (`QLayout`): The layout to add the message to.
        - `message` (`str`): The message to display.

        """
        # Clear existing content
        self._clear_layout(layout)

        # Create and add label
        label: QLabel = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #666; padding: 20px;")
        layout.addWidget(label)

    def _show_category_label_context_menu(self, position: QPoint) -> None:
        """Show context menu on the category label with all available categories."""
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

        selected_action = context_menu.exec(self.label_category_now.mapToGlobal(position))
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

    def _show_transactions_context_menu(self, position: QPoint) -> None:
        """Show context menu for transactions table.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        context_menu: QMenu = QMenu(self)

        # Get the clicked index
        index: QModelIndex = self.tableView_transactions.indexAt(position)
        if index.isValid():
            # Get the date from the Date column (index 4)
            date_index: QModelIndex = self.tableView_transactions.model().index(index.row(), 4)
            if date_index.isValid():
                date_value: str = self.tableView_transactions.model().data(date_index)
                if date_value:
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

        # Delete action
        delete_action = context_menu.addAction("🗑 Delete selected row")

        export_action = context_menu.addAction("📤 Export to CSV")

        action = context_menu.exec(self.tableView_transactions.mapToGlobal(position))

        if action == export_action:
            self.on_export_csv()
        elif action == delete_action:
            print("🔧 Context menu: Delete action triggered")
            # Perform the deletion
            self.delete_record("transactions")
        elif (
            ("set_date_action" in locals() and action == set_date_action)
            or ("set_date_plus_one_action" in locals() and action == set_date_plus_one_action)
            or ("set_date_minus_one_action" in locals() and action == set_date_minus_one_action)
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
        context_menu.exec(self.pushButton_yesterday.mapToGlobal(position))

    def _subtract_one_day_from_main(self) -> None:
        """Subtract one day from the current date in main date field."""
        current_date: QDate = self.dateEdit.date()
        new_date: QDate = current_date.addDays(-1)
        self.dateEdit.setDate(new_date)

    def _transform_transaction_data(self, rows: list[list]) -> list[list]:
        """Transform transaction data for display with colors and daily totals.

        Args:

        - `rows` (`list[list]`): Raw transaction data.

        Returns:

        - `list[list]`: Transformed data with colors and daily totals.

        """
        transformed_data: list[list] = []

        # Calculate daily expenses
        daily_expenses: dict[str, float] = self._calculate_daily_expenses(rows)

        # Create a mapping of dates to color indices
        date_to_color_index: dict[str, int] = {}
        color_index: int = 0

        # Track which dates we've already shown totals for
        dates_with_totals: set[str] = set()

        for row in rows:
            transaction_id: int = row[0]
            amount_cents: int = row[1]
            description: str = row[2]
            category_name: str = row[3]
            currency_code: str = row[4]
            date: str = row[5]
            tag: str = row[6]
            category_type: int = row[7]
            icon: str = row[8]  # category icon

            # Convert amount from minor units to display format using currency subdivision
            amount: float
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

            color: QColor = self.date_colors[date_to_color_index[date]]

            # Add emoji prefix and "(Income)" suffix for income categories
            display_category_name: str = category_name
            if icon:
                display_category_name = f"{icon} {category_name}"
            if category_type == 1:  # Income category
                display_category_name = f"{display_category_name} (Income)"

            # Determine if this is the first transaction for this date
            is_first_of_day: bool = date not in dates_with_totals
            if is_first_of_day:
                dates_with_totals.add(date)

            # Get daily total for this date
            daily_total: float = daily_expenses.get(date, 0.0)
            total_display: str = f"-{daily_total:.2f}" if is_first_of_day and daily_total > 0 else ""

            # Format amount with minus sign for expenses
            amount_display: str = f"-{amount:.2f}" if category_type == 0 else f"{amount:.2f}"

            transformed_row: list = [
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
            # Get recent transaction descriptions for autocomplete
            recent_descriptions: list[str] = self.db_manager.get_recent_transaction_descriptions_for_autocomplete(1000)

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

            # Reset category selection label
            self.label_category_now.setText("No category selected")

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
    app: QApplication = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))
    win: MainWindow = MainWindow()
    win.tabWidget.setCurrentIndex(0)
    sys.exit(app.exec())
