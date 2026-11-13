"""Tests for Matplotlib chart hover tooltip helpers."""

from __future__ import annotations

from datetime import date, datetime

from harrix_swiss_knife.apps.common.chart_hover import format_chart_point
from harrix_swiss_knife.apps.habits.ticktick_task_stats import heatmap_cell_tooltip


def test_format_chart_point_formats_dates_and_numbers() -> None:
    """Hover text is readable for dates and numeric values."""
    assert format_chart_point(date(2024, 1, 2), 3) == "2024-01-02: 3"
    assert format_chart_point(datetime(2024, 1, 2, 15, 30, 0), 1.5) == "2024-01-02 15:30: 1.5"  # noqa: DTZ001
    assert format_chart_point(10, 7, label="Weight") == "Weight: 10 → 7"


def test_heatmap_cell_tooltip_keeps_task_wording() -> None:
    """TickTick calendar hover keeps task-oriented wording."""
    assert heatmap_cell_tooltip(date(2024, 1, 2), 2) == "2024-01-02: 2 tasks"
