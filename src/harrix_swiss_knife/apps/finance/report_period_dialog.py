"""Dialogs to pick a month/year or year for period expense summaries."""

from __future__ import annotations

from datetime import UTC, datetime

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_dialog_buttons

_MONTH_NAMES: list[str] = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


class ReportPeriodDialog(QDialog):
    """Pick a calendar month+year, or a single year, for a period report."""

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
            self._month_combo.addItems(_MONTH_NAMES)
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
