---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `day_macros_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AdviceMacrosDialogBase`](#%EF%B8%8F-class-advicemacrosdialogbase)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `set_busy`](#%EF%B8%8F-method-set_busy)
- [🏛️ Class `DayMacrosDialog`](#%EF%B8%8F-class-daymacrosdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `set_analysis`](#%EF%B8%8F-method-set_analysis)
- [🏛️ Class `MacroValueRow`](#%EF%B8%8F-class-macrovaluerow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `set_value`](#%EF%B8%8F-method-set_value)
- [🏛️ Class `RangeMacrosDialog`](#%EF%B8%8F-class-rangemacrosdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `set_range_analysis`](#%EF%B8%8F-method-set_range_analysis)

</details>

## 🏛️ Class `AdviceMacrosDialogBase`

```python
class AdviceMacrosDialogBase(QDialog)
```

Shared shell: status, bilingual tabs, Analyze / Refresh / Delete / Close.

<details>
<summary>Code:</summary>

```python
class AdviceMacrosDialogBase(QDialog):

    refresh_requested = Signal()
    delete_requested = Signal()

    def __init__(
        self,
        parent: QWidget | None,
        *,
        title: str,
        local_language_label: str,
        show_macro_rows: bool,
    ) -> None:
        """Build the shared macros dialog chrome."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(560, 640)
        self.resize(600, 720)
        qt_modality.set_owner_window_modal(self)
        self._local_tab_label = local_language_label.strip() or "Local"
        self._build_ui(show_macro_rows=show_macro_rows)

    def set_busy(self, *, busy: bool) -> None:
        """Disable action buttons while a BotHub request is in flight."""
        self._analyze_button.setEnabled(not busy)
        self._refresh_button.setEnabled(not busy)
        self._delete_button.setEnabled(not busy)

    def _apply_text(
        self,
        *,
        status: DayMacrosStatus,
        analysis_present: bool,
        verdict_local: str,
        verdict_en: str,
        notes_local: str,
        notes_en: str,
        empty_message: str,
    ) -> None:
        self._status_label.setText(f"Status: {status.value}")
        needs_ai = status in {DayMacrosStatus.MISSING, DayMacrosStatus.STALE}
        self._analyze_button.setVisible(needs_ai or not analysis_present)
        self._refresh_button.setVisible(True)
        self._delete_button.setVisible(analysis_present)
        if not analysis_present:
            self._verdict_local.setText(empty_message)
            self._verdict_en.setText(empty_message)
            _set_advice_markdown(self._notes_local, "")
            _set_advice_markdown(self._notes_en, "")
            return
        self._verdict_local.setText(verdict_local or verdict_en or "—")
        self._verdict_en.setText(verdict_en or verdict_local or "—")
        _set_advice_markdown(self._notes_local, notes_local or notes_en)
        _set_advice_markdown(self._notes_en, notes_en or notes_local)

    def _build_ui(self, *, show_macro_rows: bool) -> None:
        self._status_label = QLabel("")
        self._protein_row = MacroValueRow()
        self._fat_row = MacroValueRow()
        self._carb_row = MacroValueRow()
        self._kcal_row = MacroValueRow()

        form = QFormLayout()
        if show_macro_rows:
            form.addRow("Protein", self._protein_row)
            form.addRow("Fat", self._fat_row)
            form.addRow("Carbs", self._carb_row)
            form.addRow("kcal", self._kcal_row)

        self._verdict_local = QLabel("")
        self._verdict_local.setWordWrap(True)
        self._verdict_en = QLabel("")
        self._verdict_en.setWordWrap(True)
        self._notes_local = _make_advice_browser()
        self._notes_en = _make_advice_browser()

        local_page = QWidget()
        local_layout = QVBoxLayout(local_page)
        local_layout.addWidget(QLabel("Verdict"))
        local_layout.addWidget(self._verdict_local)
        local_layout.addWidget(QLabel("Advice"))
        local_layout.addWidget(self._notes_local, 1)

        en_page = QWidget()
        en_layout = QVBoxLayout(en_page)
        en_layout.addWidget(QLabel("Verdict"))
        en_layout.addWidget(self._verdict_en)
        en_layout.addWidget(QLabel("Advice"))
        en_layout.addWidget(self._notes_en, 1)

        self._tabs = QTabWidget()
        self._tabs.addTab(local_page, self._local_tab_label)
        self._tabs.addTab(en_page, "English")
        preferred = load_macros_preferred_text_language()
        self._tabs.setCurrentIndex(1 if preferred == "en" else 0)
        self._tabs.currentChanged.connect(self._on_tab_changed)

        self._analyze_button = make_lucide_push_button("Analyze", "sparkles", parent=self)
        self._refresh_button = make_lucide_push_button("Refresh", "refresh-cw", parent=self)
        self._delete_button = make_lucide_push_button("Delete", "trash", parent=self)
        self._analyze_button.clicked.connect(self.refresh_requested.emit)
        self._refresh_button.clicked.connect(self.refresh_requested.emit)
        self._delete_button.clicked.connect(self.delete_requested.emit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        apply_lucide_dialog_buttons(button_box)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(self._analyze_button)
        buttons_row.addWidget(self._refresh_button)
        buttons_row.addWidget(self._delete_button)
        buttons_row.addStretch(1)
        buttons_row.addWidget(button_box)

        layout = QVBoxLayout(self)
        layout.addWidget(self._status_label)
        layout.addLayout(form)
        layout.addWidget(self._tabs, 1)
        layout.addLayout(buttons_row)

    def _on_tab_changed(self, index: int) -> None:
        lang: MacrosTextLanguage = "en" if index == 1 else "local"
        save_macros_preferred_text_language(lang)

    def _set_macro_row(self, row: MacroValueRow, text: str, tone: MacroTone) -> None:
        row.set_value(text, tone)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, *, title: str, local_language_label: str, show_macro_rows: bool) -> None
```

Build the shared macros dialog chrome.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        *,
        title: str,
        local_language_label: str,
        show_macro_rows: bool,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(560, 640)
        self.resize(600, 720)
        qt_modality.set_owner_window_modal(self)
        self._local_tab_label = local_language_label.strip() or "Local"
        self._build_ui(show_macro_rows=show_macro_rows)
```

</details>

### ⚙️ Method `set_busy`

```python
def set_busy(self, *, busy: bool) -> None
```

Disable action buttons while a BotHub request is in flight.

<details>
<summary>Code:</summary>

```python
def set_busy(self, *, busy: bool) -> None:
        self._analyze_button.setEnabled(not busy)
        self._refresh_button.setEnabled(not busy)
        self._delete_button.setEnabled(not busy)
```

</details>

## 🏛️ Class `DayMacrosDialog`

```python
class DayMacrosDialog(AdviceMacrosDialogBase)
```

Show one day's approximate P/F/C intake against AI daily norms.

<details>
<summary>Code:</summary>

```python
class DayMacrosDialog(AdviceMacrosDialogBase):

    def __init__(
        self,
        parent: QWidget | None,
        day: str,
        analysis: FoodDayMacrosAnalysis | None,
        status: DayMacrosStatus,
        *,
        thresholds: CalorieThresholds | None = None,
        local_language_label: str = "Local",
    ) -> None:
        """Open the day macros dialog for `day`."""
        self.day = day
        self._thresholds = thresholds or CalorieThresholds()
        super().__init__(
            parent,
            title=f"Day macros — {day}",
            local_language_label=local_language_label,
            show_macro_rows=True,
        )
        self.set_analysis(analysis, status)

    def set_analysis(self, analysis: FoodDayMacrosAnalysis | None, status: DayMacrosStatus) -> None:
        """Update labels from a persisted analysis and freshness status."""
        if analysis is None:
            self._set_macro_row(self._protein_row, "—", "neutral")
            self._set_macro_row(self._fat_row, "—", "neutral")
            self._set_macro_row(self._carb_row, "—", "neutral")
            self._set_macro_row(self._kcal_row, "—", "neutral")
            self._apply_text(
                status=status,
                analysis_present=False,
                verdict_local="",
                verdict_en="",
                notes_local="",
                notes_en="",
                empty_message="No analysis yet. Run Analyze.",
            )
            return
        self._set_macro_row(
            self._protein_row,
            _format_vs_norm(analysis.protein_g, analysis.norm_protein_g, "g"),
            macro_tone(analysis.protein_g, analysis.norm_protein_g),
        )
        self._set_macro_row(
            self._fat_row,
            _format_vs_norm(analysis.fat_g, analysis.norm_fat_g, "g"),
            macro_tone(analysis.fat_g, analysis.norm_fat_g),
        )
        self._set_macro_row(
            self._carb_row,
            _format_vs_norm(analysis.carb_g, analysis.norm_carb_g, "g"),
            macro_tone(analysis.carb_g, analysis.norm_carb_g),
        )
        self._set_macro_row(
            self._kcal_row,
            _format_vs_norm(analysis.kcal, analysis.norm_kcal, "kcal"),
            _combine_tones(
                macro_tone(analysis.kcal, analysis.norm_kcal),
                kcal_tone(analysis.kcal, self._thresholds),
            ),
        )
        self._apply_text(
            status=status,
            analysis_present=True,
            verdict_local=analysis.verdict.strip(),
            verdict_en=analysis.verdict_en.strip(),
            notes_local=analysis.notes.strip(),
            notes_en=analysis.notes_en.strip(),
            empty_message="",
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, day: str, analysis: FoodDayMacrosAnalysis | None, status: DayMacrosStatus, *, thresholds: CalorieThresholds | None = None, local_language_label: str = 'Local') -> None
```

Open the day macros dialog for [`day`](../habits/dashboard_widgets.g.md#%EF%B8%8F-method-day).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        day: str,
        analysis: FoodDayMacrosAnalysis | None,
        status: DayMacrosStatus,
        *,
        thresholds: CalorieThresholds | None = None,
        local_language_label: str = "Local",
    ) -> None:
        self.day = day
        self._thresholds = thresholds or CalorieThresholds()
        super().__init__(
            parent,
            title=f"Day macros — {day}",
            local_language_label=local_language_label,
            show_macro_rows=True,
        )
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
        if analysis is None:
            self._set_macro_row(self._protein_row, "—", "neutral")
            self._set_macro_row(self._fat_row, "—", "neutral")
            self._set_macro_row(self._carb_row, "—", "neutral")
            self._set_macro_row(self._kcal_row, "—", "neutral")
            self._apply_text(
                status=status,
                analysis_present=False,
                verdict_local="",
                verdict_en="",
                notes_local="",
                notes_en="",
                empty_message="No analysis yet. Run Analyze.",
            )
            return
        self._set_macro_row(
            self._protein_row,
            _format_vs_norm(analysis.protein_g, analysis.norm_protein_g, "g"),
            macro_tone(analysis.protein_g, analysis.norm_protein_g),
        )
        self._set_macro_row(
            self._fat_row,
            _format_vs_norm(analysis.fat_g, analysis.norm_fat_g, "g"),
            macro_tone(analysis.fat_g, analysis.norm_fat_g),
        )
        self._set_macro_row(
            self._carb_row,
            _format_vs_norm(analysis.carb_g, analysis.norm_carb_g, "g"),
            macro_tone(analysis.carb_g, analysis.norm_carb_g),
        )
        self._set_macro_row(
            self._kcal_row,
            _format_vs_norm(analysis.kcal, analysis.norm_kcal, "kcal"),
            _combine_tones(
                macro_tone(analysis.kcal, analysis.norm_kcal),
                kcal_tone(analysis.kcal, self._thresholds),
            ),
        )
        self._apply_text(
            status=status,
            analysis_present=True,
            verdict_local=analysis.verdict.strip(),
            verdict_en=analysis.verdict_en.strip(),
            notes_local=analysis.notes.strip(),
            notes_en=analysis.notes_en.strip(),
            empty_message="",
        )
```

</details>

## 🏛️ Class `MacroValueRow`

```python
class MacroValueRow(QWidget)
```

One intake-vs-norm line with a tone icon; warn/bad stay colored.

<details>
<summary>Code:</summary>

```python
class MacroValueRow(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the icon + text row."""
        super().__init__(parent)
        self._icon = QLabel()
        self._icon.setFixedSize(20, 20)
        self._text = QLabel("")
        self._text.setWordWrap(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self._text, 1)

    def set_value(self, text: str, tone: MacroTone) -> None:
        """Set the displayed value text and tone icon/color."""
        color = _TONE_COLORS[tone]
        self._text.setText(text)
        self._text.setStyleSheet(f"color: {color}; font-weight: 600;")
        icon_name = _TONE_ICONS[tone]
        icon_color = QColor(_TONE_ICON_COLORS[tone])
        self._icon.setPixmap(create_lucide_icon(icon_name, 18, color=icon_color).pixmap(18, 18))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create the icon + text row.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._icon = QLabel()
        self._icon.setFixedSize(20, 20)
        self._text = QLabel("")
        self._text.setWordWrap(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self._text, 1)
```

</details>

### ⚙️ Method `set_value`

```python
def set_value(self, text: str, tone: MacroTone) -> None
```

Set the displayed value text and tone icon/color.

<details>
<summary>Code:</summary>

```python
def set_value(self, text: str, tone: MacroTone) -> None:
        color = _TONE_COLORS[tone]
        self._text.setText(text)
        self._text.setStyleSheet(f"color: {color}; font-weight: 600;")
        icon_name = _TONE_ICONS[tone]
        icon_color = QColor(_TONE_ICON_COLORS[tone])
        self._icon.setPixmap(create_lucide_icon(icon_name, 18, color=icon_color).pixmap(18, 18))
```

</details>

## 🏛️ Class `RangeMacrosDialog`

```python
class RangeMacrosDialog(AdviceMacrosDialogBase)
```

Show a multi-day macros summary (verdict and advice).

<details>
<summary>Code:</summary>

```python
class RangeMacrosDialog(AdviceMacrosDialogBase):

    def __init__(
        self,
        parent: QWidget | None,
        date_from: str,
        date_to: str,
        analysis: FoodRangeMacrosAnalysis | None,
        status: DayMacrosStatus,
        *,
        local_language_label: str = "Local",
    ) -> None:
        """Open the period macros dialog for `date_from`…`date_to`."""
        self.date_from = date_from
        self.date_to = date_to
        super().__init__(
            parent,
            title=f"Period macros — {date_from} … {date_to}",
            local_language_label=local_language_label,
            show_macro_rows=False,
        )
        self.set_range_analysis(analysis, status)

    def set_range_analysis(self, analysis: FoodRangeMacrosAnalysis | None, status: DayMacrosStatus) -> None:
        """Update bilingual text from a persisted range analysis."""
        if analysis is None:
            self._apply_text(
                status=status,
                analysis_present=False,
                verdict_local="",
                verdict_en="",
                notes_local="",
                notes_en="",
                empty_message="No period analysis yet. Run Analyze.",
            )
            return
        self._apply_text(
            status=status,
            analysis_present=True,
            verdict_local=analysis.verdict.strip(),
            verdict_en=analysis.verdict_en.strip(),
            notes_local=analysis.notes.strip(),
            notes_en=analysis.notes_en.strip(),
            empty_message="",
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, date_from: str, date_to: str, analysis: FoodRangeMacrosAnalysis | None, status: DayMacrosStatus, *, local_language_label: str = 'Local') -> None
```

Open the period macros dialog for `date_from`…`date_to`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        date_from: str,
        date_to: str,
        analysis: FoodRangeMacrosAnalysis | None,
        status: DayMacrosStatus,
        *,
        local_language_label: str = "Local",
    ) -> None:
        self.date_from = date_from
        self.date_to = date_to
        super().__init__(
            parent,
            title=f"Period macros — {date_from} … {date_to}",
            local_language_label=local_language_label,
            show_macro_rows=False,
        )
        self.set_range_analysis(analysis, status)
```

</details>

### ⚙️ Method `set_range_analysis`

```python
def set_range_analysis(self, analysis: FoodRangeMacrosAnalysis | None, status: DayMacrosStatus) -> None
```

Update bilingual text from a persisted range analysis.

<details>
<summary>Code:</summary>

```python
def set_range_analysis(self, analysis: FoodRangeMacrosAnalysis | None, status: DayMacrosStatus) -> None:
        if analysis is None:
            self._apply_text(
                status=status,
                analysis_present=False,
                verdict_local="",
                verdict_en="",
                notes_local="",
                notes_en="",
                empty_message="No period analysis yet. Run Analyze.",
            )
            return
        self._apply_text(
            status=status,
            analysis_present=True,
            verdict_local=analysis.verdict.strip(),
            verdict_en=analysis.verdict_en.strip(),
            notes_local=analysis.notes.strip(),
            notes_en=analysis.notes_en.strip(),
            empty_message="",
        )
```

</details>
