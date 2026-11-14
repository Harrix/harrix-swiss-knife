"""Tests for Finance chart control wiring."""

from __future__ import annotations

import inspect

from harrix_swiss_knife.apps.finance.main import MainWindow


def test_compare_controls_rebuild_finance_chart() -> None:
    """Month count and same-month combo must trigger a chart rebuild via the toolbar."""
    source = inspect.getsource(MainWindow._install_chart_toolbar)
    assert "toolbar.connect_changed(self._update_finance_chart)" in source
    assert "toolbar.bind_host(self)" in source


def test_year_start_prompt_only_when_switching_chart_type() -> None:
    """Changing compare count must not re-open the year-start dialog."""
    source = inspect.getsource(MainWindow._update_finance_chart)
    assert "if sender in year_start_radios and not self._prompt_compare_last_years_start()" in source
    assert "radioButton_type_of_chart_balance_compare_last_years" in source


def test_balance_compare_last_years_uses_spinbox_years() -> None:
    source = inspect.getsource(MainWindow._update_finance_chart)
    assert "radioButton_type_of_chart_balance_compare_last_years.isChecked()" in source
    assert "_draw_balance_compare_last_years_chart" in source
    draw_source = inspect.getsource(MainWindow._draw_balance_compare_last_years_chart)
    assert "compute_balance_compare_last_years" in draw_source


def test_finance_toolbar_mode_sync_covers_compare_and_salary() -> None:
    source = inspect.getsource(MainWindow._sync_finance_chart_toolbar_mode)
    assert 'toolbar.set_mode("compare_last")' in source
    assert 'toolbar.set_mode("compare_same")' in source
    assert 'toolbar.set_mode("compare_years")' in source
    assert 'toolbar.set_mode("labels_only", show_count=False)' in source
