"""Tests for Finance Transactions day group headers."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QTableView

from harrix_swiss_knife.apps.finance.transaction_day_headers import (
    DAY_HEADER_INCOME_ROLE,
    IS_DAY_HEADER_ROLE,
    IS_MONTH_HEADER_ROLE,
    TransactionDayHeaderProxy,
    _day_header_total_right,
    _format_header_income,
    _format_header_total,
    apply_transaction_day_header_spans,
)
from harrix_swiss_knife.apps.finance.transaction_day_totals import (
    TRANSACTION_COL_AMOUNT,
    TRANSACTION_COL_CATEGORY,
    TRANSACTION_COL_DATE,
    TRANSACTION_COL_TOTAL_PER_DAY,
)
from harrix_swiss_knife.apps.finance.transactions_ui_settings import TRANSACTION_COL_TAG


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


def _proxy_with_current_month(source: QStandardItemModel, month_key: str) -> TransactionDayHeaderProxy:
    proxy = TransactionDayHeaderProxy()
    proxy.current_month_key_override = month_key
    proxy.setSourceModel(source)
    return proxy


def test_day_header_proxy_inserts_headers_per_date(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(8)
    source.appendRow(_row("2026-08-25", "-80.00"))
    source.appendRow(_row("2026-08-25", ""))
    source.appendRow(_row("2026-08-24", "-10.00"))

    proxy = _proxy_with_current_month(source, "2026-08")

    # current-month banner + 2 day headers + 3 data rows
    assert proxy.rowCount() == 6
    assert bool(proxy.index(0, 0).data(IS_MONTH_HEADER_ROLE))
    assert "Current month" in str(proxy.index(0, 0).data(Qt.ItemDataRole.DisplayRole))
    assert bool(proxy.index(1, 0).data(IS_DAY_HEADER_ROLE))
    assert proxy.index(1, 0).data(Qt.ItemDataRole.DisplayRole) == "2026-08-25"
    assert not bool(proxy.index(2, 0).data(IS_DAY_HEADER_ROLE))
    assert bool(proxy.index(4, 0).data(IS_DAY_HEADER_ROLE))
    assert proxy.index(4, 0).data(Qt.ItemDataRole.DisplayRole) == "2026-08-24"

    mapped = proxy.mapToSource(proxy.index(2, TRANSACTION_COL_DATE))
    assert mapped.isValid()
    assert mapped.row() == 0
    assert not proxy.mapToSource(proxy.index(0, 0)).isValid()
    # QAbstractProxyModel.parent is pure virtual; views call it via isValid/selection.
    assert not proxy.parent(proxy.index(0, 0)).isValid()


def test_month_header_above_previous_month_block(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(8)
    source.appendRow(_row("2026-11-02", "-20.00"))
    source.appendRow(_row("2026-10-31", "-50.00"))
    source.appendRow(_row("2026-10-31", ""))
    expense = _row("2026-10-01", "-10.00")
    expense[TRANSACTION_COL_AMOUNT] = QStandardItem("-10.00")
    expense[TRANSACTION_COL_CATEGORY] = QStandardItem("Food")
    income = _row("2026-10-01", "")
    income[TRANSACTION_COL_AMOUNT] = QStandardItem("100.00")
    income[TRANSACTION_COL_CATEGORY] = QStandardItem("Salary (Income)")
    source.appendRow(expense)
    source.appendRow(income)

    proxy = _proxy_with_current_month(source, "2026-11")
    # current Nov + Nov day + Oct month + Oct-31 day + Oct-01 day + 5 data
    assert proxy.rowCount() == 10
    assert bool(proxy.index(0, 0).data(IS_MONTH_HEADER_ROLE))
    assert "Current month" in str(proxy.index(0, 0).data(Qt.ItemDataRole.DisplayRole))
    assert bool(proxy.index(1, 0).data(IS_DAY_HEADER_ROLE))
    assert proxy.index(1, 0).data(Qt.ItemDataRole.DisplayRole) == "2026-11-02"
    assert bool(proxy.index(3, 0).data(IS_MONTH_HEADER_ROLE))
    assert proxy.index(3, 0).data(Qt.ItemDataRole.DisplayRole) == "October 2026"
    assert proxy.index(3, 0).data(DAY_HEADER_INCOME_ROLE) == "100.00"
    assert bool(proxy.index(4, 0).data(IS_DAY_HEADER_ROLE))
    assert proxy.index(4, 0).data(Qt.ItemDataRole.DisplayRole) == "2026-10-31"


def test_empty_current_month_banner_omitted(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(8)
    source.appendRow(_row("2026-10-31", "-50.00"))
    source.appendRow(_row("2026-10-01", "-10.00"))

    proxy = _proxy_with_current_month(source, "2026-11")
    # No Current month · … — only October month + 2 day headers + 2 data
    assert proxy.rowCount() == 5
    assert bool(proxy.index(0, 0).data(IS_MONTH_HEADER_ROLE))
    assert proxy.index(0, 0).data(Qt.ItemDataRole.DisplayRole) == "October 2026"
    assert "Current month" not in str(proxy.index(0, 0).data(Qt.ItemDataRole.DisplayRole))


def test_day_header_spans_full_row(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(8)
    source.appendRow(_row("2026-08-25", "-80.00"))
    proxy = _proxy_with_current_month(source, "2026-08")
    view = QTableView()
    view.setModel(proxy)
    apply_transaction_day_header_spans(view)
    # Force view paths that call parent() (selection / index validation).
    view.selectRow(0)
    assert view.rowSpan(0, 0) == 1
    assert view.columnSpan(0, 0) == 8
    view.close()


def test_day_header_total_aligns_with_amount_not_tag(qapp: QApplication) -> None:
    source = QStandardItemModel()
    source.setColumnCount(8)
    source.appendRow(_row("2026-08-25", "-80.00"))
    view = QTableView()
    view.setModel(source)
    view.resize(640, 200)
    view.show()
    qapp.processEvents()
    for column, width in enumerate((180, 120, 100, 110, 70, 90, 110, 90)):
        view.setColumnWidth(column, width)
    view.setColumnHidden(TRANSACTION_COL_DATE, True)  # noqa: FBT003
    view.setColumnHidden(TRANSACTION_COL_TOTAL_PER_DAY, True)  # noqa: FBT003
    span = QRect(0, 0, 640, 30)
    total_right = _day_header_total_right(view, span)
    amount_right = view.columnWidth(0) + view.columnWidth(1) + view.columnWidth(TRANSACTION_COL_AMOUNT)
    assert total_right == amount_right
    assert total_right < span.width() - view.columnWidth(TRANSACTION_COL_TAG)
    view.close()


def test_day_header_includes_income_total(qapp: QApplication) -> None:  # noqa: ARG001
    source = QStandardItemModel()
    source.setColumnCount(8)
    expense = _row("2026-08-25", "-80.00")
    expense[TRANSACTION_COL_AMOUNT] = QStandardItem("-80.00")
    expense[TRANSACTION_COL_CATEGORY] = QStandardItem("Food")
    income = _row("2026-08-25", "")
    income[TRANSACTION_COL_AMOUNT] = QStandardItem("1500.00")
    income[TRANSACTION_COL_CATEGORY] = QStandardItem("Salary (Income)")
    source.appendRow(expense)
    source.appendRow(income)

    proxy = _proxy_with_current_month(source, "2026-08")
    day_row = 1
    assert bool(proxy.index(day_row, 0).data(IS_DAY_HEADER_ROLE))
    assert proxy.index(day_row, 0).data(DAY_HEADER_INCOME_ROLE) == "1500.00"
    assert bool(proxy.index(0, 0).data(IS_MONTH_HEADER_ROLE))
    assert proxy.index(0, 0).data(DAY_HEADER_INCOME_ROLE) == "1500.00"


def test_day_header_labels_expenses_when_income_present() -> None:
    assert _format_header_total("-80.00", None) == "Total: -80.₀₀"
    assert _format_header_total("-80.00", None, has_income=True) == "Expenses: -80.₀₀"
    assert _format_header_income("1500.00", None) == "Income: +1 500.₀₀"


def test_flat_filtered_mode_shows_date_hides_total(qapp: QApplication) -> None:  # noqa: ARG001
    from harrix_swiss_knife.apps.finance.transactions_entry_chrome import (  # noqa: PLC0415
        _apply_day_header_column_policy,
    )

    source = QStandardItemModel()
    source.setColumnCount(8)
    source.appendRow(_row("2026-08-25", "-80.00"))
    view = QTableView()
    view.setModel(source)
    _apply_day_header_column_policy(view)
    assert not view.isColumnHidden(TRANSACTION_COL_DATE)
    assert view.isColumnHidden(TRANSACTION_COL_TOTAL_PER_DAY)

    proxy = _proxy_with_current_month(source, "2026-08")
    view.setModel(proxy)
    _apply_day_header_column_policy(view)
    assert view.isColumnHidden(TRANSACTION_COL_DATE)
    assert view.isColumnHidden(TRANSACTION_COL_TOTAL_PER_DAY)
    view.close()


def test_cosmetic_data_changed_does_not_rebuild_headers(qapp: QApplication) -> None:
    source = QStandardItemModel()
    source.setColumnCount(8)
    source.appendRow(_row("2026-08-25", "-80.00"))
    source.appendRow(_row("2026-08-24", "-10.00"))
    proxy = _proxy_with_current_month(source, "2026-08")
    # current-month + 2 day headers + 2 data rows
    assert proxy.rowCount() == 5
    resets = {"count": 0}
    proxy.modelAboutToBeReset.connect(lambda: resets.__setitem__("count", resets["count"] + 1))
    # Simulate theme day-band refresh across Date/Total columns.
    top = source.index(0, 0)
    bottom = source.index(1, TRANSACTION_COL_TOTAL_PER_DAY)
    source.dataChanged.emit(
        top,
        bottom,
        [int(Qt.ItemDataRole.BackgroundRole), int(Qt.ItemDataRole.ForegroundRole)],
    )
    qapp.processEvents()
    assert resets["count"] == 0
    assert proxy.rowCount() == 5
