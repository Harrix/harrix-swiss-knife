"""Report-tab UI operations for the finance tracker."""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import cast

from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtGui import QColor, QFont, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QAbstractItemView, QDialog, QMenu, QWidget

from harrix_swiss_knife import toast_countdown_notification
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.day_bands import set_readable_cell_fill
from harrix_swiss_knife.apps.finance.category_icon_display import category_lucide_icon
from harrix_swiss_knife.apps.finance.delegates import ReportAmountDelegate, YearDeltaCellDelegate
from harrix_swiss_knife.apps.finance.exchange_rates_operations import (
    DbFilenameUnavailableForWorkerThreadError,
    _require_db_filename_for_worker,
)
from harrix_swiss_knife.apps.finance.mixins import requires_database
from harrix_swiss_knife.apps.finance.report_build_worker import ReportBuildResult, ReportBuildWorker
from harrix_swiss_knife.apps.finance.report_generators import PeriodExpenseCategory
from harrix_swiss_knife.apps.finance.report_period_dialog import ReportPeriodDialog
from harrix_swiss_knife.fluent.tokens import ICON_SIZE
from harrix_swiss_knife.qt_lucide_icon import (
    LUCIDE_COLOR_BLUE,
    LUCIDE_COLOR_CYAN,
    LUCIDE_COLOR_GREEN,
    LUCIDE_COLOR_ORANGE,
    LUCIDE_COLOR_TURQUOISE,
    LUCIDE_COLOR_YELLOW,
    create_lucide_icon,
    set_action_text_with_lucide_icon,
)

logger = logging.getLogger(__name__)

_MONTH_KEY_RE = re.compile(r"^(\d{4})-(\d{2})$")

# Lucide id, CodeStyle stroke, report title (UserRole / worker key).
REPORT_TYPES: tuple[tuple[str, str, str], ...] = (
    ("calendar", LUCIDE_COLOR_BLUE, "Monthly Summary"),
    ("calendar-range", LUCIDE_COLOR_BLUE, "Yearly Summary"),
    ("list-tree", LUCIDE_COLOR_YELLOW, "Month Summary"),
    ("folder-tree", LUCIDE_COLOR_ORANGE, "Year Summary"),
    ("folders", LUCIDE_COLOR_YELLOW, "Category Analysis"),
    ("arrow-left-right", LUCIDE_COLOR_TURQUOISE, "Currency Analysis"),
    ("landmark", LUCIDE_COLOR_BLUE, "Account Balances"),
    ("scale", LUCIDE_COLOR_CYAN, "Income vs Expenses"),
    ("chart-line", LUCIDE_COLOR_GREEN, "Monthly Income vs Previous Years"),
    ("briefcase", LUCIDE_COLOR_ORANGE, "Average Salary by Year"),
)

_REPORT_TOTAL_FILL = QColor(255, 255, 0)
_REPORT_SECTION_FILL = QColor(200, 200, 255)
_REPORT_POSITIVE_FILL = QColor(200, 255, 200)
_REPORT_NEGATIVE_FILL = QColor(255, 200, 200)
_REPORT_AMOUNT_FILL = QColor(255, 250, 205)
_REPORT_YEAR_FILL = QColor(220, 235, 255)
_REPORT_COMBINED_FILL = QColor(220, 220, 220)


