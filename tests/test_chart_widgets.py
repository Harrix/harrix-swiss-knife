"""Chart card shell: year navigator, sidebar titles, and KPI row."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel

from harrix_swiss_knife.apps.common.chart_widgets import (
    ALL_YEARS_KEY,
    LAST_365_KEY,
    ChartPage,
    ChartSidebar,
    KpiRow,
    KpiSpec,
    YearNavigator,
)

_APP: QApplication | None = None


def _ensure_app() -> QApplication:
    global _APP  # noqa: PLW0603
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    _APP = QApplication([])
    return _APP


def test_year_navigator_orders_years_descending() -> None:
    """Arrows walk Last 365 days, newest year, then All years."""
    _ensure_app()
    navigator = YearNavigator()
    navigator.set_years([2020, 2026, 2024])
    assert navigator.selection() == LAST_365_KEY
    navigator.step(1)
    assert navigator.selection() == "2026"
    assert navigator.year() == 2026
    navigator.step(1)
    assert navigator.selection() == "2024"
    navigator._combo.setCurrentIndex(navigator._combo.count() - 1)
    assert navigator.selection() == ALL_YEARS_KEY
    assert navigator.year() is None
    assert not navigator._next.isEnabled()
    navigator.close()


def test_sidebar_section_drops_colon() -> None:
    """Section titles are stored without a trailing colon."""
    _ensure_app()
    sidebar = ChartSidebar()
    layout = sidebar.add_section("Habit:")
    label = layout.itemAt(0).widget()
    assert isinstance(label, QLabel)
    assert label.text() == "Habit"
    sidebar.close()


def test_kpi_row_keeps_six_equal_cards() -> None:
    """A row shows at most six metrics and reveals itself when filled."""
    _ensure_app()
    row = KpiRow()
    assert row.isHidden()
    specs = [KpiSpec(caption=f"M{index}", value=str(index), trend="up") for index in range(8)]
    row.set_metrics(specs)
    assert not row.isHidden()
    assert row._layout.count() == 6
    row.close()


def test_chart_page_sidebar_limits() -> None:
    """The shell sidebar stays inside 220-420 px and the bottom row has a minimum height."""
    _ensure_app()
    page = ChartPage()
    assert page.sidebar.minimumWidth() == 220
    assert page.sidebar.maximumWidth() == 420
    assert page.bottom.minimumHeight() == 240
    page.close()
