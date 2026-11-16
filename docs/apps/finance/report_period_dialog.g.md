---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `report_period_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ReportPeriodBar`](#%EF%B8%8F-class-reportperiodbar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `selected_month`](#%EF%B8%8F-method-selected_month)
  - [⚙️ Method `selected_year`](#%EF%B8%8F-method-selected_year)
  - [⚙️ Method `set_mode`](#%EF%B8%8F-method-set_mode)
  - [⚙️ Method `set_period`](#%EF%B8%8F-method-set_period)
- [🏛️ Class `ReportPeriodDialog`](#%EF%B8%8F-class-reportperioddialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `selected_month`](#%EF%B8%8F-method-selected_month-1)
  - [⚙️ Method `selected_year`](#%EF%B8%8F-method-selected_year-1)
- [🔧 Function `last_calendar_month`](#-function-last_calendar_month)
- [🔧 Function `last_calendar_year`](#-function-last_calendar_year)

</details>

## 🏛️ Class `ReportPeriodBar`

```python
class ReportPeriodBar(QWidget)
```

Inline month/year controls shown above Month Summary / Year Summary.

<details>
<summary>Code:</summary>

```python
class ReportPeriodBar(QWidget):

    period_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create month and year combo boxes in a horizontal row."""
        super().__init__(parent)
        self.setObjectName("reportPeriodBar")
        self._mode = "month"
        self._syncing = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(8)

        self._month_label = QLabel("Month:", self)
        layout.addWidget(self._month_label)
        self._month_combo = QComboBox(self)
        self._month_combo.addItems(MONTH_NAMES)
        self._month_combo.setMinimumWidth(120)
        layout.addWidget(self._month_combo)

        self._year_label = QLabel("Year:", self)
        layout.addWidget(self._year_label)
        self._year_combo = QComboBox(self)
        self._year_combo.setMinimumWidth(80)
        layout.addWidget(self._year_combo)
        layout.addStretch(1)

        self._month_combo.currentIndexChanged.connect(self._emit_period_changed)
        self._year_combo.currentIndexChanged.connect(self._emit_period_changed)

    def selected_month(self) -> int | None:
        """Return 1-12 in month mode, otherwise `None`."""
        if self._mode != "month":
            return None
        return self._month_combo.currentIndex() + 1

    def selected_year(self) -> int | None:
        """Return the selected year, or `None` when the combo is empty."""
        text = self._year_combo.currentText().strip()
        if not text:
            return None
        return int(text)

    def set_mode(self, mode: str) -> None:
        """Show month+year (`month`) or year only (`year`)."""
        self._mode = mode if mode in {"month", "year"} else "month"
        show_month = self._mode == "month"
        self._month_label.setVisible(show_month)
        self._month_combo.setVisible(show_month)

    def set_period(self, *, year: int, month: int | None, years: list[int]) -> None:
        """Populate year choices and select `year` / `month` without emitting."""
        year_choices = sorted(years or [year], reverse=True)
        if year not in year_choices:
            year_choices = sorted({*year_choices, year}, reverse=True)
        self._syncing = True
        try:
            self._year_combo.blockSignals(True)
            self._month_combo.blockSignals(True)
            self._year_combo.clear()
            self._year_combo.addItems([str(y) for y in year_choices])
            self._year_combo.setCurrentText(str(year))
            if month is not None:
                self._month_combo.setCurrentIndex(max(0, min(11, month - 1)))
        finally:
            self._year_combo.blockSignals(False)
            self._month_combo.blockSignals(False)
            self._syncing = False

    def _emit_period_changed(self, *_args: object) -> None:
        if self._syncing:
            return
        self.period_changed.emit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create month and year combo boxes in a horizontal row.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("reportPeriodBar")
        self._mode = "month"
        self._syncing = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(8)

        self._month_label = QLabel("Month:", self)
        layout.addWidget(self._month_label)
        self._month_combo = QComboBox(self)
        self._month_combo.addItems(MONTH_NAMES)
        self._month_combo.setMinimumWidth(120)
        layout.addWidget(self._month_combo)

        self._year_label = QLabel("Year:", self)
        layout.addWidget(self._year_label)
        self._year_combo = QComboBox(self)
        self._year_combo.setMinimumWidth(80)
        layout.addWidget(self._year_combo)
        layout.addStretch(1)

        self._month_combo.currentIndexChanged.connect(self._emit_period_changed)
        self._year_combo.currentIndexChanged.connect(self._emit_period_changed)
```

</details>

### ⚙️ Method `selected_month`

```python
def selected_month(self) -> int | None
```

Return 1-12 in month mode, otherwise `None`.

<details>
<summary>Code:</summary>

```python
def selected_month(self) -> int | None:
        if self._mode != "month":
            return None
        return self._month_combo.currentIndex() + 1
```

</details>

### ⚙️ Method `selected_year`

```python
def selected_year(self) -> int | None
```

Return the selected year, or `None` when the combo is empty.

<details>
<summary>Code:</summary>

```python
def selected_year(self) -> int | None:
        text = self._year_combo.currentText().strip()
        if not text:
            return None
        return int(text)
```

</details>

### ⚙️ Method `set_mode`

```python
def set_mode(self, mode: str) -> None
```

Show month+year (`month`) or year only ([`year`](../common/chart_widgets.g.md#%EF%B8%8F-method-year)).

<details>
<summary>Code:</summary>

```python
def set_mode(self, mode: str) -> None:
        self._mode = mode if mode in {"month", "year"} else "month"
        show_month = self._mode == "month"
        self._month_label.setVisible(show_month)
        self._month_combo.setVisible(show_month)
```

</details>

### ⚙️ Method `set_period`

```python
def set_period(self, *, year: int, month: int | None, years: list[int]) -> None
```

Populate year choices and select [`year`](../common/chart_widgets.g.md#%EF%B8%8F-method-year) / `month` without emitting.

<details>
<summary>Code:</summary>

```python
def set_period(self, *, year: int, month: int | None, years: list[int]) -> None:
        year_choices = sorted(years or [year], reverse=True)
        if year not in year_choices:
            year_choices = sorted({*year_choices, year}, reverse=True)
        self._syncing = True
        try:
            self._year_combo.blockSignals(True)
            self._month_combo.blockSignals(True)
            self._year_combo.clear()
            self._year_combo.addItems([str(y) for y in year_choices])
            self._year_combo.setCurrentText(str(year))
            if month is not None:
                self._month_combo.setCurrentIndex(max(0, min(11, month - 1)))
        finally:
            self._year_combo.blockSignals(False)
            self._month_combo.blockSignals(False)
            self._syncing = False
```

</details>

## 🏛️ Class `ReportPeriodDialog`

```python
class ReportPeriodDialog(QDialog)
```

Pick a calendar month+year, or a single year, for a period report.

<details>
<summary>Code:</summary>

```python
class ReportPeriodDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        mode: str = "month",
        years: list[int] | None = None,
        default_year: int | None = None,
        default_month: int | None = None,
    ) -> None:
        """Initialize the period picker.

        Args:

        - `mode` (`str`): `"month"` for month+year, `"year"` for year only.
        - `years` (`list[int] | None`): Years to offer; defaults to current year alone.
        - `default_year` / `default_month`: Initial selection.

        """
        super().__init__(parent)
        self._mode = mode if mode in {"month", "year"} else "month"
        self.setWindowTitle("Select month" if self._mode == "month" else "Select year")
        qt_modality.set_owner_window_modal(self)

        now = datetime.now(UTC).astimezone()
        year_choices = sorted(years or [now.year], reverse=True)
        if not year_choices:
            year_choices = [now.year]
        year = default_year if default_year in year_choices else year_choices[0]
        month = max(1, min(12, default_month or now.month))

        layout = QVBoxLayout(self)
        if self._mode == "month":
            layout.addWidget(QLabel("Choose the month and year for the expense summary."))
        else:
            layout.addWidget(QLabel("Choose the year for the expense summary."))

        picker_row = QHBoxLayout()
        if self._mode == "month":
            picker_row.addWidget(QLabel("Month:"))
            self._month_combo = QComboBox(self)
            self._month_combo.addItems(MONTH_NAMES)
            self._month_combo.setCurrentIndex(month - 1)
            picker_row.addWidget(self._month_combo)
        else:
            self._month_combo = None

        picker_row.addWidget(QLabel("Year:"))
        self._year_combo = QComboBox(self)
        self._year_combo.addItems([str(y) for y in year_choices])
        self._year_combo.setCurrentText(str(year))
        picker_row.addWidget(self._year_combo)
        layout.addLayout(picker_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_lucide_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_month(self) -> int | None:
        """Return 1-12 when mode is month, otherwise `None`."""
        if self._month_combo is None:
            return None
        return self._month_combo.currentIndex() + 1

    def selected_year(self) -> int:
        """Return the selected calendar year."""
        return int(self._year_combo.currentText())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, mode: str = 'month', years: list[int] | None = None, default_year: int | None = None, default_month: int | None = None) -> None
```

Initialize the period picker.

Args:

- `mode` (`str`): `"month"` for month+year, `"year"` for year only.
- `years` (`list[int] | None`): Years to offer; defaults to current year alone.
- `default_year` / `default_month`: Initial selection.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        mode: str = "month",
        years: list[int] | None = None,
        default_year: int | None = None,
        default_month: int | None = None,
    ) -> None:
        super().__init__(parent)
        self._mode = mode if mode in {"month", "year"} else "month"
        self.setWindowTitle("Select month" if self._mode == "month" else "Select year")
        qt_modality.set_owner_window_modal(self)

        now = datetime.now(UTC).astimezone()
        year_choices = sorted(years or [now.year], reverse=True)
        if not year_choices:
            year_choices = [now.year]
        year = default_year if default_year in year_choices else year_choices[0]
        month = max(1, min(12, default_month or now.month))

        layout = QVBoxLayout(self)
        if self._mode == "month":
            layout.addWidget(QLabel("Choose the month and year for the expense summary."))
        else:
            layout.addWidget(QLabel("Choose the year for the expense summary."))

        picker_row = QHBoxLayout()
        if self._mode == "month":
            picker_row.addWidget(QLabel("Month:"))
            self._month_combo = QComboBox(self)
            self._month_combo.addItems(MONTH_NAMES)
            self._month_combo.setCurrentIndex(month - 1)
            picker_row.addWidget(self._month_combo)
        else:
            self._month_combo = None

        picker_row.addWidget(QLabel("Year:"))
        self._year_combo = QComboBox(self)
        self._year_combo.addItems([str(y) for y in year_choices])
        self._year_combo.setCurrentText(str(year))
        picker_row.addWidget(self._year_combo)
        layout.addLayout(picker_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_lucide_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
```

</details>

### ⚙️ Method `selected_month`

```python
def selected_month(self) -> int | None
```

Return 1-12 when mode is month, otherwise `None`.

<details>
<summary>Code:</summary>

```python
def selected_month(self) -> int | None:
        if self._month_combo is None:
            return None
        return self._month_combo.currentIndex() + 1
```

</details>

### ⚙️ Method `selected_year`

```python
def selected_year(self) -> int
```

Return the selected calendar year.

<details>
<summary>Code:</summary>

```python
def selected_year(self) -> int:
        return int(self._year_combo.currentText())
```

</details>

## 🔧 Function `last_calendar_month`

```python
def last_calendar_month(*, now: datetime | None = None) -> tuple[int, int]
```

Return `(year, month)` for the previous calendar month.

<details>
<summary>Code:</summary>

```python
def last_calendar_month(*, now: datetime | None = None) -> tuple[int, int]:
    current = now or datetime.now(UTC).astimezone()
    if current.month == 1:
        return current.year - 1, 12
    return current.year, current.month - 1
```

</details>

## 🔧 Function `last_calendar_year`

```python
def last_calendar_year(*, now: datetime | None = None) -> int
```

Return the previous calendar year.

<details>
<summary>Code:</summary>

```python
def last_calendar_year(*, now: datetime | None = None) -> int:
    current = now or datetime.now(UTC).astimezone()
    return current.year - 1
```

</details>
