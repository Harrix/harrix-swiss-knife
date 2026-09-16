---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `day_macros_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DayMacrosDialog`](#%EF%B8%8F-class-daymacrosdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `set_analysis`](#%EF%B8%8F-method-set_analysis)
  - [⚙️ Method `set_busy`](#%EF%B8%8F-method-set_busy)

</details>

## 🏛️ Class `DayMacrosDialog`

```python
class DayMacrosDialog(QDialog)
```

Show one day's approximate P/F/C intake against AI daily norms.

Attributes:

- [`day`](../habits/dashboard_widgets.g.md#%EF%B8%8F-method-day) (`str`): Calendar date `YYYY-MM-DD`.
- `refresh_requested` (`Signal`): Emitted when the user asks to (re)run AI.

<details>
<summary>Code:</summary>

```python
class DayMacrosDialog(QDialog):

    refresh_requested = Signal()

    def __init__(
        self,
        parent: QWidget | None,
        day: str,
        analysis: FoodDayMacrosAnalysis | None,
        status: DayMacrosStatus,
    ) -> None:
        """Build the dialog for `day`.

        Args:

        - `parent` (`QWidget | None`): Parent window.
        - `day` (`str`): Date shown in the title.
        - `analysis` (`FoodDayMacrosAnalysis | None`): Cached row, if any.
        - `status` (`DayMacrosStatus`): `missing` / `ok` / `stale` vs current log.

        """
        super().__init__(parent)
        self.day = day
        self.setWindowTitle(f"Day macros — {day}")
        self.setMinimumWidth(420)
        qt_modality.set_owner_window_modal(self)

        self._status_label = QLabel("")
        self._verdict_label = QLabel("")
        self._verdict_label.setWordWrap(True)
        self._notes_edit = QTextEdit()
        self._notes_edit.setReadOnly(True)
        self._notes_edit.setMaximumHeight(140)

        self._protein_label = QLabel("")
        self._fat_label = QLabel("")
        self._carb_label = QLabel("")
        self._kcal_label = QLabel("")

        form = QFormLayout()
        form.addRow("Protein", self._protein_label)
        form.addRow("Fat", self._fat_label)
        form.addRow("Carbs", self._carb_label)
        form.addRow("kcal", self._kcal_label)

        self._analyze_button = make_lucide_push_button("Analyze", "sparkles", parent=self)
        self._refresh_button = make_lucide_push_button("Refresh", "refresh-cw", parent=self)
        self._analyze_button.clicked.connect(self.refresh_requested.emit)
        self._refresh_button.clicked.connect(self.refresh_requested.emit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        apply_lucide_dialog_buttons(button_box)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(self._analyze_button)
        buttons_row.addWidget(self._refresh_button)
        buttons_row.addStretch(1)
        buttons_row.addWidget(button_box)

        layout = QVBoxLayout(self)
        layout.addWidget(self._status_label)
        layout.addLayout(form)
        layout.addWidget(QLabel("Verdict"))
        layout.addWidget(self._verdict_label)
        layout.addWidget(QLabel("Advice"))
        layout.addWidget(self._notes_edit)
        layout.addLayout(buttons_row)

        self.set_analysis(analysis, status)

    def set_analysis(self, analysis: FoodDayMacrosAnalysis | None, status: DayMacrosStatus) -> None:
        """Update labels from a persisted analysis and freshness status."""
        self._status_label.setText(f"Status: {status.value}")
        needs_ai = status in {DayMacrosStatus.MISSING, DayMacrosStatus.STALE}
        self._analyze_button.setVisible(needs_ai)
        self._refresh_button.setVisible(analysis is not None)
        if analysis is None:
            self._protein_label.setText("—")
            self._fat_label.setText("—")
            self._carb_label.setText("—")
            self._kcal_label.setText("—")
            self._verdict_label.setText("No analysis yet. Run Analyze.")
            self._notes_edit.clear()
            return
        self._protein_label.setText(_format_vs_norm(analysis.protein_g, analysis.norm_protein_g, "g"))
        self._fat_label.setText(_format_vs_norm(analysis.fat_g, analysis.norm_fat_g, "g"))
        self._carb_label.setText(_format_vs_norm(analysis.carb_g, analysis.norm_carb_g, "g"))
        self._kcal_label.setText(_format_vs_norm(analysis.kcal, analysis.norm_kcal, "kcal"))
        self._verdict_label.setText(analysis.verdict.strip() or "—")
        self._notes_edit.setPlainText(analysis.notes.strip())

    def set_busy(self, *, busy: bool) -> None:
        """Disable analyze/refresh while a BotHub request is in flight."""
        self._analyze_button.setEnabled(not busy)
        self._refresh_button.setEnabled(not busy)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, day: str, analysis: FoodDayMacrosAnalysis | None, status: DayMacrosStatus) -> None
```

Build the dialog for [`day`](../habits/dashboard_widgets.g.md#%EF%B8%8F-method-day).

Args:

- `parent` (`QWidget | None`): Parent window.
- [`day`](../habits/dashboard_widgets.g.md#%EF%B8%8F-method-day) (`str`): Date shown in the title.
- `analysis` (`FoodDayMacrosAnalysis | None`): Cached row, if any.
- `status` ([`DayMacrosStatus`](day_macros.g.md#%EF%B8%8F-class-daymacrosstatus)): `missing` / `ok` / `stale` vs current log.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        day: str,
        analysis: FoodDayMacrosAnalysis | None,
        status: DayMacrosStatus,
    ) -> None:
        super().__init__(parent)
        self.day = day
        self.setWindowTitle(f"Day macros — {day}")
        self.setMinimumWidth(420)
        qt_modality.set_owner_window_modal(self)

        self._status_label = QLabel("")
        self._verdict_label = QLabel("")
        self._verdict_label.setWordWrap(True)
        self._notes_edit = QTextEdit()
        self._notes_edit.setReadOnly(True)
        self._notes_edit.setMaximumHeight(140)

        self._protein_label = QLabel("")
        self._fat_label = QLabel("")
        self._carb_label = QLabel("")
        self._kcal_label = QLabel("")

        form = QFormLayout()
        form.addRow("Protein", self._protein_label)
        form.addRow("Fat", self._fat_label)
        form.addRow("Carbs", self._carb_label)
        form.addRow("kcal", self._kcal_label)

        self._analyze_button = make_lucide_push_button("Analyze", "sparkles", parent=self)
        self._refresh_button = make_lucide_push_button("Refresh", "refresh-cw", parent=self)
        self._analyze_button.clicked.connect(self.refresh_requested.emit)
        self._refresh_button.clicked.connect(self.refresh_requested.emit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        apply_lucide_dialog_buttons(button_box)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(self._analyze_button)
        buttons_row.addWidget(self._refresh_button)
        buttons_row.addStretch(1)
        buttons_row.addWidget(button_box)

        layout = QVBoxLayout(self)
        layout.addWidget(self._status_label)
        layout.addLayout(form)
        layout.addWidget(QLabel("Verdict"))
        layout.addWidget(self._verdict_label)
        layout.addWidget(QLabel("Advice"))
        layout.addWidget(self._notes_edit)
        layout.addLayout(buttons_row)

        self.set_analysis(analysis, status)
```

</details>

### ⚙️ Method `set_analysis`

```python
def set_analysis(self, analysis: FoodDayMacrosAnalysis | None, status: DayMacrosStatus) -> None
```

Update labels from a persisted analysis and freshness status.

<details>
<summary>Code:</summary>

```python
def set_analysis(self, analysis: FoodDayMacrosAnalysis | None, status: DayMacrosStatus) -> None:
        self._status_label.setText(f"Status: {status.value}")
        needs_ai = status in {DayMacrosStatus.MISSING, DayMacrosStatus.STALE}
        self._analyze_button.setVisible(needs_ai)
        self._refresh_button.setVisible(analysis is not None)
        if analysis is None:
            self._protein_label.setText("—")
            self._fat_label.setText("—")
            self._carb_label.setText("—")
            self._kcal_label.setText("—")
            self._verdict_label.setText("No analysis yet. Run Analyze.")
            self._notes_edit.clear()
            return
        self._protein_label.setText(_format_vs_norm(analysis.protein_g, analysis.norm_protein_g, "g"))
        self._fat_label.setText(_format_vs_norm(analysis.fat_g, analysis.norm_fat_g, "g"))
        self._carb_label.setText(_format_vs_norm(analysis.carb_g, analysis.norm_carb_g, "g"))
        self._kcal_label.setText(_format_vs_norm(analysis.kcal, analysis.norm_kcal, "kcal"))
        self._verdict_label.setText(analysis.verdict.strip() or "—")
        self._notes_edit.setPlainText(analysis.notes.strip())
```

</details>

### ⚙️ Method `set_busy`

```python
def set_busy(self, *, busy: bool) -> None
```

Disable analyze/refresh while a BotHub request is in flight.

<details>
<summary>Code:</summary>

```python
def set_busy(self, *, busy: bool) -> None:
        self._analyze_button.setEnabled(not busy)
        self._refresh_button.setEnabled(not busy)
```

</details>
