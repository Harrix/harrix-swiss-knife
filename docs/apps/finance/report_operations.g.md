---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `report_operations.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ReportOperations`](#%EF%B8%8F-class-reportoperations)
  - [⚙️ Method `on_generate_report`](#%EF%B8%8F-method-on_generate_report)

</details>

## 🏛️ Class `ReportOperations`

```python
class ReportOperations
```

Mixin: generate and display finance reports on the Reports tab.

<details>
<summary>Code:</summary>

```python
class ReportOperations:

    @requires_database()
    def on_generate_report(self, *, refresh_summary: bool = False) -> None:
        """Generate selected report on a background thread with a countdown toast."""
        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        worker = getattr(self, "_report_build_worker", None)
        if worker is not None and worker.isRunning():
            return

        report_type: str = self.comboBox_report_type.currentText()

        try:
            db_filename = _require_db_filename_for_worker(self.db_manager)
        except DbFilenameUnavailableForWorkerThreadError:
            message_box.warning(cast("QWidget", self), "Error", "Database path is not available for report generation.")
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

    def _cleanup_report_build_worker(self) -> None:
        """Release the report build worker after the thread finishes."""
        worker = getattr(self, "_report_build_worker", None)
        if worker is not None:
            worker.deleteLater()
            self._report_build_worker = None
        self.pushButton_generate_report.setEnabled(True)

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

    def _set_reports_model_and_stretch(self, model: QStandardItemModel) -> None:
        """Set model on reports table and stretch columns."""
        self.tableView_reports.setModel(model)
        reports_header = self.tableView_reports.horizontalHeader()
        if reports_header.count() > 0:
            for i in range(reports_header.count()):
                reports_header.setSectionResizeMode(i, reports_header.ResizeMode.Stretch)
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
            logger.error("❌ Database manager is not initialized")
            return

        worker = getattr(self, "_report_build_worker", None)
        if worker is not None and worker.isRunning():
            return

        report_type: str = self.comboBox_report_type.currentText()

        try:
            db_filename = _require_db_filename_for_worker(self.db_manager)
        except DbFilenameUnavailableForWorkerThreadError:
            message_box.warning(cast("QWidget", self), "Error", "Database path is not available for report generation.")
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
