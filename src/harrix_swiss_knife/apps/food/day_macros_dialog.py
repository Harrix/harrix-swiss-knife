"""Dialog showing AI day or range macros with bilingual advice."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.food.day_macros import (
    CalorieThresholds,
    DayMacrosStatus,
    FoodDayMacrosAnalysis,
    FoodRangeMacrosAnalysis,
    MacroTone,
    kcal_tone,
    macro_tone,
    percent_of_norm,
)
from harrix_swiss_knife.apps.food.day_macros_prefs import (
    MacrosTextLanguage,
    load_macros_preferred_text_language,
    save_macros_preferred_text_language,
)
from harrix_swiss_knife.qt_lucide_icon import (
    apply_lucide_dialog_buttons,
    create_lucide_icon,
    make_lucide_push_button,
)

_TONE_COLORS: dict[MacroTone, str] = {
    "good": "#15803D",
    "warn": "#A16207",
    "bad": "#B91C1C",
    "neutral": "#4B5563",
}
_TONE_ICONS: dict[MacroTone, str] = {
    "good": "circle-check",
    "warn": "triangle-alert",
    "bad": "circle-x",
    "neutral": "minus",
}


class AdviceMacrosDialogBase(QDialog):
    """Shared shell: status, bilingual tabs, Analyze / Refresh / Delete / Close."""

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
            self._notes_local.clear()
            self._notes_en.clear()
            return
        self._verdict_local.setText(verdict_local or verdict_en or "—")
        self._verdict_en.setText(verdict_en or verdict_local or "—")
        self._notes_local.setPlainText(notes_local or notes_en)
        self._notes_en.setPlainText(notes_en or notes_local)

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
        self._notes_local = QTextEdit()
        self._notes_local.setReadOnly(True)
        self._notes_local.setMinimumHeight(220)
        self._notes_local.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._notes_en = QTextEdit()
        self._notes_en.setReadOnly(True)
        self._notes_en.setMinimumHeight(220)
        self._notes_en.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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


class DayMacrosDialog(AdviceMacrosDialogBase):
    """Show one day's approximate P/F/C intake against AI daily norms."""

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


class MacroValueRow(QWidget):
    """One intake-vs-norm line with a tone icon and colored text."""

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
        self._icon.setPixmap(create_lucide_icon(icon_name, 18, color=QColor(color)).pixmap(18, 18))


class RangeMacrosDialog(AdviceMacrosDialogBase):
    """Show a multi-day macros summary (verdict and advice)."""

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


def _combine_tones(a: MacroTone, b: MacroTone) -> MacroTone:
    order = {"good": 0, "neutral": 1, "warn": 2, "bad": 3}
    return a if order[a] >= order[b] else b


def _format_vs_norm(value: float, norm: float, unit: str) -> str:
    pct = percent_of_norm(value, norm)
    pct_text = f" ({pct:.0f}% of norm)" if pct is not None else ""
    return f"{value:.1f} {unit} / norm {norm:.1f} {unit}{pct_text}"
