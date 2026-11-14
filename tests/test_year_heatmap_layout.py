"""Layout rules for the shared year heatmap and the TickTick page."""

from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import QApplication, QSplitter, QWidget

from harrix_swiss_knife.apps.common.chart_theme import quantile_intensity_ranges
from harrix_swiss_knife.apps.common.chart_timeline import TimelineBar, build_timeline_figure
from harrix_swiss_knife.apps.common.year_heatmap import heatmap_column_count
from harrix_swiss_knife.apps.habits.habit_process_charts import habit_calendar_model, habit_period_stats
from harrix_swiss_knife.apps.habits.ticktick_task_stats import task_timeline_bars
from harrix_swiss_knife.apps.habits.ticktick_task_stats_widget import TickTickTaskStatsWidget


def test_quantile_ranges_keep_an_outlier_in_its_own_upper_bin() -> None:
    """A single busy day must not push every other day into the empty color."""
    ranges = quantile_intensity_ranges([1, 1, 2, 3, 4, 5, 8, 145])
    assert ranges
    assert ranges[0][0] == 1
    assert ranges[-1] == (145, 145) or ranges[-1][1] == 145
    assert ranges[0][1] < 50


def test_quantile_ranges_collapse_equal_values_and_ignore_zero() -> None:
    """Zero is a separate legend entry, and one repeated count is one range."""
    assert quantile_intensity_ranges([0, 0, 0]) == []
    assert quantile_intensity_ranges([4, 4, 0]) == [(4, 4)]


def test_heatmap_column_count_follows_the_visible_months() -> None:
    """Month blocks split shared weeks, so a year is not forced to 52 columns."""
    columns = heatmap_column_count(date(2024, 1, 1), date(2024, 12, 31))
    assert columns > 52


def test_habit_calendar_keeps_a_missing_day_distinct_from_zero() -> None:
    """No database row is not the same state as an explicit Not done."""
    tokens, _marks, legend, _bins = habit_calendar_model(
        {date(2024, 1, 2): 0, date(2024, 1, 3): 1},
        date(2024, 1, 1),
        date(2024, 1, 3),
        is_bool=True,
    )
    assert tokens[date(2024, 1, 1)] is None
    assert tokens[date(2024, 1, 2)] == "not_done"
    assert tokens[date(2024, 1, 3)] == "done"
    assert ("absent", "No data") in legend
    assert ("not_done", "Not done") in legend
    assert ("done", "Done") in legend


def test_habit_completion_percent_ignores_days_without_a_record() -> None:
    """Only stored done and not-done days enter the percentage."""
    stats = habit_period_stats(
        {date(2024, 1, 2): 1, date(2024, 1, 3): 0},
        date(2024, 1, 1),
        date(2024, 1, 5),
        is_bool=True,
        today=date(2024, 1, 5),
    )
    assert stats.completed == 1
    assert stats.counted == 2
    assert stats.completion_percent == 50


def test_task_timeline_keeps_zero_days_and_aggregates_a_long_range() -> None:
    """A day with no completions is a zero, and a narrow year uses week bars."""
    short, weekly_short = task_timeline_bars(
        {date(2024, 1, 1): 3},
        date(2024, 1, 1),
        date(2024, 1, 3),
        width_px=4000,
    )
    assert weekly_short is False
    assert [bar.value for bar in short] == [3, 0, 0]

    long, weekly_long = task_timeline_bars({}, date(2024, 1, 1), date(2024, 12, 31), width_px=400)
    assert weekly_long is True
    assert long
    assert long[0].end > long[0].start


def test_percent_timeline_leaves_room_above_full_bars() -> None:
    """A solid 100% habit must not weld the bars into the top edge of the plot."""
    if not isinstance(QApplication.instance(), QApplication):
        QApplication([])
    bars = [
        TimelineBar(date(2024, 1, 1), date(2024, 1, 7), 100.0, 100.0, "week"),
        TimelineBar(date(2024, 1, 8), date(2024, 1, 14), 100.0, 100.0, "week"),
    ]
    figure = build_timeline_figure(
        bars,
        title="Completion over time",
        ylabel="Completion",
        bar_label="Weekly completion",
        line_label="30-day average",
        figsize=(6.4, 3.2),
        y_max=100,
    )
    axis = figure.axes[0]
    bottom, top = axis.get_ylim()
    assert bottom == 0
    assert top > 100
    patches = axis.patches
    assert patches
    assert patches[0].get_width() < 7


def test_ticktick_heatmap_page_puts_tasks_in_a_side_column() -> None:
    """The day list is a third column, not a table beside a short heatmap."""
    if not isinstance(QApplication.instance(), QApplication):
        QApplication([])
    widget = TickTickTaskStatsWidget()
    filters = widget.findChild(QWidget, "ticktickFilters")
    day_panel = widget.findChild(QWidget, "ticktickDayPanel")
    splitter = widget.findChild(QSplitter, "ticktickBodySplitter")
    assert filters is not None
    assert day_panel is not None
    assert splitter is not None
    assert filters.minimumWidth() == 220
    assert day_panel.minimumWidth() == 240
    assert day_panel.maximumWidth() == 420
    assert splitter.indexOf(day_panel) >= 0
    assert widget.findChild(QWidget, "ticktickHeatmapTitle") is not None
    widget.close()
