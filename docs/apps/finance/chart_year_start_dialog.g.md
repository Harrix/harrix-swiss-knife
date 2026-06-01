---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_year_start_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ChartYearStartDialog`](#%EF%B8%8F-class-chartyearstartdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_year_start`](#%EF%B8%8F-method-get_year_start)

</details>

## 🏛️ Class `ChartYearStartDialog`

```python
class ChartYearStartDialog(QDialog)
```

Pick day and month for the start of comparison years (calendar year is ignored).

<details>
<summary>Code:</summary>

```python
class ChartYearStartDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        start_month: int = 1,
        start_day: int = 1,
    ) -> None:
        """Initialize the dialog with optional default month and day."""
        super().__init__(parent)
        self.setWindowTitle("Year start date")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Choose the day and month when each comparison year begins.\n"
                "For example, 1 September for a school year.",
            ),
        )

        self._date_edit = QDateEdit(self)
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("d MMMM")
        safe_month = max(1, min(12, start_month))
        safe_day = max(1, min(QDate(2000, safe_month, 1).daysInMonth(), start_day))
        self._date_edit.setDate(QDate(2000, safe_month, safe_day))

        layout.addWidget(self._date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_year_start(self) -> tuple[int, int]:
        """Return `(month, day)` for the selected year start."""
        selected = self._date_edit.date()
        return selected.month(), selected.day()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the dialog with optional default month and day.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        start_month: int = 1,
        start_day: int = 1,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Year start date")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Choose the day and month when each comparison year begins.\n"
                "For example, 1 September for a school year.",
            ),
        )

        self._date_edit = QDateEdit(self)
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("d MMMM")
        safe_month = max(1, min(12, start_month))
        safe_day = max(1, min(QDate(2000, safe_month, 1).daysInMonth(), start_day))
        self._date_edit.setDate(QDate(2000, safe_month, safe_day))

        layout.addWidget(self._date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
```

</details>

### ⚙️ Method `get_year_start`

```python
def get_year_start(self) -> tuple[int, int]
```

Return `(month, day)` for the selected year start.

<details>
<summary>Code:</summary>

```python
def get_year_start(self) -> tuple[int, int]:
        selected = self._date_edit.date()
        return selected.month(), selected.day()
```

</details>
