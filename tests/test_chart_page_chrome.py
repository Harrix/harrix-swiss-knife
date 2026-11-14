"""Tests for the shared chart toolbar mode visibility."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.chart_page_chrome import ChartToolbar

_APP: QApplication | None = None


def _ensure_app() -> QApplication:
    global _APP  # noqa: PLW0603
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    _APP = QApplication([])
    return _APP


def _shown_toolbar() -> ChartToolbar:
    _ensure_app()
    toolbar = ChartToolbar()
    frame = toolbar.build()
    frame.show()
    return toolbar


def test_chart_toolbar_range_mode_shows_dates_hides_count() -> None:
    toolbar = _shown_toolbar()
    toolbar.set_mode("range")
    assert toolbar.combo_period is not None
    assert not toolbar.combo_period.isHidden()
    assert toolbar.date_from is not None
    assert not toolbar.date_from.isHidden()
    assert toolbar.button_last_week is not None
    assert not toolbar.button_last_week.isHidden()
    assert toolbar.spin_count is not None
    assert toolbar.spin_count.isHidden()
    assert toolbar.combo_month is not None
    assert toolbar.combo_month.isHidden()
    assert toolbar.button_prev_year is not None
    assert toolbar.button_prev_year.isHidden()


def test_chart_toolbar_compare_same_shows_years_and_month() -> None:
    toolbar = _shown_toolbar()
    toolbar.set_mode("compare_same")
    assert toolbar.combo_period is not None
    assert toolbar.combo_period.isHidden()
    assert toolbar.date_from is not None
    assert toolbar.date_from.isHidden()
    assert toolbar.spin_count is not None
    assert not toolbar.spin_count.isHidden()
    assert toolbar.label_count is not None
    assert "year" in toolbar.label_count.text().lower()
    assert toolbar.combo_month is not None
    assert not toolbar.combo_month.isHidden()
    assert toolbar.label_month is not None
    assert not toolbar.label_month.isHidden()


def test_chart_toolbar_heatmap_shows_year_nav() -> None:
    toolbar = _shown_toolbar()
    toolbar.set_mode("heatmap")
    assert toolbar.combo_labels is not None
    assert toolbar.combo_labels.isHidden()
    assert toolbar.button_prev_year is not None
    assert not toolbar.button_prev_year.isHidden()
    assert toolbar.button_next_year is not None
    assert not toolbar.button_next_year.isHidden()
    assert toolbar.button_last_month is not None
    assert toolbar.button_last_month.isHidden()


def test_chart_toolbar_labels_only_hides_count() -> None:
    toolbar = _shown_toolbar()
    toolbar.set_mode("labels_only", show_count=False)
    assert toolbar.combo_labels is not None
    assert not toolbar.combo_labels.isHidden()
    assert toolbar.spin_count is not None
    assert toolbar.spin_count.isHidden()
    assert toolbar.date_from is not None
    assert toolbar.date_from.isHidden()
