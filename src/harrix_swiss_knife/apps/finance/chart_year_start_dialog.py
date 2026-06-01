"""Dialog to pick the day and month when a comparison year begins."""

from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


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
