"""Dialog to pick the day and month when a comparison year begins."""

from __future__ import annotations

import calendar

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

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


class ChartYearStartDialog(QDialog):
    """Pick day and month for the start of comparison years (calendar year is ignored)."""

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

        picker_row = QHBoxLayout()
        picker_row.addWidget(QLabel("Day:"))
        self._day_combo = QComboBox(self)
        picker_row.addWidget(self._day_combo)

        picker_row.addWidget(QLabel("Month:"))
        self._month_combo = QComboBox(self)
        self._month_combo.addItems(_MONTH_NAMES)
        picker_row.addWidget(self._month_combo)

        layout.addLayout(picker_row)

        safe_month = max(1, min(12, start_month))
        safe_day = max(1, min(calendar.monthrange(2000, safe_month)[1], start_day))
        self._month_combo.setCurrentIndex(safe_month - 1)
        self._month_combo.currentIndexChanged.connect(self._on_month_changed)
        self._populate_day_combo(safe_day)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_year_start(self) -> tuple[int, int]:
        """Return `(month, day)` for the selected year start."""
        return self._month_combo.currentIndex() + 1, self._day_combo.currentIndex() + 1

    def _on_month_changed(self) -> None:
        current_day = self._day_combo.currentIndex() + 1 if self._day_combo.count() else 1
        self._populate_day_combo(current_day)

    def _populate_day_combo(self, selected_day: int) -> None:
        month = self._month_combo.currentIndex() + 1
        max_day = calendar.monthrange(2000, month)[1]
        safe_day = max(1, min(max_day, selected_day))
        self._day_combo.clear()
        self._day_combo.addItems([str(day) for day in range(1, max_day + 1)])
        self._day_combo.setCurrentIndex(safe_day - 1)
