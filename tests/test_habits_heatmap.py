"""Tests for habit calendar heatmap labels."""

from __future__ import annotations

from datetime import date

from harrix_swiss_knife.apps.habits.main import numeric_habit_heatmap_cell_labels


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