class ReportOperations:
    """Mixin: generate and display finance reports on the Reports tab."""

    @requires_database()
    def on_generate_report(
        self,
        *,
        refresh_summary: bool = False,
        report_type: str | None = None,
        period_year: int | None = None,
        period_month: int | None = None,
        prompt_for_period: bool = True,
    ) -> None:
        """Generate selected report on a background thread with a countdown toast.

        Args:

        - `report_type` (`str | None`): Override list selection (e.g. from context menu).
        - `period_year` / `period_month`: When set with `prompt_for_period=False`, skip the
          Month/Year Summary dialogs and use these values.

        """
        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        worker = getattr(self, "_report_build_worker", None)
        if worker is not None and worker.isRunning():
            return

        selected_type = report_type if report_type is not None else self._selected_report_type()

        year_start_month = 1
        year_start_day = 1
        if selected_type == "Average Salary by Year":
            if not self._prompt_compare_last_years_start():
                return
            year_start_month = self._compare_last_years_start_month
            year_start_day = self._compare_last_years_start_day
        elif selected_type == "Month Summary":
            if prompt_for_period or period_year is None or period_month is None:
                picked = self._prompt_report_period(mode="month")
                if picked is None:
                    return
                period_year, period_month = picked
        elif selected_type == "Year Summary":
            if prompt_for_period or period_year is None:
                picked = self._prompt_report_period(mode="year")
                if picked is None:
                    return
                period_year, period_month = picked

        try:
            db_filename = _require_db_filename_for_worker(self.db_manager)
        except DbFilenameUnavailableForWorkerThreadError:
            message_box.warning(cast("QWidget", self), "Error", "Database path is not available for report generation.")
            return

        self._report_build_toast = toast_countdown_notification.ToastCountdownNotification("Building report…")
        self._report_build_toast.start_countdown()

        if refresh_summary:
            self._refresh_summary_if_needed()

        self._report_build_worker = ReportBuildWorker(
            db_filename,
            selected_type,
            year_start_month=year_start_month,
            year_start_day=year_start_day,
            period_year=period_year,
            period_month=period_month,
        )
        self._report_build_worker.report_completed.connect(self._on_report_build_completed)
        self._report_build_worker.report_failed.connect(self._on_report_build_failed)
        self._report_build_worker.finished.connect(self._cleanup_report_build_worker)
        self.listView_report_type.setEnabled(False)
        self._report_build_worker.start()

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
                    set_readable_cell_fill(item, _REPORT_TOTAL_FILL)
            model.appendRow(items)
        self._set_reports_model_and_stretch(model)

    def _apply_average_salary_by_year_report(self, headers: list[str], report_data: list[list[str]]) -> None:
        """Bind average salary by year report data to the reports table."""
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
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
                    set_readable_cell_fill(item, _REPORT_SECTION_FILL)
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
                    set_readable_cell_fill(items[3], _REPORT_POSITIVE_FILL)
                elif balance_value < 0:
                    set_readable_cell_fill(items[3], _REPORT_NEGATIVE_FILL)
            except (ValueError, IndexError):
                pass
            model.appendRow(items)
        self._set_reports_model_and_stretch(model)

    def _apply_monthly_income_year_delta_report(self, headers: list[str], report_data: list[list[str]]) -> None:
        """Bind monthly income year-delta report data to the reports table."""
        model: QStandardItemModel = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        self.tableView_reports.setRootIsDecorated(False)
        self.tableView_reports.setItemsExpandable(False)
        for row_data in report_data:
            items = [QStandardItem(str(value)) for value in row_data]
            if row_data and row_data[0] == "TOTAL":
                for item in items:
                    set_readable_cell_fill(item, _REPORT_TOTAL_FILL)
            else:
                for column, item in enumerate(items[1:], start=1):
                    text = str(row_data[column]) if column < len(row_data) else ""
                    first_line = text.split("\n", 1)[0]
                    if first_line in {"", "—"}:
                        continue
                    header = headers[column] if column < len(headers) else ""
                    if header.isdigit():
                        fill = _REPORT_AMOUNT_FILL if column == 1 else _REPORT_YEAR_FILL
                        set_readable_cell_fill(item, fill, band_index=column % 2)
                        continue
                    try:
                        amount = float(first_line.replace("+", "").split(maxsplit=1)[0])
                    except (ValueError, IndexError):
                        continue
                    if amount > 0:
                        set_readable_cell_fill(item, _REPORT_POSITIVE_FILL)
                    elif amount < 0:
                        set_readable_cell_fill(item, _REPORT_NEGATIVE_FILL)
            model.appendRow(items)
        self._set_reports_model_and_stretch(model)
        delegate = YearDeltaCellDelegate(self.tableView_reports)
        for column in range(1, model.columnCount()):
            self.tableView_reports.setItemDelegateForColumn(column, delegate)
        reports_header = self.tableView_reports.horizontalHeader()
        for column in range(reports_header.count()):
            reports_header.setSectionResizeMode(column, reports_header.ResizeMode.Interactive)
        self.tableView_reports.resizeColumnsToContents()
        self.tableView_reports.resizeRowsToContents()

    def _apply_monthly_summary_report(
        self,
        headers: list[str],
        rows: list[tuple[str, float, float, dict[int, float]]],
        expense_categories: list[tuple[int, str, str, str]],
    ) -> None:
        """Bind monthly or yearly expense-by-category summary to the reports table."""
        if not expense_categories:
            model: QStandardItemModel = QStandardItemModel()
            model.setHorizontalHeaderLabels(headers)
            self.tableView_reports.setModel(model)
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        self._set_monthly_summary_header_icons(model, expense_categories)

        num_categories = len(expense_categories)
        category_colors: list[QColor] = []
        for i in range(num_categories):
            hue = (i * 360) / num_categories if num_categories > 0 else 0
            category_colors.append(QColor.fromHsv(int(hue), 80, 240))

        current_year: str = datetime.now(UTC).astimezone().strftime("%Y")

        for period_name, period_total, combined_total, by_category in rows:
            row_items = []
            period_item = QStandardItem(period_name)
            if period_name == current_year or period_name.startswith(f"{current_year}-"):
                font = period_item.font()
                font.setBold(True)
                period_item.setFont(font)
            row_items.append(period_item)

            total_item = QStandardItem(f"{period_total:.2f}")
            set_readable_cell_fill(total_item, _REPORT_AMOUNT_FILL)
            total_item.setData(period_total, Qt.ItemDataRole.UserRole)
            row_items.append(total_item)

            combined_item = QStandardItem(f"{combined_total:.2f}")
            set_readable_cell_fill(combined_item, _REPORT_COMBINED_FILL, band_index=1)
            combined_item.setData(combined_total, Qt.ItemDataRole.UserRole)
            row_items.append(combined_item)

            for idx, (category_id, _name, _emoji, _lucide) in enumerate(expense_categories):
                amount = by_category.get(category_id, 0.0)
                item = QStandardItem(f"{amount:.2f}")
                set_readable_cell_fill(item, category_colors[idx], band_index=idx % 2)
                item.setData(amount, Qt.ItemDataRole.UserRole)
                row_items.append(item)

            model.appendRow(row_items)

        self.tableView_reports.setRootIsDecorated(False)
        self.tableView_reports.setItemsExpandable(False)
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

    def _apply_period_expense_summary_report(
        self,
        headers: list[str],
        categories: list[PeriodExpenseCategory],
        grand_total: float,
    ) -> None:
        """Bind Month/Year Summary as an expandable category tree."""
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        total_label = QStandardItem("TOTAL")
        total_amount = QStandardItem(f"{grand_total:.2f}")
        total_amount.setData(grand_total, Qt.ItemDataRole.UserRole)
        total_date = QStandardItem("")
        for item in (total_label, total_amount, total_date):
            set_readable_cell_fill(item, _REPORT_TOTAL_FILL)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        model.appendRow([total_label, total_amount, total_date])

        for category in categories:
            name_item = QStandardItem(category.name)
            name_item.setIcon(category_lucide_icon(category.icon, lucide_name=category.icon_lucide))
            amount_item = QStandardItem(f"{category.total:.2f}")
            amount_item.setData(category.total, Qt.ItemDataRole.UserRole)
            set_readable_cell_fill(amount_item, _REPORT_AMOUNT_FILL)
            bold = QFont(name_item.font())
            bold.setBold(True)
            name_item.setFont(bold)
            amount_item.setFont(bold)
            date_item = QStandardItem("")
            for transaction in category.transactions:
                child_name = QStandardItem(transaction.description or "(no description)")
                child_amount = QStandardItem(f"{transaction.amount:.2f}")
                child_amount.setData(transaction.amount, Qt.ItemDataRole.UserRole)
                child_date = QStandardItem(transaction.date)
                name_item.appendRow([child_name, child_amount, child_date])
            model.appendRow([name_item, amount_item, date_item])

        self.tableView_reports.setSortingEnabled(False)
        self.tableView_reports.setRootIsDecorated(True)
        self.tableView_reports.setItemsExpandable(True)
        self.tableView_reports.setModel(model)
        self.tableView_reports.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for column in range(model.columnCount()):
            self.tableView_reports.setItemDelegateForColumn(column, None)
        amount_delegate = ReportAmountDelegate(self.tableView_reports, is_bold=True)
        self.tableView_reports.setItemDelegateForColumn(1, amount_delegate)
        reports_header = self.tableView_reports.horizontalHeader()
        for i in range(reports_header.count()):
            reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Interactive)
        self.tableView_reports.resizeColumnsToContents()
        if reports_header.count() > 1:
            self.tableView_reports.setColumnWidth(0, max(220, self.tableView_reports.columnWidth(0) + 40))
            self.tableView_reports.setColumnWidth(1, self.tableView_reports.columnWidth(1) + 24)

    def _apply_report_build_result(self, result: ReportBuildResult) -> None:
        """Dispatch report build result to the appropriate table binder."""
        report_type = result.report_type
        self._displayed_report_type = report_type
        if report_type in {"Monthly Summary", "Yearly Summary"}:
            if result.monthly_rows is None or result.expense_categories is None:
                return
            self._apply_monthly_summary_report(result.headers, result.monthly_rows, result.expense_categories)
        elif report_type in {"Month Summary", "Year Summary"}:
            if result.period_categories is None or result.period_grand_total is None:
                return
            self._apply_period_expense_summary_report(
                result.headers,
                result.period_categories,
                result.period_grand_total,
            )
        elif report_type == "Category Analysis":
            self._apply_category_analysis_report(result.headers, result.table_rows or [])
        elif report_type == "Currency Analysis":
            self._apply_currency_analysis_report(result.headers, result.table_rows or [])
        elif report_type == "Account Balances":
            self._apply_account_balances_report(result.headers, result.table_rows or [])
        elif report_type == "Income vs Expenses":
            self._apply_income_vs_expenses_report(result.headers, result.table_rows or [])
        elif report_type == "Monthly Income vs Previous Years":
            self._apply_monthly_income_year_delta_report(result.headers, result.table_rows or [])
        elif report_type == "Average Salary by Year":
            self._apply_average_salary_by_year_report(result.headers, result.table_rows or [])

    def _cleanup_report_build_worker(self) -> None:
        """Release the report build worker after the thread finishes."""
        worker = getattr(self, "_report_build_worker", None)
        if worker is not None:
            worker.deleteLater()
            self._report_build_worker = None
        self.listView_report_type.setEnabled(True)

    def _close_report_build_toast(self) -> None:
        """Close the report-building countdown toast if it is open."""
        toast = getattr(self, "_report_build_toast", None)
        if toast is not None:
            toast.close()
            self._report_build_toast = None

    def _on_report_build_completed(self, result: ReportBuildResult) -> None:
        """Apply report data to the reports table after background computation."""
        self._close_report_build_toast()
        try:
            self._apply_report_build_result(result)
        except Exception as e:
            message_box.warning(cast("QWidget", self), "Report Error", f"Failed to display report: {e}")

    def _on_report_build_failed(self, error_message: str) -> None:
        """Handle report build worker failure."""
        self._close_report_build_toast()
        message_box.warning(cast("QWidget", self), "Report Error", f"Failed to generate report: {error_message}")

    def _open_month_summary_for_period(self, year: int, month: int) -> None:
        """Select Month Summary in the list and build it for `year`/`month` without a prompt."""
        self._report_period_year = year
        self._report_period_month = month
        self._select_report_type_in_list("Month Summary")
        self.on_generate_report(
            report_type="Month Summary",
            period_year=year,
            period_month=month,
            prompt_for_period=False,
        )

    @staticmethod
    def _parse_month_key(text: str) -> tuple[int, int] | None:
        """Parse `YYYY-MM` into `(year, month)`, or `None` when invalid."""
        match = _MONTH_KEY_RE.fullmatch(text.strip())
        if match is None:
            return None
        year = int(match.group(1))
        month = int(match.group(2))
        if not 1 <= month <= 12:
            return None
        return year, month

    def _prompt_report_period(self, *, mode: str) -> tuple[int, int | None] | None:
        """Ask for month+year or year; return `(year, month)` or `None` if cancelled."""
        years = self._report_period_years()
        now = datetime.now(UTC).astimezone()
        default_year = getattr(self, "_report_period_year", now.year)
        default_month = getattr(self, "_report_period_month", now.month)
        dialog = ReportPeriodDialog(
            cast("QWidget", self),
            mode=mode,
            years=years,
            default_year=default_year,
            default_month=default_month,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        year = dialog.selected_year()
        month = dialog.selected_month()
        self._report_period_year = year
        if month is not None:
            self._report_period_month = month
        return year, month

    def _report_period_years(self) -> list[int]:
        """Return calendar years from earliest transaction through today."""
        now = datetime.now(UTC).astimezone()
        start_year = now.year
        if self.db_manager is not None:
            earliest = self.db_manager.get_earliest_transaction_date()
            if earliest:
                start_year = datetime.fromisoformat(earliest).year
        return list(range(start_year, now.year + 1))

    def _reports_month_key_at(self, position: QPoint) -> tuple[int, int] | None:
        """Return `(year, month)` for the Monthly Summary row under `position`."""
        if getattr(self, "_displayed_report_type", "") != "Monthly Summary":
            return None
        index = self.tableView_reports.indexAt(position)
        if not index.isValid():
            return None
        month_index = index.sibling(index.row(), 0)
        text = month_index.data(Qt.ItemDataRole.DisplayRole)
        if not isinstance(text, str):
            return None
        return self._parse_month_key(text)

    def _select_report_type_in_list(self, report_type: str) -> None:
        """Select `report_type` in `listView_report_type` without regenerating."""
        model = self.listView_report_type.model()
        if model is None:
            return
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            if index.data(Qt.ItemDataRole.UserRole) == report_type:
                self.listView_report_type.setCurrentIndex(index)
                return

    def _selected_report_type(self) -> str:
        """Return the report type currently selected in `listView_report_type`."""
        index = self.listView_report_type.currentIndex()
        if index.isValid():
            text = index.data(Qt.ItemDataRole.UserRole)
            if isinstance(text, str) and text.strip():
                return text
        return REPORT_TYPES[0][2]

    def _show_reports_table_context_menu(self, position: QPoint) -> None:
        """Context menu on Monthly Summary rows to open Month Summary for that month."""
        period = self._reports_month_key_at(position)
        if period is None:
            return
        year, month = period
        index = self.tableView_reports.indexAt(position)
        if index.isValid():
            self.tableView_reports.setCurrentIndex(index.sibling(index.row(), 0))

        menu = QMenu(cast("QWidget", self))
        action = menu.addAction("Month Summary")
        set_action_text_with_lucide_icon(action, "Month Summary", "list-tree")
        action.triggered.connect(lambda: self._open_month_summary_for_period(year, month))
        viewport = self.tableView_reports.viewport()
        if viewport is None:
            return
        menu.exec(viewport.mapToGlobal(position))

    @staticmethod
    def _set_monthly_summary_header_icons(
        model: QStandardItemModel,
        expense_categories: list[tuple[int, str, str, str]],
    ) -> None:
        """Attach Lucide category icons to Monthly/Yearly Summary column headers."""
        combined = model.horizontalHeaderItem(2)
        if combined is not None:
            combined.setIcon(category_lucide_icon("🍔", lucide_name="utensils"))

        for col, (_cid, _name, emoji, lucide) in enumerate(expense_categories, start=3):
            header_item = model.horizontalHeaderItem(col)
            if header_item is None:
                continue
            header_item.setIcon(category_lucide_icon(emoji, lucide_name=lucide))

    def _set_reports_model_and_stretch(self, model: QStandardItemModel) -> None:
        """Set model on reports table and stretch columns."""
        self.tableView_reports.setSortingEnabled(False)
        self.tableView_reports.setRootIsDecorated(False)
        self.tableView_reports.setItemsExpandable(False)
        self.tableView_reports.setModel(model)
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)

    def _setup_report_type_list(self) -> None:
        """Populate `listView_report_type` with colored Lucide icons."""
        model = QStandardItemModel(self.listView_report_type)
        for lucide_name, color, report_type in REPORT_TYPES:
            item = QStandardItem(report_type)
            item.setIcon(create_lucide_icon(lucide_name, ICON_SIZE, color=color))
            item.setData(report_type, Qt.ItemDataRole.UserRole)
            item.setEditable(False)
            model.appendRow(item)
        self.listView_report_type.setModel(model)
        self.listView_report_type.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.listView_report_type.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listView_report_type.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        if model.rowCount() > 0:
            self.listView_report_type.setCurrentIndex(model.index(0, 0))
        self.tableView_reports.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_reports.customContextMenuRequested.connect(self._show_reports_table_context_menu)
