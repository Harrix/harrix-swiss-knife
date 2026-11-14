"""Chart number, money, and date-axis formatting."""

from __future__ import annotations

from datetime import date, datetime

import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg

from harrix_swiss_knife.apps.common.chart_format import fmt_compact, fmt_date, fmt_money, fmt_number, setup_date_axis
from harrix_swiss_knife.apps.common.chart_theme import themed_figure


def test_fmt_number_uses_space_and_drops_counter_decimals() -> None:
    """Thousands use a space, and whole counts are not written as `10.0`."""
    text = fmt_number(1_314_733.47)
    assert text.startswith("1 314 733")
    assert "," not in text
    assert fmt_number(10.0) == "10"
    assert fmt_number(10) == "10"


def test_fmt_money_appends_currency() -> None:
    """Money keeps the spaced amount and the currency symbol."""
    text = fmt_money(1_314_733.47, "₽")
    assert text.startswith("1 314 733")
    assert "₽" in text
    assert "," not in text


def test_fmt_compact_scales() -> None:
    """Large point labels use K and M suffixes."""
    assert fmt_compact(1_310_000) == "1.31M"
    assert fmt_compact(25_600) == "25.6K"
    assert fmt_compact(10) == "10"
    assert fmt_compact(1_310_000, unit="₽").endswith("₽")


def test_fmt_date_is_weekday_first() -> None:
    """Tooltip dates read as `Sat, 14 Nov 2026`."""
    assert fmt_date(date(2026, 11, 14)) == "Sat, 14 Nov 2026"
    assert fmt_date(datetime(2026, 11, 14, 11, 45, 0)) == "Sat, 14 Nov 2026 11:45"  # noqa: DTZ001


def test_setup_date_axis_is_horizontal() -> None:
    """Date ticks use a concise formatter and stay horizontal."""
    from PySide6.QtWidgets import QApplication  # noqa: PLC0415

    if QApplication.instance() is None:
        QApplication([])
    figure = themed_figure()
    FigureCanvasAgg(figure)
    axis = figure.add_subplot(111)
    axis.plot([datetime(2020, 1, 1), datetime(2024, 6, 1)], [1, 2])  # noqa: DTZ001
    setup_date_axis(axis, period="Months")
    figure.canvas.draw()
    assert isinstance(axis.xaxis.get_major_formatter(), mdates.ConciseDateFormatter)
    for label in axis.get_xticklabels():
        assert label.get_rotation() == 0
