"""Tests for Action usage stats table copy helper."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QTableWidgetSelectionRange

from harrix_swiss_knife.actions.common.action_usage_stats_browser import copy_table_widget_selection


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_copy_table_widget_selection_copies_tab_separated_cells(qapp: QApplication) -> None:
    table = QTableWidget(2, 3)
    table.setItem(0, 0, QTableWidgetItem("1"))
    table.setItem(0, 1, QTableWidgetItem("Finance"))
    table.setItem(0, 2, QTableWidgetItem("Apps"))
    table.setItem(1, 0, QTableWidgetItem("2"))
    table.setItem(1, 1, QTableWidgetItem("Fitness"))
    table.setItem(1, 2, QTableWidgetItem("Apps"))
    table.setRangeSelected(QTableWidgetSelectionRange(0, 0, 1, 1), True)  # noqa: FBT003

    text = copy_table_widget_selection(table)
    assert text == "1\tFinance\n2\tFitness"
    clipboard = qapp.clipboard()
    assert clipboard is not None
    assert clipboard.text() == text
