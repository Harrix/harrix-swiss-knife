"""Tests for shared Qt table model helpers."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import QApplication, QTableView

from harrix_swiss_knife.apps.common.table_models import (
    create_colored_table_proxy_model,
    next_table_sort_order,
    sort_table_by_header_click,
)


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for table widgets."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_next_table_sort_order_toggles_same_column() -> None:
    """A second click on the same column reverses the order."""
    assert next_table_sort_order(2, Qt.SortOrder.AscendingOrder, 2) == Qt.SortOrder.DescendingOrder
    assert next_table_sort_order(2, Qt.SortOrder.DescendingOrder, 2) == Qt.SortOrder.AscendingOrder
    assert next_table_sort_order(1, Qt.SortOrder.DescendingOrder, 3) == Qt.SortOrder.AscendingOrder
    assert next_table_sort_order(-1, Qt.SortOrder.AscendingOrder, 1) == Qt.SortOrder.AscendingOrder


def test_sort_table_by_header_click_skips_image_and_toggles(qapp: QApplication) -> None:
    """Header clicks sort text columns and ignore the image column."""
    assert qapp is not None
    proxy = create_colored_table_proxy_model(
        [
            [QIcon(), "Zulu", "2.0", 1, QColor("white")],
            [QIcon(), "Alpha", "1.0", 2, QColor("white")],
            [QIcon(), "Mike", "3.0", 3, QColor("white")],
        ],
        ["", "Exercise", "Value"],
    )
    table = QTableView()
    table.setModel(proxy)
    header = table.horizontalHeader()
    header.setSectionsClickable(True)

    names_before = [proxy.index(row, 1).data() for row in range(3)]
    assert sort_table_by_header_click(table, 0, skip_section=0) is None
    assert [proxy.index(row, 1).data() for row in range(3)] == names_before

    first = sort_table_by_header_click(table, 1, skip_section=0)
    assert first == (1, Qt.SortOrder.AscendingOrder)
    assert [proxy.index(row, 1).data() for row in range(3)] == ["Alpha", "Mike", "Zulu"]

    header.setSortIndicator(1, Qt.SortOrder.DescendingOrder)
    second = sort_table_by_header_click(
        table,
        1,
        skip_section=0,
        current_section=first[0],
        current_order=first[1],
    )
    assert second == (1, Qt.SortOrder.DescendingOrder)
    assert [proxy.index(row, 1).data() for row in range(3)] == ["Zulu", "Mike", "Alpha"]

    assert sort_table_by_header_click(table, 0, skip_section=0) is None
    assert header.sortIndicatorSection() == 1
    assert header.sortIndicatorOrder() == Qt.SortOrder.DescendingOrder
