"""Period pickers for Month Summary / Year Summary reports."""

from __future__ import annotations

from datetime import UTC, datetime

from PySide6.QtCore import Qt, Signal
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
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, SPACE_S, SPACE_XS
from harrix_swiss_knife.fluent.widgets import FluentComboBox
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_dialog_buttons

MONTH_NAMES: list[str] = [
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


class ReportPeriodBar(QWidget):
    """Inline month/year controls shown above Month Summary / Year Summary."""

    period_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create month and year combo boxes in a horizontal row."""
        super().__init__(parent)
        self.setObjectName("reportPeriodBar")
        self._mode = "month"
        self._syncing = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, SPACE_XS)
        layout.setSpacing(SPACE_S)

        self._month_label = QLabel("Month:", self)
        self._month_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._month_label)
        self._month_combo = FluentComboBox(self, items=MONTH_NAMES)
        self._month_combo.setMinimumWidth(140)
        self._month_combo.setFixedHeight(CONTROL_HEIGHT)
        layout.addWidget(self._month_combo)

        self._year_label = QLabel("Year:", self)
        self._year_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._year_label)
        self._year_combo = FluentComboBox(self)
        self._year_combo.setMinimumWidth(96)
        self._year_combo.setFixedHeight(CONTROL_HEIGHT)
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
            self._year_combo.blockSignals(True)  # noqa: FBT003
            self._month_combo.blockSignals(True)  # noqa: FBT003
            self._year_combo.clear()
            self._year_combo.addItems([str(y) for y in year_choices])
            self._year_combo.setCurrentText(str(year))
            if month is not None:
                self._month_combo.setCurrentIndex(max(0, min(11, month - 1)))
        finally:
            self._year_combo.blockSignals(False)  # noqa: FBT003
            self._month_combo.blockSignals(False)  # noqa: FBT003
            self._syncing = False

    def _emit_period_changed(self, *_args: object) -> None:
        if self._syncing:
            return
        self.period_changed.emit()


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


def last_calendar_month(*, now: datetime | None = None) -> tuple[int, int]:
    """Return `(year, month)` for the previous calendar month."""
    current = now or datetime.now(UTC).astimezone()
    if current.month == 1:
        return current.year - 1, 12
    return current.year, current.month - 1


def last_calendar_year(*, now: datetime | None = None) -> int:
    """Return the previous calendar year."""
    current = now or datetime.now(UTC).astimezone()
    return current.year - 1
