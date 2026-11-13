"""Tests for Fitness Sets day/month group headers."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QTableView

from harrix_swiss_knife.apps.fitness.fitness_ui_settings import PROCESS_COL_DATE
from harrix_swiss_knife.apps.fitness.process_day_headers import (
    DAY_HEADER_SETS_ROLE,
    IS_DAY_HEADER_ROLE,
    IS_MONTH_HEADER_ROLE,
    ProcessDayHeaderProxy,
    apply_process_day_header_spans,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _row(date: str, exercise: str = "Push-up") -> list[QStandardItem]:
    items = [QStandardItem("") for _ in range(4)]
    items[0] = QStandardItem(exercise)
    items[1] = QStandardItem("")
    items[2] = QStandardItem("10 times")
    items[PROCESS_COL_DATE] = QStandardItem(date)
    return items


def _proxy_with_current_month(source: QStandardItemModel, month_key: str) -> ProcessDayHeaderProxy:
    proxy = ProcessDayHeaderProxy()
    proxy.current_month_key_override = month_key
    proxy.setSourceModel(source)
    return proxy


def test_day_header_proxy_inserts_headers_per_date(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(4)
    source.appendRow(_row("2026-08-25"))
    source.appendRow(_row("2026-08-25"))
    source.appendRow(_row("2026-08-24"))

    proxy = _proxy_with_current_month(source, "2026-08")

    # current-month banner + 2 day headers + 3 data rows
    assert proxy.rowCount() == 6
    assert bool(proxy.index(0, 0).data(IS_MONTH_HEADER_ROLE))
    assert "Current month" in str(proxy.index(0, 0).data(Qt.ItemDataRole.DisplayRole))
    assert bool(proxy.index(1, 0).data(IS_DAY_HEADER_ROLE))
    assert proxy.index(1, 0).data(Qt.ItemDataRole.DisplayRole) == "2026-08-25"
    assert proxy.index(1, 0).data(DAY_HEADER_SETS_ROLE) == "2"
    assert not bool(proxy.index(2, 0).data(IS_DAY_HEADER_ROLE))
    assert bool(proxy.index(4, 0).data(IS_DAY_HEADER_ROLE))
    assert proxy.index(4, 0).data(Qt.ItemDataRole.DisplayRole) == "2026-08-24"
    assert proxy.index(4, 0).data(DAY_HEADER_SETS_ROLE) == "1"

    mapped = proxy.mapToSource(proxy.index(2, PROCESS_COL_DATE))
    assert mapped.isValid()
    assert mapped.row() == 0
    assert not proxy.mapToSource(proxy.index(0, 0)).isValid()
    assert not proxy.parent(proxy.index(0, 0)).isValid()


def test_empty_current_month_banner_omitted(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(4)
    source.appendRow(_row("2026-10-31"))
    source.appendRow(_row("2026-10-01"))

    proxy = _proxy_with_current_month(source, "2026-11")
    assert proxy.rowCount() == 5
    assert bool(proxy.index(0, 0).data(IS_MONTH_HEADER_ROLE))
    assert proxy.index(0, 0).data(Qt.ItemDataRole.DisplayRole) == "October 2026"
    assert "Current month" not in str(proxy.index(0, 0).data(Qt.ItemDataRole.DisplayRole))
    assert proxy.index(0, 0).data(DAY_HEADER_SETS_ROLE) == "2"


def test_day_header_spans_full_row(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(4)
    source.appendRow(_row("2026-08-25"))
    proxy = _proxy_with_current_month(source, "2026-08")
    view = QTableView()
    view.setModel(proxy)
    apply_process_day_header_spans(view)
    view.selectRow(0)
    assert view.rowSpan(0, 0) == 1
    assert view.columnSpan(0, 0) == 4
    view.close()


def test_headers_are_not_selectable(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(4)
    source.appendRow(_row("2026-08-25"))
    proxy = _proxy_with_current_month(source, "2026-08")
    flags = proxy.flags(proxy.index(0, 0))
    assert flags & Qt.ItemFlag.ItemIsEnabled
    assert not (flags & Qt.ItemFlag.ItemIsSelectable)
    assert not (flags & Qt.ItemFlag.ItemIsEditable)
