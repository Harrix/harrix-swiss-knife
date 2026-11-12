"""Tests for Finance Transactions day group headers."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QTableView

from harrix_swiss_knife.apps.finance.transaction_day_headers import (
    IS_DAY_HEADER_ROLE,
    TransactionDayHeaderProxy,
    apply_transaction_day_header_spans,
)
from harrix_swiss_knife.apps.finance.transaction_day_totals import (
    TRANSACTION_COL_DATE,
    TRANSACTION_COL_TOTAL_PER_DAY,
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


def _row(date: str, total: str = "") -> list[QStandardItem]:
    items = [QStandardItem("") for _ in range(8)]
    items[TRANSACTION_COL_DATE] = QStandardItem(date)
    items[TRANSACTION_COL_TOTAL_PER_DAY] = QStandardItem(total)
    return items


def test_day_header_proxy_inserts_headers_per_date(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(8)
    source.appendRow(_row("2026-08-25", "-80.00"))
    source.appendRow(_row("2026-08-25", ""))
    source.appendRow(_row("2026-08-24", "-10.00"))

    proxy = TransactionDayHeaderProxy()
    proxy.setSourceModel(source)

    # 2 headers + 3 data rows
    assert proxy.rowCount() == 5
    assert bool(proxy.index(0, 0).data(IS_DAY_HEADER_ROLE))
    assert proxy.index(0, 0).data(Qt.ItemDataRole.DisplayRole) == "2026-08-25"
    assert not bool(proxy.index(1, 0).data(IS_DAY_HEADER_ROLE))
    assert bool(proxy.index(3, 0).data(IS_DAY_HEADER_ROLE))
    assert proxy.index(3, 0).data(Qt.ItemDataRole.DisplayRole) == "2026-08-24"

    mapped = proxy.mapToSource(proxy.index(1, TRANSACTION_COL_DATE))
    assert mapped.isValid()
    assert mapped.row() == 0
    assert not proxy.mapToSource(proxy.index(0, 0)).isValid()
    # QAbstractProxyModel.parent is pure virtual; views call it via isValid/selection.
    assert not proxy.parent(proxy.index(0, 0)).isValid()


def test_day_header_spans_full_row(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(8)
    source.appendRow(_row("2026-08-25", "-80.00"))
    proxy = TransactionDayHeaderProxy()
    proxy.setSourceModel(source)
    view = QTableView()
    view.setModel(proxy)
    apply_transaction_day_header_spans(view)
    # Force view paths that call parent() (selection / index validation).
    view.selectRow(0)
    assert view.rowSpan(0, 0) == 1
    assert view.columnSpan(0, 0) == 8
    view.close()
