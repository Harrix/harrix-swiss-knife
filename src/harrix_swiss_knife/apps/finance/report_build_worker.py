"""Worker thread for finance report data computation."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QThread, Signal

from harrix_swiss_knife.apps.finance.report_build_context import ReportBuildContext
from harrix_swiss_knife.apps.finance.report_generators import (
    get_account_balances_report_data,
    get_average_salary_by_year_report_data,
    get_category_analysis_report_data,
    get_currency_analysis_report_data,
    get_income_vs_expenses_report_data,
    get_monthly_income_year_delta_report_data,
    get_monthly_summary_report_data,
)


@dataclass(frozen=True, slots=True)
class ReportBuildResult:
    """Report data computed off the UI thread, ready to bind to Qt models."""

    report_type: str
    headers: list[str]
    table_rows: list[list[str]] | None = None
    monthly_rows: list[tuple[str, float, float, dict[int, float]]] | None = None
    expense_categories: list[tuple[int, str, str]] | None = None


class ReportBuildWorker(QThread):
    """Load report data from the database on a background thread."""

    report_completed: Signal = Signal(object)  # ReportBuildResult
    report_failed: Signal = Signal(str)

    def __init__(
        self,
        db_filename: str,
        report_type: str,
        *,
        year_start_month: int = 1,
        year_start_day: int = 1,
    ) -> None:
        """Initialize the worker.

        Args:

        - `db_filename` (`str`): Path to the finance SQLite database file.
        - `report_type` (`str`): Value from the report type list.
        - `year_start_month` (`int`): Fiscal year start month (1-12).
        - `year_start_day` (`int`): Fiscal year start day.

        """
        super().__init__()
        self.db_filename = db_filename
        self.report_type = report_type
        self.year_start_month = year_start_month
        self.year_start_day = year_start_day

    def run(self) -> None:
        """Compute report data for the selected report type."""
        try:
            ctx = ReportBuildContext.load(self.db_filename)
            report_type = self.report_type

            if report_type == "Monthly Summary":
                headers, rows, expense_categories, _ = get_monthly_summary_report_data(ctx)
                result = ReportBuildResult(
                    report_type=report_type,
                    headers=headers,
                    monthly_rows=rows,
                    expense_categories=expense_categories,
                )
            elif report_type == "Category Analysis":
                headers, report_data = get_category_analysis_report_data(ctx)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Currency Analysis":
                headers, report_data = get_currency_analysis_report_data(ctx)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Account Balances":
                headers, report_data = get_account_balances_report_data(ctx)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Income vs Expenses":
                headers, report_data = get_income_vs_expenses_report_data(ctx)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Monthly Income vs Previous Years":
                headers, report_data = get_monthly_income_year_delta_report_data(ctx)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Average Salary by Year":
                headers, report_data = get_average_salary_by_year_report_data(
                    ctx,
                    year_start_month=self.year_start_month,
                    year_start_day=self.year_start_day,
                )
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            else:
                self.report_failed.emit(f"Unknown report type: {report_type}")
                return

            self.report_completed.emit(result)
        except Exception as e:
            self.report_failed.emit(str(e))
