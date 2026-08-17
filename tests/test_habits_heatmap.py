"""Tests for habit calendar heatmap labels."""

from __future__ import annotations

from datetime import date

from harrix_swiss_knife.apps.habits.main import (
    HEATMAP_MONTH_GAP,
    habit_heatmap_month_ranges,
    habit_heatmap_month_separated_positions,
    habit_heatmap_weekday_index,
    numeric_habit_heatmap_cell_labels,
)


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
