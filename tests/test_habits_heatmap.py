"""Tests for habit calendar heatmap labels."""

from __future__ import annotations

from datetime import date

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow

from harrix_swiss_knife.apps.habits.main import (
    HEATMAP_MONTH_GAP,
    habit_heatmap_month_ranges,
    habit_heatmap_month_separated_positions,
    habit_heatmap_weekday_index,
    heatmap_year_after_step,
    numeric_habit_heatmap_cell_labels,
)
from harrix_swiss_knife.apps.habits.window import Ui_MainWindow


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Charts UI widgets."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_habits_charts_heatmap_year_buttons_exist(qapp: QApplication) -> None:
    """Calendar Heatmap has dashboard-style prev/next year buttons at the top."""
    assert qapp is not None
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    assert ui.pushButton_charts_heatmap_prev_year.text() == "←"
    assert ui.pushButton_charts_heatmap_next_year.text() == "→"
    assert ui.pushButton_charts_heatmap_prev_year.toolTip() == "Previous year"
    assert ui.pushButton_charts_heatmap_next_year.toolTip() == "Next year"


def test_heatmap_year_after_step_walks_available_years() -> None:
    """Prev/next arrows move through years in the Charts filter, never past today."""
    years = [2026, 2024, 2020]
    assert heatmap_year_after_step("Last 365 days", years, step=-1, today_year=2026) == 2026
    assert heatmap_year_after_step("Last 365 days", years, step=1, today_year=2026) is None
    assert heatmap_year_after_step("2026", years, step=-1, today_year=2026) == 2024
    assert heatmap_year_after_step("2026", years, step=1, today_year=2026) is None
    assert heatmap_year_after_step("2024", years, step=1, today_year=2026) == 2026
    assert heatmap_year_after_step("2024", years, step=-1, today_year=2026) == 2020
    assert heatmap_year_after_step("2020", years, step=-1, today_year=2026) is None
    assert heatmap_year_after_step("2024", [2027, 2024], step=1, today_year=2026) is None
    assert heatmap_year_after_step("2024", [], step=-1, today_year=2026) is None


def test_numeric_habit_heatmap_cell_labels_skips_zero() -> None:
    """Only non-zero values are labeled, in calendar-cell order."""
    start = date(2026, 1, 1)
    labels = numeric_habit_heatmap_cell_labels(
        start,
        5,
        {
            date(2026, 1, 1): 0,
            date(2026, 1, 2): 3,
            date(2026, 1, 4): -2,
        },
    )
    assert labels == [(1, 3), (3, -2)]


def test_habit_heatmap_weekday_index_sunday_first() -> None:
    """Sunday is the first heatmap row, matching dayplot and LeetCode."""
    assert habit_heatmap_weekday_index(date(2025, 2, 2)) == 0
    assert habit_heatmap_weekday_index(date(2025, 2, 3)) == 1
    assert habit_heatmap_weekday_index(date(2025, 2, 8)) == 6


def test_habit_heatmap_month_ranges_keeps_partial_months() -> None:
    """Visible month blocks follow the requested date range, not full calendar months."""
    assert habit_heatmap_month_ranges(date(2026, 1, 15), date(2026, 3, 10)) == [
        (date(2026, 1, 15), date(2026, 1, 31)),
        (date(2026, 2, 1), date(2026, 2, 28)),
        (date(2026, 3, 1), date(2026, 3, 10)),
    ]


def test_habit_heatmap_month_separated_positions_splits_shared_week() -> None:
    """A week that spans two months is split into two month blocks with a gap."""
    positions, month_labels, total_width = habit_heatmap_month_separated_positions(
        date(2025, 1, 1),
        date(2025, 2, 1),
    )
    january_friday = positions[date(2025, 1, 31)]
    february_saturday = positions[date(2025, 2, 1)]

    assert january_friday[0] == 4
    assert january_friday[1] == 5
    assert february_saturday[0] == 5 + HEATMAP_MONTH_GAP
    assert february_saturday[1] == 6
    assert february_saturday[0] > january_friday[0]
    assert [label for label, _x in month_labels] == ["Jan", "Feb"]
    assert month_labels[1][1] == 5 + HEATMAP_MONTH_GAP
    assert total_width == 6 + HEATMAP_MONTH_GAP
