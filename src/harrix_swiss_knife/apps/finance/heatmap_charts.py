"""Expense calendar heatmap for the Finance Charts tab."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from harrix_swiss_knife.apps.common.calendar_heatmap import heatmap_year_bands
from harrix_swiss_knife.apps.common.chart_format import fmt_money, fmt_number
from harrix_swiss_knife.apps.common.chart_hover import create_chart_canvas, install_chart_hover
from harrix_swiss_knife.apps.common.chart_page_chrome import MetricStrip
from harrix_swiss_knife.apps.common.chart_timeline import TimelineBar, bar_at_x, build_timeline_figure
from harrix_swiss_knife.apps.common.year_heatmap import YearHeatmap, YearHeatmapStack
from harrix_swiss_knife.apps.finance.transaction_helpers import calculate_daily_expenses
from harrix_swiss_knife.apps.habits.habit_process_charts import (
    habit_calendar_model,
    habit_legend_colors,
    habit_period_stats,
    habit_timeline_bars,
    habit_token_color,
)
from harrix_swiss_knife.fluent.tokens import SPACE_S
from harrix_swiss_knife.fluent.widgets import FluentText, TextRole

if TYPE_CHECKING:
    from collections.abc import Sequence

    from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager

LAST_365_LABEL = "Last 365 days"
ALL_YEARS_LABEL = "All years"
_CHART_PERIOD_DAYS = 365
_RANGE_PERIOD_ITEMS: tuple[str, ...] = ("Days", "Months", "Years")


def daily_expense_recorded(
    rows: list[list[Any]],
    db_manager: DatabaseManager | None,
    target_currency_id: int | None = None,
) -> dict[date, int]:
    """Return daily expenses as integer cents for heatmap binning."""
    by_day = calculate_daily_expenses(rows, db_manager, target_currency_id=target_currency_id)
    recorded: dict[date, int] = {}
    for text, amount in by_day.items():
        try:
            day = date.fromisoformat(str(text)[:10])
        except ValueError:
            continue
        cents = round(float(amount) * 100)
        if cents > 0:
            recorded[day] = recorded.get(day, 0) + cents
    return recorded


def expense_years(recorded: dict[date, int], *, today: date | None = None) -> list[int]:
    """Return descending calendar years that have expense activity."""
    limit = today or datetime.now(UTC).astimezone().date()
    return sorted({day.year for day in recorded if day.year <= limit.year}, reverse=True)


def heatmap_period_choices(years: Sequence[int]) -> list[tuple[str, object]]:
    """Build ChartToolbar period choices for the expense heatmap."""
    choices: list[tuple[str, object]] = [(LAST_365_LABEL, LAST_365_LABEL), (ALL_YEARS_LABEL, ALL_YEARS_LABEL)]
    choices.extend((str(year), year) for year in years)
    return choices


def present_expense_heatmap(
    layout: QVBoxLayout,
    recorded: dict[date, int],
    *,
    selection: object,
    currency_symbol: str,
    today: date | None = None,
) -> None:
    """Fill `layout` with metrics, calendar heatmap, and optional timeline."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget() if item is not None else None
        if widget is not None:
            widget.deleteLater()

    day = today or datetime.now(UTC).astimezone().date()
    if not recorded:
        empty = FluentText("No expenses to show.", word_wrap=True, role=TextRole.SECONDARY)
        layout.addWidget(empty)
        layout.addStretch(1)
        return

    bounds = _period_bounds(selection, day)
    metrics = MetricStrip()
    layout.addWidget(metrics)

    if bounds is None:
        _present_all_years(layout, metrics, recorded, currency_symbol=currency_symbol, today=day)
        return

    start, end = bounds
    period_recorded = {key: value for key, value in recorded.items() if start <= key <= end}
    first_day = min(period_recorded) if period_recorded else None
    tokens, marks, legend, bin_count = habit_calendar_model(
        period_recorded,
        start,
        end,
        is_bool=False,
        activity_start=first_day,
        today=day,
    )
    colors = {cell: habit_token_color(state, bin_count=bin_count) for cell, state in tokens.items()}
    tips = {cell: _expense_cell_tip(cell, period_recorded.get(cell, 0), currency_symbol) for cell in tokens}
    heatmap = YearHeatmap()
    heatmap.set_calendar(
        start,
        end,
        colors,
        legend=habit_legend_colors(legend, bin_count=bin_count),
        marks=marks,
        tooltips=tips,
    )
    layout.addWidget(heatmap)

    stats = habit_period_stats(period_recorded, start, end, is_bool=False, today=day)
    metrics.set_metrics(_metric_pairs(stats, currency_symbol))

    raw_bars, _percent = habit_timeline_bars(period_recorded, start, end, is_bool=False, today=day)
    bars = [
        TimelineBar(
            bar.start,
            bar.end,
            bar.value / 100,
            None if bar.line is None else bar.line / 100,
            _expense_week_tip(bar.start, bar.end, period_recorded, currency_symbol),
        )
        for bar in raw_bars
    ]

    time_host = QWidget()
    time_layout = QVBoxLayout(time_host)
    time_layout.setContentsMargins(0, SPACE_S, 0, 0)
    time_layout.setSpacing(0)
    layout.addWidget(time_host, 1)
    if not bars:
        return

    width = max(time_host.width(), 480)
    height = max(220, 240)
    figure = build_timeline_figure(
        bars,
        title="Expenses over time",
        ylabel="Weekly total",
        bar_label="Weekly total",
        line_label="7-day average",
        figsize=(width / 100, height / 100),
        line_on_twin=True,
        line_ylabel="7-day average",
    )
    canvas = create_chart_canvas(figure)

    def resolve_tooltip(event: Any) -> str | None:
        if event.xdata is None:
            return None
        bar = bar_at_x(bars, float(event.xdata))
        return None if bar is None else bar.tooltip

    install_chart_hover(canvas, resolve_tooltip=resolve_tooltip)
    canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    time_layout.addWidget(canvas, stretch=1)
    canvas.show()
    canvas.draw()


