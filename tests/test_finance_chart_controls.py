"""Tests for Finance chart control wiring."""

from __future__ import annotations

import inspect

from harrix_swiss_knife.apps.finance.main import MainWindow


def test_compare_controls_rebuild_finance_chart() -> None:
    """Month count and same-month combo must trigger a chart rebuild."""
    source = inspect.getsource(MainWindow._connect_signals)
    assert "self.spinBox_compare_last.valueChanged.connect(self._update_finance_chart)" in source
    assert "self.comboBox_compare_same_months.currentIndexChanged.connect(self._update_finance_chart)" in source


def test_year_start_prompt_only_when_switching_chart_type() -> None:
    """Changing compare count must not re-open the year-start dialog."""
    source = inspect.getsource(MainWindow._update_finance_chart)
    assert "if sender in year_start_radios and not self._prompt_compare_last_years_start()" in source
