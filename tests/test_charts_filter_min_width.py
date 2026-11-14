"""Charts filter columns share one minimum width across trackers."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.chart_widgets import CHARTS_FILTER_MIN_WIDTH
from harrix_swiss_knife.apps.finance import layout_chrome as finance_layout
from harrix_swiss_knife.apps.fitness import layout_chrome as fitness_layout
from harrix_swiss_knife.apps.food import layout_chrome as food_layout
from harrix_swiss_knife.apps.habits import layout_chrome as habits_layout
from harrix_swiss_knife.apps.habits.ticktick_task_stats_widget import _SIDEBAR_MIN


def test_charts_filter_min_width_is_shared() -> None:
    assert CHARTS_FILTER_MIN_WIDTH == 280
    assert fitness_layout._SIDE_MIN == CHARTS_FILTER_MIN_WIDTH
    assert habits_layout._FILTER_MIN == CHARTS_FILTER_MIN_WIDTH
    assert food_layout._STATS_LEFT_MIN == CHARTS_FILTER_MIN_WIDTH
    assert _SIDEBAR_MIN == CHARTS_FILTER_MIN_WIDTH
    # Finance Charts splitter uses the shared floor; Exchange keeps its own wider min.
    assert finance_layout._EXCHANGE_FORM_MIN_WIDTH > CHARTS_FILTER_MIN_WIDTH