def range_period_choices() -> list[tuple[str, object]]:
    """Restore the default Days / Months / Years period combo."""
    return [(item, item) for item in _RANGE_PERIOD_ITEMS]


def _expense_cell_tip(day: date, cents: int, currency_symbol: str) -> str:
    if cents <= 0:
        return f"{day.isoformat()}\nNo expenses"
    return f"{day.isoformat()}\n{fmt_money(cents / 100, currency_symbol)}"


def _expense_week_tip(
    start: date,
    end: date,
    recorded: dict[date, int],
    currency_symbol: str,
) -> str:
    present = [day for day in recorded if start <= day <= end]
    total_cents = sum(recorded[day] for day in present)
    return (
        f"{start.isoformat()} - {end.isoformat()}\n"
        f"Total: {fmt_money(total_cents / 100, currency_symbol)}\n"
        f"Days with expenses: {fmt_number(len(present), decimals=0)}"
    )


def _metric_pairs(stats: Any, currency_symbol: str) -> list[tuple[str, str]]:
    total = float(getattr(stats, "total", 0)) / 100
    return [
        ("Total", fmt_money(total, currency_symbol)),
        ("Active days", fmt_number(getattr(stats, "completed", 0), decimals=0)),
        ("Current streak", fmt_number(getattr(stats, "current_streak", 0), decimals=0)),
        ("Longest streak", fmt_number(getattr(stats, "longest_streak", 0), decimals=0)),
    ]


def _period_bounds(selection: object, today: date) -> tuple[date, date] | None:
    if selection == ALL_YEARS_LABEL:
        return None
    if selection == LAST_365_LABEL or selection is None:
        return today - timedelta(days=_CHART_PERIOD_DAYS - 1), today
    if isinstance(selection, int):
        return date(selection, 1, 1), date(selection, 12, 31)
    if isinstance(selection, str) and selection.isdigit():
        year = int(selection)
        return date(year, 1, 1), date(year, 12, 31)
    return today - timedelta(days=_CHART_PERIOD_DAYS - 1), today


def _present_all_years(
    layout: QVBoxLayout,
    metrics: MetricStrip,
    recorded: dict[date, int],
    *,
    currency_symbol: str,
    today: date,
) -> None:
    years = sorted({day.year for day in recorded if day.year <= today.year}, reverse=True)
    bands = heatmap_year_bands(years, today=today)
    if not bands:
        empty = FluentText("No expenses to show.", word_wrap=True, role=TextRole.SECONDARY)
        layout.addWidget(empty)
        layout.addStretch(1)
        return
    start = bands[-1][1]
    end = bands[0][2]
    first_day = min(recorded)
    tokens, marks, legend, bin_count = habit_calendar_model(
        recorded,
        start,
        end,
        is_bool=False,
        activity_start=first_day,
        today=today,
    )
    colors = {cell: habit_token_color(state, bin_count=bin_count) for cell, state in tokens.items()}
    tips = {cell: _expense_cell_tip(cell, recorded.get(cell, 0), currency_symbol) for cell in tokens}
    stack = YearHeatmapStack()
    stack.set_years(
        bands,
        colors,
        legend=habit_legend_colors(legend, bin_count=bin_count),
        marks=marks,
        tooltips=tips,
    )
    layout.addWidget(stack, 1)
    stats = habit_period_stats(recorded, start, end, is_bool=False, today=today)
    metrics.set_metrics(_metric_pairs(stats, currency_symbol))
