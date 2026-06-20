---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `report_build_worker.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ReportBuildResult`](#️-class-reportbuildresult)
- [🏛️ Class `ReportBuildWorker`](#️-class-reportbuildworker)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `run`](#️-method-run)

</details>

## 🏛️ Class `ReportBuildResult`

```python
class ReportBuildResult
```

Report data computed off the UI thread, ready to bind to Qt models.

<details>
<summary>Code:</summary>

```python
class ReportBuildResult:

    report_type: str
    headers: list[str]
    table_rows: list[list[str]] | None = None
    monthly_rows: list[tuple[str, float, float, dict[int, float]]] | None = None
    expense_categories: list[tuple[int, str, str]] | None = None
```

</details>

## 🏛️ Class `ReportBuildWorker`

```python
class ReportBuildWorker(QThread)
```

Load report data from the database on a background thread.

<details>
<summary>Code:</summary>

```python
class ReportBuildWorker(QThread):

    report_completed: Signal = Signal(object)  # ReportBuildResult
    report_failed: Signal = Signal(str)

    def __init__(self, db_filename: str, report_type: str) -> None:
        """Initialize the worker.

        Args:

        - `db_filename` (`str`): Path to the finance SQLite database file.
        - `report_type` (`str`): Value from the report type combobox.

        """
        super().__init__()
        self.db_filename = db_filename
        self.report_type = report_type

    def run(self) -> None:
        """Compute report data for the selected report type."""
        try:
            db_manager = DatabaseManager(self.db_filename)
            currency_id: int = db_manager.get_default_currency_id()
            report_type = self.report_type

            if report_type == "Monthly Summary":
                headers, rows, expense_categories, _ = get_monthly_summary_report_data(db_manager, currency_id)
                result = ReportBuildResult(
                    report_type=report_type,
                    headers=headers,
                    monthly_rows=rows,
                    expense_categories=expense_categories,
                )
            elif report_type == "Category Analysis":
                headers, report_data = get_category_analysis_report_data(db_manager)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Currency Analysis":
                headers, report_data = get_currency_analysis_report_data(db_manager)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Account Balances":
                headers, report_data = get_account_balances_report_data(db_manager, currency_id)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Income vs Expenses":
                headers, report_data = get_income_vs_expenses_report_data(db_manager, currency_id)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            else:
                self.report_failed.emit(f"Unknown report type: {report_type}")
                return

            self.report_completed.emit(result)
        except Exception as e:
            self.report_failed.emit(str(e))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, db_filename: str, report_type: str) -> None
```

Initialize the worker.

Args:

- `db_filename` (`str`): Path to the finance SQLite database file.
- `report_type` (`str`): Value from the report type combobox.

<details>
<summary>Code:</summary>

```python
def __init__(self, db_filename: str, report_type: str) -> None:
        super().__init__()
        self.db_filename = db_filename
        self.report_type = report_type
```

</details>

### ⚙️ Method `run`

```python
def run(self) -> None
```

Compute report data for the selected report type.

<details>
<summary>Code:</summary>

```python
def run(self) -> None:
        try:
            db_manager = DatabaseManager(self.db_filename)
            currency_id: int = db_manager.get_default_currency_id()
            report_type = self.report_type

            if report_type == "Monthly Summary":
                headers, rows, expense_categories, _ = get_monthly_summary_report_data(db_manager, currency_id)
                result = ReportBuildResult(
                    report_type=report_type,
                    headers=headers,
                    monthly_rows=rows,
                    expense_categories=expense_categories,
                )
            elif report_type == "Category Analysis":
                headers, report_data = get_category_analysis_report_data(db_manager)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Currency Analysis":
                headers, report_data = get_currency_analysis_report_data(db_manager)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Account Balances":
                headers, report_data = get_account_balances_report_data(db_manager, currency_id)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            elif report_type == "Income vs Expenses":
                headers, report_data = get_income_vs_expenses_report_data(db_manager, currency_id)
                result = ReportBuildResult(report_type=report_type, headers=headers, table_rows=report_data)
            else:
                self.report_failed.emit(f"Unknown report type: {report_type}")
                return

            self.report_completed.emit(result)
        except Exception as e:
            self.report_failed.emit(str(e))
```

</details>
