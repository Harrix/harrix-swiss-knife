"""Dialog showing AI day macros intake versus suggested norms."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.food.day_macros import (
    DayMacrosStatus,
    FoodDayMacrosAnalysis,
    percent_of_norm,
)
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_dialog_buttons, make_lucide_push_button


class DayMacrosDialog(QDialog):
    """Show one day's approximate P/F/C intake against AI daily norms.

    Attributes:

    - `day` (`str`): Calendar date `YYYY-MM-DD`.
    - `refresh_requested` (`Signal`): Emitted when the user asks to (re)run AI.

    """

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


def _format_vs_norm(value: float, norm: float, unit: str) -> str:
    pct = percent_of_norm(value, norm)
    pct_text = f" ({pct:.0f}% of norm)" if pct is not None else ""
    return f"{value:.1f} {unit} / norm {norm:.1f} {unit}{pct_text}"
