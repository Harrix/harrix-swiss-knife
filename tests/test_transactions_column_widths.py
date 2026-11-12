"""Tests for Finance Transactions visible-column viewport fill."""

from __future__ import annotations

import pytest
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QTableView

from harrix_swiss_knife.apps.finance.transactions_entry_chrome import (
    _visible_transaction_column_widths,
    apply_transactions_table_column_widths,
)
from harrix_swiss_knife.apps.finance.transactions_ui_settings import (
    TRANSACTION_COL_DATE,
    TRANSACTION_COL_TAG,
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


def test_visible_widths_ignore_hidden_budget(qapp: QApplication) -> None:  # noqa: ARG001
    # Description + Amount + Tag visible; Date/Total must not steal width.
    widths = _visible_transaction_column_widths(
        500,
        8,
        flexible=[0, 2],
        tag_idx=TRANSACTION_COL_TAG,
        min_size=24,
    )
    assert widths[TRANSACTION_COL_TAG] == 100
    assert widths[0] + widths[2] + widths[TRANSACTION_COL_TAG] == 500


def test_apply_widths_fills_viewport_with_hidden_day_columns(qapp: QApplication) -> None:
    model = QStandardItemModel()
    model.setColumnCount(8)
    model.appendRow([QStandardItem("") for _ in range(8)])
    view = QTableView()
    view.setModel(model)
    view.resize(640, 240)
    view.show()
    qapp.processEvents()
    view.setColumnHidden(TRANSACTION_COL_DATE, True)  # noqa: FBT003
    view.setColumnHidden(TRANSACTION_COL_TOTAL_PER_DAY, True)  # noqa: FBT003
    apply_transactions_table_column_widths(view)
    qapp.processEvents()
    header = view.horizontalHeader()
    visible_total = sum(header.sectionSize(i) for i in range(header.count()) if not view.isColumnHidden(i))
    assert abs(visible_total - view.viewport().width()) <= 2
    view.close()
