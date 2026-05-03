"""Finance tracker GUI.

This module contains a single `MainWindow` class that provides a Qt-based GUI for a
SQLite database with transactions, categories, accounts, currencies and exchange rates.
"""

from __future__ import annotations

import contextlib
import gc
import re
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

import harrix_pylib as h
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import (
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
from PySide6.QtGui import (
    QBrush,
    QCloseEvent,
    QColor,
    QCursor,
    QIcon,
    QKeyEvent,
    QMouseEvent,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCompleter,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLayout,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import resources_rc  # noqa: F401
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.app_entry import run_app_main
from harrix_swiss_knife.apps.common.chart_colors import generate_pastel_qcolors
from harrix_swiss_knife.apps.common.qt_main_window import AppWindowMixin
from harrix_swiss_knife.apps.common.table_models import create_table_proxy_model
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
from harrix_swiss_knife.apps.finance.exchange_validation import validate_exchange_data
from harrix_swiss_knife.apps.finance.mixins import (
    AutoSaveOperations,
    ChartOperations,
    DateOperations,
    TableOperations,
    ValidationOperations,
    requires_database,
)
from harrix_swiss_knife.apps.finance.report_generators import (
    get_account_balances_report_data,
    get_category_analysis_report_data,
    get_currency_analysis_report_data,
    get_income_vs_expenses_report_data,
    get_monthly_summary_report_data,
)
from harrix_swiss_knife.apps.finance.services.account_balance import format_total_accounts_balance_details
from harrix_swiss_knife.apps.finance.text_input_dialog import TextInputDialog
from harrix_swiss_knife.apps.finance.text_parser import TextParser
from harrix_swiss_knife.apps.finance.transaction_helpers import calculate_daily_expenses as calc_daily_expenses
from harrix_swiss_knife.apps.finance.transaction_helpers import calculate_exchange_loss as calc_exchange_loss
from harrix_swiss_knife.apps.finance.transaction_helpers import (
    calculate_exchange_loss_in_source_currency as calc_exchange_loss_source,
)
from harrix_swiss_knife.apps.finance.transaction_helpers import convert_currency_amount as convert_currency
from harrix_swiss_knife.apps.finance.transaction_helpers import (
    get_accounting_balance_latest_rates,
    get_balance_difference,
    get_natural_currency_reconciliation,
    get_transaction_money_op_value,
)
from harrix_swiss_knife.apps.finance.transaction_helpers import (
    transform_transaction_data as transform_transaction_data_helper,
)
from harrix_swiss_knife.apps.finance.widgets import ClickableCategoryLabel
from harrix_swiss_knife.paths import get_config_path_str


class MainWindow(
    QMainWindow,
    window.Ui_MainWindow,
    AppWindowMixin,
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
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())

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
        self.date_colors: list[QColor] = generate_pastel_qcolors(50)

        # Initialize mouse button tracking
        self._right_click_in_progress: bool = False

        # Hover-delay timer for category dropdown on label_category_now
        self._category_label_hover_delay_ms: int = 800
        self._category_label_hover_menu_pos: QPoint = QPoint(0, 0)
        self._category_label_hover_timer: QTimer = QTimer(self)
        self._category_label_hover_timer.setSingleShot(True)
        self._category_label_hover_timer.timeout.connect(self._on_category_label_hover_timeout)

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

        category: str | None = self.comboBox_filter_category.currentText() or None
        currency: str | None = self.comboBox_filter_currency.currentText() or None
        description_filter: str | None = self.lineEdit_filter_description.text().strip() or None

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
        """Delete selected row(s) from table using database manager methods.

        For ``transactions``, deletes every selected row; other tables delete one row.

        Args:

        - `table_name` (`str`): Name of the table to delete from. Must be in _SAFE_TABLES.

        Raises:

        - `ValueError`: If table_name is not in _SAFE_TABLES.

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

        # Show category menu on hover with delay (mouse enter) over label_category_now
        if obj == self.label_category_now and event.type() == QEvent.Type.Enter:
            if self.label_category_now is not None:
                self._category_label_hover_menu_pos = QPoint(0, self.label_category_now.height())
            self._category_label_hover_timer.start(self._category_label_hover_delay_ms)
            return True

        if obj == self.label_category_now and event.type() == QEvent.Type.Leave:
            if self._category_label_hover_timer.isActive():
                self._category_label_hover_timer.stop()
            return False

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
    def on_add_as_text(self) -> None:
        """Open text input dialog and process entered purchases."""
        # Get date from dateEdit to use as default in dialog
        default_date: QDate = self.dateEdit.date()

        # Create and show the text input dialog
        dialog: TextInputDialog = TextInputDialog(self, default_date=default_date)
        result: int = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            text: str | None = dialog.get_text()
            date: str | None = dialog.get_date()
            if text and date:
                self._process_text_input(text, date)

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
            _amount, _desc, cat_id, _curr_id, _date, _tag = data
            current_date = self.dateEdit.date()
            self._mark_transactions_changed()
            self.update_all()
            self.update_summary_labels()
            self._update_autocomplete_data()
            self.doubleSpinBox_amount.setValue(100.0)
            self.lineEdit_description.clear()
            self.lineEdit_tag.clear()
            self.dateEdit.setDate(current_date)
            QTimer.singleShot(100, self._focus_description_and_select_text)
            self._select_category_by_id(cat_id)

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
                if hasattr(self.db_manager, "_exchange_rate_cache"):
                    self.db_manager._exchange_rate_cache.clear()  # noqa: SLF001
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
            message_box.warning(self, "Report Error", f"Failed to generate report: {e}")

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
                self.update_chart_comboboxes()
                id_charts_tab: int = 6
                if self.tabWidget.currentIndex() == id_charts_tab:
                    self.update_charts()
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
            layout = self.scrollAreaWidgetContents_charts.layout()
            if layout is not None:
                self._show_no_data_label(layout, "No data found for balance chart")
            return

        # Calculate running balance
        balance: float = 0.0
        balance_data: list[tuple[datetime, float]] = []

        for date_str, _amount in rows:
            trans_rows = self.db_manager.get_filtered_transactions(date_from=date_str, date_to=date_str)
            daily_balance = sum(
                get_transaction_money_op_value(trans_row, self.db_manager, default_currency_id)
                for trans_row in trans_rows
                if trans_row[5] == date_str
            )
            balance += daily_balance
            date_obj: datetime = datetime.fromisoformat(date_str).replace(tzinfo=UTC)
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

        layout = self.scrollAreaWidgetContents_charts.layout()
        if layout is not None:
            self._create_chart(layout, balance_data, chart_config)

    @requires_database()
    def show_pie_chart(self) -> None:
        """Show pie chart of expenses by category."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get default currency (for chart title)
        default_currency_code: str = self.db_manager.get_default_currency()

        # Get date range
        date_from: str = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to: str = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Get expense transactions with money op in default currency (one query, no per-row conversion)
        expense_rows: list = self.db_manager.get_transactions_with_money_op_in_currency(
            target_currency_id=None,
            category_type=0,
            date_from=date_from,
            date_to=date_to,
        )

        if not expense_rows:
            charts_layout = self.scrollAreaWidgetContents_charts.layout()
            if charts_layout is not None:
                self._show_no_data_label(charts_layout, "No expense data found for pie chart")
            return

        # Group by category; row[10] is money_op_major (negative for expenses, sum absolute for display)
        category_totals: dict[str, float] = {}
        for row in expense_rows:
            category_name = row[3]
            amount_in_currency: float = abs(float(row[10]))
            if category_name in category_totals:
                category_totals[category_name] += amount_in_currency
            else:
                category_totals[category_name] = amount_in_currency

        # Create pie chart
        self._create_pie_chart(category_totals, f"Expenses by Category ({default_currency_code})")

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
            charts_layout = self.scrollAreaWidgetContents_charts.layout()
            if charts_layout is not None:
                self._show_no_data_label(charts_layout, "No data found for the selected period")
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

        layout = self.scrollAreaWidgetContents_charts.layout()
        if layout is not None:
            self._create_chart(layout, chart_data, chart_config)

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
            today: str = datetime.now(UTC).astimezone().date().strftime("%Y-%m-%d")

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
                self._show_error("Error", f"Failed to add {entity_name}")
        except Exception as e:
            self._show_db_error(f"Failed to add {entity_name}: {e}")

    def _calculate_daily_expenses(self, rows: list[list]) -> dict[str, float]:
        """Calculate daily expenses from transaction data.

        Args:

        - `rows` (`list[list]`): Raw transaction data from database.

        Returns:

        - `dict[str, float]`: Dictionary mapping dates to total expenses for that day.

        """
        return calc_daily_expenses(rows, self.db_manager)

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
        return calc_exchange_loss_source(amount_from, amount_to, rate_to_per_from, fee)

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
        self.pushButton_balance_check.clicked.connect(self._on_balance_check_clicked)
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
        return convert_currency(amount, from_currency_id, to_currency_id, self.db_manager, date)

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
        layout = self.scrollAreaWidgetContents_charts.layout()
        if layout is not None:
            self._clear_layout(layout)

        if not data:
            layout = self.scrollAreaWidgetContents_charts.layout()
            if layout is not None:
                self._show_no_data_label(layout, "No data for pie chart")
            return

        # Create matplotlib figure
        fig: Figure = Figure(figsize=(10, 8), dpi=100)
        canvas: FigureCanvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Prepare data for pie chart
        labels: list[str] = list(data.keys())
        sizes: list[float] = list(data.values())

        # Create pie chart
        pie_result = ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        _wedges, _texts, *autotexts = pie_result
        autotexts = autotexts[0] if autotexts else []

        # Customize appearance
        ax.set_title(title, fontsize=14, fontweight="bold")

        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        fig.tight_layout()
        layout = self.scrollAreaWidgetContents_charts.layout()
        if layout is not None:
            layout.addWidget(canvas)
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
        headers, report_data = get_account_balances_report_data(self.db_manager, currency_id)
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

    def _generate_category_analysis_report(self, _currency_id: int) -> None:
        """Generate category analysis report.

        Args:

        - `_currency_id` (`int`): Currency ID for conversion.

        """
        headers, report_data = get_category_analysis_report_data(self.db_manager)
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

    def _generate_currency_analysis_report(self) -> None:
        """Generate currency analysis report."""
        headers, report_data = get_currency_analysis_report_data(self.db_manager)
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            model.appendRow(items)
        self._set_reports_model_and_stretch(model)

    def _generate_income_vs_expenses_report(self, currency_id: int) -> None:
        """Generate income vs expenses report.

        Args:

        - `currency_id` (`int`): Currency ID for conversion.

        """
        headers, report_data = get_income_vs_expenses_report_data(self.db_manager, currency_id)
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

    def _generate_monthly_summary_report(self, currency_id: int) -> None:
        """Generate monthly summary report showing expenses by category per month.

        Args:

        - `currency_id` (`int`): Currency ID for conversion.

        """
        headers, rows, expense_categories, _ = get_monthly_summary_report_data(self.db_manager, currency_id)
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
        filename: Path = Path(self._app_config["sqlite_finance"])

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

        # Recompute natural reconciliation in-place, disable button if diff became zero.
        refreshed_tx = self.db_manager.get_all_transactions()
        refreshed_ex = self.db_manager.get_all_currency_exchanges()
        refreshed_accounts = self.db_manager.get_all_accounts()
        refreshed_natural = get_natural_currency_reconciliation(
            refreshed_tx, refreshed_ex, refreshed_accounts, self.db_manager
        )
        self._refresh_test_balance_table(table, refreshed_natural)

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
        try:
            transaction_rows: list = self.db_manager.get_all_transactions()
            exchange_rows: list = self.db_manager.get_all_currency_exchanges()
            accounts_rows: list = self.db_manager.get_all_accounts()
            accounting_balance: float
            accounts_balance: float
            difference: float
            accounting_balance, accounts_balance, difference = get_balance_difference(
                transaction_rows, exchange_rows, self.db_manager, target_currency_id=None
            )
            accounting_balance_latest = get_accounting_balance_latest_rates(
                transaction_rows, exchange_rows, self.db_manager, target_currency_id=None
            )
            difference_latest = accounts_balance - accounting_balance_latest
            natural_rows = get_natural_currency_reconciliation(
                transaction_rows, exchange_rows, accounts_rows, self.db_manager
            )
            default_currency_code: str = self.db_manager.get_default_currency()
            default_currency_info = self.db_manager.get_currency_by_code(default_currency_code)
            symbol: str = default_currency_info[2] if default_currency_info else ""
            self._show_test_balance_dialog(
                default_currency_symbol=symbol,
                accounts_balance=accounts_balance,
                accounting_balance_latest=accounting_balance_latest,
                difference_latest=difference_latest,
                accounting_balance_historical=accounting_balance,
                difference_historical=difference,
                natural_rows=natural_rows,
            )
        except Exception as e:
            print(f"Error in test balance: {e}")
            message_box.warning(self, "Error", f"Error: {e!s}")

    def _on_category_label_hover_timeout(self) -> None:
        """Open category menu only if the cursor still hovers label."""
        if self.label_category_now is None:
            return
        if not self.label_category_now.underMouse():
            return
        self._show_category_label_context_menu(self._category_label_hover_menu_pos, from_hover=True)

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
        """Handle error completion of startup update."""
        self._on_exchange_update_finished_error(error_message, startup=True)

    def _on_startup_update_finished_success(self, processed_count: int, total_operations: int) -> None:
        """Handle successful completion of startup update."""
        self._on_exchange_update_finished_success(processed_count, total_operations, startup=True)

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
            message_box.warning(self, "Auto-save Error", error_msg)

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
        """Handle error completion."""
        self._on_exchange_update_finished_error(error_message, startup=False)

    def _on_update_finished_success(self, processed_count: int, total_operations: int) -> None:
        """Handle successful completion."""
        self._on_exchange_update_finished_success(processed_count, total_operations, startup=False)

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

    def _process_text_input(self, text: str, purchase_date: str) -> None:
        """Process text input and add purchases to database.

        Args:

        - `text` (`str`): Text input to process.
        - `purchase_date` (`str`): Date for purchases in yyyy-MM-dd format.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Create parser and parse text
        parser: TextParser = TextParser()
        parsed_items: list = parser.parse_text(text)

        if not parsed_items:
            message_box.information(self, "No Items", "No valid purchase items found in the text.")
            return

        # Get default currency ID
        default_currency: str | None = self.db_manager.get_default_currency()
        if not default_currency:
            message_box.warning(self, "Error", "No default currency set")
            return

        default_currency_info = self.db_manager.get_currency_by_code(default_currency)
        default_currency_id: int = default_currency_info[0]
        default_currency_symbol: str = default_currency_info[2] if default_currency_info else ""

        # Add items to database
        success_count: int = 0
        error_count: int = 0
        error_messages: list[str] = []
        total_amount: float = 0.0

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
                    total_amount += item.amount
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
            error_text: str = (
                f"Added {success_count} purchases successfully "
                f"(total: {total_amount:,.2f} {default_currency_symbol}).\n\n"
                "Errors:\n" + "\n".join(error_messages[:max_error_messages])
            )
            if len(error_messages) > max_error_messages:
                error_text += f"\n... and {len(error_messages) - 10} more errors"
            message_box.warning(self, "Results", error_text)
        else:
            message_box.information(
                self,
                "Success",
                f"Successfully added {success_count} purchases (total: {total_amount:,.2f} {default_currency_symbol}).",
            )

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
            if d_minor == 0:
                table.removeCellWidget(row_idx, 4)
                table.setItem(row_idx, 4, QTableWidgetItem("-"))

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
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        new_date: str = date_edit.date().toString("yyyy-MM-dd")
        if self.db_manager.update_transactions_date(transaction_ids, new_date):
            self._mark_transactions_changed()
            self.update_all()
            self.update_summary_labels()
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
            new_label.setText(old_label.text())

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

    def _show_category_label_context_menu(self, position: QPoint, *, from_hover: bool = False) -> None:
        """Show context menu on the category label with all available categories.

        Args:

        - `position` (`QPoint`): Position where the menu is requested.
        - `from_hover` (`bool`): If True, menu was opened by hover delay; it will close
          when mouse leaves menu and label.

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

        if from_hover:
            hover_close_filter = _CategoryMenuHoverCloseFilter(context_menu, self.label_category_now, parent=self)
            context_menu.installEventFilter(hover_close_filter)
            self.label_category_now.installEventFilter(hover_close_filter)

            def remove_filter() -> None:
                self.label_category_now.removeEventFilter(hover_close_filter)

            context_menu.aboutToHide.connect(remove_filter)

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
            menu = QMenu(purchases_table)
            remove_action = menu.addAction("🏷️ Remove tag from this transaction")
            chosen = menu.exec(purchases_table.mapToGlobal(position))
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
        close_btn = QPushButton("Close", dialog)
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

            if d_minor != 0:
                button = QPushButton("Add revision", table)
                button.clicked.connect(
                    lambda _checked=False, c=cid, dm=d_minor: self._on_add_revision_clicked(c, dm, table)
                )
                table.setCellWidget(row_idx, 4, button)
            else:
                table.setItem(row_idx, 4, QTableWidgetItem("-"))

        header = table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(table)

        button_row = QHBoxLayout()
        copy_btn = QPushButton("Copy", dialog)
        copy_btn.clicked.connect(lambda: self._copy_test_balance_to_clipboard(summary_lines, natural_rows))
        close_btn = QPushButton("Close", dialog)
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

        if len(selected_transaction_ids) > 1:
            ids_for_date_change = list(selected_transaction_ids)
            bulk_date_action = context_menu.addAction("📅 Set date for all selected rows…")
            bulk_date_action.triggered.connect(
                lambda _checked=False, ids=ids_for_date_change: self._set_date_for_selected_transactions(ids),
            )

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

    def _transform_transaction_data(self, rows: list[list]) -> list[list]:
        """Transform transaction data for display with colors and daily totals.

        Args:

        - `rows` (`list[list]`): Raw transaction data.

        Returns:

        - `list[list]`: Transformed data with colors and daily totals.

        """
        daily_expenses: dict[str, float] = calc_daily_expenses(rows, self.db_manager)
        return transform_transaction_data_helper(rows, daily_expenses, self.date_colors, self.db_manager)

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


class _CategoryMenuHoverCloseFilter(QObject):
    """Event filter that closes the menu when mouse leaves both menu and label (for hover-opened menu)."""

    def __init__(self, menu: QMenu, label: QWidget, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._menu = menu
        self._label = label

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() == QEvent.Type.Leave and obj in (self._menu, self._label):
            QTimer.singleShot(50, self._close_if_outside)
        return False

    def _close_if_outside(self) -> None:
        pos = QCursor.pos()
        w = QApplication.widgetAt(pos)
        if w is None:
            self._menu.hide()
            return
        if w == self._label:
            return
        if w == self._menu or self._menu.isAncestorOf(w):
            return
        self._menu.hide()


if __name__ == "__main__":
    run_app_main(MainWindow)
