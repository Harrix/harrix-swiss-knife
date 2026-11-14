"""Tests for Matplotlib chart hover tooltip helpers."""

from __future__ import annotations

from datetime import date, datetime

from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.chart_hover import create_chart_canvas, format_chart_point
from harrix_swiss_knife.apps.common.chart_theme import themed_figure
from harrix_swiss_knife.apps.habits.ticktick_task_stats import heatmap_cell_tooltip


def test_format_chart_point_formats_dates_and_numbers() -> None:
    """Hover text uses a readable date and a spaced number."""
    assert format_chart_point(date(2024, 1, 2), 3) == "Tue, 2 Jan 2024 — 3"
    timed = format_chart_point(datetime(2024, 1, 2, 15, 30, 0), 1.5)  # noqa: DTZ001
    assert timed.startswith("Tue, 2 Jan 2024 15:30 — ")
    assert "1" in timed
    assert format_chart_point(10, 7, label="Weight") == "10 — 7 (Weight)"


def test_hover_cursor_does_not_add_a_data_line() -> None:
    """The hover guide stays outside Matplotlib so the axis limits cannot jump."""
    if QApplication.instance() is None:
        QApplication([])
    figure = themed_figure()
    axis = figure.add_subplot(111)
    axis.plot([1.0, 2.0], [1.0, 2.0])
    limits = (axis.get_xlim(), axis.get_ylim())
    canvas = create_chart_canvas(figure)
    canvas.set_hover_cursor(120)
    canvas.set_hover_cursor(None)
    assert len(axis.lines) == 1
    assert axis.get_xlim() == limits[0]
    assert axis.get_ylim() == limits[1]
    canvas.close()


def test_heatmap_cell_tooltip_keeps_task_wording() -> None:
    """TickTick calendar hover keeps task-oriented wording."""
    assert heatmap_cell_tooltip(date(2024, 1, 2), 2) == "2024-01-02: 2 tasks"
